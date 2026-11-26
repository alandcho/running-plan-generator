"""Every tunable number in the generator, in one place.

Tags follow research/running-plan-framework.md:
  [E] evidence-backed, [C] coaching consensus, [H] framework heuristic.
Most values are [C] or [H] and are expected to be tuned from outcome data.
"""
from __future__ import annotations

TIERS = ("beginner", "intermediate", "advanced")
RACE_GOALS = ("5k", "10k", "HM", "FM")

# --- Classification (§3) ---------------------------------------------------
# Load tier: upper bounds for beginner / intermediate. [H]
LOAD_VOLUME_KM = (25.0, 55.0)
LOAD_LONG_RUN_KM = (10.0, 21.0)
LOAD_TRAINING_AGE_YR = (1.0, 3.0)

# Performance tier from age-grade %. [C, WMA informal tiers shifted for recreational runners]
PERF_AGE_GRADE = (50.0, 65.0)
PERF_TIERS = ("developing", "intermediate", "advanced")

# Approximate open (age 20-34) road standards, seconds. Close to road world bests.
# [H] Replace with official WMA tables for production accuracy.
AGE_GRADE_STANDARD_S = {
    "M": {"5k": 12 * 60 + 49, "10k": 26 * 60 + 24, "HM": 57 * 60 + 30, "FM": 2 * 3600 + 35},
    "F": {"5k": 13 * 60 + 54, "10k": 28 * 60 + 46, "HM": 3600 + 2 * 60 + 52, "FM": 2 * 3600 + 9 * 60 + 56},
}
# Slowdown of the standard per year of age (piecewise). [H]
AGE_SLOWDOWN = ((35, 50, 0.0075), (50, 70, 0.010), (70, 120, 0.015))

# --- Fitness (§4) ----------------------------------------------------------
RACE_FULL_WEIGHT_WEEKS = 8          # [H]
RACE_MAX_AGE_WEEKS = 52             # [H]
RACE_DECAY_PER_WEEK = 0.0015        # VDOT fraction lost per week past full weight [H]

# FM prediction penalty by weekly volume (km, penalty). Linear in between. [H, after Vickers 2016]
FM_PENALTY = ((30.0, 0.08), (35.0, 0.06), (50.0, 0.03), (70.0, 0.0))

# Detraining: (max days off, VDOT multiplier, volume restart fraction). [E->H]
NO_UPPER_LIMIT_DAYS = 10**6
DETRAINING = ((5, 1.00, 1.00), (14, 0.97, 0.80), (28, 0.93, 0.65), (56, 0.88, 0.50),
              (NO_UPPER_LIMIT_DAYS, 0.82, 0.40))

# Max upward VDOT recalibration. [H, after Daniels]
VDOT_MAX_GAIN = 1.0
VDOT_MAX_GAIN_WEEKS = 3

# --- Plan length & feasibility (§5) -----------------------------------------
MIN_WEEKS = {"5k": 6, "10k": 8, "HM": 10, "FM": 12}
TYPICAL_WEEKS = {"5k": (8, 12), "10k": (10, 12), "HM": (12, 16), "FM": (16, 20)}
# Minimum base to start a race plan: (weekly km, long run km) by load tier = beginner.
MIN_BASE = {"5k": (8.0, 3.0), "10k": (12.0, 5.0), "HM": (15.0, 6.0), "FM": (40.0, 16.0)}
# Reachability: projected peak long run must reach (km, minutes) — either satisfies. [C/H]
# Races are exempt from the spike rule, so this is what keeps the race itself reasonable.
MIN_PEAK_LONG_RUN = {"HM": (16.0, 105.0), "FM": (26.0, 165.0)}

