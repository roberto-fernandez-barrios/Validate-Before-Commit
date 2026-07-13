# Harness v2 — Registered replication protocol (LOCKED BEFORE the confirmatory run)

**Date:** 2026-07-14 · **Status:** REGISTERED. This document, and the v2 harness it describes,
are committed and pushed to the public repository and tagged (`harness-v2-protocol`) BEFORE any
confirmatory v2 seed is run. The git tag's public timestamp is the registration timestamp.
Smoke evidence so far: seeds 101–103, ToN only, used exclusively to verify the harness runs and
that the common-stream property holds (no-adaptation rows bit-identical across arms); no other
v2 results exist at registration time.

## What v2 fixes (the three harness criticisms of the external review)
1. **Common streams**: the evaluation stream and calibration draws are pre-generated from an
   environment RNG seeded by the seed only; every arm processes exactly the same windows.
   Verified: no-adaptation rows and pre-trigger detector scores are bit-identical across arms.
2. **Role-disjoint partitions**: per seed, each class pool is split 50/30/20 into
   window/train/probe partitions; stream windows, training data and probes cannot overlap.
3. **Separate RNGs**: environment (seed), initial training (seed+777), detector calibration
   (seed+888), candidate training (seed·100003+t), probe (seed·200003+t), recalibration
   (seed·1000+999+t). No generator is ever advanced by policy actions.

Plus per-trigger logging (pre-trigger degradation over the last 5 windows, detector score, and
incumbent-vs-candidate BA on the next 5 future windows — lookahead used for logging only).

## Confirmatory design (fixed)
- **Seeds: 101–130** (30 fresh seeds; 1–30 were used by the v1 study and never overlap).
- Regimes: CICIDS PortScan (benefit), UNSW Reconnaissance (marginal), ToN-IoT Scanning (harm).
- Downstream: SVC-RBF. Settings: window 128, dim 8, post 100, ramp 80, calibration 30,
  trigger 3-consecutive + cooldown 10, adapt 512/class, initial 2000/class (identical to v1).
- Arms:
  - KS-max × {none, labeled_probe b=32, labeled_probe_holdout b=32, labeled_probe_lcb b=64
    (alpha=0.10), unsup_disagree tau=0.15} — 15 runs;
  - QK-ZZ × {none, labeled_probe b=32} — 6 runs (detector invariance).
- 21 runs total; gains computed against the shared-stream no-adaptation baseline; contrasts are
  now TRULY paired (identical streams). Paired bootstrap CI95 over seeds, 5000 resamples.

## Confirmatory criteria (fixed; evaluated on labeled_probe b=32)
- **B (harm avoidance, decisive):** ToN-IoT gate gain vs no-adaptation ≥ −0.5 AND gate
  significantly above naive (paired CI95 > 0), for KS-max.
- **A (benefit preservation):** PortScan gate gain ≥ naive gain − 0.3, for KS-max.
- **C (marginal non-degradation):** UNSW gate gain ≥ naive gain − 0.3, for KS-max.
- **I (detector invariance):** B and A hold with the same signs for QK-ZZ.
- The v1 study is reported as the initial (exploratory) study; v2 is the confirmatory
  replication. If any criterion fails, the manuscript reports the failure as the primary result
  of the replication — no re-runs, no seed additions, no criterion changes.

## Pre-declared exploratory analyses (reported as exploratory)
- **Holdout gate**: if |holdout − labeled_probe| ≤ 0.3 in every regime, the gate's incremental
  label cost is zero (the probe can be carved from the retraining batch).
- **LCB gate**: operating point (commits, safety, benefit) vs the plain probe.
- **Per-trigger mechanism**: from the trigger logs, correlate delta_future5 (candidate −
  incumbent BA on the next 5 windows) with (a) deg_pre5 (incumbent BA over the previous 5
  windows) and (b) the detector score at the trigger, within regime and pooled; the paper's
  account predicts (a) strongly negative, (b) weak/inconsistent. This is the reviewer's
  requested non-coupled, per-decision test: predictor and outcome share no algebraic term.

## Stopping rule
One pass of the 21 runs at seeds 101–130. No additional seeds, arms, regimes or criteria after
this tag. Aggregation: `src/analysis/aggregate_paper2_v2_replication.py` (to be written against
this spec; its criteria constants must match this document).
