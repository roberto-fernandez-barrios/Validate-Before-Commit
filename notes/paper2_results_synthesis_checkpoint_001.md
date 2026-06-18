# Paper 2 results synthesis checkpoint 001

## Purpose

This note synthesizes the current experimental evidence for Paper 2. It separates supported claims from unsupported claims and identifies which results should be used as main paper evidence.

## Experimental blocks completed

- Controlled streaming drift detection.
- Adaptive monitor update.
- Downstream adaptation with global trigger policy.
- Downstream adaptation with detector-specific optimized policies.
- Hybrid classical-quantum monitor analysis.
- Geometry diagnostics linking score behavior and downstream utility.

## High-level verdict

The current evidence does not support a universal quantum advantage claim. QK-MMD does not dominate MMD-RBF across all regimes or downstream settings.

The evidence does support a more careful and scientifically defensible claim: quantum-kernel drift monitors provide regime-dependent and complementary drift evidence. MMD-RBF is stronger in low-moderate downstream adaptation, whereas QK-MMD provides stronger high-severity post-drift alarm persistence and competitive downstream recovery.

## Block 1: Controlled streaming drift detection

Best pre/post AUC by severity:

| severity | method         | n_seeds | pre_post_auc_mean | score_gap_mean |
| -------- | -------------- | ------- | ----------------- | -------------- |
| 0.1000   | QK-MMD ZZ      | 30      | 0.5132            | 0.0001         |
| 0.2500   | QK-MMD PauliXZ | 30      | 0.5482            | 0.0002         |
| 0.5000   | QK-MMD PauliXZ | 30      | 0.6923            | 0.0009         |
| 0.7500   | QK-MMD PauliXZ | 30      | 0.8110            | 0.0016         |
| 1.0000   | QK-MMD PauliXZ | 30      | 0.9182            | 0.0029         |

Best low-false-alarm policy by severity:

| severity | method         | threshold_quantile | consecutive_k | false_alarm_any_rate | post_detect_any_rate | trigger_gain |
| -------- | -------------- | ------------------ | ------------- | -------------------- | -------------------- | ------------ |
| 0.1000   | MMD-RBF        | 0.9500             | 2             | 0.1000               | 0.1667               | 0.0667       |
| 0.2500   | QK-MMD PauliXZ | 0.9500             | 2             | 0.0333               | 0.2000               | 0.1667       |
| 0.5000   | QK-MMD PauliXZ | 0.9500             | 2             | 0.0333               | 0.5667               | 0.5333       |
| 0.7500   | QK-MMD PauliXZ | 0.9500             | 2             | 0.0333               | 0.6667               | 0.6333       |
| 1.0000   | QK-MMD PauliXZ | 0.9500             | 2             | 0.0333               | 0.9000               | 0.8667       |

Interpretation: the controlled streaming block is the strongest evidence that quantum-kernel geometries, especially PauliXZ/ZZ in earlier results, can produce useful drift-monitoring signals. This is where the quantum contribution is most visible.

## Block 2: Adaptive monitor

Best clean adaptation by severity:

| severity | method         | n_seeds | false_alarm_any_rate | post_detect_any_rate | adaptation_success_rate | clean_adaptation_success_rate | score_reduction_after_adaptation_mean |
| -------- | -------------- | ------- | -------------------- | -------------------- | ----------------------- | ----------------------------- | ------------------------------------- |
| 0.1000   | MMD-RBF        | 30      | 0.1000               | 0.1667               | 0.1667                  | 0.1333                        | 0.0001                                |
| 0.2500   | MMD-RBF        | 30      | 0.1667               | 0.2000               | 0.1333                  | 0.1000                        | 0.0001                                |
| 0.5000   | QK-MMD PauliXZ | 30      | 0.1667               | 0.6667               | 0.5667                  | 0.4667                        | 0.0011                                |
| 0.7500   | QK-MMD PauliXZ | 30      | 0.1000               | 0.7333               | 0.6667                  | 0.6333                        | 0.0027                                |
| 1.0000   | MMD-RBF        | 30      | 0.1000               | 0.7667               | 0.7333                  | 0.6333                        | 0.0025                                |

Interpretation: the adaptive monitor block shows that drift alarms can be connected to an adaptive update of the monitoring reference/calibration. It supports operational utility at the monitor level, but not by itself a downstream IDS performance claim.

## Block 3: Downstream adaptation with global policy

Severity 1.0 downstream global-policy summary:

