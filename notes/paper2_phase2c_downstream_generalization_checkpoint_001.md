# Paper 2 — Phase 2c: downstream-classifier generalization (important honest finding)

**Date:** 2026-07-04 · **Trigger:** the student asked whether we had extracted maximum value; the biggest
untested axis was downstream-model dependence (everything was SVC-RBF). This experiment answers it.
Artifacts: `results/tables/paper2_phase2c_downstream_generalization_001/`, Table 6, Fig 6.
Code: `--downstream-model {svc_rbf,random_forest,logreg,mlp}`. Analysis: `make_paper2_downstream_generalization`.

## Setup
KS-max trigger, 3 regimes (PortScan/UNSW-Recon/ToN-IoT), gates {none(naive), lp32}, 20 seeds (SVC at 30),
4 downstream classifiers: SVC-RBF, Random Forest, LogReg, MLP.

## Three findings

1. **Mechanism law generalizes (robust core).** Benefit ~ deployed-model degradation for all four models:
   low no-adapt BA → large gain (RF/MLP PortScan start 69–70% → +27; LogReg ToN start 84% → +6.7), high
   no-adapt BA → small gain (RF ToN starts 97% → +1.9). r=−0.89 is a property of the problem, not of SVC.

2. **Net-harm is downstream-SPECIFIC (headline must be qualified).** Naive triggering below no-adaptation
   occurs ONLY for **SVC-RBF on ToN-IoT (−1.36)**. Random Forest (+1.88), LogReg (+6.70) and MLP (+0.24)
   all stay non-negative there. SVC-RBF is fragile enough that retraining on a narrow window loses more than
   it gains; more robust models do not. **We do NOT claim naive readaptation is universally harmful.**

3. **The gate is UNIVERSALLY SAFE (key defensive result).** Across all 4 downstream × 3 regimes (12 cells),
   the labeled-probe gate never underperforms no-adaptation and never underperforms naive triggering
   (Table 6, all "gate avoids harm = yes"). The solution generalizes even where the harm does not.

## Why this matters (and why it was worth running)
A Q1 reviewer testing another downstream model would have found that the dramatic "no-adaptation beats
everything" hook is SVC-specific — a potential rejection landmine. Finding it ourselves:
- removes the landmine;
- generalizes the two most defensible claims (the r=−0.89 law; the gate's safety) across 4 models;
- costs the shock value of the harm hook, but yields a more mature, harder-to-attack paper.

Net effect on Q1: roughly neutral-to-positive — less dramatic headline, but a general safety guarantee and a
general law, and one fewer rejection risk.

## Manuscript integration (done)
Abstract, §5.1, contributions #2/#5, Discussion ("why retraining can hurt, and why it is model-dependent"),
Limitations, and new §5.7 "Generalization across downstream classifiers" + Table 6 + Fig 6. The net-harm
claim is now explicitly conditioned on the fragile SVC-RBF downstream; the law and the gate are framed as the
general results.
