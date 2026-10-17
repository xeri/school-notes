import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from studymcp import config, corpus, drill, links
from studymcp.state import format_error_line, parse_error_line
from studymcp.tools import Study

P = config.load(Path(__file__).parents[3]).drill if (Path(__file__).parents[3] / "STUDY-PLAN.md").exists() else {}


# ------------------------------------------------------------------ corpus

def test_slug_matches_github():
    assert corpus.slugify("Conditions of demand — what shifts the curve") == "conditions-of-demand--what-shifts-the-curve"
    assert corpus.slugify("PED and *total* revenue ($TR$)") == "ped-and-total-revenue-tr"
    assert corpus.slugify("[Link](x.md) text") == "link-text"


def test_duplicate_headings_and_math_blocks(study):
    page = study.ix.page("MAQ", "algebra")
    ids = [r["id"] for r in page]
    assert "MAQ/algebra#quadratics--factorising-and-the-formula" in ids
    assert "MAQ/algebra#quadratics--factorising-and-the-formula-1" in ids
    first = study.ix.get("MAQ/algebra#quadratics--factorising-and-the-formula")
    assert first["text"].count("$$") == 2


def test_long_tables_split_with_header():
    rows = "\n".join(f"| row {i} | {'x' * 80} |" for i in range(80))
    text = "| A | B |\n|---|---|\n" + rows
    parts = corpus.split_text(text, 1000)
    assert len(parts) > 1
    assert all(p.startswith("| A | B |\n|---|---|") for p in parts)
    assert sum(p.count("| row ") for p in parts) == 80


def test_math_block_never_split():
    body = "intro\n\n$$\n" + "\n".join("a + b" * 20 for _ in range(40)) + "\n$$\n\nafter"
    parts = corpus.split_text(body, 500)
    assert all(p.count("$$") in (0, 2) for p in parts)


def test_deck_parser():
    from tests.conftest import FILES
    _, cards = corpus.parse_deck(FILES["T4-MAQ/anki/algebra.txt"], "MAQ", "algebra", "x")
    assert len(cards) == 3
    cloze = cards[1].extra
    assert cloze["cloze"] and cloze["q"].count("[…]") == 2
    assert "**b² − 4ac**" in cloze["a"] and "*two*" in cloze["a"] and "\n" in cloze["a"]
    assert cards[2].extra["q"] == '"Solve" demands?' and cards[2].extra["a"] == "working & answer"
    assert cards[0].id.startswith("MAQ/algebra~")


def test_glossary_and_acronyms(study):
    d = study.ix.definition("what is hydraulic action")
    assert d and d[0]["id"] == "GEQ/TERMS~hydraulic-action"
    assert study.ix.definition("wave")[0]["id"] == "GEQ/coasts~wave"
    assert corpus.acronyms("the price elasticity of demand (PED) is") == {"PED": "price elasticity of demand"}


def test_school_dedupe_and_kind(study):
    rows = study.ix.db.execute("SELECT id, kind FROM chunks WHERE stem LIKE 'F00%'").fetchall()
    assert ("GEQ/F001#p1", "paper") in rows
    assert not any(r[0].startswith("GEQ/F002") for r in rows)  # identical page dropped


# ------------------------------------------------------------------- links

def test_syllabus_objectives_and_codes(study):
    g = study.ix.graph
    alg, gr = g["MAQ"].topics["algebra"], g["MAQ"].topics["graphs"]
    assert ("E2.1", "Use letters for generalised numbers.") in alg.objectives
    assert any(c == "E2.9" for c, _ in gr.objectives) and not any(c == "E2.9" for c, _ in alg.objectives)
    coasts, rivers = g["GEQ"].topics["coasts"], g["GEQ"].topics["rivers"]
    assert any("coastal" in x for _, x in coasts.objectives) and not any("coastal" in x for _, x in rivers.objectives)
    assert coasts.group == "Theme 1: Natural Environment"


def test_priority_and_tiers(study):
    g = study.ix.graph
    assert g["MAQ"].topics["exam-errors"].rank == 1 and g["MAQ"].topics["exam-errors"].tier == 1
    assert g["MAQ"].topics["algebra"].rank == 2 and g["MAQ"].topics["algebra"].method == "Past papers"
    assert g["MAQ"].topics["graphs"].tier == 2
    assert g["GEQ"].topics["coasts"].rank == 1 and g["GEQ"].topics["rivers"].tier == 2
    assert links.parse_tier("3 (overlaps Economics)") == 3 and links.parse_tier("—") is None


def test_exam_dates(study):
    g = study.ix.graph
    assert g["MAQ"].exam_date == date(2026, 10, 27)
    assert g["GEQ"].exam_date == date(2026, 11, 4)
    assert links.expand_codes("E2.6, E2.9–2.11, E5") == ["E2.6", "E2.9", "E2.10", "E2.11", "E5"]


def test_traps_and_cites(study):
    g = study.ix.graph
    assert g["GEQ"].topics["coasts"].traps and g["MAQ"].topics["algebra"].traps
    assert g["MAQ"].topics["exam-errors"].cites == ["2023 Q6(a)(v)"]


