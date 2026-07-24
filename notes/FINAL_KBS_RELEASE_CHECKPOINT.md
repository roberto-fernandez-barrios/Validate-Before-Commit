# FINAL KBS RELEASE CHECKPOINT

## A. Version

- **Final version:** `v1.22.3` (editorial narrative-rebuild PATCH over the sealed v1.22.0 science; resolution in `notes/FINAL_RELEASE_VERSION_RESOLUTION.md`).
- **Source scientific commit:** `43d9c255af48db9bcc3c6eb341a153381b18c8e8` (tag `v1.22.0`, size-matched control sealed; ATTENUATION).
- **Editorial source commit (manifest source):** `5ade58d6cdc268cb6e011d6a55692e69b101a1f9` (Finalize).
- **Sealing commit:** `3fbe1e64f49c36f12f1615d24c262ca40fcf8a90` (Stamp).
- **Tag:** `v1.22.3` (annotated) → remote ref `a183d0c96d7bdfc1e9801602b65a8bc758328bf2`, points to sealing commit `3fbe1e6`.

## B. Integration

- **Source branch:** `editorial/q1-final-narrative-rebuild`.
- **Merge type:** fast-forward (`git merge --ff-only`), no merge commit; 7 linear commits.
- **main HEAD:** `3fbe1e6` = `origin/main` = `tag v1.22.3` (pushed).
- **Working tree:** clean except the two known untracked personal files (`PLAN_Q1_DEFINITIVO_VBC.md`, `notes/recovered_run_q1_faseC.py.txt`) and the untracked `dist/` release build outputs — neither committed.

## C. Manuscript

- **Title:** Candidate Comparability Before Promotion: Conditional Validation in Adaptive Network Intrusion Detection.
- **Abstract words:** 221.
- **Main pages:** 32. **Supplement pages:** 30. **IEEE pages:** 24.
- **Figures (main):** 2 in-body (decision-pipeline Fig. 1; per-trigger mechanism Fig. 2) plus the graphical abstract.
- **Tables (main):** 2 in-body (temporal-latency; evidence-blocks-at-a-glance) plus 13 `\input` result tables.

## D. Scientific integrity

- **No new experiments** were run.
- **Raw results unchanged:** `git diff v1.22.2 HEAD -- results/raw` is empty (byte-identical).
- **Sealed CSV manifest unchanged:** `results/tables/MANIFEST.sha256` byte-identical to v1.22.2; `verify_results_manifest` 185/185, 0 unpinned extras.
- **Registered outcomes unchanged:** symmetric-pipeline Scenario A; size-matched **ATTENUATION** — preserved, not reinterpreted.
- **Seeds / margins / statistical families unchanged.**
- **Manifests status:** `results/final_manifest.json` regenerated mechanically (source-commit, version 1.22.3, pages 32/30/24, audit 630/630); no scientific field (seeds, outcomes, dataset hashes) changed. `results/tables/MANIFEST.sha256` untouched.

## E. Validation (on the sealed commit `3fbe1e6`)

- **pytest:** 135 passed.
- **audit:** `audit_paper2_claims` 630/630 checks pass.
- **hashes:** `verify_results_manifest` 185/185 pinned CSVs match, 0 unpinned extras.
- **orphans:** none (no orphaned result directories; no accidental regeneration).
- **PDF build:** main 32 pp, supplement 30 pp, IEEE 24 pp — official `build_pdfs` workflow.
- **references/citations:** 0 undefined in all three documents.
- **overfull boxes:** main — 2 pre-existing CAS-template artifacts (`\maketitle` 117 pt; graphical-abstract/highlights strip 9.7 pt), present at baseline, unrelated to this rebuild; IEEE — 0; supplement — 3 minor wide-data-table boxes in the untouched S7/S8 confirmatory matrices (largest 85 pt), pre-existing. No serious (grave) boxes.

## F. Release assets (SHA-256)

Attached to GitHub Release `v1.22.3`:

| Asset | Bytes | SHA-256 |
|---|---|---|
| `main.pdf` | 1,194,854 | `8041228ecc56ad93d4c9c894d3dbb34ab6a1393cc6d04704ec9405be4f1d6164` |
| `supplement.pdf` | 936,913 | `b9fa5f6f3b069907896a2b29aaf62544d0c80b5ec6cbaefd5bfc30a89970fe2c` |
| `main_ieee.pdf` | 899,434 | `41f069f7725b12f8e6fe5e5ec759a277229364a88f4d78f55ef09bfd50b42513` |
| `release_manifest.json` | 2,534 | `585d2171b3176d1044b1d75ed8ed0c96d69983091d1a6d1df19c648d232d34eb` |
| `v1.22.3_narrative_rebuild_artifacts.zip` | 299,229 | `646be3826d76ae3a52abc037e7550dc2f9a5a80b5276708b66b3d187e71de94a` |

- **ZIP contents (reproducible, fixed timestamps):** `release_manifest.json`, `final_manifest.json`, `highlights.md`, `graphical_abstract.png`, `README.md`, `CITATION.cff`, `.zenodo.json`, `notes/FINAL_RELEASE_VERSION_RESOLUTION.md`, `notes/Q1_FINAL_NARRATIVE_REBUILD_CHECKPOINT.md`, `notes/Q1_FINAL_CLAIM_AUDIT.md`.
- **`release_manifest.json`** carries: version 1.22.3, definitive title, scientific-source commit `43d9c25`, sealing/release commit `3fbe1e6`, asset hashes, pages, word counts, validation (pytest/audit/hashes), datasets, seeds, registered outcomes, and the no-new-experiments / results-raw-intact declarations. `release_version_doi` = `10.5281/zenodo.21534289`, `zenodo_status` = `published`.

