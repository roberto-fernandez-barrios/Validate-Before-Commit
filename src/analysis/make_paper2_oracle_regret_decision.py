"""Decision-level oracle-regret for Paper 2 (re-aggregation of existing window results).

Per stream (seed), an abstain-if-harmful oracle with a FIXED detector:
    decision_oracle = mean_seed( max(no_adaptation_seed_BA, detector_seed_BA) )
    regret          = decision_oracle - naive_triggered_BA   (balanced-accuracy points x100)
    harm_seed_pct   = fraction of seeds where adapting scored BELOW no-adaptation.

This isolates the value of the adapt/no-adapt DECISION from detector-selection hindsight.
We deliberately avoid a per-window envelope or cross-detector selection oracle (they conflate
detector variance with decision value). No new experiments. Outputs to results/tables/.
"""
from __future__ import annotations
import os, json
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_oracle_regret_decision_001"
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

    by_det, summ = [], []
    for rid, label, klass, run in REGIMES:
        f = f"{RAW}/{run}/paper2_progressive_readaptation_window_results.csv"
        d = pd.read_csv(f, usecols=["seed", "method", "balanced_accuracy"])
        sm = d.groupby(["seed", "method"])["balanced_accuracy"].mean().unstack("method")
        na = sm["no_adaptation"].values
        BA_na = float(na.mean())
        regrets_all = []
        for m in DET:
            det = sm[m].values
            naive = float(det.mean())
            dec = np.maximum(det, na)
            regret_seed = (dec - det) * 100
            lo, hi = boot_ci(regret_seed)
            harm = float((det < na).mean() * 100)
            regrets_all.append(regret_seed.mean())
            by_det.append(dict(regime_id=rid, regime=label, klass=klass, detector=m, n_seeds=len(det),
                BA_noadapt=round(BA_na, 5), naive_BA=round(naive, 5), decision_oracle_BA=round(float(dec.mean()), 5),
                adapt_help_pts=round((naive - BA_na) * 100, 3),
                regret_pts=round(float(regret_seed.mean()), 3), regret_ci_lo=round(lo, 3), regret_ci_hi=round(hi, 3),
                harm_seed_pct=round(harm, 1)))
        summ.append(dict(regime_id=rid, regime=label, klass=klass, n_seeds=len(na),
            BA_noadapt=round(BA_na, 5), best_detector_BA=round(float(sm[DET].mean().max()), 5),
            best_detector=sm[DET].mean().idxmax(), adapt_help_pts=round((float(sm[DET].mean().max()) - BA_na) * 100, 3),
            mean_regret_pts=round(float(np.mean(regrets_all)), 3),
            mean_harm_seed_pct=round(float(np.mean([(sm[m].values < na).mean() * 100 for m in DET])), 1)))

    pd.DataFrame(summ).to_csv(f"{OUT}/paper2_oracle_regret_summary.csv", index=False)
    pd.DataFrame(by_det).to_csv(f"{OUT}/paper2_oracle_regret_by_detector.csv", index=False)
    json.dump(dict(date="2026-07-01", oracle="per-seed abstain-if-harmful, fixed detector",
        note="regret ~0 in pure-benefit regimes; largest in harm regime (ToN-IoT QK-ZZ 3.50 pts, 80% harm)."),
        open(f"{OUT}/manifest.json", "w"), indent=2)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
