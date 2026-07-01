# Paper 2 — Safe-Readaptation Rescue Review

**Prepared by:** Claude (Opus 4.8)
**Date:** 2026-06-29
**Branch:** paper2-expensive-downstream
**Trigger:** Final external results in (UNSW-NB15 mixed, ToN-IoT Q1-gate failed). Request for a brutally honest, anti-anchored strategic review before committing to (or rejecting) a safe/cost-aware readaptation pivot.
**Role taken:** skeptical Q1 reviewer + worried thesis director + scientific strategist.

This note does **not** anchor on the safe-readaptation pivot. It independently derives the alternatives first, ranks them, and only then judges the pivot.

---

## 0. Brutal verdict (read this first)

Three things are now true and not negotiable:

1. **The quantum-advantage story is dead.** Three datasets, no replication. CICIDS gives narrow regime-dependent operating points; UNSW gives non-significant mixed evidence; ToN-IoT actively contradicts it (no-adaptation beats every triggered strategy). Any paper whose central claim *depends on QK winning* is unsalvageable. Stop trying to make QK the hero.

2. **The current detector-comparison paper is Q2, not Q1 — and framing cannot fix that.** Q1 at TDSC/TIFS/Computers & Security requires external validity. You have single-dataset positives plus two failed external replications plus a 114× overhead with no delivered advantage. That is an honest, well-powered, incremental empirical study. It is a solid Q2. It is not Q1. A reviewer does not reject this paper; a reviewer declines to call it Q1.

3. **You are sitting on a genuinely stronger result than the one you went looking for.** The most important, most generalizable signal in the entire campaign is *not* about QK. It is that **drift-triggered readaptation is frequently harmful**, and that the "detect drift → retrain" pipeline is the wrong abstraction. ToN-IoT is not a failure — it is the cleanest evidence you have for a better paper.

**Bottom line:** There is a credible route with a *shot* at Q1 and a guaranteed Q2-strong floor. It is the safe/cost-aware readaptation pivot — **but only in a specific, detector-agnostic form, and only if a cheap diagnostic says the headroom exists.** It is not a guaranteed Q1. Anyone who promises you Q1 here is selling optimism.

---

## 1. Is Q1 still possible?

**For the detector-comparison paper as currently scoped: no.** Honest probability at a serious Q1 venue, with the best possible framing, ~15–25%. Not worth attempting. This matches both previous strategic reviews.

**For a repositioned decision-policy paper: conditionally, with a realistic ceiling of "Q1-borderline / strong Q2."** Probability of a real Q1 (e.g. Computers & Security, possibly TDSC) ~35–50% *if and only if* the policy experiment produces a clean positive result. Probability of Q2-strong floor regardless: ~75%.

There is no honest path to "Q1-strong, high confidence" from this evidence base. I will not pretend otherwise.

---

## 2. Independent alternative routes (derived before judging the pivot)

I treated the safe-readaptation pivot as just one candidate. Here is the full set I see in the results.

### Route A — Plain Q2 operational characterization (the current default)
QK-MMD regime-dependent operating points on CICIDS2017, UNSW/ToN-IoT honest in appendix. This is the path both prior reviews land on.

### Route B — Repositioned policy paper (detector-agnostic safe/cost-aware readaptation)
Protagonist = the *adapt / don't-adapt decision problem under cost and uncertainty*. QK is demoted to one instrument among classical detectors. Negatives become motivation. This is the pivot — but stripped of any dependence on QK winning.

### Route C — Harmful-adaptation / over-adaptation phenomenon paper
A focused empirical paper: "When does triggered readaptation hurt adaptive IDS?" Centered on the ToN-IoT phenomenon + CICIDS regime-dependence. A narrower sibling of B (phenomenon, not method).

### Route D — Negative-results / benchmarking paper
"Do quantum-kernel drift detectors help adaptive IDS? A multi-dataset null result." Honest, but low prestige; rarely Q1; weak thesis centerpiece.

