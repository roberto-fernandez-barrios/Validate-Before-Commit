# Paper 2 — Manuscript Skeleton (phenomenon-framed, ready to write)

**Prepared by:** Claude (Opus 4.8)
**Date:** 2026-07-01
**Purpose:** Turn the recommended Route-1 story into a section-by-section writing guide. For each section: its narrative beat, the exact table/figure with source path, the key numbers to state, and draft bridge prose you can lift directly.
**Companion notes:** `claude_paper2_final_salvage_review_001.md` (decision), `paper2_storyline_001.md` (earlier structure to cannibalize).

**Spine (put on a sticky note):**
> Drift detectors answer *"did the distribution change?"*; adaptive IDS needs *"will retraining improve the classifier?"*. These are different questions. The gap between them makes drift-triggered readaptation range from strongly beneficial to actively harmful — and it is invisible to the detector, classical or quantum.

**Number-provenance legend:**
- ✅ = verified against the CSV in this session.
- 📄 = stated in checkpoint notes, re-verify against the raw CSV before it goes in the PDF.
- ⧗ = artifact must be computed/assembled from existing raw data (no new experiment).

Write **Results → Discussion → Conclusion → Intro** last. The intro must reflect the story you actually tell.

---

## Figure & table inventory (build these first)

| ID | Type | Content | Source artifact | Beat |
|---|---|---|---|---|
| **Fig 1** | Bar chart (the money figure / hook) | Gain vs no-adaptation for every dataset×regime, colored by sign (green=benefit, grey=marginal, red=harm); BA and attack-F1 | ✅ **built** `results/tables/paper2_metrics_ba_f1_summary_001/paper2_fig1_regime_spectrum.csv` | 3 (teaser in Intro) |
| Fig 2 | Scatter | Per-detector operating points on CICIDS: mean BA (y) vs n_adaptations (x), one panel per regime | `paper2_progressive_multi_scenario_cicids_001/` + `..._thursday_webattacks_final_001/` | 2 |
| **Fig 3** | Scatter/bar | **Decision-oracle regret vs harm-frequency** per regime (monotone) — the actionability-gap figure | ✅ `results/tables/paper2_oracle_regret_decision_001/` (built 2026-07-01) | 4 |
| Fig 4 | Pareto scatter | Gain vs adaptations per policy (Phase 1), naive & no-adapt & oracle marked; safe policies do NOT dominate | `paper2_safe_readaptation_phase1_001/paper2_phase1_all_policy_method_summary.csv` | 5 |
| Table 1 | Summary | CICIDS 4 regimes × 6 detectors: **BA + attack-F1**, gain, n_adapt, detector runtime | ✅ BA+F1 `paper2_metrics_ba_f1_summary_001/paper2_ba_f1_by_regime_method.csv`; runtime/n_adapt from run summaries | 2 |
| Table 2 | Paired CI95 | CICIDS strict paired diffs (QK-ZZ vs Energy/MMD; PauliXZ in WebAttacks) | `..._multi_scenario_paired.csv`, `..._thursday_webattacks_qk_paulixz_paired.csv` 📄 | 2 |
| Table 3 | External summary | UNSW-DoS, UNSW-Recon, ToN-IoT-Scanning × 6 detectors: **BA + attack-F1**, gain, n_adapt | ✅ same BA+F1 table (filter external regimes) + run summaries | 3 |
| **Table 4** | Regret | Per-regime × detector: naive BA, decision-oracle BA, regret (pts, CI95), harm-seed% | ✅ `paper2_oracle_regret_decision_001/paper2_oracle_regret_by_detector.csv` | 4 |
| Table 5 | Policy gate | Phase 1: best-safe vs legacy vs no-adapt, per regime, + criteria pass/fail | `paper2_phase1_gate_summary.csv` ✅, `paper2_phase1_success_checks.csv` ✅ | 5 |
| Table 6 | Utility | λ/γ/η strict-positive zones (QK-ZZ vs Energy, Wednesday) | `paper2_actionable_drift_wednesday_001/` | 2/6 |
| App tables | — | feature-map sensitivity, RF downstream, nuisance controls, ToN-IoT smokes, Phase-1 full | respective dirs | App |

**Before writing:** ~~add an attack-F1 column~~ **DONE (2026-07-01)** — attack-F1 is in the raw window results and is now in the BA+F1 table. **Bonus robustness asset** (`paper2_f1_regret_robustness_qkzz.csv`): the regime taxonomy and the harmful-adaptation finding are *metric-robust* — under attack-F1 the CICIDS benefits grow (DDoS best gain +32.3 F1 pts) and ToN-IoT stays harmful for **every** detector (Energy −0.77, KS-max −9.49, QK-ZZ −4.83 F1 pts); the F1 decision-regret reproduces the BA pattern (ToN-IoT QK-ZZ 5.08 F1 pts, 80% harm; Wednesday/DDoS 0.000). This both pre-empts the "BA is the wrong IDS metric" reviewer *and* strengthens the harm story. State it in §5.3/§5.6.

