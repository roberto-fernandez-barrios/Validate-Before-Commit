# Paper 2 operational scale impact checkpoint 001

## Purpose

This analysis evaluates whether small detector/adaptation differences can
become operationally meaningful at high traffic volume.

It does not claim exact numbers of additional correct classifications.
Instead, it defines flow-equivalent operational impact proxies.

## Metrics

- detected_drift_flow_equiv = post_alarm_rate * traffic_volume
- missed_drift_flow_equiv = (1 - post_alarm_rate) * traffic_volume
- additional_detected_flow_equiv_vs_mmd = (post_alarm_rate_method - post_alarm_rate_mmd) * traffic_volume
- scaled_clean_gain_units = clean_adaptation_gain * traffic_volume
- degradation_units_saved_vs_mmd = (degradation_mmd - degradation_method) * traffic_volume

## Quantum candidate zone criterion

A QK-MMD method is marked as a candidate operational advantage zone when:

- post_alarm_rate_qk > post_alarm_rate_mmd
- clean_gain_qk is not worse than MMD-RBF by more than 0.01
- false_alarm_qk is not higher than MMD-RBF by more than 0.05

A strong operational zone additionally requires:

- additional_detected_flow_equiv_vs_mmd >= 100000

## Generated tables

- `results\tables\paper2_operational_scale_impact_001\paper_table_operational_scale_by_method.csv`
- `results\tables\paper2_operational_scale_impact_001\paper_table_quantum_operational_advantage_zones.csv`
- `results\tables\paper2_operational_scale_impact_001\paper_table_quantum_strong_operational_zones.csv`
- `results\tables\paper2_operational_scale_impact_001\paper_table_quantum_strict_operational_zones.csv`
- `results\tables\paper2_operational_scale_impact_001\paper_table_operational_scale_paired_differences.csv`
- `results\tables\paper2_operational_scale_impact_001\paper_table_operational_scale_key_paired_differences.csv`

## Main result

Strong quantum operational zones were found under the current criterion.

 severity         method  traffic_volume  post_alarm_delta_vs_mmd  additional_detected_flow_equiv_vs_mmd  clean_gain_delta_vs_mmd  false_alarm_delta_vs_mmd
     0.50 QK-MMD PauliXZ        10000000                 0.060000                           6.000000e+05                -0.005208                  0.033333
     0.50 QK-MMD PauliXZ       100000000                 0.060000                           6.000000e+06                -0.005208                  0.033333
     0.50      QK-MMD ZZ        10000000                 0.053333                           5.333333e+05                -0.005456                  0.033333
     0.50      QK-MMD ZZ       100000000                 0.053333                           5.333333e+06                -0.005456                  0.033333
     0.75 QK-MMD PauliXZ        10000000                 0.081667                           8.166667e+05                 0.000078                  0.000000
     0.75 QK-MMD PauliXZ       100000000                 0.081667                           8.166667e+06                 0.000078                  0.000000
     0.75      QK-MMD ZZ        10000000                 0.071667                           7.166667e+05                 0.000078                  0.000000
     0.75      QK-MMD ZZ       100000000                 0.071667                           7.166667e+06                 0.000078                  0.000000
     1.00 QK-MMD PauliXZ         1000000                 0.336667                           3.366667e+05                 0.008529                 -0.033333
     1.00 QK-MMD PauliXZ        10000000                 0.336667                           3.366667e+06                 0.008529                 -0.033333
     1.00 QK-MMD PauliXZ       100000000                 0.336667                           3.366667e+07                 0.008529                 -0.033333
     1.00      QK-MMD ZZ         1000000                 0.306667                           3.066667e+05                 0.008529                 -0.033333
     1.00      QK-MMD ZZ        10000000                 0.306667                           3.066667e+06                 0.008529                 -0.033333
     1.00      QK-MMD ZZ       100000000                 0.306667                           3.066667e+07                 0.008529                 -0.033333

## Paper interpretation

This analysis should be presented as an operational scaling proxy.
It supports the question of whether small monitoring gains can matter
at high traffic volume.

It should not be presented as direct proof of more correctly classified
samples unless a later experiment computes sample-level errors directly.
