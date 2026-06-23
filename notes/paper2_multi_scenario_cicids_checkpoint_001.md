# Paper 2 multi-scenario CICIDS progressive drift checkpoint 001

## Purpose

This checkpoint consolidates the progressive readaptation results across three CICIDS2017 regimes:

- Tuesday -> Wednesday
- Tuesday -> Friday PortScan
- Tuesday -> Friday DDoS

## Multi-scenario summary

 scenario    method_label  n_seeds  mean_balanced_accuracy  cumulative_error_area_mean  cumulative_gain_vs_no_adapt_mean  n_adaptations_mean  adaptation_efficiency_mean  detector_runtime_sec_total_mean
     DDoS       QK-MMD ZZ       30                0.893271                   10.672917                         19.496875            3.600000                    5.531654                         6.070541
     DDoS Energy distance       30                0.891417                   10.858333                         19.311458            5.433333                    3.595795                         0.040211
     DDoS             JSD       30                0.890026                   10.997396                         19.172396            4.166667                    4.760082                         0.014318
     DDoS         MMD-RBF       30                0.885495                   11.450521                         18.719271            4.366667                    4.387409                         1.857102
     DDoS          KS-max       30                0.884146                   11.585417                         18.584375            3.833333                    4.938841                         0.156981
 PortScan       QK-MMD ZZ       30                0.939115                    6.088542                          6.203906            4.066667                    1.544783                         6.113158
 PortScan Energy distance       30                0.932669                    6.733073                          5.559375            2.700000                    2.122678                         0.055530
 PortScan          KS-max       30                0.932557                    6.744271                          5.548177            3.333333                    1.667687                         0.199714
 PortScan             JSD       30                0.922977                    7.702344                          4.590104            3.866667                    1.196289                         0.021419
 PortScan         MMD-RBF       30                0.906477                    9.352344                          2.940104            2.500000                    1.064193                         1.658449
Wednesday       QK-MMD ZZ       30                0.884826                   11.517448                         11.889323            3.166667                    3.880794                         6.048713
Wednesday Energy distance       30                0.884724                   11.527604                         11.879167            5.266667                    2.328859                         0.053273
Wednesday             JSD       30                0.880992                   11.900781                         11.505990            3.600000                    3.282682                         0.021458
Wednesday         MMD-RBF       30                0.879904                   12.009635                         11.397135            4.100000                    2.806254                         1.638038
Wednesday          KS-max       30                0.877216                   12.278385                         11.128385            3.466667                    3.264175                         0.202530

## QK-MMD ZZ vs Energy distance paired comparisons

 scenario        method_a        method_b                      metric  n_pairs  mean_diff_a_minus_b  ci95_low  ci95_high  prob_diff_gt_0                         positive_means  ci_excludes_zero_positive
