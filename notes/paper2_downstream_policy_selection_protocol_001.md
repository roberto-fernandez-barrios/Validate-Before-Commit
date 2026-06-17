# Paper 2 - Downstream trigger policy selection protocol

## Motivation

The downstream adaptation experiment uses a drift-triggered retraining policy.
The detector produces one score per monitoring window, but an operational
trigger policy is required to decide when the downstream classifier should be
adapted.

The policy has two hyperparameters:

- threshold_quantile q
- consecutive threshold exceedances k

The value k=3 is not assumed a priori to be optimal. It is selected using a
separate validation protocol to avoid tuning on the final test seeds.

## Policy grid

The following trigger policies are evaluated on validation seeds:

- q in {0.90, 0.95, 0.975, 0.99}
- k in {1, 2, 3}

## Validation / test split

Policy tuning:

- seeds 1-10

Final evaluation:

- seeds 11-40

The final evaluation seeds are not used for policy selection.

## Selection criterion

The main policy is selected globally, i.e. the same q/k policy is applied to
all drift detectors.

The selection criterion is:

1. keep policies with low false alarms:
   - mean_false_alarm_any_rate <= 0.15
   - max_false_alarm_any_rate <= 0.10

2. among eligible policies, maximize:
   - mean_clean_adaptation_gain

3. tie-breakers:
   - higher mean_clean_downstream_adaptation_rate
   - lower mean_false_alarm_any_rate
   - lower mean_trigger_delay_windows

## Selected global policy

The validation sweep selected:

- threshold_quantile = 0.95
- consecutive_k = 3

Validation summary:

- mean_clean_adaptation_gain = 0.1234
- mean_clean_downstream_adaptation_rate = 0.7267
- mean_false_alarm_any_rate = 0.0067
- max_false_alarm_any_rate = 0.10

## Interpretation

k=3 is selected because it provides a conservative low-false-alarm trigger while
preserving downstream adaptation gains. It requires drift evidence to persist
across three consecutive windows before retraining the downstream classifier.

This avoids adapting the IDS due to isolated score fluctuations.
