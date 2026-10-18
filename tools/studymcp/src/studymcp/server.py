"""MCP stdio server: seven tools over the Pre-Q notes and the study state.

stdout carries JSON-RPC only, so nothing in this package prints to stdout;
diagnostics go to stderr.
"""

import secrets
import sys
from typing import Literal, NotRequired, TypedDict

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

from .config import find_root
from .tools import Study

INSTRUCTIONS = """Pre-Q exam notes for Maths, Economics, English, Business, Geography and Physics, plus the student's study state.
Ground subject answers in search/read: the notes win. General knowledge is fine for examples and contrasts, but
exam-specific facts (quotes, figures, case details, named places) come only from the notes.
Study sessions: session gives a sweep (fast true/false over every idea, level 1; each F answer comes with its fix)
or ideas to deepen (levels 2-5), with last time's carryover first.
Log every answer with log(reviews=[{id, grade, level, conf?}]); it replies in one line.
School material (kind paper/scheme/course) is an unverified text extraction: say so when you rely on it."""

mcp = FastMCP("study", instructions=INSTRUCTIONS)
_study = None
RO = ToolAnnotations(readOnlyHint=True, openWorldHint=False)


def study():
    global _study
    if _study is None:
        _study = Study()
    return _study


class ErrorItem(TypedDict):
    what: str
    fix: str
    type: NotRequired[str]
    source: NotRequired[str]


class Review(TypedDict):
    id: str
    grade: Literal["ok", "shaky", "slip", "miss"]
    level: NotRequired[int]
    conf: NotRequired[Literal["sure", "guess"]]


@mcp.tool(structured_output=False, annotations=RO)
def search(query: str, subject: str | None = None,
           kind: Literal["all", "notes", "ref", "terms", "syllabus", "cards", "school", "papers"] = "all",
           limit: int = 8) -> str:
    """Full-text search over notes, glossary, reference sheets, syllabus, flashcards and school material.
    Returns ranked hits as `id · page › section · kind` + snippet; an exact glossary definition comes first.
    subject: code, name or alias (econ, geo, maths...). kind=papers for past papers and mark schemes."""
    return study().search(query, subject, kind, limit)


@mcp.tool(structured_output=False, annotations=RO)
def read(id: str, part: int = 1) -> str:
    """Read by id from search/topic. A section id (ECQ/markets#slug) returns the section with its sub-sections
    and an exam-link footer; a page id (ECQ/markets) returns the page or its outline; card, glossary and
    school ids (ECQ/F012#p3) work too. Long text is split into parts."""
    return study().read(id, part)


@mcp.tool(structured_output=False, annotations=RO)
def session(subject: str | None = None, focus: str | None = None, sweep: bool = False) -> str:
    """The brief for the next stretch of a study session; the first one in a chat starts with last time's
    carryover. Picks the topic (carries on from last time, the planner's pick, or focus text such as 'ped').
    A new topic, one untouched for 5+ days, or sweep=true gives a sweep: every idea with ready-made
    true/false statements, about 15 in all (sweep=true with no focus, or the day before the exam: the
    whole subject). A sweep too long for one brief says so; sweep=true again gives the rest. After the
    day-before sweep, the next brief is only its misses.
    Otherwise about 8 ideas to deepen (missed, shaky, warm, fading, new...), each with its state,
    level now -> next, id, a plain gist and statements, plus mix-ins (one from a paired subject),
    traps and the student's past mistakes. Ideas already sent in this chat are one line marked ↺.
    Call again when the topic is solid, the student wants a change, or the ideas are used up."""
    return study().session(subject, focus, sweep=sweep)


@mcp.tool(structured_output=False, annotations=RO)
def topic(subject: str, topic: str | None = None) -> str:
    """Map of a topic: exam date and priority, syllabus objectives (the big picture), key ideas with
    ids and the student's state on each, key words, diagrams, formulas, chains and traps.
    Without a topic: the subject's exam format, priority order and topics with mastery.
    topic is free text ('ped', 'coasts', 'quadratics')."""
    return study().topic(subject, topic)


@mcp.tool(structured_output=False, annotations=RO)
def drill(subject: str | None = None, topic: str | None = None, n: int = 10,
          focus: Literal["auto", "missed", "new"] = "auto") -> str:
    """Quick-fire items from the flashcard decks and logged mistakes: recent misses first, then items about
    to be forgotten, then new high-priority ones. Each item has id, Q, A, hint, why it was chosen, and a
    level and form (true/false, multiple choice, fix, recall). No subject = all subjects by exam urgency."""
    return study().drill(subject, topic, n, focus)


@mcp.tool(structured_output=False)
def log(subject: str, topic: str = "", mode: str = "session",
        score: float | None = None, out_of: float | None = None,
        errors: list[ErrorItem] | None = None, reviews: list[Review] | None = None,
        note: str | None = None) -> str:
    """Record answers. reviews = one per idea, card or mistake id touched: grade ok / shaky (hint, partly
    right, or right but a guess) / slip (careless, not a gap) / miss; level 1-5 of the task; conf sure or
    guess when the student shows it. errors = what the student believed plus the fix (type slip, fact,
    mix-up or link); they go to the private error log and come back later. mode = the task used (sweep,
    fix it, what if, plan it...). note = what works for the student, in a few words (kept for next time).
    Rewrites the subject's carryover. Replies in one line with level changes and any warnings."""
    return study().log(subject, topic, mode, score, out_of, errors, reviews, note)


@mcp.tool(structured_output=False, annotations=RO)
def plan(subject: str | None = None) -> str:
    """Exam countdown, the top three things to do now (with why and a starting level), what is due to
    come back, mastery by subject or by topic, common error types and leeches."""
    return study().plan(subject)


def http_token():
    """Secret path segment for HTTP mode, kept in local/ (gitignored) so the connector URL stays stable."""
    path = find_root() / "local" / "mcp-token"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(secrets.token_urlsafe(24), encoding="utf-8")
    return path.read_text(encoding="utf-8").strip()


def run(port=None):
    study().warm()  # build the index in the background so the first call is fast
    if port is None:
        return mcp.run("stdio")
    # HTTP mode for claude.ai through a tunnel: the secret path is the only auth, and the
    # tunnel's Host header is not localhost, so DNS-rebinding protection must be off.
    mcp.settings.port = port
    mcp.settings.stateless_http = True
    mcp.settings.streamable_http_path = f"/{http_token()}/mcp"
    mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    print(f"study MCP on http://127.0.0.1:{port}{mcp.settings.streamable_http_path}", file=sys.stderr)
    mcp.run("streamable-http")
