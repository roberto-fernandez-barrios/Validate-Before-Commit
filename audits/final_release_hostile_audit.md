# Final hostile release audit — v1.23.0 (read-only; no scientific prose edited)

Date: 2026-09-01. Object: `main` at the sealing line `19d5a80` (final manuscript integration)
→ `7b87c2f` (Seal post-KBS confirmatory artifact for release) → `fc73b8e` (Make the claim audit
runnable from repository contents alone) → this audit and the fresh-clone record, to be tagged
`v1.23.0`. Each question is answered only with evidence that exists in the repository or in
the recorded validation runs.

1. **Are all paper numbers backed by sealed outputs?** Yes. The claim audit (632/632) checks
   every pinned main-text number against the result CSVs and the flattened claim surfaces;
   the B2/B1 tables are generated exclusively from the now-sealed CSVs by
   `src/analysis/make_post_kbs_final_tables.py`, and `tests/test_post_kbs_final_manuscript_guards.py`
   re-derives the quoted B2/B1 values from those CSVs. The two VBC-SG per-proposal cells that
   only existed in raw logs are now sealed in `results/final_manifest.json` (schema 1.2.1) and
   audited from there when raw outputs are absent.
2. **Are all new B1/B2 outputs pinned?** Yes: 22 CSVs (11 + 11) in `MANIFEST.sha256`,
   hashes equal to disk; the two verdict JSONs are tracked; `verify_results_manifest` reports
   207 pinned, 0 unpinned extras (`tests/test_v1_23_0_release_guards.py`).
3. **Can a fresh clone verify every sealed CSV?** Yes. A clone of `main` from the local
   repository into a new temporary directory reported a clean tree and
   `207 pinned CSVs match MANIFEST.sha256 (0 unpinned extras)`; the claim audit passed 632/632
   in that clone using the sealed manifest fallback for the two raw-only cells (with an explicit
   note), and all three PDFs compiled with 0 undefined references/citations
   (`audits/final_fresh_clone_validation.md`).
4. **Do protocol commits predate experimental execution?** Yes, from this repository's own
   chronology: protocol freeze `a68c90e` 2026-08-31 18:14 (+02:00); B1 amendment `5a4ce6f`
   18:32; B2 implementation `9f1159a` 18:42 and B2 raw completion markers 21:39–22:15 (+02:00),
   results `61f5c5a` 22:17; B1 implementation `9f58b6c` 22:22 and B1 raw completion markers
   22:23–23:49, results `8285b04` 23:52. Every per-arm `run_config.json`/`run_completion.csv`
   records the implementation commit as `source_commit` with a clean tree and `mode=run`.
5. **Are the 5001–5030 and 6001–6030 seed blocks exact?** Yes: every B1 arm records
   `seeds=5001-5030, n_seeds=30` (96/96 complete); every B2 arm `seeds=6001-6030, n_seeds=30`
   (21/21 complete); the arm counts match the protocols' matrices; no seed was substituted.
6. **Did any frozen protocol change?** No. `git diff --quiet a68c90e HEAD` is empty for both
   protocol notes and the B2 config; `git diff --quiet 5a4ce6f HEAD` is empty for the B1
   amendment and the v2 config. The pre-seal inventory hashes of all 100 protocol/checkpoint
   notes and 6 configs are unchanged after sealing.
7. **Did any historical output change?** No. All 185 historical manifest lines are byte-identical
   to the manifest at `19d5a80` (22 insertions, 0 deletions), the pre-seal inventory hashes
   match after sealing, and `test_historical_pins_unchanged_since_integration_commit` enforces it.
   Raw completion markers all predate the sealing inventory; no runner invocation occurred.
8. **Does README accurately expose B1/B2?** Yes: the summary paragraph reports both blocks with
   their registered outcomes and "sealed in artifact v1.23.0"; reviewer quick-map rows 10–12
   point to protocols, amendment, configs, analysis scripts, outputs, checkpoints and the
   final-table generator (paths verified to exist by `test_readme_reviewer_quick_map_paths_exist`).
9. **Does the artifact overclaim SoTA?** No. README, REPRODUCE, `.zenodo.json`, the release
   notes and the manuscript contain no "SoTA"/"state-of-the-art adaptive" claim; the manuscript
   states "not a state-of-the-art ranking" and the guard suite bans the phrasings.
10. **Does the manuscript still acknowledge the absence of an end-to-end external adaptive-NIDS
    reproduction?** Yes — stated in §4.4, §5.6 and §7 ("no faithfully reproducible end-to-end
    published adaptive-NIDS system …", 2 occurrences in the flattened main text) with the frozen
    reasons; also in Supplement S10 and `final_manifest.json`
    (`end_to_end_adaptive_nids_system_reproduced: false`).
11. **Does it preserve ATTENUATION for the historical zero-drift registered classification?**
    Yes: 4 occurrences in the main text, the §5.3 paragraph "Registered outcome: ATTENUATION",
    the sentence that the full-drift control "does not retroactively change this historical
    classification", the audit guard "registered ATTENUATION outcome retained", and
    `final_manifest.json` (`size_matched_control_v1_22.registered_outcome = ATTENUATION`).
12. **Does it preserve HOMOGENEOUS-SIZE BENEFIT for B2?** Yes: the sealed
    `CLAIM_INTERPRETATION.json`, the manuscript (§5.4, table caption), the release guards and
    `final_manifest.json` all carry `HOMOGENEOUS-SIZE BENEFIT`.
13. **Does it preserve the negative/neutral gate results?** Yes: 0/6 positive gate effects at
    2,000/class under drift, the resolved strict-gate cost (UNSW-Recon −0.34), 0/6 at zero
    drift, and the B1 anchor descriptives are all in §5.4–§5.6 and pinned by
    `test_post_kbs_final_manuscript_guards.py`.
14. **Is ATC described as the strongest published generic competitor rather than an adaptive-NIDS
    SoTA method?** Yes: "ATC is the strongest published zero-target-label competitor"; its
    table origin is "published generic"; PortScan full drift is reported UNRESOLVED, not rounded
    up.
15. **Is the calibrated ensemble correctly identified?** Yes: "standard baseline", "the
    strongest standard label-free baseline (it commits every trigger and cannot decline an
    update, and it fails recall non-inferiority on PortScan)"; MATERIAL GAIN only on PortScan
    zero drift; ordering-change statement S4 fires for it.
16. **Is the chronological limitation preserved?** Yes: §5.7 keeps "net harm remains
    unobserved", "ToN-IoT ships no timestamps" (2 occurrences), no prevalence estimate, the
    registered family "structurally easy to satisfy", the unresolved Wednesday counterexample,
    and VBC-SG retaining 0–9 % of recovery; §7 repeats the boundary.

Release-engineering observations (not blockers): the raw per-arm outputs of every block remain
unshipped by design (documented in README/REPRODUCE: verification, tests and the claim audit run
from repository contents alone; raw-data regeneration requires the public datasets under
`data/`); the v1.23.0 version DOI does not exist until Zenodo mints it after the GitHub release
and is therefore absent from every file in the tagged tree.

## Verdict

**READY TO RELEASE**
