# final-q1 — Fase E checkpoint (part 1: restructure + Fase-C integration)

Date: 2026-07-20. Branch `final-q1`. NOT committed. Fase D batches still in flight; this
part covers everything that does not depend on their results.

## P2 restructure (Sol's editorial blocker)

`\S5.3` (one 20-paragraph section covering everything) split into three, per the reviewer's
own suggested structure:

| new | title | label | content |
|---|---|---|---|
| 5.3 | Confirmatory and causal results | `sec:v2` | harness, per-trigger mechanism, hierarchical model, decision quality, model-agnosticism, update generators, robustness envelope, two-stage, cost accounting, leakage-free causal arm |
| 5.4 | Risk-controlled candidate governance | `sec:risk` | mild-drift prediction test, zero-drift control, classifiers/generators, A/B mechanism + equivalence, tail + anytime-valid gates, **budget frontier**, risk axis |
| 5.5 | Operational and chronological boundaries | `sec:boundaries` | probe prevalence retraction, two-stage health reference, [operational e2e — Fase D5], chronological replays |

All 20 `\ref{sec:v2}` cross-references audited one by one and retargeted where the content
moved (6 → `sec:risk`, 3 → `sec:boundaries`, 2 rewritten as local "below", the rest correct
as-is). Both roadmap sentences rewritten to describe the three-way split. 0 undefined
references in all three PDFs.

## The non-vacuity result written up (Sol blocker #4)

New paragraph in 5.4 + `tab:budget_frontier` (emitted from the frozen CSV by
`make_paper2_q1_tables.py`, so every number traces to an artifact). The honest framing: the
earlier "maximally-stacked configuration commits nothing" was a statement about a $b{=}64$
budget, not about the rule. Twelve configurations meet the pre-declared non-vacuity target;
the headline is pooled EB-CS + deferral + lifetime Bonferroni at cap 512 recovering **93% of
naive's benefit at 578 probe labels per proposal**, with **zero commits under zero drift at
every cap**, and VBC-SG-Cohort (fully stratified) at 81%. The price is stated in the same
breath: 74–86% abstention, ~4 windows of deferral, and the zero-cost strict gate still buying
most of the practical safety — presented as a menu, not a winner.

## The A/B equivalence + decomposition written up (Sol blockers #3 and part of #2)

New paragraph in 5.4 + `tab:ab_equivalence`. Reports the pilot/confirmatory split honestly:
own-transformer **equivalent to zero on all three benchmarks** (ToN tight enough for ±0.2),
UNSW independent equivalent too; PortScan/ToN independent **unresolved, not shown null** —
the pre-agreed D2 fallback wording, with the inversion carrying the identification. The
decomposition is new evidence rather than a hedge: the **standardizer** carries essentially
the whole ownership advantage (−12.17 [−15.26, −9.23] of the full −12.35) and the PCA
carries none (+0.16 [−2.90, +3.08]) — consistent with a variance-scaled RBF bandwidth.

## Highlights + graphical abstract

Highlights replaced by the five the protocol fixed (all ≤85 chars; the mild-drift one now
carries "resolved in two" inline, per Sol). Graphical abstract simplified from four crowded
caveat boxes to three messages with larger type and no overlap (verified by rendering);
"mechanism identified" wording dropped there too.

## Verification

- Audit **439/439** (24 new pinned checks: frontier anchors and endpoints, zero-drift safety
  across the whole sweep, zero harmful commits, the six TOST verdicts and both decomposition
  cells).
- PDFs: 30 pp CAS / 21 pp supplement / 23 pp IEEE, 0 undefined refs or citations.
  **30 pp is over the ≤27 target** — expected at this stage (two tables and ~2 pages of new
  results just landed). The trimming pass belongs to Fase E part 2, together with the Fase-D
  integration, and is where superseded intermediate material moves to the supplement.
- README/REPRODUCE audit counts synced to 439; test expectations updated for the two new
  body tables.

## Part 2 — Fase D integration and the trimming pass (DONE)

**Integrated into \S5.5**: the pre-enumerated chronological matrix (`tab:chronological_q1`)
and the operational end-to-end evaluation (`tab:operational_e2e`), both emitted from frozen
CSVs, with 20 further pinned audit checks. The chronological write-up states the conditional
prediction where it holds (UNSW: gates beat naive, strict by +2.78/+1.34 on non-overlapping
intervals) AND where it does not (Wednesday intra-day, healthy but gates 0.5–0.7 below naive,
unresolved), so it reads as a tendency, not a law. The e2e write-up leads with the honest
headline form ("32 adjudicated labels, costing X inspected flows under policy Y at prevalence
$\pi$") and reports the disagreement-sampling negative as it came out.

**Trimming to target.** Body went 31 pp $\to$ **27 pp of content** (references start at
p. 28), meeting the frozen protocol's $\le$27. What moved, all of it on the reviewer's own
move-to-supplement list:
- the amendment-by-amendment history of the causal arm $\to$ \S S2.7;
- the superseded three-point EB-CS budget sweep $\to$ \S S2.8 (the registered frontier
  supersedes it in scope);
- the two superseded risk-gate implementations (Robbins CS, Bonferroni sequential probe)
  $\to$ \S S2.9;
- `table_temporal_streams` (the six earlier replays) $\to$ supplement, where \S S2.6 already
  carried their narrative;
- `table_symmetric_ab` $\to$ **merged into** `tab:ab_equivalence`, which now carries the
  confirmatory equivalence, the scaler/PCA decomposition and the pilot ownership inversion in
  one mechanism table (two tables $\to$ one);
- triple-stated harness description (\S4, \S5.1, \S5.3) collapsed to one;
- per-model and per-generator enumerations that duplicated the adjacent table.

## Verification (final for Fase E)

Audit **459/459**, tests **33/33**, PDFs 30 pp CAS (27 pp body) / 23 pp supplement / 23 pp
IEEE, 0 undefined references or citations in any of the three.

## Pending

Fase F: `make final-paper` end to end, an independent hostile review of the result, freeze.
Then, only with Roberto's explicit authorization: commit/push of `final-q1`, release v1.18.0
+ Zenodo (v1.17.0 stays frozen), submission.
