# Paper 2 final Q1-oriented synthesis checkpoint 001

## Executive summary

This synthesis consolidates the full Paper 2 experimental story after adding progressive drift readaptation and cost-sensitive utility analysis.

The main conclusion is not universal quantum superiority. The defensible claim is that QK-MMD provides regime-dependent drift monitoring advantages under moderate-to-severe drift and enables more efficient readaptation under progressive drift.

In single-change downstream adaptation, QK-MMD does not significantly improve absolute downstream accuracy over MMD-RBF because all detectors can trigger adaptation at similar points and then use the same SVC-RBF retraining loop.

In progressive drift, however, QK-MMD reaches comparable downstream performance with significantly fewer readaptations and significantly higher adaptation efficiency. A cost-sensitive utility analysis further shows that QK-MMD ZZ achieves higher net utility than MMD-RBF across meaningful readaptation-cost regions, despite higher detector runtime.

## What has been done

1. Synthetic/calibration smoke experiments for QK-MMD and MMD-RBF.
2. CICIDS2017 real-data drift experiments.
3. BENIGN-only temporal shift analysis.
4. Controlled streaming detection experiments across drift severities.
5. Adaptive monitor experiments.
6. Single-change downstream adaptation with SVC-RBF.
7. Detector-specific policy optimization.
8. Hybrid classical-quantum monitor experiments.
9. Geometry diagnostics linking detector behavior to downstream outcomes.
10. Statistical uncertainty summaries.
11. Runtime and cost-benefit analysis.
12. Operational-scale proxy analysis.
13. Long-stream downstream validation.
14. Progressive drift readaptation.
15. Cost-sensitive progressive utility analysis.

## Block 1: Controlled streaming detection

Controlled streaming is the strongest pure monitoring evidence. QK-MMD, especially PauliXZ and ZZ, improves pre/post drift AUC in moderate-to-severe regimes.

 severity         method  n_seeds  score_gap_mean  pre_post_auc_mean
     0.10      QK-MMD ZZ       30        0.000089           0.513167
     0.10 QK-MMD PauliXZ       30        0.000081           0.511417
     0.10        MMD-RBF       30        0.000078           0.494833
     0.25 QK-MMD PauliXZ       30        0.000183           0.548167
     0.25      QK-MMD ZZ       30        0.000184           0.546667
     0.25        MMD-RBF       30        0.000139           0.522417
     0.50 QK-MMD PauliXZ       30        0.000917           0.692333
     0.50      QK-MMD ZZ       30        0.000935           0.685833
     0.50        MMD-RBF       30        0.000692           0.619083
     0.75 QK-MMD PauliXZ       30        0.001610           0.811000
     0.75      QK-MMD ZZ       30        0.001617           0.798083
     0.75        MMD-RBF       30        0.001300           0.699083
     1.00 QK-MMD PauliXZ       30        0.002876           0.918167
     1.00      QK-MMD ZZ       30        0.002888           0.906917
     1.00        MMD-RBF       30        0.002328           0.800000

Interpretation: QK-MMD provides stronger drift-monitoring sensitivity in moderate-to-severe regimes, but this should not be phrased as universal earlier triggering.

## Block 2: Single-change downstream adaptation

