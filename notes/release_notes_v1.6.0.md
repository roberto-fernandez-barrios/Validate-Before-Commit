## What changed since v1.5.0 (amendment 004 — the fourth external review, fully executed)

**Corrected chronological streams (registered fix + rerun, fresh seeds).** The review caught a
real flaw in the first Friday replay (stride mismatch: candidates trained on ~28k rows never
presented as windows; mixed accuracy/BA metric). The corrected runner (candidates = the last 8
OBSERVED windows only; homogeneous BA-over-two-class-windows headline) was re-run on Friday
(seeds 165–194) plus two new streams: Wednesday (196–225) and Thursday (227–256). The corrected
picture is sharper in both directions: recoveries of +13.6 to +27.6 BA points confirm the
phenomenon on real drift, and the gate's premium is metric-dependent — Friday −6.34 [−6.83,
−5.90] BA yet +4.19 [3.85, 4.52] on overall accuracy; Wednesday pays no premium (+0.40). Cause
identified and reported: the gate inherits the metric and class composition of its probe.

**v2 robustness suite (paired on the common streams).** Budget: the initial "8 labels suffice"
is corrected — at b=8 the gate reduces harm (+1.22 above naive) but is not net-positive; the
operating point is b=32. Latency 20 holds in the harm regime (+0.95). Corruption: harm
avoidance survives 40% flipped labels; net benefit survives 25%.

**Two-stage gate.** Instantiates the corrected cost account (ε* = λ_U/(λ_e·N); training costs
belong to the antecedent decision): probes the incumbent BEFORE training, trains 74% fewer
candidates in the harm regime, total labels below naive's (1,182 vs 2,594), still net-positive.

**Calibrated ensemble — claim revised.** Platt calibration fixes the marginal-regime dilution
(UNSW +1.72, above both naive and the gate); the gate stays ahead in the decisive regimes and
remains the only policy with an explicit no-deploy decision. "None attains safety and full
benefit" removed from the paper.

**Reference-implementation validation (river).** Our DDM agrees (94%); in-harness river-DDM
replicates the net-harm (ToN −2.23). Our ADWIN variant under-fires (57%) — the review's
suspicion confirmed; the reference ADWIN is reported instead.

**Decision quality + hierarchical model.** Gate cuts per-trigger regret ~22× in the harm
regime (recall 0.95); MixedLM with severity/time controls: only degradation predicts update
value (pooled β −1.02 [−1.17, −0.87]); LORO transfers directionally, not in scale (reported).

**Cost accounting.** New main-text table: candidates dominate every policy's label bill; the
gate's total cost exceeds naive's; the probe is ~3% of it. "Label-efficient" = the decision.

**Manuscript surgery.** Commit/deployment reframing; sunk-cost-correct ε*; v2 promoted to the
opening of Results with the main confirmatory table; coupled Fig. 2 demoted to appendix;
"fails safe"/"never significantly worse" purged repo-wide; graphical abstract regenerated;
README/REPRODUCE synchronized; classifiers_lp32 aggregation committed (traceability closed);
requirements-lock.txt added. Claims audit: 155 → **208 checks**, all passing.
