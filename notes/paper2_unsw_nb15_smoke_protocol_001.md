# Paper 2 UNSW-NB15 External Dataset Smoke Protocol 001

## Purpose

This protocol defines the first external-dataset validation smoke for Paper 2.

The current evidence is based on CICIDS2017 across multiple attack regimes. That is enough for a strong Q2 submission, but a Q1 submission requires external validation on a dataset outside the CICIDS2017/CICFlowMeter ecosystem.

## Dataset choice

Recommended dataset:

- UNSW-NB15

Reason:

- It is independent from CICIDS2017.
- It is a canonical IDS benchmark.
- It includes binary labels and attack categories.
- It allows attack-category-based drift scenarios.
- It is more valuable for Q1 than adding more CICIDS2017 scenarios.

## Goal of the smoke

The smoke is not intended to produce publishable claims.

It only answers:

1. Can the existing Paper 2 pipeline be adapted to UNSW-NB15?
2. Are there enough samples per attack category?
3. Can we build progressive drift scenarios analogous to CICIDS2017?
4. Does QK-MMD show any non-trivial behavior outside CICIDS2017?

## Candidate scenarios

Preferred smoke scenarios:

1. Normal/reference -> DoS current
2. Normal/reference -> Reconnaissance current

Alternative scenarios if sample counts are low:

- Normal/reference -> Generic
- Normal/reference -> Exploits
- Normal/reference -> Fuzzers

## Smoke configuration

Methods:

- Energy distance
- MMD-RBF
- QK-MMD ZZ

Seeds:

- 1,2,3

Windows:

- 20 post-windows
- 20 ramp-windows

Calibration:

- 10 calibration windows
- 50 permutations

Quantum config:

- q_reps = 1
- q_input_scaling = atan_standard

## Stop criteria

Stop after smoke if:

1. preprocessing is unstable;
2. sample counts are too low;
3. labels cannot be mapped consistently;
4. all detectors fail to produce meaningful adaptation behavior;
5. QK-MMD is clearly dominated with no useful trade-off.

Proceed to medium/final only if:

1. pipeline works cleanly;
2. at least one scenario has enough samples;
3. QK-MMD shows either efficiency, recovery, or a meaningful negative result worth reporting.

## Reporting rule

If UNSW-NB15 is used, all smoke results must be documented, even if QK-MMD performs poorly.

Negative UNSW results should be treated as external limitation, not hidden.
