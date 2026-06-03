# Paper 2 - Anchored streaming cal30 diagnostic

## Experiment
CICIDS2017 BENIGN-only Tuesday vs Wednesday.
Anchored streaming protocol with:
- calibration_windows = 30
- pre_eval_windows = 20
- post_windows = 20
- window_size = 256
- dim = 8
- detectors = MMD-RBF, QK-MMD ZZ, QK-MMD PauliXZ
- seeds = 30

## Main result

The anchored streaming trigger is not robust enough.

Best QK-MMD low-false-alarm configurations:
- q=0.975, k=3, ZZ:
  - false_alarm_any_rate = 0.0333
  - post_detect_any_rate = 0.1000
  - trigger_gain = 0.0667
  - delay_windows_mean = 4.6667

- q=0.975, k=3, PauliXZ:
  - false_alarm_any_rate = 0.0333
  - post_detect_any_rate = 0.1000
  - trigger_gain = 0.0667
  - delay_windows_mean = 4.6667

MMD-RBF reaches higher trigger gain with k=1, but with high false alarm rates:
- q=1.0, k=1:
  - false_alarm_any_rate = 0.3333
  - post_detect_any_rate = 0.6000
  - trigger_gain = 0.2667

## Score separability diagnostic

Pre/post AUC:
- QK-MMD PauliXZ: 0.5472
- QK-MMD ZZ: 0.5436
- MMD-RBF: 0.5272

Cohen's d:
- QK-MMD PauliXZ: 0.1320
- QK-MMD ZZ: 0.1209
- MMD-RBF: 0.1509

## Interpretation

The weak streaming performance is not mainly a threshold-policy problem.
The window-level score distributions between pre-drift and post-drift overlap strongly.

This suggests that the static BENIGN-only QK-MMD advantage does not automatically transfer to a naive anchored streaming trigger.

## Decision

Do not keep tuning threshold quantiles or consecutive-k policies blindly.

Next step:
Move to controlled streaming drift with explicit severity levels, where post-drift windows are generated with controlled mixtures between reference BENIGN traffic and shifted BENIGN traffic.

This keeps the Paper 2 objective aligned:
monitoring distribution drift and evaluating whether quantum kernel geometries provide earlier or more sensitive drift signals.
