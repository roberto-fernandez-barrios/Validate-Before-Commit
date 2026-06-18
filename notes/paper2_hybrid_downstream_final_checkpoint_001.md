# Paper 2 hybrid downstream final checkpoint 001

## Protocol

Hybrid policy selected on tuning seeds:

- policy: hybrid_or
- threshold_quantile: 0.95
- consecutive_k: 3

Final evaluation:

- seeds: 11-40
- dataset: CICIDS2017 Tuesday vs Wednesday
- downstream model: SVC-RBF
- protocol: balanced-prior controlled temporal shift

## Main finding

The selected hybrid OR monitor improves low-moderate drift adaptation but does
not improve global robustness relative to the best individual detector.

## Severity 0.25

Hybrid OR improves slightly over MMD-RBF:

- Hybrid OR:
  - balanced accuracy: 0.9085
  - degradation area: 0.0214
  - clean adaptation rate: 0.8333
  - clean adaptation gain: 0.0453
  - false alarm rate: 0.0333

- MMD-RBF:
  - balanced accuracy: 0.9047
  - degradation area: 0.0251
  - clean adaptation rate: 0.8000
  - clean adaptation gain: 0.0437
  - false alarm rate: 0.0000

## Severity 1.0

Hybrid OR underperforms QK-MMD individual detectors in clean adaptation:

- Hybrid OR:
  - clean adaptation rate: 0.8667
  - clean adaptation gain: 0.2335
  - false alarm rate: 0.1333

- QK-MMD ZZ / PauliXZ:
  - clean adaptation rate: 0.9667
  - clean adaptation gain: 0.2596
  - false alarm rate: 0.0333

## Interpretation

The hybrid result does not support a claim of globally superior
classical-quantum hybrid adaptation.

It supports a narrower claim:

- Hybrid OR can improve low-moderate drift adaptation.
- QK-MMD remains useful as a complementary signal.
- However, detector choice remains regime-dependent.
- No universal dominance is observed.

## Paper usage

Use this as a robustness/negative-result analysis, not as the main claim.
