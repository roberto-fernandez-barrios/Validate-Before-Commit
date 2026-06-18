# Paper 2 geometry diagnostics checkpoint 001

## Objective

This diagnostic block connects detector score geometry with downstream
adaptive utility.

The main quantities are:

- score_ratio = score / threshold
- score_ratio_gap = post_score_ratio_mean - pre_score_ratio_mean
- post-drift alarm rate
- clean downstream adaptation gain
- degradation area

Score window source: `results\raw\paper2_adaptive_monitor_final_001\paper2_adaptive_monitor_window_results.csv`

## Generated artifacts

- Figures: `results\figures\paper2_geometry_diagnostics_001`
- Tables: `results\tables\paper2_geometry_diagnostics_001`

## Geometry/downstream interpretation

The table `paper_table_geometry_vs_downstream.csv` joins detector
score separation with downstream adaptation metrics.

Use this to assess whether detectors with stronger post/pre score
separation also produce higher clean adaptation gain or lower
degradation area.

## Correlations

Correlation values are stored in:

- `paper_table_geometry_downstream_correlations.csv`

These values should be interpreted cautiously because the number of
severity points per detector is small.

## Paper usage

This block should not be presented as a standalone performance claim.
It is an explanatory diagnostic supporting the regime-dependent
interpretation of QK-MMD and MMD-RBF behavior.
