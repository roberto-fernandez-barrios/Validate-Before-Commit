# Amendment 004 — checkpoint (all runs complete, all outcomes reported)

**Date:** 2026-07-14. Protocol: `paper2_harness_v2_amendment_004.md` (committed+pushed at
`3762318` BEFORE any run below). Runner backward-compat verified: seed 104 ToN lp32 under the
modified runner is bit-identical to the published run (`smoke004_regression`). 45 runs
(39 v6 robustness + 6 temporal), 30 seeds each, zero failures. Audit: 208/208.

## A. Corrected temporal streams (seeds 165–194 fri / 196–225 wed / 227–256 thu)
Headline = BA over two-class windows; secondary = accuracy over all windows.
- **Friday**: no-adapt 71.97; naive +13.55 [11.00,16.07]; gate +7.22 [4.73,9.61];
  gate−naive **−6.34 [−6.83,−5.90]** (premium GREW vs the flawed run's −1.42) — but on
  overall accuracy the gate **beats** naive (+4.19 [3.85,4.52]).
- **Wednesday**: no-adapt 53.35; naive +27.63; gate +28.03; gate−naive **+0.40 [0.09,0.74]**
  (no premium).
- **Thursday**: no-adapt 61.08; naive +22.74; gate +17.76; gate−naive −4.98 [−9.21,−1.38] BA,
  +1.23 [0.61,1.86] accuracy.
- **Mechanism identified**: the gate inherits the metric/composition of its probe. A natural-
  composition past-window probe is benign-dominated → optimizes accuracy, not BA. Reported
  as the gate's honest boundary, with cause. All three streams are deep-benefit (every
  Tuesday incumbent collapses); a chronological harm/mixed stream remains an open external test
  (disclosed in Limitations).

## B. v2 robustness suite (seeds 104–133, paired on common streams)
- **Budget**: b≥32 stable (ToN lp64 +0.92, lp128 +1.01). **b=8 does NOT fully replicate v1**:
  ToN −0.42 [−1.15,0.23] (harm-reducing vs naive +1.22, not net-positive). b=16 borderline
  +0.29. → operating point revised to b=32 everywhere in the paper.
- **Latency 20**: ToN holds (+0.95); PortScan pays −0.47 [−0.74,−0.22] vs fresh.
- **Corruption**: harm avoidance survives 40% flips (+1.60 above naive); net benefit survives
  25% (+0.57) but not 40% (−0.04). Sharper than the v1 claim; abstract/README updated.

## C. Two-stage gate (train-gating; instantiates the sunk-cost-correct §3.4)
ToN: trains 0.90 candidates/stream (vs 3.43 lp32; −74%), total labels 1,182 (< naive's
2,594), still net-positive +0.16 [0.03,0.31]. PortScan pays −1.00 vs plain gate. UNSW ≈ naive.

## D. Calibrated ensemble (review request) — claim REVISED
Platt-calibrated soft ensemble: ToN +0.56 [0.26,0.87]; PortScan +8.55; UNSW +1.72
(**+0.51 [0.38,0.66] above naive — calibration FIXES the dilution and beats the gate there**).
Gate remains ahead in ToN (+0.23 [0.04,0.41]) and PortScan (+0.57 [0.10,1.11]) and is the only
policy with an explicit no-deploy decision. "None attains safety and full benefit" REMOVED from
the paper; replaced by the accurate combination claim.

## E. river reference monitors
Unit cross-check (`paper2_monitor_validation_004.csv`): our DDM ≈ river's (94% agreement);
**our ADWIN variant under-fires (57%)** — Sol's suspicion confirmed; reference ADWIN reported
instead. In-harness river-DDM **replicates the net-harm** (ToN −2.23 [−5.29,−0.05]); river-ADWIN
fires rarely (PortScan +1.77 vs naive +8.25; zero triggers UNSW/ToN).

## F. Decision quality + hierarchical model (locked definitions, existing logs)
ToN: beneficial-rejection 4.9%, recall 0.95, regret 0.0020 vs always-commit 0.0452 (~22×).
PortScan: 0.0028 vs 0.0140 (~5×). Pooled: precision 0.74, recall 0.87, harmful-commit 23%.
MixedLM (Δ5 ~ deg + score + severity + t, seed RE): only deg_pre5 excludes 0 — pooled
−1.02 [−1.17,−0.87]; per-regime −1.10/−0.43/−1.15 (ToN via cluster-bootstrap, boundary MLE).
LORO R²: 0.18/0.36 (PortScan/ToN held out), ≤0 without degradation; UNSW fails in scale
(−10.5) → claim stated as ranking signal, not calibrated law.

## G. Label/compute accounting (Table label_cost)
Candidates dominate every policy's bill; the gate's TOTAL cost exceeds naive's (3,626 vs
2,594 in ToN; probe ≈3%). "Label-efficient" = the decision, stated explicitly. Two-stage is
the cheapest safe policy.

## H. Manuscript/artifact surgery (Sol's imprescindibles, all done)
Commit/deployment reframing everywhere; ε* = λ_U/(λ_e·N) with sunk-cost discussion and the
two-stage instantiation; "fails safe"/"never significantly worse" purged (manuscript, README,
highlights, graphical abstract regenerated); v2 promoted to §5.1 + main table; §5.10 broken
into structured blocks with temporal + cost tables; Fig 2 (coupled) → appendix, per-trigger
figure central; classifiers_lp32 block added to the committed aggregator (traceability closed);
README/REPRODUCE synchronized (v2 primary example, amendment commands, temporal commands,
requirements-lock.txt); pre-specified vs registered standardized; abstract 249 words, leads
with the two-decision framing and reports the boundary. Audit extended 155 → **208 checks**.
Builds: main.pdf 28 pp, main_ieee.pdf 22 pp (body auto-ported from main.tex).