### Route E — IDS decision-policy framework (generalization of B)
The contribution is a *framework* for jointly choosing detector + trigger policy + cost objective. Essentially B with a stronger methodological frame.

### Route F — Split into two papers
Paper A (Q2 now): QK-MMD characterization. Paper B (Q1 later): safe readaptation policies. Thesis = both.

### Route G — Q2 now, Q1 later (sequential F)
Write the detector paper now; reserve the policy paper as the Q1 target after the bounded experiment.

### Route H — Strengthen the current paper through analysis only
Add oracle-regret + harmful-adaptation framing on *existing* data, no new experiments. Cheapest possible upgrade.

### Route I — Abandon the Q1 attempt
Write Route A and submit.

---

## 3. Ranking of routes (best → worst)

Scored on: novelty, Q1 plausibility, post-hoc risk, additional experiments, thesis value, time, acceptance probability.

| Rank | Route | Novelty | Q1 plausibility | Post-hoc risk | New experiments | Thesis value | Time | Accept prob |
|---|---|---|---|---|---|---|---|---|
| **1** | **B — detector-agnostic safe-readaptation policy paper** | High | Moderate (ceiling Q1-borderline) | Moderate, manageable | Bounded, pre-registered | **High** | Medium | Q1 35–50% / Q2 ~75% |
| **2** | **H — analysis-only strengthening (oracle-regret on existing data)** | Medium | Low–moderate | Low | **None** | Medium | Low | Q2-strong ~80%, Q1 ~25% |
| **3** | **F/G — split / sequential (Q2 now + Q1 policy later)** | High (combined) | Moderate | Low | Bounded (deferred) | **High** | High (two papers) | Q2 high + Q1 later 35–50% |
| 4 | C — harmful-adaptation phenomenon paper | Medium–high | Low–moderate | Low | Small | Medium | Low–medium | Q2 high, Q1 ~25% |
| 5 | A / I — plain Q2 / abandon Q1 | Low | n/a | None | None | Low | Low | Q2 70–80% |
| 6 | E — full decision framework | High | Moderate but over-scoped | Medium | Large (risk of sprawl) | High | High | Uncertain |
| 7 | D — negative-results paper | Low–medium | Very low | Low | None | Low | Low | Niche venues only |

**Key insight from the ranking:** Routes B, C, E, F, G, H are *all variants of the same underlying realization* — that the real contribution lives in the decision/policy layer, not the detector. The practical decision is not "which idea," it is **"how much new experimentation do I commit to before knowing it will pay off."** That is exactly what the gated diagnostic in §7 resolves.

H is ranked #2 deliberately: it is the cheapest way to discover whether B is even viable, and it is a no-regret first step. B is #1 because it has the highest ceiling and the best thesis spine — but it should be *unlocked by* H, not committed to blindly.

---

## 4. Is the safe-readaptation pivot scientifically legitimate?

**Yes — but only in one specific form. The legitimacy hinges on a single test:**

> **A pivot is legitimate if and only if the new claim does not depend on the failed claim.**

- **Legitimate form (Route B):** "Drift detection alone is insufficient; the critical problem is *when not to adapt*. We characterize harmful readaptation and evaluate safe/cost-aware policies. QK-MMD is one of several instruments." — This claim **survives deleting every QK result** and replacing it with classical detectors. The backbone (oracle-regret, harmful adaptation, policy comparison) is detector-agnostic. **Not a rescue. A correct re-reading of what the data is saying.**

- **Illegitimate form:** "QK-MMD enables safe readaptation / is a better safe-adaptation trigger." — Still needs QK to win. The data does not support it (ToN-IoT: QK-ZZ is among the worst, gain −3.28). This would be a transparent rescue and a reviewer would catch it. **Do not write this paper.**

