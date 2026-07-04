# Paper 2 — Strategic Review After UNSW-NB15 Medium

**Date:** 2026-06-29  
**Branch:** paper2-expensive-downstream  
**Trigger:** UNSW-NB15 medium (10 seeds, 100 windows, DoS + Reconnaissance) completed

---

## 0. Brutal Verdict

**UNSW-NB15 medium did not replicate the main findings. The efficiency story is CICIDS2017-specific. The recovery story is CICIDS2017-specific. The paper is still publishable, but only at Q2 — and only if framed honestly.**

The previous strategic decision tree was explicit: "Smoke fails / pattern does not replicate → Q2-now path." UNSW medium is not a smoke — it is a full 10-seed experiment. The pattern did not replicate in either scenario. The decision tree already told you what to do. The answer has not changed: **Q2-now.**

Do not scale UNSW to 30 seeds. Do not improve the UNSW protocol. Stop experiments. Start writing.

---

## 1. What UNSW Medium Actually Shows

The following is a raw reading of the CI tables, not a motivated interpretation.

### UNSW DoS — QK-MMD ZZ

- BA diff vs Energy: +0.001375 → CI [-0.012, 0.008] — not significant, mean favors Energy
- n_adaptations diff vs Energy: -0.4 → CI [-0.9, 0.1] — not significant
- n_adaptations diff vs MMD-RBF: +0.4 → CI [0.1, 0.7] — **significantly more adaptations than MMD-RBF**
- Mean BA ranking: QK-ZZ is **last** among all detectors (including no adaptation as baseline)

**CICIDS2017 DoS analog pattern:** ZZ fewer adaptations, tied BA vs Energy → significant.  
**UNSW DoS reality:** ZZ not fewer adaptations vs Energy, not tied BA vs Energy, ranked last in BA, uses significantly more adaptations than MMD-RBF.  
**Verdict: does not replicate.**

### UNSW DoS — QK-MMD PauliXZ

- BA diff vs Energy: +0.004 → CI [-0.003, 0.011] — not significant
- BA diff vs MMD-RBF: +0.0001 → CI [-0.011, 0.009] — tied (essentially identical)
- BA diff vs KS-max: -0.004 → CI [-0.014, 0.005] — not significant, mean favors KS
- n_adaptations vs MMD-RBF: +0.6 → CI [0.1, 1.1] — **significantly more adaptations than MMD-RBF**

**KS-max and JSD lead the BA ranking in UNSW DoS. Two of the cheapest classical detectors outperform every QK variant without statistical uncertainty about their ranking at the mean level.**  
**Verdict: not only no QK advantage — cheap classical methods dominate.**

### UNSW Reconnaissance — QK-MMD ZZ

- BA diff vs Energy: +0.001 → CI [-0.003, 0.005] — not significant
- BA diff vs MMD-RBF: +0.002 → CI [-0.002, 0.005] — not significant
- BA diff vs KS-max: +0.003 → CI [-0.003, 0.008] — not significant
- n_adaptations vs Energy: +0.4 → CI [0.1, 0.7] — **significantly more adaptations than Energy**
- Only significant positive: better than JSD (a weak baseline, CI [0.0003, 0.010]) and better than PauliXZ

**CICIDS2017 PortScan pattern:** ZZ more adaptations, but significantly better BA vs Energy (CI [0.001, 0.013]) — at least the BA gain was significant.  
**UNSW Recon reality:** ZZ more adaptations vs Energy (again, higher cost), but BA gain is NOT significant (+0.001, CI [-0.003, 0.005]).  
**Verdict: the cost side replicates (more adaptations), the benefit side does not (BA gain is not significant). The PortScan story breaks here.**

### Why the Magnitudes Are Smaller in UNSW

This is a critical observation: the absolute scale of drift benefit is much smaller in UNSW.

| Metric | CICIDS Wednesday | UNSW DoS | UNSW Recon |
|---|---:|---:|---:|
| No adaptation BA | ~0.843 | 0.840 | 0.846 |
| Best detector BA | ~0.987 | 0.854 | 0.849 |
| Max gain from adapting | ~0.144 | 0.014 | 0.003 |

UNSW DoS and Reconnaissance are **mild drift scenarios** where the maximum performance gain from adapting is 1–2 BA points. In that regime, all detectors perform nearly identically because the drift signal is weak. The distributional shift in UNSW DoS/Recon is much smaller than in CICIDS2017 regimes. This is not just "QK fails" — it is "no detector discriminates here because the stakes are too low."

