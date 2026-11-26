"""Step 7: workout library and selection (§7, §8). All tunables live in config.py."""
from __future__ import annotations

from dataclasses import dataclass

from . import config as C
from .config import RepSpec
from .models import Workout
from .vdot import fmt_duration

SEC = C.SECONDS_PER_MINUTE
HARD_ZONES = {"M", "T", "I", "R", "F", "5k", "10k", "HM", "FM", "TT"}
ZONE_NAMES = {"E": "E", "jog": "easy jog", "M": "M", "T": "T", "I": "I", "R": "R",
              "F": "fartlek effort", "5k": "5k pace", "10k": "10k pace",
              "HM": "HM pace", "FM": "M", "TT": "all-out", "walk": "walk"}
RPE = {"E": "2-4", "M": "5-6", "T": "6-7", "I": "8-9", "R": "9", "5k": "8-9",
       "10k": "7-8", "HM": "6-7", "TT": "9-10"}


@dataclass
class Ctx:
    paces: dict[str, float]     # s/km per zone (E, jog, M, T, I, R, F, 5k, 10k, HM, FM, TT, walk)
    weekly_km: float
    tier: str
    cap_km: float               # max single-run distance this week (spike rule, ≤ long run)
    cap_min: float | None       # weekday time cap
    hard_budget_min: float      # hard minutes this session may use

    @property
    def wu(self) -> float:
        return C.WARMUP_KM[self.tier]

    def km_for_minutes(self, minutes: float, zone: str) -> float:
        return minutes * SEC / self.paces[zone]

    def minutes_for_km(self, km: float, zone: str) -> float:
        return km * self.paces[zone] / SEC


def dose_km(zone: str, weekly_km: float) -> float:
    frac, absolute = C.DOSE_CAP.get(zone, C.DOSE_CAP["T"])
    return min(frac * weekly_km, absolute)


def pace_str(ctx: Ctx, zone: str) -> str:
    if zone == "E":
        return f"{fmt_duration(ctx.paces['E_fast'])}-{fmt_duration(ctx.paces['E_slow'])}/km"
    return f"{fmt_duration(ctx.paces[zone])}/km"


def _make(ctx: Ctx, wtype: str, title: str, desc: str, segments: list[tuple[float, str]],
          rpe: str, quality: bool, extra_min: float = 0.0) -> Workout:
    zone_km: dict[str, float] = {}
    minutes, hard = extra_min, 0.0
    for km, zone in segments:
        zone_km[zone] = zone_km.get(zone, 0.0) + km
        m = ctx.minutes_for_km(km, zone)
        minutes += m
        if zone in HARD_ZONES:
            hard += m
    shown = {z: pace_str(ctx, z) for z in zone_km if z not in ("jog", "walk")}
    return Workout(type=wtype, title=title, description=desc,
                   km=round(sum(k for k, _ in segments), 1), est_minutes=round(minutes, 1),
                   hard_minutes=round(hard, 1), zone_km={z: round(k, 2) for z, k in zone_km.items()},
                   paces=shown, rpe=rpe, is_quality=quality)


def _dist_label(km: float) -> str:
    return f"{int(round(km * C.METERS_PER_KM))} m" if km < 1 else f"{km:g} km"


def _shrink_warmup_to_fit(fits, wu: float) -> float:
    while not fits(wu) and wu > C.MIN_WARMUP_KM:
        wu -= C.WARMUP_SHRINK_STEP_KM
    return wu


# --- Easy & long runs -------------------------------------------------------

def rest(note: str = "Rest") -> Workout:
    return Workout(type="rest", title=note, description="Rest, or easy cross-training / strength.")


def easy(ctx: Ctx, km: float, strides: int = 0) -> Workout:
    km = round(km, 1)
    if strides:
        return _make(ctx, "E+S", "Easy + strides",
                     f"{km:g} km @ E, then {strides} × {C.STRIDE_SECONDS} s strides "
                     "(fast, relaxed), full recovery",
                     [(km, "E")], RPE["E"], False, extra_min=strides * C.STRIDE_MINUTES_PER_REP)
    return _make(ctx, "E", "Easy run", f"{km:g} km @ E (conversational)", [(km, "E")],
                 RPE["E"], False)


