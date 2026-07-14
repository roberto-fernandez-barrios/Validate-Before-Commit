# Amendment 005 — checkpoint (all runs complete, all outcomes reported)

**Date:** 2026-07-14. Protocol: `paper2_harness_v2_amendment_005.md` (registered at `773e692`
BEFORE any run). 33 runs (27 v7 + 3 stratified temporal + 3 UNSW chronological), 30 seeds each,
zero failures. Identity check for the horizon-logging change: PASS (bit-identical policy).
Audit: 240/240.

## A. Split-probe two-stage gate — the review's selection-bias objection was REAL
Corrected (health/commit halves disjoint), δ sweep {0.03, 0.05, 0.10}:
- ToN d05: gain **+0.15 [−0.15, 0.46]** (the probe-reusing version's +0.16 [0.03, 0.31] was
  optimistic — net gain over never-adapt is now honestly unresolved at 30 seeds); still
  **+1.79 [0.69, 2.92] above naive**; 1.07 candidates (−69% vs lp32), 1,341 total labels.
- δ is a clean operating characteristic (d03: ToN +0.34, PortScan −0.76 vs lp32;
  d10: ToN +0.04, PortScan −1.80). Manuscript, README, cost table, frontier all updated.

## B. Horizon-robust local regret (hz logging reruns, identity-verified)
ToN 15–23× at h∈{1,3,5,10}; PortScan 4–5×; UNSW an honest wash (0.8–1.0 on regrets an order
of magnitude smaller). Renamed everywhere: "local per-decision regret on the gate policy's
trigger states" (not the full naive trajectory).

## C. Monitor budget sweep (river, 4× and 10× labels)
No budget fixes the monitors: DDM ToN −1.04 [−1.87, −0.37] at 4×, −0.45 at 10×; PortScan
+7.08 at 10× (< naive); ADWIN silent in ToN at every budget. Claim rewritten budget-conditional.

## D. Stratified temporal probe — our composition diagnosis was REFUTED
fri strat−gate: **−0.05 [−0.49, 0.41]** (premium unchanged). Composition account not supported
where testable (caveat: ~2/3 of past windows single-class). Surviving hypothesis: probe
staleness under fast drift — stated as hypothesis, not mechanism. Manuscript/README rewritten.

## E. UNSW-NB15 chronological stream — the external healthy-incumbent test, and it PASSES
Raw captures sorted by Stime (2.54M flows; train = first 30%, attack mix 2.9%→16.8%):
incumbent stays healthy (**82.3% BA**, no collapse; 163/200 two-class windows, ~21
triggers/stream); naive +7.33 [6.80, 7.85]; **gate premium ZERO** (+0.16 [−0.31, 0.63] BA;
+0.21 acc). Exactly the account's prediction: insurance is free where the incumbent's health
makes the decision genuinely uncertain. Chronological NET-HARM remains unobserved — stated
as the outstanding external test in Limitations.

## F. Model-specification upgrades
Pooled MixedLM re-clustered regime×seed: β_deg −1.02 [−1.61, −0.43] (wider, still excludes 0);
random slope converges (−0.92 [−1.30, −0.55]). VIFs: deg ≤2.4, score ≈1 (clean); severity↔time
60–230 (structurally collinear on a ramp — disclosed, coefficients not separately interpreted).
**QK-ZZ extension** (311 triggers): r_deg −0.50..−0.72, pooled −0.59 [−0.68, −0.45]; β_deg
−0.38..−1.07 all excluding 0; raw score ≈0 in all six cells; ONE conditional exception —
QK/PortScan score β +5.49 [0.27, 10.72] — reported. "Detector scores predict nothing" replaced
by "no consistent signal" everywhere.

## G. Frontier + utility scenarios (locked constants)
No policy dominates. Under all four (c_L, c_U) scenarios the cheap policies (split two-stage,
DDM trigger) win the utility at N=12,800; the plain gate overtakes two-stage in the harm regime
only beyond ~46k flows at c_L=0.1. New main-text frontier table; single-winner claim removed.

## H. Structure/prose/reproducibility
Methods rewritten around harness v2 (v1 = "initial exploratory study" with caveats); title →
"Validate Before Commit: Label-Efficient Commit Decisions for Drift-Triggered Classifier
Updates in Network Intrusion Detection" (propagated to tex/md/README/CITATION.cff/.zenodo.json);
keywords distribution-drift/risk-aware; conclusion bounded by the chronological premium;
confirmatory CSVs committed + MANIFEST.sha256 + Makefile (`make reproduce`). Audit 208 → 240.
Builds: 30 pp CAS / 23 pp IEEE.
