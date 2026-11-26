# Running Plan Generator: Research & Algorithm Framework

Status: research draft v0.1 (2026-11-26). Units are metric. Convert miles at the input boundary.

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
| `injury_history` | list + current pain flag | Current pain → screen out or route to medical (§12). |
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

Rule: `load_tier = min(tier by volume, tier by long run, tier by training age + 1)` [H].
Taking the **minimum** is deliberate: injury risk follows the weakest link. The training-age term can only lower the tier by one step, so a 6-month runner already at 50 km/wk is still capped at Intermediate.

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

Daniels and Gilbert model ([reference code](./vdot.py)):

```
v       = distance_m / time_min                              # m/min
VO2     = -4.60 + 0.182258·v + 0.000104·v²
%max    = 0.8 + 0.1894393·e^(-0.012778·t) + 0.2989558·e^(-0.1932605·t)
VDOT    = VO2 / %max
```

Choosing which result to use:
1. Only include all-out races or time trials on roughly flat courses. Training runs underestimate fitness.
2. Weight by recency: full weight if ≤ 8 weeks old. Then decay it (§4.3) or drop it after 12 months [H].
3. Prefer distances closest to the goal distance when results disagree. An HM result predicts FM better than a 5k result does.
4. **No usable race:** schedule a time trial in week 1 or 2 (5k for most runners; 3k or a 30-minute test for beginners). Until then, estimate from easy pace: `VDOT_est ≈ VDOT whose E-pace midpoint = user's easy pace`, and lower confidence [H].

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

Reference outputs (from `vdot.py`, per km; R per 400 m):

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
- **Goal race pace** (HM or FM pace work) uses the *goal* time, but only if the goal passes the feasibility check (§5.3). Otherwise use the predicted time.
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
| FM | 12 wk | 16–20 wk | Beginner should start at ≥ 30 km/wk and long run ≥ 13 km. Otherwise prepend an aerobic_base block. |

If time < minimum: offer options instead of compressing silently. Choices are (a) a later race, (b) a "finish" objective with a shorter plan, or (c) a capped plan with a warning.

### 5.3 Goal feasibility check [H]

Compute `ΔVDOT = VDOT(goal) − VDOT(current, detrained, marathon-penalized for FM)`.
Rough achievable gain over one 12–16 week block, assuming the plan is followed:

| Performance tier | Plausible ΔVDOT per block |
|---|---|
| Developing / new runner | +3 to +6 |
| Intermediate | +1 to +3 |
| Advanced | +0.5 to +1.5 |

- Within range: accept.
- Up to 1.5× range: accept with a "stretch goal" warning.
- Beyond that: propose the realistic target, explain why, and let the user override (record the override).

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

`peak = clamp(target_for_tier, current × 1.0, current × 1.5)` [H]. Two further caps apply:
- **Frequency cap:** `peak ≤ days_per_week × max_sensible_run_avg`, where the average is 10 km for Beginner, 13 km for Intermediate and 16 km for Advanced [H].
- **Time cap:** the weekday maximum and the long-run maximum.

### 6.2 Weekly progression

What the evidence says [E]:
- The "10% rule" has **little direct support**. In novice runners (Nielsen 2014, n = 874), more than 30% progression over 2 weeks was associated with more distance-related injuries than less than 10% (HR 1.59, borderline significance). No difference was found between 10% and roughly 24%.
- Large GPS cohort (Frandsen 2025, n ≈ 5,200, 588k sessions): **week-to-week change was not associated with injury**, but single-session spikes were (§6.4).
- The acute:chronic workload ratio (ACWR) has been heavily criticized on statistical grounds (Impellizzeri 2020). **Do not build the engine on ACWR.**

Framework rule [H]:
- Average ramp: Beginner +5–8% per week, Intermediate +8–10%, Advanced +10%. Never exceed **+20% per week** or **+30% across 2 weeks**.
- A beginner adding a run day counts as a ramp week. Do not add a day and distance in the same week.
- Step loading: **3 build weeks, then 1 down week at −20 to −30%**. Masters (50+) and beginners use **2:1** [C].
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

### 6.4 Long run [E/C]

