## What changed since v1.12.0 (amendment 011 — the third-round review, executed)

A registered program (predictions P1–P4 fixed before any run) addressing the reviewer's blocking
and recommended items: 33 arms plus a coverage simulation, 30 seeds, zero failures. Claims audit
**350 → 367/367**; builds **37 pp CAS / 29 pp IEEE**.

**The top blocker — train/future-test overlap in the causal arm — is eliminated, and the result
survives.** The pools were sampled with replacement, so a candidate-training row could recur in a
later evaluation window (387–1,319 per stream). A new stream mode draws every window *without
replacement* within the value-deduplicated window pool, so no row — and no identical feature
vector — appears in more than one window. Collisions fall to ≈0 (0.2–1.1 per stream), and the
harm-regime result holds: the causal gate still converts the ToN-IoT harm, gate−naive **+2.95
[1.53, 4.50]** at full drift and **+1.40 [0.29, 2.87]** at mild drift. One honest correction:
PortScan's small *benefit*-regime gate premium (+0.95) was partly a leakage artifact and is now
indistinguishable from zero — immaterial, since in a pure-benefit regime the gate has nothing to
add over naive.

**The confidence-sequence guarantee is now stated precisely.** A new Methods subsection specifies
the risk-controlled gates (exact McNemar, Robbins CS, empirical-Bernstein CS) and the *scope* of
their guarantee: they bound the per-proposal probability of falsely establishing candidate
superiority **on the probe distribution**, uniformly over the stopping time — not the probability
of future balanced-accuracy harm (which needs probe representativeness), and per proposal, not
stream-wide (a stream with M proposals has a union bound Mα). The accuracy-maximizing ε=0 gate is
now clearly separated from the risk-controlled gates throughout.

**Cumulative controls: the harm is not a duplication or regularization artifact.** None of
row-deduplication, adding the incumbent's initial training set, or n-scaled SVC regularization
removes the zero-drift replacement harm; deduplication and n-scaling *deepen* it, and
initial+observed only attenuates it (while flipping the marginal UNSW case positive). The effect
is replacement variance, and we keep the claim at the tested-implementation scope.

**The label budget, not the rule, is the binding constraint.** An empirical-Bernstein budget sweep
(128, 256 flows) recovers the 1-point UNSW/ToN benefits the gate missed at 64 (UNSW +0.00 → +0.78),
at proportional labeling cost.

**Two audits back the risk claims.** The empirical per-stream harmful-commit rate is 37–70% of
streams for the ε=0 gate but zero for the risk-controlled gates; and a Monte-Carlo coverage check
confirms the sequences hold under i.i.d./without-replacement probes (≤0.002) but shows the tighter
empirical-Bernstein sequence exceeds nominal α under strong within-probe autocorrelation (0.18 vs
0.10) — making the probe-representativeness caveat quantitative.

Editorial fixes: the abstract's "every update generator" now notes the calibrated-ensemble
exception; Figure 8's title is "random label corruption" (not "adversarial"); "predicts nothing"
softened to "no consistent association"; headroom framed conditional on the candidate generator.
