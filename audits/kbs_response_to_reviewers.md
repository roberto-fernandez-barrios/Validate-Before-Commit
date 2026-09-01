# Proposed response to reviewers — KNOSYS-D-26-17242 (internal audit trail)

Manuscript: *Candidate Comparability Before Promotion: Conditional Validation in Adaptive
Network Intrusion Detection* (rejected by Knowledge-Based Systems; revised 2026-08-31 and
extended 2026-09-01 for submission elsewhere). Section numbers below refer to the final
`manuscript/main.tex` (§) and `manuscript/supplement.tex` (S) after the post-KBS
integration. The editorial revision of 2026-08-31 re-ran no experiment; the 2026-09-01
integration adds two registered confirmatory blocks whose protocols were frozen before
implementation (B2: size-matched challengers under drift, seeds 6001–6030; B1: a
common-harness comparison with published and reference baselines, seeds 5001–5030). No
sealed historical output was altered.

We thank both reviewers. The revision addresses every comment as follows.

---

## Reviewer #1

**R1.1 — "The paper is not well-written and hard to read."**

We agree that the previous version stacked several caveats, experiments and guarantees into
single sentences. The revision applies a "one scientific message per paragraph" rule to the
sections a reader meets first and to the densest technical sections:

- *Abstract* rewritten from scratch in a fixed conceptual order — problem → what is
  decomposed → result 1 (frozen preprocessing amplified apparent harm) → result 2 (candidate
  evidence matters at zero drift and, materially, under real drift: +0.82/+1.66/+1.00 BA
  points) → result 3 (validation is conditional; no average benefit at parity) → result 4
  (registered common-harness comparison; no policy dominates) → conclusion. About 210 words;
  no VBC-SG, protocol-history or quantum detail.
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

We took this comment as a request for an experimental comparison under one harness, not
for a conceptual table, and we answer it in two parts.

*(a) A registered common-harness comparison was run (new §5.6, Table `tab:common_harness`;
Supplement S10).* Under the final trusted configuration — self-contained challengers on
bit-identical raw streams at nominal 2,000-per-class evidence parity, with a 512/class
sensitivity block — we evaluated, on 30 fresh seeds and six scenarios, the two standard
published label-free accuracy estimators used as promotion rules (ATC, Garg et al. 2022;
DoC, Guillory et al. 2021), the `river` 0.25.0 reference implementations of DDM and ADWIN
as retraining triggers, a calibrated soft ensemble and replay-50/50 retraining as standard
baselines, and our own anchors (never-adapt, always-deploy, point and strict gates). The
protocol, its pre-implementation amendment (primary comparison at evidence parity,
magnitude-aware per-cell classification, documented information budgets) and the analysis
script were committed before any result existed. The registered outcome is reported
literally: at parity under full drift ATC and the calibrated ensemble are COMPATIBLE with
always-deploy (CI90 within ±0.5 points) while DoC, replay, river-DDM and river-ADWIN pay
MATERIAL COSTS; at zero drift no policy has a loss left to avoid; ATC is compatible with the
point gate on five of six scenarios; and the registered ordering-change rule fires for ATC
and the ensemble — the apparent ranking of update policies depends on whether the candidate
generator is comparable. Nothing is called a state-of-the-art adaptive-NIDS method, and the
comparison is presented as a map of accuracy/label/update trade-offs, not a ranking.

*(b) What was not done, and why.* We did not reproduce an end-to-end published adaptive-NIDS
system, because under the frozen selection criteria (same decision problem, public
reproducibility, dataset compatibility, no privileged information, checkable fidelity) none
matched the decision problem and information interface of this study: the closest security
systems reject individual samples or adapt continuously (Transcend/Transcendent, CADE,
INSOMNIA) rather than deciding whether a specific retrained challenger replaces the
incumbent, and the cost-schedule formulations (CARA, Regol, IGPC-MSOS) require inputs their
papers do not supply for this harness. Reconstructing such a system from partial descriptions
and presenting the result as its reproduction would not be a faithful comparison; the
manuscript states this limitation explicitly (§5.6, §7) and the historical single-block
comparisons remain available in Supplement S2.12 with their evidence tiers. Related Work
distinguishes the conceptual positioning table from the experimental comparison.

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

Added directly after the matched-size result (now §5.3, "What nominal sample-size parity does
and does not match"). It states that 2,000 rows/class versus 2,000 rows/class matches nominal
sample size only and does not establish equality in effective sample size, temporal
coverage, temporal diversity, subtype support, duplication, label quality, prevalence or
information content; that pool draws are with replacement; that the candidate batch is a
controlled balanced sample rather than a time-ordered slice; and that, within those
conditions, the experiment isolates the nominal row-count factor. The zero-drift size-control
conclusion itself is unchanged (registered outcome ATTENUATION). The integration adds the
registered full-drift size control (§5.4, Supplement S9): the same nested 512→2,000
intervention improves promotion outcomes by +0.82/+1.66/+1.00 BA points under real drift
(HOMOGENEOUS-SIZE BENEFIT), which answers the natural objection that the zero-drift null was
expected of exchangeable re-draws; the manuscript states that nominal rows are still not
effective information and claims no universal monotonic benefit from more data.

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

- Post-KBS integration (2026-09-01): the manuscript was rebuilt around the final thesis
  hierarchy (primary: candidate comparability of construction and evidence; secondary:
  conditional validation; tertiary: formal, diagnostic and operational instruments). The
  interpretation moved from "harmful promotion → gate rescues" to "apparent promotion
  behaviour depends on comparable construction and evidence": the historical frozen
  configuration is now §5.1, construction §5.2, evidence at zero drift §5.3, evidence under
  drift §5.4 (new), conditional validation §5.5, the registered common-harness comparison
  §5.6 (new), and the mechanism/formal/chronological/operational instruments §5.7. A central
  CSV-generated evidence matrix (Table `tab:synthesis`) opens the Results. VBC-SG is
  de-emphasized to a formal instrument (its guarantee, non-guarantee, cost, abstention and
  chronological conservatism kept; implementation detail in S2.13). Validation is never
  called necessary, generally safer, superior or the recommended default; 0/6 positive gate
  effects at parity under drift and the resolved strict-gate cost are reported.
- The historical compact baseline table left the main body (full matrix retained in S2.12);
  the symmetric-replication guardrail panel moved to S7; B2 and B1 full matrices, statements
  and budgets are S9 and S10.
- Evidence-tier language, the preregistered outcome rules, the statistical families, the
  PortScan margin-dependence caveat, the ATTENUATION outcome of the zero-drift control, the
  fresh-seed/paired/multiplicity statements and every sealed numerical value are unchanged
  (guard suite, 631-check claim audit, 185 sealed CSVs byte-verified, numeric-token diff
  against the previous commit with every removed and introduced scientific number
  accounted for in `audits/post_kbs_final_manuscript_hostile_review.md`).
- The title is unchanged. The artifact version and DOIs are unchanged; the two new blocks
  are identified as post-v1.22 registered results pending a sealed release.
