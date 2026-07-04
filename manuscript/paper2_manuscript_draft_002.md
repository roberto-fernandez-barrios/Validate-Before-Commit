# Paper 2 — Manuscript Draft 002 (solution-framed, post-Phase 2)

> Supersedes `paper2_manuscript_skeleton_001.md` (which was QK-centric, pre-Phase 2). This draft reframes the paper as a *solution* paper around the adapt/no-adapt decision. All numbers are verified against committed artifacts (`results/tables/paper2_*`, 30-seed Phase 2). Prose is submission-oriented; edit voice to taste.

---

## Title

**Knowing When Not to Retrain: Label-Efficient Safe Readaptation for Adaptive Network Intrusion Detection under Concept Drift**

## Abstract

Adaptive network intrusion detection systems (NIDS) retrain their classifiers to cope with concept drift, and a large literature optimizes drift *detectors* to decide when to retrain. We show this framing is incomplete and can be counterproductive. Across three public benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) and seven attack regimes, the value of drift-triggered readaptation ranges from strongly beneficial to, for a fragile downstream classifier, actively harmful: in a ToN-IoT scanning regime with an SVC-RBF downstream, naive triggering degrades balanced accuracy below a no-adaptation baseline for every detector we test, classical or quantum-kernel. We find that the sign and size of this effect are governed almost entirely by how much the deployed model has already degraded — the benefit of adaptation correlates with the no-adaptation accuracy at r = −0.89 — a quantity that drift detectors, which measure distributional change, do not observe; this law holds across four downstream classifiers (SVC, random forest, logistic regression, MLP), even though whether the effect crosses into net harm is downstream-dependent. Consistent with this, the choice of detector (including quantum-kernel MMD) does not change the qualitative outcome, and simple confirmation/cooldown policies fail to prevent harm. We therefore reframe readaptation as a cost-aware decision and introduce a label-efficient *validate-before-commit* gate: on each trigger, a candidate model is retrained but deployed only if it beats the incumbent on a small labeled probe. Across benefit, mixed, and harmful regimes and two detectors, the gate (30 seeds, pre-registered) converts net-harmful adaptation into net benefit — in ToN-IoT, from −1.4/−3.7 balanced-accuracy points (naive) to +0.9/+1.1, significantly above both naive triggering (+2.3/+4.7 pts, CI95) and no-adaptation (+0.9/+1.1 pts, CI95) — while preserving the gains where adaptation helps, using on the order of one hundred labeled flows — and a budget sweep shows as few as a few dozen suffice. A zero-label variant fails, delimiting the method: a few labels are necessary. Crucially, the gate is safe across all four downstream classifiers and all regimes — it never underperforms no-adaptation and never underperforms naive triggering — so the safety guarantee generalizes even where the harm itself is downstream-specific, and it tolerates label latency (probes up to 20 windows stale). Our results indicate that *when not to adapt* is as important as detecting drift, that the decision — not the detector — is the operative lever, and that a small, deployable label budget resolves the harmful-adaptation problem.

## Contributions

1. **A regime taxonomy of readaptation value** across three benchmarks: adaptation is strongly beneficial (CICIDS2017), marginal (UNSW-NB15), or net-harmful (ToN-IoT), quantified with 30-seed CI95.
2. **Evidence that naive drift-triggered readaptation can be net-harmful (for a fragile downstream model)**, with a mechanistic law that *does* generalize: the benefit of adaptation is predicted by deployed-model degradation (r = −0.89) across four downstream classifiers, a quantity drift detectors do not measure — hence detection ≠ decision.
3. **Detector-invariance**: classical (Energy, MMD-RBF, KS, JSD) and quantum-kernel (ZZ, PauliXZ) detectors yield the same qualitative outcome; QK-MMD is an instrument, not the lever. An oracle-regret analysis quantifies the headroom left by naive triggering.
4. **A pre-registered negative on simple policies**: k-of-n confirmation and cooldown do not prevent harmful adaptation.
5. **A label-efficient validate-before-commit gate** that resolves the problem: it preserves benefit, avoids harm, and beats both naive triggering and no-adaptation, with a few dozen labeled flows — and is **universally safe across two detectors and four downstream classifiers** (never worse than no-adaptation or naive), whereas a zero-label variant fails.

