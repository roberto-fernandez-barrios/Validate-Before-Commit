# Amendment 004 — temporal-runner correction, chronological mixed/harm streams, v2 robustness suite, two-stage gate, monitor validation, decision-quality analysis (LOCKED before runs)

**Date:** 2026-07-14 · Committed and pushed BEFORE any confirmatory run listed here.
Trigger: fourth external mock review (Major Revision). Every item below is locked in this note
before its runs/analyses execute; outcomes are reported whatever they are.

## Seed ledger (discipline unchanged: smoke seeds are excluded from confirmation)
- 101–103: burned (v2 smoke). 104: burned (temporal smoke). 104–133: v2 confirmatory window
  (streams are pre-generated per seed; NEW ARMS on these seeds are paired extensions on
  bit-identical streams, not contamination — they are declared descriptive, not confirmatory).
- 134–163: temporal run under the FLAWED runner (see A below); superseded, retained as
  exploratory with the caveat disclosed.
- 164: temporal-corrected smoke. **165–194: temporal-corrected confirmatory (Friday).**
- 195: Wednesday smoke. **196–225: Wednesday confirmatory.**
- 226: Thursday smoke. **227–256: Thursday confirmatory.**

## A. Temporal runner correction + rerun (CONFIRMATORY, supersedes protocol 001 run)
The review found a real implementation flaw: with `stride = max(window_rows, total//n_windows)`
(~3,500 rows on Friday), the candidate slice `Xs[starts[t-8]:st]` spans ~28k rows, most of them
never processed as windows — contradicting "retrained on the last 8 observed windows". The
per-run metric also averaged plain accuracy (single-class windows) with balanced accuracy.
**Fixes (locked):**
1. Candidate trains ONLY on the concatenation of the last 8 observed 256-row windows (~2,048 rows).
2. The post-commit detector reference resamples from those same observed windows.
3. Metric homogeneity: per-window logs carry `balanced_accuracy` (NaN when single-class) AND
   plain `accuracy`; the HEADLINE metric is mean BA over two-class windows; mean accuracy over
   all windows is reported as secondary.
Questions T1–T3 of `paper2_temporal_stream_protocol_001.md` unchanged, evaluated on the
homogeneous metric. Seeds 165–194 (smoke 164). Any outcome reported; the candidate is weaker
than in the flawed run (~2k vs ~28k rows), so the recovery and the gate premium may both move.

## B. Chronological mixed/harm streams (CONFIRMATORY for external validity)
Same corrected runner, same T1–T3, incumbent trained on Tuesday:
- **Wednesday** (`Wednesday-workingHours.pcap_ISCX.csv`, DoS/DDoS day), seeds 196–225.
- **Thursday** (`Thursday-…Morning-WebAttacks` + `Thursday-…Afternoon-Infilteration`, in file
  order), seeds 227–256. Attack mass is small; the incumbent plausibly stays healthy and
  candidates trained on nearly-benign windows may be worse — the chronological analogue of the
  mixed/harm regimes. Expectations are NOT criteria; we report whatever happens, including
  trigger starvation. If fewer than 20% of windows are two-class, the BA headline is reported
  with that caveat and the accuracy series carries the narrative.

## C. v2 robustness suite (descriptive, seeds 104–133, paired on the common streams)
New runner features (flags added before runs; RNG namespaces disjoint from existing ones):
- `--probe-latency L`: the probe is drawn at the severity of window max(0, t−L) (stale labels).
- `--probe-flip-frac f`: after drawing, a fraction f of probe labels is flipped
  (`default_rng(seed*500_009 + t)`).
- Gate `two_stage`: at trigger, FIRST spend the 32-label probe on the incumbent alone; if the
  incumbent's probe accuracy is within δ_health = 0.05 of its severity-0 reference (64 labels,
  `default_rng(seed+887)`, measured once at arm start), DO NOT train a candidate (no candidate
  labels, no compute); otherwise train and commit iff candidate ≥ incumbent on the SAME probe
  (zero additional labels). This instantiates the two-stage train/deploy decision the review
  asked for.
