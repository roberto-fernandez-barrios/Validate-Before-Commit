"""Regenerate the per-trigger mechanism figure (docs/img/fig9_pertrigger.png).

Amendment 007: this figure had been produced ad hoc and its generator was never versioned --- a
reproducibility defect. It is rebuilt here from the committed trigger logs, for BOTH detectors,
with wording that matches what the statistics support: at triggered decisions the incumbent's
recent health predicts the future value of committing, while the detectors' scalar scores show
no consistent association (one small exception, QK/PortScan, is reported in the paper).
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "docs/img"
REGIMES = [("portscan", "PortScan (benefit)", "#2a9d8f"),
           ("unsw_recon", "UNSW Recon (marginal)", "#e9c46a"),
           ("ton_scanning", "ToN-IoT (harm)", "#e76f51")]
SEEDS = set(range(104, 134))


def load(reg: str, det: str) -> pd.DataFrame:
    parts = []
    for d in [f"paper2_v2_{reg}_{det}_none", f"paper2_v2_{reg}_{det}_none_top"]:
        f = f"{RAW}/{d}/paper2_v2_trigger_log.csv"
        if os.path.exists(f):
            parts.append(pd.read_csv(f))
    d = pd.concat(parts)
    return d[d.seed.isin(SEEDS)].dropna(subset=["delta_future5", "deg_pre5", "score"])


def main():
    os.makedirs(OUT, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.2))
    for i, (det, dname) in enumerate([("ks", "KS-max (classical)"), ("qk", "QK-ZZ (quantum)")]):
        data = {r: load(r, det) for r, _, _ in REGIMES}
        allr = pd.concat(data.values())
        for j, (xcol, xlabel) in enumerate([
                ("deg_pre5", "Incumbent BA over the 5 windows BEFORE the trigger"),
                ("score", f"{dname.split()[0]} detector score at the trigger")]):
            ax = axes[i, j]
            for reg, label, color in REGIMES:
                d = data[reg]
                ax.scatter(d[xcol], d["delta_future5"] * 100, s=16, alpha=0.55,
                           color=color, label=label if (i == 0 and j == 0) else None)
            r = float(np.corrcoef(allr[xcol], allr["delta_future5"])[0, 1])
            ax.axhline(0, color="#495057", lw=1, ls="--")
            ax.set_xlabel(xlabel, fontsize=9.5)
            ax.set_ylabel("Candidate $-$ incumbent BA\nover the 5 windows AFTER (pts)", fontsize=9.5)
            title = ("Incumbent health predicts\nthe value of committing"
                     if xcol == "deg_pre5"
                     else "No consistent score–value\nassociation at triggers")
            ax.set_title(f"{dname}\n{title}  (pooled r = {r:+.2f})", fontsize=10, weight="bold")
            ax.tick_params(labelsize=8.5)
            ax.grid(alpha=0.15)
    fig.legend(loc="lower center", ncol=3, frameon=False, fontsize=10, bbox_to_anchor=(0.5, -0.015))
    fig.suptitle("Per-trigger test (harness v2, pristine seeds): predictor and outcome share no algebraic term",
                 fontsize=12.5, weight="bold", y=0.995)
    fig.tight_layout(rect=[0, 0.035, 1, 0.97])
    fig.savefig(f"{OUT}/fig9_pertrigger.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{OUT}/fig9_pertrigger.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {OUT}/fig9_pertrigger.png")


if __name__ == "__main__":
    main()
