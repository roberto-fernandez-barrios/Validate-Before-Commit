# Harness v2 — Amendment 002 (LOCKED before the amended runs)

**Date:** 2026-07-14 · Committed/pushed before any amended run. Responds to the third external
review round. Changes to the registered design, each with its reason:

1. **Confirmatory seed window shifts to 104–133.** Seeds 101–103 were used in the ToN smoke
   test before registration and are therefore not pristine; we run seeds 131–133 as a top-up
   for every arm and report 104–133 (30 pristine seeds). Criteria unchanged.
2. **Holdout gate deduplication.** With-replacement batch draws could place copies of one flow
   in both the training rows and the held-out probe; the batch is now deduplicated by row
   identity before the split. Holdout arms are fully re-run (seeds 104–133) under the fix.
3. **Natural-prevalence calibration.** Detector reference and calibration windows now follow
   the stream's operating prevalence; the natural-prevalence arms are re-run (π = 0.05,
   seeds 104–133) so the detector is no longer comparing a balanced reference to an
   imbalanced stream.
4. **Model-agnosticism under v2.** New arms: {random_forest, logreg, mlp} × {naive, holdout
   gate} × 3 regimes, KS-max, seeds 104–133 — the four-classifier claim moves onto the
   hardened harness with paired CIs.
5. **Per-trigger inference hardening (analysis only).** The mechanism correlations gain
   cluster (per-seed) bootstrap CIs and leave-one-regime-out checks; conclusions will be
   stated predictively, not causally.
