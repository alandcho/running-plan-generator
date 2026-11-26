# Running Plan Generator: Research & Algorithm Framework

Status: research draft v0.2 (2026-11-26), revised after an independent review (see §15). Units are metric. Convert miles at the input boundary.

Each rule below is tagged with its evidence level:

- **[E] Evidence**: backed by peer-reviewed studies (cited in §13).
- **[C] Coaching consensus**: established methods (Daniels, Pfitzinger, Hansons and similar) that are widely used but not validated as cut-offs.
- **[H] Heuristic**: a number chosen for this framework that is reasonable but arbitrary. These are the knobs to tune.

**A blunt finding up front:** the research is strong on *what kinds* of training work: mostly easy running, a little intensity, progressive overload, and a taper. It is weak on *exact numbers*: the safe weekly increase, the cut-off between "beginner" and "intermediate", the right long-run length. Most numbers in any plan generator, including this one, are [C] or [H]. The design should keep them configurable and make the plan adapt from feedback instead of trusting the first prescription.

---

## 1. Design principles

1. **Two separate limits.** Aerobic fitness (the *engine*, seen in race times) and tissue tolerance (the *chassis*: tendons, bones and muscles, seen in training history) adapt at different rates. Set paces from the engine. Set volume and its progression from the chassis.
2. **Progress from what the runner has actually done recently**, not from their goal. Single-session spikes matter more than weekly totals [E: Frandsen 2025].
3. **Most running is easy.** Roughly 75–90% of running time should be easy [C/E]. Hard days are hard and easy days are easy.
4. **Specificity rises as the goal approaches.** The plan moves from general fitness to goal-pace work.
5. **Recovery is part of the plan**: down weeks, a taper, and rest days.
6. **Adapt to the runner.** Recalibrate paces from tune-up races and adjust load from check-ins.
7. **Be honest about feasibility.** Flag goals that are unrealistic for the time available instead of producing a plan that cannot work.

---

## 2. Inputs

### 2.1 Current capability

| Field | Type | Notes |
|---|---|---|
| `weekly_volume_km` | avg of last 4 weeks | Use the 4-week average, not the best week. If only "typical" is known, use it and lower confidence. |
| `longest_run_30d_km` | number | **Required**: it drives the long-run cap (§6.4). |
| `max_long_run_ever_km` | number | Optional. Helps when the runner is returning to a distance they have run before. |
| `runs_per_week_current` | int | Current frequency; adding days is itself a load increase. |
| `race_results[]` | {distance, time, date, effort} | PBs **and recent results**. A PB from 4 years ago is not current fitness. |
| `training_age_years` | number | Years of *consistent* running (≥3×/week most weeks). |
| `weeks_since_break` / `last_break_length_weeks` | numbers | For detraining adjustment (§4.3). |
| `age`, `sex` | | For age-grading (§3) and recovery (masters). |
| `injury_last_12_months`, `bone_stress_injury_ever` | bools | Prior injury is the most consistent injury risk factor [E: Saragiotto 2014]. Makes the load rules more conservative (§6.2). |
| `current_pain`, `injury_cleared` | bools | Current pain or an uncleared injury → blocking screen (§12). |
| `health_screen` | PAR-Q+ style answers | Chest pain, fainting, known cardiac/metabolic/renal disease, medications. Any "yes" → blocking until a clinician clears (§12). |
| `energy_availability_screen` | optional answers | No periods ≥ 3 months, prior bone-stress injury, disordered eating → refer (RED-S, §12). |
| `can_run_continuous_min` | number | Minutes of continuous easy running possible today. **Always asked.** < 30 → run-walk entry (§7.7). |
| `easy_pace_s_per_km`, `hr_max`, `hr_rest` | optional | Fallback when there are no race results; enables HR zones. |

### 2.2 Goal

| Goal type | Definition | Required extra input |
|---|---|---|
| `race` | Run a specific distance on a date: 5k, 10k, HM, FM; ultra is out of scope for v1 | distance, race date, objective = `finish` or `time` (target time) |
| `speed` | Get faster over short distances (5k/10k) without a fixed race | optional target 5k time |
| `aerobic_base` | Build volume and endurance; usually the phase before a race block | optional target weekly volume |
| `maintenance` | Hold fitness with less time (busy period, off-season) | time budget |
| `recovery` | After a race or a hard block; reverse taper | race just completed + date |
| `return_to_running` | After a break (≥2 weeks) or medically cleared injury | break length, cleared Y/N |
| `general_fitness` | Health and habit; mostly for beginners | none |

### 2.3 Constraints and preferences

| Field | Why it matters |
|---|---|
| `plan_start_date`, `plan_weeks` (or race date) | Drives periodization. Validate against the minimums in §5.2. |
| `days_per_week` (2–7) | Caps attainable volume and the number of quality days (§6.5). |
| `long_run_day` | Anchors the weekly template. |
| `unavailable_days`, `preferred_quality_days` | Template placement. |
| `max_weekday_minutes`, `max_long_run_minutes` | Time caps often bind before distance caps. |
| `surface` / `treadmill` / `hilly` | Pace targets become effort targets on hills and trails. |
| `climate` (heat/humidity), `altitude` | Pace adjustment (§8.3). |
| `strength_training` Y/N, `cross_training` options | Recommended add-ons; cross-training can replace easy volume. |
| `units` (km/mi), `pace_display` | Presentation only. |

---

## 3. Classifying the runner (beginner / intermediate / advanced)

**Research finding:** there is **no validated standard** for these labels. Coaching books use them loosely, usually keyed to weekly mileage. The closest objective performance scale is **WMA age-grading**: performance as a percentage of the age- and sex-adjusted world standard. Its informal tiers are 60% local, 70% regional, 80% national and 90% world class, and they are popular benchmarks rather than an official WMA scheme [E/C].

Because of principle 1.1, **classify along two axes** instead of using one label.

### 3.1 Load tier: drives volume, long run and progression

| Tier | Weekly volume (4-wk avg) | Longest run (30 d) | Consistent training age |
|---|---|---|---|
| **Beginner** | < 25 km | < 10 km | < 1 yr |
| **Intermediate** | 25–55 km | 10–21 km | 1–3 yr |
| **Advanced** | > 55 km | > 21 km | > 3 yr |

Rule: `load_tier = min(tier by volume, tier by long run + 1, tier by training age + 1)` [H].
Taking the **minimum** is deliberate: injury risk follows the weakest link. Volume is the primary axis. The long-run and training-age terms can each lower the tier by **at most one step**:
- A 6-month runner already at 50 km/wk is capped at Intermediate.
- A 5k/10k specialist at 80 km/wk whose long runs are 18 km stays Advanced, not Intermediate.

### 3.2 Performance tier: drives workout complexity and intensity dose

| Tier | Age-grade % (best recent race) | ≈ VDOT (open age, male / female) |
|---|---|---|
| **Developing** | < 50% | < ~38 / < ~34 |
| **Intermediate** | 50–65% | ~38–50 / ~34–45 |
| **Advanced** | > 65% | > ~50 / > ~45 |

Use age-grade, not raw VDOT, so a 60-year-old with a 25-minute 5k is not labelled a beginner. The VDOT columns are rough guides for runners aged 20–35 [H].

### 3.3 Combined label (for display) and mismatch handling

- Display label = `load_tier`. It is the conservative one.
- **Fast but low-volume** (performance > load): use the performance tier's workout *types*, but the load tier's *volumes* and long-run caps. Flag that marathon predictions are optimistic (§4.2).
- **High-volume but slow** (load > performance): normal volume progression; keep intensity simple (fewer, longer-rest intervals).

---

## 4. Estimating current fitness and paces

### 4.1 VDOT from race results [C, validated formula]

Daniels and Gilbert model ([`running_plan/vdot.py`](../running_plan/vdot.py)). Coefficient names are in §14:

