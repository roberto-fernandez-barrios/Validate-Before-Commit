# Paper 2 Safe Readaptation Phase 1 Protocol 001

## Purpose

This protocol defines the minimal Phase 1 experiment for the safe-readaptation pivot.

Phase 1 is not designed to rescue a quantum-advantage claim.

It is designed to test the following claim:

> Drift detection alone is insufficient for adaptive IDS readaptation. Safe readaptation policies are required because drift-triggered updates can be beneficial, neutral, or harmful depending on the network regime.

## Background

Phase 0 showed that existing results contain three regimes:

1. Benefit regime:
   - triggered readaptation improves IDS performance.

2. Mixed regime:
   - some drift monitors improve performance while others damage it.

3. Harm regime:
   - no-adaptation outperforms every triggered-readaptation strategy.

This justifies a minimal policy experiment.

## Central research question

RQ1:

Can safe readaptation policies reduce harmful IDS updates while preserving useful adaptation gains under progressive network drift?

## Secondary research question

RQ2:

Do quantum-kernel and classical drift monitors induce different safe-readaptation operating profiles?

## Explicit non-claim

This experiment does not claim universal quantum advantage.

QK-MMD is evaluated as one family of drift signals inside a broader safe-readaptation framework.

## Datasets and regimes

Only three regimes are included.

They are selected before running Phase 1 because they represent the three Phase 0 outcomes.

### Regime 1: Benefit

Dataset/regime:

- CICIDS2017 PortScan

Reason:

- Readaptation clearly improves over no-adaptation.
- QK-MMD ZZ was the best or among the best methods.
- Tests whether conservative policies preserve useful gains.

### Regime 2: Mixed

Dataset/regime:

- UNSW-NB15 Reconnaissance

Reason:

- Some methods improve over no-adaptation.
- Some methods harm performance.
- Tests whether safe policies can separate useful from harmful signals.

### Regime 3: Harm

Dataset/regime:

- ToN-IoT Scanning

Reason:

- No-adaptation outperforms all triggered-readaptation methods.
- Tests whether safe policies can avoid harmful readaptation.

## Excluded regimes

The following are excluded from Phase 1 to avoid experiment sprawl:

- CICIDS2017 DDoS
- CICIDS2017 Wednesday
- Thursday WebAttacks
- UNSW-NB15 DoS
- ToN-IoT DDoS
- ToN-IoT Injection
- feature-map sensitivity variants
- additional datasets

These may be used only in appendix or future work, not for Phase 1 model/policy selection.

## Detectors

Only two detectors are included.

### Detector 1: QK-MMD ZZ

Reason:

- canonical quantum-kernel detector in the current paper;
- strongest or most interpretable QK profile in PortScan and UNSW Reconnaissance;
- avoids feature-map shopping.

Configuration:

- q_reps = 1
- q_input_scaling = atan_standard

### Detector 2: KS-max

Reason:

- cheap, strong classical baseline;
- competitive on UNSW-NB15;
- operationally simple.

Excluded detectors:

- Energy distance
- MMD-RBF
- JSD
- QK-MMD PauliXZ
- QK feature-map repetitions 2/3

Reason for exclusion:

- reduce experiment sprawl;
- prevent post-hoc detector shopping;
- focus on policy behavior rather than detector leaderboard.

## Policies

The following policies are fixed before execution.

### Policy 0: no_adaptation

Never readapt.

Purpose:

- safety baseline.

### Policy 1: immediate_trigger

Current detector-triggered readaptation.

Rule:

- adapt whenever the detector trigger condition fires.

Purpose:

- current baseline.

### Policy 2: k2_of_3

Rule:

- adapt only if at least 2 of the last 3 windows trigger.

Purpose:

- moderate confirmation policy.

### Policy 3: k3_of_5

Rule:

- adapt only if at least 3 of the last 5 windows trigger.

Purpose:

- conservative confirmation policy.

### Policy 4: k2_of_3_cooldown3

Rule:

