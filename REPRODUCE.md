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
python -m src.analysis.paper2_decision_quality_004          # per-trigger decision metrics + hierarchical model (004 spec)
python -m src.analysis.paper2_decision_quality_005          # regime x seed clusters, VIFs, QK extension, horizon regret
python -m src.analysis.paper2_policy_frontier_005           # policy frontier + operational-utility scenarios
python -m src.analysis.validate_monitors_vs_river           # DDM/ADWIN unit cross-check vs river
```

Or run the whole derived pipeline in one command (`make reproduce` = analysis + manifest + audit).
The small confirmatory CSVs are **committed** under `results/tables/` and pinned by
`results/tables/MANIFEST.sha256`; regenerated outputs can be diffed against them. The
UNSW chronological staging is `python -m src.analysis.prepare_paper2_unsw_chronological`
(raw captures 1–4 sorted by Stime; train = first 30% of the timeline).

Outputs: `results/tables/paper2_*` and `results/figures/paper2/*.{png,pdf}`.

## 5. Key claims → where to check

| Claim | Artifact |
|---|---|
| Readaptation ranges benefit→harm across 3 datasets | `paper2_metrics_ba_f1_summary_001/`, Table 1, Fig 1 |
| Benefit ~ deployed-model degradation, r = −0.89 | Fig 2 (`make_paper2_figures`) |
| The law survives disaggregation (r = −0.91 per-seed) and any leave-one-out | `paper2_mechanism_law_robustness_001/`, Table 7 |
| Replay retraining does not rescue naive triggering; the gate composes with it | `paper2_phase2i_replay_baseline_001/`, §5.6 |
| The probe need not be balanced: full safety/benefit at natural prevalence (π=0.10/0.01) | `paper2_phase2j_probe_prevalence_001/`, §5.6 |
| Harm is not a size/PCA artifact: deepens with size-matched candidates; persists point-wise at full dim | `paper2_phase2k_size_dim_controls_001/`, §5.6 |
| Registered replication (harness v2, common streams, disjoint partitions, fresh seeds): all criteria pass; per-trigger mechanism (r_deg −0.65..−0.70 vs r_score ≈0) | `paper2_v2_replication_001/`, §5.10, tag `harness-v2-protocol` |
| Hierarchical per-trigger model (β_deg −1.02 [−1.17,−0.87]; score/severity/time ≈ 0) + decision metrics (regret 22× lower than always-commit in the harm regime) | `paper2_decision_quality_004/` |
| v2 robustness: budget (b=32 operating point; b=8 corrected), latency 20, corruption (harm-avoidance to 40%, net benefit to 25%) | `paper2_amendment_004/robustness.csv` |
| Two-stage gate: 74% fewer candidates, ~½ of naive's total labels, still net-positive in the harm regime | `paper2_amendment_004/robustness.csv` + `label_cost.csv` |
| Total label/compute accounting per policy (candidates dominate; probe ≈3% of the gate's bill) | `paper2_amendment_004/label_cost.csv`, Table 9 |
| DDM/ADWIN validated vs reference implementations (river): DDM net-harm replicates; our ADWIN variant under-fires, reference reported | `paper2_monitor_validation_004.csv`, `paper2_v6_*_{ddm,adwin}river_none/` |
| Calibrated soft ensemble: strongest label-free rule, harm-avoiding everywhere, beats gate in marginal regime, cannot decline updates | `paper2_v6_*_enscal_none/`, `paper2_amendment_004/robustness.csv` |
| Chronological streams (corrected runner): deep-benefit recoveries on all three days; gate premium on Friday/Thursday BA, gate ahead on overall accuracy; no premium on Wednesday | `paper2_amendment_004/temporal.csv`, Table 8 |
| Detector is not the lever (oracle-regret, invariance) | `paper2_oracle_regret_decision_001/`, Table 4, Fig 3 |
| Simple k-of-n/cooldown policies fail (pre-registered) | Table 5; `notes/paper2_safe_readaptation_phase1_*` |
| Label-efficient gate solves it (30 seeds, both detectors) | `paper2_phase2_gated_readaptation_001/`, Tables 2-3, Fig 4 |
| ~how few labels suffice (label-efficiency frontier) | `paper2_phase2b_budget_curve_001/`, Fig 5 |

## 6. Notes

- Quantum kernels are classically simulated; runtimes are simulation figures.
- The gate assumes a small labeled probe at decision time; the probe budget is the reported cost (Fig 5).
- Pre-registration precedes the confirmatory 30-seed run; Phase 2b (budget curve, extra benefit regimes) is
  explicitly labeled post-registration robustness.
