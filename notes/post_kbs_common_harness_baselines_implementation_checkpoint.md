# CHECKPOINT — Implementation of the amended common-harness baselines experiment (B1)

Date: 2026-08-31. Branch: `post-kbs-hardening`.
Protocol: `notes/post_kbs_common_harness_baselines_protocol_001.md` (frozen a68c90e) as
amended by `notes/post_kbs_common_harness_baselines_amendment_001.md` (amendment commit
5a4ce6f, BEFORE this implementation). Config: `configs/post_kbs_common_harness_baselines_v2.json`
(byte-identical to its amendment-freeze state). No B1 confirmatory result existed before
this implementation (seeds 5001–5030 untouched; verified again at this checkpoint).

## A. What was implemented

1. `run_symmetric_pipeline_replication.py`: `common_harness_arms` builder (matrix_kind
   `post_kbs_common_harness_baselines`): 96 arms = 6 scenarios × (never + 9 primary
   policies @2,000/class + 6 secondary policies @512/class), `own_transformer_per_model`,
   tags `bh_*`, per-arm origin recorded; policy flags override scenario flags (so
   DDM/ADWIN keep their trigger role at zero drift). No science-module change was needed:
   every policy reuses the sealed v2 code paths (atc/doc gates, ensemble_cal, replay,
   ddm_river/adwin_river) driven over raw own-transformer environments.
2. `src/analysis/make_post_kbs_common_harness_001.py` — the confirmatory analysis,
   committed BEFORE the confirmatory run: families PF1–PF3 (primary, @2,000) and SF4–SF5
   (secondary), Holm within family, seed = inferential unit; anchor-vs-anchor contrasts
   emitted as DESCRIPTIVE only (amendment: no double-testing of B2's or the sealed
   control's estimands); per-cell MATERIAL GAIN / MATERIAL COST / COMPATIBLE / UNRESOLVED
   classification; statements S1–S4 evaluated literally; per-policy budget table
   (ATC/DoC training-time validation labels documented analytically — the runner's
   counters do not include them); recall/FPR NI guardrails (language-gating);
   run-completion ledger. No sign-rate criterion anywhere.
3. `tests/test_post_kbs_common_harness.py` — implementation-fidelity suite (11 tests).

## B. Implementation-fidelity gates (config `fidelity_gates`), status

| Gate | Where | Status |
|---|---|---|
| ATC/DoC traced to the published definitions | test_F1: shipped `_labelfree_estimate` equals an independent transcription of Garg et al. (threshold at the (1−acc) source-confidence quantile) and Guillory et al. (difference of confidences) exactly | PASS |
| ATC/DoC raw-mode fidelity | test_F2: ModelPipeline path bit-agrees with the plain-model path on the same classifier/data; test_F3: e2e own-transformer ATC arm — probability=True candidates, triggers = commits + rejects | PASS |
| river reference implementations | test_F4: `river_drift.binary.DDM()` / `river_drift.ADWIN(delta=0.002)` objects, river 0.25.0 (requirements-lock pin); input granularity documented in-source: the monitors receive the incumbent's per-flow Bernoulli errors on the 8-label/window monitoring sample (800 labels/stream), never candidate-validation labels; deploy-on-fire (no reject) | PASS |
| DDM/ADWIN e2e | test_F5/F6: 8×windows monitoring labels booked; zero gate rejections | PASS |
| Calibrated ensemble | test_F7 (members Platt-calibrated, probabilistic nesting, predict = soft-vote threshold; labelled standard baseline / internal implementation everywhere, never SoTA); test_F8 e2e: commits every trigger, cannot decline | PASS |
| Replay 50/50 rule preserved | test_F9: every replay candidate's training-row hash reconstructs exactly as half proposal-time-severity + half severity-0 draws from the per-trigger RNG | PASS |
| probability=True does not change `.predict` | test_F10 (SVC(probability=proba) — plain in-libsvm Platt, not a CalibratedClassifierCV wrapper), confirming the amendment §3 fairness note | PASS |
| Shared raw stream across policy arms | test_F11 | PASS |
| Anchor flag-off byte-parity | driver `--parity` vs stored v1.21.0-code smoke outputs (seeds 4242–4243, comparison only): **PASS, all 5 CSVs BIT_IDENTICAL** | PASS |
| Smoke covers every new code path | 6/6 smoke arms complete on 5401–5402 (atc, doc, enscal, ddm, adwin, replay — all under own-transformer raw mode on the real benchmarks), SMOKE_ONLY | PASS |
| Grid/firewall | test_G1 (96 arms, tags, flag overrides, frozen 512-exclusions); test_G2 (5001–5030 refused in every unauthorized mode) | PASS |

Full suite: **211 passed** under the paper2 environment (= requirements-lock: numpy
2.4.4, pandas 3.0.3, scikit-learn 1.8.0, scipy 1.17.1, river 0.25.0, python 3.11.15).
Note: the paper2 environment is the environment of record for validation and every run;
the base interpreter lacks `river`, so the river fidelity tests require paper2.

## C. Not executed

Seeds 5001–5030 remain untouched at this commit. The confirmatory run is the next step:
`--run --confirmatory-authorized --config configs/post_kbs_common_harness_baselines_v2.json`
under the paper2 environment (arm-partitioned across parallel workers via the registered
`--only-arm` CLI for wall-clock only — same commands, same arms, no science change), with
no retries, substitutions, parameter changes or arm edits.