---

## 1. Introduction

Machine-learning network intrusion detection systems (NIDS) are trained on historical traffic, yet the traffic they monitor evolves: new services, shifting user behaviour, reconfigured infrastructure and novel attacks all move the input distribution away from the training distribution, a phenomenon known as concept drift \cite{shyaa2024evolving,wahab2022intrusion,roshan2018adaptive}. As the distribution shifts, a frozen classifier loses accuracy, so operational NIDS periodically **retrain** their downstream classifier on recent traffic \cite{wahab2022intrusion,camarda2025managing,constantinides2019novel}. Retraining is not free — it consumes labeled data and compute and briefly destabilizes a deployed model — so the central operational question is *when* to retrain.

The dominant answer frames this as a **drift-detection** problem: run a statistical monitor that compares recent traffic to a reference window, and trigger retraining when the monitor signals a change \cite{gama2004learning,rabanser2019failing,lukats2024benchmark}. A large literature accordingly competes to build more sensitive monitors, from univariate change detectors to multivariate two-sample tests such as maximum mean discrepancy (MMD) and energy distance \cite{gretton2012kernel,szekely2013energy}, and more recently to quantum-kernel similarity measures whose feature-map geometry may respond differently to distributional change \cite{havlicek2019supervised,schuld2019quantum,kaissar2026enhancing}. The implicit assumption is that a better change detector yields a better retraining policy.

This paper challenges that assumption on empirical grounds. We evaluate quantum-kernel and classical drift monitors as retraining triggers under progressive drift across three public benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) and find, first, that no monitor delivers a robust advantage: quantum-kernel MMD defines regime-dependent operating points on one dataset that do not replicate externally. More importantly, we find that the premise beneath the whole detection-centric framing is false: **drift-triggered retraining is not always beneficial.** Across seven attack regimes the value of retraining ranges from strongly positive to negative — in a ToN-IoT scanning regime, *no adaptation* outperforms every triggered strategy we test, classical or quantum. Whether retraining helps is governed not by how much the distribution moved but by how much the deployed model has already degraded: the two correlate at r = −0.89. A drift monitor, which measures distributional change, cannot observe this quantity, which is precisely why sensitive detectors — and simple confirmation/cooldown policies built on them — fail to prevent harmful retraining.

We therefore argue that adaptive retraining should be recast from a *detection* problem to a cost-aware *decision*: not "did the distribution change?" but "will retraining improve the classifier?". This reframing yields a simple, deployable solution. We propose a **validate-before-commit** gate that, on each triggered drift, retrains a candidate model but deploys it only if it beats the incumbent on a small labeled probe drawn from current traffic. Across benefit, mixed and harmful regimes and both a classical and a quantum detector, the gate (pre-registered, 30 seeds) preserves the gains of retraining where it helps, avoids harm where it does not, and significantly outperforms both naive triggering and never adapting — using on the order of one hundred labeled flows per stream. A zero-label variant fails, showing that a few labels, spent on the decision rather than the detector, are both necessary and sufficient.

Our contributions are: (1) a regime taxonomy showing readaptation value spans benefit to net-harm across three benchmarks; (2) a mechanistic account (r = −0.89) explaining harmful adaptation as loss of a still-good model, invisible to drift detectors; (3) detector-invariance evidence and an oracle-regret analysis showing the decision, not the detector — classical or quantum — is the lever; (4) a pre-registered negative result on simple confirmation/cooldown policies; and (5) a label-efficient validate-before-commit gate that resolves the problem. The remainder of the paper reviews related work (§2), formalizes the decision and the gate (§3), details the protocol (§4), reports results (§5), and discusses implications and limits (§6–§8).

## 2. Related work

