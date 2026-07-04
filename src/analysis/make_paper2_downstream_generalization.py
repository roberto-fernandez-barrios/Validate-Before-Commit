"""Phase 2c: does harmful adaptation AND the gate generalize beyond SVC-RBF downstream?

Aggregates results/raw/paper2_phase2{,c}_* for downstream in {svc_rbf, random_forest, logreg, mlp}
across the 3 regimes, KS-max detector, gate in {none(naive), lp32}. Reports per (downstream, regime):
no-adapt BA, naive gain, gate gain, and three qualitative flags — harm reproduced (naive < no-adapt),
gate avoids harm (gate >= no-adapt - eps), gate preserves/beats naive. No new experiments.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW = "results/raw"
OUTT = "results/tables/paper2_phase2c_downstream_generalization_001"
OUTF = "results/figures/paper2"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
RLABEL = {"portscan": "PortScan (benefit)", "unsw_recon": "UNSW Recon (mixed)", "ton_scanning": "ToN-IoT (harm)"}
DOWNSTREAM = ["svc_rbf", "random_forest", "logreg", "mlp"]
DLABEL = {"svc_rbf": "SVC-RBF", "random_forest": "Random Forest", "logreg": "LogReg", "mlp": "MLP"}
EPS = 0.005


def _load(regime, downstream, tag):
    if downstream == "svc_rbf":
        p = f"{RAW}/paper2_phase2_{regime}_ks_max_{tag}/paper2_progressive_readaptation_by_seed.csv"
    else:
        p = f"{RAW}/paper2_phase2c_{regime}_{downstream}_ks_max_{tag}/paper2_progressive_readaptation_by_seed.csv"
    return pd.read_csv(p) if os.path.exists(p) else None


def main():
    os.makedirs(OUTT, exist_ok=True)
    os.makedirs(OUTF, exist_ok=True)
    rows = []
    for dm in DOWNSTREAM:
        for reg in REGIMES:
            none = _load(reg, dm, "none")
            lp = _load(reg, dm, "lp32")
            if none is None or lp is None:
                continue
            na = none[none.method == "no_adaptation"]["mean_balanced_accuracy"].mean()
            naive = none[none.method == "ks_max"]["mean_balanced_accuracy"].mean()
            gate = lp[lp.method == "ks_max"]["mean_balanced_accuracy"].mean()
            rows.append(dict(
                downstream=dm, regime=reg, n_seeds=len(none[none.method == "ks_max"]),
                noadapt_BA=round(na, 4), naive_BA=round(naive, 4), gate_BA=round(gate, 4),
                naive_gain=round((naive - na) * 100, 2), gate_gain=round((gate - na) * 100, 2),
                harm_reproduced=bool(naive < na - EPS),
                gate_avoids_harm=bool(gate >= na - EPS),
                gate_beats_naive=bool(gate >= naive - EPS),
            ))
    T = pd.DataFrame(rows)
    T.to_csv(f"{OUTT}/paper2_downstream_generalization.csv", index=False)

    # Figure: ToN-IoT (harm regime) — naive vs gate gain across downstream models
    ton = T[T.regime == "ton_scanning"]
    if len(ton):
        fig, ax = plt.subplots(figsize=(6, 3.6))
        x = np.arange(len(ton)); w = 0.38
        ax.bar(x - w / 2, ton["naive_gain"], w, label="naive", color="#adb5bd")
        ax.bar(x + w / 2, ton["gate_gain"], w, label="gate-32", color="#2a9d8f")
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xticks(x); ax.set_xticklabels([DLABEL[d] for d in ton["downstream"]], fontsize=9)
        ax.set_ylabel("Gain vs no-adaptation (BA pts)")
        ax.set_title("ToN-IoT (harm regime): does harmful adaptation depend on the downstream model?")
        ax.legend(fontsize=8)
        fig.savefig(f"{OUTF}/fig6_downstream_generalization.png", dpi=200, bbox_inches="tight")
        fig.savefig(f"{OUTF}/fig6_downstream_generalization.pdf", bbox_inches="tight")
        plt.close(fig)

    pd.set_option("display.width", 220, "display.max_columns", 20)
    print(T.to_string(index=False))
    print("\n--- Summary flags ---")
    print("harm reproduced (naive < no-adapt) by downstream x regime:")
    print(T.pivot(index="downstream", columns="regime", values="harm_reproduced").to_string())
    print("\ngate avoids harm (gate >= no-adapt) by downstream x regime:")
    print(T.pivot(index="downstream", columns="regime", values="gate_avoids_harm").to_string())
    print("\nwrote", OUTT, "and fig6_downstream_generalization")


if __name__ == "__main__":
    main()
