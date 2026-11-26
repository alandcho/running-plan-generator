# Benchmark: How Commercial Tools Build Running Plans

Status: v0.2 (2026-11-26). Compares Runna, Garmin Coach / Run Coach, TrainAsONE, VDOT O2 and open-source projects (§8) with our framework ([running-plan-framework.md](running-plan-framework.md) v0.2).

**Source quality.** No vendor publishes its algorithm.
- **Runna** is the best documented. Its support centre describes its rules in some detail, and those articles were read directly (marked **[primary]**).
- **Garmin** is documented through one Garmin blog page **[primary]** plus reviews.
- **TrainAsONE and VDOT O2** come from app-store listings and search summaries only; their sites block automated access. Treat those claims as **[secondary]**.
- **Criticisms** are mostly anecdotal, apart from one WSJ report on physiotherapist caseloads.

---

## 1. Key takeaways

1. **Runna and our framework share the same skeleton.** Both:
   - anchor all paces to one estimated race time
   - progress weekly volume and the long run on separate limits
   - schedule deload weeks and a taper
   - block races that the long run can't build toward. Runna does this check too, which supports our review fix C1.
2. **Runna is stronger on what happens *during* a plan:**
   - pace recalibration from workout data
   - a "not feeling 100%" state
   - holiday and illness re-entry caps
   - B-races
   - user-facing intensity and volume settings
