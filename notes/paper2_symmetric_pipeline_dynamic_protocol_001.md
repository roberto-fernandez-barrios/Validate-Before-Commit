# Paper 2 — Symmetric-pipeline dynamic replication protocol (v001, FROZEN)

Status: **FROZEN before any confirmatory seed is executed.**
Baseline: tag `v1.20.2`, sealing commit `3b00cc406ed22e7e8fbbdd0f4f517f2d0353888c`,
source commit `031f86f3eb094f9569f3e5f0b3c420954ef9a9bb`,
version DOI `10.5281/zenodo.21481392`.
Scope of this document: the registered protocol for the symmetric-pipeline
replication of the Q1 harmful-update / validate-before-commit result. The
preparation phase that freezes this document implements and validates the
harness but executes NO confirmatory seed and produces NO claim-bearing result.

---

## 1.1 Primary question

> Does Validate Before Commit retain material value when incumbent and
> challenger are self-contained predictive pipelines, each evaluated on the
> same raw stream and each using the preprocessing components with which it
> was trained?

The published v1.20.2 result was obtained under a frozen-initial-transformer
update policy: one scaler+PCA fitted on the initial training set serves every
model for the whole trajectory, and a commit replaces only the classifier.
The principal external objection is that the harmful-update effect could be an
artifact of that representation asymmetry (challengers trained inside a
representation fitted on pre-drift data). This protocol isolates exactly one
scientific intervention — preprocessing **ownership** — while holding the raw
stream, candidate batches, probes, gates, detector, and temporal semantics
fixed.

## 1.2 Transformer policies

### P0 — `frozen_initial_transformer`

Exact semantics (must reproduce v1.20.2 bit-for-bit):

- scaler and PCA are fitted ONCE on the initial training set;
- they remain frozen for the whole trajectory;
- the incumbent and every challenger use those same objects;
- a commit replaces the classifier but keeps the initial transformer;
- the ambiguous name `frozen_incumbent_transformer` is NOT used anywhere.

### P1 — `own_transformer_per_model`

- each challenger fits its own scaler exclusively on its own
  candidate-training batch (raw), and its own PCA exclusively on the scaler
  output of that same batch;
- the probe participates in NO fit;
- future windows participate in NO fit;
- the incumbent keeps the scaler, PCA and classifier it was trained with;
- a commit deploys the COMPLETE bundle (scaler + PCA + classifier
  [+ probabilistic calibrator when present] + metadata);
- the raw candidate batch is exactly the same as under P0 (same rows, same
  order, same hash);
- PCA dimension, solver, random_state and classifier type/hyperparameters are
  identical to P0;
- the ONLY scientific intervention is preprocessing ownership.

### P2 — `independent_neutral_transformer`

NOT part of the primary phase. Registered only as a conditional future
sensitivity, to be considered ONLY if P0-vs-P1 leaves the interpretation
ambiguous. No implementation commitment is made here.

### Detector representation (held fixed)

The drift monitor keeps its v1.20.2 representation (initial scaler+PCA) under
BOTH policies (`detector_transform_policy = frozen_initial`). Changing the
predictive pipeline must not simultaneously change the drift-monitoring
representation; that would confound candidate-construction policy with
monitoring policy.

## 1.3 Confirmatory matrix (RESERVED — next phase, NOT executed now)

Primary scenarios:

- **Full drift**: CICIDS2017 PortScan; UNSW-NB15 Reconnaissance; ToN-IoT
  Scanning.
- **Zero drift**: same three datasets, `--max-severity 0`,
  `--trigger-mode random --trigger-prob 0.05` (the v1.20.2 zero-drift design).

Mild drift is OUTSIDE the primary matrix; it may be opened only if full and
zero jointly cannot distinguish persistence / attenuation / elimination.

Adaptation policies:

- never-adapt (the shared no-adaptation baseline; run once per scenario and
  seed, since it does not depend on transformer policy);
