"""Settings, paths and subject lookup.

The repo root is the folder holding STUDY-PLAN.md, found by walking up from this
file (so the server works whatever directory it is started from). STUDY_ROOT
overrides it, which the tests use to point at a fixture repo.
"""

import os
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
CONFIG_FILE = PKG_DIR.parents[1] / "config.toml"


def find_root():
    env = os.environ.get("STUDY_ROOT")
    if env:
        return Path(env).resolve()
    for d in PKG_DIR.parents:
        if (d / "STUDY-PLAN.md").exists():
            return d
    raise RuntimeError("STUDY-PLAN.md not found above " + str(PKG_DIR))


@dataclass
class Subject:
    code: str
    name: str
    aliases: list
    weight: float = 1.0


@dataclass
class Config:
    root: Path
    term: str
    subjects: dict  # code -> Subject
    topic_aliases: dict = field(default_factory=dict)  # (code, words) -> stem
    drill: dict = field(default_factory=dict)
    plan: dict = field(default_factory=dict)
    caps: dict = field(default_factory=dict)

    def subject_dir(self, code):
        return self.root / f"{self.term}-{code}"

    @property
    def progress_dir(self):
        env = os.environ.get("STUDY_PROGRESS")
        return Path(env) if env else self.root / "local" / "progress"

    @property
    def extracted_dir(self):
        return self.root / "local" / "extracted"

    def resolve_subject(self, text):
        """code, name or alias -> code, else None."""
        if not text:
            return None
        t = text.strip().lower()
        for code, s in self.subjects.items():
            if t == code.lower() or t == s.name.lower() or t in s.aliases:
                return code
        for code, s in self.subjects.items():
            if s.name.lower().startswith(t) and len(t) >= 3:
                return code
        return None

    def split_subject(self, text):
        """'econ ped' -> ('ECQ', 'ped'); leading subject word(s) are optional."""
        words = (text or "").split()
        for n in (2, 1):
            if len(words) >= n:
                code = self.resolve_subject(" ".join(words[:n]))
                if code:
                    return code, " ".join(words[n:])
        return None, text or ""


def load(root=None):
    data = tomllib.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    subjects = {
        code: Subject(code, s["name"], [a.lower() for a in s.get("aliases", [])], float(s.get("weight", 1.0)))
        for code, s in data["subjects"].items()
    }
    aliases = {}
    for key, stem in data.get("topic_aliases", {}).items():
        code, _, words = key.partition(":")
        aliases[(code, norm_words(words))] = stem
    return Config(
        root=Path(root) if root else find_root(),
        term=data.get("term", "T4"),
        subjects=subjects,
        topic_aliases=aliases,
        drill=data.get("drill", {}),
        plan=data.get("plan", {}),
        caps=data.get("caps", {}),
    )


def norm_words(text):
    return " ".join(re.findall(r"\w+", (text or "").lower()))