Single-change downstream adaptation confirms that drift-triggered adaptation reduces degradation, but QK-MMD does not robustly outperform MMD-RBF in final downstream accuracy.

 severity                             strategy  post_balanced_accuracy_mean  degradation_area_mean  adaptation_gain_vs_no_adapt_mean  clean_downstream_adaptation_rate  clean_adaptation_gain_mean  false_alarm_any_rate
     0.10         mmd_rbf_triggered_adaptation                     0.919141               0.023997                          0.001901                          0.066667                    0.001068              0.033333
     0.10                        no_adaptation                     0.917240               0.025898                          0.000000                          0.000000                    0.000000              0.000000
     0.10                    oracle_adaptation                     0.940495               0.000000                          0.023255                          0.000000                    0.000000              0.000000
     0.10 qk_mmd_pauli_xz_triggered_adaptation                     0.918763               0.024375                          0.001523                          0.066667                    0.001029              0.066667
     0.10       qk_mmd_zz_triggered_adaptation                     0.919115               0.024023                          0.001875                          0.100000                    0.001380              0.066667
     0.25         mmd_rbf_triggered_adaptation                     0.904740               0.025091                          0.042995                          0.800000                    0.043711              0.000000
     0.25                        no_adaptation                     0.861745               0.068906                          0.000000                          0.000000                    0.000000              0.000000
     0.25                    oracle_adaptation                     0.929688               0.000000                          0.067943                          0.000000                    0.000000              0.000000
     0.25 qk_mmd_pauli_xz_triggered_adaptation                     0.885065               0.045586                          0.023320                          0.400000                    0.021211              0.033333
     0.25       qk_mmd_zz_triggered_adaptation                     0.884922               0.045729                          0.023177                          0.400000                    0.021068              0.033333
     0.50         mmd_rbf_triggered_adaptation                     0.893997               0.021380                          0.126706                          1.000000                    0.126706              0.000000
     0.50                        no_adaptation                     0.767292               0.148086                          0.000000                          0.000000                    0.000000              0.000000
     0.50                    oracle_adaptation                     0.915378               0.000000                          0.148086                          0.000000                    0.000000              0.000000
     0.50 qk_mmd_pauli_xz_triggered_adaptation                     0.892930               0.022448                          0.125638                          0.966667                    0.121497              0.033333
     0.50       qk_mmd_zz_triggered_adaptation                     0.892682               0.022695                          0.125391                          0.966667                    0.121250              0.033333
     0.75         mmd_rbf_triggered_adaptation                     0.872096               0.035339                          0.197370                          0.966667                    0.190794              0.033333
     0.75                        no_adaptation                     0.674727               0.232708                          0.000000                          0.000000                    0.000000              0.000000
     0.75                    oracle_adaptation                     0.907435               0.000000                          0.232708                          0.000000                    0.000000              0.000000
     0.75 qk_mmd_pauli_xz_triggered_adaptation                     0.872096               0.035339                          0.197370                          0.966667                    0.190872              0.033333
     0.75       qk_mmd_zz_triggered_adaptation                     0.872096               0.035339                          0.197370                          0.966667                    0.190872              0.033333
     1.00         mmd_rbf_triggered_adaptation                     0.849219               0.046888                          0.268411                          0.933333                    0.251120              0.066667
     1.00                        no_adaptation                     0.580807               0.315299                          0.000000                          0.000000                    0.000000              0.000000
     1.00                    oracle_adaptation                     0.896107               0.000000                          0.315299                          0.000000                    0.000000              0.000000
     1.00 qk_mmd_pauli_xz_triggered_adaptation                     0.849219               0.046888                          0.268411                          0.966667                    0.259648              0.033333
     1.00       qk_mmd_zz_triggered_adaptation                     0.849219               0.046888                          0.268411                          0.966667                    0.259648              0.033333

Main paired comparisons:

 experiment_block  severity                           strategy_a                           strategy_b       method_a       method_b                metric  n_pairs  mean_diff_a_minus_b  ci95_low  ci95_high  prob_diff_gt_0                                                                               interpretation
