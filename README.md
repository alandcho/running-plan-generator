# Running Plan Generator

Generates personalized running plans from a runner's current capability, goal and constraints.

## Status

Research phase.

- [`research/running-plan-framework.md`](research/running-plan-framework.md) covers the evidence review, runner classification, pace model, periodization, safety rules, the end-to-end algorithm and a worked example.
- [`research/vdot.py`](research/vdot.py) is a reference Daniels–Gilbert VDOT and training-pace calculator. Example: `python3 research/vdot.py 10000 50:00`.
