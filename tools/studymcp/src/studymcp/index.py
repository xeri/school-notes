"""In-memory SQLite FTS5 index over every chunk, refreshed from file stats.

Nothing is written to disk: the first call builds the index (about a second),
and every later call stats the files and re-parses only the ones that changed,
so edits to notes show up on the next tool call.
"""

import difflib
import json
import os
import re
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

from . import corpus, links
from .config import norm_words

KIND_BOOST = {"terms": 1.6, "notes": 1.3, "ref": 1.2, "syllabus": 1.0, "cards": 0.8,
              "paper": 0.7, "scheme": 0.7, "spec": 0.6, "course": 0.6, "school": 0.6}
KIND_GROUPS = {
    "notes": ("notes",), "ref": ("ref",), "terms": ("terms",), "syllabus": ("syllabus",),
    "cards": ("cards",), "school": ("paper", "scheme", "course", "spec", "school"),
    "papers": ("paper", "scheme"),
}
GROUP_CAP = {"notes": 5, "ref": 5, "syllabus": 2, "terms": 2, "cards": 2,
             "paper": 2, "scheme": 2, "course": 2, "spec": 1, "school": 1}
QUERY_STOP = {"what", "is", "are", "the", "a", "an", "of", "how", "does", "do", "why", "explain",
              "define", "definition", "meaning", "mean", "means", "in", "to", "and", "for", "on",
              "about", "me", "tell", "i", "need", "know", "with", "vs", "versus", "between", "it"}


def log(msg):
    print(f"[studymcp] {msg}", file=sys.stderr, flush=True)