# Plausible VDOT gain per ~14-week block by performance tier. [H]
VDOT_GAIN_RANGE = {"developing": (3.0, 6.0), "intermediate": (1.0, 3.0), "advanced": (0.5, 1.5)}
FEASIBILITY_REF_WEEKS = 14
# ΔVDOT ≤ range midpoint → accepted; ≤ top → stretch; > top → unrealistic. [H]
CONSERVATIVE_GOAL_DELTA_VDOT = -1.0   # goal this far below current fitness gets a note [H]

# Phase fractions of non-taper weeks: (base, build, specific). [C/H]
PHASE_SPLIT = {
    "5k": (0.30, 0.40, 0.30), "10k": (0.35, 0.35, 0.30),
    "HM": (0.35, 0.30, 0.35), "FM": (0.35, 0.25, 0.40),
    "speed": (0.20, 0.50, 0.30), "aerobic_base": (0.80, 0.20, 0.0),
    "general_fitness": (0.60, 0.40, 0.0),
}
# Taper: fraction of peak volume per taper week; last entry = race week (excl. race). [E: Bosquet 2007]
TAPER = {"5k": (0.60,), "10k": (0.60,), "HM": (0.75, 0.50), "FM": (0.80, 0.65, 0.45)}
TAPER_LONG_RUN = {"5k": (), "10k": (), "HM": (0.65,), "FM": (0.70, 0.50)}  # of peak LR, pre-race weeks

# --- Volume (§6) -----------------------------------------------------------
PEAK_VOLUME_KM = {  # (beginner, intermediate, advanced) ranges [C/H]
    "5k": ((20, 30), (35, 55), (60, 90)),
    "10k": ((25, 35), (40, 60), (65, 100)),
    "HM": ((30, 40), (45, 65), (70, 110)),
    "FM": ((40, 55), (55, 80), (85, 130)),
    "speed": ((20, 30), (35, 55), (60, 90)),
    "aerobic_base": ((25, 35), (45, 65), (70, 110)),
    "general_fitness": ((15, 25), (25, 40), (40, 60)),
}
PEAK_MAX_GROWTH = 1.5                         # peak <= current * 1.5 [H]
AVG_RUN_CAP_KM = {"beginner": 10.0, "intermediate": 13.0, "advanced": 16.0}  # frequency cap [H]
RAMP_RATE = {"beginner": 0.06, "intermediate": 0.09, "advanced": 0.10}      # per build week [H]
MAX_WEEKLY_INCREASE = 0.20                    # vs. last build week [E/H]
MAX_TWO_WEEK_INCREASE = 0.30                  # [E: Nielsen 2014]
DOWN_WEEK_CUT = 0.22                          # [C]
MASTERS_AGE = 50
ADAPT_CONSISTENT_OF_LAST = (2, 3)   # "consistently" = 2 of the last 3 sessions [H]

# --- Long run (§6.4) -------------------------------------------------------
SPIKE_LIMIT = 1.10            # any run <= 110% of longest run in prior 30 days [E: Frandsen 2025]
SPIKE_WINDOW_DAYS = 30
SPIKE_LIMIT_AFTER_INJURY = 1.05   # injury in last 12 months or bone-stress ever [H]
RACE_EVE_MAX_KM = 4.0            # run the day before a race [C]
# Max long-run share of weekly volume by run days. 30% is the default [C]; with fewer
# days the long run cannot be ≤ 30% without being shorter than an average run, so the
# cap rises and the plan carries a warning. [H]
LONG_RUN_SHARE = {2: 0.55, 3: 0.45, 4: 0.40, 5: 0.35, 6: 0.30, 7: 0.30}
LONG_RUN_SHARE_DEFAULT = 0.30
LONG_RUN_MAX_MIN = 150        # [C]
LONG_RUN_MAX_MIN_FM = 180     # beginner/intermediate marathoners [C]
LONG_RUN_STEP_KM = 2.0        # max build-week increment [C]
LONG_RUN_DOWN_CUT = 0.28      # [C]
PEAK_LONG_RUN_KM = {  # (beginner, intermediate, advanced) ranges [C]
    "5k": ((8, 12), (14, 18), (18, 24)), "10k": ((8, 12), (14, 18), (18, 24)),
    "HM": ((16, 19), (19, 24), (22, 28)), "FM": ((26, 30), (29, 32), (32, 37)),
    "speed": ((8, 12), (12, 16), (16, 20)), "aerobic_base": ((10, 14), (16, 22), (22, 28)),
    "general_fitness": ((6, 10), (10, 14), (14, 18)),
}
PEAK_LONG_RUN_POSITION = 0.4  # where in the range to aim [H]

