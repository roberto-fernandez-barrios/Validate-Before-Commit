# CHECKPOINT — Scenario A manuscript rewrite

Date: 2026-07-22. Branch: `feature/symmetric-pipeline-replication`
(11 commits ahead of `main`; no merge, no tag, no release, no Zenodo).
Rewrite protocol: `notes/symmetric_pipeline_scenario_a_rewrite_protocol.md`
(commit `3d1d9f6`). Rewrite commits: `0b832f5` (manuscript), `417647e`
(artifact/audits/guards).

## A. Scientific framing

- **Old thesis**: drift-triggered updating can be harmful, particularly in the
  original ToN-IoT full-drift setting (frozen preprocessing implicit).
- **New thesis**: drift alarms do not establish challenger superiority.
  Preprocessing ownership can strongly amplify promotion harm, but even
  self-contained candidate pipelines remain risky when the incumbent is
  healthy; explicit candidate–incumbent validation reduces that residual
  promotion risk.
- **Claims removed**: ToN full-drift frozen harm as general/definitive
  evidence; "93%/frontier" as headline of the abstract; gate as universal
  improvement; abstract's 533-word-era survey structure.
- **Claims added** (all from the frozen analysis): full-drift non-persistence
  (+7.21/+2.55/+1.03); ownership interaction (+5.98 ToN full, +5.49 ton_zero,
  +2.36 ps_zero); zero-drift material residual (−1.74/−0.65; −0.38 resolved
  sub-material); 6/6 zero-drift gate recoveries Holm-sig.; unsw_zero strict
  recall↔FPR trade-off; locus-shift sentence (mandatory nuance) verbatim.
- **Frozen vs own scope**: QK-ZZ, VBC-SG/budget frontier and mild drift are
  explicitly scoped to the historical frozen policy (Limitations paragraph +
  audit guard SP5); no transfer is claimed.

## B. Manuscript

