# Paper 2 progressive utility analysis checkpoint 001

## Purpose

This analysis converts the progressive readaptation result into a cost-sensitive
operational utility comparison.

The utility is defined as:

`utility = cumulative_gain_vs_no_adapt - lambda * n_adaptations - gamma * detector_runtime_sec_total`

where `lambda` is the cost of each readaptation and `gamma` is the cost of
monitoring runtime.

## Motivation

The progressive drift experiment showed that QK-MMD does not significantly
improve absolute balanced accuracy over MMD-RBF, but it does achieve comparable
performance with significantly fewer readaptations and significantly higher
gain per readaptation.

This analysis tests whether that efficiency translates into higher net utility
when readaptations have nonzero operational cost.

## Representative utility grid

        method  lambda_adaptation_cost  gamma_runtime_cost  mean_utility_diff_qk_minus_mmd  ci95_low  ci95_high  prob_diff_gt_0  qk_utility_better_ci95
     QK-MMD ZZ                    0.00                0.00                        0.607812 -0.154440   1.538281        0.466667                   False
     QK-MMD ZZ                    0.00                0.05                        0.401349 -0.360565   1.330812        0.466667                   False
     QK-MMD ZZ                    0.00                0.10                        0.194885 -0.567527   1.123577        0.433333                   False
     QK-MMD ZZ                    0.25                0.00                        0.882812  0.132546   1.797676        0.533333                    True
     QK-MMD ZZ                    0.25                0.05                        0.676349 -0.072842   1.591635        0.466667                   False
     QK-MMD ZZ                    0.25                0.10                        0.469885 -0.278585   1.384885        0.466667                   False
     QK-MMD ZZ                    0.50                0.00                        1.157812  0.409368   2.057298        0.733333                    True
     QK-MMD ZZ                    0.50                0.05                        0.951349  0.203146   1.850596        0.633333                    True
     QK-MMD ZZ                    0.50                0.10                        0.744885 -0.002817   1.643250        0.600000                   False
     QK-MMD ZZ                    1.00                0.00                        1.707812  0.957812   2.582292        0.833333                    True
     QK-MMD ZZ                    1.00                0.05                        1.501349  0.751519   2.374842        0.833333                    True
     QK-MMD ZZ                    1.00                0.10                        1.294885  0.545421   2.167913        0.766667                    True
QK-MMD PauliXZ                    0.00                0.00                        0.384375 -0.572428   1.405495        0.433333                   False
QK-MMD PauliXZ                    0.00                0.05                        0.156703 -0.802157   1.177187        0.433333                   False
QK-MMD PauliXZ                    0.00                0.10                       -0.070970 -1.030310   0.948979        0.366667                   False
QK-MMD PauliXZ                    0.25                0.00                        0.659375 -0.297409   1.660684        0.600000                   False
QK-MMD PauliXZ                    0.25                0.05                        0.431703 -0.524165   1.433435        0.466667                   False
QK-MMD PauliXZ                    0.25                0.10                        0.204030 -0.751939   1.206023        0.433333                   False
QK-MMD PauliXZ                    0.50                0.00                        0.934375 -0.025280   1.925521        0.733333                   False
QK-MMD PauliXZ                    0.50                0.05                        0.706703 -0.254866   1.699146        0.700000                   False
QK-MMD PauliXZ                    0.50                0.10                        0.479030 -0.483967   1.472710        0.566667                   False
QK-MMD PauliXZ                    1.00                0.00                        1.484375  0.515885   2.477096        0.766667                    True
QK-MMD PauliXZ                    1.00                0.05                        1.256703  0.287233   2.249524        0.766667                    True
QK-MMD PauliXZ                    1.00                0.10                        1.029030  0.059619   2.020385        0.733333                    True

## Strict positive utility regions

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

## Break-even lambda by runtime cost

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

## Interpretation

- If `lambda = 0`, the comparison reduces mostly to cumulative gain minus runtime cost.
- As `lambda` increases, fewer readaptations become operationally valuable.
- A strict positive CI95 lower bound means QK-MMD has higher utility than MMD-RBF under that cost setting.
- This should be presented as a cost-sensitive operational analysis, not as universal accuracy superiority.

## Generated artifacts

- `results\tables\paper2_progressive_utility_analysis_001\paper_table_progressive_utility_grid.csv`
- `results\tables\paper2_progressive_utility_analysis_001\paper_table_progressive_utility_strict_positive.csv`
- `results\tables\paper2_progressive_utility_analysis_001\paper_table_progressive_utility_break_even.csv`
- `results\figures\paper2_progressive_utility_analysis_001`
