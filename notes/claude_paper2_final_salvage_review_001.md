# Paper 2 — Final Salvage Review

> **ADDENDUM (2026-07-01, supersedes the Q1 verdict below).** After this review, two things changed the picture: (1) an audit produced a mechanism law `corr(base BA, adaptation benefit) = −0.894`; (2) a **pre-registered Phase 2** built and validated the deployable solution this review said was missing — a **label-efficient validate-before-commit readaptation gate**. It PASSES all pre-registered criteria for BOTH classical (KS-max) and quantum (QK-ZZ) detectors: in the harm regime (ToN-IoT) it turns net-harmful naive triggering (−1 to −2 pts) into net benefit (+1.2 to +1.3 pts), significantly beating **both** naive (+2.4/+3.5 pts, CI95) **and** no-adaptation (+1.2/+1.3 pts, CI95), with ~100 labels; the zero-label unsupervised variant fails (labels are necessary). See `paper2_phase2_gated_readaptation_checkpoint_001.md`. **Revised verdict: Q1 is now credible (~45–60% at Computers & Security / TDSC), not dead.** The paper is now a *solution* paper (harmful adaptation → mechanism law → working label-efficient gate), not a diagnostic one. The §2 "Q1 is dead" conclusion below reflected the evidence BEFORE Phase 2 and is retained only for history.

**Prepared by:** Claude (Opus 4.8)
**Date:** 2026-07-01
**Branch:** paper2-expensive-downstream
**Trigger:** All experimental routes closed — QK universal advantage dead, external Q1-gate (ToN-IoT) failed, safe-readaptation Phase 1 failed its pre-registered criteria. Request for a brutally honest, anti-anchored, final decision on whether anything remains salvageable as a paper or thesis chapter.
**Roles taken:** skeptical Q1 reviewer + worried thesis director + publication strategist. No artificial optimism.

This note supersedes `claude_paper2_safe_readaptation_rescue_review_001.md` for the go/no-go decision, because the gated experiment that review proposed has now *run and returned a verdict*. It does not delete anything. No commit. No experiments.

---

## 1. Brutal verdict (read this first)

The project is **not dead, but it is smaller than you hoped, and the Q1 door is closed.** Three things are now settled by data, not by framing:

1. **The quantum-advantage claim is dead — confirmed three independent ways.** CICIDS2017 gives narrow, regime-dependent operating points. UNSW-NB15 gives non-significant mixed evidence. ToN-IoT actively contradicts it (no-adaptation beats every triggered strategy, QK-ZZ among the worst). No paper whose central claim depends on QK winning is salvageable. Stop trying to make QK the hero. This is final.

2. **The safe-readaptation pivot has now also failed its own pre-registered test — and this is not a surprise, it is the system working.** The previous strategic review (Opus, 2026-06-29) built a gated protocol with an explicit stop rule: *"No policy validated → report characterization + oracle-regret → Q2-strong, and stop."* Phase 1 ran. No policy was validated (A: fail, B: fail, C: pass-narrowly). **You are now standing exactly on the pre-committed stop condition.** The honest move is not to mourn it — it is to execute the rule you wrote in advance. Anything else is post-hoc thrashing.

3. **What actually survives is real, but it is a *characterization + negative-results* contribution, not a *method-wins* contribution.** That is a genuine Q2 paper and a genuine, defensible thesis chapter. It is not Q1. Do not let anyone — including a future version of me — tell you a fourth pivot gets you to Q1. It won't; it will read as desperation.

**One-line verdict:** *Stop experimenting. Write one honest Q2 paper framed around the decision problem (when readaptation helps vs. hurts), with QK-MMD as an instrument and every negative result load-bearing. It is a solid thesis chapter. Q1 is not reachable from this evidence base and pursuing it further is the single biggest risk to the thesis.*

---

## 2. Is Q1 still credible?

**No.** Honest probability at a serious Q1 venue (TDSC, TIFS, Computers & Security top track), with the best possible framing: **~10–20%.** Not worth attempting. Reasons, in order of severity:

- **No external validity for any positive claim.** Q1 IDS venues treat cross-dataset generalization as a data property, not a writing property. You have one dataset with positive-ish signal (CICIDS), one marginal (UNSW), one contradicting (ToN-IoT). That is the *definition* of "does not generalize."
- **The one route that could have carried Q1 — a validated safe/cost-aware policy — failed.** A Q1 "solution" paper needs a solution that works. You have a problem (harmful adaptation) and a *failed* fix (simple k-of-n/cooldown). "We found a problem and our fix didn't work" is honest and publishable, but it is a diagnostic/negative contribution, and top venues rarely rate that Q1.
- **Post-hoc exposure is now high.** Three reframings are on record (QK-advantage → operational characterization → safe-readaptation). A fourth pivot toward Q1 would be transparently a rescue. Reviewers punish this hard.
- **The 114× monitoring overhead with no delivered advantage** is a standing liability no framing removes.