The data *genuinely* redirects attention to the decision layer:
- ToN-IoT Scanning: no-adaptation (BA 0.9201) beats every triggered strategy → naive triggering is harmful.
- CICIDS regime-dependence → the optimal adapt/no-adapt policy is regime-dependent.
- Benign nuisance → detectors fire on harmless drift.
- UNSW mild drift → adaptation gains are often tiny, so the cost of adapting can exceed the benefit.

These are not five separate failures. They are five pieces of evidence for **one** thesis: the field has been optimizing the wrong object (detector sensitivity) instead of the right one (the cost-aware adaptation decision).

**Verdict: the pivot is legitimate in its detector-agnostic form, and is arguably the scientifically *correct* framing — not merely a rescue.**

---

## 5. Is the pivot the best route — and would a reviewer see ToN-IoT as weakness or motivation?

**Best route: yes, Route B is the best route — with two non-negotiable conditions** (detector-agnostic framing; gated by the cheap diagnostic in §7). It is the best thesis spine, it converts liabilities into motivation, and it has a Q2-strong floor.

**ToN-IoT — weakness or motivation?** In the *current* paper it is a weakness ("your method fails externally"). In Route B it is **the single most valuable result in the paper** — direct, quantified evidence that triggered readaptation can be net-harmful, which is precisely the problem the paper solves. The same number (no-adapt BA 0.9201 > best adaptive 0.9139) flips from embarrassing to load-bearing purely by changing the question from "is QK the best detector?" to "should we have adapted at all?"

This sign-flip is the whole reason the pivot is worth taking seriously.

---

## 6. Direct answers to your 12 questions

1. **Is the detector-comparison paper truly only Q2?** Yes. Q1 is not reachable by framing alone — it lacks external validity, which is a data property, not a writing property.
2. **Is the pivot valid or just a rescue?** Valid, in detector-agnostic form (§4). A rescue, and unsupported, in any QK-centric form.
3. **Alternative routes ranked?** §2–§3. Best is B (detector-agnostic policy paper), unlocked by H (free oracle-regret diagnostic).
4. **Would a Q1 reviewer see ToN-IoT as weakness or motivation?** Weakness in the current paper; motivation/core evidence in Route B (§5).
5. **Is "safe readaptation under network drift" a stronger thesis than "QK-MMD comparison"?** Yes, clearly and honestly. It is a real problem with a clean motivating result, a detector-agnostic backbone, and it gives Paper 1 a better narrative role (quantum kernels as one instrument in an operational decision problem).
6. **Minimum experiment to validate the best route?** A two-phase gated protocol (§7): Phase 0 = free oracle-regret diagnostic on existing window-level results; Phase 1 = one bounded, pre-registered policy grid on 3 representative regimes — only if Phase 0 says the headroom exists.
7. **All datasets or selected?** **Selected representative regimes**, spanning the three phenomena: adaptation helps (CICIDS Wednesday), inverts (CICIDS PortScan), hurts (ToN-IoT Scanning); optionally UNSW DoS as mild-drift. Using all regimes is sprawl and dilutes.
8. **Which policies, to avoid arbitrary-k criticism?** A small *principled* grid with both bounds present: no-adapt and oracle (bounds), naive 1-of-1 (current), k-of-n {2-of-3, 3-of-5}, cooldown {2 settings}, one cost-aware (λ,γ) objective. Present the **Pareto front**, not a single chosen k — that defuses "why k=3?".
9. **How to avoid post-hoc/cherry-picking criticism?** (i) Pre-register the policy protocol (timestamped) *before* running. (ii) Keep QK as instrument, not hero — claims must not depend on it. (iii) Report all negatives transparently. (iv) The litmus test (§4): if the thesis survives deleting all QK content, it is not a quantum rescue. (v) Fix representative regimes and the success criterion in advance; honor the stop rule.
10. **Pivot paper full spec?** §8.
11. **Better-route spec (if not the pivot)?** The best route *is* the pivot in detector-agnostic form; its spec is §8. The no-pivot Q2 fallback spec is §9.
12. **If no Q1 route is viable?** Then it is Route A: stop experiments, write the Q2 paper. The Phase-0 diagnostic (§7) is the explicit, pre-committed decision rule that sends you here if the headroom is small.

