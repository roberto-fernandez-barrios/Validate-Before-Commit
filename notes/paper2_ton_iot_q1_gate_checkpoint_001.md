# Paper 2 ToN-IoT Q1-Gate Checkpoint 001

## Purpose

This checkpoint documents the final external-dataset Q1-gate experiment for Paper 2.

The experiment was introduced after UNSW-NB15 medium produced mixed and weak external validation. The goal was to test whether a third independent network IDS dataset could provide a clearer external QK-MMD operating profile.

## Dataset

Dataset:

- ToN-IoT Network Train/Test dataset

Raw file:

- data/raw/ton_iot/train_test_network.csv

Dataset counts:

- normal: 50,000
- backdoor: 20,000
- ddos: 20,000
- dos: 20,000
- injection: 20,000
- password: 20,000
- ransomware: 20,000
- scanning: 20,000
- xss: 20,000
- mitm: 1,043

Label columns:

- label: binary
- type: attack category

## Preprocessing

Processed directory:

- data/processed/ton_iot_q1_gate/

Feature policy:

- numeric features retained;
- selected low-cardinality categorical features one-hot encoded;
- high-cardinality identifiers and text fields dropped;
- resulting feature count: 88.

Categorical features included:

- proto
- service
- conn_state
- dns_AA
- dns_RD
- dns_RA
- dns_rejected
- ssl_version
- ssl_cipher
- ssl_resumed
- ssl_established
- http_trans_depth
- http_method
- http_version
- weird_notice

Split policy:

- per-type 50/50 split;
- normal rows split between reference and current to avoid overlap;
- target attack appears only in current for each scenario;
- reference contains benign plus non-target attacks.

Scenarios prepared:

1. DDoS
2. Scanning
3. Injection

Each scenario:

- reference rows: 95,521
- reference label counts:
  - ATTACK: 70,521
  - BENIGN: 25,000
- current rows: 45,000
- current label counts:
  - BENIGN: 25,000
  - ATTACK: 20,000

## Smoke results

The initial 3-seed smoke showed:

- DDoS: negative for QK.
- Injection: negative or not promising for QK.
- Scanning: apparently promising for QK-MMD ZZ.

According to the pre-registered Q1-gate rule, only Scanning was escalated to medium.

## ToN-IoT Scanning medium setup

- seeds: 10
- post_windows: 100
- ramp_windows: 100
- calibration_windows: 30
- n_permutations: 100
- methods:
  - Energy distance
  - MMD-RBF
  - KS-max
  - JSD
  - QK-MMD ZZ
  - QK-MMD PauliXZ
- q_reps: 1
- q_input_scaling: atan_standard

Raw results:

- results/raw/paper2_ton_iot_scanning_medium_001/

## ToN-IoT Scanning medium results

| method | BA | cumulative error | gain vs no adapt | adaptations | detector runtime |
|---|---:|---:|---:|---:|---:|
| No adaptation | 0.920125 | 7.987500 | 0.000000 | 0.0 | 0.000000 |
| QK-MMD PauliXZ | 0.913906 | 8.609375 | -0.621875 | 2.8 | 7.470943 |
| Energy distance | 0.907336 | 9.266406 | -1.278906 | 1.3 | 0.065371 |
| JSD | 0.889484 | 11.051563 | -3.064063 | 2.6 | 0.026589 |
| QK-MMD ZZ | 0.887313 | 11.268750 | -3.281250 | 3.0 | 7.158150 |
| KS-max | 0.878172 | 12.182813 | -4.195313 | 2.5 | 0.263484 |
| MMD-RBF | 0.875211 | 12.478906 | -4.491406 | 1.2 | 4.535770 |

## Interpretation

The Scanning smoke result did not survive medium validation.

The key result is that no-adaptation outperforms every triggered-readaptation strategy.

All detectors produce negative gain versus no-adaptation.

QK-MMD PauliXZ is the best adaptive detector in mean BA, but it still underperforms no-adaptation and requires 2.8 readaptations on average.

QK-MMD ZZ performs poorly:

- BA: 0.887313
- gain vs no-adaptation: -3.281250
- adaptations: 3.0
- runtime: 7.158150 seconds

Therefore, ToN-IoT does not provide positive external validation for a QK-MMD advantage.

## Q1-gate decision

The Q1-gate fails.

ToN-IoT does not support escalation toward a Q1 quantum-advantage claim.

The final experimental conclusion is:

> QK-MMD exhibits interesting regime-dependent operational profiles on CICIDS2017, but these profiles do not robustly replicate across external datasets. UNSW-NB15 gives mixed and marginal evidence, while ToN-IoT shows that triggered readaptation can underperform no-adaptation in the tested scanning scenario.

## Strategic consequence

Stop experiments.

Do not test more datasets.

Do not test more ToN-IoT attacks.

Do not tune policies post-hoc.

Do not scale ToN-IoT to 30 seeds.

Move to manuscript writing.

## Paper positioning

The paper should be positioned as a strong Q2 contribution:

> An operational characterization of quantum-kernel MMD drift monitors for adaptive IDS readaptation under progressive drift.

It should not be positioned as:

> A demonstration of robust quantum advantage.

## Main paper recommendation

Main paper:

- CICIDS2017 four-regime story.
- UNSW-NB15 external mixed validation, briefly.
- Honest limitations.

Appendix or repository note:

- ToN-IoT Q1-gate negative result.

ToN-IoT should not become a central part of the manuscript because it dilutes the already weak external-validation story. It is useful internally and for transparency, but not as the main narrative.

## Final decision

This is the final experimental stopping point.

The next action is manuscript writing.
