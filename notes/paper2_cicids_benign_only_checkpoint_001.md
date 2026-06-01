# Paper 2 - CICIDS BENIGN-only QK-MMD checkpoint

## Dataset
CICIDS2017 Tuesday vs Wednesday, filtered to BENIGN labels only.

## Protocol
- Reference: Tuesday BENIGN
- Current: Wednesday BENIGN
- Detectors: MMD-RBF, QK-MMD
- Quantum maps: z, zz, pauli_xz
- Windows: 128, 256
- Dimensions: 4, 6, 8
- Seeds: 30
- Permutations: 500
- Alpha: 0.05

## Main finding
The strongest regime is window_size=256 and dim=8.

- qk_mmd pauli_xz: power=0.50, fpr=0.0333, net_power=0.4667
- qk_mmd zz: power=0.4333, fpr=0.0333, net_power=0.40
- qk_mmd z: power=0.2333, fpr=0.0333, net_power=0.20
- mmd_rbf: power=0.1667, fpr=0.0667, net_power=0.10

Interpretation:
QK-MMD does not dominate universally, but certain quantum feature-map geometries, especially PauliXZ and ZZ, show higher sensitivity to subtle benign-only temporal shift while maintaining controlled false positives.

Next step:
Move from static two-sample detection to streaming detection-delay evaluation.