**Concept drift and adaptive intrusion detection.** Concept drift degrades ML-based NIDS, and a body of work adapts models online or on a schedule to compensate \cite{gama2014survey,lu2019learning,shyaa2024evolving}. Most such systems assume adaptation is beneficial and focus on *how* to adapt (incremental learning, windowing, ensembles) \cite{constantinides2019novel,roshan2018adaptive,shyaa2023enhanced}. We instead study *whether and when* adaptation helps, and show it can be net-harmful — connecting to, but distinct from, work on negative transfer and catastrophic forgetting in continual learning \cite{mccloskey1989catastrophic,kirkpatrick2017overcoming,zhang2023survey}, which we observe operationally in a security setting.

**Drift detection and two-sample monitors.** Drift is commonly detected with change detectors \cite{bifet2007learning,gama2004learning,baena2006early,raab2020reactive} or multivariate two-sample tests — MMD, energy distance, Kolmogorov–Smirnov and Jensen–Shannon divergence — used as retraining or alarm triggers \cite{gretton2012kernel,rizzo2016energy,lin1991divergence,darling1957ks}. Our classical baselines are drawn from this family. We use these monitors but argue that improving them does not improve the retraining decision, because they are blind to model degradation.

**Quantum kernels for drift monitoring.** Quantum-kernel methods embed data via parameterized quantum feature maps and have been proposed for classification and similarity estimation \cite{havlicek2019supervised,schuld2019quantum,huang2021power}, including exploratory use in cybersecurity \cite{gouveia2020towards,nicesio2023quantum,bellante2025evaluating}. Prior work (our Paper 1 \cite{fernandez_paper1}) reported settings where quantum kernels generalize differently, motivating their evaluation as drift monitors here. We find they act as one instrument among several and do not change the adapt/no-adapt outcome.

**When to retrain: cost-aware and validation-gated updates.** Beyond detection, some work weighs the cost of adaptation or validates a candidate before deployment, e.g. in MLOps model-update pipelines and shadow/champion–challenger evaluation \cite{nath2007champion,sculley2015hidden,kreuzberger2023mlops,guissouma2023continuous}. Our gate instantiates this idea for streaming NIDS and, crucially, quantifies its label cost and demonstrates its necessity — that detection and simple policies are insufficient without it. Its reliance on a small labeled probe connects to active and label-efficient learning for data streams \cite{cacciarelli2024active,krawczyk2019adaptive,liu2021comprehensive}, where labels are scarce and must be spent where they most affect the decision.

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

**Datasets and regimes.** CICIDS2017 \cite{sharafaldin2018toward} (Tuesday reference → Wednesday, Friday-DDoS, Friday-PortScan, Thursday-WebAttacks), UNSW-NB15 \cite{moustafa2015unsw} (DoS, Reconnaissance) and ToN-IoT \cite{alsaedi2020toniot} (Scanning), spanning benefit, marginal/mixed and harmful readaptation. Features are numeric, standardized and PCA-reduced to 8 dimensions; windows contain 128 flows.

**Runs.** The regime taxonomy and detector operating points use 30 seeds (CICIDS) / 10 seeds (external medium). The Phase-2 gate evaluation uses **30 seeds** across three representative regimes (PortScan/benefit, UNSW-Reconnaissance/mixed, ToN-IoT-Scanning/harm) and two detectors (KS-max, QK-ZZ), with the trigger fixed at legacy confirmation ($k{=}3$ consecutive, cooldown 10). Fresh no-adaptation and naive baselines are generated within every run for paired comparison.

**Pre-registration.** The gate family (`none`, `labeled_probe` at $b\in\{32,64\}$, `unsup_disagree` at $\tau{=}0.15$), the three regimes, the two detectors and the success criteria (benefit preservation, harm avoidance, mixed non-degradation, label efficiency, detector-invariance) were registered before the confirmatory 30-seed run; no gates, thresholds, datasets or regimes were added post hoc. A prior pre-registered policy grid (k-of-n confirmation and cooldown, no decision gate) is reported as a negative baseline (Appendix E).

