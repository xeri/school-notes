"""Parse the repo into chunks: note sections, glossary lines, flashcards and
school-material pages. Pure functions of file text, so they are easy to test.

Chunk ids:
  ECQ/markets                    a whole notes page (outline)
  ECQ/markets#conditions-of-demand   a section (GitHub slug; ~2 = second part of a long one)
  ECQ/FORMULAS#...  ECQ/SYLLABUS#...  PLAN#...   reference, syllabus, study plan
  ECQ/markets~1a2b3c4d           a flashcard (deck stem + hash of the front)
  ECQ/TERMS~need                 a glossary definition
  ECQ/F012#p3                    page 3 of school file ECQ-F012 (s = slide, t = table, w = window)
"""

import hashlib
import html
import posixpath
import re
from dataclasses import dataclass, field

MAX_CHUNK = 3500

TRAP_HEADING = re.compile(r"loses? marks|exam errors|mark-losing|traps?\b|common .*errors|mistakes", re.I)
TRAP_LABEL = re.compile(r"^[*_]{0,2}(This loses marks|Mark-losing errors?|Marks are lost by|Common errors?|Traps?)\b[^:\n]{0,30}:", re.I)
CITE = re.compile(r"\b(20\d\d)\s+((?:Q\d+(?:\([a-z0-9]+\))*(?:,\s*)?)+|CT#?\d)")
DEF_LINE = re.compile(r"^\*\*([^*]{1,80}?)\*\*\s*(?:—|–|=|:)\s+(.{8,600})$")
ACRONYM = re.compile(r"\(([A-Z]{2,6})\)")
STOP = {"of", "and", "the", "a", "an", "in", "on", "for", "to", "per"}


@dataclass
class Chunk:
    id: str
    subject: str
    kind: str          # notes | ref | syllabus | terms | cards | paper | scheme | course | spec | school
    path: str          # repo-relative, forward slashes
    stem: str          # page stem, deck stem or school file id
    title: str
    heading: str = ""  # breadcrumb, " › " separated
    level: int = 0     # heading level (1 = page intro)
    text: str = ""
    extra: dict = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# text helpers
# --------------------------------------------------------------------------- #

def slugify(heading):
    """GitHub-style anchor: lower case, drop punctuation, spaces to hyphens."""
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = t.lower().strip()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def plain_heading(heading):
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    return re.sub(r"[*_`]", "", t).strip()


def clean_html(text):
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</?i>", "*", text, flags=re.I)
    text = re.sub(r"</?b>", "**", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def index_text(text):
    """what goes into the full-text index: link targets and markup removed."""
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r" \1 ", text)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"\{\{c\d+::(.*?)(?:::[^}]*)?\}\}", r"\1", t)
    return t


def rewrite_links(text, code, page_dir):
    """turn relative repo links into tool ids, so Claude can read() them.

    page_dir is the folder of the page relative to the subject folder:
    "notes" for notes pages, "" for SYLLABUS and reference files.
    """
    def repl(m):
        label, target = m.group(1), m.group(2)
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            return m.group(0)
        path, _, anchor = target.partition("#")
        full = posixpath.normpath(posixpath.join(page_dir or ".", path))
        anchor = f"#{anchor}" if anchor else ""
        if full.startswith("notes/") and full.endswith(".md"):
            return f"[{label}]({code}/{full[6:-3]}{anchor})"
        if full.endswith(".md") and "/" not in full:
            return f"[{label}]({code}/{full[:-3]}{anchor})"
        if full.startswith("anki/") and full.endswith(".txt"):
            return f"[{label}](deck {code}/{full[5:-4]})"
        if full.endswith(".svg"):
            return f"[{label}]({code}/notes/{posixpath.basename(full)})"
        return m.group(0)

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+\.svg)\)", r"[figure: \1 (\2)]", text)
    return re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", repl, text)


def link_stems(text, page_dir="notes"):
    """note stems a piece of markdown links to (relative to page_dir)."""
    stems = []
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        path = target.partition("#")[0]
        if not path or re.match(r"[a-z]+:", path):
            continue
        full = posixpath.normpath(posixpath.join(page_dir or ".", path))
        if full.startswith("notes/") and full.endswith(".md"):
            stem = full[6:-3]
            if stem not in stems:
                stems.append(stem)
    return stems


def link_decks(text, page_dir="notes"):
    decks = []
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        full = posixpath.normpath(posixpath.join(page_dir or ".", target.partition("#")[0]))
        if full.startswith("anki/") and full.endswith(".txt") and full[5:-4] not in decks:
            decks.append(full[5:-4])
    return decks


def acronyms(text):
    """'price elasticity of demand (PED)' -> {'PED': 'price elasticity of demand'}"""
    found = {}
    for m in ACRONYM.finditer(text):
        acr = m.group(1)
        if acr in found:
            continue
        before = re.sub(r"[*_`\[\]]", "", text[max(0, m.start() - 90): m.start()])
        words = re.findall(r"[A-Za-z][\w'-]*", before)
        for k in range(len(acr), min(len(words), len(acr) + 3) + 1):
            cand = words[-k:]
            initials = "".join(w[0] for w in cand if w.lower() not in STOP).upper()
            if initials == acr:
                found.setdefault(acr, " ".join(cand).strip(" ,;:").lower())
                break
    return found


