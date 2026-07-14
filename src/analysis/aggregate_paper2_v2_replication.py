"""Harness-v2 registered replication (amendment 002): verdict on pristine seeds 104-133.

Criteria transcribe the locked protocol + amendment: top-up dirs (`_top`, seeds 131-133) are
merged with the originals and the confirmatory window is seeds 104-133; the holdout arm uses
the deduplicated rerun (`holdout32b`). Adds cluster (per-seed) bootstrap CIs and
leave-one-regime-out to the per-trigger mechanism, plus classifier-generalization and
natural-prevalence (natural calibration) aggregations.
Outputs results/tables/paper2_v2_replication_001/*.csv (summary, paired_ci, verdict,
mechanism, classifiers, natprev).
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_v2_replication_001"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
SEEDS = set(range(104, 134))
rng = np.random.default_rng(20260714)


def boot_ci(v, nb=5000):
    v = np.asarray(v); n = len(v)
    b = v[rng.integers(0, n, (nb, n))].mean(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def read_by_seed(dirs, method, col="mean_balanced_accuracy"):
    parts = []
    for d in dirs:
        f = f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv"
        if os.path.exists(f):
            parts.append(pd.read_csv(f))
    if not parts:
        return None
    d = pd.concat(parts)
    d = d[(d.method == method) & (d.seed.isin(SEEDS))]
    s = d.set_index("seed")[col]
    return s.sort_index() if len(s) else None


def arm_dirs(reg, det, arm):
    if arm == "holdout32":
        return [f"paper2_v2_{reg}_ks_holdout32b"]
    base = f"paper2_v2_{reg}_{det}_{arm}"
    return [base, base + "_top"]


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, cis = [], []
    G = {}
    for reg in REGIMES:
        for det, arms in [("ks", ["none", "lp32", "holdout32", "lcb64", "unsup"]),
                          ("qk", ["none", "lp32"])]:
            method = "ks_max" if det == "ks" else "qk_mmd_zz"
            for arm in arms:
                dirs = arm_dirs(reg, det, arm)
                na = read_by_seed(dirs, "no_adaptation")
                g = read_by_seed(dirs, method)
                if na is None or g is None or len(g) < 25:
                    print(f"[skip] {reg} {det} {arm} n={0 if g is None else len(g)}"); continue
                gain = (g - na) * 100
                G[(det, reg, arm)] = gain
                lo, hi = boot_ci(gain.values)
                rows.append(dict(detector=det, regime=reg, arm=arm, n=len(gain),
                                 gain_pts=round(float(gain.mean()), 3),
                                 ci_lo=round(lo, 3), ci_hi=round(hi, 3)))
    for (det, reg, arm), gain in list(G.items()):
        if arm == "none" or (det, reg, "none") not in G:
            continue
        naive = G[(det, reg, "none")]
        idx = gain.index.intersection(naive.index)
        d = (gain[idx] - naive[idx]).values
        lo, hi = boot_ci(d)
        cis.append(dict(detector=det, regime=reg, contrast=f"{arm}_vs_naive", n=len(idx),
                        diff=round(float(d.mean()), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3)))
    R, C = pd.DataFrame(rows), pd.DataFrame(cis)

    def g(det, reg, arm):
        return float(R[(R.detector == det) & (R.regime == reg) & (R.arm == arm)]["gain_pts"].iloc[0])

    def ci(det, reg, con, col):
        return float(C[(C.detector == det) & (C.regime == reg) & (C.contrast == con)][col].iloc[0])

    verdicts = [
        dict(criterion="B ToN lp32 >= -0.5 AND sig above naive (KS)", value=g("ks", "ton_scanning", "lp32"),
             passed=bool(g("ks", "ton_scanning", "lp32") >= -0.5 and ci("ks", "ton_scanning", "lp32_vs_naive", "ci_lo") > 0)),
        dict(criterion="A PortScan lp32 >= naive-0.3 (KS)", value=g("ks", "portscan", "lp32"),
             passed=bool(g("ks", "portscan", "lp32") >= g("ks", "portscan", "none") - 0.3)),
        dict(criterion="C UNSW lp32 >= naive-0.3 (KS)", value=g("ks", "unsw_recon", "lp32"),
             passed=bool(g("ks", "unsw_recon", "lp32") >= g("ks", "unsw_recon", "none") - 0.3)),
        dict(criterion="I detector invariance (QK-ZZ)", value=g("qk", "ton_scanning", "lp32"),
             passed=bool(g("qk", "ton_scanning", "lp32") >= -0.5 and ci("qk", "ton_scanning", "lp32_vs_naive", "ci_lo") > 0
                         and g("qk", "portscan", "lp32") >= g("qk", "portscan", "none") - 0.3)),
        dict(criterion="EXPL holdout(dedup) ~ lp32 (|diff|<=0.3)", value=g("ks", "ton_scanning", "holdout32"),
             passed=bool(all(abs(g("ks", r, "holdout32") - g("ks", r, "lp32")) <= 0.3 for r in REGIMES))),
    ]
    V = pd.DataFrame(verdicts)

    # per-trigger mechanism with clustered inference (naive KS arms, incl. top-ups)
    def trig(reg):
        parts = []
        for d in [f"paper2_v2_{reg}_ks_none", f"paper2_v2_{reg}_ks_none_top"]:
            f = f"{RAW}/{d}/paper2_v2_trigger_log.csv"
            if os.path.exists(f):
                parts.append(pd.read_csv(f))
        d = pd.concat(parts)
        d = d[d.seed.isin(SEEDS)].dropna(subset=["delta_future5", "deg_pre5", "score"])
        d["regime"] = reg
        return d

    T = pd.concat([trig(r) for r in REGIMES])
    def pear(d, x): return float(np.corrcoef(d[x], d["delta_future5"])[0, 1])
    mech = []
    for reg in REGIMES + ["POOLED"]:
        d = T if reg == "POOLED" else T[T.regime == reg]
        seeds = d.seed.unique()
        boots_deg, boots_sc = [], []
        for _ in range(2000):
            pick = rng.choice(seeds, len(seeds), replace=True)
            db = pd.concat([d[d.seed == s] for s in pick])
            if db.deg_pre5.std() > 0 and db.delta_future5.std() > 0:
                boots_deg.append(pear(db, "deg_pre5"))
                boots_sc.append(pear(db, "score"))
        mech.append(dict(regime=reg, n_triggers=len(d), n_seeds=len(seeds),
                         r_deg=round(pear(d, "deg_pre5"), 3),
                         r_deg_lo=round(float(np.percentile(boots_deg, 2.5)), 3),
                         r_deg_hi=round(float(np.percentile(boots_deg, 97.5)), 3),
                         r_score=round(pear(d, "score"), 3),
                         r_score_lo=round(float(np.percentile(boots_sc, 2.5)), 3),
                         r_score_hi=round(float(np.percentile(boots_sc, 97.5)), 3)))
    for reg in REGIMES:  # leave-one-regime-out on the pooled correlation
        d = T[T.regime != reg]
        mech.append(dict(regime=f"LORO_wo_{reg}", n_triggers=len(d), n_seeds=d.seed.nunique(),
                         r_deg=round(pear(d, "deg_pre5"), 3), r_deg_lo=None, r_deg_hi=None,
                         r_score=round(pear(d, "score"), 3), r_score_lo=None, r_score_hi=None))
    M = pd.DataFrame(mech)

    # classifier generalization on v2 (naive vs holdout, paired)
    cls_rows = []
    for reg in REGIMES:
        for dm in ["random_forest", "logreg", "mlp"]:
            na_d = [f"paper2_v2_{reg}_ks_none_{dm}"]; ho_d = [f"paper2_v2_{reg}_ks_holdout32_{dm}"]
            base = read_by_seed(na_d, "no_adaptation"); nv = read_by_seed(na_d, "ks_max")
            hb = read_by_seed(ho_d, "no_adaptation"); ho = read_by_seed(ho_d, "ks_max")
            if base is None or nv is None or ho is None:
                print(f"[skip cls] {reg} {dm}"); continue
            gn, gh = (nv - base) * 100, (ho - hb) * 100
            dlo, dhi = boot_ci((gh - gn).values)
            hlo, hhi = boot_ci(gh.values)
            cls_rows.append(dict(regime=reg, downstream=dm,
                                 naive_gain=round(float(gn.mean()), 3), hold_gain=round(float(gh.mean()), 3),
                                 hold_vs_naive=round(float((gh - gn).mean()), 3),
                                 hvn_lo=round(dlo, 3), hvn_hi=round(dhi, 3),
                                 hold_vs_noadapt_lo=round(hlo, 3), hold_vs_noadapt_hi=round(hhi, 3)))
    CL = pd.DataFrame(cls_rows)

    # classifier generalization on v2 with the PRIMARY gate (naive vs fresh probe, paired) --
    # this block produces classifiers_lp32.csv, the table the manuscript reports (amendment 004
    # committed it; the runs are paper2_v2_{reg}_ks_lp32_{dm})
    cls2_rows = []
    for reg in REGIMES:
        for dm in ["random_forest", "logreg", "mlp"]:
            na_d = [f"paper2_v2_{reg}_ks_none_{dm}"]; lp_d = [f"paper2_v2_{reg}_ks_lp32_{dm}"]
            base = read_by_seed(na_d, "no_adaptation"); nv = read_by_seed(na_d, "ks_max")
            lb = read_by_seed(lp_d, "no_adaptation"); lp = read_by_seed(lp_d, "ks_max")
            if base is None or nv is None or lb is None or lp is None:
                print(f"[skip cls-lp32] {reg} {dm}"); continue
            gn, gl = (nv - base) * 100, (lp - lb) * 100
            dlo, dhi = boot_ci((gl - gn).values)
            llo, lhi = boot_ci(gl.values)
            cls2_rows.append(dict(regime=reg, dm=dm,
                                  naive=round(float(gn.mean()), 3), lp32=round(float(gl.mean()), 3),
                                  lp32_vs_naive=round(float((gl - gn).mean()), 3),
                                  lvn_lo=round(dlo, 3), lvn_hi=round(dhi, 3),
                                  lp32_vs_na_lo=round(llo, 3), lp32_vs_na_hi=round(lhi, 3)))
    CL2 = pd.DataFrame(cls2_rows)

    # natural prevalence, natural calibration
    np_rows = []
    for reg in REGIMES:
        for arm in ["none", "lp32"]:
            d = [f"paper2_v3b_{reg}_natprev2_{arm}"]
            base = read_by_seed(d, "no_adaptation"); gv = read_by_seed(d, "ks_max")
            if base is None or gv is None:
                print(f"[skip natprev2] {reg} {arm}"); continue
            gain = (gv - base) * 100
            lo, hi = boot_ci(gain.values)
            w = pd.read_csv(f"{RAW}/{d[0]}/paper2_progressive_readaptation_window_results.csv")
            k = w[(w.method == "ks_max") & (w.seed.isin(SEEDS))]
            fpr_s = k.groupby("seed").fpr.mean(); rec_s = k.groupby("seed").recall.mean(); al_s = k.groupby("seed").alerts.mean()
            flo, fhi = boot_ci(fpr_s.values)
            np_rows.append(dict(regime=reg, arm=arm, gain=round(float(gain.mean()), 3),
                                ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                                fpr=round(float(fpr_s.mean()), 4), fpr_lo=round(flo, 4), fpr_hi=round(fhi, 4),
                                recall=round(float(rec_s.mean()), 4), alerts=round(float(al_s.mean()), 2)))
    NP = pd.DataFrame(np_rows)

    for name, df in [("summary", R), ("paired_ci", C), ("verdict", V), ("mechanism", M),
                     ("classifiers", CL), ("classifiers_lp32", CL2), ("natprev", NP)]:
        df.to_csv(f"{OUT}/{name}.csv", index=False)
        print(f"== {name} =="); print(df.to_string(index=False)); print()


if __name__ == "__main__":
    main()