There is no honest path to Q1-strong. I will not pretend otherwise, and you should distrust anyone who says there is.

---

## 3. Is Q2 credible?

**Yes — with the right framing, ~65–75% at a suitable venue.** But be precise about *why*, because the wrong framing turns the same results into a weak "our method didn't win" paper that reviewers reject as thin.

- **Weak Q2 framing (avoid):** "QK-MMD as a drift monitor for adaptive IDS." Reads as: quantum method, doesn't beat classical, single dataset, expensive. A reviewer's honest summary is "incremental, negative, why publish."
- **Strong Q2 framing (recommended):** "Whether and when to readapt is the real problem; drift-triggered retraining is regime-dependent and sometimes net-harmful; detector choice (classical *or* quantum-kernel) is not the decisive lever; and simple safe-policies do not fix it." Here the negatives are the *content*. ToN-IoT flips from embarrassing to load-bearing. QK becomes an honestly-reported instrument, not a failed hero.

The strong framing is not spin — it is the correct reading of what the data says. The whole campaign is five pieces of evidence for one thesis: *the field optimizes the wrong object (detector sensitivity) instead of the right one (the cost-aware adapt/no-adapt decision).* That is a real, publishable idea at Q2.

**Even-Q2-is-weak check:** Is there a risk even Q2 fails? Yes, a real one, if the paper is written as a chronological pile or as a quantum paper. Written as a disciplined phenomenon paper, Q2 is solid. The risk is *execution* (writing), not evidence.

---

## 4. Does thesis value remain? (Yes — and this is the most important answer)

**Thesis value clearly remains, and it is stronger than a single Q2 paper suggests.** Here is exactly why, so you can defend it to your director:

- A PhD is judged on a coherent line of inquiry with honest, well-powered findings — **not** on journal tier. You have a genuine multi-dataset investigation with pre-registration, CI95, negative controls, and honored stop rules. That is *good science*, and examiners reward it independently of venue.
- The negative results are a contribution, not a hole. "We tested whether quantum-kernel drift monitors help adaptive IDS across three benchmarks and they do not robustly; and we showed the deeper reason is that the adapt/no-adapt decision — not detector sensitivity — governs outcomes, sometimes making no-adaptation optimal" is a **defensible, quotable thesis conclusion.** It closes a real question the field left open.
- It gives Paper 1 a better role. The quantum-kernel work becomes *one instrument* inside an operational decision problem, rather than a stand-alone advantage claim that Paper 2 then fails to extend. The arc "we found a quantum-kernel signal (P1) → we tested whether it is operationally decisive for adaptive IDS and found the decision layer dominates (P2)" is a *stronger, more mature* narrative than "quantum kernels win."
- Methodological transferables: the progressive-drift readaptation protocol, the λ/γ/η utility framework, the oracle-regret diagnostic, and the pre-registered policy grid are reusable contributions that stand on their own.

**Bottom line for the director:** the thesis does not depend on Q1. A strong Q2 paper plus an honest "here is why the obvious approach doesn't work" chapter is a legitimate, examinable, defensible doctoral contribution.

---

## 5. Ranked salvage routes

I re-derived the option set independently rather than anchoring on prior pivots. After Phase 1's failure, several previously-attractive routes collapse into each other (the "policy solution" leg is gone), which simplifies the ranking.

