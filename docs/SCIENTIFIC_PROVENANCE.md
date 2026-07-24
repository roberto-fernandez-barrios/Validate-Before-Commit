# Scientific Provenance

A neutral map from released versions to the scientific record. It narrates neither
conversations nor review cycles — only protocol evolution, scientific changes, associated
versions, invariants, and links to the authoritative artifacts.

## Sources of truth

| Artifact | Location | Role |
|---|---|---|
| Sealed result CSVs | `results/tables/**` pinned by `results/tables/MANIFEST.sha256` | 185 CSVs, byte-verifiable (`make verify-hashes`) |
| Final machine-readable manifest | `results/final_manifest.json` | final-kbs artifact manifest |
| Experiment ledger | `results/final_experiment_ledger.csv` (built by `src/analysis/make_final_experiment_ledger.py`) | maps each paper table to its registered protocol note + config SHA-256 |
| Registered protocols / amendments | `notes/*_protocol.md`, `notes/*_preregistration_*.md`, `notes/paper2_harness_v2_amendment_*.md`, `notes/q1_max_protocol.md` | experimental designs frozen before execution |
| Claims / evidence audits | `notes/Q1_FINAL_CLAIM_AUDIT.md`, `notes/Q1_FINAL_EVIDENCE_MAP.md` | claim → artifact pins; `make audit` re-checks them in code |
| Per-version narrative | **GitHub Releases** — <https://github.com/roberto-fernandez-barrios/Validate-Before-Commit/releases> | permanent human-readable changelog per tag |
| Archival deposit | Zenodo concept DOI [10.5281/zenodo.21322256](https://doi.org/10.5281/zenodo.21322256) | resolves to the latest version; every tagged release has its own minted version DOI listed on the concept record |

Reproduction entry points: `REPRODUCE.md` (experiment commands) and `make final-paper` (hash
verification → analysis → tables/figures → manifests → tests → PDF compile → claim audit).

## Invariants held across the sealed science

- **ATTENUATION**: the registered attenuation outcome is retained verbatim in `main.tex`,
  `main_ieee.tex`, and `supplement.tex`, and is asserted by `audit_paper2_claims.py`
  (guard "v1221 A: registered ATTENUATION outcome retained (main+ieee)").
- **Manifest pinning**: 185 result CSVs match `MANIFEST.sha256` with zero unpinned extras.
- **Claim surface**: the numeric claims in `manuscript/paper2_manuscript_draft_002.md` are the
  audited source of truth for `audit_paper2_claims.py`.
- Editorial-only releases (v1.20.1 onward, and the v1.22.x line) do not alter sealed result
  CSVs; the scientific content of the v1.22.x line is that of **v1.22.0**.

## Version → scientific record

Each version's full narrative lives in its GitHub Release (byte-identical to the internal
release notes it replaced). Governing registered designs are named below.

