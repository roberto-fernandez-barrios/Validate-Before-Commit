"""Amendment 009 aggregator: 4-classifier + no-PCA mild/zero drift, zero-drift alternative
update generators (ensemble_cal / sliding / cumulative / replay), the confidence-sequence
gate, and the CICIDS Tuesday chronological stream.

Every number is a paired per-seed gain vs no-adaptation (ks_max - no_adaptation), *100 BA
points, with a 95% bootstrap CI. Gate-vs-naive contrasts are paired differences of gains.

Outputs results/tables/paper2_amendment_009/{summary.csv,contrasts.csv}
"""
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_009"
SEEDS = set(range(104, 134))
CHRONO_SEEDS = set(range(401, 431))
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]


def by_seed_gain(dirname, seeds=SEEDS):
    """Per-seed (ks_max - no_adaptation)*100 gain array for one arm dir; None if missing."""
    p = f"{RAW}/{dirname}/paper2_progressive_readaptation_by_seed.csv"
    if not os.path.exists(p):
        return None
    d = pd.read_csv(p)
    d = d[d.seed.isin(seeds)]
    g = d[d.method == "ks_max"].set_index("seed")["mean_balanced_accuracy"]
    b = d[d.method == "no_adaptation"].set_index("seed")["mean_balanced_accuracy"]
    common = g.index.intersection(b.index)
    if len(common) == 0:
        return None
    return ((g.loc[common] - b.loc[common]) * 100).sort_index()


def means_col(dirname, col, seeds=SEEDS):
    p = f"{RAW}/{dirname}/paper2_progressive_readaptation_summary.csv"
    if not os.path.exists(p):
        p = f"{RAW}/{dirname}/paper2_progressive_readaptation_by_seed.csv"
    d = pd.read_csv(p)
    d = d[(d.seed.isin(seeds)) & (d.method == "ks_max")]
    return float(d[col].mean()) if col in d.columns and len(d) else np.nan


def boot_ci(x, n=10000, seed=0):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    bs = rng.choice(x, size=(n, x.size), replace=True).mean(1)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def summarize(dirname, seeds=SEEDS):
    g = by_seed_gain(dirname, seeds)
    if g is None:
        return None
    lo, hi = boot_ci(g.values)
    return dict(n=len(g), gain=round(float(g.mean()), 3), lo=round(lo, 3), hi=round(hi, 3))


def paired(gate_dir, naive_dir, seeds=SEEDS):
    a, b = by_seed_gain(gate_dir, seeds), by_seed_gain(naive_dir, seeds)
    if a is None or b is None:
        return None
    common = a.index.intersection(b.index)
    d = (a.loc[common] - b.loc[common])
    lo, hi = boot_ci(d.values)
    return round(float(d.mean()), 3), round(lo, 3), round(hi, 3), len(common)


