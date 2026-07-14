# Amendment 008 — size-matched zero-drift control, detector-triggered zero-drift reporting, anytime-valid sequential gate, candidate/future-evaluation leakage audit, and the reframing from "drift" to "candidate governance" (LOCKED before runs)

**Date:** 2026-07-15 · Committed and pushed BEFORE any run below. Trigger: eighth external
review. It identifies a real confound in the zero-drift headline, a reporting omission, two
overclaims that our own intervals contradict, a leakage the row-identity fix did not cover, and
an invalid sequential procedure. All are corrected here; several could weaken the paper and we
report whatever the runs show.

## Confirmed problems (ours), and the fix
1. **The zero-drift harm is confounded with candidate size.** The incumbent trains on 2{,}000
   flows/class; each candidate on 512/class. So the zero-drift result compares a 4{,}000-flow
   model against 1{,}024-flow re-estimates of the *same* distribution --- part of the harm is a
   finite-sample replacement cost, not a property of "updating a healthy model". (A) runs the
   decisive control: zero drift with **size-matched** candidates (2{,}000/class).
2. **Registered detector-triggered zero-drift arms were run but not reported.** `sev0_none` and
   `sev0_lp32` exist in the artifact; the manuscript showed only the random-trigger arms. Under
   the *real* detector at zero drift the trigger fires 0.07--0.13 times per stream, so the
   monitor largely prevents the harm by not firing --- which directly bounds the "no monitor can
   prevent this loss" claim. (B) reports them and the claim is rewritten.
3. **Two overclaims contradicted by our own Table 9.** "No monitor can prevent this loss; only
   validating the candidate can" is false: the well-specified detector mostly prevents it, and
   the gate under zero drift stays significantly *below* no-adaptation in all three benchmarks
   ($-$1.11, $-$0.56, $-$0.25) --- it reduces the harm, it does not prevent it. "Recovers most of
   the loss in each" is false for UNSW (0.19/0.75 = 25%). Corrected in abstract, conclusion,
   Table-9 caption and README, independently of any run.
4. **Candidate-training rows can reappear in future evaluation windows.** The row-identity fix
   (amendment 007) covers probe-vs-candidate only. Streams are pre-generated from pools with
   replacement, so a candidate-training row can recur in $W_{t+1},W_{t+2},\dots$ and the
   candidate is then scored on a row it trained on. (D) instruments the runner to count
   `cand_future_collisions` and re-runs the causal arm; the count is reported and, if material,
   the evaluation excludes those rows.
5. **The sequential gate was not anytime-valid.** Inspecting a fixed-sample 90% interval at
   16/32/48/64 flows inflates the error rate (optional stopping). (E) adds
   `labeled_probe_seqav`: a Bonferroni-over-looks procedure (each of the $K{=}4$ looks tests at
   $\alpha/K$), which is a valid sequential test; the earlier `labeled_probe_seq` is relabelled
   a heuristic. Reported: harmful-commit rate and labels spent for both.

## Seed ledger
- v2 arms: seeds 104--133 on the common streams. New-environment arms (`--max-severity 0`,
  `--adapt-size-per-class 2000`) are their own studies on those seeds.

## A. SIZE-MATCHED ZERO-DRIFT CONTROL (the decisive confound test)
`--trigger-mode random --max-severity 0 --adapt-size-per-class 2000`, arms {none, lp32},
3 regimes (seeds 104--133). **Pre-stated readings (not criteria):** if size-matched naive is
still net-harmful at zero drift, replacing a healthy model is harmful beyond the finite-sample
cost, and the account survives; if size-matched naive is harmless, then the zero-drift harm was
substantially a candidate-size artifact and the manuscript must scope the claim to a fixed
update generator (small full-replacement candidates). Either way reported.

## B. DETECTOR-TRIGGERED ZERO DRIFT (reporting the registered arms)
`sev0_none`, `sev0_lp32` (real KS-max, zero drift) enter Table 9 and the text: the detector
rarely fires (0.07--0.13/stream), so it mostly avoids the harm --- the honest limit on the
"monitor cannot prevent" claim, and the pivot to the candidate-governance framing.

## C. RISK-AVERSE GATES UNDER ZERO DRIFT (the gate's hardest case)
Under `--trigger-mode random --max-severity 0`, arms {lcb64, mcnemar32, seqav64}, 3 regimes.
Zero drift is where ties dominate and the $\varepsilon{=}0$ gate commits on no evidence; a
strict rule should avoid the harm. Reported against the $\varepsilon{=}0$ gate and no-adaptation.

## D. CANDIDATE / FUTURE-EVALUATION LEAKAGE AUDIT
New counter `cand_future_collisions`: for each committed candidate (sliding-window), the number
of its training rows (by exact feature identity) that recur in the evaluation windows after the
commit. Re-run the causal arm {tcausal_none, tcausal_gate}, 3 regimes; the counter is logging-
only (identity check required). If collisions are material, a `--no-future-leak` mode drops
matching rows from future evaluation and Table 8 is re-run; otherwise the count is reported as
evidence the effect is negligible.

## E. ANYTIME-VALID SEQUENTIAL GATE
`labeled_probe_seqav`: draw in blocks of 16 up to 64; at look $k$ compute the one-sided
$(1-\alpha/K)$ normal interval ($K{=}4$, $\alpha{=}0.10$); commit if the LCB $>0$, reject if the
UCB $<0$, else continue; undecided at 64 $\Rightarrow$ reject (the risk-averse default, unlike
the heuristic's point-comparison fallback). Bonferroni over the 4 looks controls the
family-wise error, so the procedure is anytime-valid. Runs: 3 regimes on the normal streams and
under zero drift.

## F. Claims, structure, artifact (no new data)
Reframe the thesis from drift to **candidate governance**: "drift alarms are proposal
generators, not deployment evidence; whatever produces a proposal --- true drift, a false alarm,
or scheduled updating --- the challenger should be validated against the incumbent before
deployment." Rewrite "no monitor can prevent"/"only validating prevents" as conditional
statements; reframe headroom as "under a fixed update generator, recent incumbent health is a
strong ranking feature for update value" (update value $= Q(h')-Q(h)$; headroom is only the
second term). Remove the superseded natural-prevalence claim from the body (\S5.7) rather than
retract it later; delete every remaining "fails safe"; soften Fig.~3's "identically"; rename
Fig.~8's "adversarial" to random label corruption; scope the mild/zero-drift harm headline to
the evaluated SVC-PCA8 update pipeline; keep the chronological-net-harm gap explicit in abstract
and conclusion; and synchronize the README method section (flags: sequential gate, observed
recalibration, random triggers; drop "the fix"; distinguish core-oracle vs observed probe).
