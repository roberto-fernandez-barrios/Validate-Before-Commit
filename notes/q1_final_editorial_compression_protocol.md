# Q1 Final Editorial Compression & Scope Hardening — Frozen Protocol (v1.20.2)

**Status:** FROZEN before any edit. Amendments only via dated appendix.
**Baseline:** v1.20.1 (A' `1befbf5`, B' `8f1a431` = HEAD, DOI 10.5281/zenodo.21480893).
pytest 66/66, audit 521/521, hashes 164/164, PDFs 32/24/24. Main body word count
(from `\begin{abstract}`): **19,413**. All 164 scientific CSVs SHA-256-frozen in
`scratchpad/csv_baseline_v1201.json`.

## Scope — exclusively textual/editorial

No experimental runner, no scientific configuration, no seeds, no raw outputs, no primary
figures, no multiplicity results, no scientific CSV contents, no Paper 1 reference, no
PLAN_Q1_DEFINITIVO_VBC.md. Any scientific CSV byte-change ⇒ stop and revert.

## Density objective

Reduce main.tex narrative by **8–12%** (target ≈1,600–2,300 words; hard cap 15%), primarily
by relocating forensic/changelog detail (Supplement/notes already carry the full history) and
deduplicating repeated claims. Priorities per mission: Intro contributions ¶, §4 protocol
history, §5.1 tiers (≈half), §5.3 forensic phrases, §5.4 repetition, §5.5 prior-replay
history, §6 result repetition, §7 thematic grouping, §8 conclusion (−25%). Style: ≤220-word
paragraphs where reasonable, split >50–55-word sentences, cut multi-parenthetical asides.
All load-bearing limits preserved verbatim in meaning.

## Exact claim list to retouch (C-blocks, mandatory)

C1 remove causal-inference language: "causal arm/genuinely causal/causal result/causal
experiment" → "leakage-free observed-data (policy-evaluation) arm", "free of
simulator-oracle information and train/future leakage"; "causal" survives only in "causal
information availability" (temporal availability sense) with rewording where ambiguous;
Table 4 title → "Final leakage-free observed-data policy-evaluation arm". No claim of causal
estimand/identification.
C2 separate pooled empirical control vs stratified formal guarantee (mandated sentence).
C3 cap-vs-total: every "512-flow probe cap" clarified with ≈578 (pooled) / 580 (Cohort-sim)
/ 579 (Refresh) adjudicated labels/proposal after deferrals; abstract uses the compact form.
C4 "realistic cost" → "adjudication count under the evaluated protocol" + mandated sentence;
unmodeled costs kept explicit.
C5 detector identity secondary only *conditional on a comparable proposal being generated* +
imbalance caveat sentence.
C6 "reliable safeguard" → "direct safeguard is candidate–incumbent validation" + mandated
formal-control sentence distinguishing point/strict/stratified.
D1 "operating point we recommend" → descriptive/first-evaluated phrasing. D2 scaler
mechanism always scoped to evaluated SVC-RBF pipeline. D3 hierarchical model = supporting
predictive/robustness evidence (never independent confirmation/proof), caveats retained.
D4 captions: Table 9 ≤120w, Table 10 ≤100w, Table 11 ≤120w (via generators). D5 optional
review-artifacts zip (existing files only).

## Files permitted

main.tex; main_ieee.tex (ported); supplement.tex (receiving relocated text/consistency);
highlights.md; README.md; REPRODUCE.md; table generators (captions only);
audit_paper2_claims.py; textual/claim-scope tests; claim-scope generator; this protocol +
compression report + checkpoint; version metadata; MANIFEST.sha256/ledger only if mechanical
regeneration requires; final_manifest.json only in Commit B.

## Allowed regeneration

Table generators (existing CSV readers), port_ieee, build_pdfs, claim-scope audit,
audit_paper2_claims, verify_results_manifest, pytest, make_final_experiment_ledger,
make_final_manifest (sealing phase). Forbidden: any run_paper2_*/run_q1_* runner or
raw-output regeneration.

## Acceptance / stopping rule

(1) word reduction in [8%,12%] (≤15%); (2) C1–C6 applied and guarded; (3) all 164 CSV hashes
byte-identical to baseline; (4) harm 520/340/180/506/14/0, families 6/15/7, survivors
3/6·13/15·7/7 untouched; (5) pytest/audit/hashes/PDFs green, 0 orphans, 0 undefined refs,
0 control chars; (6) hostile-review checkpoint answers the 15 questions with READY verdict;
(7) seal v1.20.2 (Commit A → manifest → Commit B → tag → Release → Zenodo); (8) after
sealing, the review cycle is CLOSED — no further iterations except editor/reviewer-mandated.
