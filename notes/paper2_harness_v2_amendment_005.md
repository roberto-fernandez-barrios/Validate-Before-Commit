# Amendment 005 — two-stage split-probe fix, horizon logging, monitor budget sweep, stratified temporal probes, UNSW chronological stream, model-specification upgrades (LOCKED before runs)

**Date:** 2026-07-14 · Committed and pushed BEFORE any run below. Trigger: fifth external mock
review (Major Revision, "closer to acceptance"). Every design is locked here first; outcomes
reported whatever they are.

## Seed ledger additions
- v2 arm variants and logging reruns (A/B/C below): seeds 104–133 — NEW ARMS / logging-only
  reruns on the same pre-generated common streams (paired extensions, declared descriptive).
- Temporal stratified-probe arm (D): same per-stream seeds as amendment 004 (fri 165–194,
  wed 196–225, thu 227–256) — new arm, paired against the existing naive/gate arms.
- UNSW chronological (E): smoke **300**; confirmatory **301–330**.

## A. Two-stage gate, corrected (split probe — fixes the review's selection-bias objection)
The amendment-004 two_stage reused one 32-label probe for BOTH the health check and the commit
comparison: training is triggered exactly when the incumbent's probe realization is low, and
comparing on that same probe inflates commits (regression to the mean; double statistical use).
**Fix (locked):** the same 32-label draw is PARTITIONED per class into a health half (8/8) and
a commit half (8/8). Health decision: incumbent accuracy on the health half vs the severity-0
health reference (unchanged: 64 labels at arm start) minus δ_health. Commit decision: candidate
vs incumbent BA on the commit half only. No sample is used twice. New flag `--two-stage-delta`;
sensitivity δ_health ∈ {0.03, 0.05, 0.10} × 3 regimes = 9 runs. The amendment-004 two_stage
numbers are retained in the artifact but flagged as optimistically biased; the split-probe
version supersedes them in the manuscript.

## B. Horizon-robust per-trigger logging (logging-only reruns)
The trigger log gains lookahead at horizons h ∈ {1, 3, 5, 10} (columns inc/cand/delta_future{h};
h=5 keeps its current names). Lookahead remains logging-only; policies are bit-identical — the
identity check (seed-level mean BA equal to the published runs) is REQUIRED before use.
Reruns: ks_none and ks_lp32 × 3 regimes into `_hz` dirs (seeds 104–133).
Analyses: per-horizon local regret; the 22× figure is renamed everywhere to
"local per-decision regret on the gate policy's trigger states" (it conditions on the gate
arm's trigger states, not the full naive trajectory).

## C. Monitor budget sweep (river reference implementations)
ddm_river and adwin_river at `--monitor-labels` ∈ {32, 80} (8 already run) × 3 regimes =
12 runs, gate none, seeds 104–133. The claim "labels are better spent on the commit decision
than on monitoring" is rewritten as budget-conditional using this curve, whatever it shows.

## D. Stratified temporal probes (causal test of the composition-inheritance diagnosis)
New temporal gate `labeled_probe_strat`: the 32-flow probe from window t−9 is drawn as 16 per
class where both classes are present (a class with <16 rows contributes all its rows, the
probe is filled to 32 from the remainder; single-class windows fall back to the plain draw and
are flagged). Pre-stated reading (not a criterion): if the Friday/Thursday BA premium shrinks
materially under stratification while Wednesday stays unchanged, the "gate inherits its probe's
composition" mechanism is supported causally. Runs: fri/wed/thu × 1 arm, same seeds as 004.

## E. UNSW-NB15 chronological stream (external temporal dataset; harm/mixed candidate)
Staging (`src/analysis/prepare_paper2_unsw_chronological.py`, locked): concatenate raw
UNSW-NB15_{1..4}.csv (2,540,044 rows, headers from NUSW-NB15_features.csv), sort stably by
Stime; drop srcip, sport, dstip, dsport, proto, state, service, attack_cat, Stime, Ltime;
coerce remaining columns to numeric, median-fill; Label = BENIGN/ATTACK from the binary label
column. Split: first 30% of the sorted timeline = training past; final 70% = evaluation stream.
Runner: `run_paper2_temporal_stream` (200 × 256-row windows, stride spans the stream), arms
{none, labeled_probe, labeled_probe_strat}; questions T1–T3 of the temporal protocol unchanged
(headline = BA over two-class windows). Expectation stated, not required: the incumbent may
stay healthier than the Tuesday→Friday CICIDS case (same network, evolving attack mix), giving
the gate genuinely mixed commit decisions. ANY outcome is reported, including trigger
starvation or another deep-benefit regime. Seeds 301–330 (smoke 300).

## F. Mechanism/model specification upgrades (analysis, locked)
- MixedLM clusters corrected to **regime × seed** in the pooled model (a seed is not the same
  experimental unit across regimes); per-regime models keep seed clusters. VIFs reported for
  deg_pre5 / score / severity / window_idx. Random slope on deg_pre5 attempted; reported if it
  converges.
- The per-trigger mechanism and the hierarchical model are repeated on the **QK-ZZ** trigger
  logs (existing `qk_none` dirs, 342 triggers) — extending the "score predicts nothing" test
  beyond KS-max, whatever it shows. Wording in abstract/§5 is restricted to the evaluated
  detectors at triggered decisions.
- Regret is recomputed at horizons {1,3,5,10} from the `_hz` logs.

## G. Policy frontier and operational-utility scenarios (locked)
Frontier table per regime over {naive, lp32, holdout, lcb64, two_stage(split), ensemble_cal,
ddm_river, sliding_window}: gain, total labels, commits, model growth (yes/no), explicit
no-deploy (yes/no). Utility in flow-error equivalents over N = 12,800 evaluated flows/stream:
U = (ΔBA/100)·N − c_L·total_labels − c_U·commits, scenarios (c_L, c_U) ∈
{(0.1, 50), (1, 50), (0.1, 500), (1, 500)}. Replaces the single-winner claim with a frontier;
the manuscript reports which policy wins each scenario, whatever it is.

## H. Manuscript/structure (listed for completeness)
Methods rewritten around harness v2 (v1 becomes "initial exploratory study" with its caveats
moved to its own subsection); title → "Validate Before Commit: Label-Efficient Commit
Decisions for Drift-Triggered Classifier Updates in Network Intrusion Detection"; keywords
"concept drift"→"distribution drift", "safe model updating"→"risk-aware model updating";
conclusion and Discussion bounded by the chronological premium; "detector scores predict
nothing" restricted; frontier table replaces dominance; reproducibility hardening (confirmatory
CSVs committed, SHA-256 manifest, single reproduce script).
