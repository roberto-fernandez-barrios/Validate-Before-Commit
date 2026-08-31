# Revision report — after the Knowledge-Based Systems rejection (KNOSYS-D-26-17242)

Date: 2026-08-31. Branch: `main`. Scope protocol: `notes/kbs_revision_editorial_protocol_001.md`.
Companion: `audits/kbs_response_to_reviewers.md` (proposed point-by-point response).

Section numbers refer to the revised `manuscript/main.tex` (§) and `manuscript/supplement.tex` (S).
The revision is editorial and structural only: **no experiment was run, no sealed CSV, raw output,
protocol, preregistration note or manifest was modified, and no numerical value in the manuscript
changed** (verified by a numeric-token diff of `main.tex` against the previous commit — zero removed
tokens — and by the 631-check claim audit).

---

## 1. Overall revision summary

| Item | Before | After |
|---|---|---|
| Abstract | 216 words, results and caveats interleaved | 236 words (audit method; limit 250), fixed order: problem → six-stage decomposition → three results → external scope → conclusion |
| Introduction | one 300-word paragraph carrying claim + results + caveats + scope; contribution list flat | single-message paragraphs; explicit "Scope of the net-harm findings" paragraph before any result; contribution hierarchy Primary / Secondary / Tertiary |
| §3.5 VBC-SG | 1,190 words, one 1,000-word paragraph | 884 words (−26 %), six labelled items (A)–(F); mechanics relocated verbatim to S2.13 |
| §3 overall | 2,467 words | 2,137 words (−13 %) |
| §5.2 | parity caveat only in §4.2.2 and §7 | explicit "What nominal sample-size parity does and does not match" paragraph next to the matched-size result |
| §5.6 | — | new "Comparison with strong baselines and alternative update policies" (485 words + table of 31 evaluated policy rows in five registered blocks) |
| Discussion | Q1–Q4 as four dense paragraphs | Q1–Q4 split into single-message paragraphs; new "Computational overhead of self-contained challengers" paragraph (operational implication, coarse measured wall-clock, not a benchmark) |
| Limitations / Conclusion | — | de-duplicated parity list (pointer to §5.2); configuration-dependence restated once in the Conclusion; stale S-pointer fixed |
| Supplement | — | S2.13 (relocated VBC-SG definitions); S0 provenance table pointers corrected and a baseline-comparison row added; S4 pointer updated |
| README / REPRODUCE | stale "§5.3" pointers; no reviewer map | "Reviewer quick map" (9 items) in README; all section pointers corrected; size-matched, chronological-matrix and baseline rows added to the claim → artifact table |
| Tests | 136 | 152 (new `tests/test_kbs_revision_guards.py`: 16 guards) |

