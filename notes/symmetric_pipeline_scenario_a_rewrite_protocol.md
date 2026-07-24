# Scenario-A manuscript rewrite protocol (FROZEN)

Date: 2026-07-22. Branch: `feature/symmetric-pipeline-replication`.
Authorization: human authorization "Reescritura del manuscrito bajo ESCENARIO A"
(2026-07-22), based on `notes/symmetric_pipeline_confirmatory_checkpoint.md` and
protocol Appendix A (commit `96576bb`).

## Frozen interpretation

- Classification: **Scenario A — persistence** (per Appendix A; BA determines
  A/B/C; recall/FPR restrict language only). NOT reinterpreted as B for the
  `unsw_zero strict` cell — that cell is a local trade-off, reported as such.
- Authorized central interpretation:
  "Preprocessing asymmetry amplified harmful promotion, but candidate
  governance remains materially useful with self-contained predictive
  pipelines."
- Mandatory nuance: "The locus of average harm shifts from full-drift
  replacement under frozen preprocessing to healthy-incumbent replacement
  under self-contained pipelines."

## Allowed claims (load-bearing numbers, from the frozen analysis)

- Full drift, own-transformer, naive−never: PortScan +7.21 [4.89, 9.52];
  UNSW +2.55 [2.34, 2.75]; ToN +1.03 [0.55, 1.53] — mean full-drift harm does
  not persist under self-contained pipelines.
- Ownership interaction (own-naive − frozen-naive): +0.90 / +1.15 / +5.98
  (full); ps_zero +2.36; ton_zero +5.49 — preprocessing ownership is a major
  amplifier.
- Zero drift, own, naive−never: PortScan −1.74 [−2.35, −0.96]; UNSW −0.65
  [−0.77, −0.55] (both material, Holm-sig.); ToN −0.38 [−0.53, −0.25]
  (significant, sub-material, NOT equivalent to zero).
- Gates under own: all six zero-drift gate contrasts positive and Holm-sig.
  (ps_zero strict +1.68, point +0.75; unsw_zero strict +0.51, point +0.19;
  ton_zero strict +0.34, point +0.11); ton_full point +0.64.
- Costs reported honestly: unsw_full point −0.21 [−0.36, −0.06]; ps_full
  gates ≈ 0 ns.
- Harmful proposals persist (descriptive, seed-clustered): naive-own
  harmful@H5 = 65% (ps_zero), 61% (unsw_zero), 46% (ton_zero), 42% (ton_full);
  strict cuts commits (ps_zero 104→14, unsw_zero 104→20, ton_zero 104→5).
- Security guardrails: winning cells pass both NI margins EXCEPT unsw_zero
  strict (Δrecall −0.99, one-sided lo95 −1.26 vs margin −1.0; passes lax −2.0;
  FPR improves −2.0) → trade-off language only.

## Forbidden claims (enforced by audit guards + tests)

1. Full-drift harm persists under own-transformer (it does not).
2. Own-transformer / per-model preprocessing eliminates all harmful updating
   (zero-drift material harm persists in 2 of 3 benchmarks).
3. Universal gate improvement (unsw_full point has a small significant cost;
   ps_full gates add ≈ nothing).
4. "Security improvement" for `unsw_zero strict`.
5. Generalizing QK-ZZ / VBC-SG / mild-drift results to own-transformer
   pipelines (they remain evaluated under the historical frozen policy).
6. Treating harmful commits as independent trials / binomial inference.
7. Equivalence of own-naive vs never in critical cells.
8. Scenario names other than the protocol's A/B/C definitions.
9. Causal language beyond the registered design; generality beyond the
   evaluated pipelines.

## New tables (generated from the frozen analysis outputs only)

- `manuscript/tables/table_symmetric_pipeline.tex` — main-body compact matrix
  (6 scenarios × frozen/own; never/naive/point/strict; naive−never,
  point−naive, strict−naive with CI95 + Holm).
- `manuscript/tables/table_symmetric_security.tex` — main-body security panel
  (BA, attack recall, FPR, attack F1, NI verdicts).
- Supplement: full F1–F4 multiplicity, equivalence verdicts, transformer
  interactions, harmful@H1/3/5/10 + censoring (moved out of the main body).
- Generator: `src/analysis/make_symmetric_pipeline_tables.py`, reading
  exclusively `results/tables/symmetric_pipeline_dynamic_001/`.

## Manuscript structure changes

1. Abstract: full rewrite, 200–240 words, per the authorized outline.
2. Contributions: reduced to four (governance / symmetric replication /
   mechanism / frontier).
3. Method: new subsection "Self-contained candidate-pipeline replication"
   (raw stream, DetectorPipeline, ModelPipeline, frozen vs own semantics,
   identical raw candidate batches, raw probe, complete-bundle commit, t+1
   serving, seeds 3001–3030, estimands, margins, guardrails).
4. Results: new early subsection "Symmetric-pipeline dynamic replication"
   (the central new result) + security panel + harmful-proposals summary;
   historical frozen core reframed as the motivating configuration.
5. Mechanism section: connected to the dynamic replication (scaler-dominated
   ownership; own-transformer corrects mean full-drift harm; zero-drift
   promotion risk remains; no single-cause claim).
6. Discussion: three findings — construction necessary but insufficient;
   incumbent health determines when governance matters; validation has
   opportunity cost (no policy dominates).
7. Limitations: updated per the authorization list, incl. explicit scope
   statement that QK/VBC-SG/mild remain frozen-policy evidence.
8. Conclusion: rewritten to the authorized closing message.
9. Title: NOT changed in this phase; a recommendation with justification goes
   in the checkpoint.

## Files to modify

`manuscript/main.tex`, `manuscript/main_ieee.tex` (regenerated via
`src/analysis/port_ieee.py`), `manuscript/supplement.tex`,
`manuscript/highlights.md`, `manuscript/tables/*` (new), `README.md`,
`REPRODUCE.md`, `src/analysis/make_symmetric_pipeline_tables.py` (new),
`src/analysis/make_final_experiment_ledger.py`,
`src/analysis/audit_paper2_claims.py` (updated wording checks + new guards),
`tests/` (new guards), `results/tables/MANIFEST.sha256` (ADDITIVE pin of the
new CSVs only), PDFs.

## Explicitly NOT done in this phase

- No scientific runner executes (QK-ZZ, VBC-SG, mild, neutral, frontier,
  chronological, new datasets, new seeds: all forbidden).
- No modification of confirmatory results, margins, families, A/B/C rules,
  seeds, the pending Paper 1 reference, or v1.20.2 historical outputs.
- `results/final_manifest.json` stays the SEALED v1.20.2 manifest: per repo
  convention the versioned manifest is stamped in the sealing commit of a
  release; the v1.21.0 manifest will be stamped when v1.21.0 is sealed. This
  phase proposes v1.21.0 (not v1.20.3) and prepares a provisional artifact
  candidate without sealing it.
- No merge, tag, release, Zenodo, DOI.

## Stopping rule

Deliver `notes/symmetric_pipeline_scenario_a_manuscript_checkpoint.md` and the
console checkpoint; then stop. Recommendation is exactly one of
READY FOR FINAL HOSTILE REVIEW AND v1.21.0 SEALING / NOT READY — BLOCKER.
