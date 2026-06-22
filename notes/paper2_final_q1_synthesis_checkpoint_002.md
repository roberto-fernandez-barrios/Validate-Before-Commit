# Paper 2 final Q1-oriented synthesis checkpoint 002

## Executive summary

This checkpoint updates the Paper 2 synthesis after adding strong classical distributional baselines to the progressive drift readaptation experiment.

The final defensible story is not universal quantum advantage. The strongest claim is that QK-MMD provides regime-dependent monitoring advantages and, under progressive drift, QK-MMD ZZ matches the best classical distributional baseline in downstream performance while requiring significantly fewer readaptations and achieving significantly higher adaptation efficiency.

The cost-sensitive utility analysis further shows that QK-MMD ZZ becomes preferable when readaptation costs are non-negligible, despite higher monitoring runtime.

This significantly strengthens the Q1 positioning because the paper no longer depends only on comparison against MMD-RBF.

## Final core claim

Under progressive drift, QK-MMD ZZ is competitive with strong classical distributional baselines and provides a favorable operational trade-off when readaptation cost is explicitly modeled.

More precisely:

QK-MMD ZZ matches Energy distance in downstream balanced accuracy, cumulative degradation, and cumulative gain, but requires significantly fewer readaptations and achieves significantly higher gain per readaptation.

## What changed since checkpoint 001

Checkpoint 001 compared QK-MMD mainly against MMD-RBF.

Checkpoint 002 adds:

1. KS-max detector.
2. Histogram Jensen-Shannon divergence detector.
3. Energy-distance detector.
4. Paired comparisons between QK-MMD ZZ and all baselines.
5. Cost-sensitive utility against all baselines.

The key result is that Energy distance is a very strong classical baseline, but QK-MMD ZZ remains competitive and uses substantially fewer readaptations.

## Evidence block 1: controlled streaming

Controlled streaming remains the main evidence that QK-MMD has regime-dependent monitoring sensitivity, especially under moderate-to-severe drift.

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

Interpretation: QK-MMD improves monitoring sensitivity in moderate-to-severe drift regimes, but the paper should not claim universal earlier detection.

## Evidence block 2: single-change downstream adaptation

Single-change downstream adaptation shows that triggered adaptation is useful, but QK-MMD does not robustly improve final downstream accuracy over MMD-RBF when both trigger adaptation in similar windows.

 severity                             strategy  post_balanced_accuracy_mean  degradation_area_mean  adaptation_gain_vs_no_adapt_mean  false_alarm_any_rate
     0.10         mmd_rbf_triggered_adaptation                     0.919141               0.023997                          0.001901              0.033333
     0.10                        no_adaptation                     0.917240               0.025898                          0.000000              0.000000
     0.10                    oracle_adaptation                     0.940495               0.000000                          0.023255              0.000000
     0.10 qk_mmd_pauli_xz_triggered_adaptation                     0.918763               0.024375                          0.001523              0.066667
     0.10       qk_mmd_zz_triggered_adaptation                     0.919115               0.024023                          0.001875              0.066667
     0.25         mmd_rbf_triggered_adaptation                     0.904740               0.025091                          0.042995              0.000000
     0.25                        no_adaptation                     0.861745               0.068906                          0.000000              0.000000
     0.25                    oracle_adaptation                     0.929688               0.000000                          0.067943              0.000000
     0.25 qk_mmd_pauli_xz_triggered_adaptation                     0.885065               0.045586                          0.023320              0.033333
     0.25       qk_mmd_zz_triggered_adaptation                     0.884922               0.045729                          0.023177              0.033333
     0.50         mmd_rbf_triggered_adaptation                     0.893997               0.021380                          0.126706              0.000000
     0.50                        no_adaptation                     0.767292               0.148086                          0.000000              0.000000
     0.50                    oracle_adaptation                     0.915378               0.000000                          0.148086              0.000000
     0.50 qk_mmd_pauli_xz_triggered_adaptation                     0.892930               0.022448                          0.125638              0.033333
     0.50       qk_mmd_zz_triggered_adaptation                     0.892682               0.022695                          0.125391              0.033333
     0.75         mmd_rbf_triggered_adaptation                     0.872096               0.035339                          0.197370              0.033333
     0.75                        no_adaptation                     0.674727               0.232708                          0.000000              0.000000
     0.75                    oracle_adaptation                     0.907435               0.000000                          0.232708              0.000000
     0.75 qk_mmd_pauli_xz_triggered_adaptation                     0.872096               0.035339                          0.197370              0.033333
     0.75       qk_mmd_zz_triggered_adaptation                     0.872096               0.035339                          0.197370              0.033333
     1.00         mmd_rbf_triggered_adaptation                     0.849219               0.046888                          0.268411              0.066667
     1.00                        no_adaptation                     0.580807               0.315299                          0.000000              0.000000
     1.00                    oracle_adaptation                     0.896107               0.000000                          0.315299              0.000000
     1.00 qk_mmd_pauli_xz_triggered_adaptation                     0.849219               0.046888                          0.268411              0.033333
     1.00       qk_mmd_zz_triggered_adaptation                     0.849219               0.046888                          0.268411              0.033333