downstream_global      0.25                        no_adaptation         mmd_rbf_triggered_adaptation  No adaptation        MMD-RBF      degradation_area       30             0.043815  0.035260   0.051888        0.833333 Positive means no_adaptation has larger degradation area, so adaptation reduces degradation.
downstream_global      0.25                        no_adaptation       qk_mmd_zz_triggered_adaptation  No adaptation      QK-MMD ZZ      degradation_area       30             0.023177  0.013750   0.033047        0.433333 Positive means no_adaptation has larger degradation area, so adaptation reduces degradation.
downstream_global      0.25                        no_adaptation qk_mmd_pauli_xz_triggered_adaptation  No adaptation QK-MMD PauliXZ      degradation_area       30             0.023320  0.013711   0.033138        0.433333 Positive means no_adaptation has larger degradation area, so adaptation reduces degradation.
downstream_global      1.00                        no_adaptation         mmd_rbf_triggered_adaptation  No adaptation        MMD-RBF      degradation_area       30             0.268411  0.263581   0.274831        1.000000 Positive means no_adaptation has larger degradation area, so adaptation reduces degradation.
downstream_global      1.00                        no_adaptation       qk_mmd_zz_triggered_adaptation  No adaptation      QK-MMD ZZ      degradation_area       30             0.268411  0.263632   0.274858        1.000000 Positive means no_adaptation has larger degradation area, so adaptation reduces degradation.
downstream_global      1.00                        no_adaptation qk_mmd_pauli_xz_triggered_adaptation  No adaptation QK-MMD PauliXZ      degradation_area       30             0.268411  0.263437   0.275156        1.000000 Positive means no_adaptation has larger degradation area, so adaptation reduces degradation.
downstream_global      0.25         mmd_rbf_triggered_adaptation qk_mmd_pauli_xz_triggered_adaptation        MMD-RBF QK-MMD PauliXZ clean_adaptation_gain       30             0.022500  0.013099   0.031823        0.633333                            Positive means MMD-RBF has higher clean gain than QK-MMD PauliXZ.
downstream_global      0.25         mmd_rbf_triggered_adaptation       qk_mmd_zz_triggered_adaptation        MMD-RBF      QK-MMD ZZ clean_adaptation_gain       30             0.022643  0.012707   0.032097        0.633333                                 Positive means MMD-RBF has higher clean gain than QK-MMD ZZ.
downstream_global      1.00 qk_mmd_pauli_xz_triggered_adaptation         mmd_rbf_triggered_adaptation QK-MMD PauliXZ        MMD-RBF clean_adaptation_gain       30             0.008529 -0.017760   0.034818        0.066667                            Positive means QK-MMD PauliXZ has higher clean gain than MMD-RBF.
downstream_global      1.00       qk_mmd_zz_triggered_adaptation         mmd_rbf_triggered_adaptation      QK-MMD ZZ        MMD-RBF clean_adaptation_gain       30             0.008529 -0.017760   0.035052        0.066667                                 Positive means QK-MMD ZZ has higher clean gain than MMD-RBF.
  hybrid_selected      0.25       hybrid_or_triggered_adaptation         mmd_rbf_triggered_adaptation      Hybrid OR        MMD-RBF clean_adaptation_gain       30             0.001615 -0.001107   0.005209        0.166667                                 Positive means Hybrid OR has higher clean gain than MMD-RBF.
  hybrid_selected      1.00 qk_mmd_pauli_xz_triggered_adaptation       hybrid_or_triggered_adaptation QK-MMD PauliXZ      Hybrid OR clean_adaptation_gain       30             0.026107  0.000000   0.060273        0.100000                          Positive means QK-MMD PauliXZ has higher clean gain than Hybrid OR.

Interpretation: adaptation itself is valuable, but single-change downstream experiments do not support a strong QK-MMD downstream-superiority claim.

## Block 3: Geometry diagnostics

Geometry diagnostics explain why the behavior is regime-dependent: MMD-RBF is stronger in low/moderate drift, while QK-MMD has stronger severe-drift post-alarm persistence.

 severity         method  score_ratio_gap_post_minus_pre  alarm_rate_post  clean_downstream_adaptation_rate  clean_adaptation_gain_mean  false_alarm_any_rate
     0.25        MMD-RBF                        0.029978         0.113333                          0.800000                    0.043711              0.000000
     0.25 QK-MMD PauliXZ                        0.017300         0.116667                          0.400000                    0.021211              0.033333
     0.25      QK-MMD ZZ                        0.018347         0.113333                          0.400000                    0.021068              0.033333
     1.00        MMD-RBF                        0.447046         0.420000                          0.933333                    0.251120              0.066667
     1.00 QK-MMD PauliXZ                        0.341269         0.756667                          0.966667                    0.259648              0.033333
     1.00      QK-MMD ZZ                        0.343131         0.726667                          0.966667                    0.259648              0.033333

## Block 4: Long-stream validation

