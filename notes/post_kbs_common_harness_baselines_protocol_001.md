# FROZEN PROTOCOL — Common-harness evaluation of published/external baselines (post-KBS Experiment 1)

Status: **PROTOCOL FROZEN BEFORE IMPLEMENTATION. No experiment code for this protocol has
been written, no smoke or confirmatory seed has been executed, and no results exist.**
Implementation and execution require separate, explicit authorization after this freeze.

Branch: `post-kbs-hardening`. Baseline of record: Phase A hardening commit
(`audits/post_kbs_hardening_report.md`); sealed science = v1.22.0 line, untouched.
Config: `configs/post_kbs_common_harness_baselines_v1.json` (SHA-256 to be recorded in every
arm's `run_config.json` at execution time).
Companion preflight: `audits/post_kbs_protocol_preflight.md`.

## 1. Question and motivation

The strongest surviving external criticism (hostile audit, finding M3) is that the
recognizable published baselines — ATC, DoC, the `river` reference monitors, replay and the
calibrated ensemble — were never evaluated under the final trusted harness (self-contained
`own_transformer_per_model` challengers on bit-identical streams). Block III evidence is
exploratory (harness v1, unpaired); Blocks I–II are frozen-transformer.

**Registered question Q-B1:** under the final self-contained harness, on bit-identical
streams, how do the published label-free alternatives and reference monitors trade
zero-drift loss avoidance against full-drift benefit, relative to always-deploy and to the
point/strict labeled-probe gates?

This is a trade-off mapping question. It is NOT a superiority hypothesis for the gates, and
no outcome of this experiment may be summarized as "our gate dominates".

## 2. Baseline selection (criteria frozen before any result)

Selection criteria, in order: (1) closeness to the same decision problem (commit/skip a
drift-triggered challenger, or trigger retraining from labels); (2) public reproducibility
(published description or reference implementation); (3) compatibility with the three
datasets and the registered protocol; (4) no information requirement unavailable to the
competing methods; (5) reasonable implementation fidelity, checkable against a reference.
No method is selected or excluded on the basis of expected results.

**Category A — published generic model-comparison / accuracy-estimation methods:**
- **ATC** (Garg et al. 2022, `garg2022atc`) as a commit gate: each of incumbent and
  challenger estimates its current-window accuracy from its own confidences with a
  threshold fit on a labeled validation sample drawn at its own training time (zero
  target-window labels); commit iff the challenger's estimate is higher.
- **DoC** (Guillory et al. 2021, `guillory2021doc`) as a commit gate: same information
  budget, difference-of-confidences accuracy estimate.

**Category B — published performance-aware drift/retraining monitors (reference
implementations):**
- **DDM** (`river` reference implementation), 8 labels/window (800/stream), as the
  retraining trigger with always-deploy.
- **ADWIN** (`river` reference implementation), same budget, same role.

**Category C — published adaptive-NIDS update systems: none qualify; stated plainly.**
Bibliography audit (Related Work §2): INSOMNIA performs continuous semi-supervised
adaptation of a NIDS (no discrete incumbent/challenger promotion decision); Transcend /
Transcendent and CADE abstain on or explain individual samples (per-sample rejection, not
candidate promotion); CARA / Regol / IGPC-MSOS are cost-schedule or update-mode
formulations whose required inputs (cost ratios, system feedback signals) have no faithful
instantiation in this harness without inventing values their papers do not supply. Each is
therefore **not directly comparable**, and this protocol does not label any evaluated row
an "adaptive-NIDS SoTA baseline". The manuscript's conceptual positioning table remains the
comparison surface for these systems.

**Strong standard baselines (not published-method claims):** calibrated soft ensemble
(always-deploy) and replay 50/50 retraining (always-deploy) — the two strongest label-free
update rules from the earlier blocks.

**Anchors (this paper's policies, included only as anchors):** never-adapt, always-deploy
(naive), point gate b=32, strict gate b=32.

Total: 10 policies per scenario. Preference for 2–4 strong external baselines over a weak
long list is met: ATC, DoC, DDM, ADWIN are the external rows; ensemble/replay are standard
baselines; the rest are anchors.

## 3. Common-harness design (all fixed in advance)

- Machinery: `run_symmetric_pipeline_replication` + the v2 science module, exactly as the
  registered symmetric-pipeline replication, config-driven.
- Challenger construction: `own_transformer_per_model`, candidate size **512 flows/class**
  (the historical size shared by every arm of the program; candidate-size effects are
  Experiment 2's question, kept orthogonal by design). Incumbent 2,000/class. SVC-RBF,
  PCA-8, window 128, KS-max detector for distribution-triggered arms; detector
  representation frozen-initial (monitoring policy never confounded with construction).
- Streams: per seed, one pre-generated raw stream served bit-identically to all 10 arms
  (hash-verified). Scenarios: PortScan, UNSW-Recon, ToN-IoT × {full drift, zero drift}
  (zero drift = random proposal trigger p=0.05, severity 0) — 6 scenarios, 60 arms.
- Information budgets per proposal (identical evidence wherever the method definition
  allows): candidate training 1,024 labels (all policies that train); point/strict probe 32
  target labels; ATC/DoC zero target labels + training-time validation sample (512 rows,
  drawn from the train partition at candidate-training severity, disjoint from the
  candidate batch by draw); DDM/ADWIN 8 monitoring labels/window in place of a
  distribution detector (they replace the trigger, not the gate); ensemble/replay/naive
  zero decision labels. No method reads sev(t) or any simulator oracle beyond what the
  pool-based harness gives every arm equally.
- Temporal semantics, cooldown, trigger confirmation: byte-identical to the symmetric
  replication config.

## 4. Estimands and statistical families (frozen)

Inferential unit: the seed (30 paired seeds). Deterministic centered paired bootstrap
(B=100,000, per-contrast seed base 20260721), CI95 for signed effects, CI90 for
equivalence at the registered ±0.5-pp materiality margin (±0.2/±1.0 sensitivities). Holm
within each family; paired t / Wilcoxon reported as sensitivities. Recall/FPR
non-inferiority guardrails (−1.0 pp / +0.5 pp one-sided 95%) gate safety language only.

- **F1 (zero-drift loss avoidance; 18 contrasts, Holm):** for each of ATC, DoC, ensemble,
  replay, DDM, ADWIN: policy − naive on each zero-drift scenario.
- **F2 (full-drift benefit retention; 18 contrasts, Holm):** the same six policies − naive
  on each full-drift scenario.
- **F3 (against the labeled probe; 12 contrasts, Holm):** ATC, DoC − point gate on all six
  scenarios.
- Descriptive (uncorrected, labelled): everything else, including strict-gate comparisons
  and all commit/label accounting.

## 5. Outcome rules (magnitude-aware; frozen; no sign-rate criteria)

Per policy k and scenario s, classify the primary contrast (k − naive):
- **MATERIAL GAIN:** Holm-significant, effect ≥ +0.5 pp.
- **MATERIAL COST:** Holm-significant, effect ≤ −0.5 pp.
- **COMPATIBLE (no material effect):** CI90 fully inside ±0.5 pp.
- **UNRESOLVED:** none of the above. (A true null with small symmetric noise lands in
  COMPATIBLE once precision suffices; it can never be forced into GAIN/COST — the
  preflight verifies this distinguishability requirement.)

Registered summary statements (the only confirmatory sentences this experiment can emit):
- S1: "Published estimator k avoids the zero-drift loss under the final harness" iff k is
  MATERIAL GAIN in ≥2 of 3 zero-drift scenarios and never MATERIAL COST there.
- S2: "Published estimator k pays for it at full drift" iff k is MATERIAL COST in ≥1
  full-drift scenario (reported per scenario, never averaged away).
- S3: "k matches the point gate" iff every F3 contrast for k is COMPATIBLE.
- Any mixed pattern is reported cell-by-cell with no aggregate label.
No outcome may be reported as a ranking; the trade-off framing of Q-B1 is mandatory.

## 6. Seeds, stop rule, fidelity

- **Confirmatory seeds 5001–5030 (RESERVED; virgin — repository-wide scan found zero
  references to this block).** Smoke seeds 5401–5402. One pass, no extension, no interim
  peeking; the analysis script runs once after all 60 arms complete.
- Implementation-fidelity gates (must pass before confirmatory execution, on smoke seeds
  only): (i) DDM/ADWIN driven through the `river` objects themselves (as in
  `validate_monitors_vs_river`); (ii) ATC/DoC decisions bit-agree with the existing v1
  implementations on a shared smoke configuration; (iii) anchor arms (never/naive/point/
  strict) reproduce the symmetric-replication code path bit-for-bit at flag-off on the
  stored smoke outputs; (iv) raw-stream hashes identical across all 10 arms per seed.
- Exploratory Block III numbers are context only and are never merged with, averaged with,
  or replaced by silent reuse as, these confirmatory outcomes.

## 7. What this experiment cannot show (frozen scope)

No head-to-head claim against CARA/Regol/IGPC-MSOS/INSOMNIA/CADE/Transcendent; no
population or deployment prevalence; no transfer of results to candidate sizes other than
512/class (Experiment 2's territory); no claim about probe-acquisition cost at operational
prevalence.

## 8. Estimated compute (no confirmatory science executed to obtain this)

60 arms × ~2 min/arm (observed whole-arm wall-clock of the same machinery) ≈ 2 hours
single-machine, plus smoke/fidelity runs ≈ 15 min.
