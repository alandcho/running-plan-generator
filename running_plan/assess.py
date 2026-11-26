"""Steps 2-4: fitness estimate, two-axis classification, goal feasibility."""
from __future__ import annotations

import math

from . import config as C
from .models import Assessment, Goal, Profile
from .vdot import (BISECTION_ITERATIONS, DISTANCES_M, REPS_400M_PER_KM, fmt_duration,
                   parse_duration_min, predict_time_min, training_paces, vdot)

PERCENT = 100


def _interp(x: float, table: tuple[tuple[float, float], ...]) -> float:
    if x <= table[0][0]:
        return table[0][1]
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return table[-1][1]


def detraining(days_off: int, cross_trained: bool = False) -> tuple[float, float]:
    """(VDOT multiplier, volume restart fraction) after `days_off` without running."""
    for max_days, mult, vol in C.DETRAINING:
        if days_off <= max_days:
            if cross_trained:
                mult = 1 - (1 - mult) / 2
            return mult, vol
    raise AssertionError("unreachable")


def fm_penalty(weekly_km: float) -> float:
    return _interp(weekly_km, C.FM_PENALTY)


def current_vdot(p: Profile, goal_distance: str | None = None) -> tuple[float | None, str]:
    """Recency-decayed VDOT from all-out races (§4.1), else an easy-pace estimate.

    If results disagree by more than RESULT_DISAGREEMENT_VDOT, weight them by how close
    their distance is to the goal distance, so a fast 5k does not set marathon paces.
    """
    cands = []
    for r in p.race_results:
        if not r.all_out or r.weeks_ago > C.RACE_MAX_AGE_WEEKS:
            continue
        v = vdot(DISTANCES_M[r.distance], parse_duration_min(r.time))
        stale = max(0.0, r.weeks_ago - C.RACE_FULL_WEIGHT_WEEKS)
        cands.append((v * (1 - C.RACE_DECAY_PER_WEEK * stale), r))
    best, src = None, "none"
    if cands:
        values = [v for v, _ in cands]
        if goal_distance and max(values) - min(values) > C.RESULT_DISAGREEMENT_VDOT:
            gd = DISTANCES_M[goal_distance]
            weights = [1 / (1 + abs(math.log(DISTANCES_M[r.distance] / gd))) for _, r in cands]
            best = sum(w * v for w, (v, _) in zip(weights, cands)) / sum(weights)
            src = "distance-weighted: " + ", ".join(f"{r.distance} {r.time}" for _, r in cands)
        else:
            best, r = max(cands, key=lambda c: c[0])
            src = f"{r.distance} {r.time} ({r.weeks_ago:g} wk ago)"
    if best is None and p.easy_pace_s_per_km:
        best, src = vdot_from_easy_pace(p.easy_pace_s_per_km), "estimated from easy pace (low confidence)"
    if best is not None:
        mult, _ = detraining(p.days_off_recent, p.cross_trained_during_break)
        if mult < 1:
            src += f"; ×{mult:.2f} for {p.days_off_recent} days off"
        best *= mult
    return best, src


def vdot_from_easy_pace(pace_s_per_km: float) -> float:
    """VDOT whose easy-zone midpoint equals the runner's easy pace (bisection)."""
    lo, hi = C.VDOT_SEARCH_RANGE
    for _ in range(BISECTION_ITERATIONS):
        mid = (lo + hi) / 2
        p = training_paces(mid)
        # Map to the FAST end of E: recreational runners usually run easy too fast (§4.1).
        if p["E_fast"] > pace_s_per_km:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def age_grade_pct(distance: str, time_min: float, age: int, sex: str) -> float:
    # Unknown sex uses the male standard, which gives the LOWER (more conservative) grade.
    std = C.AGE_GRADE_STANDARD_S[sex if sex in ("M", "F") else "M"][distance]
    factor = 1.0
    for a0, a1, rate in C.AGE_SLOWDOWN:
        if age > a0:
            factor += (min(age, a1) - a0) * rate
    return PERCENT * std * factor / (time_min * C.SECONDS_PER_MINUTE)


