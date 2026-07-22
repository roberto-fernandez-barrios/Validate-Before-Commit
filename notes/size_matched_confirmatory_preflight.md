# Preflight — Size-matched own-transformer control (confirmatory readiness)

Date: 2026-07-22
Branch: `feature/size-matched-own-transformer`
Protocol: `notes/paper2_size_matched_own_transformer_protocol_001.md`
(protocol commit `114513f8613d0b76b206d03dc74aeefe1ea7200e`).

## Frozen inputs

- Config: `configs/size_matched_own_transformer_v1.json`
  SHA-256 `6873cc1a3ed0048238104ff907da1675384f353302770918219a2cff03e2df60`
- Confirmatory seeds: **4001–4030** (virgin block; scan record in protocol §1.4).
- Smoke seeds: **4401–4402**. Parity reference seeds: 4242–4243 (previous
  phase's smoke seeds; comparison only).
- Matrix: 21 arms (3 zero-drift scenarios × {never, naive/point/strict ×
  {512, 2000}}), own_transformer_per_model only.
- Registered analysis (pre-run): `src/analysis/make_size_matched_own_transformer_001.py`
  (families F1–F4, margins, P/A/E rules §6 literal; E3 contradiction
  threshold registered pre-run in code: naive-2000 with ≥5 evaluable H5
  commits and harmful_rate_h5 ≥ 0.4).

## Implementation (minimal, no science duplication)

- `src/experiments/run_paper2_readaptation_v2.py`: new flag
  `--candidate-size-per-class` (default None = historical byte-identical
  path) + `nested_candidate_draw` (protocol §2.2 canonical draw: historical
  B512 continued by E1488 from the same per-trigger RNG stream; asserts
  full_replace and severity 0; refuses any other size).
- `src/experiments/run_symmetric_pipeline_replication.py`: `--config`
  (default = historical config, behavior unchanged), `size_matched_arms`
  21-arm builder, config-driven firewall message, per-candidate provenance
  capture (`candidate_provenance.jsonl`: size, full row hash, nested-prefix
  row hash, scaler/PCA/gamma provenance), `config_sha256` recorded in each
  arm's `run_config.json`.
- No change to stream generation, ModelPipeline, DetectorPipeline,
  build_candidate_pipeline, gates, temporal semantics, resolution logging or
  harmful-commit accounting.

## Test gates (all green)

- `pytest tests -q`: **110 passed** (96 baseline + 14 new in
  `tests/test_size_matched_control.py`).
- New suite maps to protocol §8: T1 flag-512 ≡ flag-absent bit parity
  (in-process); T2 nested draw unit + end-to-end + provenance wrapper;
  T3 same raw stream across arms; T4 same triggers/probes across sizes;
  T5 no leakage (scaler saw exactly 2×size rows, refit reproduces params);
  T6 identical hyperparameters (C=1.0, gamma='scale', same training seed) +
  `cn` scaling unreachable; T7 complete-bundle commit at full size;
  T8 determinism; T9 firewall on 4001–4030 (new config); T10 metrics
  recomputation; T11 sealed v1.21.0 artifact unchanged (all 173 pinned
  hashes re-verified inside the test).

## Baseline parity at real scale (T1b) — PASS

`--parity --config configs/size_matched_own_transformer_v1.json`
(arm `parity_ton_zero_naive_512`, seeds 4242–4243) vs the stored
v1.21.0-code smoke outputs of `sp_ton_zero_naive_own`:
**5/5 files BIT_IDENTICAL** (by_seed, summary, window_results,
resolution_log, trigger_log). Verdict PASS
(`results/smoke/size_matched_own_transformer/parity/parity_ton_zero_naive_512/parity_report.json`).

## Smoke (seeds 4401–4402, SMOKE_ONLY_DO_NOT_ANALYZE) — mechanical PASS

Arms executed (the registered maximum): `sm_ps_zero_naive_512`,
`sm_ps_zero_naive_2000`, `sm_ps_zero_strict_2000`, under
`results/smoke/size_matched_own_transformer/` (gitignored, marker file
present). Mechanical validations only — no aggregation, no interpretation:

- Nesting at real scale: 5/5 common (seed, window) candidates satisfy
  `nested_prefix_row_hash(2000) == training_row_hash(512)` — PASS.
- Candidate sizes recorded: {512} in the 512 arm, {2000} in the 2000 arms.
- Raw-stream hash identical across all three smoke arms (single SHA-256
  `65c9e46c…b72fa77b` for the three `raw_stream_hash.txt`).
- `candidate_provenance.jsonl` of naive-2000 and strict-2000 are
  byte-identical (candidate construction independent of the gate, as
  designed).
- Commits observed under naive; strict rejected proposals (gate exercised).
- Output hashes (by_seed.csv): naive_512 `44d4b86f…`, naive_2000
  `781fcea7…`, strict_2000 `d948a233…`.

## Repository gates

- `audit_paper2_claims`: 561 PASS / 0 FAIL.
- `verify_results_manifest`: 173/173, 0 unpinned extras.
- `--list-arms`: 21 arms enumerated; `--dry-run`: 21 argv lines, nothing
  executed, block 4001–4030 firewalled.
- Firewall live-tested: `--smoke --seeds 4005` refused (exit 1).
- v1.21.0 sealed artifact untouched (T11 + manifest gate).

## GO / NO-GO

All protocol §10 preconditions hold: protocol committed, tests green,
nesting PASS, baseline parity PASS, config frozen, preflight PASS.

**GO** for the confirmatory execution: 21/21 arms × 30/30 seeds
(4001–4030), synchronous, no background processes, zero parameter changes.