# --------------------------------------------------------------------------- #
# markdown pages
# --------------------------------------------------------------------------- #

def _blocks(lines):
    """group lines into blocks that must not be split: paragraphs, $$ maths, tables."""
    blocks, cur, in_math = [], [], False

    def flush():
        if cur:
            blocks.append(list(cur))
            cur.clear()

    for line in lines:
        s = line.strip()
        if in_math:
            cur.append(line)
            if s.endswith("$$"):
                in_math = False
            continue
        if s.startswith("$$") and not (len(s) > 2 and s.endswith("$$")):
            in_math = True
            cur.append(line)
            continue
        is_table = s.startswith("|")
        if cur and (not s or (is_table != cur[-1].strip().startswith("|"))):
            flush()
        if s:
            cur.append(line)
    flush()
    return blocks


def _is_group_row(row):
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    return len(cells) > 1 and cells[0].startswith("**") and not any(cells[1:])


def _split_table(block, limit):
    head, rows = block[:2], block[2:]
    pieces, cur, size = [], [], 0
    for row in rows:
        if cur and (size + len(row) > limit or (_is_group_row(row) and size > limit // 3)):
            pieces.append(head + cur)
            cur, size = [], 0
        cur.append(row)
        size += len(row) + 1
    if cur:
        pieces.append(head + cur)
    return pieces


def split_text(text, limit=MAX_CHUNK):
    """split a long section at block boundaries; long tables repeat their header."""
    if len(text) <= limit:
        return [text]
    units = []
    for b in _blocks(text.split("\n")):
        body = "\n".join(b)
        if len(body) > limit and b[0].strip().startswith("|") and len(b) > 3:
            units.extend("\n".join(p) for p in _split_table(b, limit))
        else:
            units.append(body)
    pieces, cur = [], ""
    for u in units:
        if cur and len(cur) + len(u) + 2 > limit:
            pieces.append(cur)
            cur = u
        else:
            cur = f"{cur}\n\n{u}" if cur else u
    if cur:
        pieces.append(cur)
    return pieces


def parse_markdown(text, code, stem, kind, path, page_dir):
    """one chunk per ## / ### / #### section (plus the intro), long ones split."""
    lines = text.split("\n")
    title = stem
    for line in lines:
        if line.startswith("# "):
            title = plain_heading(line[2:])
            break
    base = f"{code}/{stem}" if code else stem
    chunks, seen = [], {}
    stack = []  # (level, plain heading)
    cur_head, cur_level, cur_lines = None, 1, []
    in_math = False

    def emit():
        body = "\n".join(cur_lines).strip()
        if cur_head is None:
            slug = "top"
        else:
            slug = slugify(cur_head)
            n = seen.get(slug, 0)
            seen[slug] = n + 1
            if n:
                slug = f"{slug}-{n}"
        if not body and cur_head is None:
            return
        crumbs = " › ".join(h for _, h in stack)
        body = rewrite_links(body, code, page_dir) if code else body
        for i, piece in enumerate(split_text(body) if body else [""]):
            cid = f"{base}#{slug}" + (f"~{i + 1}" if i else "")
            chunks.append(Chunk(cid, code, kind, path, stem, title, crumbs, cur_level, piece))

    for line in lines:
        s = line.strip()
        if s.startswith("$$") and not (len(s) > 2 and s.endswith("$$")):
            in_math = not in_math
        m = None if in_math else re.match(r"^(#{1,4})\s+(.*)$", line)
        if m and len(m.group(1)) == 1:
            continue
        if m:
            emit()
            level = len(m.group(1))
            cur_head = m.group(2).strip()
            cur_level = level
            stack = [(lv, h) for lv, h in stack if lv < level] + [(level, plain_heading(cur_head))]
            cur_lines = []
        else:
            cur_lines.append(line)
    emit()
    return title, chunks


def definitions(text, code, stem, path, title):
    """glossary chunks: '**Term** — definition' in reference files, '**Term** = definition'
    in notes (notes use the dash for labels, not definitions)."""
    out, seen = [], set()
    in_notes = "/notes/" in path
    if stem == "study-guide":
        return out
    for line in text.split("\n"):
        m = DEF_LINE.match(line.strip())
        if not m or (in_notes and not re.match(r"^\*\*[^*]+\*\*\s*=", line.strip())):
            continue
        term = plain_heading(m.group(1)).rstrip(":").strip()
        if len(term) < 2 or term.lower() in {"why", "method", "start here", "facts", "chain"}:
            continue
        slug = slugify(term)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        body = rewrite_links(m.group(2).strip(), code, "notes" if "/notes/" in path else "")
        out.append(Chunk(f"{code}/{stem}~{slug}", code, "terms", path, stem, title, term, 0,
                         f"**{term}** — {body}", {"term": term}))
    return out


def traps(chunks):
    """(chunk id, excerpt) for trap sections and 'This loses marks:' paragraphs."""
    found = []
    for c in chunks:
        last = c.heading.split(" › ")[-1] if c.heading else ""
        if last and TRAP_HEADING.search(last):
            found.append((c.id, c.text[:700]))
            continue
        for para in c.text.split("\n\n"):
            if TRAP_LABEL.match(para.strip()):
                found.append((c.id, para.strip()[:700]))
    return found


def cites(text):
    return sorted({f"{m.group(1)} {m.group(2).strip(', ')}" for m in CITE.finditer(text)})


# --------------------------------------------------------------------------- #
# flashcards
# --------------------------------------------------------------------------- #

def parse_deck(text, code, stem, path):
    deck, tags, cards = stem, "", []
    for line in text.split("\n"):
        if not line.strip():
            continue
        if line.startswith("#"):
            key, _, val = line[1:].partition(":")
            if key == "deck":
                deck = val.strip()
            elif key == "tags":
                tags = val.strip()
            continue
        f = line.split("\t")
        if len(f) < 2:
            continue
        ntype = f[0].strip()
        front = f[1]
        back = f[2] if len(f) > 2 else ""
        hint = f[3] if len(f) > 3 else ""
        cloze = "cloze" in ntype.lower() or "{{c" in front
        if cloze:
            question = re.sub(r"\{\{c\d+::(.*?)(?:::([^}]*))?\}\}",
                              lambda m: f"[{m.group(2)}…]" if m.group(2) else "[…]", front)
            answer = re.sub(r"\{\{c\d+::(.*?)(?:::[^}]*)?\}\}", r"**\1**", front)
            if back.strip():
                answer += "\n" + back
        else:
            question, answer = front, back
        h = hashlib.sha1(front.encode("utf-8")).hexdigest()[:8]
        q, a, hn = clean_html(question), clean_html(answer), clean_html(hint)
        cards.append(Chunk(f"{code}/{stem}~{h}", code, "cards", path, stem, deck, deck, 0,
                           f"{q}\n→ {a}" + (f"\n(hint: {hn})" if hn else ""),
                           {"q": q, "a": a, "hint": hn, "cloze": cloze, "deck": deck, "tags": tags}))
    return deck, cards


# --------------------------------------------------------------------------- #
# school material (local/extracted)
# --------------------------------------------------------------------------- #

def school_kind(source):
    s = source.lower()
    if "mark-scheme" in s or "markscheme" in s:
        return "scheme"
    if "/assessment/" in s or s.startswith("sources/assessment") or "question-paper" in s:
        return "paper"
    if "specification" in s:
        return "spec"
    if "/course/" in s or s.startswith("sources/course"):
        return "course"
    return "school"


def parse_extracted(text, code, path):
    """split an extracted file into pages/slides; returns (meta, chunks)."""
    fid = posixpath.basename(path)[:-3]          # ECQ-F012
    short = fid.split("-", 1)[-1]                # F012
    m = re.search(r"Source:\s*`([^`]+)`", text)
    source = m.group(1) if m else ""
    if "archive/excluded" in source:
        return None, []
    kind = school_kind(source)
    year = re.search(r"/(20\d\d)/", source)
    title = posixpath.splitext(posixpath.basename(source))[0] if source else fid
    meta = {"source": source, "year": year.group(1) if year else "", "file": fid}
    parts = re.split(r"^## (Page|Slide|Table) (\d+)\s*$", text, flags=re.M)
    pieces = []
    if len(parts) > 1:
        for i in range(1, len(parts), 3):
            pieces.append((f"{parts[i][0].lower()}{parts[i + 1]}", f"{parts[i]} {parts[i + 1]}", parts[i + 2]))
    else:
        body = text.split("\n", 3)[-1]
        buf, n = "", 0
        for line in body.split("\n"):
            buf += line + "\n"
            if len(buf) > 2000:
                n += 1
                pieces.append((f"w{n}", f"Part {n}", buf))
                buf = ""
        if buf.strip():
            n += 1
            pieces.append((f"w{n}", f"Part {n}", buf))
    chunks = []
    for key, label, body in pieces:
        body = re.sub(r"[ \t]+", " ", body)
        body = re.sub(r"\n\s*\n+", "\n\n", body).strip()
        if len(body) < 20:
            continue
        for j, piece in enumerate(split_text(body, 4000)):
            cid = f"{code}/{short}#{key}" + (f"~{j + 1}" if j else "")
            chunks.append(Chunk(cid, code, kind, path, short, title, label, 0, piece, dict(meta)))
    return meta, chunks


def text_hash(text):
    return hashlib.sha1(re.sub(r"\s+", " ", text).strip().lower().encode("utf-8")).hexdigest()
