"""Adaptive drill: a small memory model per item and the queue that uses it.

Each item (a flashcard or a logged mistake) has a stability S in days: the
time for predicted recall to fall to 90%. Recall after t days is 0.9^(t/S).
An item comes back once recall drops below the target, i.e. just before it
would be forgotten. A miss shrinks S to minutes, so it resurfaces quickly;
a correct answer grows S, more so when recall had already faded (the
spacing effect) and hardly at all when it was asked again too soon.

Each item also has a level, 0 to 5: how hard a task the student can do on
it (1 spot it, 2 fix it, 3 build it, 4 explain it, 5 from memory). An answer
at level r moves it: ok -> at least r, shaky -> max(level, r) - 1 (a doubtful
answer drops it by one at most), miss -> at most r - 1, slip -> unchanged.
Level 1 is the sweep (fast true/false); deeper tasks start at 2. Easy tasks
grow S less (credit per level), so a true/false counts for less than a blurt.
Numbers come from [drill] and [levels] in config.toml.
"""

import math
from dataclasses import dataclass, replace
from datetime import datetime

DAY = 86400.0


@dataclass
class Memory:
    S: float               # stability, days
    last: datetime
    reps: int = 0
    lapses: int = 0
    last_grade: str = ""
    streak: int = 0         # correct answers in a row
    level: int = 0          # highest level answered solidly (0 = never)
    last_level: int = 0     # level of the latest answer (1 = a sweep)


def elapsed_days(mem, at):
    return max(0.0, (at - mem.last).total_seconds() / DAY)


def recall(mem, at):
    return 0.9 ** (elapsed_days(mem, at) / max(mem.S, 1e-6))


def due_after(mem, target):
    """days after mem.last at which recall reaches target."""
    return mem.S * math.log(target) / math.log(0.9)


def credit(level, p):
    """how much an answer at this level counts towards S growth (1.0 when unknown)."""
    cr = p.get("credit") or []
    if not level or not cr:
        return 1.0
    return cr[min(int(level), len(cr)) - 1]


def new_level(old, grade, r):
    if not r:  # no level given (older events): small steps
        return max(old, 1) if grade == "ok" else max(0, old - 1) if grade == "miss" else old
    r = max(1, min(int(r), 5))
    if grade == "ok":
        return max(old, r)
    if grade == "shaky":
        return max(old, r) - 1
    if grade == "miss":
        return min(old, r - 1)
    return old  # slip: a careless error, not a gap


def update(mem, grade, at, p, target=None, level=None):
    """p holds [drill] plus the [levels] credit list. grade: ok | shaky | slip | miss."""
    target = target or p.get("target_recall", 0.9)
    miss_days = p.get("miss_minutes", 10) / 1440
    k = credit(level, p)
    lv = int(level or 0)
    if mem is None:
        S = {"ok": p.get("first_ok_days", 1.0) * k, "shaky": p.get("first_shaky_days", 0.25) * k,
             "slip": p.get("first_shaky_days", 0.25) * k}.get(grade, miss_days)
        return Memory(S, at, 1, 1 if grade == "miss" else 0, grade, 1 if grade == "ok" else 0,
                      new_level(0, grade, level), lv)
    R = recall(mem, at)
    t = elapsed_days(mem, at)
    lvl = new_level(mem.level, grade, level)
    if grade == "miss":
        S = max(miss_days, mem.S * p.get("miss_factor", 0.2))
        return replace(mem, S=S, last=at, reps=mem.reps + 1, lapses=mem.lapses + 1, last_grade=grade,
                       streak=0, level=lvl, last_level=lv)
    if grade in ("shaky", "slip"):
        growth = p.get("shaky_growth", 1.3)
        factor = 1 + (growth - 1) * min(1.0, (1 - R) / (1 - target)) * k
        S = max(mem.S * factor, t * 0.5)
        return replace(mem, S=S, last=at, reps=mem.reps + 1, last_grade=grade, streak=0, level=lvl, last_level=lv)
    growth = p.get("ok_growth", 2.5)
    if R >= target:   # asked again before it was due: little new evidence
        factor = 1 + (growth - 1) * (1 - R) / (1 - target)
    else:             # recalled although it was fading: big boost
        factor = growth * (1 + p.get("difficulty_bonus", 1.0) * (target - R))
    factor = 1 + (factor - 1) * k
    S = max(mem.S * factor, t * 1.2 * k)
    return replace(mem, S=S, last=at, reps=mem.reps + 1, last_grade=grade, streak=mem.streak + 1, level=lvl,
                   last_level=lv)