## 5. Results

We present results in logical, not chronological, order. Section 5.1 establishes that readaptation is beneficial on CICIDS2017 but *not* on the external benchmarks; 5.2 explains the pattern with a mechanistic law; 5.3 shows the detector — classical or quantum — is not the lever; 5.4 shows simple policies do not fix it; 5.5 presents the label-efficient gate that does; 5.6 reports robustness and controls.

### 5.1 Readaptation is regime-dependent and sometimes harmful

Under progressive drift, an unadapted classifier degrades and triggered readaptation can recover much of the loss — on CICIDS2017. Averaged over 30 seeds and 100 post-drift windows, the best detector-triggered strategy recovers +19.5 balanced-accuracy (BA) points over no-adaptation in the Friday-DDoS regime, +11.9 in Wednesday, +7.6 in WebAttacks and +6.2 in PortScan (Table 1, Fig. 1). This is the familiar picture that motivates adaptive NIDS.

The picture does not survive to independent data. On UNSW-NB15 the best recovery is marginal (+1.4 points for DoS, +0.3 for Reconnaissance), and on ToN-IoT Scanning it becomes *negative* for the SVC-RBF downstream used here: no detector-triggered strategy matches a no-adaptation baseline (best adaptive −0.6 points; worst −4.5), so the correct decision there is **not to adapt** (Fig. 1). This net-harm is downstream-dependent — it does not appear for more robust classifiers — while the degradation law that governs it is not (§5.7). The effect is not a balanced-accuracy artifact: under attack-F1 the CICIDS benefits grow (e.g. +32.3 F1 points for DDoS) and ToN-IoT remains harmful for every detector (Energy −0.8, KS-max −9.5 F1 points). We stress the claim is not "adaptation usually hurts" — it is that the *sign* of the payoff is regime- and dataset-dependent, spanning +19.5 to −4.5 BA points, which is precisely what an adaptive system must anticipate.

### 5.2 The value of readaptation is governed by model degradation, not distribution change

Why does adaptation help enormously in one regime and hurt in another? The answer is not the amount of drift but the state of the deployed model. Across all seven regimes, the benefit of adaptation is almost perfectly predicted by the no-adaptation accuracy: **r = −0.89** between deployed-model BA and adaptation gain across the seven SVC-RBF regimes (Fig. 2), and **r = −0.82 (bootstrap CI95 [−0.95, −0.59], 16 model×regime points)** when pooled across all four downstream classifiers (Fig. 2b). Where the deployed model has already collapsed (DDoS: 69.8% without adaptation), retraining on a fresh window is a large gain; where it remains strong (ToN-IoT: 92.0%), replacing a well-generalized model with a narrowly-fit current-window model is a net loss.

This exposes the core problem. Drift detectors answer *"has the distribution changed?"*, but an adaptive NIDS needs *"will retraining improve the classifier?"* — and these are different questions. We quantify the gap with a decision-level oracle that, per stream, abstains when adaptation would hurt (holding the detector fixed). The resulting *regret* of naive triggering is essentially zero where adaptation always helps (Wednesday, DDoS: 0.00 points, adaptation hurt on 0% of streams) and largest where it hurts (ToN-IoT: 3.50 points for QK-ZZ, CI95 [0.96, 7.45], adaptation hurt on 80% of streams), scaling monotonically with harm frequency (Fig. 3). The headroom left by naive triggering is real and concentrated exactly where the deployed model is already good.

### 5.3 The detector is not the lever

Because drift detectors are blind to model degradation, improving the detector cannot solve the problem — and it does not. Quantum-kernel MMD monitors do define distinct *operating points* on CICIDS2017 (QK-MMD ZZ triggers 1.8–2.1 fewer readaptations than Energy distance at equivalent accuracy in Wednesday/DDoS, and inverts in PortScan), but at a ~114× monitoring-runtime cost, and these profiles do not replicate externally. Critically, the regime taxonomy and the harmful-adaptation outcome are identical for classical and quantum detectors (Fig. 3, Table 1): on ToN-IoT, naive triggering is net-harmful whether the trigger is KS-max (−1.4 points) or QK-ZZ (−3.7 points). The lever is the adapt/no-adapt decision, not the similarity measure that fires the trigger.

