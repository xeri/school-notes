"""The seven tools (plus brief and doctor), as plain functions returning compact
markdown. server.py exposes them over MCP; cli.py runs them in a terminal.
"""

import hashlib
import re
import threading
import time
from collections import Counter, defaultdict
from datetime import date, timedelta

from . import bank, carry, config, drill, ideas, links
from .config import norm_words
from .index import KIND_GROUPS, QUERY_STOP, Index
from .state import State, format_error_line, local_date, now, parse_error_line, parse_time

GRADES = {"ok": "ok", "correct": "ok", "right": "ok", "yes": "ok", "good": "ok", "easy": "ok", "pass": "ok",
          "shaky": "shaky", "hard": "shaky", "partial": "shaky", "slow": "shaky", "half": "shaky", "hint": "shaky",
          "slip": "slip", "typo": "slip", "careless": "slip",
          "miss": "miss", "wrong": "miss", "no": "miss", "again": "miss", "fail": "miss", "missed": "miss"}
CONF = {"sure": "sure", "confident": "sure", "certain": "sure",
        "guess": "guess", "?": "guess", "unsure": "guess", "maybe": "guess", "doubt": "guess"}
SCHOOL = {"paper", "scheme", "course", "spec", "school"}
MARK = {"new": "·", "missed": "✗", "shaky": "?", "warm": "+", "fading": "~", "learning": "~", "solid": "✓"}
LEVEL_NAMES = {1: "spot it", 2: "fix it", 3: "build it", 4: "explain it", 5: "from memory"}


def clip(text, n):
    text = text or ""
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def oneline(text, n=160):
    t = re.sub(r"\s*\n\s*", " ", text or "")
    t = re.sub(r"\|?\s*-{3,}\s*\|", " ", t)
    t = re.sub(r"\s{2,}", " ", t)
    return clip(t.strip(), n)


def pct(x):
    return "—" if x is None else f"{x:.0%}"


