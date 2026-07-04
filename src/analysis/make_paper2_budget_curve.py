"""Phase 2b: label-budget curve + extra benefit regimes for the gate (post-registration robustness).

Reads the labeled-probe gate at budgets {8,16,24,32,48,64,96,128} (KS-max, 30 seeds) and plots
gain-vs-no-adaptation as a function of labels used per regime — the label-efficiency frontier.
Also summarizes the gate on additional benefit regimes (Wednesday, DDoS). No new experiments here;
this only aggregates results/raw/paper2_phase2{,b}_* produced by run_paper2_progressive_readaptation.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW = "results/raw"
OUTT = "results/tables/paper2_phase2b_budget_curve_001"
OUTF = "results/figures/paper2"
CORE = ["portscan", "unsw_recon", "ton_scanning"]
BENEFIT_EXTRA = ["wednesday", "ddos"]
BUDGETS = [8, 16, 24, 32, 48, 64, 96, 128]
RLABEL = {"portscan": "PortScan (benefit)", "unsw_recon": "UNSW Recon (mixed)",
          "ton_scanning": "ToN-IoT (harm)", "wednesday": "Wednesday (benefit)", "ddos": "DDoS (benefit)"}
RCOLOR = {"portscan": "#2a9d8f", "unsw_recon": "#e9c46a", "ton_scanning": "#e76f51",
          "wednesday": "#264653", "ddos": "#8ab17d"}


def _dir(regime, tag):
    """Prefer phase2 (pre-registered) dirs for lp32/lp64 on core regimes; else phase2b."""
    for base in (f"{RAW}/paper2_phase2_{regime}_ks_max_{tag}",
                 f"{RAW}/paper2_phase2b_{regime}_ks_max_{tag}"):
        p = f"{base}/paper2_progressive_readaptation_by_seed.csv"
        if os.path.exists(p):
            return p
    return None


def _load(regime, tag):
    p = _dir(regime, tag)
    return pd.read_csv(p) if p else None


def main():
    os.makedirs(OUTT, exist_ok=True)
    os.makedirs(OUTF, exist_ok=True)

    rows = []
    for regime in CORE + BENEFIT_EXTRA:
        none = _load(regime, "none")
        if none is None:
            continue
        na = none[none.method == "no_adaptation"]["mean_balanced_accuracy"].mean()
        naive = none[none.method == "ks_max"]["mean_balanced_accuracy"].mean()
        rows.append(dict(regime=regime, budget=0, policy="no_adapt", BA=round(na, 5), gain_pts=0.0, labels=0.0))
        rows.append(dict(regime=regime, budget=-1, policy="naive", BA=round(naive, 5),
                         gain_pts=round((naive - na) * 100, 3), labels=0.0))
        budgets = BUDGETS if regime in CORE else [32, 64]
        for b in budgets:
            d = _load(regime, f"lp{b}")
            if d is None:
                continue
            e = d[d.method == "ks_max"]
            rows.append(dict(regime=regime, budget=b, policy=f"lp{b}",
                             BA=round(e["mean_balanced_accuracy"].mean(), 5),
                             gain_pts=round((e["mean_balanced_accuracy"].mean() - na) * 100, 3),
                             labels=round(e["labels_used_total"].mean(), 1)))
    T = pd.DataFrame(rows)
    T.to_csv(f"{OUTT}/paper2_phase2b_budget_curve.csv", index=False)

    # Figure: label-efficiency frontier (core regimes) — gain vs labels used
    fig, ax = plt.subplots(figsize=(6, 4))
    for regime in CORE:
        d = T[(T.regime == regime) & (T.budget > 0)].sort_values("labels")
        if len(d):
            ax.plot(d["labels"], d["gain_pts"], "-o", color=RCOLOR[regime], label=RLABEL[regime], ms=4)
        naive = T[(T.regime == regime) & (T.policy == "naive")]
        if len(naive):
            ax.axhline(float(naive["gain_pts"].iloc[0]), color=RCOLOR[regime], ls=":", lw=1, alpha=0.7)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("Labels used per stream (probe budget)")
    ax.set_ylabel("Gain vs no-adaptation (BA pts)")
    ax.set_title("Label-efficiency frontier: a small probe suffices to avoid harm")
    ax.legend(fontsize=8)
    ax.annotate("naive triggering (dotted)", (0.5, 0.04), xycoords="axes fraction", fontsize=7, color="gray")
    fig.savefig(f"{OUTF}/fig5_label_budget_curve.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{OUTF}/fig5_label_budget_curve.pdf", bbox_inches="tight")
    plt.close(fig)

    pd.set_option("display.width", 200)
    print("=== budget curve (core regimes) ===")
    print(T[T.regime.isin(CORE)].to_string(index=False))
    print("\n=== extra benefit regimes ===")
    print(T[T.regime.isin(BENEFIT_EXTRA)].to_string(index=False))
    print("\nwrote", OUTT, "and fig5_label_budget_curve")


if __name__ == "__main__":
    main()
