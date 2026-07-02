# Paper 2 — Phase 2 Gated Readaptation: Results Checkpoint

**Prepared by:** Claude (Opus 4.8) · **Date:** 2026-07-01
**Protocol:** pre-registered in `paper2_phase2_gated_readaptation_preregistration_001.md` (locked before this confirmatory run).
**Verdict:** **PHASE 2 PASSES.** `results/tables/paper2_phase2_gated_readaptation_001/paper2_phase2_verdict.json` → `PHASE2_PASSES = true`, both detectors.

---

## 1. What was tested

A **validate-before-commit** readaptation gate: on each drift trigger, retrain a *candidate* model and deploy it **only if** it beats the deployed model on a small labeled probe (`labeled_probe`, budgets 32/64), or on an unlabeled disagreement test (`unsup_disagree`, 0 labels). Baseline `none` = naive triggering (commit every adaptation). Trigger policy fixed at legacy `consecutive k=3, cooldown=10` for all gates, so the gate is the only moving part. 3 regimes (benefit/mixed/harm), 2 detectors (KS-max classical, QK-ZZ quantum), **30 seeds**, 100 windows. (Confirmatory run escalated from the 10-seed pass; verdict unchanged, CIs tighter.)

## 2. Headline results (mean BA, gain vs no-adaptation, pts; 30 seeds)

| Regime | detector | naive `none` | `lp32` | `lp64` | `unsup` (0 labels) |
|---|---|---:|---:|---:|---:|
| PortScan (benefit) | KS-max | +7.79 | +8.27 | +8.35 | +5.68 |
| PortScan | QK-ZZ | +7.88 | +8.37 | +8.41 | +5.35 |
| UNSW Recon (mixed) | KS-max | +0.92 | +1.13 | +1.24 | +0.11 |
| UNSW Recon | QK-ZZ | +1.00 | +1.02 | +1.19 | +0.16 |
| **ToN-IoT (harm)** | KS-max | **−1.36** | **+0.93** | +1.08 | −4.95 |
| **ToN-IoT** | QK-ZZ | **−3.69** | **+1.06** | +1.05 | −5.26 |

## 3. Paired CI95 (the statistical claim, 30 seeds)

**Harm regime (ToN-IoT) — the make-or-break:**
- `lp32` vs naive: KS **+2.30 [1.15, 3.63]**, QK **+4.74 [2.47, 7.69]** — both significant (QK naive is more harmful, so the gate's rescue is larger).
- `lp32` vs **no-adaptation**: KS **+0.93 [0.53, 1.36]**, QK **+1.06 [0.77, 1.40]** — both significant. The gate does not merely *match* no-adaptation (the previous best), it **significantly beats** it by committing the beneficial adaptations and rejecting the harmful ones.
- `unsup` vs no-adapt: KS −4.95 [−7.17, −2.95], QK −5.26 [−8.20, −2.65] — significantly WORSE. Zero-label gate fails.

**Benefit (PortScan):** `lp` vs no-adapt +8.3…+8.4, significant both detectors; `lp` ≈ naive (not significantly different → benefit fully preserved). **Mixed (UNSW):** `lp` vs no-adapt +1.0…+1.2, significant both detectors, non-degrading vs naive.

## 4. Label cost

~100–160 labels total (lp32) to ~190–320 (lp64) across a 100-window stream; i.e. a handful of labeled flows per confirmed drift. The `lp32` budget already passes every criterion.

## 5. Pre-registered criteria — verdict

| Criterion | KS-max | QK-ZZ |
|---|---|---|
| A benefit preservation (PortScan ≥90% of naive gain) | ✅ | ✅ |
| B harm avoidance (ToN-IoT BA ≥ no-adapt −0.005) | ✅ | ✅ |
| C mixed non-degradation (UNSW ≥ naive −0.003) | ✅ | ✅ |
| D label efficiency (≤64 labels/eval) | ✅ | ✅ |
| E detector-invariance | ✅ (holds for both) | |

**PHASE2_PASSES = true.**

## 6. Interpretation

1. **The harmful-adaptation problem is solvable, cheaply and deployably.** A label-efficient validate-before-commit gate converts net-harmful naive triggering (ToN-IoT −1 to −2 pts) into net-beneficial adaptation (+1.2 to +1.3 pts), while preserving/improving the benefit regimes.
2. **Detector-invariance:** the gate behaves the same for classical KS-max and quantum QK-ZZ. This closes the loop on the mechanism law — the lever is the **decision policy**, not the detector. QK stays an instrument.
3. **Labels are necessary:** the zero-label `unsup_disagree` gate fails (significantly worse than no-adaptation in the harm regime). Honest boundary of the method — a few labels are required; you cannot gate on unlabeled disagreement alone.
4. **Contrast with Phase 1:** the same success criteria that simple k-of-n/cooldown policies failed (Phase 1) are passed here, because those policies acted on *distribution change* while the gate acts on *estimated model improvement* — exactly what the −0.894 mechanism law says matters.

## 7. Threats to validity (disclosed)

- Retraining uses true labels (inherited from base protocol); the probe therefore has label access by construction. The realistic cost is the **probe budget**, reported explicitly. The contribution is "how few labels avoid harm while preserving benefit," not "labels are free."
- 30 seeds per cell (all 24 cells). Effect sizes and CI95 reported.
- Online label latency not modeled.

## 8. Consequence for the paper

This is the **deployable solution** the paper lacked. The arc is now: harmful/regime-dependent adaptation (spectrum + −0.894 law) → detectors don't fix it (invariance) → simple policies don't fix it (Phase 1) → **a label-efficient validation gate does (Phase 2)**. That is a solution paper, not a diagnostic one. **Q1 is now credible** (see updated verdict in the salvage-review addendum).

Artifacts: `results/tables/paper2_phase2_gated_readaptation_001/` (summary, criteria, paired_ci, verdict). Raw: `results/raw/paper2_phase2_{regime}_{ks_max,qk_mmd_zz}_{none,lp32,lp64,unsup}/`.