Body length (tables and code excluded): 13,035 → ≈13,660 words. The net increase is entirely the
reviewer-requested additions (§5.6 ≈ 485 words, scope paragraph ≈ 150, §5.2 parity paragraph ≈ 170,
overhead paragraph ≈ 230, hierarchy labels ≈ 40 ≈ 1,075 words); excluding them the pre-existing text
shrank by ≈ 450 words (−3.5 %), concentrated in §3 (−13 %) and §3.5 (−26 %). The density target of
Task 2 was therefore met in the prioritized technical sections (§3.5) and partially in the
Introduction (−12 % on the pre-existing text; +2 % net after the scope paragraph and hierarchy that
Reviewer #2 and Task 4/11 required); §5.5 and the Discussion were split into single-message paragraphs
rather than shortened, because their remaining content is scope qualification that the guard tests
and the science require.

Compiled sizes: main 29 physical pages (27 numbered body pages after the graphical-abstract and
highlights sheets; CAS single column), supplement 37 pp, IEEE port 21 pp; zero undefined
references or citations in all three.

---

## 2. Reviewer #1

### R1.1 "The paper is not well-written and hard to read."

Changes (all in `manuscript/main.tex`; the IEEE port `main_ieee.tex` is regenerated mechanically):

- **Abstract** rewritten (Task 3 order). Shorter sentences; each result carries its own scope
  qualifier; "compatibility with a margin, not absence of an effect" stated in one sentence.
- **Introduction** (§1): paragraph 1 context (condensed); paragraph 2 central claim; paragraph 3
  *new* scope statement; paragraph 4 staged-evidence + "preregistered" definition; paragraph 5
  degradation–headroom regularity (shortened); paragraph 6 validate-before-commit as a family
  (shortened); contributions as three labelled tiers. The redundant restatement of the two
  controls' results (previously repeated three times in §1) was removed once.
- **§3.5** condensed to items (A)–(F) (see §5 of this report).
- **§5.1** finding (1)/(2)/(3) split into three paragraphs; **§5.4** two ~450-word paragraphs
  split into six; **§5.5** intro split (scope statement / historical diagnostic), robustness
  block split, evidence-map pointers corrected; **Discussion** Q1/Q2/Q4 shortened and split;
  **Limitations** "Prevalence, labels and probe representativeness" split into two paragraphs
  with a new lead ("Latency, adversaries and probe representativeness").

### R1.2 "There is no results comparisons with SoTA."

- **Audit of what already existed**: the program had evaluated always-deploy, sliding-window,
  calibrated soft ensemble, replay 50/50, unsupervised disagreement, ATC, DoC, DDM and ADWIN
  (validated against `river`), holdout, LCB, exact McNemar, Robbins CS, empirical-Bernstein CS
  (pooled and stratified), two-stage split, and VBC-SG (Cohort-sim / Refresh / Accumulate). Their
  numbers were in `table_policy_frontier` (supplement S2.12), `table_zero_drift` (S2.12),
  `table_budget_frontier` (S2.12), supplement S1.5 prose (ATC/DoC/replay), and S2.1 prose
  (DDM/ADWIN). The only main-body table was the conceptual positioning table.
- **New §5.6 + `tab:baselines`** (main body, `table*`): 31 rows grouped in five blocks with
  columns Policy · Labels at decision (monitoring labels folded in for DDM/ADWIN) · h′ vs h ·
  Reject · Probe-level guarantee · PortScan · UNSW-Recon · ToN-IoT · Labels. Block I: historical frozen
  harness (v2, seeds 104–133, full drift, paired). Block II: zero-drift control (amendment 008,
  seeds 104–133). Block III: exploratory harness v1 (seed-matched, unpaired; ATC/DoC/replay/
  disagreement). Block IV: lifetime-budgeted sequential gates (seeds 501–530; PortScan full vs
  ToN zero drift). Block V: self-contained challengers (seeds 3001–3030 / 4001–4030). The caption
  and the text state that only within-block contrasts are paired, that cross-block comparisons
  are descriptive and support no common ranking, and that Blocks I–IV are frozen-policy
  512/class evidence that should not be assumed to transfer.
- Three reading patterns are stated (only h′-vs-h rules convert the harm regime; label-free
  estimators pay for harm avoidance with benefit; statistical rules alone commit nothing under
  zero drift) with the cost-decision framing (utility scenarios in S2.12).
- **Related Work** now separates conceptual positioning (Table 1) from experimental comparison
  (§5.6); the Introduction contribution (3) points to §5.6.
- **Sources** (all sealed): `results/tables/paper2_policy_frontier_005/frontier.csv`,
  `paper2_amendment_006/summary.csv` (McNemar), `paper2_amendment_004/robustness.csv` (ADWIN),
  `paper2_amendment_008/summary.csv`, `paper2_phase2h_labelfree_gates_001/*.csv`,
  `paper2_phase2i_replay_baseline_001/summary.csv`, `paper2_final_q1/frontier_anchors.csv`,
  `paper2_final_q1/budget_frontier.csv`, `symmetric_pipeline_dynamic_001/paired_contrasts.csv`,
  `v1_22_1_editorial/evidence_validation_tradeoff.csv`. Every cell is re-checked against its CSV
  by `tests/test_kbs_revision_guards.py` (tolerance 0.006 pp; the supplement's own rounding of
  half-cent values is respected).
- **Nothing fabricated**: no method that was not run appears in the table.

---

## 3. Reviewer #2 — six comments

| # | Comment | Response / change | Location |
|---|---|---|---|
| 1 | Simplify abstract phrasing without losing the decomposition | Rewritten; six stages named once in order; one sentence per result with attached scope | Abstract |
| 2 | State in the Introduction that net-harm findings are configuration-dependent, not universal | New paragraph "Scope of the net-harm findings" (3rd paragraph, before any number): configuration-dependent; not claimed as universal properties of adaptive NIDS or retraining; traced to two asymmetries each isolated by a preregistered control; robust learners and self-contained size-matched configurations behave differently; "read every harm figure as a statement about the configuration that produced it". Conclusion restates it in one sentence. Abstract/Intro/Discussion/Conclusion checked for consistency; new guard against "adaptation is generally harmful" wording | §1 ¶3; §8 |
| 3 | Clarify in §5.2 that nominal sample-size matching ≠ effective information parity / temporal diversity | New paragraph after the matched-size result: 2,000 vs 2,000 rows/class matches nominal size only; not effective sample size, temporal coverage, temporal diversity, subtype support, duplication, label quality, prevalence, information content; pool draws with replacement; balanced pool sample, not time-ordered slice; the control isolates the nominal row-count factor (conclusion unchanged) | §5.2 |
| 4 | Condense §3.5's VBC-SG variants, keep the guarantee distinctions | §3.5 → (A) point/strict, (B) risk-controlled (McNemar, Robbins CS, EB-CS), (C) pooled vs stratified, (D) COMMIT/REJECT/DEFER + continuation modes named, (E) guarantee (per-proposal and deployment-long false probe-superiority), Proposition 1 statement, (F) not guaranteed (future accuracy/harm unless representativeness holds). Continuation-mode definitions, spending schedules, "levels used", fixed-sample stratified variant and the four stated properties relocated verbatim to S2.13 | §3.5; S2.13; S4 pointer |
| 5 | Brief discussion of computational overhead, self-contained vs frozen | New Discussion paragraph, explicitly "operational implication, not a benchmark": per-candidate scaler+PCA refit and one stored bundle per model at training time; inference structurally similar; no isolated timing study exists; only measured evidence = per-arm wall-clock in the completion markers — own/frozen 0.97× (18 matched pairs, 0.89–1.06); 2,000/class arms 1.2–1.5× the 512 arms (candidate-size cost); distinct from the ≈114× simulated quantum-monitor overhead. Derivation: `src/analysis/make_kbs_revision_runtime_summary.py` → `audits/pipeline_arm_wallclock_summary.csv` (outside `results/tables`, so the sealed manifest is untouched) | §6 |
| 6 | Supplementary references correctly linked and accessible | Full pointer audit (section 6 below); four stale pointers fixed; README reviewer map; guard test resolves every `\S S<n>.<m>` at every build | §5.5, §7, S0, README, REPRODUCE, tests |

---

## 4. New / strengthened SoTA comparison

See §2 (R1.2). Additional design decisions:

- The table is hand-maintained in `main.tex` (like the conceptual table) rather than generated,
  because it aggregates ten sealed CSVs from five blocks; integrity is enforced by the new test
  rather than by a generator. `tests/test_claims.py::test_main_tables_final_only` (which pins the
  set of `\input` tables) therefore needed no change.
- Block V uses the size-matched control (seeds 4001–4030) for the zero-drift rows so that every
  value is a direct CSV entry (no derived sums).
- The `93 %` pooled figure carries "approximate pooled" within the guard window and the `81 %`
  stratified figure within 400 characters, as the existing overclaim guards require.

---

## 5. Sections condensed or relocated

| Section | Action | Words |
|---|---|---|
| Abstract | rewritten | 216 → 236 |
| §1 Introduction | restructured; redundant restatement removed; scope paragraph + hierarchy added | 1,219 → 1,244 (pre-existing text −12 %) |
| §3.5 Risk-controlled gates | condensed to (A)–(F); mechanics → S2.13 | 1,190 → 884 (−26 %) |
| §3 whole | | 2,467 → 2,137 (−13 %) |
| §4.2.2 nested batches | parity list replaced by pointer to §5.2 | −45 |
| §5.5 | intro split; robustness split; evidence-map pointers fixed; stray sentence removed | 982 → 960 |
| §5.6 | new | +485 (+ table) |
| §6 Discussion | Q1/Q2/Q4 tightened and split; overhead paragraph added | 1,212 → 1,429 (−1 % excluding the new paragraph) |
| §7 Limitations | parity paragraph de-duplicated; long paragraph split; S5→S6 | ≈ unchanged |
| §8 Conclusion | tightened; configuration-dependence sentence | 211 → 230 |
| Supplement | + S2.13 (≈ 700 words relocated verbatim); S0 table rows; intro; S4 pointer | +1 page |

Nothing was deleted from the project: every definition removed from §3.5 is in S2.13 verbatim.

---

## 6. Artifact-link audit

Method: every `Supplementary \S S<n>[.<m>]` in `main.tex` was resolved against the compiled
supplement's actual section list (S0 … S8; S1.1–S1.7; S2.1–S2.13); every `\ref`/`\label`
resolved by the LaTeX build (0 undefined); every path cited in the supplement, README and
REPRODUCE checked for existence.

Found and fixed:

| Pointer | Was | Is | Where fixed |
|---|---|---|---|
| Benjamini–Hochberg multiplicity table | "Supplementary §S5" (S5 is the label ledger) | §S6 | main §7 |
| VBC-SG budget frontier table | §S2.8 (the superseded three-point sweep) | §S2.12 (+S2.13 for definitions) | main Table "evidence map", §5.5, S0 table |
| Ownership A/B (`table_ab_equivalence`) | "§S6" in the supplement's own S0 provenance table | §S2.12 | S0 table |
| Classifier/generator and mild-drift blocks | "§S1.5–S1.6", "§S2" | §S1.6 + S2.12; §S2.12 | main evidence map, §5.5 |
| "no mathematical novelty" pointer | §S2.8–S2.9 | §S2.9, §S4 | main §5.5 |
| README figure/section pointers | "§5.3" (pre-restructuring numbering) ×3; "policy-frontier table" unlocated | §5.5 / §5.6 / S2.12 / S2.2 | README |
| REPRODUCE claim → artifact table | "§5.3" ×5; stale "label-efficient gating" framing; "439-check audit" | §5.4 / §5.5 / S5 / S2.12; current title; "claim audit"; + size-matched, chronological-matrix and baseline rows | REPRODUCE |
| S4 proof scope pointer | "continuation modes of §3.5 of the main paper" | §S2.13 | supplement S4 |

Verified present and unchanged: `results/tables/paper2_final_q1/multiplicity.csv`,
`results/tables/symmetric_pipeline_dynamic_001/`, `results/tables/size_matched_own_transformer_001/`
(+ `CLAIM_INTERPRETATION.json` in both), `configs/*.json` (SHA-256 unchanged per audit),
`notes/*protocol*.md`, `results/final_experiment_ledger.csv`, `results/final_manifest.json`,
`results/tables/MANIFEST.sha256` (185 pins, byte-verified, untouched).

Added: README "Reviewer quick map" (main manuscript; supplement; preregistered protocols;
result tables; reproduction commands; symmetric-pipeline replication; size-matched replication;
chronological replay evidence; baseline/SoTA comparison evidence) with paths checked by
`test_readme_reviewer_quick_map_paths_exist`.

Not changed: provenance files (`docs/SCIENTIFIC_PROVENANCE.md`, notes, manifests) — the new
`notes/kbs_revision_editorial_protocol_001.md` is additive and dated.

---

## 7. Issues that could not be solved without new experiments

1. **Isolated compute benchmark, frozen vs self-contained.** Only whole-arm wall-clock exists;
   the manuscript reports it as coarse context and says so. A clean micro-benchmark (transformer
   fit time, bundle size, inference latency per flow) would be a new measurement.
2. **VBC-SG / quantum monitor / mild-drift matrix under self-contained, size-matched pipelines.**
   Still scoped to the frozen policy; §7 states it. The baseline table therefore cannot place the
   sequential gates on the same footing as Block V.
3. **Head-to-head paired comparison across blocks.** ATC/DoC/replay live on the exploratory
   harness (unpaired realizations); a paired re-run on the v2 harness would make Block III
   inferentially comparable with Block I. The table is explicit that it is descriptive across
   blocks.
4. **Full-drift size-matched arms; joint self-contained + size-matched + observed-data + real
   alarm + natural prevalence.** Unchanged limitation.
5. **Information-parity beyond nominal rows (temporal diversity, effective sample size).**
   Now stated explicitly in §5.2, but only a differently constructed control could test it.

None of these is required to answer the two reviews; items 1 and 3 are the ones most likely to
be raised again by a reviewer of the next venue (see section 10).

---

## 8. Scientific inconsistencies discovered

No numerical inconsistency between text and sealed outputs was found (audit 631/631).
Cross-reference inconsistencies (section 6): four main→supplement pointers and the supplement's
own S0 table pointed to the wrong sections; README/REPRODUCE carried pre-restructuring section
numbers. One wording inconsistency: the supplement caption and `frontier_anchors.csv` round
`−0.175` (zero-drift point gate) to `−0.17`; the new table follows the existing caption. The
replay-with-gate PortScan value (`8.255`) appears as `+8.26` in the existing supplement prose and
is kept identical in the new table.

---

## 9. Build / test results

Final state (after all edits):

- `python -m src.analysis.port_ieee` — `main_ieee.tex` regenerated from `main.tex`.
- `python -m src.analysis.build_pdfs` — main.pdf **29 pages** (27 numbered), supplement.pdf
  **37 pages**, main_ieee.pdf **21 pages**; **0 undefined references/citations** in all three logs.
- `python -m pytest tests -q` — **152 passed** (136 pre-existing + 16 new), ≈ 41 s.
- `python -m src.analysis.audit_paper2_claims` — **631/631 checks pass**.
- `python -m src.analysis.verify_results_manifest` — 185 pinned CSVs match `MANIFEST.sha256`.
- Numeric-token diff of `manuscript/main.tex` vs `HEAD` — **0 tokens removed**; added tokens are
  exclusively the new table cells, the wall-clock ratios (0.97, 0.89, 1.06, 1.2, 1.5, 18) and
  section/seed identifiers.
- Compiled PDFs are build products (git-ignored, as before); they were regenerated locally.

---

## 10. Remaining risks before resubmission

1. **Page count** rose from 27 to 29 physical pages (CAS) with the new table and the paragraph
   splits; still within the previous ≤ 33 budget, but the nine-column baseline table is
   typeset at reduced size (`resizebox`) and a two-column venue may need it moved to a
   landscape page or split into a properties table and an outcomes table.
2. **Block III (exploratory) numbers in a main-body table** could be challenged as
   lower-tier evidence; the caption and text label them as unpaired and descriptive, but a
   reviewer may still ask for a paired re-run of ATC/DoC on the v2 harness (section 7, item 3).
3. **Wall-clock figures** are coarse; a reviewer may ask for an isolated benchmark (section 7,
   item 1). The text already says none exists.
4. **Length.** The body is ≈ 13.7k words; the reviewer-requested additions offset the cuts.
   Further reduction would require removing scope qualifications that guard tests pin, or
   moving §5.5's mechanism/robustness paragraphs to the supplement (a structural decision for
   the authors).
