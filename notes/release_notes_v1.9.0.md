## What changed since v1.8.0 (amendment 007 — the seventh external review, fully executed)

**The zero-drift control, and what it does to the thesis.** A reviewer objected that the
mild-drift harm might have nothing to do with drift: replacing a healthy model with a finite
re-estimate introduces variance, and that alone could explain a small negative mean. We
registered the decisive control and ran it: triggers fired at a fixed rate, on streams with
**no drift at all**. He is right — and the result is stronger than the one it displaces.
Always-deploy is significantly net-harmful in all three benchmarks with zero drift
(PortScan −2.76 [−3.76, −2.03], UNSW −0.75, ToN-IoT −4.75 [−8.12, −2.01]), and the commit gate
recovers most of the loss in each. Three consequences, all now in the paper: much of the
mild-drift harm is the *price of replacing a healthy model*, not a drift-specific effect; this
is precisely the account's limiting case (zero headroom ⟹ an update's value cannot be positive),
so the control that could have falsified the account confirms it; and — the sharpest form of the
paper's thesis — **when there is no drift to detect, no monitor, however sensitive, can prevent
this loss. Only validating the candidate can.**

**The causal arm, this time for real.** Our previous "fully causal" arm was not: after every
commit the detector was still recalibrated from the simulator's pools at the true severity, and
since gate and naive commit at different times, that oracle state interacts with the policy. The
review caught it. With observed-only recalibration (`--recal-source observed`) and probes made
**row-identity disjoint** from the candidate's training rows (27–38 shared flows per stream were
being silently reused, because pools are sampled with replacement), the result survives intact:
ToN naive −3.19 → gate +0.67, **+3.86 [1.67, 6.73] above naive**, and still statistically
indistinguishable from the oracle-probe gate in the harm regime. The mild-drift prediction test
now replicates *inside the same causal pipeline*, so both of the paper's central defenses hold in
one experiment.

**Two misstatements of ours, corrected.** We had written that mild-drift harm was "net-harmful in
all three benchmarks" (the CICIDS interval includes zero — the correct statement is *negative in
all three, resolved in two*) and that "the gate stays non-negative" (in UNSW it is 0.09 points
below no-adaptation — inside the registered −0.2 tolerance, but resolved). Our own confidence
intervals contradicted both. Fixed everywhere.

**A sequential probe gate.** Buy 16 labels; stop as soon as the one-sided 90% interval resolves
the sign; buy more only near ties. It spends 51–54 labels per decision and is the best gate we
evaluated in the benefit regime (+9.21), matching the fixed probe elsewhere.

**Also:** Algorithm 1A (core simulation) and 1B (observed data) replace one algorithm that
described neither; Figure 2 is regenerated from a **committed generator** — it had been produced
ad hoc and never versioned, a reproducibility defect in its own right — and now carries wording
the statistics support; the graphical abstract is re-centred on the healthy-incumbent result.
Claims audit: **305 checks**, all passing.
