# KBS FINAL FOCUS CUT — BASELINE

Recorded before the final editorial focus cut, on branch `editorial/kbs-final-focus-cut`.

## Provenance

- **Branch created from:** `main` @ `49ade7fcb3efc185e94f7f53ba0557caf7480dbc` ("Record v1.22.3 Zenodo publication").
- **Sealing tag:** `v1.22.3` → `3fbe1e64f49c36f12f1615d24c262ca40fcf8a90` (unmoved; the documentation commit `94b8931` and the Zenodo commit `49ade7f` sit after it).
- **Untracked, left untouched:** `PLAN_Q1_DEFINITIVO_VBC.md`, `notes/recovered_run_q1_faseC.py.txt`, `dist/` (v1.22.3 release build outputs).

## Manuscript metrics (baseline)

- **Title:** Candidate Comparability Before Promotion: Conditional Validation in Adaptive Network Intrusion Detection.
- **Abstract:** 221 words.
- **Main-body prose:** 13,210 words. **IEEE body:** 12,886. **Supplement:** 6,535.
- **Pages:** main **32**, supplement **30**, IEEE **24**.
- **Main figures:** 2 (Fig. 1 decision pipeline; Fig. 2 per-trigger degradation/headroom) + graphical abstract.
- **Main `\input` tables:** 13.

### Section prose lengths (main)

| Section | Words |
|---|---|
| §5.5 Mechanism, formal and operational extensions | **4,111** |
| Discussion | 1,077 |
| Limitations | 1,093 |
| Conclusion | 249 |

§5.5 alone is 31% of the body and holds 8 secondary tables — the primary compression target.

### Current main-body table order (Tables 1–15 mapping)

| main `\input` | subsection | disposition |
|---|---|---|
| table_symmetric_pipeline | §5.1 ownership | KEEP (primary) |
| table_symmetric_security | §5.1 guardrails | KEEP (boundary) |
| table_size_matched | §5.2 size | KEEP (primary) |
| table_evidence_validation_tradeoff | §5.3 validation | KEEP (primary; audit-pinned in main) |
| table_chronological_q1 | §5.4 chronological | KEEP (boundary) |
| table_policy_frontier | §5.5 | MOVE → supplement |
| table_causal_probe | §5.5 observed-data | MOVE → supplement |
| table_harm_generality | §5.5 mild drift | MOVE → supplement |
| table_zero_drift | §5.5 frozen zero-drift | MOVE → supplement |
| table_ab_equivalence | §5.5 A/B ownership | MOVE → supplement |
| table_amendment009 | §5.5 classifier/generator (≈Table 13) | MOVE → supplement |
| table_budget_frontier | §5.5 VBC-SG frontier (≈Table 14) | MOVE → supplement |
| table_operational_e2e | §5.5 acquisition yield (≈Table 15) | MOVE → supplement |

The two in-body figures and the inline evidence-map `tabular` (`tab:evidence_map`) are not `\input` tables. New main will keep 5 `\input` tables + 1 compact evidence-map table.

## Genealogy / defensive expressions found in main.tex

- Genealogy: `harness v1` (2), `harness v2` (1), `pristine seeds` (5), `Six tiers of evidence` (1), tier markers `(i$'`, `(i$''` (3), `historical convention` (4), `historical frozen-policy` (2), `frozen-initial-transformer` (2).
- Defensive/self-justifying: `we say so plainly`, `rather than hide`, `honest conclusion`, `honest summary`, `reported as-is`, `we prove nothing stronger`, `kept distinct`, `to close the forking-paths`, `the error was`, `earlier claim`, `the objection`.
- Each to be neutralized in FASE 4 (caveats retained, self-justification removed).

## Guard dependencies to honor during the cut

- `tests/test_claims.py::test_main_tables_final_only` pins the exact `\input` sets: `FINAL_BODY_TABLES` (main + IEEE) and `V1_SUPPLEMENT_TABLES` (supplement). **Moving 8 tables requires updating both sets** (remove from body set, add to supplement set).
- Moved tables' in-body `Table~\ref{...}` must become plain "Supplementary \S SX" text (cross-document `\ref` does not resolve).
- Caption content in `manuscript/tables/*.tex` is audit-pinned (e.g. `acquisition yield`, `historical frozen-policy diagnostic`, `centered paired bootstrap`) — **do not edit the generated table `.tex` files**; only relocate their `\input`.
- Required in-main phrases stay verbatim: ATTENUATION, `within triggered decisions`, `non-vacuous within the evaluated`, `leakage-free observed-data`, `not independent trials`, `under the historical frozen`, `only under zero drift`, `sample-size parity`, nominal-vs-effective caveat, `net harm remains unobserved`, `unresolved counterexample`, Cohort-sim, `controlled balanced-probe`, DOIs and sealing commit.

## Baseline gates (all green)

- `pytest tests -q`: **135 passed**.
- `audit_paper2_claims`: **630/630 pass**.
- `verify_results_manifest`: **185/185 match, 0 unpinned extras**.
- PDFs build clean: main 32 pp, supplement 30 pp, IEEE 24 pp.

## Compression targets (orientation)

- Main-body words: 13,210 → **10,800–11,500**.
- Main PDF: 32 → **27–29 pp**.
- Reduction sourced from: relocating the 8 §5.5 tables, removing genealogy/amendment narrative, compressing §5.5 to 4 paragraphs (~1,100 words), −20–30% Discussion, consolidated Limitations, simpler captions, removed self-justification. **Not** from cutting load-bearing limits, negative results, scope, reproducibility methods, the size-matched result, or the chronological boundary.
