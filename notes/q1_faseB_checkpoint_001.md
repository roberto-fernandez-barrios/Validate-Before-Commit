# final-q1 — Fase B checkpoint (P0 blockers implemented)

Date: 2026-07-19. Branch `final-q1` (base e7aae30 = v1.17.0). NOT committed (protocol §1.3).
Protocol: `notes/q1_max_protocol.md` (frozen, with Roberto's six precisions of 2026-07-19
incorporated: D1 formal chain required, D2 pilot/confirmatory split, D3 registered endpoints,
D4 strict obligatory + VBC gated on invariants, D5 hybrid kept + inspected-flows-per-attack,
versioning freeze at v1.17.0).

## D1 / P0.1 — VBC-SG defer semantics (code + theory + tests)

- `--vbc-defer-mode {accumulate,cohort,refresh}` implemented in `run_paper2_readaptation_v2.py`
  for `vbc_sg` and `labeled_probe_ebcs_defer`:
  * accumulate (default; the pre-existing behaviour, now the ablation): same e-process,
    continuation labels at the CURRENT window's mixture;
  * cohort: continuation labels at the PROPOSAL-time mixture (`pending["sev0"]`, which honours
    probe latency) — fixed-target guarantee;
  * refresh: each deferral window is a FRESH evidence set; the proposal's alpha is
    Bonferroni-split as alpha/(1+defer_windows) across the at most 1+D sets (applied at the
    initial test too).
- Registered pending-candidate policy: an unresolved DEFER now explicitly BLOCKS new proposals
  (absorbed like cooldown). Unreachable under defer<cooldown configs -> bit-identical to the
  released runner for every existing arm (verified: old-vs-new by_seed outputs identical for
  vbc_sg and ebcs_defer on synthetic data, default flags).
- Continuation now uses the proposal's stored alpha (correctness fix; identical in value for
  all existing runs since pending blocks proposals).
- Audit counters added to the per-seed summary: n_defer_continuations, n_defer_draws_at_sev0,
  defer_evidence_max, vbc_defer_mode.
- **D1 formal chain (i)-(iv) CLOSED:**
  (i) H0_cond defined; (ii) exact e-process identified with the code-theorem correspondence
  LCB>0 <=> W>1/alpha; (iii) supermartingale proof under variable conditional means written
  out in supplement §S4 (Fan's inequality; predictability of lambda_i, mu_hat checked against
  the implementation); (iv) `test_weak_null_drifting_means` PASSES (false-commit <= alpha
  under oscillating/trending means <= 0 and changing tie probabilities).
  => Proposition 1 added to §3.5; the accumulate mode carries the WEAK-null guarantee
  (explicitly stated as "conditionally better at some window, not necessarily at commit
  time"); cohort/refresh presented as the interpretable variants under drift.

## P0.2 — Candidate-label latency

- Contradiction resolved: Limitations sentence replaced; new Table `tab:latency` in §4 fixes
  the causal availability of every object (probe pool/observed, candidate pool/sliding,
  recalibration, training completion = 0 assumed, pending policy), read off the code.
- Semantics verified in code: `--candidate-latency L` shifts the WHOLE batch (features+labels)
  — pool arms sample at sev(t-L) (so the a014 e2e claim was correct), sliding arms train on
  the 8 windows ending t-L. Instrumented: trow now logs cand_latency, cand_sev_used,
  cand_newest_window. `test_candidate_latency_semantics` PASSES.

## D2 / P0.3 — A/B equivalence machinery

- `paper2_symmetric_ab_final.py`: per-seed output (symmetric_ab_perseed*.csv), CLI
  (--seed-start/--seed-end/--datasets/--models/--decompose/--out-suffix), scaler/PCA
  decomposition conditions {inc_scaler_indep_pca, indep_scaler_inc_pca} (ToN x SVC scope).
  RNG-consumption order unchanged -> pilot aggregates reproduce deterministically; default
  files untouched.
- `paper2_ab_equivalence.py`: bootstrap TOST at margins ±0.5/±1.0/±2.0; PRIMARY = seeds
  2001-2100 only; pooled 130 labeled "pilot-plus-confirmatory" (secondary). Fallback wording
  enforced in the console verdict. `test_ab_equivalence_margin` PASSES.
- Manuscript already softened per D2: "identified" -> representation-ownership interaction
  dominant in the evaluated SVC-RBF pipeline; "statistically zero" -> "unresolved from zero
  (equivalence not established at this precision)"; same in Limitations; decomposition and
  equivalence analysis announced as registered.

## P0.4 — Overclaim sweep (applied + regression-tested)

Fixed: Discussion "empirically, safe across all four downstream models" -> "not materially
worse in the evaluated average results" (+ measured exceptions named); "is safe"/"fully safe"
in §5 -> harm-avoiding / commits nothing; abstract "A replication" -> "An internal
replication"; blacklist extended in test_no_superseded_claims (9 new patterns, incl. the old
defer phrasing, "gap statistically zero", the latency contradiction and "empirically safe").

## P0.5 — Evidence hierarchy

"Three levels" -> "Five tiers of evidence, kept separate" in §5.1: confirmatory core /
registered follow-ups / causal-operational feasibility / external boundary (chronological) /
exploratory, with the internal-not-external framing up front. `test_evidence_tier_labels`
PASSES.

## State

- PDFs: 28 pp CAS / 21 pp supplement / 21 pp IEEE, 0 undefined refs (page +1 vs v1.17.0 from
  tab:latency + Proposition 1; Fase E restructure will absorb it — target <= 27 pp).
- Audit: 415/415. README/REPRODUCE synced (new flags + protocol pointer).
- New tests: test_q1_defer.py (7) + test_q1_claims.py (5, one skip until Fase C) on top of the
  existing 14.
- supplement: new §S4 proof; amssymb added.

## Next (Fase C — needs no further authorization per plan, but no commits)

1. A/B confirmatory run: seeds 2001-2100, SVC {independent, own_transformer} x 3 datasets +
   decomposition (ToN x SVC); then `paper2_ab_equivalence` (TOST verdicts).
2. Budget frontier (D3): caps {64..1024} x {bonferroni, pseries}, 3 scenarios, seeds 501-530,
   policies {pooled EB-CS+defer, VBC-SG-Cohort, VBC-SG-Refresh} + point/strict anchors;
   registered endpoints e1-e6; stopping rule = non-vacuity clause.
