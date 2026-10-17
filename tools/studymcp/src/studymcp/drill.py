"""Adaptive drill: a small memory model per item and the queue that uses it.

Each item (a flashcard or a logged mistake) has a stability S in days: the
time for predicted recall to fall to 90%. Recall after t days is 0.9^(t/S).
An item comes back once recall drops below the target, i.e. just before it
would be forgotten. A miss shrinks S to minutes, so it resurfaces quickly;
a correct answer grows S, more so when recall had already faded (the
spacing effect) and hardly at all when it was asked again too soon.
All numbers come from [drill] in config.toml.
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


def elapsed_days(mem, at):
    return max(0.0, (at - mem.last).total_seconds() / DAY)


def recall(mem, at):
    return 0.9 ** (elapsed_days(mem, at) / max(mem.S, 1e-6))


def due_after(mem, target):
    """days after mem.last at which recall reaches target."""
    return mem.S * math.log(target) / math.log(0.9)


def update(mem, grade, at, p, target=None):
    target = target or p.get("target_recall", 0.9)
    miss_days = p.get("miss_minutes", 10) / 1440
    if mem is None:
        S = {"ok": p.get("first_ok_days", 1.0), "shaky": p.get("first_shaky_days", 0.25)}.get(grade, miss_days)
        return Memory(S, at, 1, 1 if grade == "miss" else 0, grade, 1 if grade == "ok" else 0)
    R = recall(mem, at)
    t = elapsed_days(mem, at)
    if grade == "miss":
        S = max(miss_days, mem.S * p.get("miss_factor", 0.2))
        return replace(mem, S=S, last=at, reps=mem.reps + 1, lapses=mem.lapses + 1, last_grade=grade, streak=0)
    if grade == "shaky":
        growth = p.get("shaky_growth", 1.3)
        factor = 1 + (growth - 1) * min(1.0, (1 - R) / (1 - target))
        S = max(mem.S * factor, t * 0.5)
        return replace(mem, S=S, last=at, reps=mem.reps + 1, last_grade=grade, streak=0)
    growth = p.get("ok_growth", 2.5)
    if R >= target:   # asked again before it was due: little new evidence
        factor = 1 + (growth - 1) * (1 - R) / (1 - target)
    else:             # recalled although it was fading: big boost
        factor = growth * (1 + p.get("difficulty_bonus", 1.0) * (target - R))
    S = max(mem.S * factor, t * 1.2)
    return replace(mem, S=S, last=at, reps=mem.reps + 1, last_grade=grade, streak=mem.streak + 1)


def ago(mem, at):
    mins = elapsed_days(mem, at) * 1440
    return f"{mins:.0f} min" if mins < 90 else (f"{mins / 60:.0f} h" if mins < 2880 else f"{mins / 1440:.0f} days")


def describe(mem, at):
    if mem is None:
        return "new"
    return f"recall {recall(mem, at):.0%}, last {mem.last_grade} {ago(mem, at)} ago, missed {mem.lapses}×"


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