---

## 7. The minimal, pre-registered, gated experiment (anti-sprawl)

This is designed so you cannot drift into another experiment-sprawl phase. It has a free go/no-go gate and a hard stop rule.

### Phase 0 — Oracle-regret diagnostic (FREE, from existing data, no model retraining of new datasets)
Using the existing `paper2_progressive_readaptation_window_results.csv` files you already have for each regime:
- For each regime, compute a **per-window envelope** across {no-adaptation, all detectors already run}. The per-window max BA is a (loose) lower bound on the oracle.
- Define **regret = (envelope/oracle BA) − (best realized naive-trigger BA)** per regime.
- **This quantifies how much performance naive triggering leaves on the table.** It is the entire justification for a policy paper.

**Go/no-go rule (pre-registered):**
- If regret is **large in ≥2 of the representative regimes** (e.g. ≥ the CI width of the naive results) → headroom exists → proceed to Phase 1.
- If regret is **small everywhere** → smart policies cannot help → **STOP. Write the Q2 paper (Route A).** No Phase 1.

Phase 0 costs essentially nothing and is the single most important step in this whole plan. Do it before deciding anything.

### Phase 1 — Bounded policy grid (ONLY if Phase 0 says go)
- **Regimes (fixed, 3 + optional 1):** CICIDS Wednesday (helps), CICIDS PortScan (inverts), ToN-IoT Scanning (hurts); optional UNSW DoS (mild). No others.
- **Detectors (only 2):** one cheap classical (Energy or KS) + QK-ZZ. **Not all six** — detector identity is not the contribution.
- **Policies:** no-adapt; naive 1-of-1 (current); k-of-n ∈ {2-of-3, 3-of-5}; cooldown ∈ {2 settings}; one cost-aware objective maximizing `gain − λ·adaptations − γ·runtime`; **oracle** upper bound.
- **Seeds/windows:** match existing protocol (10 seeds medium → 30 only for the final reported regimes).

**Pre-registered success criterion:** a policy is *validated* iff, across the representative regimes, it (i) never underperforms no-adaptation by more than ε in the harmful regime (ToN-IoT), AND (ii) preserves ≥X% of the naive-trigger gain in the beneficial regimes (Wednesday/PortScan). I.e. it Pareto-dominates the naive 1-of-1 policy on the harm-vs-gain plane. Fix ε and X *before* running.

**Stop rule (hard):**
- Policy validated → Q1 submission (Route B).
- No policy validated → report characterization + oracle-regret as the contribution → **Q2-strong**, and **stop**.
- Either way: **no additional datasets, no additional policies, no post-hoc tuning.** This is a closed protocol.

---

## 8. Pivot paper spec (Route B)

**Title:** *Knowing When Not to Retrain: Safe and Cost-Aware Readaptation for Adaptive Network Intrusion Detection under Concept Drift*

**Central research questions:**
- RQ1: How often, and by how much, does drift-triggered readaptation *harm* downstream IDS performance across attack regimes and datasets?
- RQ2: How large is the gap between naive triggering and an oracle adapt/no-adapt policy (the regret)?
- RQ3: Can simple, deployable safe/cost-aware policies (k-of-n, cooldown, cost-aware thresholds) close that gap without harming beneficial regimes?
- RQ4 (secondary): Does the choice of drift detector — classical or quantum-kernel — materially change the policy conclusions?

**Contributions:**
1. Evidence that naive drift-triggered readaptation is net-harmful in realistic regimes (ToN-IoT Scanning; UNSW mild drift), and regime-dependent in others (CICIDS).
2. An oracle-regret analysis quantifying the headroom for smarter adaptation decisions — detector-agnostic.
3. A family of safe/cost-aware readaptation policies and a Pareto evaluation on the harm-vs-gain plane.
4. A negative-but-important secondary result: detector choice (incl. QK-MMD) is *not* the lever — the policy is. This subsumes and correctly contextualizes the Paper-1/Paper-2 quantum-kernel work.

