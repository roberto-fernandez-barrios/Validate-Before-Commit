# Registered protocol — Size-matched self-contained challenger control (001)

Status: FROZEN. This file must be committed before any confirmatory seed is
executed. After the confirmatory run starts, nothing in this protocol may
change.

Branch: `feature/size-matched-own-transformer`
Baseline: tag `v1.21.0`, commit `7f9ea405f6bd30e457f714c1a5ebc6b463e74c50`
(scientific commit `588c89e90b823813043a559e7ebd307cf57baf2a`).
Baseline checkpoint: `notes/size_matched_own_transformer_baseline_checkpoint.md`.

## 1.1 Primary question

> Does harmful candidate promotion under zero drift persist when
> self-contained challengers are trained with the same per-class sample size
> as the initial incumbent?

This is the single residual objection this closed extension addresses. The
v1.21.0 zero-drift arms train challengers on 512 samples per class while the
initial incumbent was trained on 2000 per class; the observed harm could in
principle be (a) mostly a small-challenger artifact, (b) amplified but not
explained by size, or (c) a size-robust re-estimation/promotion risk. The
design below distinguishes the three.

## 1.2 Scope

### Datasets / scenarios (zero drift only)

Exactly the v1.21.0 zero-drift scenario definitions (no re-derivation):

| scenario | data | zero-drift definition |
|---|---|---|
| `ps_zero` | CICIDS2017 PortScan source/reference | `--trigger-mode random --trigger-prob 0.05 --max-severity 0` |
| `unsw_zero` | UNSW-NB15 Reconnaissance | same |
| `ton_zero` | ToN-IoT Scanning | same |

All other stream parameters are byte-for-byte the v1.21.0 fixed flags
(`configs/symmetric_pipeline_dynamic_v1.json` `fixed_flags`): window 128,
post-windows 100, ramp-windows 80, calibration 30, cooldown 10, dim 8,
svc_rbf, `adapt-strategy full_replace`, probe/recal source pools,
stream prevalence 0.5, lifetime-max-proposals 10, candidate latency 0,
probe latency 0, `sevmax = 0` (severity identically zero in every window).

### Transformer policy

Exclusively `own_transformer_per_model`: each challenger fits its own
StandardScaler + PCA(dim=8) on its candidate batch only, then SVC-RBF; the
incumbent keeps the bundle it was trained with; a commit replaces scaler,
PCA, classifier and metadata as one bundle, serving from t+1
(`src/experiments/symmetric_pipeline.py::build_candidate_pipeline`,
unchanged).

`never-adapt` is transformer-policy independent and runs once per
scenario/seed.

### Candidate sizes (the ONLY new experimental variable)

`candidate_size_per_class ∈ {512, 2000}`. The initial incumbent keeps
`--train-size-per-class 2000`. Nothing else changes: same trigger, same
probe, same gates, same hyperparameters, same temporal semantics, same
evaluation, same statistical machinery.

### Policies

`never-adapt`, `naive` (gate none), `point` (labeled_probe, probe 32,
margin 0.0), `strict` (labeled_probe, probe 32, margin 0.001) — identical
flag sets to v1.21.0.

## 1.3 Arm matrix (21 arms, frozen)

Per scenario: `never`, `naive_512`, `point_512`, `strict_512`, `naive_2000`,
`point_2000`, `strict_2000`.

Tags: `sm_{scenario}_never` and `sm_{scenario}_{policy}_{size}`, e.g.
`sm_ps_zero_naive_2000`. 3 scenarios × 7 arms = **21 arms × 30 seeds**.
No cell may be added or removed after the run.

## 1.4 Seeds

