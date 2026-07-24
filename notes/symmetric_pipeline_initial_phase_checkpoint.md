# CHECKPOINT — Symmetric pipeline preparation and parity (initial phase)

Date: 2026-07-22
Branch: `feature/symmetric-pipeline-replication`
Protocol: `notes/paper2_symmetric_pipeline_dynamic_protocol_001.md` (FROZEN,
commit `88385660edd849f9ea54b2c6e8462d59119d2741`)

## A. Baseline

- Initial branch/HEAD: `main` @ `3b00cc406ed22e7e8fbbdd0f4f517f2d0353888c`
  (= sealing commit of tag `v1.20.2`; tag verified at HEAD).
- Baseline gates (before any change): pytest **67/67**, audit **538/538**,
  manifest hashes **164/164**, 0 unpinned extras / orphan dirs.
- Scientific hashes at baseline: `results/tables/MANIFEST.sha256`
  `dcf32268...e4420c36`; `results/final_manifest.json` (sealed checkout)
  `11474601...052a5b12` (see correction note in
  `notes/symmetric_pipeline_baseline_checkpoint.md`: the sealed test suite
  itself restamps this file's two provenance lines on every pytest run;
  restored with `git restore`, scientific content unchanged).
- Local files excluded (pre-existing, untracked, untouched): known local untracked files.

## B. Protocol

- Frozen at commit `8838566` (local tag `symmetric-pipeline-dynamic-protocol-local`,
  NOT pushed).
- Confirmatory seeds RESERVED: **3001-3030** (ledger/config/source/notes audit:
  zero collisions). NOT executed — firewalled in the driver (T12).
- Smoke seeds: **4242, 4243** (collision-free; SMOKE_ONLY).
- Estimands: Δ_naive,own vs never; Δ_transformer = BA_naive,own − BA_naive,frozen
  (primary answer to the objection); Δ_point−naive,own; Δ_strict−naive,own;
  secondary gate×transformer interactions (descriptive).
- Families: F1 (3 contrasts, harm own/full), F2 (3, transformer interaction/full),
  F3 (6, gate value own/full), F4 (12, zero-drift secondary) — all Holm FWER.
- Margins proposed (pending human approval, protocol §1.7): BA equivalence
  ±0.5 pp (sens. ±0.2/±1.0); attack-recall NI 1.0 pp (sens. 0.5/2.0); FPR NI
  0.5 pp (sens. 0.2/1.0).
- Confirmatory matrix: 42 arms = 6 scenarios (ps/unsw/ton × full/zero) ×
  (never + {naive,point,strict} × {frozen,own}); KS-max; **NOT executed** —
  `results/raw/symmetric_pipeline/` does not exist.

## C. Architecture (commit `2d93fe4`)

- `src/experiments/symmetric_pipeline.py` (new): `ModelPipeline` (scaler+PCA+
  classifier+metadata, predicts on RAW features), `DetectorPipeline` (monitor
  with its own explicit representation, pinned `frozen_initial` under both
  policies), `build_candidate_pipeline` (single constructor for
  `frozen_initial_transformer` and `own_transformer_per_model`),
  `build_raw_environment` (raw-stream re-expression of the historical env),
  `rows_hash`/`obj_hash`/`stream_raw_hash`.
- `src/experiments/run_paper2_readaptation_v2.py` (minimal refactor,
  default-preserving): Environment gains optional `stream_raw`,
  `init_train_raw`, `detector_factory`, `candidate_factory` (all default None
  → bit-identical historical behaviour, proven by parity); `build_environment`
  additionally records the raw stream (same draws, no extra RNG); `run_arm`
  routes detector/candidate construction through the optional factories;
  `build_parser`/`run_seed`/`write_outputs` extracted so the new driver reuses
  the exact scientific loop and CSV emission (no duplicated science).
- Frozen semantics: candidates always carry the ORIGINAL initial scaler/PCA
  objects (identity-checked, even after multiple commits). Own semantics:
  scaler fit on the candidate batch only, PCA on its scaled output only, same
  dim/solver/config/classifier; probe and future windows in no fit;
  candidate raw batch identical to frozen (hash-verified). Commit deploys the
  complete bundle; detector representation unchanged.
- Gate evaluates both pipelines on the same RAW probe (env transformer is the
  identity in raw mode; each pipeline transforms internally).

## D. Parity (T1) — frozen mode vs published v1.20.2 arms

Historical seeds 501-530 (parity ONLY, never new evidence), full 30-seed runs,
outputs under `results/smoke/symmetric_pipeline/parity/` (outside scientific
paths), compared file-by-file against the published frozen arms:

| parity arm | published dir | verdict |
|---|---|---|
| parity_ps_full_point | results/raw/q1fc_ps_full_point | **PASS** |
| parity_ton_full_naive | results/raw/q1fc_ton_full_none | **PASS** |
| parity_ton_zero_point | results/raw/q1fc_ton_zero_point | **PASS** |
| parity_ps_full_vbccoh_c64_bonf (deferred commits) | results/raw/q1fc_ps_full_vbccoh_c64_bonf | **PASS** (all 5 files BIT_IDENTICAL) |

