# CHECKPOINT — Confirmatory symmetric-pipeline replication

Date: 2026-07-22
Branch: `feature/symmetric-pipeline-replication` (no merge, no push, no tag, no release).

## A. Frozen protocol

- Protocol: `notes/paper2_symmetric_pipeline_dynamic_protocol_001.md`, commit `8838566`.
- Appendix A (margins + machine-evaluable A/B/C rules): commit `96576bb`, frozen and
  committed BEFORE any confirmatory seed ran.
- Config: `configs/symmetric_pipeline_dynamic_v1.json`,
  sha256 `52794778...893d40e8` (unchanged since `bd6bcbb`).
- Margins: BA equivalence ±0.5 pp (sens. ±0.2/±1.0, CI90 fully inside); attack-recall NI
  −1.0 pp (sens. −0.5/−2.0, one-sided 95% lower bound); FPR NI +0.5 pp (sens. +0.25/+1.0,
  one-sided 95% upper bound). BA determines A/B/C; recall/FPR restrict safety language.
- Families: F1 (3), F2 (3), F3 (6), F4 (12) — Holm FWER within family, deterministic
  centered paired bootstrap (100k, seed base 20260721, reused from the published module),
  t-test/Wilcoxon sensitivities. Inferential unit = seed.
- Critical cells (A.2): ton_full, ps_zero, unsw_zero, ton_zero. Benefit cells: ps_full,
  unsw_full.
- Confirmatory seeds: 3001-3030, authorized for this phase only, executed via
  `--run --confirmatory-authorized`.

## B. Execution

- Expected arms: 42. Completed: **42/42** (`--validate-complete` → COMPLETE).
- Seeds: 3001-3030 in every arm (30/30 verified in every by_seed and run_config).
- Total runtime: **77.6 min** (sum of per-arm durations; sequential, synchronous, zero
  background processes). Retries: **0**. Failures: **0**.
- All 42 arms ran at source commit `a33837f` (uniform; recorded per-arm in
  run_config.json). Outputs: `results/raw/symmetric_pipeline/sp_*/` with the 3 runner CSVs
  (+ trigger/resolution logs for policy arms), run_config.json, command.txt,
  environment.json, raw_stream_hash.txt, completion_marker.json.
- Pre-flight gates and fixes (commits `96576bb`, `29c55c6`, `a33837f`) recorded in
  `notes/symmetric_pipeline_confirmatory_preflight.md`: pytest 87/87, audit 538/538,
  hashes 164/164, sealed manifest byte-identical after pytest (side effect fixed),
  provenance metadata complete + 3 new tests.

## C. Pairing and provenance

- Raw-stream identity: within every scenario the 7 arms share an identical
  `raw_stream_hash.txt` (byte-level) — **PAIRED, 6/6 scenarios**.
- Candidate-batch identity, probe identity, frozen semantics, own-refit-on-same-batch,
  detector `frozen_initial` policy, leakage disjointness: enforced by the T1-T12 +
  provenance test suite (19 tests green at execution commit).
- Pipeline provenance recorded per candidate: transformer policy, training-row hash,
  scaler object/mean_/scale_ hashes, PCA components/explained-variance hashes, PCA dim,
  classifier params, SVC configured gamma ('scale') and fitted effective gamma,
  creation window, deployed version.
- Detector: KS-max only; representation = initial transformer under both policies.

## D. Primary contrasts (full drift; effect in BA pp, Holm-adjusted)

| Contrast | effect | CI95 | p_holm | verdict |
|---|---|---|---|---|
| ps_full own-naive vs never | **+7.21** | [4.89, 9.52] | 3e-5 | naive BENEFICIAL |
| unsw_full own-naive vs never | **+2.55** | [2.34, 2.75] | 3e-5 | naive BENEFICIAL |
| ton_full own-naive vs never | **+1.03** | [0.55, 1.53] | 5e-5 | naive BENEFICIAL (published frozen harm −1.97 does NOT persist) |
| ps_full own-naive vs frozen-naive | +0.90 | [0.26, 1.75] | 0.019 | own > frozen |
| unsw_full own-naive vs frozen-naive | +1.15 | [0.95, 1.35] | 3e-5 | own > frozen |
| ton_full own-naive vs frozen-naive | **+5.98** | [3.82, 8.26] | 3e-5 | ownership = major amplifier |
| ps_full own-point vs own-naive | +0.19 | [−0.06, 0.41] | 0.41 | ns |
| ps_full own-strict vs own-naive | +0.05 | [−0.33, 0.41] | 0.96 | ns |
| unsw_full own-point vs own-naive | −0.21 | [−0.36, −0.06] | 0.038 | small significant COST |
| unsw_full own-strict vs own-naive | −0.15 | [−0.35, 0.05] | 0.44 | ns |
| ton_full own-point vs own-naive | **+0.64** | [0.26, 1.06] | 0.015 | gate win (≥ +0.5) |
| ton_full own-strict vs own-naive | +0.18 | [−0.31, 0.67] | 0.96 | ns |