```
v       = distance_m / time_min                              # m/min
VO2     = -4.60 + 0.182258·v + 0.000104·v²
%max    = 0.8 + 0.1894393·e^(-0.012778·t) + 0.2989558·e^(-0.1932605·t)
VDOT    = VO2 / %max
```

Choosing which result to use:
1. Only include all-out races or time trials on roughly flat courses. Training runs underestimate fitness.
2. Weight by recency: full weight if ≤ 8 weeks old. Then decay it (§4.3) or drop it after 12 months [H].
3. When results disagree by more than 1 VDOT (`RESULT_DISAGREEMENT_VDOT`), **weight by closeness to the goal distance** instead of taking the maximum. An HM result predicts FM better than a fast 5k does. Taking the maximum lets a short-distance PB set marathon paces.
4. **No usable race:** prescribe by **RPE and talk test only**, not by estimated paces. Schedule a time trial in **week 3–4**, once running is consistent (5k for most runners; 3k for beginners). If the runner reports a typical easy pace, map it to the **fast end** of the E range (`VDOT whose E_fast = easy pace`). Recreational runners usually run easy too fast, so matching the midpoint would inflate VDOT [H].

### 4.2 Race-time prediction and the marathon problem [E]

- VDOT and Riegel (`T2 = T1·(D2/D1)^1.06`) predict well **up to the half marathon**.
- For recreational runners they **underestimate marathon time**: for half of runners the prediction was at least 10 minutes too fast (Vickers & Vertosick 2016, n = 2,303). Weekly mileage is a key moderator, and low-mileage runners fade more.
- Framework rule [H]: `FM_prediction = VDOT_FM_time × (1 + penalty)`, where the penalty is 0% at ≥ 70 km/wk, 3% at 50 km/wk, 6% at 35 km/wk and 8% below 30 km/wk. Interpolate in between. Tune this once real data exist.

### 4.3 Detraining adjustment after a break [E → H]

Evidence: highly trained runners can lose 4–14% of VO2max within 2–4 weeks of stopping. Beginners lose less, and losses level off after about 8 weeks (Mujika & Padilla 2000). Daniels publishes a similar table. Rule [H]:

| Time off (no running) | VDOT multiplier | Volume restart (% of prior) |
|---|---|---|
| ≤ 5 days | 1.00 | 100% |
| 6–14 days | 0.97 | 80% |
| 15–28 days | 0.93 | 60–70% |
| 29–56 days | 0.88 | 50% |
| > 8 weeks | 0.80–0.85; **re-test** | treat as new runner of the appropriate tier |

Cross-training during the break: halve the loss [H].

### 4.4 Training paces (intensity zones)

| Zone | Purpose | Pace definition [C] | % HRmax (approx.) | RPE (1–10) | Talk test |
|---|---|---|---|---|---|
| **E** Easy / Long | Aerobic base, capillaries, tissue tolerance, recovery | 62–70% of VDOT | 65–78% | 2–4 | Full sentences |
| **M** Marathon | FM-specific; steady aerobic | VDOT marathon-equivalent pace | 80–88% | 5–6 | Short sentences |
| **T** Threshold | Raise lactate threshold; "comfortably hard" | 88% of VDOT (≈ race pace for ~50–60 min) | 88–92% | 6–7 | A few words |
| **I** Interval | VO2max | 97.5–100% of VDOT (≈ 3k–5k race pace) | 95–100% (at end of rep) | 8–9 | No |
| **R** Repetition | Speed, economy, form | ≈ current mile race pace | n/a (too short) | 9 | No |
| Strides | Neuromuscular; 15–20 s fast and relaxed | ≈ R pace, by feel | n/a | 7–8 | n/a |

Reference outputs (from `running_plan/vdot.py`, per km; R per 400 m):

| VDOT | 5k | FM equiv. | E | M | T | I | R/400 |
|---|---|---|---|---|---|---|---|
| 40 | 24:06 | 3:49:37 | 6:07–6:44 | 5:27 | 5:06 | 4:41 | 1:46 |
| 45 | 21:49 | 3:28:16 | 5:34–6:08 | 4:56 | 4:38 | 4:16 | 1:36 |
| 50 | 19:56 | 3:10:40 | 5:07–5:38 | 4:31 | 4:15 | 3:55 | 1:27 |
| 55 | 18:22 | 2:55:55 | 4:44–5:13 | 4:10 | 3:56 | 3:37 | 1:20 |
| 60 | 17:03 | 2:43:22 | 4:25–4:52 | 3:52 | 3:40 | 3:23 | 1:14 |

Validation: Daniels' published VDOT 40 row gives 10k 50:03, FM 3:49:45, T 5:06 and I 4:42. The code's results agree within about 10 seconds.

**Which VDOT to use for each pace [C]:**
- E, T, I and R use **current** VDOT. Training at goal fitness before having it is the most common cause of overcooked plans.
- **Goal race pace is not used from day one.** Race-pace work starts at the **predicted** race pace from current VDOT. It moves toward goal pace only as recalibrated VDOT (tune-ups and time trials) supports it. A goal that needs +1.3 VDOT cannot be trained at goal pace in week 8 if the runner has not gained that fitness yet.
- **Dose by the zone the pace actually falls in.** If a race-pace rep is within `GOAL_PACE_T_MARGIN` (2%) of current T pace, or faster, it counts against the **T cap** (10% of weekly volume), not the race-pace cap. Example: goal HM pace 5:07/km against current T 5:05/km is threshold work.
- **Below VDOT 30 (`EFFORT_BASED_EASY_BELOW_VDOT`), easy runs are by effort [C/H].** Daniels' tables start at VDOT 30 (about a 30:40 5k), so slower paces are extrapolated. Near this level the E range also overlaps brisk walking (a 41:00 5k gives E 10:00–10:50/km). Easy and long runs are then prescribed by talk test and RPE 2–4, with E_fast shown only as a speed limit ("no faster than 10:00/km"), and walk breaks are explicitly allowed. All paces are labelled low-confidence until a time trial confirms them.
- Recalculate VDOT after each tune-up race or time trial. Move paces up by **at most +1 VDOT per 3–4 weeks**, even if a race suggests more [H, after Daniels].

---

## 5. Periodization (macro plan)

### 5.1 Phases

| Phase | Focus | Typical content |
|---|---|---|
| **Base** | Volume, frequency, tissue tolerance | E runs, long run, strides, hill sprints; optional light T |
| **Build** | Raise threshold and VO2max | T and I sessions, long run progresses |
| **Specific** | Race-specific | Goal-pace work; long runs with race-pace segments (HM/FM); race-pace intervals (5k/10k) |
| **Taper** | Freshen up | Volume down 40–60%, intensity kept (§5.4) |

Phase proportions by goal (fraction of non-taper weeks) [C/H]:

| Goal | Base | Build | Specific | Taper |
|---|---|---|---|---|
| 5k | 30% | 40% | 30% | 1 wk |
| 10k | 35% | 35% | 30% | 1–1.5 wk |
| HM | 35% | 30% | 35% | 1.5–2 wk |
| FM | 35% | 25% | 40% | 2–3 wk |
| speed | 20% | 50% | 30% | optional "test" week |
| aerobic_base | 80% | 20% (light T only) | n/a | n/a |
| maintenance | n/a | flat (§7.4) | n/a | n/a |
| recovery / return | progressive Base only | n/a | n/a | n/a |

If the runner is not at least at Intermediate base volume for the goal distance, extend Base first. Shrink Specific last.

### 5.2 Plan length [C]

| Goal | Minimum | Typical | Notes |
|---|---|---|---|
| 5k | 6 wk | 8–12 wk | |
| 10k | 8 wk | 10–12 wk | |
| HM | 10 wk | 12–16 wk | Beginner should start at ≥ 15 km/wk and long run ≥ 6 km |
| FM | 12 wk | 16–20 wk | Beginner should start at ≥ 40 km/wk and long run ≥ 16 km. Otherwise prepend an aerobic_base block. |

If time < minimum: offer options instead of compressing silently. Choices are (a) a later race, (b) a "finish" objective with a shorter plan, or (c) a capped plan with a warning.

