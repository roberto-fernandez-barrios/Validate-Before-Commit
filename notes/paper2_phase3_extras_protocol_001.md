# Phase 3 extras — performance-aware trigger & natural-prevalence streams (LOCKED before runs)

**Date:** 2026-07-14 · Committed/pushed before the confirmatory batch. Harness v2, seeds 101–130.

## 3a — Performance-aware (DDM-style) trigger baseline
Labels spent on MONITORING instead of gating: 8 labeled flows/window from the probe partition;
trigger when the incumbent's mean monitored error over the last 3 windows exceeds the
calibration mean + 3σ (30 pre-drift windows). Arms: {perf-naive, perf+lp32} × 3 regimes.
Label budget: 800/stream (vs gate ≈0–160). Fixed questions: (Q1) does perf-naive avoid the
ToN harm (gain ≥ −0.5)? (Q2) does it capture the PortScan benefit (≥ detector-naive − 0.3)?
(Q3) does the gate still add value on top? Any outcome reported.

## 3b — Natural-prevalence evaluation streams (π = 0.05) with operational metrics
Evaluation/calibration windows drawn at attack fraction 0.05 (≥1 attack floor); FPR, recall
and alert volume logged per window. Arms: {none, lp32} × 3 regimes. Fixed questions:
(Q4) does the harm/benefit/marginal sign pattern hold on imbalanced streams (BA)?
(Q5) is the gate still safe and benefit-preserving? (Q6) report FPR/alert-volume deltas.
