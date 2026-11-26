"""Independent re-check of a generated plan against the safety rules (§6).

The generator should never produce violations. Tests run this over many profiles.
"""
from __future__ import annotations

from . import config as C
from .models import Week
from .workouts import dose_km



def long_run_share_cap(days: int) -> float:
    return C.LONG_RUN_SHARE.get(days, C.LONG_RUN_SHARE_DEFAULT)


def validate(weeks: list[Week], initial_history: list[tuple[int, float]], start_volume: float,
             min_easy_share: float) -> list[str]:
    errors: list[str] = []
    history = list(initial_history)

    def max30(day: int) -> float:
        return max((km for d, km in history if day - C.SPIKE_WINDOW_DAYS <= d < day), default=0.0)

    prev_hard_day = None
    for w in weeks:
        for day in w.days:
            wo = day.workout
            idx = (w.index - 1) * C.DAYS_PER_WEEK + day.weekday
            if wo.type == "rest":
                continue
            ref = max30(idx)
            if (not wo.is_race and wo.type != "RunWalk" and ref > 0
                    and wo.km > C.SPIKE_LIMIT * ref + C.VALIDATE_KM_TOLERANCE):
                errors.append(f"wk{w.index} {day.weekday}: {wo.km} km > 110% of 30-day max {ref}")
            hard = wo.is_quality and wo.type not in ("HillSprint",)
            if hard:
                if prev_hard_day is not None and idx - prev_hard_day < C.HARD_DAY_MIN_GAP_DAYS:
                    errors.append(f"wk{w.index} {day.weekday}: hard sessions on consecutive days")
                prev_hard_day = idx
            for zone, km in wo.zone_km.items():
                if zone in C.DOSE_CAP and wo.type != "TT":
                    cap = dose_km(zone, max(w.target_km, w.total_km))
                    if km > cap + C.VALIDATE_KM_TOLERANCE:
                        errors.append(f"wk{w.index} {wo.type}: {km} km @ {zone} > cap {cap:.1f}")
            history.append((idx, wo.km))

        if w.phase != "race" and w.easy_share < min_easy_share - C.VALIDATE_SHARE_TOLERANCE:
            errors.append(f"wk{w.index}: easy share {w.easy_share:.0%} < {min_easy_share:.0%}")
        lr = w.long_run
        run_days = sum(1 for d in w.days if d.workout.type != "rest")
        if lr and lr.km > long_run_share_cap(run_days) * max(w.target_km, w.total_km) \
                + C.VALIDATE_LONG_RUN_SHARE_TOLERANCE_KM:
            errors.append(f"wk{w.index}: long run {lr.km} km over share cap")

    # Weekly ramp, measured against the last non-down week (down weeks are not the baseline).
    ref_totals: list[float] = [start_volume]
    for w in weeks:
        if w.phase in ("taper", "race", "recovery"):
            continue
        base = ref_totals[-1]
        if base > 0 and w.total_km > (1 + C.MAX_WEEKLY_INCREASE) * base + C.VALIDATE_RAMP_TOLERANCE_KM:
            errors.append(f"wk{w.index}: {w.total_km} km is >20% above {base}")
        if len(ref_totals) >= 2 and ref_totals[-2] > 0 and \
                w.total_km > (1 + C.MAX_TWO_WEEK_INCREASE) * ref_totals[-2] \
                + C.VALIDATE_RAMP_TOLERANCE_KM:
            errors.append(f"wk{w.index}: {w.total_km} km is >30% above two build weeks ago")
        if not w.is_down_week:
            ref_totals.append(w.total_km)
    return errors