Interpretation: the value of QK-MMD should not be framed as better retrained accuracy after a single drift event. The adaptation mechanism is the same SVC-RBF.

## Evidence block 3: long-stream validation

Long-stream validation showed that when MMD-RBF and QK-MMD trigger in the same window, downstream results converge.

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

Interpretation: the contribution is not simply earlier single-trigger adaptation, but monitoring behavior and scheduling efficiency under progressive drift.

## Evidence block 4: progressive drift without extra classical baselines

The original progressive drift experiment showed that QK-MMD ZZ improves adaptation efficiency over MMD-RBF, but absolute accuracy/degradation gains were not statistically conclusive.

  method_label  n_seeds  mean_balanced_accuracy  cumulative_error_area_mean  cumulative_gain_vs_no_adapt_mean  adaptation_efficiency_mean  n_adaptations_mean  detector_runtime_sec_total_mean
       MMD-RBF       30                0.874219                   12.578125                         14.674479                    3.345352            4.433333                         1.857428
 No adaptation       30                0.727474                   27.252604                          0.000000                         NaN            0.000000                         0.000000
QK-MMD PauliXZ       30                0.878063                   12.193750                         15.058854                    4.609310            3.333333                         6.410877
     QK-MMD ZZ       30                0.880297                   11.970313                         15.282292                    4.708746            3.333333                         5.986702

      method_a       method_b                      metric  n_pairs  mean_diff_a_minus_b  ci95_low  ci95_high         positive_means
     QK-MMD ZZ        MMD-RBF      mean_balanced_accuracy       30             0.006078 -0.001544   0.015383              QK better
       MMD-RBF      QK-MMD ZZ       cumulative_error_area       30             0.607812 -0.154440   1.538281              QK better
     QK-MMD ZZ        MMD-RBF cumulative_gain_vs_no_adapt       30             0.607812 -0.154440   1.538281              QK better
       MMD-RBF      QK-MMD ZZ               n_adaptations       30             1.100000  0.833333   1.366667 QK fewer readaptations
     QK-MMD ZZ        MMD-RBF  detector_runtime_sec_total       30             4.129274  4.077078   4.180054      QK more expensive
QK-MMD PauliXZ        MMD-RBF      mean_balanced_accuracy       30             0.003844 -0.005724   0.014055              QK better
       MMD-RBF QK-MMD PauliXZ       cumulative_error_area       30             0.384375 -0.572428   1.405495              QK better
QK-MMD PauliXZ        MMD-RBF cumulative_gain_vs_no_adapt       30             0.384375 -0.572428   1.405495              QK better
       MMD-RBF QK-MMD PauliXZ               n_adaptations       30             1.100000  0.833333   1.366667 QK fewer readaptations
QK-MMD PauliXZ        MMD-RBF  detector_runtime_sec_total       30             4.553449  4.493515   4.611672      QK more expensive

## Evidence block 5: progressive drift with classical baselines

This is the new key robustness block. It compares QK-MMD ZZ against Energy distance, JSD, KS-max, MMD-RBF, and QK-MMD PauliXZ under the same progressive readaptation protocol.

