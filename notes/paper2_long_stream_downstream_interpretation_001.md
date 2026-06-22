# Paper 2 long-stream downstream interpretation 001

## Purpose

This note interprets the long-stream downstream validation experiment.

The goal was to test whether a longer post-drift stream makes the QK-MMD
monitoring advantage translate into direct downstream performance gains.

## Protocol

- dataset: CICIDS2017 Tuesday vs Wednesday binary downstream adaptation
- post_windows: 100
- severities: 0.75 and 1.0
- seeds: 30
- trigger policy: threshold_quantile = 0.95, consecutive_k = 3
- methods: MMD-RBF, QK-MMD ZZ, QK-MMD PauliXZ
- downstream adaptation: SVC-RBF retraining with the same adaptation mechanism

## Severity 0.75

MMD-RBF and QK-MMD obtain the same post-adaptation balanced accuracy and
degradation area:

- balanced accuracy: 0.8996 for all triggered methods
- degradation area: 0.00697 for all triggered methods
- trigger delay: 2.0 windows for all triggered methods

However, QK-MMD has a slightly lower clean adaptation rate due to more false
alarms:

- MMD-RBF clean adaptation rate: 0.9667
- QK-MMD clean adaptation rate: 0.9333
- MMD-RBF false alarm rate: 0.0333
- QK-MMD false alarm rate: 0.0667

Interpretation:

At severity 0.75, the long-stream downstream experiment does not support a QK
downstream advantage. All methods trigger at the same delay and converge to the
same retrained-model performance.

## Severity 1.0

At severity 1.0, MMD-RBF and QK-MMD are identical under the long-stream
downstream protocol:

- balanced accuracy: 0.8884
- degradation area: 0.00956
- clean adaptation rate: 1.0
- clean adaptation gain: 0.3066
- false alarm rate: 0.0
- trigger delay: 2.0 windows

Paired differences between QK-MMD and MMD-RBF are zero for:

- balanced accuracy
- degradation area
- clean adaptation gain
- trigger delay
- false alarms
- triggered post-drift rate

Interpretation:

When all detectors trigger adaptation in the same window, downstream performance
becomes identical because the same retraining mechanism is applied.

## Paper-level implication

The long-stream experiment does not show direct downstream superiority for
QK-MMD.

Instead, it supports a more precise interpretation:

QK-MMD provides value primarily as a drift-monitoring signal, especially through
higher post-drift alarm coverage in severe/high-volume regimes. However, when a
strong classical detector such as MMD-RBF also triggers adaptation early enough,
the final retrained downstream model converges to the same performance.

## Relationship with operational scale analysis

This result does not invalidate the strict operational advantage zones.

The operational scale analysis measures monitoring coverage and flow-equivalent
drift detection at scale.

The long-stream downstream experiment measures final downstream performance
after retraining.

Together, they show:

- QK-MMD can provide stronger drift-monitoring coverage in severe/high-volume
  regimes.
- That monitoring advantage does not necessarily translate into higher final
  downstream accuracy when MMD-RBF also triggers adaptation at the same time.
- Therefore, the correct QK-MMD claim is operational monitoring advantage, not
  universal downstream superiority.

## Recommended manuscript use

Use this result as a robustness/limitation analysis.

Do not present it as a failure of the paper. Present it as evidence that the
benefit of QK-MMD lies in earlier or more persistent drift monitoring, while
post-adaptation downstream performance is dominated by the shared retraining
mechanism.
