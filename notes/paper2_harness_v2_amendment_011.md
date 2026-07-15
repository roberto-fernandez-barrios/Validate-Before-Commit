# Amendment 011 — registered pre-run (Sol's 3rd-round review: leakage, guarantee scope, overclaims)

Registered before any run. Same discipline: protocol + predictions fixed first, smoke before full,
negatives reported as negatives, no re-tuning to force a sign. Addresses the blocking and
recommended items of the third review.

## Blocking items and how each is discharged
1. **Leakage-free causal arm (top blocker).** New `--stream-disjoint-windows`: every stream window
   is drawn WITHOUT replacement within the window pool (train/probe pools are already ID-disjoint,
   `split_pools`), so no original row appears in more than one window and a candidate-training row
   can never recur in a future evaluation window. Streams stay bit-identical across arms (env
   depends on seed + flag only). Re-run the causal Table 8 (observed arm, full drift) and the
   mild-drift causal, verify `cand_future_collisions` → ~0, and check the paired gate−naive
   contrast is preserved. **Prediction P1:** collisions drop to ~0 and the causal gate−naive
   contrast stays within CI of the leaky version (leakage was symmetric, as argued) — if the sign
   or significance flips, that is a reportable correction.
2. **CS guarantee scope (method).** State formally: the confidence sequence controls the
   per-proposal probability of falsely establishing positive expected paired correctness ON THE
   PROBE DISTRIBUTION; translating to future ΔBA needs probe representativeness. Manuscript-only.
3. **Lifetime vs per-proposal risk.** Clarify the CS/McNemar process restarts per challenger
   (per-proposal α); a stream with M proposals has a union bound ≤ Mα. Report the empirical
   per-stream harmful-commit rate from the trigger logs, and state a global alpha-spending option.
   Analysis + method text.
4. **"every update generator" overclaim.** Abstract + text: calibrated ensemble on PortScan is the
   exception (+0.84). Manuscript-only.
5. **Full Methods spec of the CS gates** (Robbins + EB): random variable, α, stopping rule, looks,
   behaviour at 64 labels, assumptions. Manuscript-only.
6. **Separate ε=0 (accuracy-max) from risk-controlled gate** in abstract/method/conclusion.
7. **Soften universal headroom / detector-score claims** ("predicts nothing" → "no consistent
   association at triggered decisions"; "benefit is essentially headroom" → conditional on the
   candidate generator).
8. **Editorial:** `notably,significantly` typo; Fig 5 title "adversarial" → "random label
   corruption"; §5.6 "make readaptation safe" → operating-point-specific; purge "never sacrificing
   benefit"; Fig 2 "predicts nothing".

## Recommended (optional — the user asked for all of it)
R1. **Cumulative controls**: add `initial+observed` (initial training set + all observed windows),
   `dedup` (row-identity dedup before fit), and `C~1/n` (SVC C scaled by n) variants; report unique
   sample counts. Soften the "just use more data" claim to the tested-implementation scope.
   **Prediction P2:** dedup/initial+observed reduce but do not remove the zero-drift replacement
   harm (if any variant becomes SAFE, that is an important boundary and is reported as such).
R2. **CS budget sweep > 64** (probe 128, 256) to quantify when EB-CS recovers the 1-point UNSW/ToN
   benefits. **Prediction P3:** EB-CS gain rises with budget and resolves the ~1-point benefits by
   b≈128–256, evidencing the "label budget is binding" reading.
R3. **CS empirical coverage test**: standalone simulation measuring the CS false-positive
   (harmful-commit) rate under iid, sampling-without-replacement, autocorrelated, and stale-probe
   regimes vs the nominal α. **Prediction P4:** iid coverage ≤ α; stale/autocorrelated can exceed α
   (probe-representativeness caveat made quantitative).
R4. **Per-stream harmful-commit rate + global alpha-spending** (blocking #3 analysis).

## Out of scope (declared)
- Full end-to-end operational-prevalence + candidate-label-latency simulation (needs a scheduling
  rewrite); named as future work.
- Moving v1/amendments to a supplement: a large structural change; we improve labeling instead of
  risking a reorganization that could desynchronize the audited numbers.

## Output naming
v12 arms `results/raw/paper2_v12_*`; aggregator `aggregate_paper2_amendment_011.py`; coverage sim
`paper2_cs_coverage_011.py`. Every new number added to `audit_paper2_claims.py`.

## RESULTS (33 arms + coverage sim, 0 failures; audit 350 -> 367/367; 37 pp CAS / 29 pp IEEE)
- **Leakage-free causal (blocker #1): FIX WORKS, RESULT SURVIVES.** `--stream-disjoint-windows`
  (value-deduped, no-replacement) drops `cand_future_collisions` from 387--1319 to 0.2--1.1. The
  ToN-IoT harm-regime rescue survives: gate$-$naive **+2.95 [1.53,4.50]** full (vs +3.86 leaky),
  **+1.40 [0.29,2.87]** mild. Honest change: PortScan's benefit-regime premium (+0.95 leaky) was
  partly leakage; now $-$0.06 [$-$0.33,0.18] (immaterial: pure-benefit regime). P1 confirmed.
- **Cumulative controls (rec #1-3): none removes the harm, refutes the confounds.** dedup (100%
  unique) DEEPENS it (ToN $-$9.46$\to-$10.74, PortScan $-$7.04$\to-$11.36); cn ($C\sim n$) leaves it
  ($-$10.65/$-$9.73); initial+observed attenuates ($-$8.27/$-$5.14) and flips UNSW positive
  (+0.53). Observed cumulative is 76-83% unique. -> replacement variance, not duplication/reg.
- **EB-CS budget sweep (rec #6): budget is the binding constraint.** PortScan +5.17$\to$+7.31(128)
  $\to$+8.07(256); UNSW +0.00$\to$+0.12$\to$+0.78 (resolves small benefit by 256); ToN full
  +0.00$\to$+0.12. 63/124/239 labels/decision. P3 confirmed.
- **Harmful-commit rate (blocker #3):** $\varepsilon{=}0$ gate commits harmful on 37-70% of streams
  (15-32% of commits harmful); McNemar/EB-CS = 0 harmful/stream. Grounds per-proposal-vs-lifetime.
- **CS coverage (rec #5):** iid/no-replace false-commit $\le$0.002 (both sequences); EB EXCEEDS
  nominal under autocorrelation (0.18 vs 0.10) -> probe-representativeness caveat made quantitative.
- **Manuscript:** new Methods subsection `sec:riskgates` (formal guarantee scope: false
  probe-superiority, per-proposal, not future dBA); causal paragraph + generalization paragraph +
  CS paragraph + Limitations updated; abstract overclaim fixed (ensemble exception, eps0 vs
  risk-controlled); "predicts nothing"->"no consistent association"; headroom conditional; Fig 8
  title "adversarial"->"random label corruption" (regenerated); sign-vs-magnitude; cs-budget/
  harmful-commit/coverage integrated; cites howard2021timeuniform + waudbysmith2023betting.
  **DECLINED (judgment):** title change and full v1->supplement restructure (risk > reward;
  labeling improved instead). **PENDING (user):** arXiv Paper 1, submit KBS.
