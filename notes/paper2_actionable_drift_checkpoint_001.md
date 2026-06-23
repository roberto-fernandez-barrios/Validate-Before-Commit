# Paper 2 actionable drift checkpoint 001

## Purpose

This checkpoint evaluates whether adversarial drift benefits remain useful after penalizing nuisance/non-adversarial triggers measured on benign-only streams.

## Component summary

         method    method_label  n_seeds  adversarial_gain_mean  adversarial_readaptations_mean  benign_nuisance_triggers_mean  nodrift_nuisance_triggers_mean  excess_nuisance_triggers_mean  excess_nuisance_triggers_clipped_mean  mean_balanced_accuracy  cumulative_error_area_mean  total_runtime_adv_plus_benign_mean
        mmd_rbf         MMD-RBF       30              11.397135                        4.100000                       0.700000                        0.633333                       0.066667                               0.366667                0.879904                   12.009635                            3.920187
         ks_max          KS-max       30              11.128385                        3.466667                       0.833333                        0.600000                       0.233333                               0.566667                0.877216                   12.278385                            0.422418
qk_mmd_pauli_xz  QK-MMD PauliXZ       30              11.254167                        3.200000                       1.133333                        0.666667                       0.466667                               0.566667                0.878474                   12.152604                           17.830375
energy_distance Energy distance       30              11.879167                        5.266667                       1.033333                        0.400000                       0.633333                               0.700000                0.884724                   11.527604                            0.118639
      qk_mmd_zz       QK-MMD ZZ       30              11.889323                        3.166667                       1.400000                        0.533333                       0.866667                               0.900000                0.884826                   11.517448                           16.697242
            jsd             JSD       30              11.505990                        3.600000                       1.633333                        0.600000                       1.033333                               1.133333                0.880992                   11.900781                            0.043274

## Strict positive actionable utility regions for QK-MMD ZZ

       baseline  lambda_cost  eta_cost  gamma_cost  nuisance_mode  mean_actionable_utility_diff_qk_minus_baseline  ci95_low  ci95_high  prob_diff_gt_0  qk_better_ci95
            JSD         0.10      2.00        0.00          total                                        0.893333  0.017432   1.757051        0.700000            True
        MMD-RBF         0.25      0.00        0.00          total                                        0.725521  0.076276   1.527350        0.533333            True
         KS-max         0.25      0.00        0.00          total                                        0.835938  0.056504   1.934388        0.633333            True
            JSD         0.25      1.00        0.00          total                                        0.725000  0.052344   1.470592        0.666667            True
            JSD         0.25      2.00        0.00          total                                        0.958333  0.080990   1.827350        0.700000            True
Energy distance         0.50      0.00        0.00          total                                        1.060156  0.415605   1.759388        0.700000            True
        MMD-RBF         0.50      0.00        0.00          total                                        0.958854  0.307526   1.752350        0.600000            True
         KS-max         0.50      0.00        0.00          total                                        0.910937  0.152077   1.983646        0.633333            True
Energy distance         0.50      0.00        0.01          total                                        0.894370  0.248690   1.593915        0.700000            True
        MMD-RBF         0.50      0.00        0.01          total                                        0.831084  0.178971   1.624078        0.566667            True
Energy distance         0.50      0.25        0.00          total                                        0.968490  0.336979   1.652624        0.666667            True
        MMD-RBF         0.50      0.25        0.00          total                                        0.783854  0.148958   1.572409        0.633333            True
            JSD         0.50      0.25        0.00          total                                        0.658333  0.006504   1.509134        0.633333            True
Energy distance         0.50      0.25        0.01          total                                        0.802704  0.171016   1.487666        0.666667            True
        MMD-RBF         0.50      0.25        0.01          total                                        0.656084  0.021128   1.443949        0.600000            True
Energy distance         0.50      0.50        0.00          total                                        0.876823  0.240859   1.572168        0.733333            True
            JSD         0.50      0.50        0.00          total                                        0.716667  0.072135   1.526569        0.600000            True
