# Baseline checkpoint — Size-matched own-transformer control

Date: 2026-07-22
Branch: `feature/size-matched-own-transformer` (created from `main` @ v1.21.0)

## Source of truth

- Tag: `v1.21.0` (points at HEAD of `main` at branch time)
- Commit A (scientific): `588c89e90b823813043a559e7ebd307cf57baf2a`
- Commit B (manifest stamp / branch point): `7f9ea405f6bd30e457f714c1a5ebc6b463e74c50`
- Version DOI: `10.5281/zenodo.21495829`
- Concept DOI: `10.5281/zenodo.21322256`

## Preflight gates (all green)

| Gate | Result |
|---|---|
| `git branch --show-current` (before branch) | `main` |
| `git rev-parse HEAD` | `7f9ea405f6bd30e457f714c1a5ebc6b463e74c50` |
| `git tag --points-at HEAD` | `v1.21.0` |
| Working tree | clean except known personal untracked files `PLAN_Q1_DEFINITIVO_VBC.md`, `notes/recovered_run_q1_faseC.py.txt` |
| `pytest tests -q` | 96 passed |
| `src.analysis.audit_paper2_claims` | 561 PASS / 0 FAIL |
| `src.analysis.verify_results_manifest` | 173/173 pinned CSVs match, 0 unpinned extras (orphans: 0) |

## Artifact hashes

- SHA-256 `results/final_manifest.json`: `5f8a1e434b45401fe210e4ddfcd4743b9b1eeb731c46add41b1dd13cab443ee6`
- SHA-256 `results/tables/MANIFEST.sha256`: `8500c6e2e241a34bca1001f7f312e3e3ab663aab1d9bd537288469a7cd3cdc43`

## v1.21.0 integrity note (line-ending representation incident, resolved)

On first run, `verify_results_manifest` reported 9 hash mismatches, all in
`results/tables/symmetric_pipeline_dynamic_001/*.csv`. Diagnosis:

- The 9 files on disk were byte-identical to the blobs committed at v1.21.0
  (`git hash-object` == `HEAD` blob for every file), i.e. **no content
  corruption**.
- The sealed `MANIFEST.sha256` records SHA-256 of the **CRLF** on-disk
  representation of these CSVs (Python `csv` module writes `\r\n`; the seal
  was computed against those working files). 164/173 pinned CSVs still carry
  that CRLF representation on disk and passed.
- The 9 files had been re-materialized by git as **LF** at some point after
  sealing (`.gitattributes`: `*.csv text eol=lf`), which changes the raw-byte
  hash without changing content.

Resolution (scripted, verify-before-write):
`scratchpad/restore_crlf_sealed_tables.py` first verified read-only that the
CRLF variant of each current file matches its sealed hash exactly (9/9
matched), and only then rewrote the 9 files with CRLF line endings, restoring
the sealed disk representation. `git update-index --really-refresh` then
re-confirmed the worktree files as content-identical to HEAD (clean status).
No committed content, no sealed manifest, and no raw output was modified.

Post-resolution: `verify_results_manifest` = 173/173 PASS; `git status` clean.

Reproducibility caveat for the record: a fresh clone will materialize all
CSVs as LF (per `.gitattributes`), so `verify_results_manifest` will report
raw-byte mismatches for CRLF-hashed entries even though content is intact.
This is a representation issue of the sealed manifest, out of scope for this
extension (the sealed MANIFEST must not be modified).

## Scope of this branch

Single closed extension: size-matched self-contained challenger control
(`candidate_size_per_class ∈ {512, 2000}`) under zero drift and
`own_transformer_per_model`, per the frozen instructions. No manuscript,
metadata, release, tag, merge, or Zenodo changes. Stop after the confirmatory
checkpoint.