The long-stream experiment validates that when MMD-RBF and QK-MMD trigger in the same window, downstream metrics become identical because the same adaptation mechanism is used.

 severity            method  n_seeds  post_balanced_accuracy_mean  degradation_area_mean  adaptation_gain_vs_no_adapt_mean  clean_downstream_adaptation_rate  clean_adaptation_gain_mean  triggered_post_rate  false_alarm_any_rate  trigger_delay_windows_mean
     0.75           MMD-RBF       30                     0.899609               0.006971                          0.224336                          0.966667                    0.216862                  1.0              0.033333                         2.0
     0.75     No adaptation       30                     0.675273               0.231307                          0.000000                          0.000000                    0.000000                  0.0              0.000000                         NaN
     0.75 Oracle adaptation       30                     0.906581               0.000000                          0.231307                          0.000000                    0.000000                  1.0              0.000000                         0.0
     0.75    QK-MMD PauliXZ       30                     0.899609               0.006971                          0.224336                          0.933333                    0.209687                  1.0              0.066667                         2.0
     0.75         QK-MMD ZZ       30                     0.899609               0.006971                          0.224336                          0.933333                    0.209687                  1.0              0.066667                         2.0
     1.00           MMD-RBF       30                     0.888430               0.009562                          0.306607                          1.000000                    0.306607                  1.0              0.000000                         2.0
     1.00     No adaptation       30                     0.581823               0.316169                          0.000000                          0.000000                    0.000000                  0.0              0.000000                         NaN
     1.00 Oracle adaptation       30                     0.897992               0.000000                          0.316169                          0.000000                    0.000000                  1.0              0.000000                         0.0
     1.00    QK-MMD PauliXZ       30                     0.888430               0.009562                          0.306607                          1.000000                    0.306607                  1.0              0.000000                         2.0
     1.00         QK-MMD ZZ       30                     0.888430               0.009562                          0.306607                          1.000000                    0.306607                  1.0              0.000000                         2.0

Interpretation: QK-MMD's value is not final retrained accuracy under a fixed single-change trigger; it lies in monitoring coverage and adaptation scheduling.

## Block 5: Progressive drift readaptation

Progressive drift models a more realistic scenario in which drift evolves over time and the system can readapt multiple times.

  method_label  n_seeds  mean_balanced_accuracy  cumulative_error_area_mean  cumulative_gain_vs_no_adapt_mean  adaptation_efficiency_mean  adaptation_efficiency_std  n_adaptations_mean  false_adaptations_mean  first_adaptation_window_mean  detector_runtime_sec_total_mean
       MMD-RBF       30                0.874219                   12.578125                         14.674479                    3.345352                   0.704585            4.433333                     0.0                     17.900000                         1.857428
 No adaptation       30                0.727474                   27.252604                          0.000000                         NaN                        NaN            0.000000                     0.0                           NaN                         0.000000
QK-MMD PauliXZ       30                0.878063                   12.193750                         15.058854                    4.609310                   0.872313            3.333333                     0.0                     24.166667                         6.410877
     QK-MMD ZZ       30                0.880297                   11.970313                         15.282292                    4.708746                   0.910133            3.333333                     0.0                     24.266667                         5.986702

Progressive paired comparisons:

      method_a       method_b                      metric  n_pairs  mean_diff_a_minus_b  ci95_low  ci95_high  prob_diff_gt_0         positive_means
     QK-MMD ZZ        MMD-RBF      mean_balanced_accuracy       30             0.006078 -0.001544   0.015383        0.466667              QK better
       MMD-RBF      QK-MMD ZZ       cumulative_error_area       30             0.607812 -0.154440   1.538281        0.466667              QK better
     QK-MMD ZZ        MMD-RBF cumulative_gain_vs_no_adapt       30             0.607812 -0.154440   1.538281        0.466667              QK better
       MMD-RBF      QK-MMD ZZ               n_adaptations       30             1.100000  0.833333   1.366667        0.800000 QK fewer readaptations
     QK-MMD ZZ        MMD-RBF  detector_runtime_sec_total       30             4.129274  4.077078   4.180054        1.000000      QK more expensive
QK-MMD PauliXZ        MMD-RBF      mean_balanced_accuracy       30             0.003844 -0.005724   0.014055        0.433333              QK better
       MMD-RBF QK-MMD PauliXZ       cumulative_error_area       30             0.384375 -0.572428   1.405495        0.433333              QK better
