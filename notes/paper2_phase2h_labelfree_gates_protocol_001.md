# Phase 2h — Label-free gates (ATC / DoC) vs the labeled probe: protocol

**Date:** 2026-07-12 · **Status:** post-registration robustness; criteria fixed BEFORE analysis.
**Motivation:** external literature review flagged that the "labels are necessary" claim rests on defeating
only a naive zero-label baseline (raw disagreement, τ=0.15), while the label-free accuracy-estimation
literature (ATC, Garg et al. ICLR'22; DoC, Guillory et al. ICCV'21; Agreement-on-the-Line; Dis²) estimates
exactly sign(acc(h′)−acc(h)) without target labels. We therefore instantiate the two standard estimators as
gates in our own harness and test them head-to-head.

## Gates
- **`atc`** (Average Thresholded Confidence, ATC-MC): per model, learn threshold t on a *labeled
  in-distribution validation sample drawn at that model's training time* such that the fraction of val
  confidences above t equals val accuracy; estimate target accuracy as the fraction of target-window
  confidences above t. Commit iff est(h′) ≥ est(h).
- **`doc`** (Difference of Confidences): est_target(m) = acc_val(m) − (mean_conf_val(m) − mean_conf_target(m)).
  Commit iff est(h′) ≥ est(h).
- Confidences = max predict_proba (SVC trained with probability=True / Platt when these gates are active).
- **Label accounting (honest):** both gates use labeled *source/validation* data available at training time
  (standard assumption of this literature) and **zero labels from the evaluation window** — the exact
  resource distinction vs our `labeled_probe`, which spends target-window labels.

## Design (fixed)
- Gates: {atc, doc}; detector: KS-max; trigger: legacy consecutive-3 + cooldown 10 (unchanged).
- Regimes: PortScan (benefit), UNSW Reconnaissance (marginal), ToN-IoT Scanning (harm).
- Downstream: **SVC-RBF** (the fragile/harm case; Platt-calibrated) and **Random Forest** (native
  predict_proba — pre-empts "your models lack calibrated probabilities" and tests the estimators at their
  best). 30 seeds, 100 windows. RF `none`/`lp32` baselines re-run at 30 seeds for paired comparison.
- gate_val_size = 256 (balanced), drawn at the training severity of each model.

## Pre-fixed success criteria (mirror of Phase-2 A/B/C, evaluated per gate × downstream)
- **B (harm avoidance, decisive):** ToN-IoT gain vs no-adaptation ≥ −0.5 pts.
- **A (benefit preservation):** PortScan BA ≥ naive − 0.3 pts.
- **C (marginal non-degradation):** UNSW BA ≥ naive − 0.3 pts.

## Interpretation rules (fixed before results)
- If ATC/DoC **fail B on the fragile downstream** (SVC): the necessity claim is upgraded — "a few target
  labels are necessary" now holds against the state-of-the-art label-free estimators, not just naive
  disagreement. Report as a positive empirical result with the C1 literature cited.
- If ATC/DoC **pass everywhere**: the necessity claim is withdrawn; the contribution is reframed as the
  validate-before-commit abstraction with two instantiations (target-label probe; label-free estimate),
  and the labeled probe retained as the variant with distribution-free guarantees.
- Mixed outcomes (e.g., pass on RF, fail on SVC): report the boundary honestly — label-free gating works
  where calibrated probabilities survive shift, and fails where they do not; target labels remain necessary
  in the fragile case, which is exactly where the harm lives.
