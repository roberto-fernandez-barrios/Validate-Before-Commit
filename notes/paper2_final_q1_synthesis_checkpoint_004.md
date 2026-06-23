# Paper 2 final Q1-oriented synthesis checkpoint 004

## Executive verdict

This checkpoint supersedes checkpoint_003. The paper should no longer be framed as a simple quantum-vs-classical detector comparison. The strongest framing is a cost-sensitive actionable drift study for adaptive intrusion detection.

Final positioning:

- Q2 strong: yes.
- Q1 possible: yes, with careful venue targeting.
- Q1 guaranteed: no.
- Universal quantum advantage: no.
- Strongest contribution: operational trade-off characterization under progressive adversarial and benign/non-adversarial drift.

The paper is substantially stronger after adding multi-regime CICIDS validation and nuisance benign controls. However, the final claim must remain nuanced: QK-MMD ZZ does not universally suppress benign nuisance triggers and is computationally more expensive. Its value appears in cost regimes where readaptation is expensive relative to monitoring runtime.

## Final core claim

QK-MMD ZZ provides regime-dependent operational benefits for adaptive IDS drift monitoring. Across multiple CICIDS2017 progressive adversarial drift regimes, it is competitive with strong classical distributional baselines. In Wednesday and DDoS, it achieves comparable downstream performance with fewer readaptations and higher adaptation efficiency; in PortScan, it significantly improves downstream performance at the cost of more readaptations. Benign-only controls show that QK-MMD ZZ does not universally reduce nuisance triggers, but actionable utility analysis indicates that its adversarial readaptation savings can compensate for nuisance-trigger penalties when readaptation cost is non-negligible.

## One-sentence paper thesis

Quantum-kernel MMD is not a universally superior drift detector, but it can alter the operational trade-off between adversarial recovery, readaptation frequency, benign nuisance triggers, and monitoring cost in adaptive intrusion detection.

## Multi-scenario adversarial evidence

 scenario    method_label  n_seeds  mean_balanced_accuracy  cumulative_error_area_mean  cumulative_gain_vs_no_adapt_mean  n_adaptations_mean  adaptation_efficiency_mean  detector_runtime_sec_total_mean
     DDoS       QK-MMD ZZ       30                0.893271                   10.672917                         19.496875            3.600000                    5.531654                         6.070541
     DDoS Energy distance       30                0.891417                   10.858333                         19.311458            5.433333                    3.595795                         0.040211
     DDoS             JSD       30                0.890026                   10.997396                         19.172396            4.166667                    4.760082                         0.014318
     DDoS  QK-MMD PauliXZ       30                0.888435                   11.156510                         19.013281            3.533333                    5.463520                         6.511849
     DDoS         MMD-RBF       30                0.885495                   11.450521                         18.719271            4.366667                    4.387409                         1.857102
     DDoS          KS-max       30                0.884146                   11.585417                         18.584375            3.833333                    4.938841                         0.156981
 PortScan       QK-MMD ZZ       30                0.939115                    6.088542                          6.203906            4.066667                    1.544783                         6.113158
 PortScan Energy distance       30                0.932669                    6.733073                          5.559375            2.700000                    2.122678                         0.055530
 PortScan          KS-max       30                0.932557                    6.744271                          5.548177            3.333333                    1.667687                         0.199714
 PortScan  QK-MMD PauliXZ       30                0.930768                    6.923177                          5.369271            4.166667                    1.258012                         6.405552
 PortScan             JSD       30                0.922977                    7.702344                          4.590104            3.866667                    1.196289                         0.021419
 PortScan         MMD-RBF       30                0.906477                    9.352344                          2.940104            2.500000                    1.064193                         1.658449
Wednesday       QK-MMD ZZ       30                0.884826                   11.517448                         11.889323            3.166667                    3.880794                         6.048713
Wednesday Energy distance       30                0.884724                   11.527604                         11.879167            5.266667                    2.328859                         0.053273
Wednesday             JSD       30                0.880992                   11.900781                         11.505990            3.600000                    3.282682                         0.021458
Wednesday         MMD-RBF       30                0.879904                   12.009635                         11.397135            4.100000                    2.806254                         1.638038
Wednesday  QK-MMD PauliXZ       30                0.878474                   12.152604                         11.254167            3.200000                    3.573351                         6.416026
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

## Actionable drift component summary

