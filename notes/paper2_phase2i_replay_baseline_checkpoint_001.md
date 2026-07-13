# Phase 2i checkpoint — replay does not rescue naive triggering; the gate composes with it

**Date:** 2026-07-13 · Protocol: `paper2_phase2i_replay_baseline_protocol_001.md` (criteria pre-fixed).
Artifacts: `results/tables/paper2_phase2i_replay_baseline_001/{summary,paired_ci,verdict}.csv`.
Runs: 6 (3 regimes × replay × {none, lp32} × KS-max × SVC-RBF × 30 seeds; Phase-2 settings).
Note: PortScan runs completed in the original sequential batch; the remaining 4 were re-launched
in parallel after finding the box saturated by another project (identical seeds/settings).

## Verdict (pre-fixed criteria): R1/R2/R3 FAIL, G PASSES everywhere — the strongest outcome

| criterion | value | pass |
|---|---|---|
| R1 harm avoidance (ToN replay-naive ≥ −0.5) | **−4.54** [−7.06, −2.34] | ❌ |
| R2 benefit (PortScan replay-naive ≥ 7.79 − 0.3) | +6.59 | ❌ |
| R3 marginal (UNSW replay-naive ≥ 0.92 − 0.3) | +0.16 | ❌ |
| G gate orthogonality (6 contrasts, ci_hi ≥ 0) | all | ✅ |

Key numbers (gain vs within-run no-adaptation, BA pts):
- **Harm regime (ToN):** replay-naive **−4.54** — significantly harmful, and *worse* than
  full-replacement naive (−1.36): under a still-advancing severity ramp, a candidate anchored
  50% to the stale reference misfits later windows even more. Gate-on-replay: **+0.59**,
  significantly above no-adaptation [0.23, 0.97] and above replay-naive (+5.13 [2.96, 7.60]).
- **Benefit regime (PortScan):** replay-naive +6.59 loses part of the full-replacement gain
  (+7.79). Gate-on-replay **+8.26** — the gate *recovers* the benefit replay loses
  (+1.66 [0.52, 3.04] vs replay-naive).
- **Marginal (UNSW):** +0.16 naive-replay / +0.28 gated; no significant differences.

## Interpretation (per the pre-fixed rules: "R1 fails" branch)

1. **The strawman objection is closed with data**: harmful adaptation is NOT an artifact of
   full-replacement retraining — the standard label-free mitigation (retrain-current-plus-replay,
   50/50) is *more* harmful in the harm regime and benefit-lossy elsewhere.
2. Replay is another **dominated point** on the benefit–safety front (worse than ATC/DoC, which
   at least avoided harm). The labeled probe remains the only gate on the Pareto front.
3. **The gate composes with the update strategy**: placed on top of replay it restores safety
   AND recovers the lost benefit — evidence that validate-before-commit is orthogonal to how
   the candidate is trained.

## Manuscript changes applied
§5.6: extensions count 7→8, new *Replay retraining* item with the numbers above; abstract and
contribution (4) now name replay among the failed alternatives; Limitations updated (replay
tested and rejected; richer update strategies — ensembles, incremental/weighted training,
dynamic windows — remain future work). Audit extended to 102 checks.