### Ranking by cumulative degradation

   method_label  n_seeds  mean_balanced_accuracy  cumulative_error_area_mean  cumulative_gain_vs_no_adapt_mean  n_adaptations_mean  adaptation_efficiency_mean  detector_runtime_sec_total_mean
      QK-MMD ZZ       30                0.884826                   11.517448                         11.889323            3.166667                    3.880794                         6.048713
Energy distance       30                0.884724                   11.527604                         11.879167            5.266667                    2.328859                         0.053273
            JSD       30                0.880992                   11.900781                         11.505990            3.600000                    3.282682                         0.021458
        MMD-RBF       30                0.879904                   12.009635                         11.397135            4.100000                    2.806254                         1.638038
 QK-MMD PauliXZ       30                0.878474                   12.152604                         11.254167            3.200000                    3.573351                         6.416026
         KS-max       30                0.877216                   12.278385                         11.128385            3.466667                    3.264175                         0.202530
  No adaptation       30                0.765932                   23.406771                          0.000000            0.000000                         NaN                         0.000000

### Key paired comparisons

       method_a        method_b                      metric  n_pairs  mean_diff_a_minus_b  ci95_low  ci95_high                         positive_means
      QK-MMD ZZ Energy distance      mean_balanced_accuracy       30             0.000102 -0.005654   0.006521              QK-MMD ZZ better accuracy
Energy distance       QK-MMD ZZ       cumulative_error_area       30             0.010156 -0.565404   0.652109            QK-MMD ZZ lower degradation
      QK-MMD ZZ Energy distance cumulative_gain_vs_no_adapt       30             0.010156 -0.565404   0.652109                  QK-MMD ZZ higher gain
Energy distance       QK-MMD ZZ               n_adaptations       30             2.100000  1.733333   2.433333          QK-MMD ZZ fewer readaptations
      QK-MMD ZZ Energy distance       adaptation_efficiency       30             1.551936  1.168571   1.955149 QK-MMD ZZ better adaptation efficiency
      QK-MMD ZZ Energy distance  detector_runtime_sec_total       30             5.995440  5.917411   6.076280               QK-MMD ZZ more expensive
      QK-MMD ZZ             JSD      mean_balanced_accuracy       30             0.003833 -0.002688   0.012677              QK-MMD ZZ better accuracy
            JSD       QK-MMD ZZ       cumulative_error_area       30             0.383333 -0.268757   1.267721            QK-MMD ZZ lower degradation
      QK-MMD ZZ             JSD cumulative_gain_vs_no_adapt       30             0.383333 -0.268757   1.267721                  QK-MMD ZZ higher gain
            JSD       QK-MMD ZZ               n_adaptations       30             0.433333  0.200000   0.666667          QK-MMD ZZ fewer readaptations
      QK-MMD ZZ             JSD       adaptation_efficiency       30             0.598112  0.228491   1.001496 QK-MMD ZZ better adaptation efficiency
      QK-MMD ZZ             JSD  detector_runtime_sec_total       30             6.027255  5.949252   6.107062               QK-MMD ZZ more expensive
      QK-MMD ZZ         MMD-RBF      mean_balanced_accuracy       30             0.004922 -0.001675   0.013018              QK-MMD ZZ better accuracy
        MMD-RBF       QK-MMD ZZ       cumulative_error_area       30             0.492188 -0.167454   1.301842            QK-MMD ZZ lower degradation
      QK-MMD ZZ         MMD-RBF cumulative_gain_vs_no_adapt       30             0.492188 -0.167454   1.301842                  QK-MMD ZZ higher gain
        MMD-RBF       QK-MMD ZZ               n_adaptations       30             0.933333  0.633333   1.200000          QK-MMD ZZ fewer readaptations
      QK-MMD ZZ         MMD-RBF       adaptation_efficiency       30             1.074540  0.719711   1.448043 QK-MMD ZZ better adaptation efficiency
      QK-MMD ZZ         MMD-RBF  detector_runtime_sec_total       30             4.410675  4.320250   4.492284               QK-MMD ZZ more expensive

Interpretation:

- QK-MMD ZZ and Energy distance are statistically tied in raw downstream performance metrics.
- QK-MMD ZZ requires significantly fewer readaptations than Energy distance.
- QK-MMD ZZ has significantly higher adaptation efficiency than Energy distance.
- QK-MMD ZZ has much higher detector runtime than Energy distance.

