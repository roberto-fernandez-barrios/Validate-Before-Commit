# Paper 2 runtime/cost analysis checkpoint 001

## Purpose

This analysis summarizes detector runtime and compares the operational
monitoring benefit of QK-MMD against its additional detector runtime cost.

## Generated tables

- `results\tables\paper2_runtime_cost_001\paper_table_runtime_by_method.csv`
- `results\tables\paper2_runtime_cost_001\paper_table_runtime_ratio_vs_mmd.csv`
- `results\tables\paper2_runtime_cost_001\paper_table_runtime_cost_benefit_strict_zones.csv`

## Interpretation

The paper should not claim that QK-MMD is computationally cheaper than
MMD-RBF. Instead, the correct cost-benefit claim is that QK-MMD may be
worth using as a specialized severe-drift monitor when the operational
cost of missing drift is high enough to justify the additional detector
runtime.

The strict operational zones should therefore be discussed together with
runtime ratios, not in isolation.