3. **Our framework is stronger on what happens *before* a plan:**
   - evidence-tagged rules
   - a per-session spike rule (Runna's long-run build is 10–15% per week)
   - FM prediction penalty
   - feasibility check
   - health screening
   - two-axis classification (Runna's levels come from the longest comfortable single run)
4. **The common criticism of Runna** is too much intensity for beginners and easy runs drifting to moderate effort. Our minimum easy share (80–85%) and beginner quality limits address exactly that, so they're worth making visible in the product.
5. **Garmin Run Coach and its Daily Suggested Workouts** use readiness data (sleep, stress, HRV, recovery) to change the day's workout. We have nothing like this yet. It's a v2 feature that needs wearable data.

---

## 2. Runna [primary unless noted]

### 2.1 Inputs and levels
- **Inputs:** ability level, current weekly mileage, current longest run, recent race times, runs per week, plan end date or race date, and Training Preferences (Training Volume and Difficulty) [1][4].
- **Levels** are defined by the distance you can comfortably run in one go, *not* weekly mileage [2]:

| Level | Criterion |
|---|---|
| Beginner | Can run 5 km non-stop in < 60 min |
| Intermediate | Regularly runs ≥ 5 km, no structured plan |
| Advanced | Regularly runs ≥ 10 km, some structured training (intervals) |
| Elite | Regularly runs HM+, experienced with structured training |
| Elite Plus | Consistently 80–100 km/week |

- **What the level controls:** starting weekly mileage, the length of each run, and the long run. Race times affect *paces only, not mileage* [4]. Changing the level rebuilds the plan, and Runna advises not raising it before weeks 2–3 [2].

### 2.2 Paces
- **One fitness anchor.** A single estimated race time sets paces for every distance [1]. Third-party reviews add that updating your 5k estimate changes your other estimates too [secondary].
- **Pace Insights** [3]:
  - compares achieved vs. target pace in **speed sessions only** (intervals, tempo, time trials)
  - checks consistency within and between workouts
  - suggests a change only when it sees a clear trend
  - the user must **accept**; nothing changes automatically
  - it ignores free runs, manual uploads, incomplete workouts and poor GPS
  - if you edit by hand, Runna advises moving the estimated race time **20–30 s at a time**
- **Easy runs** should always feel conversational, whatever the targets say [3].
- **Heart rate:** a 2025 comparison says Runna uses pace only and does not adjust plans from HR [secondary]. Runna does have an "Adapt for Heat" pacing feature [secondary: Wareable headline].

### 2.3 Volume and long run
- **Weekly mileage** follows a rising curve with a **fixed weekly ceiling calculated from current mileage** [1]. This means:
  - very low-mileage runners can still progress
  - high-mileage runners are protected from big jumps
- **More experienced runners get higher targets but not faster build rates** [1].
- **Frequency scaling** [1][5]:
  - non-distance plans use a fixed weekly percentage that is *higher* for fewer run days
  - **6–7 days/week** gets a more conservative build rate
- **The long run has its own build limit**, separate from weekly mileage. It guards against a single over-long session and against a long run building faster than recovery [5]. Marathon long runs [6]:
  - grow **10–15% per week**, with a deload every **4–5 weeks**
  - peak at **32 km once or twice**; experienced runners go longer
  - plans over 14 weeks allow more long runs; plans under 13 weeks have fewer
- **Long-run threshold cut:** if the long run reaches a set distance for your ability, that week is automatically reduced, whatever the cycle position [7].
- **No back-to-back long runs** [7].
- **Shorter plans progress faster** [4].

### 2.4 Recovery
- **Deload weeks** [7][5]:
  - their number scales with plan length
  - **hard sessions are cut more than easy runs**
  - the long-run cut depends on how long the long run has become and on ability, with more rest for longer long runs and less experienced runners
  - foundation plans at 4 days/week drop to 3 runs; above that, one weekly workout is made easier even outside deloads
- **Taper** [7]:
  - **3 weeks** for HM and longer, or any plan of 10 weeks or more
  - **2 weeks** for 10k and shorter on a short plan
  - hard sessions are reduced or removed and the long run drops back, with a minimum session length kept
- **B-races** [7]: recovery scales with how demanding the race is (one easy day up to several rest days), plus a long-run mini-taper the week before.
- **Post-race plans** carry over the race data automatically [1].

### 2.5 Interruptions
- **Not Feeling 100%** [7][5]:
  - pauses mileage *and* pace progression for up to 14 days
  - caps session distances by ability
  - returns in up to three stages to full training with speed work
  - the user picks a fast, balanced or slow return
- **Holiday with no running:** the first week back has a mileage cap [7].
- **Two or more weeks without a long run:** the long run is capped on return [7].

### 2.6 Foundation plans (New to Running, Return to Running, Path to parkrun) [1][5]
- **Starting point:** a questionnaire on time since last run, current exercise frequency and type. Cross-training counts as aerobic base.
- **Progression:** a **double constraint**. Each week's ceiling is `min(current best + fixed increase, current best × multiple)`.
- **Walk-run to continuous:** the share of continuous runs rises in defined stages. Return to Running does this over four quarters of the plan; New to Running is slower. These plans have no pace targets.

### 2.7 Plan types [1]
- Distance and race plans, 5k to 50 km
- Post-race, post-injury and post-natal plans
- New to Running, Return to Running, Path to parkrun
- Run Faster, Run Further, Run to Maintain (with target-mileage settings) and Run/Train Your Way

### 2.8 Training Preferences [4][5]
- **Training Volume** (Gradual / Steady / Progressive) sets how fast mileage builds.
- **Difficulty** sets workout intensity and the number of speed sessions.

### 2.9 Criticisms [secondary]
- **Injury reports:** the WSJ reported physiotherapists seeing multiple Runna-related injuries each week. Runna then added ways to dial intensity down [8].
- **Too much speed work for beginners:** a London physio's comment on Reddit, anecdotal [8].
- **Easy runs too hard:** many users run easy mileage at moderate effort [8].
- **Weak automatic adaptation:** earlier reviews said plans didn't adjust week to week unless the user updated their race time [9]. Pace Insights now addresses this, but still needs the user to accept.
- **Runna's position:** plans are "designed by highly experienced coaches… not created by AI"; a rules engine adapts them [8].

---

## 3. Garmin

| | Garmin Coach | Garmin Run Coach / Daily Suggested Workouts |
|---|---|---|
| Who designs | 3 coaches: Galloway (run/walk), McMillan, Parkerson-Mitchell [10] | Garmin algorithm |
| Goals | 5k, 10k, HM; finish or time goal; run/walk 5k option [10][11] | Race or fitness goal, end date, chosen train/rest days [10] |
| Inputs | Current weekly mileage, goal [11] | VO2max, lactate threshold, training history, **sleep, stress, recovery** (wear the watch overnight) [10] |
| Adapts to | Performance as fitness improves [10] | Performance, recovery and health metrics, **daily** [10] |
| Extras | Coach videos | Optional strength workouts [10] |
| Criticism | Adapts to pace, not recovery; hard sessions kept on low-readiness days [secondary, competitor's claim + forum reports] | Suggestion generated at midnight, before that night's sleep data [secondary, forum] |

## 4. TrainAsONE [secondary]
- **Inputs:** running history, availability and race date/distance.
- **Re-plans after every run**, planned or not, and adjusts for missed or off-plan workouts and the weather forecast [12].
- **Safety:** claims to "minimise the risk of injuries". No independent validation found, and some users report regressing [12].

## 5. VDOT O2 (Jack Daniels) [secondary]
- **Paces:** VDOT assessment and Daniels training paces pushed to the watch; syncs with Garmin, COROS, Strava and Apple Health [13].
- **Not automatically adaptive.** The user tells it when they're ready to level up [13].
- Mostly used by coaches managing many athletes.

---

## 6. Feature comparison

● = has it, ◐ = partial, ○ = no / not documented

| Capability | Runna | Garmin Coach | Garmin Run Coach | TrainAsONE | VDOT O2 | **Ours v0.2** |
|---|---|---|---|---|---|---|
| Paces from one fitness anchor | ● | ● | ● (VO2max) | ● | ● | ● (VDOT, distance-weighted) |
| FM prediction penalty for low volume | ○ | ○ | ○ | ? | ○ | **●** |
| Goal feasibility check | ○ | ○ | ○ | ? | ○ | **●** |
| Race-reachability check | ● | ○ | ? | ? | ○ | ● |
| Levels / classification | ◐ single-run distance | ◐ mileage | ◐ metrics | ? | ◐ VDOT | **● two-axis** |
| Separate long-run limit | ● 10–15%/wk | ? | ? | ? | ○ | **● ≤ 110% of 30-day max (evidence-based)** |
| Weekly cap scaled to current mileage | ● | ? | ? | ? | ○ | ◐ % only |
| Frequency-scaled ramp | ● | ○ | ? | ? | ○ | ○ |
| Deload: hard cut more than easy | ● | ? | ? | ? | ○ | ◐ |
| Taper | ● 2–3 wk | ● | ● | ● | ● | ● 1–3 wk by distance |
| Pace recalibration from workouts | ● Pace Insights | ● | ● | ● | ○ manual | ◐ races and TTs only |
| Not-feeling-well / illness state | ● | ○ | ● (readiness) | ◐ | ○ | ◐ check-in rules |
| Holiday / missed-long-run re-entry caps | ● | ? | ? | ● | ○ | ◐ via actuals |
| B-races (mini-taper and recovery) | ● | ○ | ? | ? | ○ | ○ |
| Readiness (HRV / sleep) | ○ | ○ | ● | ? | ○ | ○ |
| Re-plan after every run | ○ | ○ | ● daily | ● | ○ | ○ weekly |
| User intensity/volume settings | ● | ○ | ○ | ◐ | ○ | ○ |
| Walk-run foundation plans | ● | ● Galloway | ? | ? | ○ | ● ladder |
| Health / RED-S screening | ○ | ○ | ○ | ? | ○ | **●** |
| Minimum easy-share rule | ? | ? | ? | ? | ◐ | **● 80–85%** |
| Evidence-tagged rules | ○ | ○ | ○ | ○ | ◐ Daniels | **●** |
| Strength sessions | ? | ○ | ● | ? | ○ | ◐ optional slot |

---

## 7. Proposed changes to our framework (not yet applied)

**Adopt in v1** (cheap, safety- or usability-positive):

| # | Change | From | Where |
|---|---|---|---|
| B1 | **Pace recalibration from workouts.** Compare achieved vs. target pace in T/I/TT sessions. If ≥ 3 eligible sessions in a row are ≥ 2% fast (or slow) with consistent reps, *suggest* ±0.5 VDOT. User accepts. The existing +1 VDOT per 3 weeks cap still applies. | Runna Pace Insights | §4.4, §10 |
| B2 | **Weekly increase with a floor:** `max_increase = max(RAMP_RATE × vol, MIN_WEEKLY_INCREASE_KM)`. Low-volume runners get e.g. +2 km rather than +0.6 km, while the session spike rule still protects them. | Runna | §6.2 |
| B3 | **Frequency-scaled ramp:** slightly higher % at 2–3 days, lower at 6–7 days. | Runna | §6.2 |
| B4 | **Deload shape:** cut quality volume 35–40% and easy volume ~15%; cut the long run more when it is long relative to tier; beginners at 4+ days drop one run. | Runna | §6.2, §6.5 |
| B5 | **"Not feeling 100%" state:** pause volume and pace progression for up to 14 days, cap run length, and return in 3 stages (easy only → easy + strides → full) at a fast, balanced or slow rate. | Runna | §10 |
| B6 | **Re-entry caps:** after a week with no running, cap the first week back at ~70% of plan; after ≥ 2 weeks without a long run, cap the long run at ~75% of the last one. This adds explicit rules on top of the spike rule. | Runna | §10 |
| B7 | **Foundation double constraint:** each run-walk step ≤ `min(best + fixed minutes, best × multiple)`, with cross-training counted toward the starting point. | Runna | §7.6, §7.7 |
| B8 | **User settings within safety bounds:** a Volume setting (gradual / steady / progressive → ramp × 0.7 / 1.0 / 1.2, still under the hard ceilings) and a Difficulty setting (number of quality sessions −1 / 0 / +0, never above the tier table). | Runna | §2.3, §6 |

**Adopt in v1.1:**
- **B9 B-races:** a long-run mini-taper the week before; 1–3 easy or rest days after, scaled by race distance.
- **B10 Heat adjustment:** a pace slowdown formula rather than effort guidance alone.

**Later (v2, needs wearable data):**
- **B11 Readiness-based daily adjustment** (HRV, sleep, stress), as in Garmin Run Coach and Daily Suggested Workouts.
- **B12 Re-plan after every logged run**, as in TrainAsONE.

**Deliberately not adopted:**
- **Runna's 10–15% weekly long-run increase.** We keep the per-session ≤ 110%-of-30-day-max rule. It's tighter and backed by the 2025 cohort study (Frandsen).
- **Runna's level definitions** (single comfortable run distance). We keep the two-axis classification, which also uses weekly volume and training age.
- **Runna's 3-week taper for HM and plans of 10+ weeks.** We keep ~2 weeks for HM, per the Bosquet 2007 meta-analysis. Runna's choice is defensible for less-trained runners, so this could become a setting.
- **Same build rate for all levels.** Runna gives experienced runners higher targets, not faster rates. Our rates differ slightly by tier (6/9/10%). Neither choice is evidence-based; this is open question Q9.

---

## 8. Open-source projects

Searched GitHub (repository search) and the web on 2026-11-26. The field is **small and young**: no project has more than ~10 stars, and most were created in 2025–26. The relevant ones were shallow-cloned and read; none of their code was run.

| Project | What it is | Licence | Approach vs. ours |
|---|---|---|---|
| [adrienpoly/strava-running-coach](https://github.com/adrienpoly/strava-running-coach) | Claude skill plus a tested Python script (`runcoach.py`: digest, paces, check, activity). Reads Strava, builds, checks and adapts plans | **MIT** | **Closest in philosophy.** Same evidence choices: Frandsen 2025 per-run spike rule, rejects ACWR, paces from current fitness rather than goal, a goal verdict, labels conventions as conventions. Goes further on *data*: classifies runs from Strava, checks easy runs by heart rate, run-level analysis (splits, HR drift, reps vs. target), layoff discount. Plan design is left to the LLM and then linted; ours is a deterministic generator. |
| [GeoffreyDjof/running-plan-engine](https://github.com/GeoffreyDjof/running-plan-engine) | Deterministic Python engine (Pydantic I/O, French output), VDOT paces, safety validator, typed refusals (`VOLUME_TOO_LOW_FOR_GOAL`, `GOAL_TOO_SOON`, `INJURY_BLOCKS_QUALITY`) | **none** (all rights reserved) | **Closest in architecture.** Named constants, validator and refusal codes, like ours. Differences: fixed templates per level × distance × days instead of computed weeks; 10% weekly cap and 75–80% easy share; long-run share 35/38/40% by tier; injury caps long run at 30% and blocks quality. No spike rule, FM penalty or screening. |
| [neilasiii/Stridion](https://github.com/neilasiii/Stridion) | Self-hosted AI running coach using Claude Code as the reasoning engine; VDOT-based | none | An LLM-first coach, not a rules engine. |
| [AustinOrphan/training-plan-generator](https://github.com/AustinOrphan/training-plan-generator) | TypeScript library: VDOT, critical speed, periodization, 80/20, **ACWR** | none | Broad but unfinished ("advanced features coming soon"). Relies on ACWR, which our research rejects. |
| [hoovercj/time-to-run](https://github.com/hoovercj/time-to-run) | Web app: pick a published plan (Pfitzinger, Hansons, Higdon), set the race date, export to a calendar | MIT (code) | Static plans, no personalisation. Its plan content comes from copyrighted books. |
| [johanneskasser/zenit-it.fit](https://github.com/johanneskasser/zenit-it.fit) | Training-plan *editor* for runners (Supabase) | MIT | Editing and management UI, not generation. |
| [PatrickWiloak/proper-distance-running-training-guidance](https://github.com/PatrickWiloak/proper-distance-running-training-guidance) | Evidence-based written guide: principles, workouts, HR/VDOT zones | CC BY 4.0 | Documentation, not code. A useful cross-check for our research doc. |

**Takeaways**
1. **No mature open-source equivalent exists.** Nothing combines deterministic generation, evidence tagging, feasibility and reachability checks, screening and an independent validator. That supports building our own.
2. **Reuse is mostly ideas, not code.** Two of the three closest projects have no licence, so their code can't legally be reused. strava-running-coach is MIT, so its Strava digest and run-analysis logic could be adapted with attribution.
3. **Ideas worth taking:**
   - **From strava-running-coach:**
     - baseline volume computed three ways from logged runs
     - run classification from Strava
     - easy-run check by heart rate
     - per-run feedback (splits, HR drift, reps vs. target)
     - an A goal, B goal and checkpoint in the goal verdict
   - **From running-plan-engine:**
     - typed refusal codes with exit codes in the CLI
     - an as-of date so the same input always gives the same plan
     - a VDOT self-check against a reference anchor (5k 20:00 → VDOT ≈ 51 ± 0.5)
4. Both close projects arrived independently at the same core rules we did (spike rule or 10% cap, ≥ 75–80% easy, named constants, validator). That's a reasonable sign the design is sound, not proof.

---

## 9. Sources

Primary (read in full):
1. Runna – How does Runna build your training plan around your current fitness? https://support.runna.com/en/articles/15231838-how-does-runna-build-your-training-plan-around-your-current-fitness
2. Runna – Adjusting your running ability. https://support.runna.com/en/articles/6205993-how-to-adjust-your-running-ability
3. Runna – What are Pace Insight recommendations and how do they work? https://support.runna.com/en/articles/10854865-what-are-pace-insights-and-how-do-pace-recommendations-work
4. Runna – How Runna calculates your mileage, and how to adjust it. https://support.runna.com/en/articles/14666572-how-runna-calculates-your-mileage-and-how-to-adjust-it
5. Runna – How does Runna reduce the risk of injury and overtraining? https://support.runna.com/en/articles/15279082-how-does-runna-reduce-the-risk-of-injury-and-overtraining
6. Runna – How is my long run distance calculated in my marathon plan? https://support.runna.com/en/articles/9144831-how-is-my-long-run-distance-calculated-in-my-marathon-plan
7. Runna – How does Runna build recovery into your training plan? https://support.runna.com/en/articles/15272605-how-does-runna-build-recovery-into-your-training-plan
10. Garmin – How to use Garmin Coach training plans for runners. https://www.garmin.com/en-MY/blog/running/how-to-use-garmin-coach-training-plans-for-runners/

Secondary (search summaries; pages blocked automated access):

8. Criticism and Runna's response:
   - the5krunner, "Runna: Is your AI marathon training plan injuring you?": https://the5krunner.com/2026/02/21/runna-ai-marathon-training-injury/
   - TechRadar: https://www.techradar.com/health-fitness/are-ai-training-apps-like-runna-putting-you-at-risk-of-injury-i-asked-a-real-life-running-coach
   - bioethics.com summary: https://bioethics.com/archives/101474
9. Reviews of Runna:
   - The Runner Beans: https://therunnerbeans.com/runna-coaching-app-review/
   - Running Westward Ho: https://www.runningwestwardho.co.uk/post/the-problem-with-runna
11. Garmin – Which adaptive training plan is right for you? https://www.garmin.com/en-GB/blog/which-adaptive-training-plan-is-right-for-you/
    - Competitor critique: gneta.app: https://www.gneta.app/blog/garmin-coach-review
12. TrainAsONE:
    - App Store: https://apps.apple.com/app/id1541355896
    - Google Play: https://play.google.com/store/apps/details?id=com.trainasone
13. VDOT O2:
    - App Store: https://apps.apple.com/app/id977666802
    - Runcoach vs VDOT O2: https://www.sundried.com/blogs/wearables-and-tech/runcoach-vs-vdot-o2-which-platform-is-best-for-coaches
    - Running Coach vs Runna (for the HR claim): https://blog.runningcoach.me/en/2025/09/15/running-coach-vs-runna-which-training-plan-is-right-for-you/
