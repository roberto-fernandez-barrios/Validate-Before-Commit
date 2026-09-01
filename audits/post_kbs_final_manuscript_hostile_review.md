# Hostile final manuscript review — post-KBS integration (read-only self-review before commit)

Date: 2026-09-01. Branch `post-kbs-hardening`, base `8285b04`. Object: the rebuilt
`manuscript/main.tex` (cas-sc, 30 pp.), `manuscript/supplement.tex` (45 pp.), the IEEE port
(23 pp.), the CSV-generated tables (`src/analysis/make_post_kbs_final_tables.py`) and the
updated docs. Every attack below is answered only with what the current sealed/confirmatory
evidence supports; where the manuscript is weaker than a referee would like, the weakness is
recorded as such rather than argued away.

Validation state at review time: claim audit 632/632; `verify_results_manifest` 185/185 sealed
CSVs byte-identical (22 unpinned post-v1.22 extras, warn-only by design); main/supplement/IEEE
compile with 0 undefined references and 0 undefined citations; abstract 212 words; guard suite
run under the paper2 environment (final count recorded in the commit report); numeric-token
diff against `8285b04` accounted below.

## 1. Novelty

**Attack.** Champion–challenger evaluation, validation gates, label-efficient model comparison
and "retrain only when it pays" are all published. What is new?

**Manuscript.** Related Work now says exactly that ("this paper claims none of them as novel")
and states the contribution as an *experimentally supported decomposition*: two preregistered
controls show that upstream candidate construction and evidence conditions reverse both the
apparent harm of promotion and the apparent ordering of update policies (S4 fires for ATC and
the ensemble; 15/15 resolved method×size interactions negative). No "no prior work" claim is
made; the closest formulations are positioned conceptually in Table 1 with an explicit
statement that no head-to-head superiority is claimed against them.

**Residual weakness.** The novelty is methodological (an evaluation-discipline result on three
benchmarks with one primary learner). A referee who wants a new algorithm will not find one;
the paper says so. *Defended, honestly scoped.*

## 2. SoTA / external comparison

**Attack.** KBS R1: "no results comparison with SoTA".

**Manuscript.** §5.6 + Table `tab:common_harness` + Supplement S10: a registered,
pre-implementation-frozen comparison on bit-identical streams at nominal 2,000/class parity
(seeds 5001–5030, 96 arms) of ATC, DoC, calibrated ensemble, replay, river-DDM, river-ADWIN
against never/naive/point/strict, with per-cell magnitude-aware classification, a 512/class
sensitivity block and documented budgets. Nothing is called SoTA; the section is labelled
"not a state-of-the-art ranking". The exploratory DoC-beats-gate reading is reported together
with its confirmatory reversal.

**Residual weakness.** ATC on PortScan full drift is UNRESOLVED (−0.65), so the strongest
published competitor's status is "compatible on 2/3, unresolved on 1/3"; the manuscript states
it that way and does not round it up. *Substantially answered for generic/reference methods.*

## 3. Readability

**Attack.** KBS R1: "not well written, hard to read".

**Manuscript.** One central problem, three contributions (C1–C3) with the supporting
instruments explicitly demoted; a synthesis table opens the Results; each Results subsection
carries numbered findings; the abstract has no caveat chain, no VBC-SG, no protocol history.
VBC-SG is now a single subsection of §3 plus one paragraph of §5.7.

**Residual weakness.** §3.5 and §5.7 remain dense (the formal guarantee/non-guarantee pair and
the chronological price paragraph are long by necessity); §4.2 carries three registered
designs. Page count 30 (cas-sc) is above the previous 28 because two registered blocks were
added. *Improved; density in §3.5/§5.7 is the remaining readability cost.*

## 4. Exchangeability objection

**Attack.** The zero-drift size control is null by construction: a 2,000/class challenger drawn
from the incumbent's own pools at severity 0 is an exchangeable re-draw of the incumbent.