---

## Section 1 — Introduction  *(write LAST)*  · Beat 1: setup & tension

**Job:** pose the *operational decision* problem, not the quantum problem. Land the two-questions hook. Tease Fig 1.

Paragraph plan:
1. ML-based IDS degrade under network concept drift; adaptive IDS periodically retrain.
2. Retraining is costly, so the field frames the core task as **drift detection**: build a sensitive monitor, retrain when it fires. A large literature optimizes detectors (incl. two-sample tests; and, motivated by Paper 1, quantum-kernel MMD).
3. **The gap we expose:** a detector answers "did the distribution change?" but the system needs "will retraining help?". Detection sensitivity is optimized as a proxy for a decision it cannot actually make.
4. **Preview of the finding (cite Fig 1):** across three benchmarks the payoff of readaptation spans strong benefit → marginal → net-harm; in a ToN-IoT scanning regime *no adaptation* beats every triggered strategy, classical or quantum-kernel.
5. Contributions (5 bullets, lift from salvage note §9).

**Bridge to §2:** *"Before presenting our study we position it against three literatures it connects: drift detection for adaptive classifiers, two-sample tests and quantum kernels as detectors, and adaptive IDS under concept drift."*

---

## Section 2 — Related Work

Four short subsections (lift from `paper2_storyline_001.md` §2): (i) drift detection for adaptive classifiers; (ii) two-sample tests as detectors (MMD, Energy, KS, JSD); (iii) quantum kernels in ML; (iv) adaptive IDS under drift. **The gap sentence to plant:** existing work evaluates *detector quality*, not the *value of the retraining decision the detector triggers* — nobody measures when retraining helps vs hurts across regimes/datasets.

**Bridge to §3:** *"We therefore formalize adaptive retraining as a decision problem in which a drift monitor is only one component, and make explicit the metrics that separate detection quality from decision value."*

---

## Section 3 — Problem formulation & method  · (conceptual core)

3.1 **Two questions, one loop.** Formalize: detector fires an alarm on distribution change; a *policy* maps alarm history → retrain/don't; retraining has cost and an uncertain, possibly negative, payoff. State the actionability gap crisply here — this is the sentence reviewers will quote.

3.2 **QK-MMD as an instrument.** ZZ and PauliXZ maps, kernel, MMD statistic. Reported as *one* detector among classical baselines; **no** quantum-advantage framing.

3.3 **Progressive-drift readaptation protocol.** Ramp/plateau windows, trigger (threshold quantile, consecutive-k, cooldown), SVC-RBF downstream with recalibration.

3.4 **Metrics.** `mean_BA`, `n_adaptations`, `gain vs no-adaptation`, `adaptation_efficiency`, detector runtime, and the `actionable_utility(λ,γ,η)`. Introduce the **oracle** (per-window BA envelope) as a diagnostic upper bound → defines **regret**.

3.5 **Baselines & policies.** Energy, MMD-RBF, KS-max, JSD (+ QK ZZ/PauliXZ); legacy trigger + the safe policy family (k-of-n, cooldown).

**Bridge to §4:** *"We instantiate this protocol on three public IDS benchmarks chosen to span, a priori, distinct drift and attack characteristics."*

---

## Section 4 — Experimental protocol

Datasets: CICIDS2017 (4 regimes: Wednesday, DDoS, PortScan, WebAttacks), UNSW-NB15 (DoS, Reconnaissance), ToN-IoT (Scanning main; DDoS/Injection smokes). Reference/current construction, numeric-only vs 88-feature preprocessing (be explicit per dataset), seeds (30 CICIDS / 10 external), windows, CI95 by paired bootstrap, **pre-registration** of the feature-map sensitivity and the Phase-1 policy grid (cite the timestamped protocol notes).

**Bridge to §5:** *"We present results in logical, not chronological, order: first that adaptation is strongly beneficial and characterizable on CICIDS2017, then that this benefit does not survive to external data, then why, and finally whether simple policies can recover it."*

---

## Section 5 — Results

### 5.1 (optional, brief) Detection power under controlled drift · Beat 1→2 motivation
Fig/Table: AUC by severity, `paper2_controlled_streaming_final_001/paper_table_auc_by_severity.csv`.
State 📄: QK ZZ/PauliXZ reach AUC ≈0.918 at max severity vs MMD-RBF ≈0.800 — motivates *different trigger timing*, nothing more. **One paragraph.** No downstream numbers here.

