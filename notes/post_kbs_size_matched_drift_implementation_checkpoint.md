# CHECKPOINT — Implementation of the size-matched-under-drift experiment (B2)

Date: 2026-08-31. Branch: `post-kbs-hardening`.
Registered protocol: `notes/post_kbs_size_matched_drift_protocol_001.md` (frozen at commit
a68c90e, BEFORE this implementation). Config: `configs/post_kbs_size_matched_drift_v1.json`
(byte-identical to its frozen state; runnable keys are DERIVED by the driver from the
sealed `configs/symmetric_pipeline_dynamic_v1.json`, whose SHA-256 is recorded per arm as
`derived_operational_from` — the frozen preregistration JSON was never edited).

## A. Authorization record

Implementation and execution of B2 were AUTHORIZED by user decision on 2026-08-31
("B2: AUTHORIZED FOR IMPLEMENTATION AND EXECUTION, subject to the normal
implementation-before-confirmatory validation gates"). B1 remains governed by amendment
001 (commit 5a4ce6f) and its own gates. The v1 config's freeze-time status string is
retained as a historical record; this checkpoint is the authorization record the guard
tests reference.

## B. What was implemented (exactly the preregistered mechanism)

1. `run_paper2_readaptation_v2.py`:
   - new flag `--nested-draw-domain {zero,drift}` (default `zero`);
   - `nested_candidate_draw` extended per protocol 2.1: under `drift`, B_base and the
     extension are drawn from the SAME per-trigger RNG stream, BOTH at the proposal-time
     severity sev(t), so both sizes sample the same proposal-time target mixture;
   - the sealed zero-domain path is byte-identical and still refuses severity > 0.
2. `run_symmetric_pipeline_replication.py`:
   - `size_matched_drift_arms` builder (matrix_kind `post_kbs_size_matched_drift`):
     21 arms = 3 full-drift scenarios x (never + {naive,point,strict} x {512,2000}),
     own_transformer_per_model, tags `smd_*`;
   - operational-skeleton derivation in `load_config` (fixed flags / data / scenarios /
     policies from the sealed base config; output roots; smoke arms; parity arms), with
     the base config SHA-256 recorded per arm;
   - `_recording_candidate_factory` now records `candidate_sev` (proposal-time severity
     of each candidate, protocol 2.1) via the arm's raw stream; sealed outputs untouched.
3. `src/analysis/make_post_kbs_size_matched_drift_001.py` — the confirmatory analysis,
   committed BEFORE the confirmatory run as the protocol requires: families G1-G4 (Holm
   within family, deterministic centered paired bootstrap, seed = inferential unit),
   CI90 equivalence at the ±0.5-pp margin (0.2/1.0 sensitivities), recall/FPR NI
   guardrails (language-gating), nesting+severity audit, naive-coupling audit (raises on
   violation), gated pairs classified seed-paired, DESCRIPTIVE-ONLY future-value
   accounting, and the protocol section 4 taxonomy (SIZE BENEFIT / SIZE COST /
   NO MATERIAL SIZE EFFECT / RESOLVED SUB-MATERIAL / UNRESOLVED; HOMOGENEOUS /
   HETEROGENEOUS program label). No sign-rate criterion exists anywhere.

## C. Required implementation checks (16/16), status before any confirmatory seed

| # | Required check | Where | Status |
|---|---|---|---|
| 1 | 512-path parity | test_C1 (in-process, drift domain) + driver parity arm `parity_smd_ps_full_point_own_nested512` vs stored v1.21.0-code smoke outputs | PASS (all CSVs BIT_IDENTICAL) |
| 2 | B512 prefix equality inside B2000 at nonzero severities | test_C2 (sev 0.37/0.85/1.0) + confirmatory-scale nesting audit in the analysis | PASS |
| 3 | Same proposal-time severity across sizes | test_C3_C5 (cand_sev_used equal) + analysis sev audit | PASS |
| 4 | Same raw stream hash | test_C4 + per-arm raw_stream_hash.txt | PASS |
| 5 | Same trigger state for exactly coupled naive arms | test_C3_C5 (trigger+commit timelines identical) + analysis audit_coupling (raises on violation) | PASS |
| 6 | Documented loss of exact coupling after gate divergence | protocol 2.2 + analysis audit_coupling labels + test_C6 | PASS |
| 7 | Same raw probe for comparable proposal states | test_C7 ((seed,t)-keyed probe RNG) | PASS |
| 8 | Own scaler/PCA fit only on candidate batch | test_C8 (refit reproduction; n_samples_seen = 2·size) | PASS |
| 9 | Complete-bundle deployment | test_C9_C10 | PASS |
| 10 | t+1 serving semantics | test_C9_C10 (served_model_version) | PASS |
| 11 | Same SVC hyperparameters | test_C11 | PASS |
| 12 | Determinism | test_C12 (bit-equal frames + hashes) | PASS |
| 13 | No seed collision | test_C13_C14 (6001-6030/6401-6402 disjoint from every ledgered block incl. 5001-5030/5401-5402) | PASS |
| 14 | Confirmatory firewall | test_C13_C14 (refusals in smoke/parity/dry-run/development; smoke+parity seeds pass) | PASS |
| 15 | No train/probe/future leakage beyond frozen harness semantics | role-disjoint partitions unchanged; test_C8 | PASS |
| 16 | Analysis reads seed trajectories as inferential units | test_C16 + analysis paired() assertion | PASS |

## D. Gates executed (paper2 env = requirements-lock: numpy 2.4.4, pandas 3.0.3,
scikit-learn 1.8.0, scipy 1.17.1; python 3.11.15)

- Unit/synthetic suite: full pytest **198 passed** (includes the sealed suites:
  test_size_matched_control T1-T11 and test_symmetric_pipeline T1-T12 stay green, so the
  zero-domain byte path and the sealed artifacts are untouched).
- Driver parity (`--parity --config configs/post_kbs_size_matched_drift_v1.json`,
  seeds 4242-4243, comparison only): **PASS, 2/2 arms, every runner CSV BIT_IDENTICAL**
  vs `results/smoke/symmetric_pipeline/sp_ps_full_point_own` — for BOTH the flag-off
  path and the nested drift-domain 512 path.
- Smoke (`--smoke`, seeds 6401-6402, SMOKE_ONLY): 3/3 arms complete
  (smd_ps_full_naive_512, smd_ps_full_naive_2000, smd_ton_full_strict_2000).

## E. Not executed

Seeds 6001-6030 remain untouched at this commit; the confirmatory run is the NEXT step
and will use exactly `--run --confirmatory-authorized --config
configs/post_kbs_size_matched_drift_v1.json` under the paper2 environment, with no
retries, substitutions, parameter changes or arm edits.
