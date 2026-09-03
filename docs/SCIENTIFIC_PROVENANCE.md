# Scientific Provenance

A neutral map from the sealed science to its authoritative artifacts:
**version → protocol → config → experiment → outcome → manifest → DOI**. It records registered
designs, the code and configs that realize them, the datasets, the invariants, and the archival
identifiers. It is not a changelog and contains no project or editorial history.

## Sources of truth

| Artifact | Location | Role |
|---|---|---|
| Sealed result CSVs | `results/tables/**`, pinned by `results/tables/MANIFEST.sha256` | 230 CSVs in the current v1.24.0 artifact (185 historical + 22 post-KBS sealed additively at v1.23.0 + 23 exact-feature-disjoint sensitivity CSVs sealed additively at v1.24.0), byte-verifiable via `make verify-hashes`; earlier releases pinned fewer and remain immutable |
| Final machine-readable manifest | `results/final_manifest.json` | artifact manifest (arm counts, hashes, statistical families) |
| Experiment ledger | `results/final_experiment_ledger.csv` (built by `src/analysis/make_final_experiment_ledger.py`) | maps each paper table to its registered protocol and config SHA-256 |
| Registered protocols / amendments | `notes/*_protocol.md`, `notes/*_preregistration_*.md`, `notes/paper2_harness_v2_amendment_*.md`, `notes/q1_max_protocol.md` | experimental designs frozen before execution |
| Claims / evidence audits | `notes/Q1_FINAL_CLAIM_AUDIT.md`, `notes/Q1_FINAL_EVIDENCE_MAP.md`; `src/analysis/audit_paper2_claims.py` | claim → artifact pins, re-checked in code by `make audit` |
| Manuscript sources | `manuscript/{main,main_ieee,supplement}.tex` | the claim surfaces the audit verifies |
| Archival deposit | Zenodo concept DOI [10.5281/zenodo.21322256](https://doi.org/10.5281/zenodo.21322256) | resolves to the latest version; each tagged release has its own version DOI on the concept record; the current version is v1.24.0, version DOI [10.5281/zenodo.22239106](https://doi.org/10.5281/zenodo.22239106) |

Reproduction entry points: `REPRODUCE.md` (experiment commands) and `make final-paper`
(hash verification → analysis → tables/figures → manifests → tests → PDF compile → claim audit).

## Invariants

- **ATTENUATION**: the registered attenuation outcome under frozen P/A/E rules is retained in
  `main.tex`, `main_ieee.tex`, and `supplement.tex`, and is asserted by `audit_paper2_claims.py`.
- **Manifest pinning**: the 230 sealed result CSVs of the current v1.24.0 artifact (185 historical
  entries, byte-identical to every earlier v1.22.x pin, plus the 22 post-KBS confirmatory CSVs
  pinned additively at v1.23.0, plus the 23 exact-feature-disjoint sensitivity CSVs pinned
  additively at v1.24.0) match `MANIFEST.sha256` byte-for-byte; `verify_results_manifest`
  reports 0 unpinned extras. Earlier releases pinned fewer CSVs and remain immutable.
- **Sealed science**: `results/raw/**` and the pinned CSVs are byte-stable; the v1.22 line is the
  v1.22.0 science; the v1.23 line adds the two registered post-KBS blocks (B2 size-matched
  drift, seeds 6001-6030; B1 common-harness baselines, seeds 5001-5030) sealed at v1.23.0; the
  v1.24 line adds the exact-cleaned-feature-disjoint integrity sensitivity (B2, seeds 7001-7030;
  B1, seeds 8001-8030) sealed additively at v1.24.0.

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
| v1.23.0 (B2) | `post_kbs_size_matched_drift_protocol_001.md`; `configs/post_kbs_size_matched_drift_v1.json` (operational keys derived from the sealed size-matched config, SHA recorded) | size-matched self-contained challengers under full drift (seeds 6001–6030; 21 arms) | HOMOGENEOUS-SIZE BENEFIT (+0.82/+1.66/+1.00 BA points); 0/6 positive gate effects at 2,000/class; outputs `results/tables/post_kbs_size_matched_drift_001/` (manifest-pinned at v1.23.0) |
| v1.23.0 (B1) | `post_kbs_common_harness_baselines_protocol_001.md` + `post_kbs_common_harness_baselines_amendment_001.md`; `configs/post_kbs_common_harness_baselines_v2.json` | registered common-harness comparison: never/naive/point/strict, ATC, DoC, calibrated ensemble, replay, river-DDM, river-ADWIN at 2,000/class (+512 sensitivity); seeds 5001–5030; 96 arms | ATC and ensemble COMPATIBLE with always-deploy at full drift; DoC/replay/DDM/ADWIN MATERIAL COST; S4 ordering change for ATC and ensemble; outputs `results/tables/post_kbs_common_harness_baselines_001/` (manifest-pinned at v1.23.0) |
| v1.24.0 (B2) | `ijis_exact_value_disjoint_sensitivity_protocol_001.md`; `configs/ijis_exact_value_disjoint_b2_v1.json` | exact-cleaned-feature-disjoint role assignment (every identical cleaned feature vector confined to one window, training or probe role); size-matched self-contained challengers under full drift (seeds 7001–7030; 21 arms) | PARTIAL ROBUSTNESS: size effect +0.53/+1.67/+0.38 BA points, all Holm-resolved, material in PortScan/UNSW-Recon and sub-material in ToN-IoT; outputs `results/tables/ijis_exact_value_disjoint_b2_001/` (manifest-pinned at v1.24.0) |
| v1.24.0 (B1) | `ijis_exact_value_disjoint_sensitivity_protocol_001.md`; `configs/ijis_exact_value_disjoint_b1_v1.json` | registered common-harness policy set under exact-cleaned-feature-disjoint roles (seeds 8001–8030; 96 arms) | PARTIALLY ROBUST (4/6 registered predicates): size-dependent policy ordering and no global dominance survive; ATC/calibrated-ensemble retention statements narrow; outputs `results/tables/ijis_exact_value_disjoint_b1_001/` (manifest-pinned at v1.24.0) |

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

## Historical commit identifiers

Frozen notes, configs and sealed verdict files record git SHAs from the development history
in which they were written (e.g. `8838566`, `96576bb`, `114513f…`, `7f9ea40…`). That history
was consolidated when the repository was curated for publication, so those objects are not
resolvable from the published history; `audits/protocol_commit_reachability.csv` enumerates
every such reference and its status. No identifier was rewritten or replaced — the notes are
frozen. The pre-run-freeze evidence that *is* verifiable from the published history is its
own commit chronology: each registered protocol and config commit precedes the corresponding
results commit.

## Datasets

Public benchmarks, not redistributed: CICIDS2017 (Sharafaldin et al. 2018), UNSW-NB15
(Moustafa & Slay 2015), ToN-IoT (Alsaedi et al. 2020). Preprocessing and split layout in
`REPRODUCE.md`.