Energy distance         0.50      0.50        0.01          total                                        0.711037  0.074019   1.406277        0.666667            True
Energy distance         0.50      1.00        0.00          total                                        0.693490  0.011198   1.426595        0.600000            True
            JSD         0.50      1.00        0.00          total                                        0.833333  0.149993   1.594544        0.666667            True
            JSD         0.50      2.00        0.00          total                                        1.066667  0.185391   1.936986        0.700000            True
            JSD         0.50      2.00        0.01          total                                        0.900127  0.019500   1.770531        0.666667            True
Energy distance         1.00      0.00        0.00          total                                        2.110156  1.350514   2.884648        0.900000            True
        MMD-RBF         1.00      0.00        0.00          total                                        1.425521  0.746328   2.219277        0.800000            True
         KS-max         1.00      0.00        0.00          total                                        1.060938  0.316406   2.094805        0.700000            True
            JSD         1.00      0.00        0.00          total                                        0.816667  0.095046   1.768750        0.700000            True
Energy distance         1.00      0.00        0.01          total                                        1.944370  1.184273   2.719432        0.866667            True
        MMD-RBF         1.00      0.00        0.01          total                                        1.297750  0.617485   2.091273        0.766667            True
         KS-max         1.00      0.00        0.01          total                                        0.898189  0.154285   1.930854        0.666667            True
Energy distance         1.00      0.00        0.05          total                                        1.281226  0.519405   2.059945        0.766667            True
        MMD-RBF         1.00      0.00        0.05          total                                        0.786668  0.106367   1.579128        0.600000            True
Energy distance         1.00      0.25        0.00          total                                        2.018490  1.274987   2.782038        0.900000            True
        MMD-RBF         1.00      0.25        0.00          total                                        1.250521  0.586452   2.034681        0.800000            True
         KS-max         1.00      0.25        0.00          total                                        0.919271  0.152057   1.997676        0.666667            True
            JSD         1.00      0.25        0.00          total                                        0.875000  0.172904   1.769271        0.700000            True
Energy distance         1.00      0.25        0.01          total                                        1.852704  1.108561   2.616522        0.833333            True
        MMD-RBF         1.00      0.25        0.01          total                                        1.122750  0.458766   1.906669        0.766667            True
            JSD         1.00      0.25        0.01          total                                        0.708460  0.006408   1.603005        0.666667            True
Energy distance         1.00      0.25        0.05          total                                        1.189559  0.442645   1.952811        0.800000            True
Energy distance         1.00      0.50        0.00          total                                        1.926823  1.174473   2.689850        0.866667            True
        MMD-RBF         1.00      0.50        0.00          total                                        1.075521  0.423958   1.863294        0.700000            True
            JSD         1.00      0.50        0.00          total                                        0.933333  0.237214   1.784909        0.700000            True
Energy distance         1.00      0.50        0.01          total                                        1.761037  1.007733   2.525044        0.833333            True
        MMD-RBF         1.00      0.50        0.01          total                                        0.947750  0.296628   1.734067        0.666667            True
            JSD         1.00      0.50        0.01          total                                        0.766794  0.070862   1.618297        0.666667            True
Energy distance         1.00      0.50        0.05          total                                        1.097893  0.341512   1.865034        0.766667            True
Energy distance         1.00      1.00        0.00          total                                        1.743490  0.953874   2.550000        0.766667            True
        MMD-RBF         1.00      1.00        0.00          total                                        0.725521  0.047637   1.555286        0.600000            True
            JSD         1.00      1.00        0.00          total                                        1.050000  0.328372   1.851595        0.733333            True
Energy distance         1.00      1.00        0.01          total                                        1.577704  0.787362   2.384202        0.733333            True
            JSD         1.00      1.00        0.01          total                                        0.883460  0.161277   1.684971        0.700000            True
Energy distance         1.00      1.00        0.05          total                                        0.914559  0.122866   1.721032        0.700000            True
Energy distance         1.00      2.00        0.00          total                                        1.376823  0.409896   2.375521        0.700000            True
            JSD         1.00      2.00        0.00          total                                        1.283333  0.371849   2.174746        0.766667            True
