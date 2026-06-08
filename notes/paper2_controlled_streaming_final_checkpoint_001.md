# Paper 2 - Controlled streaming drift final checkpoint 001

## Experiment

CICIDS2017 BENIGN-only Tuesday vs Wednesday.

Final controlled streaming protocol:
- Reference: Tuesday BENIGN
- Current: Wednesday BENIGN
- Controlled mixture severities: 0.10, 0.25, 0.50, 0.75, 1.00
- window_size = 256
- dim = 8
- seeds = 30
- calibration_windows = 20
- pre_windows = 20
- post_windows = 20
- n_permutations = 500
- alpha = 0.05
- detectors = MMD-RBF, QK-MMD ZZ, QK-MMD PauliXZ

## Final AUC result

Pre/post score separability:

- severity 0.10:
  - QK-MMD ZZ: 0.5132
  - QK-MMD PauliXZ: 0.5114
  - MMD-RBF: 0.4948

- severity 0.25:
  - QK-MMD PauliXZ: 0.5482
  - QK-MMD ZZ: 0.5467
  - MMD-RBF: 0.5224

- severity 0.50:
  - QK-MMD PauliXZ: 0.6923
  - QK-MMD ZZ: 0.6858
  - MMD-RBF: 0.6191

- severity 0.75:
  - QK-MMD PauliXZ: 0.8110
  - QK-MMD ZZ: 0.7981
  - MMD-RBF: 0.6991

- severity 1.00:
  - QK-MMD PauliXZ: 0.9182
  - QK-MMD ZZ: 0.9069
  - MMD-RBF: 0.8000

## Interpretation

The final 30-seed experiment confirms the main pattern.

At severity 0.10, all detectors are close to random separability. This regime should be reported as a weak/no-signal regime.

From severity 0.25 onward, QK-MMD begins to outperform MMD-RBF in pre/post score separability.

From severity 0.50 onward, the advantage becomes operationally meaningful:
QK-MMD PauliXZ and QK-MMD ZZ produce higher score separability and stronger low-false-alarm trigger policies than MMD-RBF.

The strongest detector is QK-MMD PauliXZ, followed closely by QK-MMD ZZ.

## Defensible claim

The evidence does not support universal quantum superiority.

It supports a regime-aware claim:

Certain quantum kernel geometries, especially PauliXZ and ZZ, provide stronger streaming drift sensitivity than a classical RBF-MMD baseline under controlled benign-only temporal drift, particularly once the drift severity becomes operationally meaningful.

## Paper 2 status

This block is now strong enough to become a main experimental result.

Next steps:
1. Generate paper-ready tables from the final summary CSVs.
2. Generate the AUC-vs-severity figure.
3. Generate the low-false-alarm trigger-gain figure.
4. Freeze this protocol before adding any extra dataset or ablation.
