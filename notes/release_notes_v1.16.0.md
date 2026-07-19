## What changed since v1.15.0 (final-KBS phases A–D + amendment 014)

This release executes phases A–D of the frozen max-ceiling protocol (`notes/final_kbs_protocol.md`)
plus the sixth review's two verified blockers: ~90 harness arms and two symmetric-A/B experiments,
30 seeds. Claims audit **395 → 415/415**; builds **39 pp CAS / 32 pp IEEE**.

**The zero-drift mechanism, identified under all four pre-declared criteria.** The symmetric A/B
was redone correctly — globally value-deduplicated **disjoint** T/M1/M2/E blocks (asserted), the
incumbent role **randomized** per seed, four transformer conditions. For SVC-RBF in the
harm-regime dataset: independent transformer → gap ≈ 0 (−1.78 [−7.45, +3.92]); fit on the
incumbent → systematic incumbent advantage (−12.35 [−19.33, −6.45]); fit on the challenger →
the effect **inverts** (+17.77 [+11.00, +24.75]); own transformer each → **eliminated** (+0.05).
Random forest shows no effect anywhere. The zero-drift replacement harm is *transformer
ownership* — whichever model owns the frozen preprocessing wins — learner-specific to SVC-RBF,
with per-challenger preprocessing as the mitigation. The earlier anomalous +4.99 was the
with-replacement sampling the review flagged.

**A truly stratified anytime-valid gate, and VBC-SG.** The previous "stratified" gate was a
fixed-sample normal LCB; the real thing now exists (per-class empirical-Bernstein confidence
sequences at α/2, sequential looks), plus an exact per-class McNemar baseline, and the assembled
**VBC-SG** policy — commit/reject/**defer** on stratified sequences with a deployment-long alpha
budget (Bonferroni or p-series spending), each proposal's effective α logged, and four
propositions in Methods stating exactly what is and is not guaranteed. The empirical frontier
prices each guarantee layer: under zero drift every risk configuration is fully safe (zero
commits); at full drift on PortScan, pooled EB-CS with deferral captures +6.76, the full
stratified VBC-SG +3.02, a Bonferroni lifetime budget +1.01, and the maximally-stacked p-series
configuration commits nothing at these label budgets — a deployment-long stratified guarantee is
currently unaffordable at b=64, reported plainly.

**The causal table is now a unified window-64 leakage-free matrix.** All three datasets at the
same window size, collisions exactly zero, zero unvalidated commits, the strict reject-ties gate
as a policy column: ToN-IoT gates +4.05 (full) / +4.83 (mild) above naive with strict on par;
PortScan preserved; UNSW's marginal-regime boundary reported as-is; the 128-window sensitivity
retains the same conclusions.

**Operational prevalence, end-to-end lite.** With stream, probe and *all* labels at operating
conditions (π ∈ {0.01, 0.05, 0.10}, labels lagged 5–20 windows), the binding constraint is
upstream of the gate: the KS detector is starved at low prevalence (ToN-IoT 0.03 triggers/stream);
where triggers exist the gate matches or beats naive.

**Editorial.** The abstract's causal claim is narrowed to what the arm shows; the §5.3 opener is
conditioned on the evaluated settings; the P0.5 claims sweep is applied throughout.
