"""Sweeps, warm ideas, the carryover, the one-line log, the prep bank and paired subjects."""

import json
import re
from datetime import date, datetime, timedelta, timezone

from studymcp import bank, carry
from studymcp.ideas import idea_hash
from studymcp.state import ErrorEntry

EARLY = date(2026, 10, 1)
NOW = datetime.now(timezone.utc)


def algebra(study):
    return [c["id"] for c in study._ideas("MAQ", "algebra")]


def events(study):
    return [json.loads(x) for x in (study.cfg.progress_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()]


def add_events(study, evs):
    f = study.cfg.progress_dir / "events.jsonl"
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a", encoding="utf-8") as out:
        for e in evs:
            out.write(json.dumps(e) + "\n")


def review(item, grade, t, level=None, topic="algebra"):
    e = {"t": t.isoformat(timespec="seconds"), "ev": "review", "subject": "MAQ", "topic": topic, "item": item,
         "grade": grade}
    return {**e, "level": level} if level else e


def bank_draft(study, ids, links=()):
    d = study.bank.draft_path("MAQ", "algebra")
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(json.dumps({"ideas": {i: {
        "gist": f"Plain gist for {i.split('#')[1]}.", "weight": "high",
        "statements": [{"text": "The quadratic formula solves any quadratic.", "true": True},
                       {"text": "The quadratic formula only solves quadratics that factorise.", "true": False,
                        "fix": "It solves any quadratic.", "change": "always"},
                       {"text": "The ± gives two roots.", "true": True}],
        "mixups": ["factorising vs the formula"], "links": list(links)} for i in ids},
        "flags": [f"{ids[0]}: thin notes"]}), encoding="utf-8")


# ------------------------------------------------------------------ sweeps

def test_level_one_ok_is_warm_never_solid(study):
    ids = algebra(study)
    for _ in range(3):
        study.log("maths", mode="sweep", reviews=[{"id": ids[0], "grade": "ok", "level": 1}])
    mem = study.state.memories()[ids[0]]
    assert mem.level == 1 and study._idea_state(mem, NOW, 0.9) == "warm"


def test_untouched_topic_sweeps_again(study):
    old = NOW - timedelta(days=6)
    add_events(study, [review(i, "ok", old, 3) for i in algebra(study)])
    out = study.session("maths algebra", today=EARLY)
    assert out.startswith("# Sweep · Mathematics · Algebra") and "why: untouched 6 days" in out


def test_sweep_on_request(study):
    ids = algebra(study)
    study.log("maths", reviews=[{"id": ids[0], "grade": "ok", "level": 2}])
    out = study.session("maths", "algebra", today=EARLY, sweep=True)
    assert out.startswith("# Sweep · Mathematics · Algebra") and "why: you asked" in out
    assert all(i in out for i in ids)
    whole = study.session("maths", today=EARLY, sweep=True)
    assert whole.startswith("# Sweep · Mathematics · whole subject") and "MAQ/graphs#" in whole


def test_day_before_the_exam_sweeps_seen_ideas_only(study):
    ids = algebra(study)
    study.log("maths", mode="fix it", reviews=[{"id": ids[0], "grade": "ok", "level": 2}])
    out = study.session("maths", today=date(2026, 10, 26))
    assert out.startswith("# Sweep · Mathematics · whole subject") and "exam tomorrow" in out
    assert ids[0] in out and ids[1] not in out and "MAQ/graphs#" not in out  # nothing new
    study.log("maths", mode="sweep", reviews=[{"id": ids[0], "grade": "ok", "level": 1}])
    assert study.session("maths", today=date(2026, 10, 26)).startswith("# Session")  # swept today: deepen


def test_after_the_day_before_sweep_only_its_misses_are_deepened(study):
    ids = algebra(study)
    study.log("maths", mode="fix it", reviews=[{"id": i, "grade": "ok", "level": 2} for i in ids[:2]])
    study.log("maths", mode="sweep", reviews=[{"id": ids[0], "grade": "miss", "level": 1},
                                              {"id": ids[1], "grade": "ok", "level": 1}])
    out = study.session("maths", today=date(2026, 10, 26))
    assert out.startswith("# Session · Mathematics · misses from today's sweep")
    assert ids[0] in out and ids[1] not in out
    study.log("maths", reviews=[{"id": ids[0], "grade": "ok", "level": 3}])
    assert "misses from today's sweep" not in study.session("maths", today=date(2026, 10, 26))


def test_exam_question_once_per_study_session(study):
    ids = algebra(study)
    add_events(study, [{"t": (NOW - timedelta(hours=3)).isoformat(timespec="seconds"), "ev": "attempt",
                        "subject": "MAQ", "topic": "algebra", "mode": "plan it", "score": 4, "out_of": 5}])
    study.log("maths", reviews=[{"id": i, "grade": "ok", "level": 3} for i in ids])
    assert "exam question on Algebra is allowed first" in study.session("maths", today=EARLY)  # earlier session
    study.log("maths", "algebra", mode="plan it", score=4, out_of=5)
    assert "exam question" not in study.session("maths", today=EARLY)


def test_two_days_out_mixes_half_the_brief(study, monkeypatch):
    asked, real = [], study._mix_in
    monkeypatch.setattr(study, "_mix_in", lambda code, stem, k, *a: asked.append(k) or real(code, stem, k, *a))
    study.log("maths", reviews=[{"id": algebra(study)[0], "grade": "ok", "level": 2}])
    study.session("maths algebra", today=EARLY)
    assert "no new ideas" in study.session("maths algebra", today=date(2026, 10, 25))
    assert asked == [3, 4]  # of 8 ideas: 3 mixed in normally, half when the exam is 2 days off


def test_sent_ideas_come_back_as_one_line(study):
    ids = algebra(study)
    study.log("maths", reviews=[{"id": i, "grade": "ok", "level": 1} for i in ids])
    first = study.session("maths algebra", today=EARLY)
    again = study.session("maths algebra", today=EARLY)
    assert "↺" not in first.split("## Mix in")[0]
    assert f"{ids[0]} · Quadratics" in again and " ↺" in again and len(again) < len(first)
    study.log("maths", reviews=[{"id": ids[0], "grade": "miss", "level": 2}])
    assert next(l for l in study.session("maths algebra", today=EARLY).splitlines() if ids[0] in l)[-1] != "↺"


def test_level_cap(study, monkeypatch):
    monkeypatch.setitem(study.cfg.levels, "cap_subjects", {"MAQ": 2})
    ids = algebra(study)
    study.log("maths", reviews=[{"id": i, "grade": "ok", "level": 3} for i in ids[:1]] +
              [{"id": ids[1], "grade": "ok", "level": 1}])
    out = study.session("maths algebra", today=EARLY)
    assert "level 2 at most" in out and "→3" not in out


# ------------------------------------------------------------ log, carryover

def test_log_is_one_line_with_note_and_conf(study):
    ids = algebra(study)
    out = study.log("maths", mode="sweep", note="examples first",
                    reviews=[{"id": ids[0], "grade": "shaky", "level": 1, "conf": "?"},
                             {"id": ids[1], "grade": "miss", "level": 1, "conf": "sure"},
                             {"id": "MAQ/nope#x", "grade": "ok"}],
                    errors=[{"what": "thought it needs factorising", "fix": "QF works for any quadratic",
                             "type": "mix-up", "source": ids[1]}])
    assert "\n" not in out and out.startswith("Logged 2 (1 shaky, 1 miss), 1 error, note")
    assert "unknown id MAQ/nope#x" in out
    ev = events(study)
    assert {e.get("conf") for e in ev if e["ev"] == "review"} == {"guess", "sure"}
    assert any(e["ev"] == "note" and e["text"] == "examples first" for e in ev)


def test_carryover_is_rewritten_after_every_log(study):
    ids = algebra(study)
    study.log("maths", mode="sweep", note="batches of 5",
              reviews=[{"id": ids[0], "grade": "ok", "level": 1}, {"id": ids[1], "grade": "miss", "level": 1}],
              errors=[{"what": "thought it needs factorising", "fix": "any quadratic", "type": "mix-up",
                       "source": ids[1]}])
    text = (study.cfg.progress_dir / "carryover" / "MAQ.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0].startswith("Mathematics · ") and "stopped: Algebra › " in lines[0] and "(mid gap loop)" in lines[0]
    assert "retest: " in text and "(mix-up)" in text
    assert 'plant: "thought it needs factorising"' in text
    assert "swept: algebra ✓" in text and "works: batches of 5" in text
    study.log("maths", reviews=[{"id": ids[1], "grade": "ok", "level": 3}])
    text = (study.cfg.progress_dir / "carryover" / "MAQ.md").read_text(encoding="utf-8")
    assert "retest" not in text and "(mid gap loop)" not in text


def test_first_brief_carries_over_once(study):
    study.log("maths", reviews=[{"id": algebra(study)[0], "grade": "ok", "level": 1}], note="examples first")
    assert "Last time:\n  Mathematics · " in study.session("maths", today=EARLY)
    assert "Last time:" not in study.session("maths", today=EARLY)


def test_retest_drops_after_three_untouched_sessions():
    t0 = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)
    evs = [review("MAQ/a#x", "miss", t0, 2), review("MAQ/a#y", "ok", t0, 2)]
    build = lambda e: carry.build("MAQ", "Maths", e, [], {}, lambda i: i, lambda s: s, lambda s: [], t0)
    for k in range(1, 4):
        evs.append(review("MAQ/a#y", "ok", t0 + timedelta(hours=3 * k), 2))
        assert ("MAQ/a#x (missed)" in build(evs)) == (k < 3)


def test_carryover_cap_and_calibration():
    t0 = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)
    evs = [{**review(f"MAQ/a#idea-with-a-long-name-{i}", "miss", t0 + timedelta(minutes=i), 1), "conf": "sure"}
           for i in range(40)]
    evs += [{"t": t0.isoformat(), "ev": "note", "subject": "MAQ", "text": "x" * 70} for _ in range(5)]
    errs = [ErrorEntry(f"ERR/MAQ/{i}", "MAQ", "2026-10-01", "a", "w" * 90, "f") for i in range(5)]
    text = carry.build("MAQ", "Maths", evs, errs, {}, lambda i: i.split("#")[1], lambda s: s, lambda s: [], t0)
    assert len(text) <= 800 and "retest: " in text and "calibration: sure but wrong 40/40" in text


