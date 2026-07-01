"""Aggregate Paper 2 Phase 2 gated-readaptation results and evaluate pre-registered criteria.

Reads results/raw/paper2_phase2_{regime}_{detector}_{gate}/ by_seed CSVs, computes per
(regime, detector, gate) means, and checks the pre-registered success criteria A/B/C/D/E
from notes/paper2_phase2_gated_readaptation_preregistration_001.md. No new experiments.
"""
from __future__ import annotations
import os, glob, json
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_phase2_gated_readaptation_001"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
GATES = ["none", "lp32", "lp64", "unsup"]


def load(regime, detector, gate):
    f = f"{RAW}/paper2_phase2_{regime}_{detector}_{gate}/paper2_progressive_readaptation_by_seed.csv"
    if not os.path.exists(f):
        return None
    return pd.read_csv(f)


def main():
    os.makedirs(OUT, exist_ok=True)
    # discover detectors present
    dets = set()
    for p in glob.glob(f"{RAW}/paper2_phase2_*_*_*"):
        name = os.path.basename(p)
        for reg in REGIMES:
            if name.startswith(f"paper2_phase2_{reg}_"):
                rest = name[len(f"paper2_phase2_{reg}_"):]
                for g in GATES:
                    if rest.endswith(f"_{g}"):
                        dets.add(rest[: -(len(g) + 1)])
    dets = sorted(dets)

    rows = []
    for reg in REGIMES:
        for det in dets:
            # baseline no-adapt from the 'none' run
            base = load(reg, det, "none")
            if base is None:
                continue
            na = base[base["method"] == "no_adaptation"]["mean_balanced_accuracy"].mean()
            for gate in GATES:
                d = load(reg, det, gate)
                if d is None:
                    continue
                e = d[d["method"] == det]
                if len(e) == 0:
                    continue
                rows.append(dict(
                    regime=reg, detector=det, gate=gate, n_seeds=len(e),
                    BA_noadapt=round(na, 5),
                    BA=round(e["mean_balanced_accuracy"].mean(), 5),
                    gain_pts=round((e["mean_balanced_accuracy"].mean() - na) * 100, 3),
                    commits=round(e["n_adaptations"].mean(), 2),
                    triggers=round(e.get("n_triggers", pd.Series([np.nan])).mean(), 2),
                    rejections=round(e.get("n_gate_rejections", pd.Series([0])).mean(), 2),
                    labels=round(e.get("labels_used_total", pd.Series([0])).mean(), 1),
                ))
    T = pd.DataFrame(rows)
    T.to_csv(f"{OUT}/paper2_phase2_summary.csv", index=False)

    # Paired bootstrap CIs: gate vs naive(none) and gate vs no-adaptation, per seed.
    rng = np.random.default_rng(20260701)
    def boot_ci(v, nb=5000):
        v = np.asarray(v); n = len(v)
        b = v[rng.integers(0, n, (nb, n))].mean(1)
        return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
    ci_rows = []
    for reg in REGIMES:
        for det in dets:
            none = load(reg, det, "none")
            if none is None:
                continue
            naive_seed = none[none.method == det].set_index("seed")["mean_balanced_accuracy"]
            na_seed = none[none.method == "no_adaptation"].set_index("seed")["mean_balanced_accuracy"]
            for gate in ["lp32", "lp64", "unsup"]:
                d = load(reg, det, gate)
                if d is None:
                    continue
                g_seed = d[d.method == det].set_index("seed")["mean_balanced_accuracy"]
                idx = g_seed.index.intersection(naive_seed.index)
                dvn = (g_seed.loc[idx] - naive_seed.loc[idx]).values * 100
                dvna = (g_seed.loc[idx] - na_seed.loc[idx]).values * 100
                lo1, hi1 = boot_ci(dvn); lo2, hi2 = boot_ci(dvna)
                ci_rows.append(dict(regime=reg, detector=det, gate=gate, n=len(idx),
                    diff_vs_naive_pts=round(dvn.mean(), 3), naive_ci_lo=round(lo1, 3), naive_ci_hi=round(hi1, 3),
                    naive_sig=bool(lo1 > 0 or hi1 < 0),
                    diff_vs_noadapt_pts=round(dvna.mean(), 3), noadapt_ci_lo=round(lo2, 3), noadapt_ci_hi=round(hi2, 3),
                    noadapt_sig=bool(lo2 > 0 or hi2 < 0)))
    CI = pd.DataFrame(ci_rows)
    CI.to_csv(f"{OUT}/paper2_phase2_paired_ci.csv", index=False)

    # Pre-registered criteria per detector
    checks = []
    for det in dets:
        def ba(reg, gate):
            r = T[(T.regime == reg) & (T.detector == det) & (T.gate == gate)]
            return float(r["BA"].iloc[0]) if len(r) else np.nan
        def gain(reg, gate):
            r = T[(T.regime == reg) & (T.detector == det) & (T.gate == gate)]
            return float(r["gain_pts"].iloc[0]) if len(r) else np.nan
        na_ton = ba("ton_scanning", "none")
        na_ton_base = T[(T.regime == "ton_scanning") & (T.detector == det) & (T.gate == "none")]["BA_noadapt"]
        na_ton_base = float(na_ton_base.iloc[0]) if len(na_ton_base) else np.nan
        for gate in ["lp32", "lp64", "unsup"]:
            gA = gain("portscan", gate); gA_naive = gain("portscan", "none")
            A = (gA >= 0.90 * gA_naive) and (ba("portscan", gate) >= ba("portscan", "none") - 0.003)
            B = ba("ton_scanning", gate) >= na_ton_base - 0.005
            C = ba("unsw_recon", gate) >= ba("unsw_recon", "none") - 0.003
            checks.append(dict(detector=det, gate=gate,
                A_benefit_preservation=bool(A), B_harm_avoidance=bool(B),
                C_mixed_nondegradation=bool(C),
                passes_ABC=bool(A and B and C)))
    C = pd.DataFrame(checks)
    C.to_csv(f"{OUT}/paper2_phase2_criteria.csv", index=False)

    # Overall verdict
    lp = C[C.gate.isin(["lp32", "lp64"])]
    dets_pass = lp.groupby("detector")["passes_ABC"].any()
    D_label_eff = bool(lp[lp.passes_ABC]["gate"].isin(["lp32", "lp64"]).any())
    E_invariance = bool(dets_pass.all()) and len(dets_pass) >= 1
    verdict = dict(detectors=list(dets),
                   per_detector_labeled_probe_passes={k: bool(v) for k, v in dets_pass.items()},
                   D_label_efficiency=D_label_eff,
                   E_detector_invariance=E_invariance,
                   PHASE2_PASSES=bool(D_label_eff and E_invariance))
    json.dump(verdict, open(f"{OUT}/paper2_phase2_verdict.json", "w"), indent=2)

    pd.set_option("display.width", 200, "display.max_columns", 20)
    print("=== SUMMARY ===")
    print(T.to_string(index=False))
    print("\n=== CRITERIA (labeled_probe & unsup, per detector) ===")
    print(C.to_string(index=False))
    print("\n=== PAIRED CIs (gate vs naive / vs no-adapt, pts, CI95) ===")
    print(CI.to_string(index=False))
    print("\n=== VERDICT ===")
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
