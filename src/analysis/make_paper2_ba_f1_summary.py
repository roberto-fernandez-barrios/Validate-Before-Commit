"""BA + attack-F1 combined summary, Fig-1 regime spectrum, and F1 robustness of the harm pattern.

Re-aggregation of existing raw window results (no new experiments). Shows the regime taxonomy
(benefit/marginal/mixed/harmful) is metric-robust: under attack-F1 the CICIDS benefits grow and
ToN-IoT stays harmful for every detector. Outputs to results/tables/.
"""
from __future__ import annotations
import os, json
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_metrics_ba_f1_summary_001"
REGIMES = [
    ("cicids_wednesday", "CICIDS Wednesday", "benefit", "paper2_progressive_classical_baselines_final_001"),
    ("cicids_ddos", "CICIDS DDoS", "benefit", "paper2_progressive_cicids_tuesday_friday_ddos_final_001"),
    ("cicids_portscan", "CICIDS PortScan", "benefit", "paper2_progressive_cicids_tuesday_friday_portscan_final_001"),
    ("cicids_webattacks", "CICIDS WebAttacks", "benefit", "paper2_progressive_thursday_webattacks_final_001"),
    ("unsw_dos", "UNSW-NB15 DoS", "marginal", "paper2_unsw_nb15_dos_full30_001"),
    ("unsw_recon", "UNSW-NB15 Reconnaissance", "marginal", "paper2_unsw_nb15_reconnaissance_full30_001"),
    ("ton_iot_scanning", "ToN-IoT Scanning", "harmful", "paper2_ton_iot_scanning_full30_001"),
]
DET = ["energy_distance", "mmd_rbf", "ks_max", "jsd", "qk_mmd_zz", "qk_mmd_pauli_xz"]


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.default_rng(20260701)

    def boot_ci(v, nb=5000):
        v = np.asarray(v); n = len(v)
        b = v[rng.integers(0, n, (nb, n))].mean(1)
        return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    rows, fig1, f1_regret = [], [], []
    for rid, label, klass, run in REGIMES:
        f = f"{RAW}/{run}/paper2_progressive_readaptation_window_results.csv"
        d = pd.read_csv(f, usecols=["seed", "method", "balanced_accuracy", "f1"])
        ba = d.groupby(["seed", "method"])["balanced_accuracy"].mean().unstack("method")
        f1 = d.groupby(["seed", "method"])["f1"].mean().unstack("method")
        na_ba, na_f1 = ba["no_adaptation"], f1["no_adaptation"]
        for m in ["no_adaptation"] + DET:
            rows.append(dict(regime_id=rid, regime=label, klass=klass, method=m, n_seeds=len(ba),
                mean_BA=round(float(ba[m].mean()), 5), mean_F1=round(float(f1[m].mean()), 5),
                gain_BA_pts=round((float(ba[m].mean()) - float(na_ba.mean())) * 100, 3) if m != "no_adaptation" else 0.0,
                gain_F1_pts=round((float(f1[m].mean()) - float(na_f1.mean())) * 100, 3) if m != "no_adaptation" else 0.0))
        detmeans = ba[DET].mean()
        fig1.append(dict(regime_id=rid, regime=label, klass=klass, noadapt_BA=round(float(na_ba.mean()), 5),
            best_adaptive_method=detmeans.idxmax(), best_adaptive_BA=round(float(detmeans.max()), 5),
            best_gain_BA_pts=round((float(detmeans.max()) - float(na_ba.mean())) * 100, 3),
            worst_gain_BA_pts=round((float(detmeans.min()) - float(na_ba.mean())) * 100, 3),
            best_gain_F1_pts=round((float(f1[DET].mean().max()) - float(na_f1.mean())) * 100, 3)))
        det = f1["qk_mmd_zz"].values; na = na_f1.values
        dec = np.maximum(det, na); lo, hi = boot_ci(dec - det)
        f1_regret.append(dict(regime=label, klass=klass, QKzz_naive_F1=round(float(det.mean()), 5),
            QKzz_decOracle_F1=round(float(dec.mean()), 5), regret_F1_pts=round(float(((dec - det) * 100).mean()), 3),
            ci_lo=round(lo * 100, 3), ci_hi=round(hi * 100, 3), harm_seed_pct=round(float((det < na).mean() * 100), 1)))

    pd.DataFrame(rows).to_csv(f"{OUT}/paper2_ba_f1_by_regime_method.csv", index=False)
    pd.DataFrame(fig1).to_csv(f"{OUT}/paper2_fig1_regime_spectrum.csv", index=False)
    pd.DataFrame(f1_regret).to_csv(f"{OUT}/paper2_f1_regret_robustness_qkzz.csv", index=False)
    json.dump(dict(date="2026-07-01",
        note="BA+F1 summary, Fig1 spectrum, F1 robustness of harm/regret pattern from raw window results."),
        open(f"{OUT}/manifest.json", "w"), indent=2)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
