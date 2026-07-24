# Q1 FINAL CLAIM AUDIT

Every strong claim across the title, abstract, highlights, introduction, contributions,
results, discussion, conclusion and graphical abstract of the rebuilt manuscript, with its
support, scope, qualification and status. All rows terminate in PASS. No scientific result
was recomputed; every number is quoted from a sealed CSV verified by `verify_results_manifest`
(185/185) and cross-checked by `audit_paper2_claims` (630/630).

| # | Surface | Claim | Supporting artifact | Scope | Qualification | Status |
|---|---|---|---|---|---|---|
| 1 | Title | "Candidate Comparability Before Promotion: Conditional Validation" | whole-paper thesis | framing | Validate Before Commit retained as framework/repo name only | PASS |
| 2 | Abstract | Incumbent-owned frozen preprocessing strongly amplified apparent promotion harm; own pipelines remove mean full-drift harm | `symmetric_pipeline_dynamic_001` F1/F2 | 3 benchmarks, SVC-RBF | "amplified", not "sole cause"; configuration-dependent | PASS |
| 3 | Abstract | At nominal 2,000/class parity, always-deploy mean-equivalent to never within ±0.5; gates no detectable average benefit | `size_matched_own_transformer_001` F1/F3, equivalence.csv | zero drift, own transformer | nominal size only; PortScan margin-sensitive at ±0.2 | PASS |
| 4 | Abstract | Registered outcome ATTENUATION; sign-based future-value criterion inconclusive around near-zero mean | CLAIM_INTERPRETATION.json | frozen outcome rules | not ELIMINATION; formal vs substantive kept distinct | PASS |
| 5 | Abstract | Thirteen chronological replays show no net harm from always deploying | chronological matrix, 601–630 | real time-ordered streams | boundary, not prevalence claim | PASS |
| 6 | Abstract | Validation is a conditional safeguard, not a universal requirement | synthesis of R1–R4 | evaluated settings | "conditional", never "unnecessary" | PASS |
| 7 | Highlights | "Drift alarms propose challengers; they do not establish challenger superiority" | Fig. 1, §3.1 | framing | — | PASS |
| 8 | Highlights | "Gates helped under limited candidate evidence, not under the size-matched control" | §5.3 F3/F4 | zero drift | no average benefit ≠ no value (stated in §5.3) | PASS |
| 9 | Contributions | C1 candidate-governance decomposition (6 stages) | Fig. 1 | conceptual | not claimed novel per stage individually | PASS |
| 10 | Contributions | C2 staged controlled study: preprocessing ownership + candidate size dominate promotion outcome | §5.1, §5.2 | 3 benchmarks | sequential-but-preregistered, declared once | PASS |
| 11 | Contributions | C3 conditional (not universal) average value of validation | §5.3 | zero-drift control | — | PASS |
| 12 | Contributions | C4 formal/chronological/operational boundary analyses | §3.4, §5.4, §5.5 | frozen policy | "formal option", no math-novelty claim | PASS |
| 13 | Results §5.1 | Own-transformer always-deploy beneficial in all 3 full-drift regimes (+7.21/+2.55/+1.03) | paired_contrasts.csv (SP7-pinned) | full drift, own | Holm-significant | PASS |
| 14 | Results §5.1 | Ownership interaction up to +5.98 on ToN-IoT | paired_contrasts.csv | full/zero drift | "major amplifier — not complete explanation" | PASS |
| 15 | Results §5.1 | Residual zero-drift 512 harm (−1.74/−0.65/−0.38) | paired_contrasts.csv | zero drift, 512 | ToN sub-material, significant, not equivalent | PASS |
| 16 | Results §5.2 | Size effect +1.89/+0.63/+0.23 Holm-significant everywhere | multiplicity.csv (P2-pinned) | zero drift | mirror of 512 harm | PASS |
| 17 | Results §5.2 | naive-2000 ≈ never, CI90 in ±0.5 in 3/3 (+0.19/−0.02/−0.01) | equivalence.csv (P1-pinned) | zero drift | margin-dependent; PortScan tight (0.49) | PASS |
| 18 | Results §5.3 | 512: point/strict improve over naive in all six zero-drift comparisons (up to +1.68) | F4 CSV | zero drift, 512 | "improve over naive", scoped | PASS |
| 19 | Results §5.3 | 2,000: all six gate contrasts <0.14, none Holm-sig, F4 uniformly negative | F3/F4 CSV (P3-pinned) | zero drift, 2,000 | "no average benefit ≠ no value" stated | PASS |
| 20 | Results §5.4 | Net harm unobserved on every chronological stream; incumbent health sorts the trade-off | chronological_q1 CSV | 13 replays | Wednesday = unresolved counterexample (stated) | PASS |
| 21 | Results §5.5 | Frozen-policy diagnostic: gate rescues ToN harm, detector-invariant | v2 confirmatory CSV | frozen policy | re-captioned "historical frozen-policy diagnostic" | PASS |
| 22 | Results §5.5 | Degradation predicts update value (r≈−0.7); detector score does not | per-trigger logs, hierarchical model | within triggered decisions | "no consistent signal, not provably none" | PASS |
| 23 | Results §5.5 | Budget frontier: 93% (pooled) / 81% (VBC-SG-Cohort stratified) at cap 512 | budget_frontier CSV (BH block) | frozen policy | 93% marked "approximate pooled"; 81% stratified stated alongside | PASS |
| 24 | Results §5.5 | 0/506 evaluable risk-gate commits harmful | frontier logs | descriptive | clustered, "not 506 independent Bernoulli trials"; "not eliminates" | PASS |
| 25 | Results §5.5 | Alert-enriched inspection cuts attack-label search 5–8× | operational_e2e CSV | acquisition-yield sim | not end-to-end deployment cost | PASS |
| 26 | Discussion | Q1–Q4 (comparability / when validation helps / when it delays / operational implications) | §5.1–5.5 | evaluated settings | four-question structure, no trajectory narration | PASS |
| 27 | Discussion | Conditional operating policy (5 steps) | synthesis | recommendation | no "gate every adaptation" | PASS |
| 28 | Conclusion | Size matching neutralizes mean zero-drift harm; validation conditional; incumbent health governs | §5.2, §5.3, §5.4 | evaluated settings | ATTENUATION kept; formal/substantive distinct | PASS |
| 29 | Graphical abstract | Four messages: trigger≠superiority; construction/size alter outcome; validation conditional; incumbent health sets trade-off | Fig content | — | "ZERO-DRIFT CONTROL", "nominal size parity", no universal rule | PASS |

## Forbidden-claim negative checks (all confirmed absent by audit + tests)

- ATTENUATION never glossed as ELIMINATION / near-elimination / residual-mean-harm (`v122sm N4/N10/P4`, `v1221 A`).
- "no average benefit" never stated as "no value" / "validation unnecessary" (`v122sm N2/N3`).
- nominal size matching never equated with full evidence comparability (`v1221 T` nominal-vs-effective caveat present).
- probe-superiority guarantee never stated as future-deployment guarantee (`v121 D`, Limitations).
- controlled harm never generalized to operational prevalence (`v1221 C`, chronological boundary present).
- frozen-policy full-drift harm never transferred to own-transformer setting (`v121sp SP1/SP5`).
- VBC-SG never presented as fundamental mathematical innovation (`sec:riskgates` text; "no claim of fundamental mathematical novelty").
- no "universally required/beneficial", no "gate every adaptation", no "harm eliminated", no "manufacture(d)", no "fair challenger" (`v122sm N3`, `v1222 W`).
- fraud/spam/maintenance named only as expected transfer, "evidence confined to network-security benchmarks".

## Verdict

All 29 strong claims PASS; all negative checks confirmed. The manuscript claims nothing
stronger than the sealed evidence supports.
