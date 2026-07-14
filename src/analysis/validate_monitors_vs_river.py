"""Unit cross-check of our DDM/ADWIN against river's reference implementations (amendment 004).

Deterministic synthetic Bernoulli error streams with a step change: error rate p0 for the first
half, p1 for the second. Our DDM consumes per-window error rates (m Bernoullis incorporated per
update); river's binary.DDM consumes individual outcomes. We feed BOTH the same underlying
outcome sequence and compare (a) whether each fires, (b) the detection delay in windows.
Output: results/tables/paper2_monitor_validation_004.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.experiments.run_paper2_readaptation_v2 import ADWIN, DDM

M_PER_WINDOW = 8      # matches --monitor-labels in the harness
N_WINDOWS = 100       # matches --post-windows
CHANGE_AT = 50


def run_case(p0: float, p1: float, seed: int) -> dict:
    from river import drift as river_drift
    rng = np.random.default_rng(seed)
    outcomes = np.concatenate([
        rng.random(CHANGE_AT * M_PER_WINDOW) < p0,
        rng.random((N_WINDOWS - CHANGE_AT) * M_PER_WINDOW) < p1]).astype(bool)

    ours_ddm, ours_adwin = DDM(), ADWIN(delta=0.002)
    riv_ddm, riv_adwin = river_drift.binary.DDM(), river_drift.ADWIN(delta=0.002)
    fire = dict(ours_ddm=None, river_ddm=None, ours_adwin=None, river_adwin=None)
    for t in range(N_WINDOWS):
        w = outcomes[t * M_PER_WINDOW:(t + 1) * M_PER_WINDOW]
        err_rate = float(w.mean())
        if fire["ours_ddm"] is None and ours_ddm.update(err_rate, M_PER_WINDOW):
            fire["ours_ddm"] = t
        if fire["ours_adwin"] is None and ours_adwin.update(err_rate):
            fire["ours_adwin"] = t
        for e in w:
            riv_ddm.update(bool(e))
            if fire["river_ddm"] is None and riv_ddm.drift_detected:
                fire["river_ddm"] = t
            riv_adwin.update(int(e))
            if fire["river_adwin"] is None and riv_adwin.drift_detected:
                fire["river_adwin"] = t
    return dict(p0=p0, p1=p1, seed=seed, **{k: (v if v is not None else -1) for k, v in fire.items()})


def main():
    rows = [run_case(p0, p1, seed)
            for (p0, p1) in [(0.05, 0.30), (0.05, 0.15), (0.10, 0.40), (0.05, 0.05), (0.20, 0.20)]
            for seed in range(20)]
    df = pd.DataFrame(rows)
    out = "results/tables/paper2_monitor_validation_004.csv"
    df.to_csv(out, index=False)

    def agree(a, b):
        return float(((df[a] >= 0) == (df[b] >= 0)).mean())
    print(df.groupby(["p0", "p1"]).agg(
        ours_ddm_fired=("ours_ddm", lambda s: float((s >= 0).mean())),
        river_ddm_fired=("river_ddm", lambda s: float((s >= 0).mean())),
        ours_ddm_delay=("ours_ddm", lambda s: float(s[s >= 0].mean()) if (s >= 0).any() else np.nan),
        river_ddm_delay=("river_ddm", lambda s: float(s[s >= 0].mean()) if (s >= 0).any() else np.nan),
        ours_adwin_fired=("ours_adwin", lambda s: float((s >= 0).mean())),
        river_adwin_fired=("river_adwin", lambda s: float((s >= 0).mean())),
    ).to_string())
    print(f"\nfire/no-fire agreement: DDM {agree('ours_ddm', 'river_ddm'):.2f}, "
          f"ADWIN {agree('ours_adwin', 'river_adwin'):.2f}")
    print(f"written: {out}")


if __name__ == "__main__":
    main()
