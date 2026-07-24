# Q1 FINAL NARRATIVE REBUILD — BASELINE

Recorded before any editorial change on branch `editorial/q1-final-narrative-rebuild`.

## Starting point

- **Source branch:** `main`
- **Source commit (HEAD):** `1e0c72ff02f79b0b6f9378805e6fdc31e62178a8` — "Stamp v1.22.2 final artifact manifest"
- **Last tag:** `v1.22.2` (editorial); last *scientific* sealing tag `v1.22.0` @ `43d9c255af48db9bcc3c6eb341a153381b18c8e8`
- **Size-matched control integration:** run sealed at `c4df062` (freeze) / `3f3a401` (analysis tables), manuscript integration at `d2de866` + `cccc5e4`, sealed as v1.22.0 (`43d9c25`), editorially scoped in v1.22.1 (`46f2aab`…`0a5998c`) and microcorrected in v1.22.2 (`f729d80`, `1e0c72f`).
- **Working tree at branch creation:** clean except two untracked files that predate this phase and are left untouched: `PLAN_Q1_DEFINITIVO_VBC.md` (the instruction document for this phase) and `notes/recovered_run_q1_faseC.py.txt` (recovered frontier driver, documented in project memory).

## Sealed scientific results (unchanged by this phase)

- Symmetric-pipeline dynamic replication `symmetric_pipeline_dynamic_001` (seeds 3001–3030, Scenario A): frozen config SHA-256 `5279…40e8`, 42/42 arms complete.
- Size-matched own-transformer control `size_matched_own_transformer_001` (seeds 4001–4030): frozen config SHA-256 `6873…df60`, 21/21 arms complete, registered outcome **ATTENUATION** (`CLAIM_INTERPRETATION.json`, follow_up_authorized=false, 999 nested pairs verified).
- Headline effects pinned by audit SP7: +7.21 / +2.55 / +1.03 (full-drift own-naive vs never), +5.98 (ToN ownership interaction), −1.74 / −0.65 (zero-drift 512 residual), +1.68 (strict vs naive PS zero); size effects +1.89 / +0.63 / +0.23; naive-2000 vs never +0.19 / −0.02 / −0.01 (CI90 inside ±0.5 in 3/3).
- 13 chronological replays: no net harm of always-deploy vs never-adapt observed.

## Gates at baseline (all green)

- `pytest tests -q`: **135 passed** (53 s).
- `python -m src.analysis.audit_paper2_claims`: **all checks PASS** (v1.22.2 guard set).
- `python -m src.analysis.verify_results_manifest`: **185 pinned CSVs match MANIFEST.sha256, 0 unpinned extras**.
- Interpreter: conda env `paper2` (Python 3.11.15).

## Manuscript metrics at baseline

| Artifact | Pages | Body prose words | Sections | Subsections | Figures | Tables (env) | Table inputs |
|---|---|---|---|---|---|---|---|
| main.pdf (CAS) | 33 | 14,679 | 12 | 15 | 1 (+GA) | 1 inline | 13 |
| main_ieee.pdf | 25 | 14,497 | 9 | 15 | 1 | 1 inline | 13 |
| supplement.pdf | 30 | 6,535 | 9 | 18 | 9 | 0 inline | 17 |

- Title at baseline: *Validate Before Commit: A Controlled Study of Pipeline Construction, Evidence Asymmetry, and Candidate Promotion in Network Intrusion Detection*.
- Abstract at baseline: ~285 words, ~20 numeric values, chronology-ordered ("In our original experiments…").
- Contributions: 3 (decomposition; two asymmetries; conditional gate value).
- Results order at baseline: 5.1 historical frozen-policy diagnostic → 5.2 symmetric replication → 5.3 size-matched control → 5.4 v1 summary → 5.5 confirmatory/observed-data → 5.6 risk-controlled governance → 5.7 operational and chronological boundaries.

## Editorial guard surface (must be honored or additively updated)

- `audit_paper2_claims.py` pins ~120 manuscript-text checks (phrases, headline numbers, DOIs, sealed CSV cross-checks). Title check T1 pins the v1.22 title on 5 surfaces; the established repo pattern for title changes is an additive guard update retiring the previous title (as v1.22 did with the v1.21 title).
- `tests/test_scenario_a_claims.py` (NEW_TITLE), `tests/test_v1_22_1_editorial_guards.py` (abstract must contain exactly one ATTENUATION sentence; highlights format 3–5 bullets ≤85 chars; graphical-abstract script must keep "ZERO-DRIFT CONTROL", "nominal size parity", "0.5"), `tests/test_size_matched_claims.py`, `tests/test_q1_claim_scope.py`, `tests/test_claims.py` pin further claim surfaces.
- All required scoping phrases (ATTENUATION, margin-dependence, nominal-parity caveats, frozen-policy scoping, chronological no-net-harm, 506-commit clustering, Cohort-sim, etc.) are preserved verbatim in the rebuild.

## Files that WILL be modified in this phase

`manuscript/main.tex`, `manuscript/main_ieee.tex`, `manuscript/supplement.tex` (light, cross-reference/relocation only), `manuscript/highlights.md`, `src/analysis/make_paper2_graphical_abstract_final.py` + regenerated `docs/img/graphical_abstract.png`, `README.md`, `CITATION.cff`, `.zenodo.json`, `tests/test_scenario_a_claims.py` + `src/analysis/audit_paper2_claims.py` (title-guard retirement only, additive), `notes/Q1_FINAL_*` notes.

## Files that will NOT be touched

`results/raw/**`, `results/tables/**` (sealed CSVs + MANIFEST.sha256), `results/final_manifest.json`, `configs/**`, `src/experiments/**`, `data/**`, all registered protocol notes, all sealed checkpoints, `references.bib` scientific entries (metadata-only edits allowed if title consistency requires), the pending Paper 1 reference (explicitly out of scope).