QK-MMD PauliXZ        MMD-RBF cumulative_gain_vs_no_adapt       30             0.384375 -0.572428   1.405495        0.433333              QK better
       MMD-RBF QK-MMD PauliXZ               n_adaptations       30             1.100000  0.833333   1.366667        0.800000 QK fewer readaptations
QK-MMD PauliXZ        MMD-RBF  detector_runtime_sec_total       30             4.553449  4.493515   4.611672        1.000000      QK more expensive

Interpretation: QK-MMD does not significantly improve absolute balanced accuracy, but it requires significantly fewer readaptations and achieves significantly higher adaptation efficiency.

## Block 6: Cost-sensitive utility

The cost-sensitive utility analysis formalizes why fewer readaptations matter. The utility is defined as:

`utility = cumulative_gain_vs_no_adapt - lambda * n_adaptations - gamma * detector_runtime_sec_total`

Strict positive utility regions:

        method  lambda_adaptation_cost  gamma_runtime_cost  mean_utility_diff_qk_minus_mmd  ci95_low  ci95_high  prob_diff_gt_0  qk_utility_better_ci95
     QK-MMD ZZ                    0.25                0.00                        0.882812  0.132546   1.797676        0.533333                    True
     QK-MMD ZZ                    0.25                0.01                        0.841520  0.091464   1.756290        0.533333                    True
     QK-MMD ZZ                    0.50                0.00                        1.157812  0.409368   2.057298        0.733333                    True
     QK-MMD ZZ                    0.50                0.01                        1.116520  0.368205   2.015667        0.700000                    True
     QK-MMD ZZ                    0.50                0.05                        0.951349  0.203146   1.850596        0.633333                    True
     QK-MMD ZZ                    0.75                0.00                        1.432813  0.687760   2.315638        0.800000                    True
     QK-MMD ZZ                    0.75                0.01                        1.391520  0.646704   2.274217        0.800000                    True
     QK-MMD ZZ                    0.75                0.05                        1.226349  0.481808   2.108469        0.733333                    True
     QK-MMD ZZ                    0.75                0.10                        1.019885  0.275077   1.901397        0.700000                    True
     QK-MMD ZZ                    1.00                0.00                        1.707812  0.957812   2.582292        0.833333                    True
     QK-MMD ZZ                    1.00                0.01                        1.666520  0.917007   2.540802        0.833333                    True
     QK-MMD ZZ                    1.00                0.05                        1.501349  0.751519   2.374842        0.833333                    True
     QK-MMD ZZ                    1.00                0.10                        1.294885  0.545421   2.167913        0.766667                    True
     QK-MMD ZZ                    1.50                0.00                        2.257812  1.495046   3.128392        0.900000                    True
     QK-MMD ZZ                    1.50                0.01                        2.216520  1.453962   3.087249        0.900000                    True
     QK-MMD ZZ                    1.50                0.05                        2.051349  1.287539   2.922106        0.900000                    True
     QK-MMD ZZ                    1.50                0.10                        1.844885  1.080972   2.715655        0.866667                    True
     QK-MMD ZZ                    1.50                0.25                        1.225494  0.460152   2.096512        0.700000                    True
     QK-MMD ZZ                    2.00                0.00                        2.807812  1.997910   3.680475        0.900000                    True
     QK-MMD ZZ                    2.00                0.01                        2.766520  1.956375   3.639238        0.900000                    True
     QK-MMD ZZ                    2.00                0.05                        2.601349  1.790500   3.473997        0.900000                    True
     QK-MMD ZZ                    2.00                0.10                        2.394885  1.582536   3.266278        0.900000                    True
     QK-MMD ZZ                    2.00                0.25                        1.775494  0.961890   2.643722        0.833333                    True