# --- Intensity (§6.3) -------------------------------------------------------
MIN_EASY_SHARE = 0.80             # of running time [E/C]
MIN_EASY_SHARE_BEGINNER = 0.85
AEROBIC_BASE_MIN_EASY_SHARE = 0.90   # [C] §7.3
SPEED_LONG_RUN_SHARE = 0.25          # [C] §7.2
# Session dose caps: (fraction of weekly volume, absolute km cap). [C: Daniels]
DOSE_CAP = {"T": (0.10, 99.0), "I": (0.08, 10.0), "R": (0.05, 8.0), "M": (0.20, 29.0),
            "10k": (0.12, 9.0), "HM": (0.20, 16.0), "5k": (0.08, 10.0)}

# Quality sessions excluding the long run, by tier and days/week. [C/H]
QUALITY_COUNT = {
    "beginner": {2: 0, 3: 0, 4: 1, 5: 1},
    "intermediate": {2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2},
    "advanced": {2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 2},
}
MAX_DAYS_BEGINNER = 5

MIN_EASY_RUN_KM = 4.0      # [H]
WARMUP_KM = {"beginner": 1.5, "intermediate": 2.0, "advanced": 3.0}

# --- Maintenance / recovery (§7) -------------------------------------------
MAINTENANCE_VOLUME = 0.60          # of previous normal [E: reduced-training studies]
MAINTENANCE_LONG_RUN = 0.65
RECOVERY_WEEKS = {"5k": (0.80,), "10k": (0.70,), "HM": (0.50, 0.75), "FM": (0.30, 0.50, 0.70)}
RECOVERY_NO_HARD_DAYS = {"5k": 2, "10k": 3, "HM": 7, "FM": 14}

# Run-walk ladder for return to running: (run min, walk min, reps). [C]
# Continuous steps grow ≤ 10% so they also respect the spike rule.
RUN_WALK_LADDER = ((1, 1, 10), (2, 1, 8), (3, 1, 7), (4, 1, 6), (5, 1, 5), (8, 1, 3),
                   (10, 1, 2), (20, 0, 1), (22, 0, 1), (24, 0, 1), (26, 0, 1), (28, 0, 1),
                   (30, 0, 1))
RUN_WALK_THRESHOLD_DAYS = 56   # non-injury breaks longer than this restart with run-walk [C]
NOVICE_CONTINUOUS_RUN_MIN = 30  # cannot run this long continuously → run-walk entry [C]
# Below this VDOT (the floor of Daniels' published tables) paces are extrapolated:
# easy and long runs are prescribed by effort, with E_fast only as a speed limit. [C/H]
EFFORT_BASED_EASY_BELOW_VDOT = 30.0

# --- Units -------------------------------------------------------------------
SECONDS_PER_MINUTE = 60
METERS_PER_KM = 1000
DAYS_PER_WEEK = 7
FLOAT_EPSILON = 1e-9

