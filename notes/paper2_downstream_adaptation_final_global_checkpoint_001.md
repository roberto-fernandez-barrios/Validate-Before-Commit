# Paper 2 downstream adaptation final global checkpoint 001

## Protocol

Dataset:

- CICIDS2017 Tuesday vs Wednesday.
- Binary IDS task: BENIGN=0, ATTACK=1.
- Balanced-prior windows.
- Initial downstream model: SVC-RBF.
- Reference regime: Tuesday.
- Shifted regime: controlled mixtures toward Wednesday.

Policy selection:

- Policy tuning seeds: 1-10.
- Final evaluation seeds: 11-40.
- Final global trigger policy:
  - threshold_quantile = 0.95
  - consecutive_k = 3

The final seeds are not used for policy selection.

## Main result

Drift-triggered adaptation substantially reduces downstream degradation relative
to no adaptation.

At severity 1.0:

- No adaptation:
  - balanced accuracy = 0.5808
  - degradation area = 0.3153

- Oracle adaptation:
  - balanced accuracy = 0.8961
  - degradation area = 0.0000

- MMD-RBF triggered adaptation:
  - balanced accuracy = 0.8492
  - degradation area = 0.0469
  - clean adaptation rate = 0.9333
  - clean adaptation gain = 0.2511
  - false alarm rate = 0.0667

- QK-MMD ZZ triggered adaptation:
  - balanced accuracy = 0.8492
  - degradation area = 0.0469
  - clean adaptation rate = 0.9667
  - clean adaptation gain = 0.2596
  - false alarm rate = 0.0333

- QK-MMD PauliXZ triggered adaptation:
  - balanced accuracy = 0.8492
  - degradation area = 0.0469
  - clean adaptation rate = 0.9667
  - clean adaptation gain = 0.2596
  - false alarm rate = 0.0333

## Regime-level interpretation

At severity 0.25:

- MMD-RBF is stronger:
  - clean adaptation rate = 0.8000
  - clean gain = 0.0437

- QK-MMD ZZ:
  - clean adaptation rate = 0.4000
  - clean gain = 0.0211

- QK-MMD PauliXZ:
  - clean adaptation rate = 0.4000
  - clean gain = 0.0212

At severities 0.5 and 0.75, all triggered adaptation strategies recover a
large fraction of the oracle gain.

At severity 1.0, QK-MMD variants achieve slightly higher clean adaptation rates
than MMD-RBF under the selected global policy, while all triggered strategies
substantially reduce degradation.

## Paper claim supported

The downstream block supports the claim that drift-triggered adaptation can
substantially reduce IDS degradation under temporal distribution shift.

The evidence does not support universal QK-MMD dominance in downstream adaptation.
Instead, it supports a regime-dependent and complementary claim:

- MMD-RBF is stronger in low-moderate downstream adaptation at severity 0.25.
- QK-MMD is competitive in moderate-to-high drift.
- QK-MMD variants show slightly better clean adaptation behavior at severity 1.0.
- Combined with the controlled streaming monitor results, quantum-kernel drift
  monitors provide useful complementary geometry for drift-aware adaptation.
