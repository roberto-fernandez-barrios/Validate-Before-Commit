# Paper 2 Rescue Review — QK-MMD Drift Detection in Adaptive IDS

**Reviewer:** Claude Sonnet 4.6  
**Date:** 2026-06-23  
**Branch:** paper2-qkmmd-drift  
**Scope:** Full repository audit — notes, scripts, result CSVs — for Q1 submission readiness

---

## 1. Verdict Brutal

The paper does not have a clean, single claim. It has three partially-supported sub-claims that apply to different scenarios, and one is contradicted in a third scenario. The framing "QK-MMD is better than classical drift detectors for adaptive IDS" is not defensible. The narrower framing "QK-MMD ZZ alters the readaptation trade-off favorably in scenarios where drift is adversarial and progressive" is defensible with strict statistical support — but only under specific utility-function assumptions that must be declared upfront.

The paper **can** be published in Q1. Two conditions must both be met:
1. The submission abandons any claim of BA superiority as the central result.
2. The inconsistency of the PortScan scenario (QK triggers MORE, not fewer) is addressed honestly — as a scope condition, not swept under the rug.

If the authors refuse to do (2), the paper becomes a cherry-pick and a careful reviewer will kill it.

---

## 2. Claim More Defensible Than Everything Else

**Primary publishable claim (strictly supported):**

> Under progressive drift in network intrusion scenarios where the adaptation cost per retraining episode is non-negligible (λ ≥ 0.5), QK-MMD ZZ yields higher adaptation efficiency than all classical baselines in Wednesday and DDoS scenarios — using fewer total readaptations while producing comparable downstream accuracy — at the cost of a 100-fold detector runtime overhead.

**Secondary claim (conditional):**

> In PortScan, QK-MMD ZZ achieves higher downstream accuracy (strict CI vs. Energy, JSD, KS-max, MMD-RBF), but triggers more readaptations. This dissociation between trigger rate and accuracy outcome indicates that the operational advantage of QK-MMD depends on the attack type and must be evaluated scenario-specifically.

These two claims are consistent and falsifiable. Together they constitute an "operational profiling" contribution, not a universal superiority claim.

---

## 3. Evidence That Supports the Primary Claim

All CIs are 95% paired across 30 seeds.

### n_adaptations (QK-ZZ fewer triggers — strict CI excludes zero)

| Scenario | Baseline | QK-ZZ diff | CI95 |
|----------|----------|------------|------|
| Wednesday | Energy | −2.10 fewer | [−2.43, −1.73] |
| Wednesday | JSD | −0.43 fewer | [−0.67, −0.20] |
| Wednesday | KS-max | −0.30 fewer | [−0.57, −0.03] |
| Wednesday | MMD-RBF | −0.93 fewer | [−1.20, −0.63] |
| DDoS | Energy | −1.83 fewer | [−2.13, −1.53] |
| DDoS | JSD | −0.57 fewer | [−0.83, −0.30] |
| DDoS | MMD-RBF | −0.77 fewer | [−1.00, −0.53] |

### adaptation_efficiency (QK-ZZ higher — strict CI)

| Scenario | Baseline | QK-ZZ diff | CI95 |
|----------|----------|------------|------|
| Wednesday | Energy | +1.55 | [+1.17, +1.96] |
| Wednesday | JSD | +0.60 | [+0.23, +1.00] |
| Wednesday | KS-max | +0.62 | [+0.28, +0.99] |
| Wednesday | MMD-RBF | +1.07 | [+0.72, +1.45] |
| DDoS | Energy | +1.94 | [+1.60, +2.30] |
| DDoS | JSD | +0.77 | [+0.37, +1.18] |
| DDoS | KS-max | +0.59 | [+0.02, +1.16] |
| DDoS | MMD-RBF | +1.14 | [+0.80, +1.49] |

### Actionable utility (strict positive CI vs. all baselines when λ ≥ 0.5, Wednesday)