| severity | method            | balanced_accuracy | degradation_area | clean_rate | clean_gain | false_alarm |
| -------- | ----------------- | ----------------- | ---------------- | ---------- | ---------- | ----------- |
| 1.0000   | No adaptation     | 0.5808            | 0.3153           | 0.0000     | 0.0000     | 0.0000      |
| 1.0000   | MMD-RBF           | 0.8492            | 0.0469           | 0.9333     | 0.2511     | 0.0667      |
| 1.0000   | QK-MMD ZZ         | 0.8492            | 0.0469           | 0.9667     | 0.2596     | 0.0333      |
| 1.0000   | QK-MMD PauliXZ    | 0.8492            | 0.0469           | 0.9667     | 0.2596     | 0.0333      |
| 1.0000   | Oracle adaptation | 0.8961            | 0.0000           | 0.0000     | 0.0000     | 0.0000      |

Severity 0.25 downstream global-policy summary:

| severity | method         | balanced_accuracy | degradation_area | clean_rate | clean_gain | false_alarm |
| -------- | -------------- | ----------------- | ---------------- | ---------- | ---------- | ----------- |
| 0.2500   | MMD-RBF        | 0.9047            | 0.0251           | 0.8000     | 0.0437     | 0.0000      |
| 0.2500   | QK-MMD ZZ      | 0.8849            | 0.0457           | 0.4000     | 0.0211     | 0.0333      |
| 0.2500   | QK-MMD PauliXZ | 0.8851            | 0.0456           | 0.4000     | 0.0212     | 0.0333      |

Interpretation: the global downstream block shows that drift-triggered adaptation substantially reduces degradation relative to no adaptation. However, under the common global policy, MMD-RBF is stronger at severity 0.25, all methods are competitive at moderate drift, and QK-MMD variants are slightly cleaner in severe drift.

## Block 4: Detector-specific optimized policies

Best detector-specific optimized method by severity:

| severity | method         | threshold_quantile | consecutive_k | post_balanced_accuracy_mean | degradation_area_mean | clean_downstream_adaptation_rate | clean_adaptation_gain_mean | false_alarm_any_rate |
| -------- | -------------- | ------------------ | ------------- | --------------------------- | --------------------- | -------------------------------- | -------------------------- | -------------------- |
| 0.1000   | QK-MMD ZZ      | 0.9500             | 2             | 0.9204                      | 0.0221                | 0.2000                           | 0.0027                     | 0.1667               |
| 0.2500   | MMD-RBF        | 0.9900             | 2             | 0.9015                      | 0.0284                | 0.7667                           | 0.0404                     | 0.0000               |
| 0.5000   | MMD-RBF        | 0.9900             | 2             | 0.9011                      | 0.0143                | 1.0000                           | 0.1338                     | 0.0000               |
| 0.7500   | MMD-RBF        | 0.9900             | 2             | 0.8837                      | 0.0237                | 0.9667                           | 0.2023                     | 0.0333               |
| 1.0000   | QK-MMD PauliXZ | 0.9000             | 3             | 0.8492                      | 0.0469                | 0.9667                           | 0.2596                     | 0.0333               |

Interpretation: detector-specific optimization does not produce universal QK-MMD dominance. MMD-RBF remains strong in low-moderate drift, QK-MMD ZZ is competitive in moderate-to-severe drift, and QK-MMD PauliXZ is strongest in clean adaptation behavior at severity 1.0.

## Block 5: Hybrid classical-quantum monitor

Hybrid comparison at severity 0.25:

| severity | method         | balanced_accuracy | degradation_area | clean_rate | clean_gain | false_alarm |
| -------- | -------------- | ----------------- | ---------------- | ---------- | ---------- | ----------- |
| 0.2500   | Hybrid OR      | 0.9085            | 0.0214           | 0.8333     | 0.0453     | 0.0333      |
| 0.2500   | MMD-RBF        | 0.9047            | 0.0251           | 0.8000     | 0.0437     | 0.0000      |
| 0.2500   | QK-MMD ZZ      | 0.8849            | 0.0457           | 0.4000     | 0.0211     | 0.0333      |
| 0.2500   | QK-MMD PauliXZ | 0.8851            | 0.0456           | 0.4000     | 0.0212     | 0.0333      |

Hybrid comparison at severity 1.0:

| severity | method         | balanced_accuracy | degradation_area | clean_rate | clean_gain | false_alarm |
| -------- | -------------- | ----------------- | ---------------- | ---------- | ---------- | ----------- |
| 1.0000   | Hybrid OR      | 0.8492            | 0.0469           | 0.8667     | 0.2335     | 0.1333      |
| 1.0000   | MMD-RBF        | 0.8492            | 0.0469           | 0.9333     | 0.2511     | 0.0667      |
| 1.0000   | QK-MMD ZZ      | 0.8492            | 0.0469           | 0.9667     | 0.2596     | 0.0333      |
| 1.0000   | QK-MMD PauliXZ | 0.8492            | 0.0469           | 0.9667     | 0.2596     | 0.0333      |

