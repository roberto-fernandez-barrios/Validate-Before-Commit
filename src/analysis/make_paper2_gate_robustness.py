"""Phase 2d/e/f: gate robustness — label latency, extra harm regimes, commit margin.

Aggregates results/raw/paper2_phase2{d,e,f}_* (SVC-RBF downstream, KS-max, gate lp32) into three tables:
  A (2d) label-latency: gate gain vs probe-lag {0,5,10,20} per regime — does stale labeling break safety?
  B (2e) extra harm regimes: ToN-IoT DDoS/Injection naive vs gate — does harm generalize (SVC) and gate fix it?
  C (2f) commit-margin sweep: gate gain/commits vs margin {0,0.01,0.02,0.05} per regime.
No new experiments. Outputs to results/tables/paper2_gate_robustness_001/ + Fig 7 (label-latency).
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW = "results/raw"
OUT = "results/tables/paper2_gate_robustness_001"
OUTF = "results/figures/paper2"
CORE = ["portscan", "unsw_recon", "ton_scanning"]
RLABEL = {"portscan": "PortScan (benefit)", "unsw_recon": "UNSW Recon (mixed)", "ton_scanning": "ToN-IoT (harm)"}
RCOLOR = {"portscan": "#2a9d8f", "unsw_recon": "#e9c46a", "ton_scanning": "#e76f51"}
EPS = 0.005


def _read(path):
    return pd.read_csv(path) if os.path.exists(path) else None


def _base(regime):
    """no-adapt and naive from the pre-registered phase2 SVC/KS runs."""
    d = _read(f"{RAW}/paper2_phase2_{regime}_ks_max_none/paper2_progressive_readaptation_by_seed.csv")
    if d is None:
        return None, None
    na = d[d.method == "no_adaptation"]["mean_balanced_accuracy"].mean()
    naive = d[d.method == "ks_max"]["mean_balanced_accuracy"].mean()
    return na, naive


def _gain(path, na):
    d = _read(path)
    if d is None or na is None:
        return None, None
    e = d[d.method == "ks_max"]
    return (e["mean_balanced_accuracy"].mean() - na) * 100, e["n_adaptations"].mean()


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(OUTF, exist_ok=True)

    # ---- A: label latency ----
    rowsA = []
    for reg in CORE:
        na, naive = _base(reg)
        for lag in [0, 5, 10, 20]:
            if lag == 0:
                p = f"{RAW}/paper2_phase2_{reg}_ks_max_lp32/paper2_progressive_readaptation_by_seed.csv"
            else:
                p = f"{RAW}/paper2_phase2d_{reg}_lag{lag}/paper2_progressive_readaptation_by_seed.csv"
            g, _ = _gain(p, na)
            if g is None:
                continue
            rowsA.append(dict(regime=reg, probe_lag=lag, gate_gain=round(g, 2),
                              naive_gain=round((naive - na) * 100, 2),
                              gate_avoids_harm=bool(g >= -EPS * 100)))
    A = pd.DataFrame(rowsA)
    A.to_csv(f"{OUT}/paper2_gate_label_latency.csv", index=False)

    # ---- B: extra harm regimes ----
    rowsB = []
    for atk in ["ddos", "injection"]:
        none = _read(f"{RAW}/paper2_phase2e_ton_{atk}_none/paper2_progressive_readaptation_by_seed.csv")
        lp = _read(f"{RAW}/paper2_phase2e_ton_{atk}_lp32/paper2_progressive_readaptation_by_seed.csv")
        if none is None or lp is None:
            continue
        na = none[none.method == "no_adaptation"]["mean_balanced_accuracy"].mean()
        naive = none[none.method == "ks_max"]["mean_balanced_accuracy"].mean()
        gate = lp[lp.method == "ks_max"]["mean_balanced_accuracy"].mean()
        rowsB.append(dict(regime=f"ToN-IoT {atk}", noadapt_BA=round(na, 4),
                          naive_gain=round((naive - na) * 100, 2), gate_gain=round((gate - na) * 100, 2),
                          harm_reproduced=bool(naive < na - EPS), gate_avoids_harm=bool(gate >= na - EPS)))
    B = pd.DataFrame(rowsB)
    B.to_csv(f"{OUT}/paper2_gate_extra_harm_regimes.csv", index=False)

    # ---- C: margin sweep ----
    rowsC = []
    for reg in CORE:
        na, _ = _base(reg)
        for m, tag in [(0.0, None), (0.01, "m01"), (0.02, "m02"), (0.05, "m05")]:
            if tag is None:
                p = f"{RAW}/paper2_phase2_{reg}_ks_max_lp32/paper2_progressive_readaptation_by_seed.csv"
            else:
                p = f"{RAW}/paper2_phase2f_{reg}_{tag}/paper2_progressive_readaptation_by_seed.csv"
            g, commits = _gain(p, na)
            if g is None:
                continue
            rowsC.append(dict(regime=reg, gate_margin=m, gate_gain=round(g, 2), commits=round(commits, 2)))
    C = pd.DataFrame(rowsC)
    C.to_csv(f"{OUT}/paper2_gate_margin_sweep.csv", index=False)

    # Fig 7: label latency (gate gain vs lag)
    if len(A):
        fig, ax = plt.subplots(figsize=(6, 3.8))
        for reg in CORE:
            d = A[A.regime == reg].sort_values("probe_lag")
            if len(d):
                ax.plot(d["probe_lag"], d["gate_gain"], "-o", color=RCOLOR[reg], label=RLABEL[reg], ms=5)
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xlabel("Probe label lag (windows)")
        ax.set_ylabel("Gate gain vs no-adaptation (BA pts)")
        ax.set_title("Gate robustness to label latency (SVC-RBF, KS-max)")
        ax.legend(fontsize=8)
        fig.savefig(f"{OUTF}/fig7_label_latency.png", dpi=200, bbox_inches="tight")
        fig.savefig(f"{OUTF}/fig7_label_latency.pdf", bbox_inches="tight")
        plt.close(fig)

    # ---- D: adversarial / noisy probe (poisoned validation labels) ----
    rowsD = []
    for reg in CORE:
        na, naive = _base(reg)
        for pois, tag in [(0.0, None), (0.1, "10"), (0.2, "20"), (0.4, "40")]:
            if tag is None:
                p = f"{RAW}/paper2_phase2_{reg}_ks_max_lp32/paper2_progressive_readaptation_by_seed.csv"
            else:
                p = f"{RAW}/paper2_phase2g_{reg}_poison{tag}/paper2_progressive_readaptation_by_seed.csv"
            g, commits = _gain(p, na)
            if g is None:
                continue
            rowsD.append(dict(regime=reg, probe_poison=pois, gate_gain=round(g, 2),
                              naive_gain=round((naive - na) * 100, 2), commits=round(commits, 2),
                              still_beats_naive=bool(g >= (naive - na) * 100 - EPS * 100),
                              avoids_harm=bool(g >= -EPS * 100)))
    D = pd.DataFrame(rowsD)
    D.to_csv(f"{OUT}/paper2_gate_probe_poison.csv", index=False)
    if len(D):
        fig, ax = plt.subplots(figsize=(6, 3.8))
        for reg in CORE:
            d = D[D.regime == reg].sort_values("probe_poison")
            if len(d):
                ax.plot(d["probe_poison"] * 100, d["gate_gain"], "-o", color=RCOLOR[reg], label=RLABEL[reg], ms=5)
                nv = D[(D.regime == reg) & (D.probe_poison == 0)]["naive_gain"]
                if len(nv):
                    ax.axhline(float(nv.iloc[0]), color=RCOLOR[reg], ls=":", lw=1, alpha=0.6)
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xlabel("Poisoned probe labels (%)")
        ax.set_ylabel("Gate gain vs no-adaptation (BA pts)")
        ax.set_title("Gate under random label corruption (dotted = naive)")
        ax.legend(fontsize=8)
        fig.savefig(f"{OUTF}/fig8_probe_poison.png", dpi=200, bbox_inches="tight")
        fig.savefig(f"{OUTF}/fig8_probe_poison.pdf", bbox_inches="tight")
        plt.close(fig)

    pd.set_option("display.width", 200)
    print("=== A: label latency ===\n", A.to_string(index=False))
    print("\n=== B: extra harm regimes (ToN-IoT DDoS/Injection, SVC) ===\n", B.to_string(index=False))
    print("\n=== C: commit-margin sweep ===\n", C.to_string(index=False))
    print("\n=== D: adversarial/noisy probe ===\n", D.to_string(index=False))


if __name__ == "__main__":
    main()
