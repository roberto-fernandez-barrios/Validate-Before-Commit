# v1.22.1 Editorial Scope Protocol (FROZEN)

Frozen before any manuscript modification of this phase. Governs every change in
`fix/v1.22.1-editorial-scope`. Baseline: `notes/v1_22_1_editorial_scope_baseline.md`
(v1.22.0, sealing commit `43d9c255af48db9bcc3c6eb341a153381b18c8e8`).

## 1. Authorized changes (exhaustive)

1. **Data Availability correction**: replace the stale `v1.20.2` artifact declaration in
   `manuscript/main.tex` and `manuscript/main_ieee.tex` with the exact v1.22.0 identity
   (version DOI `10.5281/zenodo.21517899`, concept DOI `10.5281/zenodo.21322256`, tag
   `v1.22.0`, sealing commit `43d9c25…`). No claim that v1.22.1 exists.
2. **Size-matched scope limitation**: every size-matched claim in abstract, highlights,
   graphical abstract, introduction, contributions, Results, Discussion, practitioner
   guidance, conclusion, README, REPRODUCE, captions and the IEEE port must carry the
   evaluated scope: zero drift, random proposal trigger, balanced pools, SVC-RBF,
   own-transformer, nominal per-class sample-size parity.
3. **Conditional gating recommendations**: remove universal "validate every proposal"
   recommendations; replace with the conditional formulation (validate when construction
   or evidence conditions are asymmetric or uncertain).
4. **Terminology**: describe the 512-vs-2,000 control as "nominal per-class sample-size
   parity" / "matched nominal per-class training size"; never as "fair/equivalent/fully
   comparable/guaranteed-comparable evidence". Add the nominal-vs-effective caveat in
   Method or Limitations and the Discussion sentence distinguishing row counts from
   operational evidence comparability. "Evidence Asymmetry" stays in the title.
5. **Equivalence margin sensitivity**: report ±0.2 / ±0.5 / ±1.0 pp verdicts from a new
   deterministic generator; ±0.5 remains the preregistered primary margin; PortScan
   described as margin-sensitive; no "identical"/"equal performance" without a margin.
6. **Evidence–validation trade-off table**: the single substantive analytical addition
   (section 3 below).
7. **Historical repositioning**: rename the frozen-policy confirmatory table/caption to a
   historical/initial diagnostic; optionally move the full table to the supplement with a
   compact summary in main. Numbers unchanged.
8. **Detector-score claims**: scope to "within triggered decisions under the evaluated
   detectors"; no absolute "the detector is not the lever"/"scores are uninformative".
9. **ATTENUATION presentation**: keep the registered outcome everywhere it is registered;
   abstract/conclusion lead with the substantive result, ≤1 abstract sentence on the
   taxonomy; forbidden phrasings: "near-elimination", "effectively ELIMINATION",
   "formal elimination", "residual mean harm under ATTENUATION".
10. **VBC-SG compression**: compact main-text description as a scoped, secondary
    extension; details remain in the supplement; frozen-transformer scope retained.
11. **Editorial compression** to hold page/word budgets (section 5).
12. **Tests and audits** guarding all of the above (plan section 16).
13. **Notes**: baseline, this protocol, compression report, hostile review, checkpoint.

## 2. Claims: permitted / prohibited

Permitted (canonical forms):
- "Under the evaluated zero-drift, random-proposal control with balanced pools,
  self-contained challengers trained with nominal 2,000-per-class sample-size parity
  were equivalent to never-adapt within the preregistered ±0.5-pp BA margin."
- "Under that same zero-drift control, point and strict gates provided no measurable
  gain once nominal per-class training size was matched."
- "The zero-drift control shows that the measured value of the gate disappears when the
  evaluated representation and nominal sample-size asymmetries are removed."
- "Within triggered decisions under the evaluated detectors, score magnitude provided no
  consistent incremental information about future candidate value beyond incumbent
  degradation."

Prohibited:
- Any transfer of the size-matched result to mild drift, full drift, observed temporal
  sampling, operational class imbalance, VBC-SG, other classifiers, or "arbitrary
  comparable challengers".