5. **Front matter**: the only overfull box is the CAS title block (pre-existing, cosmetic).
6. **Release metadata** (`CITATION.cff`, `.zenodo.json`, Data Availability) still identify
   artifact v1.22.0 on purpose — the guard tests require it; a new release/DOI is a separate,
   authorized step.

---

## 11. Target-journal positioning and title

**Positioning.** The revised paper reads as an *evaluation-methodology* contribution for
adaptive security ML (comparability controls before promotion), with a decision-support
instrument (conditional validation, VBC-SG) as secondary. Venues where that framing fits, in
order of fit: *Expert Systems with Applications* or *Engineering Applications of Artificial
Intelligence* (Elsevier, CAS source reusable as is; both value preregistered, reproducible
applied ML); *IEEE Transactions on Dependable and Secure Computing* (the IEEE port builds; the
security-evaluation-discipline angle — TESSERACT/Arp et al. — is native there); *Journal of
Information Security and Applications* as the fallback in the authors' existing ladder
(`notes/paper2_venue_decision_003.md`). For any venue, the cover letter should lead with the
configuration-dependence of the harm result and the §5.6 comparison, which are the two points the
KBS reviews missed.

**Title.** Unchanged (pinned by `tests/test_scenario_a_claims.py`; the repository contains no
instruction authorizing editorial title changes). Three candidates if the authors choose to
revisit it:

