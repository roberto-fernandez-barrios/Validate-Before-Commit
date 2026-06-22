# Paper 2 progressive classical baselines checkpoint 001

## Purpose

This checkpoint extends the progressive drift readaptation experiment with additional classical distributional baselines:

- KS-max
- JSD
- Energy distance

The goal is to test whether QK-MMD ZZ remains competitive beyond MMD-RBF.

## Summary ranking by cumulative degradation

   method_label  n_seeds  mean_balanced_accuracy  cumulative_error_area_mean  cumulative_gain_vs_no_adapt_mean  n_adaptations_mean  adaptation_efficiency_mean  detector_runtime_sec_total_mean
      QK-MMD ZZ       30                0.884826                   11.517448                         11.889323            3.166667                    3.880794                         6.048713
Energy distance       30                0.884724                   11.527604                         11.879167            5.266667                    2.328859                         0.053273
            JSD       30                0.880992                   11.900781                         11.505990            3.600000                    3.282682                         0.021458
        MMD-RBF       30                0.879904                   12.009635                         11.397135            4.100000                    2.806254                         1.638038
 QK-MMD PauliXZ       30                0.878474                   12.152604                         11.254167            3.200000                    3.573351                         6.416026
         KS-max       30                0.877216                   12.278385                         11.128385            3.466667                    3.264175                         0.202530
  No adaptation       30                0.765932                   23.406771                          0.000000            0.000000                         NaN                         0.000000

## Key paired comparisons

       method_a        method_b                      metric  n_pairs  mean_diff_a_minus_b  ci95_low  ci95_high  prob_diff_gt_0                         positive_means
      QK-MMD ZZ Energy distance      mean_balanced_accuracy       30             0.000102 -0.005654   0.006521        0.400000              QK-MMD ZZ better accuracy
Energy distance       QK-MMD ZZ       cumulative_error_area       30             0.010156 -0.565404   0.652109        0.400000            QK-MMD ZZ lower degradation
      QK-MMD ZZ Energy distance cumulative_gain_vs_no_adapt       30             0.010156 -0.565404   0.652109        0.400000                  QK-MMD ZZ higher gain
Energy distance       QK-MMD ZZ               n_adaptations       30             2.100000  1.733333   2.433333        0.966667          QK-MMD ZZ fewer readaptations
      QK-MMD ZZ Energy distance       adaptation_efficiency       30             1.551936  1.168571   1.955149        0.966667 QK-MMD ZZ better adaptation efficiency
      QK-MMD ZZ Energy distance  detector_runtime_sec_total       30             5.995440  5.917411   6.076280        1.000000               QK-MMD ZZ more expensive
      QK-MMD ZZ             JSD      mean_balanced_accuracy       30             0.003833 -0.002688   0.012677        0.600000              QK-MMD ZZ better accuracy
            JSD       QK-MMD ZZ       cumulative_error_area       30             0.383333 -0.268757   1.267721        0.600000            QK-MMD ZZ lower degradation
      QK-MMD ZZ             JSD cumulative_gain_vs_no_adapt       30             0.383333 -0.268757   1.267721        0.600000                  QK-MMD ZZ higher gain
            JSD       QK-MMD ZZ               n_adaptations       30             0.433333  0.200000   0.666667        0.466667          QK-MMD ZZ fewer readaptations
      QK-MMD ZZ             JSD       adaptation_efficiency       30             0.598112  0.228491   1.001496        0.733333 QK-MMD ZZ better adaptation efficiency
      QK-MMD ZZ             JSD  detector_runtime_sec_total       30             6.027255  5.949252   6.107062        1.000000               QK-MMD ZZ more expensive
      QK-MMD ZZ         MMD-RBF      mean_balanced_accuracy       30             0.004922 -0.001675   0.013018        0.500000              QK-MMD ZZ better accuracy
        MMD-RBF       QK-MMD ZZ       cumulative_error_area       30             0.492188 -0.167454   1.301842        0.500000            QK-MMD ZZ lower degradation
      QK-MMD ZZ         MMD-RBF cumulative_gain_vs_no_adapt       30             0.492188 -0.167454   1.301842        0.500000                  QK-MMD ZZ higher gain
        MMD-RBF       QK-MMD ZZ               n_adaptations       30             0.933333  0.633333   1.200000        0.700000          QK-MMD ZZ fewer readaptations
      QK-MMD ZZ         MMD-RBF       adaptation_efficiency       30             1.074540  0.719711   1.448043        0.833333 QK-MMD ZZ better adaptation efficiency
      QK-MMD ZZ         MMD-RBF  detector_runtime_sec_total       30             4.410675  4.320250   4.492284        1.000000               QK-MMD ZZ more expensive