## Evidence block 6: cost-sensitive utility against all baselines

Utility is defined as `cumulative_gain_vs_no_adapt - lambda * n_adaptations - gamma * detector_runtime_sec_total`.

Strict positive utility regions indicate settings where QK-MMD ZZ has a positive bootstrap CI lower bound over the corresponding baseline.

       baseline  lambda_cost  gamma_cost  mean_utility_diff_qk_minus_baseline  ci95_low  ci95_high  qk_better_ci95
         KS-max         0.25        0.00                             0.835938  0.056504   1.934388            True
        MMD-RBF         0.25        0.00                             0.725521  0.076276   1.527350            True
        MMD-RBF         0.25        0.01                             0.681414  0.032122   1.483351            True
Energy distance         0.50        0.00                             1.060156  0.415605   1.759388            True
         KS-max         0.50        0.00                             0.910937  0.152077   1.983646            True
        MMD-RBF         0.50        0.00                             0.958854  0.307526   1.752350            True
Energy distance         0.50        0.01                             1.000202  0.355457   1.699921            True
         KS-max         0.50        0.01                             0.852476  0.093174   1.925460            True
        MMD-RBF         0.50        0.01                             0.914747  0.263243   1.707483            True
Energy distance         0.50        0.05                             0.760384  0.115562   1.461245            True
        MMD-RBF         0.50        0.05                             0.738320  0.086651   1.531136            True
Energy distance         1.00        0.00                             2.110156  1.350514   2.884648            True
            JSD         1.00        0.00                             0.816667  0.095046   1.768750            True
         KS-max         1.00        0.00                             1.060938  0.316406   2.094805            True
        MMD-RBF         1.00        0.00                             1.425521  0.746328   2.219277            True
Energy distance         1.00        0.01                             2.050202  1.290179   2.824913            True
            JSD         1.00        0.01                             0.756394  0.034950   1.708562            True
         KS-max         1.00        0.01                             1.002476  0.258170   2.036559            True
        MMD-RBF         1.00        0.01                             1.381414  0.701790   2.175141            True
Energy distance         1.00        0.05                             1.810384  1.048911   2.585989            True
         KS-max         1.00        0.05                             0.768628  0.024372   1.801517            True
        MMD-RBF         1.00        0.05                             1.204987  0.523658   1.997479            True
Energy distance         1.00        0.10                             1.510612  0.747366   2.287248            True
        MMD-RBF         1.00        0.10                             0.984453  0.303707   1.776199            True
Energy distance         2.00        0.00                             4.210156  3.167402   5.198451            True
            JSD         2.00        0.00                             1.250000  0.385671   2.310716            True
         KS-max         2.00        0.00                             1.360937  0.564811   2.345586            True
        MMD-RBF         2.00        0.00                             2.358854  1.543991   3.237513            True
Energy distance         2.00        0.01                             4.150202  3.106775   5.138724            True
            JSD         2.00        0.01                             1.189727  0.325056   2.250118            True
         KS-max         2.00        0.01                             1.302476  0.506257   2.287423            True
        MMD-RBF         2.00        0.01                             2.314747  1.499488   3.193947            True
Energy distance         2.00        0.05                             3.910384  2.865580   4.898956            True
            JSD         2.00        0.05                             0.948637  0.083431   2.009584            True
         KS-max         2.00        0.05                             1.068628  0.272070   2.053280            True
        MMD-RBF         2.00        0.05                             2.138320  1.321475   3.017820            True
Energy distance         2.00        0.10                             3.610612  2.563389   4.599411            True
        MMD-RBF         2.00        0.10                             1.917787  1.101831   2.796624            True
Energy distance         2.00        0.25                             2.711296  1.659171   3.702799            True
        MMD-RBF         2.00        0.25                             1.256185  0.440599   2.131691            True

Interpretation:

QK-MMD ZZ becomes preferable to Energy distance once readaptation cost is non-negligible, e.g. lambda >= 0.5 for low/moderate runtime penalty settings.

This supports the operational claim: QK-MMD ZZ is not necessarily cheaper or more accurate, but it can provide higher net utility when readaptation is costly.

## Runtime and cost caveat

