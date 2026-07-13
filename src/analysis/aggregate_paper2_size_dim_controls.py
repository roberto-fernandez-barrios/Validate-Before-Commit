"""Phase 2k: candidate-size and dimensionality controls — is the harm a size or PCA artifact?

Arms (KS-max, SVC-RBF, 30 seeds, Phase-2 settings):
  cand2000_{none,lp32} x 3 regimes  — candidate trained on 2000/class, the SAME size as the
                                      initial model (kills the "4x smaller candidate" confound);
  fulldim_none x {ton_scanning, portscan} — full feature dimensionality (PCA disabled).
Outputs results/tables/paper2_phase2k_size_dim_controls_001/summary.csv.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_phase2k_size_dim_controls_001"
rng = np.random.default_rng(20260714)


def gains(path):
    d = pd.read_csv(f"{RAW}/{path}/paper2_progressive_readaptation_by_seed.csv")
    ba = d.set_index(["seed", "method"])["mean_balanced_accuracy"].unstack("method")
    g = (ba["ks_max"] - ba["no_adaptation"]) * 100
    b = g.values
    bs = b[rng.integers(0, len(b), (5000, len(b)))].mean(1)
    return float(g.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for reg in ["ton_scanning", "portscan", "unsw_recon"]:
        for arm in ["none", "lp32"]:
            m, lo, hi = gains(f"paper2_phase2k_{reg}_cand2000_{arm}")
            rows.append(dict(control="cand2000", regime=reg, arm=arm,
                             gain_pts=round(m, 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3)))
    for reg in ["ton_scanning", "portscan"]:
        m, lo, hi = gains(f"paper2_phase2k_{reg}_fulldim_none")
        rows.append(dict(control="fulldim", regime=reg, arm="none",
                         gain_pts=round(m, 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3)))
    S = pd.DataFrame(rows)
    S.to_csv(f"{OUT}/summary.csv", index=False)
    print(S.to_string(index=False))


if __name__ == "__main__":
    main()