Energy distance: strict CI at λ=0.5, γ=0 → CI [+0.42, +1.76]; at λ=1.0, γ=0 → CI [+1.35, +2.88].  
MMD-RBF: strict CI at λ=0.25 onward.  
All four classical baselines: strictly beaten at λ=2.0.

These results hold under three nuisance penalty values (η=0, 0.25, 0.5) and detector runtime penalties (γ=0, 0.01, 0.05).

---

## 4. Evidence That Weakens the Primary Claim

### 4.1 PortScan: QK-ZZ triggers MORE (strict CI)

| Comparison | diff in n_adaptations (QK minus baseline) | CI95 |
|------------|------------------------------------------|------|
| vs Energy | +1.37 MORE | [+1.10, +1.63] |
| vs KS-max | +0.73 MORE | [+0.47, +1.00] |
| vs MMD-RBF | +1.57 MORE | [+1.30, +1.80] |

There is no single behavioral explanation for why QK fires less in Wednesday/DDoS but more in PortScan. This inconsistency is the single most dangerous reviewer attack. The paper must explain it — not ignore it.

### 4.2 BA improvement: only in PortScan and DDoS vs MMD-RBF, not universally

| Scenario | Comparison | BA diff | CI95 |
|----------|-----------|---------|------|
| Wednesday | vs Energy | +0.0001 | [−0.006, +0.007] — includes zero |
| Wednesday | vs MMD-RBF | +0.005 | [−0.002, +0.013] — includes zero |
| DDoS | vs Energy | +0.002 | [−0.005, +0.009] — includes zero |
| DDoS | vs MMD-RBF | +0.008 | [+0.0004, +0.0155] — strict |
| PortScan | vs Energy | +0.006 | [+0.001, +0.013] — strict |
| PortScan | vs MMD-RBF | +0.033 | [+0.014, +0.056] — strict |

BA advantage is real in PortScan (3 percentage points vs MMD-RBF, strict), marginal in DDoS vs MMD-RBF, and zero in Wednesday. The efficiency advantage, not BA, is the stronger claim.

### 4.3 Runtime overhead is extreme and unconditional

QK-ZZ detector runtime: ~6.05s/window vs 0.053s/window for Energy distance — a 114× penalty.  
QK-ZZ is strictly more expensive in all comparisons in all scenarios (CI95 universally excludes zero on the expensive side).

The actionable utility analysis correctly shows this matters: at γ=0.25, several utility CIs shrink or disappear. At γ=0.5, QK loses the utility argument entirely even at λ=2.

### 4.4 Nuisance triggers on benign-only streams

From `paper2_cicids_benign_only_checkpoint_001.md`: QK-PauliXZ has higher trigger sensitivity (power=0.50 at w=256, d=8) on benign distribution shift. This is framed positively in that note but it is a double-edged sword: the same sensitivity causes false adaptation triggers on non-adversarial drift.  

The multi-scenario nuisance controls show QK-ZZ triggers 1.40 false adaptations on benign-only streams vs Energy 1.03. This is not large, but a reviewer will ask whether the efficiency advantage disappears when false triggers are counted properly.

### 4.5 Single dataset

All results are on CICIDS2017. Three scenarios share the same Tuesday reference and differ only in current-day attack type. A Q1 reviewer at TIFS or TDSC will ask for a second dataset (UNSW-NB15 or CIC-IDS2018) or at minimum argue the CICIDS2017 scenarios are not independent enough to constitute evidence for generalizability.

### 4.6 Feature-map coverage: only ZZ-r1 and PauliXZ-r1

The progressive readaptation experiment uses `reps=1` (from the checkpoint notes and the experiment script default). The expensive-downstream script uses `--q-reps 2` as default, but was never run to completion with results. A reviewer will ask why reps=1 was the only configuration tested, whether the efficiency advantage holds at reps=2 or 3, and whether this is post-hoc selection.

---