The actionable analysis combines adversarial progressive drift benefits with benign-only nuisance triggers. This avoids claiming that every distributional alarm is useful.

   method_label  n_seeds  adversarial_gain_mean  adversarial_readaptations_mean  benign_nuisance_triggers_mean  nodrift_nuisance_triggers_mean  excess_nuisance_triggers_mean  mean_balanced_accuracy  cumulative_error_area_mean  total_runtime_adv_plus_benign_mean
        MMD-RBF       30              11.397135                        4.100000                       0.700000                        0.633333                       0.066667                0.879904                   12.009635                            3.920187
         KS-max       30              11.128385                        3.466667                       0.833333                        0.600000                       0.233333                0.877216                   12.278385                            0.422418
 QK-MMD PauliXZ       30              11.254167                        3.200000                       1.133333                        0.666667                       0.466667                0.878474                   12.152604                           17.830375
Energy distance       30              11.879167                        5.266667                       1.033333                        0.400000                       0.633333                0.884724                   11.527604                            0.118639
      QK-MMD ZZ       30              11.889323                        3.166667                       1.400000                        0.533333                       0.866667                0.884826                   11.517448                           16.697242
            JSD       30              11.505990                        3.600000                       1.633333                        0.600000                       1.033333                0.880992                   11.900781                            0.043274

## Actionable utility

Actionable utility is defined as adversarial gain minus readaptation cost, nuisance-trigger cost, and runtime cost. Two nuisance modes are tracked: total benign nuisance triggers and clipped excess nuisance triggers relative to the no-drift benign control.

The strict positive regions below indicate settings where QK-MMD ZZ has a positive bootstrap CI lower bound against a baseline.

       baseline  lambda_cost  eta_cost  gamma_cost  nuisance_mode  mean_actionable_utility_diff_qk_minus_baseline  ci95_low  ci95_high  qk_better_ci95
