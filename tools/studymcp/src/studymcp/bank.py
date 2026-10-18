"""The prep bank: plain gists and true/false statements per idea, written by Claude.

local/bank/<CODE>/<stem>.json (gitignored, rebuildable; .claude/skills/study/prep.md says how):
    {"topic": "ECQ/markets", "built": "YYYY-MM-DD",
     "ideas": {"ECQ/markets#x": {"hash", "gist", "weight": "high|medium|low",
                                 "statements": [{"text", "true", "fix"?, "change"?}],
                                 "mixups": [...], "links": [idea ids]}},
     "flags": ["ECQ/markets#x: thin notes ..."]}

An entry counts only while its hash matches the idea's current notes text, so an edited
section falls back to the regex gist and an excerpt until the topic is rebuilt.
"""

import json
import os
import re
from datetime import date

from .ideas import idea_hash

WEIGHTS = ("high", "medium", "low")
MOST_STATEMENTS = 16
# wording about the notes rather than the subject ("the plan concludes...", "the notes say...")
META = re.compile(r"\b(?:the|these|this) (?:notes|section|page|slides)\b"
                  r"|\b(?:the|this|each) (?:\w+ )?plans? (?:argues|concludes|says|runs|starts|ends)\b", re.I)


def recommended(text):
    """how many statements an idea's notes deserve: 4 for a short idea, about one per 500
    characters for a long one, at most 12."""
    return max(4, min(12, round(len(text) / 500)))


