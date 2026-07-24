# KBS FINAL FOCUS CUT CHECKPOINT

## A. Baseline

- **Branch:** `editorial/kbs-final-focus-cut` (from `main` @ `49ade7fcb3efc185e94f7f53ba0557caf7480dbc`).
- **Source version:** v1.22.3 (sealing tag `v1.22.3` → `3fbe1e6`, unmoved).
- **Baseline pages:** main 32, supplement 30, IEEE 24.
- **Baseline words:** main body 13,210; abstract 221.
- **Baseline main tables:** 13 `\input` + 2 in-body; figures 2 + graphical abstract.
- **Baseline gates:** pytest 135, audit 630/630, hashes 185/185 (all green).

## B. Scientific invariants (confirmed unchanged)

- **Datasets, experiments, results, seeds, margins, families, estimands, registered outcomes:** unchanged.
- **ATTENUATION:** preserved; no ELIMINATION-as-outcome string introduced.
- **`results/raw/**` and `results/tables/MANIFEST.sha256`:** byte-identical to the branch base (`git diff 49ade7f HEAD -- results/` is empty).
- **`results/final_manifest.json`:** untouched this phase (not regenerated, per rule).
- **Science DOI `10.5281/zenodo.21517899`, concept DOI `10.5281/zenodo.21322256`, v1.22.3 version DOI `10.5281/zenodo.21534289`:** unchanged; manuscript Data Availability still cites the sealed v1.22.0 science DOI.
- **Gates after the cut:** pytest 135/135, audit 630/630, hashes 185/185.

## C. Main-paper hierarchy

- **Five primary blocks, central:** candidate-governance decomposition (§3.1, Fig. 1); preprocessing ownership (§5.1); candidate-size control (§5.2); conditional validation (§5.3); chronological external boundary (§5.4).
- **External boundary** (§5.4, Table 6): thirteen replays, no net harm observed, incumbent-health trade-off — prominent.
- **Secondary evidence** (§5.5): one compact subsection (~1,150 words) — four paragraphs (mechanism, robustness, VBC-SG cost, operational) + a six-row evidence-map table (Table 7); full grids in the supplement.
- **VBC-SG:** a formal option — one §3.5 method subsection + one §5.5 paragraph + one Table 7 row; explicitly "no mathematical novelty," "not necessary under the size-matched control."

## D. Content moved

| Element | Old location | New location | Reason |
|---|---|---|---|
| Six-tier evidence taxonomy | Main §4 paragraph | Supplement S0 | Genealogy/traceability, not body narrative |
| Per-block provenance | (none) | Supplement S0 table | Traceability catalogue |
| table_policy_frontier | Main §5.5 | Supplement S2 (relocated) | Secondary robustness |
| table_causal_probe | Main §5.5 | Supplement S2 | Observed-data feasibility |
| table_harm_generality | Main §5.5 | Supplement S2 | Mild-drift robustness |
| table_zero_drift | Main §5.5 | Supplement S2 | Frozen zero-drift (historical) |
| table_ab_equivalence | Main §5.5 | Supplement S2 | Ownership mechanism support |
| table_amendment009 | Main §5.5 | Supplement S2 | Classifier/generator robustness |
| table_budget_frontier | Main §5.5 | Supplement S2 | VBC-SG formal cost |
| table_operational_e2e | Main §5.5 | Supplement S2 | Operational acquisition yield |
| §5.5 ten-block narrative (~4,280 w) | Main | Compressed to 4 paragraphs (~1,150 w) | Focus; full detail in supplement |

## E. Content retained (each main table load-bearing)

- **Table 2 (symmetric_pipeline):** the ownership primary result — full own-vs-frozen matrix.
- **Table 3 (symmetric_security):** the preregistered recall/FPR guardrails — the boundary that restricts safety language.
- **Table 4 (size_matched):** the decisive candidate-size control — the central mechanism.
- **Table 5 (evidence_validation_tradeoff):** the nominal evidence-vs-validation trade-off — the conditional-validation primary.
- **Table 6 (chronological_q1):** the pre-enumerated chronological matrix — the external boundary.
- **Table 7 (evidence map):** a six-row at-a-glance of the secondary blocks — replaces eight full tables in the body.
- **Fig. 1 (pipeline):** the decomposition. **Fig. 2 (per-trigger):** the mechanism.

## F. Graphical abstract

- **Old:** flow with a nominal-parity decision branch, three lower badges, ~10 boxes.
- **New:** three central steps (DRIFT ALARM → IS THE CHALLENGER COMPARABLE? → VALIDATE CONDITIONALLY) over three result messages.
- **Boxes:** 6. **Words in diagram:** ~50. **No** confidence intervals, secondary numbers or promotional language.
- **Central message:** a drift alarm proposes; comparability and conditional validation decide.