### 5.4 Simple confirmation and cooldown policies do not prevent harm

If the decision is the lever, the natural fix is a smarter trigger policy. We pre-registered a grid of alarm-confirmation (k-of-n) and cooldown policies and evaluated them against fixed success criteria (preserve benefit in PortScan; avoid harm in ToN-IoT; do not degrade UNSW). None passed: in the harmful regime the tested policies remained far below no-adaptation and did not reduce adaptations relative to a conservative legacy baseline (Appendix E). Confirmation and cooldown act on the *persistence* of distributional change, which is exactly the signal that is uninformative about whether adaptation helps. This negative result motivates a policy that acts on the right quantity.

### 5.5 A label-efficient validate-before-commit gate resolves the problem

We introduce a decision gate that acts directly on estimated model improvement. On each drift trigger, a candidate model is retrained as usual, but it is **deployed only if it beats the incumbent on a small labeled probe** drawn from the current window (budget 32 or 64 flows); otherwise the incumbent is kept. We evaluate the gate against the same pre-registered criteria (30 seeds, 100 windows, legacy trigger fixed so the gate is the only variable) across the benefit (PortScan), mixed (UNSW Reconnaissance) and harmful (ToN-IoT) regimes, for both a classical (KS-max) and a quantum (QK-ZZ) detector (Table 2, Fig. 4).

The gate passes every criterion for both detectors. In the harmful regime it turns net-harmful naive triggering into net benefit: ToN-IoT gain moves from −1.36 (KS-max) and −3.69 (QK-ZZ) points to +0.93 and +1.06, **significantly above naive triggering** (+2.30 points, CI95 [1.15, 3.63] for KS-max; +4.74, [2.47, 7.69] for QK-ZZ) and, notably, **significantly above no-adaptation itself** (+0.93, [0.53, 1.36]; +1.06, [0.77, 1.40]) — the gate does not merely stop adapting, it commits the minority of beneficial adaptations while rejecting the harmful majority. In the benefit regime it preserves the full gain (PortScan +8.3/+8.4 points, statistically indistinguishable from naive), and it does not degrade the mixed regime. The label cost is small: roughly 100–160 labeled flows over a 100-window stream at budget 32.

The gate's power comes from labels, not from the confirmation heuristic: a zero-label variant that commits on deployed-vs-candidate prediction *disagreement* fails, remaining significantly below no-adaptation in the harmful regime (−4.95 and −5.26 points; Table 2). A handful of labeled flows per confirmed drift is therefore both necessary and sufficient to make readaptation safe. Because the gate behaves identically for the classical and quantum detectors (Fig. 4), the contribution is a detector-agnostic decision mechanism.

### 5.6 Gate robustness (post-registration)

Five extensions beyond the pre-registered design (explicitly labeled as robustness, not part of the confirmatory claim) probe the gate's limits. *Label efficiency:* sweeping the probe budget from 8 to 128 flows (KS-max, 30 seeds; Fig. 5) shows the gate is remarkably label-cheap — in the harmful regime even the smallest budget avoids harm, ~8 labeled flows per confirmed drift (≈23 per stream) already lifting ToN-IoT gain from −1.36 (naive) to +0.38, plateauing near +1.1 by budget 32–64; benefit-regime gain is flat at every budget. A few dozen labels, not hundreds, suffice. *Benefit breadth:* beyond PortScan the gate preserves — and slightly improves — the benefit in the two strongest benefit regimes, Wednesday (naive +15.39 → +16.32) and DDoS (naive +24.81 → +25.27), never sacrificing benefit where adaptation helps, across three benefit regimes.