**Protocol:** the gated two-phase design in §7. Pre-registered.

**Main tables/figures:**
- Fig 1: per-regime BA of {no-adapt, naive, oracle} — the motivating harm/regret figure.
- Table 1: regret per regime/dataset (Phase 0).
- Fig 2: Pareto front (downstream gain vs adaptations/harm) per regime, policies as points, naive and oracle marked.
- Table 2: validated-policy comparison vs naive and no-adapt, CI95.
- Table 3 (secondary): detector-swap robustness (classical vs QK-ZZ) showing policy conclusions are detector-invariant.

**Success criteria:** §7 (a policy Pareto-dominates naive across representative regimes).
**Stop criteria:** §7 hard stop rule.

**Main vs appendix:**
- *Main:* harm/regret motivation, oracle-regret, policy Pareto, validated-policy table, detector-invariance (secondary).
- *Appendix:* full CICIDS four-regime detector characterization (the old "main" results become supporting evidence), UNSW + ToN-IoT full tables, feature-map sensitivity, expensive-RF, QK circuit details.

---

## 9. No-pivot Q2 paper spec (Route A — fallback)

If Phase 0 regret is small (or you choose the safe path), write the paper the previous reviews already specced:

**Title:** *Quantum-Kernel Drift Detection for Adaptive Network Intrusion Detection Systems: An Operational Characterization Across Attack Regimes*

**RQ:** Does QK-MMD provide a superior or complementary operating point vs classical drift detectors for triggering IDS readaptation under progressive drift?

**Contributions:** four-regime CICIDS characterization; operational utility framework (λ/γ/η); pre-registered feature-map sensitivity; honest external attempts (UNSW, ToN-IoT).

**Protocol/tables/main-vs-appendix:** exactly as in `paper2_storyline_001.md` and the two prior strategic reviews — UNSW *and ToN-IoT* both go to appendix as honest external evidence, with the harmful-adaptation observation noted in the discussion as future work (the seed of the policy paper).

**Success criterion:** coherent, honest, well-powered single-dataset characterization. **Stop:** no further experiments. Target Computer Networks / Computers & Security (Q2) / Expert Systems with Applications.

---

## 10. Revised abstract — PIVOT scenario (Route B)

> Adaptive Network Intrusion Detection Systems retrain their classifiers to cope with concept drift, and a large literature optimizes drift *detectors* to decide when to retrain. We show that this framing is incomplete and sometimes counterproductive: across three public IDS benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) and multiple attack regimes, drift-triggered readaptation ranges from strongly beneficial to actively harmful — in a ToN-IoT scanning regime, *no adaptation* outperforms every triggered strategy we evaluate, classical or quantum-kernel. We reframe adaptive retraining as a cost-aware sequential decision problem and quantify, via an oracle analysis, the regret incurred by naive triggering. We then evaluate a family of deployable safe/cost-aware readaptation policies (alarm confirmation, cooldown, and cost-aware thresholds) on representative regimes spanning beneficial, inverted, and harmful adaptation, presenting results on the harm-versus-gain Pareto plane. Our results indicate that *when not to adapt* is as important as drift sensitivity, that the choice of detector — including quantum-kernel MMD — is not the decisive lever, and that simple confirmation/cooldown policies can prevent harmful updates while preserving most of the benefit where adaptation helps. We release a pre-registered protocol to avoid post-hoc selection.

## 11. Revised abstract — NO-PIVOT scenario (Route A)

