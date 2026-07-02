# Paper 2 — Manuscript Draft 002 (solution-framed, post-Phase 2)

> Supersedes `paper2_manuscript_skeleton_001.md` (which was QK-centric, pre-Phase 2). This draft reframes the paper as a *solution* paper around the adapt/no-adapt decision. All numbers are verified against committed artifacts (`results/tables/paper2_*`, 30-seed Phase 2). Prose is submission-oriented; edit voice to taste.

---

## Title

**Knowing When Not to Retrain: Label-Efficient Safe Readaptation for Adaptive Network Intrusion Detection under Concept Drift**

## Abstract

Adaptive network intrusion detection systems (NIDS) retrain their classifiers to cope with concept drift, and a large literature optimizes drift *detectors* to decide when to retrain. We show this framing is incomplete and can be counterproductive. Across three public benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) and seven attack regimes, the value of drift-triggered readaptation ranges from strongly beneficial to actively harmful: in a ToN-IoT scanning regime, naive triggering degrades balanced accuracy below a no-adaptation baseline for every detector we test, classical or quantum-kernel. We find that the sign and size of this effect are governed almost entirely by how much the deployed model has already degraded — the benefit of adaptation correlates with the no-adaptation accuracy at r = −0.89 across regimes — a quantity that drift detectors, which measure distributional change, do not observe. Consistent with this, the choice of detector (including quantum-kernel MMD) does not change the qualitative outcome, and simple confirmation/cooldown policies fail to prevent harm. We therefore reframe readaptation as a cost-aware decision and introduce a label-efficient *validate-before-commit* gate: on each trigger, a candidate model is retrained but deployed only if it beats the incumbent on a small labeled probe. Across benefit, mixed, and harmful regimes and two detectors, the gate (30 seeds, pre-registered) converts net-harmful adaptation into net benefit — in ToN-IoT, from −1.4/−3.7 balanced-accuracy points (naive) to +0.9/+1.1, significantly above both naive triggering (+2.3/+4.7 pts, CI95) and no-adaptation (+0.9/+1.1 pts, CI95) — while preserving the gains where adaptation helps, using roughly one hundred labeled flows. A zero-label variant fails, delimiting the method: a few labels are necessary. Our results indicate that *when not to adapt* is as important as detecting drift, that the decision — not the detector — is the operative lever, and that a small, deployable label budget resolves the harmful-adaptation problem.

## Contributions

1. **A regime taxonomy of readaptation value** across three benchmarks: adaptation is strongly beneficial (CICIDS2017), marginal (UNSW-NB15), or net-harmful (ToN-IoT), quantified with 30-seed CI95.
2. **Evidence that naive drift-triggered readaptation can be net-harmful**, with a mechanistic law: the benefit of adaptation is predicted by deployed-model degradation (r = −0.89), a quantity drift detectors do not measure — hence detection ≠ decision.
3. **Detector-invariance**: classical (Energy, MMD-RBF, KS, JSD) and quantum-kernel (ZZ, PauliXZ) detectors yield the same qualitative outcome; QK-MMD is an instrument, not the lever. An oracle-regret analysis quantifies the headroom left by naive triggering.
4. **A pre-registered negative on simple policies**: k-of-n confirmation and cooldown do not prevent harmful adaptation.
5. **A label-efficient validate-before-commit gate** that resolves the problem: it preserves benefit, avoids harm, and beats both naive triggering and no-adaptation, for both a classical and a quantum detector, with ~100 labeled flows; a zero-label variant fails.

---

## 5. Results

We present results in logical, not chronological, order. Section 5.1 establishes that readaptation is beneficial on CICIDS2017 but *not* on the external benchmarks; 5.2 explains the pattern with a mechanistic law; 5.3 shows the detector — classical or quantum — is not the lever; 5.4 shows simple policies do not fix it; 5.5 presents the label-efficient gate that does; 5.6 reports robustness and controls.

### 5.1 Readaptation is regime-dependent and sometimes harmful

Under progressive drift, an unadapted classifier degrades and triggered readaptation can recover much of the loss — on CICIDS2017. Averaged over 30 seeds and 100 post-drift windows, the best detector-triggered strategy recovers +19.5 balanced-accuracy (BA) points over no-adaptation in the Friday-DDoS regime, +11.9 in Wednesday, +7.6 in WebAttacks and +6.2 in PortScan (Table 1, Fig. 1). This is the familiar picture that motivates adaptive NIDS.

