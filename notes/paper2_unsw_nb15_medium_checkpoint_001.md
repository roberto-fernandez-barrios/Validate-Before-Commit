# Paper 2 UNSW-NB15 Medium Checkpoint 001

## Purpose

This checkpoint summarizes the first external-dataset medium experiment for Paper 2.

UNSW-NB15 was introduced because all previous evidence came from CICIDS2017. The goal was not to prove universal quantum advantage, but to test whether the regime-dependent behavior of QK-MMD appears outside the CICIDS2017/CICFlowMeter ecosystem.

## Dataset

Dataset:

- UNSW-NB15

Raw files used:

- data/raw/unsw_nb15/Training and Testing Sets/UNSW_NB15_training-set.csv
- data/raw/unsw_nb15/Training and Testing Sets/UNSW_NB15_testing-set.csv

Processed scenarios:

1. UNSW DoS
   - reference: training set excluding DoS
   - current: testing set with Normal + DoS

2. UNSW Reconnaissance
   - reference: training set excluding Reconnaissance
   - current: testing set with Normal + Reconnaissance

Preprocessing:

- numeric features only;
- dropped id, label, attack_cat;
- did not one-hot encode proto/service/state in this first smoke/medium;
- binary Label = BENIGN vs ATTACK.

## Medium setup

- seeds: 10
- post_windows: 100
- ramp_windows: 100
- calibration_windows: 30
- n_permutations: 100
- methods:
  - Energy distance
  - MMD-RBF
  - KS-max
  - JSD
  - QK-MMD ZZ
  - QK-MMD PauliXZ
- q_reps: 1
- q_input_scaling: atan_standard

## UNSW DoS mean results

| method | BA | cumulative error | gain vs no adapt | adaptations | detector runtime |
|---|---:|---:|---:|---:|---:|
| KS-max | 0.853953 | 14.604688 | 1.389844 | 2.4 | 0.258563 |
| JSD | 0.852281 | 14.771875 | 1.222656 | 2.1 | 0.024572 |
| QK-MMD PauliXZ | 0.849617 | 15.038281 | 0.956250 | 2.2 | 7.282473 |
| MMD-RBF | 0.849555 | 15.044531 | 0.950000 | 1.6 | 3.972786 |
| Energy distance | 0.845836 | 15.416406 | 0.578125 | 2.4 | 0.064312 |
| QK-MMD ZZ | 0.844461 | 15.553906 | 0.440625 | 2.0 | 6.999288 |
| No adaptation | 0.840055 | 15.994531 | 0.000000 | 0.0 | 0.000000 |

## UNSW DoS paired interpretation

QK-MMD PauliXZ is not significantly better than Energy distance:

- BA diff: +0.003781
- CI95: [-0.002961, 0.010664]

QK-MMD PauliXZ is essentially tied with MMD-RBF:

- BA diff: +0.000062
- CI95: [-0.011196, 0.009008]

QK-MMD PauliXZ is not significantly better than KS-max:

- BA diff: -0.004336
- CI95: [-0.014438, 0.005367]

QK-MMD ZZ is not significantly better than Energy distance:

- BA diff: -0.001375
- CI95: [-0.011649, 0.008430]

Conclusion for DoS:

> UNSW DoS does not provide evidence of a QK-MMD advantage. QK-MMD PauliXZ is competitive with MMD-RBF but not better, while KS-max and JSD have the best mean performance.

## UNSW Reconnaissance mean results

| method | BA | cumulative error | gain vs no adapt | adaptations | detector runtime |
|---|---:|---:|---:|---:|---:|
| QK-MMD ZZ | 0.849461 | 15.053906 | 0.343750 | 2.7 | 7.246585 |
| Energy distance | 0.848438 | 15.156250 | 0.241406 | 2.3 | 0.066566 |
| MMD-RBF | 0.847914 | 15.208594 | 0.189063 | 2.6 | 4.420077 |
| KS-max | 0.846922 | 15.307813 | 0.089844 | 2.5 | 0.268791 |
| No adaptation | 0.846023 | 15.397656 | 0.000000 | 0.0 | 0.000000 |
| QK-MMD PauliXZ | 0.845742 | 15.425781 | -0.028125 | 2.2 | 7.598221 |
| JSD | 0.844734 | 15.526563 | -0.128906 | 2.1 | 0.027209 |

## UNSW Reconnaissance paired interpretation

QK-MMD ZZ is not significantly better than Energy distance:

- BA diff: +0.001023
- CI95: [-0.003406, 0.005000]

QK-MMD ZZ is not significantly better than MMD-RBF:

- BA diff: +0.001547
- CI95: [-0.001922, 0.005008]

QK-MMD ZZ is not significantly better than KS-max:

- BA diff: +0.002539
- CI95: [-0.002547, 0.007641]

QK-MMD ZZ is significantly better than JSD:

- BA diff: +0.004727
- CI95: [0.000281, 0.009555]

QK-MMD ZZ is significantly better than QK-MMD PauliXZ:

- BA diff: +0.003719
- CI95: [0.000211, 0.006891]

Conclusion for Reconnaissance:

> UNSW Reconnaissance provides a weak signal in favor of QK-MMD ZZ, but not a statistically conclusive advantage over the strongest classical baselines Energy, MMD-RBF or KS-max.

## Overall UNSW interpretation

UNSW-NB15 provides external validation that the Paper 2 pipeline works outside CICIDS2017.

However, it does not provide a strong QK advantage.

The results are mixed:

- UNSW DoS: classical KS/JSD lead in mean BA; QK-PauliXZ is competitive with MMD-RBF but not better.
- UNSW Reconnaissance: QK-ZZ leads in mean BA, but not significantly over strong classical baselines.

Therefore, UNSW supports a cautious external generalization claim:

> QK-MMD remains competitive in selected regimes outside CICIDS2017, but its advantages are marginal and generally not statistically significant against the strongest classical baselines.

## Strategic consequence

UNSW-NB15 medium does not justify a strong Q1 quantum-advantage claim.

It can support:

1. A Q2 paper with external validation and honest limitations.
2. A Q1-submission attempt only if framed as operational characterization, not QK superiority.

A 30-seed UNSW final is not recommended unless the goal is to document external mixed evidence rather than seek a strong positive result.

## Recommended next step

Do not immediately scale UNSW to 30 seeds.

First, ask for strategic review:

- Should UNSW medium be included as external validation?
- Should the UNSW protocol be improved with categorical features or additional attack categories?
- Or should the paper now move to writing with UNSW as a mixed external validation result?

## Files

Raw results:

- results/raw/paper2_unsw_nb15_dos_medium_001/
- results/raw/paper2_unsw_nb15_reconnaissance_medium_001/

Tables:

- results/tables/paper2_unsw_nb15_dos_medium_001/
- results/tables/paper2_unsw_nb15_reconnaissance_medium_001/

Scripts:

- src/analysis/prepare_paper2_unsw_nb15_smoke.py
- src/analysis/make_paper2_unsw_nb15_medium_artifacts.py

Protocol:

- notes/paper2_unsw_nb15_smoke_protocol_001.md
