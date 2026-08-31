# FROZEN PROTOCOL — Size-matched self-contained challengers under drift (post-KBS Experiment 2)

Status: **PROTOCOL FROZEN BEFORE IMPLEMENTATION. No experiment code for this protocol has
been written, no smoke or confirmatory seed has been executed, and no results exist.**
Implementation and execution require separate, explicit authorization after this freeze.

Branch: `post-kbs-hardening`. Baseline of record: Phase A hardening commit.
Config: `configs/post_kbs_size_matched_drift_v1.json`.
Companion preflight: `audits/post_kbs_protocol_preflight.md`.

## 1. Question and motivation

The registered size-matched control (seeds 4001–4030) was zero-drift only, and at severity
zero the 2,000/class own-pipeline challenger is close to an exchangeable re-draw of the
incumbent, so mean parity there is the expected outcome (main §4.2.2). The missing cell —
the only one in which "candidate evidence size" is a non-trivial hypothesis — is
**own-transformer + nominal size matching + real progressive drift**, where candidate
recency carries genuinely shifted information. Under the *frozen* transformer, full-drift
size-matching previously **deepened** harm (Supplementary S1.5); under self-contained
pipelines the outcome is genuinely open.

**Registered question Q-B2:** under full progressive drift with self-contained challengers,
does increasing nominal candidate evidence from 512 to 2,000 flows/class help, hurt, or
have no material effect — and does the point/strict gate retain value at the matched size?

This experiment does NOT re-test the zero-drift result and is not designed to "prove" it.
All four registered outcomes below are acceptable; none is preferred.

## 2. Design

- Machinery: `run_symmetric_pipeline_replication` + the v2 science module; scenarios
  PortScan-full, UNSW-Recon-full, ToN-IoT-full (mixing ramp 0→1 over 80 of 100 windows —
  the registered full-drift construction; mild drift deliberately excluded to keep the
  factorial minimal).
- Arms per scenario: never + {naive, point, strict} × candidate size {512, 2,000}/class =
  7 arms; 21 arms total. `own_transformer_per_model` exclusively; incumbent 2,000/class;
  KS-max; SVC-RBF (C=1.0, gamma=scale, PCA-8); windows 128; probe 32; trigger 3-of-k with
  10-window cooldown — every constant byte-identical to
  `configs/symmetric_pipeline_dynamic_v1.json` except the new candidate-size axis.
- Streams: per seed one pre-generated raw stream, served bit-identically to all 7 arms
  (hash-verified).

### 2.1 Nested candidate draw at severity > 0 (the one new mechanism; frozen here)

The existing `nested_candidate_draw` asserts severity == 0 and MUST NOT be reused outside
that validated domain. The drift-domain draw is defined as follows and must be implemented
exactly so:

At a proposal at window t with proposal-time severity sev(t), using the per-trigger RNG
stream `cand_rng(seed, t)`: first draw `B512 = sample_balanced_from_distribution(train
pools, 512/class, sev(t))` — byte-identical to the historical own-transformer draw at this
(seed, t, sev) — then, continuing the SAME RNG stream, draw the extension
`E1488 = sample_balanced_from_distribution(train pools, 1,488/class, sev(t))` at the SAME
sev(t). `B2000 = concat(B512, E1488)`; training uses the prefix selected by the arm's
candidate size. Both sizes therefore sample the SAME proposal-time target mixture,
differing only in nominal candidate evidence; neither size ever receives a different
temporal target. Per-candidate provenance must record sev(t), the full-batch row hash and
the 512-prefix row hash; the analysis verifies prefix-hash equality at every coupled
proposal.

### 2.2 Coupling scope (stated in advance, not discovered later)

Trigger times are policy-dependent only through commits (detector reference resets on
commit). The two **naive** arms commit at every confirmed trigger, so naive-512 and
naive-2000 share identical trigger/commit timelines for a given seed: their proposals are
exactly coupled (same t, same sev(t), nested batches) for the whole stream. **Gated** arms'
decision histories can diverge between size conditions after the first discordant commit,
so gate-arm contrasts across sizes are seed-paired through the shared raw stream but NOT
proposal-coupled; the analysis treats them accordingly (seed-level pairing only) and never
claims proposal-level coupling for them. D3 (below) is the exactly-coupled estimand.

## 3. Estimands and statistical families (frozen)

