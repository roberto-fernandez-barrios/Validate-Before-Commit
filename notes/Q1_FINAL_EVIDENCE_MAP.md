# Q1 FINAL EVIDENCE MAP

Audit of every evidence block against the locked thesis, before the manuscript reorganization.
No result is modified here; this note only fixes each block's function and placement.

**Locked thesis.** Drift detection and candidate promotion are different decisions. Before
attributing benefit or harm to an adaptive promotion policy, the challenger construction
process and the comparability of its evidence with the incumbent must be audited.
Incumbent-owned preprocessing and limited candidate evidence substantially amplified harmful
promotion in the controlled experiments. Once pipelines were self-contained and candidate
training size was matched nominally, no average promotion harm or average validation benefit
was detectable in the zero-drift control. Validation gates are conditional safeguards, not
universally beneficial defaults.

## Evidence table

| # | Claim | Evidence block | Datasets | Pipeline policy | Cand. size | Drift | Metric | Inferential status | Establishes | Does NOT establish | Class | Placement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Frozen incumbent-owned preprocessing amplified apparent promotion harm; mean full-drift harm does not persist under own pipelines (+7.21/+2.55/+1.03; interaction up to +5.98) | `symmetric_pipeline_dynamic_001` F1/F2 | CICIDS-PS, UNSW-Recon, ToN-IoT | frozen vs own | 512 | full+zero | BA (recall/FPR guardrails) | Registered confirmatory, Holm | Ownership is a major amplifier; original full-drift harm configuration-dependent | That ownership explains all promotion risk; that frozen policies are illegitimate | PRIMARY MECHANISM | Main §5.1 |
| 2 | Zero-drift promotion harm persists at 512/class for self-contained challengers (−1.74/−0.65/−0.38) | same, F4 | 3 benchmarks | own | 512 | zero | BA | Registered confirmatory, Holm | Residual mean harm at historical size | That re-estimation per se is harmful | PRIMARY MECHANISM (bridge) | Main §5.1→§5.2 |
| 3 | Candidate evidence size explains the residual zero-drift mean harm: at nominal 2,000/class parity naive≈never (CI90 in ±0.5, 3/3; size effect +1.89/+0.63/+0.23 Holm-sig; PortScan margin-sensitive at ±0.2) | `size_matched_own_transformer_001` F1/F2 | 3 benchmarks | own | 512 vs 2000 (nested) | zero | BA | Registered confirmatory, Holm + equivalence | ATTENUATION of mean harm via size | ELIMINATION; full evidence equivalence (nominal only); zero drift only; SVC-RBF only | PRIMARY MECHANISM | Main §5.2 |
| 4 | Registered outcome ATTENUATION (sign-rate criterion inconclusive; mean future value ≈0) | same, CLAIM_INTERPRETATION.json | 3 benchmarks | own | 2000 | zero | 5-window future value | Frozen outcome rules | Formal classification distinct from substantive reading | Absence of per-proposal risk; deployment probability | PRIMARY MECHANISM (qualifier) | Main §5.2 |
| 5 | Point/strict gates improve over naive in all six zero-drift comparisons at 512 (up to +1.68) | symmetric F4 | 3 benchmarks | own | 512 | zero | BA | Registered, Holm | Gate value under evidence asymmetry | Universal gate value | PRIMARY CONDITIONAL EFFECT | Main §5.3 |
| 6 | At nominal 2,000 parity, no detectable average gate benefit (all six <0.14, none Holm-sig; F4 interactions uniformly negative) | size-matched F3/F4 | 3 benchmarks | own | 2000 | zero | BA | Registered, Holm + equivalence | Conditional (not universal) gate value | "Validation unnecessary"; absence of value vs individual bad candidates/tail risk | PRIMARY CONDITIONAL EFFECT | Main §5.3 |
| 7 | Frozen-policy confirmatory core: naive harmful in ToN-IoT, gate rescues; detector-invariant (QK-ZZ) | v2 harness, seeds 104–133 | 3 benchmarks | frozen | 512 | ramps | BA | Registered confirmatory (historical diagnostic) | Gate value under frozen configuration | Transfer to own-transformer setting | HISTORICAL / SUPERSEDED as headline; retained as diagnostic | Main §5.5 (compact) + Supp S2.11 |
| 8 | Mild-drift matrix: healthy incumbent → naive harmful in all 3 benchmarks; gate meets tolerance | amendment 006 | 3 benchmarks | frozen | 512 | mild | BA | Registered follow-up | Incumbent health, not dataset, sorts outcomes | Own-transformer transfer | ROBUSTNESS / SENSITIVITY | Main §5.5 (brief) + Supp |
| 9 | Zero-drift frozen control: harm real; McNemar/reject-ties recover loss; well-specified monitor rarely fires | amendment 008 | 3 benchmarks | frozen | 512/2000 | zero | BA | Registered follow-up | Calibrated validator does nothing when nothing to gain | Own-transformer persistence (refuted by #3) | ROBUSTNESS + HISTORICAL (size part superseded) | Main §5.5 (brief) + Supp |
| 10 | Four-classifier controls: zero-drift harm sign general at 512; size-matching removes it for RF/LR/MLP; SVC-RBF persistence frozen-bound | amendments 009/012 | 3 benchmarks | frozen (+own via #3) | 512/2000 | zero/mild/full | BA | Registered follow-up | SVC-specificity of magnitude; sign generality at asymmetric budget | Harm generality at matched size | ROBUSTNESS / SENSITIVITY | Main §5.5 (brief) + Supp S1.6 |
| 11 | A/B ownership decomposition: scaling (not PCA) owns the effect; inversion under challenger-owned transformer | registered A/B, seeds 2001–2100 | 3 benchmarks | ownership randomized | matched blocks | static | BA | Registered follow-up, TOST | Mechanism = feature scaling under RBF | Universal mechanism beyond SVC-RBF | PRIMARY MECHANISM (support) | Main §5.5 (compact) |
| 12 | Chronological replays (13): no net harm of always-deploy vs never; gates pay premium on collapsed incumbents, win on healthy UNSW timelines; Wednesday unresolved counterexample | replays + chronological matrix, seeds 601–630 | CICIDS days, UNSW timeline | frozen | 512 | real time | BA (+acc) | Registered, BH-corrected block | External boundary: harmful promotion not observed chronologically; incumbent health governs trade-off | That harmful promotion is operationally frequent; a universal healthy-timeline law | EXTERNAL BOUNDARY | Main §5.4 |
| 13 | Observed-data (leakage-free) arm: gate implementable without simulator privileges; harm-regime rescue reproduces; UNSW below no-adapt at 64-flow windows | amendments 011–013 | 3 benchmarks | frozen | 512 | full/mild | accuracy/BA | Registered feasibility | Core decision transfers off oracle | Exact replica of core; size-matched transfer | OPERATIONAL FEASIBILITY | Main §5.5 (compact) + Supp S2.7 |
| 14 | VBC-SG family: probe-level false-superiority control; commit/reject/defer; lifetime spending; budget frontier non-vacuous from b=256 (93%/81%/68% of naive benefit at cap 512) | riskgates + budget frontier, seeds 501–530 | 3 benchmarks | frozen | 512 | zero/full | BA + labels + abstention | Registered follow-up, BH | Price of formal guarantees; guarantee ≠ future deployment | Necessity at matched size; math novelty; operational safety guarantee | FORMAL EXTENSION | Main §3 (compact) + §5.5; grids in Supp |
| 15 | Per-trigger mechanism: pre-trigger degradation predicts update value (r≈−0.7); detector score does not (within triggered decisions) | v2 per-trigger logs + hierarchical model | 3 benchmarks | frozen | 512 | ramps | Δ5 | Registered, clustered | Degradation–headroom account | Causal proof; universal law | PRIMARY MECHANISM (support) | Main §5.5 (compact) + Supp S1.1 |
| 16 | Quantum monitor (QK-ZZ/Pauli-XZ): detector family does not change conclusions; ~114× simulated cost | QK arms across core | 3 benchmarks | frozen | 512 | ramps | BA | Registered (invariance) | Detector-invariance of conclusions | Anything about quantum advantage | ROBUSTNESS / SENSITIVITY | Main §5.5 (one para) + Supp S1.2 |
| 17 | Acquisition yield: alert-enriched inspection cuts attack-label search 5–8×; uniform validation half preserved | operational e2e sim | CICIDS-PS, UNSW | frozen | 512 | ramps | inspected flows/attack label | Registered feasibility (bounded) | Discovery-cost pricing; not end-to-end deployment cost | End-to-end deployment evaluation; economic dominance | OPERATIONAL FEASIBILITY | Main §5.5 (compact) |
| 18 | Prevalence sensitivities: gate holds to π≈0.05; dissolves at 0.01; trigger starvation upstream problem | corrected probes + prevalence-lite | 3 benchmarks | frozen | 512 | ramps | BA | Registered correction (one retraction) | Bounded probe tolerance | Operational validation at extreme imbalance | ROBUSTNESS / SENSITIVITY | Main §5.5 (brief) + Supp S2.3 |
| 19 | Security guardrails: recall/FPR non-inferiority; one 512 strict cell fails recall NI (UNSW zero); all matched-size cells pass | symmetric + size-matched security CSVs | 3 benchmarks | own | 512/2000 | zero/full | recall, FPR | Registered guardrails | Safety language restrictions | Security improvement claims | ROBUSTNESS (guardrail) | Main §5.1/§5.2 (kept) |
| 20 | harmful@H accounting: 0/506 evaluable risk-gate commits harmful (clustered, descriptive); naive 39% | budget frontier logs | 3 benchmarks | frozen | 512 | all | H5 sign | Descriptive, cluster-caveated | Empirical harm-avoidance texture | Population rate bound | FORMAL EXTENSION (support) | Main §5.5 (one sentence) + Supp |
| 21 | Label/latency accounting: probe ~3% of gate's total bill; two-stage variant halves pipeline cost; staleness/corruption envelope | v2 extensions | 3 benchmarks | frozen | 512 | ramps | labels, BA | Registered | Cost decomposition of the decision | Label-efficiency of retraining pipeline | OPERATIONAL FEASIBILITY | Main §5.5 (brief) + Supp S5 |
| 22 | v1 exploratory study (regime taxonomy, +19.5…−4.6 span) | harness v1 | 3 benchmarks | frozen | 512 | ramps | BA | Exploratory (superseded where v2 exists) | Hypothesis generation | Any confirmatory claim | HISTORICAL / SUPERSEDED | Supp S1 only; one-line pointer in main |

## Abstract / intro / contributions / discussion / conclusion claim triage

| Current claim surface | Decision |
|---|---|
| Abstract chronology ("In our original experiments… A preregistered replication… A final control…") | REFRAME → thesis-first structure (problem → framework → design → R1 → R2 → R3 → R4 → conclusion), ≤5 numerals |
| Abstract: "at nominal 2,000-per-class sample-size parity … equivalent … ±0.5 CI90" | KEEP (one of the ≤5 numeric facts) |
| Abstract: full list of nine effect sizes | REMOVE AS DUPLICATE (tables carry them) |
| Abstract: ATTENUATION sentence | KEEP (exactly one sentence; guard-pinned) |
| Intro paragraph narrating detector literature then pivoting | REFRAME: open from the promotion-decision thesis |
| Contribution list (3 items) | REFRAME → 4 contributions per plan (C1 decomposition, C2 staged construction study, C3 conditional validation, C4 boundary/formal analyses) |
| "the paper's algorithmic contribution is that family together with the frontier" | REFRAME → formal option positioning (C4), no algorithmic-breakthrough language |
| §5.1-first ordering (historical diagnostic leads Results) | MOVE: mechanism results lead; diagnostic becomes compact block in extensions subsection (heading string preserved) |
| "The trajectory of this paper is itself a result" (Discussion Finding 3) | REFRAME → methodology contribution stated once, without self-referential trajectory narration |
| Genealogy phrases in body ("answering it took three registered iterations", "amendment 004/008/012" call-outs) | MOVE TO SUPPLEMENT / REFRAME to design language; supplement keeps the full account |
| "Negative results improve adaptive-system evaluation" | REFRAME into Discussion Q1/Q4 answers |
| Practitioner guidance (i)–(iii) | KEEP, REFRAME to 5-step conditional policy per plan |
| Conclusion | REFRAME per plan's closing paragraph (all pinned phrases preserved) |
| Any "gate every adaptation", "universally required", "harm eliminated" | FORBIDDEN (already absent; guards keep them out) |
| "Retraining is generally harmful" in any form | FORBIDDEN (not present; keep out) |
| Chronological no-net-harm boundary | KEEP prominent (main §5.4 + abstract + conclusion) |

## Hierarchy rule application (secondary content)

- VBC-SG: qualifies via C (quantifies cost of decision process) → compact method subsection + compact results block; grids/variants stay in Supp.
- Observed-data: qualifies via E (reproducibility/safety guardrail — removes simulator privilege) → compact synthesis.
- Chronological replays: qualifies via B (external boundary) → main §5.4, full per-replay detail in Supp.
- Acquisition yield/prevalence: qualifies via C → operational synthesis, tables stay.
- Mild drift: qualifies via D (perturbation test of conclusion) → brief.
- Quantum monitor: qualifies via D (detector invariance) → one paragraph.
- Classifier controls: qualifies via D → brief.
- Two-stage gate / ensemble / label-free estimators: qualifies via C/D → condensed mentions, detail in Supp.
- v1 exploratory: fails A–E for main body → pointer only.
