# final-q1 — Fase C checkpoint (partial: A/B confirmatory DONE; frontier in flight)

Date: 2026-07-19. Branch `final-q1`. NOT committed.

## A/B confirmatory run (D2/P0.3) — COMPLETE

Seeds 2001–2100 (100 fresh; pilot 104–133 excluded from the primary analysis), SVC-RBF,
conditions {independent, own_transformer} × 3 datasets + ToN scaler/PCA decomposition.
Outputs: `symmetric_ab_conf2001_2100.csv`, `symmetric_ab_perseed_conf2001_2100.csv`,
`ab_equivalence.csv` (all under results/tables/paper2_final_kbs/).

### TOST verdicts (PRIMARY: confirmatory seeds only, margin ±1.0 BA, bootstrap CI90)

| dataset | condition | mean gap | CI90 | verdict |
|---|---|---:|---|---|
| ToN | own_transformer | −0.01 | [−0.085, 0.067] | **EQUIVALENT** (also within ±0.2) |
| PortScan | own_transformer | +0.01 | [−0.09, 0.12] | **EQUIVALENT** |
| UNSW | own_transformer | −0.00 | [−0.06, 0.05] | **EQUIVALENT** |
| UNSW | independent | +0.04 | [−0.01, 0.09] | **EQUIVALENT** |
| ToN | independent | −1.43 | [−4.47, 1.63] | NOT established → D2 fallback wording |
| PortScan | independent | −0.30 | [−3.88, 3.28] | NOT established → D2 fallback wording |

Exactly the pre-registered expectation (H3): own_transformer passes everywhere; the
independent condition's role-randomized gap on the two high-variance SVC datasets stays
unresolved (huge seed-level SD ~18 pts — the bimodal ToN/PortScan SVC instability), so the
paper keeps the fallback wording for those cells and the INVERSION remains the load-bearing
evidence. The pilot's −1.78 (ToN) is consistent with the confirmatory −1.43.

### Decomposition (registered; NEW mechanistic finding)

- `inc_scaler_indep_pca` (incumbent's standardizer + independent PCA): **−12.17
  [−15.26, −9.23]** — reproduces essentially the FULL incumbent-fit advantage (−12.35).
- `indep_scaler_inc_pca` (independent standardizer + incumbent's PCA): **+0.16
  [−2.90, +3.08]** — no resolved effect (equivalence to zero not established at this
  precision; stated as such).

→ The representation-ownership interaction localizes to STANDARDIZER ownership, not PCA:
whoever's data sets the feature variances sets the SVC-RBF kernel geometry
(gamma='scale' scales with feature variance). This answers Sol's "decompose transformer
ownership" ask with a resolved single-component attribution, honestly bounded.

## Frontier (D3) — COMPLETE (99/99 arms, seeds 501–530) — RESULTS FROZEN

Outputs: results/tables/paper2_final_q1/{budget_frontier,frontier_anchors}.csv.

### Anchors (fresh internal replication of the core phenomena at seeds 501–530)

- ps_full: naive +7.22 [5.01, 9.39]; point +7.65; strict +7.57.
- ton_full: naive **−1.97 [−4.01, −0.14]** (harm replicates); point +1.17 [0.67, 1.80];
  strict +1.09 [0.57, 1.79].
- ton_zero: naive **−5.35 [−7.77, −3.13]**; point −0.18 [−0.36, −0.03] (residual tie-commits);
  **strict −0.01 [−0.02, +0.00] at 0.13 commits/stream** — the zero-cost conservative
  baseline essentially removes the zero-drift replacement cost.

### Registered non-vacuity verdict (PortScan full): **POSITIVE — 12 configurations qualify**

Target: ≥1 commit, ≥50% of naive benefit, 0 zero-drift commits, <1,024 probe labels/proposal.
- **ebcsdef (pooled EB-CS + defer + lifetime Bonferroni) cap 512: +6.74 = 93% of naive,
  578 labels/proposal** (cap 256: 82%; cap 128: 71%; cap 64: 53% — non-vacuous from the
  SMALLEST cap).
- **VBC-SG-Cohort (fully stratified + defer + lifetime) cap 512: +5.84 = 81%** (cap 256: 62%).
- VBC-SG-Refresh cap 512: +4.92 = 68%.
- e1 (smallest committing cap): ebcsdef 64; vbccoh 64 (bonf) / 128 (pser); vbcref 256.
- ton_zero: **0 commits in EVERY lifetime configuration at EVERY cap** (perfect safety).
- ton_full: small positive resolved gains at c512 (ebcsdef +0.50 [0.01, 1.25]).
- e4 abstention 74–86%; e5 delay ~3.7–4.5 windows; e6 harmful immediate commits **0 observed
  in every configuration** (CP upper bounds 0.17–0.98 depending on commit counts).

→ The a014 "maximally-stacked commits nothing" was the b=64 bottom of a curve, not a property
of the rule: **deployment-long VBC-SG is a practical policy at cap 256–512**. Sol blocker #4
resolved with data.

### Recommended-policy selection (protocol Fase C step 15)

- Zero-cost conservative baseline: **strict** (removes zero-drift cost at 0.13 commits/stream,
  keeps +7.6/+1.1 in benefit/harm regimes).
- Accuracy-oriented: **point** (b=32).
- Risk-controlled with deployment-long guarantee: **pooled EB-CS+defer, cap 512, Bonferroni
  lifetime** (93% of naive; weak-null accumulate per Prop. 1 — or Cohort mode for the
  fixed-target guarantee at 81%).

## Frontier (D3) — status before completion

99 arms (3 scenarios × [3 anchors + 3 policies × 5 caps × 2 schedules]), seeds 501–530,
runner patched pre-launch with e4/e5 instrumentation (n_defer_cap_reject, defer delay);
2 pre-patch partial arms deleted and re-run. Machine shared with kernel-shift-framework
(18 workers) → slow. Aggregator ready (`make_paper2_q1_frontier.py`, endpoints e1–e6 +
registered non-vacuity verdict).

## Pending in Fase C

frontier completion → aggregator + non-vacuity verdict → §5 text updates (A/B confirmatory
numbers + TOST verdicts + decomposition + frontier verdict) with matching audit checks
(Fase E does the full restructure; the numeric updates land with their pinned checks).
