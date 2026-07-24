# Q1 Final Acceptance Patch — Frozen Protocol

**Status:** FROZEN on creation. Do not edit below this line after experiments run,
except by appending a dated `## Appendix — deviation` section explaining any
unavoidable divergence.

**Baseline of record (published v1.19.1):**
- git tag `v1.19.1`; editorial source commit `25a79f7`; sealing commit `cb9040c`.
- pytest 47/47; audit 477/477; hashes 163/163.
- PDFs: main 31 pp, supplement 24 pp, IEEE 23 pp.
- harmful accounting: 520 commits / 340 immediate / 180 deferred / 506 evaluable H5 /
  14 censored / 0 harmful.
- artifact version 1.19.1.

**Non-goals (hard):** no new datasets, classifiers, gates, detectors, or research
lines. No git/commit/push/tag/release/Zenodo/DOI. No version bump. Paper 1 reference
untouched. Do not artificially preserve v1.19.1 numbers; report whatever the corrected
code produces.

---

## Block A — temporal semantics of deferred commits

### Hypothesis (H-A)

In `src/experiments/run_paper2_readaptation_v2.py` the `pending` (deferred-decision)
block executes at the **start** of a window iteration `t`, *before* the window is
served/evaluated. On a deferred COMMIT it reassigns `model = pending["cand"]` and
rebuilds+recalibrates the detector, and only *afterwards* does
`m = evaluate_model(model, Xw, yw)` (line 634), `pred = model.predict(Xw)` (635) and
`score = detector.score(Xw)` (641) run. Therefore, on the resolution window `t`:

- the served **balanced accuracy / predictions / alerts** logged in the per-window
  `rows` are credited to the **challenger**, and
- the **detector score / alarm** for `t` are computed with the **freshly rebuilt
  detector**,

i.e. the challenger retroactively "serves" the very window whose arrival resolved the
decision. Immediate commits do **not** have this problem: `model = candidate` happens
after `m = evaluate_model(...)`, so the challenger serves from `t+1`.

**Verified independently (2026-07-21):** confirmed at code level (pending block
542–633 precedes eval at 634; `model` reassigned at 578/607; detector rebuilt at
579/608). Confirmed asymmetry with the immediate path (`model = candidate` at 1138,
after eval). A minimal reproduction test (T1) is written *before* the fix and must fail
on the current code.

**Scope of impact (stated in advance, to be confirmed by rerun, not assumed):**
- The **resolution log** (`log_resolution`) already scores harm from `t_res + 1`
  onward (line 404), so `delta_resH` already excludes `W_t`. The harm accounting is
  therefore expected to be *largely* insensitive to the fix, but the fix perturbs the
  per-window detector score / served BA on deferred-commit windows, which can perturb
  future alarms/triggers and hence the realised trajectory. **We do not assume commits
  stay 520.** All affected numbers are regenerated from real reruns.

### Mandatory production semantics (per window `t`)

1. `W_t` is served by the model deployed at the **start** of `t`
   (`serving_model`, `serving_detector`).
2. Compute & record that model's performance and detector score/alarm on `W_t`.
3. Then absorb evidence arriving in `t` (deferred-continuation probe draws).
4. Then resolve any immediate or deferred proposal.
5. A COMMIT resolved in `t` enters service from `W_{t+1}`.
6. No decision may retroactively modify `W_t`'s performance, predictions, detector
   score, or per-window logs.

### Planned code changes

- `src/experiments/run_paper2_readaptation_v2.py`: restructure the per-window loop so
  the block is explicit and ordered — `serving_model_at_window_start` →
  window evaluation + detector score + alarm → `rows` entry for `t` → `seen.append` →
  deferred-pending resolution (effective `t+1`) → immediate trigger (effective `t+1`).
  The deferred model swap / detector rebuild / cooldown / alarm reset must all move to
  **after** the window-`t` evaluation and logging.
- Add in-runner semantic assertions where cheap (e.g. that no resolution mutates the
  already-appended `rows[t]`).
- Touch the following auxiliary concerns during the review, changing them only if the
  reorder makes it necessary: detector recalibration source (`observed` vs pool),
  cooldown, alarm absorption while a decision is pending, `n_adapt` / `adapt_windows`,
  per-trigger and resolution logs, `delta_res{1,3,5,10}`, `delta_until_next`, end-of-
  stream censoring, immediate-vs-deferred accounting, cohort/refresh/accumulate defer
  modes, pooled EB-CS defer and VBC-SG, training/probe latency.

### Tests (must fail on current code, pass after fix) — `tests/test_q1_temporal_semantics.py`

