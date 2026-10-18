"""Levels, idea clusters and the session brief."""

import json
from datetime import date, datetime, timedelta, timezone

from studymcp import drill, ideas

T0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
EARLY = date(2026, 10, 1)  # well before the fixture's Maths exam (27 Oct)


def params(study):
    return study.cfg.memory


# ------------------------------------------------------------------ levels

def test_level_rules(study):
    P = params(study)
    m = drill.update(None, "ok", T0, P, level=3)
    assert m.level == 3 and drill.next_level(m, T0, 0.9) == 4  # a clean level-3 answer skips 1 and 2
    later = T0 + timedelta(hours=1)
    assert drill.update(m, "slip", later, P, level=4).level == 3   # a slip is not a gap
    assert drill.update(m, "shaky", later, P, level=4).level == 3  # 4 not solid yet: try 4 again
    assert drill.update(m, "miss", later, P, level=2).level == 1   # a real gap at 2: back to 2
    assert drill.update(m, "shaky", later, P, level=1).level == 2  # a doubtful sweep answer: one level down
    assert drill.next_level(m, T0, 0.9, cap=3) == 3                # Physics-style cap
    assert drill.next_level(m, T0 + timedelta(days=60), 0.9) == 3  # faded: one level easier
    assert drill.next_level(None, T0, 0.9) == 1
    missed = drill.update(None, "miss", T0, P, level=1)
    assert drill.next_level(missed, T0, 0.9, days_to_exam=2, p=P) == 3  # near the exam: less support
    assert drill.next_level(missed, T0, 0.9) == 1 and drill.next_level(missed, T0, 0.9, floor=2) == 2  # 1 is the sweep


def test_credit_scales_growth(study):
    P = {**params(study), "credit": [0.5, 0.7, 0.85, 1.0, 1.0]}
    gap = T0 + timedelta(days=3)
    easy = drill.update(drill.update(None, "ok", T0, P, level=1), "ok", gap, P, level=1)
    hard = drill.update(drill.update(None, "ok", T0, P, level=5), "ok", gap, P, level=5)
    assert easy.S < hard.S


# --------------------------------------------------------------- clusters

def row(i, level, heading, text="Some text that is long enough to count as content."):
    return {"id": f"X/p#{i}", "subject": "X", "stem": "p", "heading": heading, "level": level, "text": text}


def test_idea_clusters():
    rows = [row("top", 1, ""), row("a", 2, "A"), row("a-1", 3, "A › Child"),
            {**row("a", 2, "A"), "id": "X/p#a~2"}, row("b", 2, "B"), row("c", 2, "C"),
            row("this-loses-marks", 2, "This loses marks")]
    cs = ideas.clusters(rows)
    assert [c["id"] for c in cs] == ["X/p#a", "X/p#b", "X/p#c", "X/p#this-loses-marks"]
    assert cs[0]["members"] == ["X/p#a", "X/p#a-1", "X/p#a~2"] and "### Child" in cs[0]["text"]
    assert [c["id"] for c in ideas.ideas(rows)] == ["X/p#a", "X/p#b", "X/p#c"]  # traps are not ideas
    few = [row("a", 2, "A", "intro"), row("x", 3, "A › X"), row("y", 3, "A › Y")]
    assert [c["id"] for c in ideas.clusters(few)] == ["X/p#x", "X/p#y"]  # under 3 `##`: split at `###`
    assert ideas.count_ideas("# T\n\n## A\n\n## B\n\n## C\n\n## This loses marks\n") == 3
    long = "word " * 300
    big = [row("a", 2, "A", "short intro"), row("a-1", 3, "A › One", long), row("a-2", 3, "A › Two", long),
           row("a-2-x", 4, "A › Two › X", long), row("b", 2, "B"), row("c", 2, "C")]
    assert [c["id"] for c in ideas.ideas(big, max_chars=2000)] == ["X/p#a-1", "X/p#a-2", "X/p#b", "X/p#c"]
    assert [c["id"] for c in ideas.ideas(big)] == ["X/p#a", "X/p#b", "X/p#c"]  # under the limit: one idea
    md = "# T\n\n## A\n\nshort intro\n\n### One\n\n" + long + "\n\n### Two\n\n" + long + "\n\n## B\n\nx\n\n## C\n\ny\n"
    assert ideas.count_ideas(md, max_chars=2000) == 4 and ideas.count_ideas(md) == 3
    assert ideas.signals("$5 and $10, then $15") == []
    assert "chain" in ideas.signals("price up → demand down → revenue falls")


