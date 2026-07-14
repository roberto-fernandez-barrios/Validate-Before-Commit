# Harness v2 — Amendment 003: canonical monitors + adaptive-update baselines (LOCKED before runs)

**Date:** 2026-07-14 · Committed/pushed before the runs. Harness v2, pristine seeds 104–133,
KS-max where a detector applies, SVC-RBF, Phase-2 settings.

## 3c — Canonical performance-aware triggers (replaces the ad-hoc "DDM-style" monitor)
- **DDM** (Gama et al. 2004): p+s vs p_min+3·s_min on a monitored error stream (8 labels/window,
  incorporated as Bernoulli observations), reset on commit.
- **ADWIN** (Bifet & Gavaldà 2007): exact adaptive-window cut test (δ=0.002) on window error
  rates, reset on commit. Both self-confirm (no 3-consecutive rule) with the usual cooldown.
- Arms: {ddm, adwin} × {naive, lp32} × 3 regimes = 12 runs. Fixed questions:
  Q1 does either canonical monitor avoid the ToN harm without a gate? Q2 does it capture the
  PortScan benefit (≥ detector-naive − 0.3)? Q3 does the gate still add value on top?
  Label budget reported (800/stream monitoring vs ≈0–160 for the gate).

## 3d — Adaptive-update baselines (the update rule, not the decision, as the variable)
- **ensemble**: on commit, deploy a soft incumbent+candidate ensemble instead of replacing.
- **sliding_window**: the candidate retrains on the last 8 *observed* (already-seen, labeled)
  stream windows — a realistic temporal window, natural mixture, no pool access.
- Arms: {ensemble, sliding_window} × {naive, lp32} × 3 regimes = 12 runs. Fixed questions:
  Q4 does either update rule alone avoid the ToN harm? Q5 does it preserve benefit?
  Q6 does the gate compose (never significantly below the ungated variant or no-adaptation)?

## Interpretation rules (fixed)
Any outcome is reported. If a canonical monitor or update rule passes Q1+Q2 (or Q4+Q5) on its
own, the gate's claim narrows to label cost and composability, and the abstract is softened
accordingly. If they fail, the corresponding review objection ("weak baseline") is closed with
data. Cost-utility formalization (§3) and the temporal-stream study are registered separately.
