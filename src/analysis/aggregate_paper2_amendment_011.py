"""Amendment 011 aggregator:
  - causal leakage-free (stream-disjoint) vs leaky, full + mild: gains, gate-vs-naive, collisions;
  - cumulative controls (initial_plus_observed / dedup / cn) vs the a009 observed cumulative,
    with unique-sample fractions;
  - EB-CS budget sweep (64/128/256) at full drift;
  - per-stream harmful-commit rate + alpha-spending context (blocking #3).

Outputs results/tables/paper2_amendment_011/{summary.csv,contrasts.csv,harmful_commit.csv}.
"""
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_011"
SEEDS = set(range(104, 134))
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]


def by_seed_gain(dirname):
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


def summ(dirname):
    g = by_seed_gain(dirname)
    if g is None:
        return None
    lo, hi = boot_ci(g.values)
    return dict(n=len(g), gain=round(float(g.mean()), 3), lo=round(lo, 3), hi=round(hi, 3))


def paired(a, b):
    ga, gb = by_seed_gain(a), by_seed_gain(b)
    if ga is None or gb is None:
        return None
    c = ga.index.intersection(gb.index)
    d = (ga.loc[c] - gb.loc[c]); lo, hi = boot_ci(d.values)
    return round(float(d.mean()), 3), round(lo, 3), round(hi, 3), len(c)


def scol(dirname, col):
    p = f"{RAW}/{dirname}/paper2_progressive_readaptation_summary.csv"
    if not os.path.exists(p):
        return np.nan
    d = pd.read_csv(p); d = d[(d.seed.isin(SEEDS)) & (d.method == "ks_max")]
    return float(d[col].mean()) if col in d.columns and len(d) else np.nan


def harmful_commit(dirname, horizon="delta_future5"):
    """Per-stream commits, harmful commits (committed & future value < 0), and rates."""
    p = f"{RAW}/{dirname}/paper2_v2_trigger_log.csv"
    if not os.path.exists(p):
        return None
    d = pd.read_csv(p); d = d[d.seed.isin(SEEDS)]
    if "committed" not in d.columns:
        return None
    per = []
    for s, g in d.groupby("seed"):
        com = g[g.committed == True]
        harm = com[com[horizon] < 0]
        per.append((len(com), len(harm)))
    per = np.array(per, float)
    n_streams = len(per)
    return dict(streams=n_streams,
                commits_per_stream=round(per[:, 0].mean(), 3),
                harmful_per_stream=round(per[:, 1].mean(), 3),
                frac_streams_with_harm=round(float((per[:, 1] > 0).mean()), 3),
                harmful_frac_of_commits=round(float(per[:, 1].sum() / max(per[:, 0].sum(), 1)), 3))


