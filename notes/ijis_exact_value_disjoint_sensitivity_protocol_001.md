# FROZEN PROTOCOL - Final IJIS exact-feature-value-disjoint sensitivity

Status at freeze: **PRE-IMPLEMENTATION, PRE-SMOKE, PRE-CONFIRMATORY.** The exact-X
overlap forensic audit has been run, because it motivates this protocol, but no result
from the sensitivity defined here exists. No outcome is preferred. This is the final
authorized scientific reopening: after the registered B2 and B1 blocks there is no
follow-up or rescue experiment.

Baseline of record: `5bb5c5336448e941d1bb7aba6b1793fe4b18cac8`.
Historical release v1.23.0 and its 207 sealed CSVs remain immutable.

Configs:

- `configs/ijis_exact_value_disjoint_b2_v1.json`
- `configs/ijis_exact_value_disjoint_b1_v1.json`

Companion forensic evidence:

- `audits/exact_feature_overlap_audit.md`
- `audits/exact_feature_overlap_summary.csv`

## 1. Registered question and scope

**Question.** Do the central post-KBS conclusions survive when window, train and probe
roles are disjoint not only by source-row identity but also by exact cleaned raw feature
vector?

Primary claims under test:

1. **B2:** the effect of nominal candidate evidence, 2,000/class versus 512/class, under
   pool-constructed progressive drift between empirical regime pools.
2. **B1:** the registered common-harness interpretation among the complete frozen policy
   set, at 2,000/class primary and 512/class secondary where originally meaningful.

This is an exact-duplicate exposure sensitivity. It is not a global deduplication, an
approximate-neighbour study, a new deployment experiment or causal proof of the effect of
duplicates. The group split changes the empirical role samples; numeric equality with the
historical blocks is neither expected nor required.

## 2. Exact feature identity

Use the exact cleaned raw representation consumed by the experiment before any scaler or
PCA:

1. common columns sorted exactly as in the runner;
2. numeric coercion with errors to NaN;
3. `+/-inf -> NaN -> 0.0`;
4. contiguous little-endian float64;
5. canonicalize only `-0.0` to `+0.0`;
6. no rounding and no approximate matching.

The deterministic group key is SHA-256 of the full canonical float64 byte vector. Hash
matches must be checked against actual canonical vector equality. Any collision between
different vectors is an objective blocker.

The key contains features only. It must not include label, ref/current membership,
benign/attack membership or source-row identity.

## 3. Feature-group-disjoint role assignment

Do **not** delete duplicate rows. Every source row and its original label is retained.
All rows sharing one exact X key form one indivisible group and must be assigned to one
and only one of `window`, `train`, `probe`. Consequently:

```
X(window) intersect X(train) = empty
X(window) intersect X(probe) = empty
X(train)  intersect X(probe) = empty
```

Within-role multiplicity remains unchanged. Sampling with replacement remains unchanged.
Contradictory-label groups are kept intact, with all original labels, in one role; no row
is deleted, relabelled or majority-voted.

### 3.1 Frozen deterministic assignment algorithm

For every dataset and seed:

1. Build every exact-X group and its four-dimensional row-count vector
   `c_g = (ref benign, ref attack, current benign, current attack)`.
2. Let `N_s` be total rows in stratum `s` and targets
   `T[r,s] = f[r] * N_s`, with `f = (0.50, 0.30, 0.20)` for
   `(window, train, probe)`.
3. Order groups by:
   - descending `max_s(c_g[s] / N_s)`;
   - descending total group multiplicity;
   - ascending SHA-256 of `seed || group_feature_sha256`.
4. Starting from zero assigned counts, place each complete group into the role that
   minimizes, after the tentative placement,

   `J = max_{r,s} abs(A[r,s]-T[r,s])/N_s
        + sum_{r,s} ((A[r,s]-T[r,s])/N_s)^2`.

   Exact objective ties are resolved by ascending SHA-256 of
   `seed || group_feature_sha256 || role_name`.
5. No performance result, model output, trigger time or policy action enters grouping,
   ordering or assignment.

Required postconditions, checked before model construction:

- each source row assigned exactly once;
- each X group assigned to exactly one role;
- zero exact-X cross-role intersection;
- row multiplicity and labels preserved;
- all four strata non-empty in every role;
- absolute deviation from each registered stratum-role target <= 0.50 percentage points.

Failure of any postcondition for any registered seed is a blocker. Sample sizes, role
fractions and group semantics must not be changed after seeing a failure.

