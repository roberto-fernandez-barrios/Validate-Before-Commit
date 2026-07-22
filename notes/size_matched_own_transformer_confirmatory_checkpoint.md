# CHECKPOINT — Size-matched own-transformer control

Date: 2026-07-22
Branch: `feature/size-matched-own-transformer`
Registered protocol: `notes/paper2_size_matched_own_transformer_protocol_001.md`

## A. Baseline

- Start: tag `v1.21.0`, commit `7f9ea405f6bd30e457f714c1a5ebc6b463e74c50`
  (scientific commit `588c89e90b823813043a559e7ebd307cf57baf2a`).
- Branch created from that commit; `main` untouched.
- Initial gates: pytest 96/96, audit 561/0, manifest 173/173 (after restoring
  the sealed CRLF disk representation of 9 content-intact CSVs — see
  `notes/size_matched_own_transformer_baseline_checkpoint.md`).
- Sealed hashes unchanged throughout:
  `results/final_manifest.json` = `5f8a1e43…cab443ee6`,
  `results/tables/MANIFEST.sha256` = `8500c6e2…7cd3cdc43`.

## B. Frozen protocol

- Protocol commit: `114513f8613d0b76b206d03dc74aeefe1ea7200e` (committed
  before any implementation, smoke or confirmatory seed).
- Config: `configs/size_matched_own_transformer_v1.json`, SHA-256
  `6873cc1a3ed0048238104ff907da1675384f353302770918219a2cff03e2df60`
  (recorded identically in all 21 `run_config.json`).
- Confirmatory seeds: 4001–4030 (virgin block, scan documented in protocol
  §1.4). Smoke seeds: 4401–4402. Parity reference: 4242–4243.
- Matrix: 21 arms = 3 zero-drift scenarios × {never, naive/point/strict ×
  {512, 2000}}, own_transformer_per_model only.
- Margins: BA equivalence ±0.5 pp (sens. ±0.2/±1.0); recall NI −1.0 pp;
  FPR NI +0.5 pp (v1.21.0 values, reused).
- Families F1–F4 and outcome rules P/A/E frozen in protocol §5–6;
  E3's contradiction detector registered pre-run in the analysis code
  (freeze commit), threshold: naive-2000 with ≥5 evaluable H5 commits and
  harmful_rate_h5 ≥ 0.4.

## C. Implementation

- `--candidate-size-per-class` in `run_paper2_readaptation_v2` (default
  None = byte-identical historical path).
- Nested-batch mechanism (`nested_candidate_draw`): at each proposal,
  `cand_rng = default_rng(seed·100003 + t)` draws the UNCHANGED historical
  B512 (bit-identical to v1.21.0), then continues the same stream through
  the same sampler for E1488; batch_2000 = concat(B512, E1488). The 512
  condition trains on B512, the 2000 condition on batch_2000; rows 0–1023 of
  batch_2000 ARE the 512 batch (same rows/labels/order/hash). Only defined
  at severity 0 under full_replace (asserted).
- Exact semantics: incumbent stays at 2000/class; SVC C = 1.0 both sizes
  (`cn` scaling unreachable); gamma configured `'scale'` both; training
  seed `seed+t+1` both; per-candidate provenance (size, full row hash,
  nested-prefix hash, scaler mean/scale hashes, PCA components/EV hashes,
  configured+effective gamma, classifier params, creation window) in
  `candidate_provenance.jsonl` per arm.
- Files changed (freeze commit `c4df062…`): science module (flag + draw),
  driver (`--config`, 21-arm builder, provenance capture, config-driven
  firewall), registered analysis, config, tests, preflight note. No change
  to streams, pipelines, gates, temporal semantics, resolution logging or
  harm accounting.

## D. Tests

`tests/test_size_matched_control.py` (14 tests; suite total 110/110):

- T1 512 parity: (a) in-process flag-512 ≡ flag-absent bit-identical;
  (b) driver parity vs stored v1.21.0-code smoke outputs
  (`sp_ton_zero_naive_own`, seeds 4242–4243): **5/5 BIT_IDENTICAL**.
- T2 nesting: unit + end-to-end + provenance wrapper; at confirmatory scale
  the analysis verified **999 (seed, window) pairs** with
  prefix-hash(2000) == training-hash(512), zero violations.
- T3 raw-stream pairing: identical stream hash across all arms (test +
  identical `raw_stream_hash.txt` digests per scenario at scale).
- T4 probe identity: same triggers and same (seed, t)-keyed probe draws
  across sizes.
- T5 leakage: scaler/PCA refit-reproducible from the candidate batch alone;
  scaler saw exactly 2×size rows.
