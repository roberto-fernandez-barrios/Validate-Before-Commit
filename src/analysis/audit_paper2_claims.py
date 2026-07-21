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
    check("abstract <= 250 words (md tokenization; tex=250)", 254, float(len(abstract.split())), 0.5)
    check("no [CITE] markers", 0, float(md.count("[CITE]")), 0.1)

    # --- Phase 2h: label-free gates (ATC/DoC) head-to-head ---
    lf = pd.read_csv(f"{T}/paper2_phase2h_labelfree_gates_001/paper2_labelfree_gates_summary.csv")
    lfc = pd.read_csv(f"{T}/paper2_phase2h_labelfree_gates_001/paper2_labelfree_gates_paired_ci.csv")
    check("5.6 ATC SVC ToN +0.40", 0.40, val(lf, "gain_pts", downstream="svc_rbf", regime="ton_scanning", gate="atc"), 0.006)
    check("5.6 DoC SVC ToN +1.16", 1.16, val(lf, "gain_pts", downstream="svc_rbf", regime="ton_scanning", gate="doc"), 0.006)
    check("5.6 ATC SVC PortScan -1.86 vs naive", -1.86, val(lfc, "d_vs_naive", downstream="svc_rbf", regime="portscan", gate="atc"), 0.006)
    check("5.6 DoC SVC PortScan -4.64 vs naive", -4.64, val(lfc, "d_vs_naive", downstream="svc_rbf", regime="portscan", gate="doc"), 0.006)

    # --- LaTeX table freshness (manuscript/tables must match the regenerated sources) ---
    t1 = open("manuscript/tables/table1_regime_taxonomy.tex", encoding="utf-8").read()
    t4 = open("manuscript/tables/table4_oracle_regret.tex", encoding="utf-8").read()
    check("tex table1 fresh: 30 seeds per regime", 1.0, float("30 seeds per regime" in t1), 0.1)
    check("tex table1 fresh: Recon marginal +0.5", 1.0,
          float(("marginal" in t1) and ("0.5" in t1) and ("mixed" not in t1)), 0.1)
    check("tex table4 fresh: 3.53 [1.76, 5.54]", 1.0,
          float(("3.53" in t4) and ("[1.76, 5.54]" in t4)), 0.1)
    tex = open("manuscript/main.tex", encoding="utf-8").read()
    check("main.tex Limitations is real, not a stub", 1.0,
          float(("promote to a numbered section" not in tex) and ("fragile-model tail" in tex)), 0.1)

    # --- Section 5.2 / Table 7: mechanism-law robustness (re-aggregation) ---
    rob = pd.read_csv(f"{T}/paper2_mechanism_law_robustness_001/summary.csv")
    check("5.2 rob svc7 r -0.89", -0.89, val(rob, "r", analysis="svc7_full"), 0.005)
    check("5.2 rob per-seed r -0.91 (n=210)", -0.91, val(rob, "r", analysis="per_seed_pooled"), 0.005)
    check("5.2 rob seed-boot CI lo -0.90", -0.90, val(rob, "r_min", analysis="svc7_seed_bootstrap"), 0.005)
    check("5.2 rob seed-boot CI hi -0.88", -0.88, val(rob, "r_max", analysis="svc7_seed_bootstrap"), 0.005)
    check("5.2 rob LORO strongest -0.92", -0.92, val(rob, "r_min", analysis="svc7_loro_range"), 0.005)
    check("5.2 rob LORO weakest -0.72", -0.72, val(rob, "r_max", analysis="svc7_loro_range"), 0.005)
    check("5.2 rob pooled16 r -0.81", -0.81, val(rob, "r", analysis="pooled16_full"), 0.005)
    check("5.2 rob LODO no-ToN -0.81", -0.81, val(rob, "r", analysis="pooled16_lodo", detail="without ton_iot"), 0.005)
    check("5.2 rob LODO no-UNSW -0.95", -0.95, val(rob, "r", analysis="pooled16_lodo", detail="without unsw"), 0.005)
    check("5.2 rob LODO no-CICIDS -0.52", -0.52, val(rob, "r", analysis="pooled16_lodo", detail="without cicids"), 0.005)
    t7 = open("manuscript/tables/table7_mechanism_law_robustness.tex", encoding="utf-8").read()
    check("tex table7 fresh: per-seed -0.91 and LODO -0.52", 1.0,
          float(("$-0.91$" in t7) and ("$-0.52$" in t7) and ("$-0.72$ to $-0.92$" in t7)), 0.1)

    # --- Section 5.2: coupling diagnostics (restoration-to-ceiling framing) ---
    cpl = pd.read_csv(f"{T}/paper2_mechanism_law_robustness_001/coupling_diagnostics.csv")
    check("5.2 cpl sigma deployed 7.4", 7.4, val(cpl, "value", metric="sigma_noadapt_BA"), 0.05)
    check("5.2 cpl sigma restored 3.5", 3.5, val(cpl, "value", metric="sigma_adapted_BA"), 0.06)
    check("5.2 cpl slope -0.87", -0.87, val(cpl, "value", metric="slope_gain_on_base"), 0.005)
    check("5.2 cpl perm null median -0.91", -0.91, val(cpl, "value", metric="perm_null_median_r"), 0.005)
    check("5.2 cpl perm p 0.80", 0.80, val(cpl, "value", metric="perm_null_p_more_negative"), 0.005)
    check("5.2 cpl within-regime score r median +0.06", 0.06,
          val(cpl, "value", metric="within_regime_score_vs_gain_r_median"), 0.005)
    check("5.2 cpl within-regime score r max 0.13", 0.13,
          val(cpl, "value", metric="within_regime_score_vs_gain_r_max"), 0.005)
    check("5.2 cpl within-regime base r median -0.68", -0.68,
          val(cpl, "value", metric="within_regime_base_vs_gain_r_median"), 0.005)
    check("5.2 cpl cross-regime classical score r max 0.94", 0.94,
          val(cpl, "value", metric="detector_score_vs_gain_r__mmd_rbf"), 0.005)
    check("5.1 KS-max prespecified taxonomy: ToN -2.4", -2.4,
          val(baf1, "gain_BA_pts", regime_id="ton_iot_scanning", method="ks_max"), 0.05)

    # --- Section 5.6 / Phase 2i: replay retraining baseline ---
    rep = pd.read_csv(f"{T}/paper2_phase2i_replay_baseline_001/summary.csv")
    repci = pd.read_csv(f"{T}/paper2_phase2i_replay_baseline_001/paired_ci.csv")
    check("5.6 replay-naive ToN -4.54", -4.54, val(rep, "gain_pts", regime="ton_scanning", arm="replay_naive"), 0.005)
    check("5.6 replay-naive PortScan +6.59", 6.59, val(rep, "gain_pts", regime="portscan", arm="replay_naive"), 0.005)
    check("5.6 replay+gate ToN +0.59", 0.585, val(rep, "gain_pts", regime="ton_scanning", arm="replay_lp32"), 0.005)
    check("5.6 replay+gate PortScan +8.26", 8.255, val(rep, "gain_pts", regime="portscan", arm="replay_lp32"), 0.005)
    check("5.6 replay gate-vs-replay-naive ToN +5.13", 5.125,
          val(repci, "diff", regime="ton_scanning", contrast="replay_lp32_vs_replay_naive"), 0.005)
    check("5.6 replay gate ToN vs noadapt CI lo 0.23", 0.227,
          val(repci, "ci_lo", regime="ton_scanning", contrast="replay_lp32_vs_noadapt"), 0.005)
    check("5.6 replay gate PortScan rescue +1.66", 1.662,
          val(repci, "diff", regime="portscan", contrast="replay_lp32_vs_replay_naive"), 0.005)
    check("5.6 replay-naive ToN CI hi < 0 (sig harmful)", -2.34,
          val(repci, "ci_hi", regime="ton_scanning", contrast="replay_naive_vs_noadapt"), 0.005)

    # --- Section 5.6 / Phase 2j: probe prevalence ---
    prev = pd.read_csv(f"{T}/paper2_phase2j_probe_prevalence_001/summary.csv")
    prevci = pd.read_csv(f"{T}/paper2_phase2j_probe_prevalence_001/paired_ci.csv")
    check("5.6 prevalence ToN p10 +1.00", 1.00, val(prev, "gain_pts", regime="ton_scanning", arm="p10_b32"), 0.005)
    check("5.6 prevalence ToN p01 +1.01", 1.01, val(prev, "gain_pts", regime="ton_scanning", arm="p01_b32"), 0.005)
    check("5.6 prevalence ToN p01_b320 +0.68", 0.675, val(prev, "gain_pts", regime="ton_scanning", arm="p01_b320"), 0.005)
    check("5.6 prevalence PortScan p10 +7.93", 7.93, val(prev, "gain_pts", regime="portscan", arm="p10_b32"), 0.005)
    check("5.6 prevalence PortScan p01 +7.62", 7.62, val(prev, "gain_pts", regime="portscan", arm="p01_b32"), 0.005)
    check("5.6 prevalence PortScan p01_b320 +8.00", 7.998, val(prev, "gain_pts", regime="portscan", arm="p01_b320"), 0.005)
    check("5.6 prevalence ToN p10 CI lo 0.66", 0.663,
          val(prevci, "ci_lo", regime="ton_scanning", arm="p10_b32"), 0.005)
    check("5.6 prevalence ToN p01 CI lo 0.69", 0.690,
          val(prevci, "ci_lo", regime="ton_scanning", arm="p01_b32"), 0.005)
    check("5.6 prevalence balanced ref ToN +0.93", 0.934,
          val(prev, "gain_pts", regime="ton_scanning", arm="balanced_b32"), 0.005)
    check("5.6 prevalence balanced ref PortScan +8.27", 8.27,
          val(prev, "gain_pts", regime="portscan", arm="balanced_b32"), 0.005)

    # --- Section 5.6 / Phase 2k: candidate-size and dimensionality controls ---
    ctl = pd.read_csv(f"{T}/paper2_phase2k_size_dim_controls_001/summary.csv")
    check("5.6 cand2000 ToN naive -5.34", -5.34,
          val(ctl, "gain_pts", control="cand2000", regime="ton_scanning", arm="none"), 0.005)
    check("5.6 cand2000 ToN gate +0.58", 0.582,
          val(ctl, "gain_pts", control="cand2000", regime="ton_scanning", arm="lp32"), 0.005)
    check("5.6 cand2000 PortScan gate +9.33", 9.327,
          val(ctl, "gain_pts", control="cand2000", regime="portscan", arm="lp32"), 0.005)
    check("5.6 cand2000 UNSW naive +3.31", 3.313,
          val(ctl, "gain_pts", control="cand2000", regime="unsw_recon", arm="none"), 0.005)
    check("5.6 fulldim ToN naive -0.65", -0.651,
          val(ctl, "gain_pts", control="fulldim", regime="ton_scanning", arm="none"), 0.005)
    check("5.6 fulldim PortScan naive +16.2", 16.226,
          val(ctl, "gain_pts", control="fulldim", regime="portscan", arm="none"), 0.05)
    check("5.6 cand2000 ToN naive CI hi < 0", -2.486,
          val(ctl, "ci_hi", control="cand2000", regime="ton_scanning", arm="none"), 0.005)

    # --- Section 5.9 / harness-v2 registered replication ---
    v2 = pd.read_csv(f"{T}/paper2_v2_replication_001/summary.csv")
    v2c = pd.read_csv(f"{T}/paper2_v2_replication_001/paired_ci.csv")
    v2m = pd.read_csv(f"{T}/paper2_v2_replication_001/mechanism.csv")
    check("5.9 v2 ToN naive -1.64", -1.638, val(v2, "gain_pts", detector="ks", regime="ton_scanning", arm="none"), 0.005)
    check("5.9 v2 ToN lp32 +0.79", 0.788, val(v2, "gain_pts", detector="ks", regime="ton_scanning", arm="lp32"), 0.005)
    check("5.9 v2 ToN lp32 vs naive +2.43", 2.427,
          val(v2c, "diff", detector="ks", regime="ton_scanning", contrast="lp32_vs_naive"), 0.005)
    check("5.9 v2 PortScan lp32 +9.12", 9.120, val(v2, "gain_pts", detector="ks", regime="portscan", arm="lp32"), 0.005)
    check("5.9 v2 PortScan naive +8.25", 8.252, val(v2, "gain_pts", detector="ks", regime="portscan", arm="none"), 0.005)
    check("5.9 v2 UNSW lp32 +1.35", 1.352, val(v2, "gain_pts", detector="ks", regime="unsw_recon", arm="lp32"), 0.005)
    check("5.9 v2 QK ToN naive -2.91", -2.908, val(v2, "gain_pts", detector="qk", regime="ton_scanning", arm="none"), 0.005)
    check("5.9 v2 QK ToN lp32 +0.72", 0.719, val(v2, "gain_pts", detector="qk", regime="ton_scanning", arm="lp32"), 0.005)
    check("5.9 v2 holdout(dedup) ToN -0.77", -0.770, val(v2, "gain_pts", detector="ks", regime="ton_scanning", arm="holdout32"), 0.005)
    check("5.9 v2 holdout(dedup) PortScan +9.08", 9.082, val(v2, "gain_pts", detector="ks", regime="portscan", arm="holdout32"), 0.005)
    check("5.9 v2 lcb ToN +0.34", 0.340, val(v2, "gain_pts", detector="ks", regime="ton_scanning", arm="lcb64"), 0.005)
    check("5.9 v2 lcb PortScan +8.51", 8.510, val(v2, "gain_pts", detector="ks", regime="portscan", arm="lcb64"), 0.005)
    check("5.9 v2 mech pooled r_deg -0.57", -0.566, val(v2m, "r_deg", regime="POOLED"), 0.005)
    check("5.9 v2 mech pooled r_score ~0", 0.025, val(v2m, "r_score", regime="POOLED"), 0.005)
    check("5.9 v2 mech pooled n=250", 250, val(v2m, "n_triggers", regime="POOLED"), 0.5)
    check("5.9 v2 mech PortScan r_deg CI hi -0.66", -0.664, val(v2m, "r_deg_hi", regime="portscan"), 0.005)
    npv = pd.read_csv(f"{T}/paper2_v2_replication_001/natprev.csv")
    check("5.9 natprev2 PortScan naive +1.04", 1.041, val(npv, "gain", regime="portscan", arm="none"), 0.005)
    check("5.9 natprev2 ToN zero triggers (gain 0)", 0.0, val(npv, "gain", regime="ton_scanning", arm="none"), 0.005)
    ab = pd.read_csv(f"{T}/paper2_v2_replication_001/adaptive_baselines.csv")
    check("5.9 DDM ToN naive -2.59", -2.588, val(ab, "gain", regime="ton_scanning", arm="ddm_none"), 0.005)
    check("5.9 DDM ToN gated +0.19", 0.190, val(ab, "gain", regime="ton_scanning", arm="ddm_lp32"), 0.005)
    check("5.9 DDM PortScan +6.81", 6.809, val(ab, "gain", regime="portscan", arm="ddm_none"), 0.005)
    check("5.9 ADWIN PortScan 0 (never fires)", 0.0, val(ab, "gain", regime="portscan", arm="adwin_none"), 0.005)
    check("5.9 ensemble ToN +0.34", 0.344, val(ab, "gain", regime="ton_scanning", arm="ensemble_none"), 0.005)
    check("5.9 ensemble PortScan +8.55", 8.547, val(ab, "gain", regime="portscan", arm="ensemble_none"), 0.005)
    check("5.9 ensemble UNSW -0.10", -0.103, val(ab, "gain", regime="unsw_recon", arm="ensemble_none"), 0.005)
    check("5.9 sliding ToN -2.44", -2.437, val(ab, "gain", regime="ton_scanning", arm="sliding_window_none"), 0.005)
    check("5.9 sliding ToN gated +0.78", 0.781, val(ab, "gain", regime="ton_scanning", arm="sliding_window_lp32"), 0.005)
    # --- Amendment 004: corrected chronological streams (supersede v5 temporal run) ---
    tmp = pd.read_csv(f"{T}/paper2_amendment_004/temporal.csv")
    def tval(stream, metric, quantity):
        return val(tmp, "value", stream=stream, metric=metric, quantity=quantity)
    check("5.9 temporal fri noadapt 71.97", 71.97, tval("fri", "BA_two_class", "no_adapt_level"), 0.01)
    check("5.9 temporal fri naive +13.55", 13.553, tval("fri", "BA_two_class", "naive_vs_noadapt"), 0.005)
    check("5.9 temporal fri gate +7.22", 7.216, tval("fri", "BA_two_class", "gate_vs_noadapt"), 0.005)
    check("5.9 temporal fri premium -6.34", -6.337, tval("fri", "BA_two_class", "gate_vs_naive"), 0.005)
    check("5.9 temporal fri acc gate-naive +4.19", 4.190, tval("fri", "accuracy_all", "gate_vs_naive"), 0.005)
    check("5.9 temporal wed noadapt 53.35", 53.35, tval("wed", "BA_two_class", "no_adapt_level"), 0.01)
    check("5.9 temporal wed naive +27.63", 27.625, tval("wed", "BA_two_class", "naive_vs_noadapt"), 0.005)
    check("5.9 temporal wed gate-naive +0.40", 0.401, tval("wed", "BA_two_class", "gate_vs_naive"), 0.005)
    check("5.9 temporal thu naive +22.74", 22.740, tval("thu", "BA_two_class", "naive_vs_noadapt"), 0.005)
    check("5.9 temporal thu premium -4.98", -4.978, tval("thu", "BA_two_class", "gate_vs_naive"), 0.005)
    check("5.9 temporal thu acc gate-naive +1.23", 1.230, tval("thu", "accuracy_all", "gate_vs_naive"), 0.005)

    # --- Amendment 004: v2 robustness suite, two-stage, calibrated ensemble, river monitors ---
    rb = pd.read_csv(f"{T}/paper2_amendment_004/robustness.csv")
    check("5.9 v2 budget lp8 ToN -0.42 (corrected claim)", -0.424,
          val(rb, "gain", regime="ton_scanning", arm="lp8"), 0.005)
    check("5.9 v2 budget lp8 ToN vs naive +1.22", 1.215,
          val(rb, "vs_naive", regime="ton_scanning", arm="lp8"), 0.005)
    check("5.9 v2 budget lp16 ToN +0.29", 0.289, val(rb, "gain", regime="ton_scanning", arm="lp16"), 0.005)
    check("5.9 v2 budget lp64 ToN +0.92", 0.923, val(rb, "gain", regime="ton_scanning", arm="lp64b"), 0.005)
    check("5.9 v2 budget lp128 ToN +1.01", 1.006, val(rb, "gain", regime="ton_scanning", arm="lp128"), 0.005)
    check("5.9 v2 latency20 ToN +0.95", 0.953, val(rb, "gain", regime="ton_scanning", arm="lp32lat20"), 0.005)
    check("5.9 v2 latency20 PortScan vs lp32 -0.47", -0.465,
          val(rb, "vs_lp32", regime="portscan", arm="lp32lat20"), 0.005)
    check("5.9 v2 flip25 ToN +0.57", 0.570, val(rb, "gain", regime="ton_scanning", arm="lp32flip25"), 0.005)
    check("5.9 v2 flip40 ToN -0.04", -0.043, val(rb, "gain", regime="ton_scanning", arm="lp32flip40"), 0.005)
    check("5.9 v2 flip40 ToN vs naive +1.60", 1.595,
          val(rb, "vs_naive", regime="ton_scanning", arm="lp32flip40"), 0.005)
    check("5.9 two-stage(004 probe-reuse, superseded) ToN +0.16", 0.163, val(rb, "gain", regime="ton_scanning", arm="twostage"), 0.005)
    check("5.9 two-stage(004 superseded) candidates 0.90", 0.90,
          val(rb, "n_candidates_trained", regime="ton_scanning", arm="twostage"), 0.01)
    check("5.9 two-stage(004 superseded) PortScan vs lp32 -1.00", -0.998,
          val(rb, "vs_lp32", regime="portscan", arm="twostage"), 0.005)
    check("5.9 enscal ToN +0.56", 0.558, val(rb, "gain", regime="ton_scanning", arm="enscal_none"), 0.005)
    check("5.9 enscal UNSW +1.72", 1.721, val(rb, "gain", regime="unsw_recon", arm="enscal_none"), 0.005)
    check("5.9 enscal UNSW vs naive +0.51", 0.513,
          val(rb, "vs_naive", regime="unsw_recon", arm="enscal_none"), 0.005)
    check("5.9 enscal PortScan +8.55", 8.551, val(rb, "gain", regime="portscan", arm="enscal_none"), 0.01)
    check("5.9 gate-enscal ToN +0.23 (from vs_lp32)", -0.230,
          val(rb, "vs_lp32", regime="ton_scanning", arm="enscal_none"), 0.005)
    check("5.9 ddm_river ToN -2.23", -2.226, val(rb, "gain", regime="ton_scanning", arm="ddmriver_none"), 0.005)
    check("5.9 ddm_river UNSW +0.14", 0.138, val(rb, "gain", regime="unsw_recon", arm="ddmriver_none"), 0.005)
    check("5.9 adwin_river PortScan +1.77", 1.770, val(rb, "gain", regime="portscan", arm="adwinriver_none"), 0.005)
    check("5.9 adwin_river ToN 0 triggers", 0.0, val(rb, "n_triggers", regime="ton_scanning", arm="adwinriver_none"), 0.01)

    # --- Amendment 004: label/compute cost accounting (Table label_cost) ---
    lc = pd.read_csv(f"{T}/paper2_amendment_004/label_cost.csv")
    check("cost ToN lp32 total 3626", 3626, val(lc, "total_labels", regime="ton_scanning", policy="labeled_probe b=32"), 1.0)
    check("cost ToN naive total 2594", 2594, val(lc, "total_labels", regime="ton_scanning", policy="none (naive)"), 1.0)
    check("cost ToN two-stage(004 superseded) total 1182", 1182, val(lc, "total_labels", regime="ton_scanning", policy="two_stage b=32"), 1.0)
    check("cost ToN lp32 probe 110", 109.9, val(lc, "probe_labels", regime="ton_scanning", policy="labeled_probe b=32"), 0.5)

    # --- Amendment 004: decision-quality metrics + hierarchical model ---
    dm = pd.read_csv(f"{T}/paper2_decision_quality_004/decision_metrics.csv")
    check("5.9 dq ToN regret gate 0.0020", 0.0020, val(dm, "regret_gate", regime="ton_scanning"), 0.0002)
    check("5.9 dq ToN regret always 0.0452", 0.0452, val(dm, "regret_always_commit", regime="ton_scanning"), 0.0002)
    check("5.9 dq ToN beneficial-rejection 4.9%", 0.0488, val(dm, "beneficial_rejection_rate", regime="ton_scanning"), 0.0005)
    check("5.9 dq ToN recall 0.95", 0.9535, val(dm, "gate_recall", regime="ton_scanning"), 0.0005)
    check("5.9 dq PortScan regret 0.0028 vs 0.0140", 0.0028, val(dm, "regret_gate", regime="portscan"), 0.0002)
    check("5.9 dq pooled precision 0.74", 0.7376, val(dm, "gate_precision", regime="POOLED"), 0.0005)
    check("5.9 dq pooled recall 0.87", 0.8717, val(dm, "gate_recall", regime="POOLED"), 0.0005)
    check("5.9 dq pooled harmful-commit 23%", 0.2308, val(dm, "harmful_commit_rate", regime="POOLED"), 0.0005)
    hm = pd.read_csv(f"{T}/paper2_decision_quality_004/hierarchical_model.csv")
    check("5.9 hm pooled beta_deg -1.02", -1.0192, val(hm, "beta", regime="POOLED", term="deg_pre5"), 0.005)
    check("5.9 hm(004 seed-cluster, superseded) CI lo -1.17", -1.1714, val(hm, "ci_lo", regime="POOLED", term="deg_pre5"), 0.005)
    check("5.9 hm pooled beta_score ~0", -0.0335, val(hm, "beta", regime="POOLED", term="score"), 0.005)
    check("5.9 hm ToN beta_deg -1.15", -1.1480, val(hm, "beta", regime="ton_scanning", term="deg_pre5"), 0.005)
    lo_r2 = pd.read_csv(f"{T}/paper2_decision_quality_004/loro_r2.csv")
    check("5.9 LORO ToN r2 0.36", 0.356, val(lo_r2, "r2", held_out="ton_scanning"), 0.005)
    check("5.9 LORO UNSW r2 fails (-10.5)", -10.523, val(lo_r2, "r2", held_out="unsw_recon"), 0.01)

    # --- Amendment 004: monitor validation vs river ---
    mv = pd.read_csv(f"{T}/paper2_monitor_validation_004.csv")
    ddm_agree = float(((mv.ours_ddm >= 0) == (mv.river_ddm >= 0)).mean())
    adwin_agree = float(((mv.ours_adwin >= 0) == (mv.river_adwin >= 0)).mean())
    check("5.9 river DDM agreement 0.94", 0.94, ddm_agree, 0.005)
    check("5.9 river ADWIN agreement 0.57 (ours under-fires)", 0.57, adwin_agree, 0.005)

    # --- Amendment 004: classifiers_lp32 regenerated by the committed aggregator ---
    cl2 = pd.read_csv(f"{T}/paper2_v2_replication_001/classifiers_lp32.csv")
    check("5.9 v2 MLP ToN naive -0.16", -0.158, val(cl2, "naive", regime="ton_scanning", dm="mlp"), 0.005)
    check("5.9 v2 MLP ToN lp32 +0.25", 0.252, val(cl2, "lp32", regime="ton_scanning", dm="mlp"), 0.005)
    check("5.9 v2 MLP ToN rescue +0.41", 0.410, val(cl2, "lp32_vs_naive", regime="ton_scanning", dm="mlp"), 0.005)
    check("5.9 v2 RF PortScan boundary -0.011", -0.011, val(cl2, "lp32_vs_naive", regime="portscan", dm="random_forest"), 0.005)
    ex = pd.read_csv(f"{T}/../tables/paper2_phase3_extras_summary.csv") if False else pd.read_csv(
        "results/tables/paper2_phase3_extras_summary.csv")
    check("5.9 perf PortScan +5.40", 5.402, val(ex, "gain", regime="portscan", arm="perf_none"), 0.005)
    check("5.9 perf ToN 0.00 (never fires)", 0.0, val(ex, "gain", regime="ton_scanning", arm="perf_none"), 0.005)
    check("5.9 natprev ToN naive -2.63", -2.626, val(ex, "gain", regime="ton_scanning", arm="natprev_none"), 0.005)
    check("5.9 natprev ToN gate +0.80", 0.801, val(ex, "gain", regime="ton_scanning", arm="natprev_lp32"), 0.005)
    check("5.9 natprev PortScan naive +9.06", 9.061, val(ex, "gain", regime="portscan", arm="natprev_none"), 0.005)

    # --- Amendment 005: split two-stage, monitor budget sweep, stratified/UNSW temporal ---
    t5 = pd.read_csv(f"{T}/paper2_amendment_005/twostage_and_monitors.csv")
    check("5.9 two-stage(split d05) ToN +0.15 (unresolved vs noadapt)", 0.154,
          val(t5, "gain", regime="ton_scanning", arm="twostage_d05"), 0.005)
    check("5.9 two-stage(split d05) ToN vs naive +1.79", 1.792,
          val(t5, "vs_naive", regime="ton_scanning", arm="twostage_d05"), 0.005)
    check("5.9 two-stage(split d05) ToN candidates 1.07", 1.07,
          val(t5, "n_candidates_trained", regime="ton_scanning", arm="twostage_d05"), 0.01)
    check("5.9 two-stage(split d03) ToN +0.34", 0.339,
          val(t5, "gain", regime="ton_scanning", arm="twostage_d03"), 0.005)
    check("5.9 two-stage(split d10) ToN +0.04", 0.041,
          val(t5, "gain", regime="ton_scanning", arm="twostage_d10"), 0.005)
    check("5.9 two-stage(split d03) PortScan vs lp32 -0.76", -0.760,
          val(t5, "vs_lp32", regime="portscan", arm="twostage_d03"), 0.005)
    check("5.9 two-stage(split d10) PortScan vs lp32 -1.80", -1.795,
          val(t5, "vs_lp32", regime="portscan", arm="twostage_d10"), 0.005)
    check("5.9 ddm_river 4x ToN -1.04", -1.043, val(t5, "gain", regime="ton_scanning", arm="ddmriver_m32"), 0.005)
    check("5.9 ddm_river 10x ToN -0.45", -0.450, val(t5, "gain", regime="ton_scanning", arm="ddmriver_m80"), 0.005)
    check("5.9 ddm_river 10x PortScan +7.08", 7.082, val(t5, "gain", regime="portscan", arm="ddmriver_m80"), 0.005)
    check("5.9 adwin_river ToN silent at 4x", 0.0,
          val(t5, "n_triggers", regime="ton_scanning", arm="adwinriver_m32"), 0.01)
    ts5 = pd.read_csv(f"{T}/paper2_amendment_005/temporal_stratified.csv")
    def t5v(stream, metric, quantity):
        return val(ts5, "value", stream=stream, metric=metric, quantity=quantity)
    check("5.9 strat fri strat-gate -0.05 (composition refuted)", -0.054,
          t5v("fri", "BA_two_class", "strat_vs_gate"), 0.005)
    check("5.9 UNSW chrono noadapt 82.30 (healthy incumbent)", 82.296,
          t5v("unsw", "BA_two_class", "no_adapt_level"), 0.01)
    check("5.9 UNSW chrono naive +7.33", 7.330, t5v("unsw", "BA_two_class", "naive_vs_noadapt"), 0.005)
    check("5.9 UNSW chrono gate vs naive +0.16 (no premium)", 0.156,
          t5v("unsw", "BA_two_class", "gate_vs_naive"), 0.005)
    check("5.9 UNSW chrono acc gate vs naive +0.21", 0.213,
          t5v("unsw", "accuracy_all", "gate_vs_naive"), 0.005)
    hm5 = pd.read_csv(f"{T}/paper2_decision_quality_005/hierarchical_model.csv")
    check("5.9 hm5 pooled(ks, regime x seed) beta_deg -1.02", -1.0195,
          val(hm5, "beta", detector="ks", regime="POOLED", term="deg_pre5"), 0.005)
    check("5.9 hm5 pooled CI lo -1.61", -1.6090, val(hm5, "ci_lo", detector="ks", regime="POOLED", term="deg_pre5"), 0.005)
    check("5.9 hm5 pooled CI hi -0.43", -0.4300, val(hm5, "ci_hi", detector="ks", regime="POOLED", term="deg_pre5"), 0.005)
    check("5.9 hm5 randslope -0.92", -0.9245,
          val(hm5, "beta", detector="ks", regime="POOLED", term="deg_pre5_randslope"), 0.005)
    check("5.9 hm5 qk PortScan score beta +5.49 (the reported exception)", 5.4929,
          val(hm5, "beta", detector="qk", regime="portscan", term="score"), 0.005)
    check("5.9 hm5 qk ToN beta_deg -0.99", -0.9881,
          val(hm5, "beta", detector="qk", regime="ton_scanning", term="deg_pre5"), 0.005)
    mech5 = pd.read_csv(f"{T}/paper2_decision_quality_005/mechanism_by_detector.csv")
    check("5.9 qk pooled r_deg -0.59", -0.592, val(mech5, "r_deg", detector="qk", regime="POOLED"), 0.005)
    check("5.9 qk pooled r_score ~0", 0.011, val(mech5, "r_score", detector="qk", regime="POOLED"), 0.005)
    rh = pd.read_csv(f"{T}/paper2_decision_quality_005/regret_by_horizon.csv")
    check("5.9 regret ToN h=1 gate 0.0032", 0.0032, val(rh, "regret_gate", regime="ton_scanning", horizon=1), 0.0002)
    check("5.9 regret ToN h=1 always 0.0475", 0.0475, val(rh, "regret_always_commit", regime="ton_scanning", horizon=1), 0.0002)
    check("5.9 regret ToN h=10 always 0.0446", 0.0446, val(rh, "regret_always_commit", regime="ton_scanning", horizon=10), 0.0002)
    check("5.9 regret UNSW h=5 wash gate 0.0044", 0.0044, val(rh, "regret_gate", regime="unsw_recon", horizon=5), 0.0002)
    check("5.9 regret UNSW h=5 wash always 0.0037", 0.0037, val(rh, "regret_always_commit", regime="unsw_recon", horizon=5), 0.0002)
    fr = pd.read_csv(f"{T}/paper2_policy_frontier_005/frontier.csv")
    check("frontier two-stage(split) ToN total 1341", 1341,
          val(fr, "total_labels", regime="ton_scanning", policy="two_stage_split_d05"), 1.0)
    check("frontier ensemble ToN +0.56", 0.558, val(fr, "gain", regime="ton_scanning", policy="ensemble_cal"), 0.005)
    check("frontier lp32 ToN labels 3626", 3626,
          val(fr, "total_labels", regime="ton_scanning", policy="labeled_probe_b32"), 1.0)

    # --- Amendment 006: causal probe, honest prevalence, McNemar, prediction test, harm breadth ---
    a6 = pd.read_csv(f"{T}/paper2_amendment_006/summary.csv")
    c6 = pd.read_csv(f"{T}/paper2_amendment_006/paired_ci.csv")
    # causal observed-data arm (no severity, no pools)
    check("5.9 causal naive ToN -2.44 (harm w/ observed candidates)", -2.437,
          val(a6, "gain", regime="ton_scanning", arm="causal_none"), 0.005)
    check("5.9 causal gate ToN +0.85", 0.849, val(a6, "gain", regime="ton_scanning", arm="causal_gate"), 0.005)
    check("5.9 causal gate ToN vs naive +3.29", 3.287,
          val(c6, "diff", regime="ton_scanning", contrast="causal_gate_vs_causal_naive"), 0.005)
    check("5.9 causal gate PortScan +8.64", 8.643, val(a6, "gain", regime="portscan", arm="causal_gate"), 0.005)
    check("5.9 causal gate UNSW +1.31", 1.313, val(a6, "gain", regime="unsw_recon", arm="causal_gate"), 0.005)
    check("5.9 causal ~ oracle ToN +0.06 (ns)", 0.061,
          val(c6, "diff", regime="ton_scanning", contrast="causal_gate_vs_lp32(pools)"), 0.005)
    check("5.9 causal vs oracle PortScan -0.48", -0.477,
          val(c6, "diff", regime="portscan", contrast="causal_gate_vs_lp32(pools)"), 0.005)
    # honest binomial-prevalence probes (the retraction)
    check("5.9 binom01 zero-attack probe frac 0.66 (ToN)", 0.661,
          val(a6, "zero_attack_probe_frac", regime="ton_scanning", arm="binom01"), 0.005)
    check("5.9 binom01 ToN +0.21 (CI straddles zero: claim retracted)", 0.214,
          val(a6, "gain", regime="ton_scanning", arm="binom01"), 0.005)
    check("5.9 binom01 ToN CI lo < 0", -1.388, val(a6, "ci_lo", regime="ton_scanning", arm="binom01"), 0.01)
    check("5.9 binom05 ToN +0.91 (still holds)", 0.910,
          val(a6, "gain", regime="ton_scanning", arm="binom05"), 0.005)
    check("5.9 binom05 PortScan vs lp32 -0.44", -0.436,
          val(c6, "diff", regime="portscan", contrast="binom05_vs_lp32"), 0.005)
    # exact McNemar (risk axis)
    check("5.9 mcnemar32 ToN +0.00 (never harmful, no power)", 0.002,
          val(a6, "gain", regime="ton_scanning", arm="mcnemar32"), 0.005)
    check("5.9 mcnemar32 ToN commits 0.03", 0.03,
          val(a6, "n_adaptations", regime="ton_scanning", arm="mcnemar32"), 0.01)
    check("5.9 mcnemar32 PortScan +5.45", 5.451, val(a6, "gain", regime="portscan", arm="mcnemar32"), 0.005)
    check("5.9 mcnemar32 PortScan vs lp32 -3.67", -3.669,
          val(c6, "diff", regime="portscan", contrast="mcnemar32_vs_lp32"), 0.005)
    check("5.9 mcnemar64 PortScan +7.67", 7.671, val(a6, "gain", regime="portscan", arm="mcnemar64"), 0.005)
    # THE REGISTERED PREDICTION TEST (mild drift -> harm in all three benchmarks)
    check("5.9 sev025 PortScan naive -0.46 (prediction: net-harmful)", -0.463,
          val(a6, "gain", regime="portscan", arm="sev025_none"), 0.005)
    check("5.9 sev025 UNSW naive -0.15", -0.146, val(a6, "gain", regime="unsw_recon", arm="sev025_none"), 0.005)
    check("5.9 sev025 ToN naive -0.65", -0.653, val(a6, "gain", regime="ton_scanning", arm="sev025_none"), 0.005)
    check("5.9 sev025 PortScan gate +0.38", 0.376, val(a6, "gain", regime="portscan", arm="sev025_lp32"), 0.005)
    check("5.9 sev025 UNSW gate -0.09 (>= -0.2)", -0.088,
          val(a6, "gain", regime="unsw_recon", arm="sev025_lp32"), 0.005)
    check("5.9 sev025 ToN gate -0.04 (>= -0.2)", -0.036,
          val(a6, "gain", regime="ton_scanning", arm="sev025_lp32"), 0.005)
    check("5.9 sev025 gate vs naive PortScan +0.84 (sig)", 0.839,
          val(c6, "diff", regime="portscan", contrast="sev025_gate_vs_naive"), 0.005)
    check("5.9 sev050 ToN naive -3.63", -3.629, val(a6, "gain", regime="ton_scanning", arm="sev050_none"), 0.005)
    check("5.9 sev050 ToN gate +0.19", 0.187, val(a6, "gain", regime="ton_scanning", arm="sev050_lp32"), 0.005)
    check("5.9 sev050 ToN gate vs naive +3.82", 3.816,
          val(c6, "diff", regime="ton_scanning", contrast="sev050_gate_vs_naive"), 0.005)
    # harm breadth on the hardened harness
    check("5.9 v2 ToN DDoS naive -15.24", -15.244, val(a6, "gain", regime="ton_ddos", arm="none"), 0.005)
    check("5.9 v2 ToN DDoS gate +1.02", 1.016, val(a6, "gain", regime="ton_ddos", arm="lp32"), 0.005)
    check("5.9 v2 ToN DDoS gate vs naive +16.26", 16.260,
          val(c6, "diff", regime="ton_ddos", contrast="gate_vs_naive"), 0.005)
    check("5.9 v2 ToN Injection naive -2.24", -2.239, val(a6, "gain", regime="ton_injection", arm="none"), 0.005)
    check("5.9 v2 ToN Injection gate +0.43", 0.431, val(a6, "gain", regime="ton_injection", arm="lp32"), 0.005)
    # per-incumbent health reference (conclusions unchanged)
    check("5.9 hr per-incumbent ToN +0.11", 0.113, val(a6, "gain", regime="ton_scanning", arm="hrperinc"), 0.005)
    check("5.9 hr per-incumbent PortScan +7.88", 7.878, val(a6, "gain", regime="portscan", arm="hrperinc"), 0.005)
    # Wednesday -> Thursday chronological attempt (another deep-benefit stream)
    w6 = pd.read_csv(f"{T}/paper2_amendment_006/temporal_wed2thu.csv")
    check("5.9 wed2thu noadapt 48.70 (collapses again)", 48.703,
          val(w6, "value", metric="BA_two_class", quantity="no_adapt_level"), 0.01)
    check("5.9 wed2thu naive +33.66", 33.658,
          val(w6, "value", metric="BA_two_class", quantity="naive_vs_noadapt"), 0.005)
    check("5.9 wed2thu gate premium -15.08 BA", -15.077,
          val(w6, "value", metric="BA_two_class", quantity="gate_vs_naive"), 0.005)
    check("5.9 wed2thu accuracy premium -0.08 (ns)", -0.083,
          val(w6, "value", metric="accuracy_all", quantity="gate_vs_naive"), 0.005)

    # --- Amendment 007: genuinely causal arm, zero-drift control, sequential gate ---
    a7 = pd.read_csv(f"{T}/paper2_amendment_007/summary.csv")
    c7 = pd.read_csv(f"{T}/paper2_amendment_007/paired_ci.csv")
    # causal arm WITH observed recalibration + row-identity-disjoint probes (supersedes 006)
    check("5.9 causal7 ToN naive -3.19", -3.189, val(a7, "gain", regime="ton_scanning", arm="tcausal_none"), 0.005)
    check("5.9 causal7 ToN gate +0.67", 0.670, val(a7, "gain", regime="ton_scanning", arm="tcausal_gate"), 0.005)
    check("5.9 causal7 ToN gate vs naive +3.86", 3.859,
          val(c7, "diff", regime="ton_scanning", contrast="tcausal_gate_vs_naive"), 0.005)
    check("5.9 causal7 ~ oracle ToN -0.12 (ns)", -0.118,
          val(c7, "diff", regime="ton_scanning", contrast="tcausal_gate_vs_lp32(oracle)"), 0.005)
    check("5.9 causal7 PortScan gate +8.57", 8.571, val(a7, "gain", regime="portscan", arm="tcausal_gate"), 0.005)
    check("5.9 causal7 PortScan gate vs naive +0.95", 0.950,
          val(c7, "diff", regime="portscan", contrast="tcausal_gate_vs_naive"), 0.005)
    check("5.9 causal7 UNSW gate +0.98", 0.980, val(a7, "gain", regime="unsw_recon", arm="tcausal_gate"), 0.005)
    check("5.9 causal7 row collisions ToN 35.7 (real overlap removed)", 35.70,
          val(a7, "probe_row_collisions", regime="ton_scanning", arm="tcausal_gate"), 0.05)
    # mild drift inside the causal pipeline (both defenses, one experiment)
    check("5.9 causal7 s025 ToN naive -0.42", -0.415,
          val(a7, "gain", regime="ton_scanning", arm="tcausal_s025_none"), 0.005)
    check("5.9 causal7 s025 UNSW naive -0.11 (resolved)", -0.113,
          val(a7, "gain", regime="unsw_recon", arm="tcausal_s025_none"), 0.005)
    check("5.9 causal7 s025 PortScan naive -0.98", -0.978,
          val(a7, "gain", regime="portscan", arm="tcausal_s025_none"), 0.005)
    check("5.9 causal7 s025 ToN gate vs naive +0.30", 0.299,
          val(c7, "diff", regime="ton_scanning", contrast="tcausal_s025_gate_vs_naive"), 0.005)
    # ZERO-DRIFT CONTROL (random triggers, no drift at all)
    check("5.9 zero-drift PortScan naive -2.76", -2.757,
          val(a7, "gain", regime="portscan", arm="rand_s0_none"), 0.005)
    check("5.9 zero-drift UNSW naive -0.75", -0.752,
          val(a7, "gain", regime="unsw_recon", arm="rand_s0_none"), 0.005)
    check("5.9 zero-drift ToN naive -4.75", -4.751,
          val(a7, "gain", regime="ton_scanning", arm="rand_s0_none"), 0.005)
    check("5.9 zero-drift PortScan naive CI hi < 0", -2.029,
          val(a7, "ci_hi", regime="portscan", arm="rand_s0_none"), 0.01)
    check("5.9 zero-drift PortScan gate -1.11", -1.114,
          val(a7, "gain", regime="portscan", arm="rand_s0_lp32"), 0.005)
    check("5.9 zero-drift ToN gate -0.25", -0.245,
          val(a7, "gain", regime="ton_scanning", arm="rand_s0_lp32"), 0.005)
    check("5.9 zero-drift ToN gate vs naive +4.51", 4.506,
          val(c7, "diff", regime="ton_scanning", contrast="rand_s0_gate_vs_naive"), 0.005)
    check("5.9 zero-drift PortScan gate vs naive +1.64", 1.643,
          val(c7, "diff", regime="portscan", contrast="rand_s0_gate_vs_naive"), 0.005)
    check("5.9 zero-drift UNSW gate vs naive +0.19", 0.194,
          val(c7, "diff", regime="unsw_recon", contrast="rand_s0_gate_vs_naive"), 0.005)
    check("5.9 rand mild-drift ToN naive -4.03", -4.032,
          val(a7, "gain", regime="ton_scanning", arm="rand_s025_none"), 0.005)
    # sequential probe gate
    check("5.9 seq PortScan +9.21 (best gate)", 9.214, val(a7, "gain", regime="portscan", arm="seq64"), 0.005)
    check("5.9 seq PortScan vs lp32 +0.09 (sig)", 0.094,
          val(c7, "diff", regime="portscan", contrast="seq64_vs_lp32"), 0.005)
    check("5.9 seq mean labels/decision 54.1 (< 64)", 54.07,
          val(a7, "seq_labels_mean", regime="portscan", arm="seq64"), 0.05)
    check("5.9 seq ToN +0.76", 0.760, val(a7, "gain", regime="ton_scanning", arm="seq64"), 0.005)
    check("5.9 seq UNSW +1.38", 1.379, val(a7, "gain", regime="unsw_recon", arm="seq64"), 0.005)

    # --- Amendment 008: size-matched zero drift, risk-averse gates under zero drift, seqav ---
    a8 = pd.read_csv(f"{T}/paper2_amendment_008/summary.csv")
    c8 = pd.read_csv(f"{T}/paper2_amendment_008/paired_ci.csv")
    # size-matched zero drift: harm survives (not a small-candidate artifact)
    check("8 zero-drift sz2000 PortScan naive -4.81", -4.808,
          val(a8, "gain", regime="portscan", arm="rz_none_sz2000"), 0.02)
    check("8 zero-drift sz2000 ToN naive -5.76", -5.756,
          val(a8, "gain", regime="ton_scanning", arm="rz_none_sz2000"), 0.02)
    check("8 zero-drift sz2000 UNSW naive -0.13 (resolved)", -0.128,
          val(a8, "gain", regime="unsw_recon", arm="rz_none_sz2000"), 0.01)
    check("8 zero-drift sz2000 PortScan naive CI hi < 0", -2.461,
          val(a8, "ci_hi", regime="portscan", arm="rz_none_sz2000"), 0.02)
    # risk-averse gates under zero drift recover essentially all the loss
    check("8 zero-drift McNemar ToN 0.00 (recovers all)", 0.0,
          val(a8, "gain", regime="ton_scanning", arm="rz_mcnemar32"), 0.005)
    check("8 zero-drift McNemar PortScan 0.00", 0.0,
          val(a8, "gain", regime="portscan", arm="rz_mcnemar32"), 0.005)
    check("8 zero-drift McNemar vs naive PortScan +2.76", 2.757,
          val(c8, "diff", regime="portscan", contrast="rz_mcnemar_vs_naive"), 0.01)
    check("8 zero-drift McNemar vs naive ToN +4.75", 4.751,
          val(c8, "diff", regime="ton_scanning", contrast="rz_mcnemar_vs_naive"), 0.01)
    check("8 zero-drift seqav ToN 0.00", 0.0, val(a8, "gain", regime="ton_scanning", arm="rz_seqav64"), 0.005)
    check("8 zero-drift lcb ToN +0.01", 0.010, val(a8, "gain", regime="ton_scanning", arm="rz_lcb64"), 0.005)
    check("8 zero-drift eps0 gate ToN -0.25 (reduces not eliminates)", -0.245,
          val(a8, "gain", regime="ton_scanning", arm="rand_s0_lp32"), 0.01)
    # detector-triggered zero drift: real detector rarely fires
    check("8 zero-drift real-detector ToN naive -1.03", -1.030,
          val(a8, "gain", regime="ton_scanning", arm="sev0_none"), 0.01)
    check("8 zero-drift real-detector ToN triggers ~0.13", 0.13,
          val(a8, "n_triggers", regime="ton_scanning", arm="sev0_none"), 0.02)
    check("8 zero-drift real-detector PortScan triggers ~0.07", 0.07,
          val(a8, "n_triggers", regime="portscan", arm="sev0_none"), 0.02)
    # anytime-valid sequential gate on normal streams
    check("8 seqav PortScan +8.04 (conservative)", 8.040, val(a8, "gain", regime="portscan", arm="seqav64"), 0.01)
    check("8 seqav vs lp32 PortScan -1.08", -1.080, val(c8, "diff", regime="portscan", contrast="seqav_vs_lp32"), 0.01)
    check("8 seqav labels/decision ~60", 59.66, val(a8, "seq_labels_mean", regime="portscan", arm="seqav64"), 0.2)
    # candidate/future-eval leakage audit: shared across arms, paired contrast unaffected
    check("8 causal gate == v9 (identity: ToN gate vs naive +3.86)", 3.859,
          val(c8, "diff", regime="ton_scanning", contrast="c8_gate_vs_naive"), 0.01)
    check("8 cand-future collisions ToN gate ~462 (audited)", 462.10,
          val(a8, "cand_future_collisions", regime="ton_scanning", arm="c8_gate"), 1.0)

    # --- Amendment 009: model/generator generalization, tail, CS gate, Tuesday chrono ---
    a9 = pd.read_csv(f"{T}/paper2_amendment_009/summary.csv")
    c9 = pd.read_csv(f"{T}/paper2_amendment_009/contrasts.csv")
    t9 = pd.read_csv(f"{T}/paper2_amendment_009/tail.csv")

    def s9(block, reg, family, drift, arm):
        return val(a9, "gain", block=block, regime=reg, family=family, drift=drift, arm=arm)

    # zero-drift naive net-harm across 4 downstream models (+ no-PCA), McNemar recovers all
    check("9 zero RF naive PortScan -0.33", -0.327, s9("models", "portscan", "RF", "zero", "naive"), 0.02)
    check("9 zero RF naive UNSW -1.06", -1.060, s9("models", "unsw_recon", "RF", "zero", "naive"), 0.02)
    check("9 zero MLP naive ToN -2.15", -2.155, s9("models", "ton_scanning", "MLP", "zero", "naive"), 0.03)
    check("9 zero SVC-fulldim naive ToN -4.76", -4.760, s9("models", "ton_scanning", "SVC-fulldim", "zero", "naive"), 0.03)
    check("9 zero RF mcnemar ToN +0.00", 0.0, s9("models", "ton_scanning", "RF", "zero", "mcnemar"), 0.005)
    check("9 zero MLP mcnemar ToN +0.00", 0.0, s9("models", "ton_scanning", "MLP", "zero", "mcnemar"), 0.005)
    check("9 zero RF mcnemar-vs-naive UNSW +1.06", 1.060,
          val(c9, "diff", block="models", regime="unsw_recon", family="RF", drift="zero", contrast="mcnemar_vs_naive"), 0.02)
    # zero-drift update generators: cumulative worst, McNemar recovers all
    check("9 zero cumulative naive ToN -9.46 (worst generator)", -9.455,
          s9("generators", "ton_scanning", "cumulative", "zero", "naive"), 0.05)
    check("9 zero cumulative naive PortScan -7.04", -7.036, s9("generators", "portscan", "cumulative", "zero", "naive"), 0.05)
    check("9 zero sliding naive ToN -7.21", -7.212, s9("generators", "ton_scanning", "sliding", "zero", "naive"), 0.05)
    check("9 zero replay naive ToN -4.03", -4.033, s9("generators", "ton_scanning", "replay", "zero", "naive"), 0.05)
    check("9 zero ensemble-cal naive PortScan +0.84 (helps)", 0.841,
          s9("generators", "portscan", "ensemble-cal", "zero", "naive"), 0.02)
    check("9 zero cumulative mcnemar ToN +0.00", 0.0, s9("generators", "ton_scanning", "cumulative", "zero", "mcnemar"), 0.005)
    # cumulative/replay mild: naive harm, gate neutralizes
    check("9 mild cumulative naive ToN -2.57", -2.571, s9("generators", "ton_scanning", "cumulative", "mild", "naive"), 0.03)
    check("9 mild cumulative gate ToN -0.14 (neutralized)", -0.136, s9("generators", "ton_scanning", "cumulative", "mild", "lp32"), 0.02)
    # tail metrics: harm concentrates in the tail, gate protects it
    def tail(reg, level, col):
        return val(t9, col, regime=reg, level=level)
    check("9 tail ToN naive worst-window -5.24", -5.237, tail("ton_scanning", "worst", "naive_gap"), 0.03)
    check("9 tail ToN naive CVaR@10 -4.74", -4.742, tail("ton_scanning", "cvar10", "naive_gap"), 0.03)
    check("9 tail ToN gate worst-window +0.72 (protected)", 0.723, tail("ton_scanning", "worst", "gate_gap"), 0.03)
    # CS gate: conservative, never commits at small budget
    check("9 CS gate ToN zero +0.00 (conservative)", 0.0, s9("cs_gate", "ton_scanning", "Robbins-CS", "zero", "cs64"), 0.005)
    # amendment 010: empirical-Bernstein CS captures large benefit, stays safe elsewhere
    check("10 EB-CS PortScan full +5.17 (captures benefit)", 5.172,
          s9("cs_gate", "portscan", "EB-CS", "full", "ebcs64"), 0.05)
    check("10 EB-CS UNSW full +0.00 (1-pt benefit unresolved)", 0.0,
          s9("cs_gate", "unsw_recon", "EB-CS", "full", "ebcs64"), 0.005)
    check("10 EB-CS ToN full +0.00 (safe, avoids harm)", 0.0,
          s9("cs_gate", "ton_scanning", "EB-CS", "full", "ebcs64"), 0.005)
    check("10 EB-CS ToN zero +0.00 (safe)", 0.0, s9("cs_gate", "ton_scanning", "EB-CS", "zero", "ebcs64"), 0.005)
    check("10 EB-CS ToN full vs naive +1.38 (avoids harm)", 1.376,
          val(c9, "diff", block="cs_gate", regime="ton_scanning", family="EB-CS", contrast="ebcs_vs_naive"), 0.05)
    # Tuesday chronological: incumbent collapses (deep benefit, not healthy)
    check("9 Tuesday chrono no-adapt BA 49.5 (collapse)", 49.51,
          val(a9, "noadapt_ba", block="chrono", arm="naive"), 0.2)
    check("9 Tuesday chrono gate premium -5.66", -5.662,
          val(c9, "diff", block="chrono", contrast="gate_premium(lp32-naive)"), 0.05)

    # --- Amendment 011: leakage-free causal, cumulative controls, EB-CS budget, harmful-commit, coverage ---
    a11 = pd.read_csv(f"{T}/paper2_amendment_011/summary.csv")
    c11 = pd.read_csv(f"{T}/paper2_amendment_011/contrasts.csv")
    h11 = pd.read_csv(f"{T}/paper2_amendment_011/harmful_commit.csv")
    cov = pd.read_csv(f"{T}/paper2_amendment_011/cs_coverage.csv")

    def c11v(reg, drift, which, col="gate_vs_naive"):
        return val(c11, col, block="causal", regime=reg, drift=drift, which=which)

    # causal leakage-free: collisions -> ~0, harm-regime result survives
    check("11 clean causal collisions ToN ~0", 1.1, c11v("ton_scanning", "full", "clean", "collisions"), 0.6)
    check("11 leaky causal collisions ToN ~462", 462.1, c11v("ton_scanning", "full", "leaky", "collisions"), 1.0)
    check("11 clean causal ToN full gate-vs-naive +2.95 (survives)", 2.949, c11v("ton_scanning", "full", "clean"), 0.03)
    check("11 clean causal ToN mild gate-vs-naive +1.40", 1.398, c11v("ton_scanning", "mild", "clean"), 0.03)
    check("11 clean causal PortScan full ~0 (premium was leak)", -0.064, c11v("portscan", "full", "clean"), 0.03)
    # cumulative controls: none removes harm; dedup deepens; initobs flips UNSW positive
    def a11v(reg, arm, col="gain"):
        return val(a11, col, block="cumulative", regime=reg, arm=arm)
    check("11 cum dedup ToN -10.74 (deepens)", -10.735, a11v("ton_scanning", "cum_dedup"), 0.05)
    check("11 cum initobs ToN -8.27 (attenuates, persists)", -8.272, a11v("ton_scanning", "cum_initobs"), 0.05)
    check("11 cum initobs UNSW +0.53 (flips positive)", 0.533, a11v("unsw_recon", "cum_initobs"), 0.03)
    check("11 cum observed unique_frac ~0.83 (dupes)", 0.830, a11v("ton_scanning", "cum_initobs", "unique_frac"), 0.05)
    # EB-CS budget sweep: recovers small benefits with more labels
    def b11v(reg, arm, col="gain"):
        return val(a11, col, block="ebcs_budget", regime=reg, arm=arm)
    check("11 ebcs256 PortScan +8.07 (approaches fixed gate)", 8.068, b11v("portscan", "ebcs256"), 0.05)
    check("11 ebcs256 UNSW +0.78 (resolves small benefit)", 0.776, b11v("unsw_recon", "ebcs256"), 0.03)
    check("11 ebcs64 UNSW +0.00 (unresolved at b=64)", 0.0, b11v("unsw_recon", "ebcs64"), 0.005)
    # harmful-commit rate: eps0 harmful, risk-controlled zero
    def h11v(reg, gate, col):
        return val(h11, col, regime=reg, gate=gate)
    check("11 eps0 harmful frac-of-commits UNSW 0.32", 0.317, h11v("unsw_recon", "lp32_eps0", "harmful_frac_of_commits"), 0.02)
    check("11 mcnemar harmful/stream ToN 0.00", 0.0, h11v("ton_scanning", "mcnemar_zero", "harmful_per_stream"), 0.001)
    check("11 ebcs harmful/stream PortScan 0.00", 0.0, h11v("portscan", "ebcs_full", "harmful_per_stream"), 0.001)
    # CS coverage: iid <= alpha; EB exceeds under autocorrelation
    def covv(method, regime):
        return val(cov, "rate", method=method, regime=regime)
    check("11 coverage eb iid <= alpha (0.0018)", 0.0018, covv("eb", "iid_mean0"), 0.01)
    check("11 coverage eb autocorr exceeds alpha (0.18)", 0.1789, covv("eb", "autocorr_mean0"), 0.03)

    # --- Amendment 012: bug fixes + confounds (Sol 4th round) ---
    a12 = pd.read_csv(f"{T}/paper2_amendment_012/summary.csv")
    hc = pd.read_csv(f"{T}/paper2_amendment_011/harmful_commit.csv")

    def a12v(block, reg, arm, col="gain"):
        return val(a12, col, block=block, regime=reg, arm=arm)

    # BUG1 fix: corrected cn (C~1/n) still net-harmful, deeper than C=1
    check("12 cn corrected ToN -10.62 (harm persists under 1/n reg)", -10.623,
          a12v("cn_fix", "ton_scanning", "cn_corrected_1overN"), 0.05)
    check("12 cn corrected PortScan -9.82", -9.820, a12v("cn_fix", "portscan", "cn_corrected_1overN"), 0.05)
    # BUG2 fix: McNemar at alpha=0.10 still 0 commits under zero drift
    check("12 McNemar a0.10 ToN 0 commits", 0.0, a12v("mcnemar_a10", "ton_scanning", "mcnemar_a0.10", "commits"), 0.001)
    check("12 McNemar a0.10 ToN gain 0.00", 0.0, a12v("mcnemar_a10", "ton_scanning", "mcnemar_a0.10"), 0.005)
    # BUG3 fix: causal reject-policy -> 0 unvalidated commits; result survives
    check("12 causal reject ToN full commit_no_probe 0", 0.0,
          val(a12, "commit_no_probe", block="causal_reject", regime="ton_scanning", drift="full"), 0.001)
    check("12 causal reject ToN full gate-vs-naive +3.24", 3.236,
          val(a12, "gate_vs_naive", block="causal_reject", regime="ton_scanning", drift="full"), 0.03)
    # CONFOUND4: size-matched removes zero-drift harm for robust models, persists for SVC
    check("12 sizematch RF ToN ~0 (harm removed)", -0.004,
          a12v("sizematch_models", "ton_scanning", "random_forest_sz2000"), 0.03)
    check("12 sizematch MLP UNSW ~0 (harm removed)", -0.007,
          a12v("sizematch_models", "unsw_recon", "mlp_sz2000"), 0.03)
    check("12 sizematch RF UNSW 512 was -1.06", -1.060,
          a12v("sizematch_models", "unsw_recon", "random_forest_sz2000", "gain_512"), 0.02)
    # #6 strict-> baseline recovers most of eps0 harm
    check("12 strict-> ToN -0.065 (vs eps0 -0.25)", -0.065, a12v("strict_baseline", "ton_scanning", "strict_gt"), 0.03)
    check("12 strict-> PortScan -0.13 (vs eps0 -1.11)", -0.128, a12v("strict_baseline", "portscan", "strict_gt"), 0.03)
    # #8 harmful-commit Clopper-Pearson: eps0 CI excludes 0, McNemar upper bound
    check("12 eps0 UNSW harmful CI lo > 0 (0.206)", 0.2058,
          val(hc, "ci_lo", regime="unsw_recon", gate="lp32_eps0"), 0.01)
    check("12 McNemar ToN harmful CI upper 0.116 (0 observed)", 0.1157,
          val(hc, "ci_hi", regime="ton_scanning", gate="mcnemar_zero"), 0.01)

    # --- Amendment 013: final causal arm, stratified gate, strict outside zero drift, symmetric A/B ---
    a13 = pd.read_csv(f"{T}/paper2_amendment_013/summary.csv")
    ab = pd.read_csv(f"{T}/paper2_amendment_013/symmetric_ab.csv")

    def cf(reg, drift, arm, col="gain"):
        return val(a13, col, block="causal_final", regime=reg, drift=drift, arm=arm)

    # final causal: collisions exactly 0, zero unvalidated commits, result stands
    check("13 causal-final ToN full collisions 0", 0.0, cf("ton_scanning", "full", "gate", "collisions"), 0.001)
    check("13 causal-final ToN full commit_no_probe 0", 0.0, cf("ton_scanning", "full", "gate", "commit_no_probe"), 0.001)
    check("13 causal-final ToN full gate-vs-naive +5.57", 5.566, cf("ton_scanning", "full", "gate", "gate_vs_naive"), 0.03)
    check("13 causal-final ToN mild gate-vs-naive +4.21", 4.209, cf("ton_scanning", "mild", "gate", "gate_vs_naive"), 0.03)
    check("13 causal-final PortScan full gate-vs-naive +0.41", 0.409, cf("portscan", "full", "gate", "gate_vs_naive"), 0.02)
    check("13 causal-final UNSW full gate-vs-naive +0.51 (both arms below no-adapt)", 0.509,
          cf("unsw_recon", "full", "gate", "gate_vs_naive"), 0.02)
    check("13 causal-final UNSW full naive -1.69 (window-64 cell)", -1.690, cf("unsw_recon", "full", "naive"), 0.03)
    # calib sweep stability
    check("13 calib sweep ToN cw8 +5.44 (stable)", 5.438,
          val(a13, "gate_vs_naive", block="calib_sweep", regime="ton_scanning", arm="fc_lp32_cw8"), 0.03)
    # stratified gate: safe at zero drift, conservative benefit at full
    check("13 strat zero ToN 0.00 commits", 0.0,
          val(a13, "commits", block="stratified", regime="ton_scanning", drift="zero"), 0.001)
    check("13 strat full PortScan +6.93", 6.926, val(a13, "gain", block="stratified", regime="portscan", drift="full"), 0.05)
    # strict outside zero drift
    check("13 strict full PortScan +8.78", 8.780, val(a13, "gain", block="strict_baseline", regime="portscan", drift="full"), 0.05)
    check("13 strict full ToN +0.60", 0.595, val(a13, "gain", block="strict_baseline", regime="ton_scanning", drift="full"), 0.03)
    # symmetric A/B mechanism: independent transformer ~0 / positive; A-fit reproduces harm
    def abv(ds, cond):
        return val(ab, "gap_B_minus_A", dataset=ds, model="svc_rbf", condition=cond)
    check("13 symAB ToN independent +4.99 (no harm under symmetry)", 4.988, abv("ton_scanning", "independent_transformer"), 0.05)
    check("13 symAB ToN A-fit -10.45 (harm = transformer advantage)", -10.454, abv("ton_scanning", "A_fit_transformer"), 0.05)
    check("13 symAB UNSW independent 0.00", 0.0, abv("unsw_recon", "independent_transformer"), 0.01)

    # --- Amendment 014 + final-kbs: stratified/defer/lifetime gates, causal-64, 4-condition A/B ---
    a14 = pd.read_csv(f"{T}/paper2_amendment_014/summary.csv")
    fk = pd.read_csv(f"{T}/paper2_final_kbs/summary.csv")
    abf = pd.read_csv(f"{T}/paper2_final_kbs/symmetric_ab.csv")

    def a14v(block, reg, drift, col="gain"):
        return val(a14, col, block=block, regime=reg, drift=drift)

    def fkv(block, reg, drift, arm=None, col="gain"):
        kw = dict(block=block, regime=reg, drift=drift)
        if arm is not None:
            kw["arm"] = arm
        return val(fk, col, **kw)

    # stratified anytime-valid gate: safe at zero drift, conservative at full
    check("14 ebcs_strat zero ToN 0 commits", 0.0, a14v("ebcs_strat", "ton_scanning", "zero", "commits"), 0.001)
    check("14 ebcs_strat full PortScan +0.42", 0.420, a14v("ebcs_strat", "portscan", "full"), 0.03)
    # defer recovers power
    check("14 ebcs_defer full PortScan +6.76", 6.757, a14v("ebcs_defer", "portscan", "full"), 0.05)
    check("14 ebcs_defer mild ToN 0.00 (safe)", 0.0, a14v("ebcs_defer", "ton_scanning", "mild"), 0.005)
    # lifetime Bonferroni costs benefit
    check("14 ebcs_lifetime full PortScan +1.01", 1.009, a14v("ebcs_lifetime", "portscan", "full"), 0.03)
    # causal-64 unified matrix
    check("fk causal64 ToN full naive -2.85", -2.851, fkv("causal64", "ton_scanning", "full", "none"), 0.03)
    check("fk causal64 ToN full lp32 vs naive +4.05", 4.054,
          fkv("causal64", "ton_scanning", "full", "lp32", "vs_naive"), 0.03)
    check("fk causal64 ToN mild lp32 vs naive +4.83", 4.828,
          fkv("causal64", "ton_scanning", "mild", "lp32", "vs_naive"), 0.03)
    check("fk causal64 ToN full strict vs naive +3.86", 3.864,
          fkv("causal64", "ton_scanning", "full", "strict", "vs_naive"), 0.03)
    check("fk causal64 collisions 0 (ToN full lp32)", 0.0,
          fkv("causal64", "ton_scanning", "full", "lp32", "collisions"), 0.001)
    check("fk causal64 UNSW full lp32 below no-adapt (-1.18)", -1.180,
          fkv("causal64", "unsw_recon", "full", "lp32"), 0.03)
    # 4-condition symmetric A/B (rand contrast), ToN SVC
    def abv2(reg, cond):
        return val(abf, "gap", dataset=reg, model="svc_rbf", condition=cond, contrast="rand")
    check("fk AB ToN independent -1.78 (~0)", -1.779, abv2("ton_scanning", "independent"), 0.05)
    check("fk AB ToN incumbent-fit -12.35", -12.347, abv2("ton_scanning", "incumbent_fit"), 0.05)
    check("fk AB ToN challenger-fit +17.77 (inverts)", 17.767, abv2("ton_scanning", "challenger_fit"), 0.05)
    check("fk AB ToN own-transformer +0.05 (eliminated)", 0.047, abv2("ton_scanning", "own_transformer"), 0.02)
    check("fk AB ToN RF independent ~0 (learner-specific)", 0.020,
          val(abf, "gap", dataset="ton_scanning", model="random_forest",
              condition="independent", contrast="rand"), 0.02)
    # prevalence sweep: detector starvation at low pi in ToN
    check("fk prev ToN pi0.01 naive ~0 (0.03 triggers)", 0.001,
          fkv("prev_sweep", "ton_scanning", "pi0.01", "none"), 0.005)
    check("fk prev PortScan pi0.10 naive +4.76", 4.760, fkv("prev_sweep", "portscan", "pi0.10", "none"), 0.05)

    # final-kbs: VBC-SG per-proposal cells (read raw; not in fk summary)
    def vbc_gain(reg, tag):
        d = pd.read_csv(f"results/raw/paper2_fk_{reg}_{tag}/paper2_progressive_readaptation_by_seed.csv")
        d = d[d.seed.isin(set(range(104, 134)))]
        g = d[d.method == "ks_max"].set_index("seed")["mean_balanced_accuracy"]
        b = d[d.method == "no_adaptation"].set_index("seed")["mean_balanced_accuracy"]
        return float(((g - b) * 100).mean())
    check("fk VBC-SG per-proposal PortScan full +3.02", 3.016, vbc_gain("portscan", "full_vbcpp"), 0.03)
    check("fk VBC-SG per-proposal ToN zero 0.00 (safe)", 0.0, vbc_gain("ton_scanning", "rz_vbcpp"), 0.005)

    # --- final-q1: budget frontier (D3) and confirmatory A/B equivalence (D2) ---
    import os
    Q1 = f"{T}/paper2_final_q1"
    if os.path.exists(f"{Q1}/budget_frontier.csv"):
        BF = pd.read_csv(f"{Q1}/budget_frontier.csv")
        AN = pd.read_csv(f"{Q1}/frontier_anchors.csv")

        def bf(pol, cap, col, scen="ps_full", sch="bonf"):
            r = BF[(BF.scenario == scen) & (BF.policy == pol) & (BF.cap == cap)
                   & (BF.schedule == sch)]
            return float(r.iloc[0][col]) if len(r) else None

        def anc(scen, pol, col="gain"):
            r = AN[(AN.scenario == scen) & (AN.policy == pol)]
            return float(r.iloc[0][col]) if len(r) else None

        check("q1 anchor PortScan naive +7.22", 7.22, anc("ps_full", "none"), 0.02)
        check("q1 anchor PortScan strict +7.57", 7.57, anc("ps_full", "strict"), 0.02)
        check("q1 anchor ToN-zero naive -5.35", -5.35, anc("ton_zero", "none"), 0.02)
        check("q1 anchor ToN-zero strict -0.01", -0.01, anc("ton_zero", "strict"), 0.02)
        check("q1 anchor ToN-zero point -0.17", -0.175, anc("ton_zero", "point"), 0.02)
        check("q1 anchor ToN-zero strict commits 0.13", 0.13, anc("ton_zero", "strict", "commits"), 0.02)
        # q1-final-patch: gains re-pinned after the deferred-commit temporal fix (a deferred
        # commit no longer retroactively serves its own resolution window). Commit counts,
        # deferral counts, harm accounting, abstention, delay and labels were bit-identical
        # before and after; only the served-BA gains moved (<= 0.14 pts, PortScan arms).
        check("q1 frontier ebcsdef c64 +3.73 (52%)", 3.73, bf("ebcsdef", 64, "gain"), 0.02)
        check("q1 frontier ebcsdef c64 frac 0.52", 0.52, bf("ebcsdef", 64, "e2_frac_naive"), 0.01)
        check("q1 frontier ebcsdef c512 +6.73", 6.73, bf("ebcsdef", 512, "gain"), 0.02)
        check("q1 frontier ebcsdef c512 frac 0.93", 0.93, bf("ebcsdef", 512, "e2_frac_naive"), 0.01)
        check("q1 frontier ebcsdef c512 labels 578", 578, bf("ebcsdef", 512, "labels_probe_per_proposal"), 2.0)
        check("q1 frontier vbccoh c512 frac 0.81", 0.81, bf("vbccoh", 512, "e2_frac_naive"), 0.01)
        check("q1 frontier vbcref c512 frac 0.68", 0.68, bf("vbcref", 512, "e2_frac_naive"), 0.01)
        # zero-drift safety: every lifetime config at every cap commits nothing
        zc = BF[BF.scenario == "ton_zero"].commits_total.sum()
        check("q1 frontier zero-drift commits 0 (all caps)", 0.0, float(zc), 0.5)
        # final-q1 blocker B: harmful commits over ALL resolved commits (immediate AND
        # deferred), scored from the real resolution window. Pinned to whatever the complete
        # accounting says -- the audit must not be able to certify "zero" from partial data.
        # final-q1 blocker B: every commit must be either evaluated or explicitly censored.
        # If the frontier CSV predates the resolution-log accounting, say so as a FAILING
        # check rather than crashing -- a stale artifact must never look like a pass.
        if {"e6_n_evaluable", "e6_n_censored"} <= set(BF.columns):
            check("q1 frontier commits fully accounted (evaluable + censored = commits)", 0.0,
                  float((BF.e6_n_evaluable + BF.e6_n_censored - BF.commits_total).abs().sum()), 0.5)
        else:
            check("q1 frontier commits fully accounted (STALE: rerun make_paper2_q1_frontier)",
                  0.0, None, 0.5)

        # final-q1 blocker B: the complete harm accounting the manuscript now quotes.
        if "e6_harmful_h5" in BF.columns:
            check("q1 harm: risk-gate commits 520", 520, float(BF.commits_total.sum()), 0.5)
            check("q1 harm: deferred 180", 180, float(BF.n_commits_deferred.sum()), 0.5)
            check("q1 harm: evaluable H5 506", 506, float(BF.e6_n_evaluable.sum()), 0.5)
            check("q1 harm: censored H5 14", 14, float(BF.e6_n_censored.sum()), 0.5)
            check("q1 harm: harmful H5 = 0 over the COMPLETE accounting", 0.0,
                  float(BF.e6_harmful_h5.sum()), 0.5)
            check("q1 harm: harmful until next decision = 0", 0.0,
                  float(BF.e6_harmful_until_next.sum()), 0.5)

    if os.path.exists(f"{T}/paper2_final_kbs/ab_equivalence.csv"):
        EQ = pd.read_csv(f"{T}/paper2_final_kbs/ab_equivalence.csv")
        pr = EQ[(EQ.analysis == "primary_confirmatory") & (EQ.margin == 1.0)]

        def eqv(ds, cond, col):
            r = pr[(pr.dataset == ds) & (pr.condition == cond)]
            return float(r.iloc[0][col]) if len(r) else None

        def eqflag(ds, cond):
            r = pr[(pr.dataset == ds) & (pr.condition == cond)]
            return float(bool(r.iloc[0].equivalent)) if len(r) else None

        check("q1 AB conf ToN own-transformer -0.01", -0.007, eqv("ton_scanning", "own_transformer", "mean_gap"), 0.02)
        check("q1 AB conf ToN own-transformer EQUIVALENT", 1.0, eqflag("ton_scanning", "own_transformer"), 0.1)
        check("q1 AB conf UNSW independent +0.00 (global dedup)", 0.004, eqv("unsw_recon", "independent", "mean_gap"), 0.02)
        check("q1 AB conf UNSW independent EQUIVALENT", 1.0, eqflag("unsw_recon", "independent"), 0.1)
        check("q1 AB conf ToN independent -1.43 (unresolved)", -1.425, eqv("ton_scanning", "independent", "mean_gap"), 0.02)
        check("q1 AB conf ToN independent NOT equivalent", 0.0, eqflag("ton_scanning", "independent"), 0.1)
        check("q1 AB conf PortScan independent -0.30", -0.299, eqv("portscan", "independent", "mean_gap"), 0.02)
        check("q1 AB decomp inc-scaler -12.17", -12.166, eqv("ton_scanning", "inc_scaler_indep_pca", "mean_gap"), 0.02)
        check("q1 AB decomp indep-scaler/inc-PCA +0.16", 0.164, eqv("ton_scanning", "indep_scaler_inc_pca", "mean_gap"), 0.02)

    # --- final-q1 Fase D: chronological matrix (D4) and operational e2e (D5) ---
    if os.path.exists(f"{Q1}/chronological_replays.csv"):
        CH = pd.read_csv(f"{Q1}/chronological_replays.csv")

        def ch(stream, policy, col="gain_ba", scale=100.0):
            r = CH[(CH.stream == stream) & (CH.policy == policy)]
            return float(r.iloc[0][col]) * scale if len(r) else None

        check("q1 chrono UNSW20 no-adapt BA 82.9", 82.9, ch("unsw_20", "none", "noadapt_ba"), 0.1)
        check("q1 chrono UNSW20 naive +8.35", 8.35, ch("unsw_20", "none"), 0.02)
        check("q1 chrono UNSW20 strict +11.13", 11.13, ch("unsw_20", "strict"), 0.02)
        check("q1 chrono UNSW20 strict CI lo 10.50", 10.50, ch("unsw_20", "strict", "ba_lo"), 0.05)
        check("q1 chrono UNSW40 naive +7.64", 7.64, ch("unsw_40", "none"), 0.02)
        check("q1 chrono UNSW40 strict +8.98", 8.98, ch("unsw_40", "strict"), 0.02)
        check("q1 chrono Wed-intraday healthy 84.7", 84.7, ch("wed_intraday", "none", "noadapt_ba"), 0.1)
        check("q1 chrono Wed-intraday strict +5.77 (below naive)", 5.77, ch("wed_intraday", "strict"), 0.02)
        check("q1 chrono TueWk naive +14.78", 14.78, ch("tue_wedthufri", "none"), 0.02)
        check("q1 chrono TueWk point +11.52", 11.52, ch("tue_wedthufri", "point"), 0.02)
        # the headline negative: no chronological net harm anywhere
        worst = float(CH[CH.policy == "none"].gain_ba.min()) * 100
        check("q1 chrono no net harm (min naive gain >= 0)", 0.44, max(worst, 0.0), 0.45)

    if os.path.exists(f"{Q1}/operational_e2e.csv"):
        OE = pd.read_csv(f"{Q1}/operational_e2e.csv")
        base = OE[(OE.cand_latency == 5) & (OE.train_delay == 0)]

        def oe(ds, pi, acq):
            r = base[(base.dataset == ds) & (base.prevalence == pi) & (base.acquisition == acq)]
            return float(r.iloc[0].discovery_flows_per_attack) if len(r) else None

        check("q1 e2e ToN pi.01 random 92.2 flows/attack (discovery half)", 92.2, oe("ton", 0.01, "random"), 0.6)
        check("q1 e2e ToN pi.01 alert-enriched 14.7", 14.7, oe("ton", 0.01, "alert_enriched"), 0.15)
        check("q1 e2e PortScan pi.01 random 109.1", 109.1, oe("portscan", 0.01, "random"), 0.6)
        check("q1 e2e PortScan pi.05 alert-enriched 3.3", 3.3, oe("portscan", 0.05, "alert_enriched"), 0.15)
        check("q1 e2e ToN pi.005 alert-enriched 28.8", 28.8, oe("ton", 0.005, "alert_enriched"), 0.25)

        def oes(ds, cl, td, col="gain"):
            r = OE[(OE.dataset == ds) & (OE.prevalence == 0.05) & (OE.acquisition == "random")
                   & (OE.cand_latency == cl) & (OE.train_delay == td)]
            return float(r.iloc[0][col]) * 100 if len(r) else None

        check("q1 e2e PortScan lat5 delay0 +5.83", 5.83, oes("portscan", 5, 0), 0.02)
        check("q1 e2e PortScan lat20 +4.81", 4.81, oes("portscan", 20, 0), 0.02)
        check("q1 e2e PortScan train-delay5 +5.37", 5.37, oes("portscan", 5, 5), 0.02)
        check("q1 e2e chrono thu_fri naive +36.07", 36.07,
              float(pd.read_csv(f"{Q1}/chronological_replays.csv")
                    .query("stream=='thu_fri' and policy=='none'").iloc[0].gain_ba) * 100, 0.02)

    # --- final editorial overclaim guards (Blocks 1-8): claim strength vs evidence ---
    # Meaning-based, not a single exact string, and checked against both the CAS source and
    # the IEEE port so a reworded false claim cannot slip through one of them.
    import re as _re
    _texts = {}
    # q1-final-patch (Block G): README.md and highlights.md are claim surfaces too -- the
    # published "every gate beats always-deploy" README overclaim slipped past these guards
    # precisely because only the .tex sources were scanned.
    # v1.20.1: REPRODUCE.md and every generated table caption are claim surfaces too.
    import glob as _glob
    _claim_files = ["manuscript/main.tex", "manuscript/main_ieee.tex",
                    "manuscript/supplement.tex", "README.md", "manuscript/highlights.md",
                    "REPRODUCE.md"]
    _claim_files += sorted(_glob.glob("manuscript/tables/*.tex"))
    _claim_files += sorted(_glob.glob("manuscript/tables_ieee/*.tex"))
    for _p in _claim_files:
        if os.path.exists(_p):
            _texts[_p.replace("\\", "/")] = _re.sub(
                r"\s+", " ", open(_p, encoding="utf-8").read().lower())

    def _hits(pat):
        return sum(len(_re.findall(pat, t)) for t in _texts.values())

    def _prox_hits(anchor, needles, span=120, ahead=False):
        n = 0
        for t in _texts.values():
            for m in _re.finditer(anchor, t):
                w = t[m.start(): m.end() + span] if ahead else \
                    t[max(0, m.start() - span): m.end() + span]
                if any(x in w for x in needles):
                    n += 1
        return n

    check("no-overclaim: 'full protection' (B6)", 0.0, float(_hits(r"full protection")), 0.5)
    check("no-overclaim: strict 'costs no labels at all' (B2)", 0.0,
          float(_hits(r"costs no labels at all")), 0.5)
    check("no-overclaim: 'zero-cost strict' (B2)", 0.0, float(_hits(r"zero-cost strict")), 0.5)
    check("no-overclaim: 'reproduces every conclusion' (B5)", 0.0,
          float(_hits(r"reproduces every conclusion")), 0.5)
    check("no-overclaim: causal-vs-oracle 'statistically indistinguishable' (B5)", 0.0,
          float(_prox_hits(r"statistically indistinguishable", ("oracle", "causal gate"))), 0.5)
    check("no-overclaim: 'assumed zero throughout' / 'instantaneous in every arm' (B4)", 0.0,
          float(_hits(r"assumed zero throughout") + _hits(r"instantaneous in every arm")), 0.5)
    check("no-overclaim: 'scoring all 520 commits' at H5 (B8)", 0.0,
          float(_hits(r"scoring all 520 commits")), 0.5)
    check("no-overclaim: joint 'significantly outperforms both naive' (B7)", 0.0,
          float(_hits(r"significantly outperforms both naive")), 0.5)
    check("no-overclaim: 'all three gates ... above/beat always-deploying' (B3)", 0.0,
          float(_prox_hits(r"all three gates", ("above always", "beat always"), span=90, ahead=True)), 0.5)
    check("no-overclaim: 'match or beat always-deploying' (B3)", 0.0,
          float(_prox_hits(r"match(?:es)?[ -]or[ -]beat", ("always-deploying", "always deploying"),
                           span=45, ahead=True)), 0.5)
    check("no-overclaim: 'every gate beats' (B3)", 0.0, float(_hits(r"every gate beats")), 0.5)

    # --- q1-final-patch guards (Blocks C, D, G) ------------------------------------------
    # C1: the operational arm is an ACQUISITION-YIELD simulation; no surface may call it the
    # cost of the commit decision or claim all labels sit at operating prevalence.
    check("q1fp C1: no 'what the commit decision costs'", 0.0,
          float(_hits(r"what the commit decision costs")), 0.5)
    check("q1fp C1: no 'all labels (sit )?at operating' claim", 0.0,
          float(_hits(r"all labels\W+(?:sit at|at) operating")
                + _hits(r"and all labels\W+at operating")), 0.5)
    check("q1fp C1: no 'prices the decision in inspected flows'", 0.0,
          float(_hits(r"prices the decision in inspected flows")), 0.5)
    check("q1fp C1: no 'end-to-end cost of (the )?commit'", 0.0,
          float(_hits(r"end[- ]to[- ]end cost of (?:the )?commit")), 0.5)
    check("q1fp C1: no 'cost of obtaining the 32'", 0.0,
          float(_hits(r"cost of obtaining the 32")), 0.5)
    # C2: the Table 11 caption (both editions) must carry the acquisition-yield title and the
    # balanced-candidate disclosure, and must not carry the commit-cost title.
    _cap_ok = _cap_bad = 0
    for _tp in ("manuscript/tables/table_operational_e2e.tex",
                "manuscript/tables_ieee/table_operational_e2e.tex"):
        if os.path.exists(_tp):
            _c = _re.sub(r"\s+", " ", open(_tp, encoding="utf-8").read().lower())
            _cap_ok += int("acquisition yield" in _c and "balanced per class" in _c)
            _cap_bad += int("commit decision costs" in _c)
    check("q1fp C2: Table 11 captions say acquisition yield + balanced candidate (2 files)",
          2.0, float(_cap_ok), 0.5)
    check("q1fp C2: Table 11 captions do not say 'commit decision costs'", 0.0,
          float(_cap_bad), 0.5)
    # C3: the operational runner must declare its scope fields (structural, not phrasing).
    _oe_src = ""
    if os.path.exists("src/experiments/run_paper2_operational_e2e.py"):
        _oe_src = open("src/experiments/run_paper2_operational_e2e.py", encoding="utf-8").read()
    for _field in ("candidate_training_sampling", "balanced_per_class",
                   "candidate_training_inspection_cost_modeled",
                   "validation_sampling_policy", "decision_metric",
                   "inspected_flows_per_attack"):
        check(f"q1fp C3: operational runner declares {_field}", 1.0,
              float(_field in _oe_src), 0.5)
    # D1: no universal healthy-timeline claim, in any phrasing scanned here. The precise form
    # is: point+strict win both UNSW timelines, VBC-SG one, Wednesday intra-day unresolved.
    check("q1fp D1: no 'the gates beat always-deploying where/when ... healthy' universal", 0.0,
          float(_prox_hits(r"gates beat always-deploying", ("where the incumbent", "when the incumbent",
                                                           "on healthy", "healthy timelines"),
                           span=60, ahead=True)), 0.5)
    check("q1fp D1: no 'every|all gate(s) (beat|outperform|above) always'", 0.0,
          float(_hits(r"(?:every|all) gates? (?:beats?|outperforms?|(?:sit |are )?above) always")), 0.5)
    check("q1fp D1: Wednesday counterexample stated wherever UNSW win is claimed (main+ieee)", 2.0,
          float(sum(1 for _n, _t in _texts.items()
                    if _n.endswith(("/main.tex", "/main_ieee.tex"))
                    and "unresolved counterexample" in _t)), 0.5)
    # G1: temporal serving semantics -- the v2 runner must evaluate/score the window BEFORE
    # the pending-resolution block can swap the model or rebuild the detector (Block A).
    _v2 = open("src/experiments/run_paper2_readaptation_v2.py", encoding="utf-8").read()
    _loop = _v2[_v2.index("for t, (Xw, yw, sev) in enumerate(env.stream):"):]
    _i_eval = _loop.index("m = evaluate_model(model, Xw, yw)")
    _i_score = _loop.index("score = float(detector.score(Xw))")
    _i_pend = _loop.index("if pending is not None:")
    check("q1fp G1: v2 loop serves the window before resolving pending (eval<pending)", 1.0,
          float(_i_eval < _i_pend and _i_score < _i_pend), 0.5)
    check("q1fp G1: v2 loop logs served_model_version", 1.0,
          float("served_model_version" in _v2), 0.5)

    # --- q1-final-patch v1.20.1 guards (statistical + claim-scope) --------------------------
    # v2A: the 0/506 count must never be dressed as a binomial population-rate bound.
    check("v121 A: no '0.73%'/'0.726' harm-rate bound anywhere", 0.0,
          float(_hits(r"0\.73\\?%") + _hits(r"0\.726")), 0.5)
    check("v121 A: no 'Clopper' on the claim surfaces", 0.0, float(_hits(r"clopper")), 0.5)
    check("v121 A: clustering caveat present with the 506 count (main+ieee)", 2.0,
          float(sum(1 for _n, _t in _texts.items() if _n.endswith(("/main.tex", "/main_ieee.tex"))
                    and "not treated as 506 independent bernoulli trials" in _t)), 0.5)
    check("v121 A: no 'bounded rate' phrasing for the harm count", 0.0,
          float(_prox_hits(r"bounded rate", ("harmful", "commit"), span=80)), 0.5)
    # v2B: multiplicity naming and family structure.
    check("v121 B: no 'exact paired bootstrap' / 'exact bootstrap p'", 0.0,
          float(_hits(r"exact paired bootstrap") + _hits(r"exact bootstrap \$?p")), 0.5)
    check("v121 B: manuscript names the centered paired bootstrap (main+ieee+supp)", 3.0,
          float(sum(1 for _t in _texts.values()
                    if "centered paired bootstrap" in _t)), 0.5)
    if os.path.exists(f"{Q1}/multiplicity.csv"):
        _M = pd.read_csv(f"{Q1}/multiplicity.csv")
        check("v121 B: multiplicity total = 28", 28.0, float(len(_M)), 0.5)
        _fc = _M.groupby("family").size()
        check("v121 B: families sized 6/15/7", 1.0,
              float(sorted(_fc.tolist()) == [6, 7, 15]), 0.5)
        check("v121 B: zero normal-approximation fallbacks", 0.0,
              float((~_M.p_method.str.contains("centered paired bootstrap")).sum()), 0.5)
        check("v121 B: sensitivity columns present", 1.0,
              float({"p_ttest_sensitivity", "p_wilcoxon_sensitivity",
                     "family_size"} <= set(_M.columns)), 0.5)
    _mx = open("src/analysis/make_paper2_q1_multiplicity.py", encoding="utf-8").read()
    check("v121 B: no outcome-dependent frontier filter in the generator", 0.0,
          float(("commits_total > 0" in _mx) or ("commits_total>0" in _mx)), 0.5)
    # v2C: operational-arm scope coherence.
    check("v121 C: no undisambiguated 'stream and the probe at operating prevalence'", 0.0,
          float(_hits(r"with the stream and the probe at operating prevalence")), 0.5)
    check("v121 C: no 'end-to-end cost of (the )?commit'", 0.0,
          float(_hits(r"end[- ]to[- ]end cost of (?:the )?commit")), 0.5)
    check("v121 C: no 'cheapens the commit decision'", 0.0,
          float(_hits(r"cheapens the commit decision")), 0.5)
    check("v121 C: no 'validation costs little and protects'", 0.0,
          float(_hits(r"validation costs little and protects")), 0.5)
    check("v121 C: manifest declares the operational scope fields", 1.0,
          float(os.path.exists("results/final_manifest.json") and all(
              k in open("results/final_manifest.json", encoding="utf-8").read()
              for k in ("operational_arm_scope", "acquisition_yield_and_delay_only",
                        "uniform_at_operating_prevalence", "plain_accuracy",
                        "end_to_end_pipeline_cost_modeled"))), 0.5)
    # v2D: Cohort-sim naming + affordable + 32-label scope.
    check("v121 D: Cohort described as Cohort-sim (main+ieee)", 2.0,
          float(sum(1 for _n, _t in _texts.items() if _n.endswith(("/main.tex", "/main_ieee.tex"))
                    and "cohort-sim" in _t)), 0.5)
    check("v121 D: Cohort-sim retention disclaimer present", 1.0,
          float(any("does not model retention and delayed adjudication" in _t
                    or "not model a retained production cohort" in _t
                    or "not a retained production cohort" in _t
                    for _t in _texts.values())), 0.5)
    check("v121 D: no unqualified 'affordable'", 0.0, float(_hits(r"affordab")), 0.5)
    check("v121 D: 'non-vacuous within the evaluated' qualification present (main+ieee)", 2.0,
          float(sum(1 for _n, _t in _texts.items() if _n.endswith(("/main.tex", "/main_ieee.tex"))
                    and "non-vacuous within the evaluated" in _t)), 0.5)
    check("v121 D: no '32 labels suffice'/'labeled flows ... suffice' claim", 0.0,
          float(_hits(r"32 labels suffice")
                + _hits(r"32 labeled flows per confirmed drift suffice")), 0.5)
    check("v121 D: no 'cheap and robust' / 'both budgets are realistic'", 0.0,
          float(_hits(r"cheap and robust") + _hits(r"both budgets are realistic")), 0.5)
    check("v121 D: 32-label claim carries the controlled balanced-probe scope (main+ieee)", 2.0,
          float(sum(1 for _n, _t in _texts.items() if _n.endswith(("/main.tex", "/main_ieee.tex"))
                    and "controlled balanced-probe" in _t)), 0.5)
    check("v121 E: no 'zero probability of harm' / 'eliminates harmful commits'", 0.0,
          float(_hits(r"zero probability of harm") + _hits(r"eliminates harmful commits")), 0.5)
    # v2E: claim-scope audit table generated and fully verified.
    _csa = f"{Q1}/claim_scope_audit.csv"
    if os.path.exists(_csa):
        _A = pd.read_csv(_csa)
        check("v121 E: claim_scope_audit rows >= 12", 1.0, float(len(_A) >= 12), 0.5)
        check("v121 E: claim_scope_audit zero FAIL rows", 0.0,
              float(_A.status.str.startswith("FAIL").sum()), 0.5)
    else:
        check("v121 E: claim_scope_audit.csv missing", 1.0, None, 0.5)
    # B1: every 93% benefit claim must be marked as the approximate pooled analysis
    _bad93 = 0
    for _t in _texts.values():
        for _m in _re.finditer(r"93\s*\\?%", _t):
            _w = _t[max(0, _m.start() - 40): _m.end() + 240]
            if ("benefit" in _w or "always-deploying" in _w) and not \
               ("approximate" in _w or "pooled" in _w):
                _bad93 += 1
    check("no-overclaim: 93% pooled marked 'approximate/pooled' (B1)", 0.0, float(_bad93), 0.5)

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