| Rank | Route | What it is | Q1 | Q2 | Post-hoc risk | New experiments | Thesis value |
|---|---|---|---|---|---|---|---|
| **1** | **Phenomenon + characterization Q2 paper** (A+C merged) | Protagonist = when/whether to readapt (helps/inverts/harms); QK = instrument; failed safe-policies = honest negative + future work | No | **~70%** | Moderate, manageable | **None** | **High** |
| 2 | Plain QK operational-characterization Q2 (Route A) | CICIDS four-regime QK story; external + policy work to appendix | No | ~65% | Low | None | Medium |
| 3 | Thesis-chapter-only (no journal now) | Archive everything as a chapter; submit nothing | n/a | n/a | None | None | Medium–High |
| 4 | Split into two papers (F) | QK characterization + decision-layer study separately | No | Each ~55% | Medium (thin halves) | None | Medium |
| 5 | Negative-results / benchmarking paper (D) | "Do QK drift monitors help adaptive IDS? A null result" | Very low | Niche only | Low | None | Low–Medium |
| 6 | Redesign safe-policy grid and rerun (rescue Phase 1) | Longer cooldowns / abstention-by-default / cost-aware objective | ~15% | (delays Q2) | **High** | Bounded but real | Medium |
| 7 | Add a 4th external dataset / more ToN-IoT attacks | Chase replication | ~10% | (delays) | **Very high** | Large | Low |
| 8 | Keep chasing QK advantage | — | ~0% | — | Fatal | Any | Negative |

**Why Route 1 wins:** it requires zero new computation, converts every liability into signal, gives the best thesis spine, and has the highest Q2 acceptance probability. Routes 6–8 all trade high post-hoc risk and real compute for marginal Q1 probability that the evidence already argues against.

**On Route 6 (the tempting one):** Phase 1's failure has a charitable mechanical reading — the "safe" policies used cooldown 0 and were therefore *more aggressive* than the legacy 3-consecutive + cooldown-10 policy, so of course they increased adaptations (see gate summary: PortScan best-safe adaptation reduction vs legacy = **−1.8**, i.e. +1.8 *more*). A redesigned grid with genuine abstention/longer cooldowns *might* pass Criterion B. **But do not do this.** Two reasons: (i) in ToN-IoT the optimal policy degenerates to *never adapt*, and no drift-triggered policy can beat "never adapt" by construction when the drift is real but non-actionable — so the ceiling of the whole exercise is "match no-adaptation," which is not a Q1 result; (ii) a fourth experimental round after two failed gates is exactly the sprawl/desperation pattern reviewers and examiners read as loss of control. The honest, and frankly the disciplined, move is to *report the mechanism as the finding*, not to keep tuning.

---

## 6. Final recommended route

**Route 1: one honest Q2 paper, phenomenon-framed, zero new experiments, then stop.**

Protagonist: the **adapt / don't-adapt decision under concept drift** in adaptive IDS. QK-MMD is the studied instrument (continuity with Paper 1), not the hero. Every negative result is content. The failed safe-policy grid is presented as a pre-registered negative that motivates the future-work direction ("principled cost-aware decision policies, not more sensitive detectors").

**Fallback (risk-averse choice):** if you or your director judge the phenomenon framing too exposed to "rebranded failed quantum paper," fall back to Route 2 (plain QK operational characterization, ToN-IoT/UNSW/policy work in appendix). It is safer and slightly less novel. My recommendation is Route 1, but Route 2 is a legitimate, defensible second choice — decide based on your appetite for the reframing-risk trade-off.

**Hard rules going forward (self-binding):** no new datasets; no new policies; no policy re-tuning; no QK-advantage rescue; no more ToN-IoT attacks. The experimental phase is over. The remaining work is *writing*.

---

## 7. Exact paper title

**Primary (Route 1, phenomenon-framed, keeps QK visible for thesis continuity):**

> *When Not to Retrain: Regime-Dependent and Sometimes Harmful Readaptation in Adaptive Network Intrusion Detection under Concept Drift, with Classical and Quantum-Kernel Drift Monitors*

Tighter variant:

> *Knowing When Not to Retrain: The Adapt/No-Adapt Decision Dominates Detector Choice in Adaptive IDS under Concept Drift*

**Fallback (Route 2, QK-characterization-framed):**

> *Quantum-Kernel Drift Monitoring for Adaptive Network Intrusion Detection: An Operational Characterization and Its Limits Across Datasets*

---

## 8. Exact research questions

- **RQ1 (phenomenon, primary):** Across attack regimes and independent datasets, when does drift-triggered readaptation *improve* downstream IDS performance, and when does it *degrade* it relative to no adaptation?
- **RQ2 (regret):** How much performance does naive drift-triggered readaptation leave on the table relative to an oracle adapt/no-adapt decision?
- **RQ3 (detector, demoted):** Do quantum-kernel MMD monitors define operating points that differ from strong classical detectors, and do any advantages replicate across datasets? *(Answer: regime-dependent on CICIDS, not replicated externally.)*
- **RQ4 (fix, honest negative):** Can simple, deployable safe/cost-aware policies (k-of-n confirmation, cooldown) reliably prevent harmful readaptation while preserving benefit where adaptation helps? *(Answer: not with the simple policies tested — pre-registered negative.)*