QK-MMD PauliXZ                    0.75                0.00                        1.209375  0.250000   2.198490        0.766667                    True
QK-MMD PauliXZ                    0.75                0.01                        1.163841  0.204227   2.152537        0.766667                    True
QK-MMD PauliXZ                    0.75                0.05                        0.981703  0.022303   1.971639        0.733333                    True
QK-MMD PauliXZ                    1.00                0.00                        1.484375  0.515885   2.477096        0.766667                    True
QK-MMD PauliXZ                    1.00                0.01                        1.438841  0.470152   2.431643        0.766667                    True
QK-MMD PauliXZ                    1.00                0.05                        1.256703  0.287233   2.249524        0.766667                    True
QK-MMD PauliXZ                    1.00                0.10                        1.029030  0.059619   2.020385        0.733333                    True
QK-MMD PauliXZ                    1.50                0.00                        2.034375  1.034115   3.037500        0.766667                    True
QK-MMD PauliXZ                    1.50                0.01                        1.988841  0.988498   2.991692        0.766667                    True
QK-MMD PauliXZ                    1.50                0.05                        1.806703  0.805985   2.809575        0.766667                    True
QK-MMD PauliXZ                    1.50                0.10                        1.579030  0.577957   2.582432        0.766667                    True
QK-MMD PauliXZ                    2.00                0.00                        2.584375  1.537474   3.615905        0.833333                    True
QK-MMD PauliXZ                    2.00                0.01                        2.538841  1.491615   3.570210        0.833333                    True
QK-MMD PauliXZ                    2.00                0.05                        2.356703  1.309094   3.386130        0.800000                    True
QK-MMD PauliXZ                    2.00                0.10                        2.129030  1.079743   3.156817        0.766667                    True
QK-MMD PauliXZ                    2.00                0.25                        1.446013  0.396287   2.472348        0.733333                    True

Break-even lambda values:

        method  gamma_runtime_cost  mean_gain_delta_qk_minus_mmd  mean_adaptation_saving_vs_mmd  mean_runtime_extra_vs_mmd  lambda_break_even_raw  lambda_break_even_nonnegative
     QK-MMD ZZ                0.00                      0.607812                            1.1                   4.129274              -0.552557                       0.000000
     QK-MMD ZZ                0.01                      0.607812                            1.1                   4.129274              -0.515018                       0.000000
     QK-MMD ZZ                0.05                      0.607812                            1.1                   4.129274              -0.364863                       0.000000
     QK-MMD ZZ                0.10                      0.607812                            1.1                   4.129274              -0.177168                       0.000000
     QK-MMD ZZ                0.25                      0.607812                            1.1                   4.129274               0.385915                       0.385915
     QK-MMD ZZ                0.50                      0.607812                            1.1                   4.129274               1.324386                       1.324386
     QK-MMD ZZ                1.00                      0.607812                            1.1                   4.129274               3.201329                       3.201329
QK-MMD PauliXZ                0.00                      0.384375                            1.1                   4.553449              -0.349432                       0.000000
QK-MMD PauliXZ                0.01                      0.384375                            1.1                   4.553449              -0.308037                       0.000000
QK-MMD PauliXZ                0.05                      0.384375                            1.1                   4.553449              -0.142457                       0.000000
QK-MMD PauliXZ                0.10                      0.384375                            1.1                   4.553449               0.064518                       0.064518
QK-MMD PauliXZ                0.25                      0.384375                            1.1                   4.553449               0.685443                       0.685443
QK-MMD PauliXZ                0.50                      0.384375                            1.1                   4.553449               1.720318                       1.720318
QK-MMD PauliXZ                1.00                      0.384375                            1.1                   4.553449               3.790067                       3.790067

Interpretation: QK-MMD ZZ obtains higher net utility than MMD-RBF across meaningful readaptation-cost regions. PauliXZ is also positive, but requires higher adaptation cost to overcome runtime penalties.

## Block 7: Runtime/cost