Energy distance         1.00      2.00        0.01          total                                        1.211037  0.243781   2.209801        0.666667            True
            JSD         1.00      2.00        0.01          total                                        1.116794  0.205931   2.008214        0.733333            True
Energy distance         2.00      0.00        0.00          total                                        4.210156  3.167402   5.198451        0.966667            True
        MMD-RBF         2.00      0.00        0.00          total                                        2.358854  1.543991   3.237513        0.800000            True
         KS-max         2.00      0.00        0.00          total                                        1.360937  0.564811   2.345586        0.700000            True
            JSD         2.00      0.00        0.00          total                                        1.250000  0.385671   2.310716        0.733333            True
Energy distance         2.00      0.00        0.01          total                                        4.044370  3.000050   5.032955        0.966667            True
        MMD-RBF         2.00      0.00        0.01          total                                        2.231084  1.415225   3.111062        0.766667            True
         KS-max         2.00      0.00        0.01          total                                        1.198189  0.402226   2.182631        0.666667            True
            JSD         2.00      0.00        0.01          total                                        1.083460  0.218753   2.143637        0.700000            True
Energy distance         2.00      0.00        0.05          total                                        3.381226  2.333741   4.371200        0.933333            True
        MMD-RBF         2.00      0.00        0.05          total                                        1.720001  0.906367   2.598796        0.766667            True
Energy distance         2.00      0.00        0.10          total                                        2.552296  1.501020   3.543982        0.866667            True
        MMD-RBF         2.00      0.00        0.10          total                                        1.081149  0.267977   1.960105        0.733333            True
Energy distance         2.00      0.25        0.00          total                                        4.118490  3.084857   5.101862        0.966667            True
        MMD-RBF         2.00      0.25        0.00          total                                        2.183854  1.390872   3.046882        0.833333            True
         KS-max         2.00      0.25        0.00          total                                        1.219271  0.402839   2.254701        0.666667            True
            JSD         2.00      0.25        0.00          total                                        1.308333  0.470827   2.322402        0.733333            True
Energy distance         2.00      0.25        0.01          total                                        3.952704  2.918059   4.936924        0.966667            True
        MMD-RBF         2.00      0.25        0.01          total                                        2.056084  1.262760   2.919618        0.800000            True
         KS-max         2.00      0.25        0.01          total                                        1.056523  0.240555   2.091853        0.666667            True
            JSD         2.00      0.25        0.01          total                                        1.141794  0.304469   2.156018        0.700000            True
Energy distance         2.00      0.25        0.05          total                                        3.289559  2.248633   4.275037        0.933333            True
        MMD-RBF         2.00      0.25        0.05          total                                        1.545001  0.751041   2.408636        0.766667            True
Energy distance         2.00      0.25        0.10          total                                        2.460629  1.415477   3.448292        0.833333            True
        MMD-RBF         2.00      0.25        0.10          total                                        0.906149  0.113812   1.767586        0.700000            True
Energy distance         2.00      0.50        0.00          total                                        4.026823  2.990625   5.023711        0.966667            True
        MMD-RBF         2.00      0.50        0.00          total                                        2.008854  1.233822   2.861732        0.833333            True
         KS-max         2.00      0.50        0.00          total                                        1.077604  0.227318   2.161992        0.600000            True
            JSD         2.00      0.50        0.00          total                                        1.366667  0.538021   2.330475        0.733333            True
Energy distance         2.00      0.50        0.01          total                                        3.861037  2.825239   4.858530        0.966667            True
        MMD-RBF         2.00      0.50        0.01          total                                        1.881084  1.105631   2.733992        0.800000            True
         KS-max         2.00      0.50        0.01          total                                        0.914856  0.066096   1.998357        0.600000            True
            JSD         2.00      0.50        0.01          total                                        1.200127  0.371441   2.163802        0.700000            True
