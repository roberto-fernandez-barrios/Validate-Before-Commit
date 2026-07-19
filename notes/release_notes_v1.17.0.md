# v1.17.0 — Final hostile review, `make final-paper` (P10), invariant test suite

Closing release of the final-kbs protocol (Fase E, steps 24–26). No new experiments; this
release hardens the artifact and removes every verifiable inconsistency found by the final
internal hostile review.

## Final internal hostile review (protocol step 24)

Seventeen verifiable PDF↔code↔tables↔README inconsistencies found and corrected
(`notes/paper2_final_hostile_review_001.md` has the full list). Highlights:

- **Lifetime-guarantee contradiction removed.** §3.5 and Limitations still claimed a
  deployment-long bound "requires alpha-spending …, which we do not implement" — leftover from
  amendment 011, contradicting the VBC-SG lifetime risk budget defined one paragraph earlier
  and evaluated in §5. Both passages now state that VBC-SG supplies the lifetime bound and the
  plain per-proposal gates do not.
- Abstract "the risk-controlled gates eliminate it" → "remove the observed loss", matching the
  paper's own "zero observed with a bounded rate, not eliminates" commitment.
- The mild-drift robust-learner claim restated precisely (RF/LogReg naive gains within ±0.2 of
  zero in the marginal and harm regimes — RF keeps a +2.9 benefit in PortScan) with correct
  pointers; previously "≈ 0; Supplementary S1.6" was wrong on both ends.
- README/REPRODUCE: retracted natural-prevalence claim no longer listed as-is; two-stage row
  updated to the split variant (69% fewer candidates, net gain vs never-adapt unresolved);
  stale 004-spec hierarchical CI replaced by the regime×seed-clustered [−1.61, −0.43]; flag
  list synced to the full v2-runner argparse (vbc_sg, stratified/EB-CS gates, lifetime
  spending, disjoint-stream flags); dead pre-Fase-E section/table numbers fixed.
- `requirements.txt` now actually contains statsmodels and river (REPRODUCE §1 already said it
  did) plus pytest; supplement grammar/pointer fixes; highlights.md now describes the final
  graphical abstract.

## `make final-paper` — the P10 workflow (new)

One command runs the full closing pipeline (use `PY=<python>`; needs pdflatex/bibtex on PATH):

1. `verify-hashes` — every pinned CSV in `results/tables/MANIFEST.sha256` re-hashed (136/136
   byte-identical);
2. the new invariant test suite (`tests/`, pytest; see below);
3. full derived-analysis regeneration (aggregators 004–014 + final-kbs);
4. final tables and figures (causal-64, symmetric A/B, amendment-009 table, per-trigger
   figure, graphical abstract);
5. `results/final_manifest.json` (new, committed): commit SHA, artifact version, dataset
   hashes, seed windows, window sizes, prevalences, latencies, models/generators/gates, risk
   levels and spending schedules, causal-64 collision counters (probe = 0, candidate-future =
   0, commits-without-probe = 0), output pinning, audit verdict;
6. CAS + supplement + IEEE compilation (27 pp / 20 pp / 20 pp, 0 undefined refs/citations);
7. the pinned-claims audit — **415/415**.

## Invariant test suite (new, `tests/`)

The protocol's eleven mandatory tests, implemented against the real code paths (the
end-to-end ones drive the v2 runner on synthetic data; no benchmark download needed):

`test_symmetric_ab_disjoint`, `test_global_stream_disjoint`, `test_probe_candidate_disjoint`,
`test_candidate_future_disjoint`, `test_no_probe_never_commits`, `test_stratified_gate_type`
(null simulation of the stratified EB-CS at three tie ratios), `test_lifetime_alpha_budget`
(p-series 6α/π²j² verified against the per-proposal `alpha_allocated` log),
`test_effective_alpha_manifest`, `test_main_tables_final_only`, `test_no_superseded_claims`
(regex blacklist of retracted/stale claims over the living documents),
`test_claim_table_consistency` (the 415-check audit).

## Unchanged

All experimental results, tables and figures are those of v1.16.0; committed confirmatory
CSVs regenerate byte-identically. Manuscript changes are correction-only (no claim was
strengthened).