class Bank:
    def __init__(self, folder):
        self.dir = folder
        self._cache = {}  # (code, stem) -> (file signature, data)

    def path(self, code, stem):
        return self.dir / code / f"{stem}.json"

    def draft_path(self, code, stem):
        return self.dir / code / f"{stem}.draft.json"

    def load(self, code, stem):
        f = self.path(code, stem)
        try:
            st = f.stat()
        except OSError:
            return None
        sig = (st.st_mtime_ns, st.st_size)
        hit = self._cache.get((code, stem))
        if hit and hit[0] == sig:
            return hit[1]
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            data = None
        self._cache[(code, stem)] = (sig, data)
        return data

    def entry(self, idea):
        """the bank entry for an idea cluster, or None if missing or out of date."""
        data = self.load(idea["subject"], idea["stem"])
        e = ((data or {}).get("ideas") or {}).get(idea["id"])
        return e if isinstance(e, dict) and e.get("hash") == idea_hash(idea["text"]) else None

    def status(self, code, stem, clusters):
        """(built | stale | missing | empty, ids that need building)."""
        if not clusters:
            return "empty", []
        if not self.load(code, stem):
            return "missing", [c["id"] for c in clusters]
        need = [c["id"] for c in clusters if not self.entry(c)]
        return ("stale" if need else "built"), need

    def thin(self, clusters):
        """ids of built ideas with fewer statements than their notes deserve (recommended)."""
        out = []
        for c in clusters:
            e = self.entry(c)
            if e and len(e.get("statements") or []) < recommended(c["text"]):
                out.append(c["id"])
        return out

    def flags(self, code, stem):
        return list((self.load(code, stem) or {}).get("flags") or [])

    def save(self, code, stem, clusters, known=None):
        """validate the draft, stamp hashes, merge with still-valid entries and write it in place.
        Returns (ok, errors, warnings)."""
        d = self.draft_path(code, stem)
        if not d.exists():
            return False, [f"no draft at {d}"], []
        try:
            draft = json.loads(d.read_text(encoding="utf-8-sig"))
        except ValueError as e:
            return False, [f"the draft is not valid JSON: {e}"], []
        keep = {c["id"] for c in clusters if self.entry(c)}
        errors, warnings = validate(draft, clusters, keep, known)
        if errors:
            return False, errors, warnings
        old = self.load(code, stem) or {}
        by_id = {c["id"]: c for c in clusters}
        merged = {i: e for i, e in (old.get("ideas") or {}).items() if i in keep}
        for i, e in draft["ideas"].items():
            merged[i] = {"hash": idea_hash(by_id[i]["text"]), **{k: v for k, v in e.items() if k != "hash"}}
        rebuilt = set(draft["ideas"])
        flags = [f for f in old.get("flags") or []  # on a partial rebuild, keep the other ideas' flags
                 if keep and str(f).split(":")[0].strip() not in rebuilt]
        flags += [str(f) for f in draft.get("flags") or []]
        data = {"topic": f"{code}/{stem}", "built": date.today().isoformat(),
                "ideas": {c["id"]: merged[c["id"]] for c in clusters if c["id"] in merged},
                "flags": list(dict.fromkeys(flags))}
        high = sum(1 for e in data["ideas"].values() if e.get("weight") == "high")
        if len(data["ideas"]) >= 4 and high > len(data["ideas"]) / 2:
            warnings.append(f"{high} of {len(data['ideas'])} ideas are high: keep high for the ideas the exam "
                            "leans on most, about a third of the topic")
        f = self.path(code, stem)
        tmp = f.with_name(f".{f.name}.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        os.replace(tmp, f)
        d.unlink()
        return True, [], warnings


def validate(draft, clusters, keep=(), known=None):
    """(errors, warnings) for a draft. keep: ids whose existing entries still match and may be left out.
    known(id) -> bool checks links."""
    if not isinstance(draft, dict) or not isinstance(draft.get("ideas"), dict):
        return ['the draft needs an "ideas" object'], []
    errors, warnings = [], []
    ids = [c["id"] for c in clusters]
    got = draft["ideas"]
    errors += [f"{i}: not an idea on this page" for i in got if i not in ids]
    missing = [i for i in ids if i not in got and i not in keep]
    if missing:
        errors.append("missing ideas: " + ", ".join(missing))
    by_id = {c["id"]: c for c in clusters}
    for i, e in got.items():
        if i not in ids:
            continue
        if not isinstance(e, dict):
            errors.append(f"{i}: not an object")
            continue
        want = recommended(by_id[i]["text"])
        gist = str(e.get("gist") or "").strip()
        if not gist:
            errors.append(f"{i}: no gist")
        elif len(gist) > 220:
            errors.append(f"{i}: gist is {len(gist)} characters (at most 200)")
        if e.get("weight") not in WEIGHTS:
            errors.append(f"{i}: weight must be high, medium or low")
        st = e.get("statements")
        if not isinstance(st, list) or len(st) < 3:
            errors.append(f"{i}: needs at least {want} statements")
            continue
        if len(st) > MOST_STATEMENTS:
            errors.append(f"{i}: {len(st)} statements (at most {MOST_STATEMENTS})")
        elif len(st) < want:
            warnings.append(f"{i}: {len(st)} statements; its notes deserve about {want}")
        for text in [gist] + [str(s.get("text") or "") for s in st if isinstance(s, dict)]:
            if META.search(text):
                warnings.append(f"{i}: {text[:60]!r} is about the notes; state the subject itself")
        n_false = 0
        for k, s in enumerate(st, 1):
            if not isinstance(s, dict) or not str(s.get("text") or "").strip() or not isinstance(s.get("true"), bool):
                errors.append(f"{i} statement {k}: needs text and true (true or false)")
                continue
            if not s["true"]:
                n_false += 1
                if not str(s.get("fix") or "").strip() or not str(s.get("change") or "").strip():
                    errors.append(f"{i} statement {k}: a false statement needs fix and change")
        if n_false == 0 or n_false == len(st):
            warnings.append(f"{i}: all statements are {'true' if n_false == 0 else 'false'}")
        for key in ("mixups", "links"):
            if not isinstance(e.get(key, []), list):
                errors.append(f"{i}: {key} must be a list")
        for link in e.get("links") or []:
            if known and not known(str(link)):
                warnings.append(f"{i}: link {link} is not a known idea")
    if not isinstance(draft.get("flags", []), list):
        errors.append("flags must be a list")
    return errors, warnings