Unit: seed (30 paired seeds); deterministic centered paired bootstrap (B=100,000,
per-contrast seed base 20260721); CI95 for signed effects; CI90 for the registered
±0.5-pp margin (±0.2/±1.0 sensitivities); Holm within each family; t/Wilcoxon
sensitivities; recall/FPR non-inferiority guardrails (−1.0/+0.5 pp, one-sided 95%) gating
language only. Future-value (H1/H3/H5/H10) summaries are DESCRIPTIVE ONLY — no outcome
rule, no sign-rate criterion, anywhere in this protocol.

- **G1 (value of updating; 6 contrasts, Holm):** naive_512 − never and naive_2000 − never,
  per scenario.
- **G2 (the size effect — primary; 3 contrasts, Holm):** naive_2000 − naive_512 per
  scenario (the exactly-coupled contrast).
- **G3 (gate value at matched size; 6 contrasts, Holm):** point_2000 − naive_2000 and
  strict_2000 − naive_2000, per scenario.
- **G4 (secondary; 6 contrasts, Holm):** gate × size interactions
  (gate−naive)@2000 − (gate−naive)@512.

## 4. Registered outcomes (new taxonomy; the old P/A/E rules do not apply here)

Per scenario, classify **G2** (the size effect):
- **SIZE BENEFIT:** Holm-significant with effect ≥ +0.5 pp.
- **SIZE COST:** Holm-significant with effect ≤ −0.5 pp.
- **NO MATERIAL SIZE EFFECT:** CI90 fully inside ±0.5 pp.
- **SUB-MATERIAL / UNRESOLVED:** anything else (reported as such; a Holm-significant
  sub-material effect is named "resolved but sub-material").

Program outcome: **HOMOGENEOUS-<label>** if all three scenarios share a class;
**HETEROGENEOUS** otherwise, reported per scenario with no pooled label. None of the four
outcomes is preferred, and each has a pre-agreed one-sentence reading in the manuscript:
- SIZE BENEFIT: "more candidate evidence helps under drift too; the zero-drift account
  extends directionally."
- SIZE COST: "larger current-mixture candidates over-specialize under an advancing ramp
  even with self-contained preprocessing — the frozen-policy S1.5 pattern is not a frozen
  artifact"; this WEAKENS the paper's evidence-parity recommendation and must be reported
  as doing so.
- NO MATERIAL SIZE EFFECT: "candidate size is immaterial under full drift at these
  budgets."
- HETEROGENEOUS: reported cell-by-cell.

Distinguishability requirement (checked in the preflight): a true null with small
symmetric noise reaches NO MATERIAL SIZE EFFECT (CI90 ⊂ ±0.5 is attainable at 30 seeds
given observed full-drift SEs) and can never be classified BENEFIT or COST; the rule is
two-sided and magnitude-aware, so it cannot repeat the E3 sign-rate pathology.

## 5. Seeds, parity, stop rule

- **Confirmatory seeds 6001–6030 (RESERVED; virgin — repository-wide scan found zero
  references to this block).** Smoke seeds 6401–6402. One pass, no extension, no interim
  peeking.
- Parity gates before confirmatory execution (smoke/parity only, never evidence):
  (i) flag-off path byte-identical to the current driver on the stored symmetric-pipeline
  smoke outputs (seeds 4242–4243, comparison only); (ii) at `--candidate-size 512` under
  the new drift-domain draw, batches byte-identical to the historical own-transformer
  full-drift draw at the same (seed, t) — asserted per proposal on smoke seeds; (iii)
  nesting audit (512-prefix hash = 512-batch hash) at confirmatory scale, zero violations
  required.
- The confirmatory analysis script (families G1–G4, outcome rules of §4, guardrails,
  descriptive future-value accounting) must be committed before the confirmatory run, as
  in the previous controls.

## 6. Scope (frozen)

No mild-drift arms; no observed-data arm; no VBC-SG arms; no claim about deployment
prevalence; results scoped to the pool-based full-drift construction with balanced
candidate batches sampled at proposal-time severity. Whatever the outcome, the zero-drift
control's exchangeability reading (main §4.2.2) is unaffected.

## 7. Estimated compute (no confirmatory science executed to obtain this)

21 arms; 512-arms ~2 min, 2,000-arms ~1.4× (observed whole-arm ratios) → ≈ 55 min
single-machine, plus smoke/parity ≈ 15 min.
