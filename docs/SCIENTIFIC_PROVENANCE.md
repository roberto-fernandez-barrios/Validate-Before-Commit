# Scientific Provenance

A neutral map from the sealed science to its authoritative artifacts:
**version → protocol → config → experiment → outcome → manifest → DOI**. It records registered
designs, the code and configs that realize them, the datasets, the invariants, and the archival
identifiers. It is not a changelog and contains no project or editorial history.

## Sources of truth

| Artifact | Location | Role |
|---|---|---|
| Sealed result CSVs | `results/tables/**`, pinned by `results/tables/MANIFEST.sha256` | 185 CSVs, byte-verifiable via `make verify-hashes` |
| Final machine-readable manifest | `results/final_manifest.json` | artifact manifest (arm counts, hashes, statistical families) |
| Experiment ledger | `results/final_experiment_ledger.csv` (built by `src/analysis/make_final_experiment_ledger.py`) | maps each paper table to its registered protocol and config SHA-256 |
| Registered protocols / amendments | `notes/*_protocol.md`, `notes/*_preregistration_*.md`, `notes/paper2_harness_v2_amendment_*.md`, `notes/q1_max_protocol.md` | experimental designs frozen before execution |
| Claims / evidence audits | `notes/Q1_FINAL_CLAIM_AUDIT.md`, `notes/Q1_FINAL_EVIDENCE_MAP.md`; `src/analysis/audit_paper2_claims.py` | claim → artifact pins, re-checked in code by `make audit` |
| Manuscript sources | `manuscript/{main,main_ieee,supplement}.tex` | the claim surfaces the audit verifies |
| Archival deposit | Zenodo concept DOI [10.5281/zenodo.21322256](https://doi.org/10.5281/zenodo.21322256) | resolves to the latest version; each tagged release has its own version DOI on the concept record |

Reproduction entry points: `REPRODUCE.md` (experiment commands) and `make final-paper`
(hash verification → analysis → tables/figures → manifests → tests → PDF compile → claim audit).

## Invariants

- **ATTENUATION**: the registered attenuation outcome under frozen P/A/E rules is retained in
  `main.tex`, `main_ieee.tex`, and `supplement.tex`, and is asserted by `audit_paper2_claims.py`.
- **Manifest pinning**: 185 result CSVs match `MANIFEST.sha256` with zero unpinned extras.
- **Sealed science**: `results/raw/**` and the pinned CSVs are byte-stable; the v1.22 line is the
  v1.22.0 science.

## Version → registered design → experiment → outcome

Each row: the sealed science of that version, the registered design that governs it, and the
sealed manifest/DOI that pins it. Values live in the CSVs pinned by `MANIFEST.sha256`.

| Version | Registered design (config) | Experiment | Primary outcome |
|---|---|---|---|
| v1.3.0 | `paper2_harness_v2_registered_replication_protocol_001.md` | harness-v2 replication; zero-incremental-label gate | per-trigger mechanism confirmed |
| v1.4.0 | `paper2_phase3_extras_protocol_001.md` | monitoring baseline; natural-prevalence streams | Phase-3 controls |
| v1.6.0 | `paper2_temporal_stream_protocol_001.md`, `paper2_harness_v2_amendment_004.md` | corrected temporal streams; two-stage gate | v2 robustness; decision quality |
| v1.7.0 | `paper2_harness_v2_amendment_005.md` | external chronological validation; split two-stage gate | mechanism refutation-tested |
| v1.8.0 | `paper2_harness_v2_amendment_006.md` | causal observed-data gate; three-benchmark prediction | harm generalizes to all three benchmarks |
| v1.9.0 | `paper2_harness_v2_amendment_007.md` | zero-drift control; causal arm; sequential gate | always-deploy net-harmful under zero drift; gate recovers |
| v1.10.0 | `paper2_harness_v2_amendment_008.md` | size-matched zero-drift; risk-averse gates | confound refuted; loss recovered |
| v1.11.0 | `paper2_harness_v2_amendment_009.md` | four classifiers × every update generator; anytime-valid gate | zero-drift harm generalizes |
| v1.12.0 | `paper2_harness_v2_amendment_010.md` | Empirical-Bernstein confidence-sequence gate | tighter anytime-valid commit rule |
| v1.13.0 | `paper2_harness_v2_amendment_011.md`, `paper2_leakage_verification_001.md` | leakage-free causal arm; CS budget sweep | formal guarantee scope |
| v1.14.0 | `paper2_harness_v2_amendment_012.md` | three code-bug fixes; four-classifier size-matching; Clopper–Pearson intervals | size-matching claim scoped to SVC-RBF; harm holds under corrected regularization |
| v1.15.0 | `paper2_harness_v2_amendment_013.md` | leakage-free causal arm; symmetric A/B; per-class guarantee | zero-drift mechanism identified |
| v1.16.0 | `paper2_harness_v2_amendment_014.md` | four pre-declared mechanism criteria; VBC-SG with lifetime risk budget; prevalence sweep | mechanism identified |
| v1.17.0 | `final_kbs_protocol.md` | invariant test suite; `make final-paper` (P10) | reproducibility workflow sealed |
| v1.18.0 | `q1_max_protocol.md` (deltas D1–D7); `configs/q1_budget_frontier_v2.json` | mechanism decomposition; budget frontier; chronological matrix; Proposition 1 | affordable deployment-long guarantee (93% benefit at 512-cap; nothing committed under zero drift) |
| v1.19.x | `q1_final_acceptance_patch_protocol.md`, `q1_final_statistical_claims_patch_protocol.md` | final-q1 claim scoping | KBS candidate |
| v1.20.x | budget-frontier driver committed (see below); `configs/q1_budget_frontier_v2.json` | corrected deferred-commit timing; reproduced frontier | frontier reproduced bit-for-bit on unaffected arms |
| v1.21.0 | `paper2_symmetric_pipeline_dynamic_protocol_001.md`, `symmetric_pipeline_scenario_a_rewrite_protocol.md`; `configs/symmetric_pipeline_dynamic_v1.json` | symmetric-pipeline replication (seeds 3001–3030) | candidate-governance decomposition |
| v1.22.0 | `paper2_size_matched_own_transformer_protocol_001.md`, `size_matched_final_rewrite_protocol.md`; `configs/size_matched_own_transformer_v1.json` | size-matched self-contained challenger control (seeds 4001–4030) | ATTENUATION under frozen P/A/E rules; gating is conditional, not universal |

The full per-amendment result set (effect sizes, confidence intervals, seed ranges) is in the
sealed CSVs pinned by `MANIFEST.sha256` and cross-indexed by
`results/final_experiment_ledger.csv`.

## Budget-frontier driver provenance (v1.18/v1.20 line)

The 99 published budget-frontier arms (`results/raw/q1fc_*`, protocol `q1_max_protocol.md` D3)
were originally produced by a driver, `run_q1_faseC.py` (113 lines,
SHA-256 `655309bfec1c01924fd8708b6bde4c2ee055021ba6461959aea5502df11737c7`), that passed only the
gate/policy flags and relied on the runner's argparse defaults (notably window-size 128) for
every fixed stream parameter.

- **Committed, reproducible form**: `src/experiments/run_q1_budget_frontier.py` +
  `configs/q1_budget_frontier_v2.json`, in which every fixed parameter is explicit (nothing
  relies on argparse defaults) and each arm records its resolved config, command, environment,
  and source commit.
- **Functional equivalence — validated**: arms without deferred commits are provably unaffected
  by the deferred-commit temporal fix, so they must reproduce bit-for-bit. A single-seed
  pre-check (`q1fc_ps_full_vbcref_c512_bonf`, seed 501) and a full 30-seed × 3-arm control
  (`q1fc_ps_full_vbcref_c512_bonf`, `q1fc_ton_full_vbcref_c256_bonf`,
  `q1fc_ton_zero_ebcsdef_c256_bonf`) are **bit-identical** to the published arms (the only
  additional column is the documented `served_model_version`).
- **Arm classification**: 27 of 99 arms contain ≥1 deferred commit and were re-executed with the
  committed driver; the other 72 (zero deferred commits, provably byte-equal under the reorder)
  are reused. These fields are recorded structurally in `results/final_manifest.json`
  (`recovered_driver_sha256`, `frontier_reused_verified_arms`, `reuse_criterion`).

## Datasets

Public benchmarks, not redistributed: CICIDS2017 (Sharafaldin et al. 2018), UNSW-NB15
(Moustafa & Slay 2015), ToN-IoT (Alsaedi et al. 2020). Preprocessing and split layout in
`REPRODUCE.md`.