def long_run(ctx: Ctx, km: float, variant: str, prog: int) -> Workout:
    km = round(km, 1)
    budget_km = {z: ctx.km_for_minutes(ctx.hard_budget_min, z) for z in ("M", "HM")}
    if variant == "LR-prog":
        fast = round(min(C.LR_PROG_FAST_FRACTION * km, budget_km["M"],
                         dose_km("M", ctx.weekly_km)), 1)
        if fast >= C.LR_PROG_MIN_FAST_KM:
            return _make(ctx, "LR-prog", "Progression long run",
                         f"{km - fast:g} km @ E, last {fast:g} km building to M",
                         [(km - fast, "E"), (fast, "M")], "3-6", True)
    if variant == "LR-HM":
        fast = round(min(C.LR_HM_FAST_START_KM + C.LR_HM_FAST_STEP_KM * prog, C.LR_HM_FAST_MAX_KM,
                         C.LR_HM_FAST_MAX_FRACTION * km, budget_km["HM"],
                         dose_km("HM", ctx.weekly_km)))
        if fast >= C.LR_HM_MIN_FAST_KM:
            return _make(ctx, "LR-HM", "Long run with HM-pace finish",
                         f"{km - fast:g} km @ E, last {fast:g} km @ HM pace",
                         [(km - fast, "E"), (fast, "HM")], "3-7", True)
    if variant == "LR-M":
        fast = round(min(C.LR_M_FAST_START_KM + C.LR_M_FAST_STEP_KM * prog,
                         C.LR_M_FAST_MAX_FRACTION * km, budget_km["M"], dose_km("M", ctx.weekly_km)))
        if fast >= C.LR_M_MIN_FAST_KM:
            first = round((km - fast) * C.LR_M_EASY_BEFORE_FRACTION, 1)
            return _make(ctx, "LR-M", "Marathon-pace long run",
                         f"{first:g} km @ E, {fast:g} km @ M, {km - fast - first:g} km @ E",
                         [(first, "E"), (fast, "M"), (km - fast - first, "E")], "3-6", True)
    return _make(ctx, "LR", "Long run", f"{km:g} km @ E (steady, conversational)",
                 [(km, "E")], RPE["E"], True)


# --- Quality sessions --------------------------------------------------------

def reps(ctx: Ctx, wtype: str, title: str, zone: str, spec: RepSpec, prog: int,
         dose_zone: str | None = None, rep_scale: float = 1.0, rep_reduction: int = 0,
         ) -> Workout | None:
    """Repetition session sized by the spec, then fitted to dose cap, hard budget and run cap."""
    limit = min(dose_km(dose_zone or zone, ctx.weekly_km),
                ctx.km_for_minutes(ctx.hard_budget_min, zone))
    n_target = max(spec.min_reps, spec.reps_for(prog) - rep_reduction)
    choice = None
    for rep in (r * rep_scale for r in spec.rep_options_km):
        n = min(n_target, int(limit / rep + C.FLOAT_EPSILON))
        if n >= spec.min_reps:
            choice = (rep, n)
            break
    if choice is None:
        return None
    rep, n = choice
    rec = spec.recovery_km

    def total_km(n: int, wu: float) -> float:
        return 2 * wu + n * rep + (n - 1) * rec

    def minutes(n: int, wu: float) -> float:
        return (ctx.minutes_for_km(2 * wu, "E") + ctx.minutes_for_km(n * rep, zone)
                + ctx.minutes_for_km((n - 1) * rec, "jog"))

    def fits(n: int, wu: float) -> bool:
        return (total_km(n, wu) <= ctx.cap_km
                and (ctx.cap_min is None or minutes(n, wu) <= ctx.cap_min))

    wu = _shrink_warmup_to_fit(lambda w: fits(n, w), ctx.wu)
    while not fits(n, wu) and n > spec.min_reps:
        n -= 1
    if not fits(n, wu):
        return None
    segs = [(wu, "E")] + [(rep, zone)] * n + [(rec, "jog")] * (n - 1) + [(wu, "E")]
    desc = (f"{wu:g} km WU · {n} × {_dist_label(rep)} @ {ZONE_NAMES[zone]} "
            f"({pace_str(ctx, zone)}), {spec.recovery_label} · {wu:g} km CD")
    return _make(ctx, wtype, title, desc, segs, RPE.get(zone, "7-8"), True)


