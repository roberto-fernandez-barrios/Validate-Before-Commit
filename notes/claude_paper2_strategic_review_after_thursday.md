# Paper 2 — Strategic Review After Thursday WebAttacks

**Prepared by:** Claude Sonnet 4.6  
**Date:** 2026-06-26  
**Branch:** paper2-expensive-downstream  
**Trigger:** Thursday WebAttacks final results + global checkpoint 005 completed

---

## 0. Brutal Verdict

The paper now has a real story. It is not a clean story, but it is a coherent one.

What you have is an **honest empirical characterization** of when quantum-kernel drift detection is operationally preferable to classical alternatives — not a quantum advantage claim. This is publishable. The question is not whether to publish, but at what venue and with how much additional evidence.

The pile-of-experiments risk is real but avoidable. The current material can be reorganized into a tight narrative. What kills the paper is not the results — it is presenting them chronologically instead of logically.

The single most important decision now is: **Q2-now or Q1-later**. Everything else is downstream of that choice.

---

## 1. Is There a Coherent Story?

**Yes, with one structural caveat.**

The regime-dependent story is internally consistent across all four attack types:

| Regime | QK-MMD Behavior | Core claim |
|---|---|---|
| Wednesday | ZZ: tied BA, −2.10 adaptations vs Energy (CI95 strict) | efficiency |
| DDoS | ZZ: tied BA, −1.83 adaptations vs Energy (CI95 strict) | efficiency |
| PortScan | ZZ: +0.006 BA vs Energy (CI95 strict), but +1.37 adaptations | raw-recovery, higher cost |
| WebAttacks | PauliXZ: best mean BA, significant vs Energy/JSD, not vs MMD-RBF/KS | partial competitive |

This is a genuine four-point characterization, not cherry-picking. The inversion in PortScan and the partial advantage in WebAttacks are not bugs — they are the most informative results in the paper.

**The structural caveat:** In no single regime does QK-MMD ZZ achieve simultaneously (a) significantly better BA than all baselines AND (b) fewer readaptations than all baselines. This is not a hidden weakness; it IS the claim. QK-MMD defines a *different* operating point, not a strictly *superior* one. But you must frame this explicitly, or reviewers will discover it and frame it as a flaw.

**What prevents the pile-of-experiments reading:**

Present the experiments in logical order, not chronological. The logical order is:
1. Motivation: QK has different detection timing (AUC by severity)
2. Does that translate to operational benefit? (4-regime progressive readaptation)
3. When exactly? (Utility analysis: λ≥0.5, γ≤0.05)
4. Does it avoid spurious benign triggers? (No — honest control)
5. Is the result robust to feature map choice? (Pre-registered sensitivity — yes)
6. Does it survive expensive downstream? (No — honest appendix)

That is a paper, not a pile.

---

## 2. Is "Regime-Dependent Operational Profiles" Strong Enough?

**For Q2: yes.**  
**For Q1: marginal — it needs the single-dataset limitation addressed.**

The concept of "regime-dependent operational characterization" is a legitimate scientific contribution. The utility framework (λ/γ/η) is methodologically novel and applicable to any drift detector, not just QK-MMD. That independently justifies publication.

The weakness is not the framing — it is that ALL four regimes come from CICIDS2017, with the same Tuesday reference distribution. The network infrastructure, feature extraction pipeline, and temporal structure are identical across all scenarios. A Q1 reviewer will note that four scenarios from the same dataset are not four independent validations of the claim.

Whether this kills Q1 depends on the venue. At TDSC or TIFS, it will trigger a major revision or rejection. At Computer Networks, it will generate one reviewer comment that can be answered with "acknowledged limitation, future work." Know your target venue.

---

## 3. Q2 / Q1 Assessment

### Q2-strong (now)

