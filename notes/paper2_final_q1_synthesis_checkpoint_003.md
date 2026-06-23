# Paper 2 final Q1-oriented synthesis checkpoint 003

## Executive summary

This checkpoint is the updated final synthesis after adding multi-scenario CICIDS2017 validation. The paper is no longer based on a single Tuesday-to-Wednesday setting: it now includes Wednesday, Friday PortScan, and Friday DDoS drift regimes.

The central conclusion is still not universal quantum advantage. The stronger and defensible claim is that QK-MMD ZZ provides regime-dependent adaptive-monitoring advantages. Across multiple CICIDS2017 drift regimes, it remains competitive with the strongest classical distributional baseline, Energy distance.

The type of advantage changes by regime: in Wednesday and DDoS, QK-MMD ZZ achieves comparable downstream performance with fewer readaptations and higher adaptation efficiency; in PortScan, it significantly improves downstream performance, but at the cost of more readaptations and higher monitoring runtime.

This is a stronger Q1-oriented contribution than a simple quantum-vs-classical accuracy comparison because it characterizes operational trade-offs under progressive drift rather than claiming universal dominance.

## Final verdict

Current positioning:

- Q2 strong: yes.
- Q1 possible: yes, substantially more defensible than before.
- Q1 guaranteed: no.
- Top cybersecurity Q1 without external dataset: still risky.

The main remaining limitation is that all multi-scenario validation is still within CICIDS2017. A second external dataset would further strengthen the Q1 case, but the current paper is now a coherent and defensible submission candidate if targeted carefully.

## Final core claim

QK-MMD ZZ provides regime-dependent advantages for adaptive IDS drift monitoring. Across multiple CICIDS2017 progressive-drift regimes, it is consistently competitive with strong classical distributional detectors. In some regimes, it improves readaptation efficiency; in others, it improves downstream performance at additional adaptation and monitoring cost.

## Multi-scenario evidence

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

## QK-MMD ZZ vs Energy distance

 scenario        method_a        method_b                      metric  n_pairs  mean_diff_a_minus_b  ci95_low  ci95_high                         positive_means  ci_excludes_zero_positive
Wednesday       QK-MMD ZZ Energy distance      mean_balanced_accuracy       30             0.000102 -0.005654   0.006521              QK-MMD ZZ better accuracy                      False
Wednesday Energy distance       QK-MMD ZZ       cumulative_error_area       30             0.010156 -0.565404   0.652109            QK-MMD ZZ lower degradation                      False
Wednesday       QK-MMD ZZ Energy distance cumulative_gain_vs_no_adapt       30             0.010156 -0.565404   0.652109                  QK-MMD ZZ higher gain                      False
Wednesday Energy distance       QK-MMD ZZ               n_adaptations       30             2.100000  1.733333   2.433333          QK-MMD ZZ fewer readaptations                       True
Wednesday       QK-MMD ZZ Energy distance       adaptation_efficiency       30             1.551936  1.168571   1.955149 QK-MMD ZZ better adaptation efficiency                       True
Wednesday       QK-MMD ZZ Energy distance  detector_runtime_sec_total       30             5.995440  5.917411   6.076280               QK-MMD ZZ more expensive                       True
 PortScan       QK-MMD ZZ Energy distance      mean_balanced_accuracy       30             0.006445  0.001174   0.013482              QK-MMD ZZ better accuracy                       True
 PortScan Energy distance       QK-MMD ZZ       cumulative_error_area       30             0.644531  0.117435   1.348210            QK-MMD ZZ lower degradation                       True
 PortScan       QK-MMD ZZ Energy distance cumulative_gain_vs_no_adapt       30             0.644531  0.117435   1.348210                  QK-MMD ZZ higher gain                       True
 PortScan Energy distance       QK-MMD ZZ               n_adaptations       30            -1.366667 -1.633333  -1.100000          QK-MMD ZZ fewer readaptations                      False
 PortScan       QK-MMD ZZ Energy distance       adaptation_efficiency       30            -0.577895 -0.917058  -0.227857 QK-MMD ZZ better adaptation efficiency                      False
 PortScan       QK-MMD ZZ Energy distance  detector_runtime_sec_total       30             6.057628  6.007582   6.113502               QK-MMD ZZ more expensive                       True
     DDoS       QK-MMD ZZ Energy distance      mean_balanced_accuracy       30             0.001854 -0.005435   0.009203              QK-MMD ZZ better accuracy                      False
     DDoS Energy distance       QK-MMD ZZ       cumulative_error_area       30             0.185417 -0.543496   0.920312            QK-MMD ZZ lower degradation                      False
     DDoS       QK-MMD ZZ Energy distance cumulative_gain_vs_no_adapt       30             0.185417 -0.543496   0.920312                  QK-MMD ZZ higher gain                      False
     DDoS Energy distance       QK-MMD ZZ               n_adaptations       30             1.833333  1.533333   2.133333          QK-MMD ZZ fewer readaptations                       True
     DDoS       QK-MMD ZZ Energy distance       adaptation_efficiency       30             1.935859  1.596164   2.300397 QK-MMD ZZ better adaptation efficiency                       True
     DDoS       QK-MMD ZZ Energy distance  detector_runtime_sec_total       30             6.030330  5.959551   6.099601               QK-MMD ZZ more expensive                       True