> (As in the prior strategic review.) Adaptive IDS must retrain under concept drift, and the drift trigger governs the trade-off between retraining frequency, downstream accuracy, and monitoring cost. We empirically characterize quantum-kernel MMD (ZZ, PauliXZ) as a retraining trigger across four CICIDS2017 attack regimes (30 seeds, CI95), against Energy distance, MMD-RBF, KS-max and JSD. QK-MMD ZZ significantly reduces readaptation frequency by 1.8–2.1 episodes vs Energy distance in Wednesday/DDoS at equivalent balanced accuracy and a 114× monitoring overhead; in PortScan the pattern inverts (more adaptations, higher accuracy); in WebAttacks PauliXZ leads in mean accuracy but does not significantly beat the strongest classical baselines. A parametric utility framework (λ/γ/η) delimits when QK-MMD is preferable. External attempts on UNSW-NB15 and ToN-IoT do not replicate the advantage and, in one regime, no-adaptation outperforms all detectors. We conclude that QK-MMD defines attack-regime-dependent operating points rather than a universal improvement, and that external generalization remains open.

---

## 12. Risk register

**Experiment-sprawl risk — HIGH and now the primary threat.** You have ~8 protocols already. The pivot *adds* experiments, which is exactly the danger. Mitigation: the Phase-0 free gate (kills the pivot cheaply if headroom is absent), 3 fixed regimes, 2 detectors, pre-registered policy grid, hard stop rule. **If you cannot commit to the stop rule, do not start Phase 1 — go Route A.**

**Thesis-weakness risk — this is the real driver of your anxiety, and it is legitimate.** "QK-MMD drift detector comparison" is a thin thesis spine (one Q2 paper). "Safe/cost-aware adaptation under network drift" is a strong spine that absorbs Paper 1 and Paper 2 into a coherent arc. The pivot reduces thesis-weakness risk *more* than it increases sprawl risk — provided it is gated.

**Post-hoc-perception risk — MODERATE, manageable.** Mitigated by pre-registration, detector-agnostic framing, the litmus test, and transparent reporting of all negatives (§4, §6.9). The biggest tell to avoid: never write a sentence implying you expected QK to win and were surprised. Write the paper as a problem paper from line one.

**Opportunity-cost risk.** Every week on experiments is a week not writing. The Q2 paper is fully writable today. If Phase 0 is negative, the *correct* move is to write Route A immediately, not to keep searching.

---

## 13. Final recommendation

**One call, in order:**

1. **Run Phase 0 (oracle-regret diagnostic) on existing data. It is free and decisive.** Do not skip it and do not over-build it.
2. **If regret is large in ≥2 representative regimes →** commit to **Route B (detector-agnostic safe-readaptation paper)** with the bounded, pre-registered Phase-1 policy grid as the Q1 target, keeping the CICIDS characterization as the guaranteed Q2-strong floor in the appendix. Demote QK from hero to instrument.
3. **If regret is small everywhere →** stop, accept Q1 is not reachable, and **write Route A (Q2 paper) now.**
4. **Either way:** test no new datasets, run no QK-centric rescue, honor the stop rule.

This gives you the best honest shot at Q1 *and* a strong thesis spine, while making it almost impossible to fall back into sprawl, and while guaranteeing a publishable Q2 outcome no matter what Phase 0 says.

I am **not** recommending the QK-centric version of the pivot, and I am **not** recommending abandoning Q1 outright. I am recommending a gated bet whose downside is bounded and whose upside is a genuinely better paper and thesis.

---

## 14. Text for your PhD director (Spanish, plano)

