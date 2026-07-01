# Paper 2 Feature-Map Sensitivity Protocol 001

## Purpose

This protocol tests whether the observed QK-MMD behavior is specific to a single quantum feature-map configuration or whether similar trade-offs appear across a small, pre-defined family of quantum feature-map configurations.

This is not a search for a winning quantum map. All configurations must be reported.

## Motivation

A reviewer may argue that the current QK-MMD results are limited because the main experiments only evaluate a small number of quantum feature-map settings. In particular, ZZ and PauliXZ maps may behave differently depending on the number of repetitions.

## Pre-defined configurations

The following six configurations are fixed before execution:

1. `zz_r1`: QK-MMD ZZ, reps=1
2. `zz_r2`: QK-MMD ZZ, reps=2
3. `zz_r3`: QK-MMD ZZ, reps=3
4. `paulixz_r1`: QK-MMD PauliXZ, reps=1
5. `paulixz_r2`: QK-MMD PauliXZ, reps=2
6. `paulixz_r3`: QK-MMD PauliXZ, reps=3

Fixed quantum preprocessing:

- `q_input_scaling = atan_standard`
- dimensionality: same as the main progressive readaptation script default unless explicitly overridden
- all non-quantum detector and stream parameters: same as the main progressive readaptation protocol unless explicitly overridden by smoke/medium/final mode

## Development scenario

Used first:

- Tuesday → Wednesday

This scenario is used only to understand sensitivity to feature-map configuration.

## Held-out scenarios

Only after development results are inspected:

- Tuesday → Friday PortScan
- Tuesday → Friday DDoS

## Execution phases

### Phase 1: Smoke

- Scenario: Wednesday
- Seeds: 1,2,3
- Short stream: 20 post-windows, 20 ramp-windows
- Purpose: verify scripts and detect obviously broken configurations

### Phase 2: Medium

- Scenario: Wednesday
- Seeds: 1..10
- Full stream length
- Purpose: decide whether reps sensitivity is meaningful enough to justify full held-out evaluation

### Phase 3: Full held-out

Only if Phase 2 shows meaningful differences:

- Scenarios: PortScan and DDoS
- Seeds: 1..30
- All six configurations
- Report all results

## Primary metrics

In order:

1. `adaptation_efficiency`
2. `n_adaptations`
3. `mean_balanced_accuracy`
4. `cumulative_error_area`
5. `detector_runtime_sec_total`

## Reporting rule

All six configurations must be reported.

Do not select the best configuration per scenario and present it as the method.

If one configuration is selected after Wednesday, it must be evaluated unchanged on PortScan and DDoS.

## Anti-cherry-picking rule

If reps=2 or reps=3 improves over reps=1, this must be reported as sensitivity to quantum map depth, not as a replacement of the old experiments unless the full main experiment is rerun consistently.

## Interpretation

Possible outcomes:

1. All reps behave similarly:
   - The original QK-MMD conclusions are not obviously an artifact of reps=1.

2. Higher reps improve QK substantially:
   - The paper should report map-depth sensitivity and avoid claims based only on reps=1.

3. Higher reps degrade QK:
   - The original shallow map is reasonable and deeper maps are not beneficial in this setting.

4. Different maps win different scenarios:
   - QK-MMD behavior is highly map- and regime-dependent; this weakens any universal claim but supports a characterization paper.
