## What changed since v1.7.0 (amendment 006 — the sixth external review, fully executed)

**The oracle-probe objection is answered, not disclosed.** The review's strongest point was
that the core harness hands the candidate and the probe a sample drawn from the simulator's
pools at the TRUE current severity — information no deployment has. A registered causal arm
removes it entirely: the candidate trains only on the last eight **observed** stream windows,
and the probe is 32 rows of the **observed** window t−9 (natural composition, no severity, no
pools). Both locked criteria pass: naive updating is still net-harmful (ToN −2.44 [−4.11,
−0.92]), the causal gate still converts it to a net gain (+0.85 [0.57, 1.13]; +3.29 above
naive), and it is **statistically indistinguishable from the oracle-probe gate** in the harm
and marginal regimes. The mechanism does not need the simulator.

**A registered prediction — and it holds, generalizing the paper's most novel result.** The
degradation–headroom account predicts that harm is a property of *incumbent health*, not of a
dataset: lower the drift severity, keep the incumbent healthy, and updating should turn harmful
even in "benefit" regimes. We locked that prediction publicly, then ran it. **At mild drift,
always-deploy is net-harmful in all three benchmarks** — CICIDS-PortScan (−0.46), UNSW-NB15
(−0.15) and ToN-IoT (−0.65) — while the gate stays non-negative and significantly above naive in
every one. Harmful updating is no longer one constructed cell. Harm also broadens at full drift:
two further ToN-IoT regimes (DDoS −15.24, Injection −2.24), both rescued by the gate.

**A claim we retract.** "The probe need not be balanced; it retains full safety and benefit at
π=0.01" was an artifact: the sampler forced one attack flow into every probe. With honest
Binomial composition, **66–74% of 32-flow probes at π=0.01 contain no attack at all** and the
harm-regime guarantee dissolves (+0.21 [−1.39, 1.15]). The corrected claim: the gate tolerates
genuinely random inspection down to π≈0.05; below that the probe must be enriched.

**The risk axis.** An exact one-sided McNemar gate is never harmful but has almost no power at
32 labels (0.03 commits/stream) and forfeits most of the benefit. The lesson: *the label budget,
not the decision rule, is the binding constraint.*

**Also:** the two-stage health reference is now recalibrated per incumbent (conclusions
unchanged); a fifth chronological replay (Wednesday→Thursday) again collapses the incumbent, so
chronological net-harm remains unobserved and is stated as such; evidence is now explicitly
tiered (registered confirmatory core / registered extensions / exploratory); the temporal
experiments are called "chronologically ordered subsampled replays"; utility scenarios are
framed as illustrative; README, REPRODUCE and the BibTeX title are synchronized with the
manuscript. Claims audit: **278 checks**, all passing.