- T6 hyperparameter identity: identical constructor params, C=1.0,
  gamma='scale', same training seed; `cn` scaling not reachable.
- T7 temporal semantics / complete bundle: committed 2000-bundle serves from
  t+1 and reproduces logged metrics exactly.
- T8 determinism: identical reruns bit-identical.
- T9 firewall: 4001–4030 refused in smoke/parity/dry-run/development (and
  live-tested via CLI, exit 1).
- T10 metrics: BA/recall/FPR match independent sklearn recomputation.
- T11: sealed v1.21.0 artifact byte-identical after the full suite (173
  hashes re-verified inside the test).

## E. Execution

- Expected 21 arms / completed **21/21** (`--validate-complete`:
  "21/21 COMPLETE"). 30/30 seeds (4001–4030) in every arm.
- Synchronous, sequential, no background processes; one driver invocation
  per arm; zero retries, zero failures, zero `--resume`, zero seed
  substitutions, zero parameter changes.
- Duration: 44.2 min total compute (median arm 127.5 s, max 182 s).
- Every arm carries completion marker, resolved config, command,
  environment, raw-stream hashes, candidate provenance, and the frozen
  config SHA; all 21 executed at source commit `c4df06202c3b` (freeze).

## F. Primary results (pp of balanced accuracy; CI95; Holm within family)

| dataset | naive_512 − never (desc.) | naive_2000 − never (F1) | naive_2000 − naive_512 (F2) | point_2000 − naive_2000 (F3) | strict_2000 − naive_2000 (F3) |
|---|---|---|---|---|---|
| ps_zero | −1.70 [−2.05, −1.36] | +0.19 [−0.15, +0.55], p_holm=0.906 | **+1.89** [+1.54, +2.23], p_holm=3e−5 ✓ | +0.05 [−0.00, +0.12], p_holm=0.436 | +0.13 [−0.07, +0.34], p_holm=0.441 |
| unsw_zero | −0.65 [−0.77, −0.55] | −0.02 [−0.10, +0.06], p_holm=1.0 | **+0.63** [+0.53, +0.73], p_holm=3e−5 ✓ | +0.01 [−0.02, +0.04], p_holm=0.611 | +0.06 [−0.01, +0.12], p_holm=0.436 |
| ton_zero | −0.24 [−0.39, −0.10] | −0.01 [−0.05, +0.04], p_holm=1.0 | **+0.23** [+0.10, +0.38], p_holm=0.002 ✓ | +0.02 [+0.00, +0.04], p_holm=0.436 | +0.03 [−0.01, +0.08], p_holm=0.441 |

- CI90 equivalence (±0.5 pp primary margin) for F1: ps_zero
  [−0.10, +0.49] ✓ (upper bound 0.494, inside by 0.006 — reported honestly),
  unsw_zero [−0.09, +0.05] ✓, ton_zero [−0.05, +0.03] ✓ → **all three
  naive_2000 vs never equivalent**.
- All six F3 gate contrasts CI90-equivalent to naive_2000 within ±0.5 ✓;
  none Holm-significant; no gate win ≥ +0.5 pp.
- F2 replicates the v1.21.0 residual harm on FRESH seeds at 512 (descriptive
  naive_512 − never: −1.70 / −0.65 / −0.24) and shows the size upgrade
  recovers essentially all of it.
- E5/F4 interaction (secondary): gate value shrinks significantly at
  matched size (e.g. ps_zero strict: −1.54 [−1.89, −1.20], Holm-sig.) —
  gates were compensating small-challenger noise, and have ~nothing left to
  recover at size 2000.

## G. Guardrails (primary NI margins; per relevant cell)

- All 2000-size gate cells pass BOTH recall NI (−1.0 pp) and FPR NI
  (+0.5 pp) vs naive_2000, in all three datasets.
- At 512, guardrails pass except **unsw_zero strict_512 recall-NI FAIL** —
  replicating the v1.21.0 R4 finding (strict gate recall trade-off in UNSW)
  on fresh seeds; its trade-off must be described explicitly wherever that
  cell is used.
- BA/recall/FPR cell values in
  `results/tables/size_matched_own_transformer_001/security_metrics.csv`.

## H. Future harm (descriptive only; commits cluster within seed)

naive arms, 111 logged commits each (13 censored at H5, 98 evaluable):

| cell | harmful H1/H3/H5/H10 | rate_h5 | mean Δres5 (pp) |
|---|---|---|---|
| ps_zero naive_512 | 56/61/61/61 | 0.62 | −1.03 |
| ps_zero naive_2000 | 39/43/47/43 | 0.48 | +0.03 |
| unsw_zero naive_512 | 48/54/58/53 | 0.59 | −0.38 |
| unsw_zero naive_2000 | 46/46/51/42 | 0.52 | −0.06 |
| ton_zero naive_512 | 34/40/45/48 | 0.46 | −0.13 |
| ton_zero naive_2000 | 20/32/35/36 | 0.36 | +0.02 |

