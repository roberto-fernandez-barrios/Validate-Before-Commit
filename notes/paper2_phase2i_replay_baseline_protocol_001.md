# Phase 2i — Replay retraining baseline vs the gate: protocol

**Date:** 2026-07-13 · **Status:** post-registration robustness; criteria fixed BEFORE analysis.
**Motivation:** external review point 9 — the harmful "naive" loop retrains on a narrow current
window and fully replaces the incumbent; reasonable adaptive systems use replay. If a simple
replay policy eliminates the harm without labels, the headline must be qualified to
"full-replacement retraining"; if it does not, the gate's necessity is strengthened. Either
answer improves the paper; we run it rather than argue it.

## Strategy under test
- **`replay`**: on each trigger the candidate trains on the union of the standard current-severity
  sample (512 flows/class at sev(t), unchanged) **plus an equal-size replay sample from the
  reference regime** (512/class at severity 0.0) — the standard retrain-current-plus-replay
  baseline at a 50/50 replay ratio. Full model replacement on commit, as before. Everything
  else (trigger, detector, windows, severity ramp) is unchanged.
- Implemented as `--adapt-strategy {full_replace,replay}` (+ `--replay-size-per-class`,
  default = adapt-size-per-class). `full_replace` reproduces the existing behaviour exactly.

## Design (fixed)
- Regimes: PortScan (benefit), UNSW Reconnaissance (marginal), ToN-IoT Scanning (harm).
- Detector: KS-max only (pre-specified; detector-invariance already established).
- Downstream: SVC-RBF (the fragile/harm case — where the reviewer's objection bites).
- Arms: replay×`none` (label-free replay-naive) and replay×`labeled_probe` b=32 (gate on top).
- 30 seeds, 100 windows, ramp 80, calibration 30, window 128, dim 8, legacy trigger
  (3-consecutive, cooldown 10) — identical to the Phase-2 pre-registered settings.
- 6 runs total. Smoke (3 seeds, ToN) before the batch.
- Comparisons: gains vs the *within-run* no-adaptation baseline; paired-by-seed CIs across the
  2i run dirs (replay-none vs replay-lp32), and against the published full-replacement Phase-2
  numbers (same settings) for context.

## Pre-fixed criteria (evaluated on replay×none, SVC, KS-max)
- **R1 (harm avoidance without labels):** ToN-IoT gain vs no-adaptation ≥ −0.5 pts.
- **R2 (benefit preservation):** PortScan gain ≥ full-replacement naive gain (+7.79) − 0.3 pts.
- **R3 (marginal non-degradation):** UNSW gain ≥ full-replacement naive gain (+0.94?) − 0.3 pts
  (use the Phase-2 table value for naive at analysis time).
- **G (gate orthogonality):** replay×lp32 is never significantly worse than replay×none or
  no-adaptation in any regime (paired CI).

## Interpretation rules (fixed before results)
- **R1 ∧ R2 pass:** replay alone is a label-free fix in these regimes → qualify the headline to
  full-replacement retraining wherever it appears; present replay as a complementary mitigation
  and the gate as the strategy-agnostic safety layer (it still adds a guarantee replay lacks:
  validation against the incumbent). Report prominently, not buried.
- **R1 fails:** harm is not an artifact of full replacement → the strawman objection is closed
  with data; the gate remains necessary. Report the replay numbers in §5.6.
- **R1 passes but R2 fails:** replay is another dominated point (safe but benefit-lossy, like
  ATC/DoC) → the labeled probe remains the only Pareto point; strengthen that claim.
- **G fails anywhere:** report as a genuine limitation of the gate under replay retraining.
