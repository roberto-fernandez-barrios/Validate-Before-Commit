# Paper 2 — Phase 2 Pre-Registration: Label-Efficient Gated Readaptation

**Status:** PRE-REGISTERED before the confirmatory run. Pipeline validated by smoke (energy detector, 3 seeds, 40 windows); this document locks the confirmatory design, success criteria, and stop rule BEFORE running the confirmatory seeds/detectors.
**Motivation:** The mechanism law (`corr(base no-adapt BA, adaptation benefit) = −0.894`, see `paper2_q1_audit_and_mechanism_001.md`) says adaptation helps iff the deployed model has degraded. Phase 1's k-of-n/cooldown heuristics failed because they act on *distribution change*, not *model degradation*. Phase 2 tests a policy that gates adaptation on an explicit estimate of whether the candidate model is actually better — a **validate-before-commit** gate.

---

## Hypothesis (falsifiable)

A safe/cost-aware readaptation gate that, on each drift trigger, retrains a **candidate** model and **commits it only if it beats the deployed model on a small labeled probe**, will:
- preserve the benefit of adaptation where adaptation helps (CICIDS PortScan),
- avoid the harm of adaptation where it hurts (ToN-IoT Scanning),
- not degrade the mixed regime (UNSW Reconnaissance),
- using a small label budget (≤ 64 labels per evaluation),
- and do so **independently of the drift detector** (classical KS-max and quantum QK-ZZ).

A secondary, higher-risk gate (`unsup_disagree`, zero labels, commit iff deployed/candidate prediction disagreement ≥ 0.15) is evaluated to test whether labels are actually necessary. Smoke evidence suggests it is insufficient (an honest secondary result either way).

## Gates evaluated (fixed set — no post-hoc additions)

1. `none` — naive trigger (current behavior; commits every triggered adaptation). Baseline.
2. `labeled_probe`, probe budget ∈ {32, 64}, margin = 0.0 — commit iff candidate BA ≥ deployed BA on a fresh balanced labeled probe.
3. `unsup_disagree`, threshold = 0.15 — commit iff prediction disagreement on the unlabeled current window ≥ 0.15.

Reference bounds already available: `no_adaptation` (never adapt) and the decision-oracle regret from `paper2_oracle_regret_decision_001/`.

## Regimes (fixed — chosen a priori to span the phenomenon)

- **Benefit:** CICIDS2017 PortScan (Tuesday → Friday-PortScan).
- **Mixed:** UNSW-NB15 Reconnaissance.
- **Harm:** ToN-IoT Scanning.

## Detectors (fixed)

- KS-max (cheap classical) and QK-MMD ZZ (quantum instrument). Passing on both = detector-invariance of the policy.

## Fixed protocol

- Seeds: 10 (medium). PortScan may be escalated to 30 only for the final reported number if it already passes at 10.
- post_windows = 100, ramp_windows = 80, calibration_windows = 30, window_size = 128, dim = 8.
- Trigger policy held fixed at the legacy `consecutive k=3, cooldown=10` for ALL gates, so the gate is the only moving part (isolates the gate effect from trigger-policy confounds).
- q_reps = 1, q_input_scaling = atan_standard.
- Fresh `no_adaptation` and naive baselines are generated inside every run (internal, apples-to-apples).

## Pre-registered success criteria

Let `BA_gate`, `BA_naive`, `BA_noadapt` be mean balanced accuracy over seeds; `gain = BA − BA_noadapt`.

- **A — Benefit preservation (PortScan):** `gain_gate ≥ 0.90 × gain_naive` AND `BA_gate ≥ BA_naive − 0.003`.
- **B — Harm avoidance (ToN-IoT):** `BA_gate ≥ BA_noadapt − 0.005`. (Naive fails this: BA_naive ≈ BA_noadapt − 0.03.)
- **C — Mixed non-degradation (UNSW Recon):** `BA_gate ≥ BA_naive − 0.003`.
- **D — Label efficiency:** A ∧ B achieved with a probe budget ≤ 64.
- **E — Detector-invariance:** A ∧ B ∧ C hold for BOTH KS-max and QK-ZZ.

**Phase 2 PASSES iff** A ∧ B ∧ C ∧ D ∧ E hold for the `labeled_probe` gate.

## Stop rule (hard)

- **Pass →** Q1 write-up: "safe, label-efficient readaptation solves harmful adaptation that simple policies and detector choice cannot." The gate becomes the paper's deployable contribution; QK stays an instrument (detector-invariance).
- **Fail →** the honest negative stands; write the strong Q2 (mechanism law + oracle-regret + failed simple policies). Report Phase 2 as a further honest negative.
- **Either way:** no additional gates, no threshold tuning beyond the fixed set above, no additional datasets, no additional regimes. Closed protocol.

## Threats to validity (disclosed up front)

- Retraining uses **true labels** (inherited from the base protocol); the probe gate therefore has access to labels by construction. The realistic-cost knob is the **probe budget**, which we report explicitly; the contribution is "how few labels avoid harm while preserving benefit," not "labels are free."
- The gate is evaluated at fixed severity per window; online label latency is not modeled (limitation).
- Smoke used energy detector; confirmatory uses KS-max + QK-ZZ.

## Smoke evidence (pipeline validation only, not confirmatory)

Energy detector, 3 seeds, 40 windows:
- ToN-IoT: none BA 0.904 (harm) → labeled_probe(64) BA 0.930 (harm avoided, > no-adapt 0.920); unsup_disagree 0.906 (weak).
- PortScan: none gain +6.26 → labeled_probe(64) gain +6.22 (99% preserved); unsup_disagree +3.98 (over-rejects).

*No confirmatory conclusions drawn from the smoke. Confirmatory run follows this document.*
