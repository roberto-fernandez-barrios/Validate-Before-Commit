# FINAL KBS NARRATIVE REBUILD CHECKPOINT

## A. Baseline

- **Source branch:** `main`
- **Source commit:** `1e0c72ff02f79b0b6f9378805e6fdc31e62178a8` (v1.22.2, "Stamp v1.22.2 final artifact manifest")
- **Work branch:** `editorial/q1-final-narrative-rebuild`
- **Scientific result version:** v1.22.0 sealed science (`43d9c25`), editorially scoped through v1.22.2. Unchanged by this phase.
- **Size-matched outcome:** ATTENUATION (`size_matched_own_transformer_001/CLAIM_INTERPRETATION.json`, follow_up_authorized=false).
- **Initial pages / words:** main 33 pp / 14,679 body words; IEEE 25 pp / 14,497; supplement 30 pp / 6,535. Abstract ≈285 words.
- **Initial gates (all green at baseline):** pytest 135 passed; audit all PASS; verify-hashes 185/185.

## B. Final thesis

Drift detection and candidate promotion are different decisions. Before attributing benefit or
harm to an adaptive promotion policy, the challenger construction process and the comparability
of its evidence with the incumbent must be audited. Incumbent-owned preprocessing and limited
candidate evidence substantially amplified harmful promotion in the controlled experiments; once
pipelines were self-contained and candidate training size was matched nominally, no average
promotion harm or average validation benefit was detectable in the zero-drift control. Validation
gates are conditional safeguards, not universally beneficial defaults.

- **Selected title:** *Candidate Comparability Before Promotion: Conditional Validation in Adaptive Network Intrusion Detection.*
- **Rationale:** Of the three candidate titles, this one names the paper's actual pivot (comparability precedes promotion) and its actual verdict (validation is conditional) without asserting that validating is the main conclusion. The two alternatives ("Candidate Construction Before Promotion: When Validation Gates Help…" and "Candidate Comparability and Conditional Validation for Adaptive Model Promotion…") were rejected: the first foregrounds "when gates help" (over-weights validation), and the second is longer without adding precision. *Validate Before Commit* is retained only as the framework/repository/gate-family name, never in the title, per the instruction not to keep it for brand continuity.

## C. Structural changes

- **Old structure (Results order):** 5.1 historical frozen diagnostic → 5.2 symmetric replication → 5.3 size-matched → 5.4 v1 summary → 5.5 confirmatory/observed-data → 5.6 risk-controlled governance → 5.7 operational & chronological.
- **New structure:** §1 Introduction (thesis-first) · §2 Related work · §3 Candidate promotion as a decision pipeline (pipeline figure, gates, VBC-SG as formal option) · §4 Experimental design (datasets, construction policies, promotion policies, outcomes/inference) · §5 Results: **5.1 preprocessing ownership → 5.2 candidate evidence size → 5.3 conditional value of validation → 5.4 chronological external boundary → 5.5 mechanism/formal/operational extensions** (led by an evidence-map table) · §6 Discussion (four questions + 5-step conditional policy) · §7 Limitations · §8 Conclusion.
- **Sections condensed:** frozen-policy diagnostic (was §5.1 headline → compact block in §5.5, heading string preserved); mechanism/per-trigger, downstream/monitors/update-rules, observed-data, mild-drift, classifier controls, A/B ownership, VBC-SG frontier, prevalence, acquisition — each reduced to question + main finding + scope under §5.5, full grids left in Supplement; cost-sensitive reading, VBC-SG guarantee prose, and Limitations paragraphs tightened.
- **Sections moved/relegated:** amendment-by-amendment genealogy and per-iteration accounts kept in Supplement (S2.7 etc.); v1 exploratory study reduced to a one-paragraph pointer (full account Supplement S1).
- **Sections retained in main body:** chronological replays (external boundary), observed-data synthesis, VBC-SG compact method+result, acquisition-yield synthesis, quantum-monitor invariance, classifier controls, security guardrails.
- **New display items:** Figure 1 (decision pipeline, `docs/img/fig_pipeline.png`); Table (evidence blocks at a glance).