class Index:
    def __init__(self, cfg):
        self.cfg = cfg
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.executescript("""
            CREATE TABLE chunks(rowid INTEGER PRIMARY KEY, id TEXT UNIQUE, subject TEXT, kind TEXT,
                path TEXT, stem TEXT, title TEXT, heading TEXT, level INT, ord INT, text TEXT, extra TEXT);
            CREATE INDEX chunks_path ON chunks(path);
            CREATE INDEX chunks_stem ON chunks(subject, stem);
            CREATE VIRTUAL TABLE fts USING fts5(title, heading, text,
                tokenize='porter unicode61 remove_diacritics 2');
        """)
        self.stats = {}            # path -> (mtime_ns, size)
        self.hashes = {}           # school page hash -> path (dedupe)
        self.acronyms = {}         # PED -> price elasticity of demand
        self.terms = defaultdict(list)  # normalised term -> chunk ids
        self.graph = {}
        self.built_at = 0.0
        self.build_seconds = 0.0
        self._ord = 0

    # ------------------------------------------------------------------ files

    def files(self):
        """[(Path, handler, code, extra)] for every indexed file."""
        cfg, out = self.cfg, []
        plan = cfg.root / "STUDY-PLAN.md"
        if plan.exists():
            out.append((plan, "plan", "", None))
        for code in cfg.subjects:
            d = cfg.subject_dir(code)
            if not d.exists():
                continue
            for e in _scan(d):
                if e.name.endswith(".md"):
                    out.append((Path(e.path), "syllabus" if e.name == "SYLLABUS.md" else "ref", code, e))
            for e in _scan(d / "notes"):
                if e.name.endswith(".md") and not e.name.startswith("_"):
                    out.append((Path(e.path), "notes", code, e))
            for e in _scan(d / "anki"):
                if e.name.endswith(".txt"):
                    out.append((Path(e.path), "deck", code, e))
            for e in _scan(cfg.extracted_dir / code):
                if e.name.endswith(".md"):
                    out.append((Path(e.path), "school", code, e))
        return out

    def rel(self, path):
        p, root = str(path), str(self.cfg.root)
        if p.startswith(root):
            return p[len(root):].lstrip("\\/").replace("\\", "/")
        return Path(path).resolve().relative_to(self.cfg.root.resolve()).as_posix()

    # ---------------------------------------------------------------- refresh

    def refresh(self):
        """re-parse changed files; returns the number of files changed."""
        t0 = time.perf_counter()
        seen, changed = set(), 0
        for path, handler, code, entry in self.files():
            rel = self.rel(path)
            seen.add(rel)
            try:
                st = entry.stat() if entry is not None else path.stat()
            except OSError:
                continue
            sig = (st.st_mtime_ns, st.st_size)
            if self.stats.get(rel) == sig:
                continue
            self.stats[rel] = sig
            self._remove(rel)
            try:
                self._add(path, rel, handler, code)
            except Exception as exc:  # one bad file must not take the server down
                log(f"skipped {rel}: {exc}")
            changed += 1
        for rel in [p for p in self.stats if p not in seen]:
            del self.stats[rel]
            self._remove(rel)
            changed += 1
        if changed:
            self._rebuild_graph()
            self.db.commit()
            self.built_at = time.time()
            self.build_seconds = time.perf_counter() - t0
        return changed

    def _remove(self, rel):
        rows = self.db.execute("SELECT rowid, id, kind, extra FROM chunks WHERE path=?", (rel,)).fetchall()
        for rowid, cid, kind, extra in rows:
            self.db.execute("DELETE FROM fts WHERE rowid=?", (rowid,))
            if kind == "terms":
                term = norm_words(json.loads(extra).get("term", ""))
                if cid in self.terms.get(term, []):
                    self.terms[term].remove(cid)
        self.db.execute("DELETE FROM chunks WHERE path=?", (rel,))
        for h in [h for h, p in self.hashes.items() if p == rel]:
            del self.hashes[h]

    def _add(self, path, rel, handler, code):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        chunks = []
        if handler == "plan":
            _, chunks = corpus.parse_markdown(text, "", "PLAN", "syllabus", rel, "")
        elif handler in ("syllabus", "ref", "notes"):
            kind = handler
            page_dir = "notes" if handler == "notes" else ""
            title, chunks = corpus.parse_markdown(text, code, path.stem, kind, rel, page_dir)
            chunks += corpus.definitions(text, code, path.stem, rel, title)
            for acr, long in corpus.acronyms(text).items():
                self.acronyms.setdefault(acr, long)
        elif handler == "deck":
            _, chunks = corpus.parse_deck(text, code, path.stem, rel)
        elif handler == "school":
            _, raw = corpus.parse_extracted(text, code, rel)
            for c in raw:
                h = corpus.text_hash(c.text)
                if h in self.hashes:
                    continue
                self.hashes[h] = rel
                chunks.append(c)
        for c in chunks:
            self._insert(c)

    def _insert(self, c):
        self._ord += 1
        try:
            cur = self.db.execute(
                "INSERT INTO chunks(id, subject, kind, path, stem, title, heading, level, ord, text, extra) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (c.id, c.subject, c.kind, c.path, c.stem, c.title, c.heading, c.level, self._ord,
                 c.text, json.dumps(c.extra, ensure_ascii=False)))
        except sqlite3.IntegrityError:
            return  # duplicate id (identical card fronts): keep the first
        self.db.execute("INSERT INTO fts(rowid, title, heading, text) VALUES (?,?,?,?)",
                        (cur.lastrowid, c.title, c.heading, corpus.index_text(c.text)))
        if c.kind == "terms":
            self.terms[norm_words(c.extra.get("term", ""))].append(c.id)

    def _rebuild_graph(self):
        by_stem = defaultdict(list)
        for row in self.db.execute(
                "SELECT id, subject, kind, path, stem, title, heading, level, text FROM chunks "
                "WHERE kind IN ('notes', 'ref') ORDER BY ord"):
            by_stem[(row[1], row[4])].append(corpus.Chunk(*row))
        self.graph = links.build(self.cfg, by_stem)

    # ---------------------------------------------------------------- lookups

    def get(self, cid):
        row = self.db.execute(
            "SELECT id, subject, kind, path, stem, title, heading, level, text, extra, ord FROM chunks WHERE id=?",
            (cid,)).fetchone()
        return _row(row)

    def page(self, code, stem, kinds=("notes", "ref", "syllabus")):
        q = "SELECT id, subject, kind, path, stem, title, heading, level, text, extra, ord FROM chunks " \
            f"WHERE subject=? AND stem=? AND kind IN ({','.join('?' * len(kinds))}) ORDER BY ord"
        return [_row(r) for r in self.db.execute(q, (code, stem, *kinds))]

    def section(self, cid):
        """a section plus its sub-sections, in order."""
        base = cid.split("~")[0]
        first = self.get(base)
        if not first:
            return []
        rows = self.page(first["subject"], first["stem"], (first["kind"],))
        out, inside = [], False
        for r in rows:
            if r["id"].split("~")[0] == base:
                inside = True
                out.append(r)
            elif inside:
                if r["level"] <= first["level"]:
                    break
                out.append(r)
        return out

    def cards(self, code=None, decks=None):
        q = "SELECT id, subject, kind, path, stem, title, heading, level, text, extra, ord FROM chunks WHERE kind='cards'"
        args = []
        if code:
            q += " AND subject=?"
            args.append(code)
        if decks:
            q += f" AND stem IN ({','.join('?' * len(decks))})"
            args += list(decks)
        return [_row(r) for r in self.db.execute(q + " ORDER BY ord", args)]

    def counts(self):
        return dict(self.db.execute("SELECT kind, count(*) FROM chunks GROUP BY kind").fetchall())

    # ----------------------------------------------------------------- search

    def match_query(self, query, mode="AND"):
        words = [w for w in re.findall(r"\w+", query.lower())]
        keep = [w for w in words if w not in QUERY_STOP] or words
        parts = []
        for w in keep:
            long = self.acronyms.get(w.upper())
            if long:
                parts.append(f'("{w}" OR "{long}")')
            else:
                parts.append(f'"{w}"')
        return f" {mode} ".join(parts)

    def search(self, query, code=None, kinds=None, limit=8, stems=None, grouped=True):
        """[(row dict, snippet, score)] best first."""
        results, have = [], set()
        for mode in ("AND", "OR"):
            mq = self.match_query(query, mode)
            if not mq:
                return []
            sql = ("SELECT c.id, c.subject, c.kind, c.path, c.stem, c.title, c.heading, c.level, c.text, c.extra, c.ord, "
                   "bm25(fts, 8.0, 4.0, 1.0), snippet(fts, 2, '«', '»', '…', ?) "
                   "FROM fts JOIN chunks c ON c.rowid = fts.rowid WHERE fts MATCH ?")
            args = [int(self.cfg.caps.get("snippet_tokens", 24)), mq]
            if code:
                sql += " AND c.subject=?"
                args.append(code)
            if kinds:
                sql += f" AND c.kind IN ({','.join('?' * len(kinds))})"
                args += list(kinds)
            if stems:
                sql += f" AND c.stem IN ({','.join('?' * len(stems))})"
                args += list(stems)
            sql += " ORDER BY bm25(fts, 8.0, 4.0, 1.0) LIMIT 120"
            try:
                rows = self.db.execute(sql, args).fetchall()
            except sqlite3.OperationalError as exc:
                log(f"query failed {mq!r}: {exc}")
                rows = []
            # AND hits always rank above OR-only hits
            tier = 0 if mode == "AND" else 1
            batch = [(tier, _row(r[:11]), r[12], r[11] * KIND_BOOST.get(r[2], 1.0))
                     for r in rows if r[0] not in have]
            have.update(b[1]["id"] for b in batch)
            results += batch
            if len(results) >= 3 or len(re.findall(r"\w+", query)) < 2:
                break
        results.sort(key=lambda x: (x[0], x[3]))
        results = [r[1:] for r in results]
        if not grouped:
            return results[:limit]
        out, per = [], defaultdict(int)
        for r in results:
            k = r[0]["kind"]
            if per[k] >= GROUP_CAP.get(k, 2) and not kinds:
                continue
            per[k] += 1
            out.append(r)
            if len(out) >= limit:
                break
        return out

    def definition(self, query):
        full = norm_words(query)
        lead = re.sub(r"^(what (is|are|does)( an?| the)?|define|definition of|meaning of|explain)\s+", "", full)
        q = " ".join(w for w in full.split() if w not in QUERY_STOP) or full
        ids = list(self.terms.get(lead, []) or self.terms.get(full, []) or self.terms.get(q, []))
        long = self.acronyms.get(q.upper())
        if not ids and long:
            ids = list(self.terms.get(norm_words(long), []))
        return [self.get(i) for i in ids[:3] if self.get(i)]

    # -------------------------------------------------------------- topics

    def resolve_topic(self, code, text):
        """('stem', [alternatives]) for free text within a subject; (None, alts) if unsure."""
        info = self.graph.get(code)
        if not info or not text:
            return None, []
        t = norm_words(text.split("#")[0].split("/")[-1].replace("-", " "))
        stems = list(info.topics)
        for s in stems:
            if t == s.replace("-", " "):
                return s, []
        if (code, t) in self.cfg.topic_aliases:
            return self.cfg.topic_aliases[(code, t)], []
        names = {}
        for s, top in info.topics.items():
            names[norm_words(top.title)] = s
            for r in top.rows:
                names[norm_words(re.sub(r"^\S+\s+", "", r))] = s
        if t in names:
            return names[t], []
        close = difflib.get_close_matches(t, list(names), n=3, cutoff=0.78)
        if close:
            return names[close[0]], [names[c] for c in close[1:] if names[c] != names[close[0]]]
        subs = list(dict.fromkeys(s for n, s in names.items() if t and t in n))
        if len(subs) == 1:
            return subs[0], []
        votes = defaultdict(float)
        hits = [h for h in self.search(text, code, ("notes",), limit=30, grouped=False)
                if h[0]["stem"] != "study-guide"]
        for i, (r, _, score) in enumerate(hits):
            votes[r["stem"]] += 1 / (i + 1)
        ranked = sorted(votes, key=votes.get, reverse=True)
        if not ranked:
            return (subs[0], subs[1:]) if subs else (None, [])
        return ranked[0], ranked[1:3]

    def resolve_any(self, text):
        """subject and topic from free text: 'econ ped' or just 'ped'."""
        code, rest = self.cfg.split_subject(text)
        if code:
            stem, alts = self.resolve_topic(code, rest) if rest.strip() else (None, [])
            return code, stem, alts
        hits = self.search(text, None, ("notes", "terms", "ref"), limit=10, grouped=False)
        hits = [h for h in hits if h[0]["stem"] != "study-guide"]
        if not hits:
            return None, None, []
        top = hits[0][0]
        code = top["subject"]
        stem = top["stem"] if top["kind"] == "notes" else self.resolve_topic(code, text)[0]
        alts = list(dict.fromkeys(f"{h[0]['subject']}/{h[0]['stem']}" for h in hits[1:5]))
        return code, stem, alts


def _scan(d):
    try:
        return sorted(os.scandir(d), key=lambda e: e.name)
    except OSError:
        return []


def _row(r):
    if not r:
        return None
    keys = ("id", "subject", "kind", "path", "stem", "title", "heading", "level", "text", "extra", "ord")
    d = dict(zip(keys, r))
    d["extra"] = json.loads(d["extra"]) if d.get("extra") else {}
    return d
