"""Input and output data structures. All distances in km, paces in s/km."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date

GOAL_TYPES = ("race", "speed", "aerobic_base", "maintenance", "recovery",
              "return_to_running", "general_fitness")
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


@dataclass
class RaceResult:
    distance: str               # "5k" | "10k" | "HM" | "FM"
    time: str                   # "50:00", "1:48:30"
    weeks_ago: float = 0.0
    all_out: bool = True        # training runs / easy races are ignored


@dataclass
class Profile:
    weekly_volume_km: float             # 4-week average
    longest_run_30d_km: float
    runs_per_week_current: int = 3
    training_age_years: float = 1.0
    age: int = 35
    sex: str = "M"                      # "M" | "F" (age-grading standard)
    race_results: list[RaceResult] = field(default_factory=list)
    easy_pace_s_per_km: float | None = None   # fallback when no race result
    days_off_recent: int = 0            # consecutive days without running just before the plan
    cross_trained_during_break: bool = False
    current_pain: bool = False
    injury_cleared: bool = True
    max_long_run_ever_km: float | None = None
    can_run_continuous_min: float | None = None   # None = not asked; treated as able (warn)


@dataclass
class Goal:
    type: str                           # one of GOAL_TYPES
    distance: str | None = None         # race / recovery: "5k" | "10k" | "HM" | "FM"
    target_time: str | None = None      # race with time objective
    objective: str = "time"             # race: "time" | "finish"
    target_weekly_km: float | None = None   # aerobic_base
    previous_weekly_km: float | None = None  # maintenance / recovery / return reference
    override_feasibility: bool = False


@dataclass
class Constraints:
    plan_weeks: int | None = None
    start_date: date | None = None
    race_date: date | None = None
    days_per_week: int = 4
    long_run_day: int = 6               # 0 = Mon … 6 = Sun
    unavailable_days: list[int] = field(default_factory=list)
    preferred_quality_days: list[int] = field(default_factory=list)
    max_weekday_minutes: float | None = None
    max_long_run_minutes: float | None = None
    allow_short_plan: bool = False


@dataclass
class Workout:
    type: str                   # rest | E | E+S | LR | LR-prog | LR-HM | LR-M | T-cruise | ...
    title: str
    description: str = ""
    km: float = 0.0
    est_minutes: float = 0.0
    hard_minutes: float = 0.0   # time in M/T/I/R/race-pace segments
    zone_km: dict[str, float] = field(default_factory=dict)
    paces: dict[str, str] = field(default_factory=dict)
    rpe: str = ""
    is_quality: bool = False
    is_race: bool = False


@dataclass
class Day:
    weekday: int
    date: date | None
    workout: Workout


@dataclass
class Week:
    index: int                  # 1-based
    phase: str                  # base | build | specific | taper | race | down | ...
    is_down_week: bool
    target_km: float
    days: list[Day]
    notes: list[str] = field(default_factory=list)

    @property
    def total_km(self) -> float:
        return round(sum(d.workout.km for d in self.days), 1)

    @property
    def total_minutes(self) -> float:
        return sum(d.workout.est_minutes for d in self.days)

    @property
    def easy_share(self) -> float:
        tot = sum(d.workout.est_minutes for d in self.days if not d.workout.is_race)
        hard = sum(d.workout.hard_minutes for d in self.days if not d.workout.is_race)
        return 1.0 if tot == 0 else (tot - hard) / tot

    @property
    def long_run(self) -> Workout | None:
        lrs = [d.workout for d in self.days if d.workout.type.startswith("LR")]
        return lrs[0] if lrs else None


@dataclass
class Assessment:
    vdot: float | None
    vdot_source: str
    load_tier: str
    perf_tier: str
    age_grade_pct: float | None
    display_level: str
    predictions: dict[str, str]
    paces: dict[str, str]
    goal_vdot: float | None = None
    feasibility: str = "n/a"            # accepted | stretch | unrealistic | n/a
    realistic_target: str | None = None
    easy_by_effort: bool = False        # VDOT below the table floor (§4.4)
    pace_confidence: str = "normal"     # normal | low
    run_walk_entry_rung: int | None = None   # index into RUN_WALK_LADDER; None = continuous
    notes: list[str] = field(default_factory=list)


@dataclass
class Plan:
    assessment: Assessment
    weeks: list[Week]
    warnings: list[str] = field(default_factory=list)
    blocking_issues: list[str] = field(default_factory=list)
    options: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        for w, wd in zip(self.weeks, d["weeks"]):
            wd["total_km"] = w.total_km
            wd["total_minutes"] = round(w.total_minutes)
            wd["easy_share"] = round(w.easy_share, 3)
            for day in wd["days"]:
                day["weekday"] = WEEKDAYS[day["weekday"]]
                if day["date"] is not None:
                    day["date"] = day["date"].isoformat()
        return d
