# Q1 Final Statistical & Claim-Scope Patch — Frozen Protocol (v1.20.1 candidate)

**Status:** FROZEN before any result is computed. Amendments only via dated appendix.

**Baseline of record (published v1.20.0):** Commit A `f27bded`, Commit B `5fed4b9` (HEAD),
tag v1.20.0, version DOI 10.5281/zenodo.21479193. pytest 56/56, audit 495/495, hashes
163/163, frontier 99/99, PDFs 31/24/24, harm 520/340/180/506/14/0.

**Hard scope:** no experimental runners, no new data, no git/tag/release/DOI until
authorized. Only re-analysis of existing outputs, table/manifest regeneration, tests,
audits, PDFs. Paper 1 reference untouched. Local planning files untouched.

---

## Problems to correct (frozen list)

P1 (Block A). The aggregate "exact 95% upper bound ≈0.73%" on 0/506 harmful commits treats
506 clustered commits (shared seeds 501–530, shared streams, overlapping policy/cap/schedule
cells) as independent Bernoulli trials. Remove the population-rate inference; keep the factual
count with an explicit clustering caveat; manifest records
`binomial_upper_bound_reported: false` + reason. Preferred option (adopted): **no aggregate
bound anywhere in the main paper**; no cluster-aware sensitivity is added (all clusters are
zero — a nonparametric bootstrap over all-zero clusters would fabricate a degenerate bound,
which the mission forbids). The per-arm `e6_cp_lo/hi` CSV columns are data artifacts retained
for continuity but quoted nowhere as rates.

P2 (Block B). Multiplicity: the current resampling of observed differences labelled "exact
paired bootstrap" is neither exact nor a null-hypothesis test.
- **Method (frozen before computing):** deterministic **centered paired bootstrap test**:
  `observed = mean(d)`; `d0 = d − mean(d)`; resample `d0` with replacement, B = 100,000;
  `p = (#{|mean(d0*)| ≥ |observed|} + 1)/(B + 1)` (Monte-Carlo corrected, two-sided).
  Per-contrast RNG seeded from CRC32 of the contrast label (order-independent, bit
  reproducible). Never called exact.
- **Unit of inference:** the seed-level paired difference (n = 30 seeds per contrast;
  n = 100 windows never used as unit).
- **Sensitivities (reported alongside, never substituted):** one-sample paired t-test on d;
  Wilcoxon signed-rank on d (p = NaN when d is identically zero, with a note).
- **Families (fixed, outcome-independent):**
  - F1 confirmatory core: exactly 6 = 2 detectors × 3 regimes, primary gate (lp32) vs naive.
    Holm FWER. (Registered superiority family.)
  - F2 budget frontier: exactly **15 = 3 policies × 5 caps**, PortScan-full, Bonferroni
    schedule, **including zero-commit cells** (the previous `commits_total > 0` filter is an
    outcome-dependent selection and is removed). BH within block.
  - F3 chronological: exactly 7 strict-vs-no-adaptation replays. BH within block.
  - Total 28; zero normal-approximation fallbacks permitted in the shipped CSV.
- Verdict changes, if any, are reported honestly.

P3 (Block C). Operational-prevalence contradictions. Correct description of the
**acquisition-yield arm (Table 11, seeds 801–830)**: evaluation stream balanced; detector
calibration balanced; candidate training balanced per class, acquisition cost not modeled;
adjudication candidate pool at operating prevalence; discovery auxiliary only (never
decides); validation independent uniform at operating prevalence, 32 adjudications, plain
accuracy; scope = acquisition yield and delay, not end-to-end pipeline cost.
**Documented deviation from the literal replacement text (frozen now, before editing):** the
§5.5 sentence "With the stream and the probe at operating prevalence…" describes the
DIFFERENT `paper2_fk_*_e2e*` "lite" sensitivity inside the v2 harness, whose evaluation
stream and Binomial probe demonstrably ARE at operating prevalence (verified empirically:
mean alerts 11.09 vs 11.29 predicted at π=0.01; 20.62 vs 20.46 at π=0.10), while its
detector calibration and candidate training remain balanced. Rewriting it to say the stream
is balanced would be false. The fix is **disambiguation**: that paragraph will name the arm,
state exactly its composition (stream+probe at π; calibration and candidate balanced), and
drop every "end-to-end claim" phrasing; Table 11's arm keeps the balanced-stream scope
statement. Both arms get explicit scope fields in the manifest.