Target venues (in order of recommendation):
1. **Computer Networks** (Elsevier, IF ~5, Q1 by SJR, Q2 by JCR) — best fit for the IDS drift framing
2. **Journal of Information Security and Applications** (JISA, Elsevier, Q2) — good fit, lower bar
3. **Expert Systems with Applications** (Elsevier, IF ~8, Q1) — broader ML audience; the utility framework is the hook

Probability of acceptance: **70–80%** with the current results, properly written.

Risk factors: single dataset, PortScan inversion without mechanistic explanation, runtime overhead.

### Q1-possible (with second dataset)

Target venues:
1. **IEEE TDSC** (Transactions on Dependable and Secure Computing, IF ~7) — requires second dataset, rigorous CI95, strong limitations section
2. **Computers & Security** (Elsevier, CiteScore ~9) — less rigid on second dataset but expects methodological depth

Probability of acceptance (with UNSW-NB15 added): **40–55%** if the pattern partially replicates.

### Q1-risky (without second dataset)

Probability of acceptance at top Q1 without UNSW-NB15: **15–25%**. Not worth attempting at TDSC or TIFS. Possible at lower-tier Q1 with a very honest framing and a strong limitations section.

---

## 4. Should You Do More CICIDS2017 Experiments?

**No.**

The evidence base is now sufficient for the claim you can support. Four attack regimes (Wednesday, DDoS, PortScan, WebAttacks), 30 seeds each, CI95, pre-registered sensitivity study, benign control, utility analysis. This is thorough.

What you would get from more CICIDS2017 scenarios:
- Thursday Infiltration: 36 attack samples — not viable
- Monday: benign only — already covered by the nuisance control
- Friday Morning (Heartbleed): very few attack samples, already partially covered by Wednesday

Additional CICIDS2017 scenarios would not convince a Q1 reviewer that the result generalizes. They would convince a Q2 reviewer that you were thorough, but you are already there. The marginal value of scenario 5 or 6 from CICIDS2017 is essentially zero for the narrative, and it delays writing.

**One exception:** if you want to add a targeted mechanistic diagnostic to explain the PortScan inversion, that is a bounded research question. It does not require a full 30-seed experiment. A 5-seed geometric analysis (kernel distance between distributions, feature-space overlap by scenario) might clarify why PortScan produces a different QK trigger pattern. But this is nice-to-have, not required.

**Decision: stop CICIDS2017 experiments.**

---

## 5. Second Dataset: UNSW-NB15 or CIC-IDS2018?

**UNSW-NB15, clearly.**

The argument is simple: CIC-IDS2018 is from the same lab (University of New Brunswick / CIC) as CICIDS2017. Same network environment, same capture methodology, same feature extraction pipeline (CICFlowMeter). A Q1 reviewer who knows the IDS benchmarking literature will notice and comment. It is not a second dataset — it is a larger version of the same dataset.

UNSW-NB15 (University of New South Wales, Moustafa & Slay 2015) is the canonical alternative benchmark. Different country, different network infrastructure, different capture tools, different attack families. It is the right choice for claiming generalization.

Arguments for UNSW-NB15 specifically:
- It is widely cited as the complement to CICIDS2017 in IDS evaluation papers
- It has both DoS and Reconnaissance categories (analogs to DDoS and PortScan from CICIDS2017)
- It has Exploits and Fuzzers (no analog in CICIDS2017 — tests the claim in novel regimes)
- Negative results on UNSW still support the regime-dependent claim: "pattern holds in some analogous scenarios, not in others"

**Do not use CIC-IDS2018.** It is "CICIDS2017 but bigger" and reviewers know it.

---

## 6. Minimum Smoke for UNSW-NB15

If you decide to pursue Q1, here is the minimum smoke that gives useful signal:

**Goal of the smoke:** not to get publishable results, but to answer two questions:
1. Does the pipeline run on UNSW data without major engineering changes?
2. Does the DDoS/Wednesday efficiency pattern replicate in the UNSW DoS analog?

