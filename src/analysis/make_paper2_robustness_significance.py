"""Paired bootstrap CIs for the gate's safety claims in the HARM regime (ToN-IoT) across robustness axes.

For each robustness condition (downstream model, label latency, probe poison) the gate lp32 is compared,
per seed, to naive triggering and to no-adaptation. Confirms the gate significantly avoids harm / beats
naive across conditions. No new experiments. Output: results/tables/paper2_robustness_significance_001/.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_robustness_significance_001"
rng = np.random.default_rng(20260704)


def ci(v, nb=5000):
    v = np.asarray(v); n = len(v)
    b = v[rng.integers(0, n, (nb, n))].mean(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def seedmap(path, method):
    d = pd.read_csv(path) if os.path.exists(path) else None
    if d is None:
        return None
    return d[d.method == method].set_index("seed")["mean_balanced_accuracy"]


def paired(gate_path, none_path):
    g = seedmap(gate_path, "ks_max")
    na = seedmap(none_path, "no_adaptation")
    nv = seedmap(none_path, "ks_max")
    if g is None or na is None or nv is None:
        return None
    idx = g.index.intersection(na.index)
    dvn = (g.loc[idx] - nv.loc[idx]).values * 100
    dna = (g.loc[idx] - na.loc[idx]).values * 100
    lo1, hi1 = ci(dvn); lo2, hi2 = ci(dna)
    return dict(n=len(idx),
                d_vs_naive=round(dvn.mean(), 2), naive_ci=f"[{lo1:+.2f},{hi1:+.2f}]", naive_sig=bool(lo1 > 0),
                d_vs_noadapt=round(dna.mean(), 2), noadapt_ci=f"[{lo2:+.2f},{hi2:+.2f}]", noadapt_sig=bool(lo2 > 0))


def main():
    os.makedirs(OUT, exist_ok=True)
    reg = "ton_scanning"
    rows = []
    # baseline (pre-registered lp32 vs phase2 none)
    r = paired(f"{RAW}/paper2_phase2_{reg}_ks_max_lp32/paper2_progressive_readaptation_by_seed.csv",
               f"{RAW}/paper2_phase2_{reg}_ks_max_none/paper2_progressive_readaptation_by_seed.csv")
    if r: rows.append(dict(axis="baseline", condition="lp32 (SVC)", **r))
    # downstream models (phase2c: none and lp32 per model)
    for dm in ["random_forest", "logreg", "mlp"]:
        r = paired(f"{RAW}/paper2_phase2c_{reg}_{dm}_ks_max_lp32/paper2_progressive_readaptation_by_seed.csv",
                   f"{RAW}/paper2_phase2c_{reg}_{dm}_ks_max_none/paper2_progressive_readaptation_by_seed.csv")
        if r: rows.append(dict(axis="downstream", condition=dm, **r))
    # label latency (phase2d gate vs phase2 none SVC)
    for lag in [5, 10, 20]:
        r = paired(f"{RAW}/paper2_phase2d_{reg}_lag{lag}/paper2_progressive_readaptation_by_seed.csv",
                   f"{RAW}/paper2_phase2_{reg}_ks_max_none/paper2_progressive_readaptation_by_seed.csv")
        if r: rows.append(dict(axis="latency", condition=f"lag{lag}", **r))
    # probe poison (phase2g gate vs phase2 none SVC)
    for p in [10, 20, 40]:
        r = paired(f"{RAW}/paper2_phase2g_{reg}_poison{p}/paper2_progressive_readaptation_by_seed.csv",
                   f"{RAW}/paper2_phase2_{reg}_ks_max_none/paper2_progressive_readaptation_by_seed.csv")
        if r: rows.append(dict(axis="poison", condition=f"{p}%", **r))
    T = pd.DataFrame(rows)
    T.to_csv(f"{OUT}/paper2_robustness_significance_ton.csv", index=False)
    pd.set_option("display.width", 200, "display.max_columns", 20)
    print("ToN-IoT harm regime — gate lp32 paired CI95 across robustness conditions:\n")
    print(T.to_string(index=False))
    print(f"\ngate significantly beats naive in {T.naive_sig.sum()}/{len(T)} conditions; "
          f"significantly beats no-adaptation in {T.noadapt_sig.sum()}/{len(T)}.")


if __name__ == "__main__":
    main()