## 4. Historical-path preservation

The existing row-index splitter is not altered. Add a new explicit flag/mode only:
`feature_group_disjoint_roles=true`. With the flag false or absent, historical streams,
candidate draws, RNG consumption and output bytes must remain bit-identical.

With the flag true, the role assignment is the only intended intervention. All subsequent
samplers, with-replacement multiplicity, stream construction, proposal-time severity,
model pipeline and serving semantics remain the frozen implementation.

## 5. Fresh seed firewall

Repository-wide `run_config` and ledger scan at freeze found no use of these blocks:

- **B2 confirmatory:** 7001-7030; smoke 7401-7402.
- **B1 confirmatory:** 8001-8030; smoke 8401-8402.

Smoke seeds are never inferential. Confirmatory seeds may run only after protocol,
configs, preflight, implementation, tests, smoke and analysis code are committed.

## 6. B2 design

Repeat the complete registered B2 matrix:

- scenarios: PortScan-full, UNSW-Recon-full, ToN-IoT-full;
- 100 windows, 0->1 mixture over the first 80;
- arms per scenario: never plus `{naive, point, strict}` x `{512, 2000}`/class;
- 21 arms total;
- own-transformer candidate pipeline, SVC-RBF, scaler + PCA-8;
- initial model 2,000/class; candidate probe 32; KS-max; identical triggers,
  hyperparameters, cooldown and t+1 serving semantics;
- nested proposal draw: B512 followed by E1488 from the same per-trigger RNG and the same
  proposal-time mixture; B2000 = concat(B512,E1488).

Naive cross-size proposals remain exactly coupled. Gated cross-size contrasts are paired
at seed level only after their decision histories diverge.

### 6.1 B2 estimands and multiplicity

Inferential unit: seed, n=30. Reuse the frozen deterministic centered paired bootstrap
(100,000 resamples; label-derived deterministic seed), CI95 for signed effects, CI90 for
the +/-0.5-pp materiality margin, Holm separately within each family, paired t and
Wilcoxon as sensitivities. Recall/FPR guardrails retain the frozen -1.0/+0.5-pp margins.

- G1, six contrasts, Holm: `naive_512-never`, `naive_2000-never` per scenario.
- G2, three contrasts, Holm: `naive_2000-naive_512` per scenario, primary.
- G3, six contrasts, Holm: `point_2000-naive_2000`,
  `strict_2000-naive_2000` per scenario.
- G4, six contrasts, Holm: `(gate-naive)@2000-(gate-naive)@512` for point/strict.
- G5, three independent-block robustness contrasts, Holm:
  `G2_value_disjoint-G2_historical`, using independent-seed bootstrap inference. G5
  diagnoses attenuation/amplification across role-assignment designs; it must not be
  described as a causal estimate of duplicate leakage alone.

Future-value/sign-rate summaries remain descriptive and enter no outcome rule.

### 6.2 B2 outcome rules

Per scenario, classify G2 exactly as before:

- **SIZE BENEFIT:** Holm p<0.05 and effect >= +0.5 pp.
- **SIZE COST:** Holm p<0.05 and effect <= -0.5 pp.
- **NO MATERIAL SIZE EFFECT:** CI90 strictly inside (-0.5,+0.5) pp.
- **RESOLVED SUB-MATERIAL:** Holm p<0.05 but neither material threshold reached.
- **UNRESOLVED:** otherwise.

Apply the following ordered, mutually exclusive program rule:

1. **ROBUST HOMOGENEOUS SIZE BENEFIT:** all three scenarios are SIZE BENEFIT.
2. **PARTIAL ROBUSTNESS:** at least two are SIZE BENEFIT and none is SIZE COST.
3. **NO MATERIAL SIZE EFFECT:** all three are NO MATERIAL SIZE EFFECT.
4. **SIZE COST:** at least two are SIZE COST and none is SIZE BENEFIT.
5. **HETEROGENEOUS:** every other pattern.

For each G5 cell classify MATERIAL ATTENUATION / MATERIAL AMPLIFICATION using Holm p<0.05
and effects <=-0.5 / >=+0.5 pp; COMPATIBLE if CI90 lies inside +/-0.5; otherwise
UNRESOLVED. "Original B2 materially inflated" is permitted only if at least two scenarios
show MATERIAL ATTENUATION and none MATERIAL AMPLIFICATION. Otherwise report the exact
cell pattern and do not infer causal bias.

## 7. B1 design

