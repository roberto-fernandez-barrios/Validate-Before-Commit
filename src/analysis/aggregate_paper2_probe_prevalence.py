"""Phase 2j: probe prevalence — verdict against the pre-fixed criteria.

Reads the 9 Phase-2j run dirs (3 regimes x {p10_b32, p01_b32, p01_b320}, KS-max, SVC, 30 seeds)
plus the Phase-2 balanced baselines, and evaluates the criteria of
notes/paper2_phase2j_probe_prevalence_protocol_001.md:
  P1 (pi=0.10, b=32): ToN gain >= -0.5 AND PortScan gain >= full-replace naive (7.79) - 0.3.
  P2 (pi=0.01, b=32): same thresholds, reported either way.
  P3 (pi=0.01, b=320): if P2 fails ToN, does the 10x budget restore ToN >= -0.5?
  G: no arm significantly below no-adaptation (ci_hi >= 0) except a reported P2 boundary.
Outputs results/tables/paper2_phase2j_probe_prevalence_001/{summary,paired_ci,verdict}.csv.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_phase2j_probe_prevalence_001"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
ARMS = ["p10_b32", "p01_b32", "p01_b320"]
rng = np.random.default_rng(20260713)


def boot_ci(v, nb=5000):
    v = np.asarray(v); n = len(v)
    b = v[rng.integers(0, n, (nb, n))].mean(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def seeds_ba(path, method):
    f = f"{path}/paper2_progressive_readaptation_by_seed.csv"
    if not os.path.exists(f):
        return None
    d = pd.read_csv(f)
    s = d[d.method == method].set_index("seed")["mean_balanced_accuracy"]
    return s if len(s) else None


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, cis = [], []
    naive_gain = {}
    for reg in REGIMES:
        p = f"{RAW}/paper2_phase2_{reg}_ks_max_none"
        na, nv = seeds_ba(p, "no_adaptation"), seeds_ba(p, "ks_max")
        naive_gain[reg] = float((nv - na).mean() * 100)
        # balanced-probe reference (lp32, pi=0.5)
        pb = f"{RAW}/paper2_phase2_{reg}_ks_max_lp32"
        nab, gb = seeds_ba(pb, "no_adaptation"), seeds_ba(pb, "ks_max")
        rows.append(dict(regime=reg, arm="balanced_b32", gain_pts=round(float(((gb - nab) * 100).mean()), 3),
                         fullreplace_naive_gain=round(naive_gain[reg], 3)))

    for reg in REGIMES:
        for arm in ARMS:
            p = f"{RAW}/paper2_phase2j_{reg}_{arm}"
            na = seeds_ba(p, "no_adaptation")
            g = seeds_ba(p, "ks_max")
            if na is None or g is None:
                print(f"[skip] {reg} {arm}"); continue
            gains = (g - na) * 100
            rows.append(dict(regime=reg, arm=arm, gain_pts=round(float(gains.mean()), 3),
                             fullreplace_naive_gain=round(naive_gain[reg], 3)))
            lo, hi = boot_ci(gains.values)
            cis.append(dict(regime=reg, arm=arm, contrast="vs_noadapt",
                            diff=round(float(gains.mean()), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3)))

    R = pd.DataFrame(rows); C = pd.DataFrame(cis)
    g = lambda reg, arm: float(R[(R.regime == reg) & (R.arm == arm)]["gain_pts"].iloc[0])
    verdicts = []
    p1 = (g("ton_scanning", "p10_b32") >= -0.5) and (g("portscan", "p10_b32") >= naive_gain["portscan"] - 0.3)
    verdicts.append(dict(criterion="P1 pi=0.10 b=32 (ToN >= -0.5 AND PortScan >= naive-0.3)",
                         ton=g("ton_scanning", "p10_b32"), portscan=g("portscan", "p10_b32"), passed=bool(p1)))
    p2 = (g("ton_scanning", "p01_b32") >= -0.5) and (g("portscan", "p01_b32") >= naive_gain["portscan"] - 0.3)
    verdicts.append(dict(criterion="P2 pi=0.01 b=32 (same thresholds)",
                         ton=g("ton_scanning", "p01_b32"), portscan=g("portscan", "p01_b32"), passed=bool(p2)))
    p3 = g("ton_scanning", "p01_b320") >= -0.5
    verdicts.append(dict(criterion="P3 pi=0.01 b=320 recovery (ToN >= -0.5)",
                         ton=g("ton_scanning", "p01_b320"), portscan=g("portscan", "p01_b320"), passed=bool(p3)))
    for _, r in C.iterrows():
        verdicts.append(dict(criterion=f"G {r['regime']} {r['arm']} not sig. below no-adapt",
                             ton=None, portscan=None, passed=bool(r["ci_hi"] >= 0)))
    V = pd.DataFrame(verdicts)
    R.to_csv(f"{OUT}/summary.csv", index=False)
    C.to_csv(f"{OUT}/paired_ci.csv", index=False)
    V.to_csv(f"{OUT}/verdict.csv", index=False)
    print(R.pivot(index="regime", columns="arm", values="gain_pts").to_string()); print()
    print(C.to_string(index=False)); print()
    print(V.to_string(index=False))


if __name__ == "__main__":
    main()