*Label latency:* the probe need not be current. Drawing it from traffic labeled up to 20 windows in the past (Fig. 7) leaves the gate safe and effective at every lag — in the harmful regime the gate holds at +0.9 to +1.1 (vs naive −1.36) for lags of 5, 10 and 20 windows, and the benefit regimes are essentially unchanged — so the method tolerates realistic labeling delay rather than requiring instantaneous labels. *Harm breadth:* the net-harm of naive triggering (with the fragile SVC-RBF downstream) is not confined to one ToN-IoT regime — it also appears in ToN-IoT DDoS (naive **−16.81**) and Injection (−1.21), and the gate converts all three to net-positive (+1.26, +0.80, +0.93). *Cost knob:* raising the commit margin ε from 0 to 0.01–0.02 cuts committed adaptations by ~30% (e.g. PortScan 3.1→2.2 commits) at equal downstream gain, giving a simple operating characteristic that trades update frequency for benefit.

### 5.7 Generalization across downstream classifiers

To test whether the phenomenon and the solution depend on the downstream model, we repeat the three regimes with the KS-max trigger for four downstream classifiers — SVC-RBF, random forest, logistic regression and MLP (20 seeds; Table 6, Fig. 6). Three findings stand out, and we report them plainly because they refine the headline.

First, **the mechanism law generalizes.** Across all four classifiers the benefit of adaptation tracks deployed-model degradation: where the frozen model is weak the gain is large (e.g. random forest and MLP on PortScan start at 69–70% no-adaptation BA and gain +27 points; logistic regression on ToN-IoT starts at 84% and gains +6.7), and where the frozen model is already strong the gain is small (random forest on ToN-IoT starts at 97% and gains only +1.9). Pooled across all four classifiers the degradation–benefit correlation is r = −0.82 (bootstrap CI95 [−0.95, −0.59], 16 points; Fig. 2b): the relationship is a property of the adaptation problem, not of SVC.

Second, **whether the effect crosses into net harm is downstream-specific.** The negative-gain result — naive triggering below no-adaptation — occurs only for SVC-RBF on ToN-IoT (−1.36 points); random forest (+1.88), logistic regression (+6.70) and MLP (+0.24) all remain non-negative there (Fig. 6). SVC-RBF is fragile enough on this regime that retraining on a narrow current window loses more than it gains; more robust downstream models do not. We therefore do not claim that naive readaptation is universally harmful — only that it can be, for fragile models, exactly where the mechanism law predicts the smallest headroom.

Third, and most important for deployment, **the gate is universally safe.** Across all four downstream classifiers and all three regimes (twelve settings), the labeled-probe gate never underperforms no-adaptation and never underperforms naive triggering (Table 6). The safety guarantee holds even in the settings where naive triggering is already fine (the gate simply commits), and rescues the one setting where it is harmful. The solution generalizes across downstream models even though the harm does not.

### 5.8 Controls

The findings are robust to the evaluation metric (the taxonomy and harmful-adaptation result hold under attack-F1; §5.1). Quantum monitors do not reduce nuisance triggers on benign drift (QK-MMD ZZ 1.40 vs Energy 1.03 false triggers), so their value cannot be framed as cleaner benign-drift filtering; and an expensive Random-Forest downstream shows that quantum monitoring runtime can dominate total operational cost (Appendix B). A pre-registered feature-map sensitivity study finds no deeper map that unlocks a stronger quantum advantage (Appendix A). These controls reinforce, rather than qualify, the central conclusion: the detector is not the lever.

---

## 6. Discussion

**Detection is not decision.** The empirical core of this paper is that optimizing a drift *detector* optimizes the wrong object. A detector reports that the distribution moved; an adaptive NIDS needs to know whether retraining will help, and these come apart precisely when the deployed model is still good. Our mechanism analysis makes this concrete: adaptation benefit tracks deployed-model degradation at r = −0.89 (§5.2), so the same distributional shift is worth +19 balanced-accuracy points in one regime and −4 in another. No detector, however sensitive, can distinguish these cases from the window statistics alone — which is why classical and quantum-kernel monitors, and simple confirmation/cooldown policies built on them, all fail to prevent harm (§5.3–5.4).