Energy distance         2.00      0.50        0.05          total                                        3.197893  2.160624   4.197822        0.933333            True
        MMD-RBF         2.00      0.50        0.05          total                                        1.370001  0.593494   2.221924        0.766667            True
Energy distance         2.00      0.50        0.10          total                                        2.368963  1.330462   3.371223        0.833333            True
Energy distance         2.00      1.00        0.00          total                                        3.843490  2.787988   4.868783        0.966667            True
        MMD-RBF         2.00      1.00        0.00          total                                        1.658854  0.874212   2.537812        0.833333            True
            JSD         2.00      1.00        0.00          total                                        1.483333  0.634889   2.391693        0.766667            True
Energy distance         2.00      1.00        0.01          total                                        3.677704  2.621813   4.702972        0.966667            True
        MMD-RBF         2.00      1.00        0.01          total                                        1.531084  0.746344   2.409705        0.766667            True
            JSD         2.00      1.00        0.01          total                                        1.316794  0.468866   2.225213        0.733333            True
Energy distance         2.00      1.00        0.05          total                                        3.014559  1.956074   4.043558        0.866667            True
        MMD-RBF         2.00      1.00        0.05          total                                        1.020001  0.235393   1.899430        0.700000            True
Energy distance         2.00      1.00        0.10          total                                        2.185629  1.122504   3.217075        0.800000            True
Energy distance         2.00      2.00        0.00          total                                        3.476823  2.277214   4.661725        0.833333            True
        MMD-RBF         2.00      2.00        0.00          total                                        0.958854  0.050781   1.959922        0.633333            True
            JSD         2.00      2.00        0.00          total                                        1.716667  0.721868   2.687005        0.766667            True
Energy distance         2.00      2.00        0.01          total                                        3.311037  2.111887   4.495778        0.833333            True
            JSD         2.00      2.00        0.01          total                                        1.550127  0.556602   2.520197        0.733333            True
Energy distance         2.00      2.00        0.05          total                                        2.647893  1.447383   3.832600        0.800000            True
Energy distance         2.00      2.00        0.10          total                                        1.818963  0.615105   3.000922        0.700000            True
        MMD-RBF         0.25      0.00        0.00 excess_clipped                                        0.725521  0.076276   1.527350        0.533333            True
         KS-max         0.25      0.00        0.00 excess_clipped                                        0.835938  0.056504   1.934388        0.633333            True
Energy distance         0.50      0.00        0.00 excess_clipped                                        1.060156  0.415605   1.759388        0.700000            True
        MMD-RBF         0.50      0.00        0.00 excess_clipped                                        0.958854  0.307526   1.752350        0.600000            True
         KS-max         0.50      0.00        0.00 excess_clipped                                        0.910937  0.152077   1.983646        0.633333            True
Energy distance         0.50      0.00        0.01 excess_clipped                                        0.894370  0.248690   1.593915        0.700000            True
        MMD-RBF         0.50      0.00        0.01 excess_clipped                                        0.831084  0.178971   1.624078        0.566667            True
Energy distance         0.50      0.25        0.00 excess_clipped                                        1.010156  0.379661   1.694531        0.666667            True
        MMD-RBF         0.50      0.25        0.00 excess_clipped                                        0.825521  0.190820   1.616185        0.566667            True
         KS-max         0.50      0.25        0.00 excess_clipped                                        0.827604  0.031491   1.973184        0.600000            True
Energy distance         0.50      0.25        0.01 excess_clipped                                        0.844370  0.212368   1.527873        0.666667            True
        MMD-RBF         0.50      0.25        0.01 excess_clipped                                        0.697750  0.063503   1.488780        0.566667            True
Energy distance         0.50      0.50        0.00 excess_clipped                                        0.960156  0.321868   1.644277        0.700000            True
        MMD-RBF         0.50      0.50        0.00 excess_clipped                                        0.692187  0.052344   1.485215        0.533333            True
            JSD         0.50      0.50        0.00 excess_clipped                                        0.716667  0.047643   1.560690        0.600000            True
