# Paper 2 statistical interpretation 001

## Purpose

This note interprets the statistical summaries generated in:

- `results/tables/paper2_statistical_summary_001/`
- `notes/paper2_statistical_summary_checkpoint_001.md`

The goal is to clarify which claims are supported by paired seed-level
uncertainty estimates.

## Main conclusion

The statistical summaries support the main downstream adaptation claim:

Drift-triggered adaptation substantially reduces downstream degradation
relative to no adaptation, especially under moderate and severe drift.

They do not support a strong universal QK-MMD superiority claim.

## Adaptation vs no adaptation

At severity 1.0, all triggered adaptation strategies strongly reduce
degradation area relative to no adaptation.

For MMD-RBF:

- mean paired degradation reduction: 0.2684
- CI95: [0.2636, 0.2748]
- probability of positive reduction: 1.0

For QK-MMD ZZ and QK-MMD PauliXZ:

- mean paired degradation reduction: 0.2684
- CI95 is strictly positive
- probability of positive reduction: 1.0

Interpretation:

The strongest downstream claim is that drift-triggered adaptation reduces
degradation under severe temporal shift.

## MMD-RBF vs QK-MMD at low-moderate drift

At severity 0.25, MMD-RBF has higher clean adaptation gain than QK-MMD.

MMD-RBF vs QK-MMD PauliXZ:

- mean clean gain difference: 0.0225
- CI95: [0.0131, 0.0318]

MMD-RBF vs QK-MMD ZZ:

- mean clean gain difference: 0.0226
- CI95: [0.0127, 0.0321]

Interpretation:

MMD-RBF is more effective for low-moderate downstream adaptation. This matches
the geometry diagnostics, where MMD-RBF shows stronger score separation at
severity 0.25.

## QK-MMD vs MMD-RBF at severe drift

At severity 1.0, QK-MMD has slightly higher mean clean adaptation gain than
MMD-RBF, but the paired confidence interval includes zero.

QK-MMD PauliXZ vs MMD-RBF:

- mean clean gain difference: 0.0085
- CI95: [-0.0178, 0.0348]

QK-MMD ZZ vs MMD-RBF:

- mean clean gain difference: 0.0085
- CI95: [-0.0178, 0.0351]

Interpretation:

QK-MMD is competitive with MMD-RBF in severe drift and shows slightly higher
mean clean gain, but the evidence is not strong enough to claim clear
downstream superiority.

The stronger QK-specific observation remains the geometry diagnostic:
QK-MMD produces higher post-drift alarm persistence in severe drift.

## Hybrid monitor

Hybrid OR slightly improves mean clean gain over MMD-RBF at severity 0.25, but
the paired confidence interval includes zero.

Hybrid OR vs MMD-RBF:

- mean clean gain difference: 0.0016
- CI95: [-0.0011, 0.0052]

Interpretation:

The hybrid monitor should be reported as a robustness/partial result, not as a
main contribution. It does not provide a robust global improvement over the
best individual detector.

## Paper-level implication

The final manuscript should avoid:

- universal quantum advantage claims
- universal QK-MMD dominance
- universal hybrid superiority

The paper should emphasize:

- calibrated drift monitoring
- downstream adaptation utility
- regime-dependent detector behavior
- QK-MMD high-severity alarm persistence
- geometry diagnostics explaining the observed behavior