# --------------------------------------------------------------------- bank

def test_bank_save_validates_and_feeds_the_session(study):
    ids = algebra(study)
    prep = study.prep("maths", "algebra")
    assert "Write the draft to: local/bank/MAQ/algebra.draft.json" in prep and "Ideas to build (2)" in prep
    assert all(f"### {i}" in prep for i in ids)

    bank_draft(study, ids[:1])
    assert "missing ideas: " + ids[1] in study.bank_save("maths", "algebra")
    bank_draft(study, ids)
    saved = study.bank_save("maths", "algebra")
    assert saved.startswith("saved MAQ/algebra: 2 ideas, 1 flags")
    assert "3 statements; its notes deserve about 4" in saved  # thin: a warning, not an error
    data = json.loads(study.bank.path("MAQ", "algebra").read_text(encoding="utf-8"))
    texts = {c["id"]: c["text"] for c in study._ideas("MAQ", "algebra")}
    assert all(data["ideas"][i]["hash"] == idea_hash(texts[i]) for i in ids)
    assert "MAQ algebra: built · 2 thin · 1 flags" in study.bank_status("maths")
    assert "Statements: 4 or more" in study.prep("maths", "algebra", thin=True)

    study.log("maths", reviews=[{"id": i, "grade": "ok", "level": 1} for i in ids])
    out = study.session("maths algebra", today=EARLY)
    assert "Plain gist for" in out and 'F: "The quadratic formula only solves' in out
    assert "Bank missing" not in out.split("## Mix in")[0]


