# Knowing When Not to Retrain: label-efficient safe readaptation for adaptive NIDS

Reframes Paper 2 from a quantum-kernel drift-detector comparison into a **solution paper** on the
adapt/no-adapt decision, and delivers the deployable method + full manuscript draft.

## The story (and why it's Q1-shaped)
1. **Readaptation is regime-dependent and sometimes harmful.** Across CICIDS2017, UNSW-NB15 and ToN-IoT the
   value of drift-triggered retraining spans **+19.5 to −4.5 BA points**; in ToN-IoT scanning, *no adaptation*
   beats every triggered strategy (classical or quantum).
2. **Mechanism law:** adaptation benefit ≈ deployed-model degradation, **r = −0.89** — a quantity drift
   detectors cannot see. Hence detection ≠ decision.
3. **The detector is not the lever:** classical and quantum-kernel monitors behave the same; an oracle-regret
   analysis quantifies the headroom; simple k-of-n/cooldown policies fail (pre-registered negative).
4. **Solution — a label-efficient validate-before-commit gate:** on each trigger, retrain a candidate but
   deploy it only if it beats the incumbent on a small labeled probe. Pre-registered, 30 seeds, both KS-max
   and QK-ZZ:
   - ToN-IoT (harm): naive −1.36 / −3.69 → gate **+0.93 / +1.06**; significantly above **both** naive
     (+2.30 [1.15,3.63] / +4.74 [2.47,7.69]) **and** no-adaptation (+0.93 [0.53,1.36] / +1.06 [0.77,1.40]).
   - Benefit/mixed preserved; **zero-label variant fails** (labels are necessary).
5. **Robustness (post-registration):** label-efficiency frontier shows **~8 labels/drift already avoid harm**
   (plateau ~+1.1 by budget 32–64); benefit preserved across **three** benefit regimes (PortScan, Wednesday
   +16.3, DDoS +25.3).
6. **Downstream generalization (four classifiers):** the r=−0.89 law holds for SVC-RBF, Random Forest,
   LogReg and MLP; **net-harm is specific to the fragile SVC-RBF downstream** (RF/LogReg/MLP stay
   non-negative on ToN-IoT), so the universal-harm hook is qualified; and the **gate is universally safe** —
   across all 4 downstream × 3 regimes it never underperforms no-adaptation or naive triggering (§5.7, Table 6,
   Fig 6). This removes a likely reviewer landmine and generalizes the two most defensible claims.

## What's in this branch (11 commits)
- **Code:** `--adaptation-gate {none,labeled_probe,unsup_disagree}` in `run_paper2_progressive_readaptation.py`.
- **Experiments:** pre-registered Phase 2 (30 seeds, 3 regimes × 2 detectors × 4 gates) + Phase 2b robustness.
- **Analysis (reproducible):** `aggregate_paper2_phase2_gated`, `make_paper2_{oracle_regret_decision,ba_f1_summary,budget_curve,paper_tables,figures}`.
- **Manuscript:** `manuscript/paper2_manuscript_draft_002.md` (§1–§8, solution-framed) + `references.bib`
  (50 verified refs; all 40 cited keys resolve).
- **Tables 1–5** (Markdown + LaTeX) and **Figures 1–5**.
- **`REPRODUCE.md`** (artifact-evaluation ready).
- **Notes:** pre-registration, checkpoints, mechanism-law audit, salvage-review addendum.

## Honest status
Q1 credibility ~55–60%. Strengths: pre-registration, 30 seeds + CI95, detector-invariance, deployable
label-cheap solution, unifying mechanism law, honest negatives. Disclosed threats (all answered in-text):
gate novelty is moderate (we show it is *necessary*), retraining uses true labels (the reported cost is the
probe budget), 3 regimes in the confirmatory set (breadth extended in §5.6).

## TODO before submission (author)
- [ ] Fill `@misc{fernandez_paper1}` with the real Paper 1 reference.
- [ ] Proofread the few OCR-flagged / confidence-medium refs (see `references.bib` header).
- [ ] Convert Markdown → venue LaTeX (pandoc handles `\cite{}` + `references.bib`); adjust to author voice.
- [ ] Optional: format secondary appendix tables (feature-map, UNSW/ToN full).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