## 5. Decision: RF Expensive Downstream Experiment

**Status:** Script exists (`src/experiments/run_paper2_expensive_downstream.py`) with Random Forest 500 trees. No results exist — no CSV files found in `results/tables/` matching this experiment.

**Decision: Defer. Do not include in the paper submission.**

**Rationale:**

The core argument for running this experiment was: "If retraining is expensive (RF 500 trees), then QK's fewer triggers save more total operational time." This is a reasonable hypothesis but it has two problems:

(a) **The argument is scenario-dependent.** In PortScan, QK triggers MORE than Energy distance, so the total RF retraining cost under QK would actually be HIGHER in that scenario. Including RF results from Wednesday+DDoS only, without PortScan, would look like cherry-picking.

(b) **It adds a new design dimension without closing the existing ones.** The paper does not yet have a final answer on downstream model complexity. Running an RF experiment without pre-registered results (no CSVs, preliminary 5-seed note from prior session suggests Energy wins in total operational cost anyway) creates a new axis of possible results that could further fragment the narrative.

(c) **SVC-RBF is the natural downstream for streaming IDS.** SVC-RBF fit time at train_size_per_class=2000 is negligible (~0.03s). The motivation for RF would need to be independently justified in the paper, and a reviewer will ask "why RF and not gradient boosting?" or "why 500 trees?"

**If RF is to be included later:** Run it at 30 seeds with all three scenarios, all six detectors, and include PortScan results even if they are unfavorable. Pre-register the analysis plan. This would be a revision-round addition, not a submission-time addition.

---

## 6. Decision: Feature-Map Sensitivity Study

**Status:** Only ZZ (reps=1) and PauliXZ (reps=1) have been evaluated in the main progressive drift experiments. The expensive downstream script has `--q-reps 2` as default, but was never run to completion. There is no reps=2 or reps=3 result for any scenario.

**Decision: Run the sensitivity study as a closed appendix experiment before submission.**

**Rationale:** A reviewer at TDSC or Computers & Security who knows quantum kernels will immediately ask why reps=1 was selected and whether results change at reps=2 or 3. Without this, the paper is vulnerable to "your results may be specific to a suboptimal quantum circuit." The study does not need to show QK wins at all reps — it needs to show that the reps=1 result is not anomalous.

### Pre-committed Protocol (MUST be followed exactly — no post-hoc changes)

**Configurations to evaluate (all 6, no cherry-picking):**
- ZZ-r1: ZZ feature map, reps=1
- ZZ-r2: ZZ feature map, reps=2
- ZZ-r3: ZZ feature map, reps=3
- PauliXZ-r1: PauliXZ feature map, reps=1
- PauliXZ-r2: PauliXZ feature map, reps=2
- PauliXZ-r3: PauliXZ feature map, reps=3

**Fixed parameters (non-negotiable):**
- input_scaling: `atan_standard`
- dim: 8 (consistent with main experiments)
- seeds: 30 (same as main experiments)
- window_size: 128
- All other progressive readaptation parameters: same as `run_paper2_progressive_readaptation.py` defaults

**Development scenario (used ONLY for selection if a single config must be chosen):**
- Tuesday → Wednesday

**Held-out scenarios (evaluated after development, not before):**
- Tuesday → Friday PortScan
- Tuesday → Friday DDoS

**Primary metrics (pre-specified, in this order):**
1. adaptation_efficiency (gain per readaptation episode)
2. n_adaptations (total trigger count)
3. mean_balanced_accuracy (secondary)

**Reporting rule (non-negotiable):**
Report ALL 6 configurations in a table. Do not report only the best. If reps=2 or reps=3 wins, say so and update the main experiment configuration in a note. Do not adjust the main results retroactively.

**Classical baselines always reported alongside:**
Energy distance, MMD-RBF, KS-max, JSD — same as main experiments.

