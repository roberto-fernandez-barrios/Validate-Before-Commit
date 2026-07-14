# Amendment 007 — a genuinely causal arm (detector recalibration included), row-identity disjointness, zero-drift and random-trigger controls, sequential gate, and the correction of two objective misstatements (LOCKED before runs)

**Date:** 2026-07-15 · Committed and pushed BEFORE any run below. Trigger: seventh external
review. Two of its findings are **errors of ours, confirmed in the code and in our own table**,
and are corrected here; two more are missing controls that could weaken the account, and we run
them.

## Confirmed errors (ours)
1. **The "fully causal" arm is not fully causal.** `run_arm` recalibrates the detector after
   every commit with `calibrate(detector, env, sev, ...)`, which builds the reference from
   `env.train_pools` and the calibration windows from `env.cal_scores_pools`, *at the true
   severity*. Candidate and probe were causal; the post-commit detector state was not --- and
   because gate and naive commit at different times, that oracle information interacts with the
   policy rather than cancelling between arms. The claim "no component of the arm reads
   $sev(t)$ or the pools" was false. (A) below fixes it; until the rerun, the arm is renamed.
2. **Two statements contradict our own Table 9.** We wrote that at mild drift naive is
   "net-harmful in all three benchmarks" (PortScan's CI95 is [$-$1.57, 0.42] --- a negative
   point estimate, not resolved harm) and that "the gate stays non-negative" (UNSW's gate is
   $-$0.09 [$-$0.14, $-$0.04] --- significantly *below* no-adaptation, though inside the
   pre-registered $-$0.2 tolerance). Both are corrected in the manuscript, abstract, highlights
   and README as part of this amendment, independently of any run.

## Seed ledger
- v2 arms: seeds 104--133 (paired extensions on the common streams; new environments where
  `--max-severity` changes, reported as their own study).

## A. GENUINELY CAUSAL ARM (`--recal-source observed`)
After a commit, the detector reference is rebuilt from the **last 8 observed stream windows**
(the same rows the candidate trained on, which a deployment does have) and the threshold is the
0.95 quantile of the detector's scores on the **preceding observed windows** scored against
that reference (up to 30 of them, no severity, no pools). Combined with `--adapt-strategy
sliding_window --probe-source observed`, no component of the arm reads `sev(t)` or any pool.
Runs: 3 regimes x {none, gate} (KS-max, seeds 104--133). **Locked criteria (identical to
amendment 006):** in the harm regime the gate must be significantly above the observed-candidate
naive arm and not significantly below no-adaptation. If the result does not survive genuine
recalibration, we report that the earlier causal claim depended on an oracle detector reset.

## B. ROW-IDENTITY DISJOINTNESS (probe vs candidate training)
Stream windows are drawn from pools *with replacement*, so a pool row can appear both in the
probe window $t{-}9$ and in the candidate's training windows: the arms were window-disjoint,
not row-disjoint. The causal probe now excludes, by exact feature-vector identity, every row
that also occurs in the candidate's eight training windows; the number of excluded rows is
logged (`probe_row_collisions`) and reported. If exclusions leave fewer than 8 probe rows, the
probe is padded from the remaining rows of window $t{-}9$; if that is impossible, the trigger
commits (no evidence) and is counted.

## C. ZERO-DRIFT AND RANDOM-TRIGGER CONTROLS (the review's sharpest scientific point)
At mild drift, replacing a healthy model with a finite re-estimate of nearly the same
distribution could be harmful for reasons that have nothing to do with drift: training variance
alone. The decisive control is **no drift at all**. Runs (seeds 104--133, 3 regimes):
- `--max-severity 0` with the detector trigger, arms {none, lp32};
- `--trigger-mode random --trigger-prob 0.05` (commits forced at a rate matched to the observed
  trigger rate, cooldown unchanged) at `--max-severity` $\in \{0, 0.25\}$, arms {none, lp32}.
**Pre-stated readings (not criteria):** if naive is *also* net-harmful at zero drift, then part
of the mild-drift harm is replacement variance rather than drift-specific specialization, and
the manuscript must say so and decompose the two. If naive is harmless at zero drift but harmful
at mild drift, the degradation--headroom reading is supported. Either outcome is reported.

## D. SEQUENTIAL PROBE GATE (`labeled_probe_seq`) --- the algorithmic contribution
The exact-McNemar result showed that the label budget, not the rule, is binding. The sequential
gate spends labels only where they matter: draw 16 probe flows; compute the one-sided 90\% LCB
of the per-flow correctness difference; commit if the LCB $> 0$, reject if the upper bound
$< 0$; otherwise buy 16 more (up to 64) and repeat; if still undecided at 64, fall back to the
point comparison. Runs: 3 regimes, KS-max, seeds 104--133. Reported: gain, labels actually
spent, and its position on the risk--label frontier against $\varepsilon{=}0$, LCB and McNemar.

## E. Mild-drift under the fully causal pipeline
The mild-drift prediction test (amendment 006) used pools and known severity. It is re-run at
`--max-severity 0.25` with the complete causal pipeline (sliding-window candidate, observed
probe, observed recalibration), arms {none, lp32}, 3 regimes --- so that the paper's two
headline defenses hold *in the same experiment* rather than in two separate ones.

## F. Manuscript and artifact (no new data)
Correct the two misstatements (above); rename "fully causal" until (A) lands; add Algorithm 1A
(core simulation gate) and 1B (observed-data gate) instead of one algorithm that describes
neither; fix the stale \S3.3 sentence (per-arm stream realizations belong to v1 only); rewrite
Fig. 2's panel title ("no consistent score--value association at triggered decisions"), and
commit the figure's generator script --- it was produced ad hoc and never versioned, which is a
reproducibility defect in its own right; fix the "notably,significantly" typo; enlarge the
graphical-abstract type and re-centre it on the mild-drift multi-dataset result; and replace the
remaining "the fix" framing with the frontier framing the results actually support.