- adapt only if at least 2 of the last 3 windows trigger;
- after adaptation, block further adaptations for 3 windows.

Purpose:

- moderate confirmation with repeated-update suppression.

### Policy 5: k3_of_5_cooldown5

Rule:

- adapt only if at least 3 of the last 5 windows trigger;
- after adaptation, block further adaptations for 5 windows.

Purpose:

- conservative confirmation with stronger repeated-update suppression.

## Why these policies are not arbitrary

The policies form a small monotonic family:

- 1/1: most sensitive;
- 2/3: moderate confirmation;
- 3/5: conservative confirmation;
- cooldown 3/5: adaptation-frequency control.

The goal is not to tune the best k.

The goal is to test whether increasing confirmation/cooldown reduces harmful readaptation while preserving useful gains.

## Metrics

Primary metrics:

1. mean balanced accuracy;
2. cumulative gain vs no-adaptation;
3. cumulative error area;
4. number of readaptations.

Secondary metrics:

5. detector runtime;
6. fit runtime;
7. trigger rate;
8. first adaptation window;
9. harm relative to no-adaptation.

Policy-specific metrics:

10. gain retained relative to immediate_trigger;
11. adaptation reduction relative to immediate_trigger;
12. harm avoided in the harm regime.

## Success criteria

The pivot passes Phase 1 if all conditions hold:

### Condition A: Benefit preservation

In CICIDS2017 PortScan:

- at least one safe policy preserves at least 70% of the immediate-trigger gain;
- and reduces readaptations relative to immediate_trigger.

### Condition B: Harm avoidance

In ToN-IoT Scanning:

- at least one safe policy improves over immediate_trigger;
- and moves performance closer to no_adaptation;
- and reduces readaptations.

Strong pass:

- safe policy is statistically tied with no_adaptation or better.

### Condition C: Mixed-regime non-degradation

In UNSW-NB15 Reconnaissance:

- safe policy does not materially underperform immediate_trigger;
- and reduces negative-gain behavior for unstable detectors/policies.

### Condition D: No quantum-only dependency

The safe-readaptation claim must hold even if the quantum detector is removed.

QK-MMD may provide useful operating points, but the paper claim cannot depend exclusively on QK winning.

## Failure criteria

The pivot fails if any of the following happen:

1. safe policies destroy most of the CICIDS PortScan gain;
2. safe policies fail to reduce harm in ToN-IoT Scanning;
3. improvements only appear after selecting policies post-hoc;
4. the only positive result requires a QK-only claim;
5. results are too small to justify a new contribution.

## Stop rule

After this Phase 1 experiment:

- no new datasets;
- no new detectors;
- no feature-map tuning;
- no additional policy grid;
- no repeated attempts to rescue Q1.

If Phase 1 passes, write the pivoted safe-readaptation paper.

If Phase 1 fails, write the Q2 detector-characterization paper.

## Main paper if Phase 1 passes

Working title:

Safe Readaptation under Network Drift: When Drift Detection Should Not Trigger IDS Updates

Main claim:

> Adaptive IDS should not equate drift detection with automatic readaptation. Across network regimes, triggered readaptation can help, hurt, or behave inconsistently. Simple safe-readaptation policies can reduce harmful updates while preserving useful adaptation gains.

Role of QK-MMD:

> QK-MMD is evaluated as a quantum-kernel drift signal within the safe-readaptation framework. It provides useful operating profiles in selected regimes but is not claimed to be universally superior.

## Main paper if Phase 1 fails

Working title:

Operational Characterization of Quantum-Kernel MMD Drift Monitors for Adaptive Intrusion Detection

Main claim:

> QK-MMD induces regime-dependent operational profiles, but there is no robust external evidence of universal quantum advantage.

## Pre-registration statement

This protocol is written before running Phase 1.

No additional methods, datasets, feature maps, or policy parameters may be added after observing Phase 1 results.

## Final decision

Proceed to implementation of Phase 1 only after this protocol is saved.

Do not run large experiments until the implementation is inspected and validated with a smoke test.