The picture does not survive to independent data. On UNSW-NB15 the best recovery is marginal (+1.4 points for DoS, +0.3 for Reconnaissance), and on ToN-IoT Scanning it becomes *negative*: no detector-triggered strategy matches a no-adaptation baseline (best adaptive −0.6 points; worst −4.5), so the correct decision there is **not to adapt** (Fig. 1). The effect is not a balanced-accuracy artifact: under attack-F1 the CICIDS benefits grow (e.g. +32.3 F1 points for DDoS) and ToN-IoT remains harmful for every detector (Energy −0.8, KS-max −9.5 F1 points). We stress the claim is not "adaptation usually hurts" — it is that the *sign* of the payoff is regime- and dataset-dependent, spanning +19.5 to −4.5 BA points, which is precisely what an adaptive system must anticipate.

### 5.2 The value of readaptation is governed by model degradation, not distribution change

Why does adaptation help enormously in one regime and hurt in another? The answer is not the amount of drift but the state of the deployed model. Across all seven regimes, the benefit of adaptation is almost perfectly predicted by the no-adaptation accuracy: **r = −0.89** between deployed-model BA and adaptation gain (Fig. 2). Where the deployed model has already collapsed (DDoS: 69.8% without adaptation), retraining on a fresh window is a large gain; where it remains strong (ToN-IoT: 92.0%), replacing a well-generalized model with a narrowly-fit current-window model is a net loss.

This exposes the core problem. Drift detectors answer *"has the distribution changed?"*, but an adaptive NIDS needs *"will retraining improve the classifier?"* — and these are different questions. We quantify the gap with a decision-level oracle that, per stream, abstains when adaptation would hurt (holding the detector fixed). The resulting *regret* of naive triggering is essentially zero where adaptation always helps (Wednesday, DDoS: 0.00 points, adaptation hurt on 0% of streams) and largest where it hurts (ToN-IoT: 3.50 points for QK-ZZ, CI95 [0.96, 7.45], adaptation hurt on 80% of streams), scaling monotonically with harm frequency (Fig. 3). The headroom left by naive triggering is real and concentrated exactly where the deployed model is already good.

### 5.3 The detector is not the lever

Because drift detectors are blind to model degradation, improving the detector cannot solve the problem — and it does not. Quantum-kernel MMD monitors do define distinct *operating points* on CICIDS2017 (QK-MMD ZZ triggers 1.8–2.1 fewer readaptations than Energy distance at equivalent accuracy in Wednesday/DDoS, and inverts in PortScan), but at a ~114× monitoring-runtime cost, and these profiles do not replicate externally. Critically, the regime taxonomy and the harmful-adaptation outcome are identical for classical and quantum detectors (Fig. 3, Table 1): on ToN-IoT, naive triggering is net-harmful whether the trigger is KS-max (−1.4 points) or QK-ZZ (−3.7 points). The lever is the adapt/no-adapt decision, not the similarity measure that fires the trigger.

### 5.4 Simple confirmation and cooldown policies do not prevent harm

If the decision is the lever, the natural fix is a smarter trigger policy. We pre-registered a grid of alarm-confirmation (k-of-n) and cooldown policies and evaluated them against fixed success criteria (preserve benefit in PortScan; avoid harm in ToN-IoT; do not degrade UNSW). None passed: in the harmful regime the tested policies remained far below no-adaptation and did not reduce adaptations relative to a conservative legacy baseline (Appendix E). Confirmation and cooldown act on the *persistence* of distributional change, which is exactly the signal that is uninformative about whether adaptation helps. This negative result motivates a policy that acts on the right quantity.

### 5.5 A label-efficient validate-before-commit gate resolves the problem

We introduce a decision gate that acts directly on estimated model improvement. On each drift trigger, a candidate model is retrained as usual, but it is **deployed only if it beats the incumbent on a small labeled probe** drawn from the current window (budget 32 or 64 flows); otherwise the incumbent is kept. We evaluate the gate against the same pre-registered criteria (30 seeds, 100 windows, legacy trigger fixed so the gate is the only variable) across the benefit (PortScan), mixed (UNSW Reconnaissance) and harmful (ToN-IoT) regimes, for both a classical (KS-max) and a quantum (QK-ZZ) detector (Table 2, Fig. 4).