def test_bank_warns_about_wording_and_weights():
    cs = [{"id": f"X/p#{i}", "text": "x" * 400} for i in "abcd"]
    st = [{"text": "Fact one.", "true": True}, {"text": "Fact two.", "true": True},
          {"text": "Wrong one.", "true": False, "fix": "Right one.", "change": "direction"},
          {"text": "The notes say a list is best.", "true": True}]
    draft = {"ideas": {c["id"]: {"gist": "The plan argues one thing.", "weight": "high", "statements": st}
                       for c in cs}}
    errors, warnings = bank.validate(draft, cs)
    assert not errors and any("is about the notes" in w and "The plan argues" in w for w in warnings)
    assert any("The notes say" in w for w in warnings)
    too_many = {"ideas": {"X/p#a": {"gist": "g", "weight": "low", "statements": st * 5}}}
    assert any("20 statements (at most 16)" in e for e in bank.validate(too_many, cs[:1])[0])
    assert bank.recommended("x" * 400) == 4 and bank.recommended("x" * 4000) == 8 and bank.recommended("x" * 90000) == 12


def test_sweeps_scale_and_continue(study, monkeypatch):
    ids = algebra(study)
    d = study.bank.draft_path("MAQ", "algebra")
    d.parent.mkdir(parents=True, exist_ok=True)
    st = [{"text": f"True fact {k}.", "true": True} for k in range(3)] + \
         [{"text": f"False fact {k}.", "true": False, "fix": "x", "change": "direction"} for k in range(3)]
    d.write_text(json.dumps({"ideas": {i: {"gist": "g", "weight": "high", "statements": st} for i in ids}}),
                 encoding="utf-8")
    study.bank_save("maths", "algebra")
    out = study.session("maths", "algebra", today=EARLY, sweep=True)
    assert "6 statements on 2 ideas" in out and "`T F left T T? F ear`" in out  # 2 ideas: 3 each
    assert out.count('   T: "') + out.count('   F: "') == 6
    monkeypatch.setitem(study.cfg.caps, "sweep", len(out) - 150)  # too small for both ideas
    study._swept.clear()
    first = study.session("maths", "algebra", today=EARLY, sweep=True)
    assert "(+1 more ideas: session('MAQ', 'algebra', sweep=true) for the rest of this sweep)" in first
    rest = study.session("maths", "algebra", today=EARLY, sweep=True)
    shown = [line.split()[-1] for line in rest.splitlines() if re.match(r"\d+\. ", line)]
    assert "· continued" in rest and shown == [ids[1]]
    fresh = study.session("maths", "algebra", today=EARLY, sweep=True)  # all sent: a new sweep
    assert "continued" not in fresh.splitlines()[0] and ids[0] in fresh