**Reachability check [C/H].** Races are exempt from the spike rule (§6.4), so a plan must prove it can build a long run that makes the race reasonable. Simulate the volume and long-run curves under *all* caps (ramp, frequency, share, spike, time). Then require a projected peak long run of at least `MIN_PEAK_LONG_RUN`:

| Goal | Projected peak long run |
|---|---|
| HM | ≥ 16 km or ≥ 1:45 |
| FM | ≥ 26 km or ≥ 2:45 |

If the check fails, the plan is blocked with options: a later race, more run days, or an aerobic_base block first. Example: a 30 km/wk beginner on 4 days peaks at 40 km/wk with a 16 km long run. The review found such a runner would have been sent into a 42.2 km race (a 260% session spike).

### 5.3 Goal feasibility check [H]

Compute `ΔVDOT = VDOT(goal) − VDOT(current, detrained, marathon-penalized for FM)`.
Rough achievable gain over one 12–16 week block, assuming the plan is followed:

| Performance tier | Plausible ΔVDOT per block |
|---|---|
| Developing / new runner | +3 to +6 |
| Intermediate | +1 to +3 |
| Advanced | +0.5 to +1.5 |

Thresholds use the range scaled by plan length:
- ΔVDOT ≤ range **midpoint**: accepted.
- Midpoint to **top** of range: "stretch goal" warning.
- Beyond the top: unrealistic. Propose the realistic target (current + midpoint gain), explain why, and let the user override (record the override).
- ΔVDOT < −1 (`CONSERVATIVE_GOAL_DELTA_VDOT`): flag as a "conservative goal" and offer the predicted time as an alternative.

Open question: the gain range should probably also depend on volume headroom and training age, not only age-grade (§12).

Plans built backward from impossible goals are the biggest real-world failure mode.

### 5.4 Taper [E]

Bosquet et al. 2007 meta-analysis (27 studies): **about 2 weeks**, with **volume cut 41–60%** in a progressive or exponential pattern, and **intensity and frequency maintained**. A 2023 endurance meta-analysis agreed (≤ 21 days, 41–60%, intensity and frequency unchanged). Rules:
- 5k/10k: 7–10 days, final week at 50–60% of peak.
- HM: 10–14 days. Week −2 at about 75% of peak, race week at about 50% (excluding the race).
- FM: 14–21 days, at about 80% / 65% / 45% of peak.
- Keep short race-pace sessions. Drop long-run distance first.

---

## 6. Volume and long-run progression (the safety core)

### 6.1 Peak weekly volume targets [C/H]

Typical range, km/week:

| Goal | Beginner | Intermediate | Advanced |
|---|---|---|---|
| 5k | 20–30 | 35–55 | 60–90 |
| 10k | 25–35 | 40–60 | 65–100 |
| HM | 30–40 | 45–65 | 70–110 |
| FM | 40–55 | 55–80 | 85–130 |

`peak = max(start, min(target_for_tier, start × 1.5, frequency_cap, time_cap))` [H]:
- **Target for tier:** the midpoint of the range above.
- **Frequency cap:** `days_per_week × max_sensible_run_avg`, where the average is 10 km for Beginner, 13 km for Intermediate and 16 km for Advanced [H].
- **Time cap:** the weekday maximum and the long-run maximum.

The outer `max(start, …)` means a cap **never prescribes a cut** in current volume (outside maintenance and recovery goals). If current volume already exceeds the frequency cap, hold it and warn.

### 6.2 Weekly progression

What the evidence says [E]:
- The "10% rule" has **little direct support**.
  - Buist 2008 (GRONORUN randomized trial, n = 532 novices): a graded 10%-rule programme gave the same injury rate as a standard programme (20.8% vs 20.3%).
  - Nielsen 2014 (cohort, n = 874 novices, groups < 10% / 10–30% / > 30%): more than 30% progression over 2 weeks was associated with more *distance-related* injuries than less than 10% (HR 1.59, 95% CI 0.96–2.66, borderline).
- Large GPS cohort (Frandsen 2025, n ≈ 5,200, 588k sessions): **week-to-week change was not associated with injury**, but single-session spikes were (§6.4).
- The acute:chronic workload ratio (ACWR) has been heavily criticized on statistical grounds (Impellizzeri 2020). **Do not build the engine on ACWR.**

Framework rule [H]:
- Average ramp: Beginner +5–8% per week, Intermediate +8–10%, Advanced +10%. Never exceed **+20% per week** [H] or **+30% across 2 weeks** [E→H, Nielsen 2014].
- All ramp and spike baselines use **logged actual runs**, not planned ones (§10).
- **Injury-history modifier** [E→H]: an injury in the last 12 months, or any bone-stress injury ever, means:
  - ramp rate one tier lower
  - 2:1 cycles
  - `SPIKE_LIMIT_AFTER_INJURY` = 1.05 instead of 1.10
- Cross-training replaces aerobic minutes but **never counts** toward running ramp or spike baselines.
- A beginner adding a run day counts as a ramp week. Do not add a day and distance in the same week.
- Step loading: **3 build weeks, then 1 down week at −20 to −30%** [C]. Masters (50+), beginners and runners with recent injury use **2:1** [H]. Many novice plans use 3:1, so this is a cautious choice, not consensus.
- After reaching peak, hold it (±5%) instead of continuing to climb.

### 6.3 Intensity distribution [E/C]

- Target **≥ 80% of weekly running time in zone E**. Beginners should be at ≥ 85–90%. Strides do not count as quality.
- Polarized distribution (lots of easy, some hard, little in between) is at least as good as threshold-heavy training. A 2024 meta-analysis found it superior for VO2peak, mainly in short interventions and highly trained athletes, with no clear advantage on other performance measures. Practical takeaway: keep easy days easy, and the exact model matters less. Use "pyramidal" (E > T > I) for HM/FM and allow more I for 5k/10k.

Per-session dose caps (Daniels) [C]:

| Zone | Max in one session |
|---|---|
| T | ≤ 10% of weekly volume (continuous tempo ≤ 20 min for beginners) |
| I | ≤ min(8% of weekly volume, 10 km); reps 2–5 min |
| R | ≤ min(5% of weekly volume, 8 km); reps ≤ 2 min, full recovery |
| M | ≤ min(20% of weekly volume, 29 km) |
| HM pace | ≤ min(20%, 16 km) [H]; dosed as T if within 2% of current T (§4.4) |
| 10k pace | ≤ min(12%, 9 km) [H] |
| 5k pace | ≤ min(8%, 10 km) [H] (same as I) |

### 6.4 Long run [E/C]

- **Spike rule [E]:** no single run should exceed **110% of the longest run in the previous 30 days** (`SPIKE_WINDOW_DAYS` = 30). Frandsen 2025 found injury rates were 64% higher for 10–30% spikes and 128% higher for spikes over 100%.
  - Apply it to *every* run, not just the long run.
  - **The race itself is exempt**; the reachability check (§5.2) covers it.
  - With no logged history, seed the window with `longest_run_30d_km`, or with the longest continuous run for novices.
- Share of the week [C/H]: the long run is ≤ 30% of weekly volume by default. With few run days, a 30% long run would be *shorter than an average run*, so the cap scales with frequency: 2 days 55%, 3 days 45%, 4 days 40%, 5 days 35%, 6–7 days 30% (`LONG_RUN_SHARE`). The plan warns whenever the share is above 30%.
- Time cap [C]: about 2:30 for most runners, 3:00 for beginner and intermediate marathoners (beyond that the fatigue cost outweighs the benefit).
- Peak long-run targets, km:

| Goal | Beginner | Intermediate | Advanced |
|---|---|---|---|
| 5k / 10k | 8–12 | 14–18 | 18–24 |
| HM | 16–19 | 19–24 | 22–28 |
| FM | 26–30 (or 3 h) | 29–32 | 32–37 |