**Why retraining can hurt, and why it is model-dependent.** In our protocol the candidate is retrained on a balanced, correctly-labeled sample of the current regime — near-ideal conditions. It still degrades accuracy when the incumbent is strong, because retraining on a narrow current window replaces a broadly-generalized model with one fit to a shifting slice of traffic; the loss of generalization outweighs the gain from recency. Whether this loss actually pushes the outcome below no-adaptation depends on the downstream model's robustness: the SVC-RBF classifier is fragile enough on ToN-IoT to go net-negative, whereas random forest, logistic regression and MLP retain enough generalization to stay non-negative (§5.7). This is not a contradiction of the mechanism law — all four obey the degradation–benefit relationship — but a refinement: net harm is the fragile-model tail of a general phenomenon. It is precisely why a decision layer that estimates *actual* candidate-vs-incumbent improvement, rather than distributional change, is the right abstraction: the gate is model-agnostic by construction and, empirically, safe across all four downstream models.

**Why the gate works, and why a few labels are unavoidable.** The validate-before-commit gate succeeds because it estimates the one quantity the mechanism identifies — the sign of $\mathrm{acc}(h')-\mathrm{acc}(h)$ — directly, from a small labeled probe, and acts on it. It does not merely suppress adaptation: in the harmful regime it *beats* no-adaptation by committing the minority of genuinely beneficial updates while rejecting the harmful majority (§5.5). The failure of the zero-label `unsup_disagree` variant is informative rather than disappointing: model *disagreement* on unlabeled data measures how much retraining would change decisions, not whether those changes are correct, so it cannot recover the sign. A handful of labeled flows per confirmed drift — on the order of a hundred over a stream — is both necessary and sufficient. In operational NIDS, where analysts already label a small fraction of flagged traffic, this budget is realistic.

**Practitioner guidance.** The results invert the usual deployment recipe. Rather than first choosing the most sensitive (or most expensive, e.g. quantum) detector and then wiring it to automatic retraining, a practitioner should (i) determine, on held-out labeled windows, whether their setting is in a benefit or harm regime — equivalently, whether the deployed model has headroom to lose — and (ii) gate every adaptation on a small labeled validation probe. Under this recipe the detector becomes a coarse scheduler whose exact identity is secondary; a 114× quantum monitoring overhead buys nothing once the decision, not the detection, is the bottleneck.

**Relation to quantum-kernel drift monitoring.** This work began as an evaluation of quantum-kernel MMD as a superior drift trigger. That hypothesis is not supported: QK-MMD defines regime-dependent operating points on one dataset that do not replicate externally, and it does not change the adapt/no-adapt outcome. We report this honestly and repurpose the quantum monitors as one instrument among several, whose invariance under the gate is part of the evidence that the decision layer, not the similarity measure, is what matters.

## 7. Limitations

*(See the Limitations paragraph below; promote to a numbered section at submission.)*

## 8. Conclusion

Adaptive network intrusion detection is usually framed as a detection problem: monitor for drift, retrain when it fires. We showed that this framing is incomplete and sometimes harmful — across three benchmarks the value of readaptation ranges from strongly beneficial to net-negative, governed by deployed-model degradation rather than by distributional change, and invisible to the detector. Consequently, neither more expressive detectors (including quantum kernels) nor simple confirmation/cooldown policies prevent harmful adaptation. Recast as a cost-aware decision, the problem admits a simple, deployable solution: a validate-before-commit gate that retrains a candidate but deploys it only if a small labeled probe confirms an improvement. The gate preserves the benefit of adaptation where it helps, avoids harm where it does not, and significantly outperforms both naive triggering and never adapting — for a classical and a quantum detector alike — with roughly one hundred labeled flows. *When not to retrain* is as important as detecting drift, and a few labels, spent on the decision rather than the detector, are enough to know the difference.

---

## Main tables (rendered — Markdown + LaTeX in `results/tables/paper2_paper_tables_001/`)

- **Table 1** `table1_regime_taxonomy` — Regime taxonomy: per (dataset×regime) no-adaptation BA, best adaptation gain (BA and attack-F1), class. (→ §5.1, Fig. 1)
- **Table 2** `table2_phase2_gate_summary` — Phase 2 gate: per (regime×detector×gate) BA, gain, commits, labels (30 seeds). (→ §5.5, Fig. 4)
- **Table 3** `table3_phase2_paired_ci` — Phase 2 paired bootstrap CI95, gate vs naive and vs no-adaptation. In ToN-IoT the labeled-probe gate is significantly above both. (→ §5.5)
- **Table 4** `table4_oracle_regret` — Decision oracle-regret and harm frequency per regime/detector; regret ~0 in pure-benefit regimes, 3.50 pts (ToN-IoT QK-ZZ). (→ §5.2, Fig. 3)
- **Table 6** `table6_downstream_generalization` — Gate across four downstream classifiers × 3 regimes: no-adapt/naive/gate gain + harm-reproduced / gate-avoids-harm flags. (→ §5.7, Fig. 6)
- Regenerate with `python -m src.analysis.make_paper2_paper_tables`.
- **Appendix tables** — QK operating points + paired CIs (CICIDS), UNSW/ToN-IoT full tables, Phase 1 policy grid, feature-map sensitivity, RF downstream, nuisance controls.

## Figures (rendered; `make_paper2_figures.py`, `make_paper2_budget_curve.py`)

- **Fig. 1** regime spectrum · **Fig. 2** mechanism law (r=−0.89, SVC) · **Fig. 2b** pooled mechanism law across 4 downstream models (r=−0.82, CI95) · **Fig. 3** oracle-regret vs harm-frequency · **Fig. 4** the gate (both detectors) · **Fig. 5** label-efficiency frontier (probe budget 8–128) · **Fig. 6** generalization across four downstream classifiers (harm is SVC-specific; gate safe everywhere) · **Fig. 7** gate robustness to label latency (probe up to 20 windows stale).

## Intro thesis paragraph (for §1)

> Machine-learning NIDS degrade under network concept drift, so adaptive systems periodically retrain, and the field frames the core question as *drift detection*: build a sensitive monitor, retrain when it fires. We argue this framing is wrong on both ends. Sensitive detection does not translate into good decisions — across three benchmarks, quantum-kernel and classical monitors alike yield only regime-dependent operating points that fail to replicate externally. More fundamentally, retraining is not always beneficial: we observe a spectrum from strong benefit to net harm, including a regime where no adaptation dominates every triggered strategy, and we show the sign of the effect is governed by deployed-model degradation — a quantity the detector does not measure. We therefore recast adaptive retraining as a cost-aware adapt/no-adapt decision, show that simple policies do not solve it, and give a label-efficient validate-before-commit gate that does.

## Limitations paragraph (for §7)

> Adaptation on our benchmarks retrains on labeled windows; the validate-before-commit gate accordingly assumes access to a small labeled probe at decision time, and we report its size (≈32–64 flows per confirmed drift) as the realistic cost rather than treating labels as free. The strongest positive (benefit) evidence is concentrated in CICIDS2017; the external benchmarks provide the marginal and harmful ends of the spectrum, which is what the argument requires, but broader benefit-regime replication is future work. Quantum kernels are classically simulated, so the reported 114× monitoring overhead is a simulation figure. The gate is evaluated at fixed per-window severity; we do model label latency (the probe may be up to 20 windows stale; §5.6) but not asynchronous or partial labeling. The net-harm result is specific to a fragile downstream classifier (SVC-RBF) on ToN-IoT and does not appear for more robust classifiers (§5.7); we therefore frame it as the fragile-model tail of a general degradation–benefit law rather than a universal harm claim, and note that the gate's safety — unlike the harm — generalizes across the four downstream models tested. Finally, all evaluation uses the same four downstream classifiers and three regimes for the gate; broader deployment settings remain future work.