## Scenario-specific interpretation

### Wednesday

QK-MMD ZZ and Energy distance are statistically tied in downstream performance. However, QK-MMD ZZ requires significantly fewer readaptations and achieves significantly higher adaptation efficiency. This is the clearest operational efficiency scenario.

### PortScan

QK-MMD ZZ significantly improves downstream balanced accuracy, cumulative degradation, and cumulative gain relative to Energy distance. However, it uses more readaptations and has lower adaptation efficiency than Energy distance. This is a performance-gain scenario rather than an efficiency-gain scenario.

### DDoS

QK-MMD ZZ and Energy distance are statistically tied in raw downstream performance, but QK-MMD ZZ requires significantly fewer readaptations and achieves significantly higher adaptation efficiency. This mirrors the Wednesday operational-efficiency pattern.

## Cost-sensitive utility

The cost-sensitive utility analysis uses: `utility = cumulative_gain_vs_no_adapt - lambda * n_adaptations - gamma * detector_runtime_sec_total`.

Strict positive regions indicate settings where QK-MMD ZZ has a positive bootstrap CI lower bound against the corresponding baseline.

 scenario        baseline  lambda_cost  gamma_cost  mean_utility_diff_qk_minus_baseline  ci95_low  ci95_high  qk_better_ci95
     DDoS Energy distance         0.50        0.00                             1.102083  0.393203   1.842708            True
     DDoS Energy distance         0.50        0.01                             1.041780  0.332469   1.781733            True
     DDoS Energy distance         0.50        0.05                             0.800567  0.092552   1.539229            True
     DDoS Energy distance         1.00        0.00                             2.018750  1.302064   2.800267            True
     DDoS Energy distance         1.00        0.01                             1.958447  1.241885   2.740115            True
     DDoS Energy distance         1.00        0.05                             1.717234  1.000481   2.498037            True
     DDoS Energy distance         1.00        0.10                             1.415717  0.699293   2.195921            True
     DDoS Energy distance         2.00        0.00                             3.852083  3.017956   4.769557            True
     DDoS Energy distance         2.00        0.01                             3.791780  2.957773   4.708945            True
     DDoS Energy distance         2.00        0.05                             3.550567  2.717562   4.467498            True
     DDoS Energy distance         2.00        0.10                             3.249050  2.416737   4.165674            True
     DDoS Energy distance         2.00        0.25                             2.344501  1.513261   3.256773            True
     DDoS             JSD         1.00        0.00                             0.891146  0.171595   1.750000            True
     DDoS             JSD         1.00        0.01                             0.830584  0.110863   1.689144            True
     DDoS             JSD         2.00        0.00                             1.457812  0.572897   2.460430            True
     DDoS             JSD         2.00        0.01                             1.397250  0.512025   2.400276            True
     DDoS             JSD         2.00        0.05                             1.155001  0.271274   2.156204            True
     DDoS          KS-max         1.00        0.00                             1.145833  0.018229   2.370586            True
     DDoS          KS-max         2.00        0.00                             1.379167  0.114271   2.735189            True
     DDoS          KS-max         2.00        0.01                             1.320031  0.054626   2.676978            True
     DDoS         MMD-RBF         0.00        0.00                             0.777604  0.041380   1.547161            True
     DDoS         MMD-RBF         0.10        0.00                             0.854271  0.118174   1.622661            True
     DDoS         MMD-RBF         0.10        0.01                             0.812136  0.075789   1.580511            True
     DDoS         MMD-RBF         0.25        0.00                             0.969271  0.236452   1.734928            True
     DDoS         MMD-RBF         0.25        0.01                             0.927136  0.194291   1.693119            True
     DDoS         MMD-RBF         0.25        0.05                             0.758599  0.026669   1.525827            True
     DDoS         MMD-RBF         0.50        0.00                             1.160937  0.430456   1.931510            True
     DDoS         MMD-RBF         0.50        0.01                             1.118803  0.388062   1.888888            True
     DDoS         MMD-RBF         0.50        0.05                             0.950266  0.219807   1.720583            True
     DDoS         MMD-RBF         0.50        0.10                             0.739594  0.008240   1.509853            True
     DDoS         MMD-RBF         1.00        0.00                             1.544271  0.807806   2.327878            True
     DDoS         MMD-RBF         1.00        0.01                             1.502136  0.765596   2.285912            True
     DDoS         MMD-RBF         1.00        0.05                             1.333599  0.596408   2.117084            True
     DDoS         MMD-RBF         1.00        0.10                             1.122927  0.385951   1.906592            True
     DDoS         MMD-RBF         2.00        0.00                             2.310938  1.492422   3.180208            True
     DDoS         MMD-RBF         2.00        0.01                             2.268803  1.450460   3.138787            True
     DDoS         MMD-RBF         2.00        0.05                             2.100266  1.280903   2.970939            True
     DDoS         MMD-RBF         2.00        0.10                             1.889594  1.069245   2.761126            True
     DDoS         MMD-RBF         2.00        0.25                             1.257578  0.432571   2.129864            True
 PortScan Energy distance         0.00        0.00                             0.644531  0.117435   1.348210            True
 PortScan Energy distance         0.00        0.01                             0.583955  0.057007   1.287933            True
 PortScan             JSD         0.00        0.00                             1.613802  0.457799   3.020599            True
 PortScan             JSD         0.00        0.01                             1.552885  0.397014   2.959088            True
 PortScan             JSD         0.00        0.05                             1.309215  0.154943   2.715396            True
 PortScan             JSD         0.10        0.00                             1.593802  0.431030   3.007270            True
 PortScan             JSD         0.10        0.01                             1.532885  0.369878   2.945754            True
 PortScan             JSD         0.10        0.05                             1.289215  0.125270   2.701595            True
 PortScan             JSD         0.25        0.00                             1.563802  0.390612   2.986198            True
 PortScan             JSD         0.25        0.01                             1.502885  0.330058   2.924882            True
 PortScan             JSD         0.25        0.05                             1.259215  0.087746   2.679953            True
 PortScan             JSD         0.50        0.00                             1.513802  0.324473   2.954427            True
 PortScan             JSD         0.50        0.01                             1.452885  0.263634   2.893391            True
 PortScan             JSD         0.50        0.05                             1.209215  0.020549   2.648740            True
 PortScan             JSD         1.00        0.00                             1.413802  0.171595   2.882884            True
 PortScan             JSD         1.00        0.01                             1.352885  0.111050   2.822184            True
 PortScan          KS-max         0.00        0.00                             0.655729  0.098158   1.510443            True
 PortScan          KS-max         0.00        0.01                             0.596595  0.039450   1.451309            True
 PortScan          KS-max         0.10        0.00                             0.582396  0.032909   1.424487            True
 PortScan         MMD-RBF         0.00        0.00                             3.263802  1.386712   5.558346            True
 PortScan         MMD-RBF         0.00        0.01                             3.219255  1.342174   5.513976            True
 PortScan         MMD-RBF         0.00        0.05                             3.041067  1.164417   5.336317            True
 PortScan         MMD-RBF         0.00        0.10                             2.818331  0.943259   5.113792            True
 PortScan         MMD-RBF         0.00        0.25                             2.150125  0.270913   4.446674            True
 PortScan         MMD-RBF         0.10        0.00                             3.107135  1.232957   5.401147            True
 PortScan         MMD-RBF         0.10        0.01                             3.062588  1.188157   5.356485            True
 PortScan         MMD-RBF         0.10        0.05                             2.884400  1.008996   5.178020            True
 PortScan         MMD-RBF         0.10        0.10                             2.661664  0.785096   4.955006            True
 PortScan         MMD-RBF         0.10        0.25                             1.993458  0.114241   4.289274            True
 PortScan         MMD-RBF         0.25        0.00                             2.872135  0.994010   5.166940            True
 PortScan         MMD-RBF         0.25        0.01                             2.827588  0.949170   5.122731            True
 PortScan         MMD-RBF         0.25        0.05                             2.649400  0.769821   4.944545            True
 PortScan         MMD-RBF         0.25        0.10                             2.426664  0.545578   4.721655            True
 PortScan         MMD-RBF         0.50        0.00                             2.480469  0.589063   4.774707            True
 PortScan         MMD-RBF         0.50        0.01                             2.435922  0.544654   4.730056            True
 PortScan         MMD-RBF         0.50        0.05                             2.257733  0.365682   4.551452            True
 PortScan         MMD-RBF         0.50        0.10                             2.034998  0.143317   4.328703            True
