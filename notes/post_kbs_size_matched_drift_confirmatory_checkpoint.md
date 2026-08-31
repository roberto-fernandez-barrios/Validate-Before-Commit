# CHECKPOINT — Confirmatory result of the size-matched-under-drift experiment (B2)

Date: 2026-08-31. Branch: `post-kbs-hardening`.
Protocol: `notes/post_kbs_size_matched_drift_protocol_001.md` (frozen a68c90e).
Implementation: commit 9f1159a (checkpoint `notes/post_kbs_size_matched_drift_implementation_checkpoint.md`).
Analysis: `src/analysis/make_post_kbs_size_matched_drift_001.py` — committed BEFORE the run;
executed once, unmodified, under the paper2 environment (requirements-lock versions).

## A. Execution record

- Command: `run_symmetric_pipeline_replication --run --confirmatory-authorized
  --config configs/post_kbs_size_matched_drift_v1.json` (paper2 env).
- Seeds: exactly 6001–6030 (n=30). Arms: 21/21 COMPLETE (`--validate-complete`).
- Provenance: every arm `mode=run`, `working_tree_dirty=false`, source commit 9f1159a.
- Runtime: 36.7 min total; 34–159 s per arm.
- No retries, no substituted seeds, no parameter changes, no arm additions/removals; one
  pass; the analysis ran once after all arms completed.

## B. Integrity audits (from the frozen analysis; violations raise)

- Nesting + severity audit: **707 (seed, window) candidate pairs verified** — every
  B2000's 512-prefix row-hash equals the B512 batch hash at the same proposal, the
  recorded proposal-time severity is identical across sizes and equals the stream's
  severity at that window.
- Coupling audit: **naive pairs proposal-coupled in 90/90 seed-scenarios** (identical
  trigger/commit timelines); gated cross-size pairs classified seed-paired, as
  preregistered (protocol 2.2).

## C. Registered results (families G1–G4, Holm within family; seed = unit; 30 seeds)

**G2 — the primary size effect (naive-2000 − naive-512), BA points:**

| Scenario | Effect | CI95 | p_holm | Frozen classification |
|---|---|---|---|---|
| ps_full | **+0.82** | [0.67, 0.98] | 3.0e-05 | **SIZE BENEFIT** |
| unsw_full | **+1.66** | [1.51, 1.81] | 3.0e-05 | **SIZE BENEFIT** |
| ton_full | **+1.00** | [0.60, 1.39] | 3.0e-05 | **SIZE BENEFIT** |

**Registered program outcome: `HOMOGENEOUS-SIZE BENEFIT`** — the frozen permitted reading:
"more candidate evidence helps under drift too; the zero-drift account extends
directionally." The frozen-transformer S1.5 pattern (size-matching deepens full-drift
harm) does NOT reproduce under self-contained pipelines: it is bound to the frozen
representation.

**G1 — value of updating (all six Holm-significant):** naive-512 − never = +8.90 / +2.13 /
+1.44; naive-2000 − never = +9.72 / +3.79 / +2.44 (ps/unsw/ton). Always-deploy remains
beneficial at full drift under self-contained pipelines at BOTH candidate sizes.

**G3 — gate value at the matched size under drift (0/6 positive):** point −0.06…+0.15
(none Holm-significant); strict on unsw_full **−0.34 [−0.53, −0.15], Holm-significant** —
a small resolved COST of strict validation where updating is clearly beneficial; the other
strict cells unresolved (−0.14, −0.00).

**G4 — gate×size interactions (secondary):** uniformly ≤ 0 in point estimate; only
unsw_full/strict resolved (−0.31, Holm-sig). Consistent with gate value at 512 being
partly compensation for the evidence disadvantage, now under drift as well.

## D. Guardrails (language-gating only; principal NI margins)

- Matched size (2000): all point cells pass recall+FPR NI; strict passes everywhere
  except **FPR NI on unsw_full (ΔFPR +0.86, ub95 above +0.5)** — no safety language for
  that cell.
- 512 (descriptive cells): strict fails recall NI on ps_full and ton_full (Δrecall −0.37,
  −0.75); point passes everywhere.

## E. Descriptive only (feeds no rule)

Future-value H1/3/5/10 and harmful-commit accounting are recorded in
`harmful_commit_summary.csv` with the clustering caveat; no sign-rate criterion exists in
this protocol and none was applied.

## F. Scope of what this does and does not establish

Establishes (within the pool-based full-drift construction, SVC-RBF, KS-max, 30 seeds):
a material, Holm-significant nominal candidate-size benefit under drift in 3/3
benchmarks; no measurable point/strict gate value at the matched size under drift, with
one small resolved strict cost. Does NOT establish: any deployment prevalence; any
proposal-coupled gate×size claim; anything about observed-data or natural-prevalence
operation; anything outside the evaluated sizes/budgets. The manuscript is NOT modified
in this phase; interpretation for the paper is deferred to the hostile results audit and
a separately authorized rewrite.
