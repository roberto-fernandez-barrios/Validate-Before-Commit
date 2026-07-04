# Paper 2 — Phase 2b: label-budget curve + benefit breadth (post-registration robustness)

**Date:** 2026-07-04 · **Status:** exploratory robustness, explicitly NOT part of the pre-registered Phase 2 claim.
Artifacts: `results/tables/paper2_phase2b_budget_curve_001/`, `results/figures/paper2/fig5_label_budget_curve.*`.
Regenerate: `python -m src.analysis.make_paper2_budget_curve`.

## Motivation
Address the two most likely Q1 reviewer objections to Phase 2: (1) "how few labels really?" — the title says
label-efficient but Phase 2 only tested budgets 32/64; (2) "only one benefit regime" (PortScan). Both are
robustness extensions on existing infrastructure (KS-max, 30 seeds), not new confirmatory claims.

## 1. Label-efficiency frontier (KS-max, 30 seeds, gain vs no-adaptation)

| budget (labels/stream) | PortScan (benefit) | UNSW Recon (mixed) | ToN-IoT (harm) |
|---|---:|---:|---:|
| naive (0) | +7.79 | +0.92 | **−1.36** |
| 8 (≈23) | +8.24 | +1.02 | **+0.38** |
| 16 (≈50) | +8.19 | +1.26 | +0.74 |
| 24 (≈76) | +8.18 | +1.01 | +0.77 |
| 32 (≈108) | +8.27 | +1.13 | +0.93 |
| 48 (≈146) | +8.38 | +1.11 | +0.99 |
| 64 (≈211) | +8.35 | +1.24 | +1.08 |
| 96 (≈358) | +8.32 | +1.29 | +1.06 |
| 128 (≈452) | +8.42 | +1.23 | +1.13 |

**Takeaway:** even the smallest budget (~8 labels/drift, ≈23/stream) already flips ToN-IoT from harmful
(−1.36) to beneficial (+0.38); the curve plateaus near +1.1 by budget 32–64. Benefit regime is flat and
preserved at every budget. A few dozen labels, not hundreds, suffice → strengthens the "label-efficient"
claim. (Fig 5.)

## 2. Benefit-regime breadth (KS-max, 30 seeds)

| Regime | no-adapt BA | naive gain | gate lp32 | gate lp64 |
|---|---:|---:|---:|---:|
| PortScan | 86.1 | +7.79 | +8.27 | +8.35 |
| Wednesday | 72.8 | +15.39 | +16.20 | +16.32 |
| DDoS | 64.7 | +24.81 | +24.99 | +25.27 |

**Takeaway:** across three benefit regimes (including the two strongest, Wednesday and DDoS), the gate
preserves and slightly improves the benefit of adaptation — it never sacrifices benefit where adaptation
helps. Kills the "only one benefit regime" objection.

## Manuscript integration
Added as §5.6 (post-registration robustness) with Fig 5; abstract updated ("a few dozen suffice"). The
pre-registered Phase 2 result (budgets 32/64, both detectors, 30 seeds) remains the primary confirmatory
claim; Phase 2b is clearly labeled robustness.
