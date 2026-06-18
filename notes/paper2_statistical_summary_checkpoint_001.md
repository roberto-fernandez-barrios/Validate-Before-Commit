# Paper 2 statistical summary checkpoint 001

## Purpose

This note summarizes bootstrap confidence intervals and paired seed-level
comparisons for the downstream adaptation experiments.

The goal is to support paper claims with uncertainty estimates rather than
only reporting means.

## Generated tables

- `results\tables\paper2_statistical_summary_001\paper_table_downstream_metric_bootstrap_ci.csv`
- `results\tables\paper2_statistical_summary_001\paper_table_downstream_paired_comparisons.csv`
- `results\tables\paper2_statistical_summary_001\paper_table_downstream_main_paired_comparisons.csv`

## Interpretation guidelines

- Bootstrap CIs are computed over seeds.
- Paired comparisons are computed by matching the same seed, severity and experiment block.
- `mean_diff_a_minus_b > 0` means strategy A has a larger value than strategy B.
- For degradation area, larger is worse.
- For clean adaptation gain, larger is better.

## Important caveat

These summaries are descriptive uncertainty estimates, not a substitute for
a full statistical testing protocol across multiple datasets.

They are appropriate for the current paper stage because the main objective
is to quantify robustness and support regime-dependent claims.

## Main paired comparisons

 experiment_block  severity       method_a       method_b                metric  n_pairs  mean_diff_a_minus_b  ci95_low  ci95_high  prob_diff_gt_0
downstream_global      0.25  No adaptation        MMD-RBF      degradation_area       30             0.043815  0.035260   0.051888        0.833333
downstream_global      0.25  No adaptation      QK-MMD ZZ      degradation_area       30             0.023177  0.013750   0.033047        0.433333
downstream_global      0.25  No adaptation QK-MMD PauliXZ      degradation_area       30             0.023320  0.013711   0.033138        0.433333
downstream_global      1.00  No adaptation        MMD-RBF      degradation_area       30             0.268411  0.263581   0.274831        1.000000
downstream_global      1.00  No adaptation      QK-MMD ZZ      degradation_area       30             0.268411  0.263632   0.274858        1.000000
downstream_global      1.00  No adaptation QK-MMD PauliXZ      degradation_area       30             0.268411  0.263437   0.275156        1.000000
downstream_global      0.25        MMD-RBF QK-MMD PauliXZ clean_adaptation_gain       30             0.022500  0.013099   0.031823        0.633333
downstream_global      0.25        MMD-RBF      QK-MMD ZZ clean_adaptation_gain       30             0.022643  0.012707   0.032097        0.633333
downstream_global      1.00 QK-MMD PauliXZ        MMD-RBF clean_adaptation_gain       30             0.008529 -0.017760   0.034818        0.066667
downstream_global      1.00      QK-MMD ZZ        MMD-RBF clean_adaptation_gain       30             0.008529 -0.017760   0.035052        0.066667
  hybrid_selected      0.25      Hybrid OR        MMD-RBF clean_adaptation_gain       30             0.001615 -0.001107   0.005209        0.166667
  hybrid_selected      1.00 QK-MMD PauliXZ      Hybrid OR clean_adaptation_gain       30             0.026107  0.000000   0.060273        0.100000