Repeat the complete amended B1 matrix under feature-group-disjoint roles:

- six scenarios: zero/full pool-constructed drift x three benchmarks;
- primary 2,000/class policies: never, naive, point, strict, ATC, DoC, calibrated
  ensemble, replay, river-DDM, river-ADWIN;
- secondary 512/class policies: naive, point, strict, ATC, DoC, calibrated ensemble;
- DDM/ADWIN and replay are not duplicated at 512, preserving the frozen amendment;
- 96 arms, exact original information budgets and registered reference parameters;
- no tuning and no method added or removed.

Reuse PF1 (18), PF2 (18), PF3 (12), SF4 (18) and SF5 (30), their Holm families,
materiality/compatibility margins, primary comparisons and S4 ordering-change rule
verbatim from the B1 amendment.

### 7.1 B1 robustness classification

First regenerate the original per-cell categories and S1-S4 statements mechanically.
Define these six headline predicates from the new results:

1. `ATC_RETENTION`: ATC has no MATERIAL COST versus naive in full drift and at least two
   of three full-drift cells are COMPATIBLE or MATERIAL GAIN.
2. `ENSEMBLE_RETENTION`: ensemble has no MATERIAL COST versus naive in full drift and all
   three full-drift cells are COMPATIBLE or MATERIAL GAIN.
3. `COST_ALTERNATIVES`: each of DoC, replay, DDM and ADWIN has at least one MATERIAL COST
   versus naive in full drift.
4. `ATC_VS_POINT`: at least five of six ATC-versus-point cells are COMPATIBLE or MATERIAL
   GAIN and none is MATERIAL COST.
5. `SIZE_DEPENDENT_ORDERING`: the frozen S4 rule fires for ATC or ensemble in at least one
   scenario.
6. `NO_GLOBAL_DOMINANCE`: no evaluated adaptive policy is MATERIAL GAIN versus naive in
   every one of the six scenarios.

No primary cell may reverse directly from historical MATERIAL GAIN to new MATERIAL COST,
or historical MATERIAL COST to new MATERIAL GAIN.

Ordered classification:

- **POLICY CONCLUSIONS ROBUST:** all six predicates hold and there is no direct material
  reversal.
- **PARTIALLY ROBUST:** no direct material reversal and at least four predicates hold.
- **MATERIALLY CHANGED:** direct material reversal, or fewer than four predicates hold.

Exact numeric replication is not required. Every cell is reported regardless of the
aggregate robustness label.

## 8. Implementation gates and smoke-only tests

Before confirmatory execution require:

1. historical flag-off path bit-identical;
2. zero exact-X cross-role overlap;
3. every row assigned once;
4. multiplicity preserved;
5. contradictory-label X groups intact in one role;
6. deterministic assignment;
7. every target fraction within 0.50 pp;
8. non-empty required strata and successful maximum registered draws;
9. otherwise unchanged raw-stream semantics;
10. nested B512 exact prefix of B2000;
11. identical proposal-time severity across sizes;
12. own transformer fitted only on the selected candidate batch;
13. zero exact-X probe/evaluation cross-role exposure;
14. confirmatory seed firewall;
15. no result access in smoke/preflight paths.

Smoke may cover every new code path but must use only 7401-7402 and 8401-8402. Smoke
outputs live under `results/smoke`, are marked `SMOKE_ONLY_DO_NOT_ANALYZE`, and may not be
used to alter outcome rules.

## 9. Stop, recovery and decision rules

One pass over each complete confirmatory block. No interim analysis, extension, changed
parameter, substituted seed or post-result method removal.

If an implementation bug is discovered after a confirmatory block begins, stop before
analysis. Recovery is allowed only when all of the following hold: the bug violates an
explicit implementation invariant above; the correction restores the frozen semantics
without changing any scientific parameter; every partial output from the affected block
is quarantined and excluded; the defect, files affected and correction are committed
before one complete restart of the same seeds/config. No other recovery is authorized.

After both blocks return exactly one scientific decision:

- **ROBUSTNESS CONFIRMED:** B2 = ROBUST HOMOGENEOUS SIZE BENEFIT and B1 = POLICY
  CONCLUSIONS ROBUST, with no current headline falsified.
- **THESIS REQUIRES REVISION:** a narrower publishable thesis survives without rescue
  science.
- **SCIENTIFIC BLOCKER:** no honest publishable central thesis remains, or an objective
  design/integrity invariant fails.

No further experiment is authorized under any decision.