The gate passes every criterion for both detectors. In the harmful regime it turns net-harmful naive triggering into net benefit: ToN-IoT gain moves from −1.36 (KS-max) and −3.69 (QK-ZZ) points to +0.93 and +1.06, **significantly above naive triggering** (+2.30 points, CI95 [1.15, 3.63] for KS-max; +4.74, [2.47, 7.69] for QK-ZZ) and, notably, **significantly above no-adaptation itself** (+0.93, [0.53, 1.36]; +1.06, [0.77, 1.40]) — the gate does not merely stop adapting, it commits the minority of beneficial adaptations while rejecting the harmful majority. In the benefit regime it preserves the full gain (PortScan +8.3/+8.4 points, statistically indistinguishable from naive), and it does not degrade the mixed regime. The label cost is small: roughly 100–160 labeled flows over a 100-window stream at budget 32.

The gate's power comes from labels, not from the confirmation heuristic: a zero-label variant that commits on deployed-vs-candidate prediction *disagreement* fails, remaining significantly below no-adaptation in the harmful regime (−4.95 and −5.26 points; Table 2). A handful of labeled flows per confirmed drift is therefore both necessary and sufficient to make readaptation safe. Because the gate behaves identically for the classical and quantum detectors (Fig. 4), the contribution is a detector-agnostic decision mechanism.

### 5.6 Robustness and controls

The findings are robust to the evaluation metric (the taxonomy and harmful-adaptation result hold under attack-F1; §5.1). Quantum monitors do not reduce nuisance triggers on benign drift (QK-MMD ZZ 1.40 vs Energy 1.03 false triggers), so their value cannot be framed as cleaner benign-drift filtering; and an expensive Random-Forest downstream shows that quantum monitoring runtime can dominate total operational cost (Appendix B). A pre-registered feature-map sensitivity study finds no deeper map that unlocks a stronger quantum advantage (Appendix A). These controls reinforce, rather than qualify, the central conclusion: the detector is not the lever.

---

## Main tables (data ready)

- **Table 1** — Regime taxonomy: per (dataset×regime) no-adaptation BA, best adaptation gain (BA and attack-F1), class (benefit/marginal/harm). Source: `paper2_metrics_ba_f1_summary_001/`.
- **Table 2** — Phase 2 gate: per (regime×detector×gate) BA, gain, commits, labels; paired CI95 vs naive and vs no-adaptation. Source: `paper2_phase2_gated_readaptation_001/`.
- **Table 3** — Oracle-regret and harm-frequency per regime/detector. Source: `paper2_oracle_regret_decision_001/`.
- **Appendix** — QK operating points + paired CIs (CICIDS), UNSW/ToN-IoT full tables, Phase 1 policy grid, feature-map sensitivity, RF downstream, nuisance controls.

## Figures (rendered; `src/analysis/make_paper2_figures.py`)

- **Fig. 1** regime spectrum · **Fig. 2** mechanism law (r=−0.89) · **Fig. 3** oracle-regret vs harm-frequency · **Fig. 4** the gate (both detectors).

## Intro thesis paragraph (for §1)

> Machine-learning NIDS degrade under network concept drift, so adaptive systems periodically retrain, and the field frames the core question as *drift detection*: build a sensitive monitor, retrain when it fires. We argue this framing is wrong on both ends. Sensitive detection does not translate into good decisions — across three benchmarks, quantum-kernel and classical monitors alike yield only regime-dependent operating points that fail to replicate externally. More fundamentally, retraining is not always beneficial: we observe a spectrum from strong benefit to net harm, including a regime where no adaptation dominates every triggered strategy, and we show the sign of the effect is governed by deployed-model degradation — a quantity the detector does not measure. We therefore recast adaptive retraining as a cost-aware adapt/no-adapt decision, show that simple policies do not solve it, and give a label-efficient validate-before-commit gate that does.

## Limitations paragraph (for §7)

> Adaptation on our benchmarks retrains on labeled windows; the validate-before-commit gate accordingly assumes access to a small labeled probe at decision time, and we report its size (≈32–64 flows per confirmed drift) as the realistic cost rather than treating labels as free. The strongest positive (benefit) evidence is concentrated in CICIDS2017; the external benchmarks provide the marginal and harmful ends of the spectrum, which is what the argument requires, but broader benefit-regime replication is future work. Quantum kernels are classically simulated, so the reported 114× monitoring overhead is a simulation figure. The gate is evaluated at fixed per-window severity and does not model online label latency. Finally, the harmful-adaptation result is strongest on ToN-IoT and should be read as one end of a demonstrated spectrum, not as a claim that adaptation is generally harmful.