def best_age_grade(p: Profile) -> float | None:
    grades = [age_grade_pct(r.distance, parse_duration_min(r.time), p.age, p.sex)
              for r in p.race_results if r.all_out and r.weeks_ago <= C.RACE_MAX_AGE_WEEKS]
    return max(grades) if grades else None


def _tier_from(value: float, bounds: tuple[float, float]) -> int:
    return 0 if value < bounds[0] else 1 if value <= bounds[1] else 2


def load_tier(p: Profile) -> str:
    vol = _tier_from(p.weekly_volume_km, C.LOAD_VOLUME_KM)
    lr = _tier_from(p.longest_run_30d_km, C.LOAD_LONG_RUN_KM)
    age = _tier_from(p.training_age_years, C.LOAD_TRAINING_AGE_YR)
    # Training age may lower the tier by at most one step (§3.1).
    # Volume is primary; long run and training age may each lower it by at most one step (§3.1).
    return C.TIERS[min(vol, lr + 1, age + 1, len(C.TIERS) - 1)]


def perf_tier(age_grade: float | None) -> str:
    if age_grade is None:
        return "developing"
    return C.PERF_TIERS[_tier_from(age_grade, C.PERF_AGE_GRADE)]


def feasibility(goal: Goal, v_cur: float | None, perf: str, weeks: int,
                weekly_km: float) -> tuple[str, float | None, str | None]:
    """Return (status, goal VDOT, realistic target time)."""
    if goal.type != "race" or goal.objective == "finish" or not goal.target_time or v_cur is None:
        return "n/a", None, None
    d = DISTANCES_M[goal.distance]
    v_goal = vdot(d, parse_duration_min(goal.target_time))
    v_ref = v_cur
    if goal.distance == "FM":
        # Marathon predictions are optimistic at low volume: compare like with like.
        pred = predict_time_min(v_cur, d) * (1 + fm_penalty(weekly_km))
        v_ref = vdot(d, pred)
    lo_scale, hi_scale = C.FEASIBILITY_SCALE_BOUNDS
    scale = max(lo_scale, min(hi_scale, weeks / C.FEASIBILITY_REF_WEEKS))
    lo, hi = (g * scale for g in C.VDOT_GAIN_RANGE[perf])
    mid = (lo + hi) / 2
    delta = v_goal - v_ref
    realistic = predict_time_min(v_ref + mid, d)  # v_ref already carries the FM penalty
    real_str = fmt_duration(realistic * C.SECONDS_PER_MINUTE)
    if delta < C.CONSERVATIVE_GOAL_DELTA_VDOT:
        return "conservative", v_goal, real_str
    if delta <= mid:
        return "accepted", v_goal, None
    if delta <= hi:
        return "stretch", v_goal, real_str
    return "unrealistic", v_goal, real_str


def assess(p: Profile, goal: Goal, weeks: int) -> Assessment:
    v, src = current_vdot(p, goal.distance if goal.type == "race" else None)
    ag = best_age_grade(p)
    lt, pt = load_tier(p), perf_tier(ag)
    preds, paces = {}, {}
    if v is not None:
        for name, d in DISTANCES_M.items():
            t = predict_time_min(v, d)
            if name == "FM":
                t *= 1 + fm_penalty(p.weekly_volume_km)
            preds[name] = fmt_duration(t * C.SECONDS_PER_MINUTE)
        tp = training_paces(v)
        paces = {
            "E": f"{fmt_duration(tp['E_fast'])}-{fmt_duration(tp['E_slow'])}/km",
            "M": f"{fmt_duration(tp['M'])}/km", "T": f"{fmt_duration(tp['T'])}/km",
            "I": f"{fmt_duration(tp['I'])}/km", "R": f"{fmt_duration(tp['R'] / REPS_400M_PER_KM)}/400m",
        }
    status, v_goal, realistic = feasibility(goal, v, pt, weeks, p.weekly_volume_km)
    return Assessment(vdot=round(v, 1) if v else None, vdot_source=src, load_tier=lt,
                      perf_tier=pt, age_grade_pct=round(ag, 1) if ag else None,
                      display_level=lt, predictions=preds, paces=paces,
                      goal_vdot=round(v_goal, 1) if v_goal else None,
                      feasibility=status, realistic_target=realistic)