QK-MMD is consistently more expensive in monitoring runtime. This must be explicitly framed as a trade-off rather than hidden.

 severity         method  detector_runtime_sec_mean  mmd_runtime_sec_mean  runtime_ratio_vs_mmd  extra_runtime_sec_vs_mmd  clean_gain_delta_vs_mmd  false_alarm_delta_vs_mmd
     0.10        MMD-RBF                   0.247183              0.247183              1.000000                  0.000000                 0.000000                  0.000000
     0.10 QK-MMD PauliXZ                   0.752132              0.247183              3.042808                  0.504949                -0.000039                  0.033333
     0.10      QK-MMD ZZ                   0.734601              0.247183              2.971886                  0.487418                 0.000312                  0.033333
     0.25        MMD-RBF                   0.246317              0.246317              1.000000                  0.000000                 0.000000                  0.000000
     0.25 QK-MMD PauliXZ                   0.752676              0.246317              3.055716                  0.506358                -0.022500                  0.033333
     0.25      QK-MMD ZZ                   0.729740              0.246317              2.962603                  0.483423                -0.022643                  0.033333
     0.50        MMD-RBF                   0.245229              0.245229              1.000000                  0.000000                 0.000000                  0.000000
     0.50 QK-MMD PauliXZ                   0.752046              0.245229              3.066714                  0.506818                -0.005208                  0.033333
     0.50      QK-MMD ZZ                   0.726707              0.245229              2.963383                  0.481478                -0.005456                  0.033333
     0.75        MMD-RBF                   0.238829              0.238829              1.000000                  0.000000                 0.000000                  0.000000
     0.75 QK-MMD PauliXZ                   0.748929              0.238829              3.135842                  0.510100                 0.000078                  0.000000
     0.75      QK-MMD ZZ                   0.731292              0.238829              3.061993                  0.492463                 0.000078                  0.000000
     1.00        MMD-RBF                   0.236456              0.236456              1.000000                  0.000000                 0.000000                  0.000000
     1.00 QK-MMD PauliXZ                   0.755854              0.236456              3.196596                  0.519398                 0.008529                 -0.033333
     1.00      QK-MMD ZZ                   0.734917              0.236456              3.108049                  0.498461                 0.008529                 -0.033333

## Supported claims

1. QK-MMD provides regime-dependent monitoring advantages under moderate-to-severe drift.
2. Triggered adaptation reduces downstream degradation compared with no adaptation.
3. QK-MMD does not universally dominate MMD-RBF or classical baselines in raw accuracy.
4. QK-MMD ZZ matches Energy distance in progressive downstream performance.
5. QK-MMD ZZ requires significantly fewer readaptations than Energy distance.
6. QK-MMD ZZ has significantly higher adaptation efficiency than Energy distance.
7. QK-MMD ZZ has higher monitoring runtime.
8. Cost-sensitive utility favors QK-MMD ZZ when readaptation cost is non-negligible.

## Claims to avoid

1. Universal quantum advantage.
2. QK-MMD always detects earlier.
3. QK-MMD significantly improves raw downstream accuracy over Energy distance.
4. QK-MMD is computationally cheaper.
5. Classical baselines are weak.

## Q1 readiness after classical baselines

The paper is now materially stronger than in checkpoint 001. The addition of Energy distance, JSD, and KS-max directly addresses the reviewer criticism that MMD-RBF alone is insufficient as a classical comparator.

The result is still not a universal quantum-advantage paper. It is better framed as an adaptive monitoring and operational utility paper.

Current readiness: Q1 possible and substantially better defended than before; Q2 strong if the target venue is highly skeptical of simulated quantum-kernel methods or requires multiple datasets.

## Final recommended paper narrative

This paper proposes quantum-kernel MMD as a regime-dependent drift monitoring mechanism for adaptive IDS. QK-MMD does not universally dominate classical detectors in raw downstream accuracy. However, QK-MMD ZZ matches the strongest classical distributional baseline under progressive drift while requiring substantially fewer readaptations. When operational readaptation costs are modeled explicitly, QK-MMD ZZ achieves higher net utility across meaningful cost regimes, despite higher monitoring runtime.

## Recommended next step

Do not add more detector variants immediately. The next step is to merge the classical-baselines branch back into the main paper branch, then start drafting the paper structure, figures, tables, Results, and Discussion.
