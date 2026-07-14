# Amendment 006 — causal observed-data gate, honest natural-prevalence probes, per-incumbent health reference, risk-controlled gate, and a falsifiable prediction test for net harm (LOCKED before runs)

**Date:** 2026-07-14 · Committed and pushed BEFORE any run below. Trigger: sixth external mock
review. Three code-level defects it identified are CONFIRMED and corrected here; two new
experiments target the two things the paper genuinely cannot yet claim.

## Confirmed defects (verified in the code, corrected by this amendment)
1. **The probe is not drawn from observed traffic.** `run_arm` builds it with
   `sample_balanced_from_distribution(env.probe_pools, ..., severity=sev)` — a fresh, balanced,
   class-guaranteed sample from the simulator's mixture at the TRUE current severity. So does
   the candidate. Both use information a deployment does not have. (A) below removes it.
2. **"Natural prevalence" probes force a minority-class flow.**
   `sample_prevalence_from_distribution` uses `n_att = max(1, round(n·π))`: at π=0.01, b=32 a
   genuine random draw would contain zero attacks ~72% of the time; the runner always supplies
   exactly one. The Phase-2j claim ("the probe need not be balanced; full safety/benefit at
   π=0.01") is therefore NOT demonstrated. (B) below re-tests it honestly; the claim is
   retracted from the manuscript regardless of outcome.
3. **`health_ref` is never recalibrated.** The two-stage gate measures the CURRENT incumbent's
   health against the INITIAL model's severity-0 reference; after the first commit it is
   comparing different models. (C) below fixes it.

## Seed ledger
- v2 arms (A–F): seeds 104–133 on the pre-generated common streams (paired extensions,
  descriptive unless stated). Mild-drift arms (E) use new environments (different
  `--max-severity`) on the same seeds — a different stream family, reported as its own study.
- Chronological Wednesday→Thursday (G): smoke 400; confirmatory 401–430.

## A. CAUSAL OBSERVED-DATA GATE (the review's top ask; confirmatory for the deployability claim)
New flag `--probe-source {pools, observed}`. With `observed`, at a trigger at window t:
- the candidate trains ONLY on the last 8 observed stream windows (`--adapt-strategy
  sliding_window`, already implemented; no severity, no pools);
- the probe is 32 rows sampled uniformly at random from the OBSERVED window t−9 (strictly past;
  disjoint from the candidate's training windows by construction; whatever class composition
  that window happens to have; no severity, no class balancing, no pool resampling);
- the commit rule compares plain accuracy on that probe (defined for any composition).
No component of the arm reads `sev(t)`. Runs: 3 regimes × {sliding+none, sliding+observed
probe} (KS-max, seeds 104–133). **Pre-stated criteria (locked):** the account survives if, in
the harm regime, the observed-probe gate (i) is significantly above the observed-candidate
naive arm and (ii) is not significantly below no-adaptation. If it fails, the manuscript reports
that the gate's benefit depends on oracle-quality probes — as the headline caveat.

## B. HONEST NATURAL-PREVALENCE PROBES
New flag `--probe-prevalence π` drawing `n_att ~ Binomial(b, π)` — **zero attacks allowed**
(new `sample_binomial_prevalence`); when a probe contains one class only, the gate compares
plain accuracy on it (no fallback to balance, no re-draw). Runs: π ∈ {0.10, 0.05, 0.01} × 3
regimes (balanced evaluation streams so triggers still occur; KS-max, lp32, seeds 104–133).
Reported: gate gain, the fraction of probes containing zero attacks, and the expected number of
random inspections needed to obtain one attack flow (1/π). The Phase-2j "π=0.01 is fine" claim
is retracted and replaced by whatever this shows.

## C. PER-INCUMBENT HEALTH REFERENCE
New flag `--health-ref-mode {static, per_incumbent}`. `per_incumbent`: on every commit the
health reference is reset to the newly deployed model's accuracy on the commit half of the same
probe (already labeled — zero extra cost). Runs: 3 regimes, two-stage split, δ=0.05.

## D. RISK-CONTROLLED GATE (exact test instead of a point comparison)
New gate `labeled_probe_mcnemar`: commit iff an exact one-sided McNemar test on the probe's
discordant pairs (candidate right / incumbent wrong vs the reverse) rejects at α=0.05 —
i.e. commit only on statistically resolved superiority, ties never commit. Runs: 3 regimes,
b=32 and b=64, KS-max, seeds 104–133. Reported alongside ε=0 and LCB as the risk axis of the
policy frontier.

## E. FALSIFIABLE PREDICTION TEST — does the account predict WHERE net harm appears?
The degradation--headroom account makes a prediction we have never tested: *net harm is a
function of incumbent health, not of the dataset*. Lower the drift severity and the incumbent
stays healthier; the account predicts the value of updating falls, and that benefit regimes
should move toward zero or below. We therefore run the SAME three regimes at
`--max-severity ∈ {0.25, 0.50}` (all else identical), arms {none, lp32}, KS-max, seeds 104–133.
**Locked prediction (registered before the runs):** at max-severity 0.25, naive updating's gain
in the CICIDS PortScan benefit regime falls below +1.0 BA point, and in at least one of the
three regimes naive becomes net-harmful (mean gain < 0) while the gate stays ≥ −0.2. If PortScan
retains a large gain, or the gate fails to protect wherever harm appears, the prediction is
FALSIFIED and reported as such — this is a genuine risk to the paper's central account.

## F. HARM BREADTH ON THE HARDENED HARNESS
The v1 study found naive harm in two further ToN-IoT regimes (DDoS $-$16.81, Injection $-$1.21)
under the old harness. Re-run on v2: ToN-IoT DDoS and Injection × {none, lp32}, KS-max, seeds
104–133. Whatever it shows is reported; if harm does not replicate, the harm claim narrows to
Scanning.

## G. CHRONOLOGICAL HARM ATTEMPT (the missing external test)
ToN-IoT ships no usable timestamp in the staged capture, so a ToN chronological stream is not
possible. Instead we invert the CICIDS setup to engineer a healthy incumbent: train on
**Wednesday** (DoS/DDoS-rich) and replay **Thursday** (WebAttacks → Infiltration; sparse,
mild attacks) in true temporal order. A Wednesday-trained model should stay comparatively
healthy on Thursday, and candidates retrained on nearly-benign observed windows may be worse —
the chronological analogue of the harm regime. Arms {none, labeled_probe}; seeds 401–430
(smoke 400). Any outcome reported, including another benefit regime.

## H. Claims, structure and artifact (no new data)
Retract the natural-prevalence claim (pending B); describe the core probe as an oracle-quality
sample from the simulator's current mixture and reserve "drawn from current traffic" for the
observed-probe arm; call the temporal experiments "chronologically ordered subsampled replay";
split the evidence explicitly into *registered confirmatory core* (criteria A/B/C/I),
*registered extensions*, and *exploratory* (v1); soften the remaining universal detector claims
("the wrong control variable" → "not a sufficient commit signal under the evaluated monitors");
present the utility scenarios as illustrative; move superseded v1 material to the appendix;
synchronize README (it still says "predicts nothing" and "identically"), REPRODUCE (amendment
005 missing), and the artifact title.
