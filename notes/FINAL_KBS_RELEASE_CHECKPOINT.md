# FINAL KBS RELEASE CHECKPOINT — v1.22.6 (bibliographic ceiling + Git history rewrite)

Supersedes the v1.22.4 release checkpoint. v1.22.5 is a figure-only correction (connector arrows in
Figure 1 and the graphical abstract) over the same sealed v1.22.0 science; the focus-cut content of
v1.22.4 is unchanged.

## A. Version

- **Final version:** `v1.22.6` (focal bibliographic patch + Paper 1 removal PATCH over the sealed v1.22.0 science; resolution in `notes/FINAL_RELEASE_VERSION_RESOLUTION.md`).

## B. Commits

- **Figure fix commit:** `beae745` — connector-arrow geometry + one subtitle shortened (Figure 1 + graphical abstract).
- **Editorial source (Commit A, Finalize):** `49372a663bdbc04ccadf3c7979be82dd8620e45e` — metadata bump to 1.22.5 (`references.bib`, `CITATION.cff`, `.zenodo.json`) + version-resolution note.
- **Editorial source (Commit A, Finalize):** `65dd56cd6bb202ce912482e2de18e68a51c30a04` (metadata bump to 1.22.6).
- **Sealing (Commit B, Stamp):** `504c40f03e96e175edcc55b2319d0334cfe4e463` — `results/final_manifest.json` only.
- **Git history:** rewritten (`git filter-branch`) to strip Co-Authored-By: Claude trailers from all 144 trailered commits; main, all 30 tags and the remote dev branches are trailer-free (144 originals survive only in local refs/original + backup/pre-rewrite-main). Prior tags moved (v1.22.0 43d9c25->a46edbb, v1.22.5 e9449ca->a2278c4).
- **Post-release doc commit:** records the Zenodo publication (this checkpoint + resolution note + release-manifest DOI); tag not moved.
- **Scientific source:** `43d9c255af48db9bcc3c6eb341a153381b18c8e8` (tag `v1.22.0`; ATTENUATION).

## C. Tag / integration

- **Tag:** `v1.22.5` (annotated) → sealing commit `e9449ca`; not moved. (Prior tags `v1.22.4`→`f5ca18f`, `v1.22.3`→`3fbe1e6` unchanged.)
- **Integration:** the figure fix and two-commit seal were applied directly on `main` (the focus-cut branch was already merged at v1.22.4).
- **main HEAD:** the post-release doc commit = `origin/main` (pushed).

## D. Manuscript

- **Title:** Candidate Comparability Before Promotion: Conditional Validation in Adaptive Network Intrusion Detection.
- **Pages:** main **26**, supplement **35**, IEEE **18**.
- **Words:** main body **10,607** (−19.7% from the pre-focus-cut 13,210); abstract 213.
- **Final compression:** §5.5 4,278 → 1,146 words; eight secondary tables relocated to the supplement (S0 evidence hierarchy + provenance); graphical abstract simplified to three steps; defensive/genealogy language removed. **v1.22.5 change:** connector arrows in Figure 1 and the graphical abstract corrected (visible shafts; one subtitle shortened so box text fits) — geometry/labels only.

## E. Scientific integrity

- **No new experiments.** `results/raw/**` and `results/tables/MANIFEST.sha256` byte-identical to v1.22.4 (empty `git diff v1.22.4 HEAD -- results/raw results/tables/MANIFEST.sha256`).
- **Registered outcomes unchanged:** symmetric-pipeline Scenario A; size-matched **ATTENUATION** (preserved, not reinterpreted).
- **Seeds, margins, families, estimands unchanged.** `final_manifest.json` regenerated mechanically (version 1.22.5, source Commit A, pages 25/35/18, audit 630); no scientific field changed.
- **DOIs:** science `10.5281/zenodo.21517899` and concept `10.5281/zenodo.21322256` unchanged; manuscript Data Availability still cites the sealed v1.22.0 science.