- **Spike rule [E]:** no single run should exceed **110% of the longest run in the previous 30 days**. Frandsen 2025 found injury rates were 64% higher for 10–30% spikes and 128% higher for spikes over 100%. Apply this to *every* run, not just the long run.
- Share of the week [C]: long run ≤ 30% of weekly volume (up to 35–40% only for low-frequency HM/FM plans, with a warning).
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
2. Put quality 1 about 3 days before the long run (e.g. Tue for a Sun long run). Put quality 2 at least 48 h after quality 1 and at least 48 h before the long run.
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

More I and R work. Allow up to 2 quality days plus the long run for Intermediate and above. Long run is moderate (≤ 25% of the week). Run a 5k time trial every 4–6 weeks to recalibrate VDOT. Volume stays roughly flat (±10%).

### 7.3 Aerobic endurance (base building)

The goal is to reach the target volume. About 90% of the running is E. Run strides 2× per week. Do one T session per week after week 3 (Intermediate and above). Use hill sprints for robustness. Progress per §6.2 until the target is reached, then hold for at least 3 weeks. This is the default "pre-block" when a race plan would start below the minimum base.

### 7.4 Maintenance [E]

Detraining research: VO2max and endurance hold with **volume and frequency cut by one-third to two-thirds, provided intensity is maintained**. Frequency is the least safe thing to cut. Rule [H]:
- Volume 50–70% of the previous normal; keep at least 3 runs per week.
- Keep **1 quality session** per week (rotate T and I) and a **long run at about 60–70% of the previous length**.
- No progression. Optional 4-weekly fitness check (time trial or fixed-HR run).

### 7.5 Recovery (post-race reverse taper) [C/H]

- Days of **no hard running** ≈ race distance in km ÷ 3 (5k ≈ 2 days, HM ≈ 7 days, FM ≈ 14 days), after the old rule of "one easy day per mile raced".
- FM: 3–7 days off or cross-train, then E running with volume over 3 weeks at 30% → 50% → 70%.
- HM: about 2 days off, then 2 weeks at 50% → 75%.
- Then hand off to the next goal.

### 7.6 Return to running (after a break or cleared injury)

- Apply §4.3 to VDOT and starting volume.
- Break ≥ 4 weeks or injury: start with **run-walk** (e.g. 1 min run / 1 min walk × 10–15, progressing to continuous 30 min), at most 1 progression step every 2–3 sessions, and only if pain stays ≤ 2/10 during the run and the next morning [C].
- No quality sessions until 3 weeks of pain-free continuous running.

### 7.7 General fitness

3–4 days per week, 20–45 min, mostly E with strides. Optional fartlek once per week after week 4. Progression per §6.2 with a Beginner ramp.

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

---

## 9. The algorithm (end-to-end)

```text
INPUT: profile, goal, constraints
OUTPUT: plan = weeks[] → days[] → workout{type, km|min, paces, zone, rpe, notes}

1. VALIDATE & SCREEN
   - Current pain / injury not cleared → route to return_to_running or medical advice.
   - Missing race result → plan a time trial in week 1–2; estimate VDOT from easy pace.

2. FITNESS
   VDOT_cur = best recency-weighted race VDOT × detraining_multiplier(break)
   paces    = training_paces(VDOT_cur)                       # §4.4
   if goal.type == race: pred = predict(goal.distance), FM penalty  # §4.2

3. CLASSIFY
   load_tier  = min(volume_tier, longrun_tier, training_age_tier + 1)   # §3.1
   perf_tier  = age_grade_tier(best recent race)                        # §3.2

4. FEASIBILITY
   check plan_weeks ≥ min_weeks(goal, load_tier)                         # §5.2
   check ΔVDOT within plausible range(perf_tier)                         # §5.3
   if fail → return options (later date / finish goal / revised target / base block first)

5. MACRO PLAN (work backward from race date or forward from start)
   taper_weeks = f(goal)                                                 # §5.4
   split remaining weeks into Base / Build / Specific                    # §5.1
   peak_vol    = clamp(peak_target(goal, load_tier), cur, cur×1.5) ∧ freq cap ∧ time cap
   weekly_vol[] = ramp(cur → peak, rate(load_tier), cycle = 3:1 or 2:1) then hold, then taper
   long_run[]   = progress(longest_30d → peak_LR(goal, tier)),
                  each week ≤ 1.10 × max(run in prior 30 d), ≤ 30% of week, ≤ time cap

6. WEEKLY TEMPLATE
   slots = place(long_run_day, quality_count(tier, days), spacing rules) # §6.5

7. WORKOUT SELECTION per week
   for each quality slot: choose from library by (phase, goal, perf_tier),
       apply progression lever, enforce dose caps (§6.3)
   long run variant by phase (E → prog → LR-M / LR-HM)
   down weeks: same structure, quality volume −30–40%, LR −25–35%
   insert TT / tune-up race at end of Base and mid-Build (if ≥ 10 weeks)

8. FILL & BALANCE
   easy km = weekly_vol − LR − quality totals → split across easy days (≥ min run)
   verify: easy share ≥ 80% of time; every run ≤ 1.10 × 30-day max; no hard-before-LR
   if violated → reduce weekly_vol (never break safety rules to hit a target)

9. ANNOTATE
   each workout: km, est. duration, pace range, HR/RPE alternative, purpose, warm-up/cool-down
   weekly: total km, time, % easy, phase, coaching note

10. ADAPT (weekly loop — see §10)
```

