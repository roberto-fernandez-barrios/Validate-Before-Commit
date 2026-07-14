# Amendment 008 — checkpoint (all runs complete, all outcomes reported)

**Date:** 2026-07-15. Protocol registered at `0beceb2` BEFORE any run. 24 runs, 30 seeds each,
zero failures. Identity check PASS (causal arm reproduces v9 exactly). Audit: 305 → **324/324**.
Builds: 34 pp CAS / 27 pp IEEE.

## A. SIZE-MATCHED ZERO-DRIFT CONTROL — the confound is REFUTED
The reviewer argued the zero-drift harm was a small-candidate artifact (incumbent 2,000/class,
candidate 512/class). Size-matching the candidate to 2,000/class **does not remove the harm**:
naive stays significantly net-harmful (PortScan **−4.81** [−7.68, −2.46], UNSW −0.13 [−0.23,
−0.04], ToN **−5.76** [−9.11, −2.92]) and is usually DEEPER than at 512/class, because repeated
full replacement accumulates estimation noise regardless of sample size. Mirrors the full-drift
size-matching result (−5.34). The harm is not a small-sample artifact.

## B. RISK-AVERSE GATES UNDER ZERO DRIFT — the positive result the reviewer asked for
The plain ε=0 gate reduces but does not eliminate the zero-drift harm (−1.11/−0.56/−0.25) because
it commits on ties. A **risk-controlled** gate does eliminate it: exact McNemar recovers ALL of
the loss (exactly +0.00 in all three; +2.76/+0.75/+4.75 above naive), and LCB (+0.01/−0.06/+0.01)
and the anytime-valid sequential gate (≈0 everywhere) do the same — with no real signal, a
calibrated validator correctly does almost nothing. This is the corrected, complete statement of
"validate before commit": the safeguard is a *risk-controlled* validator, not the ε=0 rule.

## C. DETECTOR-TRIGGERED ZERO DRIFT — the "no monitor can prevent" claim WITHDRAWN
The registered `sev0_none/lp32` arms (real KS-max, zero drift) were run in a007 but not reported.
The real detector fires only 0.07–0.13×/stream, so it mostly avoids the harm by not firing
(naive −0.23/−0.04/−1.03). "No monitor can prevent this loss; only validating prevents it" is
FALSE and withdrawn. Reframed to **candidate governance**: a drift alarm — or a false alarm, or a
scheduled retrain — is a proposal; any proposal reaching deployment should be validated first.

## D. CANDIDATE / FUTURE-EVAL LEAKAGE AUDIT
New counter: candidate-training rows that recur in future evaluation windows (pools sampled with
replacement) = 387–1,529/stream. But the count is essentially EQUAL for gate and naive (both
sliding-window), so the paired gate−naive contrast that carries every claim is unaffected
(c8_gate_vs_naive reproduces v9 exactly: ToN +3.86). Only absolute BA levels of any committing
arm are marginally optimistic, equally. Reported in the causal-table caption.

## E. ANYTIME-VALID SEQUENTIAL GATE
`labeled_probe_seqav`: Bonferroni over K=4 looks (α/K each) — a valid sequential test, replacing
the optional-stopping heuristic. Conservative on normal streams (PortScan +8.04, −1.08 vs fixed
b=32; UNSW +1.00; ToN +0.16), ~58–61 labels/decision, and it is exactly the rule that recovers
the zero-drift loss (B). The risk–label frontier now has a valid procedure at each point.

## F. Two overclaims of ours, corrected
"Net-harmful in all three" → "negative in all three, resolved in two" (done a007, retained).
"Only validating prevents / recovers most of the loss in each" → the ε=0 gate reduces but does
not eliminate; a risk-controlled gate eliminates; the real detector mostly prevents by not
firing. Abstract, conclusion, Table-9 caption and README all rewritten.

## G. Editorial
Headroom reframed conditional on the update generator (update value = Q(h′)−Q(h); headroom is
the second term); the superseded natural-prevalence claim removed from §5.7 (pointer to the
corrected §5.10 result instead of retracting pages later); every "fails safe" deleted; Fig. 3
"identically" → "same sign pattern (magnitudes differ)"; graphical abstract clarified
(registered core vs registered extensions, not a 2×4 factorial); README method/flags synced
(observed recalibration, random triggers, seqav, size flag). Abstract 250 words.