Interpretation: the selected Hybrid OR monitor improves low-moderate adaptation at severity 0.25, but it does not improve global robustness relative to the best individual detector. It should be used as a robustness or negative/partial result, not as the main Q1 claim.

## Block 6: Geometry diagnostics

Geometry/downstream examples at severity 0.25 and 1.0:

| severity | method         | score_ratio_gap_post_minus_pre | alarm_rate_post | clean_downstream_adaptation_rate | clean_adaptation_gain_mean | degradation_area_mean | false_alarm_any_rate |
| -------- | -------------- | ------------------------------ | --------------- | -------------------------------- | -------------------------- | --------------------- | -------------------- |
| 0.2500   | MMD-RBF        | 0.0300                         | 0.1133          | 0.8000                           | 0.0437                     | 0.0251                | 0.0000               |
| 0.2500   | QK-MMD PauliXZ | 0.0173                         | 0.1167          | 0.4000                           | 0.0212                     | 0.0456                | 0.0333               |
| 0.2500   | QK-MMD ZZ      | 0.0183                         | 0.1133          | 0.4000                           | 0.0211                     | 0.0457                | 0.0333               |
| 1.0000   | MMD-RBF        | 0.4470                         | 0.4200          | 0.9333                           | 0.2511                     | 0.0469                | 0.0667               |
| 1.0000   | QK-MMD PauliXZ | 0.3413                         | 0.7567          | 0.9667                           | 0.2596                     | 0.0469                | 0.0333               |
| 1.0000   | QK-MMD ZZ      | 0.3431                         | 0.7267          | 0.9667                           | 0.2596                     | 0.0469                | 0.0333               |

Geometry/downstream correlations:

| method         | n | spearman_score_gap_vs_clean_gain | pearson_score_gap_vs_clean_gain | spearman_alarm_rate_vs_clean_gain | pearson_alarm_rate_vs_clean_gain |
| -------------- | - | -------------------------------- | ------------------------------- | --------------------------------- | -------------------------------- |
| MMD-RBF        | 5 | 1.0000                           | 0.9571                          | 1.0000                            | 0.9795                           |
| QK-MMD PauliXZ | 5 | 1.0000                           | 0.9613                          | 1.0000                            | 0.9397                           |
| QK-MMD ZZ      | 5 | 1.0000                           | 0.9616                          | 1.0000                            | 0.9424                           |

Interpretation: geometry diagnostics explain the regime dependence. MMD-RBF has stronger low-moderate score separation, matching its better downstream behavior at severity 0.25. QK-MMD has stronger high-severity post-drift alarm persistence, matching its cleaner severe-drift adaptation.

## Claims supported

1. Drift-triggered adaptation reduces downstream degradation relative to no adaptation.
2. QK-MMD provides competitive and complementary drift signals.
3. Detector behavior is regime-dependent.
4. QK-MMD variants provide stronger high-severity post-drift alarm persistence.
5. MMD-RBF is stronger in low-moderate downstream adaptation.
6. Geometry diagnostics explain why no universal dominance is observed.

## Claims not supported

1. Universal QK-MMD superiority over MMD-RBF.
2. Universal hybrid classical-quantum superiority.
3. A broad quantum advantage claim.
4. A claim that downstream improvement is uniquely caused by QK-MMD.

## Recommended paper narrative

The recommended narrative is not `quantum beats classical`. The stronger and more defensible narrative is:

> Quantum-kernel MMD provides regime-dependent drift geometry for cybersecurity adaptation. While it does not universally dominate a classical RBF-MMD baseline, its feature-map-induced discrepancy signals are complementary, especially in high-severity drift where QK-MMD yields more persistent post-drift alarms and cleaner downstream adaptation.

## Q1 assessment

The experimental base is now substantially stronger than a simple detector comparison. However, the paper should avoid claiming universal quantum advantage. For a Q1-oriented submission, the contribution should be framed around calibrated drift monitoring, downstream adaptation utility, regime dependence, and geometry-based explanation.

## Recommended main figures/tables

Main figures:

- Controlled streaming AUC / detection sensitivity vs severity.
- Low-false-alarm post-drift detection vs severity.
- Downstream degradation area vs severity.
- Clean adaptation gain vs severity.
- Geometry score gap vs severity.
- Geometry score gap or alarm rate vs downstream clean gain.

Main tables:

- Controlled streaming best low-false-alarm policy.
- Downstream global policy summary.
- Detector-specific optimized policy summary.
- Geometry vs downstream table.

## Next work

No further large downstream policy sweeps are recommended at this stage.

Useful remaining work:

- Statistical summaries / confidence intervals for the main tables.
- Runtime/cost discussion.
- Optional lightweight KS/JSD baseline for detection-only comparison.
- Manuscript Results and Discussion drafting.