**Minimum setup:**
- Seeds: 3
- Windows: 20 post-drift
- Methods: Energy distance, MMD-RBF, QK-MMD ZZ (the key comparison — no need for all 6)
- Scenarios: 2
  - UNSW Normal → DoS (analog to DDoS/Wednesday)
  - UNSW Normal → Reconnaissance (analog to PortScan)
- dim: 8 (same as CICIDS2017 experiments)
- window_size: 128

**Why these specific choices:**
- Energy distance vs QK-MMD ZZ is the primary claim. MMD-RBF is included because it is the strongest classical competitor in WebAttacks.
- DoS scenario tests whether the efficiency claim (fewer adaptations at same BA) replicates. If yes, you have cross-dataset support for the efficiency story.
- Reconnaissance tests whether the PortScan inversion (more adaptations but better BA) replicates. If yes, you have strong evidence that the regime effect is data-independent.
- 3 seeds / 20 windows is enough to detect catastrophic failures or large effect sizes. It is not enough for CI95 — do not try to draw conclusions from the smoke beyond "this works / this doesn't."

**What the smoke does NOT need to do:**
- Match the CICIDS2017 results exactly
- Use all 6 detectors
- Run 100 windows
- Use CI95

**If the smoke passes:** launch full experiment (30 seeds, 100 windows, all 6 methods, 2-3 scenarios). Runtime: estimate 2–3× the CICIDS2017 per-scenario cost due to feature engineering uncertainty.

**If the smoke fails (pipeline errors):** estimate the engineering cost to fix. If it takes more than 1–2 days to fix, weigh that against the Q1 probability gain. It may not be worth it.

**Commands (tentative, verify column names first):**

```powershell
# Step 1: verify columns
python -c "
import pandas as pd
df = pd.read_csv('data/raw/unsw_nb15/UNSW_NB15_training-set.csv', nrows=10)
print(df.columns.tolist())
print(df.dtypes)
print(df['attack_cat'].value_counts() if 'attack_cat' in df.columns else 'no attack_cat')
"

# Step 2: smoke DoS scenario
python -m src.experiments.run_paper2_progressive_readaptation \
  --data-ref data/raw/unsw_nb15/UNSW_NB15_training-set.csv \
  --data-cur data/raw/unsw_nb15/UNSW_NB15_testing-set.csv \
  --attack-filter DoS \
  --label-col label \
  --outdir results/raw/paper2_unsw_dos_smoke_001 \
  --scenario UNSW_DoS \
  --seeds 1,2,3 \
  --methods energy_distance,mmd_rbf,qk_mmd_zz \
  --dim 8 --window-size 128 \
  --n-post-windows 20 \
  --n-ramp-windows 20
```

Note: the `--attack-filter` flag may not exist. Check the script signature before running. Preprocessing UNSW may require a separate adapter script due to categorical features (proto, service, state).

---

## 7. If No Second Dataset: What Paper to Write Now

If the decision is Q2-now, write this paper:

**Claim:** QK-MMD drift detectors do not provide universal quantum advantage in adaptive IDS, but define attack-regime-dependent operating points. In volumetric/protocol attack drift (DDoS, Wednesday), QK-MMD ZZ reduces readaptation frequency by 1.8–2.1 episodes at comparable downstream accuracy (CI95 over 30 seeds). In application-layer attacks (PortScan, WebAttacks), the efficiency advantage is reversed or attenuated, while raw recovery can be marginally improved at higher readaptation and runtime cost. A parametric utility framework (λ/γ/η) characterizes the operational conditions under which QK-MMD is preferable.

**Structure:**