def main():
    os.makedirs(OUT, exist_ok=True)

    # --- families: (family, drift-prefix, naive-suffix, gate-suffix) ---
    MODELS = [("random_forest", "RF"), ("logreg", "LogReg"), ("mlp", "MLP"),
              ("fulldim", "SVC-fulldim")]
    GENERATORS = [("ensemble_cal", "ensemble-cal"), ("sliding_window", "sliding"),
                  ("cumulative", "cumulative"), ("replay", "replay")]

    srows, crows = [], []

    # Item 1 & 2: 4 classifiers (+ no-PCA) under mild and zero drift.
    for reg in REGIMES:
        for key, label in MODELS:
            for drift, naive, gate, gname in [
                ("mild", f"paper2_v11_{reg}_mild_{key}_none", f"paper2_v11_{reg}_mild_{key}_lp32", "lp32"),
                ("zero", f"paper2_v11_{reg}_rz_{key}_none", f"paper2_v11_{reg}_rz_{key}_mcnemar32", "mcnemar"),
            ]:
                sn, sg = summarize(naive), summarize(gate)
                if sn:
                    srows.append(dict(block="models", regime=reg, family=label, drift=drift,
                                      arm="naive", **sn))
                if sg:
                    srows.append(dict(block="models", regime=reg, family=label, drift=drift,
                                      arm=gname, **sg))
                c = paired(gate, naive)
                if c:
                    crows.append(dict(block="models", regime=reg, family=label, drift=drift,
                                      contrast=f"{gname}_vs_naive", diff=c[0], lo=c[1], hi=c[2], n=c[3]))

    # Item 3 & 4: zero-drift alternative update generators (+ mild for cumulative/replay).
    for reg in REGIMES:
        for key, label in GENERATORS:
            sn, sg = summarize(f"paper2_v11_{reg}_rz_{key}_none"), summarize(f"paper2_v11_{reg}_rz_{key}_mcnemar32")
            if sn:
                srows.append(dict(block="generators", regime=reg, family=label, drift="zero", arm="naive", **sn))
            if sg:
                srows.append(dict(block="generators", regime=reg, family=label, drift="zero", arm="mcnemar", **sg))
            c = paired(f"paper2_v11_{reg}_rz_{key}_mcnemar32", f"paper2_v11_{reg}_rz_{key}_none")
            if c:
                crows.append(dict(block="generators", regime=reg, family=label, drift="zero",
                                  contrast="mcnemar_vs_naive", diff=c[0], lo=c[1], hi=c[2], n=c[3]))
            # mild for cumulative/replay
            if key in ("cumulative", "replay"):
                smn, smg = summarize(f"paper2_v11_{reg}_mild_{key}_none"), summarize(f"paper2_v11_{reg}_mild_{key}_lp32")
                if smn:
                    srows.append(dict(block="generators", regime=reg, family=label, drift="mild", arm="naive", **smn))
                if smg:
                    srows.append(dict(block="generators", regime=reg, family=label, drift="mild", arm="lp32", **smg))

    # Item 6: confidence-sequence gate (labels/decision reported).
    for reg in REGIMES:
        for drift, tag in [("zero", "rz_cs64"), ("mild", "mild_cs64")]:
            s = summarize(f"paper2_v11_{reg}_{tag}")
            if s:
                lab = means_col(f"paper2_v11_{reg}_{tag}", "seq_labels_mean")
                s["labels_per_decision"] = round(lab, 1) if lab == lab else np.nan
                srows.append(dict(block="cs_gate", regime=reg, family="CS", drift=drift, arm="cs64", **s))

    # Item 7: CICIDS Tuesday chronological (healthy-incumbent attempt).
    sn = summarize("paper2_v11_tue_chrono_none", CHRONO_SEEDS)
    sg = summarize("paper2_v11_tue_chrono_lp32", CHRONO_SEEDS)
    # also report no-adapt absolute level (incumbent health)
    def noadapt_level(dirname, seeds):
        d = pd.read_csv(f"{RAW}/{dirname}/paper2_progressive_readaptation_by_seed.csv")
        d = d[(d.seed.isin(seeds)) & (d.method == "no_adaptation")]
        return round(float(d["mean_balanced_accuracy"].mean()) * 100, 2)
    if sn:
        sn["noadapt_ba"] = noadapt_level("paper2_v11_tue_chrono_none", CHRONO_SEEDS)
        srows.append(dict(block="chrono", regime="cicids_tuesday", family="temporal", drift="chrono",
                          arm="naive", **sn))
    if sg:
        srows.append(dict(block="chrono", regime="cicids_tuesday", family="temporal", drift="chrono",
                          arm="lp32", **sg))
    c = paired("paper2_v11_tue_chrono_lp32", "paper2_v11_tue_chrono_none", CHRONO_SEEDS)
    if c:
        crows.append(dict(block="chrono", regime="cicids_tuesday", family="temporal", drift="chrono",
                          contrast="gate_premium(lp32-naive)", diff=c[0], lo=c[1], hi=c[2], n=c[3]))

    S = pd.DataFrame(srows)
    C = pd.DataFrame(crows)
    S.to_csv(f"{OUT}/summary.csv", index=False)
    C.to_csv(f"{OUT}/contrasts.csv", index=False)
    pd.set_option("display.width", 200, "display.max_rows", 300)
    print("== SUMMARY (gain vs no-adaptation, BA points, 95% boot CI) ==")
    print(S.to_string(index=False))
    print("\n== CONTRASTS (paired gate-vs-naive difference of gains) ==")
    print(C.to_string(index=False))


if __name__ == "__main__":
    main()
