"""Ideas: the units a study session works with.

An idea is one `##` section of a notes page together with its `###`
sub-sections (e.g. "what shifts demand"), so sessions stay broad rather than
fact by fact. Pages with fewer than three `##` sections are split at `###`,
and so is a `##` section longer than MAX_CHARS with two or more `###` parts
(58 allusions in one section are 58 ideas, not one): its intro stays an idea
only if it has INTRO_CHARS of its own text.
Trap sections ("This loses marks") are not ideas: they feed planted errors.
An idea's id is its first section's id, so read(id) returns the whole idea.
"""

import hashlib
import re

from .corpus import TRAP_HEADING

SKIP_HEADING = re.compile(r"^(contents|see also|sources?|references|related( pages)?|links?)$", re.I)
MAX_CHARS = 6000    # a longer `##` section with `###` parts is split into one idea per part
INTRO_CHARS = 300   # a split section's own text needs this much to stay an idea

SIGNALS = [  # (name, pattern, minimum count): hints for which tasks fit an idea
    ("chain", re.compile(r"→|->|\bleads? to\b|\bwhich (?:causes|means|leads)|\*\*Chain", re.I), 2),
    ("steps", re.compile(r"(?m)^\s*\d+\.\s"), 3),
    ("compare", re.compile(r"\bvs\.?\b|\bversus\b|\bcompared\b|\bdifference\b|\badvantages?\b|\bwhereas\b", re.I), 1),
    ("timeline", re.compile(r"\b(?:1[5-9]|20)\d\d\b|\bAct [1-5IV]+\b|\bstage \d", re.I), 3),
    ("quotes", re.compile(r"[\"“][^\"”\n]{12,}[\"”]"), 2),
    ("case", re.compile(r"\bcase stud|\bnamed example|\bfor example\b|\be\.g\.", re.I), 1),
    ("maths", re.compile(r"\$\$|\$[^$\n]*[\\^_=][^$\n]*\$"), 2),   # LaTeX, not "$5 and $10"
    ("diagram", re.compile(r"\[figure:"), 1),
    ("evaluation", re.compile(r"\bdepends\b|\bhowever\b|\bon the other hand\b|\bevaluat|\bto what extent\b|\bjudge", re.I), 2),
]


def last_heading(row):
    return row["heading"].split(" › ")[-1] if row.get("heading") else ""


def _group(rows, unit):
    out = []
    for r in rows:
        head = last_heading(r)
        starts = "~" not in r["id"] and r["level"] <= unit
        if starts or not out:
            out.append({"id": r["id"].split("~")[0], "subject": r["subject"], "stem": r["stem"],
                        "title": head, "text": r["text"].strip(), "level": r["level"], "members": [r["id"]],
                        "trap": bool(head and TRAP_HEADING.search(head))})
        else:
            sub = f"### {head}\n" if head and "~" not in r["id"] else ""
            out[-1]["text"] += "\n\n" + sub + r["text"].strip()
            out[-1]["members"].append(r["id"])
    return out


def clusters(rows, max_chars=MAX_CHARS):
    """[{id, subject, stem, title, text, members, trap}] from one notes page's rows, in page order.

    rows: chunk dicts (id, subject, stem, heading, level, text) ordered as in the page.
    """
    rows = [r for r in rows if not r["id"].split("~")[0].endswith("#top")]  # the page intro, in parts too
    heads = [r for r in rows if r["level"] == 2 and "~" not in r["id"]]
    unit = 2 if len(heads) >= 3 else 3
    by_id = {r["id"]: r for r in rows}

    def split(c):
        """c, or its parts one heading level down (recursively) when it is too long."""
        lv = c["level"] + 1
        parts = [m for m in c["members"] if "~" not in m and by_id[m]["level"] == lv]
        if lv > 4 or c["trap"] or len(c["text"]) <= max_chars or len(parts) < 2:
            return [c]
        sub = _group([by_id[m] for m in c["members"]], lv)
        if len(re.sub(r"\s+", "", sub[0]["text"])) < INTRO_CHARS:
            sub = sub[1:]
        return [x for s in sub for x in (split(s) if s["level"] == lv else [s])]

    out = [x for c in _group(rows, unit) for x in split(c)]
    keep = []
    for c in out:
        if SKIP_HEADING.match(c["title"] or ""):
            continue
        if len(re.sub(r"\s+", "", c["text"])) < 12:  # a heading with (almost) nothing under it
            continue
        keep.append(c)
    return keep


def ideas(rows, max_chars=MAX_CHARS):
    """clusters that are ideas (traps excluded)."""
    return [c for c in clusters(rows, max_chars) if not c["trap"]]


def plain(text):
    t = re.sub(r"\$\$.+?\$\$", " ", text, flags=re.S)
    t = re.sub(r"(?m)^\s*\|.*\|\s*$", " ", t)              # tables
    t = re.sub(r"\[figure: [^\]]*\]", " ", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)          # links
    t = re.sub(r"(?m)^\s*(?:#+|[-*>]|\d+\.)\s*", "", t)     # headings, bullets, quotes
    t = re.sub(r"[*_`]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def gist(text, n=160):
    """the first real sentence, in plain text."""
    t = plain(text)
    for s in re.split(r"(?<=[.!?])\s+", t):
        if len(s) >= 25:
            return s if len(s) <= n else s[: n - 1].rstrip() + "…"
    return t[:n]


def idea_hash(text):
    """a short fingerprint of an idea's text, so the prep bank can tell when the notes changed."""
    return hashlib.sha1(" ".join(text.split()).encode("utf-8")).hexdigest()[:10]


def signals(text):
    found = []
    for name, rx, least in SIGNALS:
        if len(rx.findall(text)) >= least:
            found.append(name)
    return found


def _ok_heading(h):
    return not TRAP_HEADING.search(h) and not SKIP_HEADING.match(h)


def _count_block(block, level, max_chars):
    """ideas in one markdown section that starts with a heading at `level`, split as clusters() does."""
    lv = level + 1
    kids = re.split(rf"(?m)^(?=#{{{lv}}}\s)", block)
    if lv > 4 or len(block) <= max_chars or len(kids) < 3:
        return 1
    n = 1 if len(re.sub(r"\s+", "", re.sub(r"\A#+\s.*", "", kids[0]))) >= INTRO_CHARS else 0
    for k in kids[1:]:
        m = re.match(r"#+\s+(.+)", k)
        if m and _ok_heading(m.group(1)):
            n += _count_block(k, lv, max_chars)
    return n


def count_ideas(text, max_chars=MAX_CHARS):
    """cheap idea count from raw markdown (no index): `##` sections, or `###` when fewer than 3,
    with long sections counted by their parts (as clusters() splits them)."""
    body = re.sub(r"(?ms)^```.*?^```", "", text)
    h2 = [h for h in re.findall(r"(?m)^##\s+(.+)$", body) if _ok_heading(h)]
    unit = 2 if len(h2) >= 3 else 3
    n = 0
    for block in re.split(rf"(?m)^(?=#{{2,{unit}}}\s)", body):
        m = re.match(r"(#+)\s+(.+)", block)
        if m and 2 <= len(m.group(1)) <= unit and _ok_heading(m.group(2)):
            n += _count_block(block, len(m.group(1)), max_chars)
    return max(n, 1)
