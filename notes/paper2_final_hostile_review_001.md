# Final internal hostile review (final-kbs protocol, step 24)

Date: 2026-07-19. Scope: contradictions between PDF (main/supplement/IEEE), code, tables and
README/REPRODUCE, on top of the 415-check numeric audit (which passed 415/415 before and after
this review). Per step 25, only *verifiable* errors were corrected; no claims were strengthened.

## Findings and fixes

### A. PDF-internal contradictions (fixed in `manuscript/main.tex`, propagated to IEEE)

1. **"which we do not implement" (lifetime alpha-spending) — the most serious find.**
   §3.5 "What is and is not guaranteed" and §7 (Limitations) both still said a lifetime bound
   "requires alpha-spending across proposals or a deployment-long e-process, *which we do not
   implement*" — one paragraph after §3.5 defines the VBC-SG deployment-long risk budget
   (Bonferroni / p-series spending, property (ii)) and §5 reports its empirical frontier
   (`--lifetime-alpha`, `--alpha-spending pseries` exist in the runner; per-proposal
   `alpha_allocated` is logged). Leftover text from amendment 011, superseded by final-kbs
   P0.3/P1.1. Both passages rewritten to state that VBC-SG supplies the lifetime bound and the
   *plain* per-proposal gates do not.

2. **Abstract "the risk-controlled gates eliminate it"** contradicted §5's explicit commitment
   («We state this as "zero observed with a bounded rate", not "eliminates"»). Reworded to
   "remove the observed loss".

3. **"RF/LogReg mild gains ≈ 0; Supplementary §S1.6"** — wrong on both ends: S1.6 is the v1
   *full-drift* downstream study, and the amendment-009 CSV shows RF mild-drift PortScan gain
   is +2.87 (a benefit, not ≈0). Restated precisely: mild-drift naive gains for RF/LogReg stay
   within ±0.2 of zero *in the marginal and harm regimes* (vs SVC's resolved −0.65 in ToN),
   with the correct pointers (amendment-009 artifact; S1.6 for full drift).

4. Typo "class-imbaled" → "class-imbalanced" (§3.5).

### B. Supplement (fixed in `manuscript/supplement.tex`)

5. S1.7 referenced "\S5.2" of the main paper for the attack-F1 robustness of the taxonomy; the
   fact lives in S1.1. Fixed to "\S S1.1".
6. S2.3 contained a dangling sentence fragment ("Separately, on natural-prevalence evaluation
   streams: (An earlier variant…)") — an editing artifact of the Fase-E extraction. Rewritten
   into two grammatical sentences pointing to the corrected calibrated-at-prevalence experiment
   in main §5.3.

### C. README.md (stale numbers and section pointers)

7. "+19.5 to −4.5" → **−4.6** (Table S1 / audit value).
8. Hierarchical-model CI "β_deg = −1.02 [−1.17, −0.87]" was the superseded 004-spec CI; the
   paper reports the regime×seed-clustered [−1.61, −0.43] (amendment 005). Fixed, with the
   clustering stated.
9. "§5.10" (twice) and "coupling-aware §5.3" pointed at pre-Fase-E numbering → now Supplement
   §S1.1 / paper §5.3.
10. The v2-runner flag list omitted every gate/flag added since amendment 009
    (`labeled_probe_cs/ebcs/strat/ebcs_strat/ebcs_defer/exact_strat`, `vbc_sg`, `cumulative`,
    `replay`, `--stream-disjoint-windows`, `--disjoint-window-frac`, `--min-calib-windows`,
    `--no-probe-policy`, `--cumulative-mode`, `--lifetime-alpha`, `--alpha-spending`,
    `--defer-windows`, `--candidate-latency`, `--stream-prevalence`). Synced against the
    argparse of `run_paper2_readaptation_v2.py`; VBC-SG named and its invocation given.
11. "paper, Table 5" (policy frontier) → unnumbered "policy-frontier table" (numbering shifted
    in Fase E). "all 240+ pinned numbers" → 415. Repository-structure block updated
    (supplement, tests/, committed confirmatory CSVs, `make final-paper`).

### D. REPRODUCE.md (claims → artifact map)

12. **The claims table still listed the retracted claim as-is**: "The probe need not be
    balanced: full safety/benefit at natural prevalence (π=0.10/0.01)". The paper *retracts*
    this (main §5.3, Supp §S2.3). Row rewritten as the retraction + corrected bound.
13. Two-stage row said "74% fewer candidates … still net-positive in the harm regime" — both
    superseded by the split variant (69% fewer; net gain vs never-adapt honestly unresolved,
    +0.15 [−0.15, 0.46]). Fixed.
14. Hierarchical row carried the stale 004 CI (see #8); fixed, artifact now also points to
    `paper2_decision_quality_005/`.
15. Dead pointers from pre-Fase-E numbering (§5.6, §5.10, "Table 4/5/7/8/9", "Fig 1–5")
    replaced with current section/table identities; final-kbs row added.
16. `requirements.txt` did not contain statsmodels/river although REPRODUCE §1's comment said
    it did (both are needed: MixedLM analysis, river monitors). Added (plus pytest for the
    P10 test suite).

### E. highlights.md

17. The graphical-abstract paragraph described the *old* design and the old generator script.
    Updated to the redesigned Alarm→Challenger→Validate→Commit/Reject/Defer abstract
    (`make_paper2_graphical_abstract_final`, 2299×857).

## Checked and found consistent (no action)

- 415/415 numeric audit before and after edits; all three PDFs compile with 0 undefined
  references/citations (27 pp CAS, 20 pp supplement, 20 pp IEEE).
- Body table set = exactly the 9 final tables; supplement = exactly the 7 v1 tables; no
  superseded table is input anywhere; body has no `\appendix`.
- S1.x/S2.x/S3 cross-references from the body (spot-checked all), §3.x internal refs,
  contribution count (4), replay count (six), harmful-commit rates (15–32% vs "about a
  quarter"/23% usages are per-context and consistent), zero-drift triples, A/B numbers
  (abstract/§5/Limitations/table all agree), VBC-SG frontier numbers vs `final_kbs` CSVs.
- P0.5 vocabulary scan: remaining uses of "eliminate/safe/causal/adversarial/label-efficient"
  are qualified in-sentence as the protocol requires.
- CITATION.cff / .zenodo.json / bib artifact note (Version 1.16.0) consistent.

## Verification after fixes

- `make final-paper` (new, P10): hash verification, 11-test invariant suite (disjointness,
  gate validity, lifetime budget, manifest, claims), full analysis regeneration, final tables
  and figures, `results/final_manifest.json`, three PDF builds, 415-check audit.