def main():
    os.makedirs(OUT, exist_ok=True)
    srows, crows, hrows = [], [], []

    # --- 1. causal leakage-free vs leaky ---
    for reg in REGIMES:
        # full drift: clean (v12) vs leaky (v10 c8)
        clean = paired(f"paper2_v12_{reg}_clean_full_lp32", f"paper2_v12_{reg}_clean_full_none")
        leaky = paired(f"paper2_v10_{reg}_c8_gate", f"paper2_v10_{reg}_c8_none")
        col_clean = scol(f"paper2_v12_{reg}_clean_full_lp32", "cand_future_collisions")
        col_leaky = scol(f"paper2_v10_{reg}_c8_gate", "cand_future_collisions")
        if clean:
            crows.append(dict(block="causal", regime=reg, drift="full", which="clean",
                              gate_vs_naive=clean[0], lo=clean[1], hi=clean[2],
                              collisions=round(col_clean, 1)))
        if leaky:
            crows.append(dict(block="causal", regime=reg, drift="full", which="leaky",
                              gate_vs_naive=leaky[0], lo=leaky[1], hi=leaky[2],
                              collisions=round(col_leaky, 1)))
        # mild: clean vs leaky (both v12)
        cl = paired(f"paper2_v12_{reg}_clean_mild_lp32", f"paper2_v12_{reg}_clean_mild_none")
        lk = paired(f"paper2_v12_{reg}_leaky_mild_lp32", f"paper2_v12_{reg}_leaky_mild_none")
        if cl:
            crows.append(dict(block="causal", regime=reg, drift="mild", which="clean",
                              gate_vs_naive=cl[0], lo=cl[1], hi=cl[2],
                              collisions=round(scol(f"paper2_v12_{reg}_clean_mild_lp32", "cand_future_collisions"), 1)))
        if lk:
            crows.append(dict(block="causal", regime=reg, drift="mild", which="leaky",
                              gate_vs_naive=lk[0], lo=lk[1], hi=lk[2],
                              collisions=round(scol(f"paper2_v12_{reg}_leaky_mild_lp32", "cand_future_collisions"), 1)))
        for tag in ("clean_full_none", "clean_full_lp32", "clean_mild_none", "clean_mild_lp32"):
            s = summ(f"paper2_v12_{reg}_{tag}")
            if s:
                srows.append(dict(block="causal", regime=reg, arm=tag, **s))

    # --- 2. cumulative controls (zero drift, naive) ---
    for reg in REGIMES:
        for tag, obsdir in [("cum_observed", f"paper2_v11_{reg}_rz_cumulative_none"),
                            ("cum_initobs", f"paper2_v12_{reg}_cum_initobs_none"),
                            ("cum_dedup", f"paper2_v12_{reg}_cum_dedup_none"),
                            ("cum_cn", f"paper2_v12_{reg}_cum_cn_none")]:
            s = summ(obsdir)
            if s:
                tot = scol(obsdir, "cand_rows_total"); uni = scol(obsdir, "cand_unique_total")
                s["unique_frac"] = round(uni / tot, 3) if tot and tot == tot and tot > 0 else np.nan
                srows.append(dict(block="cumulative", regime=reg, arm=tag, **s))

    # --- 3. EB-CS budget sweep (full drift) ---
    for reg in REGIMES:
        for tag, d in [("ebcs64", f"paper2_v11_{reg}_full_ebcs64"),
                      ("ebcs128", f"paper2_v12_{reg}_ebcs128_full"),
                      ("ebcs256", f"paper2_v12_{reg}_ebcs256_full")]:
            s = summ(d)
            if s:
                s["labels_per_decision"] = round(scol(d, "seq_labels_mean"), 1)
                srows.append(dict(block="ebcs_budget", regime=reg, arm=tag, **s))

    # --- 4. per-stream harmful-commit rate (blocking #3) ---
    for reg in REGIMES:
        for tag, d in [("lp32_eps0", f"paper2_v2_{reg}_ks_lp32"),
                      ("mcnemar_zero", f"paper2_v11_{reg}_rz_mcnemar32" if os.path.exists(
                          f"{RAW}/paper2_v11_{reg}_rz_mcnemar32") else f"paper2_v10_{reg}_rz_mcnemar32"),
                      ("ebcs_full", f"paper2_v11_{reg}_full_ebcs64")]:
            h = harmful_commit(d)
            if h:
                hrows.append(dict(regime=reg, gate=tag, **h))

    S = pd.DataFrame(srows); C = pd.DataFrame(crows); H = pd.DataFrame(hrows)
    S.to_csv(f"{OUT}/summary.csv", index=False)
    C.to_csv(f"{OUT}/contrasts.csv", index=False)
    H.to_csv(f"{OUT}/harmful_commit.csv", index=False)
    pd.set_option("display.width", 200)
    print("== CAUSAL leakage-free vs leaky (gate-vs-naive; collisions) ==")
    print(C[C.block == "causal"].to_string(index=False))
    print("\n== CUMULATIVE controls (zero-drift naive gain; unique_frac) ==")
    print(S[S.block == "cumulative"].to_string(index=False))
    print("\n== EB-CS budget sweep (full drift) ==")
    print(S[S.block == "ebcs_budget"].to_string(index=False))
    print("\n== HARMFUL-COMMIT rate per stream ==")
    print(H.to_string(index=False))


if __name__ == "__main__":
    main()