def tempo(ctx: Ctx, prog: int) -> Workout | None:
    if ctx.tier == "beginner":
        target = min(C.TEMPO_BEGINNER_START_MIN + C.TEMPO_BEGINNER_STEP_MIN * prog,
                     C.TEMPO_BEGINNER_MAX_MIN)
    else:
        target = C.TEMPO_START_MIN + C.TEMPO_STEP_MIN * prog
    t_min = int(min(target, ctx.minutes_for_km(dose_km("T", ctx.weekly_km), "T"),
                    ctx.hard_budget_min))
    km_t = round(ctx.km_for_minutes(t_min, "T"), 1)
    wu = _shrink_warmup_to_fit(lambda w: 2 * w + km_t <= ctx.cap_km, ctx.wu)
    if t_min < C.TEMPO_MIN_MIN or 2 * wu + km_t > ctx.cap_km:
        return None
    return _make(ctx, "T-tempo", "Tempo run",
                 f"{wu:g} km WU · {t_min} min continuous @ T ({pace_str(ctx, 'T')}) · {wu:g} km CD",
                 [(wu, "E"), (km_t, "T"), (wu, "E")], RPE["T"], True)


def fartlek(ctx: Ctx, km: float, prog: int) -> Workout | None:
    n = int(min(C.FARTLEK_START_REPS + prog, C.FARTLEK_MAX_REPS,
                ctx.hard_budget_min / C.FARTLEK_ON_MIN))
    on_km = ctx.km_for_minutes(n * C.FARTLEK_ON_MIN, "F")
    off_km = ctx.km_for_minutes(n * C.FARTLEK_OFF_MIN, "jog")
    km = min(max(km, on_km + off_km + C.FARTLEK_MIN_EASY_KM), ctx.cap_km)
    if n < C.FARTLEK_MIN_REPS or km < on_km + off_km + C.FARTLEK_MIN_SLACK_KM:
        return None
    easy_km = km - on_km - off_km
    return _make(ctx, "Fartlek", "Fartlek",
                 f"{easy_km / 2:.1f} km @ E, {n} × ({C.FARTLEK_ON_MIN} min @ ~10k effort / "
                 f"{C.FARTLEK_OFF_MIN} min easy), {easy_km / 2:.1f} km @ E",
                 [(easy_km, "E"), (on_km, "F"), (off_km, "jog")], "3-8", True)


def hill_sprints(ctx: Ctx, km: float, prog: int) -> Workout:
    n = min(C.HILL_SPRINT_START_REPS + prog, C.HILL_SPRINT_MAX_REPS)
    km = round(min(km, ctx.cap_km), 1)
    return _make(ctx, "HillSprint", "Easy + hill sprints",
                 f"{km:g} km @ E including {n} × {C.HILL_SPRINT_SECONDS} s max-effort hill "
                 "sprints, walk back down",
                 [(km, "E")], "2-4 (sprints 9)", True, extra_min=n * C.HILL_SPRINT_MINUTES_PER_REP)


def time_trial(ctx: Ctx, distance: str) -> Workout | None:
    d = C.TIME_TRIAL_KM[distance]
    wu = _shrink_warmup_to_fit(lambda w: 2 * w + d <= ctx.cap_km, ctx.wu)
    if 2 * wu + d > ctx.cap_km:
        return None
    return _make(ctx, "TT", f"{distance} time trial",
                 f"{wu:g} km WU + strides · {distance} all-out, even effort · {wu:g} km CD "
                 "— result recalibrates your paces",
                 [(wu, "E"), (d, "TT"), (wu, "E")], RPE["TT"], True)


def race(distance: str, km: float, target: str, pace: str, minutes: float) -> Workout:
    return Workout(type="race", title=f"RACE: {distance}",
                   description=f"Target {target} ({pace}). Start controlled; even pacing.",
                   km=km, est_minutes=round(minutes, 1), hard_minutes=round(minutes, 1),
                   rpe="race", is_quality=True, is_race=True)