**Smoke test protocol (run before full 30-seed run):**
```powershell
python -m src.experiments.run_paper2_progressive_readaptation `
  --data-ref <path_tuesday> --data-cur <path_wednesday> `
  --label-col Label `
  --outdir results/tables/paper2_feature_map_sensitivity_smoke_001 `
  --scenario Wednesday `
  --seeds 1,2,3 `
  --methods qk_mmd_zz `
  --q-reps 1 `
  --dim 8 --window-size 128
```
If smoke passes (completes without error, output CSV has expected columns), proceed with full run for all 6 configurations × 3 scenarios × 30 seeds.

**Expected runtime:** Each QK config × 1 scenario × 30 seeds ≈ 30 × 100 windows × ~6s/window = ~5 hours per (config, scenario) pair. 6 configs × 3 scenarios = 18 runs = ~90 hours total on a single CPU. Parallelization across configs is safe (seeds are independent).

**Stop criterion:** If reps=2 and reps=3 both yield strictly worse adaptation_efficiency than reps=1 in the development scenario (Wednesday), conclude the paper's reps=1 choice is conservative and not cherry-picked. Proceed with reps=1 as primary. Report all in appendix.

---

## 7. What Belongs in the Paper (Main Body)

**Section 4 (Experimental Setup):** CICIDS2017 preprocessing, progressive drift protocol (80-window ramp + 20-window plateau), adaptation mechanism (SVC-RBF retrain + recalibrate), cooldown=10, consecutive_k=3, threshold_quantile=0.95.

**Section 5.1 (Controlled streaming — detection power):** AUC table by severity (5 levels × 5 detectors). QK PauliXZ and ZZ both reach AUC 0.918 at severity 1.0 vs MMD-RBF 0.800. This motivates why QK might produce different trigger timing.

**Section 5.2 (Progressive readaptation — main results):** Table: n_adaptations, adaptation_efficiency, BA, cumulative_error_area, runtime for all 6 methods × 3 scenarios (Wednesday, PortScan, DDoS). Paired CI table with strict-CI flags.

**Section 5.3 (Actionable utility analysis — Wednesday):** Utility grid at λ ∈ {0.25, 0.5, 1.0, 2.0}, γ ∈ {0, 0.01, 0.05}. Show which (λ, γ) zones have strict positive CI for QK vs all baselines. This is the bridge from statistical to operational significance.

**Section 5.4 (Nuisance trigger control — benign drift):** Report false adaptation rate on benign-only streams. Honest disclosure that QK-ZZ has marginally higher nuisance rate than Energy but lower than MMD-RBF in PortScan.

**Section 6 (Discussion):** Address the PortScan inconsistency directly. Proposed explanation: PortScan's attack signature is more distributed in feature space, causing QK's geometric sensitivity to the attack manifold to interpret non-stationary behavior that classical detectors smooth over. This is a hypothesis, not a proven mechanism — say so.

---

## 8. What Goes to Appendix or Gets Cut

**Appendix A (feature-map sensitivity):** ZZ and PauliXZ at reps=1/2/3. Required to preempt reviewer attack on feature map selection.

**Appendix B (long-stream downstream validation):** 100 post-windows at sev=0.75 and 1.0. All detectors fire at window 2, downstream identical. Negative result but establishes that the adaptation protocol is not trivial. Keep brief.

**Appendix C (hybrid OR combination):** Hybrid worse than individual QK at sev=1.0. Negative result. Include as one table only — one paragraph of text. Do not try to salvage it.

**CUT: Single-change downstream adaptation:** The sev=1.0 result (all detectors triggered, downstream BA=0.8492 identical across triggered methods) adds confusion rather than clarity. The progressive readaptation experiments subsume and supersede it.

**CUT: Geometry diagnostics:** Score separation plots are diagnostic artifacts, not publishable evidence. The geometric interpretation is speculative.

**CUT: Operational scale impact / proxy calculation:** "At 1M flows/day, QK detects 336k extra attacks" is not derived from a real network experiment. Reviewers at security venues will reject this as unsubstantiated.