**Manuscript.** Stated in the design section itself (§4.2.2 "near-exchangeable re-draw …
near-zero mean effects are the outcome expected of a correct implementation") and repeated in
§5.3/§5.4; the ATTENUATION label is explained as a property of the sign-rate rule under
exchangeability, not as directional residual harm. *Conceded in the text, not hidden.*

## 5. Does B2 answer it?

**Attack.** Show me a regime where the challenger is *not* exchangeable with the incumbent.

**Manuscript.** §5.4: under full progressive drift the nested 512→2,000 intervention (same
proposal-time mixture, prefix-hash and severity equality verified at 707/707 coupled proposals)
yields +0.82 [0.67, 0.98] / +1.66 [1.51, 1.81] / +1.00 [0.60, 1.39], Holm p≈3×10⁻⁵, all above
the +0.5 margin — HOMOGENEOUS-SIZE BENEFIT. The text claims it "substantially weakens" the
objection, not that it eliminates it. It also resolves the frozen-transformer precedent in which
size-matching deepened harm (S1.5), which is the one place the old manuscript's scope was
genuinely exposed.

**Residual weakness.** B2 is a two-point dose (512 vs 2,000) under one drift construction with
one learner. *Answered within its stated domain.*

## 6. Candidate-size causal overreach

**Attack.** "More data helps" is being generalized.

**Manuscript.** Explicit non-claims in §5.4(2), §6 Q1 and §7: no effective-information parity,
no universal monotonic benefit, no causal generality beyond the nested pool-based design, no
claim that larger training windows help arbitrary adaptive systems, nominal rows drawn with
replacement remain nominal. Guard test `test_b2_claim_guards` pins these sentences. *Defended.*

## 7. Validation oversold

**Attack.** This is still a paper selling a gate.

**Manuscript.** The gate's average value is reported as zero at parity in *both* regimes
(0/6 at zero drift, 0/6 under drift) with a resolved strict-gate cost (−0.34) and a guardrail
failure; §6 Q2 states "we do not call validation necessary, generally safer, superior, or the
recommended default"; the operational reading ("validate when upstream comparability cannot
be established cheaply or when tail-risk/governance requirements justify") is labelled as an
extrapolation beyond the fixed-policy evidence. VBC-SG's chronological conservatism (0–9 % of
recovery retained) is kept at full prominence. Guard tests ban the universal phrasings.

**Residual weakness.** The 512-side gate results (6/6 at zero drift, +0.46 on ToN full) are
real and could be read as advocacy; the text ties each to evidence asymmetry. *Not oversold.*

## 8. Unfair comparison against ATC/DoC/DDM/ADWIN

**Attack.** Different label budgets, Platt calibration, a 512-row validation sample, monitor
labels — the deck is stacked.

**Manuscript.** Budgets are reported and explicitly not equalized (Table S33; §7); ATC/DoC's
training-time validation sample is documented analytically; DDM/ADWIN's 800 monitoring labels
are named in the table; fidelity tests check each policy against its reference definition and
that Platt calibration leaves hard predictions unchanged; "compatibility … not a demonstration
of equality" is stated. The 512/class block shows the same methods *winning* where naive is
harmful, so the harness is not structurally hostile to label-free rules.

**Residual weakness.** ADWIN barely fires in this harness (a reference-implementation trigger
with a fixed δ on 8 labels/window); its MATERIAL COST is partly "did not adapt", and the text
says "barely at all" only in §6. *Fair by construction; ADWIN result should be read as
under-triggering, which the text could state one sentence earlier — minor textual.*

## 9. End-to-end adaptive-NIDS baseline absence

**Attack.** Still no reproduced adaptive-NIDS system.

**Manuscript.** Stated three times (§4.4, §5.6, §7) with the frozen reasons (per-sample
rejection / continuous adaptation systems decide something else; cost-schedule formulations
lack inputs) and the explicit sentence that this absence is "stated, not used to imply
superiority"; §7 says a reviewer asking for such a reproduction "is asking for something this
design does not provide". *Permanent limitation, transparently owned.*

## 10. Artifact reproducibility

**Attack.** Are the new numbers reproducible and pinned?

**Manuscript / artifact.** Every B2/B1 number in the main text and the new tables is generated
from `results/tables/post_kbs_*` CSVs by a committed script (`make_post_kbs_final_tables.py`)
and re-derived by guard tests; protocols, amendment, configs and analysis scripts were
committed before implementation/execution (reachability recorded in
`audits/protocol_commit_reachability.csv` and the checkpoints); per-arm `run_config.json`
records clean-tree authorized-mode execution. The 185 sealed CSVs are byte-identical.

**Residual weakness.** The 22 post-v1.22 CSVs are *not* manifest-pinned and the deposit DOI
still points to v1.22.0 — the paper says "pending a subsequent sealed release". Until that
release exists, a reader of the archived deposit cannot verify B1/B2 from the DOI alone. *Real,
declared, out of scope for this phase by instruction.*

## 11. Chronological external validity

**Attack.** Thirteen replays on two datasets, no ToN-IoT, strided sampling, no prevalence.

