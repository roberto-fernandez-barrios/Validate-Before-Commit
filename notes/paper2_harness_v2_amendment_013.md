# Amendment 013 — registered pre-run (Sol 5th round: guarantee, Table 8, dedup, calibration, A/B)

Registered before any run. Executes the full tractable menu of the fifth review plus the decisive
symmetric-preprocessing control. Discipline unchanged.

## Blocking
1. **Stratified guarantee.** The probe has FIXED class quotas (b/2 benign + b/2 attack), so the CS
   / exact-McNemar assume an i.i.d. single-distribution mean but the target is balanced accuracy
   ΔBA = ½ΔAcc_benign + ½ΔAcc_attack. Add stratified gates that bound ΔBA honestly: a per-class
   lower confidence bound at α/2 (Bonferroni over the two classes), ΔBA_lb = ½(L_ben + L_att),
   commit iff ΔBA_lb > 0. Gate `labeled_probe_strat` (normal LCB per class) and, for the CS,
   `labeled_probe_ebcs_strat`. Also soften abstract to "risk-controlled under the assumed
   probe-sampling process". **P1:** the stratified gate is safe under zero drift (≈0 commits) and
   recovers benefit under full drift comparable to the pooled gate.
2. **Table 8 superseded.** Replace the causal table with the FINAL leakage-free +
   `no-probe-policy=reject` results (full + mild), collisions ≈0; move the old leaky numbers and
   the "unaffected" caption to the amendment note / supplement.
3. **Global dedup (make collisions exactly 0).** The disjoint stream deduped per-pool and
   reshuffled on exhaustion. Add a GLOBAL consumed-hash set across all four pools, assert on
   exhaustion (never silently reuse), and a test asserting exactly 0 candidate/future collisions.
   Re-run the causal arm; **P2:** collisions == 0 and the result is unchanged from the ≈0 version.

## Experiments (tractable)
4. **Detector recalibration min-windows.** `calibrate_observed` may use only 2–3 scores at early
   commits. Add `--min-calib-windows` (keep the previous threshold until the minimum is available);
   sweep {8,16,30} on the causal arm. **P3:** the causal harm-regime result is stable across the
   minimum (no dependence on unstable early recalibration).
5. **Strict-`>` baseline outside zero drift.** Run the reject-ties rule at mild and full drift, 3
   regimes, and add it to the frontier. **P4:** at full drift strict ≈ ε=0 (both capture benefit);
   at mild drift strict reduces the small harm like ε=0 does — i.e. rejecting ties is a cheap
   Pareto point, and we report it as such (the ε=0 "accuracy-maximizing" label is corrected to
   "point-estimate-maximizing on the probe").

## Decisive mechanism control
6. **Symmetric A/B preprocessing (replacement-variance test).** Standalone experiment
   `paper2_symmetric_ab_013.py`: fit scaler+PCA on an INDEPENDENT partition; train two models A, B
   on two disjoint equal-size samples of the SAME (zero-drift) distribution with that shared
   independent transformer; randomly assign incumbent; measure BA(incumbent) vs BA(challenger) on
   held-out windows, both directions, over seeds. **P5 (the crux):** if the challenger is still
   systematically worse under full symmetry, replacement variance is confirmed as the mechanism; if
   A and B are exchangeable (mean gap ≈ 0), the earlier zero-drift harm was the frozen-transformer
   / initial-sample asymmetry and we say so. Either outcome is reported plainly.

## Editorial
- Highlights + graphical-abstract + abstract: qualify the mild/zero harm as SVC-RBF-specific.
- Remove "makes readaptation safe" (§5.6) and the `notably,significantly` typo if present in build.
- Size-matched RF/LogReg/MLP numeric table (recommended item).

## Out of scope (declared)
- End-to-end operational-prevalence + candidate-label-latency; chronological harmful-update stream
  (no such dataset); 25–30% body trim (editorial; risks desyncing the 380 audited numbers — we
  instead relabel the superseded material and point the reader to the final results).

## Feasibility disclosure (found BY the new exhaustion assert — reported, not hidden)
The exact-zero-collision stream (global value-dedup + no replacement + abort-on-exhaustion) has
hard pool-size limits that the old silent-reshuffle code masked:
- PortScan **mild** and UNSW **full** exhaust an attack pool at the default window share (0.5).
  Fix: `--disjoint-window-frac` (causal arms use 0.75; UNSW 0.9) — sound because the causal arm
  draws candidates/probes from STREAM windows (pool `probe` unused, `train` = initial model only).
- UNSW **full** remains infeasible even at frac 1.0: `cur_attack` has only **2,664 unique rows**
  vs ~3,900 needed at window 128. Final UNSW-full config: **window-size 64** (needs ~1,950 ≤
  2,664) at frac 0.9. Internally paired (naive vs gate share the identical stream); disclosed in
  the Table-8 caption.

## Output naming
v14 arms `results/raw/paper2_v14_*`; final causal arms `paper2_v14b_*` (frac 0.75; UNSW 0.9,
UNSW-full window 64); `aggregate_paper2_amendment_013.py`; `paper2_symmetric_ab_013.py`;
Table-8 emitter `make_paper2_causal_final_table.py`.

## RESULTS (18 v14b + 12 v14 arms + symmetric A/B, 0 unexplained failures; audit 380 -> 395/395;
## 38 pp CAS / 30 pp IEEE)
- **Table 8 REPLACED with the final leakage-free arm.** Collisions EXACTLY 0 and commit_no_probe 0
  in every cell. ToN gate-naive **+5.57 [3.19,8.30]** full / **+4.21 [0.95,8.45]** mild; PortScan
  +0.41 [0.19,0.63]; UNSW-full (window-64 cell) both arms below no-adapt, gate still +0.51
  [0.18,0.87] above naive (reported as-is). Trajectory disclosed in one consolidation paragraph
  (+3.86 leaky -> +2.95 -> +3.24 -> +5.57); intermediate numbers live in the amendment notes only.
- **Calibration sweep {8,16,30}: stable** (ToN 5.44-5.57, PortScan 0.40-0.44) -> the causal result
  does not depend on early-recalibration instability.
- **Stratified gate (guarantee matched to the fixed-quota probe):** zero-drift 0 commits in all 3;
  full drift PortScan +6.93, UNSW +0.32, ToN +0.10 -> honest price of the aligned guarantee.
- **Strict-> outside zero drift:** full PortScan +8.78 (vs eps0 +9.12), UNSW +1.41, ToN +0.60;
  mild non-negative -> genuine zero-cost Pareto point; added to §5.
- **SYMMETRIC A/B (the decisive mechanism control): Sol was right.** Independent transformer ->
  gap B-A ~ 0 or positive (ToN +4.99, UNSW 0.00, PortScan -1.90 n.s.); incumbent-fit transformer
  -> harm reproduced (ToN **-10.45 [-16.2,-5.3]**, PortScan -3.64, UNSW -0.18). The zero-drift
  harm is NOT replacement variance; it is the incumbent's representational advantage from the
  frozen feature pipeline. Mechanism IDENTIFIED (better than a hypothesis); manuscript §5 +
  Limitations rewritten accordingly; per-challenger preprocessing named as the mitigation.
- Editorial: "makes readaptation safe" conditioned; eps0 relabeled point-estimate-maximizing;
  highlights + abstract SVC-RBF caveat; abstract CS "under the assumed probe-sampling process".
  **PENDING (user):** release v1.15.0 authorization; arXiv Paper 1; submit KBS.