**CUT: Adaptive monitor experiment:** The adaptive_monitor results predated the progressive readaptation protocol and are superseded. Do not include.

---

## 9. Reviewer Attack Simulation

### Attack 1: "The PortScan scenario contradicts your efficiency claim."

> Your paper claims QK-MMD ZZ requires fewer readaptations than classical baselines. In PortScan, QK-ZZ triggers 4.07 times vs Energy distance's 2.70 — a strict difference of +1.37 MORE triggers (CI [1.10, 1.63]). How does this support your claim?

**Required response in paper:** Section 6 must acknowledge this explicitly. Frame as: "The adaptation-efficiency advantage of QK-MMD ZZ is not universal — it depends on whether the attack distribution induces a consistent geometric signal in the quantum feature space. PortScan attacks are distributed across a wide port range, potentially producing higher moment-based divergence signals in QK's embedding. Wednesday and DDoS, which are volumetric or protocol-based attacks, produce more coherent distributional shifts. This suggests that QK-MMD's efficiency advantage is attack-type-dependent and practitioners should characterize this offline before deployment."

This framing is honest and defensible. It positions the PortScan result as a scope condition, not a failure.

### Attack 2: "Energy distance is 114× cheaper and achieves equal or better downstream accuracy."

> Table 5 shows Energy distance achieves mean_BA=0.885 in Wednesday vs QK-ZZ's 0.885 (difference non-significant). Energy distance runs in 0.05s vs 6.05s. Why should a practitioner choose QK-MMD?

**Required response:** "Energy distance achieves comparable downstream accuracy but triggers 2.10 more readaptations per 100-window stream (CI [1.73, 2.43]). In scenarios where the downstream model is expensive to retrain (e.g., Random Forest, deep learning), each additional trigger represents a significant operational cost. The actionable utility analysis (Section 5.3) identifies the break-even retraining cost above which QK-MMD ZZ yields higher net operational value."

Note: This argument is weakened by the fact that the paper currently only evaluates SVC-RBF downstream, which is cheap. If RF results are never run, this response is somewhat circular.

### Attack 3: "Your utility analysis has three free hyperparameters (λ, γ, η) chosen post-hoc."

> You show QK wins when λ≥0.5 and γ is small. But these values were chosen to make QK look favorable. If a reviewer picks λ=0.1 and γ=0.5, QK loses. Your utility analysis proves nothing.

**Required response:** "The utility analysis covers the full grid λ ∈ {0, 0.1, 0.25, 0.5, 1.0, 2.0}, γ ∈ {0, 0.01, 0.05, 0.1, 0.25}, η ∈ {0, 0.25, 0.5, 1.0, 2.0} and reports strict-CI positive zones. We do not claim QK wins at all (λ, γ, η) — only at those where CI excludes zero. The claim is that there exist realistic operational regimes (λ≥0.5, γ≤0.05) under which QK's efficiency advantage exceeds its detection overhead; practitioners must determine which regime applies to their deployment context."

This is the correct framing. The paper should be explicit that these conditions are necessary, not that QK universally wins.

### Attack 4: "Only CICIDS2017 is used — the results may not generalize."

> All three scenarios share the same reference distribution (Tuesday BENIGN+attacks) and differ only in the current day. They are not independent evaluation scenarios. Results on CICIDS2017 cannot support claims about general network IDS.

**Required response:** Acknowledge that generalization is limited. Frame the paper as "empirical characterization on a standard benchmark" rather than "proof of general superiority." Add a limitations section. If possible, add UNSW-NB15 or CIC-IDS2018 as a second dataset before submission — even if results are mixed, the addition prevents desk rejection at security venues.

### Attack 5: "Only reps=1 was tested. Your feature map is potentially suboptimal."

> ZZ and PauliXZ at reps=1 produce very shallow circuits. Deeper circuits (reps=2, 3) are known to have better kernel approximation properties. Did you tune the reps parameter? If not, your QK-MMD may be an inferior implementation of quantum kernels.