- naive always-deploy (`--adaptation-gate none`);
- point gate (`--adaptation-gate labeled_probe --probe-size 32`);
- strict reject-ties gate (`--adaptation-gate labeled_probe --probe-size 32
  --gate-margin 0.001`).

Transformer policies: `frozen_initial_transformer`, `own_transformer_per_model`.

Detector: **KS-max** (primary). QK-ZZ is outside the primary phase and may
only be authorized after the KS-max result is known.

Expected confirmatory arm count:
6 scenarios × (1 never-adapt + 3 policies × 2 transformer policies) =
**42 arms**, each over the 30 confirmatory seeds.

### Confirmatory seeds

The seed ledger (`results/final_experiment_ledger.csv`), configs, source,
notes and tests were audited on 2026-07-22. Consumed windows: 104-133,
501-530, 601-630, 701-730, 801-830, 2001-2100 (plus runner default 101). The
proposed block collides with nothing, so it is FROZEN as:

- **Confirmatory seeds: 3001-3030** (30 seeds).
- **Smoke seeds: 4242, 4243** (SMOKE_ONLY, never aggregated, never analyzed).
- Frozen-parity checks reuse HISTORICAL seeds (501-530) exclusively to verify
  bit-identity against published v1.20.2 outputs — never as new evidence.

None of the 3001-3030 seeds is executed in the preparation phase. The driver
enforces this (see firewall, Bloque 4 T12).

## 1.4 Primary estimands

All estimands are per-seed paired differences of trajectory-mean balanced
accuracy (windows 0..99), aggregated over the 30 confirmatory seeds, in BA
percentage points. `BA_never` is the shared never-adapt baseline of the same
seed and scenario.

1. **Existence of harm under own-transformer**
   `Δ_naive,own = BA_naive,own − BA_never`
2. **Effect of transformer policy on the harm** (the estimand that answers
   the objection directly)
   `Δ_transformer = (BA_naive,own − BA_never) − (BA_naive,frozen − BA_never)
                  = BA_naive,own − BA_naive,frozen`
   (equivalent because the never-adapt baseline is common and paired).
3. **Value of the point gate under own-transformer**
   `Δ_point−naive,own = BA_point,own − BA_naive,own`
4. **Value of the strict gate under own-transformer**
   `Δ_strict−naive,own = BA_strict,own − BA_naive,own`

Secondary interactions (NOT the principal estimand, reported descriptively
with CIs):
`(point − naive)_own − (point − naive)_frozen`, and the strict equivalent.

## 1.5 Metrics

Primary: balanced accuracy (trajectory mean over served windows).

Mandatory safety metrics: attack recall; false-positive rate.

Secondary: attack-class F1; triggers; candidates trained; commits; rejects;
candidate labels; probe labels; harmful commits at horizons 1/3/5/10
(resolution log); censoring; candidate-minus-incumbent future value.

Explicitly NOT added in this phase: CVaR, new utility functions,
multi-constraint gates, new composite metrics, new hypotheses.

## 1.6 Statistical families (FROZEN before any run)

All families use per-seed paired contrasts and **Holm FWER** correction
within family, with the same deterministic paired-bootstrap machinery as
v1.20.2 (`make_paper2_q1_multiplicity` conventions).

- **F1 — harm under own-transformer, full drift** (3 contrasts):
  own-naive vs never-adapt, one per regime (PortScan, UNSW-Recon,
  ToN-Scanning). Holm.
- **F2 — transformer interaction on naive, full drift** (3 contrasts):
  own-naive vs frozen-naive, one per regime, on paired raw streams. Holm.
- **F3 — gate value under own-transformer, full drift** (6 contrasts):
  own-point vs own-naive and own-strict vs own-naive, in the three regimes.
  Holm.
- **F4 — zero-drift registered secondary family** (12 contrasts):
  own-naive vs never (3 datasets); own-point vs own-naive (3); own-strict vs
  own-naive (3); own-naive vs frozen-naive (3). Holm.

No cell may be added or removed after seeing results.

## 1.7 Equivalence and non-inferiority margins (PROPOSED — require human approval)