---

## 10. Adaptation rules (closed loop)

Weekly check-in inputs: completion per session, session RPE, pain (0–10 with location), sleep/illness/stress (1–5), and race or time-trial results. Optional: resting HR, or HR at fixed easy pace.

| Signal | Action [C/H] |
|---|---|
| Pain ≥ 3/10, or pain that alters gait or worsens during a run | Stop progression; replace quality with E or cross-training; 2+ days → suggest a professional |
| Missed ≤ 3 days | Continue; don't make up the missed km |
| Missed 4–10 days | Repeat the last completed week |
| Missed > 10 days | Apply §4.3, re-run steps 5–8 from today |
| Illness | No running with fever or symptoms below the neck. Resume at 50–70% for days equal to days ill |
| Easy-run RPE consistently ≥ 5, or session RPE +2 above target for 2+ sessions | Insert a down week; re-check paces |
| Quality sessions consistently easy (RPE −2) and fully completed for 3+ weeks | Allow +0.5–1 VDOT, or schedule a time trial |
| Race or time-trial result | Recompute VDOT (cap of +1 per 3–4 weeks, §4.4); re-run the feasibility check |
| Life stress or poor sleep (≤ 2/5) for a week | Swap the next quality session for E; hold volume |

---

## 11. Worked example

**Input:** 4-week average 40 km/wk, longest run in 30 days 16 km, 4 runs/week, 2 years consistent, age 34. Recent 10k 50:00 (6 weeks ago). Goal: HM in 12 weeks, target 1:48. Runs Tue/Thu/Sat/Sun, long run Sunday.

**Step 2 – Fitness:** VDOT 40.0 → HM equivalent 1:50:52. Paces: E 6:07–6:44, T 5:06, I 4:41/km.
**Step 3 – Classify:** volume 40 → Intermediate. Long run 16 → Intermediate. Training age 2 yr → Intermediate. Load tier = Intermediate. Age-grade of 50:00 at 34 M ≈ 52% → performance tier Intermediate.
**Step 4 – Feasibility:** 1:48 needs VDOT 41.3 → ΔVDOT +1.3, inside the Intermediate range (+1 to +3). Accept. 12 weeks ≥ HM minimum of 10.
**Step 5 – Macro:** Base wks 1–3, Build 4–7, Specific 8–10, Taper 11–12. Peak target 52 km (Intermediate HM range 45–65; frequency cap 4 × 13 = 52).

| Wk | Phase | Volume | Long run | Notes |
|---|---|---|---|---|
| 1 | Base | 40 | 16 | strides 2× |
| 2 | Base | 43 | 17 | |
| 3 | Base | 46 | 18.5 | first T-cruise |
| 4 | Down | 36 | 14 | 5k TT → recalibrate |
| 5 | Build | 47 | 19 | |
| 6 | Build | 50 | 20 | |
| 7 | Build | 52 | 21 | LR-prog |
| 8 | Down | 41 | 15 | 10k tune-up race or TT |
| 9 | Specific | 52 | 21 | LR-HM (last 6 km @ goal pace) |
| 10 | Specific | 50 | 18 | 3 × 4 km @ HM pace |
| 11 | Taper | 38 | 14 | volume about 75% of peak |
| 12 | Race | ~18 + race | race | 2 short sharpening runs |

Check: every long run is ≤ 110% of the prior 30-day maximum (16 → 17 is +6%; 17 → 18.5 is +9%; 18.5 → 19 is +3% …). The ramp is ≤ 10% per week, with down weeks at −20–22%.