## F. Validation (sealed commit `504c40f`)

- **pytest:** 135 passed. **audit:** 630/630 pass. **hashes:** 185/185 match, 0 unpinned extras.
- **orphans:** none. **PDF build:** main 25 pp, supplement 35 pp, IEEE 18 pp — all 0 undefined refs/citations.
- **overfull boxes:** main 2 pre-existing CAS-template; IEEE 0; supplement 4 (two pre-existing S7/S8 data matrices ~85 pt, plus minor ~13–22 pt) — none new-and-serious.

## G. Release assets (SHA-256, verified equal local↔remote)

| Asset | Bytes | SHA-256 |
|---|---|---|
| `main.pdf` | 1,044,955 | `c5a8a9be4eda56f14800836fc61b46fe4a2f58252a7a2602fa82980a78f5f030` |
| `supplement.pdf` | 968,097 | `7d433c41b03df4b50e360660a870efb6a2c536c46e11d1e4bcbc5b087d53b022` |
| `main_ieee.pdf` | 839,563 | `44c258251acaf78b33005abb74deeb98f88ef47b1a2a9647c2faa7e785135d37` |
| `release_manifest.json` | 2,566 | `2d83bd4213da4837f47629278ad6ca67fe32fcf07ef275dd9a22ba87f5c1db09` |
| `v1.22.6_bibliographic_ceiling_artifacts.zip` | 55,571 | `78d44a53db2d2279becdf6cb1b9fcc04fa4009fbe8e123518f8c6046fbc4d1fa` |

- **ZIP contents:** release_manifest.json, final_manifest.json, scientific_manifest (MANIFEST.sha256), final_experiment_ledger.csv, the KBS focus-cut checkpoint, editorial audit, main content map, evidence map, claim audit, version-resolution note, the two sealed configs (symmetric + size-matched), CITATION.cff, .zenodo.json, README.md. No raw datasets.

## H. Publication

- **GitHub release URL:** https://github.com/roberto-fernandez-barrios/Validate-Before-Commit/releases/tag/v1.22.6 (Published, marked Latest; 5 assets, digests verified equal to local).
- **Concept DOI:** `10.5281/zenodo.21322256` (now resolves to v1.22.6 as latest).
- **v1.22.6 version DOI:** **`10.5281/zenodo.21538275` — Published** (record state "done"; version field 1.22.5; title correct). Minted automatically by the Zenodo–GitHub integration; verified via the public Zenodo record API. Zenodo archived the standard GitHub source snapshot (`Validate-Before-Commit-v1.22.6.zip`); PDFs/manifests remain the GitHub Release assets, left as-is.
- **Science version DOI (v1.22.0):** `10.5281/zenodo.21517899` (unchanged).
- **Prior version DOIs:** v1.22.4 `10.5281/zenodo.21536366`; v1.22.3 `10.5281/zenodo.21534289`.

## I. Working tree

Clean except the two untracked personal files (`PLAN_Q1_DEFINITIVO_VBC.md`, `notes/recovered_run_q1_faseC.py.txt`) and untracked `dist/` (release build outputs); no personal/dist file tracked in any commit.

## J. Verdict

**FINAL FOCUSED ARTIFACT RELEASED AND ARCHIVED — READY FOR KBS SUBMISSION**

Integration, sealing, GitHub publication and Zenodo archival are complete and verified. `main` is at
the tagged sealing commit chain, the GitHub Release `v1.22.6` is published (Latest) with five assets
whose SHA-256 digests match local computation, and Zenodo has archived the release under version DOI
`10.5281/zenodo.21538275` (Published). Every gate is green (136 pytest, 630/630 audit, 185/185
hashes) with the science bit-for-bit unchanged since v1.22.0 and ATTENUATION preserved. No external
block remains.

---

**STOP.** No further evaluation, experiment, framing change, title change, compression, new version,
tag, release or Zenodo action. This is the definitive artifact for submission to Knowledge-Based
Systems.
