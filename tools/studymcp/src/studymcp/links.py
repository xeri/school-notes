"""The topic graph: how each notes page links to the exam.

Built from SYLLABUS.md (index table, objectives, exam format), the study
guide (priority order, tiers, exam section) and STUDY-PLAN.md (exam dates).
Every parser degrades gracefully: a page with no objectives or rank is
simply "cross-cutting".
"""

import re
from dataclasses import dataclass, field
from datetime import date

from .corpus import cites, link_decks, link_stems, plain_heading, traps

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
DATE_RE = re.compile(r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w*\s+(\d{1,2})\s+([A-Za-z]{3})", re.I)


@dataclass
class Topic:
    code: str
    stem: str
    title: str
    order: int = 0
    rows: list = field(default_factory=list)        # syllabus index labels
    group: str = ""                                 # syllabus group row (GEQ themes)
    decks: list = field(default_factory=list)
    objectives: list = field(default_factory=list)  # (code, text)
    rank: int | None = None
    why: str = ""
    method: str = ""
    tier: int | None = None
    traps: list = field(default_factory=list)       # (chunk id, excerpt)
    cites: list = field(default_factory=list)


@dataclass
class SubjectInfo:
    code: str
    name: str
    exam_date: date | None = None
    exam_when: str = ""
    exam_format: str = ""
    syllabus_intro: str = ""
    marks_text: str = ""
    guide_exam: str = ""
    priority: list = field(default_factory=list)     # dicts: rank, item, stems, why, method, tier
    topics: dict = field(default_factory=dict)       # stem -> Topic
    deck_stems: dict = field(default_factory=dict)   # deck -> [stems]
    deck_tier: dict = field(default_factory=dict)    # deck -> tier
    trap_ids: set = field(default_factory=set)       # chunk ids (notes and reference) holding traps


# --------------------------------------------------------------------------- #
# markdown helpers
# --------------------------------------------------------------------------- #

def cells(row):
    return [c.strip() for c in re.split(r"(?<!\\)\|", row.strip().strip("|"))]


def tables(text):
    """[(header cells, [(row cells, raw row)])] for every pipe table."""
    out, cur = [], None
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("|"):
            if cur is None:
                cur = [cells(s), []]
            elif re.match(r"^\|[\s:|-]+\|?$", s):
                continue
            else:
                cur[1].append((cells(s), s))
        elif cur is not None:
            out.append(tuple(cur))
            cur = None
    if cur is not None:
        out.append(tuple(cur))
    return out


def sections(text, level=2):
    """{heading: body} for headings of exactly this level (first wins)."""
    out, head, buf = {}, None, []
    marker = "#" * level + " "
    for line in text.split("\n"):
        if line.startswith(marker):
            if head is not None and head not in out:
                out[head] = "\n".join(buf).strip()
            head, buf = line[len(marker):].strip(), []
        elif re.match(r"^#{1,%d} " % (level - 1), line):
            if head is not None and head not in out:
                out[head] = "\n".join(buf).strip()
            head, buf = None, []
        elif head is not None:
            buf.append(line)
    if head is not None and head not in out:
        out[head] = "\n".join(buf).strip()
    return out


def plain(text, limit=None):
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = t.replace("**", "").strip()
    if limit and len(t) > limit:
        t = t[: limit - 1].rstrip() + "…"
    return t


def parse_tier(cell):
    t = cell.replace("*", "").strip().lower()
    if t.startswith("start"):
        return 1
    m = re.match(r"\D*(\d)", t)
    return int(m.group(1)) if m else None


def find_col(header, pattern):
    for i, h in enumerate(header):
        if re.search(pattern, h.replace("*", "").strip(), re.I):
            return i
    return None


# --------------------------------------------------------------------------- #
# SYLLABUS.md
# --------------------------------------------------------------------------- #

def expand_codes(cell):
    """'E2.1–2.8, 2.12' -> ['E2.1', ..., 'E2.8', 'E2.12'];  'E5' -> ['E5']"""
    out, prefix = [], "E"
    for tok in re.split(r"[,;]", cell.replace("*", "")):
        tok = tok.strip()
        m = re.match(r"^([A-Z]?)(\d+)(?:\.(\d+))?(?:\s*[–-]\s*[A-Z]?(\d+)\.(\d+))?$", tok)
        if not m:
            continue
        prefix = m.group(1) or prefix
        major, lo, hi_major, hi = m.group(2), m.group(3), m.group(4), m.group(5)
        if lo and hi:
            out += [f"{prefix}{major}.{i}" for i in range(int(lo), int(hi) + 1)]
        elif lo:
            out.append(f"{prefix}{major}.{lo}")
        else:
            out.append(f"{prefix}{major}")
    return out


def parse_syllabus(text, info):
    """index table rows, group labels, objectives and exam text."""
    index = None
    for header, rows in tables(text):
        low = [h.lower() for h in header]
        if any("notes" in h for h in low) and any("cards" in h for h in low):
            index = (header, rows)
            break
    row_stems = {}     # row key -> stems
    code_stems = {}    # objective code / major -> stems (Maths codes column)
    order = 0
    if index:
        header, rows = index
        codes_col = find_col(header, r"^codes?$")
        label_col = 1 if len(header) > 1 else 0
        group = ""
        for c, raw in rows:
            stems = link_stems(raw, "")
            decks = link_decks(raw, "")
            if not stems:
                if c and c[0].startswith("**"):
                    group = plain(c[0])
                continue
            key = c[0].replace("*", "").strip()
            label = plain(c[label_col]) if label_col < len(c) else ""
            row_stems.setdefault(key, [])
            for s in stems:
                t = info.topics.setdefault(s, Topic(info.code, s, label or s))
                if not t.order:
                    order += 1
                    t.order = order
                t.rows.append(f"{key} {label}".strip())
                t.group = t.group or group
                for d in decks:
                    if d not in t.decks:
                        t.decks.append(d)
                    info.deck_stems.setdefault(d, [])
                    if s not in info.deck_stems[d]:
                        info.deck_stems[d].append(s)
                row_stems[key].append(s)
                if codes_col is not None and codes_col < len(c):
                    for code in expand_codes(c[codes_col]):
                        code_stems.setdefault(code, []).append(s)

    # exam format: everything before the index table / first ## topic section
    first = text.find("\n## ")
    head = text[: first if first > 0 else len(text)]
    if index:
        cut = head.find(index[1][0][1]) if index[1] else -1
        tbl = head.rfind("\n|", 0, cut) if cut > 0 else -1
        head = head[: tbl] if tbl > 0 else head
    info.syllabus_intro = plain(re.sub(r"^# .*\n", "", head), 1800)

    for h, body in sections(text, 2).items():
        if re.search(r"exam|marks|technique|format", h, re.I) and not re.match(r"^\d+\.", h):
            info.marks_text += f"### {h}\n{plain(body, 1600)}\n\n"
        sec_text = body
        m = re.match(r"^(\d+)\.", h)
        sec_default = row_stems.get(m.group(1), []) if m else []
        _objectives(sec_text, sec_default, code_stems, info, m.group(1) if m else "")
    info.marks_text = info.marks_text.strip()[:3000]


def _objectives(body, sec_default, code_stems, info, sec_no):
    block_code, block_default, block_items, n = None, [], [], 0

    def close():
        if not block_items:
            return
        linked = [s for _, _, stems in block_items for s in stems]
        for code, txt, stems in block_items:
            for s in stems or linked or block_default or sec_default:
                t = info.topics.get(s)
                if t is not None and len(t.objectives) < 40:
                    t.objectives.append((code, txt))

    for line in body.split("\n"):
        s = line.strip()
        m = re.match(r"^\*\*(\d+\.\d+)\s+(.+?)\*\*(.*)$", s)
        if m:
            close()
            block_code = m.group(1)
            block_default = link_stems(m.group(3), "")
            block_items = []
            title = plain(m.group(2))
            if block_default:
                block_items.append((block_code, title, []))
            n = 0
            continue
        if s.startswith("- "):
            n += 1
            item = s[2:]
            mc = re.match(r"^\*\*([A-Z]?\d+\.\d+)\*\*\s*(.*)$", item)
            if mc:
                code, txt = mc.group(1), mc.group(2)
                stems = list(dict.fromkeys(code_stems.get(code, []) + code_stems.get(code.split(".")[0], [])))
            else:
                code = f"{block_code}.{n}" if block_code else (f"{sec_no}.{n}" if sec_no else "")
                txt, stems = item, []
            stems = link_stems(item, "") or stems
            block_items.append((code, plain(txt, 260), stems))
    close()


# --------------------------------------------------------------------------- #
# study guide
# --------------------------------------------------------------------------- #

def parse_guide(text, info):
    secs = sections(text, 2)
    if secs:
        first_head = next(iter(secs))
        info.guide_exam = f"{first_head}\n" + plain(secs[first_head], 1400)

    prio = next((b for h, b in secs.items() if h.lower().startswith("priority")), "")
    rows = []
    tbls = tables(prio)
    if tbls:
        header, trs = tbls[0]
        rc = find_col(header, r"^(#|rank)$")
        tc = find_col(header, r"tier")
        wc = find_col(header, r"why")
        mc = find_col(header, r"^(how|method)")
        used = {rc, tc, wc, mc}
        ic = next((i for i in range(len(header)) if i not in used), 1)
        for c, raw in trs:
            get = lambda i: c[i] if i is not None and i < len(c) else ""
            rank = re.match(r"\D*(\d+)", get(rc))
            rows.append({
                "rank": int(rank.group(1)) if rank else None,
                "item": plain(get(ic), 160),
                "stems": link_stems(raw, "notes"),
                "decks": link_decks(raw, "notes"),
                "why": plain(get(wc), 420),
                "method": plain(get(mc), 300),
                "tier": parse_tier(get(tc)) if tc is not None else None,
            })
    else:
        for h, body in sections(prio, 3).items():
            m = re.match(r"^(\d+)\.\s*(.*)$", h)
            if not m:
                continue
            why = re.search(r"^\*\*Why[^*]*\*\*\s*(.*)$", body, re.M)
            meth = re.search(r"^\*\*Method[^*]*\*\*\s*\n?((?:.*\n?){1,6})", body, re.M)
            rows.append({
                "rank": int(m.group(1)),
                "item": plain(m.group(2).split(":")[0], 160),
                "stems": link_stems(h + "\n" + body, "notes"),
                "decks": link_decks(body, "notes"),
                "why": plain(why.group(1), 420) if why else "",
                "method": plain(meth.group(1), 300) if meth else "",
                "tier": None,
            })
    info.priority = rows
    for r in rows:
        for s in r["stems"]:
            t = info.topics.setdefault(s, Topic(info.code, s, s))
            if r["rank"] is not None and (t.rank is None or r["rank"] < t.rank):
                t.rank, t.why, t.method = r["rank"], r["why"], r["method"]
            if r["tier"] is not None:
                t.tier = r["tier"] if t.tier is None else min(t.tier, r["tier"])
        for d in r["decks"]:
            if r["tier"] is not None:
                info.deck_tier[d] = min(info.deck_tier.get(d, 9), r["tier"])

    check = next((b for h, b in secs.items() if h.lower().startswith("topic checklist")), "")
    for header, trs in tables(check)[:1]:
        tc = find_col(header, r"tier")
        if tc is None:
            continue
        for c, raw in trs:
            tier = parse_tier(c[tc]) if tc < len(c) else None
            if tier is None:
                continue
            for s in link_stems(raw, "notes"):
                t = info.topics.setdefault(s, Topic(info.code, s, s))
                t.tier = tier if t.tier is None else min(t.tier, tier)
            for d in link_decks(raw, "notes"):
                info.deck_tier[d] = min(info.deck_tier.get(d, 9), tier)


# --------------------------------------------------------------------------- #
# STUDY-PLAN.md
# --------------------------------------------------------------------------- #

def parse_plan(text, cfg):
    """{code: (date, 'Tue 27 Oct, morning', format)}"""
    year = re.search(r"\b(20\d\d)\b", text.split("\n", 1)[0])
    year = int(year.group(1)) if year else date.today().year
    out = {}
    for header, rows in tables(text):
        dc = find_col(header, r"^date$")
        if dc is None:
            continue
        fc = find_col(header, r"format")
        for c, _ in rows:
            name = plain(c[0])
            code = cfg.resolve_subject(name) or cfg.resolve_subject(name.split()[0])
            m = DATE_RE.search(c[dc]) if dc < len(c) else None
            if code and m and m.group(2).lower()[:3] in MONTHS:
                d = date(year, MONTHS[m.group(2).lower()[:3]], int(m.group(1)))
                out[code] = (d, plain(c[dc]), plain(c[fc]) if fc is not None and fc < len(c) else "")
        break
    return out


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #

def read(path):
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError:
        return ""


def build(cfg, note_chunks=None):
    """{code: SubjectInfo}. note_chunks (stem-grouped Chunk lists) adds traps and cites."""
    plan = parse_plan(read(cfg.root / "STUDY-PLAN.md"), cfg)
    graph = {}
    for code, subj in cfg.subjects.items():
        d = cfg.subject_dir(code)
        if not d.exists():
            continue
        info = SubjectInfo(code, subj.name)
        if code in plan:
            info.exam_date, info.exam_when, info.exam_format = plan[code]
        parse_syllabus(read(d / "SYLLABUS.md"), info)
        parse_guide(read(d / "notes" / "study-guide.md"), info)
        order = max([t.order for t in info.topics.values()] or [0])
        for f in sorted((d / "notes").glob("*.md")):
            t = info.topics.get(f.stem)
            if t is None:
                order += 1
                t = info.topics[f.stem] = Topic(code, f.stem, f.stem, order)
            body = read(f)
            m = re.search(r"^# (.+)$", body, re.M)
            if m:
                t.title = plain_heading(m.group(1))
            t.cites = cites(body)
            if note_chunks is not None:
                t.traps = traps(note_chunks.get((code, f.stem), []))
        if note_chunks is not None:
            for (c, stem), chunks in note_chunks.items():
                if c == code:
                    info.trap_ids.update(i for i, _ in traps(chunks))
        for deck, stems in info.deck_stems.items():
            if deck not in info.deck_tier:
                tiers = [info.topics[s].tier for s in stems if s in info.topics and info.topics[s].tier]
                if tiers:
                    info.deck_tier[deck] = min(tiers)
        for f in sorted((d / "anki").glob("*.txt")):
            if f.stem not in info.deck_stems:
                info.deck_stems[f.stem] = [f.stem] if f.stem in info.topics else []
        graph[code] = info
    return graph


def importance(cfg, topic):
    p = cfg.plan
    if topic is not None and topic.rank is not None:
        return 1 / (1 + p.get("rank_step", 0.15) * (topic.rank - 1))
    tiers = p.get("tier_importance", [0.8, 0.5, 0.3])
    if topic is not None and topic.tier:
        return tiers[min(topic.tier, len(tiers)) - 1]
    return 0.35
