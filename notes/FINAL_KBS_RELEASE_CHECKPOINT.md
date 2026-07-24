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
| `release_manifest.json` | 2,309 | `faa48a5caf73a342c847f04b69625d4d379cc4e51a0cfc28db52b4634333e66e` |
| `v1.22.3_narrative_rebuild_artifacts.zip` | 299,078 | `cda1abc02ecfcdde37294ddf814ffab73fcb1c898a702a28762716dfa9505592` |

- **ZIP contents (reproducible, fixed timestamps):** `release_manifest.json`, `final_manifest.json`, `highlights.md`, `graphical_abstract.png`, `README.md`, `CITATION.cff`, `.zenodo.json`, `notes/FINAL_RELEASE_VERSION_RESOLUTION.md`, `notes/Q1_FINAL_NARRATIVE_REBUILD_CHECKPOINT.md`, `notes/Q1_FINAL_CLAIM_AUDIT.md`.
- **`release_manifest.json`** carries: version 1.22.3, definitive title, scientific-source commit `43d9c25`, sealing/release commit `3fbe1e6`, asset hashes, pages, word counts, validation (pytest/audit/hashes), datasets, seeds, registered outcomes, and the no-new-experiments / results-raw-intact declarations. `release_version_doi` = `PENDING_ZENODO_PUBLICATION`.

## G. Publication

- **GitHub release URL:** https://github.com/roberto-fernandez-barrios/Validate-Before-Commit/releases/tag/v1.22.3 (published, marked latest; 5 assets, digests verified equal to local).
- **Tag:** `v1.22.3` pushed (`origin` ref `a183d0c9…`).
- **main:** pushed (`1e0c72f..3fbe1e6`).
- **Concept DOI:** `10.5281/zenodo.21322256` (unchanged; resolves to latest).
- **Science version DOI (v1.22.0):** `10.5281/zenodo.21517899` (unchanged; cited by the manuscript Data Availability).
- **v1.22.3 version DOI:** **PENDING**. Zenodo is **not authenticated in this environment** (no token, no config, no in-repo upload script); the project uses the Zenodo–GitHub webhook, which is configured on the maintainer's Zenodo account and cannot be verified or triggered from here.
- **Zenodo status:** BLOCKED ON EXTERNAL AUTH — see section J for the exact pending steps. No Zenodo publication has been simulated.

## H. Final submission package

Available and verified:

- **Main PDF:** `manuscript/main.pdf` (32 pp) — GitHub Release asset.
- **Supplement:** `manuscript/supplement.pdf` (30 pp) — GitHub Release asset.
- **IEEE PDF:** `manuscript/main_ieee.pdf` (24 pp) — GitHub Release asset.
- **Graphical abstract:** `docs/img/graphical_abstract.png` (in `\begin{graphicalabstract}` of main; in the artifacts ZIP).
- **Highlights:** `manuscript/highlights.md` (5 bullets, all ≤85 chars).
- **Declarations:** competing interest, funding, data availability, generative-AI use — all present in `main.tex`.
- **Repository URL:** https://github.com/roberto-fernandez-barrios/Validate-Before-Commit
- **DOI:** concept `10.5281/zenodo.21322256`; v1.22.3 version DOI pending Zenodo.
- **Release artifact:** `dist/v1.22.3_narrative_rebuild_artifacts.zip` + `dist/release_manifest.json`.

## I. Verdict

**FINAL ARTIFACT RELEASED — READY FOR KBS SUBMISSION**

Integration, sealing, and GitHub publication are complete and verified: `main` is at the tagged
sealing commit `3fbe1e6`, the GitHub Release `v1.22.3` is published with five assets whose SHA-256
digests match local computation, and every gate is green (135 pytest, 630/630 audit, 185/185
hashes) with the science bit-for-bit unchanged since v1.22.0. The **only** outstanding item is the
Zenodo v1.22.3 version DOI, which is blocked on external Zenodo authentication not available in this
environment (section J). The submission-ready PDFs, highlights, graphical abstract and declarations
are all in hand; the concept DOI already cited across README/CITATION/manuscript resolves to the
latest version, so KBS submission is not blocked by the pending version DOI.

## J. Pending external step — Zenodo v1.22.3 version DOI (exact procedure)

Zenodo could not be reached from this environment. The maintainer completes it as follows.

**If the Zenodo–GitHub webhook is enabled** (the project's established workflow — the concept DOI
`10.5281/zenodo.21322256` and the per-release version DOIs indicate it is):

1. Publishing the GitHub Release `v1.22.3` (done) triggers Zenodo to create a new draft version under the concept record.
2. Sign in at https://zenodo.org → *Upload* → the concept record `10.5281/zenodo.21322256` → the new `v1.22.3` draft.
3. Confirm the draft metadata matches `.zenodo.json` (title, `version: 1.22.3`, description, creators/ORCIDs, MIT license, keywords, related identifier = the GitHub release URL).
4. **Publish** the draft → the v1.22.3 **version DOI** is minted.

**If the webhook is not enabled** — mint via the API with a personal token (scope `deposit:write`):

```bash
export ZENODO_TOKEN=<personal-access-token>
CONCEPT=21322256
# 1. create a new version draft from the latest published deposit
NEWID=$(curl -s -H "Authorization: Bearer $ZENODO_TOKEN" \
  -X POST "https://zenodo.org/api/deposit/depositions/$CONCEPT/actions/newversion" \
  | python -c "import sys,json;print(json.load(sys.stdin)['links']['latest_draft'].rsplit('/',1)[1])")
# 2. clear old files, upload the five assets, PUT .zenodo.json metadata (version 1.22.3), then publish
#    (bucket upload + metadata PUT + POST .../actions/publish)
```

Then, **after the version DOI is minted**, the only mechanical follow-up (no scientific/prose change):

- If the repository convention records the version DOI anywhere machine-readable, add it (e.g. a `version_doi` field); the manuscript Data Availability is **not** changed — it correctly cites the sealed v1.22.0 science DOI. Re-run `pytest tests -q`, `audit_paper2_claims`, `verify_results_manifest` and confirm all green before any such commit.

---

**STOP.** Integration, sealing and GitHub publication complete; Zenodo version DOI pending external
authentication. No further review, experiment, extension, reframing, or manuscript change is to be
performed in this phase.
