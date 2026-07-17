# Amendment 014 — registered pre-run (Sol 6th round: two artifact-vs-claim gaps + the max-ceiling plan)

Registered before any run. Two blocking discrepancies verified in code (both ours), plus the
first phases of the reviewer's max-ceiling plan. Discipline unchanged.

## Blocking (verified)
1. **The "stratified anytime-valid CS" is not implemented.** `labeled_probe_strat` is a
   fixed-sample per-class normal LCB; the abstract claims "anytime-valid confidence sequences, in
   stratified per-class form". Fix BOTH ways: (a) implement the real thing —
   `labeled_probe_ebcs_strat`: per-class empirical-Bernstein confidence sequence at α/2
   (Bonferroni over classes), sequential looks, commit iff ½(L_ben+L_att) > 0 — and evaluate it
   (zero + full drift, 3 regimes); (b) reword the abstract to name exactly what each gate is.
   **P1:** the stratified EB-CS is safe under zero drift (≈0 commits) and captures large benefit
   at full drift (between the pooled EB-CS and the normal-LCB strat gate).
2. **The symmetric A/B is not disjoint and not role-randomized.** The script draws T/A/B/E with
   replacement and always computes BA(B)−BA(A). Redo: global value-dedup per class, per-seed
   permutation partitioned into four DISJOINT blocks, per-seed random assignment of which model is
   the incumbent, explicit both-direction reporting, full CIs in the table. **P2 (the crux,
   honest):** if the disjoint+randomized control still shows independent-transformer gap ≈ 0 and
   incumbent-fit gap < 0, the representational-advantage mechanism stands; any other outcome is
   reported and the "identified" language is withdrawn to "consistent with".

## Wording (blocking #3–4)
- Abstract "a causal arm ... reproduces it" → "reproduces the harm-regime rescue and the
  qualitative gate-vs-naive ordering" (UNSW-full cell sits below no-adaptation; feasibility caption).
- §5.3 "The answer is not the amount of drift but the state of the deployed model" → "In the
  evaluated fixed-generator settings, incumbent health was more predictive than drift magnitude."
- "mechanism identified" contingent on P2; if it stands, keep with the ToN +4.99 wide-CI caveat in
  the text and the full-CI table shown.

## Max-ceiling plan, phase 2 (novelty items from the review's plan)
3. **Deployment-long risk control.** `--lifetime-alpha A --lifetime-max-proposals M`: each
   proposal's risk gate runs at α = A/M (Bonferroni alpha-spending across the stream's proposals),
   giving an explicit lifetime false-commit bound A. Evaluate EB-CS with A=0.10, M=10 under zero +
   full drift. **P3:** zero-drift safety unchanged; full-drift benefit capture degrades gracefully.
4. **Commit/reject/defer with adaptive acquisition.** `labeled_probe_ebcs_defer`: if the CS is
   undecided at the per-window budget, DEFER — keep the candidate and continue the SAME confidence
   sequence with fresh labels at subsequent windows (anytime-validity permits continuation), up to
   `--defer-windows D`; reject at the cap. Two-sided spending (commit side and futility side at
   α/2). **P4:** deferral recovers part of the small-benefit capture that the one-shot EB-CS
   misses at b=64, at bounded extra label cost.

## Phase 3 (end-to-end lite)
5. **Label latency applied to ALL labels at natural prevalence.** `--all-label-latency L`: the
   candidate trains on the last 8 windows that are ≥L old and the probe comes from window
   t−9−L; stream and detector at π=0.05. One registered run (L=5), 3 regimes, {naive, gate}.
   **P5:** honest outcome reported either way (under imbalance the detector rarely fires; where it
   fires, latency should tax the benefit regimes most). This is the end-to-end-lite step; the full
   scheduling simulator remains out of scope.

## Declared out of scope this round
Chronological harmful-update stream (no dataset exhibits it); 24–28-pp body trim (a dedicated
editorial pass, pending the user's copy of the reviewer's plan file; a stopping rule belongs to
the submission decision, not the harness).

## Output naming
v15 arms `results/raw/paper2_v15_*`; A/B redo `paper2_symmetric_ab_014.py` →
`paper2_amendment_014/symmetric_ab.csv`; aggregator `aggregate_paper2_amendment_014.py`.

## RESULTS (a014: 24 arms + AB-2cond; final-kbs: 54+6 arms + AB-4cond; audit 395 -> 415/415;
## 39 pp CAS / 32 pp IEEE)
- **A/B 4-condition (disjoint, role-randomized) — ALL FOUR identification criteria hold (ToN SVC):**
  independent -1.78 [-7.45,3.92] (~0); incumbent-fit -12.35 [-19.33,-6.45]; challenger-fit +17.77
  [11.00,24.75] (INVERTS); own-transformer +0.05 (ELIMINATED); RF ~0 everywhere. Mechanism =
  transformer ownership, learner-specific. The 013 anomaly (+4.99) was the with-replacement overlap.
- **Causal-64 unified matrix (Table 8 final):** collisions 0, no-probe commits 0 everywhere. ToN
  naive -2.85 full / -4.75 mild -> point gate +4.05 / +4.83 above naive; strict on par (+3.86/+4.78);
  PortScan preserved; UNSW below no-adapt both arms (boundary), gates +0.51-0.64 above naive.
  128-window sensitivity = v14b (same conclusions).
- **VBC-SG frontier:** zero drift = 0 commits in EVERY risk config (safe). Full drift PortScan:
  pooled EB-CS+defer +6.76 [5.10,8.36] (~900 labels); FULL VBC-SG (strat+defer, alpha=0.10/proposal)
  +3.02 [2.09,4.00]; Bonferroni lifetime +1.01; stacked pseries+strat+defer commits nothing at b=64
  (honest: deployment-long stratified guarantee unaffordable at these budgets). exact_strat never
  commits (114-241 labels).
- **e2e prevalence sweep (all labels lagged):** detector starvation at low pi (ToN 0.03
  triggers/stream); pi=0.10 PortScan naive +4.8, gate +4.0; UNSW gate >= naive everywhere.
- Wording: mechanism "identified" now earned under the plan's own 4 criteria; abstract causal claim
  narrowed; VBC-SG + 4 propositions in sec:riskgates; P0.5 sweep done.
  **PENDING:** Fase E (24-28pp trim + supplement + graphical abstract) as a dedicated pass;
  release v1.16.0 (user OK); arXiv Paper 1; submit KBS.
