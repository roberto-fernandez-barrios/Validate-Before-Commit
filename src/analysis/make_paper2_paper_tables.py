"""Render Paper 2 main/appendix tables (Markdown + LaTeX) from committed result CSVs.

No new experiments. Outputs to results/tables/paper2_paper_tables_001/ as .md and .tex.
Tables:
  T1  Regime taxonomy (no-adapt BA, best adaptation gain BA & F1, class).
  T2  Phase 2 gate summary (per regime x detector x gate: BA, gain, commits, labels).
  T3  Phase 2 paired CI95 (gate vs naive, gate vs no-adapt) for lp32/lp64/unsup.
  T4  Decision oracle-regret (per regime x {Energy,QK-ZZ}: regret, CI, harm%).
"""
from __future__ import annotations
import os
import pandas as pd

OUT = "results/tables/paper2_paper_tables_001"
T = "results/tables"
GNAME = {"none": "naive", "lp32": "gate-32", "lp64": "gate-64", "unsup": "unsup-0"}
DNAME = {"ks_max": "KS-max", "qk_mmd_zz": "QK-ZZ", "energy_distance": "Energy",
         "qk_mmd_pauli_xz": "QK-PauliXZ", "mmd_rbf": "MMD-RBF", "jsd": "JSD"}


def pct1(series):
    return (series * 100).map(lambda x: f"{x:.1f}")
RNAME = {"portscan": "PortScan (benefit)", "unsw_recon": "UNSW Recon (mixed)", "ton_scanning": "ToN-IoT (harm)"}


def _latex_escape(s):
    s = str(s)
    for a, b in [("%", r"\%"), ("_", r"\_"), ("&", r"\&"), ("#", r"\#")]:
        s = s.replace(a, b)
    return s