---

## 9. Exact contributions

1. **A regime taxonomy of readaptation value** across three public IDS benchmarks: *beneficial* (CICIDS2017 DDoS/Wednesday/PortScan/WebAttacks), *marginal/mixed* (UNSW-NB15 DoS/Reconnaissance), *harmful* (ToN-IoT Scanning, corroborated by DDoS/Injection smokes where no-adaptation wins).
2. **Direct evidence that naive drift-triggered readaptation can be net-harmful** — in ToN-IoT Scanning (10 seeds), no-adaptation (BA 0.9201) beats *every* triggered strategy, classical or quantum-kernel.
3. **An operational characterization of QK-MMD as a retraining trigger**, with a parametric utility framework (λ/γ/η), a pre-registered feature-map sensitivity study, and an honest external-validity finding: QK advantages are regime-dependent on CICIDS and do not robustly replicate.
4. **A pre-registered negative result on safe-readaptation policies:** simple k-of-n/cooldown policies do not reliably prevent harmful adaptation, indicating that the open problem is a *principled cost-aware decision policy*, not a more sensitive detector.
5. **Reusable methodology:** the progressive-drift readaptation protocol, the oracle-regret diagnostic, and the utility framework, applicable to any drift detector in adaptive IDS.

---

## 10. Main / appendix / omit decisions

Two columns: the **recommended Route-1** placement, and the **Route-2 fallback** placement where it differs.

| Component | Route 1 (recommended) | Route 2 (fallback) | Rationale |
|---|---|---|---|
| **CICIDS2017 four regimes** | **Main** | **Main** | Core evidence in both framings; the beneficial + inverted regimes. |
| **UNSW-NB15 (DoS + Recon)** | **Main (concise)** | Appendix | In the phenomenon framing, external non-replication is load-bearing, not a footnote. |
| **ToN-IoT Scanning (medium) + DDoS/Injection (smoke)** | **Main — the star result** | Appendix | Harmful-adaptation is the paper's most valuable finding under Route 1; only a limitation under Route 2. |
| **Safe-readaptation Phase 0 (regime taxonomy)** | **Main (light — framing figure)** | Omit/appendix | The helps/inverts/harms taxonomy is a clean motivating figure. |
| **Safe-readaptation Phase 1 (failed policy grid)** | **Appendix + one honest paragraph in Discussion/Limitations** | Appendix | Pre-registered negative → future work. Must be reported (transparency), must not be protagonist. |
| **Feature-map sensitivity (ZZ/PauliXZ reps 1–3)** | Appendix | Appendix | Robustness/anti-cherry-pick check. |
| **Benign / nuisance controls** | **Main (short)** | Main (short) | Honest control; pre-empts "does QK just filter benign drift better?" (no). |
| **Expensive RF downstream** | Appendix | Appendix | Negative cost result; kills the "expensive downstream saves QK" argument honestly. |
| Adaptive monitor / long-stream single-change / hybrid OR / geometry diagnostics / operational-scale proxy | **Omit** | **Omit** | Superseded, negative, or speculative. Already flagged in `paper2_storyline_001.md`. |

**Direct answers to your itemized inclusion questions:**
- **ToN-IoT:** *Main* under Route 1 (it is the strongest finding); appendix under Route 2. Either way, include it — omitting it would be dishonest and would discard your best evidence.
- **UNSW-NB15:** Main (concise) under Route 1; appendix under Route 2. Include it.
- **Phase 1 safe-readaptation:** Appendix + a paragraph. Never main protagonist. It failed; report it as a pre-registered negative.

---

## 11. Final abstract (Route 1)

> Adaptive network intrusion detection systems (IDS) retrain their classifiers to cope with concept drift, and a large literature optimizes drift *detectors* to decide when to retrain. We show this framing is incomplete and sometimes counterproductive. Across three public IDS benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) and multiple attack regimes, drift-triggered readaptation ranges from strongly beneficial to actively harmful: in a ToN-IoT scanning regime, *no adaptation* outperforms every triggered strategy we evaluate — classical or quantum-kernel — over 10 seeds. We characterize this spectrum with an oracle-regret analysis that quantifies how much performance naive triggering leaves on the table, and we evaluate quantum-kernel Maximum Mean Discrepancy (QK-MMD) monitors (ZZ, PauliXZ) against strong classical detectors (Energy distance, MMD-RBF, KS-max, JSD) under a progressive-drift readaptation protocol with 30-seed CI95. QK-MMD defines regime-dependent operating points on CICIDS2017 — reducing readaptation frequency by 1.8–2.1 episodes at equivalent balanced accuracy in volumetric regimes, and inverting in port-scan regimes — but these profiles do not robustly replicate on UNSW-NB15 or ToN-IoT, at a 114× monitoring-runtime cost. Finally, in a pre-registered experiment we find that simple safe/cost-aware policies (k-of-n confirmation, cooldown) do *not* reliably prevent harmful readaptation. Our results indicate that *when not to adapt* is as important as drift sensitivity, that the choice of detector — including quantum kernels — is not the decisive lever, and that the open problem is a principled cost-aware adaptation decision rather than a more sensitive drift detector. We release the protocol and a pre-registered evaluation to prevent post-hoc selection.