def test_ideas_count_towards_mastery(study):
    g = study.ix.graph
    assert study.item_topic("MAQ/algebra#x", g) == ("MAQ", "algebra")
    ids = [c["id"] for c in study._ideas("MAQ", "algebra")]
    assert len(ids) == 2
    study.log("maths", reviews=[{"id": ids[0], "grade": "ok", "level": 3}])
    m = study.mastery(g, study.state.memories(), study.deck_sizes(), datetime.now(timezone.utc))[("MAQ", "algebra")]
    assert (m["ideas"], m["ideas_total"]) == (1, 2) and m["idea_m"] and m["m"]


# ---------------------------------------------------------------- session

def first_item(out):
    return next(line for line in out.splitlines() if line.startswith("1. "))


def item_no(out, cid):
    """the number of the brief item whose id is exactly cid."""
    for line in out.splitlines():
        parts = line.split(" · ")
        if line[:1].isdigit() and cid in parts:
            return int(line.split(".")[0])
    raise AssertionError(f"{cid} not in brief")


def test_session_starts_with_a_sweep(study):
    out = study.session("maths", today=EARLY)
    assert out.startswith("# Sweep · Mathematics · ") and "why: new topic · highest priority" in out
    stem = out.splitlines()[0].split("(MAQ/")[1].rstrip(")")
    assert all(i in out for i in (c["id"] for c in study._ideas("MAQ", stem)))
    assert "1–2 level-3 items" in out and "(no bank yet)" in out


def test_session_levels_rise_and_carry_on(study):
    ids = [c["id"] for c in study._ideas("MAQ", "algebra")]
    out = study.log("maths", mode="true/false", reviews=[{"id": ids[0], "grade": "ok", "level": 1}])
    assert f"{ids[0]} L0→1" in out
    out = study.session("maths", today=EARLY)
    assert "(MAQ/algebra)" in out.splitlines()[0] and "carrying on from last time" in out
    assert f"L1→2 · {ids[0]}" in out and "## Mix in" in out
    assert item_no(out, ids[0]) < item_no(out, ids[1]) and "warm" in first_item(out)  # swept: deepen it first

    study.log("maths", reviews=[{"id": ids[1], "grade": "miss", "level": 2}])
    first = first_item(study.session("maths", today=EARLY))
    assert ids[1] in first and "missed" in first

    study.log("maths", reviews=[{"id": i, "grade": "ok", "level": 3} for i in ids])
    out = study.session("maths", today=EARLY)
    assert "is solid, moving on" in out and "(MAQ/algebra)" not in out.splitlines()[0]
    assert "exam question on Algebra is allowed first" in out
    study.log("maths", "algebra", mode="plan it", score=4, out_of=5)
    assert "exam question" not in study.session("maths", today=EARLY)


def test_session_focus_on_a_section(study):
    out = study.session("maths travel graphs", today=EARLY)
    assert "(MAQ/graphs)" in out.splitlines()[0]
    assert "MAQ/graphs#travel-graphs" in first_item(out)


def test_session_near_exam_has_no_new_ideas(study):
    out = study.session("maths", today=date(2026, 10, 25))
    assert out.startswith("# Session") and "no new ideas" in out and "new→" not in out


# ------------------------------------------------------------ quick-fire

def test_quick_fire_forms(study):
    out = study.drill("maths", n=5)
    assert "L1 true/false]" in out or "L1 multiple choice]" in out
    study.log("maths", "algebra", errors=[{"what": "used 2 s.f.", "fix": "3 s.f.", "type": "slip"}])
    again = study.drill("maths", n=10)
    assert "L2 fix]" in again and "Your old answer (algebra): used 2 s.f.. Fix it." in again
    mem = drill.Memory(S=10, last=datetime.now(timezone.utc), level=3)
    it = {"id": "MAQ/algebra~x", "subject": "MAQ"}
    assert study._card_form(it, mem, datetime.now(timezone.utc), 0.9, EARLY) == (4, "recall")


def test_log_free_modes_and_slip(study):
    ids = [c["id"] for c in study._ideas("MAQ", "algebra")]
    out = study.log("maths", mode="Teach me", reviews=[{"id": ids[0], "grade": "ok", "level": 4},
                                                      {"id": ids[1], "grade": "typo", "level": 2}])
    assert f"{ids[0]} L0→4" in out
    ev = [json.loads(x) for x in (study.cfg.progress_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(e["ev"] == "attempt" and e["mode"] == "teach me" and e.get("level") == 4 for e in ev)
    assert any(e["ev"] == "review" and e["grade"] == "slip" and e["level"] == 2 for e in ev)
    study.log("maths", errors=[{"what": "x", "fix": "y", "type": "fact", "source": ids[0]}])
    assert "· algebra · [fact] x · y ·" in (study.cfg.progress_dir / "MAQ-errors.md").read_text(encoding="utf-8")
