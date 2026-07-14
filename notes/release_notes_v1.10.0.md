## What changed since v1.9.0 (amendment 008 — the eighth external review, fully executed)

**The zero-drift confound, refuted.** The reviewer's strongest objection was that the zero-drift
harm might be a small-candidate artifact: the incumbent trains on 2,000 flows/class, each
candidate on 512. We size-matched the candidates to 2,000/class and re-ran. **The harm stays,
and usually deepens** (PortScan −4.81, ToN-IoT −5.76, UNSW −0.13, all statistically resolved):
repeated full replacement accumulates estimation noise regardless of sample size. Not an
artifact.

**The positive result the review asked for: risk-averse gates under zero drift.** The plain
ε=0 gate reduces the zero-drift harm but does not eliminate it (−1.11/−0.56/−0.25) — it commits
on ties, and with no drift, ties dominate. A **risk-controlled** gate does eliminate it: the
exact-McNemar gate recovers *all* of the loss (+0.00 in all three benchmarks; +2.76/+0.75/+4.75
above naive), as do the LCB and the new anytime-valid sequential gate. This is the corrected,
complete statement of the paper's thesis: when there is genuinely nothing to gain, a properly
calibrated validator does nothing.

**Two overclaims of ours, withdrawn.** (1) "No monitor can prevent this loss" was contradicted
by our own registered arms, which we had run but not reported: with the *real* detector at zero
drift the trigger fires only ~0.1 times per stream, so a well-specified monitor mostly avoids the
harm by not firing. The claim is withdrawn and the thesis reframed as **candidate governance** —
a drift alarm (or a false alarm, or a scheduled retrain) is a *proposal*, and any proposal
reaching deployment should be validated before it replaces the incumbent. (2) "Only validating
prevents the loss / recovers most of it in each" — the ε=0 gate only reduces it; corrected.

**An anytime-valid sequential gate.** The earlier sequential heuristic inspected a fixed-sample
interval at each look (optional stopping). The new `labeled_probe_seqav` spends α/K at each of
K=4 looks (Bonferroni over looks), a valid sequential test. It is the conservative end of the
risk–label frontier and the rule that recovers the zero-drift loss.

**A leakage audit.** Candidate-training rows recur in later evaluation windows (387–1,529 per
stream, because pools are sampled with replacement) — but equally for the gate and naive arms, so
the paired contrast that carries every claim is unaffected (the causal result reproduces v9
exactly). Reported.

**Editorial.** Headroom reframed as conditional on the update generator (update value =
Q(candidate) − Q(incumbent); headroom is only the second term); the superseded natural-prevalence
claim removed from the body rather than retracted pages later; every "fails safe" deleted;
Figure 3's "identically" softened to "same sign pattern"; README and flag list synchronized.
Claims audit: **324 checks**, all passing.