This observation is honest but double-edged. A reviewer will also read it as: "QK only shows advantages when CICIDS2017-specific drift is sufficiently severe." Both readings are accurate.

---

## 2. Does UNSW Strengthen or Dilute the CICIDS2017 Story?

**It dilutes the story if put in the main paper. It is neutral to mildly positive if quarantined in the appendix with an honest framing.**

### What UNSW adds (genuinely)

1. The pipeline runs on a different dataset. The preprocessing adapter works. This is a non-trivial engineering validation, not a scientific finding.
2. UNSW does not show catastrophic failure. QK is "competitive" in the sense that it is not dramatically worse than all classical baselines.
3. The mixed results strengthen the limitations section — you can say you tried, you are honest about what you found, and you are not hiding negative evidence.
4. The "mild drift / low discrimination" observation (gain from adapting ≈ 0.003–0.014 BA) is an interesting environmental moderator that could be discussed in limitations.

### What UNSW removes (honestly)

1. The efficiency story (ZZ fewer adaptations, same BA) does not cross the Q1 replication bar. It does not cross the Q2 replication bar either — the result in UNSW DoS is not significant.
2. The BA-recovery story (ZZ more adaptations but better BA) does not replicate with significance.
3. In UNSW DoS, KS-max and JSD — the two cheapest classical detectors — lead the BA ranking. This is the most unfavorable result in the entire paper for QK because it inverts the expected hierarchy completely.
4. Any claim that includes the phrase "generalizes to" or "is confirmed on an external dataset" will be rejected by an honest reviewer. UNSW does not support generalization claims.

### Net assessment

UNSW is a weak positive when it goes in the appendix. It becomes a liability if it enters the main paper claims or if it is framed as "external validation confirms." It does not confirm. Include it, be honest, and do not oversell it.

---

## 3. Q2-Now vs Q1-Later

**Decision: Q2-now. This is not a close call.**

The previous strategic review set the Q1 condition: "pattern partially replicates on UNSW-NB15 → Q1-path." The pattern did not partially replicate. The efficiency story fails in UNSW DoS. The BA-recovery story fails significance in UNSW Recon. The previous decision tree leads unambiguously to Q2-now.

The most important thing to understand is: **running more UNSW experiments will not help.** The reason results are non-significant in UNSW is not sample size (10 seeds is sufficient to detect the effect sizes seen in CICIDS2017) — it is that the effect sizes in UNSW are genuinely small. More seeds will shrink the CI but not move the point estimate. A BA difference of +0.001 will not become significant at 30 seeds; it will become significantly not-different-from-zero.

**Q1 path probability estimate after UNSW medium: 15-25%.** This is now lower than the 40-55% estimate before UNSW, because UNSW is adverse evidence, not neutral evidence.

**Q2 path probability estimate with current materials: 70-80%.** Unchanged. The CICIDS2017 story is still coherent and well-powered. UNSW in appendix with honest framing does not hurt Q2.

---

## 4. Should We Scale UNSW to 30 Seeds?

**No. Unambiguously no.**

The argument for scaling would be: "maybe with more power we'd find a significant effect." Let's test this with the actual point estimates.

**UNSW DoS — ZZ vs Energy (n_adaptations):**
- Point estimate: -0.4 adaptations (ZZ uses fewer — but this is in the right direction at least)
- CI at 10 seeds: [-0.9, 0.1]
- Approximate CI at 30 seeds (√3 scaling): [-0.74, -0.06] — this might become significant!

Wait — this is actually worth examining more carefully. The ZZ vs Energy adaptations difference in UNSW DoS is -0.4 (CI [-0.9, 0.1]), which barely misses significance. At 30 seeds it might cross.

BUT: ZZ has BA 0.844 vs Energy 0.846 in UNSW DoS. ZZ has **lower** mean BA. Even if it triggers fewer adaptations at 30 seeds, the BA result would be: "ZZ uses fewer adaptations but has lower BA." That is the opposite of the CICIDS efficiency story (tied BA, fewer adaptations). This is a meaningless result — fewer adaptations but worse performance is not an efficiency advantage.

The fundamental problem is not statistical power — it is that ZZ is last in BA in UNSW DoS. No amount of seeds fixes that.

**Verdict: do not scale UNSW to 30 seeds. Wasted compute with no chance of rescuing the Q1 story.**

---

## 5. Should We Improve the UNSW Protocol?

### 5a. One-hot proto/service/state?

