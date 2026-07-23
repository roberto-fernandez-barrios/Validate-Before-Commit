# Reproducibility — "Validate Before Commit"

Artifact for the paper on label-efficient gating of drift-triggered classifier updates for NIDS.
Everything below regenerates from raw data; results tables/figures live under `results/` (git-ignored) and
are rebuilt by the analysis scripts. Manuscript + bibliography: `manuscript/`.

## 1. Environment

```bash
conda create -n paper2 python=3.11 -y
conda activate paper2
pip install -r requirements.txt      # numpy, pandas, scipy, scikit-learn, matplotlib, statsmodels, river
# exact versions used for the published results:
pip install -r requirements-lock.txt
```

## 2. Data

Place the public benchmarks under `data/` (not redistributed here; git-ignored):
- CICIDS2017 (`data/raw/cicids2017/MachineLearningCVE/*.csv`) — Sharafaldin et al. 2018.
- UNSW-NB15 → preprocessed binary splits in `data/processed/unsw_nb15/` — Moustafa & Slay 2015.
- ToN-IoT → preprocessed binary splits in `data/processed/ton_iot_q1_gate/` — Alsaedi et al. 2020.

The label column is `Label` (BENIGN vs. attack); features are numeric, standardized, PCA→8 dims.

## 3. Core experiment: progressive readaptation with the gate

`src/experiments/run_paper2_progressive_readaptation.py` runs one (dataset→regime, detector) stream over
30 seeds × 100 post-drift windows. Key flags:
- `--methods` : `energy_distance,mmd_rbf,ks_max,jsd,qk_mmd_zz,qk_mmd_pauli_xz`
- `--adaptation-gate` : `none` (naive) | `labeled_probe` | `unsup_disagree`  ← **the contribution**
- `--probe-size B` (labeled_probe) ; `--gate-margin` ; `--gate-disagree-threshold`

Example — the harm regime with the label-efficient gate:
```bash
python -m src.experiments.run_paper2_progressive_readaptation \
  --data-ref data/processed/ton_iot_q1_gate/ton_iot_ref_no_scanning_binary.csv \
  --data-cur data/processed/ton_iot_q1_gate/ton_iot_cur_scanning_binary.csv \
  --label-col Label --methods ks_max,qk_mmd_zz --dim 8 --window-size 128 \
  --post-windows 100 --ramp-windows 80 --calibration-windows 30 \
  --seeds $(seq -s, 1 30) \
  --adaptation-gate labeled_probe --probe-size 32 \
  --outdir results/raw/ton_scanning_ks_qk_lp32
```