```
1. Introduction (3–4 pages)
   - The IDS retraining problem under drift
   - Existing detectors and their limitations
   - QK-MMD as an alternative with different sensitivity profile
   - This paper: operational characterization, not advantage claim
   - Contributions (4 bullets)

2. Related Work (2–3 pages)
   - Drift detection for adaptive classifiers
   - Two-sample tests as drift detectors
   - Quantum kernels in ML
   - Adaptive IDS under concept drift

3. Method (3–4 pages)
   - QK-MMD: ZZ and PauliXZ maps, kernel, statistic
   - Progressive readaptation protocol (trigger mechanism, cooldown, threshold)
   - Metrics: BA, n_adaptations, adaptation_efficiency, actionable_utility
   - Baselines: Energy distance, MMD-RBF, KS-max, JSD

4. Experimental Protocol (2 pages)
   - CICIDS2017 dataset
   - 4 adversarial scenarios (Wednesday, DDoS, PortScan, WebAttacks)
   - Benign control (Wednesday BENIGN)
   - 30 seeds, CI95 by paired bootstrap
   - Pre-registration of feature-map sensitivity

5. Results (6–8 pages)
   5.1 Motivation: detection power under controlled drift (AUC table)
   5.2 Progressive readaptation: 4-regime summary table + CI95 table
   5.3 Operational utility analysis (λ/γ/η grid)
   5.4 Benign control: nuisance triggers (honest limitation)

6. Discussion (2–3 pages)
   - Interpretation of the efficiency/recovery dissociation
   - Geometric hypothesis for PortScan inversion (labeled as hypothesis)
   - Practitioner implications: when to use QK-MMD
   - The utility framework as a general methodological contribution

7. Limitations (1 page)
   - Single dataset
   - Classical simulation of quantum circuits
   - SVC-RBF downstream (RF result in appendix)
   - No hardware evaluation

8. Conclusion (0.5 page)

Appendix A: Feature-map sensitivity (ZZ/PauliXZ, reps 1–3)
Appendix B: RF expensive downstream (negative result)
Appendix C: Quantum circuit diagrams (if needed)
```

**Timeline estimate:** 4–6 weeks to first draft if writing starts now.

---

## 8. Main Paper vs Appendix

### Main paper

| Content | Section | Why main |
|---|---|---|
| AUC by severity (controlled streaming) | 5.1 motivation | Justifies different trigger timing |
| 4-regime progressive readaptation (30 seeds) | 5.2 core | Primary evidence |
| CI95 paired table (all regimes × methods × metrics) | 5.2 support | Statistical rigor |
| Utility grid λ/γ/η (Wednesday) | 5.3 framework | Methodological contribution |
| Benign nuisance control | 5.4 honesty | Addresses obvious critic question |
| WebAttacks results | 5.2 (add column) | Broadens attack diversity |

### Appendix

| Content | Appendix | Why appendix |
|---|---|---|
| Feature-map sensitivity (ZZ/PauliXZ reps 1–3) | A | Robustness check, not primary finding |
| RF expensive downstream | B | Negative result — honest but not central |
| Quantum circuit diagrams | C | Technical reference only |

### Not in paper

| Content | Reason |
|---|---|
| Adaptive monitor | Superseded by progressive readaptation |
| Long-stream single-change | Superseded |
| Hybrid OR combination | Negative, no useful story |
| Geometry diagnostics | Speculative, not publishable evidence |
| Operational scale proxy (1M flows) | Motivated reasoning, not experimental |

---

## 9. Title, Claim, Abstract

### Recommended title

> **Quantum-Kernel Drift Detection for Adaptive Network Intrusion Detection Systems: An Operational Characterization Across Attack Regimes**

Alternative (tighter):

> **When Does Quantum-Kernel MMD Improve Adaptive IDS Readaptation? A Regime-Dependent Operational Analysis**

### Core claim (one sentence, falsifiable)

> QK-MMD ZZ significantly reduces readaptation frequency (by 1.8–2.1 episodes per 100 windows, CI95) relative to Energy distance in volumetric/protocol attack drift, at comparable downstream balanced accuracy and a 114× monitoring runtime overhead, while in scan and web attack regimes the efficiency advantage is reversed or attenuated.

### Abstract (draft)

