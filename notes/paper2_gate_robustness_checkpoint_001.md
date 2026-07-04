# Paper 2 — Gate robustness (Phase 2d/e/f): label latency, harm breadth, cost knob

**Date:** 2026-07-04 · **Status:** post-registration robustness (SVC-RBF downstream, KS-max, gate lp32).
Artifacts: `results/tables/paper2_gate_robustness_001/` (3 CSVs), Fig 7. Code: `--probe-lag`, `--gate-margin`.
Analysis: `make_paper2_gate_robustness`.

## A — Label latency (answers "no real-time labels" critique) ✓ STRONG
Probe drawn from traffic labeled up to 20 windows in the past. Gate stays safe & effective at every lag:

| regime | lag0 | lag5 | lag10 | lag20 | naive |
|---|---:|---:|---:|---:|---:|
| PortScan | +8.27 | +8.39 | +8.20 | +8.06 | +7.79 |
| UNSW Recon | +1.13 | +1.26 | +1.17 | +0.97 | +0.92 |
| ToN-IoT (harm) | +0.93 | +0.98 | +1.06 | +0.95 | −1.36 |

→ The gate tolerates realistic labeling delay; it does not need instantaneous labels. (Fig 7.)

## B — Harm breadth (3 ToN-IoT regimes with SVC) ✓
Net-harm of naive triggering is not one regime; gate fixes all three:

| regime | no-adapt BA | naive gain | gate gain | gate avoids harm |
|---|---:|---:|---:|---|
| ToN-IoT Scanning | 92.2 | −1.36 | +0.93 | yes |
| ToN-IoT DDoS | 91.2 | **−16.81** | +1.26 | yes |
| ToN-IoT Injection | 92.5 | −1.21 | +0.80 | yes |

→ Blindes "harm is a single regime". The DDoS −16.81 with naive triggering is a dramatic illustration.

## C — Commit-margin knob
Raising ε from 0 reduces commits at ~equal gain (operating characteristic):

| regime | ε=0 | ε=0.01 | ε=0.02 | ε=0.05 |
|---|---|---|---|---|
| PortScan | +8.27 / 3.1c | +8.29 / 2.2c | +8.29 / 2.2c | +7.91 / 1.6c |
| UNSW | +1.13 / 2.6c | +1.23 / 2.0c | +1.23 / 2.0c | +1.08 / 1.1c |
| ToN-IoT | +0.93 / 2.2c | +0.82 / 1.2c | +0.82 / 1.2c | +0.27 / 0.5c |

→ ε≈0.01–0.02 is a sweet spot: ~30% fewer adaptations at equal benefit. The gate is a tunable policy.

## D — Adversarial / noisy validation labels (Phase 2g) ✓ ELEVATES (security angle)
An attacker (or faulty labeler) flips a fraction of the probe labels the gate trusts. Gate gain vs
no-adaptation (SVC, KS, lp32, 20 seeds), `--probe-poison`:

| regime | 0% | 10% | 20% | 40% | naive |
|---|---:|---:|---:|---:|---:|
| PortScan | +8.27 | +8.23 | +8.07 | +7.81 | +7.79 |
| UNSW Recon | +1.13 | +1.36 | +1.24 | +1.06 | +0.92 |
| ToN-IoT (harm) | +0.93 | +0.88 | +0.89 | +0.32 | −1.36 |

→ **Fails safe.** `still_beats_naive` and `avoids_harm` = True in all 12 cells. Even at 40% flipped labels
(near pure-noise 50%), the gate never goes negative and never below naive; ToN-IoT degrades gracefully
(+0.93→+0.32). Label noise perturbs deployed and candidate BA estimates symmetrically, moving the gate
along the naive→oracle line without pushing it below the safe baseline. This is a security-venue-aligned
property ("safe readaptation under adversarial supervision") — elevates, not just defends. (Fig 8.)

Also: mechanism law strengthened — pooled r=−0.82, CI95 [−0.95,−0.59] over 16 model×regime points (Fig 2b).

## Manuscript integration (done)
Folded into §5.6 "Gate robustness (post-registration)" (5 bullets: label efficiency, benefit breadth,
label latency, harm breadth, cost knob) + Fig 7; abstract + limitations updated (latency now modeled).
All positive for the paper: answers the last realism landmine (latency), broadens harm to 3 regimes,
and turns the gate into a tunable operating point.
