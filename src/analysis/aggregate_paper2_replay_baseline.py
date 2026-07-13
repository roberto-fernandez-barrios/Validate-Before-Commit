"""Phase 2i: replay retraining baseline vs the gate — verdict against pre-fixed criteria.

Reads the 6 Phase-2i run dirs (3 regimes x replay x {none, lp32}, KS-max, SVC, 30 seeds) plus
the Phase-2 full-replacement baselines for context, and evaluates the criteria of
notes/paper2_phase2i_replay_baseline_protocol_001.md:
  R1 harm avoidance (ToN replay-naive gain >= -0.5), R2 benefit preservation
  (PortScan replay-naive gain >= full-replace naive gain - 0.3), R3 marginal
  (UNSW replay-naive gain >= full-replace naive gain - 0.3), G gate orthogonality
  (replay-lp32 never significantly below replay-none or no-adaptation, paired CI).
Outputs results/tables/paper2_phase2i_replay_baseline_001/{summary,paired_ci,verdict}.csv.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_phase2i_replay_baseline_001"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
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
    rows, cis, verdicts = [], [], []
    ctx = {}  # full-replacement naive gain per regime (Phase 2 baselines, same settings)
    for reg in REGIMES:
        p = f"{RAW}/paper2_phase2_{reg}_ks_max_none"
        na, nv = seeds_ba(p, "no_adaptation"), seeds_ba(p, "ks_max")
        ctx[reg] = float((nv - na).mean() * 100) if na is not None and nv is not None else np.nan

    for reg in REGIMES:
        p_none = f"{RAW}/paper2_phase2i_{reg}_replay_none"
        p_lp = f"{RAW}/paper2_phase2i_{reg}_replay_lp32"
        na = seeds_ba(p_none, "no_adaptation")
        rn = seeds_ba(p_none, "ks_max")            # replay-naive
        na_lp = seeds_ba(p_lp, "no_adaptation")
        rl = seeds_ba(p_lp, "ks_max")              # replay + gate lp32
        if na is None or rn is None or na_lp is None or rl is None:
            print(f"[skip] {reg}: missing runs"); continue
        g_rn = (rn - na) * 100
        g_rl = (rl - na_lp) * 100
        rows.append(dict(regime=reg, arm="replay_naive", gain_pts=round(g_rn.mean(), 3),
                         fullreplace_naive_gain=round(ctx[reg], 3)))
        rows.append(dict(regime=reg, arm="replay_lp32", gain_pts=round(g_rl.mean(), 3),
                         fullreplace_naive_gain=round(ctx[reg], 3)))
        # paired CIs (seeds aligned across the two 2i dirs)
        idx = g_rn.index.intersection(g_rl.index)
        d_gate_vs_rnaive = (g_rl[idx] - g_rn[idx]).values
        lo1, hi1 = boot_ci(d_gate_vs_rnaive)
        cis.append(dict(regime=reg, contrast="replay_lp32_vs_replay_naive",
                        diff=round(float(np.mean(d_gate_vs_rnaive)), 3),
                        ci_lo=round(lo1, 3), ci_hi=round(hi1, 3)))
        lo2, hi2 = boot_ci(g_rl.values)
        cis.append(dict(regime=reg, contrast="replay_lp32_vs_noadapt",
                        diff=round(float(g_rl.mean()), 3),
                        ci_lo=round(lo2, 3), ci_hi=round(hi2, 3)))
        lo3, hi3 = boot_ci(g_rn.values)
        cis.append(dict(regime=reg, contrast="replay_naive_vs_noadapt",
                        diff=round(float(g_rn.mean()), 3),
                        ci_lo=round(lo3, 3), ci_hi=round(hi3, 3)))

    R = pd.DataFrame(rows); C = pd.DataFrame(cis)
    g = lambda reg, arm: float(R[(R.regime == reg) & (R.arm == arm)]["gain_pts"].iloc[0])
    verdicts.append(dict(criterion="R1 harm avoidance (ToN replay-naive >= -0.5)",
                         value=g("ton_scanning", "replay_naive"),
                         passed=bool(g("ton_scanning", "replay_naive") >= -0.5)))
    verdicts.append(dict(criterion=f"R2 benefit (PortScan replay-naive >= {ctx['portscan']:.2f}-0.3)",
                         value=g("portscan", "replay_naive"),
                         passed=bool(g("portscan", "replay_naive") >= ctx["portscan"] - 0.3)))
    verdicts.append(dict(criterion=f"R3 marginal (UNSW replay-naive >= {ctx['unsw_recon']:.2f}-0.3)",
                         value=g("unsw_recon", "replay_naive"),
                         passed=bool(g("unsw_recon", "replay_naive") >= ctx["unsw_recon"] - 0.3)))
    for reg in REGIMES:
        for con in ["replay_lp32_vs_replay_naive", "replay_lp32_vs_noadapt"]:
            r = C[(C.regime == reg) & (C.contrast == con)].iloc[0]
            verdicts.append(dict(criterion=f"G {reg} {con} not sig. below (ci_hi >= 0)",
                                 value=float(r["diff"]), passed=bool(r["ci_hi"] >= 0)))
    V = pd.DataFrame(verdicts)
    R.to_csv(f"{OUT}/summary.csv", index=False)
    C.to_csv(f"{OUT}/paired_ci.csv", index=False)
    V.to_csv(f"{OUT}/verdict.csv", index=False)
    print(R.to_string(index=False)); print(); print(C.to_string(index=False)); print()
    print(V.to_string(index=False))


if __name__ == "__main__":
    main()
