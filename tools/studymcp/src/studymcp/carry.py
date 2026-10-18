"""The carryover: one short rolling note per subject, so a new chat starts where the last one stopped.

local/progress/carryover/<CODE>.md is rewritten after every log and shown at the top of the
first session brief. It is derived from the event and error logs, so it never drifts; the only
free text in it is the student's "what works" notes (note events). Capped at [carryover] max_chars.

    Economics · 2026-10-17 · stopped: Demand, supply and the market › Minimum wage (mid gap loop)
    retest: Elasticity and labour (link) · Tax incidence (missed)
    plant: "income rise shifts supply" · "elastic = steep"
    swept: markets ✓ · elasticity-failure 3/9
    works: numbers before definitions · T/F in batches of 5
    calibration: guesses right 6/9 · sure but wrong 1/14
"""

import os
from datetime import timedelta

from .state import local_date, parse_time

DEFAULTS = {"max_chars": 800, "session_gap_hours": 2, "retest_sessions": 3, "works": 3,
            "plant": 2, "swept_topics": 3, "calibration_min": 5}


def _clip(text, n):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def session_index(events, gap_hours):
    """study session number of each event (events sorted by time): a gap of gap_hours or more
    starts a new session."""
    out, n, prev = [], -1, None
    gap = timedelta(hours=gap_hours)
    for e in events:
        t = parse_time(e["t"])
        if prev is None or t - prev >= gap:
            n += 1
        out.append(n)
        prev = t
    return out


def build(code, name, events, errors, mems, title, topic_title, idea_ids, at, p=None, sweep_days=5):
    """the carryover text for one subject ("" when there is no history).

    title(id) -> idea title; topic_title(stem) -> topic title; idea_ids(stem) -> ids on that page."""
    p = {**DEFAULTS, **(p or {})}
    evs = sorted((e for e in events if e.get("subject") == code and e.get("t")), key=lambda e: parse_time(e["t"]))
    if not evs:
        return ""
    sess = session_index(evs, p["session_gap_hours"])
    last_sess = sess[-1]
    reviews = [(e, s) for e, s in zip(evs, sess) if e.get("ev") == "review" and e.get("item")]

    head = f"{name} · {local_date(parse_time(evs[-1]['t'])).isoformat()}"
    if reviews:
        e = reviews[-1][0]
        where = topic_title(e.get("topic", ""))
        if "#" in e["item"]:
            where += f" › {title(e['item'])}"
        head += f" · stopped: {where}" + (" (mid gap loop)" if e.get("grade") in ("miss", "shaky") else "")
    head = _clip(head, 200)

    latest = {}
    for e, s in reviews:
        if "#" in e["item"]:
            latest[e["item"]] = (e, s)
    err_type = {}
    for x in errors:
        if x.subject == code and x.source:
            err_type[x.source] = x.type
    retest = []
    for item, (e, s) in sorted(latest.items(), key=lambda kv: kv[1][0]["t"], reverse=True):
        if e.get("grade") in ("miss", "shaky") and last_sess - s < p["retest_sessions"]:
            label = err_type.get(item) or ("missed" if e["grade"] == "miss" else "shaky")
            retest.append(f"{_clip(title(item), 50)} ({label})")

    plant = []
    for x in reversed([x for x in errors if x.subject == code]):
        m = mems.get(x.id)
        if m is None or m.last_grade != "ok":
            plant.append(f'"{_clip(x.what, 60)}"')
        if len(plant) >= p["plant"]:
            break

    swept, done = [], set()
    window = at - timedelta(days=sweep_days)
    for e, _ in reversed(reviews):
        stem = e.get("topic", "")
        if "#" not in e["item"] or not stem or stem in done:
            continue
        done.add(stem)
        ids = idea_ids(stem)
        if ids:
            recent = {i for i in ids if i in latest and parse_time(latest[i][0]["t"]) >= window}
            swept.append(f"{stem} ✓" if len(recent) == len(ids) else f"{stem} {len(recent)}/{len(ids)}")
        if len(done) >= p["swept_topics"]:
            break

    works = [_clip(e.get("text", ""), 60) for e in evs if e.get("ev") == "note" and e.get("text")]
    works = list(reversed(works))[: p["works"]]

    guesses = [e for e, _ in reviews if e.get("conf") == "guess"]
    sure = [e for e, _ in reviews if e.get("conf") == "sure"]
    calib = ""
    if len(guesses) + len(sure) >= p["calibration_min"]:
        parts = []
        if guesses:
            parts.append(f"guesses right {sum(e.get('grade') != 'miss' for e in guesses)}/{len(guesses)}")
        if sure:
            parts.append(f"sure but wrong {sum(e.get('grade') == 'miss' for e in sure)}/{len(sure)}")
        calib = "calibration: " + " · ".join(parts)

    lists = [["retest", retest], ["plant", plant], ["swept", swept], ["works", works]]

    def render():
        lines = [head] + [f"{k}: " + " · ".join(v) for k, v in lists if v]
        return "\n".join(lines + ([calib] if calib else []))

    text = render()
    while len(text) > p["max_chars"] and any(v for _, v in lists):
        max(lists, key=lambda kv: len(" · ".join(kv[1])))[1].pop()
        text = render()
    return text[: p["max_chars"]]


def write(folder, code, text):
    """atomically replace local/progress/carryover/<CODE>.md."""
    folder.mkdir(parents=True, exist_ok=True)
    f = folder / f"{code}.md"
    tmp = folder / f".{code}.md.tmp"
    tmp.write_text(text + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, f)
    return f