## Strict positive utility regions

       baseline  lambda_cost  gamma_cost  mean_utility_diff_qk_minus_baseline  ci95_low  ci95_high  prob_diff_gt_0  qk_better_ci95
         KS-max         0.25        0.00                             0.835938  0.056504   1.934388        0.633333            True
        MMD-RBF         0.25        0.00                             0.725521  0.076276   1.527350        0.533333            True
        MMD-RBF         0.25        0.01                             0.681414  0.032122   1.483351        0.533333            True
Energy distance         0.50        0.00                             1.060156  0.415605   1.759388        0.700000            True
         KS-max         0.50        0.00                             0.910937  0.152077   1.983646        0.633333            True
        MMD-RBF         0.50        0.00                             0.958854  0.307526   1.752350        0.600000            True
Energy distance         0.50        0.01                             1.000202  0.355457   1.699921        0.700000            True
         KS-max         0.50        0.01                             0.852476  0.093174   1.925460        0.600000            True
        MMD-RBF         0.50        0.01                             0.914747  0.263243   1.707483        0.600000            True
Energy distance         0.50        0.05                             0.760384  0.115562   1.461245        0.700000            True
        MMD-RBF         0.50        0.05                             0.738320  0.086651   1.531136        0.533333            True
Energy distance         1.00        0.00                             2.110156  1.350514   2.884648        0.900000            True
            JSD         1.00        0.00                             0.816667  0.095046   1.768750        0.700000            True
         KS-max         1.00        0.00                             1.060938  0.316406   2.094805        0.700000            True
        MMD-RBF         1.00        0.00                             1.425521  0.746328   2.219277        0.800000            True
Energy distance         1.00        0.01                             2.050202  1.290179   2.824913        0.866667            True
            JSD         1.00        0.01                             0.756394  0.034950   1.708562        0.700000            True
         KS-max         1.00        0.01                             1.002476  0.258170   2.036559        0.666667            True
        MMD-RBF         1.00        0.01                             1.381414  0.701790   2.175141        0.800000            True
Energy distance         1.00        0.05                             1.810384  1.048911   2.585989        0.866667            True
         KS-max         1.00        0.05                             0.768628  0.024372   1.801517        0.666667            True
        MMD-RBF         1.00        0.05                             1.204987  0.523658   1.997479        0.700000            True
Energy distance         1.00        0.10                             1.510612  0.747366   2.287248        0.800000            True
        MMD-RBF         1.00        0.10                             0.984453  0.303707   1.776199        0.633333            True
Energy distance         2.00        0.00                             4.210156  3.167402   5.198451        0.966667            True
            JSD         2.00        0.00                             1.250000  0.385671   2.310716        0.733333            True
         KS-max         2.00        0.00                             1.360937  0.564811   2.345586        0.700000            True
        MMD-RBF         2.00        0.00                             2.358854  1.543991   3.237513        0.800000            True
Energy distance         2.00        0.01                             4.150202  3.106775   5.138724        0.966667            True
            JSD         2.00        0.01                             1.189727  0.325056   2.250118        0.733333            True
         KS-max         2.00        0.01                             1.302476  0.506257   2.287423        0.666667            True
        MMD-RBF         2.00        0.01                             2.314747  1.499488   3.193947        0.800000            True
Energy distance         2.00        0.05                             3.910384  2.865580   4.898956        0.933333            True
            JSD         2.00        0.05                             0.948637  0.083431   2.009584        0.700000            True
         KS-max         2.00        0.05                             1.068628  0.272070   2.053280        0.666667            True
        MMD-RBF         2.00        0.05                             2.138320  1.321475   3.017820        0.766667            True
Energy distance         2.00        0.10                             3.610612  2.563389   4.599411        0.933333            True
        MMD-RBF         2.00        0.10                             1.917787  1.101831   2.796624        0.766667            True
Energy distance         2.00        0.25                             2.711296  1.659171   3.702799        0.866667            True
        MMD-RBF         2.00        0.25                             1.256185  0.440599   2.131691        0.766667            True

## Main interpretation

QK-MMD ZZ matches the strongest classical distributional baseline (Energy distance) in downstream balanced accuracy, cumulative degradation, and cumulative gain, with no statistically conclusive difference in raw performance metrics.

However, QK-MMD ZZ requires significantly fewer readaptations than Energy distance and achieves significantly higher adaptation efficiency. This comes at substantially higher detector runtime.

The cost-sensitive utility analysis shows that QK-MMD ZZ becomes preferable to Energy distance when readaptation cost is non-negligible and runtime cost is not dominant.

## Claim enabled

Under progressive drift, QK-MMD ZZ is competitive with strong classical distributional baselines and provides a favorable operational trade-off when readaptation cost is explicitly modeled.