Wednesday Energy distance         0.50        0.00                             1.060156  0.415605   1.759388            True
Wednesday Energy distance         0.50        0.01                             1.000202  0.355457   1.699921            True
Wednesday Energy distance         0.50        0.05                             0.760384  0.115562   1.461245            True
Wednesday Energy distance         1.00        0.00                             2.110156  1.350514   2.884648            True
Wednesday Energy distance         1.00        0.01                             2.050202  1.290179   2.824913            True
Wednesday Energy distance         1.00        0.05                             1.810384  1.048911   2.585989            True
Wednesday Energy distance         1.00        0.10                             1.510612  0.747366   2.287248            True
Wednesday Energy distance         2.00        0.00                             4.210156  3.167402   5.198451            True
Wednesday Energy distance         2.00        0.01                             4.150202  3.106775   5.138724            True
Wednesday Energy distance         2.00        0.05                             3.910384  2.865580   4.898956            True
Wednesday Energy distance         2.00        0.10                             3.610612  2.563389   4.599411            True
Wednesday Energy distance         2.00        0.25                             2.711296  1.659171   3.702799            True
Wednesday             JSD         1.00        0.00                             0.816667  0.095046   1.768750            True
Wednesday             JSD         1.00        0.01                             0.756394  0.034950   1.708562            True
Wednesday             JSD         2.00        0.00                             1.250000  0.385671   2.310716            True
Wednesday             JSD         2.00        0.01                             1.189727  0.325056   2.250118            True
Wednesday             JSD         2.00        0.05                             0.948637  0.083431   2.009584            True
Wednesday          KS-max         0.25        0.00                             0.835938  0.056504   1.934388            True
Wednesday          KS-max         0.50        0.00                             0.910937  0.152077   1.983646            True
Wednesday          KS-max         0.50        0.01                             0.852476  0.093174   1.925460            True
Wednesday          KS-max         1.00        0.00                             1.060938  0.316406   2.094805            True
Wednesday          KS-max         1.00        0.01                             1.002476  0.258170   2.036559            True
Wednesday          KS-max         1.00        0.05                             0.768628  0.024372   1.801517            True
Wednesday          KS-max         2.00        0.00                             1.360937  0.564811   2.345586            True
Wednesday          KS-max         2.00        0.01                             1.302476  0.506257   2.287423            True
Wednesday          KS-max         2.00        0.05                             1.068628  0.272070   2.053280            True
Wednesday         MMD-RBF         0.25        0.00                             0.725521  0.076276   1.527350            True
Wednesday         MMD-RBF         0.25        0.01                             0.681414  0.032122   1.483351            True
Wednesday         MMD-RBF         0.50        0.00                             0.958854  0.307526   1.752350            True
Wednesday         MMD-RBF         0.50        0.01                             0.914747  0.263243   1.707483            True
Wednesday         MMD-RBF         0.50        0.05                             0.738320  0.086651   1.531136            True
Wednesday         MMD-RBF         1.00        0.00                             1.425521  0.746328   2.219277            True
Wednesday         MMD-RBF         1.00        0.01                             1.381414  0.701790   2.175141            True
Wednesday         MMD-RBF         1.00        0.05                             1.204987  0.523658   1.997479            True
Wednesday         MMD-RBF         1.00        0.10                             0.984453  0.303707   1.776199            True
Wednesday         MMD-RBF         2.00        0.00                             2.358854  1.543991   3.237513            True
Wednesday         MMD-RBF         2.00        0.01                             2.314747  1.499488   3.193947            True
Wednesday         MMD-RBF         2.00        0.05                             2.138320  1.321475   3.017820            True
Wednesday         MMD-RBF         2.00        0.10                             1.917787  1.101831   2.796624            True
Wednesday         MMD-RBF         2.00        0.25                             1.256185  0.440599   2.131691            True

