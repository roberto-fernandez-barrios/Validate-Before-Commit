# Proposed response to reviewers — KNOSYS-D-26-17242 (internal audit trail)

Manuscript: *Candidate Comparability Before Promotion: Conditional Validation in Adaptive
Network Intrusion Detection* (rejected by Knowledge-Based Systems; revised 2026-08-31 for
submission elsewhere). Section numbers below refer to the revised `manuscript/main.tex`
(§) and `manuscript/supplement.tex` (S). No experiment was re-run and no number changed;
every revision is editorial, structural or a cross-reference correction.

We thank both reviewers. The revision addresses every comment as follows.

---

## Reviewer #1

**R1.1 — "The paper is not well-written and hard to read."**

We agree that the previous version stacked several caveats, experiments and guarantees into
single sentences. The revision applies a "one scientific message per paragraph" rule to the
sections a reader meets first and to the densest technical sections:

- *Abstract* rewritten in a fixed conceptual order — problem → six-stage decomposition →
  result 1 (frozen preprocessing amplified apparent harm) → result 2 (candidate evidence
  explains the residual zero-drift harm; matched-size means compatible with the ±0.5-point
  margin, PortScan boundary-close) → result 3 (validation is valuable under asymmetry, adds no
  detectable average benefit in the size-matched zero-drift control) → external scope
  (chronological replays) → conclusion. 236 words (audit count).
- *Introduction* restructured into single-message paragraphs, with an explicit early
  "Scope of the net-harm findings" paragraph and an explicit contribution hierarchy
  (primary: candidate comparability; secondary: conditional validation; tertiary: VBC-SG,
  quantum-monitor diagnostic, chronological and operational boundaries).
- *§3.5 (risk-controlled gates / VBC-SG)* condensed from one 1,000-word paragraph into six
  labelled items — (A) point/strict validation, (B) risk-controlled validation, (C) pooled
  versus stratified guarantees, (D) COMMIT/REJECT/DEFER, (E) what VBC-SG guarantees, (F) what
  it does not guarantee. Implementation-level definitions (continuation modes, spending
  schedules, the four stated properties) moved verbatim to Supplement S2.13; the proof stays
  in S4. Nothing was deleted from the project.
- *§5.1, §5.4, §5.5, Discussion* split into shorter paragraphs; repeated limitations were
  removed where they were restated and kept where they matter scientifically (§5.2, §7).

**R1.2 — "There is no results comparison with SoTA."**

The comparisons existed but were scattered across the supplement and the historical
sections, and the only table in the main body was a *conceptual* positioning table. The
revision adds a dedicated subsection, **§5.6 "Comparison with strong baselines and
alternative update policies"**, with a compact table (`tab:baselines`) built exclusively from
the sealed outputs. It covers every alternative the program actually evaluated:

- label-free update rules: always-deploy, sliding-window update, calibrated soft ensemble,
  replay retraining, unsupervised disagreement gate;
- label-free accuracy estimators used as gates: ATC and DoC;
- performance-aware monitors cross-checked against `river` reference implementations:
  DDM and ADWIN;
- statistical commit rules: fixed-sample LCB, exact McNemar, anytime-valid confidence
  sequences, and the lifetime-budgeted VBC-SG family (Cohort-sim / Refresh);
- the two-stage split gate and the holdout gate.

For each policy the table reports the target labels required at the decision, monitoring
labels, whether the rule explicitly compares challenger against incumbent, whether it can
reject a deployment, its probe-level guarantee, and its outcome in the benefit, marginal and
harm regimes (plus total labels). Because these results come from different registered
blocks, the table is grouped by block (historical frozen harness; zero-drift control;
exploratory harness; lifetime-budget frontier; self-contained pipelines), states which
contrasts are paired, and explicitly supports no cross-block ranking. Related Work now
distinguishes the conceptual positioning (Table 1) from this experimental comparison, and the
Introduction points to it. We did not add comparisons with methods that were never evaluated.

---

## Reviewer #2

**R2.1 — Simplify the abstract without sacrificing precision on the decomposition of the
update pipeline.**

