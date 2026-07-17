"""final-kbs aggregator: unified causal-64 matrix, VBC-SG + exact-strat, prevalence sweep,
and the 4-condition symmetric A/B. Outputs results/tables/paper2_final_kbs/summary.csv"""
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_final_kbs"
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
        # causal-64 unified matrix
        for drift in ("full", "mild"):
            nd = f"paper2_fk_{reg}_c64_{drift}_none"
            for arm in ("none", "lp32", "strict"):
                d = f"paper2_fk_{reg}_c64_{drift}_{arm}"
                s = summ(d, collisions=round(scol(d, "cand_future_collisions"), 2),
                         no_probe_commits=round(scol(d, "n_commit_no_probe"), 3))
                if s:
                    if arm != "none":
                        c = paired(d, nd)
                        if c:
                            s.update(vs_naive=c[0], vn_lo=c[1], vn_hi=c[2])
                    rows.append(dict(block="causal64", regime=reg, drift=drift, arm=arm, **s))
        # VBC-SG + exact-strat (core harness)
        for blk, tag, drift in [("vbc_sg", "rz_vbc", "zero"), ("vbc_sg", "full_vbc", "full"),
                                ("exact_strat", "rz_exs", "zero"), ("exact_strat", "full_exs", "full")]:
            d = f"paper2_fk_{reg}_{tag}"
            s = summ(d, commits=round(scol(d, "n_adaptations"), 3),
                     labels=round(scol(d, "labels_probe"), 1))
            if s:
                rows.append(dict(block=blk, regime=reg, drift=drift, **s))
        # prevalence sweep
        for pi, tag in [("0.01", "e2e01"), ("0.10", "e2e10")]:
            for arm in ("none", "lp32"):
                d = f"paper2_fk_{reg}_{tag}_{arm}"
                s = summ(d, triggers=round(scol(d, "n_triggers"), 2))
                if s:
                    rows.append(dict(block="prev_sweep", regime=reg, drift=f"pi{pi}", arm=arm, **s))
        for arm in ("none", "lp32"):
            d = f"paper2_fk_{reg}_e2e05lat20_{arm}"
            s = summ(d, triggers=round(scol(d, "n_triggers"), 2))
            if s:
                rows.append(dict(block="prev_sweep", regime=reg, drift="pi0.05lat20", arm=arm, **s))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/summary.csv", index=False)
    pd.set_option("display.width", 240, "display.max_columns", 30)
    for blk in ["causal64", "vbc_sg", "exact_strat", "prev_sweep"]:
        sub = R[R.block == blk]
        if len(sub):
            print(f"\n== {blk} ==")
            print(sub.dropna(axis=1, how="all").to_string(index=False))
    ab = f"{OUT}/symmetric_ab.csv"
    if os.path.exists(ab):
        d = pd.read_csv(ab)
        print("\n== symmetric_ab FINAL (rand contrast only) ==")
        print(d[d.contrast == "rand"].to_string(index=False))


if __name__ == "__main__":
    main()