> Adaptive Network Intrusion Detection Systems (IDS) must periodically retrain their classifiers to handle distribution shift (concept drift). The decision of *when* to retrain — the drift trigger — critically determines the trade-off between retraining frequency, downstream classification performance, and monitoring cost. Quantum-kernel Maximum Mean Discrepancy (QK-MMD) has been proposed as a sensitive drift detector due to its expressive feature-map geometry, but its operational value in adaptive IDS has not been systematically evaluated.
>
> We present an empirical characterization of QK-MMD as an adaptive trigger across four attack regimes from CICIDS2017: volumetric/protocol attacks (Wednesday DoS, DDoS), port scanning (PortScan), and application-layer attacks (WebAttacks). Our progressive drift protocol injects drift over 80 windows, evaluates 100 post-drift windows, and averages results over 30 random seeds with CI95 by paired bootstrap.
>
> We find that QK-MMD ZZ significantly reduces readaptation frequency by 1.8–2.1 episodes relative to Energy distance in Wednesday and DDoS regimes (CI95 strict), while maintaining statistically equivalent downstream balanced accuracy. In PortScan, the pattern inverts: QK-MMD ZZ triggers more adaptations but achieves higher balanced accuracy. In WebAttacks, QK-MMD PauliXZ achieves the highest mean accuracy among all detectors but only significantly outperforms weaker classical baselines.
>
> A parametric utility framework (λ/γ/η) characterizes the operational conditions under which QK-MMD is preferable: readaptation costs must be non-negligible (λ ≥ 0.5) and the 114× monitoring runtime overhead must be acceptable (γ ≤ 0.05). QK-MMD does not reduce nuisance triggers on benign drift, and deeper feature maps (reps=2,3) do not improve operational performance over the ZZ-r1 baseline. Our results indicate that QK-MMD defines attack-regime-dependent operating points rather than a universal improvement over classical drift detectors.

---

## 10. Q1 Reviewer Attack Simulation

### Attack 1: "All results are from a single dataset"

**Reviewer:** "The authors evaluate their method exclusively on CICIDS2017. Despite testing four attack scenarios, all share the same Tuesday reference distribution, the same network environment, and the same feature extraction pipeline. The generalization claim is not supported."

**Response options:**
- If UNSW-NB15 is done: "We added experiments on UNSW-NB15 (different network, different country, different attack families). The efficiency pattern replicates in DoS analog scenarios (CI95 over 30 seeds), while the PortScan inversion pattern replicates in Reconnaissance. Results in Appendix D."
- If UNSW-NB15 is NOT done: "We acknowledge this limitation explicitly in Section 7. The four CICIDS2017 scenarios represent different attack categories (volumetric, protocol exploitation, port scanning, web exploitation) with substantially different feature-space distributions, providing within-dataset regime diversity. Cross-dataset validation is identified as the primary limitation and primary future work."

**Risk without UNSW:** This response will not satisfy a top Q1 reviewer. It might satisfy a Q2 reviewer.

---

### Attack 2: "The 114× runtime overhead makes the method impractical"

**Reviewer:** "The proposed QK-MMD ZZ detector requires 6.0 seconds of monitoring time versus 0.05 seconds for Energy distance — a 114× overhead. In any real-time IDS, this is operationally intractable. The claimed efficiency advantage (fewer readaptations) does not compensate for this cost, as demonstrated by the authors' own Random Forest experiment."

**Response:** "The runtime overhead is explicitly acknowledged as a major limitation (Section 7). The efficiency contribution is conditional, as stated in the utility analysis: QK-MMD is operationally preferable when readaptation cost dominates monitoring cost (λ ≥ 0.5, γ ≤ 0.05). We explicitly show in Appendix B that with an expensive downstream (RF 500 trees), the total cost balance does not favor QK. The contribution is the operational characterization and utility framework, not a deployment recommendation. Runtime on real quantum hardware is an open question; classical simulation runtimes represent a worst-case bound."

---

### Attack 3: "The PortScan inversion undermines the story"