## D. Primary evidence (as presented)

1. **Preprocessing ownership (§5.1):** own pipelines remove mean full-drift harm (+7.21/+2.55/+1.03, Holm-sig); ownership interaction up to +5.98 on ToN-IoT; residual 512 zero-drift harm (−1.74/−0.65/−0.38). "Amplified by preprocessing ownership", configuration-dependent, not sole cause.
2. **Candidate evidence size (§5.2):** size effect +1.89/+0.63/+0.23 (Holm-sig); naive-2000 ≈ never, CI90 in ±0.5 in 3/3 (+0.19/−0.02/−0.01); PortScan margin-sensitive at ±0.2. Registered outcome ATTENUATION; formal classification and substantive reading kept distinct.
3. **Conditional gate value (§5.3):** point/strict help in all six zero-drift 512 comparisons (up to +1.68); at 2,000 all six contrasts <0.14, none Holm-sig, F4 uniformly negative. "No average benefit ≠ no value" stated explicitly.
4. **Chronological boundary (§5.4):** net harm unobserved on all thirteen replays; incumbent health sorts the trade-off; Wednesday intra-day split reported as an unresolved counterexample.

## E. Secondary evidence retained

| Block | Main placement | Supplement | Scientific purpose |
|---|---|---|---|
| VBC-SG (family, budget frontier) | §3.4 method + §5.5 compact result | S2.8/S2.9, grids/variants | Prices the cost of formal guarantees (rule C); non-vacuous from b=256 |
| Observed-data arm | §5.5 synthesis | S2.7 per-iteration | Removes simulator privilege (rule E); decision implementable leakage-free |
| Mild drift | §5.5 brief | S1.6 | Perturbation test (rule D): harm is incumbent-health, not dataset |
| Acquisition yield | §5.5 synthesis + table | — | Prices attack-label discovery (rule C); not end-to-end deployment |
| Prevalence sensitivities | §5.5 brief | S2.3 | Bounds probe tolerance (rule D); starved trigger is upstream problem |
| Quantum monitor | §5.5 one paragraph + Q4 | S1.2 | Detector-invariance (rule D); negative quantum-advantage result |
| Classifier controls | §5.5 synthesis | S1.5/S1.6 | SVC-specificity of magnitude (rule D) |
| Security guardrails | §5.1/§5.2 (kept) | S7/S8 | Recall/FPR non-inferiority (rule E); one 512 cell fails, reported |

## F. Claim corrections

- **Overclaims removed:** none newly introduced; the rebuild carries forward every v1.22.2 scoping. Genealogy phrasing ("after discovering", "to address this objection", "the hostile review", "the revised protocol", "the earlier harness", "subsequently corrected") confirmed absent from the main body.
- **Terminology corrected:** "artifact" reading of the original harm replaced by "configuration-dependent and strongly amplified by incumbent-owned preprocessing"; "the trajectory of this paper is itself a result" (self-referential) replaced by the four-question Discussion; contribution list reframed from 3 to 4 (decomposition / staged study / conditional validation / boundary analyses).
- **Causal claims narrowed:** ownership stated as "major amplifier — not a complete explanation"; size as "nominal" parity with the temporal-coverage/diversity/effective-sample caveat.
- **Generalizations removed:** fraud/spam/maintenance named only as expected transfer; "evidence confined to network-security benchmarks."
- **Guarantees delimited:** VBC-SG = "a formal option… no claim of fundamental mathematical novelty"; probe-superiority ≠ future-deployment guarantee; "zero observed harmful commits" ≠ "eliminates".

## G. Compression

| Metric | Before | After | Δ |
|---|---|---|---|
| Main body prose words | 14,679 | 13,210 | −10.0% net |
| Main pages | 33 | 32 | −1 |
| IEEE pages | 25 | 24 | −1 |
| Supplement pages | 30 | 30 | 0 |
| Abstract words | ≈285 | 221 | −22% |
| Main figures | 1 (+GA) | 2 (+GA) | +1 (pipeline) |
| Main inline tables | 1 | 2 | +1 (evidence map) |