Done (see R1.1). The six stages are now named once, in order, in a single sentence, and each
result is stated in its own sentence with its scope qualifier attached (frozen preprocessing
→ full drift; evidence disadvantage → zero drift; "compatibility with a margin, not absence of
an effect"; validation's value "mainly under asymmetric or uncertain candidate conditions").

**R2.2 — State explicitly in the Introduction that the net-harm findings are
configuration-dependent artifacts, not universal operational properties.**

Added as the third paragraph of the Introduction ("Scope of the net-harm findings"), before
any result is quoted. It states that the net-harm observations were produced by specific
candidate-construction and evidence conditions; that they are not claimed as universal
properties of adaptive NIDS or of retraining; that the program traces the mean harm to two
asymmetries (frozen incumbent-owned preprocessing under full drift; a four-fold nominal
evidence disadvantage under zero drift), each isolated by a preregistered control; and that
robust learners and self-contained, size-matched configurations behave differently. The
Conclusion now repeats the point in one sentence, and the Abstract, Introduction, Discussion
(Q1, Q4) and Conclusion were checked for mutual consistency. A guard test now fails if any
"adaptation is generally harmful" wording reappears on a claim surface.

**R2.3 — Clarify in §5.2 that nominal sample-size matching does not equate to effective
information parity or temporal diversity.**

Added directly after the matched-size result in §5.2 ("What nominal sample-size parity does
and does not match"). It states that 2,000 rows/class versus 2,000 rows/class matches nominal
sample size only and does not establish equality in effective sample size, temporal
coverage, temporal diversity, subtype support, duplication, label quality, prevalence or
information content; that pool draws are with replacement; that the candidate batch is a
controlled balanced sample rather than a time-ordered slice; and that, within those
conditions, the experiment isolates the nominal row-count factor. The size-control conclusion
itself is unchanged.

**R2.4 — Condense §3.5's description of the VBC-SG variants while retaining the essential
guarantee distinctions.**

Done (see R1.1). The main text keeps the distinctions a reader needs: point/strict versus
risk-controlled rules; pooled versus stratified (balanced-accuracy-aligned) guarantees;
COMMIT/REJECT/DEFER; the per-proposal and deployment-long false-probe-superiority bound; and
the explicit statement that none of this bounds future deployment accuracy or harm unless the
probe is representative of the deployment horizon. VBC-SG is presented as a secondary
decision-support instrument with no claim of mathematical novelty. The secondary variants and
mechanics are in Supplement S2.13.

**R2.5 — Add a brief discussion of computational overhead differences between
self-contained and frozen-transformer pipelines.**

Added to the Discussion ("Computational overhead of self-contained challengers — operational
implication, not a benchmark"). Because no isolated timing study of the two policies exists
in the artifact, we did not invent one. The paragraph explains qualitatively that a
self-contained challenger refits its scaler and PCA on its own candidate batch (additional
training-time computation and one stored bundle per deployed model) while inference cost is
structurally similar under both policies, and reports the only measured figures that exist —
the coarse per-arm wall-clock recorded with every confirmatory arm: own-transformer arms took
0.97× the wall-clock of their frozen counterparts (18 matched pairs, range 0.89–1.06), so the
refit is invisible at whole-arm granularity, whereas the 2,000-per-class arms of the
size-matched control took 1.2–1.5× the 512-per-class arms — a cost of candidate evidence, not
of preprocessing ownership. The paragraph explicitly distinguishes this from the ≈114×
simulated overhead of the quantum-kernel *monitor*. The derivation script and CSV are in the
artifact (`src/analysis/make_kbs_revision_runtime_summary.py`,
`audits/pipeline_arm_wallclock_summary.csv`).

**R2.6 — Ensure all supplementary references cited in the main text are correctly linked and
accessible within the artifact.**

We audited every main → supplement pointer against the compiled supplement and found four
stale ones, all corrected: the multiplicity table was cited as S5 (it is S6; S5 is the label
ledger); the VBC-SG budget frontier was cited as S2.8 (its table is in S2.12); the
supplement's own provenance table sent the ownership A/B control to S6 (it is in S2.12); and
the classifier/generator and mild-drift blocks now point to the subsections holding their
tables. README and REPRODUCE pointers that still referred to a pre-restructuring "§5.3" were
updated to the current sections, a "Reviewer quick map" was added to the README listing the
main manuscript, supplement, preregistered protocols, result tables, reproduction commands,
the two replication drivers, the chronological evidence and the baseline comparison, and a
new guard test resolves every `\S S<n>.<m>` pointer in the main text against the supplement's
actual section structure at every build.

---

## Changes not requested by the reviewers

- Evidence-tier language, preregistered outcome rules, statistical families, the PortScan
  boundary-close caveat, the ATTENUATION outcome, the fresh-seed/paired/multiplicity
  statements and every numerical value are unchanged (verified by the 152-test guard suite and
  the 631-check claim audit, plus a numeric-token diff of `main.tex` against the previous
  commit showing no removed values).
- The title is unchanged.