P4 (Block D). (a) "Cohort" renamed at claim surfaces to **"VBC-SG-Cohort, a proposal-target
resampling simulation (Cohort-sim)"** with the retention disclaimer; internal flag
`--vbc-defer-mode cohort` unchanged. (b) "affordable" replaced by "non-vacuous within the
evaluated balanced-probe adjudication budget" + "inspected-flow acquisition cost under
operational class imbalance is not measured", in abstract/contributions/section title/
discussion/conclusion/highlights/captions/README/REPRODUCE/graphical abstract. (c) 32-label
claims delimited to the controlled balanced-probe confirmatory setting; "both budgets are
realistic" and "validation costs little and protects" replaced by the mandated qualified
wording.

P5 (Block E). New generator `src/analysis/make_paper2_claim_scope_audit.py` →
`results/tables/paper2_final_q1/claim_scope_audit.csv` (≥12 claims, columns per mission).
New audit guards (structural + numeric, across main/IEEE/supplement/captions/highlights/
README/REPRODUCE/manifest/generated tables) blocking: 0.73%/0.726% as bound; "exact paired
bootstrap"; outcome-dependent multiplicity filters; "stream and probe at operating
prevalence" without arm disambiguation; end-to-end applied to the operational arm;
unqualified "affordable"; Cohort as a physical cohort; unqualified "32 labels suffice"/"a
few labels are enough"; "both budgets are realistic"; "zero probability of harm";
"eliminates harmful commits".

P6 (Block F). Editorial: trim forensic narration in main (traceability preserved in
supplement/notes), shorten Tables 9–11 captions, keep load-bearing limits visible (no
chronological net harm; SVC-RBF fragility; balanced evaluation; acquisition cost not
modeled; EB failure under strong autocorrelation — verify present; no population-rate
inference from 0/506).

## Files expected to change

`src/analysis/make_paper2_q1_multiplicity.py`, `src/analysis/make_final_manifest.py`,
`src/analysis/make_paper2_q1_tables.py`, `src/analysis/audit_paper2_claims.py`,
`src/analysis/make_paper2_claim_scope_audit.py` (new), `src/analysis/make_paper2_q1_frontier.py`
(only if a bound-claim string lives there), `tests/test_q1_statistics.py` (+ extensions),
`manuscript/main.tex`, `main_ieee.tex` (ported), `supplement.tex`, generated tables (both
editions), `README.md`, `REPRODUCE.md`, `manuscript/highlights.md` (if needed),
`results/tables/paper2_final_q1/multiplicity.csv` + `claim_scope_audit.csv` (regenerated),
`MANIFEST.sha256`, `results/final_experiment_ledger.csv`, `results/final_manifest.json`
(provisional stamp only; final stamp deferred to sealing), PDFs. Protocol + checkpoint notes.

## Acceptance criteria / stopping rule

(1) no population-rate inference from 0/506 anywhere; (2) count 0/506 correctly described
with clustering caveat; (3) centered-under-H0 paired bootstrap, correctly labelled,
identical in paper and code; (4) families 6/15/7 = 28, outcome-independent, 0 fallbacks;
(5) operational contradictions removed via accurate per-arm scoping; (6) Cohort-sim and
"affordable" delimited; (7) 32-label claim delimited; (8) claim-scope audit + guards in
place; (9) pytest/audit/hashes/PDFs green, orphans 0, undefined refs 0; (10) no experiment
executed; (11) Paper 1 untouched. Then checkpoint
`notes/q1_final_statistical_claims_patch_checkpoint.md`, propose v1.20.1, STOP without
committing.