**Not recommended.** Adding categorical features changes the feature space. This might help QK or hurt QK — direction unknown. If it helps: we've cherry-picked a preprocessing that makes QK look better on UNSW, which a reviewer will question. If it hurts: more time wasted. The current numeric-only preprocessing is clean and reproducible.

**Counter-argument:** Proto/service/state are important features in IDS. Not including them is a limitation of the UNSW preprocessing, not a choice to optimize QK. This is true. But it is a limitation to acknowledge, not an experiment to run.

### 5b. Generic/Exploits/Fuzzers instead of DoS/Recon?

**Not recommended.** These attack categories have no analog in CICIDS2017 scenarios. They can't be compared to anything in the main paper. Any result would be isolated and hard to interpret relative to the four-regime story. If QK does well in Generic — is that the efficiency pattern? The recovery pattern? We don't know. If QK does poorly — another negative result. Either way, it doesn't rescue the paper.

### 5c. Different reference/current construction?

**Not recommended.** The current construction (training set without the target attack as reference, testing set with Normal+attack as current) is methodologically sound and analogous to the CICIDS2017 approach. Changing it would require justification and might be seen as fishing.

### 5d. Attack recall/F1?

**Yes — but not for UNSW.** Adding attack recall or F1-attack to the CICIDS2017 tables pre-empts Reviewer Attack 7 (BA is not the right metric). This should be added before submission regardless of UNSW. It does not require any new experiments — it requires processing the existing raw CICIDS2017 results. Do this when writing Section 5.

### Summary: 5a/5b/5c = no. 5d = yes for CICIDS2017 tables.

---

## 6. Is Improving UNSW Worth the Risk of Experiment Sprawl?

**No. The risk of experiment sprawl is now the primary threat to the paper.**

Current experiment count:
- CICIDS2017: 4 attack scenarios × 30 seeds = done
- Benign controls: done
- Feature-map sensitivity: done
- RF expensive downstream: done
- UNSW DoS medium (10 seeds): done
- UNSW Reconnaissance medium (10 seeds): done

This is already 8 distinct experimental protocols. A reader (and a reviewer) who sees 8 protocols without a clear motivating question for each risks perceiving this as "throw everything at the wall." The storyline document correctly identified how to avoid this: present experiments in logical order, not chronological order.

Adding more UNSW experiments would make this 9 or 10 protocols. The marginal scientific value is zero or negative. The marginal risk to the narrative is real.

**The paper is done experimentally. The risk now is narrative clarity and timeline, not evidence.**

---

## 7. What Is the Strongest Paper We Can Write Now?

**A tight Q2 paper with 4 CICIDS2017 regimes as the main story and UNSW-NB15 as an honest appendix with mixed results.**

The structure is:

1. Introduction: the adaptive IDS readaptation problem, QK-MMD as a different operating point (not a quantum advantage claim), contributions as operational characterization
2. Related Work: drift detection, two-sample tests, quantum kernels, adaptive IDS
3. Method: QK-MMD (ZZ, PauliXZ), progressive readaptation protocol, metrics (BA, n_adaptations, adaptation_efficiency, actionable_utility), baselines
4. Experimental Protocol: CICIDS2017 (4 regimes), benign control, 30 seeds CI95, pre-registered sensitivity
5. Results: 5.1 AUC motivation, 5.2 4-regime table, 5.3 utility grid, 5.4 benign control
6. Discussion: efficiency/recovery dissociation, practitioner implications, utility framework as general contribution
7. Limitations: single primary dataset, UNSW mixed results (forward reference to appendix), runtime overhead, SVC-RBF only, classical simulation
8. Conclusion: honest, regime-dependent claim

Appendix A: Feature-map sensitivity  
Appendix B: RF expensive downstream  
Appendix C: UNSW-NB15 mixed external validation (honest framing — see Section 9 below)  
Appendix D (optional): Quantum circuit diagrams

This is a complete, honest, publishable paper. It does not overclaim. It does not underclaim. The contribution is the characterization framework and the four-regime evidence base.

---

## 8. Should We Stop Experiments and Start Writing?

**Yes. Stop experiments now. Start writing now.**

The longest outstanding risk to publication is not evidence — it is manuscript existence. The paper has zero words written. Four to six weeks of writing time minimum before a complete draft. Submission cannot happen until the draft exists.

Every week spent on experiments instead of writing is a week of delay with zero scientific upside given the current evidence base.

**Stop date for experiments: today.**  
**Start date for writing: today.**

