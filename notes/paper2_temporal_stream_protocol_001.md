# Real chronological stream — protocol (LOCKED before the confirmatory run)

**Date:** 2026-07-14 · Committed/pushed before confirmatory seeds run. Runner:
`src/experiments/run_paper2_temporal_stream.py`. Smoke: seed 104 only (verified the runner and
observed no-adapt ≈0.73 vs gated ≈0.90); seed 104 is therefore excluded from confirmation.

## Design (fixed)
- Stream: CICIDS2017 **Friday in true temporal order** (Morning/Botnet → Afternoon-PortScan →
  Afternoon-DDoS, file order), 200 consecutive 256-row blocks (stride to span the day),
  **natural class composition** (no balancing, no severity ramp, no pools).
- Incumbent: trained on Tuesday (the temporal past; balanced training sample — standard
  training practice, evaluation untouched). KS-max trigger calibrated on Tuesday-internal
  windows (q=0.95, 3-consecutive, cooldown 10).
- Candidate: retrains on the last 8 OBSERVED windows (labeled, strictly past). Probe:
  32 labeled rows from the window 9 steps back (past, disjoint from candidate training).
- Arms: {naive, labeled_probe b=32}; no-adaptation computed within each run.
- **Seeds 134–163** (30; affect only model init/subsampling — the stream order is fixed).

## Fixed questions
- T1: does drift-triggered adaptation help on a real chronological stream (naive and gated
  vs no-adaptation, paired CI)?
- T2: is the gate never significantly below naive or no-adaptation (composability/safety)?
- T3: report FPR and attack-fraction trajectories; single-class windows use plain accuracy.
Interpretation: any outcome reported; this is an external-validity study, exploratory relative
to the v2 confirmatory core.
