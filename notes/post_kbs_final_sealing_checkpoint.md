# CHECKPOINT — Final sealing of the post-KBS confirmatory artifact (v1.23.0)

Date: 2026-09-01. Branch: `main` (fast-forwarded from `post-kbs-hardening`; no merge commit).

## Commit chain
- Editorial base after KBS rejection: `57ef8e7` (previous `main` / `origin/main`).
- Phase A hardening: `c2b8899`. Protocol freeze (B1 + B2): `a68c90e`.
- B1 amendment (before implementation): `5a4ce6f`. B2 implementation: `9f1159a`.
  B2 confirmatory results: `61f5c5a`. B1 implementation: `9f58b6c`. B1 confirmatory results +
  cross-experiment hostile audit: `8285b04`.
- **Final manuscript integration: `19d5a80`** — *Integrate post-KBS confirmatory evidence into
  final manuscript* (the last scientific commit).
- Release-engineering commit (this checkpoint): *Seal post-KBS confirmatory artifact for
  release* — manifest/ledger sealing, `results/final_manifest.json` stamp (source commit
  `19d5a80`, per the manifest's documented semantics), version metadata, documentation,
  release guards, this checkpoint and the integrity report. No scientific result changed.

## Release version
- **v1.23.0.** Convention: v1.21.0 sealed the symmetric-pipeline replication, v1.22.0 the
  size-matched control; v1.22.1–v1.22.9 were editorial patches on the v1.22.0 science. B1 and
  B2 add new preregistered confirmatory evidence, so the minor version increments and the
  patch resets. `CITATION.cff`, `.zenodo.json` and the manuscript's software self-citation
  (`references.bib`, Version 1.23.0) agree; the concept DOI 10.5281/zenodo.21322256 is
  retained; no version DOI is invented (recorded post-mint in the release checklist only).

## Sealed counts
- Historical sealed CSVs: **185** (every line of `MANIFEST.sha256` at `19d5a80` is present
  byte-for-byte in the new manifest; line-ending style preserved).
- Newly sealed CSVs: **22** (11 B1 + 11 B2), pinned additively with their on-disk SHA-256.
- Total expected and observed: **207**; `verify_results_manifest` reports 0 unpinned extras.

## Seed blocks
- B1 common-harness baselines: seeds **5001–5030** (96 arms; source commit `9f58b6cb47c2`;
  config `configs/post_kbs_common_harness_baselines_v2.json`, SHA-256 `b6e4e1f6682f…`).
- B2 size-matched drift: seeds **6001–6030** (21 arms; source commit `9f1159a817be`; config
  `configs/post_kbs_size_matched_drift_v1.json`, SHA-256 `2ca8f4d3679b…`).

## Registered conclusions (unchanged by sealing)
- **B2:** registered outcome **HOMOGENEOUS-SIZE BENEFIT** — naive₂₀₀₀−naive₅₁₂ = +0.82
  [0.67, 0.98] / +1.66 [1.51, 1.81] / +1.00 [0.60, 1.39] BA points (PortScan / UNSW-Recon /
  ToN-IoT; Holm-significant, all above +0.5); always-deploy beneficial at both sizes; 0/6
  positive gate effects at 2,000/class; strict on UNSW-Recon a resolved cost (−0.34). The
  historical zero-drift classification ATTENUATION (v1.22.0) is not retroactively changed.
- **B1:** at nominal 2,000/class parity under full drift ATC and the calibrated ensemble are
  COMPATIBLE with always-deploy; DoC, replay, river-DDM and river-ADWIN are MATERIAL COST.
  S1 holds for no policy; S2 holds for DoC/replay/DDM/ADWIN; S3 holds for neither ATC nor DoC;
  S4 (ordering changes with candidate size) fires for ATC and the calibrated ensemble; all 15
  resolved method×size interactions are negative. No adaptive-NIDS SoTA claim; no end-to-end
  adaptive-NIDS system reproduced; budgets documented, not equalized.

## Final manuscript thesis
A drift alarm proposes a challenger but does not establish promotion. Promotion outcomes
changed materially when two comparability asymmetries — incumbent-owned frozen preprocessing
and nominal candidate-evidence size — were corrected, with a homogeneous size benefit under
real drift. Under comparable conditions validation ceased to provide average benefit and the
registered alternatives showed no universal winner; comparability of construction and evidence
must be established before interpreting promotion harm or comparing promotion policies.

## Validation at sealing (working tree = sealing commit content)
- Claim audit: **632/632**.
- Guard suite (paper2 environment of record): **223 passed** with the one test that requires
  the stamped `final_manifest.json` to be committed deselected; the full 224 are re-run on
  `main` after the sealing commit and recorded in `audits/final_fresh_clone_validation.md`.
- Hashes: 207/207 pinned CSVs match; 0 unpinned extras.
- Builds: main.pdf 30 pp., supplement.pdf 45 pp., main_ieee.pdf 23 pp.; 0 undefined
  references/citations in all three.

## Proof that no historical CSV changed
Pre-seal inventory (SHA-256 of all 185 pinned CSVs, all 22 post-KBS CSVs, both verdict JSONs,
manuscript sources, 100 protocol/checkpoint notes and 6 configs, taken at HEAD `19d5a80`):
all 185 historical CSV hashes and all 22 post-KBS CSV hashes are identical before and after
sealing; the manifest diff is 22 insertions / 0 deletions; every protocol note and config file
hashes identically; only the version/artifact-reference sentences of the manuscript sources
changed (Data availability and the two Supplement provenance sentences), which the guard
suite pins.

## Proof that no experiment was executed during sealing
Raw arm directories and their completion markers all predate the pre-seal inventory
timestamp (2026-09-01T10:22:15.684118+00:00):
{
  "post_kbs_size_matched_drift": {
    "n_arms": 21,
    "latest_completion_marker_utc": "2026-08-31T20:15:23.587360+00:00",
    "predates_inventory": true
  },
  "post_kbs_common_harness_baselines": {
    "n_arms": 96,
    "latest_completion_marker_utc": "2026-08-31T21:49:05.056635+00:00",
    "predates_inventory": true
  }
}
No new arm directory exists; the runner was not invoked; the analysis scripts of B1/B2 were
not re-executed (their outputs hash identically).
