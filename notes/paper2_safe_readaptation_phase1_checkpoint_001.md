# Paper 2 Safe Readaptation Phase 1 Checkpoint 001

## Purpose

This checkpoint documents the final Phase 1 safe-readaptation experiment.

Phase 1 was introduced after the detector-comparison route failed to provide robust Q1-level external validation. The goal was to test whether a legitimate pivot from "quantum advantage" to "safe readaptation" could rescue a stronger paper.

## Pre-registered success criteria

The pivot would pass if all three conditions held:

1. CICIDS2017 PortScan:
   - at least one safe policy preserves at least 70% of the legacy-trigger gain;
   - and reduces readaptations relative to legacy.

2. ToN-IoT Scanning:
   - at least one safe policy improves over legacy;
   - moves performance closer to no-adaptation;
   - and reduces readaptations.

3. UNSW-NB15 Reconnaissance:
   - safe policy does not materially underperform legacy.

## Policies tested

Legacy:

- legacy_consecutive3_cooldown10

Safe policies:

- k2_of_3_cooldown0
- k3_of_5_cooldown0
- k2_of_3_cooldown3
- k3_of_5_cooldown5

Detectors:

- QK-MMD ZZ
- KS-max

Regimes:

- CICIDS2017 PortScan
- UNSW-NB15 Reconnaissance
- ToN-IoT Scanning

## Results

Final success scan:

- criterion_A_portscan_any_pass: false
- criterion_B_ton_iot_any_pass: false
- criterion_C_unsw_any_pass: true
- phase1_passes: false

### Criterion A: PortScan

Safe policies retained or even improved gain, but did not reduce adaptations.

Example:

- QK-MMD ZZ with k2_of_3_cooldown0:
  - BA: 0.942477
  - gain vs no-adaptation: 5.069531
  - gain retention vs legacy: 1.057874
  - adaptation reduction vs legacy: -1.8

Interpretation:

The policy was not safer or more cost-aware. It was more aggressive.

### Criterion B: ToN-IoT Scanning

No safe policy avoided harmful readaptation.

Best candidate:

- KS-max with k3_of_5_cooldown0:
  - BA: 0.882812
  - gain vs no-adaptation: -3.731250
  - harm avoided vs legacy: 0.464062
  - adaptation reduction vs legacy: -0.7

Interpretation:

Even when harm was slightly reduced relative to legacy, adaptations increased and performance remained far below no-adaptation.

### Criterion C: UNSW-NB15 Reconnaissance

Some safe policies did not materially degrade relative to legacy.

Example:

- QK-MMD ZZ with k3_of_5_cooldown0:
  - BA: 0.849305
  - gain vs no-adaptation: 0.328125
  - delta BA vs legacy: -0.000156

Interpretation:

The mixed-regime criterion passed, but this is insufficient because the benefit and harm criteria failed.

## Final verdict

Phase 1 fails.

The safe-readaptation pivot was scientifically legitimate, but the tested simple k-of-n/cooldown policies do not provide a strong enough result to support a Q1 rescue.

## Strategic decision

Stop experiments.

Do not add more policies.

Do not add more datasets.

Do not tune feature maps.

Do not try to rescue a quantum-advantage claim.

Move to manuscript writing with a Q2-strong positioning.

## Final paper positioning

The paper should be framed as:

> An operational characterization of quantum-kernel MMD drift monitors for adaptive IDS readaptation under progressive drift.

The paper should not claim:

> robust quantum advantage.

The paper may include the safe-readaptation phase as an honest negative/diagnostic appendix or limitation:

> A minimal safe-readaptation policy grid showed that simple k-of-n/cooldown policies were insufficient to reliably prevent harmful readaptation, suggesting that future work requires more principled decision policies rather than more sensitive drift detectors.

## Final conclusion

The thesis/paper remains scientifically valuable, but the Q1-rescue path should be closed.
