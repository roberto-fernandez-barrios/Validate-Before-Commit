## What changed since v1.6.0 (amendment 005 — the fifth external review, fully executed)

**External chronological validation (the review's biggest ask).** A new registered stream:
the raw UNSW-NB15 captures (2.54M flows) sorted by flow start time, incumbent trained on the
first 30% of the timeline — an external, non-CICIDS temporal test with a HEALTHY incumbent
(82.3% BA, no collapse; ~21 triggers/stream). Result: updating helps moderately (+7.33
[6.80, 7.85]) and the gate pays **no premium at all** (+0.16 [−0.31, 0.63] vs naive) —
insurance is free exactly where the account predicts the commit decision is genuinely
uncertain. Chronological net-harm remains unobserved and is stated as the outstanding test.

**Two honest self-corrections, both prompted by the review and confirmed by experiment.**
(1) The two-stage gate reused one probe for its train and commit decisions — real selection
optimism. The split-probe rerun (registered, δ sweep) keeps the harm reduction (+1.79
[0.69, 2.92] above naive at half naive's label cost) but the net gain over never-adapting is
now honestly unresolved (+0.15 [−0.15, 0.46]). (2) Our composition explanation of the
chronological premium was put to a registered stratified-probe test and **refuted**
(strat−gate −0.05 [−0.49, 0.41]); probe staleness under fast drift is reported as the
surviving hypothesis, not a demonstrated mechanism.

**Model-specification upgrades.** Pooled hierarchical model re-clustered on regime×seed
(β_deg −1.02 [−1.61, −0.43]; robust to a random slope); VIFs disclosed (severity↔time
structurally collinear on a ramp; degradation and score clean); the per-trigger analysis
extended to QK-ZZ (replicates; one small conditional exception reported); local per-decision
regret renamed precisely and shown horizon-stable (h ∈ {1,3,5,10}).

**Monitor budget sweep.** 4× and 10× monitoring budgets do not fix reference DDM/ADWIN;
the "labels are better spent on the decision" claim is now budget-conditional with a curve.

**Frontier instead of a winner.** New main-text table + locked utility scenarios: no policy
dominates; the cheap policies win at the evaluated cost ratios; the plain gate is the accuracy
maximizer and overtakes beyond ~46k flows in the harm regime. Policy choice is a cost decision.

**Structure.** Methods rewritten around harness v2 (v1 demoted to "initial exploratory
study"); title sharpened to "Label-Efficient Commit Decisions for Drift-Triggered Classifier
Updates in Network Intrusion Detection"; keywords distribution-drift/risk-aware; conclusion
bounded by the measured premium.

**Reproducibility.** Confirmatory CSVs are now committed, pinned by MANIFEST.sha256, with a
single `make reproduce` workflow. Claims audit: 240 checks, all passing.