⚠ Rule conflict the engine must surface: with only 4 days per week, the long run is **≈ 38–40% of weekly volume**, above the 30% default (§6.4). The low-frequency exception allows it with a warning. The engine should also offer the alternative: add a 5th short easy day, which brings the long run to about 32%.

**Week 6 detail (Build, 50 km, VDOT still 40 unless the week-4 TT changed it):**

| Day | Workout | Distance | Pace / target |
|---|---|---|---|
| Mon | Rest | n/a | n/a |
| Tue | **T-cruise**: 3 km WU + 3 × 1.6 km @ T (1 min jog) + 3 km CD | 11 km | T **5:06/km** (RPE 6–7). T total 4.8 km ≤ 10% cap |
| Wed | Rest or cross-train / strength | n/a | n/a |
| Thu | E + 6 × 20 s strides | 10 km | E 6:07–6:44/km |
| Fri | Rest / strength | n/a | n/a |
| Sat | E | 9 km | E 6:20–6:44/km (keep it easy before the long run) |
| Sun | **LR** | 20 km | E 6:07–6:44/km, ≈ 2:10 (≤ 2:30 cap); 20 ≤ 1.1 × 19 |

Easy share by time ≈ 92% (T work about 25 of about 316 min). Weekly total 50 km. HM goal pace for later Specific weeks: **5:07/km** (1:48).

---

## 12. Safety, scope and limitations

- **Not medical advice.** Screen for current pain, recent injury, and cardiac or medical red flags. Route those users to a professional, or to the return-to-running playbook only after clearance.
- Out of scope for v1: ultras, multi-sport, pregnancy and postpartum, youth (< 16), doubles.
- Treat **all [H] thresholds as configuration**, not constants. Log plan outcomes (completion, injuries, race result vs. prediction) so they can be tuned.
- Recommended add-ons that were **not researched in this pass**: strength training (commonly cited for running economy and injury resilience), mobility, footwear, fuelling for long runs, and sleep. Treat these as open items.

### Open research questions for the next pass

1. A validated rule for the beginner→intermediate cut-off (or a decision to keep the two-axis approach).
2. Calibrating the marathon penalty (§4.2) against the Vickers & Vertosick model coefficients.
3. Evidence for strength training and its scheduling relative to quality days.
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
- Systematic review on training-load progression: [PMC9528699](https://pmc.ncbi.nlm.nih.gov/articles/PMC9528699/table/i1938-162X-57-7-650-t02).
- Impellizzeri et al. (2020), ACWR critique: [PMC7534938](https://pmc.ncbi.nlm.nih.gov/articles/PMC7534938); editorial [PMC8138569](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8138569/).

Intensity distribution
- Silva Oliveira et al. (2024), *Polarized vs other TID: systematic review & meta-analysis*, Sports Med: [PMC11329428](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11329428/).
- Rosenblat et al. (2019), polarized vs threshold meta-analysis: [PubMed 29863593](https://pubmed.ncbi.nlm.nih.gov/29863593/).

Taper, maintenance and detraining
- Bosquet et al. (2007), *Effects of tapering on performance: a meta-analysis*: [PubMed 17762369](https://pubmed.ncbi.nlm.nih.gov/17762369/).
- Tapering in endurance athletes (2023 meta-analysis): [PMC10171681](https://pmc.ncbi.nlm.nih.gov/articles/PMC10171681/).
- Mujika & Padilla (2000), detraining: [PubMed 11252068](https://pubmed.ncbi.nlm.nih.gov/11252068/).
- Neufer (1989), reduced training and detraining: [PubMed 2692122](https://pubmed.ncbi.nlm.nih.gov/2692122/).
- Detraining meta-analysis (2023): [Frontiers in Physiology](https://frontiersin.org/articles/10.3389/fphys.2023.1334766/full).

Classification
- WMA age-grading explanation: [WMA Road Age Standards 2010](https://world-masters-athletics.org/wp-content/uploads/2018/02/Road_Age_Standards_WMA_2010-Explanation.pdf); [USATF Masters age grading](https://usatfmasters.org/age-grading/); tables at [AlanLyttonJones/Age-Grade-Tables](https://www.github.com/AlanLyttonJones/Age-Grade-Tables).