# ------------------------------------------------------------------ search

def test_query_builder_is_safe(study):
    for q in ['PED (x) "y":', "-", "a OR AND NOT", "x*"]:
        study.ix.search(q)
    assert study.ix.search("longshore drift spit")[0][0]["id"]


def test_topic_resolution(study):
    assert study.ix.resolve_topic("MAQ", "quadratics")[0] == "algebra"
    assert study.ix.resolve_topic("MAQ", "graph")[0] == "graphs"
    assert study.cfg.resolve_subject("geo") == "GEQ" and study.cfg.resolve_subject("Business Studies") == "BUQ"


def test_read_and_topic_output(study):
    out = study.read("MAQ/algebra#quadratics--factorising-and-the-formula")
    assert "Exam link:" in out and "rank 2" in out
    assert "Section moved" in study.read("MAQ/algebra#nope") or "Closest" in study.read("MAQ/algebra#nope")
    pack = study.topic("maths quadratics")
    assert "Syllabus objectives" in pack and "Traps" in pack


# ------------------------------------------------------------- drill model

def test_memory_model():
    t0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
    m = drill.update(None, "miss", t0, P)
    assert m.S == pytest.approx(10 / 1440) and m.lapses == 1
    soon = drill.update(m, "ok", t0 + timedelta(minutes=1), P)
    assert soon.S < 30 / 1440  # asked again too soon: little growth
    later = drill.update(drill.update(None, "ok", t0, P), "ok", t0 + timedelta(days=3), P)
    assert later.S > 3
    assert drill.recall(later, later.last + timedelta(days=later.S)) == pytest.approx(0.9)


def test_error_line_roundtrip():
    line = format_error_line("2026-10-17", "algebra", "dropped the ± · twice", "write ± first", "method", "MAQ/algebra#x")
    e = parse_error_line("MAQ", line)
    assert (e.date, e.topic, e.type, e.fix, e.source) == ("2026-10-17", "algebra", "method", "write ± first", "MAQ/algebra#x")
    assert "dropped the ±" in e.what


def test_log_then_drill_resurfaces_misses(study):
    batch = study.drill("maths", n=5)
    first = batch.split("\n")[1].split()[1]
    out = study.log("maths", "algebra", "drill", reviews=[{"id": first, "grade": "miss"}],
                    errors=[{"what": "forgot ±", "fix": "write ± in the formula", "type": "method"}])
    assert "1 error(s)" in out
    log = (study.cfg.progress_dir / "MAQ-errors.md").read_text(encoding="utf-8")
    assert "· algebra · [method] forgot ± · write ± in the formula" in log
    again = study.drill("maths", n=5)
    lines = [l for l in again.split("\n") if l[:2] in ("1.", "2.")]
    assert any(first in l for l in lines) and any("ERR/MAQ/" in l for l in lines)


def test_plan_consolidates_near_exam(study):
    g = study.ix.graph
    mems = study.state.memories()
    mast = study.mastery(g, mems, study.deck_sizes(), datetime.now(timezone.utc))
    near = study._recommend(g, mems, mast, date(2026, 10, 26), "MAQ")
    assert near == []  # nothing attempted yet, and the exam is a day away
    far = study._recommend(g, mems, mast, date(2026, 10, 1), "MAQ")
    assert far and far[0][2] == "exam-errors"
    assert study._recommend(g, mems, mast, date(2026, 11, 1), "MAQ") == []  # exam passed


# ------------------------------------------------------------------- stdio

def test_stdio_handshake(repo):
    env = dict(os.environ, STUDY_ROOT=str(repo), PYTHONUTF8="1")
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search", "arguments": {"query": "spit"}}},
    ]
    p = subprocess.Popen([sys.executable, "-m", "studymcp.cli", "serve"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", env=env)
    lines = []
    try:
        for m in msgs:
            p.stdin.write(json.dumps(m) + "\n")
            p.stdin.flush()
            if "id" in m:  # wait for the answer before sending more (EOF would cancel it)
                while True:
                    lines.append(json.loads(p.stdout.readline()))  # every stdout line is JSON-RPC
                    if lines[-1].get("id") == m["id"]:
                        break
    finally:
        p.stdin.close()
        p.wait(timeout=30)
    tools = next(l for l in lines if l.get("id") == 2)["result"]["tools"]
    assert {t["name"] for t in tools} == {"search", "read", "topic", "drill", "log", "plan"}
    call = next(l for l in lines if l.get("id") == 3)["result"]
    assert "GEQ/" in call["content"][0]["text"] and "structuredContent" not in call


# --------------------------------------------------------------- real repo

REAL = Path(__file__).parents[3]


@pytest.mark.skipif(not (REAL / "STUDY-PLAN.md").exists(), reason="real repo not present")
def test_real_repo_doctor(monkeypatch):
    monkeypatch.delenv("STUDY_ROOT", raising=False)
    st = Study(config.load(REAL))
    report = st.doctor()
    assert "problems: none" in report
    assert st.ix.counts()["cards"] == 4029
    assert len(st.read("ECQ/policy-chains")) < 13000