Wednesday       QK-MMD ZZ Energy distance      mean_balanced_accuracy       30             0.000102 -0.005654   0.006521        0.400000              QK-MMD ZZ better accuracy                      False
Wednesday Energy distance       QK-MMD ZZ       cumulative_error_area       30             0.010156 -0.565404   0.652109        0.400000            QK-MMD ZZ lower degradation                      False
Wednesday       QK-MMD ZZ Energy distance cumulative_gain_vs_no_adapt       30             0.010156 -0.565404   0.652109        0.400000                  QK-MMD ZZ higher gain                      False
Wednesday Energy distance       QK-MMD ZZ               n_adaptations       30             2.100000  1.733333   2.433333        0.966667          QK-MMD ZZ fewer readaptations                       True
Wednesday       QK-MMD ZZ Energy distance       adaptation_efficiency       30             1.551936  1.168571   1.955149        0.966667 QK-MMD ZZ better adaptation efficiency                       True
Wednesday       QK-MMD ZZ Energy distance  detector_runtime_sec_total       30             5.995440  5.917411   6.076280        1.000000               QK-MMD ZZ more expensive                       True
 PortScan       QK-MMD ZZ Energy distance      mean_balanced_accuracy       30             0.006445  0.001174   0.013482        0.700000              QK-MMD ZZ better accuracy                       True
 PortScan Energy distance       QK-MMD ZZ       cumulative_error_area       30             0.644531  0.117435   1.348210        0.700000            QK-MMD ZZ lower degradation                       True
 PortScan       QK-MMD ZZ Energy distance cumulative_gain_vs_no_adapt       30             0.644531  0.117435   1.348210        0.700000                  QK-MMD ZZ higher gain                       True
 PortScan Energy distance       QK-MMD ZZ               n_adaptations       30            -1.366667 -1.633333  -1.100000        0.033333          QK-MMD ZZ fewer readaptations                      False
 PortScan       QK-MMD ZZ Energy distance       adaptation_efficiency       30            -0.577895 -0.917058  -0.227857        0.233333 QK-MMD ZZ better adaptation efficiency                      False
 PortScan       QK-MMD ZZ Energy distance  detector_runtime_sec_total       30             6.057628  6.007582   6.113502        1.000000               QK-MMD ZZ more expensive                       True
     DDoS       QK-MMD ZZ Energy distance      mean_balanced_accuracy       30             0.001854 -0.005435   0.009203        0.600000              QK-MMD ZZ better accuracy                      False
     DDoS Energy distance       QK-MMD ZZ       cumulative_error_area       30             0.185417 -0.543496   0.920312        0.600000            QK-MMD ZZ lower degradation                      False
     DDoS       QK-MMD ZZ Energy distance cumulative_gain_vs_no_adapt       30             0.185417 -0.543496   0.920312        0.600000                  QK-MMD ZZ higher gain                      False
     DDoS Energy distance       QK-MMD ZZ               n_adaptations       30             1.833333  1.533333   2.133333        0.966667          QK-MMD ZZ fewer readaptations                       True
     DDoS       QK-MMD ZZ Energy distance       adaptation_efficiency       30             1.935859  1.596164   2.300397        1.000000 QK-MMD ZZ better adaptation efficiency                       True
     DDoS       QK-MMD ZZ Energy distance  detector_runtime_sec_total       30             6.030330  5.959551   6.099601        1.000000               QK-MMD ZZ more expensive                       True

## Strict positive utility regions

 scenario        baseline  lambda_cost  gamma_cost  mean_utility_diff_qk_minus_baseline  ci95_low  ci95_high  prob_diff_gt_0  qk_better_ci95