Energy distance         0.50      0.00        0.00 excess_clipped                                        1.060156  0.415605   1.759388            True
Energy distance         0.50      0.00        0.01 excess_clipped                                        0.894370  0.248690   1.593915            True
Energy distance         0.50      0.25        0.00 excess_clipped                                        1.010156  0.379661   1.694531            True
Energy distance         0.50      0.25        0.01 excess_clipped                                        0.844370  0.212368   1.527873            True
Energy distance         0.50      0.50        0.00 excess_clipped                                        0.960156  0.321868   1.644277            True
Energy distance         0.50      0.50        0.01 excess_clipped                                        0.794370  0.155374   1.478903            True
Energy distance         0.50      1.00        0.00 excess_clipped                                        0.860156  0.176523   1.594290            True
Energy distance         0.50      1.00        0.01 excess_clipped                                        0.694370  0.010084   1.428821            True
Energy distance         1.00      0.00        0.00 excess_clipped                                        2.110156  1.350514   2.884648            True
Energy distance         1.00      0.00        0.01 excess_clipped                                        1.944370  1.184273   2.719432            True
Energy distance         1.00      0.00        0.05 excess_clipped                                        1.281226  0.519405   2.059945            True
Energy distance         1.00      0.25        0.00 excess_clipped                                        2.060156  1.310391   2.817988            True
Energy distance         1.00      0.25        0.01 excess_clipped                                        1.894370  1.144073   2.652131            True
Energy distance         1.00      0.25        0.05 excess_clipped                                        1.231226  0.480579   1.991538            True
Energy distance         1.00      0.50        0.00 excess_clipped                                        2.010156  1.266647   2.773184            True
Energy distance         1.00      0.50        0.01 excess_clipped                                        1.844370  1.100920   2.608533            True
Energy distance         1.00      0.50        0.05 excess_clipped                                        1.181226  0.435956   1.945227            True
Energy distance         1.00      1.00        0.00 excess_clipped                                        1.910156  1.133561   2.717467            True
Energy distance         1.00      1.00        0.01 excess_clipped                                        1.744370  0.967029   2.551079            True
Energy distance         1.00      1.00        0.05 excess_clipped                                        1.081226  0.300862   1.889181            True
Energy distance         1.00      2.00        0.00 excess_clipped                                        1.710156  0.743229   2.733079            True
Energy distance         1.00      2.00        0.01 excess_clipped                                        1.544370  0.577498   2.566864            True
Energy distance         2.00      0.00        0.00 excess_clipped                                        4.210156  3.167402   5.198451            True
Energy distance         2.00      0.00        0.01 excess_clipped                                        4.044370  3.000050   5.032955            True
Energy distance         2.00      0.00        0.05 excess_clipped                                        3.381226  2.333741   4.371200            True
Energy distance         2.00      0.00        0.10 excess_clipped                                        2.552296  1.501020   3.543982            True
Energy distance         2.00      0.25        0.00 excess_clipped                                        4.160156  3.124212   5.146100            True
Energy distance         2.00      0.25        0.01 excess_clipped                                        3.994370  2.957853   4.980603            True
Energy distance         2.00      0.25        0.05 excess_clipped                                        3.331226  2.289768   4.318551            True
Energy distance         2.00      0.25        0.10 excess_clipped                                        2.502296  1.458345   3.489669            True
Energy distance         2.00      0.50        0.00 excess_clipped                                        4.110156  3.080951   5.105215            True
Energy distance         2.00      0.50        0.01 excess_clipped                                        3.944370  2.913925   4.939179            True
Energy distance         2.00      0.50        0.05 excess_clipped                                        3.281226  2.247381   4.277243            True
Energy distance         2.00      0.50        0.10 excess_clipped                                        2.452296  1.415918   3.448004            True
Energy distance         2.00      1.00        0.00 excess_clipped                                        4.010156  2.965365   5.035417            True
Energy distance         2.00      1.00        0.01 excess_clipped                                        3.844370  2.800309   4.868868            True
Energy distance         2.00      1.00        0.05 excess_clipped                                        3.181226  2.133461   4.209244            True
Energy distance         2.00      1.00        0.10 excess_clipped                                        2.352296  1.302055   3.382040            True
Energy distance         2.00      2.00        0.00 excess_clipped                                        3.810156  2.659896   5.004193            True
Energy distance         2.00      2.00        0.01 excess_clipped                                        3.644370  2.493294   4.838837            True
Energy distance         2.00      2.00        0.05 excess_clipped                                        2.981226  1.826990   4.174688            True
Energy distance         2.00      2.00        0.10 excess_clipped                                        2.152296  0.995679   3.344280            True
            JSD         0.50      0.50        0.00 excess_clipped                                        0.716667  0.047643   1.560690            True
            JSD         0.50      1.00        0.00 excess_clipped                                        0.833333  0.095820   1.665137            True
            JSD         0.50      2.00        0.00 excess_clipped                                        1.066667  0.040365   2.044030            True
            JSD         1.00      0.00        0.00 excess_clipped                                        0.816667  0.095046   1.768750            True
            JSD         1.00      0.25        0.00 excess_clipped                                        0.875000  0.169258   1.793496            True
            JSD         1.00      0.25        0.01 excess_clipped                                        0.708460  0.002864   1.627366            True
            JSD         1.00      0.50        0.00 excess_clipped                                        0.933333  0.222917   1.826823            True
            JSD         1.00      0.50        0.01 excess_clipped                                        0.766794  0.057099   1.660130            True
            JSD         1.00      1.00        0.00 excess_clipped                                        1.050000  0.280202   1.928385            True
            JSD         1.00      1.00        0.01 excess_clipped                                        0.883460  0.114148   1.760920            True
            JSD         1.00      2.00        0.00 excess_clipped                                        1.283333  0.251543   2.286204            True
            JSD         1.00      2.00        0.01 excess_clipped                                        1.116794  0.085680   2.119589            True
            JSD         2.00      0.00        0.00 excess_clipped                                        1.250000  0.385671   2.310716            True
            JSD         2.00      0.00        0.01 excess_clipped                                        1.083460  0.218753   2.143637            True
            JSD         2.00      0.25        0.00 excess_clipped                                        1.308333  0.462500   2.339870            True
            JSD         2.00      0.25        0.01 excess_clipped                                        1.141794  0.296041   2.174396            True
            JSD         2.00      0.50        0.00 excess_clipped                                        1.366667  0.520039   2.376842            True
            JSD         2.00      0.50        0.01 excess_clipped                                        1.200127  0.353434   2.210172            True
            JSD         2.00      1.00        0.00 excess_clipped                                        1.483333  0.592422   2.470332            True
            JSD         2.00      1.00        0.01 excess_clipped                                        1.316794  0.425269   2.304254            True
            JSD         2.00      2.00        0.00 excess_clipped                                        1.716667  0.598132   2.826042            True
            JSD         2.00      2.00        0.01 excess_clipped                                        1.550127  0.431553   2.658588            True
         KS-max         0.25      0.00        0.00 excess_clipped                                        0.835938  0.056504   1.934388            True
         KS-max         0.50      0.00        0.00 excess_clipped                                        0.910937  0.152077   1.983646            True
         KS-max         0.50      0.25        0.00 excess_clipped                                        0.827604  0.031491   1.973184            True
         KS-max         1.00      0.00        0.00 excess_clipped                                        1.060938  0.316406   2.094805            True
         KS-max         1.00      0.00        0.01 excess_clipped                                        0.898189  0.154285   1.930854            True
         KS-max         1.00      0.25        0.00 excess_clipped                                        0.977604  0.190352   2.085697            True
         KS-max         1.00      0.25        0.01 excess_clipped                                        0.814856  0.028173   1.922633            True
         KS-max         1.00      0.50        0.00 excess_clipped                                        0.894271  0.047376   2.080736            True
         KS-max         2.00      0.00        0.00 excess_clipped                                        1.360937  0.564811   2.345586            True
         KS-max         2.00      0.00        0.01 excess_clipped                                        1.198189  0.402226   2.182631            True
         KS-max         2.00      0.25        0.00 excess_clipped                                        1.277604  0.426035   2.326068            True
         KS-max         2.00      0.25        0.01 excess_clipped                                        1.114856  0.263722   2.163725            True
         KS-max         2.00      0.50        0.00 excess_clipped                                        1.194271  0.285918   2.320859            True
         KS-max         2.00      0.50        0.01 excess_clipped                                        1.031523  0.124276   2.157576            True
        MMD-RBF         0.25      0.00        0.00 excess_clipped                                        0.725521  0.076276   1.527350            True
        MMD-RBF         0.50      0.00        0.00 excess_clipped                                        0.958854  0.307526   1.752350            True
        MMD-RBF         0.50      0.00        0.01 excess_clipped                                        0.831084  0.178971   1.624078            True
        MMD-RBF         0.50      0.25        0.00 excess_clipped                                        0.825521  0.190820   1.616185            True
        MMD-RBF         0.50      0.25        0.01 excess_clipped                                        0.697750  0.063503   1.488780            True
        MMD-RBF         0.50      0.50        0.00 excess_clipped                                        0.692187  0.052344   1.485215            True
        MMD-RBF         1.00      0.00        0.00 excess_clipped                                        1.425521  0.746328   2.219277            True
        MMD-RBF         1.00      0.00        0.01 excess_clipped                                        1.297750  0.617485   2.091273            True
        MMD-RBF         1.00      0.00        0.05 excess_clipped                                        0.786668  0.106367   1.579128            True
        MMD-RBF         1.00      0.25        0.00 excess_clipped                                        1.292188  0.632799   2.078145            True
        MMD-RBF         1.00      0.25        0.01 excess_clipped                                        1.164417  0.505461   1.949841            True
        MMD-RBF         1.00      0.50        0.00 excess_clipped                                        1.158854  0.512487   1.951589            True
        MMD-RBF         1.00      0.50        0.01 excess_clipped                                        1.031084  0.385078   1.822913            True
        MMD-RBF         1.00      1.00        0.00 excess_clipped                                        0.892188  0.229941   1.704694            True
        MMD-RBF         1.00      1.00        0.01 excess_clipped                                        0.764417  0.103014   1.575484            True
        MMD-RBF         2.00      0.00        0.00 excess_clipped                                        2.358854  1.543991   3.237513            True
        MMD-RBF         2.00      0.00        0.01 excess_clipped                                        2.231084  1.415225   3.111062            True
        MMD-RBF         2.00      0.00        0.05 excess_clipped                                        1.720001  0.906367   2.598796            True
        MMD-RBF         2.00      0.00        0.10 excess_clipped                                        1.081149  0.267977   1.960105            True
        MMD-RBF         2.00      0.25        0.00 excess_clipped                                        2.225521  1.439811   3.084115            True
        MMD-RBF         2.00      0.25        0.01 excess_clipped                                        2.097750  1.312300   2.955261            True
        MMD-RBF         2.00      0.25        0.05 excess_clipped                                        1.586668  0.800985   2.442654            True
        MMD-RBF         2.00      0.25        0.10 excess_clipped                                        0.947815  0.162248   1.803449            True
        MMD-RBF         2.00      0.50        0.00 excess_clipped                                        2.092188  1.320527   2.950801            True
        MMD-RBF         2.00      0.50        0.01 excess_clipped                                        1.964417  1.192102   2.821929            True
        MMD-RBF         2.00      0.50        0.05 excess_clipped                                        1.453335  0.680781   2.309805            True
        MMD-RBF         2.00      0.50        0.10 excess_clipped                                        0.814482  0.040904   1.668558            True
        MMD-RBF         2.00      1.00        0.00 excess_clipped                                        1.825521  1.063249   2.682311            True
        MMD-RBF         2.00      1.00        0.01 excess_clipped                                        1.697750  0.935929   2.555122            True
        MMD-RBF         2.00      1.00        0.05 excess_clipped                                        1.186668  0.426014   2.042398            True
        MMD-RBF         2.00      2.00        0.00 excess_clipped                                        1.292188  0.441348   2.251569            True
        MMD-RBF         2.00      2.00        0.01 excess_clipped                                        1.164417  0.313722   2.123331            True