Net main-body reduction is 10.0%; gross prose removal is larger (~13–14%) but partly offset by
four deliberately added structural aids (the decision-pipeline figure, the evidence-map table, the
four-question Discussion and the five-step conditional policy), which the plan's hierarchy rule
favours. Reduction came from removing amendment genealogy, consolidating the ten §5.5 extension
blocks into question/finding/scope form, tightening the VBC-SG guarantee prose and the cost-
sensitive derivation, and compressing repeated limitations — not from cutting methodological
transparency of the core (which the guard suite protects verbatim).

## H. Artifact consistency

- **Title:** updated on main.tex, main_ieee.tex, supplement.tex, README.md, CITATION.cff, .zenodo.json (VBC retained as framework name).
- **Abstract:** rewritten (221 words, thesis-first, 5 numeric facts) on main + IEEE.
- **Highlights:** five thesis-first bullets, all ≤85 chars.
- **Graphical abstract:** four-message revision (`make_paper2_graphical_abstract_final.py` + regenerated PNG); keeps "ZERO-DRIFT CONTROL", "nominal size parity", "0.5".
- **README / metadata:** conditional recommendation, zero-drift scope, nominal-parity terminology all retained.
- **Guards:** title guards additively retired the v1.22 title (audit `finalseal T4`, test `V122_TITLE_FRAGMENT`), mirroring the v1.21→v1.22 pattern.

## I. Validation

- **PDF build:** main 32 pp, supplement 30 pp, IEEE 24 pp — all 0 undefined refs/citations. Figure 1 on main p.5 / IEEE p.2; per-trigger figure main p.19. Latency and evidence-map tables span both IEEE columns; algorithm listing spans both IEEE columns. Residual overfull boxes: two pre-existing CAS-template artifacts (`\maketitle` 117pt; graphicalabstract strip 9.7pt), both present at baseline and unrelated to this rebuild; IEEE 0 overfull.
- **pytest:** 135 passed.
- **audit:** 630/630 checks pass.
- **verify-hashes:** 185/185 pinned CSVs match; 0 unpinned extras.
- **Manifests unchanged:** `results/final_manifest.json`, sealed CSV manifests, `MANIFEST.sha256` untouched.
- **Raw unchanged:** `results/raw/**` untouched; no analysis re-run; no result regenerated (graphical-abstract and pipeline PNGs are editorial figures, not result data).
- **Orphan status:** no orphaned result directories; no accidental regeneration.
- **Working tree:** clean except the two pre-existing untracked files left untouched by instruction — `PLAN_Q1_DEFINITIVO_VBC.md` (this phase's plan) and `notes/recovered_run_q1_faseC.py.txt`.
- **Processes:** no background processes.

## J. Remaining submission risks (editorial only)

1. Net main-body compression (10%) sits below the 15–20% orientation target; the shortfall is a deliberate trade for the added pipeline figure, evidence-map table and structured Discussion. A human editor could push further by relocating the multiplicity paragraph or the two-stage-gate detail to the Supplement, but every candidate cut touches a guard-pinned phrase and was left intact.
2. The Paper 1 reference (`fernandez_paper1`) remains a companion-study citation, unchanged per instruction (not a blocker).
3. Bibliography style/leading is tuned to hold 32 pages under the CAS class; KBS retypesets on acceptance.

## K. Final verdict

**READY FOR HUMAN REVIEW AND KBS SUBMISSION.**

The main paper now opens from its conclusion, is organized around the candidate-governance
decomposition, presents the two construction mechanisms and the conditional value of validation
as its spine, keeps the chronological no-net-harm boundary prominent, distinguishes mean effect
from per-proposal and future risk, retains ATTENUATION without reinterpretation, positions VBC-SG
as a priced formal option rather than the central result, and reproduces bit-for-bit from the
sealed artifact (135 tests, 630 audit checks, 185 hashes). No experiment was run, no scientific
result, seed, margin or registered outcome was changed, and no sealed manifest or raw result was
touched.