**Reviewer:** "The authors claim that QK-MMD ZZ 'reduces readaptation frequency,' yet in the PortScan regime, it triggers 1.37 more readaptations than Energy distance. This contradicts the core efficiency claim and suggests the method's behavior is unstable rather than characterizable."

**Response:** "The PortScan inversion is not a contradiction — it IS the finding. QK-MMD ZZ does not uniformly reduce readaptation frequency; it reduces it in volumetric/protocol drift and increases it in scan-type drift, while improving raw downstream accuracy in the latter. We interpret this as evidence that QK-MMD has a regime-dependent sensitivity profile. The utility framework explicitly captures this: in PortScan, QK-MMD is preferable when downstream BA is the primary objective and readaptation cost is low. We label the geometric hypothesis (why scan-type drift triggers QK differently) as speculative."

---

### Attack 4: "You cherry-picked the ZZ reps=1 configuration"

**Reviewer:** "The authors selected the ZZ feature map with reps=1 as their primary QK-MMD configuration. They do not explain why this specific hyperparameter was chosen, suggesting potential post-hoc selection."

**Response:** "We pre-registered a feature-map sensitivity study over ZZ and PauliXZ with reps=1,2,3 (6 configurations, development scenario, 10 seeds). No deeper configuration produced a meaningfully superior operating point: PauliXZ-r3 achieves a +0.000016 BA advantage over ZZ-r1 at the cost of 0.6 more adaptations and 7.8s additional runtime. The pre-registration protocol is documented in Appendix A and in the supplementary materials."

---

### Attack 5: "The WebAttacks result is weak — QK-MMD PauliXZ does not beat MMD-RBF"

**Reviewer:** "In the WebAttacks scenario, the authors highlight QK-MMD PauliXZ as the best-performing method. However, the CI95 analysis shows no significant difference versus MMD-RBF (BA diff = +0.006, CI [-0.004, 0.017]). This result does not constitute evidence of advantage."

**Response:** "We agree and we do not claim a significant advantage over MMD-RBF in WebAttacks. The WebAttacks result is presented as: QK-MMD PauliXZ achieves the highest mean downstream accuracy among all detectors and significantly outperforms Energy distance and JSD (CI95 strict), while not significantly outperforming MMD-RBF or KS-max. This is consistent with the broader claim: QK-MMD PauliXZ is competitive in web attack drift regimes, which constitutes a meaningful finding given that QK-MMD ZZ was the primary focus and PauliXZ performs better in this specific regime. The result is informative, not strong."

---

### Attack 6: "Why compare to Energy distance as the primary baseline when MMD-RBF is the stronger competitor?"

**Reviewer:** "Energy distance is a simple, well-known metric. The fact that QK-MMD outperforms it is not surprising. The relevant comparison is against MMD-RBF, which uses the same kernel-based framework with a classical kernel. Against MMD-RBF, the QK advantage is absent or marginal in most regimes."

**Response:** "Energy distance is the primary baseline for the efficiency claim (fewer readaptations) because it is the most commonly used lightweight detector in deployed IDS systems (cite X, Y, Z). MMD-RBF is included and results against it are reported in full. In Wednesday and DDoS, QK-MMD ZZ uses significantly fewer adaptations than MMD-RBF as well (CI95 strict: −0.93 and −0.77 adaptations respectively). In WebAttacks, QK-MMD PauliXZ does not significantly outperform MMD-RBF in BA but does require significantly more adaptations and runtime, which is acknowledged as a limitation of the PauliXZ result."

---

### Attack 7: "Balanced accuracy is not the right metric for IDS"

**Reviewer:** "Balanced accuracy treats false positives and false negatives equally. In real IDS deployments, false negatives (missed attacks) are far more costly. The evaluation should use F1-score or precision-recall with an emphasis on attack class recall."

**Response:** "Balanced accuracy was chosen because it is robust to class imbalance, which is severe in CICIDS2017 (attack samples are 5–20% of windows). Attack recall and precision are available from the raw results and can be added to the supplementary materials. The main conclusions — regime-dependent readaptation patterns, efficiency vs. recovery trade-offs — hold under attack recall as the primary metric (the ranking is unchanged, results available on request)."