Energy distance         0.50      0.00        0.00          total                                        1.060156  0.415605   1.759388            True
Energy distance         0.50      0.00        0.01          total                                        0.894370  0.248690   1.593915            True
Energy distance         0.50      0.25        0.00          total                                        0.968490  0.336979   1.652624            True
Energy distance         0.50      0.25        0.01          total                                        0.802704  0.171016   1.487666            True
Energy distance         0.50      0.50        0.00          total                                        0.876823  0.240859   1.572168            True
Energy distance         0.50      0.50        0.01          total                                        0.711037  0.074019   1.406277            True
Energy distance         0.50      1.00        0.00          total                                        0.693490  0.011198   1.426595            True
Energy distance         1.00      0.00        0.00          total                                        2.110156  1.350514   2.884648            True
Energy distance         1.00      0.00        0.01          total                                        1.944370  1.184273   2.719432            True
Energy distance         1.00      0.00        0.05          total                                        1.281226  0.519405   2.059945            True
Energy distance         1.00      0.25        0.00          total                                        2.018490  1.274987   2.782038            True
Energy distance         1.00      0.25        0.01          total                                        1.852704  1.108561   2.616522            True
Energy distance         1.00      0.25        0.05          total                                        1.189559  0.442645   1.952811            True
Energy distance         1.00      0.50        0.00          total                                        1.926823  1.174473   2.689850            True
Energy distance         1.00      0.50        0.01          total                                        1.761037  1.007733   2.525044            True
Energy distance         1.00      0.50        0.05          total                                        1.097893  0.341512   1.865034            True
Energy distance         1.00      1.00        0.00          total                                        1.743490  0.953874   2.550000            True
Energy distance         1.00      1.00        0.01          total                                        1.577704  0.787362   2.384202            True
Energy distance         1.00      1.00        0.05          total                                        0.914559  0.122866   1.721032            True
Energy distance         1.00      2.00        0.00          total                                        1.376823  0.409896   2.375521            True
Energy distance         1.00      2.00        0.01          total                                        1.211037  0.243781   2.209801            True
Energy distance         2.00      0.00        0.00          total                                        4.210156  3.167402   5.198451            True
Energy distance         2.00      0.00        0.01          total                                        4.044370  3.000050   5.032955            True
Energy distance         2.00      0.00        0.05          total                                        3.381226  2.333741   4.371200            True
Energy distance         2.00      0.00        0.10          total                                        2.552296  1.501020   3.543982            True
Energy distance         2.00      0.25        0.00          total                                        4.118490  3.084857   5.101862            True
Energy distance         2.00      0.25        0.01          total                                        3.952704  2.918059   4.936924            True
Energy distance         2.00      0.25        0.05          total                                        3.289559  2.248633   4.275037            True
Energy distance         2.00      0.25        0.10          total                                        2.460629  1.415477   3.448292            True
Energy distance         2.00      0.50        0.00          total                                        4.026823  2.990625   5.023711            True
Energy distance         2.00      0.50        0.01          total                                        3.861037  2.825239   4.858530            True
Energy distance         2.00      0.50        0.05          total                                        3.197893  2.160624   4.197822            True
Energy distance         2.00      0.50        0.10          total                                        2.368963  1.330462   3.371223            True
Energy distance         2.00      1.00        0.00          total                                        3.843490  2.787988   4.868783            True
Energy distance         2.00      1.00        0.01          total                                        3.677704  2.621813   4.702972            True
Energy distance         2.00      1.00        0.05          total                                        3.014559  1.956074   4.043558            True
Energy distance         2.00      1.00        0.10          total                                        2.185629  1.122504   3.217075            True
Energy distance         2.00      2.00        0.00          total                                        3.476823  2.277214   4.661725            True
Energy distance         2.00      2.00        0.01          total                                        3.311037  2.111887   4.495778            True
Energy distance         2.00      2.00        0.05          total                                        2.647893  1.447383   3.832600            True
Energy distance         2.00      2.00        0.10          total                                        1.818963  0.615105   3.000922            True
            JSD         0.10      2.00        0.00          total                                        0.893333  0.017432   1.757051            True
            JSD         0.25      1.00        0.00          total                                        0.725000  0.052344   1.470592            True
            JSD         0.25      2.00        0.00          total                                        0.958333  0.080990   1.827350            True
            JSD         0.50      0.25        0.00          total                                        0.658333  0.006504   1.509134            True
            JSD         0.50      0.50        0.00          total                                        0.716667  0.072135   1.526569            True
            JSD         0.50      1.00        0.00          total                                        0.833333  0.149993   1.594544            True
            JSD         0.50      2.00        0.00          total                                        1.066667  0.185391   1.936986            True
            JSD         0.50      2.00        0.01          total                                        0.900127  0.019500   1.770531            True
            JSD         1.00      0.00        0.00          total                                        0.816667  0.095046   1.768750            True