- At size 2000 the MEAN future value of committed challengers is ≈ 0
  (−0.06…+0.03 pp), vs clearly negative at 512; the ~36–52% "harmful"
  H5 rates at 2000 are near-symmetric small-magnitude sign fluctuations
  around zero, not the directional loss seen at 512.
- Caveat: descriptive; no binomial bound, no population probability, no
  production prevalence (protocol §11).

## I. Outcome (frozen rules, applied literally)

**ATTENUATION**

- P1 material size-matched harm: **False** (no dataset with
  naive_2000 − never ≤ −0.5, CI95 < 0, Holm-sig.).
- P2 gate win ≥ +0.5 Holm-sig. at 2000: **False**. P3: **False** (vacuous).
- E1 all three F1 contrasts CI90 inside ±0.5: **True**.
- E2 gates equivalent to naive_2000 in all datasets: **True**.
- E3 no harmful-future-value contradiction: **False** — the registered
  detector (≥5 evaluable H5 commits and rate ≥ 0.4) fired in ps_zero
  (0.4796) and unsw_zero (0.5204).
- P requires P1∧P2∧P3 → not P. E requires E1∧E2∧E3 → not E. → **Outcome A**.

Honest reading within the frozen rules: the registered E3 threshold keys on
the SIGN RATE of committed-challenger future value, and ~50% negative signs
with ≈0 mean magnitude is what a null effect looks like; had E3 keyed on
magnitude, the result pattern would have classified as ELIMINATION. The
rules are frozen, the outcome is ATTENUATION, and the permitted
interpretation is applied as registered — this nuance is recorded for the
manuscript phase, not used to reclassify.

Permitted interpretation (verbatim): *"Candidate size is an important
amplifier, while the remaining promotion risk is dataset- and
policy-dependent."*

## J. Implication for the paper (no text modified in this phase)

- **Conserved v1.21.0 claims:** the zero-drift promotion harm at the
  registered 512-challenger configuration is real and replicates on fresh
  seeds (−1.70/−0.65/−0.24 pp); gate value at that configuration replicates;
  the unsw strict recall trade-off replicates; all historical results
  remain valid as stated for their configuration.
- **Claims to scope/acotar:** the zero-drift harmful-promotion claim must be
  explicitly conditioned on the challenger/incumbent size asymmetry: with
  size-matched self-contained challengers the mean harm is equivalent to
  never-adapt within ±0.5 pp in all three datasets, and point/strict gates
  no longer add measurable BA value (their benefit at 512 is largely
  compensation for small-challenger noise — F4).
- **Claims that can be reinforced:** candidate-training size is identified
  as the dominant, Holm-significant driver (F2: +1.89/+0.63/+0.23 pp);
  the governance message shifts from "gates recover the zero-drift loss" to
  "gates are a cheap insurance layer whose value concentrates exactly where
  challengers are informationally disadvantaged".
- **Results to add:** the 21-arm size-matched control (tables under
  `results/tables/size_matched_own_transformer_001/`), the ATTENUATION
  outcome with its rules trace, the F4 interaction, the descriptive
  future-value table, and the residual per-commit sign-rate observation
  (with its magnitude context) as the honest statement of remaining
  re-estimation/promotion risk.
- **Historical results:** untouched and unmodified; the sealed v1.21.0
  artifact is intact.

## K. Gates (at checkpoint time)

- pytest: **110 passed** (96 baseline + 14 new).
- audit_paper2_claims: **561 PASS / 0 FAIL**.
- verify_results_manifest: **173/173 pinned match**; 10 unpinned extras =
  exactly the new (unsealed) `size_matched_own_transformer_001` tables,
  to be pinned only in the future authorized integration phase.
- `--validate-complete`: **21/21 COMPLETE**.
- v1.21.0 final manifest and MANIFEST.sha256: byte-identical (hashes in §A).
- v1.21.0 raw outputs and published tables: unchanged (T11 green).
- Working tree: clean except the two known personal untracked files.
- Processes: none running; execution was fully synchronous.

## L. Recommendation

**AUTHORIZE FINAL MANUSCRIPT UPDATE**

The control answered the registered question cleanly under the frozen
rules; there is no technical blocker. Per the absolute stop rule, no
manuscript, metadata, release, merge, tag, DOI or further experiment will
be touched without explicit human authorization.
