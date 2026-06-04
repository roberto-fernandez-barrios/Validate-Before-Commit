# Paper 2 - Controlled streaming drift checkpoint 001

## Experiment

CICIDS2017 BENIGN-only Tuesday vs Wednesday.

Protocol:
- Controlled streaming mixture
- Reference: Tuesday BENIGN
- Current: Wednesday BENIGN
- window_size = 256
- dim = 8
- seeds = 15
- calibration_windows = 20
- pre_windows = 20
- post_windows = 20
- severities = 0.1, 0.25, 0.5, 0.75, 1.0
- n_permutations = 300
- alpha = 0.05
- detectors = MMD-RBF, QK-MMD ZZ, QK-MMD PauliXZ

## Main AUC result

Pre/post score separability increases monotonically with controlled drift severity.

AUC by severity:

- severity 0.10:
  - MMD-RBF: 0.5073
  - QK-MMD ZZ: 0.5053
  - QK-MMD PauliXZ: 0.5013

- severity 0.25:
  - QK-MMD PauliXZ: 0.5623
  - QK-MMD ZZ: 0.5575
  - MMD-RBF: 0.5395

- severity 0.50:
  - QK-MMD PauliXZ: 0.7202
  - QK-MMD ZZ: 0.7135
  - MMD-RBF: 0.6468

- severity 0.75:
  - QK-MMD PauliXZ: 0.8423
  - QK-MMD ZZ: 0.8312
  - MMD-RBF: 0.7493

- severity 1.00:
  - QK-MMD PauliXZ: 0.9452
  - QK-MMD ZZ: 0.9382
  - MMD-RBF: 0.8390

## Low false-alarm policy result

Using policies with false_alarm_any_rate <= 0.10:

- severity 0.50:
  - QK-MMD PauliXZ, q=0.95, k=2:
    - false_alarm_any_rate = 0.0667
    - post_detect_any_rate = 0.6000
    - trigger_gain = 0.5333

- severity 0.75:
  - QK-MMD PauliXZ, q=0.95/0.975/0.99, k=2:
    - false_alarm_any_rate = 0.0667
    - post_detect_any_rate = 0.7333
    - trigger_gain = 0.6667

  - QK-MMD ZZ, q=0.975/0.99/1.0, k=2:
    - false_alarm_any_rate = 0.0667
    - post_detect_any_rate = 0.7333
    - trigger_gain = 0.6667

- severity 1.00:
  - QK-MMD PauliXZ, k=2:
    - false_alarm_any_rate = 0.0667
    - post_detect_any_rate = 0.9333
    - trigger_gain = 0.8667

  - QK-MMD ZZ, k=2:
    - false_alarm_any_rate = 0.0667
    - post_detect_any_rate = 0.9333
    - trigger_gain = 0.8667

## Interpretation

Very weak drift severity 0.10 is close to random for all detectors.

From severity 0.25 onward, QK-MMD starts to separate pre/post windows better than MMD-RBF.

The strongest and most stable region is severity >= 0.50, where QK-MMD PauliXZ and ZZ outperform MMD-RBF in both score separability and low-false-alarm trigger policies.

This supports the Paper 2 claim:

Quantum kernel geometries do not provide universal superiority, but certain feature maps offer stronger streaming drift sensitivity under controlled temporal distribution shifts.

## Next step

Run a final confirmatory experiment with:
- seeds = 30
- n_permutations = 500
- same protocol
- same dim/window configuration
- same detector set

Do not change the protocol before this confirmation.
