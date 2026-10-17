"""Study state: an append-only event log plus the human-readable error logs.

local/progress/events.jsonl   one JSON object per line:
    {"t": iso, "ev": "attempt", "subject", "topic", "mode", "score", "out_of"}
    {"t": iso, "ev": "review",  "subject", "topic", "item", "grade"}   grade: ok | shaky | miss
    {"t": iso, "ev": "error",   "subject", "topic", "item"}             a mark lost (also in the md log)
local/progress/<CODE>-errors.md   "- YYYY-MM-DD · topic · [type] what · fix · source"

Everything else (item memory, topic mastery) is recomputed by replaying the
events, so the model in drill.py can be retuned and history re-applies.
Both folders are gitignored; nothing here is ever published.
"""

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from . import drill


def now():
    return datetime.now(timezone.utc)


def parse_time(s):
    t = datetime.fromisoformat(s)
    return t if t.tzinfo else t.astimezone()


def local_date(t):
    return t.astimezone().date()


@dataclass
class ErrorEntry:
    id: str
    subject: str
    date: str
    topic: str
    what: str
    fix: str
    type: str = ""
    source: str = ""


def error_id(code, date, topic, what):
    return f"ERR/{code}/" + hashlib.sha1(f"{date}|{topic}|{what}".encode("utf-8")).hexdigest()[:8]


def parse_error_line(code, line):
    line = line.strip()
    if not line.startswith("- "):
        return None
    f = [x.strip() for x in line[2:].split(" · ")]
    if len(f) < 3 or not re.match(r"^\d{4}-\d{2}-\d{2}$", f[0]):
        return None
    date, topic, what = f[0], f[1], f[2]
    fix = f[3] if len(f) > 3 else ""
    source = f[4] if len(f) > 4 else ""
    m = re.match(r"^\[([^\]]+)\]\s*(.*)$", what)
    etype, what_text = (m.group(1), m.group(2)) if m else ("", what)
    return ErrorEntry(error_id(code, date, topic, what), code, date, topic, what_text, fix, etype, source)


def format_error_line(date, topic, what, fix, etype="", source=""):
    clean = lambda s: re.sub(r"\s+", " ", (s or "").replace(" · ", ", ")).strip()
    what = f"[{clean(etype)}] {clean(what)}" if etype else clean(what)
    parts = [date, clean(topic), what, clean(fix)]
    if source:
        parts.append(clean(source))
    return "- " + " · ".join(parts)


class State:
    def __init__(self, cfg):
        self.cfg = cfg
        self.dir = cfg.progress_dir
        self.events_file = self.dir / "events.jsonl"
        self._sig = None
        self.events = []
        self.errors = []

    def _signature(self):
        sig = []
        for f in [self.events_file] + sorted(self.dir.glob("*-errors.md")) if self.dir.exists() else []:
            try:
                st = f.stat()
                sig.append((f.name, st.st_mtime_ns, st.st_size))
            except OSError:
                pass
        return tuple(sig)

    def load(self):
        sig = self._signature()
        if sig == self._sig:
            return self
        self._sig = sig
        self.events = []
        if self.events_file.exists():
            for line in self.events_file.read_text(encoding="utf-8-sig").splitlines():
                try:
                    self.events.append(json.loads(line))
                except ValueError:
                    continue
        self.errors = []
        for code in self.cfg.subjects:
            f = self.dir / f"{code}-errors.md"
            if f.exists():
                for line in f.read_text(encoding="utf-8-sig").splitlines():
                    e = parse_error_line(code, line)
                    if e:
                        self.errors.append(e)
        return self

    # ---------------------------------------------------------------- writes

    def append(self, events):
        self.dir.mkdir(parents=True, exist_ok=True)
        with self.events_file.open("a", encoding="utf-8", newline="\n") as f:
            for e in events:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

    def append_errors(self, code, lines):
        self.dir.mkdir(parents=True, exist_ok=True)
        f = self.dir / f"{code}-errors.md"
        new = not f.exists()
        with f.open("a", encoding="utf-8", newline="\n") as out:
            if new:
                out.write(f"# {self.cfg.subjects[code].name} error log\n\n"
                          "One line per lost mark: date · topic · [type] what went wrong · the fix · source.\n\n")
            for line in lines:
                out.write(line + "\n")

    # ---------------------------------------------------------------- replay

    def memories(self, at=None):
        """item id -> drill.Memory, from reviews plus logged errors."""
        p = self.cfg.drill
        stream = []
        logged = set()
        for e in self.events:
            if e.get("ev") == "review" and e.get("item"):
                stream.append((parse_time(e["t"]), e["item"], e.get("grade", "ok")))
            elif e.get("ev") == "error" and e.get("item"):
                stream.append((parse_time(e["t"]), e["item"], "miss"))
                logged.add(e["item"])
        for err in self.errors:
            if err.id not in logged:  # typed into the md log by hand
                stream.append((datetime.fromisoformat(err.date).astimezone(), err.id, "miss"))
        stream.sort(key=lambda x: x[0])
        mems = {}
        for t, item, grade in stream:
            if at and t > at:
                break
            mems[item] = drill.update(mems.get(item), grade, t, p)
        return mems

    def attempts(self, code=None):
        return [e for e in self.events if e.get("ev") == "attempt" and (not code or e.get("subject") == code)]

    def topic_scores(self):
        """(code, stem) -> {"m": ewma or None, "n": attempts, "last": datetime}"""
        out = {}
        for e in self.events:
            if e.get("ev") not in ("attempt", "review"):
                continue
            key = (e.get("subject"), e.get("topic"))
            rec = out.setdefault(key, {"m": None, "n": 0, "last": None})
            t = parse_time(e["t"])
            rec["last"] = t if rec["last"] is None or t > rec["last"] else rec["last"]
            if e["ev"] == "attempt" and e.get("out_of"):
                f = max(0.0, min(1.0, float(e.get("score") or 0) / float(e["out_of"])))
                alpha = 0.5 if e.get("mode") != "drill" else 0.25
                rec["m"] = f if rec["m"] is None else rec["m"] + alpha * (f - rec["m"])
                rec["n"] += 1
        return out

    def recent_errors(self, code=None, topic=None, days=7):
        today = now().astimezone().date()
        out = []
        for e in self.errors:
            if code and e.subject != code:
                continue
            if topic and e.topic != topic:
                continue
            try:
                age = (today - datetime.fromisoformat(e.date).date()).days
            except ValueError:
                continue
            if age <= days:
                out.append(e)
        return out
