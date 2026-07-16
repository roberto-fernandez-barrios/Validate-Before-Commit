# Amendment 012 — registered pre-run (Sol 4th-round: three confirmed code bugs + confounds)

Registered before any run. Sol inspected the code and found three real bugs (all verified this
session) plus valid confounds. Same discipline: fix, smoke, re-run, report negatives honestly.

## Confirmed bugs (verified against code) and fixes
1. **`cn` regularization inverted (BLOCKER).** Line 542 did `svc_C = n_unique / train_size` (C ∝ n
   → *weakens* regularization as the cumulative set grows), the opposite of the documented
   "C ∝ 1/n" intent. Correct to keep the margin/empirical-loss balance matched to the incumbent:
   `svc_C = (2·train_size_per_class) / n_unique` (C ∝ 1/n, decreasing). Re-run cumulative `cn`.
   **P1:** the zero-drift harm persists under *correct* 1/n regularization too (if it vanishes, the
   regularization reading was right and we report that).
2. **McNemar α mismatch (BLOCKER).** §3.5 says "all three use α=0.10" but `--mcnemar-alpha`
   default is 0.05 (CS use 0.10). Fix BOTH: (a) correct the manuscript to state the effective
   values, and (b) additionally run zero-drift McNemar at α=0.10 for a homogeneous comparison.
   **P2:** McNemar at 0.10 still ≈0 commits under zero drift (the conclusion is α-robust).
3. **Causal no-probe → commit=True (BLOCKER).** Lines 621-622: when the observed probe is
   unavailable (t<9) the gate commits unvalidated. Add `--no-probe-policy {commit,reject}` (default
   `commit` preserves old arms; causal re-run uses `reject`), log `n_commit_no_probe`, and re-run
   the causal gate arms. **P3:** few triggers occur at t<9 and the harm-regime result is unchanged
   under `reject` (report the exact count either way).

## Confounds
4. **4-classifier zero-drift size asymmetry.** RF/LogReg/MLP zero-drift used adapt-size 512 vs
   incumbent 2000. Re-run size-matched (adapt-size 2000) under zero drift, 3 models × 3 datasets.
   **P4:** the harm persists (or deepens) size-matched, as it did for SVC (a008). Restrict the
   claim to "default asymmetric budget; size-matching separately verified" if any model flips.
5. **Replacement-variance mechanism.** The transformer (scaler+PCA) is fit on the incumbent's
   training data, so incumbent and challenger are not exchangeable. Sol allows two responses; we do
   BOTH where cheap: (a) DOWNGRADE the manuscript wording from "pure estimation variance" to a
   hypothesis, and (b) a symmetric control — fit the transformer on the disjoint `train` partition
   (already the case) but note the incumbent also trains there; a fully independent-transformer A/B
   is named as the decisive future control if (a)+(b) leave it ambiguous.
6. **Strict-`>` (reject-ties) baseline.** Add the obvious cheap baseline: commit iff
   p_cand > p_inc (ε≈1/b), between ε=0 and McNemar, under zero drift. **P6:** rejecting ties
   recovers much of the ε=0 zero-drift harm at ~zero cost, quantifying how much the statistical
   gates add beyond it.
7. **Harmful-commit intervals.** Report Clopper–Pearson CIs, numerator/denominator, n commits, for
   the harmful-commit rates; soften "eliminates" → "zero observed (CI …)".

## Out of scope (declared)
- Full independent-transformer symmetric A/B and end-to-end operational-prevalence + candidate-label
  latency: named as future work (transformer-partition rewrite / scheduling rewrite).
- Body trimming to supplement and graphical-abstract redesign: editorial, lower priority; we fix
  the highlights wording and soften claims but do not restructure the 37-pp body this round.

## Output naming
v13 arms `results/raw/paper2_v13_*`; aggregator `aggregate_paper2_amendment_012.py`. Every number
added to `audit_paper2_claims.py`.

## RESULTS (24 arms, 0 failures; audit 367 -> 380/380; 38 pp CAS / 30 pp IEEE)
- **BUG1 (cn) FIXED, conclusion holds.** Corrected C = 2*train/n_unique (C∝1/n, stronger reg as n
  grows). Harm persists and slightly deepens: ToN -10.62, PortScan -9.82 (vs C=1 -9.46/-7.04).
  Not a regularization artifact (P1). Manuscript numbers updated.
- **BUG2 (McNemar alpha) FIXED.** §3.5 now states CS use 0.10, McNemar its registered 0.05
  (stricter); homogeneous rerun at 0.10 still 0 commits / gain 0.00 in all 3 (P2).
- **BUG3 (no-probe commit) FIXED.** `--no-probe-policy reject`: no-probe triggers 0.6-1.0/stream,
  `commit_no_probe = 0` everywhere; causal result STRENGTHENS (ToN gate-naive +3.24 [1.68,4.93]
  full, +1.58 mild) -> every causal commit now probe-backed (P3).
- **CONFOUND4 — IMPORTANT RETRACTION.** Size-matched (2000) zero-drift: the harm VANISHES for RF
  (+0.01/+0.06/-0.00), LogReg, MLP (all ±0.1) but PERSISTS/deepens for SVC (a008 -4.81/-0.13/-5.76).
  -> the size-robust replacement harm is SVC-RBF-specific; the 512-budget harm for robust models was
  the size asymmetry. "Generalizes across 4 classifiers" RETRACTED and reframed (abstract, §5 header,
  Table 10 caption, Limitations all updated). P4 partially refuted -> honest correction.
- **#6 strict-> baseline.** Rejecting ties recovers 50-88% of eps=0 zero-drift harm at zero cost
  (ToN -0.25->-0.065, PortScan -1.11->-0.13, UNSW -0.56->-0.28); statistical gates add the residual
  + the guarantee. Added to §5.
- **#5 replacement-variance -> hypothesis** (frozen-transformer caveat; symmetric-preprocessing A/B
  named as decisive future control). **#8 Clopper-Pearson** on harmful-commit: eps=0 CI excludes 0
  (0.15-0.32), McNemar/EB-CS "0 observed, CP upper 0.12-0.17" not "eliminates". Highlights + abstract
  factorial-misreading fixed; Fig 8 title already fixed a011.
  **PENDING (user):** release v1.14.0 authorization; arXiv Paper 1, submit KBS.
