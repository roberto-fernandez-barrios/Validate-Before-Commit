# Fresh-clone (clean-room) validation — v1.23.0 line

Date: 2026-09-01. Performed before tagging, as required by the release protocol.

## Procedure
A completely new temporary directory outside the working repository
(`%LOCALAPPDATA%\Temp\vbc_clone_main`) received a clone of branch `main` from the LOCAL
repository (`git clone -b main <local path>`; `safe.directory` override only, because the
working repository is owned by a different Windows principal). No push was involved. Inside
the clone, from repository contents alone (no `results/raw/**`, no datasets under `data/`):

| step | command | result |
|---|---|---|
| checkout | `git rev-parse HEAD`, `git status` | `fc73b8e` on `main`; clean tree (0 status lines) |
| hashes | `python -m src.analysis.verify_results_manifest` (`make verify-hashes`) | **207 pinned CSVs match MANIFEST.sha256 (0 unpinned extras)** |
| claim audit | `python -m src.analysis.audit_paper2_claims` (`make audit`) | **632/632 checks pass**; two explicit notes: the VBC-SG per-proposal cells (PortScan full, ToN zero) were audited against the value sealed in `results/final_manifest.json` because `results/raw` is not shipped (commit `fc73b8e`) |
| IEEE port + PDFs | `python -m src.analysis.port_ieee`; `python -m src.analysis.build_pdfs` | main.pdf 30 pp., supplement.pdf 45 pp., main_ieee.pdf 23 pp.; **0 undefined references, 0 undefined citations** in all three |
| tests | `pytest -q` in the `paper2` environment of record | **224 passed** |
| tree after everything | `git status` (build products excluded) | `manuscript/main_ieee.tex` flagged `M` by `core.autocrlf=true`; `git diff` is empty and the committed blob and the regenerated file are byte-identical (LF, 123,029 bytes) — a Windows line-ending display artifact, not a content change |

An earlier attempt (before `fc73b8e`) failed the claim audit in the clone because one check read
raw per-seed logs that the artifact does not ship; the fix sealed those two derived cells in
`final_manifest.json` (computed from raw at stamping time) and made the audit fall back to the
sealed value with a printed note — no check was skipped and no tolerance changed. The clone was
deleted and recreated from scratch after the fix; the table above is that second, complete run.

## What the artifact supports, stated precisely
- **A. Verification from repository contents alone (no download):** hash verification of all
  207 sealed result CSVs, the 224-test guard suite, the 632-check claim audit, regeneration of
  every manuscript table from the sealed CSVs, and compilation of the manuscript, supplement
  and IEEE port. This is what the clean-room run above exercised.
- **B. Full raw-data regeneration:** re-running the experiment runners to regenerate
  `results/raw/**` and, from them, the result CSVs requires the public CICIDS2017, UNSW-NB15
  and ToN-IoT datasets placed under `data/` (REPRODUCE.md, README "not redistributed"); they are
  intentionally not redistributed, so raw-data reproduction is not zero-download and the
  documentation does not claim it is.

## Outcome
Fresh clone of `main` at `fc73b8e`: clean tree, 207/207 hashes, 224/224 tests, 632/632 claim
checks, 0 undefined references/citations. The tagged checkout is validated separately
(Step 11 record appended below once the tag exists).
