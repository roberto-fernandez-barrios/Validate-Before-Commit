# Knowing When Not to Retrain: label-efficient safe readaptation for adaptive NIDS

Reframes Paper 2 from a quantum-kernel drift-detector comparison into a **solution paper** on the
adapt/no-adapt decision, and delivers the deployable method, a full manuscript draft, and an extensive
robustness campaign.

## The story
1. **Readaptation is regime-dependent and sometimes harmful.** Across CICIDS2017, UNSW-NB15 and ToN-IoT the
   value of drift-triggered retraining spans **+19.5 to −4.5 BA points**; with a fragile downstream (SVC-RBF),
   ToN-IoT scanning makes *no adaptation* beat every triggered strategy (classical or quantum).
2. **Mechanism law:** adaptation benefit ≈ deployed-model degradation — **r = −0.89** (SVC), pooled
   **r = −0.82, CI95 [−0.95,−0.59]** across four downstream models — a quantity drift detectors cannot see.
   Detection ≠ decision.
3. **The detector is not the lever:** classical and quantum-kernel monitors behave the same; oracle-regret
   quantifies the headroom; simple k-of-n/cooldown policies fail (pre-registered negative).
4. **Solution — a label-efficient validate-before-commit gate:** retrain a candidate, deploy only if it beats
   the incumbent on a small labeled probe. Pre-registered, 30 seeds, both KS-max and QK-ZZ: ToN-IoT naive
   −1.4/−3.7 → gate **+0.9/+1.1**, significantly above **both** naive (+2.3/+4.7, CI95) **and** no-adaptation
   (+0.9/+1.1, CI95). Zero-label variant fails.

## Robustness campaign (post-registration)
- **Label efficiency:** ~8 labeled flows/drift already avoid harm; plateau by budget 32–64 (Fig 5).
- **Benefit breadth:** benefit preserved across three benefit regimes (PortScan, Wednesday +16.3, DDoS +25.3).
- **Downstream generalization (4 classifiers):** the law generalizes; **net-harm is SVC-specific** (RF/LogReg/MLP
  stay non-negative); the **gate is safe in all 12 downstream×regime cells** (Fig 6, Table 6).
- **Label latency:** gate stays safe with probe labels up to **20 windows stale** (Fig 7).
- **Harm breadth:** net-harm reproduces across three ToN-IoT regimes (Scanning −1.36, DDoS **−16.81**,
  Injection −1.21); gate converts all to positive.
- **Cost knob:** commit margin ε≈0.01–0.02 cuts adaptations ~30% at equal gain.
- **Adversarial validation labels:** the gate **fails safe** — with up to **40% of probe labels flipped** it
  never goes harmful and never below naive (Fig 8). Security-aligned "safe readaptation under adversarial
  supervision".
- **Significance:** paired bootstrap CIs confirm the gate significantly beats naive under every latency and
  poison level in the harm regime, and is **never significantly worse** than naive or no-adaptation in any
  robustness condition.

## What's in this branch (~22 commits)
- **Code:** `--adaptation-gate {none,labeled_probe,unsup_disagree}`, `--downstream-model`, `--probe-lag`,
  `--probe-poison`, `--gate-margin` in `run_paper2_progressive_readaptation.py`.
- **Analysis (reproducible):** aggregate/oracle-regret/ba-f1/budget-curve/downstream/gate-robustness/
  mechanism-law/robustness-significance/paper-tables/figures scripts.
- **Manuscript:** `manuscript/paper2_manuscript_draft_002.md` (§1–§8, solution-framed) + `references.bib`
  (50 verified refs; all cited keys resolve).
- **Tables 1–6** (Markdown + LaTeX) and **Figures 1–8 (+2b)**.
- **`REPRODUCE.md`** (artifact-evaluation ready) and checkpoint notes.

## Honest status
Q1 credibility ~60–63%. Strengths: pre-registration, 30-seed CI95, detector- and downstream-invariance,
deployable label-cheap solution robust to latency and adversarial labels, a mechanism law with a CI. Disclosed
threats (answered in-text): gate novelty is moderate (we show it is *necessary* and characterize its limits);
net-harm is downstream-specific (stated); the confirmatory set is three regimes (breadth extended in §5.6).

## TODO before submission (author)
- [ ] Fill `@misc{fernandez_paper1}` with the real Paper 1 reference.
- [ ] Proofread the few OCR-flagged / confidence-medium refs (see `references.bib` header).
- [ ] Convert Markdown → venue LaTeX (pandoc handles `\cite{}` + `references.bib`); adjust to author voice.
- [ ] Optional: secondary appendix tables (feature-map, UNSW/ToN full).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