- "Gate value disappears whenever evidence is comparable"; "no measurable value once
  sizes match" without scope; "when comparability is guaranteed, validation adds no
  value"; "every proposal should be validated".
- "identical", "equal performance" (without margin), equality-of-predictions readings.
- Economic claims: gate cheaper in production; 32 labels substitute 2,976; equal
  acquisition cost of candidate-training and probe labels; end-to-end economic analysis.

## 3. Authorized derived tables and exact sources

Both generators are deterministic, read only sealed v1.22.0 outputs plus the frozen
config, write only under `results/tables/v1_22_1_editorial/` and
`manuscript/generated/`, and never touch `results/raw/` or the pinned CSVs.

1. `src/analysis/make_size_matched_equivalence_sensitivity.py`
   - Inputs (exclusive): `results/tables/size_matched_own_transformer_001/by_seed.csv`,
     `.../paired_contrasts.csv`, `.../equivalence.csv`.
   - Unit: seed. CI90: the already-recorded CI90. Margins: preregistered ±0.2/±0.5/±1.0
     only. No new margins, no new resamples.
   - Output: `results/tables/v1_22_1_editorial/equivalence_margin_sensitivity.csv` with
     columns dataset, contrast, effect_pp, ci90_lo, ci90_hi, equivalent_pm0p2,
     equivalent_pm0p5, equivalent_pm1p0, registered_primary_margin, interpretation.
2. `src/analysis/make_evidence_validation_tradeoff.py`
   - Inputs (exclusive): `results/tables/size_matched_own_transformer_001/{by_seed,
     summary,paired_contrasts,run_completion,security_metrics}.csv`,
     `configs/size_matched_own_transformer_v1.json`; `descriptive_contrasts.csv` may be
     read only as an identity cross-check of recomputed values.
   - Main comparison per dataset: naive_512, point_512, strict_512, naive_2000
     (12 rows); point_2000/strict_2000 as a supplementary block.
   - Metrics derived exclusively: candidate size/class; nominal candidate labels per
     proposal; nominal probe labels per proposal; nominal total adjudicated labels per
     proposal; mean BA vs never (pp); CI95; gate gain vs naive at the same size;
     Holm-adjusted significance already registered; mean commits per seed; recall/FPR
     guardrail status. Candidate/probe counts come from config + logs, never hardcoded
     against a discrepancy. 2,000/class − 512/class = 1,488/class × 2 classes = 2,976
     additional candidate labels per proposal.
   - CI95 for cells already sealed (F1/F3, descriptive contrasts) must byte-match the
     sealed values (assert). For the two cells with no sealed CI (point_512/strict_512
     vs never), the CI95 is computed with the identical deterministic centered paired
     bootstrap (`boot_ci` from `make_symmetric_pipeline_dynamic_001`, same N, new unique
     labels), reported as descriptive/uncorrected. No new statistical *families*, no new
     hypothesis tests, no new margins, no monetary costs.
   - Outputs: `results/tables/v1_22_1_editorial/evidence_validation_tradeoff.csv`,
     `manuscript/generated/table_evidence_validation_tradeoff.tex`.

## 4. Scope of the size-matched control (binding wording basis)

Zero drift; random proposal trigger (p=0.05, drift-independent); balanced pools;
SVC-RBF; own-transformer per model; nominal per-class sample-size parity at 2,000/class;
controlled pool-based construction. Nominal parity ≠ equivalence in temporal coverage,
diversity, subtype support, label quality, duplication, prevalence or effective sample
size.

## 5. Hard rules

- **No new experiments**: no runners, seeds, matrices, classifiers, datasets, gates,
  primary metrics, hyperparameter searches, exploratory bootstrap with new margins, or
  factorials. Nothing under `results/raw/` changes.
- **No new statistical inferences** beyond the two derived tables of section 3.
- **Page/word budget**: main ≤ 33 pp (target 32–33); IEEE ≤ 25 pp; abstract 210–235
  words; body words ≤ v1.22.0's 18,088. Supplement may grow moderately.
- **Stop rule**: after validation + hostile review + checkpoint, STOP. No merge, no tag,
  no release, no Zenodo, no DOI, no `results/final_manifest.json` update, no
  `MANIFEST.sha256` re-pin. Human checkpoint decides sealing.