Scale anchors from published v1.20.2 evidence (results/tables/paper2_final_q1):
confirmed gate-vs-naive effects range 1.4-3.6 BA pp (ToN-Scanning KS 2.43
[1.53, 3.43]; QK 3.63 [1.66, 6.38]); the naive full-drift harm on ToN is
≈ −2.0 BA pp [−4.0, −0.14]; frontier anchor gains on PortScan are ≈ +7 BA pp.
The smallest CI half-width among confirmatory core contrasts is ≈ 0.17 pp
(UNSW), the largest ≈ 2.4 pp.

- **Primary BA equivalence margin: ±0.5 BA points.** Rationale: (i) it is
  4-14× smaller than every confirmed material effect in v1.20.2 (2.0-7.2 pp
  harms/gains), so an effect inside ±0.5 pp cannot support the paper's
  materiality language; (ii) it exceeds the seed-level Monte-Carlo noise of
  the 30-seed design on the tight regimes (UNSW CI half-width ≈ 0.2 pp), so
  equivalence is decidable; (iii) 0.5 pp of balanced accuracy on a 128-flow
  window is < 1 flow per window — operationally negligible for an IDS
  operator.
  Sensitivities: **±0.2** (stricter; near the resolution limit of the tight
  regimes) and **±1.0** (laxer; half the smallest confirmed material harm).
- **Attack-recall non-inferiority margin: 1.0 recall point** (own arm may not
  lose more than 1.0 pp attack recall vs its comparator). Rationale: missed
  attacks are the costly error class in IDS practice; 1 pp of recall at
  64 attack flows/window is < 1 missed attack per window, below operational
  noise, while the published harmful regimes move recall by several points.
  Sensitivities: 0.5 and 2.0 pp.
- **FPR non-inferiority margin: 0.5 FPR points.** Rationale: FPR drives
  analyst workload; at 64 benign flows/window, 0.5 pp is < 1 false alert per
  ~3 windows, consistent with common SOC alert-budget practice of rejecting
  changes that add ≥1 alert/window; the harmful regimes in v1.20.2 move FPR
  by multiple points. Sensitivities: 0.2 and 1.0 pp.

These margins are frozen HERE, before any confirmatory execution, and may not
be modified after observing results. **Execution of the confirmatory seeds
requires explicit human approval of these margins first.**

## 1.8 Interpretation matrix (FROZEN)

- **A — persistence**: naive remains materially below never in at least one
  critical cell with own-transformer; point or strict beats naive; harmful
  proposals continue to exist.
  → "Preprocessing asymmetry amplified the problem, but candidate governance
  remains materially useful with self-contained pipelines."
- **B — attenuation**: mean harm approaches zero, but bad proposals, regret
  or point/strict advantage persist; or the transformer interaction explains
  a substantial part without explaining everything.
  → "Preprocessing ownership is a major amplifier, while candidate promotion
  still carries residual decision risk."
- **C — elimination**: naive-own is equivalent to never; point and strict are
  equivalent to naive; material harm disappears; the degradation-value
  relation stops being operationally relevant.
  → "The principal harmful-update effect was driven by representation
  incompatibility under the frozen-initial-transformer update policy."

This matrix may not be modified after results.

## 1.9 Stopping rule for the preparation phase

The preparation phase does NOT execute this protocol. It ends when:

1. this protocol is complete and committed;
2. `configs/symmetric_pipeline_dynamic_v1.json` is defined;
3. the 3001-3030 block is reserved and firewalled;
4. families and estimands are frozen (this document);
5. the implementation (raw stream, ModelPipeline, DetectorPipeline, candidate
   builder, complete-bundle commit) is in place;
6. frozen-mode parity with v1.20.2 is demonstrated (bit-identical, or
   numerically equal at an explicitly justified machine-level tolerance);
7. all invariant tests are green.

The confirmatory matrix may only start after human review of: this protocol,
the margins in 1.7, the frozen parity evidence, the own-transformer
architecture, the leakage/symmetry tests, and the expected compute cost.