| Version | Scientific content | Registered design of record |
|---|---|---|
| v1.3.0 | harness-v2 replication; zero-incremental-label gate; per-trigger mechanism | `paper2_harness_v2_registered_replication_protocol_001.md` |
| v1.4.0 | Phase-3 extras (monitoring baseline, natural-prevalence streams) | `paper2_phase3_extras_protocol_001.md` |
| v1.5.0 | pristine-seed replication, canonical baselines, chronological stream | — |
| v1.6.0 | corrected temporal streams, v2 robustness, two-stage gate, decision quality | `paper2_temporal_stream_protocol_001.md`, `paper2_harness_v2_amendment_004.md` |
| v1.7.0 | external chronological validation, split two-stage gate, refutation-tested mechanism | `paper2_harness_v2_amendment_005.md` |
| v1.8.0 | causal observed-data gate; harm generalizes to all three benchmarks; prevalence retraction | `paper2_harness_v2_amendment_006.md` |
| v1.9.0 | zero-drift control reframes the thesis; genuinely causal arm; sequential gate | `paper2_harness_v2_amendment_007.md` |
| v1.10.0 | size-matched zero-drift refutes the confound; risk-averse gates recover the loss | `paper2_harness_v2_amendment_008.md` |
| v1.11.0 | zero-drift harm generalizes across 4 classifiers & every update generator; anytime-valid gate | `paper2_harness_v2_amendment_009.md` |
| v1.12.0 | Empirical-Bernstein confidence-sequence gate | `paper2_harness_v2_amendment_010.md` |
| v1.13.0 | leakage-free causal arm; formal guarantee scope; CS budget sweep | `paper2_harness_v2_amendment_011.md`, `paper2_leakage_verification_001.md` |
| v1.14.0 | three code-bug fixes; **size-match retraction**; Clopper–Pearson intervals | `paper2_harness_v2_amendment_012.md` |
| v1.15.0 | leakage-free causal arm (Table 8); zero-drift mechanism via symmetric A/B; per-class guarantee | `paper2_harness_v2_amendment_013.md` |
| v1.16.0 | mechanism under four pre-declared criteria; VBC-SG with lifetime risk budget; prevalence sweep | `paper2_harness_v2_amendment_014.md` |
| v1.17.0 | invariant test suite; `make final-paper` (P10) workflow | `final_kbs_protocol.md` |
| v1.18.0 | mechanism decomposition; affordable deployment-long guarantee; full chronological matrix; Proposition 1 | `q1_max_protocol.md` (deltas D1–D7) |
| v1.19.x | final-q1 KBS candidate; editorial claim hardening | `q1_final_acceptance_patch_protocol.md`, `q1_final_statistical_claims_patch_protocol.md` |
| v1.20.x | corrected deferred-commit timing; reproduced frontier; final statistical inference & claim scope | `notes/frontier_driver_recovery_report.md` (driver recovery, bit-for-bit) |
| v1.21.0 | candidate governance; symmetric-pipeline replication | `paper2_symmetric_pipeline_dynamic_protocol_001.md`, `symmetric_pipeline_scenario_a_rewrite_protocol.md` |
| v1.22.0 | controlled study (construction, evidence asymmetry, promotion); size-matched control | `paper2_size_matched_own_transformer_protocol_001.md`, `size_matched_final_rewrite_protocol.md` |
| v1.22.1–.6 | **editorial only** over sealed v1.22.0 science (scope wording, margin sensitivities, evidence–validation trade-off table, figure/bibliographic fixes) | `v1_22_1_editorial_scope_protocol.md` |

## v1.2.0 — preserved (no GitHub Release exists for this tag)

Verbatim, from the retired `notes/release_notes_v1.2.0.md`. The underlying experiments are also
documented in the retained `paper2_phase2i_replay_baseline_protocol_001.md` /
`_checkpoint_001.md`, `paper2_phase2j_probe_prevalence_protocol_001.md` / `_checkpoint_001.md`,
and `paper2_coupling_and_overclaim_revision_001.md`.

> **What changed since v1.1.0** — Two new pre-fixed robustness phases close the last two
> experimental objections from an external mock review, plus a statistics-hardening revision of
> the central analysis.
>
> **Phase 2i — replay retraining baseline.** `--adapt-strategy replay` (retrain-current-plus-
> replay, 50/50). Replay does NOT rescue naive triggering: significantly net-harmful in the
> harm regime (−4.54 [−7.06, −2.34] vs no-adaptation; worse than full replacement's −1.36) and
> benefit-lossy elsewhere (+6.59 vs +7.79). The gate composes with the update rule: on top of
> replay it restores safety (ToN +0.59) and recovers the lost benefit (PortScan +8.26).
>
> **Phase 2j — probe prevalence.** `--probe-prevalence` draws the labeled probe at the
> traffic's natural attack prevalence. The gate is essentially indifferent: full safety and
> benefit at π = 0.10 and even π = 0.01 (a single attack flow per probe); a 10× inspection
> budget changes nothing. The operative requirement is one labeled attack flow per decision,
> not a balanced sample.
>
> **Coupling-aware §5.2.** The degradation–benefit correlation is mathematically coupled
> (exhaustive re-pairing null: median r = −0.91; observed −0.89 not more extreme, p = 0.80) and
> is withdrawn as evidence. Replaced by (1) restoration-to-ceiling (σ 3.5 vs 7.4 pts, slope
> −0.87) and (2) the coupling-free contrast: within a deployment, detector scores are
> uninformative about the gain (per-seed r median +0.06) while deployed BA tracks it (−0.68).
>
> **Manuscript.** Overclaims softened; dangling appendix references fixed; full protocol
> detail added (candidate trains at current severity, never the final pool; train/probe
> disjointness; all sizes); Limitations rewritten. Claims audit extended to 112 checks, all
> passing.
