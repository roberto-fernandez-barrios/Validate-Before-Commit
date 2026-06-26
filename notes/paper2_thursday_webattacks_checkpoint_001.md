# Paper 2 Thursday WebAttacks Checkpoint 001

## Purpose

This checkpoint summarizes the final Tuesday -> Thursday WebAttacks progressive readaptation experiment.

Thursday WebAttacks was added as an additional CICIDS2017 attack regime involving application-layer/web attacks. It is not a second external dataset, but it broadens the set of evaluated attack regimes beyond Wednesday, DDoS and PortScan.

## Dataset

Reference:

- Tuesday-WorkingHours.pcap_ISCX.csv

Current:

- Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv

Labels in Thursday WebAttacks:

- BENIGN: 168186
- Web Attack Brute Force: 1507
- Web Attack XSS: 652
- Web Attack SQL Injection: 21

The experiment treats this as binary BENIGN vs WebAttack.

Thursday Infiltration was not used because it contains only 36 attack samples.

## Final setup

- seeds: 30
- windows: 100
- methods:
  - Energy distance
  - MMD-RBF
  - KS-max
  - JSD
  - QK-MMD ZZ
  - QK-MMD PauliXZ
- q_reps: 1
- q_input_scaling: atan_standard

## Mean results

| method | BA | cumulative error | gain vs no adapt | adaptations | detector runtime |
|---|---:|---:|---:|---:|---:|
| QK-MMD PauliXZ | 0.919109 | 8.089063 | 7.648438 | 4.966667 | 7.344244 |
| QK-MMD ZZ | 0.913706 | 8.629427 | 7.108073 | 5.300000 | 6.996546 |
| MMD-RBF | 0.912453 | 8.754687 | 6.982812 | 2.166667 | 4.103174 |
| KS-max | 0.909310 | 9.069010 | 6.668490 | 3.400000 | 0.273006 |
| JSD | 0.902419 | 9.758073 | 5.979427 | 3.766667 | 0.027208 |
| Energy distance | 0.900076 | 9.992448 | 5.745052 | 2.766667 | 0.067458 |
| No adaptation | 0.842625 | 15.737500 | 0.000000 | 0.000000 | 0.000000 |

## Paired interpretation: QK-MMD PauliXZ

QK-MMD PauliXZ significantly outperforms Energy distance:

- BA diff: +0.019034
- CI95: [0.000352, 0.041498]
- cumulative error diff: -1.903385
- CI95: [-4.149753, -0.035156]

QK-MMD PauliXZ significantly outperforms JSD:

- BA diff: +0.016690
- CI95: [0.002148, 0.032469]
- cumulative error diff: -1.669010
- CI95: [-3.246888, -0.214844]

However, QK-MMD PauliXZ does not significantly outperform MMD-RBF:

- BA diff: +0.006656
- CI95: [-0.004195, 0.017370]

It also does not significantly outperform KS-max:

- BA diff: +0.009799
- CI95: [-0.002344, 0.023510]

Nor does it significantly outperform QK-MMD ZZ:

- BA diff: +0.005404
- CI95: [-0.004244, 0.015534]

## Cost trade-off

QK-MMD PauliXZ requires significantly more adaptations and runtime than the classical baselines.

Compared with MMD-RBF:

- adaptations diff: +2.80
- CI95: [2.30, 3.23]
- runtime diff: +3.24 s
- CI95: [3.04, 3.47]

Compared with Energy distance:

- adaptations diff: +2.20
- CI95: [1.73, 2.60]
- runtime diff: +7.28 s
- CI95: [7.20, 7.37]

Therefore, WebAttacks supports a raw-recovery interpretation of QK-MMD PauliXZ, not an efficiency interpretation.

## Paper-level conclusion

Thursday WebAttacks strengthens the regime-dependent interpretation.

QK-MMD PauliXZ achieves the highest mean downstream accuracy and significantly improves over Energy distance and JSD, but not over the strongest classical baselines MMD-RBF and KS-max.

The result therefore supports the broader claim that quantum-kernel drift monitors can provide competitive but attack-dependent operating points. It does not support universal quantum advantage.

## Recommended placement

Include Thursday WebAttacks in the main multi-scenario results table.

Discuss it as:

- evidence that QK-MMD can be competitive in application-layer attack drift;
- evidence that the best QK map can be attack-dependent;
- evidence that QK gains often come with higher readaptation/runtime cost.

Do not present it as a clean QK win over all classical baselines.

## Files

Raw:

- results/raw/paper2_progressive_thursday_webattacks_final_001/

Tables:

- results/tables/paper2_progressive_thursday_webattacks_final_001/paper_table_thursday_webattacks_summary.csv
- results/tables/paper2_progressive_thursday_webattacks_final_001/paper_table_thursday_webattacks_qk_paulixz_paired.csv

Analysis script:

- src/analysis/make_paper2_thursday_webattacks_artifacts.py
