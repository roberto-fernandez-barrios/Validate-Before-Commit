# Amendment 007 — checkpoint (all runs complete, all outcomes reported)

**Date:** 2026-07-15. Protocol registered at `ef0b39f` BEFORE any run. 33 runs, 30 seeds each,
zero failures. Identity check PASS. Audit: 278 → **305/305**. Builds: 34 pp CAS / 27 pp IEEE.

## The two errors we were caught making, and fixed
1. **The amendment-006 "fully causal" arm was not causal**: after every commit the detector was
   recalibrated from the pools at the TRUE severity. Fixed (`--recal-source observed`) and re-run.
2. **Window-disjoint ≠ row-disjoint** (pools are sampled with replacement): 27–38 rows per
   stream were shared between the probe window and the candidate's training windows. The probe
   now excludes them by exact row identity.
Both manuscript misstatements about Table 9 ("net-harmful in all three", "gate stays
non-negative") were corrected — our own CIs contradicted them.

## A. GENUINELY CAUSAL ARM (Algorithm 1B) — criteria PASS with every privilege removed
- ToN: naive **−3.19** [−5.92, −0.99] → gate **+0.67** [0.35, 1.00]; **+3.86 [1.67, 6.73]** above
  naive (criterion i ✓), significantly above no-adaptation (ii ✓).
- Still **indistinguishable from the oracle gate** in the harm regime (−0.12 [−0.45, 0.21]);
  small real costs elsewhere (PortScan −0.55, UNSW −0.37).
- **Mild drift replicates INSIDE the causal pipeline** (naive −0.98 / −0.11 / −0.42; resolved in
  UNSW and ToN; gate significantly better in both) → the paper's two defenses now hold in ONE
  experiment.

## B. ZERO-DRIFT CONTROL — the reviewer's alternative explanation is RIGHT, and it strengthens us
Random triggers, **no drift at all**: naive is significantly net-harmful in all three benchmarks
(PortScan **−2.76** [−3.76, −2.03], UNSW **−0.75**, ToN **−4.75** [−8.12, −2.01]); the gate
recovers most of it (+1.64 / +0.19 / +4.51 above naive).
Consequences, stated in the paper:
(i) much of the mild-drift harm is the **variance cost of replacing a healthy model**, not a
drift-specific effect — the mild-drift result is the interpolation between this floor and the
benefit regime;
(ii) it is the account's limiting case (zero headroom ⟹ non-positive value), so the control that
could have falsified the account instead confirms it;
(iii) **it removes the detector from the argument entirely**: with no drift to detect, no monitor
can prevent this loss — only validating the candidate can. This is now the paper's sharpest
statement of its own thesis, and it is in the abstract and conclusion.

## C. SEQUENTIAL PROBE GATE (algorithmic contribution)
Buy 16 labels, stop as soon as the one-sided 90% interval resolves the sign, up to 64: spends
51–54 labels/decision and is the **best gate in the benefit regime** (PortScan +9.21, +0.09
[0.02, 0.18] above fixed b=32), matching it elsewhere. Point comparison / sequential / LCB /
exact McNemar span the risk–label frontier.

## D. Prose, figures, artifact
Algorithm 1A (core simulation) and 1B (observed data) replace the single algorithm that
described neither; §3.3's stale "each arm consumes its own stream realization" now scoped to v1;
**Fig. 2 regenerated from a committed generator** (`make_paper2_pertrigger_figure.py` — it had
been produced ad hoc and never versioned, a reproducibility defect in itself) with the wording
the statistics support ("no consistent score–value association at triggers"), now showing both
detectors; graphical abstract re-centred on the healthy-incumbent/zero-drift result with larger
type; utility framed as illustrative; abstract at exactly 250 words.
