"""Aggregate the amendment-008 runs (v10): size-matched zero-drift control, detector-triggered
zero-drift arms, risk-averse gates under zero drift, the anytime-valid sequential gate, and the
candidate/future-evaluation leakage audit.

Outputs results/tables/paper2_amendment_008/*.csv
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_008"
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


def paired(a, b):
    ga, ba = by_seed(a, "ks_max"), by_seed(a, "no_adaptation")
    gb, bb = by_seed(b, "ks_max"), by_seed(b, "no_adaptation")
    if any(x is None for x in (ga, ba, gb, bb)):
        return None
    d = ((ga - ba) - (gb - bb)) * 100
    lo, hi = boot_ci(d.values)
    return round(float(d.mean()), 3), round(lo, 3), round(hi, 3)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    v10 = ["rz_none_sz2000", "rz_lp32_sz2000", "rz_lcb64", "rz_mcnemar32", "rz_seqav64",
           "seqav64", "c8_none", "c8_gate"]
    v9 = {"rand_s0_none": "paper2_v9_{r}_rand_s0_none", "rand_s0_lp32": "paper2_v9_{r}_rand_s0_lp32",
          "sev0_none": "paper2_v9_{r}_sev0_none", "sev0_lp32": "paper2_v9_{r}_sev0_lp32"}
    for reg in REGIMES:
        for arm in v10:
            d = [f"paper2_v10_{reg}_{arm}"]
            g, b = by_seed(d, "ks_max"), by_seed(d, "no_adaptation")
            if g is None or b is None:
                print(f"[skip] {reg} {arm}"); continue
            gain = (g - b) * 100
            lo, hi = boot_ci(gain.values)
            m = means(d, ["n_triggers", "n_adaptations", "cand_future_collisions",
                          "probe_row_collisions", "seq_labels_mean", "labels_probe"])
            rows.append(dict(regime=reg, arm=arm, n=len(gain), gain=round(float(gain.mean()), 3),
                             ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                             **{k: round(v, 2) for k, v in m.items()}))
        for arm, tpl in v9.items():
            d = [tpl.format(r=reg)]
            g, b = by_seed(d, "ks_max"), by_seed(d, "no_adaptation")
            if g is None or b is None:
                continue
            gain = (g - b) * 100
            lo, hi = boot_ci(gain.values)
            m = means(d, ["n_triggers", "n_adaptations"])
            rows.append(dict(regime=reg, arm=arm, n=len(gain), gain=round(float(gain.mean()), 3),
                             ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                             **{k: round(v, 2) for k, v in m.items()}))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/summary.csv", index=False)
    print("== amendment 008 summary =="); print(R.to_string(index=False)); print()

    crows = []
    for reg in REGIMES:
        for lbl, a, b in [
            ("sz2000_gate_vs_naive", [f"paper2_v10_{reg}_rz_lp32_sz2000"], [f"paper2_v10_{reg}_rz_none_sz2000"]),
            ("sz2000_naive_vs_512naive", [f"paper2_v10_{reg}_rz_none_sz2000"], [f"paper2_v9_{reg}_rand_s0_none"]),
            ("rz_lcb_vs_naive", [f"paper2_v10_{reg}_rz_lcb64"], [f"paper2_v9_{reg}_rand_s0_none"]),
            ("rz_mcnemar_vs_naive", [f"paper2_v10_{reg}_rz_mcnemar32"], [f"paper2_v9_{reg}_rand_s0_none"]),
            ("rz_seqav_vs_naive", [f"paper2_v10_{reg}_rz_seqav64"], [f"paper2_v9_{reg}_rand_s0_none"]),
            ("seqav_vs_lp32", [f"paper2_v10_{reg}_seqav64"],
             [f"paper2_v2_{reg}_ks_lp32", f"paper2_v2_{reg}_ks_lp32_top"]),
            ("c8_gate_vs_naive", [f"paper2_v10_{reg}_c8_gate"], [f"paper2_v10_{reg}_c8_none"]),
        ]:
            r = paired(a, b)
            if r:
                crows.append(dict(regime=reg, contrast=lbl, diff=r[0], ci_lo=r[1], ci_hi=r[2]))
    C = pd.DataFrame(crows)
    C.to_csv(f"{OUT}/paired_ci.csv", index=False)
    print("== paired contrasts =="); print(C.to_string(index=False))


if __name__ == "__main__":
    main()
