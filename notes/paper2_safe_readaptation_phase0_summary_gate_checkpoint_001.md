# Paper 2 Safe Readaptation Phase 0 Summary Gate 001

## Purpose

This note documents the Phase 0 decision gate for the safe-readaptation pivot.

The goal was not to prove a new claim, but to decide whether existing results justify a minimal, pre-registered policy experiment.

## Evidence

The aggregate summary gate shows three distinct regimes.

### Benefit regimes

CICIDS2017 DDoS:

- no adaptation BA: 0.698302
- best adaptive method: QK-MMD ZZ
- best adaptive BA: 0.893271
- best gain vs no adaptation: +19.496875
- all adaptive methods have positive gain.

CICIDS2017 PortScan:

- no adaptation BA: 0.877076
- best adaptive method: QK-MMD ZZ
- best adaptive BA: 0.939115
- best gain vs no adaptation: +6.203906
- all adaptive methods have positive gain.

Thursday WebAttacks:

- no adaptation BA: 0.842625
- best adaptive method: QK-MMD PauliXZ
- best adaptive BA: 0.919109
- best gain vs no adaptation: +7.648438
- all adaptive methods have positive gain.

UNSW-NB15 DoS:

- no adaptation BA: 0.840055
- best adaptive method: KS-max
- best adaptive BA: 0.853953
- best gain vs no adaptation: +1.389844
- all adaptive methods have positive gain.

### Harm regime

ToN-IoT Scanning:

- no adaptation BA: 0.920125
- best adaptive method: QK-MMD PauliXZ
- best adaptive BA: 0.913906
- best gain vs no adaptation: -0.621875
- worst adaptive method: MMD-RBF
- worst gain vs no adaptation: -4.491406
- all adaptive methods have negative gain.

### Mixed regime

UNSW-NB15 Reconnaissance:

- no adaptation BA: 0.846023
- best adaptive method: QK-MMD ZZ
- best adaptive BA: 0.849461
- best gain vs no adaptation: +0.343750
- worst adaptive method: JSD
- worst gain vs no adaptation: -0.128906
- four adaptive methods have positive gain.
- two adaptive methods have negative gain.

## Interpretation

The most generalizable signal across the campaign is not universal quantum advantage.

The robust finding is that drift-triggered readaptation is regime-dependent:

- in some regimes, adaptation is beneficial;
- in some regimes, adaptation is harmful;
- in mixed regimes, the choice of detector matters.

Therefore, the safe-readaptation pivot is scientifically justified.

## Limitation

This Phase 0 gate uses aggregate summary files, not a window-level oracle regret analysis.

It should be treated as a decision gate only, not as final evidence for the paper claim.

## Decision

Proceed to a minimal pre-registered Phase 1 safe-readaptation experiment.

Do not add new datasets.

Do not tune quantum feature maps.

Do not expand the detector set.

Do not frame the claim as quantum advantage.

## Phase 1 proposed scope

Datasets/regimes:

1. CICIDS2017 PortScan: beneficial-adaptation regime.
2. UNSW-NB15 Reconnaissance: mixed regime.
3. ToN-IoT Scanning: harmful-adaptation regime.

Detectors:

1. QK-MMD ZZ.
2. KS-max.

Policies:

1. no adaptation.
2. current triggered adaptation.
3. k-of-n 2/3.
4. k-of-n 3/5.
5. k-of-n 2/3 + cooldown 3.
6. k-of-n 3/5 + cooldown 5.

Success criterion:

The pivot is viable if safe policies:

- preserve most of the gain in CICIDS PortScan;
- reduce or eliminate harmful adaptation in ToN-IoT Scanning;
- do not degrade UNSW-NB15 Reconnaissance;
- reduce readaptations relative to current triggered adaptation.

Stop criterion:

If safe policies fail to avoid harmful adaptation in ToN-IoT or destroy the gains in CICIDS, stop the Q1-rescue attempt and write the Q2 paper.

## Strategic conclusion

The safe-readaptation pivot passes the Phase 0 gate.

It is not yet a Q1 result, but it is the only scientifically legitimate route left for a stronger paper.

The paper should no longer be framed as a quantum-advantage detector comparison.

It should be framed as:

Safe readaptation under network drift: when drift detection should not trigger IDS updates.