# --- Pace model (§4.4) [C: Daniels] ------------------------------------------
EASY_FAST_FRACTION_OF_VDOT = 0.70     # fast end of the easy range
EASY_SLOW_FRACTION_OF_VDOT = 0.62     # slow end of the easy range
THRESHOLD_FRACTION_OF_VDOT = 0.88     # ≈ race pace held for ~50-60 min
INTERVAL_FRACTION_OF_VDOT = 0.975     # ≈ 3k-5k race pace
REPETITION_RACE_DISTANCE_M = 1609.34  # R pace = current mile race pace [C]
# ...or the pace of an all-out race this long, whichever is faster. Slow runners' mile
# lasts 9-12+ min, so mile pace collapses onto I pace; a 6-min race keeps R ~7.5% faster
# than I at every level and matches Daniels' mile pace around VDOT 50. [H]
REPETITION_RACE_DURATION_MIN = 6.0
FARTLEK_ON_ZONE = "10k"               # 'on' segments run at ~10k effort
WALK_PACE_S_PER_KM = 600              # used only to estimate run-walk distance
VDOT_SEARCH_RANGE = (20.0, 85.0)      # bisection bounds when inverting easy pace -> VDOT
# No race result: prescribe by RPE/talk test only; time trial once running is consistent. [C]
TIME_TRIAL_WEEK_WITHOUT_RACE = 3
RESULT_DISAGREEMENT_VDOT = 1.0       # spread above which results are weighted by distance closeness [H]
GOAL_PACE_T_MARGIN = 0.02            # race-pace reps within 2% of current T (or faster) are dosed as T [H]

# --- Feasibility scaling (§5.3) [H] -----------------------------------------
FEASIBILITY_SCALE_BOUNDS = (0.5, 1.2)  # plan_weeks / FEASIBILITY_REF_WEEKS, clamped

# --- Weekly template (§6.5) [H] ---------------------------------------------
HARD_DAY_MIN_GAP_DAYS = 2              # ≥ 48 h between quality days and the long run
QUALITY_IDEAL_DAYS_BEFORE_LONG_RUN = 3
TEMPLATE_CONSECUTIVE_DAY_PENALTY = 3   # scoring weights for choosing run days
TEMPLATE_REST_AFTER_LONG_RUN_BONUS = 2
TEMPLATE_REST_AFTER_LONG_RUN_MAX_DAYS = 5  # only prefer a rest day after the LR at ≤ 5 run days
TEMPLATE_PREFERRED_QUALITY_DAY_BONUS = 2

# --- Workout library (§8) [C/H] ---------------------------------------------
from typing import NamedTuple  # noqa: E402


