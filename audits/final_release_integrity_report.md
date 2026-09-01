# Final release integrity report — v1.23.0 (independent release-engineering audit)

Generated 2026-09-01T10:35:33Z. Scope: the sealing of the two registered post-KBS blocks into the public
artifact. This audit does not evaluate the science; it checks that what is sealed is exactly
what was produced, that nothing historical moved, and that provenance is complete.

## 1. Starting state (Step 0)
- Branch `post-kbs-hardening` at `19d5a8039d9122b0315fa15e27d8f1e00ce58d52`, clean tree.
- `main` = `origin/main` = merge-base = `57ef8e7`; 0 commits on `main` not in the branch,
  8 branch commits ahead → pure fast-forward (performed as a pointer move; no merge commit).
- `origin` = https://github.com/roberto-fernandez-barrios/Validate-Before-Commit.git (fetch
  and push). Latest tag `v1.22.9` (473cf37).

## 2. Frozen scientific surface (Step 1)
Pre-seal inventory hashed at `19d5a80`: 5 manuscript sources, 100 protocol/amendment/
checkpoint notes, 6 configs, 185 pinned CSVs (manifest hash == disk hash for every entry),
22 post-KBS CSVs, 2 verdict JSONs. Stored as a machine-readable JSON in the session
scratchpad; the checks below were re-run against it after every edit.

## 3. The 22 unpinned outputs (Step 2)
Identified independently from `verify_results_manifest` output (22 lines "not pinned"),
not from the phase report. Classification: 11 files in
`results/tables/post_kbs_common_harness_baselines_001/` (B1) and 11 in
`results/tables/post_kbs_size_matched_drift_001/` (B2). For every file: run_completion.csv
shows all arms complete (96/96, 21/21), `mode=run`, a single source commit (`9f58b6cb47c2`,
`9f1159a817be`), seeds exactly 5001–5030 / 6001–6030 (n=30), and a config SHA-256 equal to the
committed config file's hash. Verdict files agree with the confirmatory checkpoints
(B2 `HOMOGENEOUS-SIZE BENEFIT`; B1 statements S2 = {doc, replay, ddm, adwin}, S4 = {atc,
enscal}). All 22 are analysis-derived confirmatory outputs committed before manuscript
integration (`61f5c5a`, `8285b04`) and belong in the final artifact.

| # | path | SHA-256 (first 16) | block | source commit | seeds |
|---|---|---|---|---|---|
| 1 | `results/tables/post_kbs_size_matched_drift_001/by_seed.csv` | `946b42b96441404b` | B2 | 9f1159a817be | 6001-6030 |
| 2 | `results/tables/post_kbs_size_matched_drift_001/coupling_audit.csv` | `6d4067db03efe36e` | B2 | 9f1159a817be | 6001-6030 |
| 3 | `results/tables/post_kbs_size_matched_drift_001/descriptive_contrasts.csv` | `06152935ad82b751` | B2 | 9f1159a817be | 6001-6030 |
| 4 | `results/tables/post_kbs_size_matched_drift_001/equivalence.csv` | `addc0e9b3f652c84` | B2 | 9f1159a817be | 6001-6030 |
| 5 | `results/tables/post_kbs_size_matched_drift_001/harmful_commit_summary.csv` | `bb7d8f26d5a0e53f` | B2 | 9f1159a817be | 6001-6030 |
| 6 | `results/tables/post_kbs_size_matched_drift_001/multiplicity.csv` | `c58f000e334d9560` | B2 | 9f1159a817be | 6001-6030 |
| 7 | `results/tables/post_kbs_size_matched_drift_001/paired_contrasts.csv` | `b857ee8e041463ab` | B2 | 9f1159a817be | 6001-6030 |
| 8 | `results/tables/post_kbs_size_matched_drift_001/run_completion.csv` | `6c16e20300dcd8d8` | B2 | 9f1159a817be | 6001-6030 |
| 9 | `results/tables/post_kbs_size_matched_drift_001/security_metrics.csv` | `4962d44412bab252` | B2 | 9f1159a817be | 6001-6030 |
| 10 | `results/tables/post_kbs_size_matched_drift_001/size_effect_outcome.csv` | `2a1dca3e6e3ea74d` | B2 | 9f1159a817be | 6001-6030 |
| 11 | `results/tables/post_kbs_size_matched_drift_001/summary.csv` | `3c5100e8927ef944` | B2 | 9f1159a817be | 6001-6030 |
| 12 | `results/tables/post_kbs_common_harness_baselines_001/budget_table.csv` | `de1d5c3d04d747ba` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 13 | `results/tables/post_kbs_common_harness_baselines_001/by_seed.csv` | `86b53e27a90de695` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 14 | `results/tables/post_kbs_common_harness_baselines_001/cell_classification.csv` | `a6124ca55395895c` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 15 | `results/tables/post_kbs_common_harness_baselines_001/descriptive_contrasts.csv` | `21c79f9357ab59aa` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 16 | `results/tables/post_kbs_common_harness_baselines_001/equivalence.csv` | `3ca16420482138e0` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 17 | `results/tables/post_kbs_common_harness_baselines_001/multiplicity.csv` | `36d1aa3c4e5a7b72` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 18 | `results/tables/post_kbs_common_harness_baselines_001/paired_contrasts.csv` | `a153c3d152ebe349` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 19 | `results/tables/post_kbs_common_harness_baselines_001/run_completion.csv` | `0bec8e31213c0669` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 20 | `results/tables/post_kbs_common_harness_baselines_001/security_metrics.csv` | `a03090e3601b5e46` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 21 | `results/tables/post_kbs_common_harness_baselines_001/statements.csv` | `399f785d07580c3b` | B1 | 9f58b6cb47c2 | 5001-5030 |
| 22 | `results/tables/post_kbs_common_harness_baselines_001/summary.csv` | `b862a3b130bfd805` | B1 | 9f58b6cb47c2 | 5001-5030 |

