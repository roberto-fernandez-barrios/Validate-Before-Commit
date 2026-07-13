# Coupling-aware revision — response to the external (GPT) mock review

**Date:** 2026-07-13 · Re-aggregation only; no new experiments (stop-rule respected).
Artifacts: `results/tables/paper2_mechanism_law_robustness_001/coupling_diagnostics.csv`.

## The mathematical-coupling attack (reviewer point 1) — verdict: CORRECT, and answerable

gain = BA_adapt − BA_noadapt shares the baseline with the predictor, so r(N, gain) is negative
by construction. We computed the exhaustive re-pairing null (all 5040 pairings of the observed
post-adaptation values to the observed baselines, both marginals held):

- null median r = **−0.908**; observed r = −0.888; p(observed more extreme) = **0.80**.
- → The coefficient itself carries no evidence beyond the marginals. The reviewer is right.

**What survives (and is now the §5.2 claim):**
1. **Restoration to a nearly regime-invariant level**: σ(post-adapt BA) = 3.5 pts vs
   σ(deployed BA) = 7.4 pts across the 7 regimes; slope of gain on deployed BA = −0.87.
   The benefit of adapting IS the deployed model's headroom — that is the phenomenon,
   stated without leaning on r.
2. **The coupling-free contrast**: within a deployment (30 seeds per regime), the detector's
   own score is uninformative about the gain from its own triggered adaptations —
   r median **+0.06** (range +0.02..+0.13) — while deployed BA tracks it in every regime
   (median −0.68). Across regimes classical scores DO co-vary with gain (+0.75..+0.94,
   drift size confounds degradation), but that association is unavailable within a
   deployment, and the score-based persistence policies failed (§5.4, pre-registered).

Manuscript: §5.2 rewritten around these two facts, with the coupling null reported
explicitly; "mechanistic law" → "degradation–headroom regularity" everywhere; abstract,
intro, contributions, discussion and conclusion updated. Table 7 gains a coupling block.

## Other review points addressed (all three manuscript sources)

- **Appendices B/E dangling** (real bug): references repointed to Table 5 / the artifact.
- **"Adversarial" overclaim** (correct): renamed to *randomly corrupted validation labels*;
  explicit statement that a candidate-aware adversary is strictly stronger and untested (§7).
- **"Never underperforms"** (correct — Table 6 has mean deficits up to 0.11): now "never
  significantly worse; largest observed mean deficit 0.11 BA pts (RF/UNSW), within seed noise".
- **Non-inferiority** (correct): benefit preservation was ALREADY pre-registered as
  non-inferiority at margin 0.3; now stated as such with paired CI lower bounds ≥ −0.12.
- **Oracle naming** (correct): renamed *policy oracle*, framed as a conservative lower bound
  on per-trigger decision headroom.
- **Winner's curse on "best detector"** (correct): §5.1 note that pre-specified KS-max
  reproduces the taxonomy (+5.5..+18.6 / +1.5, +0.2 / −2.4).
- **Oracle-like candidate training** (INCORRECT as stated): verified in code — candidates
  train at the CURRENT mixture severity sev(t), never the final pool. Now stated in §4
  "Protocol detail", with train/probe disjointness, all sizes (2000/512/256/128/20-window
  calibration, q=0.95, 3-consec + cooldown 10).
- **Label accounting** (correct): probe framed as INCREMENTAL cost on top of the 512/class
  candidate training labels any labeled-retraining loop consumes; §4 + Limitations.
- **Balanced-probe prevalence** (correct, needs experiments to fully close): Limitations now
  quantifies ≈ b/(2π) inspections at prevalence π; budgets are post-enrichment costs.
- **Seeds ≠ environments, multiplicity, synthetic gradual drift, replay baselines**
  (correct): all added to Limitations; replay/ensemble update strategies flagged as the one
  remaining gap that would need new experiments (the gate is orthogonal to the update rule).

Audit extended to **94 checks** (10 coupling numbers + KS-max taxonomy), all passing.
Compiles clean: 22 pp (CAS) / 17 pp (IEEE); abstract 249 words.

## Not done (user decision required)
- Replay/sliding-window/incremental **baselines** (reviewer point 9) and **prevalence-sweep
  probes** (point 4) require new experiments — currently acknowledged as limitations.
- Title keeps "Safe" (now operationally defined in the text); renaming is an author call.