## G. Publication

- **GitHub release URL:** https://github.com/roberto-fernandez-barrios/Validate-Before-Commit/releases/tag/v1.22.3 (published, marked latest; 5 assets, digests verified equal to local).
- **Tag:** `v1.22.3` pushed (`origin` ref `a183d0c9…`).
- **main:** pushed (`1e0c72f..3fbe1e6`).
- **Concept DOI:** `10.5281/zenodo.21322256` (unchanged; now resolves to v1.22.3 as latest).
- **Science version DOI (v1.22.0):** `10.5281/zenodo.21517899` (unchanged; cited by the manuscript Data Availability).
- **v1.22.3 version DOI:** **`10.5281/zenodo.21534289` — Published.** Minted by the automatic Zenodo–GitHub integration (maintainer's linked account) on publishing the GitHub Release; confirmed via public Zenodo record API and by the maintainer.
- **Zenodo status:** **PUBLISHED.** No external block remains. Zenodo archived the standard GitHub source snapshot (`Validate-Before-Commit-v1.22.3.zip`); the three PDFs, `release_manifest.json` and the artifacts ZIP remain on the GitHub Release (consistent with prior versions — the deposit is deliberately left as-is, no manual attachment).

## H. Final submission package

Available and verified:

- **Main PDF:** `manuscript/main.pdf` (32 pp) — GitHub Release asset.
- **Supplement:** `manuscript/supplement.pdf` (30 pp) — GitHub Release asset.
- **IEEE PDF:** `manuscript/main_ieee.pdf` (24 pp) — GitHub Release asset.
- **Graphical abstract:** `docs/img/graphical_abstract.png` (in `\begin{graphicalabstract}` of main; in the artifacts ZIP).
- **Highlights:** `manuscript/highlights.md` (5 bullets, all ≤85 chars).
- **Declarations:** competing interest, funding, data availability, generative-AI use — all present in `main.tex`.
- **Repository URL:** https://github.com/roberto-fernandez-barrios/Validate-Before-Commit
- **DOI:** concept `10.5281/zenodo.21322256`; v1.22.3 version DOI `10.5281/zenodo.21534289` (Published); v1.22.0 science DOI `10.5281/zenodo.21517899`.
- **Release artifact:** `dist/v1.22.3_narrative_rebuild_artifacts.zip` + `dist/release_manifest.json`.

## I. Verdict

**FINAL ARTIFACT RELEASED AND ARCHIVED — READY FOR KBS SUBMISSION**

Integration, sealing, GitHub publication and Zenodo archival are complete and verified: `main` is at
the tagged sealing commit `3fbe1e6`, the GitHub Release `v1.22.3` is published with five assets whose
SHA-256 digests match local computation, the automatic Zenodo–GitHub integration has archived the
release under version DOI **`10.5281/zenodo.21534289` (Published)**, and every gate is green
(135 pytest, 630/630 audit, 185/185 hashes) with the science bit-for-bit unchanged since v1.22.0.
No external block remains. The submission-ready PDFs, highlights, graphical abstract and declarations
are all in hand.

## J. Zenodo v1.22.3 archival — completed

The GitHub Release `v1.22.3` was ingested automatically by the maintainer-linked Zenodo–GitHub
integration (no local token or manual upload). Confirmed via the public Zenodo record API and by the
maintainer:

- **Version DOI:** `10.5281/zenodo.21534289` — state **Published**, version field `1.22.3`.
- **Concept DOI:** `10.5281/zenodo.21322256` — now resolves to v1.22.3 as latest (`is_last: true`).
- **Archived file:** `roberto-fernandez-barrios/Validate-Before-Commit-v1.22.3.zip` (GitHub source snapshot, 2.7 MB) — the standard integration behavior, matching prior versions; left as-is by decision. The three PDFs, `release_manifest.json` and the artifacts ZIP remain the GitHub Release assets and are not manually attached to Zenodo.
- **Related identifier:** the GitHub `v1.22.3` release, `isSupplementTo` the paper, MIT license.

Historical record of the original pending flow (now satisfied): GitHub Release published → automatic
integration → processing → version DOI minted.

The mechanical closure applied at this step (no scientific/prose change): the DOI placeholder was
replaced in `dist/release_manifest.json` (`release_version_doi` → `10.5281/zenodo.21534289`,
`zenodo_status: published`), the artifacts ZIP regenerated, both re-uploaded to the GitHub Release,
and this checkpoint plus `notes/FINAL_RELEASE_VERSION_RESOLUTION.md` updated. The manuscript Data
Availability is unchanged — it correctly cites the sealed v1.22.0 science DOI `10.5281/zenodo.21517899`;
the concept DOI already present is unchanged; the tag `v1.22.3` still points to sealing commit `3fbe1e6`.

---

**STOP.** Integration, sealing, GitHub publication and Zenodo archival complete. No further review,
experiment, extension, reframing, manuscript change, new version, new tag, new release, or manual
Zenodo edit is to be performed. This is the definitive closure of v1.22.3.