Wednesday          KS-max         0.25        0.00                             0.835938  0.056504   1.934388        0.633333            True
Wednesday         MMD-RBF         0.25        0.00                             0.725521  0.076276   1.527350        0.533333            True
Wednesday         MMD-RBF         0.25        0.01                             0.681414  0.032122   1.483351        0.533333            True
Wednesday Energy distance         0.50        0.00                             1.060156  0.415605   1.759388        0.700000            True
Wednesday          KS-max         0.50        0.00                             0.910937  0.152077   1.983646        0.633333            True
Wednesday         MMD-RBF         0.50        0.00                             0.958854  0.307526   1.752350        0.600000            True
Wednesday Energy distance         0.50        0.01                             1.000202  0.355457   1.699921        0.700000            True
Wednesday          KS-max         0.50        0.01                             0.852476  0.093174   1.925460        0.600000            True
Wednesday         MMD-RBF         0.50        0.01                             0.914747  0.263243   1.707483        0.600000            True
Wednesday Energy distance         0.50        0.05                             0.760384  0.115562   1.461245        0.700000            True
Wednesday         MMD-RBF         0.50        0.05                             0.738320  0.086651   1.531136        0.533333            True
Wednesday Energy distance         1.00        0.00                             2.110156  1.350514   2.884648        0.900000            True
Wednesday             JSD         1.00        0.00                             0.816667  0.095046   1.768750        0.700000            True
Wednesday          KS-max         1.00        0.00                             1.060938  0.316406   2.094805        0.700000            True
Wednesday         MMD-RBF         1.00        0.00                             1.425521  0.746328   2.219277        0.800000            True
Wednesday Energy distance         1.00        0.01                             2.050202  1.290179   2.824913        0.866667            True
Wednesday             JSD         1.00        0.01                             0.756394  0.034950   1.708562        0.700000            True
Wednesday          KS-max         1.00        0.01                             1.002476  0.258170   2.036559        0.666667            True
Wednesday         MMD-RBF         1.00        0.01                             1.381414  0.701790   2.175141        0.800000            True
Wednesday Energy distance         1.00        0.05                             1.810384  1.048911   2.585989        0.866667            True
Wednesday          KS-max         1.00        0.05                             0.768628  0.024372   1.801517        0.666667            True
Wednesday         MMD-RBF         1.00        0.05                             1.204987  0.523658   1.997479        0.700000            True
Wednesday Energy distance         1.00        0.10                             1.510612  0.747366   2.287248        0.800000            True
Wednesday         MMD-RBF         1.00        0.10                             0.984453  0.303707   1.776199        0.633333            True
Wednesday Energy distance         2.00        0.00                             4.210156  3.167402   5.198451        0.966667            True
Wednesday             JSD         2.00        0.00                             1.250000  0.385671   2.310716        0.733333            True
Wednesday          KS-max         2.00        0.00                             1.360937  0.564811   2.345586        0.700000            True
Wednesday         MMD-RBF         2.00        0.00                             2.358854  1.543991   3.237513        0.800000            True
Wednesday Energy distance         2.00        0.01                             4.150202  3.106775   5.138724        0.966667            True
Wednesday             JSD         2.00        0.01                             1.189727  0.325056   2.250118        0.733333            True
Wednesday          KS-max         2.00        0.01                             1.302476  0.506257   2.287423        0.666667            True
Wednesday         MMD-RBF         2.00        0.01                             2.314747  1.499488   3.193947        0.800000            True
Wednesday Energy distance         2.00        0.05                             3.910384  2.865580   4.898956        0.933333            True
Wednesday             JSD         2.00        0.05                             0.948637  0.083431   2.009584        0.700000            True
Wednesday          KS-max         2.00        0.05                             1.068628  0.272070   2.053280        0.666667            True
Wednesday         MMD-RBF         2.00        0.05                             2.138320  1.321475   3.017820        0.766667            True
Wednesday Energy distance         2.00        0.10                             3.610612  2.563389   4.599411        0.933333            True
Wednesday         MMD-RBF         2.00        0.10                             1.917787  1.101831   2.796624        0.766667            True
Wednesday Energy distance         2.00        0.25                             2.711296  1.659171   3.702799        0.866667            True
Wednesday         MMD-RBF         2.00        0.25                             1.256185  0.440599   2.131691        0.766667            True
 PortScan Energy distance         0.00        0.00                             0.644531  0.117435   1.348210        0.700000            True
 PortScan             JSD         0.00        0.00                             1.613802  0.457799   3.020599        0.733333            True
 PortScan          KS-max         0.00        0.00                             0.655729  0.098158   1.510443        0.700000            True
 PortScan         MMD-RBF         0.00        0.00                             3.263802  1.386712   5.558346        0.800000            True
 PortScan  QK-MMD PauliXZ         0.00        0.00                             0.834635  0.051556   1.910944        0.566667            True
 PortScan Energy distance         0.00        0.01                             0.583955  0.057007   1.287933        0.666667            True
 PortScan             JSD         0.00        0.01                             1.552885  0.397014   2.959088        0.666667            True
 PortScan          KS-max         0.00        0.01                             0.596595  0.039450   1.451309        0.666667            True
 PortScan         MMD-RBF         0.00        0.01                             3.219255  1.342174   5.513976        0.800000            True
 PortScan  QK-MMD PauliXZ         0.00        0.01                             0.837559  0.054350   1.913959        0.566667            True
 PortScan             JSD         0.00        0.05                             1.309215  0.154943   2.715396        0.500000            True
 PortScan         MMD-RBF         0.00        0.05                             3.041067  1.164417   5.336317        0.733333            True
 PortScan  QK-MMD PauliXZ         0.00        0.05                             0.849255  0.065760   1.925047        0.566667            True
 PortScan         MMD-RBF         0.00        0.10                             2.818331  0.943259   5.113792        0.633333            True
 PortScan  QK-MMD PauliXZ         0.00        0.10                             0.863875  0.080209   1.939284        0.566667            True
 PortScan         MMD-RBF         0.00        0.25                             2.150125  0.270913   4.446674        0.466667            True
 PortScan  QK-MMD PauliXZ         0.00        0.25                             0.907734  0.125164   1.984459        0.566667            True
 PortScan             JSD         0.10        0.00                             1.593802  0.431030   3.007270        0.700000            True
 PortScan          KS-max         0.10        0.00                             0.582396  0.032909   1.424487        0.633333            True
 PortScan         MMD-RBF         0.10        0.00                             3.107135  1.232957   5.401147        0.766667            True
 PortScan  QK-MMD PauliXZ         0.10        0.00                             0.844635  0.061712   1.912475        0.566667            True
 PortScan             JSD         0.10        0.01                             1.532885  0.369878   2.945754        0.666667            True
 PortScan         MMD-RBF         0.10        0.01                             3.062588  1.188157   5.356485        0.766667            True
 PortScan  QK-MMD PauliXZ         0.10        0.01                             0.847559  0.064523   1.915494        0.566667            True
 PortScan             JSD         0.10        0.05                             1.289215  0.125270   2.701595        0.500000            True
 PortScan         MMD-RBF         0.10        0.05                             2.884400  1.008996   5.178020        0.666667            True
 PortScan  QK-MMD PauliXZ         0.10        0.05                             0.859255  0.076221   1.927569        0.566667            True
 PortScan         MMD-RBF         0.10        0.10                             2.661664  0.785096   4.955006        0.600000            True
 PortScan  QK-MMD PauliXZ         0.10        0.10                             0.873875  0.090946   1.942653        0.566667            True
 PortScan         MMD-RBF         0.10        0.25                             1.993458  0.114241   4.289274        0.400000            True
 PortScan  QK-MMD PauliXZ         0.10        0.25                             0.917734  0.135535   1.990203        0.566667            True
 PortScan             JSD         0.25        0.00                             1.563802  0.390612   2.986198        0.666667            True
 PortScan         MMD-RBF         0.25        0.00                             2.872135  0.994010   5.166940        0.666667            True
 PortScan  QK-MMD PauliXZ         0.25        0.00                             0.859635  0.078626   1.921628        0.566667            True
 PortScan             JSD         0.25        0.01                             1.502885  0.330058   2.924882        0.633333            True
 PortScan         MMD-RBF         0.25        0.01                             2.827588  0.949170   5.122731        0.633333            True
 PortScan  QK-MMD PauliXZ         0.25        0.01                             0.862559  0.081555   1.924899        0.566667            True
 PortScan             JSD         0.25        0.05                             1.259215  0.087746   2.679953        0.466667            True
 PortScan         MMD-RBF         0.25        0.05                             2.649400  0.769821   4.944545        0.600000            True
 PortScan  QK-MMD PauliXZ         0.25        0.05                             0.874255  0.093451   1.936266        0.566667            True
 PortScan         MMD-RBF         0.25        0.10                             2.426664  0.545578   4.721655        0.500000            True
 PortScan  QK-MMD PauliXZ         0.25        0.10                             0.888875  0.108541   1.951352        0.566667            True
 PortScan  QK-MMD PauliXZ         0.25        0.25                             0.932734  0.152418   1.995441        0.600000            True
 PortScan             JSD         0.50        0.00                             1.513802  0.324473   2.954427        0.633333            True
 PortScan         MMD-RBF         0.50        0.00                             2.480469  0.589063   4.774707        0.533333            True
 PortScan  QK-MMD PauliXZ         0.50        0.00                             0.884635  0.105723   1.941530        0.600000            True
 PortScan             JSD         0.50        0.01                             1.452885  0.263634   2.893391        0.600000            True
 PortScan         MMD-RBF         0.50        0.01                             2.435922  0.544654   4.730056        0.533333            True
 PortScan  QK-MMD PauliXZ         0.50        0.01                             0.887559  0.108531   1.944709        0.600000            True
 PortScan             JSD         0.50        0.05                             1.209215  0.020549   2.648740        0.433333            True
 PortScan         MMD-RBF         0.50        0.05                             2.257733  0.365682   4.551452        0.466667            True
 PortScan  QK-MMD PauliXZ         0.50        0.05                             0.899255  0.120563   1.957379        0.600000            True
 PortScan         MMD-RBF         0.50        0.10                             2.034998  0.143317   4.328703        0.400000            True
 PortScan  QK-MMD PauliXZ         0.50        0.10                             0.913875  0.135892   1.972505        0.600000            True
 PortScan  QK-MMD PauliXZ         0.50        0.25                             0.957734  0.179700   2.015738        0.600000            True
 PortScan             JSD         1.00        0.00                             1.413802  0.171595   2.882884        0.600000            True
 PortScan  QK-MMD PauliXZ         1.00        0.00                             0.934635  0.149707   2.003939        0.633333            True
 PortScan             JSD         1.00        0.01                             1.352885  0.111050   2.822184        0.566667            True
 PortScan  QK-MMD PauliXZ         1.00        0.01                             0.937559  0.152541   2.006634        0.633333            True
 PortScan  QK-MMD PauliXZ         1.00        0.05                             0.949255  0.163807   2.018433        0.633333            True
 PortScan  QK-MMD PauliXZ         1.00        0.10                             0.963875  0.178730   2.033180        0.633333            True
 PortScan  QK-MMD PauliXZ         1.00        0.25                             1.007734  0.224668   2.077501        0.633333            True
 PortScan  QK-MMD PauliXZ         2.00        0.00                             1.034635  0.202337   2.140651        0.600000            True
 PortScan  QK-MMD PauliXZ         2.00        0.01                             1.037559  0.205555   2.143589        0.600000            True
 PortScan  QK-MMD PauliXZ         2.00        0.05                             1.049255  0.217025   2.155340        0.600000            True
 PortScan  QK-MMD PauliXZ         2.00        0.10                             1.063875  0.231813   2.170029        0.600000            True
 PortScan  QK-MMD PauliXZ         2.00        0.25                             1.107734  0.276054   2.214092        0.600000            True
     DDoS         MMD-RBF         0.00        0.00                             0.777604  0.041380   1.547161        0.733333            True
     DDoS         MMD-RBF         0.10        0.00                             0.854271  0.118174   1.622661        0.733333            True
     DDoS         MMD-RBF         0.10        0.01                             0.812136  0.075789   1.580511        0.733333            True
     DDoS         MMD-RBF         0.25        0.00                             0.969271  0.236452   1.734928        0.733333            True
     DDoS         MMD-RBF         0.25        0.01                             0.927136  0.194291   1.693119        0.733333            True
     DDoS         MMD-RBF         0.25        0.05                             0.758599  0.026669   1.525827        0.700000            True
     DDoS Energy distance         0.50        0.00                             1.102083  0.393203   1.842708        0.733333            True
     DDoS         MMD-RBF         0.50        0.00                             1.160937  0.430456   1.931510        0.733333            True
     DDoS Energy distance         0.50        0.01                             1.041780  0.332469   1.781733        0.733333            True
     DDoS         MMD-RBF         0.50        0.01                             1.118803  0.388062   1.888888        0.733333            True
     DDoS Energy distance         0.50        0.05                             0.800567  0.092552   1.539229        0.700000            True
     DDoS         MMD-RBF         0.50        0.05                             0.950266  0.219807   1.720583        0.700000            True
     DDoS         MMD-RBF         0.50        0.10                             0.739594  0.008240   1.509853        0.633333            True
     DDoS Energy distance         1.00        0.00                             2.018750  1.302064   2.800267        0.833333            True
     DDoS             JSD         1.00        0.00                             0.891146  0.171595   1.750000        0.666667            True
     DDoS          KS-max         1.00        0.00                             1.145833  0.018229   2.370586        0.666667            True
     DDoS         MMD-RBF         1.00        0.00                             1.544271  0.807806   2.327878        0.800000            True
     DDoS Energy distance         1.00        0.01                             1.958447  1.241885   2.740115        0.833333            True
     DDoS             JSD         1.00        0.01                             0.830584  0.110863   1.689144        0.633333            True
     DDoS         MMD-RBF         1.00        0.01                             1.502136  0.765596   2.285912        0.766667            True
     DDoS Energy distance         1.00        0.05                             1.717234  1.000481   2.498037        0.800000            True
     DDoS         MMD-RBF         1.00        0.05                             1.333599  0.596408   2.117084        0.733333            True
     DDoS Energy distance         1.00        0.10                             1.415717  0.699293   2.195921        0.800000            True
     DDoS         MMD-RBF         1.00        0.10                             1.122927  0.385951   1.906592        0.633333            True
     DDoS Energy distance         2.00        0.00                             3.852083  3.017956   4.769557        1.000000            True
     DDoS             JSD         2.00        0.00                             1.457812  0.572897   2.460430        0.700000            True
     DDoS          KS-max         2.00        0.00                             1.379167  0.114271   2.735189        0.700000            True
     DDoS         MMD-RBF         2.00        0.00                             2.310938  1.492422   3.180208        0.833333            True
     DDoS Energy distance         2.00        0.01                             3.791780  2.957773   4.708945        1.000000            True
     DDoS             JSD         2.00        0.01                             1.397250  0.512025   2.400276        0.666667            True
     DDoS          KS-max         2.00        0.01                             1.320031  0.054626   2.676978        0.666667            True
     DDoS         MMD-RBF         2.00        0.01                             2.268803  1.450460   3.138787        0.833333            True
     DDoS Energy distance         2.00        0.05                             3.550567  2.717562   4.467498        0.966667            True
     DDoS             JSD         2.00        0.05                             1.155001  0.271274   2.156204        0.633333            True
     DDoS         MMD-RBF         2.00        0.05                             2.100266  1.280903   2.970939        0.800000            True
     DDoS Energy distance         2.00        0.10                             3.249050  2.416737   4.165674        0.966667            True
     DDoS         MMD-RBF         2.00        0.10                             1.889594  1.069245   2.761126        0.733333            True
     DDoS Energy distance         2.00        0.25                             2.344501  1.513261   3.256773        0.800000            True
     DDoS         MMD-RBF         2.00        0.25                             1.257578  0.432571   2.129864        0.600000            True

## Interpretation

Across three CICIDS2017 drift regimes, QK-MMD ZZ is consistently competitive with the strongest classical distributional baselines. The type of advantage is regime-dependent.

In Wednesday and DDoS, QK-MMD ZZ obtains comparable downstream performance to Energy distance while requiring fewer readaptations and achieving higher adaptation efficiency. Cost-sensitive utility favors QK-MMD ZZ when readaptation cost is non-negligible.

In PortScan, QK-MMD ZZ significantly improves downstream performance over Energy distance, but it requires more readaptations and therefore only dominates utility under low readaptation/runtime penalty settings.

The paper should therefore frame the contribution as regime-dependent quantum-kernel monitoring and operational trade-off analysis, not as universal quantum advantage.