**Bridge:** *"Higher detection power, however, is only useful if it translates into a better retraining decision. We test that next."*

### 5.2 Adaptation helps on CICIDS2017 — and QK defines distinct operating points · Beat 2
Tables 1–2, Fig 2, Table 6.
Key numbers to state (✅ from Phase-0 gate table / 📄 checkpoints):
- Adaptation recovers large BA on every CICIDS regime: DDoS 0.698→0.893 (**+19.5**), PortScan 0.877→0.939 (**+6.2**), WebAttacks 0.843→0.919 (**+7.6**); all detectors positive gain. ✅
- QK-ZZ: −2.10 / −1.83 adaptations vs Energy in Wednesday/DDoS at equal BA (CI95) 📄; PortScan inverts (+BA, +adaptations) 📄; WebAttacks PauliXZ highest mean BA, sig. vs Energy/JSD, NS vs MMD-RBF/KS 📄.
- Runtime overhead ≈114×. Utility (Table 6): QK-ZZ strict-positive vs Energy when λ≥0.5, γ≤0.05.

Tone: this is the "expected" beat. State it cleanly and rigorously; do **not** oversell QK.

**Bridge (the hinge sentence of the paper):** *"Taken alone, this is a familiar result: adaptation works, and the detector shapes its cost profile. The question we had not yet asked is whether any of this survives outside the dataset on which it was tuned."*

### 5.3 The twist: outside CICIDS, the benefit evaporates — and reverses · Beat 3
Table 3, **Fig 1** (full version here if not in intro).
Key numbers (✅/📄):
- UNSW-DoS: best gain KS-max **+1.39**, QK last; UNSW-Recon: best QK-ZZ **+0.34**, JSD negative. Marginal, no significant QK advantage.
- **ToN-IoT Scanning (10 seeds): no-adaptation BA 0.9201 beats every triggered strategy.** Best adaptive PauliXZ 0.9139 (**−0.62**); QK-ZZ 0.8873 (**−3.28**); worst MMD-RBF (**−4.49**). ✅
- Corroboration: ToN-IoT DDoS & Injection smokes — no-adaptation also wins/ties. 📄
- **Frame the claim precisely:** not "adaptation usually hurts" (that would be one dataset) but "the *sign* of the payoff is regime/dataset-dependent, spanning +19.5 to −4.5 BA points, and the detector cannot see which side it is on." Fig 1 is that spectrum.

**Bridge:** *"The detectors are not malfunctioning — they fire on genuine distribution change. The failure is conceptual: the drift they detect is not actionable. We quantify this gap next."*

### 5.4 Quantifying the actionability gap: oracle-regret & detector-invariance · Beat 4
Fig 3, Table 4. **(Materialized 2026-07-01 → `results/tables/paper2_oracle_regret_decision_001/`.)**
- **Oracle definition (use THIS one, not a per-window envelope):** per stream (seed), an *abstain-if-harmful* decision oracle holding the detector FIXED: `decision_oracle = mean_seed( max(no_adapt_BA, detector_BA) )`. `regret = decision_oracle − naive_triggered_BA` (BA points). `harm_seed% = fraction of streams where adapting scored below no-adaptation`. This isolates the *value of the adapt/no-adapt decision* from detector-selection hindsight. Explicitly state in the paper that a per-window or cross-detector oracle was rejected because it conflates detector variance with decision value (and would spuriously beat no-adaptation in the harmful regime). A loose per-window envelope is reported only as a transparency upper bound. ✅
- **Verified headline numbers (do not re-derive):**
  - Wednesday & DDoS: **regret 0.000, CI95 [0,0], harm 0%** — adaptation never hurt on any of 30 seeds → the decision has *no* value; naive triggering is optimal.
  - PortScan 0.18 pts (harm 23%), WebAttacks 0.84–1.87 pts (harm ~47–50%), UNSW DoS/Recon 0.1–0.55 pts (harm 40–50%).
  - **ToN-IoT Scanning, QK-ZZ: regret 3.50 pts, CI95 [0.96, 7.45], harm on 80% of streams** — a perfect abstainer lifts BA from 0.887 to 0.922 (above no-adapt 0.920). Energy: regret 1.63, harm 50%.
  - **Regret scales monotonically with harm-frequency** → the actionability gap, not the detector, is the lever.
- **Detector-invariance:** the regret/harm pattern holds for classical (Energy) and quantum (QK-ZZ) alike (Table 4) → detector choice is not the lever. This is the sentence that immunizes against "rebranded quantum paper."

**Bridge:** *"If the problem is the decision and not the detector, the natural fix is a smarter policy. We pre-registered and tested one."*

