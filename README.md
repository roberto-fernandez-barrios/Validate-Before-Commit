# Validate Before Commit

**Label-Efficient Empirical Gating of Drift-Triggered Classifier Updates for Network Intrusion Detection**

![status](https://img.shields.io/badge/status-under%20review-blue)
![reproducible](https://img.shields.io/badge/results-reproducible-success)
![pre-specified](https://img.shields.io/badge/protocol-pre--specified-important)
![python](https://img.shields.io/badge/python-3.11-blue)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21322256.svg)](https://doi.org/10.5281/zenodo.21322256)

![Graphical abstract](docs/img/graphical_abstract.png)

Machine-learning intrusion detectors degrade under network **concept drift**, so adaptive systems retrain their
classifiers. The field treats model updating as a **drift-detection** problem: fire a monitor, retrain on the
alarm, deploy. This repository shows that the ungoverned step is the *deployment*: always deploying the
retrained candidate is incomplete and sometimes harmful — and a small commit-time check fixes it.

> **Drift detectors answer "did the distribution change?". An adaptive IDS needs "will deploying this retrained
> candidate improve the classifier?". These are different questions — and the gap between them is where harmful
> updates live.**

---

## TL;DR

- Across **three public benchmarks** (CICIDS2017, UNSW-NB15, ToN-IoT) and multiple attack regimes, the value of
  drift-triggered retraining spans **+19.5 to −4.5 balanced-accuracy points**. For a fragile downstream model,
  *never adapting* can beat every triggered strategy.
- Whether an update helps tracks **how degraded the deployed model already is**: retraining restores
  accuracy to a nearly regime-invariant level, so the benefit is the deployed model's *headroom* — a quantity
  drift-detector scores do not measure (at individual triggered decisions a hierarchical model gives
  β_deg = −1.02 [−1.17, −0.87] vs β_score ≈ 0). The detector — classical two-sample test or quantum-kernel
  MMD — is **not the lever**.
- Simple confirmation/cooldown policies and a 50/50 replay strategy do **not** fix it (pre-specified negatives).
- **The fix:** a **validate-before-commit gate** — the loop retrains its candidate as usual, and the gate decides
  **deployment**: commit only if the candidate beats the incumbent on a small labeled probe (32 flows — the
  *decision's* incremental cost; candidates themselves consume ~1,024 labels/trigger, fully accounted in the paper).
  Confirmed by a **replication registered before execution** on a hardened harness (bit-identical streams, disjoint
  partitions, pristine seeds) across two detectors and four downstream models; robust to 20-window label latency
  and harm-avoiding up to 40% randomly flipped probe labels (net benefit survives to 25%).
- **Honest boundary:** on real chronological streams sitting deep in the benefit regime, the gate pays a measurable
  insurance premium in balanced accuracy vs always-deploy (it inherits its probe's metric and composition); on the
  same streams it *beats* always-deploy on overall accuracy. Where the incumbent stays healthy — where the gate's
  value concentrates — it is net-positive everywhere we measured.

---

## Key findings

**1 — Readaptation is regime-dependent and sometimes harmful.**

![Regime spectrum](docs/img/fig1_regime_spectrum.png)

**2 — Retraining restores accuracy to a nearly regime-invariant level, so the benefit of an update is the deployed
model's headroom. Per-trigger, non-coupled test (hardened harness): pre-trigger incumbent degradation predicts the
future value of committing; the detector score at the same triggers predicts nothing (coupling-aware analysis §5.3;
hierarchical model §5.10).**

![Per-trigger mechanism](docs/img/fig9_pertrigger.png)

**3 — The validate-before-commit gate preserves benefit, avoids harm, and beats both naive retraining and
never-adapting — identically for a classical (KS-max) and a quantum (QK-ZZ) detector.**

![Gate results](docs/img/fig4_phase2_gate.png)

**4 — The gate is harm-avoiding under randomly corrupted validation labels: at up to 40% flipped labels it stays
significantly above naive in the harm regime; net benefit over no-adaptation survives to 25% (hardened-harness
numbers in the paper, §5.10).**

![Adversarial probe](docs/img/fig8_probe_poison.png)

---

## Results at a glance (ToN-IoT harm regime — registered replication, harness v2, pristine seeds 104–133)

| Detector | naive (always deploy) | **validate-before-commit gate** | gate vs naive (CI95) | gate vs never-adapt (CI95) |
|---|---:|---:|---|---|
| KS-max (classical) | −1.64 | **+0.79** | +2.43 [1.53, 3.43] | +0.79 [0.53, 1.07] |
| QK-ZZ (quantum) | −2.91 | **+0.72** | +3.63 [1.66, 6.38] | +0.72 [0.44, 0.99] |

Balanced-accuracy points vs. the shared no-adaptation baseline (truly paired: all arms process bit-identical
streams). The v2 **label-budget sweep** puts the operating point at b = 32: at b = 8 the gate still reduces harm
(+1.22 above naive) but is no longer net-positive vs never adapting — the initial study's "8 labels suffice" is
corrected accordingly. A **two-stage** variant that health-checks the incumbent *before* training candidates cuts
total labels below half of naive's (1,182 vs 2,594 per stream) and stays net-positive (+0.16 [0.03, 0.31]).

---

## The method

On every triggered drift the loop retrains a **candidate** model as usual; the gate decides **deployment**:
commit only if the candidate beats the incumbent on a small labeled probe drawn from current traffic (default
32 flows); otherwise the incumbent is kept. A **two-stage** variant spends the same probe on the incumbent
*before* training and skips candidate construction when the incumbent is healthy — gating the training decision
itself (and its ~1,024 labels). Ablations delimit the method: among the evaluated gates, the label-free variants
(disagreement, ATC, DoC) either fail or sacrifice benefit; a properly *calibrated* soft ensemble is the strongest
label-free update rule (harm-avoiding everywhere, ahead of the gate in the marginal regime) but commits every
trigger and cannot decline an update; simple **k-of-n / cooldown** policies fail because they act on
distributional change rather than estimated model improvement. See `manuscript/` §3 (Algorithm 1) for the
full specification.

Enabled by flags on the v2 runner (`src/experiments/run_paper2_readaptation_v2.py`):
`--adaptation-gate {none,labeled_probe,labeled_probe_holdout,labeled_probe_lcb,unsup_disagree,atc,doc,two_stage}`,
`--probe-size`, `--probe-latency`, `--probe-flip-frac`, `--gate-margin`,
`--adapt-strategy {full_replace,ensemble,ensemble_cal,sliding_window}`,
`--trigger-mode {detector,performance,ddm,adwin,ddm_river,adwin_river}`,
`--downstream-model {svc_rbf,random_forest,logreg,mlp}`.

---

## Repository structure

```
manuscript/     Manuscript draft (§1–§8) + references.bib
src/experiments/  Progressive-drift readaptation runner (detectors, gate, downstream models)
src/analysis/     Reproducible aggregation, statistics, tables and figures
results/          Generated tables/figures (git-ignored; rebuilt by the scripts)
data/             Public benchmark datasets (git-ignored; see Data availability)
docs/img/         Figures used in this README
notes/            Protocols, pre-registrations, and checkpoints
REPRODUCE.md      One-command regeneration of every table and figure
```

## Reproducing the results

```bash
conda create -n paper2 python=3.11 -y && conda activate paper2
pip install -r requirements.txt
# place the datasets under data/ (see below), then:
python -m src.analysis.make_paper2_paper_tables    # Tables 1–6 (Markdown + LaTeX)
python -m src.analysis.make_paper2_figures         # Figures 1–4
python -m src.analysis.make_paper2_budget_curve    # label-efficiency frontier
python -m src.analysis.make_paper2_gate_robustness # latency / harm-breadth / margin / poison (v1)
python -m src.analysis.aggregate_paper2_v2_replication  # registered replication verdict (v2)
python -m src.analysis.aggregate_paper2_amendment_004   # robustness suite, cost table, temporal streams
python -m src.analysis.paper2_decision_quality_004      # decision metrics + hierarchical model
python -m src.analysis.validate_monitors_vs_river       # DDM/ADWIN vs reference implementations
```

A `requirements-lock.txt` (pip freeze of the environment that produced the results) accompanies
`requirements.txt` for exact reproduction.

Full details, including the exact experiment commands and a claim → artifact map, are in
[`REPRODUCE.md`](REPRODUCE.md). The **confirmatory evidence is the registered v2 replication**: protocol
publicly tagged (`harness-v2-protocol`) before any confirmatory seed ran, plus pre-run registered amendments
([002](notes/paper2_harness_v2_amendment_002.md), [003](notes/paper2_harness_v2_amendment_003.md),
[004](notes/paper2_harness_v2_amendment_004.md) — the latter also fixes and re-runs the chronological-stream
experiment). The initial Phase 2 protocol was pre-specified in
[`notes/paper2_phase2_gated_readaptation_preregistration_001.md`](notes/paper2_phase2_gated_readaptation_preregistration_001.md).

## Data availability

The three public benchmarks are **not redistributed** here (place them under `data/`):

- **CICIDS2017** — Sharafaldin, Lashkari & Ghorbani, *ICISSP* 2018.
- **UNSW-NB15** — Moustafa & Slay, *MilCIS* 2015.
- **ToN-IoT** — Alsaedi et al., *IEEE Access* 2020.

## Manuscript

The working manuscript (§1–§8, solution-framed) and its bibliography are in
[`manuscript/`](manuscript/). It is written for a top security / ML venue and is reproducible end-to-end from
this repository.

## Citation

The paper is under review; cite it as below. To cite the **software artifact** itself, use the Zenodo DOI
[10.5281/zenodo.21322256](https://doi.org/10.5281/zenodo.21322256) (metadata in `CITATION.cff`).

```bibtex
@unpublished{fernandezbarrios2026validate,
  title  = {Validate Before Commit: Label-Efficient Empirical Gating of
            Drift-Triggered Classifier Updates for Network Intrusion Detection},
  author = {Fern{\'a}ndez-Barrios, Roberto and Pastor-L{\'o}pez, Iker and
            Pikatza-Huerga, Amaia and Garc{\'i}a Bringas, Pablo},
  year   = {2026},
  note   = {Under review}
}
```

## License

The code and analysis scripts are released under the **MIT License** (see [`LICENSE`](LICENSE)).
Citation metadata for the artifact is provided in [`CITATION.cff`](CITATION.cff) and `.zenodo.json`.
