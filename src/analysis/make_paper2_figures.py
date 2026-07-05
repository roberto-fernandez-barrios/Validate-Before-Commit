"""Render Paper 2 main figures from aggregated CSVs (no new experiments).

Figures:
  F1  regime spectrum: best adaptation gain vs no-adaptation per dataset x regime (signed).
  F2  mechanism law: base no-adapt BA vs adaptation benefit, r ~= -0.894.
  F3  decision oracle-regret vs harm-frequency per regime/detector.
  F4  Phase 2 gate: gain vs no-adaptation by gate (naive/lp32/lp64/unsup) across regimes.

Reads:
  results/tables/paper2_metrics_ba_f1_summary_001/paper2_fig1_regime_spectrum.csv
  results/tables/paper2_oracle_regret_decision_001/paper2_oracle_regret_by_detector.csv
  results/tables/paper2_phase2_gated_readaptation_001/paper2_phase2_summary.csv
Outputs PNG+PDF to results/figures/paper2/.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TAB = "results/tables"
OUT = "results/figures/paper2"
SIGN_COLORS = {"benefit": "#2a9d8f", "marginal": "#e9c46a", "mixed": "#e9c46a", "harmful": "#e76f51"}


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(f"{OUT}/{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{OUT}/{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def fig1_spectrum():
    f = f"{TAB}/paper2_metrics_ba_f1_summary_001/paper2_fig1_regime_spectrum.csv"
    if not os.path.exists(f):
        return
    d = pd.read_csv(f).sort_values("best_gain_BA_pts", ascending=False)
    colors = [SIGN_COLORS.get(k, "#999") for k in d["klass"]]
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.bar(range(len(d)), d["best_gain_BA_pts"], color=colors)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(range(len(d)))
    ax.set_xticklabels(d["regime"], rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Best adaptation gain vs\nno-adaptation (BA pts)")
    ax.set_title("Readaptation is regime-dependent and sometimes harmful")
    save(fig, "fig1_regime_spectrum")


def fig2_mechanism():
    f = f"{TAB}/paper2_metrics_ba_f1_summary_001/paper2_fig1_regime_spectrum.csv"
    if not os.path.exists(f):
        return
    d = pd.read_csv(f)
    x = d["noadapt_BA"].values * 100
    y = d["best_gain_BA_pts"].values
    r = np.corrcoef(x, y)[0, 1]
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(x, y, c=[SIGN_COLORS.get(k, "#999") for k in d["klass"]], s=60, zorder=3)
    m, b = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, m * xs + b, "k--", lw=1)
    # per-label offsets (dx, dy, ha) to avoid overlapping the trend line / axis / each other
    off = {"ToN-IoT": (5, 7, "left"), "Reconnaissance": (-8, -12, "right")}
    for _, row in d.iterrows():
        name = row["regime"].replace("CICIDS ", "").replace("UNSW-NB15 ", "").replace(" Scanning", "")
        dx, dy, ha = off.get(name, (4, 3, "left"))
        ax.annotate(name, (row["noadapt_BA"] * 100, row["best_gain_BA_pts"]), fontsize=7,
                    xytext=(dx, dy), textcoords="offset points", ha=ha)
    ax.set_xlim(x.min() - 2, x.max() + 8)  # right room for the ToN-IoT label; left pad for DDoS
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel("Deployed-model BA without adaptation (%)")
    ax.set_ylabel("Adaptation benefit (BA pts)")
    ax.set_title(f"Adaptation helps only when the model has degraded (r = {r:.2f})")
    save(fig, "fig2_mechanism_law")


def fig3_regret():
    f = f"{TAB}/paper2_oracle_regret_decision_001/paper2_oracle_regret_by_detector.csv"
    if not os.path.exists(f):
        return
    d = pd.read_csv(f)
    d = d[d.detector.isin(["qk_mmd_zz", "energy_distance"])]
    fig, ax = plt.subplots(figsize=(5.2, 4))
    for det, mk in [("qk_mmd_zz", "o"), ("energy_distance", "s")]:
        s = d[d.detector == det]
        ax.scatter(s["harm_seed_pct"], s["regret_pts"], marker=mk, s=55,
                   c=[SIGN_COLORS.get(k, "#999") for k in s["klass"]], edgecolor="k", lw=0.5,
                   label=det.replace("qk_mmd_zz", "QK-ZZ").replace("energy_distance", "Energy"), zorder=3)
    ax.set_xlabel("Streams where adapting hurt (%)")
    ax.set_ylabel("Decision oracle-regret (BA pts)")
    ax.set_title("Regret grows with harm frequency")
    ax.legend(fontsize=8)
    save(fig, "fig3_oracle_regret")


def fig4_phase2():
    f = f"{TAB}/paper2_phase2_gated_readaptation_001/paper2_phase2_summary.csv"
    if not os.path.exists(f):
        return
    d = pd.read_csv(f)
    regimes = ["portscan", "unsw_recon", "ton_scanning"]
    reg_lbl = {"portscan": "PortScan\n(benefit)", "unsw_recon": "UNSW Recon\n(mixed)", "ton_scanning": "ToN-IoT\n(harm)"}
    gates = ["none", "lp32", "lp64", "unsup"]
    gate_lbl = {"none": "naive", "lp32": "gate-32", "lp64": "gate-64", "unsup": "unsup-0"}
    gate_c = {"none": "#adb5bd", "lp32": "#2a9d8f", "lp64": "#1d7870", "unsup": "#e76f51"}
    dets = sorted(d.detector.unique())
    fig, axes = plt.subplots(1, len(dets), figsize=(5.5 * len(dets), 3.6), sharey=True)
    if len(dets) == 1:
        axes = [axes]
    for ax, det in zip(axes, dets):
        w = 0.2
        for gi, g in enumerate(gates):
            vals = [d[(d.regime == r) & (d.detector == det) & (d.gate == g)]["gain_pts"].mean() for r in regimes]
            ax.bar(np.arange(len(regimes)) + gi * w, vals, w, label=gate_lbl[g], color=gate_c[g])
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xticks(np.arange(len(regimes)) + 1.5 * w)
        ax.set_xticklabels([reg_lbl[r] for r in regimes], fontsize=8)
        ax.set_title(det.replace("qk_mmd_zz", "QK-ZZ").replace("ks_max", "KS-max"))
        ax.set_ylabel("Gain vs no-adaptation (BA pts)")
    axes[-1].legend(fontsize=8, title="policy")
    fig.suptitle("Label-efficient gate: preserves benefit, avoids harm — for both detectors")
    save(fig, "fig4_phase2_gate")


if __name__ == "__main__":
    fig1_spectrum()
    fig2_mechanism()
    fig3_regret()
    fig4_phase2()
