# Paper 2 Feature-Map Sensitivity Checkpoint 001

## Purpose

This checkpoint summarizes the pre-registered feature-map sensitivity study for QK-MMD in the Wednesday development scenario.

The goal was to test whether the main QK-MMD behavior was an artifact of a single quantum feature-map configuration.

## Protocol

Pre-registered configurations:

1. ZZ-r1
2. ZZ-r2
3. ZZ-r3
4. PauliXZ-r1
5. PauliXZ-r2
6. PauliXZ-r3

Fixed quantum preprocessing:

- q_input_scaling = atan_standard
- same progressive readaptation protocol as the main experiment
- development scenario: Tuesday → Wednesday

Execution phases completed:

- smoke: 3 seeds, 20 post-windows
- medium: 10 seeds, 100 post-windows

## Medium results: Wednesday

| config | BA | cumulative error | gain vs no adapt | adaptations | adaptation efficiency | detector runtime |
|---|---:|---:|---:|---:|---:|---:|
| PauliXZ-r3 | 0.886672 | 11.332813 | 12.563281 | 3.7 | 3.395481 | 13.491980 |
| ZZ-r1 | 0.886656 | 11.334375 | 12.561719 | 3.1 | 4.052167 | 5.695984 |
| ZZ-r3 | 0.883141 | 11.685938 | 12.210156 | 3.3 | 3.700047 | 12.130083 |
| PauliXZ-r1 | 0.880727 | 11.927344 | 11.968750 | 3.2 | 3.740234 | 6.234160 |
| PauliXZ-r2 | 0.878930 | 12.107031 | 11.789063 | 3.7 | 3.186233 | 9.630510 |
| ZZ-r2 | 0.877156 | 12.284375 | 11.611719 | 3.2 | 3.628662 | 9.190042 |

No adaptation:

- BA = 0.761039
- cumulative error = 23.896094

## Interpretation

The medium Wednesday sensitivity study does not show evidence that increasing quantum map repetitions unlocks a clearly superior QK-MMD configuration.

PauliXZ-r3 obtains the numerically best BA and cumulative error, but the difference against ZZ-r1 is negligible:

- BA difference: approximately +0.000016
- cumulative error difference: approximately -0.001562

This tiny performance difference comes at a clear operational cost:

- PauliXZ-r3 uses more adaptations than ZZ-r1: 3.7 vs 3.1
- PauliXZ-r3 has lower adaptation efficiency: 3.395 vs 4.052
- PauliXZ-r3 has much higher detector runtime: 13.49s vs 5.70s

Therefore, ZZ-r1 remains the most reasonable operational configuration.

## Decision

Do not launch full held-out feature-map sensitivity on PortScan and DDoS at this stage.

The pre-registered condition for full held-out execution was a meaningful improvement in Phase 2. The Wednesday medium study shows no meaningful operational improvement from deeper maps.

## Paper-level conclusion

A predefined feature-map sensitivity study over ZZ and PauliXZ maps with reps 1, 2 and 3 found no evidence that the main QK-MMD conclusions are an artifact of using a shallow ZZ configuration.

Increasing map repetitions did not produce a clearly superior operating point. ZZ-r1 remains the most defensible primary QK-MMD configuration due to its balance between downstream performance, readaptation frequency, adaptation efficiency, and detector runtime.

## Recommended paper placement

Include this study in the appendix as a feature-map sensitivity analysis.

Use it in the main text only to answer the reviewer concern:

"The selected QK-MMD configuration was not chosen after an unreported map search. We performed a pre-defined sensitivity analysis over ZZ and PauliXZ feature maps with repetitions 1-3 and found no operationally superior deeper configuration in the development scenario."

## Files generated

Raw results:

- results/raw/paper2_feature_map_sensitivity_smoke_001/
- results/raw/paper2_feature_map_sensitivity_medium_001/

Tables:

- results/tables/paper2_feature_map_sensitivity_smoke_001/paper_table_feature_map_sensitivity_wednesday_smoke.csv
- results/tables/paper2_feature_map_sensitivity_medium_001/paper_table_feature_map_sensitivity_wednesday_medium.csv

Protocol:

- notes/paper2_feature_map_sensitivity_protocol_001.md