QK-MMD is more expensive than MMD-RBF. The paper must state this explicitly.

 severity         method  detector_runtime_sec_mean  mmd_runtime_sec_mean  runtime_ratio_vs_mmd  extra_runtime_sec_vs_mmd  clean_gain_delta_vs_mmd  false_alarm_delta_vs_mmd  trigger_delay_delta_vs_mmd
     0.10        MMD-RBF                   0.247183              0.247183              1.000000                  0.000000                 0.000000                  0.000000                    0.000000
     0.10 QK-MMD PauliXZ                   0.752132              0.247183              3.042808                  0.504949                -0.000039                  0.033333                    3.000000
     0.10      QK-MMD ZZ                   0.734601              0.247183              2.971886                  0.487418                 0.000312                  0.033333                    3.833333
     0.25        MMD-RBF                   0.246317              0.246317              1.000000                  0.000000                 0.000000                  0.000000                    0.000000
     0.25 QK-MMD PauliXZ                   0.752676              0.246317              3.055716                  0.506358                -0.022500                  0.033333                    0.473846
     0.25      QK-MMD ZZ                   0.729740              0.246317              2.962603                  0.483423                -0.022643                  0.033333                    0.550769
     0.50        MMD-RBF                   0.245229              0.245229              1.000000                  0.000000                 0.000000                  0.000000                    0.000000
     0.50 QK-MMD PauliXZ                   0.752046              0.245229              3.066714                  0.506818                -0.005208                  0.033333                    0.133333
     0.50      QK-MMD ZZ                   0.726707              0.245229              2.963383                  0.481478                -0.005456                  0.033333                    0.166667
     0.75        MMD-RBF                   0.238829              0.238829              1.000000                  0.000000                 0.000000                  0.000000                    0.000000
     0.75 QK-MMD PauliXZ                   0.748929              0.238829              3.135842                  0.510100                 0.000078                  0.000000                    0.000000
     0.75      QK-MMD ZZ                   0.731292              0.238829              3.061993                  0.492463                 0.000078                  0.000000                    0.000000
     1.00        MMD-RBF                   0.236456              0.236456              1.000000                  0.000000                 0.000000                  0.000000                    0.000000
     1.00 QK-MMD PauliXZ                   0.755854              0.236456              3.196596                  0.519398                 0.008529                 -0.033333                    0.000000
     1.00      QK-MMD ZZ                   0.734917              0.236456              3.108049                  0.498461                 0.008529                 -0.033333                    0.000000

Interpretation: the QK-MMD result is a trade-off: higher monitoring cost in exchange for fewer readaptations and higher utility when adaptation is costly.

## Claims supported

1. Drift-triggered adaptation reduces downstream degradation relative to no adaptation.
2. QK-MMD provides stronger monitoring sensitivity under moderate-to-severe drift.
3. QK-MMD provides stronger severe-drift post-alarm persistence.
4. QK-MMD does not universally dominate MMD-RBF.
5. QK-MMD does not significantly improve absolute downstream accuracy under single-change drift.
6. Under progressive drift, QK-MMD achieves comparable downstream performance with significantly fewer readaptations.
7. Under progressive drift, QK-MMD achieves significantly higher adaptation efficiency.
8. Under cost-sensitive utility, QK-MMD ZZ achieves higher net utility than MMD-RBF across meaningful readaptation-cost regions.

## Claims not supported

1. Universal quantum advantage.
2. Universal QK-MMD superiority over MMD-RBF.
3. QK-MMD always detects earlier than MMD-RBF.
4. QK-MMD significantly improves final downstream accuracy in all regimes.
5. Hybrid classical-quantum monitoring universally improves over the best individual detector.

## Final recommended narrative

The final narrative should be: QK-MMD provides regime-dependent drift geometry for adaptive IDS monitoring. It is not universally better than MMD-RBF and does not reliably improve final accuracy under a single retraining event. However, it provides stronger monitoring signals under moderate-to-severe drift and, under progressive drift, supports more efficient readaptation. When readaptation cost is explicitly modeled, QK-MMD ZZ achieves higher net utility than MMD-RBF in meaningful cost regimes.

## Q1 assessment

The paper is now stronger than a simple QK-vs-classical detector comparison. It can plausibly target Q1 venues if framed around calibrated monitoring, progressive drift readaptation, and cost-sensitive operational utility. It should not be framed as broad quantum advantage.

The remaining main risks are: single primary dataset, simulated quantum kernels, higher QK runtime, lack of statistically significant absolute accuracy gains, and limited classical detector diversity beyond MMD-RBF.

## Recommended next step

No further large experiments are recommended before drafting. The next step is to update the paper structure and start drafting Results and Discussion around the regime-dependent monitoring and cost-sensitive adaptation-efficiency claim.
