## What changed since v1.3.0

**Phase 3 extras (pre-fixed protocols, harness v2, seeds 101–130).**
- *Performance-aware (DDM-style) trigger baseline*: labels spent on monitoring the incumbent's
  error instead of gating the update. Safe where the incumbent stays healthy (never fires in
  ToN-IoT) but benefit-lossy (PortScan +5.40 vs +7.94 naive; UNSW +0.04 vs +1.22) at 800
  monitoring labels/stream versus zero incremental labels for the holdout gate — labels are
  better spent on the commit decision than on monitoring.
- *Natural-prevalence evaluation streams* (π = 0.05) with per-window operational metrics: the
  sign pattern replicates (ToN-IoT naive −2.63 [−4.07, −1.37] → gated +0.80 [0.44, 1.20];
  PortScan +9.06/+9.41), and the gate simultaneously lowers FPR (0.145 → 0.099), raises attack
  recall (0.934 → 0.957) and cuts alert volume (23.2 → 17.8 alerts/window) vs naive retraining.

**Title** updated everywhere (manuscripts, README, citation metadata, graphical abstract):
"Validate Before Commit: Label-Efficient Empirical Gating of Drift-Triggered Classifier
Updates for Network Intrusion Detection". The graphical abstract now carries the
restoration-to-ceiling/headroom framing (per-trigger detector-score r ≈ 0).

Claims audit: 138 checks, all passing.
