# Paper 2 downstream adaptation final optimized checkpoint 001

## Protocol

This checkpoint evaluates detector-specific optimized trigger policies.

Policy tuning seeds:

- 1-10

Final evaluation seeds:

- 11-40

Selected detector-specific policies:

- MMD-RBF:
  - threshold_quantile = 0.99
  - consecutive_k = 2

- QK-MMD ZZ:
  - threshold_quantile = 0.95
  - consecutive_k = 2

- QK-MMD PauliXZ:
  - threshold_quantile = 0.90
  - consecutive_k = 3

The final seeds are not used for policy selection.


## Global vs detector-specific optimized policies

The global policy uses the same q/k trigger rule for all detectors. The
detector-specific optimized setting uses policies selected on tuning seeds for
each detector separately.

The optimized setting is useful as an operational upper-bound analysis, but the
global policy remains the cleaner main comparison because it avoids assigning
different trigger sensitivity rules to different detectors in the primary result.


## Main findings

At severity 0.25, MMD-RBF remains strongest:

- MMD-RBF:
  - balanced accuracy = 0.9015
  - degradation area = 0.0284
  - clean adaptation rate = 0.7667
  - clean adaptation gain = 0.0404
  - false alarm rate = 0.0000

- QK-MMD ZZ:
  - balanced accuracy = 0.8971
  - degradation area = 0.0327
  - clean adaptation rate = 0.5000
  - clean adaptation gain = 0.0249
  - false alarm rate = 0.2000

- QK-MMD PauliXZ:
  - balanced accuracy = 0.8891
  - degradation area = 0.0408
  - clean adaptation rate = 0.4667
  - clean adaptation gain = 0.0220
  - false alarm rate = 0.1000

At severity 1.0:

- MMD-RBF:
  - balanced accuracy = 0.8651
  - degradation area = 0.0310
  - clean adaptation rate = 0.8000
  - clean adaptation gain = 0.2288
  - false alarm rate = 0.2000

- QK-MMD ZZ:
  - balanced accuracy = 0.8651
  - degradation area = 0.0310
  - clean adaptation rate = 0.8333
  - clean adaptation gain = 0.2376
  - false alarm rate = 0.1667

- QK-MMD PauliXZ:
  - balanced accuracy = 0.8492
  - degradation area = 0.0469
  - clean adaptation rate = 0.9667
  - clean adaptation gain = 0.2596
  - false alarm rate = 0.0333

## Interpretation

Detector-specific optimization does not produce universal QK-MMD dominance.

Instead, it supports a regime-dependent interpretation:

- MMD-RBF is strongest in low-moderate downstream adaptation, especially at severity 0.25.
- QK-MMD ZZ is competitive with MMD-RBF in moderate-to-severe drift.
- QK-MMD PauliXZ provides the cleanest severe-drift adaptation behavior at severity 1.0, with high clean adaptation rate and low false alarm rate.
- The main paper should therefore emphasize complementarity and regime dependence, not universal quantum advantage.

## Recommended paper usage

Use the global policy result as the main downstream adaptation result.

Use this detector-specific optimized result as a secondary operational analysis or appendix.