---

## 12. Final introduction thesis paragraph

> Machine-learning intrusion detectors degrade under network concept drift, so adaptive IDS periodically retrain. Because retraining is costly, the field frames the core question as *drift detection*: build a sensitive monitor, and retrain when it fires. This paper argues that framing is wrong on both ends. First, more sensitive detection does not translate into better outcomes: we evaluate quantum-kernel MMD monitors — motivated by geometric expressiveness and by a prior signal in Paper 1 — against strong classical two-sample detectors, and find only regime-dependent operating points on one dataset that fail to replicate on two others. Second, and more fundamentally, drift-triggered retraining is not always beneficial: across CICIDS2017, UNSW-NB15 and ToN-IoT we observe a spectrum from strong benefit to net harm, including a regime where *no adaptation* dominates every triggered strategy. We therefore reframe adaptive retraining as a cost-aware adapt/no-adapt decision, quantify the regret of naive triggering against an oracle, and show — in a pre-registered test — that simple confirmation/cooldown policies do not close the gap. The contribution is a characterization of *when* readaptation helps or hurts, and the demonstration that the decision layer, not the detector, is the object that must be optimized.

---

## 13. Final limitations paragraph

> Our study has clear limits. The positive readaptation benefits are concentrated in CICIDS2017, whose scenarios share a reference distribution and capture pipeline; the two external datasets provide, respectively, marginal (UNSW-NB15) and contradicting (ToN-IoT) evidence, so we do not claim cross-dataset generalization of any detector advantage. All quantum kernels are classically simulated; the reported 114× monitoring overhead is a simulation figure and does not represent quantum hardware. The harmful-adaptation finding is strongest on ToN-IoT and should not be read as universal — it is a demonstration that the sign of the readaptation effect is regime- and dataset-dependent, not that adaptation is generally harmful. The safe-policy experiment tested only a small family of k-of-n/cooldown rules with a single cost-aware objective; our negative result rules out these simple policies as a reliable fix, but not the broader class of principled decision policies, which we identify as future work. Downstream evaluation centers on SVC-RBF, with a Random Forest appendix showing the cost balance shifts with downstream expense. Finally, drift thresholds are calibrated offline on a historical stream rather than fully online.

---

## 14. Párrafo final para el director de tesis (Español)

> Tras las campañas completas en CICIDS2017, UNSW-NB15 y ToN-IoT, y tras dos puertas experimentales pre-registradas (el Q1-gate externo y la Fase 1 de readaptación segura), la conclusión honesta es clara y ya la habíamos comprometido de antemano: **la vía Q1 no es alcanzable con esta evidencia y debemos dejar de experimentar.** La hipótesis de partida —que el kernel cuántico QK-MMD sería un mejor monitor de drift para reentrenar el IDS— no se sostiene como ventaja cuántica: no replica fuera de CICIDS2017 y en ToN-IoT directamente *no adaptar* gana a cualquier estrategia de reentrenamiento. La Fase 1 de políticas seguras tampoco pasó sus criterios pre-registrados. Lo importante es que estos "fracasos" no dejan el proyecto vacío: **apuntan todos al mismo resultado, más general y más honesto —detectar drift no basta; el problema real es decidir cuándo NO readaptar, porque el reentrenamiento disparado por drift puede degradar el sistema, y el detector (cuántico o clásico) no es la palanca decisiva.** Propongo cerrar la fase experimental y escribir **un único paper Q2 sólido** con ese marco (el problema de decisión como protagonista, QK-MMD como instrumento, y todos los resultados negativos como contenido, no como debilidad). No es Q1, y no debemos forzar un cuarto giro para intentarlo: eso solo aumentaría el riesgo de parecer un rescate post-hoc. Como capítulo de tesis, esta línea es defendible y examinables: una investigación multi-dataset, pre-registrada, con controles negativos y reglas de parada honradas, que responde a una pregunta abierta del campo. Mi recomendación firme es: **parar, escribir el Q2, y presentar la parte de decisión de readaptación como la contribución conceptual del capítulo.**