Energy distance         0.50      0.50        0.01 excess_clipped                                        0.794370  0.155374   1.478903        0.666667            True
Energy distance         0.50      1.00        0.00 excess_clipped                                        0.860156  0.176523   1.594290        0.666667            True
            JSD         0.50      1.00        0.00 excess_clipped                                        0.833333  0.095820   1.665137        0.633333            True
Energy distance         0.50      1.00        0.01 excess_clipped                                        0.694370  0.010084   1.428821        0.666667            True
            JSD         0.50      2.00        0.00 excess_clipped                                        1.066667  0.040365   2.044030        0.633333            True
Energy distance         1.00      0.00        0.00 excess_clipped                                        2.110156  1.350514   2.884648        0.900000            True
        MMD-RBF         1.00      0.00        0.00 excess_clipped                                        1.425521  0.746328   2.219277        0.800000            True
         KS-max         1.00      0.00        0.00 excess_clipped                                        1.060938  0.316406   2.094805        0.700000            True
            JSD         1.00      0.00        0.00 excess_clipped                                        0.816667  0.095046   1.768750        0.700000            True
Energy distance         1.00      0.00        0.01 excess_clipped                                        1.944370  1.184273   2.719432        0.866667            True
        MMD-RBF         1.00      0.00        0.01 excess_clipped                                        1.297750  0.617485   2.091273        0.766667            True
         KS-max         1.00      0.00        0.01 excess_clipped                                        0.898189  0.154285   1.930854        0.666667            True
Energy distance         1.00      0.00        0.05 excess_clipped                                        1.281226  0.519405   2.059945        0.766667            True
        MMD-RBF         1.00      0.00        0.05 excess_clipped                                        0.786668  0.106367   1.579128        0.600000            True
Energy distance         1.00      0.25        0.00 excess_clipped                                        2.060156  1.310391   2.817988        0.900000            True
        MMD-RBF         1.00      0.25        0.00 excess_clipped                                        1.292188  0.632799   2.078145        0.766667            True
         KS-max         1.00      0.25        0.00 excess_clipped                                        0.977604  0.190352   2.085697        0.666667            True
            JSD         1.00      0.25        0.00 excess_clipped                                        0.875000  0.169258   1.793496        0.666667            True
Energy distance         1.00      0.25        0.01 excess_clipped                                        1.894370  1.144073   2.652131        0.900000            True
        MMD-RBF         1.00      0.25        0.01 excess_clipped                                        1.164417  0.505461   1.949841        0.766667            True
         KS-max         1.00      0.25        0.01 excess_clipped                                        0.814856  0.028173   1.922633        0.666667            True
            JSD         1.00      0.25        0.01 excess_clipped                                        0.708460  0.002864   1.627366        0.633333            True
Energy distance         1.00      0.25        0.05 excess_clipped                                        1.231226  0.480579   1.991538        0.766667            True
Energy distance         1.00      0.50        0.00 excess_clipped                                        2.010156  1.266647   2.773184        0.900000            True
        MMD-RBF         1.00      0.50        0.00 excess_clipped                                        1.158854  0.512487   1.951589        0.733333            True
         KS-max         1.00      0.50        0.00 excess_clipped                                        0.894271  0.047376   2.080736        0.666667            True
            JSD         1.00      0.50        0.00 excess_clipped                                        0.933333  0.222917   1.826823        0.666667            True
Energy distance         1.00      0.50        0.01 excess_clipped                                        1.844370  1.100920   2.608533        0.866667            True
        MMD-RBF         1.00      0.50        0.01 excess_clipped                                        1.031084  0.385078   1.822913        0.733333            True
            JSD         1.00      0.50        0.01 excess_clipped                                        0.766794  0.057099   1.660130        0.666667            True
Energy distance         1.00      0.50        0.05 excess_clipped                                        1.181226  0.435956   1.945227        0.766667            True
Energy distance         1.00      1.00        0.00 excess_clipped                                        1.910156  1.133561   2.717467        0.866667            True
        MMD-RBF         1.00      1.00        0.00 excess_clipped                                        0.892188  0.229941   1.704694        0.666667            True
            JSD         1.00      1.00        0.00 excess_clipped                                        1.050000  0.280202   1.928385        0.700000            True
