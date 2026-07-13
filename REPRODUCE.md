# Reproducibility — "Knowing When Not to Retrain"

Artifact for the paper on label-efficient safe readaptation for adaptive NIDS under concept drift.
Everything below regenerates from raw data; results tables/figures live under `results/` (git-ignored) and
are rebuilt by the analysis scripts. Manuscript + bibliography: `manuscript/`.

## 1. Environment

```bash
conda create -n paper2 python=3.11 -y
conda activate paper2
pip install -r requirements.txt      # numpy, pandas, scipy, scikit-learn, matplotlib
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

The **pre-registered Phase 2** protocol (3 regimes × 2 detectors × gates {none, lp32, lp64, unsup}, 30 seeds)
is documented in `notes/paper2_phase2_gated_readaptation_preregistration_001.md`.

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
```

Outputs: `results/tables/paper2_*` and `results/figures/paper2/*.{png,pdf}`.

## 5. Key claims → where to check

| Claim | Artifact |
|---|---|
| Readaptation ranges benefit→harm across 3 datasets | `paper2_metrics_ba_f1_summary_001/`, Table 1, Fig 1 |
| Benefit ~ deployed-model degradation, r = −0.89 | Fig 2 (`make_paper2_figures`) |
| The law survives disaggregation (r = −0.91 per-seed) and any leave-one-out | `paper2_mechanism_law_robustness_001/`, Table 7 |
| Replay retraining does not rescue naive triggering; the gate composes with it | `paper2_phase2i_replay_baseline_001/`, §5.6 |
| The probe need not be balanced: full safety/benefit at natural prevalence (π=0.10/0.01) | `paper2_phase2j_probe_prevalence_001/`, §5.6 |
| Detector is not the lever (oracle-regret, invariance) | `paper2_oracle_regret_decision_001/`, Table 4, Fig 3 |
| Simple k-of-n/cooldown policies fail (pre-registered) | Table 5; `notes/paper2_safe_readaptation_phase1_*` |
| Label-efficient gate solves it (30 seeds, both detectors) | `paper2_phase2_gated_readaptation_001/`, Tables 2-3, Fig 4 |
| ~how few labels suffice (label-efficiency frontier) | `paper2_phase2b_budget_curve_001/`, Fig 5 |

## 6. Notes

- Quantum kernels are classically simulated; runtimes are simulation figures.
- The gate assumes a small labeled probe at decision time; the probe budget is the reported cost (Fig 5).
- Pre-registration precedes the confirmatory 30-seed run; Phase 2b (budget curve, extra benefit regimes) is
  explicitly labeled post-registration robustness.