Utility favors QK-MMD ZZ most clearly in Wednesday and DDoS when readaptation cost is non-negligible. In PortScan, QK-MMD ZZ wins raw performance but loses part of the utility advantage once readaptation and runtime costs are strongly penalized.

## Claims supported

1. Triggered readaptation reduces degradation relative to no adaptation.
2. QK-MMD ZZ is consistently competitive across multiple CICIDS2017 drift regimes.
3. QK-MMD ZZ matches or exceeds Energy distance depending on the drift regime.
4. In Wednesday and DDoS, QK-MMD ZZ improves adaptation efficiency over Energy distance.
5. In PortScan, QK-MMD ZZ significantly improves downstream performance over Energy distance.
6. QK-MMD ZZ has substantially higher detector runtime.
7. The quantum-kernel benefit is regime-dependent, not universal.
8. Cost-sensitive utility can favor QK-MMD ZZ when readaptation cost is operationally relevant.

## Claims to avoid

1. Universal quantum advantage.
2. QK-MMD always detects earlier.
3. QK-MMD always improves final downstream accuracy.
4. QK-MMD is computationally cheaper.
5. Classical baselines are weak.
6. QK-MMD ZZ is always more adaptation-efficient.

## Main reviewer risks

1. All multi-scenario validation is still within CICIDS2017.
2. Energy distance is extremely competitive and much cheaper.
3. QK-MMD ZZ is simulated and has higher runtime.
4. The advantage changes by regime, which must be framed as a finding, not as inconsistency.
5. The utility analysis depends on cost assumptions.

## Recommended title direction

Regime-Dependent Quantum-Kernel Drift Monitoring for Efficient Adaptive Intrusion Detection

Alternative:

Quantum-Kernel MMD for Progressive Drift Monitoring in Adaptive Intrusion Detection: A Cost-Sensitive Multi-Regime Study

## Recommended paper framing

Frame the paper as an adaptive drift-monitoring study, not as a universal quantum advantage paper. The contribution is the detailed characterization of when quantum kernel discrepancy signals are useful, how they compare to strong classical distributional baselines, and under which operational cost regimes they become preferable.

## Recommended next step

At this point, do not add more CICIDS2017 scenarios. The next decision is strategic: either start drafting the paper with the current multi-scenario CICIDS2017 evidence, or add one external dataset if the goal is to maximize Q1 confidence.

If time is limited, start drafting. If Q1 confidence is the priority, add one external dataset after the paper structure is already outlined.