def next_level(mem, at, target, days_to_exam=None, p=None, floor=1, cap=5):
    """the level of the next task on this item: one above its level, one lower if fading,
    at least `floor` for seen items (2 in sessions: level 1 is the sweep), at least 3 for
    seen items in the last days before the exam (less support), and at most `cap`."""
    p = p or {}
    if mem is None:
        return min(1, cap)
    nxt = mem.level + 1
    if mem.last_grade != "miss" and recall(mem, at) < target:
        nxt -= 1
    nxt = max(floor, 1, min(nxt, 5))
    if days_to_exam is not None and 0 <= days_to_exam <= p.get("exam_floor_days", 3):
        nxt = max(nxt, 3)
    return min(nxt, cap)


def ago(mem, at):
    mins = elapsed_days(mem, at) * 1440
    return f"{mins:.0f} min" if mins < 90 else (f"{mins / 60:.0f} h" if mins < 2880 else f"{mins / 1440:.0f} days")


def describe(mem, at):
    if mem is None:
        return "new"
    return f"level {mem.level}, recall {recall(mem, at):.0%}, last {mem.last_grade} {ago(mem, at)} ago, missed {mem.lapses}×"


def select(items, mems, at, n, focus, importance, target_for, p):
    """choose the next n items.

    items: list of dicts with id, subject, topic.  importance(item) -> 0..1.
    Returns [(item, reason)] — reason is shown to the student.
    """
    missed, due, fresh = [], [], []
    for it in items:
        m = mems.get(it["id"])
        if m is None:
            fresh.append(it)
            continue
        R = recall(m, at)
        tgt = target_for(it["subject"])
        if m.last_grade == "miss":
            missed.append((m.last, it, f"missed {ago(m, at)} ago" + (f" ({m.lapses}× total)" if m.lapses > 1 else "")))
        elif R < tgt:
            due.append(((1 - R) * (0.5 + importance(it)), it, f"fading: recall {R:.0%}"))
    missed.sort(key=lambda x: x[0])
    due.sort(key=lambda x: -x[0])
    fresh.sort(key=lambda it: (-importance(it), it.get("order", 0)))
    fresh = _round_robin(fresh)

    if focus == "missed":
        pool = [(it, why) for _, it, why in missed] + [(it, why) for _, it, why in due]
        return pool[:n]
    if focus == "new":
        return [(it, "new") for it in fresh[:n]]

    picked = [(it, why) for _, it, why in missed[:n]]
    room = n - len(picked)
    reserve = min(len(fresh), max(1, round(n * p.get("new_share", 0.3)))) if fresh else 0
    take_due = min(len(due), max(room - reserve, 0))
    picked += [(it, why) for _, it, why in due[:take_due]]
    picked += [(it, "new" + (f", tier {it['tier']}" if it.get("tier") else "")) for it in fresh[: n - len(picked)]]
    if len(picked) < n:  # nothing new left: top up with the least-fading items
        rest = [(it, "review") for _, it, _ in due[take_due:]]
        picked += rest[: n - len(picked)]
    return _interleave(picked)


def _round_robin(fresh, width=3):
    """new items from the top few topics in turn (interleaved practice), not one deck at a time."""
    buckets = {}
    for it in fresh:
        buckets.setdefault((it["subject"], it["topic"]), []).append(it)
    queue, active, out = list(buckets.values()), [], []
    while queue or active:
        while queue and len(active) < width:
            active.append(queue.pop(0))
        for b in list(active):
            out.append(b.pop(0))
            if not b:
                active.remove(b)
    return out


def _interleave(picked):
    """keep misses first, then alternate due and new so a batch is not all new."""
    head = [x for x in picked if x[1].startswith("missed")]
    due = [x for x in picked if x[1].startswith("fading") or x[1] == "review"]
    new = [x for x in picked if x[1].startswith("new")]
    out = list(head)
    while due or new:
        if due:
            out.append(due.pop(0))
        if new:
            out.append(new.pop(0))
    return out