## G. Tone cleanup

- **Defensive expressions removed:** `we say so plainly`, `rather than hide`, `honest conclusion/summary/boundary`, `reported as-is`, `reported rather than averaged away`, `we prove nothing stronger`, `kept distinct`, `to close the (forking-paths) objection`, `the error was`.
- **Genealogy terms removed from body:** `Six tiers of evidence`, `(i$'/(i$''` tier labels, `harness v1/v2`, `pristine seeds`, discovery-of-the-problem narration.
- **Residual scan of main.tex:** NONE of the above remain. `amendment 009/012` survive only inside relocated supplement table captions and one methodological sentence; `historical convention`/`historical frozen-policy diagnostic` retained as descriptive scientific terms (not chronology).

## H. Compression

| Metric | Before | After | Δ |
|---|---|---|---|
| Main body prose words | 13,210 | 10,607 | **−19.7%** |
| Main pages | 32 | 25 | −7 |
| IEEE pages | 24 | 18 | −6 |
| Supplement pages | 30 | 35 | +5 (received the relocated tables + S0) |
| Abstract words | 221 | 213 | −8 |
| Main `\input` tables | 13 | 5 | −8 (to supplement) |
| Main figures | 2 (+GA) | 2 (+GA) | 0 |
| §5.5 prose words | 4,278 | 1,146 | −73% |
| Discussion | 1,077 | ~1,010 | light trim (four questions kept) |
| Limitations | 1,093 | ~1,060 | consolidated pointers |

Compression came from relocating the eight secondary tables, rewriting §5.5, removing genealogy and
self-justification, and simplifying the graphical abstract — not from cutting load-bearing limits,
negative results, scope, reproducibility methods, the size-matched result or the chronological
boundary. The main came in modestly below the 27–29-page / 10,800–11,500-word orientation targets
because §5.5 compressed efficiently; all primary and boundary content is retained (630/630 audit).

## I. Validation

- **pytest:** 135 passed.
- **audit_paper2_claims:** 630/630 pass.
- **verify_results_manifest:** 185/185 match, 0 unpinned extras.
- **orphans:** none.
- **PDF builds:** main 25 pp, supplement 35 pp, IEEE 18 pp — all 0 undefined refs/citations.
- **references:** resolved (supplement uses `xr`/`\externaldocument{main}` for the one relocated caption citing main sections; main compiles first).
- **overfull boxes:** main 2 (pre-existing CAS-template: `\maketitle` 117 pt, GA/highlights strip 9.7 pt); IEEE 0; supplement 4 (two pre-existing S7/S8 data matrices at ~85 pt, one ~22 pt, one ~13 pt justified-prose) — none serious/new-and-serious.
- **raw unchanged / scientific manifests unchanged:** confirmed (empty `results/` diff vs branch base).
- **processes:** none in background.
- **working tree:** clean except the two untracked personal files (`PLAN_Q1_DEFINITIVO_VBC.md`, `notes/recovered_run_q1_faseC.py.txt`) and untracked `dist/` (v1.22.3 release outputs); no personal/dist file is tracked in any branch commit.
- **Title identical on all surfaces; abstract/highlights consistent.**

## J. Final hostile-reader test

All fifteen questions PASS — see `notes/KBS_FINAL_FOCUS_AUDIT.md`. In summary: the thesis is on page 1; the main reads without project history; no stray version/amendment/final-q1 strings; VBC-SG reads as an extension; frozen-policy results are subordinated; the size-matched control is central; the 13-replay no-net-harm limit is visible; nominal parity is distinguished from effective comparability; no mean benefit is distinguished from no possible value; no defensive language remains; the graphical abstract is graspable in five seconds; every main table is load-bearing; every secondary analysis has a function; the article is cohesive; no conclusion was altered.

## K. Verdict

**READY FOR HUMAN REVIEW — FINAL KBS FOCUS CUT COMPLETE**

The manuscript is now the most focused version the sealed evidence supports: it presents the thesis
—candidate comparability precedes candidate validation, and validation has conditional rather than
universal value— directly, with the two construction mechanisms and the conditional validation
result as its spine, the chronological boundary prominent, and all secondary/formal/operational
evidence subordinated with full traceability in the supplement. No experiment was run; no scientific
result, seed, margin, family, estimand or registered outcome changed; ATTENUATION is preserved and
`results/raw` is byte-identical. No merge, tag, release or Zenodo action was taken.

**STOP.** No further experiments, factorials, health-aware implementation, VBC-SG reopening, hostile
review, result changes, merge, tag, release or Zenodo. This is the last pre-submission intervention.
