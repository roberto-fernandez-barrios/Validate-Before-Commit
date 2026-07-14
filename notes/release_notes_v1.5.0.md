## What changed since v1.4.0

**Amendment 002 — pristine confirmatory window.** Seeds touched by the harness smoke were
replaced (top-up 131–133); the registered replication now reports 30 pristine seeds 104–133.
All A/B/C/I criteria pass: ToN-IoT naive −1.64 [−2.72, −0.64] → gate +0.79 [0.53, 1.07]
(+2.43 [1.53, 3.43] vs naive); PortScan +9.12; UNSW +1.35; QK-ZZ invariant. Per-trigger
mechanism hardened with per-seed cluster-bootstrap CIs and leave-one-regime-out (r_deg
−0.67..−0.70, r_score ≈ 0), stated predictively. Honest corrections: the deduplicated holdout
gate is no longer equivalent to the fresh probe (harm reduction at zero incremental cost; the
32-label fresh probe remains the recommended gate); natural-prevalence arms recalibrated at
operating prevalence reveal the detector is starved under imbalance. Model-agnosticism
re-established on v2 with the primary gate and paired CIs (rescues MLP/ToN: −0.16 → +0.25).

**Amendment 003 — canonical monitors and adaptive-update baselines.** Canonical DDM is itself
net-harmful in the harm regime (−2.59 [−5.90, −0.34]; the gate rescues it); ADWIN never fires;
a soft incumbent+candidate ensemble is the strongest label-free rival (+0.34 ToN, +8.55
PortScan) but dilutes the marginal regime; sliding-window retraining remains harmful (−2.44).
Across eight monitoring/estimation/update alternatives, none attains safety and full benefit
in all three regimes; the labeled probe does.

**Real chronological stream (registered, seeds 134–163).** CICIDS Friday in true temporal
order: the incumbent collapses to 68.4% BA, drift-triggered retraining recovers +21.3
[20.7, 22.0], and the gate pays an insurance premium there (−1.42 [−2.45, −0.47] vs naive,
~7% of the gain) — the one pre-registered check it fails, reported as such.

**Cost-sensitive formalization.** The gate as myopic utility maximizer with
ε* = (λ_U+λ_C)/(λ_e·N); the margin sweep is its empirical operating characteristic.

Claims audit: 155 checks, all passing.
