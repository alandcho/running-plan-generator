"""Reference implementation of the Daniels-Gilbert VDOT model.

Used to validate the pace numbers in running-plan-framework.md.
Checked against Daniels' published VDOT 40 row (10k 50:03, FM 3:49:45,
T 5:06/km, I 4:42/km); this code gives 50:00 / 3:49:37 / 5:06 / 4:41.

Run:  python3 research/vdot.py 10000 50:00
"""
import math
import sys

MILE = 1609.34


def vo2_cost(v_m_per_min: float) -> float:
    """Oxygen cost (ml/kg/min) of running at velocity v (m/min)."""
    return -4.60 + 0.182258 * v_m_per_min + 0.000104 * v_m_per_min ** 2


def pct_vo2max(t_min: float) -> float:
    """Fraction of VO2max sustainable for a race lasting t minutes."""
    return (0.8 + 0.1894393 * math.exp(-0.012778 * t_min)
            + 0.2989558 * math.exp(-0.1932605 * t_min))


def vdot(distance_m: float, time_min: float) -> float:
    return vo2_cost(distance_m / time_min) / pct_vo2max(time_min)


def velocity_for_vo2(vo2: float) -> float:
    """Invert vo2_cost: velocity (m/min) that costs `vo2`."""
    a, b, c = 0.000104, 0.182258, -4.60 - vo2
    return (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)


def predict_time_min(v: float, distance_m: float) -> float:
    """Equivalent race time at the same VDOT (bisection)."""
    lo, hi = 1.0, 1000.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if vdot(distance_m, mid) > v:
            lo = mid
        else:
            hi = mid
    return mid


def training_paces(v: float) -> dict:
    """Pace targets in seconds per km (R given per 400 m)."""
    def s_per_km(vel):
        return 1000 / vel * 60

    marathon_v = 42195 / predict_time_min(v, 42195)
    return {
        "E_fast": s_per_km(velocity_for_vo2(0.70 * v)),
        "E_slow": s_per_km(velocity_for_vo2(0.62 * v)),
        "M": s_per_km(marathon_v),
        "T": s_per_km(velocity_for_vo2(0.88 * v)),
        "I": s_per_km(velocity_for_vo2(0.975 * v)),
        "R_per_400": predict_time_min(v, MILE) * 60 * 400 / MILE,
    }


def fmt(sec: float) -> str:
    sec = round(sec)
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def parse_time(s: str) -> float:
    parts = [float(p) for p in s.split(":")]
    sec = 0.0
    for p in parts:
        sec = sec * 60 + p
    return sec / 60


if __name__ == "__main__":
    dist = float(sys.argv[1]) if len(sys.argv) > 1 else 10000
    t = parse_time(sys.argv[2]) if len(sys.argv) > 2 else 50.0
    V = vdot(dist, t)
    print(f"VDOT {V:.1f}")
    for name, d in [("5k", 5000), ("10k", 10000), ("HM", 21097.5), ("FM", 42195)]:
        print(f"  {name:>3} equivalent: {fmt(predict_time_min(V, d) * 60)}")
    p = training_paces(V)
    print(f"  E {fmt(p['E_fast'])}-{fmt(p['E_slow'])}/km  M {fmt(p['M'])}/km  "
          f"T {fmt(p['T'])}/km  I {fmt(p['I'])}/km  R {fmt(p['R_per_400'])}/400m")
