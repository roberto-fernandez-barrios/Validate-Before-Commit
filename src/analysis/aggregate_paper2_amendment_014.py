"""Amendment 014 aggregator:
  - true stratified anytime-valid gate (ebcs_strat): zero + full;
  - commit/reject/defer gate (ebcs_defer): full + mild, with labels/decision;
  - lifetime-alpha EB-CS (A=0.10, M=10): zero + full;
  - end-to-end lite (pi=0.05 stream, probe-prevalence 0.05, candidate+probe latency 5):
    naive vs lp32, with trigger counts;
  - redone symmetric A/B (disjoint, role-randomized) from symmetric_ab.csv.

Outputs results/tables/paper2_amendment_014/summary.csv
"""
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_014"
SEEDS = set(range(104, 134))
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]


def gain(dirname):
    p = f"{RAW}/{dirname}/paper2_progressive_readaptation_by_seed.csv"
    if not os.path.exists(p):
        return None
    d = pd.read_csv(p); d = d[d.seed.isin(SEEDS)]
    g = d[d.method == "ks_max"].set_index("seed")["mean_balanced_accuracy"]
    b = d[d.method == "no_adaptation"].set_index("seed")["mean_balanced_accuracy"]
    c = g.index.intersection(b.index)
    return ((g.loc[c] - b.loc[c]) * 100).sort_index() if len(c) else None


def boot_ci(x, n=10000, seed=0):
    rng = np.random.default_rng(seed); x = np.asarray(x, float)
    bs = rng.choice(x, size=(n, x.size), replace=True).mean(1)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def scol(dirname, col):
    p = f"{RAW}/{dirname}/paper2_progressive_readaptation_summary.csv"
    if not os.path.exists(p):
        return np.nan
    d = pd.read_csv(p); d = d[(d.seed.isin(SEEDS)) & (d.method == "ks_max")]
    return float(d[col].mean()) if col in d.columns and len(d) else np.nan


def summ(dirname, **extra):
    g = gain(dirname)
    if g is None:
        return None
    lo, hi = boot_ci(g.values)
    return dict(n=len(g), gain=round(float(g.mean()), 3), lo=round(lo, 3), hi=round(hi, 3), **extra)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for reg in REGIMES:
        for blk, tag, drift in [
            ("ebcs_strat", "rz_ebcsstrat", "zero"), ("ebcs_strat", "full_ebcsstrat", "full"),
            ("ebcs_defer", "full_ebcsdefer", "full"), ("ebcs_defer", "mild_ebcsdefer", "mild"),
            ("ebcs_lifetime", "rz_ebcslife", "zero"), ("ebcs_lifetime", "full_ebcslife", "full"),
        ]:
            d = f"paper2_v15_{reg}_{tag}"
            s = summ(d, commits=round(scol(d, "n_adaptations"), 3),
                     labels_probe=round(scol(d, "labels_probe"), 1))
            if s:
                rows.append(dict(block=blk, regime=reg, drift=drift, **s))
        for arm in ("none", "lp32"):
            d = f"paper2_v15_{reg}_e2e_{arm}"
            s = summ(d, triggers=round(scol(d, "n_triggers"), 2),
                     commits=round(scol(d, "n_adaptations"), 2))
            if s:
                rows.append(dict(block="e2e_lite", regime=reg, drift="full", arm=arm, **s))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/summary.csv", index=False)
    pd.set_option("display.width", 220, "display.max_columns", 30)
    for blk in ["ebcs_strat", "ebcs_defer", "ebcs_lifetime", "e2e_lite"]:
        sub = R[R.block == blk]
        if len(sub):
            print(f"\n== {blk} ==")
            print(sub.dropna(axis=1, how="all").to_string(index=False))
    ab = f"{OUT}/symmetric_ab.csv"
    if os.path.exists(ab):
        print("\n== symmetric_ab (disjoint, role-randomized) ==")
        print(pd.read_csv(ab).to_string(index=False))


if __name__ == "__main__":
    main()
