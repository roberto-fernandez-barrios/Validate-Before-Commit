"""Robustness of the mechanism law: is r an artifact of aggregation, one dataset, or one regime?

Pure re-aggregation of existing artifacts (no new experiments). Four analyses:
  1. Leave-one-regime-out (LORO) on the 7-regime SVC taxonomy: range of r over the 7 leave-outs.
  2. Leave-one-dataset-out (LODO) on the pooled 16-point set (7 SVC regimes + 3 downstream
     models x 3 regimes): r without CICIDS2017, without UNSW-NB15, without ToN-IoT.
  3. Seed-resampling bootstrap of the 7-regime r: resample the 30 seeds within each regime,
     recompute the regime means and r; CI95 over 5000 resamples. Tests that the aggregate r
     is stable under the sampling variability of the underlying streams.
  4. Descriptive per-seed pooled correlation (7 regimes x 30 seeds = 210 points, best
     detector per regime, seed-paired gain) -- attenuated by within-regime noise by
     construction, reported for transparency.

Reads:
  results/raw/<run>/paper2_progressive_readaptation_window_results.csv  (7 SVC regimes)
  results/tables/paper2_metrics_ba_f1_summary_001/paper2_fig1_regime_spectrum.csv
  results/tables/paper2_phase2c_downstream_generalization_001/paper2_downstream_generalization.csv
Writes results/tables/paper2_mechanism_law_robustness_001/{summary.csv,per_seed_points.csv}.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
TAB = "results/tables"
OUT = f"{TAB}/paper2_mechanism_law_robustness_001"
rng = np.random.default_rng(20260713)

# regime -> (dataset, raw run dir); same map as make_paper2_ba_f1_summary.py
REGIMES = [
    ("CICIDS Wednesday", "cicids", "paper2_progressive_classical_baselines_final_001"),
    ("CICIDS DDoS", "cicids", "paper2_progressive_cicids_tuesday_friday_ddos_final_001"),
    ("CICIDS PortScan", "cicids", "paper2_progressive_cicids_tuesday_friday_portscan_final_001"),
    ("CICIDS WebAttacks", "cicids", "paper2_progressive_thursday_webattacks_final_001"),
    ("UNSW-NB15 DoS", "unsw", "paper2_unsw_nb15_dos_full30_001"),
    ("UNSW-NB15 Reconnaissance", "unsw", "paper2_unsw_nb15_reconnaissance_full30_001"),
    ("ToN-IoT Scanning", "ton_iot", "paper2_ton_iot_scanning_full30_001"),
]
DET = ["energy_distance", "mmd_rbf", "ks_max", "jsd", "qk_mmd_zz", "qk_mmd_pauli_xz"]


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []

    # ---- per-seed (no-adapt BA, best-detector gain) for the 7 SVC regimes -------------
    per_seed = []          # regime, dataset, seed, base_BA_pct, gain_pts
    seed_tables = {}       # regime -> DataFrame indexed by seed with base/gain columns
    for label, ds, run in REGIMES:
        f = f"{RAW}/{run}/paper2_progressive_readaptation_window_results.csv"
        d = pd.read_csv(f, usecols=["seed", "method", "balanced_accuracy"])
        ba = d.groupby(["seed", "method"])["balanced_accuracy"].mean().unstack("method")
        best = ba[DET].mean().idxmax()            # regime-level best detector (as in Fig 1)
        t = pd.DataFrame({"base": ba["no_adaptation"] * 100,
                          "gain": (ba[best] - ba["no_adaptation"]) * 100})
        seed_tables[label] = t
        for seed, r_ in t.iterrows():
            per_seed.append(dict(regime=label, dataset=ds, seed=seed, best_detector=best,
                                 base_BA_pct=round(r_["base"], 4), gain_pts=round(r_["gain"], 4)))
    PS = pd.DataFrame(per_seed)
    PS.to_csv(f"{OUT}/per_seed_points.csv", index=False)

    # regime-level means (must replicate the published 7-regime r)
    M = PS.groupby(["regime", "dataset"], as_index=False)[["base_BA_pct", "gain_pts"]].mean()
    r_full = pearson(M["base_BA_pct"], M["gain_pts"])
    rows.append(dict(analysis="svc7_full", detail="7 regime means", n=len(M), r=round(r_full, 3)))

    # ---- 1. leave-one-regime-out on the 7 regime means --------------------------------
    loro = []
    for i in range(len(M)):
        sub = M.drop(M.index[i])
        loro.append(pearson(sub["base_BA_pct"], sub["gain_pts"]))
        rows.append(dict(analysis="svc7_loro", detail=f"without {M.iloc[i]['regime']}",
                         n=len(sub), r=round(loro[-1], 3)))
    rows.append(dict(analysis="svc7_loro_range", detail="min..max over 7 leave-outs",
                     n=6, r=None, r_min=round(min(loro), 3), r_max=round(max(loro), 3)))

    # ---- 2. leave-one-dataset-out on the pooled 16-point set --------------------------
    pooled = [dict(regime=r_["regime"], dataset=r_["dataset"], base=r_["base_BA_pct"],
                   gain=r_["gain_pts"], source="svc") for _, r_ in M.iterrows()]
    dg = pd.read_csv(f"{TAB}/paper2_phase2c_downstream_generalization_001/"
                     "paper2_downstream_generalization.csv")
    ds_map = {"portscan": "cicids", "unsw_recon": "unsw", "ton_scanning": "ton_iot"}
    for _, r_ in dg.iterrows():
        if r_["downstream"] != "svc_rbf":       # SVC already covered by the taxonomy
            pooled.append(dict(regime=r_["regime"], dataset=ds_map[r_["regime"]],
                               base=r_["noadapt_BA"] * 100, gain=r_["naive_gain"],
                               source=r_["downstream"]))
    P = pd.DataFrame(pooled)
    r_pooled = pearson(P["base"], P["gain"])
    rows.append(dict(analysis="pooled16_full", detail="7 SVC + 9 downstream points",
                     n=len(P), r=round(r_pooled, 3)))
    for ds in ["cicids", "unsw", "ton_iot"]:
        sub = P[P.dataset != ds]
        rows.append(dict(analysis="pooled16_lodo", detail=f"without {ds}", n=len(sub),
                         r=round(pearson(sub["base"], sub["gain"]), 3)))

    # ---- 3. seed-resampling bootstrap of the 7-regime r -------------------------------
    boots = []
    for _ in range(5000):
        xs, ys = [], []
        for label in seed_tables:
            t = seed_tables[label]
            idx = rng.integers(0, len(t), len(t))
            xs.append(t["base"].values[idx].mean())
            ys.append(t["gain"].values[idx].mean())
        boots.append(pearson(xs, ys))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    rows.append(dict(analysis="svc7_seed_bootstrap", detail="resample 30 seeds/regime, 5000x",
                     n=7, r=round(float(np.median(boots)), 3),
                     r_min=round(float(lo), 3), r_max=round(float(hi), 3)))

    # ---- 4. descriptive per-seed pooled correlation (210 points) ----------------------
    r_seed = pearson(PS["base_BA_pct"], PS["gain_pts"])
    rows.append(dict(analysis="per_seed_pooled", detail="7 regimes x 30 seeds", n=len(PS),
                     r=round(r_seed, 3)))

    # ---- 5. coupling diagnostics: is r more than mathematical coupling? ---------------
    # gain = A - N shares N with the predictor, so r(N, A-N) is negative even if A were
    # independent of N. Diagnostics: (a) dispersion of the restored level A vs N; (b) slope
    # of gain on N; (c) exhaustive permutation null that re-pairs the observed A values with
    # the observed N values (holds both marginals; r under "A unrelated to N"); (d) the
    # non-coupled contrast: detector scores do NOT predict the gain, N does.
    from itertools import permutations
    crows = []
    N = M["base_BA_pct"].values
    A = N + M["gain_pts"].values
    crows.append(dict(metric="sigma_noadapt_BA", value=round(float(np.std(N, ddof=1)), 3)))
    crows.append(dict(metric="sigma_adapted_BA", value=round(float(np.std(A, ddof=1)), 3)))
    slope = float(np.polyfit(N, A - N, 1)[0])
    crows.append(dict(metric="slope_gain_on_base", value=round(slope, 3)))
    null_rs = [pearson(N, np.array(p) - N) for p in permutations(A)]
    r_obs = pearson(N, A - N)
    crows.append(dict(metric="perm_null_median_r", value=round(float(np.median(null_rs)), 3)))
    crows.append(dict(metric="perm_null_p_more_negative",
                      value=round(float(np.mean(np.array(null_rs) <= r_obs)), 3)))
    # detector-score contrast: per detector, corr(regime-mean score/threshold, that
    # detector's own gain) across the 7 regimes.
    gains = pd.read_csv(f"{TAB}/paper2_metrics_ba_f1_summary_001/paper2_ba_f1_by_regime_method.csv")
    det_rs = []
    for det in DET:
        xs, ys = [], []
        for label, ds, run in REGIMES:
            w = pd.read_csv(f"{RAW}/{run}/paper2_progressive_readaptation_window_results.csv",
                            usecols=["method", "score", "threshold"])
            w = w[w.method == det].dropna(subset=["score", "threshold"])
            xs.append(float((w["score"] / w["threshold"]).mean()))
            g = gains[(gains.regime == label) & (gains.method == det)]
            ys.append(float(g["gain_BA_pts"].iloc[0]))
        det_rs.append(pearson(xs, ys))
        crows.append(dict(metric=f"detector_score_vs_gain_r__{det}", value=round(det_rs[-1], 3)))
    crows.append(dict(metric="detector_score_vs_gain_r_min", value=round(min(det_rs), 3)))
    crows.append(dict(metric="detector_score_vs_gain_r_max", value=round(max(det_rs), 3)))
    # within-regime (= within a single deployment) versions: over the 30 seeds of each
    # regime, does the detector's score predict that seed's gain? does degradation?
    within_score, within_base = [], []
    for label, ds, run in REGIMES:
        w = pd.read_csv(f"{RAW}/{run}/paper2_progressive_readaptation_window_results.csv",
                        usecols=["seed", "method", "score", "threshold", "balanced_accuracy"])
        ba = w.groupby(["seed", "method"])["balanced_accuracy"].mean().unstack("method")
        best = ba[DET].mean().idxmax()
        gain_s = (ba[best] - ba["no_adaptation"]) * 100
        base_s = ba["no_adaptation"] * 100
        sc = w[w.method == best].dropna(subset=["score", "threshold"])
        ratio_s = (sc["score"] / sc["threshold"]).groupby(sc["seed"]).mean()
        idx = gain_s.index.intersection(ratio_s.index)
        if len(idx) >= 5 and ratio_s[idx].std() > 0 and gain_s[idx].std() > 0:
            within_score.append(pearson(ratio_s[idx], gain_s[idx]))
        if base_s.std() > 0 and gain_s.std() > 0:
            within_base.append(pearson(base_s, gain_s))
    crows.append(dict(metric="within_regime_score_vs_gain_r_median",
                      value=round(float(np.median(within_score)), 3)))
    crows.append(dict(metric="within_regime_score_vs_gain_r_min", value=round(min(within_score), 3)))
    crows.append(dict(metric="within_regime_score_vs_gain_r_max", value=round(max(within_score), 3)))
    crows.append(dict(metric="within_regime_base_vs_gain_r_median",
                      value=round(float(np.median(within_base)), 3)))
    crows.append(dict(metric="within_regime_base_vs_gain_r_min", value=round(min(within_base), 3)))
    crows.append(dict(metric="within_regime_base_vs_gain_r_max", value=round(max(within_base), 3)))
    C = pd.DataFrame(crows)
    C.to_csv(f"{OUT}/coupling_diagnostics.csv", index=False)

    S = pd.DataFrame(rows)
    S.to_csv(f"{OUT}/summary.csv", index=False)
    print(S.to_string(index=False))
    print()
    print(C.to_string(index=False))


if __name__ == "__main__":
    main()
