"""MCP stdio server: six tools over the Pre-Q notes and the study state.

stdout carries JSON-RPC only, so nothing in this package prints to stdout;
diagnostics go to stderr.
"""

from typing import Literal, NotRequired, TypedDict

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .tools import Study

INSTRUCTIONS = """Pre-Q exam notes for Maths, Economics, English, Business, Geography and Physics, plus the student's study state.
Ground every subject answer in search/read and cite the ids you used; the notes outrank general knowledge.
Use topic for what the exam asks (objectives, rank, traps, past questions). Record quiz marks, mistakes and card grades with log.
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
    grade: Literal["ok", "shaky", "miss"]


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
def topic(subject: str, topic: str | None = None) -> str:
    """What the exam needs for a topic: format and days left, priority rank and why, syllabus objectives,
    section ids, must-know terms/diagrams/formulas, traps, past-paper questions, and the student's mastery
    and recent mistakes. Without a topic: the subject's exam format, mark rules, priority order and topics.
    topic is free text ('ped', 'coasts', 'quadratics')."""
    return study().topic(subject, topic)


@mcp.tool(structured_output=False, annotations=RO)
def drill(subject: str | None = None, topic: str | None = None, n: int = 10,
          focus: Literal["auto", "missed", "new"] = "auto") -> str:
    """Next adaptive drill batch from the flashcard decks and logged mistakes: recent misses first, then items
    whose predicted recall is about to fall below target, then new high-priority items. Each item has
    id, question, answer, hint and why it was chosen. No subject = all subjects weighted by exam urgency."""
    return study().drill(subject, topic, n, focus)


@mcp.tool(structured_output=False)
def log(subject: str, topic: str = "",
        mode: Literal["explain", "blurt", "quiz", "paper", "drill", "cards"] = "quiz",
        score: float | None = None, out_of: float | None = None,
        errors: list[ErrorItem] | None = None, reviews: list[Review] | None = None) -> str:
    """Record study results. score/out_of for a marked attempt; errors = marks lost (appended to the
    student's error log and resurfaced in drills); reviews = drill grades per item id (ok/shaky/miss).
    Returns the mastery change and any leeches."""
    return study().log(subject, topic, mode, score, out_of, errors, reviews)


@mcp.tool(structured_output=False, annotations=RO)
def plan(subject: str | None = None) -> str:
    """Exam countdown, the top three things to do now (with why and method), drill queue size,
    mastery by subject or by topic, common error types and leeches."""
    return study().plan(subject)


def run():
    study().warm()  # build the index in the background so the first call is fast
    mcp.run("stdio")
