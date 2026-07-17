"""Amendment 013 aggregator:
  - causal FINAL (global dedup + reject + min-calib 30): gains, gate-vs-naive, collisions==0,
    no-probe commits -> the Table-8 replacement (full + mild);
  - stratified gate (zero + full drift): gains + commits;
  - strict-> baseline at mild + full drift (frontier completion);
  - calibration min-window sweep {8,16,30} stability;
  - symmetric-A/B mechanism table (read from symmetric_ab.csv).

Outputs results/tables/paper2_amendment_013/summary.csv
"""
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_013"
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


def summ(dirname, **extra):
    g = gain(dirname)
    if g is None:
        return None
    lo, hi = boot_ci(g.values)
    return dict(n=len(g), gain=round(float(g.mean()), 3), lo=round(lo, 3), hi=round(hi, 3), **extra)


def scol(dirname, col):
    p = f"{RAW}/{dirname}/paper2_progressive_readaptation_summary.csv"
    if not os.path.exists(p):
        return np.nan
    d = pd.read_csv(p); d = d[(d.seed.isin(SEEDS)) & (d.method == "ks_max")]
    return float(d[col].mean()) if col in d.columns and len(d) else np.nan


def paired(a, b):
    ga, gb = gain(a), gain(b)
    if ga is None or gb is None:
        return None
    c = ga.index.intersection(gb.index)
    d = (ga.loc[c] - gb.loc[c]); lo, hi = boot_ci(d.values)
    return round(float(d.mean()), 3), round(lo, 3), round(hi, 3)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for reg in REGIMES:
        # causal FINAL (Table 8)
        for drift, ntag, gtag in [("full", "fc_none", "fc_lp32"), ("mild", "mc_none", "mc_lp32")]:
            nd, gd = f"paper2_v14b_{reg}_{ntag}", f"paper2_v14b_{reg}_{gtag}"
            sn, sg = summ(nd), summ(gd)
            gvn = paired(gd, nd)
            if sn:
                rows.append(dict(block="causal_final", regime=reg, drift=drift, arm="naive",
                                 gain=sn["gain"], lo=sn["lo"], hi=sn["hi"],
                                 collisions=round(scol(nd, "cand_future_collisions"), 2)))
            if sg:
                rows.append(dict(block="causal_final", regime=reg, drift=drift, arm="gate",
                                 gain=sg["gain"], lo=sg["lo"], hi=sg["hi"],
                                 collisions=round(scol(gd, "cand_future_collisions"), 2),
                                 commit_no_probe=round(scol(gd, "n_commit_no_probe"), 3),
                                 gate_vs_naive=gvn[0] if gvn else np.nan,
                                 gvn_lo=gvn[1] if gvn else np.nan, gvn_hi=gvn[2] if gvn else np.nan))
        # stratified gate
        for drift, tag in [("zero", "rz_strat"), ("full", "full_strat")]:
            s = summ(f"paper2_v14_{reg}_{tag}", commits=round(scol(f"paper2_v14_{reg}_{tag}", "n_adaptations"), 3))
            if s:
                rows.append(dict(block="stratified", regime=reg, drift=drift, arm="strat", **s))
        # strict-> at mild + full
        for drift, tag in [("mild", "mild_strict"), ("full", "full_strict")]:
            s = summ(f"paper2_v14_{reg}_{tag}")
            if s:
                rows.append(dict(block="strict_baseline", regime=reg, drift=drift, arm="strict", **s))
        # calib min-window sweep (causal full gate-vs-naive)
        for cw, tag in [(30, "fc_lp32"), (16, "fc_lp32_cw16"), (8, "fc_lp32_cw8")]:
            gvn = paired(f"paper2_v14b_{reg}_{tag}", f"paper2_v14b_{reg}_fc_none")
            if gvn:
                rows.append(dict(block="calib_sweep", regime=reg, min_cw=cw, arm=tag,
                                 gate_vs_naive=gvn[0], gvn_lo=gvn[1], gvn_hi=gvn[2]))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/summary.csv", index=False)
    pd.set_option("display.width", 220, "display.max_columns", 30)
    for blk in ["causal_final", "stratified", "strict_baseline", "calib_sweep"]:
        sub = R[R.block == blk]
        if len(sub):
            print(f"\n== {blk} ==")
            print(sub.dropna(axis=1, how="all").to_string(index=False))
    ab = f"{OUT}/symmetric_ab.csv"
    if os.path.exists(ab):
        print("\n== symmetric_ab (mechanism) ==")
        print(pd.read_csv(ab).to_string(index=False))


if __name__ == "__main__":
    main()
