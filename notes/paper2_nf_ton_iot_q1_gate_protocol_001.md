# Paper 2 NF-ToN-IoT Q1-Gate Protocol 001

## Purpose

This protocol defines the final external-dataset gate for attempting to move Paper 2 from a strong Q2 paper toward a possible Q1 submission.

The current state is:

- CICIDS2017 supports a coherent regime-dependent operational story for QK-MMD.
- UNSW-NB15 external validation is mixed and does not replicate a strong QK advantage.
- More CICIDS2017 experiments are not recommended.
- More UNSW-v1 experiments are not recommended.

Therefore, this protocol defines one final external test using a NetFlow-based dataset with a common feature representation.

## Dataset

Primary dataset:

- NF-ToN-IoT

Reason:

- It is outside CICIDS2017.
- It uses NetFlow-style features.
- It belongs to the NetFlow NIDS dataset family designed for cross-dataset evaluation.
- It contains multiple attack categories with enough samples.
- It has substantially more benign samples than NF-BoT-IoT.

Backup dataset:

- NF-BoT-IoT

Only use NF-BoT-IoT if NF-ToN-IoT is unavailable or unusable.

## Research question

Does QK-MMD show a non-trivial operational profile on a second independent NetFlow-style NIDS dataset?

A non-trivial profile means at least one of:

1. comparable downstream BA/gain with fewer readaptations;
2. significantly higher downstream BA/gain with acceptable extra readaptations;
3. a clearly distinct operating point not reproduced by Energy, MMD-RBF, KS or JSD.

## Candidate attack regimes

Primary NF-ToN-IoT smoke scenarios:

1. DDoS
2. Scanning
3. Injection

Rationale:

- DDoS is analogous to CICIDS DDoS.
- Scanning is analogous to PortScan/Reconnaissance.
- Injection is analogous to WebAttacks/application-layer attacks.

## Smoke configuration

Methods:

- Energy distance
- MMD-RBF
- KS-max
- JSD
- QK-MMD ZZ
- QK-MMD PauliXZ

Seeds:

- 1,2,3

Windows:

- post_windows = 20
- ramp_windows = 20
- calibration_windows = 10

Permutations:

- n_permutations = 50

Quantum configuration:

- q_reps = 1
- q_input_scaling = atan_standard

## Stop rule

Stop permanently and write Q2 if:

- QK-MMD is worse than classical baselines in all smoke scenarios;
- QK-MMD only matches classical baselines while being more expensive;
- all scenarios show tiny gains comparable to UNSW-NB15;
- preprocessing becomes a major new project.

Proceed to medium only if:

- at least one scenario shows QK-MMD with a useful operational profile;
- the effect is not obviously due to a data preparation artifact;
- the scenario has enough benign and attack samples.

## Medium rule

If smoke is promising, run medium only for the promising scenario(s):

- seeds = 1..10
- post_windows = 100
- ramp_windows = 100
- calibration_windows = 30
- n_permutations = 100

Do not run 30 seeds unless medium shows a clear, interpretable QK profile.

## Reporting rule

All NF-ToN-IoT smoke results must be documented, including negative results.

If results are negative, they will be used to justify stopping the Q1 attempt and writing a Q2 paper.

## Final decision rule

This is the last external dataset exploration.

After NF-ToN-IoT smoke/medium:

- if QK signal is clear: prepare Q1-oriented manuscript;
- if QK signal is weak or negative: stop experiments and write Q2 manuscript.