- **T1 No retroactivity:** minimal stream where the incumbent is correct on `W_t`, the
  challenger is wrong on `W_t`, evidence in `t` forces a deferred COMMIT, and the
  challenger is better from `W_{t+1}`. Assert the served performance recorded for `W_t`
  is the incumbent's.
- **T2 Immediate/deferred symmetry:** both an immediate and a deferred commit resolved
  in `t` begin serving in `t+1`.
- **T3 Detector score:** the detector score/alarm of `W_t` are computed with the
  detector in force at the **start** of `t`, not the rebuilt one.
- **T4 Resolution logging:** `delta_resH` begins strictly after the resolution window
  and never includes `W_t` (guards the existing invariant against regressions).
- **T5 Trajectory:** a deferred decision may change the future trajectory but must never
  rewrite the resolution window.
- **T6 Censoring:** proposals resolved near the end of the stream censor the correct
  horizons.

Add structural (not phrase-only) guards to the audit for the `t → t+1` invariant.

### Acceptance (Block A)

New tests pass; the fix leaves the intent evident in loop structure; the full existing
suite still passes (or any change is explained and is a corrected number, never a
loosened assertion).

---

## Block B — rerun only the affected frontier

### Authorized scope

Re-execute the complete registered budget-frontier matrix affected by the temporal fix
and only that matrix:
- scenarios: PortScan full drift, ToN-IoT full drift, zero drift;
- caps: 64, 128, 256, 512, 1024;
- schedules: Bonferroni, p-series;
- policies: pooled EB-CS + defer, VBC-SG-Cohort, VBC-SG-Refresh;
- registered seeds 501–530;
- point and strict anchors where they belong to the frontier generator.

The exact arm set is the one the ledger/orphan checker enumerates
(`make_final_experiment_ledger`, `make_paper2_q1_frontier`). Orphan count must stay 0.

**Not** re-run unless a technical dependency proves it shares the corrected loop and its
published numbers move: confirmatory core, causal observed-data matrix, symmetric A/B,
chronological replays, operational acquisition, classifier generalization. If such a
dependency is found, stop, enumerate the extra scope, justify it, and only then run it.

### Regenerated derivatives (scripts only; never hand-edited)

`budget_frontier.csv`; immediate/deferred resolution artifacts; harmful commit ledger;
frontier table; the corresponding IEEE tables; final experiment ledger;
`MANIFEST.sha256`; `final_manifest.json`; the derived audit; and every affected number
in manuscript / abstract / conclusion / highlights / captions.

### Reported (old → new), without hiding results

Total commits; immediate; deferred; evaluable H5; censored H5; harmful H5; harmful
until-next; exact upper confidence bound; benefit recovered per cap; labels per
proposal; abstention; delay; zero-drift commits; number of non-vacuous configurations;
first non-vacuous cap for Cohort and Refresh; strict vs risk-controlled gate comparison.
The conclusion may survive, weaken, or change; filters are not tuned to recover old
numbers.

---

## Block C — operational arm scope correction (editorial + instrumentation only)

Audit `run_paper2_operational_e2e.py`, Table 11, §5.5, and every claim surface. Document
stream prevalence, detector-calibration prevalence, discovery-sample prevalence,
validation-sample prevalence, candidate-training composition (balanced), which sample
decides the commit, which metric the decision uses, the meaning of
`inspected_flows_per_attack`, and the unmodeled costs. Rename Table 11 to
"Attack-label acquisition yield under operational prevalence" (or equivalent) and remove
every "what the commit decision costs" / "all labels at operating prevalence" framing.
Add explicit manifest/output fields (`stream_prevalence`,
`candidate_training_sampling = "balanced_per_class"`, `discovery_metric =
"inspected_flows_per_attack_found"`, etc.) and tests that block incompatible claims.
Re-run the operational arm only if a purely instrumental derived file must be
regenerated (no scientific-result change).

## Block D — chronological contradiction

Replace every universal "gates beat always-deploying on healthy timelines" formulation
with: Point and strict gates outperform always-deploying on the two healthy UNSW
timelines; VBC-SG does so on one (20%) but not the other (40%); the healthy Wednesday
intra-day replay is an unresolved counterexample where gates fall slightly below naive;
no net chronological harm is observed across the thirteen replays. Add a structural
guard that catches the universal formulation, not one literal phrase.

## Block E — statistical rigor