def test_edited_notes_make_the_bank_stale(study, repo):
    ids = algebra(study)
    bank_draft(study, ids)
    study.bank_save("maths", "algebra")
    f = repo / "T4-MAQ" / "notes" / "algebra.md"
    f.write_text(f.read_text(encoding="utf-8").replace("solves any quadratic.",
                                                       "solves any quadratic, every time."), encoding="utf-8")
    study.ready()
    assert "MAQ algebra: stale (1/2 ideas)" in study.bank_status("maths")
    out = study.session("maths algebra", today=EARLY, sweep=True)
    assert "Bank missing or out of date: MAQ algebra (1 ideas changed)" in out and "(no bank yet)" in out
    assert "MAQ algebra" not in study.session("maths algebra", today=EARLY, sweep=True).split("Bank")[-1]
    assert "Partial rebuild: only the 1 ideas below" in study.prep("maths", "algebra")


def test_paired_subject_mix_in(study, monkeypatch):
    monkeypatch.setitem(study.cfg.session, "pairs", {"MAQ": ["GEQ"]})
    ids = algebra(study)
    bank_draft(study, ids, links=["GEQ/rivers#erosion"])
    study.bank_save("maths", "algebra")
    study.log("maths", reviews=[{"id": i, "grade": "ok", "level": 1} for i in ids])
    out = study.session("maths algebra", today=EARLY)
    assert "GEQ/rivers#erosion · Rivers (Geography)" in out.split("## Mix in")[1]
