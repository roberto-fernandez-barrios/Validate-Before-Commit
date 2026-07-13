"""Harness-v2 registered replication: verdict against the LOCKED protocol.

Criteria constants transcribe notes/paper2_harness_v2_registered_replication_protocol_001.md
(tag `harness-v2-protocol`). Contrasts are truly paired: all arms share bit-identical streams.
  B (decisive): ToN lp32 gain vs no-adapt >= -0.5 AND lp32 - naive paired CI95 > 0 (KS-max).
  A: PortScan lp32 gain >= naive gain - 0.3 (KS-max).
  C: UNSW lp32 gain >= naive gain - 0.3 (KS-max).
  I: B and A signs replicate for QK-ZZ.
Exploratory (pre-declared): holdout-vs-lp32 equivalence (|diff| <= 0.3 everywhere), LCB
operating point, per-trigger mechanism (delta_future5 ~ deg_pre5 vs score).
Outputs results/tables/paper2_v2_replication_001/{summary,paired_ci,verdict,mechanism}.csv.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_v2_replication_001"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
KS_ARMS = ["none", "lp32", "holdout32", "lcb64", "unsup"]
rng = np.random.default_rng(20260714)


def boot_ci(v, nb=5000):
    v = np.asarray(v); n = len(v)
    b = v[rng.integers(0, n, (nb, n))].mean(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def seeds_ba(path, method):
    f = f"{RAW}/{path}/paper2_progressive_readaptation_by_seed.csv"
    if not os.path.exists(f):
        return None
    d = pd.read_csv(f)
    s = d[d.method == method].set_index("seed")["mean_balanced_accuracy"]
    return s if len(s) else None


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, cis = [], []
    G = {}  # (det, regime, arm) -> per-seed gain series
    for reg in REGIMES:
        for det, arms in [("ks", KS_ARMS), ("qk", ["none", "lp32"])]:
            for arm in arms:
                p = f"paper2_v2_{reg}_{det}_{arm}"
                method = "ks_max" if det == "ks" else "qk_mmd_zz"
                na = seeds_ba(p, "no_adaptation")
                g = seeds_ba(p, method)
                if na is None or g is None:
                    print(f"[skip] {p}"); continue
                gain = (g - na) * 100
                G[(det, reg, arm)] = gain
                lo, hi = boot_ci(gain.values)
                rows.append(dict(detector=det, regime=reg, arm=arm,
                                 gain_pts=round(float(gain.mean()), 3),
                                 ci_lo=round(lo, 3), ci_hi=round(hi, 3)))
    # paired contrasts vs naive on shared streams
    for (det, reg, arm), gain in G.items():
        if arm == "none" or (det, reg, "none") not in G:
            continue
        naive = G[(det, reg, "none")]
        idx = gain.index.intersection(naive.index)
        d = (gain[idx] - naive[idx]).values
        lo, hi = boot_ci(d)
        cis.append(dict(detector=det, regime=reg, contrast=f"{arm}_vs_naive",
                        diff=round(float(d.mean()), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3)))
    R, C = pd.DataFrame(rows), pd.DataFrame(cis)

    def g(det, reg, arm):
        return float(R[(R.detector == det) & (R.regime == reg) & (R.arm == arm)]["gain_pts"].iloc[0])

    def ci(det, reg, con, col):
        return float(C[(C.detector == det) & (C.regime == reg) & (C.contrast == con)][col].iloc[0])

    verdicts = []
    B = (g("ks", "ton_scanning", "lp32") >= -0.5) and (ci("ks", "ton_scanning", "lp32_vs_naive", "ci_lo") > 0)
    verdicts.append(dict(criterion="B ToN lp32 >= -0.5 AND sig above naive (KS)",
                         value=g("ks", "ton_scanning", "lp32"), passed=bool(B)))
    A = g("ks", "portscan", "lp32") >= g("ks", "portscan", "none") - 0.3
    verdicts.append(dict(criterion="A PortScan lp32 >= naive-0.3 (KS)",
                         value=g("ks", "portscan", "lp32"), passed=bool(A)))
    Cc = g("ks", "unsw_recon", "lp32") >= g("ks", "unsw_recon", "none") - 0.3
    verdicts.append(dict(criterion="C UNSW lp32 >= naive-0.3 (KS)",
                         value=g("ks", "unsw_recon", "lp32"), passed=bool(Cc)))
    I = ((g("qk", "ton_scanning", "lp32") >= -0.5) and (ci("qk", "ton_scanning", "lp32_vs_naive", "ci_lo") > 0)
         and (g("qk", "portscan", "lp32") >= g("qk", "portscan", "none") - 0.3))
    verdicts.append(dict(criterion="I detector invariance (QK-ZZ: B and A signs)",
                         value=g("qk", "ton_scanning", "lp32"), passed=bool(I)))
    hold = all(abs(g("ks", r, "holdout32") - g("ks", r, "lp32")) <= 0.3 for r in REGIMES)
    verdicts.append(dict(criterion="EXPL holdout ~ lp32 (|diff|<=0.3 all regimes)",
                         value=g("ks", "ton_scanning", "holdout32"), passed=bool(hold)))
    V = pd.DataFrame(verdicts)

    # per-trigger mechanism (pre-declared exploratory), from naive KS arms
    mech = []
    for reg in REGIMES:
        f = f"{RAW}/paper2_v2_{reg}_ks_none/paper2_v2_trigger_log.csv"
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f).dropna(subset=["delta_future5", "deg_pre5", "score"])
        if len(d) >= 8:
            mech.append(dict(regime=reg, n_triggers=len(d),
                             r_deg=round(float(np.corrcoef(d.deg_pre5, d.delta_future5)[0, 1]), 3),
                             r_score=round(float(np.corrcoef(d.score, d.delta_future5)[0, 1]), 3)))
    if mech:
        alld = pd.concat([pd.read_csv(f"{RAW}/paper2_v2_{r}_ks_none/paper2_v2_trigger_log.csv")
                          for r in REGIMES]).dropna(subset=["delta_future5", "deg_pre5", "score"])
        mech.append(dict(regime="POOLED", n_triggers=len(alld),
                         r_deg=round(float(np.corrcoef(alld.deg_pre5, alld.delta_future5)[0, 1]), 3),
                         r_score=round(float(np.corrcoef(alld.score, alld.delta_future5)[0, 1]), 3)))
    M = pd.DataFrame(mech)

    R.to_csv(f"{OUT}/summary.csv", index=False)
    C.to_csv(f"{OUT}/paired_ci.csv", index=False)
    V.to_csv(f"{OUT}/verdict.csv", index=False)
    M.to_csv(f"{OUT}/mechanism.csv", index=False)
    print(R.to_string(index=False)); print()
    print(C.to_string(index=False)); print()
    print(V.to_string(index=False)); print()
    print(M.to_string(index=False))


if __name__ == "__main__":
    main()
