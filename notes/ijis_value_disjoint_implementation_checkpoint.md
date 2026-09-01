# IJIS exact-value-disjoint implementation checkpoint

Date: 2026-09-01  
Frozen protocol commit: `f8a02d4fe4e7b96d81e1695e094a2e708cd1960b`  
Status: **PASS -- implementation and smoke gates satisfied; confirmatory blocks untouched**

## Implemented surface

- The historical `source_row` split remains the default and its algorithm is unchanged.
- The new explicit `--role-split-mode exact_feature_group` groups the cleaned raw float64
  feature vector only, canonicalizing signed zero and performing no rounding.
- SHA-256 matches are collision-checked by actual vector equality.
- Whole feature groups are assigned to exactly one of window/train/probe by the frozen,
  seeded greedy rule. Every source row, label and within-role multiplicity is retained.
- Each arm writes `role_assignment_audit.csv`; confirmatory analysis is frozen in
  `make_ijis_exact_value_disjoint_b2_001.py` and
  `make_ijis_exact_value_disjoint_b1_001.py` before confirmatory execution.

## Smoke-only execution

The registered smoke seeds were used exclusively: B2 `7401-7402`, B1 `8401-8402`.
Nine arms (three B2 and six B1) completed once, in 163.0 aggregate arm-seconds. Every
output contains `SMOKE_ONLY_DO_NOT_ANALYZE`; no smoke value enters an outcome rule.

Across the 18 arm-seed role audits:

- verdict PASS: 18/18;
- exact-X overlap groups window/train, window/probe and train/probe: 0 throughout;
- total input rows equal total output rows and multiplicity is preserved: 18/18;
- largest absolute role/stratum fraction deviation: 0.005721 percentage points
  (registered maximum 0.50 pp);
- UNSW contradictory-label groups: all 403 groups, involving 1,828 rows globally, were
  kept intact by X-only assignment;
- largest retained within-role source multiplicity exercised: 3,361 (ToN-IoT).

The paired PortScan naive smoke arms had identical raw-stream-hash files. Six shared
proposal pairs were checked: every B2000 nested-prefix row hash equalled the corresponding
B512 training-row hash, and proposal-time severity matched in all six.

The smoke matrix exercised candidate sizes 512 and 2,000; no-update, always-deploy,
strict, ATC, DoC, calibrated ensemble, replay, river-DDM and river-ADWIN paths; full and
zero drift; and all three datasets across the combined smoke set. Maximum registered
draws completed without stratum-capacity failure. Sampling-with-replacement semantics
were not changed.

## Required test gates

1. old mode bit-identical: PASS;
2. zero exact-X role overlap: PASS;
3. every row assigned exactly once: PASS;
4. multiplicity preserved: PASS;
5. contradictory-label groups intact: PASS;
6. deterministic and seed-dependent assignment: PASS;
7. role fractions within 0.50 pp: PASS;
8. required strata and maximum draws: PASS;
9. otherwise unchanged raw-stream semantics: PASS;
10. B512 exact nested prefix of B2000: PASS;
11. proposal-time severity shared across sizes: PASS;
12. own transformer fitted only on the candidate batch: PASS;
13. no probe/evaluation role leakage: PASS;
14. seed firewall: PASS;
15. no confirmatory-result access or peeking: PASS.

`python -m pytest -q` result before this checkpoint: **245 passed in 63.85 s**.

The local ignored smoke directories are diagnostic evidence only. They report the frozen
protocol commit as their source plus `working_tree_dirty=true`, correctly recording that
the new implementation was under test before its implementation commit. Confirmatory
execution is authorized only after the implementation commit and a clean tree.
