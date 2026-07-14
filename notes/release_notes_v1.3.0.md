## What changed since v1.1.0

**Registered replication under harness v2 (headline).** New runner with common pre-generated
streams (arms process bit-identical windows: truly paired contrasts), role-disjoint
window/train/probe partitions, fully separated RNGs and per-trigger logging. Protocol locked
and publicly tagged (`harness-v2-protocol`) BEFORE any confirmatory seed ran; 21 runs on 30
fresh seeds (101–130). Every pre-specified criterion replicates: ToN-IoT naive −1.41 → gate
+0.95 (significantly above naive, +2.36 [1.40, 3.39]); PortScan +8.79; UNSW +1.31; QK-ZZ
invariant. The holdout gate (probe carved from the retraining batch) matches the fresh-probe
gate everywhere → the gate's incremental label cost can be zero. Per-trigger mechanism test
(no shared algebraic term, disjoint past/future windows): pre-trigger degradation predicts the
future value of committing at r = −0.65..−0.70 per regime; the detector score predicts ≈0.00.

**New robustness phases (pre-fixed protocols).** 2i replay (50/50 retrain-current-plus-replay
does not rescue naive triggering; the gate composes with it), 2j probe prevalence (gate
indifferent to probe composition down to a single attack flow), 2k size/dimensionality
controls (size-matched 2000/class candidates QUADRUPLE the harm — refuting the sample-size
confound; full-dimensional pipeline: benefit doubles, harm point estimate persists).

**Statistics and claims hardening.** Coupling-aware §5.2 (re-pairing null; restoration-to-
ceiling framing; within-deployment detector-score contrast); provenance honesty (pre-specified
protocol with disclosed 10→30 conditional expansion); harness caveats scoped to the initial
study; language harmonized across abstract, highlights, README and graphical abstract.

**Title updated** to "Validate Before Commit: Label-Efficient Empirical Gating of
Drift-Triggered Classifier Updates for Network Intrusion Detection".

Claims audit: 133 checks, all passing.
