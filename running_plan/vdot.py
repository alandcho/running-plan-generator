"""Daniels-Gilbert VDOT model: fitness from race results, equivalent times, paces.

Checked against Daniels' published VDOT 40 row (10k 50:03, FM 3:49:45,
T 5:06/km, I 4:42/km); this code gives 50:00 / 3:49:37 / 5:06 / 4:41.

    python3 -m running_plan.vdot 10000 50:00
"""
from __future__ import annotations

import math
import sys

from . import config as C

# Oxygen cost of running at velocity v (m/min):  VO2 = A + B·v + C·v²   (Daniels & Gilbert 1979)
VO2_COST_INTERCEPT = -4.60
VO2_COST_LINEAR = 0.182258
VO2_COST_QUADRATIC = 0.000104

# Fraction of VO2max sustainable for t minutes:
#   %max = BASE + FAST_AMP·e^(−FAST_RATE·t) + SLOW_AMP·e^(−SLOW_RATE·t)
SUSTAINABLE_BASE = 0.8
SUSTAINABLE_SLOW_AMPLITUDE = 0.1894393
SUSTAINABLE_SLOW_DECAY_PER_MIN = 0.012778
SUSTAINABLE_FAST_AMPLITUDE = 0.2989558
SUSTAINABLE_FAST_DECAY_PER_MIN = 0.1932605

BISECTION_ITERATIONS = 100
RACE_TIME_SEARCH_MIN = (1.0, 2000.0)   # minutes

DISTANCES_M = {"5k": 5000.0, "10k": 10000.0, "HM": 21097.5, "FM": 42195.0}
REPS_400M_PER_KM = 1000 / 400


def vo2_cost(v_m_per_min: float) -> float:
    """Oxygen cost (ml/kg/min) of running at velocity v (m/min)."""
    return VO2_COST_INTERCEPT + VO2_COST_LINEAR * v_m_per_min + VO2_COST_QUADRATIC * v_m_per_min ** 2


def pct_vo2max(t_min: float) -> float:
    """Fraction of VO2max sustainable for a race lasting t minutes."""
    return (SUSTAINABLE_BASE
            + SUSTAINABLE_SLOW_AMPLITUDE * math.exp(-SUSTAINABLE_SLOW_DECAY_PER_MIN * t_min)
            + SUSTAINABLE_FAST_AMPLITUDE * math.exp(-SUSTAINABLE_FAST_DECAY_PER_MIN * t_min))


def vdot(distance_m: float, time_min: float) -> float:
    return vo2_cost(distance_m / time_min) / pct_vo2max(time_min)


def velocity_for_vo2(vo2: float) -> float:
    """Inverse of vo2_cost (quadratic formula): velocity (m/min) whose oxygen cost is `vo2`."""
    a, b, c = VO2_COST_QUADRATIC, VO2_COST_LINEAR, VO2_COST_INTERCEPT - vo2
    return (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)


def predict_time_min(v: float, distance_m: float) -> float:
    """Equivalent race time (minutes) at the same VDOT, by bisection."""
    lo, hi = RACE_TIME_SEARCH_MIN
    for _ in range(BISECTION_ITERATIONS):
        mid = (lo + hi) / 2
        if vdot(distance_m, mid) > v:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def race_pace_s_per_km(v: float, distance_m: float) -> float:
    return predict_time_min(v, distance_m) * C.SECONDS_PER_MINUTE / (distance_m / C.METERS_PER_KM)


def training_paces(v: float) -> dict[str, float]:
    """Pace targets in seconds per km for each Daniels zone."""
    def s_per_km(vel_m_per_min: float) -> float:
        return C.METERS_PER_KM / vel_m_per_min * C.SECONDS_PER_MINUTE

    return {
        "E_fast": s_per_km(velocity_for_vo2(C.EASY_FAST_FRACTION_OF_VDOT * v)),
        "E_slow": s_per_km(velocity_for_vo2(C.EASY_SLOW_FRACTION_OF_VDOT * v)),
        "M": race_pace_s_per_km(v, DISTANCES_M["FM"]),
        "T": s_per_km(velocity_for_vo2(C.THRESHOLD_FRACTION_OF_VDOT * v)),
        "I": s_per_km(velocity_for_vo2(C.INTERVAL_FRACTION_OF_VDOT * v)),
        "R": min(race_pace_s_per_km(v, C.REPETITION_RACE_DISTANCE_M),
                 s_per_km(velocity_for_vo2(v * pct_vo2max(C.REPETITION_RACE_DURATION_MIN)))),
    }


def fmt_duration(sec: float) -> str:
    sec = round(sec)
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def parse_duration_min(s: str) -> float:
    """'50:00' -> 50.0, '1:48:00' -> 108.0 (minutes)."""
    sec = 0.0
    for part in s.strip().split(":"):
        sec = sec * C.SECONDS_PER_MINUTE + float(part)
    return sec / C.SECONDS_PER_MINUTE


def main(argv: list[str]) -> None:
    dist = float(argv[1]) if len(argv) > 1 else DISTANCES_M["10k"]
    t = parse_duration_min(argv[2]) if len(argv) > 2 else 50.0
    v = vdot(dist, t)
    print(f"VDOT {v:.1f}")
    for name, d in DISTANCES_M.items():
        print(f"  {name:>3} equivalent: {fmt_duration(predict_time_min(v, d) * 60)}")
    p = training_paces(v)
    print(f"  E {fmt_duration(p['E_fast'])}-{fmt_duration(p['E_slow'])}/km  "
          f"M {fmt_duration(p['M'])}/km  T {fmt_duration(p['T'])}/km  "
          f"I {fmt_duration(p['I'])}/km  R {fmt_duration(p['R'] / REPS_400M_PER_KM)}/400m")


if __name__ == "__main__":
    main(sys.argv)