The single permitted exception: processing attack recall and F1-attack columns from existing CICIDS2017 raw results (no new experiments, only table reformatting). This should be done during the writing phase, not as a separate experimental cycle.

---

## 9. UNSW-NB15 Appendix: Exact Framing

This appendix must be written carefully. The wrong framing is "external validation of our findings." The right framing is:

> **Appendix C: External Validation Attempt on UNSW-NB15**
>
> To assess the extent to which CICIDS2017 results generalize, we applied the paper 2 progressive readaptation protocol to UNSW-NB15 [cite], a publicly available IDS benchmark from a different institution, network environment, and attack taxonomy. We evaluated two scenarios (DoS and Reconnaissance) using all six detectors, 10 seeds, and 100 post-drift windows per seed. The preprocessing used numeric features only; categorical fields (proto, service, state) were excluded in this first external evaluation.
>
> Results were mixed. In UNSW DoS, KS-max and JSD achieved the highest mean balanced accuracy (0.854 and 0.852 respectively); QK-MMD ZZ ranked last (0.844, vs. no-adaptation baseline 0.840). No paired comparison between QK-MMD and Energy distance or MMD-RBF crossed the CI95 significance threshold in balanced accuracy or adaptation count. In UNSW Reconnaissance, QK-MMD ZZ achieved the highest mean BA (0.849) but was not significantly better than Energy distance (diff +0.001, CI [-0.003, 0.005]) or MMD-RBF (diff +0.002, CI [-0.002, 0.005]).
>
> We interpret these results as follows: UNSW DoS and Reconnaissance exhibit modest drift impact (maximum BA gain from adapting ≈ 0.014 and 0.003 respectively), compared to CICIDS2017 regimes (BA gain up to 0.144). In low-impact drift regimes where all detectors achieve similar adaptation frequency and downstream performance, fine-grained differences between detectors become statistically invisible. Whether QK-MMD advantages would replicate in more severe UNSW drift regimes, or with full categorical feature encoding, remains an open question. We report these results without modification as honest external evidence.

This framing:
- Does not claim replication
- Does not hide the negative results
- Provides the "mild drift" explanation without using it to dismiss the result
- Is honest enough to survive reviewer scrutiny

---

## 10. Final Title

**Primary recommendation:**

> Quantum-Kernel Drift Detection for Adaptive Network Intrusion Detection Systems: An Operational Characterization Across Attack Regimes

**Why:** Does not lead with the limitation. "Operational Characterization" correctly sets expectations — this is a study of operating points, not a superiority claim. "Attack Regimes" signals multi-scenario evaluation. It does not say "CICIDS2017-only" in the title, which is honest — the paper does include UNSW in appendix.

**Alternative (more cautious):**

> Regime-Dependent Operating Points of Quantum-Kernel MMD Detectors for Adaptive IDS Readaptation: Evidence from CICIDS2017 with Mixed External Validation

This alternative is more transparent but slightly unwieldy and signals weakness up front.

**Use the primary recommendation.**

---

## 11. Final Claim (One Sentence, Falsifiable)

> QK-MMD ZZ significantly reduces readaptation frequency by 1.8–2.1 episodes per 100 post-drift windows (CI95, 30 seeds) relative to Energy distance in CICIDS2017 volumetric/protocol attack regimes (Wednesday, DDoS) while maintaining statistically equivalent downstream balanced accuracy, at a 114× monitoring runtime overhead; this efficiency advantage does not hold in port-scan or application-layer attack regimes, and does not replicate with statistical significance on UNSW-NB15 DoS or Reconnaissance in the current evaluation.

Note: the last clause is new compared to the pre-UNSW claim. It is necessary. A reviewer who reads the UNSW appendix without seeing it acknowledged in the abstract or claim will flag it.

---

## 12. Revised Abstract