Energy distance         1.00      1.00        0.01 excess_clipped                                        1.744370  0.967029   2.551079        0.866667            True
        MMD-RBF         1.00      1.00        0.01 excess_clipped                                        0.764417  0.103014   1.575484        0.633333            True
            JSD         1.00      1.00        0.01 excess_clipped                                        0.883460  0.114148   1.760920        0.700000            True
Energy distance         1.00      1.00        0.05 excess_clipped                                        1.081226  0.300862   1.889181        0.766667            True
Energy distance         1.00      2.00        0.00 excess_clipped                                        1.710156  0.743229   2.733079        0.800000            True
            JSD         1.00      2.00        0.00 excess_clipped                                        1.283333  0.251543   2.286204        0.666667            True
Energy distance         1.00      2.00        0.01 excess_clipped                                        1.544370  0.577498   2.566864        0.766667            True
            JSD         1.00      2.00        0.01 excess_clipped                                        1.116794  0.085680   2.119589        0.666667            True
Energy distance         2.00      0.00        0.00 excess_clipped                                        4.210156  3.167402   5.198451        0.966667            True
        MMD-RBF         2.00      0.00        0.00 excess_clipped                                        2.358854  1.543991   3.237513        0.800000            True
         KS-max         2.00      0.00        0.00 excess_clipped                                        1.360937  0.564811   2.345586        0.700000            True
            JSD         2.00      0.00        0.00 excess_clipped                                        1.250000  0.385671   2.310716        0.733333            True
Energy distance         2.00      0.00        0.01 excess_clipped                                        4.044370  3.000050   5.032955        0.966667            True
        MMD-RBF         2.00      0.00        0.01 excess_clipped                                        2.231084  1.415225   3.111062        0.766667            True
         KS-max         2.00      0.00        0.01 excess_clipped                                        1.198189  0.402226   2.182631        0.666667            True
            JSD         2.00      0.00        0.01 excess_clipped                                        1.083460  0.218753   2.143637        0.700000            True
Energy distance         2.00      0.00        0.05 excess_clipped                                        3.381226  2.333741   4.371200        0.933333            True
        MMD-RBF         2.00      0.00        0.05 excess_clipped                                        1.720001  0.906367   2.598796        0.766667            True
Energy distance         2.00      0.00        0.10 excess_clipped                                        2.552296  1.501020   3.543982        0.866667            True
        MMD-RBF         2.00      0.00        0.10 excess_clipped                                        1.081149  0.267977   1.960105        0.733333            True
Energy distance         2.00      0.25        0.00 excess_clipped                                        4.160156  3.124212   5.146100        0.966667            True
        MMD-RBF         2.00      0.25        0.00 excess_clipped                                        2.225521  1.439811   3.084115        0.800000            True
         KS-max         2.00      0.25        0.00 excess_clipped                                        1.277604  0.426035   2.326068        0.666667            True
            JSD         2.00      0.25        0.00 excess_clipped                                        1.308333  0.462500   2.339870        0.700000            True
Energy distance         2.00      0.25        0.01 excess_clipped                                        3.994370  2.957853   4.980603        0.966667            True
        MMD-RBF         2.00      0.25        0.01 excess_clipped                                        2.097750  1.312300   2.955261        0.800000            True
         KS-max         2.00      0.25        0.01 excess_clipped                                        1.114856  0.263722   2.163725        0.666667            True
            JSD         2.00      0.25        0.01 excess_clipped                                        1.141794  0.296041   2.174396        0.666667            True
Energy distance         2.00      0.25        0.05 excess_clipped                                        3.331226  2.289768   4.318551        0.933333            True
        MMD-RBF         2.00      0.25        0.05 excess_clipped                                        1.586668  0.800985   2.442654        0.766667            True
