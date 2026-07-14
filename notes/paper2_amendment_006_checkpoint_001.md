# Amendment 006 — checkpoint (all runs complete, all outcomes reported)

**Date:** 2026-07-14. Protocol registered at `ce07c30` BEFORE any run. 44 runs (42 v8 + 2
chronological), 30 seeds each, zero failures. Identity check for the runner changes: PASS.
Audit: 240 → **278/278**. Builds: 32 pp CAS / 25 pp IEEE.

## A. CAUSAL OBSERVED-DATA GATE — the review's #1 objection, ANSWERED (criteria PASS)
No component reads `sev(t)` or the pools: candidate = last 8 OBSERVED windows; probe = 32 rows
of the OBSERVED window t−9 (natural composition).
- ToN: naive (observed candidates) **−2.44** [−4.11, −0.92] → causal gate **+0.85** [0.57, 1.13];
  **+3.29 [1.85, 5.03] above naive** (criterion i ✓), significantly above no-adaptation (ii ✓).
- PortScan +8.64; UNSW +1.31 (+0.35 [0.10, 0.63] above naive).
- **Causal ≈ oracle**: ToN +0.06 [−0.20, 0.32] and UNSW −0.04 [−0.27, 0.18] (indistinguishable);
  PortScan −0.48 [−0.76, −0.20] (small real cost). The mechanism does not need the simulator.

## B. REGISTERED PREDICTION TEST — CONFIRMED, and it generalizes the harm
Locked before running: "at max-severity 0.25, PortScan's naive gain falls below +1.0 and at
least one regime turns net-harmful while the gate holds ≥ −0.2."
**Result: naive is net-harmful in ALL THREE benchmarks at mild drift** — PortScan (CICIDS)
**−0.46**, UNSW **−0.15**, ToN **−0.65** — while the gate stays ≥ −0.09 and is significantly
above naive in every regime (+0.84 / +0.06 / +0.62). At sev 0.50: ToN naive −3.63 → gate +0.19
(+3.82 [1.62, 6.40]); UNSW naive −0.25 → gate −0.09; PortScan naive +1.40 → gate +2.88.
**Net harm is a property of the operating point (healthy incumbent), not of one dataset.** This
kills the "single constructed cell" objection with a pre-registered prediction of the theory.

## C. HARM BREADTH ON v2
ToN-IoT DDoS: naive **−15.24** [−18.13, −12.32] → gate +1.02 (+16.26 above naive).
ToN-IoT Injection: naive −2.24 → gate +0.43 (+2.67). Harm replicates in two further regimes
under the hardened harness.

## D. HONEST BINOMIAL-PREVALENCE PROBES — claim RETRACTED (Sol was right)
Zero-attack probe fractions under Binomial(b, π): π=0.10 → 2–3%; π=0.05 → 15–23%;
π=0.01 → **66–74%** (theory: 72.5%).
- π=0.10 and π=0.05: gate holds (ToN +0.82 / +0.91; PortScan pays −0.20 / −0.44 vs balanced).
- **π=0.01: ToN +0.21 [−1.39, 1.15] — no longer resolvable from zero.** The old "π=0.01 retains
  full safety and benefit" was an artifact of `max(1, ...)` forcing one attack into every probe.
  Manuscript + Limitations rewritten: the gate tolerates random inspection down to π≈0.05;
  below that the probe must be enriched (≈1/π inspections).

## E. RISK AXIS (exact McNemar)
Commit only on a significant exact one-sided McNemar test: never harmful (ToN +0.00) but
almost no power at b=32 (0.03 commits/stream) and it forfeits benefit (PortScan +5.45,
−3.67 [−4.61, −2.74] vs the plain gate; b=64 recovers to +7.67). **The label budget, not the
decision rule, is the binding constraint** — this justifies ε=0 at 32 labels and adds the risk
axis to the frontier table.

## F. PER-INCUMBENT HEALTH REFERENCE
Recalibrating on each commit (zero extra labels) leaves conclusions unchanged (ToN +0.11
[−0.27, 0.45] vs +0.15 static; PortScan +7.88 vs +7.87) — the savings were not a stale-reference
artifact. The corrected variant is the recommended one.

## G. CHRONOLOGICAL HARM ATTEMPT — FAILED (reported)
Wednesday-trained → Thursday replay: the incumbent collapses again (48.7% BA), giving a fifth
deep-benefit stream (naive +33.66; gate +18.58; premium −15.08 BA but −0.08 [−0.30, 0.15] on
accuracy — the metric-dependent pattern at its most extreme). **Chronological net-harm remains
unobserved across five replays**, and Limitations says so.

## H. Prose/artifact
Evidence taxonomy (registered confirmatory core / registered extensions / exploratory) added to
Results; "chronologically ordered subsampled replay" adopted; utility scenarios framed as
illustrative; universal detector claims softened; README claims synced with the manuscript
(the "predicts nothing"/"identically" lines are gone) and its BibTeX title fixed; REPRODUCE
carries amendments 005/006 and every new flag.
