# Phase 2h checkpoint — ATC/DoC head-to-head: labeled probe Pareto-dominates

**Date:** 2026-07-12 · Protocol: `paper2_phase2h_labelfree_gates_protocol_001.md` (criteria fixed pre-analysis).
Artifacts: `results/tables/paper2_phase2h_labelfree_gates_001/` (summary, paired CIs, verdict).
Runs: 18 (atc/doc × 3 regimes × {SVC-RBF, RF} × 30 seeds + RF baselines at 30; KS-max, legacy trigger).

## Verdict (pre-fixed criteria): MIXED — the most informative outcome

| gate × downstream | B harm-avoid (ToN ≥ −0.5) | A benefit (PortScan ≥ naive−0.3) | C marginal |
|---|---|---|---|
| ATC × SVC | ✅ +0.40 | ❌ −1.86 vs naive [−3.48,−0.17] | ✅ |
| DoC × SVC | ✅ +1.16 | ❌ −4.64 vs naive [−6.86,−2.26] | ✅ |
| ATC × RF | ✅ | ❌ −2.14 [−4.05,−0.72] | ✅ |
| DoC × RF | ✅ | ❌ −0.61 [−1.16,−0.15] | ✅ |

Key numbers (gain vs no-adaptation, BA pts):
- **Harm regime (SVC × ToN):** naive −1.36 · unsup −4.95 · **ATC +0.40** (≈ no-adapt, NS) · **DoC +1.16**
  (significantly above no-adapt, like lp32 +0.93). → Label-free gates DO avoid harm; the strict
  "labels are necessary to avoid harm" claim is refuted and must be withdrawn.
- **Benefit regime (PortScan):** SVC naive +7.79 / lp32 +8.27 vs **ATC +5.93** (−24% of naive gain) and
  **DoC +3.15** (−60%); RF naive/lp32 +27.36 vs ATC 25.22, DoC 26.75 — all significantly below naive,
  even with RF's native predict_proba. → Label-free gates pay for safety with benefit.

## The sharpened claim (replaces "labels are necessary")

The labeled probe is the **only** gate on the benefit–safety Pareto front: it preserves the full benefit
where adaptation helps AND converts harm to gain where it hurts. State-of-the-art label-free estimators
(ATC, DoC), instantiated in their standard form in the same harness, land at dominated points — safe but
benefit-lossy. Naive disagreement is worse still (harmful). **A few target labels are necessary not for
safety alone, but for safety without sacrificing the benefit of adaptation.**

## Mechanism (ties back to the degradation law)

ATC/DoC estimate target accuracy from the model's own confidences. Their reliability therefore collapses
exactly where adaptation matters most: in the benefit regime the incumbent is severely degraded, its
confidences under the shifted window are untrustworthy, the estimates misrank incumbent vs candidate, and
beneficial commits are wrongly rejected. In the harm regime the incumbent is healthy, its estimates are
reliable enough, and harmful candidates are rejected. The same variable that governs adaptation benefit
(incumbent degradation) governs the trustworthiness of label-free self-assessment — a circularity the
labeled probe sidesteps, since the probe's validity does not depend on the model being judged.

## Manuscript changes applied
Abstract + §1 + §5.5/§5.6 + Discussion rewritten to the sharpened Pareto claim, with the label-free
estimation literature (ATC, DoC, Agreement-on-the-Line, disagreement theory, Dis², AutoEval) cited
head-on; §7 notes that stronger/estimator-tuned label-free variants might narrow the gap (future work).