Multiplicity: if per-seed data allow direct paired contrasts, compute paired p-values
with a deterministic bootstrap, keep Holm for the six-contrast confirmatory family and
BH within each declared follow-up block, regenerate `multiplicity.csv`, document
resamples/seeds, add exact-reproducibility tests. Otherwise keep the approximation and
label it precisely "normal-approximation inversion of the published interval" (never
"exact bootstrap p-value"). Equivalence: either implement a formal deterministic
bootstrap equivalence procedure (±1.0 BA margin, seeds 2001–2100, pilot excluded,
±0.5/±2.0 sensitivities) or keep the current one but rename it everywhere "bootstrap
CI-based equivalence assessment using the pre-registered ±1.0 BA margin" and drop/relabel
`p_low`/`p_high` if they are not proper boundary-null tests. No verdict changed for
convenience. Do not change families after seeing results.

## Block F — editorial polish for KBS

Reduce abstract density (keep problem, candidate governance, core result, VBC-SG,
chronological limit); move secondary percentages/variants/amendment history to the body;
reduce "external review identified"/"earlier version omitted"/"amendment X corrected"
phrasing in the main text while preserving that traceability in supplement / protocol /
release notes / artifact; keep confirmatory core, registered follow-ups, feasibility,
chronological boundary, and exploratory evidence clearly separated; never use
"safe/guaranteed/eliminates harm" outside the formal scope; keep "zero observed harmful
commits with bounded rate"; position novelty as formalization + risk-controlled
evaluation of champion–challenger for adaptive NIDS, not its invention.

## Block G — guards & audit

Structural + numeric guards (not single-phrase) for: `t → t+1` semantics of all commits;
deferred non-retroactivity; operational candidate training declared balanced; discovery
sample not used for the decision; Table 11 not called commit-decision cost; no "all
labels at operating prevalence"; no universal healthy-timeline claim; pooled 93% never
tied to a per-class formal guarantee; Cohort/Refresh differentiated; full harm
accounting (immediate/deferred/evaluable/censored/H5/until-next); manuscript+tables+
audit+manifest identical numbers; no stale number anywhere in main/main_ieee/supplement/
tables/captions/README/REPRODUCE/audits/manifests.

---

## Execution order

Git audit → this protocol → failing test → fix → unit tests → full suite → frontier
rerun → regenerate derivatives → old-vs-new comparison → operational claims → chrono
fix → multiplicity/equivalence → editorial polish → regenerate tables → IEEE port →
compile 3 PDFs → full audit → hashes → ledger → manifest → tests again → hostile review
→ stop (no git/publication).

## Appendix — 2026-07-21 (dated): Block B unblocked via forensic driver recovery (Ruta A)

Written after Block A completed and before any frontier derivative was regenerated.

The frontier driver `run_q1_faseC.py` was not in the repository (a reproducibility defect in
itself). Per the authorized continuation order, a bounded forensic search recovered it intact
from the recovered local working directory (SHA256 `655309bf…`; full trail in
`notes/frontier_driver_recovery_report.md`). Ruta A criteria were met before any rerun:

- the recovered grid enumerates exactly the 99 published tags;
- all fixed parameters resolved (they are the runner's argparse defaults);
- bit-identity validated on three full 30-seed arms with zero deferred commits —
  `q1fc_ps_full_vbcref_c512_bonf`, `q1fc_ton_full_vbcref_c256_bonf`,
  `q1fc_ton_zero_ebcsdef_c256_bonf` — all five CSVs each, under the corrected runner.

Consequences (scope unchanged, method now concrete):
- The driver is committed as `src/experiments/run_q1_budget_frontier.py` +
  `configs/q1_budget_frontier_v2.json` (all parameters explicit; per-arm `run_config.json`,
  `command.txt`, `environment.json`, completion markers, run ledger). The verbatim original
  is retained locally (unversioned; machine-specific paths) and identified by the SHA256 above.
- Only the **27 arms with ≥1 deferred commit** are re-executed (they are the only arms the
  temporal fix can alter — a pending continuation that never commits is provably a no-op
  under the reorder). The other 72 published arms are reused, with reuse recorded in their
  `run_config.json`. The 27 pre-fix arm dirs and the published derived CSVs are preserved
  under `results/raw/_v1191_frontier_backup_pre_temporal_fix/` for the old→new comparison.

## Stopping rule

Stop when, simultaneously: (1) temporal semantics correct and test-covered; (2) affected
frontier fully re-run; (3) all numbers regenerated from real outputs; (4) operational
claims match what is measured; (5) chronological contradiction removed; (6) statistics
and equivalence precisely described; (7) tests/audit/hashes/ledger/PDFs green;
(8) hostile review shows no load-bearing blocker; (9) no new scientific line opened.
Then produce `CHECKPOINT FINAL — aceptación máxima KBS` and halt.
