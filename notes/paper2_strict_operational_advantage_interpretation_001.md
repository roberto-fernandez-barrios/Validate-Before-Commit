# Paper 2 strict operational advantage interpretation 001

## Main finding

The strict operational scale analysis identifies a defensible quantum
advantage zone.

QK-MMD does not provide universal downstream superiority. However, under
high-severity and high-volume drift, QK-MMD provides a clear operational
monitoring advantage over MMD-RBF.

## Strict criterion

A strict quantum operational zone requires:

- QK-MMD post-drift alarm persistence at least 5 percentage points higher than MMD-RBF.
- No clean adaptation gain loss relative to MMD-RBF.
- No false-alarm penalty relative to MMD-RBF.
- At least 100,000 additional drift-affected flow-equivalent samples flagged.

## Severity 1.0

At severity 1.0, QK-MMD PauliXZ satisfies the strict criterion.

Compared with MMD-RBF:

- post-drift alarm coverage increases by 0.3367
- clean adaptation gain increases by 0.0085
- false-alarm rate decreases by 0.0333

At scale:

- 1,000,000 flows: approximately 336,667 additional drift-affected flow-equivalent samples flagged
- 10,000,000 flows: approximately 3,366,667 additional drift-affected flow-equivalent samples flagged
- 100,000,000 flows: approximately 33,666,667 additional drift-affected flow-equivalent samples flagged

QK-MMD ZZ also satisfies the strict criterion:

- post-drift alarm coverage increases by 0.3067
- clean adaptation gain increases by 0.0085
- false-alarm rate decreases by 0.0333

At 1,000,000 flows, this corresponds to approximately 306,667 additional
drift-affected flow-equivalent samples flagged.

## Severity 0.75

At severity 0.75, QK-MMD also satisfies the strict criterion at larger traffic
volumes.

QK-MMD PauliXZ:

- post-drift alarm coverage increases by 0.0817
- clean adaptation gain is approximately neutral/slightly positive
- false-alarm penalty is 0.0

At 10,000,000 flows, this corresponds to approximately 816,667 additional
drift-affected flow-equivalent samples flagged.

QK-MMD ZZ:

- post-drift alarm coverage increases by 0.0717
- clean adaptation gain is approximately neutral/slightly positive
- false-alarm penalty is 0.0

At 10,000,000 flows, this corresponds to approximately 716,667 additional
drift-affected flow-equivalent samples flagged.

## Interpretation

This result should be used as the main operational quantum-specific claim.

The correct claim is not that QK-MMD universally improves downstream accuracy.
The correct claim is that QK-MMD provides a strict operational monitoring
advantage in severe/high-volume drift regimes.

## Caveat

The flow-equivalent analysis is an operational proxy. It should not be
presented as a direct count of additional correctly classified samples unless a
future sample-level long-stream experiment computes that directly.

## Paper usage

Use this result in Results and Discussion as:

- evidence of a high-severity/high-volume QK-MMD advantage zone
- explanation of why QK-MMD is useful despite not universally dominating MMD-RBF
- bridge between drift-monitoring gains and operational cybersecurity impact
