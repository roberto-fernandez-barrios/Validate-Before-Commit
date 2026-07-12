"""Phase 2h: label-free gates (ATC/DoC) vs labeled probe vs naive — head-to-head.

Per (regime x downstream): gain vs no-adaptation for {naive, lp32, unsup, atc, doc}, paired CIs of each
label-free gate vs naive and vs no-adaptation, and the pre-fixed criteria from
notes/paper2_phase2h_labelfree_gates_protocol_001.md:
  B harm avoidance (ToN gain >= -0.5), A benefit preservation (PortScan BA >= naive-0.3),
  C marginal non-degradation (UNSW BA >= naive-0.3).
Baselines: SVC from phase2 (30 seeds); RF from phase2h none30/lp32x30 (30 seeds).
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_phase2h_labelfree_gates_001"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
rng = np.random.default_rng(20260712)


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


def baseline_paths(reg, dm):
    if dm == "svc_rbf":
        return (f"{RAW}/paper2_phase2_{reg}_ks_max_none", f"{RAW}/paper2_phase2_{reg}_ks_max_lp32",
                f"{RAW}/paper2_phase2_{reg}_ks_max_unsup")
    return (f"{RAW}/paper2_phase2h_{reg}_random_forest_none30",
            f"{RAW}/paper2_phase2h_{reg}_random_forest_lp32x30", None)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, cis = [], []
    for dm in ["svc_rbf", "random_forest"]:
        for reg in REGIMES:
            p_none, p_lp, p_unsup = baseline_paths(reg, dm)
            na = seeds_ba(p_none, "no_adaptation")
            naive = seeds_ba(p_none, "ks_max")
            if na is None or naive is None:
                continue
            entries = {"naive": naive, "lp32": seeds_ba(p_lp, "ks_max")}
            if p_unsup:
                entries["unsup"] = seeds_ba(p_unsup, "ks_max")
            for g in ["atc", "doc"]:
                entries[g] = seeds_ba(f"{RAW}/paper2_phase2h_{reg}_{dm}_{g}", "ks_max")
            for name, s in entries.items():
                if s is None:
                    continue
                rows.append(dict(downstream=dm, regime=reg, gate=name, n=len(s),
                                 BA=round(float(s.mean()), 5),
                                 gain_pts=round(float((s.mean() - na.mean()) * 100), 3)))
                if name in ("atc", "doc"):
                    idx = s.index.intersection(naive.index)
                    dvn = (s.loc[idx] - naive.loc[idx]).values * 100
                    dna = (s.loc[idx] - na.loc[idx]).values * 100
                    l1, h1 = boot_ci(dvn); l2, h2 = boot_ci(dna)
                    cis.append(dict(downstream=dm, regime=reg, gate=name, n=len(idx),
                                    d_vs_naive=round(dvn.mean(), 2), naive_ci=f"[{l1:+.2f},{h1:+.2f}]",
                                    d_vs_noadapt=round(dna.mean(), 2), noadapt_ci=f"[{l2:+.2f},{h2:+.2f}]",
                                    sig_worse_noadapt=bool(h2 < 0), sig_worse_naive=bool(h1 < 0)))
    T = pd.DataFrame(rows); C = pd.DataFrame(cis)
    T.to_csv(f"{OUT}/paper2_labelfree_gates_summary.csv", index=False)
    C.to_csv(f"{OUT}/paper2_labelfree_gates_paired_ci.csv", index=False)

    # Pre-fixed criteria per gate x downstream
    verdicts = []
    for dm in ["svc_rbf", "random_forest"]:
        for g in ["atc", "doc"]:
            def gain(reg, gate):
                r = T[(T.downstream == dm) & (T.regime == reg) & (T.gate == gate)]
                return float(r["gain_pts"].iloc[0]) if len(r) else None
            def ba(reg, gate):
                r = T[(T.downstream == dm) & (T.regime == reg) & (T.gate == gate)]
                return float(r["BA"].iloc[0]) if len(r) else None
            gt, gp, gu = gain("ton_scanning", g), ba("portscan", g), ba("unsw_recon", g)
            np_, nu = ba("portscan", "naive"), ba("unsw_recon", "naive")
            if None in (gt, gp, gu, np_, nu):
                continue
            B = gt >= -0.5
            A = gp >= np_ - 0.003
            Cc = gu >= nu - 0.003
            verdicts.append(dict(downstream=dm, gate=g, B_harm_avoid=B, A_benefit=A, C_marginal=Cc,
                                 passes_all=bool(A and B and Cc)))
    V = pd.DataFrame(verdicts)
    V.to_csv(f"{OUT}/paper2_labelfree_gates_verdict.csv", index=False)

    pd.set_option("display.width", 220, "display.max_columns", 25)
    print("=== gains vs no-adaptation (pts) ===")
    print(T.pivot_table(index=["downstream", "regime"], columns="gate", values="gain_pts").round(2).to_string())
    print("\n=== paired CIs (atc/doc) ===")
    print(C.to_string(index=False))
    print("\n=== pre-fixed criteria verdict ===")
    print(V.to_string(index=False))


if __name__ == "__main__":
    main()
