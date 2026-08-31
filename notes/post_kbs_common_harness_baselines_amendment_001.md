# FROZEN AMENDMENT 001 — Common-harness baselines protocol (pre-implementation, pre-execution)

Amends: `notes/post_kbs_common_harness_baselines_protocol_001.md` (which stays frozen and
unmodified; where this amendment and the original conflict, this amendment governs).
Config: `configs/post_kbs_common_harness_baselines_v2.json` (v1 is superseded, retained).
Status: **frozen BEFORE any implementation of this experiment and before any smoke or
confirmatory seed of it.** No result of this experiment exists at freeze time; the B2
experiment (`post_kbs_size_matched_drift`) has likewise not produced any result at freeze
time, so nothing here conditions on data.

## 1. Reason for the amendment

The original protocol evaluated every policy with 512/class challengers. The paper's final
comparability result identifies 512/class-vs-2,000/class as a nominal candidate-evidence
asymmetry, so a comparison built to answer the surviving reviewer objection ("the
recognizable baselines were never run under the final trusted harness") must have its
PRIMARY comparison under the final nominally size-matched condition. This is a
design-strengthening change made with zero experimental information: seeds 5001–5030 have
never been executed (verified by repository scan at freeze time), so retaining the reserved
block is valid and is hereby documented.

## 2. Amended design

**Primary condition (all registered inference): candidate size 2,000 flows/class**, via the
plain balanced draw from the train pools at proposal-time severity
(`--adapt-size-per-class 2000`); `own_transformer_per_model`; incumbent 2,000/class
unchanged; same raw streams (bit-identical per seed across all arms), same proposal
semantics, preprocessing ownership, evaluation windows, KS-max detector representation and
SVC-RBF downstream as the final trusted harness. Scenarios: the six of the original
protocol (PortScan / UNSW-Recon / ToN-IoT × full drift / zero drift).

**Primary policies (10):** never-adapt; always-deploy (naive); point gate b=32; strict gate
b=32 (anchors) — ATC; DoC (published generic accuracy-estimation methods) — calibrated soft
ensemble; replay 50/50 (standard baselines; replay is included because it ports faithfully:
the frozen 50/50 rule draws half the nominal candidate evidence at proposal-time severity
and half at severity 0, unchanged) — river-DDM; river-ADWIN (published/reference drift
detectors used as the retraining trigger, always-deploy on fire). No weak internal variant
is added (holdout/LCB/McNemar/sequential gates are NOT in this matrix); the purpose is
comparison against recognizable published/reference alternatives. None of these rows is an
adaptive-NIDS SoTA method and none may be labelled one (original protocol §2, Category C,
unchanged).

**Secondary size-sensitivity block: candidate size 512/class** for exactly {naive, point,
strict, ATC, DoC, calibrated ensemble} on all six scenarios. This tests whether a nominal
evidence disadvantage changes method ordering or gate value. **DDM/ADWIN are deliberately
NOT duplicated at 512**: they are trigger policies whose candidate construction is
byte-identical to naive's full-replacement draw, so the candidate-size effect on their
deployments is exactly the naive size contrast, and their trigger behaviour does not read
the candidate at all — duplication would enlarge the table without answering any question.
**Replay is NOT duplicated at 512**: its 50/50 rule makes "candidate size" a compound
intervention (recency half and replay half shrink together), which belongs to a different
question. Arms: 6×never + 9×6 @2,000 + 6×6 @512 = **96 arms**.

The 512-side arms use the plain historical draw (`--adapt-size-per-class 512`), NOT the
nested coupled draw: cross-size contrasts in this experiment are **seed-paired only**
(paired through the shared raw stream), never proposal-coupled — proposal-coupled size
contrasts are Experiment B2's territory and are not claimed here.

## 3. Fairness accounting (frozen; reported, not equalized)

Budgets are documented and reported; no published method's definition is altered to
equalize them.

| Policy | Target-window labels/decision | Continuous monitoring labels | Candidate-training evidence (labels/proposal) | Calibration/validation evidence | Incumbent information | Can reject? | Same raw stream | Candidate construction |
|---|---|---|---|---|---|---|---|---|
| never | 0 | 0 | — | — | — | — | yes | — |
| naive | 0 | 0 | 2·size (4,000 @2000; 1,024 @512) | — | — | no | yes | full-replace balanced draw at sev(t) |
| point / strict | 32 | 0 | 2·size | — | probe compares h′ vs h | yes | yes | identical to naive |
| ATC / DoC | **0** | 0 | 2·size | 512-row labeled validation sample per model at its training time (incumbent: once per arm at sev 0; candidate: per proposal at sev(t)); drawn from the train partition | own-confidence estimates for both h′ and h | yes | yes | identical to naive (probability=True SVC; the Platt layer does not change `.predict`) |
| calibrated ensemble | 0 | 0 | 2·size | — | soft-votes with the incumbent | no (commits every trigger; model grows) | yes | identical draw; commit forms EnsembleModelCal(h, h′) |
| replay 50/50 | 0 | 0 | 2·size total (half sev(t), half sev 0) | — | — | no | yes | frozen 50/50 replay rule |
| river-DDM / river-ADWIN | 0 | 8 labels/window = 800/stream (their canonical input: per-flow Bernoulli errors of the incumbent) | 2·size | — | monitors the incumbent's error | no (they replace the trigger; deploy on fire) | yes | identical to naive |

Notes frozen with the design: (i) ATC/DoC/ensemble arms train every SVC with
probability=True (required by their definitions); sklearn's binary SVC `.predict` is
unchanged by the Platt layer, and all RNG streams that build the environment are untouched,
so streams and never/naive references remain bit-comparable across arms. (ii) DDM/ADWIN at
zero drift answer "does the reference monitor fire spuriously and what does that cost" —
a policy-level comparison against the random-proposal arms, stated as such. (iii) The
distinction published-generic / published-reference-detector / standard baseline / authors'
policy is carried per row in every output table.

## 4. Statistics (amended families; all magnitude-aware; no sign-rate criterion anywhere)

Unit = seed (30 paired seeds, 5001–5030); deterministic centered paired bootstrap
(B=100,000, seed base 20260721); CI95 signed, CI90 for the ±0.5-pp margin (±0.2/±1.0
sensitivities); Holm within family; t/Wilcoxon sensitivities; recall/FPR NI guardrails
(−1.0/+0.5 pp) gate language only.

PRIMARY (at 2,000/class):
- **P-F1 zero-drift loss avoidance (18, Holm):** {ATC, DoC, ensemble, replay, DDM, ADWIN}
  − naive, per zero-drift scenario.
- **P-F2 full-drift benefit retention (18, Holm):** the same six − naive, per full-drift
  scenario.
- **P-F3 published estimators vs the labeled probe (12, Holm):** {ATC, DoC} − point, all
  six scenarios.

SECONDARY:
- **S-F4 512 sensitivity (18, Holm):** {ATC, DoC, ensemble} − naive at 512, all six
  scenarios.
- **S-F5 method×size interaction (30, Holm):** for k ∈ {point, strict, ATC, DoC, ensemble}:
  (k − naive)@2000 − (k − naive)@512, all six scenarios (seed-paired).

Anchor-vs-anchor contrasts (naive−never, point/strict−naive at either size) are
**descriptive only** in this experiment: the corresponding registered hypotheses live in
the sealed size-matched control (zero drift) and in Experiment B2 (full drift), and this
experiment must not double-test them.

Per-cell outcome rule (unchanged from the original protocol §5, now applied at 2,000):
MATERIAL GAIN (Holm-sig, ≥ +0.5) / MATERIAL COST (Holm-sig, ≤ −0.5) / COMPATIBLE (CI90 ⊂
±0.5) / UNRESOLVED (else). Registered statements S1–S3 of the original protocol now read
"under the final self-contained harness at nominal 2,000-per-class parity". New:
- **S4 (ordering change):** "the method ordering changes with candidate size" may be
  claimed for policy k only if some S-F5 interaction for k is Holm-significant with
  |effect| ≥ 0.5 pp AND the (k − naive) contrast is MATERIAL in opposite directions (or
  MATERIAL vs COMPATIBLE) at the two sizes on that scenario. Otherwise the permitted
  sentence is "no material ordering change was resolved".

A true null lands in COMPATIBLE when precision suffices and can never be forced into
GAIN/COST; the amendment preflight re-verifies this on the amended families.

## 5. Seeds, gates, stop rule

Confirmatory seeds **5001–5030 retained** (virgin at freeze; documented above). Smoke
5401–5402. Parity reference: stored symmetric-pipeline smoke outputs (seeds 4242–4243),
comparison only. One pass, no extension, no interim analysis; the confirmatory analysis
script must be committed before the confirmatory run. Implementation-fidelity gates
(original protocol §6) unchanged, plus: (iv) ATC/DoC decisions must bit-agree with the
existing v1 implementation on a shared configuration; (v) DDM/ADWIN must be the `river`
objects receiving per-flow Bernoulli errors, version pinned by requirements-lock.

## 6. Compute estimate (no confirmatory science executed to obtain this)

96 arms; 512-arms ≈ 2 min, 2,000-arms ≈ 3–3.5 min (observed whole-arm wall-clocks and the
observed 2,000/512 ratio) → ≈ 4.5–5 h single-machine, plus smoke/parity ≈ 25 min.
