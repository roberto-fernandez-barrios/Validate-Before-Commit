# Budget-frontier driver — compatibility record

This path is retained because it is referenced by the sealed v1.22.6 artifact manifest
(`results/final_manifest.json`, field `recovery_report`). It records, in neutral terms, the
provenance and validation of the budget-frontier driver. The full scientific mapping lives in
[docs/SCIENTIFIC_PROVENANCE.md](../docs/SCIENTIFIC_PROVENANCE.md).

## Driver identity

- Original driver: `run_q1_faseC.py` (113 lines),
  SHA-256 `655309bfec1c01924fd8708b6bde4c2ee055021ba6461959aea5502df11737c7`.
  It passed only the gate/policy flags and relied on the runner's argparse defaults (notably
  window-size 128) for every fixed stream parameter.

## Committed reproducible form

- `src/experiments/run_q1_budget_frontier.py` + `configs/q1_budget_frontier_v2.json`, in which
  every fixed parameter is explicit (nothing relies on argparse defaults); each arm records its
  resolved configuration, command, environment and source commit.

## Bit-identity validation

Arms without deferred commits are provably unaffected by the deferred-commit temporal fix and
must reproduce bit-for-bit:

- **Single-seed pre-check**: `q1fc_ps_full_vbcref_c512_bonf`, seed 501 — bit-identical to the
  published arm (the only additional column is the documented `served_model_version`).
- **Full 30-seed × 3-arm control**: `q1fc_ps_full_vbcref_c512_bonf`,
  `q1fc_ton_full_vbcref_c256_bonf`, `q1fc_ton_zero_ebcsdef_c256_bonf` — all bit-identical.

## Arm classification

- **27 / 99** arms contain ≥1 deferred commit → re-executed with the committed driver.
- **72 / 99** arms have zero deferred commits (provably byte-equal under the reorder) → reused.

These fields are recorded structurally in `results/final_manifest.json`
(`recovered_driver_sha256`, `frontier_reused_verified_arms`, `reuse_criterion`).
