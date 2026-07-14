"""Aggregate the amendment-007 runs (v9): the genuinely causal arm (observed recalibration +
row-identity-disjoint probes), the zero-drift and random-trigger controls, mild drift under the
full causal pipeline, and the sequential probe gate.

Outputs results/tables/paper2_amendment_007/*.csv
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_007"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
SEEDS = set(range(104, 134))
rng = np.random.default_rng(20260715)


def boot_ci(v, nb=5000):
    v = np.asarray(v); n = len(v)
    b = v[rng.integers(0, n, (nb, n))].mean(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def by_seed(dirs, method, col="mean_balanced_accuracy"):
    parts = [pd.read_csv(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")
             for d in dirs if os.path.exists(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")]
    if not parts:
        return None
    d = pd.concat(parts)
    d = d[(d.method == method) & (d.seed.isin(SEEDS))]
    return d.set_index("seed")[col].sort_index() if len(d) else None


def means(dirs, cols):
    parts = [pd.read_csv(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")
             for d in dirs if os.path.exists(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")]
    if not parts:
        return {}
    d = pd.concat(parts)
    d = d[(d.method == "ks_max") & (d.seed.isin(SEEDS))]
    return {c: float(d[c].mean()) for c in cols if c in d.columns}


def main():
    os.makedirs(OUT, exist_ok=True)
    arms = ["tcausal_none", "tcausal_gate", "tcausal_s025_none", "tcausal_s025_gate",
            "sev0_none", "sev0_lp32", "rand_s0_none", "rand_s0_lp32",
            "rand_s025_none", "rand_s025_lp32", "seq64"]
    rows = []
    for reg in REGIMES:
        for arm in arms:
            d = [f"paper2_v9_{reg}_{arm}"]
            g, b = by_seed(d, "ks_max"), by_seed(d, "no_adaptation")
            if g is None or b is None:
                print(f"[skip] {reg} {arm}"); continue
            gain = (g - b) * 100
            lo, hi = boot_ci(gain.values)
            m = means(d, ["n_triggers", "n_adaptations", "n_probes", "probe_row_collisions",
                          "seq_labels_mean", "labels_probe"])
            rows.append(dict(regime=reg, arm=arm, n=len(gain),
                             gain=round(float(gain.mean()), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                             **{k: round(v, 2) for k, v in m.items() if np.isfinite(v)}))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/summary.csv", index=False)
    print("== amendment 007 summary =="); print(R.to_string(index=False)); print()

    crows = []
    for reg in REGIMES:
        lp32 = [f"paper2_v2_{reg}_ks_lp32", f"paper2_v2_{reg}_ks_lp32_top"]
        for lbl, a, b in [
            ("tcausal_gate_vs_naive", [f"paper2_v9_{reg}_tcausal_gate"], [f"paper2_v9_{reg}_tcausal_none"]),
            ("tcausal_gate_vs_lp32(oracle)", [f"paper2_v9_{reg}_tcausal_gate"], lp32),
            ("tcausal_s025_gate_vs_naive", [f"paper2_v9_{reg}_tcausal_s025_gate"], [f"paper2_v9_{reg}_tcausal_s025_none"]),
            ("sev0_gate_vs_naive", [f"paper2_v9_{reg}_sev0_lp32"], [f"paper2_v9_{reg}_sev0_none"]),
            ("rand_s0_gate_vs_naive", [f"paper2_v9_{reg}_rand_s0_lp32"], [f"paper2_v9_{reg}_rand_s0_none"]),
            ("rand_s025_gate_vs_naive", [f"paper2_v9_{reg}_rand_s025_lp32"], [f"paper2_v9_{reg}_rand_s025_none"]),
            ("seq64_vs_lp32", [f"paper2_v9_{reg}_seq64"], lp32),
        ]:
            ga, ba = by_seed(a, "ks_max"), by_seed(a, "no_adaptation")
            gb, bb = by_seed(b, "ks_max"), by_seed(b, "no_adaptation")
            if any(x is None for x in (ga, ba, gb, bb)):
                continue
            d = ((ga - ba) - (gb - bb)) * 100
            lo, hi = boot_ci(d.values)
            crows.append(dict(regime=reg, contrast=lbl, diff=round(float(d.mean()), 3),
                              ci_lo=round(lo, 3), ci_hi=round(hi, 3)))
    C = pd.DataFrame(crows)
    C.to_csv(f"{OUT}/paired_ci.csv", index=False)
    print("== paired contrasts =="); print(C.to_string(index=False))


if __name__ == "__main__":
    main()