- Progress the long run by 1–2 km per build week, cut back in down weeks, and place the longest run 3 weeks out (FM) or 2 weeks out (HM).

### 6.5 Weekly template rules

Number of quality sessions, counting the long run, by tier and days per week [C/H]:

| days/wk | Beginner | Intermediate | Advanced |
|---|---|---|---|
| 2–3 | LR + 0 (strides only) | LR + 1 | LR + 1 |
| 4 | LR + 0–1 | LR + 1 | LR + 1–2 |
| 5 | LR + 1 | LR + 1–2 | LR + 2 |
| 6–7 | not advised in v1 | LR + 2 | LR + 2 (+ optional doubles) |

Placement:
1. Put the long run on `long_run_day`.
2. Put quality 1 midweek, about 3 days before the long run (Thu for a Sun long run, so it is 4 days after the previous long run). Put quality 2 at least 48 h after quality 1 and at least 48 h before the long run (e.g. Tue + Thu for a Sun long run).
3. No hard session the day before the long run. The day after the long run is rest or easy.
4. Fill the remaining days with easy runs. Rest days go where the user is unavailable, then after the long run.
5. Distribute volume: long run first (§6.4), then quality-day totals (warm-up and cool-down included), then spread the rest across easy days. Minimum easy run is 4 km or 25 min [H]. If the remaining volume cannot fit within caps, lower the weekly target. Never push the long run above its cap.

---

## 7. Goal-specific playbooks

### 7.1 Race (5k / 10k / HM / FM)

| Phase | 5k / 10k key sessions | HM / FM key sessions |
|---|---|---|
| Base | E + strides; hill sprints 6–10 × 10 s; optional fartlek | E + strides; long run E; light cruise intervals (T) |
| Build | I: 5–6 × 1000 @ I (2–3 min jog); T: 3–4 × 1.6 km @ T (1 min) | T: tempo 20–30 min or 4–5 × 1.6 km; occasional I (5 × 1000) |
| Specific | Race-pace reps (10k: 3 × 3 km @ 10k pace; 5k: 5 × 1 km @ 5k pace); R for speed | HM: 2–3 × 5 km @ HM pace; long run with last 5–8 km @ HM pace. FM: long run with 10–20 km @ M; 2–3 × 6 km @ M |
| Taper | Short race-pace sharpening, strides | Short M/HM-pace segments, strides |

`finish` objective: replace Build and Specific intervals with T and fartlek, and include goal-effort segments in long runs. Beginners may use run-walk (e.g. 4:1 minutes) [C].

### 7.2 Speed (without a fixed race)

More I and R work. Allow up to 2 quality days plus the long run for Intermediate and above. The long run is moderate: ≤ 25% of the week (`SPEED_LONG_RUN_SHARE`). Run a 5k time trial every 4–6 weeks to recalibrate VDOT. Volume stays roughly flat (±10%).

### 7.3 Aerobic endurance (base building)

The goal is to reach the target volume. About 90% of the running is E (`AEROBIC_BASE_MIN_EASY_SHARE`). Run strides 2× per week. Do one T session per week after week 3 (Intermediate and above). Use hill sprints for robustness. Progress per §6.2 until the target is reached, then hold for at least 3 weeks. This is the default "pre-block" when a race plan would start below the minimum base.

### 7.4 Maintenance [E→H]