**Manuscript.** §5.7 keeps all of it: no net harm observed, no prevalence estimate, no ToN-IoT
analogue, the registered family "structurally easy to satisfy" where incumbents collapse, the
unresolved Wednesday counterexample, VBC-SG retaining 0–9 % of recovery. B1/B2 were not run on
chronological streams and the text does not pretend otherwise. *Bounded correctly; the external
tier remains the paper's weakest evidence tier and is labelled as such.*

## 12. Statistical interpretation

**Attack.** Non-rejection read as equality; multiplicity; seeds as units; descriptive cells.

**Manuscript.** COMPATIBLE is defined as CI90-within-±0.5 and is repeatedly separated from
equality; UNRESOLVED cells are named (ATC ps_full; DoC ps_zero; DDM/ADWIN ps_zero); anchor
contrasts in B1 are descriptive by amendment and marked so; Holm within family everywhere,
"no conclusion depends on the correction"; the seed is the inferential unit; commits are never
treated as independent trials; the synthesis table labels every descriptive cell and every
"not evaluated" cell. The PortScan zero-drift margin-dependence (CI90 upper 0.494) is retained.

**Residual weakness.** The synthesis table juxtaposes cells from four seed blocks; it is a map,
and its caption says so, but a hostile reader can still eyeball cross-block differences. *Sound.*

## Numeric-token accounting (main.tex, `8285b04` → final)

Final counts after the fixes below: 92 removed, 110 introduced. Removed tokens fall into: (a) the historical compact Block-I/II/III table relocated verbatim
to Supplement S2.12 (`table_baselines_full.tex`, sealed CSVs unchanged) — all ±x.xx gains of
naive/sliding/ensemble/DDM/ADWIN/point/two-stage/McNemar/v1 rows, plus the "1.86/4.64" ATC/DoC
PortScan losses of the exploratory block; (b) chronological detail condensed into §5.7 and
retained in `tab:chronological_q1` and Supplement S2.6 (+11.5/+14.8, +27.6/+35.3, +10.76/+8.35,
+6.92/+7.64, +7.33, +0.16 [−0.31, 0.63], +4.19/+1.23, +0.40 [0.09, 0.74], 82.3 %, 84.7 %,
49–59 %); (c) exploratory intro figures dropped with the intro rewrite (+19/−4, r≈−0.8…−0.9;
remain in S1.1); (d) the reject-ties commit counts (104→14/20/5; remain in S2.12); (e)
formatting/citation-year/ORCID digit artifacts (3.5, 1.08, 017, 021, 022, 12., 16, …); (f)
count reductions of tokens still present (32, 81 %, 0–9 %, −5.0/−15.1, 1.64, 2.43, 0.79). Two
values initially dropped were restored for fidelity (−3.33 FPR improvement; 5–20-window
candidate latency). Introduced tokens are exclusively: B2 values from
`post_kbs_size_matched_drift_001` (G1/G2/G3/G4 effects and CIs, +0.86 FPR, +0.46 [0.09, 0.88],
707 coupled proposals, seeds 6001–6030, 21 arms); B1 values from
`post_kbs_common_harness_baselines_001` (anchor, PF1–PF3, SF4 effects, 15 interactions, +9.5
FPR, 96 arms, seeds 5001–5030, 800 monitoring labels, 512-row validation); and pre-existing
design constants re-typeset (50/30/20, 100 windows, 1,488). No sealed historical value changed.

## Minor textual fixes applied during this review (before commit)

1. Restored the pinned phrase "price of that conservatism" (§5.7).
2. Restored the sealed chronological wording "no-adaptation BA 49–72 %" (an intermediate edit had
   substituted the 49–59 % range of a different sentence).
3. Restored two fidelity values dropped in the rewrite (−3.33; 5–20 windows).
4. Table 6 (B2) column headers shortened and set in footnotesize so the table fits the text width.
5. ADWIN's MATERIAL COST is now qualified as under-triggering at the point where it is reported
   (§5.6), not only in the Discussion (attack 8).

## Verdict

**READY WITH MINOR TEXTUAL FIXES** — the fixes listed above are applied; the remaining
weaknesses (dense §3.5/§5.7, unpinned post-v1.22 CSVs pending release, ADWIN under-triggering
phrasing, two-point size dose, no end-to-end system) are declared in the manuscript and are not
textual defects fixable from current evidence. Commit authorized under the phase instructions
once the rerun (audit, hashes, build, guard suite) is green.
