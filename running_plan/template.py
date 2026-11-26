"""Step 6: weekly template — which days to run, which are quality days (§6.5)."""
from __future__ import annotations

from itertools import combinations

from . import config as C

WEEK = C.DAYS_PER_WEEK


def _circ_dist(a: int, b: int) -> int:
    """Days between two weekdays, wrapping across the week boundary."""
    d = abs(a - b) % WEEK
    return min(d, WEEK - d)


def _days_before(day: int, anchor: int) -> int:
    return (anchor - day) % WEEK


def choose_run_days(n: int, long_run_day: int, unavailable: list[int]) -> list[int]:
    """Pick n run days (including the long-run day) spread as evenly as possible."""
    free = [d for d in range(WEEK) if d not in unavailable or d == long_run_day]
    n = max(1, min(n, len(free)))
    others = [d for d in free if d != long_run_day]
    best, best_score = None, None
    for combo in combinations(others, n - 1):
        days = sorted((*combo, long_run_day))
        consecutive = sum(1 for d in days if (d + 1) % WEEK in days) if n > 1 else 0
        min_gap = min((_circ_dist(a, b) for a, b in combinations(days, 2)), default=WEEK)
        rest_after_lr = (long_run_day + 1) % WEEK not in days
        score = -consecutive * C.TEMPLATE_CONSECUTIVE_DAY_PENALTY + min_gap
        if rest_after_lr and n <= C.TEMPLATE_REST_AFTER_LONG_RUN_MAX_DAYS:
            score += C.TEMPLATE_REST_AFTER_LONG_RUN_BONUS
        if best_score is None or score > best_score:
            best, best_score = days, score
    return best


def choose_quality_days(run_days: list[int], long_run_day: int, wanted: int,
                        preferred: list[int]) -> list[int]:
    """Quality days ≥ 48 h from each other and from the long run (so never the day before it)."""
    gap = C.HARD_DAY_MIN_GAP_DAYS
    candidates = [d for d in run_days if d != long_run_day and _circ_dist(d, long_run_day) >= gap]
    for q in range(wanted, 0, -1):
        best, best_score = None, None
        for combo in combinations(candidates, q):
            hard = (*combo, long_run_day)
            if any(_circ_dist(a, b) < gap for a, b in combinations(hard, 2)):
                continue
            key = max(combo, key=lambda d: _days_before(d, long_run_day))
            score = -abs(_days_before(key, long_run_day) - C.QUALITY_IDEAL_DAYS_BEFORE_LONG_RUN)
            score += sum(C.TEMPLATE_PREFERRED_QUALITY_DAY_BONUS for d in combo if d in preferred)
            if best_score is None or score > best_score:
                best, best_score = list(combo), score
        if best is not None:
            # Slot 0 (key session) is the one furthest before the long run.
            return sorted(best, key=lambda d: -_days_before(d, long_run_day))
    return []