- **Title**: unchanged in this phase, as instructed. **Recommendation**:
  adopt *"Validate Before Commit: Risk-Aware Promotion of Drift-Triggered
  Classifier Pipelines in Network Intrusion Detection"* at sealing.
  Justification: (i) "label-efficient" in the current title names a property
  the paper itself now scopes narrowly (the decision's incremental cost), a
  recurring reviewer flag; (ii) "risk-aware promotion" and "pipelines" match
  the new central result (promotion risk of self-contained pipelines) and the
  keyword set already in the metadata ("risk-aware model updating"); (iii) the
  paper is not yet submitted, so the change is editorially free. The
  conservative option (keep title) is defensible because §3.4/§5 define
  label-efficiency's exact scope; the decision is the human's at sealing.
- **Abstract**: fully rewritten, **232 words**, in the authorized order
  (alarm≠superiority → frozen original → preregistered replication → results →
  interaction → gate scope → chronological limit). Guard: ≤290-word test.
- **Contributions**: reduced to four (governance stages; symmetric replication
  as central result; mechanism with SVC-RBF scope; frontier + boundaries with
  frozen-policy scope). The 99-arm frontier is no longer ranked above the
  replication.
- **New subsections**: §3.6 "Self-contained candidate-pipeline replication"
  (method: raw stream, ModelPipeline/DetectorPipeline, frozen/own semantics,
  identical raw batches, raw probe, complete-bundle commit, t+1 serving, seeds
  3001–3030, estimands, margins, guardrails, seed as inferential unit);
  §5.2 "Symmetric-pipeline dynamic replication: the central new result"
  (main matrix + security panel + harmful-proposals summary + scope);
  Discussion reorganized around three findings (construction necessary but
  insufficient; incumbent health; opportunity cost / no policy dominates);
  new Limitations paragraph "Scope of the symmetric-pipeline replication";
  Conclusion rewritten to the authorized closing message.
- **Moved to supplement**: full F1–F4 contrast table, harmful H1/3/5/10 +
  censoring, gate×transformer interactions (new §S7).
- **Word/page count**: main body ≈ 14.3k words (approx, macro-stripped);
  **main.pdf 33 pages (body 30, references from p.31; +3 vs v1.20.2, driven by
  the mandated new tables/sections — flagged for the human editor; density
  unchanged)**; supplement 27 pages; IEEE 25 pages; 0 undefined refs/citations
  in all three.

## C. New evidence in the manuscript

- `tab:symmetric_pipeline` (main): 12 rows (6 scenarios × frozen/own), never
  BA + naive−never + point−naive + strict−naive, CI95, Holm daggers on the
  registered (own) cells; frozen cells labeled descriptive.
- `tab:symmetric_security` (main): 12 own-transformer gate cells, Δrecall
  (one-sided lb95), ΔFPR (ub95), NI verdicts; unsw_zero strict trade-off
  explicit in caption and text.
- Harmful-future summary in §5.2 text (65/61/46/42% at H5; seed-clustered
  caveat verbatim) + full table S7.
- Mechanism: §5.4 ownership analysis now closes with the dynamic-replication
  linkage (scaler = dominant identified amplifier, not sole cause).

## D. Statistical correspondence

- F1/F2/F3/F4 exactly as frozen (3/3/6/12 contrasts, Holm within family,
  deterministic centered paired bootstrap 100k, t/Wilcoxon sensitivities);
  margins ±0.5 (±0.2/±1.0), recall NI −1.0 (−0.5/−2.0), FPR NI +0.5
  (+0.25/+1.0) — unchanged from Appendix A.
- Adjusted results quoted in the manuscript match
  `symmetric_pipeline_dynamic_001/paired_contrasts.csv` (audit SP7 pins 7
  headline cells; test_headline_numbers_match_frozen_csv duplicates the pin).
- Equivalence: no critical cell equivalent within ±0.5 (C1 fails); reported.
- Guardrails: 1 restricted cell (unsw_zero strict), language enforced by
  audit SP4 + test.
- **A classification unchanged**: CLAIM_INTERPRETATION.json still Scenario A;
  guarded by test_scenario_is_A_per_frozen_rules.

## E. Artifact

- Files: manuscript (main/ieee/supplement/highlights/tables×2 dirs), README,
  REPRODUCE (commands + claim-map rows), new
  `src/analysis/make_symmetric_pipeline_tables.py`, ledger generator block
  (`symmetric_pipeline_dynamic`, 42 dirs, protocol commits, provenance
  pointer), `run_completion.csv` extended with per-arm transformer policy,
  detector policy, protocol commit and raw-stream-hash digest.
- `results/tables/MANIFEST.sha256`: re-pinned **additively** 164 → 173 (9 new
  CSVs; 0 removals; verify 173/173, 0 unpinned extras).
- `results/final_manifest.json`: **left at sealed v1.20.2 state**
  (`11474601…`), per repo convention the v1.21.0 manifest is stamped in the
  sealing commit; version **v1.21.0 proposed** (not v1.20.3) because the
  evidence and central interpretation changed.
- Audit: 538 → **547 checks** (9 new SP guards: full-drift non-persistence
  stated; zero-drift residual stated; no positive elimination claims; no
  positive "security improvement"; frozen-policy scope present; harmful
  commits marked non-independent; numeric pins vs frozen CSV; F4 positivity;
  scenario named per protocol) + 2 legacy wording checks updated (bootstrap
  doc count 3→5 for the new table captions; conclusion safeguard sentence
  retained verbatim).
- Tests: 87 → **95** (8 new Scenario-A guards in
  `tests/test_scenario_a_claims.py`; registries in test_claims/test_q1_claims
  updated for the new tables and the six-tier list).
- No scientific runner executed in this phase; v1.20.2 raw outputs and the
  confirmatory symmetric outputs byte-untouched (only run_completion.csv
  gained provenance columns, regenerated deterministically; all other CSVs
  byte-identical).

## F. Gates

| gate | result |
|---|---|
| pytest | **95/95** |
| audit | **547/547** |
| verify manifest | **173/173 pinned, 0 unpinned extras** |
| refs/citations | 0 undefined in main/supplement/IEEE |
| PDFs | main 33pp (body 30) / supplement 27pp / IEEE 25pp |
| orphan dirs | 0 (ledger, 11 blocks / 541 arm dirs) |
| sealed v1.20.2 manifest | byte-identical (`11474601…`) |
| historical scientific CSVs | unchanged (MANIFEST additions only) |
| background processes | none |

## G. Hostile-review response

1. **¿Persiste el daño con pipelines autocontenidas?** En media full-drift, NO
   (+7.21/+2.55/+1.03, Holm-sig.). Bajo zero drift, SÍ: material en PortScan
   (−1.74) y UNSW (−0.65), resuelto sub-material en ToN (−0.38, no
   equivalente); y las propuestas dañinas individuales siguen siendo comunes
   (42–65% harmful@H5, descriptivo).
2. **¿Cuánto explicaba preprocessing ownership?** Todo el daño medio
   full-drift (interacción +5.98 ToN full; el signo se invierte) y gran parte
   del zero-drift en ToN/PortScan (+5.49/+2.36), pero no el residual: UNSW
   zero es idéntico entre políticas (+0.03, equivalente) y ps/unsw zero
   siguen dañinos bajo own.
3. **¿Sigue siendo útil la gate?** Sí, materialmente, donde el incumbente está
   sano: 6/6 contrastes zero-drift positivos Holm-sig. (strict hasta +1.68) y
   ton_full point +0.64; strict reduce la exposición a commits en un orden de
   magnitud.
4. **¿Dónde deja de ser útil?** Con incumbente colapsado: ps_full ≈ 0 (n.s.)
   y unsw_full point −0.21 resuelto — coste de oportunidad declarado en
   Results, Discussion (Finding 3) y tabla principal.
5. **¿Trade-offs recall/FPR?** Uno: unsw_zero strict (Δrecall −0.99, lb95
   −1.26 vs margen −1.0; FPR −2.0). Reportado como trade-off; lenguaje de
   seguridad prohibido para esa celda (audit SP4 + test). Las demás celdas
   ganadoras pasan ambos márgenes y FPR mejora en todas.
6. **¿Se generaliza a QK/VBC-SG?** No se afirma: scope congelado explícito en
   Limitations + guard SP5; su evidencia queda bajo la política frozen.
7. **¿Net harm cronológico?** Sigue sin observarse en los 13 replays;
   se mantiene como límite principal de validez externa (sin cambios).
8. **¿Queda alguna objeción load-bearing?** La objeción de ownership está
   respondida con la réplica preregistrada (paridad bit a bit del modo frozen
   incluida). Restan como límites declarados, no objeciones sin responder:
   validez externa cronológica, imbalance operacional del probe/batch, y el
   scope frozen de QK/VBC-SG/mild — todos con párrafo propio en Limitations.

## H. Recommendation

**READY FOR FINAL HOSTILE REVIEW AND v1.21.0 SEALING**

Pending human decisions at sealing: (1) title option (recommendation in §B);
(2) accept main at 33pp (body 30) or order one more compression pass;
(3) stamp the v1.21.0 manifest + version metadata in the sealing commit.
