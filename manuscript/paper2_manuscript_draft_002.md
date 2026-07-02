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

## 3. Method

### 3.1 Adaptive readaptation as a sequential decision

We consider a deployed binary classifier $h_0$ (benign vs. attack) monitoring a stream of traffic windows $W_1, W_2, \dots$ Each window $W_t$ is a set of flows with (at evaluation time) ground-truth labels; the deployed model degrades as the traffic distribution drifts. A drift monitor $D$ produces a score $s_t = D(W_t)$ measuring divergence of $W_t$ from a reference. The standard adaptive-NIDS loop is: raise an alarm when $s_t$ exceeds a threshold, and upon a confirmed alarm **retrain** the classifier on recent data. We make explicit that this loop conflates two questions:

- **detection:** *has the distribution changed?* — answered by $D$;
- **decision:** *will replacing $h$ with a model retrained on the current window improve accuracy?* — which $D$ does not answer.

Let $h$ be the incumbent model and $h'$ a candidate retrained on the current regime. Adaptation is beneficial at $t$ iff $\mathrm{acc}(h', W_t) > \mathrm{acc}(h, W_t)$. Because $D$ measures distributional change rather than the sign of $\mathrm{acc}(h',\cdot)-\mathrm{acc}(h,\cdot)$, a detector-only policy commits every confirmed change, including changes for which retraining does not help. Our method (§3.4) inserts a decision step that estimates this sign before committing.

### 3.2 Drift monitors

We use two-sample drift monitors comparing a reference window (from the pre-drift regime) to the current window. Classical baselines: **Energy distance**, **RBF-MMD**, per-feature **Kolmogorov–Smirnov** (max reduction) and histogram **Jensen–Shannon** divergence. Quantum monitors: **quantum-kernel MMD** with **ZZ** and **Pauli-XZ** feature maps ($q_{\text{reps}}=1$, angle encoding with standardized `atan` scaling), the MMD being computed in the quantum-kernel-induced RKHS. All monitors expose a scalar score; thresholds are calibrated per detector on held-out calibration windows at a fixed quantile (0.95). The paper's claims are detector-agnostic; the quantum monitors are included as instruments and to test whether a more expressive kernel changes the decision (it does not, §5.3).

### 3.3 Progressive-drift readaptation protocol

Each stream has 100 post-drift windows. Window $t$ is a class-balanced sample in which each class is a mixture of the reference and current pools with mixing weight $\mathrm{sev}(t)$ ("severity"), ramped linearly from 0 to 1 over the first 80 windows and held at 1 thereafter, so drift arrives gradually. On a committed adaptation, the candidate is trained on a fresh balanced labeled sample from the current regime, and the detector reference is reset to the adapted regime. The trigger policy (alarm confirmation and cooldown) is held fixed across all gate conditions so that the decision gate is the only manipulated variable.

### 3.4 The validate-before-commit gate

Our contribution is a decision step interposed between the trigger and the model swap. On each confirmed trigger we retrain a candidate $h'$ as usual, but deploy it only if a cheap estimate says it improves on the incumbent $h$; otherwise we keep $h$ (and keep the detector reference, so a later window can re-propose once adaptation becomes worthwhile). We evaluate three gates:

- **`none` (naive):** always commit — the standard loop.
- **`labeled_probe`$(b,\varepsilon)$:** draw a small balanced labeled probe $P$ of $b$ flows from the current window; commit iff $\mathrm{BA}(h',P) \ge \mathrm{BA}(h,P) + \varepsilon$. The probe is the method's incremental labeling cost; we report $b\in\{32,64\}$, $\varepsilon=0$.
- **`unsup_disagree`$(\tau)$:** commit iff the fraction of flows on which $h$ and $h'$ disagree on the *unlabeled* current window is $\ge \tau$ (a zero-label proxy for "adaptation would change decisions"); we report $\tau=0.15$.

```
Algorithm 1: Gated progressive readaptation (one stream)
  h <- h0 ; D <- fit_reference(pre-drift) ; alarms <- [] ; cooldown <- 0
  for t = 1..T:
      W_t <- sample_window(sev(t))          # balanced, labeled
      record BA(h, W_t)
      s_t <- D.score(W_t) ; alarms.append(s_t > threshold)
      trigger <- policy(alarms) and cooldown == 0
      if trigger:
          h' <- train(current-regime balanced labeled sample)      # candidate
          commit <- gate(h, h', W_t)                               # Sec 3.4
          if commit:
              h <- h' ; D <- fit_reference(current-regime)         # deploy + reset
          alarms <- [] ; cooldown <- C                             # applied either way
      else:
          cooldown <- max(0, cooldown - 1)
  return {BA(h, W_t)}_t
```

The `labeled_probe` gate directly targets the quantity §3.1 identifies (the sign of $\mathrm{acc}(h')-\mathrm{acc}(h)$), estimated from $b$ labels; the `unsup_disagree` gate tests whether that estimate can be obtained without labels.

### 3.5 Metrics

Per window we record balanced accuracy (BA) and attack-class F1; per stream we average over the 100 windows, and per condition over seeds. We report **gain vs. no-adaptation** (the frozen $h_0$ baseline), **committed adaptations** and **labels used**. To quantify the headroom of the decision we define, per stream and detector, a **decision oracle** that abstains when adaptation hurts, $\mathrm{BA}_{\text{oracle}}=\mathbb{E}_{\text{seed}}\max(\mathrm{BA}_{\text{no-adapt}},\mathrm{BA}_{\text{detector}})$, and the **regret** of naive triggering $\mathrm{BA}_{\text{oracle}}-\mathrm{BA}_{\text{naive}}$, together with the **harm frequency** (fraction of streams on which adapting scored below no-adaptation). All comparisons use paired bootstrap 95% confidence intervals over seeds.

## 4. Experimental protocol

**Datasets and regimes.** CICIDS2017 (Tuesday reference → Wednesday, Friday-DDoS, Friday-PortScan, Thursday-WebAttacks), UNSW-NB15 (DoS, Reconnaissance) and ToN-IoT (Scanning), spanning benefit, marginal/mixed and harmful readaptation. Features are numeric, standardized and PCA-reduced to 8 dimensions; windows contain 128 flows.

**Runs.** The regime taxonomy and detector operating points use 30 seeds (CICIDS) / 10 seeds (external medium). The Phase-2 gate evaluation uses **30 seeds** across three representative regimes (PortScan/benefit, UNSW-Reconnaissance/mixed, ToN-IoT-Scanning/harm) and two detectors (KS-max, QK-ZZ), with the trigger fixed at legacy confirmation ($k{=}3$ consecutive, cooldown 10). Fresh no-adaptation and naive baselines are generated within every run for paired comparison.

**Pre-registration.** The gate family (`none`, `labeled_probe` at $b\in\{32,64\}$, `unsup_disagree` at $\tau{=}0.15$), the three regimes, the two detectors and the success criteria (benefit preservation, harm avoidance, mixed non-degradation, label efficiency, detector-invariance) were registered before the confirmatory 30-seed run; no gates, thresholds, datasets or regimes were added post hoc. A prior pre-registered policy grid (k-of-n confirmation and cooldown, no decision gate) is reported as a negative baseline (Appendix E).

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

## 6. Discussion

**Detection is not decision.** The empirical core of this paper is that optimizing a drift *detector* optimizes the wrong object. A detector reports that the distribution moved; an adaptive NIDS needs to know whether retraining will help, and these come apart precisely when the deployed model is still good. Our mechanism analysis makes this concrete: adaptation benefit tracks deployed-model degradation at r = −0.89 (§5.2), so the same distributional shift is worth +19 balanced-accuracy points in one regime and −4 in another. No detector, however sensitive, can distinguish these cases from the window statistics alone — which is why classical and quantum-kernel monitors, and simple confirmation/cooldown policies built on them, all fail to prevent harm (§5.3–5.4).

**Why retraining can hurt.** In our protocol the candidate is retrained on a balanced, correctly-labeled sample of the current regime — near-ideal conditions. It still degrades accuracy when the incumbent is strong, because retraining on a narrow current window replaces a broadly-generalized model with one fit to a shifting slice of traffic; the loss of generalization outweighs the gain from recency. This also bounds the generality of the harmful-adaptation finding in the *conservative* direction: real deployments retrain on noisier, label-scarce data, so harm can only be equal or worse, never an artifact of poor labels in our setup.

**Why the gate works, and why a few labels are unavoidable.** The validate-before-commit gate succeeds because it estimates the one quantity the mechanism identifies — the sign of $\mathrm{acc}(h')-\mathrm{acc}(h)$ — directly, from a small labeled probe, and acts on it. It does not merely suppress adaptation: in the harmful regime it *beats* no-adaptation by committing the minority of genuinely beneficial updates while rejecting the harmful majority (§5.5). The failure of the zero-label `unsup_disagree` variant is informative rather than disappointing: model *disagreement* on unlabeled data measures how much retraining would change decisions, not whether those changes are correct, so it cannot recover the sign. A handful of labeled flows per confirmed drift — on the order of a hundred over a stream — is both necessary and sufficient. In operational NIDS, where analysts already label a small fraction of flagged traffic, this budget is realistic.

**Practitioner guidance.** The results invert the usual deployment recipe. Rather than first choosing the most sensitive (or most expensive, e.g. quantum) detector and then wiring it to automatic retraining, a practitioner should (i) determine, on held-out labeled windows, whether their setting is in a benefit or harm regime — equivalently, whether the deployed model has headroom to lose — and (ii) gate every adaptation on a small labeled validation probe. Under this recipe the detector becomes a coarse scheduler whose exact identity is secondary; a 114× quantum monitoring overhead buys nothing once the decision, not the detection, is the bottleneck.

**Relation to quantum-kernel drift monitoring.** This work began as an evaluation of quantum-kernel MMD as a superior drift trigger. That hypothesis is not supported: QK-MMD defines regime-dependent operating points on one dataset that do not replicate externally, and it does not change the adapt/no-adapt outcome. We report this honestly and repurpose the quantum monitors as one instrument among several, whose invariance under the gate is part of the evidence that the decision layer, not the similarity measure, is what matters.

## 7. Limitations

*(See the Limitations paragraph below; promote to a numbered section at submission.)*

## 8. Conclusion

Adaptive network intrusion detection is usually framed as a detection problem: monitor for drift, retrain when it fires. We showed that this framing is incomplete and sometimes harmful — across three benchmarks the value of readaptation ranges from strongly beneficial to net-negative, governed by deployed-model degradation rather than by distributional change, and invisible to the detector. Consequently, neither more expressive detectors (including quantum kernels) nor simple confirmation/cooldown policies prevent harmful adaptation. Recast as a cost-aware decision, the problem admits a simple, deployable solution: a validate-before-commit gate that retrains a candidate but deploys it only if a small labeled probe confirms an improvement. The gate preserves the benefit of adaptation where it helps, avoids harm where it does not, and significantly outperforms both naive triggering and never adapting — for a classical and a quantum detector alike — with roughly one hundred labeled flows. *When not to retrain* is as important as detecting drift, and a few labels, spent on the decision rather than the detector, are enough to know the difference.

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