Energy distance         2.00      0.25        0.10 excess_clipped                                        2.502296  1.458345   3.489669        0.833333            True
        MMD-RBF         2.00      0.25        0.10 excess_clipped                                        0.947815  0.162248   1.803449        0.733333            True
Energy distance         2.00      0.50        0.00 excess_clipped                                        4.110156  3.080951   5.105215        0.966667            True
        MMD-RBF         2.00      0.50        0.00 excess_clipped                                        2.092188  1.320527   2.950801        0.800000            True
         KS-max         2.00      0.50        0.00 excess_clipped                                        1.194271  0.285918   2.320859        0.666667            True
            JSD         2.00      0.50        0.00 excess_clipped                                        1.366667  0.520039   2.376842        0.666667            True
Energy distance         2.00      0.50        0.01 excess_clipped                                        3.944370  2.913925   4.939179        0.966667            True
        MMD-RBF         2.00      0.50        0.01 excess_clipped                                        1.964417  1.192102   2.821929        0.800000            True
         KS-max         2.00      0.50        0.01 excess_clipped                                        1.031523  0.124276   2.157576        0.600000            True
            JSD         2.00      0.50        0.01 excess_clipped                                        1.200127  0.353434   2.210172        0.666667            True
Energy distance         2.00      0.50        0.05 excess_clipped                                        3.281226  2.247381   4.277243        0.900000            True
        MMD-RBF         2.00      0.50        0.05 excess_clipped                                        1.453335  0.680781   2.309805        0.766667            True
Energy distance         2.00      0.50        0.10 excess_clipped                                        2.452296  1.415918   3.448004        0.833333            True
        MMD-RBF         2.00      0.50        0.10 excess_clipped                                        0.814482  0.040904   1.668558        0.666667            True
Energy distance         2.00      1.00        0.00 excess_clipped                                        4.010156  2.965365   5.035417        0.933333            True
        MMD-RBF         2.00      1.00        0.00 excess_clipped                                        1.825521  1.063249   2.682311        0.833333            True
            JSD         2.00      1.00        0.00 excess_clipped                                        1.483333  0.592422   2.470332        0.733333            True
Energy distance         2.00      1.00        0.01 excess_clipped                                        3.844370  2.800309   4.868868        0.933333            True
        MMD-RBF         2.00      1.00        0.01 excess_clipped                                        1.697750  0.935929   2.555122        0.833333            True
            JSD         2.00      1.00        0.01 excess_clipped                                        1.316794  0.425269   2.304254        0.733333            True
Energy distance         2.00      1.00        0.05 excess_clipped                                        3.181226  2.133461   4.209244        0.933333            True
        MMD-RBF         2.00      1.00        0.05 excess_clipped                                        1.186668  0.426014   2.042398        0.733333            True
Energy distance         2.00      1.00        0.10 excess_clipped                                        2.352296  1.302055   3.382040        0.800000            True
Energy distance         2.00      2.00        0.00 excess_clipped                                        3.810156  2.659896   5.004193        0.900000            True
        MMD-RBF         2.00      2.00        0.00 excess_clipped                                        1.292188  0.441348   2.251569        0.733333            True
            JSD         2.00      2.00        0.00 excess_clipped                                        1.716667  0.598132   2.826042        0.733333            True
Energy distance         2.00      2.00        0.01 excess_clipped                                        3.644370  2.493294   4.838837        0.900000            True
        MMD-RBF         2.00      2.00        0.01 excess_clipped                                        1.164417  0.313722   2.123331        0.733333            True
            JSD         2.00      2.00        0.01 excess_clipped                                        1.550127  0.431553   2.658588        0.733333            True
Energy distance         2.00      2.00        0.05 excess_clipped                                        2.981226  1.826990   4.174688        0.833333            True
Energy distance         2.00      2.00        0.10 excess_clipped                                        2.152296  0.995679   3.344280        0.766667            True

## Interpretation guardrail

The benign control does not support the claim that QK-MMD ZZ universally reduces nuisance triggers. Its value must therefore be framed through cost-sensitive actionable utility rather than benign-trigger suppression alone.
