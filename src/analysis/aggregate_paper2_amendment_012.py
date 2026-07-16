"""Amendment 012 aggregator:
  - cn corrected (C ~ 1/n) vs buggy cn (C ~ n) and C=1 observed cumulative;
  - McNemar alpha=0.10 zero-drift (homogeneous with the CS gates) + commit counts;
  - causal reject-policy gate vs the commit-policy gate + no-probe commit counts;
  - size-matched (2000) RF/LogReg/MLP zero-drift vs the 512 default;
  - strict-> (reject-ties) baseline vs eps=0 and McNemar under zero drift.

Outputs results/tables/paper2_amendment_012/summary.csv
"""
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_012"
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
        # cn corrected vs buggy vs C=1
        s = summ(f"paper2_v13_{reg}_cum_cn_none")
        if s:
            rows.append(dict(block="cn_fix", regime=reg, arm="cn_corrected_1overN", **s))
        s = summ(f"paper2_v12_{reg}_cum_cn_none")
        if s:
            rows.append(dict(block="cn_fix", regime=reg, arm="cn_buggy_Nprop", **s))
        s = summ(f"paper2_v11_{reg}_rz_cumulative_none")
        if s:
            rows.append(dict(block="cn_fix", regime=reg, arm="C1_observed", **s))
        # McNemar alpha=0.10
        s = summ(f"paper2_v13_{reg}_rz_mcnemar_a10",
                 commits=round(scol(f"paper2_v13_{reg}_rz_mcnemar_a10", "n_adaptations"), 3))
        if s:
            rows.append(dict(block="mcnemar_a10", regime=reg, arm="mcnemar_a0.10", **s))
        # causal reject-policy
        for drift, gtag, ntag in [("full", "clean_full_lp32_reject", f"paper2_v12_{reg}_clean_full_none"),
                                  ("mild", "clean_mild_lp32_reject", f"paper2_v12_{reg}_clean_mild_none")]:
            gdir = f"paper2_v13_{reg}_{gtag}"
            s = summ(gdir,
                     no_probe=round(scol(gdir, "n_no_probe"), 3),
                     commit_no_probe=round(scol(gdir, "n_commit_no_probe"), 3))
            if s:
                c = paired(gdir, ntag)
                if c:
                    s.update(gate_vs_naive=c[0], gvn_lo=c[1], gvn_hi=c[2])
                rows.append(dict(block="causal_reject", regime=reg, drift=drift, arm=gtag, **s))
        # size-matched models (2000) vs 512
        for m in ("random_forest", "logreg", "mlp"):
            s2000 = summ(f"paper2_v13_{reg}_rz_{m}_sz2000_none")
            s512 = gain(f"paper2_v11_{reg}_rz_{m}_none")
            if s2000:
                s2000["gain_512"] = round(float(s512.mean()), 3) if s512 is not None else np.nan
                rows.append(dict(block="sizematch_models", regime=reg, arm=f"{m}_sz2000", **s2000))
        # strict-> baseline vs eps0 and mcnemar
        s = summ(f"paper2_v13_{reg}_rz_strict_none")
        if s:
            eps0 = gain(f"paper2_v9_{reg}_rand_s0_lp32")   # a007 eps=0 zero-drift gate (size 512)
            s["gain_eps0"] = round(float(eps0.mean()), 3) if eps0 is not None else np.nan
            rows.append(dict(block="strict_baseline", regime=reg, arm="strict_gt", **s))

    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/summary.csv", index=False)
    pd.set_option("display.width", 220, "display.max_columns", 30)
    for blk in ["cn_fix", "mcnemar_a10", "causal_reject", "sizematch_models", "strict_baseline"]:
        sub = R[R.block == blk]
        if len(sub):
            print(f"\n== {blk} ==")
            print(sub.dropna(axis=1, how="all").to_string(index=False))


if __name__ == "__main__":
    main()