1. *Is the Challenger Comparable? Construction and Evidence Controls Before Promoting Retrained
   Intrusion Detectors*
2. *Candidate Comparability Before Promotion: When Validation Helps — and When It Does Not — in
   Adaptive Network Intrusion Detection*
3. *Drift Alarms Propose, They Do Not Promote: Comparability Controls and Conditional Validation
   for Adaptive Intrusion Detection*

Recommendation: keep the current title; candidate 3 is the most discoverable if a change is ever
made.

---

## 12. Files changed in this revision

- `manuscript/main.tex` (all sections listed above), `manuscript/main_ieee.tex` (regenerated),
  `manuscript/supplement.tex` (S0 table, intro, S2.13, S4 pointer)
- `README.md` (reviewer quick map, pointers, structure), `REPRODUCE.md` (framing, pointers, rows)
- `src/analysis/make_kbs_revision_runtime_summary.py` (new), `audits/pipeline_arm_wallclock_summary.csv` (new, derived)
- `tests/test_kbs_revision_guards.py` (new)
- `notes/kbs_revision_editorial_protocol_001.md` (new, additive)
- `audits/kbs_rejection_revision_report.md`, `audits/kbs_response_to_reviewers.md` (this audit trail)

Not touched: `results/**`, `configs/**`, existing `notes/**`, `docs/**`, `manuscript/tables/**`,
`manuscript/references.bib`, `CITATION.cff`, `.zenodo.json`.