Equivalence (CI90 within ±0.5): none of the own-naive-vs-never or own-vs-frozen full-drift
contrasts is equivalent to zero (all are positive effects).

## E. Zero-drift contrasts (F4, all 12 rows, Holm within family)

| Contrast | effect | CI95 | p_holm | sig |
|---|---|---|---|---|
| ps_zero own-naive vs never | **−1.74** | [−2.35, −0.96] | 5.6e-4 | ✓ MATERIAL harm |
| unsw_zero own-naive vs never | **−0.65** | [−0.77, −0.55] | 1.2e-4 | ✓ MATERIAL harm |
| ton_zero own-naive vs never | −0.38 | [−0.53, −0.25] | 1.2e-4 | ✓ harm, sub-material (< 0.5), NOT equivalent either (CI90 [−0.50, −0.27]) |
| ps_zero own-point vs own-naive | **+0.75** | [0.41, 1.16] | 2.2e-3 | ✓ gate win |
| unsw_zero own-point vs own-naive | +0.19 | [0.09, 0.31] | 7.1e-3 | ✓ (sub-material) |
| ton_zero own-point vs own-naive | +0.11 | [0.03, 0.20] | 0.023 | ✓ (sub-material) |
| ps_zero own-strict vs own-naive | **+1.68** | [1.23, 2.13] | 1.2e-4 | ✓ gate win |
| unsw_zero own-strict vs own-naive | **+0.51** | [0.38, 0.64] | 1.2e-4 | ✓ gate win (guardrail-restricted, see F) |
| ton_zero own-strict vs own-naive | +0.34 | [0.20, 0.49] | 2.4e-4 | ✓ (sub-material) |
| ps_zero own-naive vs frozen-naive | +2.36 | [0.81, 4.20] | 0.023 | ✓ own less harmful |
| unsw_zero own-naive vs frozen-naive | +0.03 | [−0.04, 0.10] | 0.45 | ns (equivalent within ±0.5) |
| ton_zero own-naive vs frozen-naive | **+5.49** | [2.94, 8.76] | 4.4e-3 | ✓ own less harmful |

## F. Security metrics (gate vs naive, own-transformer; NI = principal margins)

| Cell | ΔBA | Δrecall (lo95) | ΔFPR (hi95) | recall NI | FPR NI |
|---|---|---|---|---|---|
| ton_full point | +0.64 | −0.43 (−0.71) | −1.71 (−0.93) | PASS | PASS |
| ps_zero point | +0.75 | −0.02 (−0.07) | −1.53 (−0.93) | PASS | PASS |
| ps_zero strict | +1.68 | +0.02 (−0.02) | −3.33 (−2.60) | PASS | PASS |
| unsw_zero point | +0.19 | −0.63 (−0.92) | −1.00 (−0.62) | PASS | PASS |
| unsw_zero strict | +0.51 | **−0.99 (−1.26)** | −2.00 (−1.63) | **FAIL** (passes lax −2.0) | PASS |
| ton_zero point | +0.11 | −0.13 (−0.20) | −0.35 (−0.18) | PASS | PASS |
| ton_zero strict | +0.34 | +0.10 (−0.07) | −0.57 (−0.27) | PASS | PASS |

Trade-off language: `unsw_zero strict` buys +0.51 BA and −2.0 FPR at the cost of ~1.0 pp
attack recall (one-sided lo95 −1.26 < −1.0) → NO "security improvement" language for that
cell; describe the recall/FPR trade-off explicitly. All other winning cells pass both
guardrails. (Full-drift benefit cells: ps_full strict and unsw_full point/strict fail the
FPR NI — irrelevant to the A-claim since those cells show no BA win.)