---

## 15. Reviewer attack simulation (harshest)

**A1 — "This is a failed quantum-advantage paper rebranded twice."**
> The contribution is detector-agnostic and every quantitative claim survives deleting all QK content: the regime taxonomy, the harmful-adaptation result (no-adapt > all triggered on ToN-IoT), and the oracle-regret are computed over classical and quantum detectors alike. QK is reported transparently as one instrument and shown *not* to be decisive. Pre-registration timestamps for the protocol and the policy grid are provided. (Litmus test: remove every quantum result — the paper still stands.)

**A2 — "The harmful-adaptation result is a single ToN-IoT regime — anecdotal."**
> It is the strongest of a consistent set: ToN-IoT Scanning at 10 seeds (no-adapt BA 0.9201 vs best adaptive 0.9139), corroborated by ToN-IoT DDoS and Injection smokes where no-adaptation also wins or ties. The claim is not "adaptation always hurts" — it is that the *sign* of the readaptation effect is regime/dataset-dependent, spanning benefit (CICIDS) to harm (ToN-IoT), which the oracle-regret quantifies on every regime.

**A3 — "Your proposed safe policies don't work, so what's the contribution?"**
> The failed policy grid is reported as a pre-registered negative, not hidden. Its value is diagnostic: it shows simple confirmation/cooldown rules are insufficient because in harmful regimes the optimal policy degenerates to no-adaptation, which no drift-triggered rule can beat when the drift is real but non-actionable. This localizes the open problem precisely — principled cost-aware decision policies — which is a contribution, not a gap.

**A4 — "Single positive dataset; no generalization."**
> We explicitly do not claim generalization of any detector advantage — that is a stated finding, not a limitation we tried to hide. The generalizing claim is the *phenomenon* (regime-dependent, sometimes-harmful adaptation), which we demonstrate *across* three datasets, precisely by including the non-replications.

**A5 — "114× overhead makes QK pointless."**
> Acknowledged as a hard limitation; it is a classical-simulation figure, not hardware. It reinforces, rather than undercuts, the paper's thesis: since the detector is not the decisive lever, a 114× monitor buys nothing, which is itself an operational conclusion.

**A6 — "Balanced accuracy is the wrong IDS metric."**
> BA is robust to the severe class imbalance in these benchmarks; attack-recall/F1 are available from raw results and the regime rankings are unchanged. (Add an attack-recall column before submission to close this pre-emptively.)

**A7 — "Why k=3 / cooldown 10 for legacy? Arbitrary."**
> The policy grid and legacy baseline were pre-registered; we report the full set and note explicitly that the "safe" cooldown-0 variants were in fact *more* aggressive than legacy, which is why they failed the adaptation-reduction criterion — an honest mechanistic account, not a tuned result.

---

## 16. Final stop/go decision

**STOP experiments. GO to writing. Target Q2. Preserve as a strong thesis chapter.**

- **Continue with more experiments?** No. Two pre-registered gates have fired negative; a third round is sprawl.
- **Stop and write Q2?** **Yes — this is the decision.**
- **Split paper?** No — the halves are too thin; one integrated phenomenon paper is stronger.
- **Abandon journal target?** No — a Q2 submission is warranted. Only abandon the *Q1* target, which is already unreachable.
- **Other?** Fold the decision-layer finding into the thesis as its conceptual contribution; keep Paper 1 as the instrument-level precursor.

**Recommended venues (Route 1):** Computers & Security (CiteScore ~9), Computer Networks, Journal of Information Security and Applications, Expert Systems with Applications. Lead with the decision-problem framing in the cover letter.

**Immediate next action:** create the manuscript skeleton and draft Method + Experimental Protocol (mechanical, unblocks everything), then Results in logical (not chronological) order, per `paper2_storyline_001.md` reorganized around the phenomenon frame. Add an attack-recall column to the main tables before submission.

---

*End of review. Consistent with the pre-registered stop rule in `claude_paper2_safe_readaptation_rescue_review_001.md` §7 and `paper2_safe_readaptation_phase1_checkpoint_001.md`. No commit made, nothing deleted, no experiments launched, no new datasets proposed.*
