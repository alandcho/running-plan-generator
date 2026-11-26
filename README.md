# Running Plan Generator

Generates personalized running plans from a runner's current capability, goal and constraints.

## Status

Research phase.

- [`research/running-plan-framework.md`](research/running-plan-framework.md) covers the evidence review, runner classification, pace model, periodization, safety rules, the end-to-end algorithm and a worked example.
- [`research/long-run-duration.md`](research/long-run-duration.md) reviews how long the long run should be for each race distance.
- [`research/benchmark-commercial-tools.md`](research/benchmark-commercial-tools.md) compares Runna, Garmin, TrainAsONE and VDOT O2 with this framework.
- [`running_plan/`](running_plan/) is the generator, in progress. All tunable numbers are named in [`config.py`](running_plan/config.py). Pace calculator: `python3 -m running_plan.vdot 10000 50:00`.
