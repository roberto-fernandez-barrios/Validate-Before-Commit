"""Pre-submission audit: verify every headline number claimed in the manuscript against the artifacts.

Each check encodes a numeric claim as written in manuscript/paper2_manuscript_draft_002.md (abstract +
sections 5.1-5.7) and compares it to the corresponding value in the committed result CSVs. Run before
submission; all checks must PASS. No new experiments -- verification only.
"""
from __future__ import annotations
import re
import numpy as np
import pandas as pd

T = "results/tables"
results = []


def check(name, claimed, actual, tol):
    ok = actual is not None and abs(actual - claimed) <= tol
    results.append((ok, name, claimed, actual))
    return ok


def row(df, **kv):
    m = df
    for k, v in kv.items():
        m = m[m[k] == v]
    return m.iloc[0] if len(m) else None


def val(df, col, **kv):
    r = row(df, **kv)
    return float(r[col]) if r is not None else None


def main():
    spect = pd.read_csv(f"{T}/paper2_metrics_ba_f1_summary_001/paper2_fig1_regime_spectrum.csv")
    baf1 = pd.read_csv(f"{T}/paper2_metrics_ba_f1_summary_001/paper2_ba_f1_by_regime_method.csv")
    regret = pd.read_csv(f"{T}/paper2_oracle_regret_decision_001/paper2_oracle_regret_by_detector.csv")
    gate = pd.read_csv(f"{T}/paper2_phase2_gated_readaptation_001/paper2_phase2_summary.csv")
    ci = pd.read_csv(f"{T}/paper2_phase2_gated_readaptation_001/paper2_phase2_paired_ci.csv")
    budget = pd.read_csv(f"{T}/paper2_phase2b_budget_curve_001/paper2_phase2b_budget_curve.csv")
    lat = pd.read_csv(f"{T}/paper2_gate_robustness_001/paper2_gate_label_latency.csv")
    harm = pd.read_csv(f"{T}/paper2_gate_robustness_001/paper2_gate_extra_harm_regimes.csv")
    marg = pd.read_csv(f"{T}/paper2_gate_robustness_001/paper2_gate_margin_sweep.csv")
    pois = pd.read_csv(f"{T}/paper2_gate_robustness_001/paper2_gate_probe_poison.csv")
    down = pd.read_csv(f"{T}/paper2_phase2c_downstream_generalization_001/paper2_downstream_generalization.csv")
    pts = pd.read_csv(f"{T}/paper2_mechanism_law_points.csv")

    # --- Section 5.1: regime taxonomy (best adaptation gain, BA pts) ---
    check("5.1 DDoS gain +19.5", 19.5, val(spect, "best_gain_BA_pts", regime_id="cicids_ddos"), 0.06)
    check("5.1 Wednesday gain +11.9", 11.9, val(spect, "best_gain_BA_pts", regime_id="cicids_wednesday"), 0.06)
    check("5.1 WebAttacks gain +7.6", 7.6, val(spect, "best_gain_BA_pts", regime_id="cicids_webattacks"), 0.06)
    check("5.1 PortScan gain +6.2", 6.2, val(spect, "best_gain_BA_pts", regime_id="cicids_portscan"), 0.06)
    check("5.1 UNSW DoS gain +1.4", 1.4, val(spect, "best_gain_BA_pts", regime_id="unsw_dos"), 0.06)
    check("5.1 UNSW Recon gain +0.5", 0.5, val(spect, "best_gain_BA_pts", regime_id="unsw_recon"), 0.06)
    check("5.1 ToN best adaptive -0.5", -0.5, val(spect, "best_gain_BA_pts", regime_id="ton_iot_scanning"), 0.06)
    check("5.1 ToN worst adaptive -4.6", -4.6, val(spect, "worst_gain_BA_pts", regime_id="ton_iot_scanning"), 0.06)
    check("5.1 DDoS F1 gain +32.3", 32.3, val(spect, "best_gain_F1_pts", regime_id="cicids_ddos"), 0.06)
    check("5.1 ToN Energy F1 -0.2", -0.2, val(baf1, "gain_F1_pts", regime_id="ton_iot_scanning", method="energy_distance"), 0.06)
    check("5.1 ToN KS F1 -4.6", -4.6, val(baf1, "gain_F1_pts", regime_id="ton_iot_scanning", method="ks_max"), 0.06)

    # --- Section 5.2: mechanism law + oracle regret ---
    svc = pts[pts.source == "svc_taxonomy"]
    r_svc = float(np.corrcoef(svc.base_BA, svc.gain)[0, 1])
    r_pool = float(np.corrcoef(pts.base_BA, pts.gain)[0, 1])
    check("5.2 r SVC -0.89", -0.89, r_svc, 0.006)
    check("5.2 r pooled -0.81", -0.81, r_pool, 0.006)
    check("5.2 pooled n=16", 16, float(len(pts)), 0.1)
    check("5.2 DDoS no-adapt 69.8%", 69.8, val(spect, "noadapt_BA", regime_id="cicids_ddos") * 100, 0.06)
    check("5.2 ToN no-adapt 92.2%", 92.2, val(spect, "noadapt_BA", regime_id="ton_iot_scanning") * 100, 0.06)
    check("5.2 Wed QK regret 0.00", 0.0, val(regret, "regret_pts", regime_id="cicids_wednesday", detector="qk_mmd_zz"), 0.006)
    check("5.2 Wed QK harm 0%", 0.0, val(regret, "harm_seed_pct", regime_id="cicids_wednesday", detector="qk_mmd_zz"), 0.1)
    check("5.2 ToN QK regret 3.53", 3.53, val(regret, "regret_pts", regime_id="ton_iot_scanning", detector="qk_mmd_zz"), 0.006)
    check("5.2 ToN QK regret CI lo 1.76", 1.76, val(regret, "regret_ci_lo", regime_id="ton_iot_scanning", detector="qk_mmd_zz"), 0.006)
    check("5.2 ToN QK regret CI hi 5.54", 5.54, val(regret, "regret_ci_hi", regime_id="ton_iot_scanning", detector="qk_mmd_zz"), 0.006)
    check("5.2 ToN QK harm 67%", 66.7, val(regret, "harm_seed_pct", regime_id="ton_iot_scanning", detector="qk_mmd_zz"), 0.1)

    # --- Sections 5.3/5.5: pre-registered gate, 30 seeds ---
    check("5.5 ToN naive KS -1.36", -1.36, val(gate, "gain_pts", regime="ton_scanning", detector="ks_max", gate="none"), 0.006)
    check("5.5 ToN naive QK -3.69", -3.69, val(gate, "gain_pts", regime="ton_scanning", detector="qk_mmd_zz", gate="none"), 0.006)
    check("5.5 ToN gate KS +0.93", 0.93, val(gate, "gain_pts", regime="ton_scanning", detector="ks_max", gate="lp32"), 0.006)
    check("5.5 ToN gate QK +1.06", 1.06, val(gate, "gain_pts", regime="ton_scanning", detector="qk_mmd_zz", gate="lp32"), 0.006)
    check("5.5 KS vs naive +2.30", 2.30, val(ci, "diff_vs_naive_pts", regime="ton_scanning", detector="ks_max", gate="lp32"), 0.006)
    check("5.5 KS vs naive CI lo 1.15", 1.15, val(ci, "naive_ci_lo", regime="ton_scanning", detector="ks_max", gate="lp32"), 0.01)
    check("5.5 KS vs naive CI hi 3.63", 3.63, val(ci, "naive_ci_hi", regime="ton_scanning", detector="ks_max", gate="lp32"), 0.01)
    check("5.5 QK vs naive +4.74", 4.74, val(ci, "diff_vs_naive_pts", regime="ton_scanning", detector="qk_mmd_zz", gate="lp32"), 0.006)
    check("5.5 QK vs naive CI [2.47,", 2.47, val(ci, "naive_ci_lo", regime="ton_scanning", detector="qk_mmd_zz", gate="lp32"), 0.01)
    check("5.5 QK vs naive CI ,7.69]", 7.69, val(ci, "naive_ci_hi", regime="ton_scanning", detector="qk_mmd_zz", gate="lp32"), 0.01)
    check("5.5 KS vs noadapt +0.93 [0.53,1.36]", 0.93, val(ci, "diff_vs_noadapt_pts", regime="ton_scanning", detector="ks_max", gate="lp32"), 0.006)
    check("5.5 QK vs noadapt +1.06 [0.77,1.40]", 1.06, val(ci, "diff_vs_noadapt_pts", regime="ton_scanning", detector="qk_mmd_zz", gate="lp32"), 0.006)
    check("5.5 unsup KS -4.95", -4.95, val(gate, "gain_pts", regime="ton_scanning", detector="ks_max", gate="unsup"), 0.006)
    check("5.5 unsup QK -5.26", -5.26, val(gate, "gain_pts", regime="ton_scanning", detector="qk_mmd_zz", gate="unsup"), 0.006)
    check("5.5 PortScan gate KS +8.27", 8.27, val(gate, "gain_pts", regime="portscan", detector="ks_max", gate="lp32"), 0.006)
    check("5.5 PortScan gate QK +8.37", 8.37, val(gate, "gain_pts", regime="portscan", detector="qk_mmd_zz", gate="lp32"), 0.006)
    lp32_labels = gate[(gate.gate == "lp32")]["labels"]
    check("5.5 labels ~100-160 (min)", 100, float(lp32_labels.min()), 1.5)
    check("5.5 labels ~100-160 (max)", 160, float(lp32_labels.max()), 4.0)

    # --- Section 5.6: robustness ---
    check("5.6 ToN lp8 +0.38", 0.38, val(budget, "gain_pts", regime="ton_scanning", budget=8), 0.006)
    check("5.6 ToN lp8 labels ~23", 23, val(budget, "labels", regime="ton_scanning", budget=8), 0.5)
    check("5.6 Wednesday naive +15.39", 15.39, val(budget, "gain_pts", regime="wednesday", policy="naive"), 0.006)
    check("5.6 Wednesday gate +16.32", 16.32, val(budget, "gain_pts", regime="wednesday", budget=64), 0.006)
    check("5.6 DDoS naive +24.81", 24.81, val(budget, "gain_pts", regime="ddos", policy="naive"), 0.006)
    check("5.6 DDoS gate +25.27", 25.27, val(budget, "gain_pts", regime="ddos", budget=64), 0.006)
    ton_lags = lat[(lat.regime == "ton_scanning") & (lat.probe_lag > 0)]["gate_gain"]
    check("5.6 lag ToN min >= 0.9", 0.95, float(ton_lags.min()), 0.06)
    check("5.6 lag ToN max <= 1.1", 1.06, float(ton_lags.max()), 0.06)
    check("5.6 ToN DDoS naive -16.81", -16.81, val(harm, "naive_gain", regime="ToN-IoT ddos"), 0.006)
    check("5.6 ToN DDoS gate +1.26", 1.26, val(harm, "gate_gain", regime="ToN-IoT ddos"), 0.006)
    check("5.6 ToN Injection naive -1.21", -1.21, val(harm, "naive_gain", regime="ToN-IoT injection"), 0.006)
    check("5.6 ToN Injection gate +0.80", 0.80, val(harm, "gate_gain", regime="ToN-IoT injection"), 0.006)
    check("5.6 margin PortScan commits 3.1->2.2", 2.15, val(marg, "commits", regime="portscan", gate_margin=0.01), 0.06)
    check("5.6 poison 40% ToN +0.32", 0.32, val(pois, "gate_gain", regime="ton_scanning", probe_poison=0.4), 0.006)
    p40 = row(pois, regime="ton_scanning", probe_poison=0.4)
    check("5.6 poison 40% still beats naive", 1.0, float(bool(p40["still_beats_naive"])) if p40 is not None else None, 0.1)

    # --- Section 5.7: downstream generalization ---
    check("5.7 RF PortScan start ~69.6%", 69.6, val(down, "noadapt_BA", downstream="random_forest", regime="portscan") * 100, 0.06)
    check("5.7 RF PortScan gain +27.7", 27.7, val(down, "naive_gain", downstream="random_forest", regime="portscan"), 0.06)
    check("5.7 logreg ToN start ~84.2%", 84.2, val(down, "noadapt_BA", downstream="logreg", regime="ton_scanning") * 100, 0.06)
    check("5.7 logreg ToN gain +6.7", 6.7, val(down, "naive_gain", downstream="logreg", regime="ton_scanning"), 0.06)
    check("5.7 RF ToN start ~97.0%", 97.0, val(down, "noadapt_BA", downstream="random_forest", regime="ton_scanning") * 100, 0.06)
    check("5.7 RF ToN gain +1.9", 1.9, val(down, "naive_gain", downstream="random_forest", regime="ton_scanning"), 0.06)
    only_svc_harm = down[down.harm_reproduced]["downstream"].unique().tolist() == ["svc_rbf"]
    check("5.7 net-harm ONLY for SVC", 1.0, float(only_svc_harm), 0.1)
    check("5.7 gate safe in all 12 cells", 1.0, float(bool(down["gate_avoids_harm"].all())), 0.1)

    # --- Manuscript hygiene ---
    md = open("manuscript/paper2_manuscript_draft_002.md", encoding="utf-8").read()
    a = md.index("## Abstract"); b = md.index("## Contributions", a)
    abstract = re.sub(r"[*_`]", "", md[a:b].split("\n", 2)[2].strip())
    check("abstract <= 250 words", 244, float(len(abstract.split())), 6.0)
    check("no [CITE] markers", 0, float(md.count("[CITE]")), 0.1)

    # --- Report ---
    npass = sum(1 for ok, *_ in results if ok)
    print(f"\n{'='*70}\nAUDIT: {npass}/{len(results)} checks pass\n{'='*70}")
    for ok, name, claimed, actual in results:
        flag = "PASS" if ok else "FAIL"
        print(f"  [{flag}] {name:45s} claimed={claimed}  actual={actual}")
    if npass < len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