> Después de las campañas en CICIDS2017, UNSW-NB15 y ToN-IoT, la hipótesis de partida —que el kernel cuántico QK-MMD sería un mejor monitor de drift para reentrenar el IDS— no se sostiene como ventaja cuántica: no replica fuera de CICIDS y en ToN-IoT directamente no-adaptar gana a cualquier estrategia de reentrenamiento. Lo importante es que esos "fracasos" apuntan, todos, a un resultado más fuerte y más general: **detectar drift no basta; el problema real es decidir cuándo NO readaptar, porque el reentrenamiento disparado por drift puede degradar el sistema.** Propongo reorientar el Paper 2 de "comparación de detectores cuánticos" a "readaptación segura y consciente del coste en IDS adaptativos bajo drift", donde el detector (cuántico o clásico) pasa a ser un instrumento, no el protagonista. Antes de gastar más cómputo haré un diagnóstico gratuito sobre los datos que ya tengo (cuánto rendimiento pierde el reentrenamiento ingenuo frente a un oráculo que sabe cuándo adaptar). Si ese hueco es grande, hay material para intentar Q1 con un experimento mínimo y pre-registrado de políticas de readaptación; si es pequeño, escribo directamente un Q2 sólido y honesto con lo que ya tengo. En ambos casos el cómputo está acotado, no se prueban más datasets, y no se fuerza ninguna narrativa de ventaja cuántica que los datos no respaldan. Creo que esta reorientación da una tesis más fuerte y honesta que la comparación de detectores, y mantiene un Q2 garantizado como suelo.

---

## 15. Reviewer attack simulation

**Attack 1 — "This is a failed quantum paper rebranded as a policy paper."**
> *Response:* The contribution is detector-agnostic and pre-registered. Every claim survives replacing QK-MMD with classical detectors; QK is reported as one instrument and explicitly shown *not* to be the decisive lever. The motivating result (harmful readaptation) and the oracle-regret backbone do not involve quantum kernels at all. We report all quantum negatives transparently. (Litmus test: delete all QK content — the paper still stands.)

**Attack 2 — "The harmful-adaptation result is just one ToN-IoT regime."**
> *Response:* We show a *spectrum* across regimes and datasets — beneficial (CICIDS Wednesday), inverted (PortScan), and harmful (ToN-IoT Scanning), plus mild-drift (UNSW) where adaptation gains are negligible. The point is not that adaptation always hurts; it is that the adapt/no-adapt decision is regime-dependent and naive triggering is provably sub-oracle. The oracle-regret analysis quantifies this on every regime.

**Attack 3 — "Why these k-of-n / cooldown values? Cherry-picked."**
> *Response:* We pre-register a small principled grid and present the full Pareto front with both bounds (no-adapt and oracle) marked, rather than a single chosen operating point. Conclusions are stated over the front, not a hand-picked k.

**Attack 4 — "Only two detectors and three regimes — underpowered / selective."**
> *Response:* Regimes were chosen *a priori* to span the qualitative phenomenon (helps / inverts / hurts), and detector choice is shown to be immaterial to the policy conclusion (the secondary detector-invariance result). Adding more detectors/regimes tests the same claim at higher cost; we pre-committed to representative coverage to avoid post-hoc expansion.

**Attack 5 — "Oracle is unrealizable, so the regret is meaningless for deployment."**
> *Response:* The oracle is a diagnostic upper bound that quantifies *available* headroom and motivates the problem; we never propose deploying it. The deployable contribution is the safe/cost-aware policies, evaluated against the realistic naive and no-adapt baselines.

**Attack 6 — "No statistical significance for the policy improvement."** *(fires only if Phase 1 is weak)*
> *Response (if validated):* Pareto-dominance over naive is reported with CI95 over seeds on the reported regimes. *Response (if not validated):* We do not claim a dominant policy; the contribution is the characterization of harmful adaptation and the oracle-regret, with the negative policy result reported honestly — which is itself the pre-registered Q2 outcome.

**Attack 7 — "Single-classifier (SVC-RBF) downstream."** (inherited)
> *Response:* The expensive-RF appendix shows the cost balance shifts with downstream cost; the cost-aware policy objective is explicitly parameterized to absorb this, and downstream-model sensitivity is acknowledged as a limitation.

---

*End of review. No commits made, nothing deleted, no large experiments launched. The only recommended computation — Phase 0 oracle-regret — uses existing window-level result files and is gated by a pre-registered stop rule.*