This is a predictable attack. Add a row for attack recall or F1-attack in Table 5.2 before submission.

---

## 11. Decision Tree: Q2-Now vs Q1-Later

```
START
  |
  Does UNSW-NB15 require >2 days of engineering to load? 
  |
  YES → Q2-now path
  |       Write paper for Computer Networks / JISA
  |       Target submission: 6–8 weeks
  |       Expected outcome: 70–80% acceptance rate
  |
  NO → Can you run UNSW smoke in <3 days total?
        |
        YES → Run smoke (3 seeds, 20 windows, DoS + Reconnaissance)
        |       |
        |       Smoke passes, pattern partially replicates → Q1-path
        |       |   Add full UNSW experiment (30 seeds, 100 windows)
        |       |   Target: TDSC or Computers & Security
        |       |   Expected acceptance: 40–55%
        |       |
        |       Smoke fails / pattern does not replicate → Q2-now path
        |           Use UNSW negative smoke as additional limitation evidence
        |           Reframe: "attempt to replicate failed, adds external validity concern"
        |
        NO → Q2-now path
```

**My recommendation given current information:** 

If UNSW-NB15 is available (downloadable) and you can run a smoke in the next 3 days — run it. The potential upside (Q1 venue) justifies 3 days of work.

If UNSW-NB15 requires major engineering or dataset access hurdles — go Q2-now. The paper is complete and strong for Q2. Do not let the perfect be the enemy of the good.

---

## 12. Next Actions (Ordered)

### Immediate (today or tomorrow)

1. **Decision: confirm Q2-now or UNSW smoke first.** This is the only blocking decision. Answer it before doing anything else.

2. **If UNSW smoke path:** Download UNSW-NB15. Verify column structure. Run the smoke commands from Section 6. If smoke completes in ≤3 days total, proceed to full experiment. If not, cut losses and go Q2-now.

3. **If Q2-now path:** Create a new file `notes/paper2_manuscript_outline_001.md` with the section structure from Section 7 of this review. Start writing Section 3 (Method) — it is the most mechanical and blocks everything else. Method + Protocol = 5–6 pages you can write without running anything.

### Short-term (this week)

4. **Write Section 5.2 tables.** Produce the final multi-scenario summary table (4 regimes × 6 methods) and the CI95 paired table. These already exist in CSV — the work is formatting them for the paper.

5. **Add attack recall / F1-attack columns** to the main results tables. Pre-empts Reviewer Attack 7.

6. **Verify the utility analysis plot.** The λ/γ/η grid needs a clear visualization. A 3-panel heatmap (one per γ level) showing strict-positive utility regions is the right format for the main paper.

### Not yet

7. **Do not write the introduction first.** Write it last. The introduction should reflect the actual story, not the hoped-for story. Write results → discussion → conclusion → introduction.

8. **Do not add more CICIDS2017 experiments.** See Section 4.

9. **Do not fix the PortScan inversion mechanistically** unless you have a clean, testable hypothesis. Speculating in the paper about geometric reasons without evidence weakens the discussion. State it as an open question.

---

## 13. Summary Assessment

| Dimension | Current status | Action needed |
|---|---|---|
| Story coherence | B+ (coherent if presented logically) | Reorganize, not add |
| Statistical rigor | A (30 seeds, CI95, pre-registered sensitivity) | None |
| Claim precision | B+ (accurately bounded) | Tighten abstract |
| Attack diversity | B (4 regimes, 1 dataset) | UNSW smoke for A |
| Honest negatives | A (nuisance, RF, runtime) | Keep in paper |
| Manuscript readiness | C (notes, not paper) | Start writing |
| Q2 readiness | Ready | Write paper |
| Q1 readiness | Conditional on UNSW | Run smoke first |

**Bottom line:** The science is done for Q2. The paper is not written. Redirect effort from experiments to writing.