Reduced-training research (Spiering 2021 review, built largely on Hickson's 1980s studies): endurance holds for **up to 15 weeks on as few as 2 sessions/week, or with volume per session cut 33–66%, provided intensity is maintained**. Caveats: the subjects were mostly recently trained non-runners, and the authors say there are not enough data for athletes. Keeping ≥ 3 runs/week is an [H] choice for *tissue tolerance* (impact loading), not for aerobic fitness. Rule [H]:
- Volume 50–70% of the previous normal; keep at least 3 runs per week.
- Keep **1 quality session** per week (rotate T and I) and a **long run at about 60–70% of the previous length**.
- No progression. Optional 4-weekly fitness check (time trial or fixed-HR run).

### 7.5 Recovery (post-race reverse taper) [C/H]

- Days of **no hard running** ≈ race distance in km ÷ 3 (5k ≈ 2 days, HM ≈ 7 days, FM ≈ 14 days). This is a *softened* version of the old "one easy day per mile raced" rule, which would give 26 days for FM [H].
- FM: 3–7 days off or cross-train, then E running with volume over 3 weeks at 30% → 50% → 70%.
- HM: about 2 days off, then 2 weeks at 50% → 75%.
- Then hand off to the next goal.

### 7.6 Return to running (after a break or cleared injury)

- Apply §4.3 to VDOT and starting volume.
- **Run-walk entry** (`RUN_WALK_LADDER`: 1 min run / 1 min walk × 10, progressing to continuous 30 min) is used for:
  - returns from injury, especially bone stress
  - breaks longer than 8 weeks (`RUN_WALK_THRESHOLD_DAYS` = 56)
  - anyone who cannot run 20 min continuously

  Advance at most one step every 2 sessions, and only if pain stays ≤ 2/10 during the run and the next morning [C].
- **Non-injury breaks of 15–56 days:** restart *continuous* easy running at the §4.3 volume, with no run-walk.
- No quality sessions until 3 weeks of pain-free continuous running.

### 7.7 General fitness and true novices

The generator always asks "Can you run 30 minutes non-stop?" (`can_run_continuous_min`). If the answer is missing, the plan warns and assumes yes.

- **Can run ≥ 30 min continuously:** 3–4 days per week, 20–45 min, mostly E with strides. Optional fartlek once per week after week 4. Progression per §6.2 with a Beginner ramp.
- **Cannot run 30 min continuously** (`NOVICE_CONTINUOUS_RUN_MIN`): start on the run-walk ladder (§7.6), prescribed in **minutes and RPE/talk test only**, with no paces and no hard sessions. Entry is the hardest rung whose run segment the runner can already do (someone who can run 12 min starts at 10 min run / 1 min walk, not 1/1). After continuous 30 min, the goal plan starts. Offer a time trial once 3 weeks of continuous running are logged.
- **Runner already logs real volume with walk breaks** (for example 25 km/week of run-walk): keep the current weekly time, and apply the rung's run:walk ratio *inside* each run instead of shortening sessions to the ladder's length. Progress the ratio, not the volume, until runs are continuous [H]. Not yet implemented in code.

---

## 8. Workout library and pace adjustments

### 8.1 Library (parameterized)

Each workout = `{type, purpose, warmup, main_set[], cooldown, total_km, zone_minutes{}, rpe_target, notes}`.

| ID | Main set template | Progression lever |
|---|---|---|
| `E` easy | X km @ E | distance |
| `E+S` easy + strides | X km @ E + 4–8 × 20 s strides | number of strides |
| `LR` long run | X km @ E | distance (§6.4) |
| `LR-prog` progression | last 20–30% of the long run from E to M or T | fast segment length |
| `LR-M` marathon long run | Y km @ M inside an X km long run | Y: 6 → 20 km |
| `LR-HM` | last Y km @ HM pace | Y: 3 → 8 km |
| `T-cruise` | n × 1.6 km @ T, 1 min jog | n: 3 → 5 |
| `T-tempo` | 20–30 min continuous @ T | duration |
| `I-1000` | n × 1000 m @ I, jog ≈ equal time | n: 4 → 6 |
| `I-pyramid` | 400-800-1200-800-400 @ I | volume ≤ cap |
| `R-200/400` | n × 200/400 @ R, full recovery | n |
| `HillSprint` | 6–10 × 8–10 s max hill, walk back | n |
| `Hill-reps` | 6–10 × 60–90 s uphill @ I effort | n |
| `Fartlek` | 6–10 × 1 min "on" / 1 min "off" | on-time |
| `RP` race-pace | n × d @ goal pace (sized per goal, §7.1) | n × d |
| `TT` time trial | 3k / 5k all-out (recalibrates VDOT) | n/a |

Standard warm-up and cool-down for quality: 10–15 min E (+ strides before I/R). Count them in weekly volume.

### 8.2 Prescribing duration vs. distance

- Express **beginner runs in minutes** and others in km, with the other value shown as an estimate.
- Long runs: prescribe km, and enforce the time cap using the E-pace midpoint.

### 8.3 Pace adjustments (pace → effort)

- **Heat/humidity:** slow E/M/T by about 1–3% per 5 °C above ~15 °C dew-point–adjusted temperature. Prefer HR or RPE targets on hot days [C/H].
- **Hills and trails:** prescribe by effort (RPE and HR), not pace.
- **Treadmill:** set 1% incline to approximate outdoor cost [C].
- **Altitude > 1,500 m:** prescribe by effort for the first 1–2 weeks [C].

### 8.4 What every daily prescription contains

| Field | Example |
|---|---|
| Type + purpose | "Tempo: raise lactate threshold" |
| Structure | WU · main set (reps × distance @ zone, recovery) · CD |
| Distance **and** estimated duration | 8.9 km, ~51 min (beginners: minutes first) |
| Pace target per segment | T 5:05/km; E 6:07–6:43/km |
| Effort fallback | RPE 6–7, "a few words" talk test; HR range if HRmax is measured |
| Conditions override | Heat, hills or trail → run by effort, not pace (§8.3) |
| Fuelling | Runs > 90 min: carbohydrate during the run |
| Stop rules | Pain > 3/10 or altered gait → stop; red flags (§12) |

Weekly summary: total km, total time, hard minutes, easy share, phase, and warnings (e.g. long-run share > 30%). Race week adds a **race-day pacing plan**: even splits at target pace and when to reassess.

---

## 9. The algorithm (end-to-end)

```text
INPUT: profile, goal, constraints
OUTPUT: plan = weeks[] → days[] → workout{type, km|min, paces, zone, rpe, notes}
(Names in CAPS are constants in running_plan/config.py — see §14.)

1. VALIDATE & SCREEN
   - Health screen "yes", RED-S screen "yes", current pain, or injury not cleared → blocking.
   - can_run_continuous_min < NOVICE_CONTINUOUS_RUN_MIN (30) → run-walk entry (§7.7),
     starting at the matching ladder rung; no hard sessions until 30 min continuous.
   - VDOT < EFFORT_BASED_EASY_BELOW_VDOT → E/LR by effort, E_fast as a ceiling (§4.4).
   - Missing race result → RPE/talk-test prescription; time trial in week 3–4
     (TIME_TRIAL_DISTANCE_BY_TIER). Easy-pace estimate maps to E_fast (low confidence).

2. FITNESS
   vdot_mult, volume_restart = DETRAINING[days_off]
   VDOT_cur = recency-decayed race VDOTs; if they spread > RESULT_DISAGREEMENT_VDOT,
              weight by closeness to goal distance (else take the best) × vdot_mult
   race-pace targets start at predicted pace and move toward goal pace with recalibrated VDOT;
   reps within GOAL_PACE_T_MARGIN of current T (or faster) are dosed against the T cap
   paces    = training_paces(VDOT_cur)            # *_FRACTION_OF_VDOT
   FM prediction × (1 + FM_PENALTY(weekly_km))

3. CLASSIFY
   load_tier = min(tier(weekly_km, LOAD_VOLUME_KM), tier(longest_30d, LOAD_LONG_RUN_KM) + 1,
                   tier(training_age, LOAD_TRAINING_AGE_YR) + 1)
   injury in last 12 mo or bone-stress ever → ramp one tier lower, 2:1, SPIKE_LIMIT_AFTER_INJURY
   perf_tier = tier(age_grade_pct, PERF_AGE_GRADE)

4. FEASIBILITY
   plan_weeks ≥ MIN_WEEKS[goal]; current base ≥ MIN_BASE[goal]   else → options, no silent compression
   ΔVDOT = VDOT(goal) − VDOT_cur
   (lo, hi) = VDOT_GAIN_RANGE[perf] × clamp(weeks / FEASIBILITY_REF_WEEKS, FEASIBILITY_SCALE_BOUNDS)
   mid = (lo + hi) / 2
   ΔVDOT ≤ mid → accepted;  ≤ top → stretch;  > top → unrealistic (propose current + mid)
   ΔVDOT < CONSERVATIVE_GOAL_DELTA_VDOT → "conservative goal" note
   REACHABILITY: simulate step 5 under all caps; peak LR ≥ MIN_PEAK_LONG_RUN[goal] else block

5. MACRO PLAN
   taper  = TAPER[goal] (fractions of peak);  non-taper weeks split by PHASE_SPLIT[goal]
   start  = weekly_km × volume_restart
   peak   = max(start, min(mid(PEAK_VOLUME_KM[goal][tier]), start × PEAK_MAX_GROWTH,
                           days × AVG_RUN_CAP_KM[tier]))          # caps never cut current volume
   cycle  = 2:1 if beginner or age ≥ MASTERS_AGE else 3:1
   build week:  vol = min(peak, last_build × (1 + RAMP_RATE[tier]))   (hold when a run day is added)
   down week:   vol = last_build × (1 − DOWN_WEEK_CUT)
   long run:    lr = min(prev_lr + LONG_RUN_STEP_KM, peak_lr, SPIKE_LIMIT × max_run(prior 30 d),
                         LONG_RUN_SHARE[days] × vol, max_long_run_minutes / E_pace)
                peak_lr = lo + PEAK_LONG_RUN_POSITION × (hi − lo) of PEAK_LONG_RUN_KM[goal][tier]
                down week: lr × (1 − LONG_RUN_DOWN_CUT)

6. WEEKLY TEMPLATE
   run days: choose_run_days (spread; TEMPLATE_* weights)
   quality:  QUALITY_COUNT[tier][days]; ≥ HARD_DAY_MIN_GAP_DAYS apart incl. long run;
             key session QUALITY_IDEAL_DAYS_BEFORE_LONG_RUN days before LR

7. WORKOUT SELECTION
   hard budget (min) = (1 − MIN_EASY_SHARE) × est. week minutes
   each session: RepSpec (T_CRUISE, I_1000_*, R_400, RACE_PACE_REPS[goal]) → reps_for(progression),
                 then capped by DOSE_CAP[zone], hard budget, spike cap, weekday time cap
   long-run variant by phase: LR → LR-prog (LR_PROG_*) → LR-HM (LR_HM_*) / LR-M (LR_M_*)
   time trials in down weeks before the specific phase

8. FILL & BALANCE
   easy km = vol − LR − quality → easy days (≥ MIN_EASY_RUN_KM, ≤ spike cap, ≤ LR)
   strides: STRIDES_PER_SESSION on 1–2 easy days
   never break a safety rule to hit a volume target — under-fill and note it instead

9. VALIDATE (independent re-check, validate.py) → any violation is a bug

10. ADAPT (weekly loop — §10)
```

---

## 10. Adaptation rules (closed loop)

Weekly check-in inputs: completion per session, session RPE, pain (0–10 with location), sleep/illness/stress (1–5), and race or time-trial results. Optional: resting HR, or HR at fixed easy pace.

| Signal | Action [C/H] |
|---|---|
| **Bone-stress red flags**: focal bony tenderness, pain at rest or at night, pain on hopping | **Stop running and refer.** Do not substitute easy running |
| Chest pain, fainting, palpitations, unusual breathlessness | **Stop and seek medical care.** Plan paused |
| Pain ≥ 3/10, or pain that alters gait or worsens during a run | Stop progression; replace quality with E or cross-training; 2+ days → suggest a professional |
| Missed ≤ 3 days | Continue; don't make up the missed km |
| Missed 4–10 days | Repeat the last completed week |
| Missed > 10 days | Apply §4.3, re-run steps 5–8 from today |
| Illness | No running with fever or symptoms below the neck. Resume at 50–70% for days equal to days ill |
| Easy-run RPE consistently ≥ 5, or session RPE +2 above target for 2+ sessions | Insert a down week; re-check paces |
| Quality sessions consistently easy (RPE −2) and fully completed for 3+ weeks | Allow +0.5–1 VDOT, or schedule a time trial |
| Race or time-trial result | Recompute VDOT (cap of +1 per 3–4 weeks, §4.4); re-run the feasibility check |
| Life stress or poor sleep (≤ 2/5) for a week | Swap the next quality session for E; hold volume |

Implementation rules for the loop:
- **Consistently** means ≥ 2 of the last 3 sessions of that type (`ADAPT_CONSISTENT_OF_LAST`).
- **Baselines from actuals.** Spike, ramp and long-run baselines are recomputed from logged runs, not planned ones.
- **Fixed race date.** "Repeat a week" or "insert a down week" pushes everything back, so the plan must compress. Compression order:
  1. Drop Build weeks first.
  2. Then drop Base weeks.
  3. Never shorten the taper.
  4. Never compress Specific below 2 weeks.

  After any shift, **re-run the feasibility and reachability checks**. If they fail, offer options (finish objective, revised target, later race).

---

## 11. Worked example

Computed by hand from the rules above. It will be replaced by generator output and kept as a regression test (review finding M2).

**Input:**
- 4-week average 40 km/wk; longest run in 30 days 16 km; 4 runs/week; 2 years consistent; age 34, M.
- Recent 10k 50:00 (6 weeks ago).
- Goal: HM in 12 weeks, target 1:48.
- Mon/Wed/Fri unavailable, so the runner runs Tue/Thu/Sat/Sun, long run Sunday.

**Step 2 – Fitness:** VDOT 40.0 → HM equivalent 1:50:52 (5:15/km). Paces: E 6:07–6:43, T 5:05, I 4:41/km.
**Step 3 – Classify:** volume 40 → Intermediate; long run 16 → Intermediate; training age 2 yr → Intermediate. Load tier = Intermediate. Age-grade ≈ 52.8% → performance tier Intermediate.
**Step 4 – Feasibility:** 1:48 needs VDOT 41.3, so ΔVDOT = +1.3. The Intermediate range (+1 to +3) scaled by 12/14 weeks is +0.86 to +2.57, midpoint +1.71. +1.3 ≤ midpoint → **accepted**. Reachability: projected peak long run 20.5 km ≥ 16 km ✓.
**Step 5 – Macro:** 10 non-taper weeks split 35/30/35 (rounding half up) → Base wks 1–4, Build 5–6, Specific 7–10, Taper 11, Race 12. Peak = max(40, min(55 [tier midpoint], 60 [1.5×], 52 [4 days × 13])) = **52 km**. Ramp 9%; 3:1 cycle → down weeks 4 and 8. Peak long run aim = 19 + 0.4 × (24 − 19) = 21 km. Long-run share cap at 4 days = 40%.

| Wk | Phase | Volume | Long run (share) | Thu quality | Notes |
|---|---|---|---|---|---|
| 1 | Base | 40 | 16 (40%) | Easy + hill sprints | strides 2× |
| 2 | Base | 43.5 | 17 (39%) | Easy + hill sprints | LR +6%, capped by share |
| 3 | Base | 47.5 | 18.5 (39%) | 2 × 1.6 km @ T | |
| 4 | Base (down) | 37 | 13 | **5k time trial** → recalibrate VDOT | −22% |
| 5 | Build | 52 | 20 (39%) | 3 × 1.6 km @ T | +9% vs wk 3; LR ≤ 1.1 × 18.5 |
| 6 | Build | 52 | 20.5 LR-prog | 25 min tempo @ T | see detail below |
| 7 | Specific | 52 | 20.5, last 3 km @ HM pace | 2 × 4 km @ HM pace | |
| 8 | Specific (down) | 40.5 | 14.5 | **10k tune-up race or 5k TT** | recalibrates race pace |
| 9 | Specific | 52 | 20.5 | 2 × 5 km @ HM pace | |
| 10 | Specific | 52 | 20.5, last ~4.5 km @ HM pace | 2 × 3 km @ HM pace | longest run 2 weeks out |
| 11 | Taper | 39 (75%) | 13 | 2 × 2.5 km @ HM pace | |
| 12 | Race | ~22 + race | race (Sun) | short sharpener Thu | target 26 km under-fills: race-eve run ≤ 4 km |

**HM pace used** follows §4.4. Weeks 7–8 use the **predicted** pace, 5:15/km. From week 9 the pace moves toward the goal of 5:07/km only as the week-4 and week-8 results support it, e.g. VDOT 40.6 → about 5:11/km. At 5:15/km the reps are 3.3% slower than T, so they count against the HM-pace cap (20% of the week = 10.4 km). If the goal pace were run now (5:07/km, within 2% of T), the reps would count against the T cap (5.2 km).

Checks:
- **Spike:** every long run is ≤ 110% of the 30-day maximum (16 → 17 → 18.5 → 20 = +6%, +9%, +8%).
- **Ramp:** ≤ +9% per build week and +19% over two build weeks.
- **Share:** ≤ 40%.
- **Hard budget:** within the 20% hard-time budget every week.
- ⚠ The plan warns that the long run is about 39% of volume (above the 30% default) and suggests a 5th short easy day as the alternative.

**Week 6 detail (Build, 52 km, paces from VDOT 40 unless the week-4 TT changed them):**

| Day | Workout | Distance | Est. time | Pace / target |
|---|---|---|---|---|
| Mon | Rest / strength (optional) | — | — | — |
| Tue | Easy + 6 × 20 s strides | 12.5 km | ~1:26 | E 6:07–6:43/km (RPE 2–4, full sentences) |
| Wed | Rest | — | — | — |
| Thu | **Tempo**: 2 km WU · 25 min @ T · 2 km CD | 8.9 km | ~51 min | T **5:05/km** (RPE 6–7, a few words). T = 4.9 km ≤ 10% cap |
| Fri | Rest / strength (optional) | — | — | — |
| Sat | Easy | 10 km | ~64 min | E, keep it truly easy before the long run |
| Sun | **Progression long run**: 16.4 km @ E, last 4.1 km building to M | 20.5 km | ~2:07 | E → M 5:26/km. ≤ 2:30 cap; 20.5 ≤ 1.1 × 20 |

Week total about 52 km, about 5:28. Hard time is about 47 of 328 min, so the **easy share is about 86%** (≥ 80% ✓). Fuelling: the long run is over 90 min, so take a carbohydrate source (§8.4).

---

## 12. Safety, scope and limitations

- **Not medical advice.** v1 screening is blocking: no plan is produced until each item is resolved.
  - **Health screen (PAR-Q+ style):** chest pain at rest or on exertion, fainting or dizziness, known heart, metabolic or renal disease, or a medication affecting heart rate or blood pressure. Any "yes" → see a clinician first.
  - **Current pain or uncleared injury** → see a professional. After clearance, use the return-to-running playbook (§7.6).
  - **Low energy availability (RED-S) screen** (offered to all, essential for women): no periods for ≥ 3 months, prior bone-stress injury, disordered eating or restrictive dieting. Any "yes" → refer to a clinician; do not build a volume-progression plan.
- **Stop rules printed on every plan:**
  - Chest pain, fainting, palpitations or unusual breathlessness → stop and seek care.
  - Bone-stress red flags (focal bony tenderness, pain at rest or at night, pain on hopping) → stop running and refer.
- **HR zones:** `220 − age` has an error of about ±10–12 bpm. Use a measured HRmax or prefer RPE and the talk test, especially for beginners.
- Out of scope for v1: ultras, multi-sport, pregnancy and postpartum, youth (< 16), doubles.
- Treat **all [H] thresholds as configuration**, not constants. Log plan outcomes (completion, injuries, race result vs. prediction) so they can be tuned.
- v1 includes three add-ons whose evidence is **not yet verified here**:
  - **Strength training:** 2×/week, optional, placed on hard days (after the run) or the day after the long run, never the day before a quality session or the long run. The reviewer cites moderate evidence for running economy (Blagrove 2018) and weak evidence for running-specific injury prevention (Toresdahl 2020).
  - **Fuelling note:** for runs over 90 min and all FM long runs.
  - **Cross-training:** replaces easy minutes but is excluded from ramp and spike baselines.
- Deferred to later versions: heat adjustment beyond effort-based guidance, HRV/readiness signals, menstrual-cycle adjustments, surface, and masters-specific recovery spacing.

### Open research questions for the next pass

1. A validated rule for the beginner→intermediate cut-off (or a decision to keep the two-axis approach).
2. Calibrating the marathon penalty (§4.2) against the Vickers & Vertosick model coefficients.
3. Verify strength-training evidence (Blagrove 2018; Toresdahl 2020) and its scheduling relative to quality days.
8. Should feasibility gain ranges depend on volume headroom and training age as well as age-grade?
4. Masters-specific adjustments (recovery days, 2:1 cycles), based on studies rather than coaching practice.
5. Female-specific considerations (menstrual cycle, RED-S screening).
6. HR-based zone accuracy vs. pace-based zones for beginners.
7. Whether to use the Strava connection (available in this environment) to auto-fill the 4-week volume, longest run in 30 days, and best efforts.

---

## 13. Sources

Physiology and pace model
- Daniels & Gilbert VDOT equations: summary and worked check at [notes.billmill.org](https://notes.billmill.org/fitness/calculating_v02_max.html) and [Runbundle VO2max calculator](https://runbundle.com/tools/vo2-max-calculators/vo2-max-calculator). Pace definitions: Daniels, *Daniels' Running Formula*, 4th ed. ([Human Kinetics](https://us.humankinetics.com/products/daniels-running-formula-3rd-edition)).
- Vickers & Vertosick (2016), *An empirical study of race times in recreational endurance runners*: [PMC5000509](https://pmc.ncbi.nlm.nih.gov/articles/PMC5000509/).
- Riegel formula background: [Wikipedia: Peter Riegel](https://en.wikipedia.org/wiki/Peter_Riegel).

Load and injury
- Frandsen et al. (2025), *How much running is too much? Identifying high-risk running sessions in a 5200-person cohort study*, BJSM: [PMC12421110](https://pmc.ncbi.nlm.nih.gov/articles/PMC12421110); [BJSM blog](https://blogs.bmj.com/bjsm/?p=11751).
- Nielsen et al. (2014), *Excessive progression in weekly running distance and risk of running-related injuries*, JOSPT: [AAU record](https://vbn.aau.dk/da/publications/excessive-progression-in-weekly-running-distance-and-risk-of-runn).
- Buist et al. (2008), *No effect of a graded training program on the number of running-related injuries in novice runners* (GRONORUN RCT): [RUG record](https://research.rug.nl/en/publications/no-effect-of-a-graded-training-program-on-the-number-of-running-r/).
- Saragiotto et al. (2014), *What are the main risk factors for running-related injuries?*: [PubMed 24809248](https://pubmed.ncbi.nlm.nih.gov/24809248/).
- Systematic review on training-load progression: [PMC9528699](https://pmc.ncbi.nlm.nih.gov/articles/PMC9528699/table/i1938-162X-57-7-650-t02).
- Impellizzeri et al. (2020), ACWR critique: [PMC7534938](https://pmc.ncbi.nlm.nih.gov/articles/PMC7534938); editorial [PMC8138569](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8138569/).

Intensity distribution
- Silva Oliveira et al. (2024), *Polarized vs other TID: systematic review & meta-analysis*, Sports Med: [PMC11329428](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11329428/).
- Rosenblat et al. (2019), polarized vs threshold meta-analysis: [PubMed 29863593](https://pubmed.ncbi.nlm.nih.gov/29863593/).

Taper, maintenance and detraining
- Bosquet et al. (2007), *Effects of tapering on performance: a meta-analysis*: [PubMed 17762369](https://pubmed.ncbi.nlm.nih.gov/17762369/).
- Tapering in endurance athletes (2023 meta-analysis): [PMC10171681](https://pmc.ncbi.nlm.nih.gov/articles/PMC10171681/).
- Spiering et al. (2021), *Maintaining physical performance: the minimal dose of exercise needed*: [PubMed 33629972](https://pubmed.ncbi.nlm.nih.gov/33629972).
- Mujika & Padilla (2000), detraining: [PubMed 11252068](https://pubmed.ncbi.nlm.nih.gov/11252068/).
- Neufer (1989), reduced training and detraining: [PubMed 2692122](https://pubmed.ncbi.nlm.nih.gov/2692122/).
- Detraining meta-analysis (2023): [Frontiers in Physiology](https://frontiersin.org/articles/10.3389/fphys.2023.1334766/full).

Classification
- WMA age-grading explanation: [WMA Road Age Standards 2010](https://world-masters-athletics.org/wp-content/uploads/2018/02/Road_Age_Standards_WMA_2010-Explanation.pdf); [USATF Masters age grading](https://usatfmasters.org/age-grading/); tables at [AlanLyttonJones/Age-Grade-Tables](https://www.github.com/AlanLyttonJones/Age-Grade-Tables).

---

## 14. Parameter registry

Every number the generator uses is a named constant in [`running_plan/config.py`](../running_plan/config.py) (model coefficients in [`running_plan/vdot.py`](../running_plan/vdot.py)). Treat [H] values as tuning knobs.

### Pace model
| Name | Value | Tag | Meaning |
|---|---|---|---|
| `VO2_COST_INTERCEPT` / `_LINEAR` / `_QUADRATIC` | −4.60 / 0.182258 / 0.000104 | [E] | O₂ cost of running at v m/min |
| `SUSTAINABLE_BASE` | 0.8 | [E] | Asymptotic %VO2max for very long efforts |
| `SUSTAINABLE_SLOW_AMPLITUDE` / `_DECAY_PER_MIN` | 0.1894393 / 0.012778 | [E] | Slow-decay term of sustainable %VO2max |
| `SUSTAINABLE_FAST_AMPLITUDE` / `_DECAY_PER_MIN` | 0.2989558 / 0.1932605 | [E] | Fast-decay term |
| `EASY_FAST_FRACTION_OF_VDOT` / `EASY_SLOW_…` | 0.70 / 0.62 | [C] | Easy-zone bounds |
| `THRESHOLD_FRACTION_OF_VDOT` | 0.88 | [C] | T pace |
| `INTERVAL_FRACTION_OF_VDOT` | 0.975 | [C] | I pace |
| `REPETITION_RACE_DISTANCE_M` | 1609.34 | [C] | R pace = mile race pace |
| `FM_PENALTY` | 8% @ ≤30 km/wk → 0% @ ≥70 | [H] | Marathon prediction slow-down |
| `RACE_FULL_WEIGHT_WEEKS` / `RACE_DECAY_PER_WEEK` / `RACE_MAX_AGE_WEEKS` | 8 / 0.15% / 52 | [H] | Race-result recency |
| `DETRAINING` | §4.3 table | [E→H] | VDOT multiplier and volume restart by days off |
| `VDOT_MAX_GAIN` per `VDOT_MAX_GAIN_WEEKS` | +1 per 3 wk | [H] | Recalibration cap |
| `TIME_TRIAL_WEEK_WITHOUT_RACE` | 3 | [C] | No race result → RPE-only until this week's TT (replaces v0.1 default-VDOT placeholder) |

### Classification & feasibility
| Name | Value | Tag | Meaning |
|---|---|---|---|
| `LOAD_VOLUME_KM` | 25 / 55 | [H] | Beginner/intermediate upper bounds, weekly km |
| `LOAD_LONG_RUN_KM` | 10 / 21 | [H] | … longest run in 30 days (lowers the tier by ≤ 1 step) |
| `LOAD_TRAINING_AGE_YR` | 1 / 3 | [H] | … years of consistent running |
| `PERF_AGE_GRADE` | 50 / 65 % | [H] | Performance-tier bounds |
| `AGE_GRADE_STANDARD_S`, `AGE_SLOWDOWN` | approx. | [H] | Stand-in for official WMA tables |
| `MIN_WEEKS`, `TYPICAL_WEEKS`, `MIN_BASE` | §5.2 (FM base 40 km / 16 km) | [C] | Plan-length and starting-base minimums |
| `VDOT_GAIN_RANGE` | §5.3 | [H] | Plausible VDOT gain per block |
| `FEASIBILITY_REF_WEEKS` / `FEASIBILITY_SCALE_BOUNDS` | 14 / 0.5–1.2 | [H] | Scale gain range by plan length |
| Feasibility bands | accept ≤ mid, stretch ≤ top | [H] | Replaces v0.1 `STRETCH_FACTOR` (review M9) |

### Load & progression
| Name | Value | Tag | Meaning |
|---|---|---|---|
| `PEAK_VOLUME_KM` | §6.1 | [C] | Peak weekly km by goal × tier |
| `PEAK_MAX_GROWTH` | 1.5 | [H] | Peak ≤ 1.5 × starting volume |
| `AVG_RUN_CAP_KM` | 10 / 13 / 16 | [H] | Frequency cap: peak ≤ days × this |
| `RAMP_RATE` | 6 / 9 / 10 % | [H] | Build-week increase by tier |
| `MAX_WEEKLY_INCREASE` / `MAX_TWO_WEEK_INCREASE` | 20% / 30% | [E/H] | Hard ceilings (Nielsen 2014) |
| `DOWN_WEEK_CUT` | 22% | [C] | Down-week volume reduction |
| `MASTERS_AGE` | 50 | [C] | Switch to 2:1 cycles |
| `SPIKE_LIMIT` / `SPIKE_WINDOW_DAYS` | 1.10 / 30 | [E] | Any run ≤ 110% of longest in prior ~30 d (Frandsen 2025) |
| `LONG_RUN_SHARE` | 55/45/40/35/30 % by days | [C/H] | Long-run share cap |
| `LONG_RUN_MAX_MIN` / `_FM` | 150 / 180 | [C] | Long-run time caps |
| `LONG_RUN_STEP_KM` / `LONG_RUN_DOWN_CUT` | 2 km / 28% | [C] | Long-run progression |
| `PEAK_LONG_RUN_KM` / `PEAK_LONG_RUN_POSITION` | §6.4 / 0.4 | [C/H] | Peak LR range and where to aim in it |
| `TAPER`, `TAPER_LONG_RUN` | §5.4 | [E] | Taper volume fractions (Bosquet 2007) |

### Intensity & sessions
| Name | Value | Tag | Meaning |
|---|---|---|---|
| `MIN_EASY_SHARE` / `_BEGINNER` | 80% / 85% | [E/C] | Minimum easy share of running time |
| `DOSE_CAP` | §6.3 | [C] | Per-session caps by zone (Daniels) |
| `QUALITY_COUNT` | §6.5 | [C/H] | Quality sessions by tier × days |
| `HARD_DAY_MIN_GAP_DAYS` / `QUALITY_IDEAL_DAYS_BEFORE_LONG_RUN` | 2 / 3 | [C] | Hard-day spacing |
| `TEMPLATE_*` weights | 3 / 2 / 2 | [H] | Run-day selection scoring |
| `RepSpec` sessions: `T_CRUISE*`, `I_1000_*`, `R_400`, `RACE_PACE_REPS` | config | [C/H] | Rep length options, start/max/min reps, progression rate, recovery |
| `TAPER_REP_LENGTH_SCALE` / `_COUNT_REDUCTION` | 0.5 / 1 | [H] | Taper sharpener sizing |
| `TEMPO_*` | 20 + 5/step; beginner 15 + 2, ≤ 20 | [C/H] | Tempo duration |
| `FARTLEK_*`, `HILL_SPRINT_*`, `STRIDE_*` | config | [C] | Session structure |
| `LR_PROG_*`, `LR_HM_*`, `LR_M_*` | config | [C/H] | Long-run fast-segment sizing |
| `WARMUP_KM` / `MIN_WARMUP_KM` / `WARMUP_SHRINK_STEP_KM` | 1.5–3 / 1 / 0.5 | [H] | Warm-up sizing |
| `MIN_EASY_RUN_KM` | 4 | [H] | Shortest easy run worth scheduling |
| `MAINTENANCE_VOLUME` / `_LONG_RUN` | 60% / 65% | [E/H] | Maintenance sizing |
| `RECOVERY_WEEKS` / `RECOVERY_NO_HARD_DAYS` | §7.5 | [C/H] | Reverse taper |
| `RUN_WALK_LADDER` / `RUN_WALK_THRESHOLD_DAYS` / `RUN_WALK_PAIN_STOP` | config / 56 / 2 | [C] | Return-to-running |
| `VALIDATE_*_TOLERANCE` | small | n/a | Rounding slack in the validator (not rule slack) |

### Rules added after review (v0.2)
| Name | Value | Tag | Meaning |
|---|---|---|---|
| `MIN_PEAK_LONG_RUN` | HM 16 km / 105 min; FM 26 km / 165 min | [C/H] | Reachability check (§5.2) |
| `SPIKE_LIMIT_AFTER_INJURY` | 1.05 | [H] | Spike limit after a recent or bone-stress injury |
| `GOAL_PACE_T_MARGIN` | 2% | [H] | Race-pace reps this close to T are dosed as T |
| `RESULT_DISAGREEMENT_VDOT` | 1.0 | [H] | Above this spread, weight results by distance closeness |
| `CONSERVATIVE_GOAL_DELTA_VDOT` | −1.0 | [H] | Flag goals well below current fitness |
| `NOVICE_CONTINUOUS_RUN_MIN` | 30 | [C] | Below this → run-walk entry (raised from 20 in v0.3) |
| `EFFORT_BASED_EASY_BELOW_VDOT` | 30 | [C/H] | Below this, easy runs by effort; E_fast is a ceiling |
| `SPEED_LONG_RUN_SHARE` / `AEROBIC_BASE_MIN_EASY_SHARE` | 25% / 90% | [C] | Goal-specific limits (§7.2, §7.3) |
| `ADAPT_CONSISTENT_OF_LAST` | 2 of 3 | [H] | Definition of "consistently" (§10) |
| `RACE_EVE_MAX_KM` | 4 | [C] | Day-before-race run cap |

---

## 15. Review log

**v0.2:** an independent reviewer (exercise-physiology and coaching perspective) assessed v0.1. All Critical and Major findings were accepted and applied:
- **C1** reachability check.
- **C2** blocking screening and stop rules.
- **M1** race-pace dosing by actual zone, with goal pace phased in.
- **M2** worked example recomputed from the rules.
- **M3** caps never cut current volume.
- **M4** long-run axis lowers the tier by at most one step.
- **M5** return-to-running split.
- **M6** novice run-walk entry, RPE-only until a TT in week 3–4.
- **M7** fixed-race-date compression order and baselines from actual runs.
- **M8** injury-history modifiers.
- **M9** stricter feasibility.
- **M10** weighting results by distance.

Minor fixes:
- Buist attribution for the 10%-vs-24% result.
- Maintenance claim softened (Spiering 2021).
- Quality-day placement made consistent with the code.
- Recovery rule relabelled as softened.
- Spike window set to 30 days.
- Validator long-run slack reduced to rounding only.
- Beginner 2:1 relabelled [H].

The Buist 2008 and Spiering 2021 corrections were independently re-checked. Blagrove 2018 and Toresdahl 2020 are cited by the reviewer and **not yet verified**.

**v0.3 (test with a 41:00 5k runner):** concerns found by hand-building a plan, resolved one at a time.
- Validator applied session dose caps to the race itself: fixed.
- Easy pace overlapped walking speed and the pace model was extrapolated: continuous-run question always asked with a 30 min threshold and ladder entry by ability; easy runs by effort below VDOT 30 (§4.4, §7.7).