> Adaptive Network Intrusion Detection Systems (IDS) must periodically retrain their classifiers to handle distribution shift (concept drift). The drift trigger — the decision of when to retrain — determines the trade-off between retraining frequency, downstream classification performance, and monitoring overhead. Quantum-kernel Maximum Mean Discrepancy (QK-MMD) has been proposed as a drift detector with expressive feature-map geometry, but its operational behavior in adaptive IDS has not been empirically characterized.
>
> We evaluate QK-MMD (ZZ and PauliXZ feature maps) as an adaptive retraining trigger across four attack regimes from CICIDS2017: volumetric/protocol attacks (Wednesday, DDoS), port-scanning (PortScan), and application-layer attacks (WebAttacks). Our progressive drift protocol injects drift over 80 windows, evaluates 100 post-drift windows, and averages results over 30 random seeds with CI95 by paired bootstrap. We compare against Energy distance, MMD-RBF, KS-max, and JSD.
>
> In Wednesday and DDoS regimes, QK-MMD ZZ significantly reduces readaptation frequency by 1.8–2.1 episodes (CI95 strict) relative to Energy distance, at statistically equivalent downstream balanced accuracy and a 114× monitoring runtime overhead. In PortScan, the efficiency pattern inverts: QK-MMD ZZ triggers 1.4 more adaptations but achieves significantly higher downstream accuracy. In WebAttacks, QK-MMD PauliXZ achieves the highest mean balanced accuracy among all detectors but does not significantly outperform the strongest classical baselines (MMD-RBF, KS-max). A parametric utility framework (λ/γ/η) characterizes the operational conditions under which QK-MMD is preferable. QK-MMD does not reduce nuisance triggers on benign drift, and deeper feature maps (reps=2,3) do not improve operational performance. An external validation attempt on UNSW-NB15 (DoS, Reconnaissance) yields mixed, generally non-significant results, suggesting the regime-dependent advantages are not yet confirmed outside CICIDS2017. Our results characterize QK-MMD as defining attack-regime-dependent operating points rather than a universal improvement over classical drift detectors.

---

## 13. Main Paper vs Appendix

### Main paper

| Content | Section | Rationale |
|---|---|---|
| AUC by severity (controlled streaming) | 5.1 | Motivates different trigger timing |
| 4-regime progressive readaptation (30 seeds) | 5.2 | Primary evidence |
| CI95 paired table (all regimes × methods) | 5.2 | Statistical rigor |
| Utility grid λ/γ/η (Wednesday) | 5.3 | Methodological contribution |
| Benign nuisance control | 5.4 | Honest negative control |
| Attack recall / F1-attack rows | 5.2 extended | Pre-empts metric criticism |

### Appendix

| Content | Appendix | Rationale |
|---|---|---|
| Feature-map sensitivity (ZZ/PauliXZ reps 1–3) | A | Robustness check, pre-registered |
| RF expensive downstream (negative) | B | Honest negative: runtime balance |
| UNSW-NB15 mixed external validation | C | Honest external attempt, mixed results |
| Quantum circuit diagrams (optional) | D | Technical reference |

### Not in paper

| Content | Reason |
|---|---|
| Adaptive monitor | Superseded |
| Long-stream single-change | Superseded |
| Hybrid OR combination | Negative, no useful story |
| Geometry diagnostics | Speculative |
| Operational scale proxy | Motivated reasoning, not experimental |

---

## 14. Q1 Reviewer Attack Simulation (Updated for UNSW)

### Pre-existing attacks (unchanged responses from prior review)

Attack 1 (single dataset), Attack 2 (runtime overhead), Attack 3 (PortScan inversion), Attack 4 (feature map cherry-picking), Attack 5 (WebAttacks weakness), Attack 6 (Energy distance as primary baseline), Attack 7 (BA metric) — all responses from the prior strategic review remain valid.

### New attack: UNSW results are negative, undermining generalization

**Reviewer:** "The authors include UNSW-NB15 in the appendix and acknowledge mixed results. However, the actual data shows that in UNSW DoS, QK-MMD ZZ ranked last among all detectors — behind even the no-adaptation baseline in the direction of mean BA — and that KS-max and JSD, the cheapest possible classical detectors, achieved the best mean BA. This is not 'mixed' — it is a negative result. The conclusion that QK-MMD defines meaningful operating points cannot be sustained if the pattern fails to replicate on any external dataset."

**Response:** "We agree the UNSW DoS result for QK-MMD ZZ is adverse. We report it without modification in Appendix C and acknowledge it as the primary external limitation of this work. We do not claim external generalization. We note that UNSW DoS and Reconnaissance exhibit substantially smaller drift impact than the CICIDS2017 scenarios (maximum BA gain from adaptation ≈ 0.014 and 0.003 vs. up to 0.144 in CICIDS2017). In low-impact regimes where the gain from adapting is small, all detectors produce similar behavior because the adaptation signal itself is weak — this is a property of the scenario, not specific to QK-MMD. We label this as an open question for future work: whether QK-MMD advantages emerge on external datasets under more severe drift conditions. The primary contribution of this paper is the four-regime characterization within CICIDS2017 and the operational utility framework, not a generalization claim."

