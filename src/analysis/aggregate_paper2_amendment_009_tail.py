"""Amendment 009 — Tier 0: tail / worst-case metrics (item 8).

Pure re-aggregation of per-window BA already logged in window_results.csv for the
committed v2 arms (no new runs). For each seed we compute, over the 100 post-drift
windows, the worst-window BA, the 10th-percentile BA, and CVaR@10% (mean of the
worst 10% of windows). We then form the paired per-seed gap vs no-adaptation and
report the mean gap with a bootstrap CI, at the mean, p10, worst, and CVaR levels.

The point: harm may hide in the tail. If naive triggering's worst-window/p10 gap vs
no-adaptation is more negative than its mean gap in the harm regime, harm concentrates
in the tail; a good gate should keep the tail tracking no-adaptation.

Outputs results/tables/paper2_amendment_009/tail.csv
"""
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_009"
SEEDS = set(range(104, 134))

# (regime, human label, naive dir, gate dir) — the confirmatory v2 harm/benefit/marginal arms.
ARMS = [
    ("portscan", "PortScan (benefit)", "paper2_v2_portscan_ks_none", "paper2_v2_portscan_ks_lp32"),
    ("unsw_recon", "UNSW Recon (marginal)", "paper2_v2_unsw_recon_ks_none", "paper2_v2_unsw_recon_ks_lp32"),
    ("ton_scanning", "ToN Scanning (harm)", "paper2_v2_ton_scanning_ks_none", "paper2_v2_ton_scanning_ks_lp32"),
]


def load_windows(d):
    p = f"{RAW}/{d}/paper2_progressive_readaptation_window_results.csv"
    if not os.path.exists(p):
        return None
    return pd.read_csv(p)


def per_seed_tail(df, method):
    """Return {seed: dict of tail stats} for one method's per-window BA."""
    d = df[(df.method == method) & (df.seed.isin(SEEDS))]
    out = {}
    for s, g in d.groupby("seed"):
        ba = g.sort_values("window_idx")["balanced_accuracy"].to_numpy()
        if ba.size == 0:
            continue
        k = max(1, int(round(0.10 * ba.size)))
        worst = np.sort(ba)[:k]
        out[s] = dict(
            mean=float(ba.mean()),
            p10=float(np.percentile(ba, 10)),
            worst=float(ba.min()),
            cvar10=float(worst.mean()),
        )
    return out


def boot_ci(x, n=10000, seed=0):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    bs = rng.choice(x, size=(n, x.size), replace=True).mean(1)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def paired_gap(arm_stats, base_stats, level):
    seeds = sorted(set(arm_stats) & set(base_stats))
    if not seeds:
        return None
    diff = np.array([(arm_stats[s][level] - base_stats[s][level]) * 100 for s in seeds])
    lo, hi = boot_ci(diff)
    return round(float(diff.mean()), 3), round(lo, 3), round(hi, 3), len(seeds)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for reg, label, naive_dir, gate_dir in ARMS:
        dn, dg = load_windows(naive_dir), load_windows(gate_dir)
        if dn is None or dg is None:
            print(f"[skip] {reg}: missing {naive_dir if dn is None else gate_dir}")
            continue
        base = per_seed_tail(dn, "no_adaptation")
        naive = per_seed_tail(dn, "ks_max")
        gate = per_seed_tail(dg, "ks_max")
        for level in ("mean", "p10", "worst", "cvar10"):
            gn = paired_gap(naive, base, level)
            gg = paired_gap(gate, base, level)
            if gn is None or gg is None:
                continue
            rows.append(dict(regime=reg, label=label, level=level,
                             naive_gap=gn[0], naive_lo=gn[1], naive_hi=gn[2],
                             gate_gap=gg[0], gate_lo=gg[1], gate_hi=gg[2], n=gn[3]))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/tail.csv", index=False)
    print("== amendment 009 Tier 0: tail metrics (gap vs no-adaptation, BA points) ==")
    print(R.to_string(index=False))


if __name__ == "__main__":
    main()
