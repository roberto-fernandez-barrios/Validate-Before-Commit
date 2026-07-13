# Harness-v2 registered replication — checkpoint: EVERY criterion replicates

**Date:** 2026-07-14 · Protocol: `paper2_harness_v2_registered_replication_protocol_001.md`,
publicly tagged `harness-v2-protocol` (commit b9ec2fb) BEFORE any confirmatory seed ran.
Runs: 21 (3 regimes × [KS-max × 5 gates + QK-ZZ × 2] × 30 fresh seeds 101–130), truly paired
(bit-identical streams per seed across arms; role-disjoint window/train/probe partitions).
Artifacts: `results/tables/paper2_v2_replication_001/{summary,paired_ci,verdict,mechanism}.csv`.

## Verdict (locked criteria): A ✅ B ✅ C ✅ I ✅ + both pre-declared exploratories

| arm (KS-max) | ToN (harm) | PortScan (benefit) | UNSW (marginal) |
|---|---|---|---|
| naive | **−1.41 [−2.44, −0.47]** | +7.94 | +1.22 |
| labeled probe b=32 | **+0.95 [0.62, 1.32]** (vs naive +2.36 [1.40, 3.39]) | +8.79 | +1.31 |
| **holdout b=32 (0 incremental labels)** | +0.97 | +8.69 | +1.31 |
| LCB b=64 (α=0.10) | +0.49 | +8.25 | +1.20 |
| unsup τ=0.15 | −3.10 | +6.15 | +0.13 |
| QK-ZZ naive → gated | −1.58 → +0.91 | +7.49 → +9.03 | +1.24 → +1.29 |

1. **The phenomenon and the solution replicate on a hardened harness with fresh seeds** —
   harm, gate rescue, benefit preservation, detector invariance. The initial-study caveats
   (stream realizations, pool overlap) are now confined to the initial study.
2. **The gate's incremental label cost is ZERO**: carving the probe from the retraining batch
   (holdout) is indistinguishable from a fresh probe everywhere (|Δ| ≤ 0.1). This also answers
   the reviewer's "why not a holdout from the batch?" baseline — implemented; it IS the gate.
3. **LCB rule**: safe, more conservative, benefit-lossier in the harm regime — an operating
   point, reported.
4. **Per-trigger mechanism (non-coupled test, prediction registered in the protocol):** across
   252 triggers, pre-trigger degradation (incumbent BA, 5 preceding windows) predicts the
   future value of committing (candidate−incumbent BA, 5 following windows) at
   **r = −0.696 / −0.660 / −0.645** per regime (−0.555 pooled), while the detector score at
   the same triggers predicts **r = −0.001 / −0.081 / −0.026** (−0.004 pooled). Disjoint
   past/future windows; no shared algebraic term. The degradation–headroom account is
   established per decision.

## Manuscript
New §5.9 (both tex + md), results-overview updated, Limitations harness caveats now scoped to
the initial study. Audit 133/133; 24 pp (CAS) / 18 pp (IEEE).

## Remaining (author-side / optional)
- Releases v1.2.0/v1.3.0 (user cuts them; Zenodo captures 2i/2j/2k + v2).
- Title decision ("Safe" → reviewer suggests dropping; text now defines it operationally).
- Optional Phase 3 extras not required by any criterion: DDM/performance-aware trigger baseline
  at matched label budget, natural-prevalence full streams with FPR/alert-volume metrics,
  ensemble/weighted-history update strategies under the gate.