**Risk level:** This response will satisfy a Q2 reviewer if the limitations section is strong. It will not satisfy a Q1 reviewer at TDSC or TIFS, who will ask for a second dataset where the pattern DOES replicate before accepting. This is the correct target for the venue choice: Q2.

### New attack: 10 seeds is insufficient for UNSW — results are underpowered

**Reviewer:** "The UNSW experiments use only 10 seeds while the CICIDS2017 results use 30 seeds. Results claiming to be 'mixed' may simply be underpowered."

**Response:** "We note that statistical power is not the limiting factor for the UNSW null results. The point estimates in UNSW DoS show QK-MMD ZZ ranked last in mean BA among all detectors (0.844 vs. Energy 0.846) — more seeds would narrow the CI but would not change the direction of this mean-level result. Similarly, in UNSW Reconnaissance, the point estimate for QK-MMD ZZ vs Energy distance in BA is +0.001 — an effect size approximately 6× smaller than the CICIDS2017 PortScan effect (+0.006) that reached significance at 30 seeds. Scaling to 30 seeds would sharpen the null result, not reverse it. We report these 10-seed results as the first external evaluation attempt, acknowledging they do not have the same statistical power as the primary CICIDS2017 analysis."

---

## 15. Next Actions (Strict Priority Order)

### Stop immediately

- No new UNSW experiments (not 30 seeds, not categorical features, not new attack categories)
- No new CICIDS2017 experiments
- No geometry diagnostics
- No feature engineering experiments

### This week (writing phase begins)

1. **Write Section 3 (Method)** — most mechanical, does not require final results. Estimated: 3–4 pages, 2–3 days.
   - QK-MMD definition (ZZ, PauliXZ feature maps, kernel, statistic)
   - Progressive readaptation protocol
   - Metrics (BA, n_adaptations, adaptation_efficiency, actionable_utility)
   - Baselines

2. **Write Section 4 (Experimental Protocol)** — CICIDS2017 description, 4 regimes, benign control, 30 seeds, CI95 design, pre-registration. Estimated: 2 pages, 1–2 days.

3. **Add attack recall / F1-attack columns** to the CICIDS2017 summary table. Process existing raw results. No new experiments. Pre-empts Reviewer Attack 7 during the writing phase.

### Within 2 weeks

4. **Write Section 5 (Results)** from existing tables. The tables already exist in CSV — work is formatting for publication and writing the accompanying text. Estimated: 6–8 pages, 4–5 days.

5. **Write Appendix C (UNSW)** using the exact framing from Section 9 of this review. Estimated: 1–2 pages, 1 day.

6. **Write Section 7 (Limitations)** — this section must be proactively strong. Write it before Section 6. Estimated: 1 page, 1 day.

### Within 4 weeks

7. **Write Section 6 (Discussion)** — interpret the efficiency/recovery dissociation, practitioner implications, utility framework as contribution.

8. **Write Appendix A (feature-map sensitivity)** — concise, from existing tables.

9. **Write Appendix B (RF expensive downstream)** — negative result, honest framing.

### Within 6 weeks

10. **Write Section 1 (Introduction) last** — after the rest is stable. The introduction must reflect the actual story, not the hoped-for story.

11. **Write Section 2 (Related Work)** — can be parallelized with any section.

12. **Write Section 8 (Conclusion)** — after introduction is drafted.

13. **First complete draft → internal review.**

### Do not

- Write the introduction first
- Run any experiments before first draft exists
- Change the venue target to Q1 based on UNSW results

---

## 16. Summary Assessment

| Dimension | Before UNSW | After UNSW | Action |
|---|---|---|---|
| Story coherence | B+ | B | CICIDS story unchanged; UNSW goes to appendix, not main |
| Statistical rigor | A | A | Unchanged |
| Claim precision | B+ | B | Tighten abstract to acknowledge UNSW null |
| Attack diversity | B (4 regimes, 1 dataset) | B (4 regimes, 1 dataset, 1 appendix dataset) | Unchanged — UNSW doesn't improve attack diversity claim |
| External generalization | F (none) | D (mixed, no replication) | Honest appendix |
| Honest negatives | A | A | UNSW adds to honest negatives |
| Manuscript readiness | C | C | Start writing |
| Q2 readiness | Ready | Ready | Write paper |
| Q1 readiness | Conditional on UNSW | Not viable | Abandon Q1 path |

**Bottom line:** UNSW medium closed the Q1 path. Q2 is the correct target. The CICIDS2017 story is unchanged and still publishable. The paper needs to be written, not extended. Start writing today.