## Interpretation by experimental block

### 1. Progressive adversarial drift

Triggered readaptation clearly reduces degradation relative to no adaptation. QK-MMD ZZ is competitive with Energy distance across Wednesday, PortScan, and DDoS.

### 2. Regime-dependent advantage

In Wednesday and DDoS, QK-MMD ZZ mainly improves adaptation efficiency. In PortScan, it improves downstream performance but requires more readaptations. This should be presented as regime-dependent behavior, not inconsistency.

### 3. Benign/non-adversarial drift

Benign-only controls do not support the claim that QK-MMD ZZ universally suppresses nuisance triggers. In Wednesday BENIGN, QK-MMD ZZ triggers more often than Energy, MMD-RBF, and KS-max. This must be reported as a limitation and as motivation for cost-sensitive actionability.

### 4. Actionable utility

When readaptation cost is meaningful and runtime cost is not dominant, QK-MMD ZZ can remain preferable even after nuisance-trigger penalties. When runtime is heavily penalized, Energy distance remains a very strong classical baseline.

## Claims supported

1. Triggered readaptation reduces degradation relative to no adaptation.
2. QK-MMD ZZ is competitive with strong classical distributional baselines across multiple CICIDS2017 drift regimes.
3. QK-MMD ZZ provides fewer readaptations and higher adaptation efficiency in Wednesday and DDoS.
4. QK-MMD ZZ significantly improves downstream performance in PortScan.
5. QK-MMD ZZ does not universally reduce benign nuisance triggers.
6. QK-MMD ZZ has substantially higher monitoring runtime.
7. Cost-sensitive actionable utility can favor QK-MMD ZZ when readaptation is expensive relative to monitoring.

## Claims to avoid

1. Universal quantum advantage.
2. QK-MMD always detects earlier.
3. QK-MMD always improves downstream accuracy.
4. QK-MMD is computationally cheaper.
5. QK-MMD filters benign drift better in general.
6. Every benign drift trigger is a false alarm.

## Recommended title

Quantum-Kernel MMD for Cost-Sensitive Actionable Drift Monitoring in Adaptive Intrusion Detection

Alternative:

Regime-Dependent Quantum-Kernel Drift Monitoring for Adaptive Intrusion Detection under Adversarial and Benign Distribution Shift

## Recommended abstract direction

The abstract should emphasize progressive drift, adaptive IDS readaptation, strong classical baselines, nuisance benign controls, and cost-sensitive actionable utility. It should explicitly avoid claiming universal quantum advantage.

## Recommended next step

Stop adding new experiments for now. The next step should be paper structuring: define research questions, map each experiment to a research question, and draft the Results narrative around operational trade-offs.