Full record (experiment, protocol, amendment, config, source/implementation/result commits,
seed range, evidence status, analysis script, checkpoint) per file:

| block | experiment | protocol | amendment | implementation → results | analysis script | checkpoint |
|---|---|---|---|---|---|---|
| B2 | B2 size-matched self-contained challengers under full drift | notes/post_kbs_size_matched_drift_protocol_001.md (frozen a68c90e) | nan | `9f1159a` → `61f5c5a` | `src/analysis/make_post_kbs_size_matched_drift_001.py` | `notes/post_kbs_size_matched_drift_confirmatory_checkpoint.md` |
| B1 | B1 registered common-harness comparison with published/reference baselines | notes/post_kbs_common_harness_baselines_protocol_001.md (frozen a68c90e) | notes/post_kbs_common_harness_baselines_amendment_001.md (5a4ce6f) | `9f58b6c` → `8285b04` | `src/analysis/make_post_kbs_common_harness_001.py` | `notes/post_kbs_common_harness_baselines_confirmatory_checkpoint.md` |

Evidence status of all 22: registered confirmatory (protocol frozen before implementation).

## 4. Sealing (Step 3)
- `results/tables/MANIFEST.sha256` regenerated by the repository's own generator and then
  checked, not trusted: 207 entries; the 185 pre-existing lines are a byte-identical subset
  (same hash, same path, same line-ending style); the 22 added lines carry exactly the
  independently computed SHA-256 of each file. `git diff --numstat` = 22 insertions, 0
  deletions.
- `results/final_experiment_ledger.csv` regenerated after adding two BLOCKS entries
  (`post_kbs_size_matched_drift`, 6001–6030, 21 arm dirs; `post_kbs_common_harness_baselines`,
  5001–5030, 96 arm dirs) mapping protocol, amendment, config SHA, implementation and result
  commits, and the manuscript tables (`tab:synthesis`, `tab:size_matched_drift`,
  `tab:common_harness` + supplement tables); 14 blocks, all present; orphan check 0.
- `results/final_manifest.json` regenerated (schema 1.2.0) with a `post_kbs_confirmatory_v1_23`
  section read from the sealed CSVs (outcomes, effects, classifications, statements, seeds,
  arm counts, config SHAs, protocol commits, sealing counts); `source_commit_sha` = `19d5a80`
  (HEAD at generation, the parent of the sealing commit, as the manifest's own note
  specifies); embedded audit 632/632; `n_table_csvs` 207.
- `docs/SCIENTIFIC_PROVENANCE.md`: sources-of-truth row 185 → 207, manifest-pinning invariant
  rewritten (0 unpinned extras), version table rows for v1.23.0 (B1, B2).
- Tests: the two count pins (185) updated to 207 with rationale; new
  `tests/test_v1_23_0_release_guards.py` asserts 185 + 22 = 207, on-disk hash equality for
  the 22, byte-identity of the 185 historical pins against `19d5a80`, 0 unpinned extras,
  version-surface agreement and ledger/final-manifest registration. Hash verification was
  not weakened.

## 5. Version metadata (Step 4)
v1.23.0 (minor increment: new preregistered confirmatory evidence; v1.22.x were editorial
patches over the v1.22.0 science). Updated: `CITATION.cff` (version, date-released),
`.zenodo.json` (version, description now names B1/B2), `manuscript/references.bib`
(software self-citation Version 1.23.0), README/REPRODUCE/PROVENANCE "pending sealed
release" → "sealed in v1.23.0". Manuscript: the Data-availability sentence and the two
Supplement provenance sentences that said "pending a subsequent sealed release" now say
"sealed in artifact version v1.23.0"; the exact historical science DOI (v1.22.0,
10.5281/zenodo.21517899) and the concept DOI are retained; no new DOI is stated. Historical
notes referring to earlier versions are untouched.

## 6. Integrity proofs
- Historical CSVs: 185/185 hashes identical pre/post (inventory check).
- Post-KBS CSVs: 22/22 hashes identical pre/post; pinned values equal disk values.
- Protocols/configs: 100/100 notes and 6/6 configs hash identically.
- No experiment executed: every raw completion marker predates the inventory timestamp;
  arm counts unchanged (21, 96); no runner invocation.
- Claim audit 632/632; PDFs 30/45/23 pp., 0 undefined refs/citations; guard suite 223 passed
  with the committed-manifest guard deselected pre-commit (full run after the commit is
  recorded in `audits/final_fresh_clone_validation.md`).

## 7. Deviations / notes
- The repository's earlier convention used two release commits (metadata, then a separate
  `final_manifest.json` stamp). Here the stamp is generated at HEAD `19d5a80` and sealed in the
  single release-engineering commit, which matches the manifest's documented semantics
  (`source_commit_sha` = parent of the sealing commit) and the phase requirement of one
  release-engineering commit after the scientific integration commit.
- Release audit documents produced after the sealing commit (fresh-clone validation, hostile
  release audit) are committed separately as documentation, so that the tag includes them.
- Submission-logistics documents (venue plan, cover-letter core, release notes, readiness
  status) stay local, following the repository's `.gitignore` convention for such files.
