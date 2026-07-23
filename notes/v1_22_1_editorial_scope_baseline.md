# v1.22.1 Editorial Scope Correction — Baseline Record

Date: 2026-07-23
Branch: `fix/v1.22.1-editorial-scope` (created from `main`)

## Baseline identity

- Baseline tag: `v1.22.0`
- `main` HEAD (sealing commit): `43d9c255af48db9bcc3c6eb341a153381b18c8e8`
- Source commit of v1.22.0: `cccc5e43c6769bc0b38f18370d45e44ef61c9f95`
- Version DOI: `10.5281/zenodo.21517899`
- Concept DOI: `10.5281/zenodo.21322256`
- Registered outcome: `ATTENUATION` (unchanged)

## Working tree at preflight

Clean except the two historically excluded personal files:

- `PLAN_Q1_DEFINITIVO_VBC.md` (untracked)
- `notes/recovered_run_q1_faseC.py.txt` (untracked)

## Baseline gates (executed on `main` @ 43d9c25 before branching)

- pytest: **118/118 passed** (52.01 s)
- `src.analysis.audit_paper2_claims`: **586/586 PASS, 0 FAIL**
- `src.analysis.verify_results_manifest`: **183/183 pinned CSVs match `MANIFEST.sha256` (0 unpinned extras, 0 orphans)**
- Size-matched own-transformer control (`size_matched_own_transformer_001`): **21/21 arms complete** (seeds 4001–4030)
- Symmetric-pipeline replication (`symmetric_pipeline_dynamic_001`): **42/42 arms complete** (seeds 3001–3030)
- Background processes: **none** (no shell jobs, no runners active)

## Pinned hashes at baseline

- SHA-256 `results/final_manifest.json`:
  `1f7f161757dfdf2783d7be0bc0195132ead3beaa4fe9a66bd7a51c532754f479`
- SHA-256 `results/tables/MANIFEST.sha256`:
  `132643ad37e6b959775369043a58f862ceaea067364848f970f58212e738d87f`

## Scope of the v1.22.1 phase

Editorial and derived-analysis only. No experimental runners, no new seeds, no new
matrices, no modification of raw v1.22.0/v1.21.0 outputs, no changes to preregistered
protocols, frozen configs, statistical families, or the registered ATTENUATION outcome.
No merge, tag, release, Zenodo upload, DOI, `results/final_manifest.json` update, or
`MANIFEST.sha256` re-pin until the human checkpoint approves sealing.
