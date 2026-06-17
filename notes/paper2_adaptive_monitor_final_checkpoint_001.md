# Paper 2 - Adaptive monitor final checkpoint 001

## Experiment

Adaptive monitor experiment over CICIDS2017 BENIGN-only controlled temporal drift.

Reference distribution:
- Tuesday BENIGN traffic

Shifted/current distribution:
- Wednesday BENIGN traffic

Protocol:
- Window size: 256
- Dimension: 8
- Seeds: 30
- Severities: 0.1, 0.25, 0.5, 0.75, 1.0
- Detectors:
  - MMD-RBF
  - QK-MMD ZZ
  - QK-MMD PauliXZ
- Threshold policy:
  - threshold quantile: 0.95
  - consecutive detections: 2
- Permutations: 500

## Adaptive response

When a detector triggers drift, the monitor updates its reference distribution using post-drift windows and evaluates whether alarm instability decreases after adaptation.

The strict success metric is:

clean_adaptation_success =
    no false alarm before drift
    AND detection after drift
    AND no alarm after adaptation

## Main findings

Weak severities 0.1 and 0.25 provide limited adaptive value.

At severity 0.5:
- QK-MMD PauliXZ and QK-MMD ZZ outperform MMD-RBF in post-drift detection and clean adaptive success.

At severity 0.75:
- QK-MMD PauliXZ and QK-MMD ZZ provide the strongest adaptive-monitoring performance.
- They achieve higher clean adaptation success than MMD-RBF while keeping false alarms controlled.

At severity 1.0:
- QK-MMD provides faster and more frequent post-drift detection.
- MMD-RBF provides slightly cleaner post-adaptation stabilization.
- This supports a nuanced regime-aware interpretation rather than universal quantum superiority.

## Paper interpretation

The adaptive-monitoring results support the central Paper 2 claim:

Quantum kernel geometries, especially PauliXZ and ZZ, can provide operationally useful drift signals for adaptive cybersecurity monitoring under moderate-to-strong controlled temporal drift. Their main advantage is stronger and earlier drift triggering; post-adaptation stabilization depends on severity and detector geometry.

## Generated artifacts

Figures:
- results/figures/paper2_adaptive_monitor_final_001/clean_adaptation_success_vs_severity.pdf
- results/figures/paper2_adaptive_monitor_final_001/post_detection_rate_vs_severity.pdf
- results/figures/paper2_adaptive_monitor_final_001/post_adapt_alarm_rate_vs_severity.pdf
- results/figures/paper2_adaptive_monitor_final_001/score_reduction_after_adaptation_vs_severity.pdf

Tables:
- results/tables/paper2_adaptive_monitor_final_001/paper_table_adaptive_monitor_summary.tex
- results/tables/paper2_adaptive_monitor_final_001/paper_table_best_clean_adaptation_by_severity.tex

## Status

The adaptive-monitoring experimental block is complete.