def _to_latex(df, caption, label):
    cols = list(df.columns)
    lines = [r"\begin{table}[t]", r"\centering", f"\\caption{{{_latex_escape(caption)}}}",
             f"\\label{{tab:{label}}}", "\\begin{tabular}{" + "l" * len(cols) + "}", r"\toprule",
             " & ".join(_latex_escape(c) for c in cols) + r" \\", r"\midrule"]
    for _, row in df.iterrows():
        lines.append(" & ".join(_latex_escape(v) for v in row.tolist()) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(lines)


def emit(name, df, caption):
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/{name}.md", "w", encoding="utf-8") as f:
        f.write(f"**{caption}**\n\n{df.to_markdown(index=False)}\n")
    with open(f"{OUT}/{name}.tex", "w", encoding="utf-8") as f:
        f.write(_to_latex(df, caption, name))
    print("wrote", name, df.shape)


def t1_taxonomy():
    d = pd.read_csv(f"{T}/paper2_metrics_ba_f1_summary_001/paper2_fig1_regime_spectrum.csv")
    d = d.sort_values("best_gain_BA_pts", ascending=False)
    out = pd.DataFrame({
        "Dataset / regime": d["regime"],
        "Class": d["klass"],
        "No-adapt BA": pct1(d["noadapt_BA"]),
        "Best gain (BA pts)": d["best_gain_BA_pts"].round(1),
        "Best gain (F1 pts)": d["best_gain_F1_pts"].round(1),
        "Best detector": d["best_adaptive_method"].map(lambda m: DNAME.get(m, m)),
    })
    emit("table1_regime_taxonomy", out,
         "Table 1: Readaptation value is regime-dependent. Best detector-triggered gain vs. no-adaptation (30 seeds per regime).")


def _phase2():
    return pd.read_csv(f"{T}/paper2_phase2_gated_readaptation_001/paper2_phase2_summary.csv")


def t2_gate_summary():
    d = _phase2()
    d = d[d.gate.isin(["none", "lp32", "lp64", "unsup"])].copy()
    d["order"] = d.regime.map({"portscan": 0, "unsw_recon": 1, "ton_scanning": 2})
    d = d.sort_values(["order", "detector", "gate"])
    out = pd.DataFrame({
        "Regime": d["regime"].map(RNAME),
        "Detector": d["detector"].map(DNAME),
        "Policy": d["gate"].map(GNAME),
        "BA (%)": (d["BA"] * 100).round(2),
        "Gain (pts)": d["gain_pts"].round(2),
        "Commits": d["commits"].round(1),
        "Labels": d["labels"].round(0).astype(int),
    })
    emit("table2_phase2_gate_summary", out,
         "Table 2: Phase 2 gate (30 seeds). The labeled-probe gate preserves benefit, avoids harm, and beats naive triggering; the zero-label variant fails.")


def t3_gate_ci():
    d = pd.read_csv(f"{T}/paper2_phase2_gated_readaptation_001/paper2_phase2_paired_ci.csv")
    d["order"] = d.regime.map({"portscan": 0, "unsw_recon": 1, "ton_scanning": 2})
    d = d.sort_values(["order", "detector", "gate"])

    def ci(lo, hi):
        return f"[{lo:+.2f}, {hi:+.2f}]"
    out = pd.DataFrame({
        "Regime": d["regime"].map(RNAME),
        "Detector": d["detector"].map(DNAME),
        "Policy": d["gate"].map(GNAME),
        "Δ vs naive (pts)": d["diff_vs_naive_pts"].round(2),
        "CI95 vs naive": [ci(a, b) for a, b in zip(d["naive_ci_lo"], d["naive_ci_hi"])],
        "Δ vs no-adapt (pts)": d["diff_vs_noadapt_pts"].round(2),
        "CI95 vs no-adapt": [ci(a, b) for a, b in zip(d["noadapt_ci_lo"], d["noadapt_ci_hi"])],
    })
    emit("table3_phase2_paired_ci", out,
         "Table 3: Phase 2 paired bootstrap 95% CIs (30 seeds). Bold-worthy: in ToN-IoT the labeled-probe gate is significantly above both naive triggering and no-adaptation.")


def t4_oracle_regret():
    d = pd.read_csv(f"{T}/paper2_oracle_regret_decision_001/paper2_oracle_regret_by_detector.csv")
    d = d[d.detector.isin(["energy_distance", "qk_mmd_zz"])].copy()
    out = pd.DataFrame({
        "Regime": d["regime"],
        "Class": d["klass"],
        "Detector": d["detector"].map(DNAME),
        "No-adapt BA": pct1(d["BA_noadapt"]),
        "Naive BA": pct1(d["naive_BA"]),
        "Regret (pts)": d["regret_pts"].round(2),
        "Regret CI95": [f"[{a:.2f}, {b:.2f}]" for a, b in zip(d["regret_ci_lo"], d["regret_ci_hi"])],
        "Harm streams (%)": d["harm_seed_pct"].round(0).astype(int),
    })
    emit("table4_oracle_regret", out,
         "Table 4: Decision oracle-regret and harm frequency. Regret ~0 where adaptation always helps, largest where it hurts; the pattern is detector-invariant.")


def t5_phase1_negative():
    g = pd.read_csv(f"{T}/paper2_safe_readaptation_phase1_001/paper2_phase1_gate_summary.csv")
    c = pd.read_csv(f"{T}/paper2_safe_readaptation_phase1_001/paper2_phase1_success_checks.csv")
    crit = {"cicids_portscan": "A_benefit_preservation_portscan",
            "ton_iot_scanning": "B_harm_avoidance_ton_iot",
            "unsw_nb15_reconnaissance": "C_mixed_regime_non_degradation_unsw_recon"}
    passed = dict(zip(c["criterion"], c["passed"]))
    out = pd.DataFrame({
        "Regime": g["regime_label"],
        "No-adapt BA": pct1(g["noadapt_ba"]),
        "Best safe policy": g["best_safe_policy"],
        "Safe BA": pct1(g["best_safe_ba"]),
        "Gain vs no-adapt (pts)": g["best_safe_gain"].round(2),
        "Adapt. reduction vs legacy": g["best_safe_adaptation_reduction_vs_legacy"].round(1),
        "Criterion met": [("yes" if passed.get(crit.get(r), False) else "no") for r in g["regime"]],
    })
    emit("table5_phase1_negative", out,
         "Appendix Table: Pre-registered simple policies (k-of-n confirmation, cooldown) do not prevent harmful adaptation. Best safe policy per regime vs. no-adaptation and legacy; negative adaptation-reduction means MORE adaptations than legacy. Criteria A (benefit) and B (harm) fail.")


def t6_downstream_generalization():
    f = "results/tables/paper2_phase2c_downstream_generalization_001/paper2_downstream_generalization.csv"
    if not os.path.exists(f):
        return
    d = pd.read_csv(f)
    dorder = {"svc_rbf": 0, "random_forest": 1, "logreg": 2, "mlp": 3}
    rorder = {"portscan": 0, "unsw_recon": 1, "ton_scanning": 2}
    d = d.assign(do=d.downstream.map(dorder), ro=d.regime.map(rorder)).sort_values(["do", "ro"])
    dn = {"svc_rbf": "SVC-RBF", "random_forest": "Random Forest", "logreg": "LogReg", "mlp": "MLP"}
    out = pd.DataFrame({
        "Downstream": d["downstream"].map(dn),
        "Regime": d["regime"].map(RNAME),
        "No-adapt BA": pct1(d["noadapt_BA"]),
        "Naive gain": d["naive_gain"].round(2),
        "Gate gain": d["gate_gain"].round(2),
        "Harm (naive<no-adapt)": d["harm_reproduced"].map({True: "yes", False: "no"}),
        "Gate avoids harm": d["gate_avoids_harm"].map({True: "yes", False: "no"}),
    })
    emit("table6_downstream_generalization", out,
         "Table 6: Generalization across downstream classifiers (KS-max, 20 seeds; SVC-RBF at 30). Net-harm (naive below no-adaptation) appears only for SVC-RBF on ToN-IoT; the mechanism law and the gate's safety hold for all four models.")


if __name__ == "__main__":
    t1_taxonomy()
    t2_gate_summary()
    t3_gate_ci()
    t4_oracle_regret()
    t5_phase1_negative()
    t6_downstream_generalization()
