"""The six tools (plus brief and doctor), as plain functions returning compact
markdown. server.py exposes them over MCP; cli.py runs them in a terminal.
"""

import re
import threading
import time
from collections import Counter, defaultdict
from datetime import date

from . import config, drill, links
from .index import KIND_GROUPS, Index
from .state import State, format_error_line, local_date, now, parse_error_line

GRADES = {"ok": "ok", "correct": "ok", "right": "ok", "yes": "ok", "good": "ok", "easy": "ok", "pass": "ok",
          "shaky": "shaky", "hard": "shaky", "partial": "shaky", "slow": "shaky", "half": "shaky",
          "miss": "miss", "wrong": "miss", "no": "miss", "again": "miss", "fail": "miss", "missed": "miss"}
SCHOOL = {"paper", "scheme", "course", "spec", "school"}


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

    def item_topic(self, item_id, graph):
        """card id ECQ/markets~ab12 -> (ECQ, markets); error id ERR/ECQ/.. -> (ECQ, topic)."""
        if item_id.startswith("ERR/"):
            code = item_id.split("/")[1]
            for e in self.state.errors:
                if e.id == item_id:
                    return code, e.topic
            return code, ""
        code, _, rest = item_id.partition("/")
        deck = rest.split("~")[0]
        info = graph.get(code)
        stems = info.deck_stems.get(deck, []) if info else []
        return code, (stems[0] if stems else deck)

    def mastery(self, graph, mems, sizes, at):
        """(code, stem) -> dict(m, att, n, seen, total, recall, last)"""
        scores = self.state.topic_scores()
        seen = defaultdict(list)
        for item_id, mem in mems.items():
            if item_id.startswith("ERR/"):
                continue
            code, _, rest = item_id.partition("/")
            seen[(code, rest.split("~")[0])].append(drill.recall(mem, at))
        out = {}
        for code, info in graph.items():
            for stem, t in info.topics.items():
                decks = t.decks
                total = sum(sizes.get((code, d), 0) for d in decks)
                rs = [r for d in decks for r in seen.get((code, d), [])]
                sc = scores.get((code, stem), {})
                att = sc.get("m")
                card_m = (sum(rs) / len(rs)) * (len(rs) / total) if rs and total else None
                if att is not None and card_m is not None:
                    m = 0.6 * att + 0.4 * card_m
                else:
                    m = att if att is not None else card_m
                out[(code, stem)] = {"m": m, "att": att, "n": sc.get("n", 0), "seen": len(rs), "total": total,
                                     "recall": sum(rs) / len(rs) if rs else None, "last": sc.get("last")}
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
            out.append(f"\n## Syllabus objectives ({len(t.objectives)})")
            out += [f"- {c} {clip(x, 200)}" if c else f"- {clip(x, 200)}" for c, x in t.objectives[:18]]
        out.append("\n## Sections (read(id))")
        for r in rows:
            if r["level"] <= 3 and "~" not in r["id"] and not r["id"].endswith("#top"):
                out.append(f"{'  ' * (r['level'] - 2)}- {r['heading'].split(' › ')[-1]} · {r['id']}")

        page_text = "\n".join(r["text"] for r in rows)
        terms = [r[0] for r in self.ix.db.execute(
            "SELECT json_extract(extra, '$.term') FROM chunks WHERE kind='terms' AND subject=? AND stem=?",
            (code, stem))]
        figs = re.findall(r"\[figure: ([^\]]{5,140}?)(?: \([^)]*\.svg\))?\]", page_text)
        maths = [m.strip() for m in re.findall(r"\$\$(.+?)\$\$", page_text, re.S) if len(m) < 120]
        worked = [r["id"] for r in rows if re.search(r"\*\*(Worked example|Chain|Model answer|Thesis)", r["text"])]
        out.append("\n## Must know")
        if terms:
            out.append("Define: " + "; ".join(terms[:20]))
        bold = [b for b in dict.fromkeys(re.findall(r"(?m)^\s*(?:[-*]|\d+\.)?\s*\*\*([A-Za-z][^*\n]{2,50})\*\*", page_text))
                if not b.rstrip().endswith((":", ".", "?"))]
        if not terms and bold:
            out.append("Key terms: " + "; ".join(bold[:20]))
        if figs:
            out.append("Draw: " + "; ".join(clip(f, 90) for f in figs[:8]))
        if maths:
            out.append("Formulas: " + "; ".join(f"${m}$" for m in maths[:8]))
        if worked:
            out.append("Chains / worked examples: " + ", ".join(worked[:8]))
        related = [r for r, _, _ in self.ix.search(t.title, code, ("notes", "ref"), 40, grouped=False)
                   if r["id"] in info.trap_ids and r["stem"] != stem][:3]
        if t.traps or related:
            out.append("\n## Traps (marks lost)")
            out += [f"- {i}: {oneline(x, 220)}" for i, x in t.traps[:6]]
            out += [f"- {r['id']} (related): {oneline(r['text'], 200)}" for r in related]
        if t.cites:
            out.append("\n## Past-paper questions cited in the notes\n" + ", ".join(t.cites[:14]))
        qs = self.ix.search(t.title, code, ("paper", "scheme"), 3)
        if qs:
            out.append("\n## Possible school questions (unverified extraction)")
            out += [f"- {r['id']} · {clip(r['title'], 60)} {r['heading']} · {oneline(s, 140)}" for r, s, _ in qs]

        g = self.ix.graph
        mems = self.state.memories()
        at = now()
        sizes = self.deck_sizes()
        m = self.mastery(g, mems, sizes, at).get((code, stem), {})
        missed = [i for i, mm in mems.items() if mm.last_grade == "miss" and self.item_topic(i, g) == (code, stem)]
        out.append("\n## You")
        out.append(f"Mastery {pct(m.get('m'))} · attempts {m.get('n', 0)} (avg {pct(m.get('att'))}) · "
                   f"cards seen {m.get('seen', 0)}/{m.get('total', 0)} (recall {pct(m.get('recall'))}) · "
                   f"missed now {len(missed)} · decks {', '.join(t.decks) or '—'}")
        errs = [e for e in self.state.errors if e.subject == code and e.topic == stem][-5:]
        for e in errs:
            out.append(f"- {e.date}: {clip(e.what, 120)} → {clip(e.fix, 120)}")
        return "\n".join(out)

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
                                  "q": f"Earlier you lost a mark ({e.topic}): {e.what}. What is the correct version?",
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
            return "Nothing missed or fading right now. Try focus='new' or a quiz."
        kinds = Counter(re.match(r"[a-z]+", why).group() for _, why in picked)
        scope = (g[code].name if code else "all subjects with exams ahead") + (f" · {stem}" if stem else "")
        out = [f"Drill · {scope} · {len(picked)} items ({', '.join(f'{v} {k}' for k, v in kinds.items())})"]
        for i, (it, why) in enumerate(picked, 1):
            out.append(f"{i}. {it['id']} [{why}]\n   Q: {it['q']}\n   A: {it['a']}" + (f"\n   Hint: {it['hint']}" if it["hint"] else ""))
        out.append("Grade each ok / shaky / miss, re-ask misses after ~3 items, then log(reviews=[...]).")
        return "\n".join(out)

    # ------------------------------------------------------------------- log

    def log(self, subject, topic="", mode="quiz", score=None, out_of=None, errors=None, reviews=None):
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
        before = self.mastery(g, self.state.memories(), self.deck_sizes(), at)
        events, lines, msgs = [], [], []

        if score is not None and out_of:
            events.append({"t": t, "ev": "attempt", "subject": code, "topic": stem, "mode": mode,
                           "score": float(score), "out_of": float(out_of)})
            msgs.append(f"attempt {score:g}/{out_of:g}")

        by_topic = defaultdict(list)
        for r in reviews or []:
            item = str(r.get("id", "")).strip()
            grade = GRADES.get(str(r.get("grade", "")).lower().strip())
            if not item or not grade:
                continue
            c, tp = self.item_topic(item, g)
            events.append({"t": t, "ev": "review", "subject": c, "topic": tp, "item": item, "grade": grade})
            by_topic[(c, tp)].append(grade)
        for (c, tp), grades in by_topic.items():
            if score is None:
                ok = sum(1.0 if x == "ok" else 0.5 if x == "shaky" else 0 for x in grades)
                events.append({"t": t, "ev": "attempt", "subject": c, "topic": tp, "mode": "drill",
                               "score": ok, "out_of": float(len(grades))})
        if reviews:
            gc = Counter(x for gs in by_topic.values() for x in gs)
            msgs.append(f"{sum(gc.values())} reviews ({', '.join(f'{v} {k}' for k, v in gc.items())})")

        day = local_date(at).isoformat()
        for e in errors or []:
            what = str(e.get("what", "")).strip()
            if not what:
                continue
            line = format_error_line(day, stem or e.get("topic", "") or "general", what, e.get("fix", ""),
                                     e.get("type", ""), e.get("source", ""))
            parsed = parse_error_line(code, line)
            lines.append(line)
            events.append({"t": t, "ev": "error", "subject": code, "topic": parsed.topic, "item": parsed.id})
        if lines:
            msgs.append(f"{len(lines)} error(s) → local/progress/{code}-errors.md")

        if not events:
            return "Nothing logged: give score and out_of, errors, or reviews."
        with self.lock:
            if lines:
                self.state.append_errors(code, lines)
            self.state.append(events)
            self.state.load()
        mems = self.state.memories()
        after = self.mastery(g, mems, self.deck_sizes(), at)
        out = ["Logged: " + "; ".join(msgs) + "."]
        touched = {(code, stem)} if stem else set()
        touched |= set(by_topic)
        for key in touched:
            if key in after:
                out.append(f"{key[0]}/{key[1]} mastery {pct(before.get(key, {}).get('m'))} → {pct(after[key]['m'])}")
        leech = self.cfg.drill.get("leech_lapses", 3)
        flagged = [i for i in {r.get("id") for r in reviews or []} if i in mems and mems[i].lapses >= leech]
        if flagged:
            out.append(f"Leeches (missed {leech}+ times; explain them, consider an Anki card): {', '.join(flagged)}")
        return "\n".join(out)

    # ------------------------------------------------------------------ plan

    def _recommend(self, g, mems, mast, today, subject=None, k=3):
        p = self.cfg.plan
        recs = []
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
                mode = "drill + errors" if consolidate else (
                    "need → blurt" if m.get("m") is None else "quiz" if mm < 0.6 else "drill + paper")
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
            out.append(f"{i}. {info.name} · {t.title} ({c}/{stem}) — {', '.join(why)}. "
                       f"Do: {mode}" + (f". Method: {clip(t.method, 160)}" if t.method else ""))

        missed = sum(1 for i, m in mems.items() if m.last_grade == "miss" and (not code or self.item_topic(i, g)[0] == code))
        fading = sum(1 for i, m in mems.items() if m.last_grade != "miss" and drill.recall(m, at) < self.cfg.drill.get("target_recall", 0.9)
                     and (not code or self.item_topic(i, g)[0] == code))
        total = sum(v for (c, _), v in sizes.items() if not code or c == code)
        out.append(f"\n## Drill queue\n{missed} missed · {fading} fading · {total - len(mems):,} never seen (of {total:,} cards)")

        out.append("\n## Mastery")
        if code:
            info = g[code]
            for stem, t in sorted(info.topics.items(), key=lambda kv: (kv[1].rank or 99, kv[1].order)):
                if stem == "study-guide":
                    continue
                m = mast.get((code, stem), {})
                out.append(f"- {stem}: {pct(m.get('m'))} · attempts {m.get('n', 0)} · cards {m.get('seen', 0)}/{m.get('total', 0)}")
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
        line3 = f"Drill: {missed} missed, {fading} fading. /study next · /study drill · /study explain <topic>"
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
            out.append(f"{code}: exam {info.exam_date} · {len(info.priority)} priority rows · {len(info.topics)} topics · "
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