## G. Future harm (descriptive; commits cluster within seed — no independence assumed,
no binomial bound derived)

- Own-naive commits remain frequently harmful at h5: ps_zero 65% (65/100 evaluable),
  unsw_zero 61%, ton_zero 46%, ton_full 42%, ps_full 37%, unsw_full 25%.
- Frozen-naive comparison (h5): ton_full 49% → own 42%; ps_zero 61% → 65%;
  unsw_zero 53% → 61%; ton_zero 51% → 46% — bad proposals are NOT eliminated by
  ownership (mean harm shrinks, tail persists).
- Strict slashes exposure: commits ps_zero 104→14, unsw_zero 104→20, ton_zero 104→5.
- Censoring at h10: ≤11 commits per cell (right-censored at stream end), reported per cell
  in harmful_commit_summary.csv.

## H. Decision (Appendix A applied literally)

- **A1** material harm in ≥1 critical cell: **TRUE** (ps_zero −1.74, unsw_zero −0.65;
  CI95 excludes 0, Holm-significant).
- **A2** gate win ≥ +0.5 Holm-significant in ≥1 critical/benefit cell: **TRUE**
  (ton_full point +0.64; ps_zero point +0.75; ps_zero strict +1.68; unsw_zero strict
  +0.51).
- **A3** conclusion does not contradict guardrails: **TRUE** — the claim rests on clean
  winning cells (ton_full point, ps_zero point, ps_zero strict) that pass BOTH NI margins;
  unsw_zero strict is guardrail-restricted (language only, per frozen A.1: "BA determines
  the scientific classification; recall and FPR restrict the permitted safety language").
  Transparency: a first, stricter machine reading (ALL winning cells must pass) evaluates
  FALSE and would yield B; that reading is stricter than the frozen text and is reported
  in CLAIM_INTERPRETATION.json as `A3_stricter_nonfrozen_reading_all_wins_pass`.
- **C1** fails (no critical cell equivalent within ±0.5); **C2** fails.

### Scenario: **A — persistence**

Authorized interpretation:
> Preprocessing asymmetry amplified harmful promotion, but candidate governance remains
> materially useful with self-contained predictive pipelines.

Required nuance (from the same frozen tables, not a new claim): the LOCUS of the harm
moved. Under self-contained pipelines, full-drift naive adaptation is beneficial in all
three regimes (the published ToN full-drift naive harm does not persist; F2 shows
ownership was a major amplifier, ToN +5.98 pp). The persistent material harm lives in the
zero-drift critical cells (ps_zero −1.74, unsw_zero −0.65), where point/strict recover it
(all six F4 gate contrasts positive, Holm-significant).

Forbidden interpretations: the B and C statements; any "security improvement" language for
unsw_zero strict; any claim that full-drift harmful promotion persists under self-contained
pipelines; any equivalence claim for own-naive vs never in critical cells.

## I. Gates

- pytest **87/87**; audit **538/538**; manifest verify: **164/164 pinned CSVs match**
  (9 unpinned extras = the new `symmetric_pipeline_dynamic_001` tables, deliberately NOT
  added to the sealed MANIFEST.sha256 in this phase).
- Arm completeness: **42/42** (`--validate-complete` COMPLETE).
- Sealed `results/final_manifest.json`: byte-identical (`11474601...052a5b12`);
  `results/tables/MANIFEST.sha256` unchanged (`dcf32268...e4420c36`); zero published
  scientific CSVs modified. No orphan processes; everything synchronous.

## J. Recommendation

**AUTHORIZE MANUSCRIPT REWRITE UNDER SCENARIO A** — with the mandatory locus-shift nuance
of §H and the guardrail-restricted language of §F.

One targeted follow-up is justified by a CONCRETE ambiguity (not run, not authorized here):
the A3 classification difference between the frozen-text reading (A) and the stricter
all-cells reading (B) is carried by a single cell (`unsw_zero strict`, recall lo95 −1.26 vs
margin −1.0). If the human reviewer prefers the stricter reading, the scenario becomes B
with the same numbers; no new experiment is needed to resolve this — it is a wording-level
decision that should be settled before the rewrite. No QK, VBC-SG, mild-drift or neutral-
transformer follow-up is recommended: the primary question is answered without ambiguity
about the direction and materiality of the effects.