### 5.5 Can simple safe/cost-aware policies recover it? (pre-registered negative) · Beat 5
Table 5, Fig 4.
- Criteria & verdict ✅: A (PortScan benefit preservation) **fail** — best-safe *increased* adaptations by 1.8 (the cooldown-0 "safe" policies were more aggressive than the conservative legacy 3-of-3+cooldown10); B (ToN-IoT harm avoidance) **fail** — best-safe still −3.47 gain, far below no-adapt; C (UNSW non-degradation) **pass** narrowly. Overall **phase1_passes = false**.
- Honest reading: in the harmful regime the optimal policy degenerates to *never adapt*, which no drift-triggered rule beats by construction when drift is real but non-actionable.
- **This localizes the open problem:** the fix is a principled cost-aware *decision* policy, not a more sensitive detector or a hand-tuned k.

### 5.6 Controls (brief; rest to appendix)
- **Metric robustness (report here or in §5.3):** the regime taxonomy and harmful-adaptation finding hold under attack-F1, not just BA — CICIDS benefits grow under F1, and ToN-IoT stays harmful for every detector (KS-max −9.49 F1 pts). ✅ `paper2_f1_regret_robustness_qkzz.csv`.
- Nuisance benign: QK-ZZ 1.40 vs Energy 1.03 triggers — QK does **not** filter benign drift better (honest).
- Feature-map sensitivity: no deeper map beats ZZ-r1 (anti-cherry-pick). One paragraph each; full tables in App A/nuisance.

**Bridge to §6:** *"These results cohere around a single reinterpretation of the adaptive-IDS problem."*

---

## Section 6 — Discussion  · Beat 4/6: the concept

1. **Two questions revisited.** Detection ≠ decision. Restate the actionability gap as the paper's thesis, now backed by the spectrum + regret + detector-invariance + failed-policy evidence.
2. **Why does retraining hurt in ToN-IoT? (hypothesis, not proof).** Low headroom (base BA already 0.92), mixed benign/attack current window, retraining variance on non-actionable shift. Label as hypothesis explicitly.
3. **Practitioner implication.** Decide *whether* your deployment is in a benefit or harm regime before optimizing *which* detector; a 114× monitor buys nothing if the decision is the bottleneck.
4. **Methodological takeaways.** Oracle-regret and the λ/γ/η utility framework transfer to any drift detector.

---

## Section 7 — Limitations
Lift from salvage note §13 verbatim-adaptable: positives concentrated in CICIDS; external evidence marginal/contradicting (a *finding*, not hidden); classical simulation (114× is simulation, not hardware); harmful-adaptation strongest on ToN-IoT, not claimed universal; policy family limited to k-of-n/cooldown (negative rules out these, not the broader class); SVC-RBF-centric downstream (RF appendix); offline threshold calibration.

## Section 8 — Conclusion
One tight paragraph: *when not to retrain* is as important as detecting drift; it is a cost-aware decision problem; detector choice — including quantum kernels — is not decisive; simple policies do not suffice; principled cost-aware decision policies are the open problem. (Adapt salvage-note abstract's last two sentences.)

---

## Appendices
- **A** Feature-map sensitivity (ZZ/PauliXZ reps 1–3) — robustness.
- **B** Expensive RF downstream — negative cost result.
- **C** UNSW-NB15 full tables + paired CIs.
- **D** ToN-IoT full tables + DDoS/Injection smokes.
- **E** Phase-1 safe-policy full grid + pre-registered protocol + per-criterion candidate tables.
- **F** QK circuit diagrams (only if venue audience warrants).

**Omit entirely** (already superseded/speculative): adaptive monitor, long-stream single-change, hybrid OR, geometry diagnostics, operational-scale proxy.

---

## Writing order & first actions
1. ~~Build Fig 1 (money figure) and Table 1/3 data~~ **DONE (2026-07-01)** → `paper2_metrics_ba_f1_summary_001/` (Fig 1 spectrum + BA+F1 by regime/method). Only the plot rendering remains.
2. ~~Add attack-F1 column~~ **DONE** — see robustness asset above.
3. ~~Assemble oracle-regret Fig 3 / Table 4~~ **DONE (2026-07-01)** → `results/tables/paper2_oracle_regret_decision_001/` (summary + by_detector + manifest.json). Risk check passed: regret is 0.000 in pure-benefit regimes and 3.50 pts (CI [0.96,7.45], 80% harm) in ToN-IoT. Generator logic is inline in `notes/` session; re-run only if raw window data changes.
4. Draft §5 → §6 → §7 → §8 → §3/§4 → §1/§2.
5. Re-verify every 📄 number against its CSV before it enters the PDF.

*No experiments. No new datasets. All artifacts above are existing results or re-aggregations of existing raw window data.*