def run_walk(ctx: Ctx, run_min: int, walk_min: int, reps_n: int) -> Workout:
    if walk_min == 0:
        return Workout(type="E", title="Continuous easy run",
                       description=f"{run_min} min continuous @ easy effort",
                       km=round(ctx.km_for_minutes(run_min, "E_slow"), 1), est_minutes=run_min,
                       rpe="2-4", paces={"E": pace_str(ctx, "E")})
    km = reps_n * (ctx.km_for_minutes(run_min, "E_slow") + ctx.km_for_minutes(walk_min, "walk"))
    return Workout(type="RunWalk", title="Run-walk",
                   description=f"{reps_n} × ({run_min} min easy run / {walk_min} min walk). "
                               f"Stop if pain > {C.RUN_WALK_PAIN_STOP}/10.",
                   km=round(km, 1), est_minutes=reps_n * (run_min + walk_min), rpe="2-3",
                   paces={"E": pace_str(ctx, "E")})


# --- Selection ---------------------------------------------------------------

def race_pace_session(ctx: Ctx, distance: str, prog: int, taper: bool = False) -> Workout | None:
    zone = "M" if distance == "FM" else distance
    if taper:
        return reps(ctx, "RP", f"{distance}-pace sharpener", zone, C.RACE_PACE_REPS[distance], 0,
                    dose_zone=zone, rep_scale=C.TAPER_REP_LENGTH_SCALE,
                    rep_reduction=C.TAPER_REP_COUNT_REDUCTION)
    return reps(ctx, "RP", f"{distance}-pace reps", zone, C.RACE_PACE_REPS[distance], prog,
                dose_zone=zone)


def quality_session(goal_key: str, phase: str, slot: int, ctx: Ctx, prog: int,
                    finish_only: bool, easy_km: float) -> Workout | None:
    """Session for one quality slot (slot 0 = key session), or None if it cannot fit."""
    beginner = ctx.tier == "beginner"

    def cruise(spec: RepSpec = C.T_CRUISE, p: int = prog):
        return reps(ctx, "T-cruise", "Cruise intervals", "T", spec, p)

    def intervals(spec: RepSpec):
        return reps(ctx, "I-1000", "VO2max intervals", "I", spec, prog)

    def speed_reps():
        return reps(ctx, "R-400", "Speed repetitions", "R", C.R_400, prog)

    if goal_key == "general_fitness":
        return fartlek(ctx, easy_km, prog) if phase == "build" else None
    if phase == "base":
        # Hill sprints first; light threshold only once the base is a few weeks old.
        if beginner or prog < C.T_CRUISE_BASE.weeks_per_extra_rep or goal_key == "speed":
            return hill_sprints(ctx, easy_km, prog) if slot == 0 else fartlek(ctx, easy_km, prog)
        return cruise(C.T_CRUISE_BASE, prog - C.T_CRUISE_BASE.weeks_per_extra_rep) if slot == 0 \
            else fartlek(ctx, easy_km, prog)
    if goal_key in ("aerobic_base", "maintenance"):
        if slot == 0:
            alternate_to_vo2 = goal_key == "maintenance" and prog % 2 == 1
            return intervals(C.I_1000_SECONDARY) if alternate_to_vo2 else cruise()
        return hill_sprints(ctx, easy_km, prog)
    if beginner or finish_only:
        if slot == 0:
            return tempo(ctx, prog) if prog % 2 == 0 else cruise(C.T_CRUISE_BEGINNER)
        return fartlek(ctx, easy_km, prog)
    short = goal_key in ("5k", "10k", "speed")
    if phase == "build":
        if short:
            return intervals(C.I_1000_PRIMARY) if slot == 0 else cruise()
        if slot == 0:
            return cruise() if prog % 2 == 0 else tempo(ctx, prog)
        return intervals(C.I_1000_SECONDARY)
    if phase == "specific":
        if goal_key == "speed":
            return intervals(C.I_1000_SPEED) if slot == 0 else speed_reps()
        if goal_key == "FM":
            return cruise() if slot == 0 else race_pace_session(ctx, "FM", prog)
        if slot == 0:
            return race_pace_session(ctx, goal_key, prog)
        if goal_key == "5k":
            return speed_reps()
        return cruise() if goal_key == "10k" else intervals(C.I_1000_SECONDARY)
    if phase == "taper":
        if slot == 0 and goal_key in C.RACE_PACE_REPS:
            return race_pace_session(ctx, goal_key, 0, taper=True)
        return cruise(C.T_CRUISE_TAPER)
    return None
