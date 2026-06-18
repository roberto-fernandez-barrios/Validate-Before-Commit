# Paper 2 geometry diagnostics interpretation 001

## Purpose

This note interprets the geometry diagnostics generated in:

- `results/tables/paper2_geometry_diagnostics_001/`
- `results/figures/paper2_geometry_diagnostics_001/`

The goal is to connect detector score behavior with downstream adaptation utility.

## Main observation

The detector score geometry explains the regime-dependent downstream results.

QK-MMD does not universally dominate MMD-RBF. Instead, each detector produces
useful drift evidence in different regimes.

## Low-moderate drift: severity 0.25

At severity 0.25, MMD-RBF shows the strongest post-pre score separation:

- MMD-RBF score ratio gap: 0.0300
- QK-MMD PauliXZ score ratio gap: 0.0173
- QK-MMD ZZ score ratio gap: 0.0183

This matches downstream adaptation:

- MMD-RBF clean adaptation gain: 0.0437
- QK-MMD PauliXZ clean adaptation gain: 0.0212
- QK-MMD ZZ clean adaptation gain: 0.0211

Interpretation:

MMD-RBF provides a stronger low-moderate drift signal, which explains why it
outperforms QK-MMD in downstream adaptation at severity 0.25.

## Moderate drift: severity 0.5

At severity 0.5, MMD-RBF still has a larger score ratio gap:

- MMD-RBF score ratio gap: 0.1336
- QK-MMD PauliXZ score ratio gap: 0.0979
- QK-MMD ZZ score ratio gap: 0.1006

However, downstream gains are already similar:

- MMD-RBF clean adaptation gain: 0.1267
- QK-MMD PauliXZ clean adaptation gain: 0.1215
- QK-MMD ZZ clean adaptation gain: 0.1213

Interpretation:

Although MMD-RBF has a stronger raw score separation, QK-MMD produces enough
post-drift evidence to trigger effective adaptation.

## High drift: severity 0.75

At severity 0.75, QK-MMD produces higher post-drift alarm rates:

- MMD-RBF post alarm rate: 0.2767
- QK-MMD PauliXZ post alarm rate: 0.3583
- QK-MMD ZZ post alarm rate: 0.3483

Downstream clean adaptation gains are essentially equivalent:

- MMD-RBF clean adaptation gain: 0.1908
- QK-MMD PauliXZ clean adaptation gain: 0.1909
- QK-MMD ZZ clean adaptation gain: 0.1909

Interpretation:

QK-MMD does not require the largest score ratio gap to be operationally useful.
Its post-drift alarm persistence is sufficient to support downstream adaptation.

## Severe drift: severity 1.0

At severity 1.0, QK-MMD shows much stronger post-drift alarm persistence:

- MMD-RBF post alarm rate: 0.4200
- QK-MMD PauliXZ post alarm rate: 0.7567
- QK-MMD ZZ post alarm rate: 0.7267

This matches the downstream clean adaptation behavior:

- MMD-RBF clean adaptation rate: 0.9333
- QK-MMD PauliXZ clean adaptation rate: 0.9667
- QK-MMD ZZ clean adaptation rate: 0.9667

Clean adaptation gain is also slightly higher for QK-MMD:

- MMD-RBF clean adaptation gain: 0.2511
- QK-MMD PauliXZ clean adaptation gain: 0.2596
- QK-MMD ZZ clean adaptation gain: 0.2596

Interpretation:

In severe drift, quantum-kernel monitors provide more persistent post-drift
evidence, explaining their higher clean downstream adaptation rates.

## Correlation caveat

The geometry/downstream correlations are high, including Spearman correlations
of 1.0. These should not be overinterpreted because there are only five severity
points per detector.

The safe interpretation is:

Detector score separation and post-drift alarm persistence increase
monotonically with severity and track downstream adaptation gains.

This supports the regime-dependent interpretation but does not establish a
causal mechanism by itself.

## Paper-level claim supported

The geometry diagnostics support the following claim:

Quantum-kernel MMD does not universally outperform classical RBF-MMD. Instead,
quantum-kernel feature maps induce drift signals with different operating
characteristics. MMD-RBF provides stronger low-moderate score separation, while
QK-MMD provides stronger high-severity post-drift alarm persistence. These
differences explain the observed regime-dependent downstream adaptation
behavior.

## Recommended use in manuscript

Use this block in Discussion or Results as an explanatory analysis.

Suggested framing:

- Do not claim universal quantum advantage.
- Emphasize regime-dependent geometry.
- Emphasize complementarity.
- Use QK-MMD high-severity alarm persistence as the strongest quantum-specific
  observation.
