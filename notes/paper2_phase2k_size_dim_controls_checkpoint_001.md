# Phase 2k checkpoint — the harm is not a size or dimensionality artifact

**Date:** 2026-07-14 · Response to the strict external (GPT-5.6) mock review, blocking point 1
(candidate-size confound) and the PCA-8 concern. 8 runs × 30 seeds (KS-max, SVC, Phase-2 settings).
Artifacts: `results/tables/paper2_phase2k_size_dim_controls_001/summary.csv`.

## Verdict: the size confound is refuted — in the strongest possible direction

| arm | ToN (harm) | PortScan (benefit) | UNSW (marginal) |
|---|---|---|---|
| naive, 512/class (paper) | −1.36 | +7.79 | +0.92 |
| **naive, 2000/class (size-matched)** | **−5.34 [−8.73, −2.49]** | +6.70 | +3.31 |
| gate lp32, 2000/class | +0.58 | **+9.33** | +3.37 |
| naive, full-dim (no PCA) | −0.65 [−3.03, +1.44] (NS) | **+16.2** | — |

- The reviewer's simplest explanation ("keeping a 4000-sample model vs replacing it with a
  1024-sample one") predicts the harm should shrink or vanish with size-matched candidates.
  **It quadruples.** A larger candidate fits the current mixture better and mis-specializes
  harder while the ramp keeps advancing — exactly the paper's mechanism.
- The gate stays safe and beneficial with big candidates (and PortScan improves to +9.33).
- Candidate size DOES shift magnitudes in the marginal regime (UNSW +3.31 vs +0.92) — reported.
- Full dimensionality: benefit doubles (+16.2), harm point estimate stays negative but is NS at
  30 seeds — reported plainly; PCA-8 attenuates but does not create the phenomenon.

## Honesty pass applied in the same revision (review points verified and accepted)

- **Pre-registration provenance** (CONFIRMED: prereg fixed 10 seeds, conditional PortScan
  scaling; prereg+checkpoint entered the repo in one commit): §4 renamed "Pre-specified
  protocol" and discloses both the 10→30 conditional expansion and the non-external registry;
  "pre-registered" → "pre-specified" in abstract/intro/highlights/README/graphical abstract.
- **Calibration windows**: manuscript said 20 (my error, taken from the argparse default);
  runs used 30 (verified: thresholds identical between phase2 and cal-30 phase2i runs). Fixed.
- **RNG stream divergence across arms** (CONFIRMED: per-method seed offsets): "the only
  manipulated variable" → "only designed difference"; "paired bootstrap" → "seed-matched
  bootstrap" with the realization caveat; Limitations paragraph added; common-stream harness
  named as the natural hardening.
- **Probe/train overlap** (CONFIRMED: sampling with replacement from shared pools): "never
  overlaps" replaced by the quantified statement (pools ≥ 2×10⁴/class → expected collisions
  < 1 flow per 32-flow probe; not identifier-disjoint).
- **Prevalence conditioning** (CONFIRMED: max(1,·) floor): §5.6 now states the probe is
  conditioned on ≥1 attack and that an unconditioned 32-sample at π=0.01 is attack-free 72%
  of the time (conditioning = labeling until the first attack, the ≈1/π inspections).
- **Scope softeners**: "among the gates evaluated" (Pareto), "50/50 replay retraining",
  "(with SVC)/(with KS-max)" factorial honesty; fig-8 caption, highlights, README and
  graphical abstract harmonized with "random label corruption" and "never significantly worse".

Audit: 119 checks, all passing. 23 pp (CAS) / 17 pp (IEEE); abstract 250 words.

## Left open (requires the harness-v2 program, user decision)
Common-stream + identifier-disjoint harness with separate RNGs and per-trigger logging;
externally registered replication (fresh seeds); labeled baselines (holdout-from-batch gate,
performance-aware/DDM trigger at matched label budget, LCB gate); title decision on "Safe".