class RepSpec(NamedTuple):
    """A repetition session. Rep count grows by 1 every `weeks_per_extra_rep`
    non-down weeks in the phase, up to `max_reps`. Shorter rep options are used
    when the dose cap or hard-minute budget cannot fit `min_reps` of the first."""
    rep_options_km: tuple[float, ...]
    start_reps: int
    weeks_per_extra_rep: int
    max_reps: int
    min_reps: int
    recovery_km: float
    recovery_label: str

    def reps_for(self, progression: int) -> int:
        return min(self.max_reps, self.start_reps + progression // self.weeks_per_extra_rep)


_T_REPS_KM = (1.6, 1.0, 0.8)
_I_REPS_KM = (1.0, 0.8, 0.6, 0.4)
T_CRUISE_BASE = RepSpec(_T_REPS_KM, 2, 2, 3, 2, 0.2, "1 min jog")
T_CRUISE = RepSpec(_T_REPS_KM, 3, 2, 5, 2, 0.2, "1 min jog")
T_CRUISE_BEGINNER = RepSpec(_T_REPS_KM, 2, 2, 4, 2, 0.2, "1 min jog")
T_CRUISE_TAPER = RepSpec(_T_REPS_KM, 2, 99, 2, 2, 0.2, "1 min jog")
I_1000_PRIMARY = RepSpec(_I_REPS_KM, 4, 1, 6, 3, 0.4, "jog ≈ equal time")    # 5k/10k build
I_1000_SECONDARY = RepSpec(_I_REPS_KM, 4, 2, 6, 3, 0.4, "jog ≈ equal time")  # HM/FM support
I_1000_SPEED = RepSpec(_I_REPS_KM, 5, 1, 6, 3, 0.4, "jog ≈ equal time")
R_400 = RepSpec((0.4, 0.2), 6, 1, 10, 4, 0.4, "400 m walk/jog (full recovery)")
RACE_PACE_REPS = {
    "5k": RepSpec((1.0, 0.8, 0.6), 4, 1, 6, 2, 0.4, "400 m easy jog"),
    "10k": RepSpec((3.0, 2.0, 1.0), 3, 2, 4, 2, 0.4, "400 m easy jog"),
    "HM": RepSpec((5.0, 4.0, 3.0, 2.0), 2, 2, 3, 2, 0.4, "400 m easy jog"),
    "FM": RepSpec((6.0, 5.0, 4.0, 3.0), 2, 2, 3, 2, 0.4, "400 m easy jog"),
}
TAPER_REP_LENGTH_SCALE = 0.5      # taper race-pace reps are half length …
TAPER_REP_COUNT_REDUCTION = 1     # … and one fewer
TAPER_MIN_REPS = 2

TEMPO_START_MIN = 20
TEMPO_STEP_MIN = 5                # + per progression step
TEMPO_BEGINNER_START_MIN = 15
TEMPO_BEGINNER_STEP_MIN = 2
TEMPO_BEGINNER_MAX_MIN = 20       # [C] continuous tempo ≤ 20 min for beginners
TEMPO_MIN_MIN = 10                # shorter than this is not worth a tempo session

FARTLEK_START_REPS = 6
FARTLEK_MAX_REPS = 10
FARTLEK_MIN_REPS = 4
FARTLEK_ON_MIN = 1
FARTLEK_OFF_MIN = 1
FARTLEK_MIN_EASY_KM = 2.0         # easy running around the fartlek block
FARTLEK_MIN_SLACK_KM = 1.0        # below this the block does not fit the run cap

HILL_SPRINT_START_REPS = 6
HILL_SPRINT_MAX_REPS = 10
HILL_SPRINT_SECONDS = 10
HILL_SPRINT_MINUTES_PER_REP = 1.5  # sprint + walk-back recovery

STRIDE_SECONDS = 20
STRIDE_MINUTES_PER_REP = 1.0       # stride + recovery
STRIDES_PER_SESSION = 6

MIN_WARMUP_KM = 1.0                # warm-up/cool-down never shrink below this
WARMUP_SHRINK_STEP_KM = 0.5

TIME_TRIAL_KM = {"3k": 3.0, "5k": 5.0}
TIME_TRIAL_DISTANCE_BY_TIER = {"beginner": "3k", "intermediate": "5k", "advanced": "5k"}

LR_PROG_FAST_FRACTION = 0.20       # last 20% of a progression long run at M
LR_PROG_MIN_FAST_KM = 2.0
LR_HM_FAST_START_KM = 3.0          # HM-pace finish: 3 km, +1.5 km per step, ≤ 8 km and ≤ 40% of LR
LR_HM_FAST_STEP_KM = 1.5
LR_HM_FAST_MAX_KM = 8.0
LR_HM_FAST_MAX_FRACTION = 0.40
LR_HM_MIN_FAST_KM = 2.0
LR_M_FAST_START_KM = 6.0           # M-pace block: 6 km, +2 km per step, ≤ 60% of LR
LR_M_FAST_STEP_KM = 2.0
LR_M_FAST_MAX_FRACTION = 0.60
LR_M_MIN_FAST_KM = 3.0
LR_M_EASY_BEFORE_FRACTION = 0.60   # share of the easy km placed before the M block

RUN_WALK_PAIN_STOP = 2             # stop if pain exceeds this (0-10 scale) [C]

# --- Validator tolerances (rounding slack, not rule slack) -------------------
VALIDATE_KM_TOLERANCE = 0.15
VALIDATE_SHARE_TOLERANCE = 0.01
VALIDATE_LONG_RUN_SHARE_TOLERANCE_KM = 0.05
VALIDATE_RAMP_TOLERANCE_KM = 1.0
