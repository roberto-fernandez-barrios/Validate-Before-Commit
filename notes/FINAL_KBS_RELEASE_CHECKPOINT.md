# FINAL KBS RELEASE CHECKPOINT — v1.22.4 (final focused submission artifact)

Supersedes the v1.22.3 release checkpoint. v1.22.4 is the final editorial focus cut of the same
sealed v1.22.0 science.

## A. Version

- **Final version:** `v1.22.4` (editorial focus-cut PATCH over the sealed v1.22.0 science; resolution in `notes/FINAL_RELEASE_VERSION_RESOLUTION.md`).

## B. Commits

- **Editorial source (Commit A, Finalize):** `c7238c75d6961830a709db4dd82f79f4ffb0e4e2` — metadata bump to 1.22.4 (`references.bib`, `CITATION.cff`, `.zenodo.json`) + version-resolution note.
- **Sealing (Commit B, Stamp):** `f5ca18fa899eb44aee23900a97652c0c7101a92c` — `results/final_manifest.json` only.
- **Post-release doc commit:** records the Zenodo publication (this checkpoint + resolution note + release-manifest DOI); tag not moved.
- **Scientific source:** `43d9c255af48db9bcc3c6eb341a153381b18c8e8` (tag `v1.22.0`; ATTENUATION).

## C. Tag / integration

- **Tag:** `v1.22.4` (annotated) → sealing commit `f5ca18f` (remote ref `e4f2105a…`); not moved.
- **Integration:** fast-forward merge of `editorial/kbs-final-focus-cut` into `main` (6 commits, no merge commit).
- **main HEAD:** the post-release doc commit = `origin/main` (pushed).

## D. Manuscript

- **Title:** Candidate Comparability Before Promotion: Conditional Validation in Adaptive Network Intrusion Detection.
- **Pages:** main **25**, supplement **35**, IEEE **18**.
- **Words:** main body **10,607** (−19.7% from the pre-focus-cut 13,210); abstract 213.
- **Final compression:** §5.5 4,278 → 1,146 words; eight secondary tables relocated to the supplement (S0 evidence hierarchy + provenance); graphical abstract simplified to three steps; defensive/genealogy language removed.

## E. Scientific integrity

- **No new experiments.** `results/raw/**` and `results/tables/MANIFEST.sha256` byte-identical to v1.22.3 (empty `git diff v1.22.3 HEAD -- results/raw results/tables/MANIFEST.sha256`).
- **Registered outcomes unchanged:** symmetric-pipeline Scenario A; size-matched **ATTENUATION** (preserved, not reinterpreted).
- **Seeds, margins, families, estimands unchanged.** `final_manifest.json` regenerated mechanically (version 1.22.4, source Commit A, pages 25/35/18, audit 630); no scientific field changed.
- **DOIs:** science `10.5281/zenodo.21517899` and concept `10.5281/zenodo.21322256` unchanged; manuscript Data Availability still cites the sealed v1.22.0 science.

## F. Validation (sealed commit `f5ca18f`)

- **pytest:** 135 passed. **audit:** 630/630 pass. **hashes:** 185/185 match, 0 unpinned extras.
- **orphans:** none. **PDF build:** main 25 pp, supplement 35 pp, IEEE 18 pp — all 0 undefined refs/citations.
- **overfull boxes:** main 2 pre-existing CAS-template; IEEE 0; supplement 4 (two pre-existing S7/S8 data matrices ~85 pt, plus minor ~13–22 pt) — none new-and-serious.

## G. Release assets (SHA-256, verified equal local↔remote)

| Asset | Bytes | SHA-256 |
|---|---|---|
| `main.pdf` | 1,048,668 | `61e92b6a50a19728943ecb20adb5c277088d3a43168441ba6b2b7af6d197dc6b` |
| `supplement.pdf` | 968,097 | `fff23035df904214038d085c4baacb796c72dc3d646ecbd6194cfbdd19558b8d` |
| `main_ieee.pdf` | 843,261 | `df3159bb330de19aae38a52367a202e075212833b2f129d81044ee2d4d9fe1b7` |
| `release_manifest.json` | 2,644 | `558a0ac3b308717a97ea71f1f1921e2c34a745964ddb9f4ac7b4098466fe62ef` |
| `v1.22.4_final_focus_artifacts.zip` | 55,173 | `19fdb22c39ccee05d242bd0924f7acab25d553502383cabbe2a470252f7b5398` |

- **ZIP contents:** release_manifest.json, final_manifest.json, scientific_manifest (MANIFEST.sha256), final_experiment_ledger.csv, the KBS focus-cut checkpoint, editorial audit, main content map, evidence map, claim audit, version-resolution note, the two sealed configs (symmetric + size-matched), CITATION.cff, .zenodo.json, README.md. No raw datasets.

## H. Publication

- **GitHub release URL:** https://github.com/roberto-fernandez-barrios/Validate-Before-Commit/releases/tag/v1.22.4 (Published, marked Latest; 5 assets, digests verified equal to local).
- **Concept DOI:** `10.5281/zenodo.21322256` (now resolves to v1.22.4 as latest).
- **v1.22.4 version DOI:** **`10.5281/zenodo.21536366` — Published** (record state "done"; version field 1.22.4; title correct). Minted automatically by the Zenodo–GitHub integration; verified via the public Zenodo record API. Zenodo archived the standard GitHub source snapshot (`Validate-Before-Commit-v1.22.4.zip`); PDFs/manifests remain the GitHub Release assets, left as-is.
- **Science version DOI (v1.22.0):** `10.5281/zenodo.21517899` (unchanged).
- **Prior version DOIs:** v1.22.3 `10.5281/zenodo.21534289`.

## I. Working tree

Clean except the two untracked personal files (`PLAN_Q1_DEFINITIVO_VBC.md`, `notes/recovered_run_q1_faseC.py.txt`) and untracked `dist/` (release build outputs); no personal/dist file tracked in any commit.

## J. Verdict

**FINAL FOCUSED ARTIFACT RELEASED AND ARCHIVED — READY FOR KBS SUBMISSION**

Integration, sealing, GitHub publication and Zenodo archival are complete and verified. `main` is at
the tagged sealing commit chain, the GitHub Release `v1.22.4` is published (Latest) with five assets
whose SHA-256 digests match local computation, and Zenodo has archived the release under version DOI
`10.5281/zenodo.21536366` (Published). Every gate is green (135 pytest, 630/630 audit, 185/185
hashes) with the science bit-for-bit unchanged since v1.22.0 and ATTENUATION preserved. No external
block remains.

---

**STOP.** No further evaluation, experiment, framing change, title change, compression, new version,
tag, release or Zenodo action. This is the definitive artifact for submission to Knowledge-Based
Systems.
