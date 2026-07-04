"""Strengthen the mechanism law: benefit ~ deployed-model degradation, across models and regimes.

Pools (no-adaptation BA, adaptation gain) points from (i) the SVC-RBF 7-regime taxonomy (best-detector
gain) and (ii) the 4-downstream x 3-regime generalization runs (KS-max naive gain), and reports the
Pearson r with a bootstrap CI for each and pooled. No new experiments. Adds Fig 2b (pooled scatter).
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TAB = "results/tables"
OUTF = "results/figures/paper2"
rng = np.random.default_rng(20260704)


def boot_r(x, y, nb=5000):
    x, y = np.asarray(x), np.asarray(y)
    n = len(x)
    rs = []
    for _ in range(nb):
        idx = rng.integers(0, n, n)
        if np.std(x[idx]) == 0 or np.std(y[idx]) == 0:
            continue
        rs.append(np.corrcoef(x[idx], y[idx])[0, 1])
    return np.percentile(rs, 2.5), np.percentile(rs, 97.5)


def main():
    pts = []  # (base_BA_pct, gain_pts, source)

    f1 = f"{TAB}/paper2_metrics_ba_f1_summary_001/paper2_fig1_regime_spectrum.csv"
    if os.path.exists(f1):
        d = pd.read_csv(f1)
        for _, r in d.iterrows():
            pts.append((r["noadapt_BA"] * 100, r["best_gain_BA_pts"], "svc_taxonomy"))

    f2 = f"{TAB}/paper2_phase2c_downstream_generalization_001/paper2_downstream_generalization.csv"
    if os.path.exists(f2):
        d = pd.read_csv(f2)
        for _, r in d.iterrows():
            # avoid double-counting SVC on the 3 phase2c regimes (already covered by taxonomy);
            # keep the non-SVC downstream models here
            if r["downstream"] != "svc_rbf":
                pts.append((r["noadapt_BA"] * 100, r["naive_gain"], r["downstream"]))

    P = pd.DataFrame(pts, columns=["base_BA", "gain", "source"])
    os.makedirs(TAB, exist_ok=True)
    points_path = f"{TAB}/paper2_mechanism_law_points.csv"
    P.to_csv(points_path, index=False)

    def report(name, sub):
        if len(sub) < 3 or sub["base_BA"].std() == 0:
            return
        r = np.corrcoef(sub["base_BA"], sub["gain"])[0, 1]
        lo, hi = boot_r(sub["base_BA"].values, sub["gain"].values)
        print(f"{name:22s} n={len(sub):2d}  r={r:+.3f}  CI95=[{lo:+.3f}, {hi:+.3f}]")

    print("Mechanism law: corr(no-adaptation BA, adaptation gain)")
    report("SVC taxonomy (7)", P[P.source == "svc_taxonomy"])
    report("non-SVC downstream (9)", P[P.source != "svc_taxonomy"])
    report("POOLED (all)", P)

    # Fig 2b: pooled scatter
    os.makedirs(OUTF, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5.2, 4))
    for src, c, m in [("svc_taxonomy", "#264653", "o"), ("random_forest", "#2a9d8f", "s"),
                      ("logreg", "#e9c46a", "^"), ("mlp", "#e76f51", "D")]:
        s = P[P.source == src]
        if len(s):
            ax.scatter(s["base_BA"], s["gain"], c=c, marker=m, s=45, edgecolor="k", lw=0.4,
                       label=src.replace("svc_taxonomy", "SVC (7 regimes)").replace("_", " "))
    r = np.corrcoef(P["base_BA"], P["gain"])[0, 1]
    mm, bb = np.polyfit(P["base_BA"], P["gain"], 1)
    xs = np.linspace(P["base_BA"].min(), P["base_BA"].max(), 50)
    ax.plot(xs, mm * xs + bb, "k--", lw=1)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xlabel("Deployed-model BA without adaptation (%)")
    ax.set_ylabel("Adaptation gain (BA pts)")
    ax.set_title(f"Mechanism law across models & regimes (pooled r = {r:.2f})")
    ax.legend(fontsize=7)
    fig.savefig(f"{OUTF}/fig2b_mechanism_law_pooled.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{OUTF}/fig2b_mechanism_law_pooled.pdf", bbox_inches="tight")
    plt.close(fig)
    print("\nwrote", points_path, "and fig2b_mechanism_law_pooled")


if __name__ == "__main__":
    main()