The **pre-specified Phase 2** protocol (criteria fixed at 10 seeds, conditionally expanded to 30; see the
manuscript's honesty notes) is documented in `notes/paper2_phase2_gated_readaptation_preregistration_001.md`.
The **confirmatory study is the harness-v2 registered replication** (protocol publicly tagged
`harness-v2-protocol` + amendments 002/003/004; pristine seeds 104–133). v2 runner — the PRIMARY arm
(fresh-probe commit gate):

```bash
python -m src.experiments.run_paper2_readaptation_v2 \
  --data-ref data/processed/ton_iot_q1_gate/ton_iot_ref_no_scanning_binary.csv \
  --data-cur data/processed/ton_iot_q1_gate/ton_iot_cur_scanning_binary.csv \
  --seeds 104,...,133 --methods ks_max --adaptation-gate labeled_probe --probe-size 32 \
  --outdir results/raw/paper2_v2_ton_scanning_ks_lp32
```
Other arms swap `--adaptation-gate` (`none` = naive, `labeled_probe_holdout` → `..._holdout32b` dirs,
`labeled_probe_lcb`, `labeled_probe_mcnemar`, `two_stage`), `--methods` (`qk_mmd_zz`), `--downstream-model`,
`--stream-prevalence 0.05`, `--adapt-strategy {ensemble,ensemble_cal,sliding_window}`,
`--trigger-mode {ddm,adwin,ddm_river,adwin_river}`, `--probe-size {8,16,64,128}`, `--probe-latency {5,20}`,
`--probe-flip-frac {0.10,0.25,0.40}`, `--max-severity {0.25,0.50}` (the mild-drift prediction test), and the
amendment-006 causal flags `--probe-source observed` (with `--adapt-strategy sliding_window`: candidate and
probe come only from observed past traffic), `--probe-prevalence {0.10,0.05,0.01}` (Binomial probe composition,
zero-attack probes allowed) and `--health-ref-mode per_incumbent`. The full arm
lists, with seeds and output-dir naming, are enumerated in
`notes/paper2_harness_v2_registered_replication_protocol_001.md` and amendments
`notes/paper2_harness_v2_amendment_00{2,3,4}.md` (004 also carries the seed ledger).
Amendment 009 (`notes/paper2_harness_v2_amendment_009.md`) adds `--downstream-model {random_forest,logreg,mlp}`
and `--dim 100` (no PCA) under `--max-severity {0.25,0}`, the update generators
`--adapt-strategy {cumulative,replay}` (cumulative = all observed windows; replay = current + severity-0
reference, 50/50), and the anytime-valid confidence-sequence gate `--adaptation-gate labeled_probe_cs`
(Robbins normal-mixture, `--seqav-alpha` the harmful-commit bound); its `paper2_v11_*` arm/seed ledger is in
that note. The CICIDS Tuesday chronological stream is staged by
`python -m src.analysis.prepare_paper2_cicids_tuesday_chronological` (train = first 30% of the timeline)
and run with `run_paper2_temporal_stream` on seeds 401--430.
Amendment 011 (`notes/paper2_harness_v2_amendment_011.md`) adds `--stream-disjoint-windows`
(without-replacement, value-deduplicated stream: removes candidate-train/future-eval overlap in the
observed-data arm) and `--cumulative-mode {initial_plus_observed,dedup,cn}` (cumulative-generator controls);
its `paper2_v12_*` arms plus the standalone CS coverage simulation are enumerated in that note.
Amendment 012 (`notes/paper2_harness_v2_amendment_012.md`) fixes three code bugs and adds
`--no-probe-policy {commit,reject}` (early-trigger behaviour when the observed probe is unavailable),
corrects the `cn` regularization to `C = 2*train_size/n_unique` (C∝1/n), and its `paper2_v13_*` arms
(corrected cn; McNemar α=0.10; causal reject-policy; size-matched RF/LogReg/MLP; strict-`>` baseline)
are enumerated there.
Amendment 013 (`notes/paper2_harness_v2_amendment_013.md`) adds the exact-zero-collision stream
(global value-dedup + abort-on-exhaustion; `--disjoint-window-frac`, UNSW-full at window 64 for
pool feasibility), `--min-calib-windows`, the stratified per-class gate `labeled_probe_strat`, and
the symmetric-A/B mechanism control; its `paper2_v14*_*` arms are enumerated there.
The final-q1 protocol (`notes/q1_max_protocol.md`, frozen with registered deltas D1–D7 over
`PLAN_Q1_CLAUDE_CODE.md`) adds `--vbc-defer-mode {accumulate,cohort,refresh}` (defer-continuation
semantics; the accumulate mode's weak-conditional-null guarantee is Proposition 1 / supplement §S4),
the per-seed symmetric-A/B output + scaler/PCA decomposition (`--decompose`, `--seed-start/--seed-end`,
`--out-suffix` on `paper2_symmetric_ab_final`), and the bootstrap CI-based equivalence analysis
(`python -m src.analysis.paper2_ab_equivalence`). Its four experiment blocks:

- **Budget frontier (D3)**, seeds 501–530: driven end to end by the committed driver
  `python -m src.experiments.run_q1_budget_frontier --run` — the 99-arm grid and every fixed
  parameter live in `configs/q1_budget_frontier_v2.json`, and each arm records its exact
  command, resolved configuration, environment and completion marker
  (`--list-arms`/`--dry-run`/`--only-arm`/`--range`/`--resume`/`--force`/`--validate-complete`).
  Equivalent per-arm invocation: `run_paper2_readaptation_v2` with
  `--adaptation-gate {labeled_probe_ebcs_defer,vbc_sg}`, `--probe-size {64,128,256,512,1024}`,
  `--seq-block 16 --defer-windows 5 --lifetime-alpha 0.10 --alpha-spending {bonferroni,pseries}`,
  on {PortScan full, ToN full, ToN zero-drift}; anchors `none` / `labeled_probe` /
  `labeled_probe --gate-margin 0.001` (strict). Aggregate:
  `python -m src.analysis.make_paper2_q1_frontier` (endpoints e1–e6 + non-vacuity verdict).
- **Confirmatory A/B (D2)**, seeds 2001–2100:
  `python -m src.analysis.paper2_symmetric_ab_final --seed-start 2001 --seed-end 2100
  --models svc_rbf --conditions independent,own_transformer --decompose
  --out-suffix _conf2001_2100`, then `paper2_ab_equivalence`.
- **Chronological matrix (D4)**, seeds 601–630: `run_paper2_temporal_stream` over the seven
  pre-enumerated streams (Tue→Wed+Thu+Fri, Wed→Fri, Thu→Fri, Wednesday and Thursday intra-day
  splits staged by `prepare_paper2_cicids_intraday_chronological --day {wednesday,thursday}`,
  and UNSW at `prepare_paper2_unsw_chronological --train-frac {0.20,0.40}`), each under
  `--adaptation-gate {none,labeled_probe,labeled_probe + --gate-margin 0.001,vbc_sg}`
  (`--vbc-defer-mode cohort`). Aggregate: `make_paper2_q1_chronological`.
- **Operational acquisition-yield and delay simulation (D5)**, seeds **801–830** (the earlier
  701–730 window is a pilot: it was inspected before the dual-sample redesign):
  `run_paper2_operational_e2e` with `--probe-prevalence {0.005,0.01,0.05,0.10}`,
  `--acquisition-policy {random,alert_enriched,disagreement,hybrid}`,
  `--candidate-latency/--probe-latency {5,20}`, `--training-delay {0,5}`, `--probe-size 64`
  and **`--dual-sample`**. The last flag is what makes the arm statistically valid: it splits
  the adjudication budget into an enriched *discovery* half (measures attack-finding yield
  only) and an independent uniform *validation* half at operating prevalence (the only sample
  the commit rule sees, compared by plain accuracy). Scope: the evaluation stream and detector
  calibration remain balanced, and the candidate training batch remains balanced per class
  with its acquisition cost not modeled — the arm measures label-acquisition yield; it does not
  price the commit pipeline end to end. It runs inside the pool-based harness and is
  **not** the leakage-free observed-data arm.
  Aggregate: `make_paper2_q1_e2e`. Tables for all four: `make_paper2_q1_tables`.

Three cross-cutting artifacts complete the final phase:

```bash
python -m src.analysis.make_final_experiment_ledger   # results/final_experiment_ledger.csv:
                                                      #   block -> tier, script, seeds,
                                                      #   protocol, manuscript table
python -m src.analysis.make_paper2_q1_multiplicity    # Holm (confirmatory core) + BH
                                                      #   (follow-up blocks); supplement S5
python -m src.analysis.make_final_manifest            # manifest incl. ledger summary and the
                                                      #   immediate/deferred harm accounting
```

**Harmful-commit accounting.** Every risk gate writes `paper2_v2_resolution_log.csv`: one row
per resolved proposal with its *real* resolution window, whether it was immediate or deferred,
the delay, and the incumbent-vs-challenger balanced accuracy over the windows that follow the
**resolution** at horizons 1/3/5/10 and until the next decision. Commits whose horizon runs
past the end of the stream are marked censored. This is what lets the harmful-commit rate
cover deferred commits; scoring only the immediate ones left ~35% of the frontier's commits
unevaluated in the previous release.
The final-kbs protocol (`notes/final_kbs_protocol.md`, frozen copy of the reviewer's max-ceiling plan)
adds the named VBC-SG policy (`--adaptation-gate vbc_sg`: stratified per-class EB-CS + commit/reject/
defer + lifetime alpha spending via `--lifetime-alpha/--alpha-spending {bonferroni,pseries}`), the
exact stratified baseline (`labeled_probe_exact_strat`), `--candidate-latency` (end-to-end lite), the
unified window-64 causal matrix (`paper2_fk_*_c64_*`), the operational-prevalence sweep
(`paper2_fk_*_e2e*`), and the 4-condition disjoint role-randomized symmetric A/B.

**Symmetric-pipeline dynamic replication (v1.21 — the central new evidence block).**
Registered protocol `notes/paper2_symmetric_pipeline_dynamic_protocol_001.md` (frozen commit
`8838566`; margins + machine-evaluable A/B/C decision rules in Appendix A, commit `96576bb`);
config `configs/symmetric_pipeline_dynamic_v1.json`. Incumbent and challengers are
self-contained `ModelPipeline`s over a shared raw stream (`src/experiments/symmetric_pipeline.py`);
the drift monitor keeps the initial-transformer representation under both policies
(`DetectorPipeline`). 42 arms = 6 scenarios (PortScan/UNSW-Recon/ToN-IoT × full/zero drift)
× (never + {naive, point, strict} × {frozen_initial_transformer, own_transformer_per_model}),
KS-max, confirmatory seeds 3001–3030 (firewalled: the driver refuses them without
`--confirmatory-authorized`, and always in smoke/parity modes):

```bash
python -m src.experiments.run_symmetric_pipeline_replication --list-arms
python -m src.experiments.run_symmetric_pipeline_replication --parity           # frozen mode is
#   bit-identical to the published v1.20.2 frontier arms (seeds 501-530, byte-level reports)
python -m src.experiments.run_symmetric_pipeline_replication --run --confirmatory-authorized
python -m src.analysis.make_symmetric_pipeline_dynamic_001   # F1-F4 (Holm), equivalence (CI90),
#   recall/FPR NI guardrails, harmful-commit accounting, Scenario A/B/C rules applied literally
python -m src.analysis.make_symmetric_pipeline_tables        # tab:symmetric_pipeline etc.
```

Outputs: `results/raw/symmetric_pipeline/sp_*` (per-arm run_config/command/environment/
raw_stream_hash/completion marker) and `results/tables/symmetric_pipeline_dynamic_001/`
(by_seed, paired_contrasts, multiplicity, equivalence, security_metrics,
harmful_commit_summary, transformer_interaction, run_completion, CLAIM_INTERPRETATION.json —
machine verdict: **Scenario A**). Invariants (frozen parity, batch/probe identity, leakage,
role symmetry, temporal semantics, determinism, provenance, seed firewall):
`tests/test_symmetric_pipeline.py`.

**Size-matched self-contained challenger control (v1.22 candidate — the decisive final block).**
Registered protocol `notes/paper2_size_matched_own_transformer_protocol_001.md` (frozen commit
`114513f` BEFORE implementation; machine-evaluable P/A/E outcome rules in §6); config
`configs/size_matched_own_transformer_v1.json` (SHA-256 recorded in every arm's `run_config.json`).
21 arms = 3 zero-drift scenarios × (never + {naive, point, strict} × candidate size {512, 2000}/class),
own-transformer only, confirmatory seeds 4001–4030 (firewalled), smoke 4401–4402. The
`--candidate-size-per-class` flag activates the nested canonical draw (`nested_candidate_draw` in the
v2 runner): the 512 batch is bit-identical both to the v1.21.0 draw (5/5 CSVs BIT_IDENTICAL in the
parity run) and to the first 512 rows/class of the 2000 batch (999 proposal pairs verified):

```bash
SM_CFG=configs/size_matched_own_transformer_v1.json
python -m src.experiments.run_symmetric_pipeline_replication --list-arms --config $SM_CFG
python -m src.experiments.run_symmetric_pipeline_replication --parity    --config $SM_CFG
python -m src.experiments.run_symmetric_pipeline_replication --run --confirmatory-authorized --config $SM_CFG
python -m src.analysis.make_size_matched_own_transformer_001  # F1-F4 (Holm), CI90 equivalence,
#   guardrails, future-negative-sign accounting, nesting audit, P/A/E rules applied literally
python -m src.analysis.make_size_matched_tables               # tab:size_matched etc.
```

Outputs: `results/raw/size_matched_own_transformer/sm_*` (per-arm run_config/command/environment/
raw_stream_hash/candidate_provenance.jsonl/completion marker) and
`results/tables/size_matched_own_transformer_001/` (by_seed, paired_contrasts, multiplicity,
equivalence, security_metrics, harmful_commit_summary, candidate_size_interaction,
descriptive_contrasts, run_completion, CLAIM_INTERPRETATION.json — machine verdict:
**ATTENUATION**, with the substantive reading — mean zero-drift harm equivalent to zero within the
preregistered ±0.5-pp margin — recorded alongside). Invariants
(flag-off bit-parity, nesting, raw-stream pairing, probe identity, leakage, hyperparameter
identity, complete-bundle commit, determinism, seed firewall, metric recomputation, sealed
v1.21.0 artifact unchanged): `tests/test_size_matched_control.py`.

**Real chronological streams** (corrected runner, amendment 004; Friday seeds 165–194, Wednesday 196–225,
Thursday 227–256):

```bash
python -m src.experiments.run_paper2_temporal_stream \
  --data-train data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv \
  --data-stream data/raw/cicids2017/MachineLearningCVE/Friday-WorkingHours-Morning.pcap_ISCX.csv \
                data/raw/cicids2017/MachineLearningCVE/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv \
                data/raw/cicids2017/MachineLearningCVE/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv \
  --seeds 165,...,194 --adaptation-gate labeled_probe \
  --outdir results/raw/paper2_v6_temporal_fri_labeled_probe
```

## 4. Analysis → tables and figures (all read the raw window/summary CSVs)

```bash
python -m src.analysis.aggregate_paper2_phase2_gated       # Phase 2 verdict + paired CIs
python -m src.analysis.make_paper2_oracle_regret_decision  # decision oracle-regret (r=-0.89 story)
python -m src.analysis.make_paper2_ba_f1_summary           # regime taxonomy (BA + attack-F1), Fig 1 data
python -m src.analysis.make_paper2_budget_curve            # Phase 2b label-efficiency frontier + benefit regimes
python -m src.analysis.make_paper2_paper_tables            # Tables 1-5 (Markdown + LaTeX booktabs)
python -m src.analysis.make_paper2_figures                 # Figs 1-4 (spectrum, mechanism, regret, gate)
python -m src.analysis.make_paper2_mechanism_law_robustness # Table 7: LORO/LODO/per-seed robustness of r
python -m src.analysis.aggregate_paper2_replay_baseline     # Phase 2i: replay baseline verdict
python -m src.analysis.aggregate_paper2_probe_prevalence    # Phase 2j: probe-prevalence verdict
python -m src.analysis.aggregate_paper2_size_dim_controls   # Phase 2k: candidate-size / full-dim controls
python -m src.analysis.aggregate_paper2_v2_replication      # Harness-v2 registered replication verdict
python -m src.analysis.aggregate_paper2_amendment_004       # v2 robustness suite, cost table, temporal streams
python -m src.analysis.aggregate_paper2_amendment_005       # split two-stage, monitor budgets, stratified/UNSW temporal
python -m src.analysis.aggregate_paper2_amendment_006       # causal observed-data gate, binomial-prevalence probes,
                                                           #   McNemar gate, mild-drift prediction test, harm breadth
python -m src.analysis.aggregate_paper2_amendment_009_tail  # amendment 009: tail/worst-case/CVaR metrics (item 8)
python -m src.analysis.aggregate_paper2_amendment_009       # amendment 009: 4-classifier + no-PCA mild/zero drift,
                                                           #   zero-drift generator sweep (ensemble/sliding/cumulative/replay),
                                                           #   confidence-sequence gate, Tuesday chronological
python -m src.analysis.make_paper2_amendment009_table       # Table (tab:amendment009) -> tables/ and tables_ieee/
python -m src.analysis.aggregate_paper2_amendment_011        # amendment 011: leakage-free causal, cumulative
                                                           #   controls, EB-CS budget sweep, per-stream harmful-commit
python -m src.analysis.paper2_cs_coverage_011               # amendment 011: CS empirical coverage (iid/no-replace/autocorr)
python -m src.analysis.aggregate_paper2_amendment_012        # amendment 012: cn fix, McNemar a=0.10, causal reject-policy,
                                                           #   size-matched RF/LogReg/MLP zero-drift, strict-> baseline
python -m src.analysis.aggregate_paper2_amendment_013        # amendment 013: FINAL leakage-free observed-data arm, stratified gate,
                                                           #   strict outside zero drift, calib-min sweep
python -m src.analysis.paper2_symmetric_ab_013               # amendment 013: symmetric-A/B mechanism control (superseded)
python -m src.analysis.make_paper2_causal_final_table        # Table 8 emitter (superseded by final-kbs)
python -m src.analysis.aggregate_paper2_amendment_014        # amendment 014: stratified/defer/lifetime gates, e2e-lite
python -m src.analysis.paper2_symmetric_ab_014               # amendment 014: A/B disjoint + role-randomized (2 conditions)
python -m src.analysis.aggregate_paper2_final_kbs             # final-kbs: causal-64 matrix, VBC-SG, prevalence sweep
python -m src.analysis.paper2_symmetric_ab_final              # final-kbs: A/B 4 conditions (the mechanism table)
python -m src.analysis.make_paper2_final_tables               # final tables: causal-64 (tab:causal_probe) + tab:symmetric_ab
python -m src.analysis.paper2_decision_quality_004          # per-trigger decision metrics + hierarchical model (004 spec)
python -m src.analysis.paper2_decision_quality_005          # regime x seed clusters, VIFs, QK extension, horizon regret
python -m src.analysis.paper2_policy_frontier_005           # policy frontier + operational-utility scenarios
python -m src.analysis.validate_monitors_vs_river           # DDM/ADWIN unit cross-check vs river
```

Or run the whole derived pipeline in one command (`make reproduce` = analysis + manifest + audit;
`make final-paper` = hash verification + invariant tests (`tests/`) + analysis + final tables + figures +
`results/final_manifest.json` + CAS/supplement/IEEE compilation + the 439-check audit — the P10 workflow).
The small confirmatory CSVs are **committed** under `results/tables/` and pinned by
`results/tables/MANIFEST.sha256`; regenerated outputs can be diffed against them. The
UNSW chronological staging is `python -m src.analysis.prepare_paper2_unsw_chronological`
(raw captures 1–4 sorted by Stime; train = first 30% of the timeline).

Outputs: `results/tables/paper2_*` and `results/figures/paper2/*.{png,pdf}`.

## 5. Key claims → where to check

| Claim | Artifact |
|---|---|
| Readaptation ranges benefit→harm across 3 datasets | `paper2_metrics_ba_f1_summary_001/`, Supp §S1.1 |
| Benefit ~ deployed-model degradation, r = −0.89 (descriptive; coupling-aware) | Supp §S1.1/S3 (`make_paper2_figures`) |
| The law survives disaggregation (r = −0.91 per-seed) and any leave-one-out | `paper2_mechanism_law_robustness_001/`, Supp §S3 |
| Replay retraining does not rescue naive triggering; the gate composes with it | `paper2_phase2i_replay_baseline_001/`, Supp §S1.5 |
| Natural-prevalence probes: the initial "probe need not be balanced" claim is RETRACTED; the corrected Binomial rerun holds to π≈0.05 and dissolves at π=0.01 | `paper2_phase2j_probe_prevalence_001/` (superseded) + amendment-006 binomial arms; main §5.3, Supp §S2.3 |
| Harm is not a size/PCA artifact: deepens with size-matched candidates; persists point-wise at full dim | `paper2_phase2k_size_dim_controls_001/`, Supp §S1.5 |
| Registered replication (harness v2, common streams, disjoint partitions, fresh seeds): all criteria pass; per-trigger mechanism (r_deg −0.65..−0.70 vs r_score ≈0) | `paper2_v2_replication_001/`, §5.3, tag `harness-v2-protocol` |
| Hierarchical per-trigger model, regime×seed clusters (β_deg −1.02 [−1.61,−0.43]; score ≈ 0) + decision metrics (local per-decision regret ~22× lower than always-commit in the harm regime) | `paper2_decision_quality_004/` + `paper2_decision_quality_005/` |
| v2 robustness: budget (b=32 operating point; b=8 corrected), latency 20, corruption (harm-avoidance to 40%, net benefit to 25%) | `paper2_amendment_004/robustness.csv` |
| Split two-stage gate: 69% fewer candidates, ~½ of naive's total labels, above naive; net gain vs never-adapt honestly unresolved at 30 seeds | `paper2_amendment_005/` + `paper2_amendment_004/label_cost.csv` |
| Total label/compute accounting per policy (candidates dominate; probe ≈3% of the gate's bill) | `paper2_amendment_004/label_cost.csv`, label-cost table (§5.3) |
| DDM/ADWIN validated vs reference implementations (river): DDM net-harm replicates; our ADWIN variant under-fires, reference reported | `paper2_monitor_validation_004.csv`, `paper2_v6_*_{ddm,adwin}river_none/` |
| Calibrated soft ensemble: strongest label-free rule, harm-avoiding everywhere, beats gate in marginal regime, cannot decline updates | `paper2_v6_*_enscal_none/`, `paper2_amendment_004/robustness.csv` |
| Chronological streams (corrected runner): deep-benefit recoveries on all CICIDS days; gate premium on Friday/Thursday BA, gate ahead on overall accuracy; no premium on Wednesday or external UNSW | `paper2_amendment_004/temporal.csv`, temporal-streams table (§5.3), Supp §S2.6 |
| Causal-64 matrix, VBC-SG frontier, prevalence sweep (final-kbs) | `paper2_final_kbs/`, Tables causal_probe/symmetric_ab, §5.3 |
| Symmetric-pipeline replication (Scenario A): mean full-drift harm does not persist under self-contained pipelines (+7.21/+2.55/+1.03); ownership interaction up to +5.98; zero-drift harm persists (−1.74/−0.65 material, −0.38 resolved) and gates recover it (6/6 Holm-sig.); unsw_zero strict = recall↔FPR trade-off | `symmetric_pipeline_dynamic_001/` (CLAIM_INTERPRETATION.json), tab:symmetric_pipeline, Supp §S7 |
| Frozen-mode parity: the new self-contained harness reproduces published v1.20.2 arms bit-for-bit (4 arms × 30 seeds; deferred arm 5/5 files byte-identical) | `results/smoke/symmetric_pipeline/parity/*/parity_report.json` |
| Detector score carries no consistent incremental signal within triggered decisions (oracle-regret, invariance) | `paper2_oracle_regret_decision_001/`, Supp §S1.1–S1.2 |
| Simple k-of-n/cooldown policies fail (pre-registered) | Supp §S1.3/S3; `notes/paper2_safe_readaptation_phase1_*` |
| Label-efficient gate solves it (30 seeds, both detectors) | `paper2_phase2_gated_readaptation_001/`, Supp §S1.4 |
| ~how few labels suffice (label-efficiency frontier) | `paper2_phase2b_budget_curve_001/`, Supp §S1.5 |

## 6. Notes

- Quantum kernels are classically simulated; runtimes are simulation figures.
- The gate assumes a small labeled probe at decision time; the probe budget is the reported cost (Supp §S1.5).
- Pre-registration precedes the confirmatory 30-seed run; Phase 2b (budget curve, extra benefit regimes) is
  explicitly labeled post-registration robustness.
