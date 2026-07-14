"""Aggregate the amendment-005 runs: split-probe two-stage gate (delta sensitivity),
river monitor budget sweep, stratified temporal probes, and the UNSW chronological stream.

Contrasts vs naive/lp32 use the common-stream property (same-seed arms are truly paired);
temporal stratified arms pair against the amendment-004 arms on the same seeds.
Outputs results/tables/paper2_amendment_005/*.csv
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_005"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
SEEDS = set(range(104, 134))
rng = np.random.default_rng(20260714)


def boot_ci(v, nb=5000):
    v = np.asarray(v); n = len(v)
    b = v[rng.integers(0, n, (nb, n))].mean(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def by_seed(dirs, method, col="mean_balanced_accuracy", seeds=SEEDS):
    parts = [pd.read_csv(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")
             for d in dirs if os.path.exists(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")]
    if not parts:
        return None
    d = pd.concat(parts)
    d = d[(d.method == method) & (d.seed.isin(seeds))]
    return d.set_index("seed")[col].sort_index() if len(d) else None


def means(dirs, method, cols, seeds=SEEDS):
    parts = [pd.read_csv(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")
             for d in dirs if os.path.exists(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")]
    d = pd.concat(parts)
    d = d[(d.method == method) & (d.seed.isin(seeds))]
    return {c: float(d[c].mean()) for c in cols if c in d.columns}


def main():
    os.makedirs(OUT, exist_ok=True)
    naive = {r: by_seed([f"paper2_v2_{r}_ks_none", f"paper2_v2_{r}_ks_none_top"], "ks_max") for r in REGIMES}
    base = {r: by_seed([f"paper2_v2_{r}_ks_none", f"paper2_v2_{r}_ks_none_top"], "no_adaptation") for r in REGIMES}
    lp32 = {r: by_seed([f"paper2_v2_{r}_ks_lp32", f"paper2_v2_{r}_ks_lp32_top"], "ks_max") for r in REGIMES}

    arms = ["twostage_d03", "twostage_d05", "twostage_d10",
            "ddmriver_m32", "ddmriver_m80", "adwinriver_m32", "adwinriver_m80"]
    rows = []
    for reg in REGIMES:
        for arm in arms:
            d = [f"paper2_v7_{reg}_{arm}"]
            g, b = by_seed(d, "ks_max"), by_seed(d, "no_adaptation")
            if g is None or b is None:
                print(f"[skip] {reg} {arm}"); continue
            gain = (g - b) * 100
            lo, hi = boot_ci(gain.values)
            vs_n = gain - (naive[reg] - base[reg]) * 100
            nlo, nhi = boot_ci(vs_n.values)
            vs_l = gain - (lp32[reg] - base[reg]) * 100
            llo, lhi = boot_ci(vs_l.values)
            extra = means(d, "ks_max", ["n_triggers", "n_adaptations", "n_candidates_trained",
                                        "n_train_skipped", "labels_probe", "labels_monitor",
                                        "labels_candidate"])
            rows.append(dict(regime=reg, arm=arm, n=len(gain),
                             gain=round(float(gain.mean()), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                             vs_naive=round(float(vs_n.mean()), 3), vsn_lo=round(nlo, 3), vsn_hi=round(nhi, 3),
                             vs_lp32=round(float(vs_l.mean()), 3), vsl_lo=round(llo, 3), vsl_hi=round(lhi, 3),
                             **{k: round(v, 2) for k, v in extra.items()}))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/twostage_and_monitors.csv", index=False)
    print("== two-stage (split probe) + monitor budget sweep ==")
    print(R.to_string(index=False)); print()

    # --- stratified temporal probes (paired vs amendment-004 arms, same seeds) ---
    t_rows = []
    tseeds = dict(fri=set(range(165, 195)), wed=set(range(196, 226)), thu=set(range(227, 257)),
                  unsw=set(range(301, 331)))
    for stream in ["fri", "wed", "thu", "unsw"]:
        S = tseeds[stream]
        pref = "paper2_v6_temporal" if stream != "unsw" else "paper2_v7_temporal"
        arms_t = {"naive": f"{pref}_{stream}_none",
                  "gate": f"{pref}_{stream}_labeled_probe",
                  "strat": (f"paper2_v7_temporal_{stream}_strat" if stream != "unsw"
                            else f"paper2_v7_temporal_{stream}_labeled_probe_strat")}
        for col, mname in [("mean_balanced_accuracy", "BA_two_class"), ("mean_accuracy", "accuracy_all")]:
            series = {}
            for k, dname in arms_t.items():
                series[k] = by_seed([dname], "ks_max", col=col, seeds=S)
                series[k + "_base"] = by_seed([dname], "no_adaptation", col=col, seeds=S)
            if any(v is None for v in series.values()):
                print(f"[skip temporal] {stream} {mname}"); continue
            basev = series["naive_base"]
            for name, v in [("naive_vs_noadapt", (series["naive"] - basev) * 100),
                            ("gate_vs_noadapt", (series["gate"] - basev) * 100),
                            ("strat_vs_noadapt", (series["strat"] - basev) * 100),
                            ("gate_vs_naive", (series["gate"] - series["naive"]) * 100),
                            ("strat_vs_naive", (series["strat"] - series["naive"]) * 100),
                            ("strat_vs_gate", (series["strat"] - series["gate"]) * 100),
                            ("no_adapt_level", basev * 100)]:
                vals = v.dropna()
                lo, hi = boot_ci(vals.values)
                t_rows.append(dict(stream=stream, metric=mname, quantity=name,
                                   value=round(float(vals.mean()), 3),
                                   ci_lo=round(lo, 3), ci_hi=round(hi, 3), n=len(vals)))
    T = pd.DataFrame(t_rows)
    T.to_csv(f"{OUT}/temporal_stratified.csv", index=False)
    print("== temporal: stratified probe + UNSW chronological ==")
    print(T.to_string(index=False))


if __name__ == "__main__":
    main()