**Required response:** The feature-map sensitivity study (Appendix A) addresses this. If it is not completed before submission, the paper is exposed. This attack is the hardest to deflect with text alone — empirical results are required.

---

## 10. Final Recommendation

**Recommendation: Submit to Q2 now; aim for Q1 revision.**

**Option A (submit now to Q2 — high confidence):**
Target: Computer Networks (Elsevier), Journal of Information Security and Applications, or Expert Systems with Applications. Submit within 4-8 weeks. Accept that the PortScan inconsistency will generate one revision round but not rejection.

**Option B (delay 3 months, submit to Q1 — conditional confidence):**
Target: IEEE TDSC or Computers & Security (Elsevier, CiteScore ~9). Before submission:
1. Complete the feature-map sensitivity study (reps=1/2/3 for ZZ and PauliXZ, all 3 scenarios, 30 seeds). This is the most critical gap.
2. Run the RF expensive downstream at 30 seeds with all 3 scenarios (optional but strengthens the efficiency argument).
3. Add a second network dataset — even with 1-2 scenarios.
4. Tighten the framing: remove all UA ("detects drift better") language; replace with "modifies readaptation frequency under progressive drift in adversarial IDS scenarios."

**Do NOT do:**
- Do not add a "theoretical analysis of quantum advantage" section that isn't backed by the existing results.
- Do not expand the utility analysis with more parameters — the grid is already large enough to look tuned.
- Do not cherry-pick: if the feature-map study shows reps=2 wins, update the main experiments to reps=2 and re-report all results. Do not show only the best reps for each scenario.
- Do not include the operational scale proxy calculation. It reads as motivated reasoning.

---

## 11. Commands Executed and Files Created

**Read operations performed this session (no data was modified):**
- `results/tables/paper2_progressive_multi_scenario_cicids_001/paper_table_multi_scenario_summary.csv`
- `results/tables/paper2_progressive_multi_scenario_cicids_001/paper_table_multi_scenario_paired.csv`
- `results/tables/paper2_progressive_multi_scenario_cicids_001/paper_table_multi_scenario_utility_strict_positive.csv`
- `results/tables/paper2_actionable_drift_wednesday_001/paper_table_actionable_utility_strict_positive.csv`
- `notes/paper2_cicids_benign_only_checkpoint_001.md`
- `src/experiments/run_paper2_expensive_downstream.py`
- `src/experiments/run_paper2_progressive_readaptation.py` (previous session)
- Multiple notes checkpoints (previous session)

**Files created this session:**
- `notes/claude_paper2_rescue_review.md` — this file

**No experiments were run. No existing files were modified. No commits were made.**

---

## Summary Table of Strict Claims

| Claim | Strict CI support | Scenarios | Status |
|-------|-------------------|-----------|--------|
| QK-ZZ fewer n_adaptations vs Energy | YES | Wednesday, DDoS | Publishable |
| QK-ZZ fewer n_adaptations vs MMD-RBF | YES | Wednesday, DDoS | Publishable |
| QK-ZZ better adaptation_efficiency vs all | YES | Wednesday, DDoS | Publishable |
| QK-ZZ better BA vs MMD-RBF | YES | PortScan (+3pp), DDoS (+0.8pp) | Publishable (scope-limited) |
| QK-ZZ better utility at λ≥0.5 vs Energy | YES | Wednesday | Publishable (λ-conditional) |
| QK-ZZ MORE triggers vs Energy/MMD-RBF | YES (strictly MORE) | PortScan | Must disclose |
| QK-ZZ cheaper runtime | NO (strictly more expensive) | All scenarios | Must disclose |
| QK-ZZ better BA vs Energy | CI includes zero | Wednesday, DDoS | Cannot claim |
| Hybrid OR QK better than individual QK | NO | All | Negative result, appendix |