For the first three arms: by_seed, summary, trigger_log and resolution_log are
**BIT_IDENTICAL**; window_results is exactly value-identical on all 14
published columns with ONE justified extra logging column
(`served_model_version`, added to the runner by f27bded AFTER those older CSVs
were generated; audited by audit q1fp G1). The deferred arm (re-run post-fix)
is bit-identical in all five files including that column. Detailed SHA-256
pairs: `parity_report.json` in each parity output dir.
Additional regression: the untouched historical CLI path
(`run_paper2_readaptation_v2`, default factories) re-run on seeds 501-502 of
ps_full_point matches the published rows exactly (same criterion).
`--validate-complete --parity` → PARITY COMPLETE.

## E. Invariants (tests/test_symmetric_pipeline.py, T1-T12, 16 tests)

- T1 frozen parity (synthetic, in-process, point gate AND deferred vbc_sg):
  exact-equality of window/trigger/summary/resolution frames.
- T2 candidate raw-batch identity frozen vs own (hash-per-trigger-window).
- T3 probe raw identity (identity pass-through; draw depends only on seed/t/pools).
- T4 no future leakage (own scaler/PCA exactly reproducible from the candidate
  batch alone) + train/probe pool row-disjointness.
- T5 own-pipeline role symmetry (gap inverts exactly under swap; incumbent
  handle inert; no label advantage).
- T6 frozen semantic identity (original transformer objects after ≥2 commits).
- T7 complete-bundle commit (served windows after commit reproduce exactly with
  the challenger's full bundle; commit window itself served by the old model).
- T8 detector independence (equal raw-stream hash, frozen_initial
  representation both policies, identical scores/thresholds up to first commit).
- T9 temporal semantics in raw mode (served_model_version lags adapted_now by
  exactly one window).
- T10 determinism (two identical runs: same stream/batch/metadata hashes, same
  outputs, exact).
- T11 security metrics (BA, attack recall, FPR, attack-F1 equal sklearn
  recomputation on raw windows).
- T12 confirmatory seed firewall (function level + driver CLI level; smoke and
  parity refuse 3001-3030 even WITH --confirmatory-authorized; the flag is
  incompatible with smoke/parity/dry-run).

## F. Smoke (SMOKE_ONLY)

- Seeds 4242, 4243; arms `sp_ps_full_point_own`, `sp_ton_zero_naive_own`.
- Runner terminates; logs, bundle commits, metrics and hashes written
  (run_config.json, command.txt, environment.json, raw_stream_hash.txt,
  completion_marker.json, SMOKE_ONLY_DO_NOT_ANALYZE marker).
- Outputs under `results/smoke/symmetric_pipeline/` only; NOT aggregated, NOT
  compared, NO conclusions drawn; no confirmatory seed used.

## G. Gates (end of phase)

- pytest **83/83** (67 baseline + 16 new invariants).
- audit **538/538**.
- manifest verify **164/164** pinned CSVs, 0 unpinned extras / orphan dirs.
- Scientific CSV diff: none (`git status` clean on tracked scientific paths;
  `results/tables/MANIFEST.sha256` hash unchanged `dcf32268...`).
- `results/final_manifest.json`: restored to sealed state after the pre-existing
  pytest restamp side effect (2 provenance lines; see A / blockers).
- Background processes: none (all runs synchronous and finished).

## H. Git

- `8838566` Freeze symmetric-pipeline dynamic replication protocol
  (protocol + baseline checkpoint notes).
- `2d93fe4` Add self-contained predictive pipelines to the readaptation harness
  (symmetric_pipeline.py; v2 runner compat refactor; temporal-semantics test
  string updated to the hook name).
- branch tip (the commit that contains this file; SHA self-reference is
  impossible — see `git log -1 feature/symmetric-pipeline-replication`)
  Validate frozen parity and symmetric-pipeline invariants
  (driver, config, invariant tests, checkpoint notes update).
- Working tree at end: clean except the two pre-existing personal untracked
  files. No merge, no push, no public tag, no release, no DOI. Local tag
  `symmetric-pipeline-dynamic-protocol-local` only.

## I. Blockers / risks / decisions requiring human approval

1. **Margins (protocol §1.7)** — proposed, must be approved before any
   confirmatory seed.
2. **Pre-existing test side effect** — `tests/test_gates.py` regenerates
   `results/final_manifest.json` (2 provenance lines) on every full pytest run,
   already at v1.20.2. Harmless to science but noisy for tree hygiene; decide
   whether to patch it in a future phase (out of scope here).
3. **window_results column note** — the three older published frontier anchor
   CSVs lack `served_model_version` (added later by f27bded); parity uses the
   documented value-identical-plus-justified-column criterion for them. The
   post-fix published arm is fully bit-identical, so the runner is exact.
4. **Expected confirmatory cost** — 42 arms × 30 seeds; measured ~10 s/seed on
   the anchor-style arms (~5-6 min per 30-seed arm) → rough total ≈ 4-5 h
   single-process, plus UNSW zero/full untested at scale in this phase.
5. No other technical blockers: parity exact, invariants green, firewall active.

## J. Verdict

**READY TO AUTHORIZE CONFIRMATORY SYMMETRIC-PIPELINE RUN**
(conditional on human approval of: protocol, margins §1.7, parity evidence §D,
own-transformer architecture §C, leakage/symmetry tests §E, and compute cost §I.4).