class Study:
    def __init__(self, cfg=None):
        self.cfg = cfg or config.load()
        self.ix = Index(self.cfg)
        self.state = State(self.cfg)
        self.lock = threading.Lock()
        self._idea_cache = {}
        self.bank = bank.Bank(self.cfg.bank_dir)
        self._sent = {}         # idea id -> state when its content was last sent in this chat
        self._swept = defaultdict(set)  # (code, stem or "") -> idea ids sent in that sweep in this chat
        self._shown = []        # the ideas the last brief showed (set by _fit)
        self._carried = set()   # subjects whose carryover this chat has seen
        self._bank_told = set()  # (code, stem) bank warnings already given

    # ------------------------------------------------------------ plumbing

    def ready(self):
        with self.lock:
            self.ix.refresh()
            self.state.load()
        return self

    def warm(self):
        threading.Thread(target=self.ready, daemon=True).start()

    def graph(self):
        if self.ix.graph:
            return self.ix.graph
        return links.build(self.cfg)

    def days_left(self, info, today=None):
        if not info or not info.exam_date:
            return None
        return (info.exam_date - (today or date.today())).days

    def subject_or_error(self, subject):
        code = self.cfg.resolve_subject(subject)
        if not code:
            names = ", ".join(f"{c} {s.name}" for c, s in self.cfg.subjects.items())
            return None, f"Unknown subject {subject!r}. Use one of: {names}."
        return code, None

    def deck_sizes(self):
        sizes = {}
        for code in self.cfg.subjects:
            for f in (self.cfg.subject_dir(code) / "anki").glob("*.txt"):
                try:
                    n = sum(1 for line in f.read_text(encoding="utf-8-sig").splitlines()
                            if line.strip() and not line.startswith("#"))
                except OSError:
                    n = 0
                sizes[(code, f.stem)] = n
        return sizes

    def idea_counts(self):
        """(code, stem) -> number of ideas on that notes page, from the files (no index needed)."""
        out = {}
        for code in self.cfg.subjects:
            for f in (self.cfg.subject_dir(code) / "notes").glob("*.md"):
                key = (code, f.stem)
                try:
                    st = f.stat()
                    sig = (st.st_mtime_ns, st.st_size)
                    cached = self._idea_cache.get(key)
                    if not cached or cached[0] != sig:
                        cached = (sig, ideas.count_ideas(f.read_text(encoding="utf-8-sig"), self._max_chars()))
                        self._idea_cache[key] = cached
                except OSError:
                    continue
                out[key] = cached[1]
        return out

    def target_for(self, code, today=None, graph=None):
        p = self.cfg.drill
        d = self.days_left((graph or self.graph()).get(code), today)
        win = p.get("exam_window_days", 2)
        return p.get("target_recall_exam", 0.95) if d is not None and 0 <= d <= win else p.get("target_recall", 0.9)

    def item_topic(self, item_id, graph):
        """card ECQ/markets~ab12 -> (ECQ, markets); idea ECQ/markets#x -> (ECQ, markets);
        error ERR/ECQ/.. -> (ECQ, topic)."""
        if item_id.startswith("ERR/"):
            code = item_id.split("/")[1]
            for e in self.state.errors:
                if e.id == item_id:
                    return code, e.topic
            return code, ""
        code, _, rest = item_id.partition("/")
        if "#" in rest:
            return code, rest.split("#")[0]
        deck = rest.split("~")[0]
        info = graph.get(code)
        stems = info.deck_stems.get(deck, []) if info else []
        return code, (stems[0] if stems else deck)

    def mastery(self, graph, mems, sizes, at):
        """(code, stem) -> dict(m, att, n, seen, total, recall, ideas, ideas_total, idea_m, last).

        m blends ideas (seen x recall over the page's ideas), marked attempts and cards,
        weighted by [plan] mastery_weights over whichever parts exist."""
        counts = self.idea_counts()
        w = self.cfg.plan.get("mastery_weights", {"ideas": 0.5, "attempts": 0.3, "cards": 0.2})
        scores = self.state.topic_scores()
        cards, idea_rs = defaultdict(list), defaultdict(list)
        for item_id, mem in mems.items():
            if item_id.startswith("ERR/"):
                continue
            code, _, rest = item_id.partition("/")
            if "#" in rest:
                idea_rs[(code, rest.split("#")[0])].append(drill.recall(mem, at))
            else:
                cards[(code, rest.split("~")[0])].append(drill.recall(mem, at))
        out = {}
        for code, info in graph.items():
            for stem, t in info.topics.items():
                total = sum(sizes.get((code, d), 0) for d in t.decks)
                rs = [r for d in t.decks for r in cards.get((code, d), [])]
                irs = idea_rs.get((code, stem), [])
                n_ideas = max(counts.get((code, stem), 0), len(irs))
                sc = scores.get((code, stem), {})
                parts = {"attempts": sc.get("m"),
                         "cards": sum(rs) / total if rs and total else None,
                         "ideas": sum(irs) / n_ideas if irs and n_ideas else None}
                have = {k: v for k, v in parts.items() if v is not None and w.get(k, 0) > 0}
                m = sum(w[k] * v for k, v in have.items()) / sum(w[k] for k in have) if have else None
                out[(code, stem)] = {"m": m, "att": sc.get("m"), "n": sc.get("n", 0), "seen": len(rs), "total": total,
                                     "recall": sum(rs) / len(rs) if rs else None, "ideas": len(irs),
                                     "ideas_total": n_ideas, "idea_m": parts["ideas"], "last": sc.get("last")}
        return out

    # ---------------------------------------------------------------- search

    def search(self, query, subject=None, kind="all", limit=8):
        self.ready()
        code = None
        if subject:
            code, err = self.subject_or_error(subject)
            if err:
                return err
        kinds = KIND_GROUPS.get(kind) if kind and kind != "all" else None
        limit = max(1, min(int(limit or 8), 25))
        out = []
        if kind in (None, "all", "terms"):
            for d in self.ix.definition(query):
                if not code or d["subject"] == code:
                    out.append(f"Definition ({d['id']}): {oneline(d['text'], 400)}")
        hits = self.ix.search(query, code, kinds, limit)
        if not hits and not out:
            return f"No matches for {query!r}" + (f" in {code}" if code else "") + ". Try other words or kind=all."
        for r, snip, _ in hits:
            where = r["title"] + (f" › {r['heading'].split(' › ')[-1]}" if r["heading"] and r["kind"] != "cards" else "")
            tag = r["kind"] + (" · school material, unverified" if r["kind"] in SCHOOL else "")
            out.append(f"- {r['id']} · {clip(where, 110)} · {tag}\n  {oneline(snip, 220)}")
        out.append("read(id) for the full section · topic(subject, topic) for exam links")
        return "\n".join(out)

    # ------------------------------------------------------------------ read

    def read(self, id, part=1):
        self.ready()
        cid = self._normalise_id(id)
        cap = int(self.cfg.caps.get("read", 6000))
        part = max(1, int(part or 1))
        row = self.ix.get(cid)

        if row and row["kind"] == "cards":
            e = row["extra"]
            return (f"Card {cid} · {e.get('deck')}\nQ: {e.get('q')}\nA: {e.get('a')}"
                    + (f"\nHint: {e['hint']}" if e.get("hint") else ""))
        if row and row["kind"] == "terms":
            return f"{row['text']}\n(from {row['path']}; full page: {row['subject']}/{row['stem']})"
        if row and row["kind"] in SCHOOL:
            body = f"{row['title']} · {row['heading']} · {row['kind']} · school material, unverified extraction\n" \
                   f"Source: {row['extra'].get('source', '')}\n\n{row['text']}"
            return self._page(body, cap, part, cid)

        if "#" not in cid and "~" not in cid:
            code, _, stem = cid.partition("/")
            if re.match(r"^F\d+$", stem):
                return self._school_file(code, stem)
            rows = self.ix.page(code, stem)
            if not rows:
                return self._missing(id)
            full = "\n\n".join(self._render_chunk(r) for r in rows)
            footer = self._exam_footer(code, stem)
            if len(full) <= cap:
                return self._page(full + footer, cap * 2, part, cid)
            lines = [f"{rows[0]['title']} ({cid}) — {len(full):,} chars, read a section:"]
            for r in rows:
                if r["id"].endswith("#top") or "~" in r["id"]:
                    continue
                head = r["heading"].split(" › ")[-1] if r["heading"] else ""
                lines.append(f"{'  ' * max(0, r['level'] - 2)}- {head} · {r['id']}")
            return "\n".join(lines) + footer

        rows = self.ix.section(cid)
        if not rows:
            return self._missing(id)
        body = "\n\n".join(self._render_chunk(r) for r in rows)
        first = rows[0]
        head = f"{first['title']} › {first['heading']} ({cid})\n\n" if first["heading"] else ""
        footer = self._exam_footer(first["subject"], first["stem"]) if first["kind"] == "notes" else ""
        return self._page(head + body, cap, part, cid, footer)

    def _normalise_id(self, id):
        cid = (id or "").strip().strip("`").replace("\\", "/")
        cid = re.sub(rf"^(?:{self.cfg.term}-)?([A-Z]{{3}})/(?:notes/)?", r"\1/", cid)
        cid = re.sub(r"\.md(?=$|#)", "", cid)
        m = re.match(r"^([A-Za-z]+)[/ ](.+)$", cid)
        if m and not re.match(r"^[A-Z]{3}$", m.group(1)):
            code = self.cfg.resolve_subject(m.group(1))
            if code:
                cid = f"{code}/{m.group(2)}"
        return cid

    def _render_chunk(self, r):
        head = r["heading"].split(" › ")[-1] if r["heading"] else ""
        hashes = "#" * max(2, r["level"]) if r["level"] > 1 else ""
        title = f"{hashes} {head}\n" if head and not r["id"].endswith("#top") and "~" not in r["id"].split("#")[-1] else ""
        return (title + r["text"]).strip()

    def _page(self, text, cap, part, cid, footer=""):
        parts = [text[i: i + cap] for i in range(0, len(text), cap)] or [""]
        if part > len(parts):
            return f"{cid} has only {len(parts)} part(s)."
        out = parts[part - 1]
        if len(parts) > 1:
            out += f"\n\n[part {part} of {len(parts)}" + (f"; read({cid!r}, part={part + 1}) for more]" if part < len(parts) else "]")
        if part == len(parts):
            out += footer
        return out

    def _school_file(self, code, short):
        rows = [r for r in self.ix.db.execute(
            "SELECT id, heading, text, extra FROM chunks WHERE subject=? AND stem=? ORDER BY ord", (code, short))]
        if not rows:
            return self._missing(f"{code}/{short}")
        import json
        src = json.loads(rows[0][3]).get("source", "")
        lines = [f"{code}-{short} · {len(rows)} parts · school material, unverified · Source: {src}"]
        lines += [f"- {r[0]} · {r[1]} · {oneline(r[2], 90)}" for r in rows[:60]]
        return "\n".join(lines)

    def _missing(self, id):
        words = re.sub(r"[#~/_-]+", " ", id or "")
        hits = self.ix.search(words, None, None, 5)
        alt = "\n".join(f"- {r['id']} · {clip(r['title'], 60)}" for r, _, _ in hits)
        return f"No section {id!r} (headings may have changed). Closest:\n{alt}" if alt else f"No section {id!r}."

    def _exam_footer(self, code, stem):
        info = self.ix.graph.get(code)
        t = info.topics.get(stem) if info else None
        if not t:
            return ""
        bits = []
        if t.rank is not None:
            bits.append(f"priority rank {t.rank} of {len([r for r in info.priority if r['rank']])}")
        if t.tier:
            bits.append(f"tier {t.tier}")
        days = self.days_left(info)
        if days is not None and days >= 0:
            bits.append(f"exam in {days} days ({info.exam_when})")
        lines = ["\n\n---\nExam link: " + (" · ".join(bits) if bits else "cross-cutting page")]
        if t.why:
            lines.append(f"Why it matters: {clip(t.why, 260)}")
        if t.objectives:
            lines.append("Objectives: " + "; ".join(f"{c} {clip(x, 70)}" if c else clip(x, 70) for c, x in t.objectives[:4])
                         + (f" (+{len(t.objectives) - 4} more: topic())" if len(t.objectives) > 4 else ""))
        if t.traps:
            lines.append("Traps: " + ", ".join(i for i, _ in t.traps[:4]))
        if t.decks:
            lines.append("Decks: " + ", ".join(t.decks))
        return "\n".join(lines)

    # ----------------------------------------------------------------- topic

    def topic(self, subject, topic=None):
        self.ready()
        code, rest = self.cfg.split_subject(subject or "")
        if not code and subject:
            code, _, _ = self.ix.resolve_any(subject)
            rest = subject if not topic else ""
        if not code:
            return self.subject_or_error(subject)[1]
        text = " ".join(x for x in (rest, topic or "") if x).strip()
        info = self.ix.graph[code]
        if not text:
            return self._subject_overview(code, info)
        stem, alts = self.ix.resolve_topic(code, text)
        if not stem or stem not in info.topics:
            names = ", ".join(f"{s} ({t.title})" for s, t in list(info.topics.items())[:40])
            return f"No {code} topic matches {text!r}. Topics: {names}"
        return clip(self._topic_pack(code, info, stem, alts), int(self.cfg.caps.get("topic", 8000)))

    def _subject_overview(self, code, info):
        days = self.days_left(info)
        g = self.graph()
        mems = self.state.memories()
        mast = self.mastery(g, mems, self.deck_sizes(), now())
        out = [f"# {info.name} ({code})"]
        if info.exam_date:
            out.append(f"Exam: {info.exam_when} — {days} days · {info.exam_format}")
        out.append("\n## Exam format (SYLLABUS)\n" + clip(info.syllabus_intro, 1200))
        if info.guide_exam:
            out.append("\n## From the study guide\n" + clip(info.guide_exam, 1000))
        if info.marks_text:
            out.append("\n## How marks are awarded\n" + clip(info.marks_text, 1200))
        out.append("\n## Priority order (study guide)")
        for r in info.priority:
            st = ", ".join(r["stems"]) or "—"
            out.append(f"{r['rank'] or '·'}. {clip(r['item'], 90)} → {st}")
        out.append("\n## Topics (stem · tier · mastery)")
        for stem, t in sorted(info.topics.items(), key=lambda kv: (kv[1].rank or 99, kv[1].order)):
            m = mast.get((code, stem), {})
            out.append(f"- {stem} · {t.title} · tier {t.tier or '—'} · {pct(m.get('m'))}")
        return "\n".join(out)

    def _topic_pack(self, code, info, stem, alts):
        t = info.topics[stem]
        rows = self.ix.page(code, stem, ("notes",))
        days = self.days_left(info)
        out = [f"# {t.title} ({code}/{stem}) — {info.name}"]
        if alts:
            out.append(f"(also matched: {', '.join(alts)})")
        if info.exam_date:
            out.append(f"Exam: {info.exam_when}, {days} days · {info.exam_format}")
        pr = f"rank {t.rank} of {len([r for r in info.priority if r['rank']])}" if t.rank else "not ranked"
        out.append(f"Priority: {pr} · tier {t.tier or '—'}" + (f" · {t.group}" if t.group else ""))
        if t.why:
            out.append(f"Why: {t.why}")
        if t.method:
            out.append(f"Method: {t.method}")
        if t.objectives:
            out.append(f"\n## Big picture: syllabus objectives ({len(t.objectives)})")
            out += [f"- {c} {clip(x, 160)}" if c else f"- {clip(x, 160)}" for c, x in t.objectives[:12]]
            if len(t.objectives) > 12:
                out.append(f"- (+{len(t.objectives) - 12} more)")

        g = self.ix.graph
        mems = self.state.memories()
        at = now()
        target = self.target_for(code, graph=g)
        idea_list = self._ideas(code, stem)
        out.append(f"\n## Key ideas ({len(idea_list)}) · ✓ solid · + warm · ~ learning or fading · ? shaky · ✗ missed · · new")
        for c in idea_list:
            st = self._idea_state(mems.get(c["id"]), at, target)
            lvl = mems[c["id"]].level if c["id"] in mems else 0
            out.append(f"{MARK[st]} {c['id']} · L{lvl} · {c['title']}: {ideas.gist(c['text'], 120)}")

        page_text = "\n".join(r["text"] for r in rows)
        terms = [r[0] for r in self.ix.db.execute(
            "SELECT json_extract(extra, '$.term') FROM chunks WHERE kind='terms' AND subject=? AND stem=?",
            (code, stem))]
        bold = [b for b in dict.fromkeys(re.findall(r"(?m)^\s*(?:[-*]|\d+\.)?\s*\*\*([A-Za-z][^*\n]{2,50})\*\*", page_text))
                if not b.rstrip().endswith((":", ".", "?"))]
        words = list(dict.fromkeys(terms + bold))
        figs = re.findall(r"\[figure: ([^\]]{5,140}?)(?: \([^)]*\.svg\))?\]", page_text)
        maths = [m.strip() for m in re.findall(r"\$\$(.+?)\$\$", page_text, re.S) if len(m) < 120]
        worked = [r["id"] for r in rows if re.search(r"\*\*(Worked example|Chain|Model answer|Thesis)", r["text"])]
        if words:
            out.append("\nKey words: " + "; ".join(words[:24]))
        if figs:
            out.append("Draw: " + "; ".join(clip(f, 90) for f in figs[:8]))
        if maths:
            out.append("Formulas: " + "; ".join(f"${m}$" for m in maths[:8]))
        if worked:
            out.append("Chains / worked examples: " + ", ".join(worked[:8]))
        related = [r for r, _, _ in self.ix.search(t.title, code, ("notes", "ref"), 40, grouped=False)
                   if r["id"] in info.trap_ids and r["stem"] != stem][:3]
        if t.traps or related:
            out.append("\n## Traps (good errors to plant)")
            out += [f"- {i}: {oneline(x, 220)}" for i, x in t.traps[:6]]
            out += [f"- {r['id']} (related): {oneline(r['text'], 200)}" for r in related]

        sizes = self.deck_sizes()
        m = self.mastery(g, mems, sizes, at).get((code, stem), {})
        missed = [i for i, mm in mems.items() if mm.last_grade == "miss" and self.item_topic(i, g) == (code, stem)]
        out.append("\n## You")
        out.append(f"Mastery {pct(m.get('m'))} · ideas seen {m.get('ideas', 0)}/{m.get('ideas_total', 0)} · "
                   f"cards seen {m.get('seen', 0)}/{m.get('total', 0)} · missed now {len(missed)} · "
                   f"decks {', '.join(t.decks) or '—'}")
        errs = [e for e in self.state.errors if e.subject == code and e.topic == stem][-5:]
        for e in errs:
            out.append(f"- {e.date}: {clip(e.what, 120)} → {clip(e.fix, 120)}")
        return "\n".join(out)

    # --------------------------------------------------------------- session

    def _ideas(self, code, stem):
        return ideas.ideas(self.ix.page(code, stem, ("notes",)), self._max_chars())

    def _max_chars(self):
        return int(self.cfg.session.get("idea_max_chars", ideas.MAX_CHARS))

    def _idea_of(self, code, row):
        """the idea a search hit belongs to (None for a trap section or skipped heading)."""
        for c in self._ideas(code, row["stem"]):
            if row["id"] in c["members"] or row["id"].split("~")[0] in c["members"]:
                return c
        return None

    def _idea_state(self, mem, at, target):
        if mem is None:
            return "new"
        if mem.last_grade == "miss":
            return "missed"
        if mem.last_grade == "shaky":
            return "shaky"
        if drill.recall(mem, at) < target:
            return "fading"
        if mem.level >= self.cfg.session.get("solid_level", 3):
            return "solid"
        if mem.last_level == 1 and mem.last_grade == "ok":
            return "warm"  # right in a sweep, not yet tested deeper
        return "learning"

    def _focus(self, code, text):
        """(stem, idea id or None): a topic named exactly, else a section whose heading
        carries the words (that idea), else the best-matching topic."""
        stem = self.ix.exact_topic(code, text)
        if stem:
            return stem, None
        all_words = re.findall(r"\w+", norm_words(text))
        words = [w for w in all_words if w not in QUERY_STOP]
        bold = re.compile(r"\*\*[^*\n]{0,40}\b" + r"\W+".join(map(re.escape, all_words)) + r"[^*\n]{0,30}\*\*", re.I)
        hits = [r for r, _, _ in self.ix.search(text, code, ("notes",), 10, grouped=False)
                if r["stem"] != "study-guide"]

        def idea_of(r):
            c = self._idea_of(code, r)
            return c["id"] if c else None

        for r in hits:  # the words are in a heading: that idea
            head = [w[:5] for w in re.findall(r"\w+", norm_words(r["heading"] or ""))]
            if words and sum(w[:5] in head for w in words) / len(words) >= 0.6 and idea_of(r):
                return r["stem"], idea_of(r)
        # otherwise pick the topic (a bold label such as "**2. Completing the square**", or the
        # full-text vote), then the best-matching idea inside it
        stem = next((r["stem"] for r in hits if all_words and bold.search(r["text"])), None)
        stem = stem or self.ix.resolve_topic(code, text)[0]
        for r in hits:
            if r["stem"] == stem and idea_of(r):
                return stem, idea_of(r)
        return stem, None

    def _annotate(self, cs, mems, at, target, days, today):
        p = self.cfg.memory
        caps = self.cfg.levels.get("cap_subjects", {})
        for c in cs:
            mem = mems.get(c["id"])
            c["mem"] = mem
            c["state"] = self._idea_state(mem, at, target)
            c["lvl"] = mem.level if mem else 0
            c["next"] = drill.next_level(mem, at, target, days, p, floor=2, cap=caps.get(c["subject"], 5))
            c["today"] = bool(mem and local_date(mem.last) == today and c["state"] in ("learning", "fading", "solid"))
        return cs

    def _rank_key(self, c):
        """missed, shaky, warm, fading, new, learning, then anything touched today, then solid;
        heavier exam weight first within each."""
        if c["state"] == "solid":
            r = 7
        elif c["today"]:
            r = 6
        else:
            r = {"missed": 0, "shaky": 1, "warm": 2, "fading": 3, "new": 4, "learning": 5}[c["state"]]
        return r, self._weight(c)

    def _weight(self, c):
        return {"high": 0, "medium": 1, "low": 2}.get((self.bank.entry(c) or {}).get("weight"), 1)

    def _next_topic(self, code, stem, mast, today):
        g = self.ix.graph
        mems = self.state.memories()
        for r in self._recommend(g, mems, mast, today, code, k=6):
            if r[2] != stem:
                return r[2]
        order = sorted((t.order, s) for s, t in g[code].topics.items() if s != "study-guide")
        after = [s for o, s in order if o > g[code].topics[stem].order]
        return after[0] if after else None

    def _mix_in(self, code, stem, k, mems, at, target, days, today, mast, consolidate, focus_ideas):
        """k ideas from other topics: one from a paired subject (bank links first, else the closest
        notes), the rest from neighbours in reading order and weak topics in this subject."""
        info = self.ix.graph[code]
        here = info.topics[stem].order
        p = self.cfg.plan
        pair = self._pair_idea(code, stem, focus_ideas, mems, at, today, consolidate) if k else None
        scored = []
        for s, t in info.topics.items():
            if s in (stem, "study-guide"):
                continue
            m = mast.get((code, s), {}).get("m")
            need = 1 - (m if m is not None else p.get("unknown_mastery", 0.2))
            near = 1.5 if abs(t.order - here) == 1 else 1.0
            scored.append((links.importance(self.cfg, t) * need * near, s))
        pools = []
        for _, s in sorted(scored, reverse=True)[:3]:
            cs = self._annotate(self._ideas(code, s), mems, at, target, days, today)
            cs = [c for c in cs if c["state"] != "solid" and not c["today"] and not (consolidate and c["state"] == "new")]
            pools.append(sorted(cs, key=self._rank_key))
        out = []
        while len(out) < k - (1 if pair else 0) and any(pools):
            for pool in pools:
                if pool and len(out) < k - (1 if pair else 0):
                    out.append(pool.pop(0))
        return out + ([pair] if pair else [])

    def _pair_idea(self, code, stem, focus_ideas, mems, at, today, consolidate):
        g = self.ix.graph
        pairs = []
        for pc in self.cfg.session.get("pairs", {}).get(code, []):
            d = self.days_left(g.get(pc), today)
            if pc in g and d is not None and d >= 0:
                pairs.append(pc)
        if not pairs:
            return None
        cands = []
        for c in focus_ideas:
            cands += [x for x in ((self.bank.entry(c) or {}).get("links") or []) if str(x).split("/")[0] in pairs]
        for pc in pairs:
            for r, _, _ in self.ix.search(g[code].topics[stem].title, pc, ("notes",), 5, grouped=False):
                x = self._idea_of(pc, r) if r["stem"] != "study-guide" else None
                if x:
                    cands.append(x["id"])
        for cid in dict.fromkeys(cands):
            pc, _, rest = str(cid).partition("/")
            s = rest.split("#")[0]
            if pc not in pairs or s not in g[pc].topics:
                continue
            c = next((x for x in self._ideas(pc, s) if x["id"] == cid), None)
            if not c:
                continue
            self._annotate([c], mems, at, self.target_for(pc, today, g), self.days_left(g[pc], today), today)
            if c["state"] != "solid" and not c["today"] and not (consolidate and c["state"] == "new"):
                return c
        return None

    def _bank_statements(self, c):
        e = self.bank.entry(c)
        return [s for s in (e or {}).get("statements") or [] if isinstance(s, dict) and s.get("text")]

    def _statements(self, c, n, sweep=False):
        """n bank statements for an idea, rotated by how often it has been reviewed, or None without
        a bank entry. Deepen briefs get one false and one true first; sweeps pick each slot true or
        false by a hash, so about half are false with no pattern within an idea."""
        st = self._bank_statements(c)
        if not st or n < 1:
            return None
        reps = c["mem"].reps if c.get("mem") else 0
        off = (reps * n) % len(st)
        rot = st[off:] + st[:off]
        out = []
        if sweep:
            seed = int(hashlib.sha1(f"{c['id']}|{reps}".encode("utf-8")).hexdigest()[:8], 16)
            for slot in range(min(n, len(rot))):
                want = bool((seed >> slot) & 1)
                left = [s for s in rot if s not in out]
                out.append(next((s for s in left if bool(s.get("true")) == want), left[0]))
            return out
        if n >= 2:
            out = [x for x in (next((s for s in rot if not s.get("true")), None),
                               next((s for s in rot if s.get("true")), None)) if x]
        out += [s for s in rot if s not in out]
        return out[:n]

    def _sweep_counts(self, pool):
        """statements per idea in a topic sweep: one each, then extra ones for the heaviest and
        longest ideas until the sweep reaches [session] sweep_target (at most sweep_per_idea each)."""
        S = self.cfg.session
        target, most = int(S.get("sweep_target", 15)), int(S.get("sweep_per_idea", 3))
        k = {c["id"]: 1 for c in pool}
        room = {c["id"]: min(most, len(self._bank_statements(c))) for c in pool}
        order = sorted(pool, key=lambda c: (self._weight(c), -len(c["text"])))
        total = len(pool)
        while total < target:
            grew = False
            for c in order:
                if total < target and k[c["id"]] < room[c["id"]]:
                    k[c["id"]] += 1
                    total += 1
                    grew = True
            if not grew:
                break
        return k

    @staticmethod
    def _fmt_statement(s):
        if s.get("true"):
            return f'T: "{clip(s["text"], 130)}"'
        return f'F: "{clip(s["text"], 130)}" → {clip(s.get("fix", ""), 100)}'

    def _fallback(self, c, n=None):
        n = n or int(self.cfg.session.get("fallback_excerpt", 250))
        return clip(re.sub(r"\s+", " ", c["text"]).strip(), n)

    def _show(self, i, c, code, other=False, n=None):
        """one idea in a deepen brief; ideas already sent in this chat (same state) as one line."""
        g = self.ix.graph
        lv = f"L{c['lvl']}→{c['next']}" if c["mem"] else f"new→{c['next']}"
        where = ""
        if other:
            sc = c["subject"]
            where = f" · {g[sc].topics[c['stem']].title}" + (f" ({g[sc].name})" if sc != code else "")
        head = f"{i}. {MARK[c['state']]} {c['state']} · {lv} · {c['id']}{where} · {c['title']}"
        if self._sent.get(c["id"]) == c["state"]:
            return head + " ↺"
        e = self.bank.entry(c)
        if not e:
            return head + "\n   " + (ideas.gist(c["text"], 140) if other else self._fallback(c, n))
        lines = [head, "   " + clip(str(e.get("gist", "")), 220)]
        if not other:
            lines += ["   " + self._fmt_statement(s)
                      for s in self._statements(c, int(self.cfg.session.get("statements", 2))) or []]
            if c["state"] in ("missed", "shaky"):
                extra = []
                if e.get("mixups"):
                    extra.append("mix-ups: " + "; ".join(clip(str(x), 60) for x in e["mixups"][:2]))
                if e.get("links"):
                    extra.append("links: " + ", ".join(map(str, e["links"][:3])))
                if extra:
                    lines.append("   " + " · ".join(extra))
        return "\n".join(lines)

    def _sweep_line(self, i, c, k, n=None):
        """one idea in a sweep: its id (the title too when there is no bank entry) and k statements."""
        st = self._statements(c, k, sweep=True)
        if st:
            return f"{i}. {MARK[c['state']]} {c['id']}\n" + "\n".join("   " + self._fmt_statement(s) for s in st)
        return f"{i}. {MARK[c['state']]} {c['id']} · {c['title']}\n   (no bank yet) " + self._fallback(c, n)

    def _fit(self, entries, post, cap, more="call session again for them"):
        """the brief within cap characters. entries: lines (str) or (number, idea, render(i, c, n));
        post (the bank line, footer) is always kept. Shorter fallback excerpts first, then entries
        are dropped from the end. The ideas shown are marked as sent in this chat."""
        def render(n, upto):
            return [e if isinstance(e, str) else e[2](e[0], e[1], n) for e in entries[:upto]]

        upto = len(entries)
        for n in (int(self.cfg.session.get("fallback_excerpt", 250)), 140, 80):
            body = render(n, upto)
            if len("\n".join(body + post)) <= cap:
                break
        while upto and len("\n".join(body + post)) > cap:
            upto -= 1
            while upto and isinstance(entries[upto - 1], str) and entries[upto - 1].lstrip().startswith("## "):
                upto -= 1  # no dangling section heading
            body = render(n, upto)
            dropped = sum(1 for e in entries[upto:] if not isinstance(e, str))
            if dropped:
                body.append(f"(+{dropped} more ideas: {more})")
        self._shown = [e[1] for e in entries[:upto] if not isinstance(e, str)]
        for c in self._shown:
            self._sent[c["id"]] = c["state"]
        return "\n".join(body + post)

    def _bank_line(self, code, stems):
        """'Bank: …' for topics whose bank is missing or out of date, once per topic per chat."""
        bits = []
        for s in stems:
            if (code, s) in self._bank_told:
                continue
            state, need = self.bank.status(code, s, self._ideas(code, s))
            if state in ("missing", "stale"):
                self._bank_told.add((code, s))
                bits.append(f"{code} {s}" + (f" ({len(need)} ideas changed)" if state == "stale" else ""))
        if not bits:
            return ""
        more = f" (+{len(bits) - 3} more)" if len(bits) > 3 else ""
        return ("Bank missing or out of date: " + ", ".join(bits[:3]) + more
                + ". Start the background prep (prep.md) for each; use the fallback text meanwhile.")

    def _swept_today(self, code, today):
        return any(e.get("ev") == "review" and e.get("subject") == code and e.get("level") == 1
                   and local_date(parse_time(e["t"])) == today for e in self.state.events)

    def _exam_q_this_session(self, code, at):
        """an exam question (plan it) already done for this subject in the current study session:
        back from now until a gap of session_gap_hours, as in the carryover."""
        gap = timedelta(hours=float((self.cfg.carryover or {}).get("session_gap_hours", 2)))
        start = at
        for e in reversed([e for e in self.state.events if e.get("subject") == code]):
            t = parse_time(e["t"])
            if start - t >= gap:
                break
            start = t
            if e.get("ev") == "attempt" and re.search(r"plan|exam", e.get("mode") or ""):
                return True
        return False

    def _sweep_misses(self, code, mems, at, target, days, today):
        """ideas missed or shaky in today's level-1 reviews and not yet put right."""
        ids = list(dict.fromkeys(e["item"] for e in self.state.events
                                 if e.get("ev") == "review" and e.get("subject") == code and e.get("level") == 1
                                 and e.get("grade") in ("miss", "shaky")
                                 and local_date(parse_time(e["t"])) == today))
        out = []
        for stem in dict.fromkeys(i.split("/")[1].split("#")[0] for i in ids if "/" in i):
            if stem in self.ix.graph[code].topics:
                cs = [c for c in self._ideas(code, stem) if c["id"] in ids]
                out += [c for c in self._annotate(cs, mems, at, target, days, today)
                        if c["state"] in ("missed", "shaky")]
        return sorted(out, key=self._rank_key)

    def _past_mistakes(self, code, stem=None, k=3):
        mine = [e for e in self.state.errors if e.subject == code]
        errs = [e for e in mine if stem and e.topic == stem][-k:] or mine[-k:]
        if not errs:
            return []
        return ["\n## Their past mistakes to plant"] + [f"- {clip(e.what, 100)} → {clip(e.fix, 100)}" for e in errs]

    def _carry_block(self, code, mems, at):
        """last time's carryover, on the first brief for this subject in this chat only."""
        if code in self._carried:
            return []
        self._carried.add(code)
        text = self.carryover(code, mems, at)
        return ["Last time:\n  " + text.replace("\n", "\n  ")] if text else []

    def session(self, subject=None, focus=None, today=None, sweep=False):
        """the brief for the next stretch of a study session: a sweep (fast true/false over every
        idea) or about 8 ideas to deepen, plus last time's carryover on the first call."""
        self.ready()
        g = self.ix.graph
        today = today or date.today()
        at = now()
        mems = self.state.memories()
        S = self.cfg.session
        mast = self.mastery(g, mems, self.deck_sizes(), at)
        code, rest, stem, idea_focus, why = None, "", None, None, ""
        if subject:
            code, rest = self.cfg.split_subject(subject)
            if not code:  # "/study ped": find the subject from the words
                code, stem, _ = self.ix.resolve_any(subject)
                rest = subject
                if not code:
                    return self.subject_or_error(subject)[1]
        text = " ".join(x for x in (rest, focus or "") if x).strip()
        if not code:
            recs = self._recommend(g, mems, mast, today)
            if not recs:
                return "No exams ahead. Name a subject: /study <subject>."
            code, stem, why = recs[0][1], recs[0][2], "top of your plan"
        info = g[code]
        days = self.days_left(info, today)
        target = self.target_for(code, today, g)
        consolidate = days is not None and 0 <= days <= self.cfg.plan.get("consolidate_days", 2)
        exam = (f"exam {info.exam_when}, {days} days" if days is not None and days >= 0 else "no exam ahead")

        if not text and (sweep or (days is not None and 0 <= days <= 1 and not self._swept_today(code, local_date(at)))):
            reason = "you asked" if sweep else ("exam today" if days == 0 else "exam tomorrow")
            return self._subject_sweep(code, info, mems, at, target, days, today, consolidate,
                                       [f"# Sweep · {info.name} · whole subject", f"{exam} · why: {reason}"],
                                       self._carry_block(code, mems, at))
        if not text and days is not None and 0 <= days <= 1:  # swept today: deepen only its misses
            misses = self._sweep_misses(code, mems, at, target, days, local_date(at))
            if misses:
                return self._misses_brief(code, info, misses, exam, self._carry_block(code, mems, at))

        if not why:
            if text:
                stem, idea_focus = self._focus(code, text)
                why = f"you asked for {text!r}"
            else:
                last, _ = self.state.last_topic(code)
                if last in info.topics and last != "study-guide":
                    stem, why = last, "carrying on from last time"
                else:
                    recs = self._recommend(g, mems, mast, today, code, k=1)
                    stem = recs[0][2] if recs else min(
                        (s for s in info.topics if s != "study-guide"),
                        key=lambda s: (info.topics[s].rank or 99, info.topics[s].order), default=None)
                    why = "highest priority for you now"
        if not stem or stem not in info.topics:
            names = ", ".join(s for s in info.topics if s != "study-guide")
            return f"No {code} topic matches {text!r}. Topics: {names}"

        focus_ideas = self._annotate(self._ideas(code, stem), mems, at, target, days, today)
        solid = bool(focus_ideas) and all(c["state"] == "solid" for c in focus_ideas)
        notes = []
        if solid and not text:
            nxt = self._next_topic(code, stem, mast, today)
            if nxt:
                why = f"{info.topics[stem].title} is solid, moving on"
                if not self._exam_q_this_session(code, at):
                    why += f" (an exam question on {info.topics[stem].title} is allowed first: plan it)"
                stem = nxt
                focus_ideas = self._annotate(self._ideas(code, stem), mems, at, target, days, today)
                solid = bool(focus_ideas) and all(c["state"] == "solid" for c in focus_ideas)
        t = info.topics[stem]
        seen = [c for c in focus_ideas if c["mem"]]

        reason = ""
        if sweep:
            reason = "you asked"
        elif not seen and not consolidate:
            reason = "new topic"
        elif seen:
            idle = (at - max(c["mem"].last for c in seen)).days
            if idle >= int(S.get("sweep_after_days", 5)):
                reason = f"untouched {idle} days"
        if reason:
            pool = [c for c in focus_ideas if c["mem"] or not consolidate]
            if pool:
                return self._topic_sweep(code, info, stem, pool, reason, why, exam, consolidate,
                                         self._carry_block(code, mems, at))

        head = [f"# Session · {info.name} · {t.title} ({code}/{stem})", f"{exam} · why here: {why}"]
        counts = Counter(c["state"] for c in focus_ideas)
        status = f"{len(seen)}/{len(focus_ideas)} ideas seen · " + ", ".join(f"{v} {k}" for k, v in counts.most_common())
        if seen:
            status += f" · average level {sum(c['lvl'] for c in seen) / len(seen):.1f}"
        body = [status]
        if consolidate:
            body.append(f"Exam in {days} days: no new ideas. Work the seen ones at level 3 and up.")
        elif days is not None and 0 <= days <= self.cfg.levels.get("exam_floor_days", 3):
            body.append("Exam close: seen ideas start at level 3 (less support).")
        cap = self.cfg.levels.get("cap_subjects", {}).get(code)
        if cap:
            body.append(f"{info.name}: level {cap} at most (recognition and formulas) unless they push for more.")
        if solid:
            nxt = self._next_topic(code, stem, mast, today)
            gate = "" if self._exam_q_this_session(code, at) else "An exam question is allowed (plan it). "
            body.append(f"This topic is solid. {gate}Mix it into questions on {nxt or 'other topics'} and move on.")

        pos = {c["id"]: i for i, c in enumerate(focus_ideas)}
        near = set()
        if idea_focus in pos:
            i = pos[idea_focus]
            near = {c["id"] for c in focus_ideas[max(0, i - 1): i + 2]}
        pool = [c for c in focus_ideas if not (consolidate and c["state"] == "new")]
        pool.sort(key=lambda c: (c["id"] != idea_focus, c["id"] not in near, self._rank_key(c), pos[c["id"]]))
        n, k = int(S.get("candidates", 8)), int(S.get("interleave", 3))
        if consolidate:  # near the exam: mixed questions across everything seen
            k = max(k, n // 2)
        mixed = self._mix_in(code, stem, k, mems, at, target, days, today, mast, consolidate, focus_ideas) if k else []
        main = pool[: n - len(mixed)]

        show = lambda i, c, n: self._show(i, c, code, False, n)
        show_other = lambda i, c, n: self._show(i, c, code, True, n)
        entries = body + ["\n## Ideas (state · level now→next · id · title)"]
        entries += [(i, c, show) for i, c in enumerate(main, 1)]
        if mixed:
            entries.append("\n## Mix in")
            entries += [(i, c, show_other) for i, c in enumerate(mixed, len(main) + 1)]
        if not main and not mixed:
            entries.append("Nothing left to work on here. Try another topic in this subject.")

        traps = [x for _, x in t.traps[:3]]
        if len(traps) < 2:  # e.g. Economics keeps its traps in DIAGRAMS
            traps += [r["text"] for r, _, _ in self.ix.search(t.title, code, ("notes", "ref"), 30, grouped=False)
                      if r["id"] in info.trap_ids and r["stem"] != stem][: 3 - len(traps)]
        if traps:
            entries.append("\n## Traps to plant")
            entries += [f"- {oneline(x, 150)}" for x in traps]
        entries += self._past_mistakes(code, stem)
        post = [x for x in (self._bank_line(code, [stem]), "↺ = sent earlier in this chat. read(id) for level 3+.") if x]
        brief = self._fit(entries, post, int(self.cfg.caps.get("session", 3000)))
        return "\n".join(head + self._carry_block(code, mems, at) + [brief])

    def _misses_brief(self, code, info, misses, exam, carry_block):
        n = int(self.cfg.session.get("candidates", 8))
        head = [f"# Session · {info.name} · misses from today's sweep", f"{exam} · why: deepen only the misses"]
        entries = [f"{len(misses)} ideas missed or shaky in today's sweep. Work each at level 3 and up; "
                   "no new ideas.", "\n## Ideas (state · level now→next · id · title)"]
        entries += [(i, c, lambda i, c, k: self._show(i, c, code, False, k)) for i, c in enumerate(misses[:n], 1)]
        post = ["↺ = sent earlier in this chat. read(id) for level 3+."]
        return "\n".join(head + carry_block + [self._fit(entries, post, int(self.cfg.caps.get("session", 3000)))])

    SWEEP_RULES = ("5 statements per message, answered like `T F left T T? F ear`: after each F, the word or two "
                   "that makes it true; ? = a guess. Reply ✓ or a one-line fix per miss, then the next 5. "
                   "Log each message at level 1: one review per idea, its worst statement's grade.")

    def _unswept(self, key, pool, limit=None):
        """the part of a sweep not yet sent in this chat (a fresh sweep once it has all been sent).
        With limit, the sweep is that many ideas in all."""
        sent = self._swept[key]
        rest = [c for c in pool if c["id"] not in sent]
        if not rest or (limit and len(sent) >= limit):
            sent.clear()
            rest = list(pool)
        return rest[: limit - len(sent)] if limit else rest, bool(sent)

    def _topic_sweep(self, code, info, stem, pool, reason, why, exam, consolidate, carry_block):
        t = info.topics[stem]
        key = (code, stem)
        pool, cont = self._unswept(key, pool)
        most = int(self.cfg.session.get("sweep_max", 25))
        if len(pool) > most:  # e.g. 50 allusions: the weakest and weightiest first, kept in page order
            pos = {c["id"]: i for i, c in enumerate(pool)}
            pool = sorted(sorted(pool, key=self._rank_key)[:most], key=lambda c: pos[c["id"]])
        k = self._sweep_counts(pool)
        head = [f"# Sweep · {info.name} · {t.title} ({code}/{stem})" + (" · continued" if cont else ""),
                f"{exam} · why: {reason} · {why}"]
        entries = [f"{sum(k.values())} statements on {len(pool)} ideas. {self.SWEEP_RULES} "
                   "Misses wait for the deepen pass."]
        if reason == "new topic" and not cont:
            entries.append("New topic: after the sweep, 1–2 level-3 items to find the edge.")
        if consolidate:
            entries.append("Exam close: seen ideas only.")
        entries.append("\n## Statements (state · id)")
        line = lambda i, c, n: self._sweep_line(i, c, k[c["id"]], n)
        entries += [(i, c, line) for i, c in enumerate(pool, 1)]
        entries += self._past_mistakes(code, stem, 2)
        post = [x for x in (self._bank_line(code, [stem]),) if x]
        out = self._fit(entries, post, int(self.cfg.caps.get("sweep", 4500)),
                        f"session({code!r}, {stem!r}, sweep=true) for the rest of this sweep")
        self._swept[key].update(c["id"] for c in self._shown)
        return "\n".join(head + carry_block + [out])

    def _subject_sweep(self, code, info, mems, at, target, days, today, consolidate, head, carry_block):
        buckets = []
        for s, t in sorted(info.topics.items(), key=lambda kv: -links.importance(self.cfg, kv[1])):
            if s == "study-guide":
                continue
            cs = self._annotate(self._ideas(code, s), mems, at, target, days, today)
            if consolidate:
                cs = [c for c in cs if c["mem"]]
            cs.sort(key=lambda c: (self._weight(c), drill.recall(c["mem"], at) if c["mem"] else 0.0))
            if cs:
                buckets.append(cs)
        ranked = []
        while any(buckets):
            for b in buckets:
                if b:
                    ranked.append(b.pop(0))
        key = (code, "")
        limit = int(self.cfg.session.get("sweep_max", 25))
        picked, cont = self._unswept(key, ranked, limit)
        if cont:
            head = [head[0] + " · continued"] + head[1:]
        entries = [f"{len(picked)} statements across the subject, weightiest and most faded first. {self.SWEEP_RULES} "
                   "Then deepen only the misses (call session again)."]
        if consolidate:
            entries.append("Exam close: seen ideas only, nothing new.")
        entries.append("\n## Statements (state · id)")
        line = lambda i, c, n: self._sweep_line(i, c, 1, min(n, 160))
        entries += [(i, c, line) for i, c in enumerate(picked, 1)]
        if not picked:
            entries.append("Nothing seen yet to sweep in this subject.")
        stems = list(dict.fromkeys(c["stem"] for c in picked))
        post = [x for x in (self._bank_line(code, stems),) if x]
        out = self._fit(entries, post, int(self.cfg.caps.get("sweep", 4500)),
                        f"session({code!r}, sweep=true) for the rest of this sweep")
        self._swept[key].update(c["id"] for c in self._shown)
        return "\n".join(head + carry_block + [out])

    # ------------------------------------------------------------------ bank

    def _known_idea(self, cid):
        code, _, rest = str(cid).partition("/")
        stem = rest.split("#")[0]
        info = self.ix.graph.get(code)
        return bool(info and "#" in rest and stem in info.topics
                    and any(c["id"] == cid for c in self._ideas(code, stem)))

    def _bank_topic(self, subject, topic):
        code, err = self.subject_or_error(subject)
        if err:
            return None, None, err
        info = self.ix.graph[code]
        stem = topic if topic in info.topics else self.ix.resolve_topic(code, topic or "")[0]
        if not stem or stem not in info.topics:
            names = ", ".join(s for s in info.topics if s != "study-guide")
            return code, None, f"No {code} topic {topic!r}. Topics: {names}"
        return code, stem, None

    def _link_candidates(self, c, k=4):
        g = self.ix.graph
        code = c["subject"]
        out = []
        q = f"{c['title']} {ideas.gist(c['text'], 80)}"
        for sc in [code] + [p for p in self.cfg.session.get("pairs", {}).get(code, []) if p in g]:
            for r, _, _ in self.ix.search(q, sc, ("notes",), 6, grouped=False):
                if r["stem"] in ("study-guide", c["stem"]):
                    continue
                x = self._idea_of(sc, r)
                if x and x["id"] not in [o["id"] for o in out]:
                    out.append(x)
        return out[:k]

    def prep(self, subject, topic, thin=False):
        """the input for building one topic's bank entry (prep.md). thin: also rebuild built ideas
        with fewer statements than their notes deserve."""
        self.ready()
        code, stem, err = self._bank_topic(subject, topic)
        if err:
            return err
        info = self.ix.graph[code]
        t = info.topics[stem]
        cs = self._ideas(code, stem)
        state, need = self.bank.status(code, stem, cs)
        if thin:
            need = list(dict.fromkeys(need + self.bank.thin(cs)))
        todo = [c for c in cs if c["id"] in need] or cs
        rel = lambda p: p.relative_to(self.cfg.root).as_posix() if p.is_relative_to(self.cfg.root) else str(p)
        out = [f"# Prep · {info.name} · {t.title} ({code}/{stem})",
               f"Write the draft to: {rel(self.bank.draft_path(code, stem))}",
               f"Then run: uv run --quiet --frozen --project tools/studymcp studymcp bank --save {code} {stem}",
               (f"Build all {len(cs)} ideas." if len(todo) == len(cs) else
                f"Partial rebuild: only the {len(todo)} ideas below; the other {len(cs) - len(todo)} are kept.")]
        if t.why:
            out.append(f"Why it matters: {t.why}")
        pr = f"rank {t.rank}" if t.rank else "not ranked"
        out.append(f"Priority: {pr} · tier {t.tier or '—'}")
        none = "- (none for this topic: judge from the notes and the priority above)"
        out.append(f"\n## Syllabus objectives ({len(t.objectives)})")
        out += [f"- {c} {x}" if c else f"- {x}" for c, x in t.objectives] or [none]
        related = [r for r, _, _ in self.ix.search(t.title, code, ("notes", "ref"), 40, grouped=False)
                   if r["id"] in info.trap_ids and r["stem"] != stem][:3]
        out.append("\n## Traps")
        out += [f"- {i}: {oneline(x, 400)}" for i, x in t.traps]
        out += [f"- {r['id']} (related): {oneline(r['text'], 300)}" for r in related]
        if not t.traps and not related:
            out.append("- (none for this topic: use the common mistakes the notes warn about)")
        papers = self.ix.search(t.title, code, KIND_GROUPS["papers"], 8, grouped=False)
        out.append("\n## Past-paper and mark-scheme hits (for weight; unverified text extraction)")
        out += [f"- {r['id']}: {oneline(r['text'], 220)}" for r, _, _ in papers] or [none]
        out.append(f"\n## Ideas to build ({len(todo)})")
        for c in todo:
            cands = self._link_candidates(c)
            out.append(f"\n### {c['id']} · {c['title']}")
            out.append(f"Statements: {bank.recommended(c['text'])} or more")
            if cands:
                out.append("Possible links: " + "; ".join(f"{x['id']} ({x['title']})" for x in cands))
            out.append(c["text"].strip())
        return "\n".join(out)

    def bank_status(self, subject=None, show_flags=False):
        self.ready()
        codes = list(self.ix.graph)
        if subject:
            code, err = self.subject_or_error(subject)
            if err:
                return err
            codes = [code]
        out, tally = [], Counter()
        for code in codes:
            info = self.ix.graph[code]
            for stem in info.topics:
                if stem == "study-guide":
                    continue
                cs = self._ideas(code, stem)
                state, need = self.bank.status(code, stem, cs)
                tally[state] += 1
                fl = self.bank.flags(code, stem)
                th = self.bank.thin(cs)
                line = f"{code} {stem}: {state}" + (f" ({len(need)}/{len(cs)} ideas)" if state == "stale" else "")
                out.append(line + (f" · {len(th)} thin" if th else "") + (f" · {len(fl)} flags" if fl else ""))
                if show_flags:
                    out += [f"    - {f}" for f in fl]
        head = "Bank " + " · ".join(f"{v} {k}" for k, v in tally.most_common()) + f" ({self.cfg.bank_dir})"
        return "\n".join([head] + out)

    def bank_save(self, subject, topic):
        self.ready()
        code, stem, err = self._bank_topic(subject, topic)
        if err:
            return err
        cs = self._ideas(code, stem)
        ok, errors, warnings = self.bank.save(code, stem, cs, self._known_idea)
        if not ok:
            return "not saved:\n" + "\n".join(f"- {e}" for e in errors + [f"(warning) {w}" for w in warnings])
        data = self.bank.load(code, stem) or {}
        out = [f"saved {code}/{stem}: {len(data.get('ideas') or {})} ideas, {len(data.get('flags') or [])} flags"]
        return "\n".join(out + [f"- (warning) {w}" for w in warnings])

    # ----------------------------------------------------------------- drill

    def drill(self, subject=None, topic=None, n=10, focus="auto"):
        self.ready()
        g = self.ix.graph
        today = date.today()
        code = None
        if subject:
            code, rest = self.cfg.split_subject(subject)
            if not code:
                return self.subject_or_error(subject)[1]
            topic = " ".join(x for x in (rest, topic or "") if x).strip() or None
        stem = None
        if code and topic:
            stem, _ = self.ix.resolve_topic(code, topic)
        codes = [code] if code else [c for c, i in g.items() if (self.days_left(i, today) or 0) >= 0]

        items = []
        for c in codes:
            info = g[c]
            decks = None
            if stem:
                decks = [d for d, ss in info.deck_stems.items() if stem in ss] or info.topics[stem].decks
            for r in self.ix.cards(c, decks):
                e = r["extra"]
                ss = info.deck_stems.get(r["stem"], [])
                items.append({"id": r["id"], "subject": c, "topic": ss[0] if ss else r["stem"],
                              "q": e["q"], "a": e["a"], "hint": e.get("hint", ""), "order": r["ord"],
                              "tier": info.deck_tier.get(r["stem"])})
            for e in self.state.errors:
                if e.subject == c and (not stem or e.topic == stem):
                    items.append({"id": e.id, "subject": c, "topic": e.topic, "order": 0, "tier": None,
                                  "q": e.what,
                                  "a": e.fix or "(no fix recorded)", "hint": e.type})
        if not items:
            return "Nothing to drill" + (f" for {code} {topic or ''}" if code else "") + "."

        mems = self.state.memories()
        at = now()
        p = self.cfg.drill
        win = p.get("exam_window_days", 2)

        def target_for(c):
            d = self.days_left(g.get(c), today)
            return p.get("target_recall_exam", 0.95) if d is not None and 0 <= d <= win else p.get("target_recall", 0.9)

        def importance(it):
            info = g.get(it["subject"])
            tp = info.topics.get(it["topic"]) if info else None
            imp = links.importance(self.cfg, tp)
            if not code:
                d = self.days_left(info, today)
                k = self.cfg.plan.get("urgency_days", 7)
                imp *= k / (k + max(d, 0)) if d is not None else 0.3
                imp *= self.cfg.subjects[it["subject"]].weight
            return imp

        n = max(1, min(int(n or 10), 30))
        picked = drill.select(items, mems, at, n, focus or "auto", importance, target_for, p)
        if not picked:
            return "Nothing missed or fading right now. Try focus='new', or a session."
        kinds = Counter(re.match(r"[a-z]+", why).group() for _, why in picked)
        scope = (g[code].name if code else "all subjects with exams ahead") + (f" · {stem}" if stem else "")
        out = [f"Quick-fire · {scope} · {len(picked)} items ({', '.join(f'{v} {k}' for k, v in kinds.items())})"]
        for i, (it, why) in enumerate(picked, 1):
            lvl, form = self._card_form(it, mems.get(it["id"]), at, target_for(it["subject"]), today)
            q = f"Your old answer ({it['topic']}): {it['q']}. Fix it." if it["id"].startswith("ERR/") else it["q"]
            out.append(f"{i}. {it['id']} [{why} · L{lvl} {form}]\n   Q: {q}\n   A: {it['a']}"
                       + (f"\n   Hint: {it['hint']}" if it["hint"] else ""))
        out.append("Forms: true/false = state the answer correct or subtly changed, they say which and type the fix; "
                   "multiple choice = 4 options, distractors from close mix-ups; fix = show a version with one planted "
                   "error to correct; recall = ask Q as written. Batch quick ones. "
                   "log(reviews=[{id, grade, level}]) every few answers.")
        return "\n".join(out)

    def _card_form(self, it, mem, at, target, today):
        """(level, form) for a quick-fire item: 1 true/false (some multiple choice), 2 fix, 3+ recall."""
        days = self.days_left(self.ix.graph.get(it["subject"]), today)
        lvl = drill.next_level(mem, at, target, days, self.cfg.memory)
        if it["id"].startswith("ERR/"):
            return max(lvl, 2), "fix" if lvl < 3 else "recall"
        if lvl >= 3:
            return lvl, "recall"
        if lvl == 2:
            return lvl, "fix"
        L = self.cfg.levels
        share = L.get("mcq_share_subjects", {}).get(it["subject"], L.get("mcq_share", 0.15))
        roll = int(hashlib.sha1(it["id"].encode("utf-8")).hexdigest()[:4], 16) / 0xFFFF
        return 1, "multiple choice" if roll < share else "true/false"

    # ------------------------------------------------------------------- log

    def log(self, subject, topic="", mode="session", score=None, out_of=None, errors=None, reviews=None,
            note=None):
        self.ready()
        code, err = self.subject_or_error(subject)
        if err:
            return err
        g = self.ix.graph
        stem = ""
        if topic:
            stem, _ = self.ix.resolve_topic(code, topic)
            stem = stem or topic
        at = now()
        t = at.isoformat(timespec="seconds")
        mode = re.sub(r"\s+", " ", str(mode or "session")).strip().lower()[:40]
        mems_before = self.state.memories()
        events, lines, msgs, warn = [], [], [], []

        if score is not None and out_of:
            events.append({"t": t, "ev": "attempt", "subject": code, "topic": stem, "mode": mode,
                           "score": float(score), "out_of": float(out_of)})
            msgs.append(f"attempt {score:g}/{out_of:g}")

        by_topic, levels = defaultdict(list), defaultdict(list)
        for r in reviews or []:
            item = str(r.get("id", "")).strip()
            grade = GRADES.get(str(r.get("grade", "")).lower().strip())
            if not item or not grade:
                warn.append(f"skipped {item or 'a review'} (grade {r.get('grade')!r})")
                continue
            c, tp = self.item_topic(item, g)
            if c not in g or ("#" in item and tp not in g[c].topics):
                warn.append(f"unknown id {item}")
                continue
            ev = {"t": t, "ev": "review", "subject": c, "topic": tp, "item": item, "grade": grade}
            try:
                lvl = int(r.get("level") or 0)
            except (TypeError, ValueError):
                lvl = 0
            if 1 <= lvl <= 5:
                ev["level"] = lvl
                levels[(c, tp)].append(lvl)
            conf = CONF.get(str(r.get("conf", "") or "").lower().strip())
            if conf:
                ev["conf"] = conf
            events.append(ev)
            by_topic[(c, tp)].append(grade)
        for (c, tp), grades in by_topic.items():
            if score is None:
                ok = sum(1.0 if x == "ok" else 0.75 if x == "slip" else 0.5 if x == "shaky" else 0 for x in grades)
                ev = {"t": t, "ev": "attempt", "subject": c, "topic": tp, "mode": mode,
                      "score": ok, "out_of": float(len(grades))}
                if levels.get((c, tp)):
                    ev["level"] = max(levels[(c, tp)])
                events.append(ev)
        if by_topic:
            gc = Counter(x for gs in by_topic.values() for x in gs)
            msgs.insert(0, f"{sum(gc.values())} ({', '.join(f'{v} {k}' for k, v in gc.items())})")

        day = local_date(at).isoformat()
        for e in errors or []:
            what = str(e.get("what", "")).strip()
            if not what:
                continue
            src = str(e.get("source", "") or "").strip()
            src_topic = self.item_topic(src, g)[1] if src.startswith(code + "/") else ""
            line = format_error_line(day, stem or e.get("topic", "") or src_topic or "general", what,
                                     e.get("fix", ""), e.get("type", ""), src)
            parsed = parse_error_line(code, line)
            lines.append(line)
            events.append({"t": t, "ev": "error", "subject": code, "topic": parsed.topic, "item": parsed.id})
        if lines:
            msgs.append(f"{len(lines)} error{'s' if len(lines) > 1 else ''}")
        note = re.sub(r"\s+", " ", str(note or "")).strip()
        if note:
            events.append({"t": t, "ev": "note", "subject": code, "text": note[:80]})
            msgs.append("note")

        if not events:
            return "Nothing logged: give reviews, errors, a note, or score and out_of." + (
                " " + "; ".join(warn) if warn else "")
        with self.lock:
            if lines:
                self.state.append_errors(code, lines)
            self.state.append(events)
            self.state.load()
        mems = self.state.memories()
        out = ["Logged " + ", ".join(msgs)]
        for item in dict.fromkeys(str(r.get("id", "")).strip() for r in reviews or []):
            if item in mems and "#" in item:
                old = mems_before[item].level if item in mems_before else 0
                if mems[item].level != old:
                    out.append(f"{item} L{old}→{mems[item].level}")
        leech = self.cfg.drill.get("leech_lapses", 3)
        flagged = [i for i in dict.fromkeys(str(r.get("id", "")) for r in reviews or [])
                   if i in mems and mems[i].lapses >= leech]
        if flagged:
            out.append(f"leech (missed {leech}+ times: explain it, maybe an Anki card): {', '.join(flagged)}")
        out += warn
        for c in sorted({code} | {c for c, _ in by_topic}):
            self._write_carryover(c, mems)
        return " · ".join(out)

    def carryover(self, code, mems=None, at=None):
        """the rolling note for one subject (see carry.py)."""
        g = self.ix.graph
        info = g.get(code)
        cache = {}

        def clusters(stem):
            if stem not in cache:
                cache[stem] = self._ideas(code, stem) if info and stem in info.topics else []
            return cache[stem]

        def title(item):
            stem = item.partition("/")[2].split("#")[0]
            return next((c["title"] for c in clusters(stem) if c["id"] == item),
                        item.split("#")[-1].replace("-", " "))

        def topic_title(stem):
            return info.topics[stem].title if info and stem in info.topics else (stem or "general")

        return carry.build(code, self.cfg.subjects[code].name, self.state.events, self.state.errors,
                           mems if mems is not None else self.state.memories(), title, topic_title,
                           lambda s: [c["id"] for c in clusters(s)], at or now(), self.cfg.carryover,
                           self.cfg.session.get("sweep_after_days", 5))

    def _write_carryover(self, code, mems=None):
        text = self.carryover(code, mems)
        if text:
            carry.write(self.cfg.progress_dir / "carryover", code, text)
        return text

    # ------------------------------------------------------------------ plan

    def _levels_by_topic(self, g, mems, at, today):
        """(code, stem) -> [next level of each seen idea]."""
        out = defaultdict(list)
        days = {c: self.days_left(i, today) for c, i in g.items()}
        targets = {c: self.target_for(c, today, g) for c in g}
        for item, mem in mems.items():
            code, _, rest = item.partition("/")
            if "#" not in rest or code not in g:
                continue
            out[(code, rest.split("#")[0])].append(
                drill.next_level(mem, at, targets[code], days[code], self.cfg.memory))
        return out

    def _recommend(self, g, mems, mast, today, subject=None, k=3):
        p = self.cfg.plan
        recs = []
        lv = self._levels_by_topic(g, mems, now(), today)
        for code, info in g.items():
            if subject and code != subject:
                continue
            days = self.days_left(info, today)
            if days is not None and days < 0:
                continue
            urg = p.get("urgency_days", 7) / (p.get("urgency_days", 7) + max(days, 0)) if days is not None else 0.3
            consolidate = days is not None and days <= p.get("consolidate_days", 2)
            for stem, t in info.topics.items():
                if stem == "study-guide" or (t.rank is None and t.tier is None):
                    continue
                m = mast.get((code, stem), {})
                if consolidate and m.get("m") is None:
                    continue
                mm = m.get("m") if m.get("m") is not None else p.get("unknown_mastery", 0.2)
                errs = len(self.state.recent_errors(code, stem, 7))
                need = min(1.0, 1 - mm + min(p.get("error_bump_max", 0.3), p.get("error_bump", 0.1) * errs))
                last = m.get("last")
                rec = p.get("practised_today", 0.5) if last and local_date(last) == today else 1.0
                imp = links.importance(self.cfg, t)
                w = self.cfg.subjects[code].weight
                score = urg * imp * need * rec * w
                why = [f"exam in {days} d" if days is not None else "no exam date",
                       f"rank {t.rank}" if t.rank else f"tier {t.tier}",
                       f"mastery {pct(m.get('m'))}" if m.get("m") is not None else "not practised yet"]
                if errs:
                    why.append(f"{errs} recent error(s)")
                if rec < 1:
                    why.append("done today")
                if consolidate:
                    why.append("consolidate only")
                seen = lv.get((code, stem))
                if consolidate:
                    mode = "seen ideas only, level 3+"
                elif not seen:
                    mode = "new: quick probe"
                else:
                    n = round(sum(seen) / len(seen))
                    mode = f"around level {n} ({LEVEL_NAMES[n]})"
                recs.append((score, code, stem, t, why, mode, info))
        recs.sort(key=lambda x: -x[0])
        out, per = [], Counter()
        for r in recs:
            if per[r[1]] >= 2 and not subject:
                continue
            per[r[1]] += 1
            out.append(r)
            if len(out) >= k:
                break
        return out

    def plan(self, subject=None):
        self.ready()
        code = None
        if subject:
            code, err = self.subject_or_error(subject)
            if err:
                return err
        g = self.ix.graph
        today = date.today()
        at = now()
        mems = self.state.memories()
        sizes = self.deck_sizes()
        mast = self.mastery(g, mems, sizes, at)
        out = ["## Countdown"]
        for c, info in sorted(g.items(), key=lambda kv: kv[1].exam_date or date.max):
            d = self.days_left(info, today)
            if d is not None and d >= 0 and (not code or c == code):
                out.append(f"- {info.name}: {info.exam_when} — {d} days")
        recs = self._recommend(g, mems, mast, today, code)
        out.append("\n## Do next")
        for i, (score, c, stem, t, why, mode, info) in enumerate(recs, 1):
            out.append(f"{i}. {info.name} · {t.title} ({c}/{stem}) — {', '.join(why)}. Start: {mode}")

        due = Counter()
        for i, m in mems.items():
            c = self.item_topic(i, g)[0]
            if code and c != code:
                continue
            kind = "ideas" if "#" in i else "mistakes" if i.startswith("ERR/") else "cards"
            if m.last_grade == "miss":
                due[(kind, "missed")] += 1
            elif drill.recall(m, at) < self.cfg.drill.get("target_recall", 0.9):
                due[(kind, "fading")] += 1
        total = sum(v for (c, _), v in sizes.items() if not code or c == code)
        n_cards = sum(1 for i in mems if "#" not in i and not i.startswith("ERR/"))
        out.append("\n## Due to come back\n" + " · ".join(
            f"{kind}: {due[(kind, 'missed')]} missed, {due[(kind, 'fading')]} fading" for kind in ("ideas", "mistakes", "cards"))
            + f" · {max(total - n_cards, 0):,} cards never seen")

        out.append("\n## Mastery")
        if code:
            info = g[code]
            for stem, t in sorted(info.topics.items(), key=lambda kv: (kv[1].rank or 99, kv[1].order)):
                if stem == "study-guide":
                    continue
                m = mast.get((code, stem), {})
                out.append(f"- {stem}: {pct(m.get('m'))} · ideas {m.get('ideas', 0)}/{m.get('ideas_total', 0)} · "
                           f"cards {m.get('seen', 0)}/{m.get('total', 0)}")
        else:
            for c, info in g.items():
                vals = [mast[(c, s)]["m"] for s in info.topics if mast.get((c, s), {}).get("m") is not None]
                started = len(vals)
                avg = sum(vals) / started if started else None
                out.append(f"- {info.name}: {started}/{len(info.topics)} topics started · avg {pct(avg)}")

        errs = [e for e in self.state.errors if not code or e.subject == code]
        if errs:
            types = Counter((e.subject, e.type or "untyped") for e in errs)
            out.append("\n## Error types\n" + "; ".join(f"{c} {t} ×{n}" for (c, t), n in types.most_common(8)))
        leech = self.cfg.drill.get("leech_lapses", 3)
        leeches = [i for i, m in mems.items() if m.lapses >= leech and (not code or self.item_topic(i, g)[0] == code)]
        if leeches:
            out.append(f"\n## Leeches (missed {leech}+ times)\n" + ", ".join(leeches[:12]))
        out.append(f"\n(index: {sum(self.ix.counts().values()):,} chunks, built in {self.ix.build_seconds:.1f}s)")
        return "\n".join(out)

    # ----------------------------------------------------------------- brief

    def brief(self):
        """3 lines for the session start. Skips the full-text index (fast)."""
        self.state.load()
        g = links.build(self.cfg)
        today = date.today()
        at = now()
        mems = self.state.memories()
        mast = self.mastery(g, mems, self.deck_sizes(), at)
        ahead = sorted(((self.days_left(i, today), i) for i in g.values()
                        if i.exam_date and self.days_left(i, today) >= 0), key=lambda x: x[0])
        line1 = "Exams: " + ", ".join(f"{i.name} {d}d" for d, i in ahead[:4]) if ahead else "No exams ahead."
        recs = self._recommend(g, mems, mast, today)
        line2 = "Top now: " + "; ".join(f"{i + 1}) {r[6].name} {r[3].title} [{r[5]}]" for i, r in enumerate(recs))
        missed = sum(1 for m in mems.values() if m.last_grade == "miss")
        fading = sum(1 for m in mems.values() if m.last_grade != "miss" and drill.recall(m, at) < self.cfg.drill.get("target_recall", 0.9))
        line3 = f"Coming back: {missed} missed, {fading} fading. Start: /study or /study <subject>"
        return "\n".join([line1, line2, line3])

    # ---------------------------------------------------------------- doctor

    def doctor(self):
        t0 = time.perf_counter()
        self.ready()
        out = [f"root {self.cfg.root}", f"index built in {self.ix.build_seconds:.2f}s (call {time.perf_counter() - t0:.2f}s)",
               "chunks: " + ", ".join(f"{k} {v}" for k, v in sorted(self.ix.counts().items())),
               f"acronyms {len(self.ix.acronyms)} · glossary terms {sum(len(v) for v in self.ix.terms.values())}"]
        problems = []
        for code, info in self.ix.graph.items():
            d = self.cfg.subject_dir(code)
            missing = [s for s in info.topics if not (d / "notes" / f"{s}.md").exists()]
            decks = [x for x in info.deck_stems if not (d / "anki" / f"{x}.txt").exists()]
            unranked = [s for s, t in info.topics.items() if t.rank is None and t.tier is None and s != "study-guide"]
            n_ideas = sum(len(self._ideas(code, s)) for s in info.topics if s != "study-guide")
            out.append(f"{code}: exam {info.exam_date} · {len(info.priority)} priority rows · {len(info.topics)} topics · "
                       f"{n_ideas} ideas · "
                       f"{sum(len(t.objectives) for t in info.topics.values())} objectives · "
                       f"{len(info.trap_ids)} trap sections"
                       + (f" · no rank/tier: {', '.join(unranked)}" if unranked else ""))
            if missing:
                problems.append(f"{code}: links to missing notes {missing}")
            if decks:
                problems.append(f"{code}: links to missing decks {decks}")
            if len(info.priority) < 5:
                problems.append(f"{code}: only {len(info.priority)} priority rows parsed")
            if not info.exam_date:
                problems.append(f"{code}: no exam date found in STUDY-PLAN.md")
        self.state.load()
        out.append(f"state: {len(self.state.events)} events, {len(self.state.errors)} logged errors")
        out.append("problems: " + ("none" if not problems else "\n  " + "\n  ".join(problems)))
        return "\n".join(out)