- `--adapt-strategy ensemble_cal`: as `ensemble`, but every model is trained with Platt
  calibration (`SVC(probability=True)`) and the ensemble averages `predict_proba` — the
  calibrated version of the strongest label-free rival.
- `--trigger-mode ddm_river|adwin_river`: the same 8 monitoring labels/window are fed as
  INDIVIDUAL Bernoulli outcomes to `river.drift.binary.DDM` / `river.drift.ADWIN(delta=0.002)`
  (reference implementations), naive commit; validates the amendment-003 monitor claims.
Runs (all 3 regimes, KS-max unless stated): budget lp8/lp16/lp64/lp128; latency lp32 with
L∈{5,20}; corruption lp32 with f∈{0.10,0.25,0.40}; two_stage; ensemble_cal (trigger=detector,
gate none); ddm_river + adwin_river (gate none). Pre-stated reading (not criteria): v1 found
benefit stable for b≥8, tolerance to 20-window staleness and 40% flips — do these survive v2?
For river monitors: does canonical-DDM net-harm in ToN-IoT replicate under the reference
implementation, and does ADWIN fire at 8 labels/window?
Additionally a deterministic unit cross-check (`src/analysis/validate_monitors_vs_river.py`):
synthetic Bernoulli step streams, our DDM/ADWIN vs river's, agreement on fire/no-fire and
detection delay reported.

## D. Label & compute accounting (locked definitions)
New per-arm counters: `labels_probe`, `labels_monitor`, `labels_candidate` (rows actually used
to train candidates, incl. later-rejected ones; sliding-window counts its 8×128 window rows),
`n_candidates_trained`. For pre-existing runs these are reconstructed exactly:
candidates = n_triggers (training precedes the gate in every arm except two_stage),
labels_candidate = n_triggers × 2 × 512, probe = n_triggers × probe_size (fresh) or 0 (holdout).
A total-cost table (per policy × regime: monitoring / candidate / probe / total labels,
candidates trained, rejected) becomes a main-text table.

## E. Decision-quality metrics (locked; computed from existing v2 per-trigger logs, lp32 arms)
Ground truth per trigger: Δ5 = cand_future5 − inc_future5 (logged lookahead, never policy input).
- harmful-commit rate = #(commit ∧ Δ5<0)/#commit; beneficial-rejection rate = #(reject ∧ Δ5>0)/#reject
- gate precision = #(commit ∧ Δ5>0)/#commit; gate recall = #(commit ∧ Δ5>0)/#(Δ5>0)
- per-trigger regret = Δ5·1[reject ∧ Δ5>0] + (−Δ5)·1[commit ∧ Δ5<0]; baseline: always-commit
  regret = (−Δ5)·1[Δ5<0] on the same triggers.
Per regime and pooled; per-seed cluster bootstrap (2,000 resamples) CIs.

## F. Hierarchical per-trigger model (locked)
MixedLM: Δ5 ~ deg_pre5 + score + severity_t + window_idx with random intercept per seed;
fit per regime and pooled (regime fixed effects). Report coefficients with 95% CIs and
leave-one-regime-out predictive R² of the fixed part. Read predictively, not causally.

## G. Traceability fixes (no new data)
The fresh-probe classifier-generalization runs exist (`paper2_v2_{reg}_ks_lp32_{dm}`) and
`classifiers_lp32.csv` matches the manuscript, but the aggregation block that produced it was
not committed — it is added to `aggregate_paper2_v2_replication.py` now. README/REPRODUCE are
synchronized with v2/amendments/temporal commands, and a `requirements-lock.txt` (pip freeze)
is added.

## H. Framing & claims (manuscript-only, listed for completeness)
Commit/deployment-gating reframing; ε* corrected for sunk costs (commit rule ε*=λ_U/(λ_e·N);
λ_C belongs to the antecedent train decision, instantiated by the two_stage gate); removal of
"fails safe"/"never significantly worse" in favor of bounded, evidence-matched statements;
v2 promoted to the main tables/figures with v1 explicitly exploratory; coupled Fig. 2 demoted.
