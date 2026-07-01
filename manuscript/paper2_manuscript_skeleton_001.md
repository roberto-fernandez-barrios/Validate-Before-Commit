# Paper 2 Manuscript Skeleton

## Working title

Regime-Dependent Quantum-Kernel Drift Monitoring for Adaptive Intrusion Detection Systems

Alternative:

Operational Trade-offs of Quantum-Kernel MMD for Adaptive IDS Readaptation under Progressive Drift

## Core claim

Quantum-kernel MMD drift monitors do not provide universal quantum advantage over classical detectors. However, they induce attack-regime-dependent operating profiles for adaptive IDS readaptation: in some CICIDS2017 regimes QK-MMD reduces readaptation frequency at comparable downstream performance, while in others it improves raw recovery at higher operational cost. External UNSW-NB15 results show competitive but marginal QK behavior, reinforcing a cautious operational characterization rather than a superiority claim.

## Abstract draft

Adaptive intrusion detection systems must decide when to update their downstream classifiers as traffic distributions evolve. Drift monitors based on maximum mean discrepancy provide a natural trigger for such readaptation, and quantum kernels offer an alternative similarity measure that may respond differently to distributional change. This paper evaluates quantum-kernel MMD monitors for progressive drift readaptation in intrusion detection systems. We compare QK-MMD variants against classical Energy distance, RBF-MMD, Kolmogorov-Smirnov and Jensen-Shannon detectors across multiple CICIDS2017 attack regimes and an external UNSW-NB15 validation. Rather than finding universal quantum advantage, our results show attack-dependent operating profiles. In CICIDS2017 Wednesday and DDoS regimes, QK-MMD ZZ achieves downstream performance comparable to Energy distance while requiring fewer readaptations. In PortScan, QK-MMD ZZ improves raw recovery but triggers more readaptations. In WebAttacks, QK-MMD PauliXZ obtains the highest mean downstream accuracy and significantly improves over Energy/JSD, but not over the strongest classical baselines. Benign-drift controls show that QK-MMD does not reduce nuisance triggers, while an expensive Random Forest downstream test shows that quantum monitoring overhead can dominate operational cost. A feature-map sensitivity study finds no evidence that deeper maps unlock a stronger advantage. External UNSW-NB15 results are mixed, with QK-MMD remaining competitive but not significantly better than strong classical baselines. The results position QK-MMD as a regime-dependent operational alternative for adaptive IDS readaptation, not as a universally superior drift detector.

## Contributions

1. We formulate QK-MMD drift monitoring as a trigger for adaptive IDS readaptation under progressive traffic drift.

2. We introduce an operational evaluation protocol that measures not only detection, but downstream balanced accuracy, degradation area, gain versus no adaptation, readaptation frequency, nuisance triggers and runtime.

3. We compare QK-MMD against strong classical detectors across four CICIDS2017 adversarial regimes: Wednesday, DDoS, PortScan and WebAttacks.

4. We show that QK-MMD produces regime-dependent operating profiles rather than universal superiority.

5. We provide negative and robustness controls, including benign-drift nuisance analysis, expensive downstream retraining, feature-map sensitivity and external UNSW-NB15 validation.

## Section plan

### 1. Introduction

Purpose:

- motivate adaptive IDS under distribution shift;
- explain why drift detection alone is insufficient;
- introduce readaptation-triggering problem;
- position QK-MMD as candidate monitor;
- state honest claim: operational characterization, not universal advantage.

### 2. Related Work

Subsections:

- IDS under concept drift;
- MMD and two-sample testing for drift detection;
- quantum kernels for machine learning;
- quantum methods in cybersecurity/IDS;
- adaptive model retraining and operational cost.

### 3. Method

Include:

- classical MMD;
- quantum-kernel MMD;
- feature maps ZZ and PauliXZ;
- classical baselines: Energy, MMD-RBF, KS, JSD;
- triggered readaptation policy;
- downstream classifier;
- metrics.

### 4. Experimental Protocol

Include:

- CICIDS2017 scenarios;
- UNSW-NB15 external validation;
- progressive drift construction;
- calibration windows;
- readaptation policy;
- seeds and paired CI;
- nuisance benign controls;
- feature-map sensitivity.

### 5. Results

Main structure:

5.1 Does progressive drift degrade IDS performance?

5.2 Does triggered readaptation recover performance?

5.3 CICIDS2017 multi-regime comparison.

5.4 Operational profiles: efficiency vs raw recovery.

5.5 Benign/nuisance drift controls.

5.6 Cost and runtime analysis.

5.7 External UNSW-NB15 validation.

### 6. Discussion

Discuss:

- no universal QK advantage;
- regime-dependent behavior;
- why PortScan/WebAttacks differ from Wednesday/DDoS;
- runtime limitations;
- benign drift limitations;
- when QK-MMD may be operationally useful.

### 7. Limitations

Include:

- mainly CICIDS2017;
- UNSW mixed;
- simulator/progressive drift construction;
- quantum simulation runtime;
- small quantum feature maps;
- downstream model choices;
- no deployment claim.

### 8. Conclusion

Close with:

- QK-MMD as operationally distinct but not universally better;
- adaptive IDS evaluation should consider readaptation frequency, nuisance, and runtime;
- future work: hardware-aware kernels, stronger external datasets, learned policies.

## Main tables

1. CICIDS2017 multi-regime summary.
2. Paired CI QK vs strongest classical baseline by regime.
3. Operational profile table: BA/gain/adaptations/runtime.
4. Benign nuisance table.
5. Utility/cost table.
6. UNSW external validation summary.

## Appendix tables

1. Feature-map sensitivity.
2. RF expensive downstream.
3. UNSW paired details.
4. Additional detector diagnostics.
