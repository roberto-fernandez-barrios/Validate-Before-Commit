# Editorial Compression Report — v1.20.2

Baseline: v1.20.1 (`8f1a431`). Method: word count over `manuscript/main.tex` from
`\begin{abstract}` (identical measurement before/after; includes captions of the two inline
tables and section text, excludes preamble).

## Density

| metric | before | after | delta |
|---|---|---|---|
| main.tex words (from abstract) | 19,413 | 17,827 | **−1,586 (−8.2%)** |
| main.pdf pages | 32 | **30** | −2 |
| main_ieee.pdf pages | 24 | **22** | −2 |
| supplement.pdf pages | 24 | 24 | 0 |
| Table 9 caption (words) | 163 | ≈118 | −45 |
| Table 10 caption | 115 | ≈98 | −17 |
| Table 11 caption | 188 | ≈118 | −70 |

Within the mandated 8–12% band; hard cap 15% respected.

## Most-reduced sections

1. **§7 Limitations**: 1,805 → 1,230 words (−32%), restructured into five thematic blocks
   (external validity; learner/update scope; prevalence & acquisition cost; probe
   representativeness & information availability; statistical granularity & multiplicity).
   Every load-bearing limit retained (verified list below).
2. **§8 Conclusion**: 549 → 416 words (−24%); only the mandated numbers repeated (32 labels
   in the controlled point-gate setting; 93%/81%; 13 replays without net harm).
3. **§5.1 Five tiers**: ≈330 → ≈195 words (compressed to ~60%, hierarchy intact).
4. **§5.3**: forensic phrases removed or condensed ("first implementation…", "external
   review identified…", "an earlier version looked equivalent…", duplicated three-iteration
   narrative), Results-intro roadmap shortened, monitor/ensemble paragraphs tightened.
5. **§5.5**: six-replay history condensed (~430 → ~280 words); operational paragraph
   de-duplicated against the Table 11 caption.
6. **Intro**: contributions paragraph 330 → ~250 words; robustness-envelope sentence chain
   folded; §4 v1-history paragraph 200 → ~110 words.

## Material relocated or condensed (not deleted)

Registered-amendment histories, correction narratives and per-iteration accounts remain in
Supplement (§S2.4, §S2.6, §S2.7) and the registered notes; main text keeps one-line
transparency pointers. No scientific evidence removed.

## Load-bearing limits — all retained (verified)

no chronological net harm (principal external-validity limit); SVC-RBF fragility and
size-matched localization; balanced evaluation windows; inspected-flow acquisition cost not
measured/modeled (candidate batch, stratified probes, pipeline end to end); probe
representativeness assumption and empirical-Bernstein failure under strong within-probe
autocorrelation; no population-rate inference from 0/506 (clustering caveat verbatim);
prevalence overclaim retraction (π=0.01); Wednesday intra-day unresolved counterexample;
per-proposal vs lifetime guarantee distinction; hierarchical-model caveats (collinearity,
boundary variance, QK exception, failed scale transfer).

## Scientific figures — unchanged

All 164 scientific CSVs byte-identical to the v1.20.1 baseline (SHA-256 verified; 0 diffs,
0 new). Harm accounting 520/340/180/506/14/0; multiplicity 28 = 6/15/7, survivors 3/6,
13/15, 7/7, 0 fallbacks. No experimental runner executed.

## Claim-scope changes applied alongside (Block C/D)

C1 causal→leakage-free observed-data (all claim surfaces; Table 4 caption retitled; label
`tab:causal_probe` and the negation "not as a causal proof" retained; temporal
"causal-information availability" sense retained). C2 pooled-empirical vs stratified-formal
sentence. C3 cap-512 vs ≈578/580/579 realized labels (abstract compact form; §5.4; README).
C4 "realistic cost"→"incremental adjudication count under the evaluated protocol" +
not-an-acquisition-cost sentence. C5 conditional-on-proposal detector wording + imbalance
caveat. C6 "direct safeguard is candidate–incumbent validation" + formal-control sentence.
D1 first-evaluated operating point. D2 mechanism scoped to evaluated SVC-RBF (conclusion
sentence per mission). D3 hierarchical model as predictive support (already compliant).
D4 captions shortened. Guards: +17 audit checks (538 total) and one extended test module.
