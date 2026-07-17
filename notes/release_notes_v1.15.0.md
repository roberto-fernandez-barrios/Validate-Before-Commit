## What changed since v1.14.0 (amendment 013 — fifth-round review, executed in full)

A registered program (predictions P1–P6 before any run) addressing the reviewer's blocking items
plus the decisive mechanism control: 30 harness arms and a standalone symmetric-A/B experiment,
30 seeds. Claims audit **380 → 395/395**; builds **38 pp CAS / 30 pp IEEE**.

**The zero-drift mechanism is now identified, not hypothesized — and the reviewer was right.**
A symmetric A/B control fits the standardizer+PCA on an independent partition and trains two
equal-size models on disjoint samples of the same distribution: replacing one with the other is
then **harmless** (gap ≈ 0: ToN-IoT +4.99, UNSW 0.00, PortScan −1.90 n.s.), while fitting the
transformer on the incumbent's data — the standard freeze-the-pipeline convention — **reproduces
the harm** (ToN-IoT −10.45 [−16.2, −5.3]). The zero-drift replacement harm is therefore not
re-estimation variance but the incumbent's representational advantage from the frozen feature
pipeline; per-challenger preprocessing is the mitigation. The manuscript is rewritten accordingly.

**Table 8 is replaced by the final leakage-free causal arm.** The stream now draws every window
without replacement from a globally value-deduplicated pool with an abort-on-exhaustion assertion:
candidate-training/future-evaluation collisions are **exactly zero** in every cell; the gate
rejects at early no-probe triggers (zero unvalidated commits); the observed threshold is
recomputed only once 30 score-windows exist (a sweep over {8,16,30} leaves the contrast
unchanged). The harm-regime result is the strongest yet: ToN-IoT gate−naive **+5.57 [3.19, 8.30]**
at full drift and **+4.21 [0.95, 8.45]** at mild drift. The superseded leaky numbers move to the
amendment notes, with the full trajectory disclosed (+3.86 → +2.95 → +3.24 → +5.57). One honest
feasibility disclosure, surfaced by the new assertion: UNSW at full drift cannot sustain 128-flow
windows without replacement (its attack pool holds 2,664 unique rows), so that cell runs 64-flow
windows — and there both arms sit below no-adaptation, with the gate still +0.51 [0.18, 0.87]
above naive, reported as-is.

**A guarantee matched to the probe actually drawn.** The probe uses fixed class quotas, so pooled
i.i.d. tests match the sampling only approximately. A stratified per-class gate (Bonferroni α/2
per class, commit iff the balanced-accuracy lower bound clears zero) bounds false superiority for
ΔBA under the stratified design itself: zero commits under zero drift, conservative benefit
capture at full drift (PortScan +6.93).

**The strict-comparison baseline, evaluated everywhere.** Rejecting ties (commit only on strict
probe superiority) was previously shown only under zero drift; at full drift it retains essentially
the whole benefit (PortScan +8.78, UNSW +1.41, ToN +0.60) and stays non-negative at mild drift —
a genuine zero-cost Pareto point, now on the frontier, quantifying exactly what the statistical
gates add: the last fraction of harm plus the formal control.

**Editorial.** "Makes readaptation safe" is now conditioned on the operating point; the ε=0 gate is
relabeled point-estimate-maximizing; the highlights carry the SVC-RBF qualifier; the abstract
states the confidence-sequence guarantee "under the assumed probe-sampling process"; the causal
iteration history is consolidated to a single disclosure paragraph.