- **Confirmatory block: 4001–4030** (30 seeds, contiguous). Verified virgin
  on 2026-07-22 by a structured offline scan over
  5470 CSVs (every `seed`-like column) and 286 JSONs (every `seed`-like key)
  under `results/`, `configs/`, `notes/`, `src/`, `tests/`, `docs/`,
  `paper/`, plus regex extraction of literal seed ranges in all `.py/.md/
  .txt/.json`: zero collisions with 4001–4030; the only seeds ever used in
  [4000, 5000) are 4242–4243 (previous phase's smoke seeds). The block also
  does not intersect any historical block (104–133, 501–530, 601–630,
  701–730, 801–830, 2001–2100, 3001–3030). These seeds are RESERVED and
  firewalled: never in smoke, parity, dry-run or development mode.
- **Smoke seeds: 4401–4402** (same scan: zero hits). Smoke outputs are
  `SMOKE_ONLY_DO_NOT_ANALYZE` and never aggregated.
- **Parity reference seeds: 4242–4243** — used ONLY to compare the new
  512-path bit-for-bit against the stored v1.21.0-code smoke outputs of
  `sp_ton_zero_naive_own` (`results/smoke/symmetric_pipeline/`); never new
  evidence.
- Unit tests use small ad-hoc seeds (< 100) and synthetic pools, never the
  confirmatory block (enforced by the driver firewall, test T9).

## 2. Semantics of the size change

### 2.1 Single intervention

The only new experimental variable is `candidate_size_per_class`. Explicitly
NOT changed: transformer type/config, PCA dim (8) and solver, SVC C (fixed
1.0 in the `full_replace` path — the `cn` C-scaling belongs exclusively to
the `cumulative` strategy and is NOT active here), SVC gamma (configured
`'scale'` in both conditions), trigger, probe size, gate margins, stream,
calibration, cooldown, duration, environment RNG.

Inevitable mathematical effects of the estimators themselves (fitted scaler
mean/scale, PCA components/explained variance, libsvm's effective gamma
under `gamma='scale'`, support vectors) follow from the batch and are
RECORDED per candidate, not controlled. `sklearn` receives identical
constructor arguments in both conditions; the candidate training seed stays
`seed + t + 1` (size-independent, unchanged from v1.21.0).

### 2.2 Nested candidate batches (canonical draw)

Frozen mechanism, chosen so that BOTH (i) the 512 condition is bit-identical
to the v1.21.0 own-transformer zero-drift arms and (ii) `batch_512 ⊂
batch_2000` exactly:

- v1.21.0 semantics (unchanged): at trigger window `t`,
  `cand_rng = np.random.default_rng(seed * 100_003 + t)` (fresh per
  proposal; `cand_rng` is not consumed after the candidate draw in the
  `full_replace` path), then
  `sample_balanced_from_distribution(train_pools, n_per_class=512,
  severity=0.0, rng=cand_rng)` → the historical batch **B512**
  (512/class, with replacement, benign block then attack block, then a
  single permutation of the 1024 rows).
- Canonical extension (new, only when `--candidate-size-per-class` is set):
  continuing from the SAME `cand_rng` stream, draw
  `sample_balanced_from_distribution(train_pools, n_per_class=1488,
  severity=0.0, rng=cand_rng)` → extension **E1488** (1488/class, same
  sampler function, same pools, same with-replacement policy, own internal
  permutation).
- **batch_2000 = concat(B512, E1488)** (rows and labels, in that order).
- The 512 condition trains on exactly **B512**; the 2000 condition trains on
  exactly **batch_2000**. Both conditions execute the identical draw code
  (the full canonical draw), guaranteeing per-proposal nesting regardless of
  trajectory.

Consequences (machine-checked, tests T1/T2):
- rows 0–1023 of `batch_2000` ARE `B512`: same rows, same labels, same
  order, same row hash — the first 512 samples per class of `batch_2000`
  are precisely the 512-condition batch;
- the extra 1488 samples per class are the ONLY additional information in
  the 2000 condition;
- there are NOT two independent draws for 512 and 2000;
- `B512` is bit-identical to what the v1.21.0 code produces at
  `--adapt-size-per-class 512` for the same (seed, t) — the 512 arms of
  this control replicate v1.21.0 candidate construction exactly.

The mechanism is only defined at severity 0 (this experiment's entire
scope); the implementation asserts `severity == 0.0` and
`adapt_strategy == "full_replace"` whenever the size flag is active, and
aborts otherwise. If any assertion fires during smoke/preflight, the run
stops and the problem is documented (per the no-nesting-no-run rule).

### 2.3 Sampling policy

Identical to v1.21.0: same per-seed role-disjoint pools (`train_pools`),
sampling with replacement via `sample_rows` (`rng.integers`), balanced
per-class, same counterfactual generator, severity fixed at zero. This
experiment is NOT presented as observed-data or operational.

### 2.4 Per-candidate registration (provenance)

For every candidate trained in every size-matched arm, the driver records to
`candidate_provenance.jsonl` (one JSON object per candidate):
candidate size per class; full training-batch row hash; row hash of the
initial 512-per-class subset (`rows_hash(X[:1024], y[:1024])`); scaler
`mean_`/`scale_` hashes; PCA components hash; explained-variance hash;
configured gamma (`'scale'`); fitted effective gamma (`svc._gamma`);
classifier parameters; creation window; training seed; deployed model
version (from the serving log). This reuses
`symmetric_pipeline.preprocessing_provenance` (already published machinery).

No hyperparameter is adjusted as a function of size. The only automatic
n-dependent regularization in the codebase (`cumulative`-mode `cn` scaling
of SVC C, amendment 012) is NOT on this code path; its non-involvement is
frozen here before the run and asserted by test T6.

## 3. Estimands (percentage points of balanced accuracy, per dataset)

- **E1 — size-matched damage:** Δ2000 = BA(naive_2000) − BA(never).
- **E2 — candidate-size effect on naive:** Δsize = BA(naive_2000) − BA(naive_512).
- **E3 — point gate at matched size:** Δpoint,2000 = BA(point_2000) − BA(naive_2000).
- **E4 — strict gate at matched size:** Δstrict,2000 = BA(strict_2000) − BA(naive_2000).
- **E5 (secondary) — gate × size interaction:**
  [BA(point_2000) − BA(naive_2000)] − [BA(point_512) − BA(naive_512)], and
  the strict analogue. E5 never substitutes for the primary estimands.

Descriptive (uncorrected, labelled `desc|`): naive_512 − never, and any
other cell needed for the checkpoint's narrative tables.

## 4. Metrics and margins (reused from v1.21.0, no new metrics)

- Primary: balanced accuracy (per-seed trajectory mean over evaluated
  windows, identical computation to v1.21.0).
- Guardrails: attack recall, false-positive rate.
- Frozen margins: BA equivalence ±0.5 pp primary (sensitivities ±0.2, ±1.0);
  equivalence declared when the full CI90 lies inside the margin.
  Attack-recall non-inferiority −1.0 pp primary (sens. −0.5, −2.0).
  FPR non-inferiority +0.5 pp primary (sens. +0.25, +1.0).
- Secondary descriptive: attack F1, triggers, candidates trained, commits,
  rejects, candidate labels, probe labels, future value H1/H3/H5/H10,
  censoring, harmful committed proposals, mean future loss, model versions.
- NOT introduced: CVaR, economic utility, alert-cost models, new composite
  metrics.

## 5. Statistical families (frozen)

Inferential unit: the seed (30 paired trajectories per contrast; windows,
triggers, commits are never independent units). Machinery: the published
deterministic centered paired bootstrap (100 000 resamples, per-contrast
label seeding), Holm within family, paired t-test and Wilcoxon as
sensitivities, CI95 for superiority/harm, CI90 for equivalence — imported
from `src.analysis.make_paper2_q1_multiplicity` /
`make_symmetric_pipeline_dynamic_001` (reused, not reimplemented).

- **F1 — size-matched damage** (3 contrasts, Holm FWER):
  naive_2000 vs never, one per dataset.
- **F2 — candidate-size effect** (3 contrasts, Holm FWER):
  naive_2000 vs naive_512, one per dataset.
- **F3 — gate value at size 2000** (6 contrasts, Holm FWER):
  point_2000 vs naive_2000 and strict_2000 vs naive_2000, per dataset.
- **F4 — gate × size interaction, secondary** (6 contrasts, Holm FWER):
  (point − naive)_2000 − (point − naive)_512 and the strict analogue, per
  dataset. Interaction differences are computed per seed (paired at the
  seed level) before bootstrapping.

No cells are added or removed after the run.

## 6. Machine-evaluable outcome rules (frozen verbatim)

### Outcome P — PERSISTENCE (size-robust)

Classify as PERSISTENCE iff ALL of:
1. at least one dataset satisfies naive_2000 − never ≤ −0.5 pp with CI95
   entirely below zero and the F1 contrast Holm-significant;
2. point_2000 or strict_2000 improves on naive_2000 by ≥ +0.5 pp in at
   least one cell with the F3 contrast Holm-significant;
3. the conclusion can rest on at least one cell that passes the
   recall/FPR guardrails (primary NI margins).

Allowed interpretation: "Candidate-size asymmetry amplifies the effect, but
harmful promotion persists even for self-contained challengers trained with
the same per-class sample size as the incumbent."

### Outcome E — ELIMINATION (by size)

Classify as ELIMINATION iff ALL of:
1. all three naive_2000 − never contrasts have CI90 entirely inside
   ±0.5 pp;
2. point_2000 and strict_2000 are equivalent to naive_2000 within ±0.5 pp
   (CI90 inside the margin) in all three datasets;
3. harmful future value shows no material reduction pattern that
   contradicts that equivalence.

Allowed interpretation: "The residual zero-drift harm was primarily
attributable to promoting challengers trained with substantially less data
than the incumbent."

### Outcome A — ATTENUATION / mixed

Any result that does not fully satisfy P or E. Includes: reduced but not
equivalent harm; persistence in one dataset without a clean gate win; useful
gates with vanished mean harm; a large but not fully explanatory size
effect; heterogeneous datasets.

Allowed interpretation: "Candidate size is an important amplifier, while the
remaining promotion risk is dataset- and policy-dependent."

These rules may not be modified after the confirmatory seeds run.

## 7. Implementation plan (minimal, no science duplication)

- `configs/size_matched_own_transformer_v1.json`: registers source tag/
  commit, protocol commit, datasets, zero-drift config, sizes, policies,
  seeds, margins, families, expected_arms = 21, output paths.
- `src/experiments/run_paper2_readaptation_v2.py`: add
  `--candidate-size-per-class` (default None → byte-identical historical
  behavior). When set, the `full_replace` branch performs the §2.2 canonical
  nested draw (B512 + E1488) and trains on the prefix selected by the flag.
  No other line of the science module changes.
- `src/experiments/run_symmetric_pipeline_replication.py`: add `--config`
  (default: the historical config → all existing behavior unchanged) and a
  `size_matched` matrix builder for the 21-arm grid; per-candidate
  provenance capture (§2.4) via a recording wrapper around the environment's
  `candidate_factory`. Stream generation, ModelPipeline, DetectorPipeline,
  candidate builder, gates, temporal semantics, resolution logging and
  harmful-commit accounting are reused, not duplicated. The firewall reads
  the reserved block from the loaded config (4001–4030 here).
- Analysis: `src/analysis/make_size_matched_own_transformer_001.py`,
  importing the published bootstrap/Holm machinery.

## 8. Mandatory tests (T1–T11)

- **T1 Baseline 512 parity** — (a) with the flag at 512, in-process outputs
  are identical to the flag-absent historical path for the same seed/args;
  (b) the driver's 512-path reproduces the stored v1.21.0-code smoke outputs
  of `sp_ton_zero_naive_own` (seeds 4242–4243) bit-for-bit.
- **T2 Nested batches** — per (seed, proposal): batch_512 ==
  first_512_per_class(batch_2000), by content and by hash; provenance prefix
  hash of every 2000-candidate equals the 512-candidate's training hash at
  the same (seed, creation window) along equivalent trajectories.
- **T3 Same raw stream** — all 7 arms of a scenario share the raw-stream
  hash per seed.
- **T4 Same probes** — at the same trigger and equivalent trajectory, 512
  and 2000 receive the same raw probe (probe RNG keyed by (seed, t) only).
- **T5 No leakage** — scaler/PCA of both sizes fit on the candidate training
  batch only (n_samples_seen_ == 2×size; parameters recomputable from the
  batch).
- **T6 Same hyperparameters** — all configuration identical except candidate
  size and its inevitable estimator effects; svc_C == 1.0 in both; the
  `cn` scaling is not reachable in `full_replace`.
- **T7 Complete-bundle commit** — the 2000 bundle (scaler+PCA+classifier+
  metadata) deploys whole and serves from t+1.
- **T8 Determinism** — two identical executions produce identical hashes.
- **T9 Seed firewall** — the driver refuses 4001–4030 in smoke/parity/
  dry-run/development modes with the new config.
- **T10 Metrics** — BA, recall, FPR match an independent recomputation.
- **T11 Historical artifact unchanged** — running the suite leaves the
  v1.21.0 final manifest, MANIFEST.sha256, raw outputs and published tables
  byte-identical.

## 9. Smoke & preflight (before any confirmatory seed)

Smoke seeds 4401–4402 only; at most: `sm_ps_zero_naive_512`,
`sm_ps_zero_naive_2000`, and one strict-2000 arm if needed to validate the
gate. Outputs under `results/smoke/size_matched_own_transformer/` marked
`SMOKE_ONLY_DO_NOT_ANALYZE`; never aggregated or interpreted. Then: full
pytest, audit, manifest verification, `--list-arms`, `--dry-run`, preflight
note, and the freeze commit ("Freeze size-matched own-transformer control")
containing protocol + config + implementation + tests + preflight and ZERO
confirmatory results.

## 10. Confirmatory execution

Only after: protocol committed, tests green, nesting PASS, baseline parity
PASS, config frozen, preflight PASS. Then exactly 21/21 arms × 30/30 seeds
(4001–4030), synchronous, no background processes, zero parameter changes,
`--resume` only after technical interruption, no seed substitution, no arm
removal, no partial-result peeking to change the protocol. Output:
`results/raw/size_matched_own_transformer/`, each arm with completion
marker, resolved config, command, environment and hashes.
`--validate-complete` must report 21/21 COMPLETE before any analysis.

## 11. Analysis outputs

`results/tables/size_matched_own_transformer_001/`: by_seed.csv,
summary.csv, paired_contrasts.csv, multiplicity.csv, equivalence.csv,
security_metrics.csv, harmful_commit_summary.csv,
candidate_size_interaction.csv, run_completion.csv,
CLAIM_INTERPRETATION.json (outcome PERSISTENCE | ATTENUATION | ELIMINATION,
protocol commit, config sha256, confirmatory seeds, rules_passed,
primary_conclusion, allowed_claims, forbidden_claims,
follow_up_authorized=false). F1–F4 and the P/A/E rules apply literally; no
unregistered analyses. Harmful proposals are reported descriptively
(H1/H3/H5/H10, censoring, commit counts, per-seed clustering) with NO
binomial bound, population probability, or production-prevalence estimate.

## 12. Absolute stop rule

After the confirmatory checkpoint
(`notes/size_matched_own_transformer_confirmatory_checkpoint.md`): stop. No
manuscript/README/metadata changes, no v1.22.0, no merge/tag/release/DOI, no
mild/full drift, no observed-data, no VBC-SG, no QK-ZZ, no new datasets, no
additional factorials. The next phase is exclusively the human-authorized
integration of this result — whatever it is — and submission.
