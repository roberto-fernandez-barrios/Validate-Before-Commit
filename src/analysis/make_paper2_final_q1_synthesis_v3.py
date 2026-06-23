from __future__ import annotations

from pathlib import Path

import pandas as pd


TABLES_DIR = Path("results/tables/paper2_progressive_multi_scenario_cicids_001")
NOTES_DIR = Path("notes")


def safe_read(path: str | Path) -> pd.DataFrame | None:
    path = Path(path)
    if not path.exists():
        print(f"[WARN] Missing: {path}")
        return None
    return pd.read_csv(path)


def preview(df: pd.DataFrame | None, cols: list[str] | None = None, n: int | None = None) -> str:
    if df is None or df.empty:
        return "No rows."

    out = df.copy()

    if cols is not None:
        out = out[[c for c in cols if c in out.columns]]

    if n is not None:
        out = out.head(n)

    return out.to_string(index=False)


def main() -> None:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    summary = safe_read(TABLES_DIR / "paper_table_multi_scenario_summary.csv")
    paired = safe_read(TABLES_DIR / "paper_table_multi_scenario_paired.csv")
    utility = safe_read(TABLES_DIR / "paper_table_multi_scenario_utility_strict_positive.csv")

    qk_vs_energy = None
    if paired is not None and not paired.empty:
        qk_vs_energy = paired[
            (
                (paired["method_a"] == "QK-MMD ZZ")
                & (paired["method_b"] == "Energy distance")
            )
            | (
                (paired["method_a"] == "Energy distance")
                & (paired["method_b"] == "QK-MMD ZZ")
            )
        ].copy()

    qk_summary = None
    if summary is not None and not summary.empty:
        qk_summary = summary[
            summary["method"].isin(["qk_mmd_zz", "energy_distance", "mmd_rbf", "jsd", "ks_max"])
        ].copy()
        qk_summary = qk_summary.sort_values(["scenario", "cumulative_error_area_mean"])

    utility_focus = None
    if utility is not None and not utility.empty:
        utility_focus = utility[
            utility["baseline"].isin(["Energy distance", "MMD-RBF", "JSD", "KS-max"])
        ].copy()
        utility_focus = utility_focus.sort_values(["scenario", "baseline", "lambda_cost", "gamma_cost"])

    md = []

    md.append("# Paper 2 final Q1-oriented synthesis checkpoint 003")
    md.append("")
    md.append("## Executive summary")
    md.append("")
    md.append(
        "This checkpoint is the updated final synthesis after adding multi-scenario "
        "CICIDS2017 validation. The paper is no longer based on a single Tuesday-to-Wednesday "
        "setting: it now includes Wednesday, Friday PortScan, and Friday DDoS drift regimes."
    )
    md.append("")
    md.append(
        "The central conclusion is still not universal quantum advantage. The stronger and "
        "defensible claim is that QK-MMD ZZ provides regime-dependent adaptive-monitoring "
        "advantages. Across multiple CICIDS2017 drift regimes, it remains competitive with "
        "the strongest classical distributional baseline, Energy distance."
    )
    md.append("")
    md.append(
        "The type of advantage changes by regime: in Wednesday and DDoS, QK-MMD ZZ achieves "
        "comparable downstream performance with fewer readaptations and higher adaptation "
        "efficiency; in PortScan, it significantly improves downstream performance, but at "
        "the cost of more readaptations and higher monitoring runtime."
    )
    md.append("")
    md.append(
        "This is a stronger Q1-oriented contribution than a simple quantum-vs-classical "
        "accuracy comparison because it characterizes operational trade-offs under progressive "
        "drift rather than claiming universal dominance."
    )
    md.append("")

    md.append("## Final verdict")
    md.append("")
    md.append("Current positioning:")
    md.append("")
    md.append("- Q2 strong: yes.")
    md.append("- Q1 possible: yes, substantially more defensible than before.")
    md.append("- Q1 guaranteed: no.")
    md.append("- Top cybersecurity Q1 without external dataset: still risky.")
    md.append("")
    md.append(
        "The main remaining limitation is that all multi-scenario validation is still within "
        "CICIDS2017. A second external dataset would further strengthen the Q1 case, but the "
        "current paper is now a coherent and defensible submission candidate if targeted carefully."
    )
    md.append("")

    md.append("## Final core claim")
    md.append("")
    md.append(
        "QK-MMD ZZ provides regime-dependent advantages for adaptive IDS drift monitoring. "
        "Across multiple CICIDS2017 progressive-drift regimes, it is consistently competitive "
        "with strong classical distributional detectors. In some regimes, it improves "
        "readaptation efficiency; in others, it improves downstream performance at additional "
        "adaptation and monitoring cost."
    )
    md.append("")

    md.append("## Multi-scenario evidence")
    md.append("")
    md.append(preview(
        qk_summary,
        cols=[
            "scenario",
            "method_label",
            "n_seeds",
            "mean_balanced_accuracy",
            "cumulative_error_area_mean",
            "cumulative_gain_vs_no_adapt_mean",
            "n_adaptations_mean",
            "adaptation_efficiency_mean",
            "detector_runtime_sec_total_mean",
        ],
    ))
    md.append("")

    md.append("## QK-MMD ZZ vs Energy distance")
    md.append("")
    md.append(preview(
        qk_vs_energy,
        cols=[
            "scenario",
            "method_a",
            "method_b",
            "metric",
            "n_pairs",
            "mean_diff_a_minus_b",
            "ci95_low",
            "ci95_high",
            "positive_means",
            "ci_excludes_zero_positive",
        ],
    ))
    md.append("")

    md.append("## Scenario-specific interpretation")
    md.append("")
    md.append("### Wednesday")
    md.append("")
    md.append(
        "QK-MMD ZZ and Energy distance are statistically tied in downstream performance. "
        "However, QK-MMD ZZ requires significantly fewer readaptations and achieves "
        "significantly higher adaptation efficiency. This is the clearest operational "
        "efficiency scenario."
    )
    md.append("")
    md.append("### PortScan")
    md.append("")
    md.append(
        "QK-MMD ZZ significantly improves downstream balanced accuracy, cumulative "
        "degradation, and cumulative gain relative to Energy distance. However, it uses "
        "more readaptations and has lower adaptation efficiency than Energy distance. "
        "This is a performance-gain scenario rather than an efficiency-gain scenario."
    )
    md.append("")
    md.append("### DDoS")
    md.append("")
    md.append(
        "QK-MMD ZZ and Energy distance are statistically tied in raw downstream performance, "
        "but QK-MMD ZZ requires significantly fewer readaptations and achieves significantly "
        "higher adaptation efficiency. This mirrors the Wednesday operational-efficiency pattern."
    )
    md.append("")

    md.append("## Cost-sensitive utility")
    md.append("")
    md.append(
        "The cost-sensitive utility analysis uses: "
        "`utility = cumulative_gain_vs_no_adapt - lambda * n_adaptations - gamma * detector_runtime_sec_total`."
    )
    md.append("")
    md.append(
        "Strict positive regions indicate settings where QK-MMD ZZ has a positive bootstrap "
        "CI lower bound against the corresponding baseline."
    )
    md.append("")
    md.append(preview(
        utility_focus,
        cols=[
            "scenario",
            "baseline",
            "lambda_cost",
            "gamma_cost",
            "mean_utility_diff_qk_minus_baseline",
            "ci95_low",
            "ci95_high",
            "qk_better_ci95",
        ],
        n=120,
    ))
    md.append("")
    md.append(
        "Utility favors QK-MMD ZZ most clearly in Wednesday and DDoS when readaptation cost "
        "is non-negligible. In PortScan, QK-MMD ZZ wins raw performance but loses part of "
        "the utility advantage once readaptation and runtime costs are strongly penalized."
    )
    md.append("")

    md.append("## Claims supported")
    md.append("")
    md.append("1. Triggered readaptation reduces degradation relative to no adaptation.")
    md.append("2. QK-MMD ZZ is consistently competitive across multiple CICIDS2017 drift regimes.")
    md.append("3. QK-MMD ZZ matches or exceeds Energy distance depending on the drift regime.")
    md.append("4. In Wednesday and DDoS, QK-MMD ZZ improves adaptation efficiency over Energy distance.")
    md.append("5. In PortScan, QK-MMD ZZ significantly improves downstream performance over Energy distance.")
    md.append("6. QK-MMD ZZ has substantially higher detector runtime.")
    md.append("7. The quantum-kernel benefit is regime-dependent, not universal.")
    md.append("8. Cost-sensitive utility can favor QK-MMD ZZ when readaptation cost is operationally relevant.")
    md.append("")

    md.append("## Claims to avoid")
    md.append("")
    md.append("1. Universal quantum advantage.")
    md.append("2. QK-MMD always detects earlier.")
    md.append("3. QK-MMD always improves final downstream accuracy.")
    md.append("4. QK-MMD is computationally cheaper.")
    md.append("5. Classical baselines are weak.")
    md.append("6. QK-MMD ZZ is always more adaptation-efficient.")
    md.append("")

    md.append("## Main reviewer risks")
    md.append("")
    md.append("1. All multi-scenario validation is still within CICIDS2017.")
    md.append("2. Energy distance is extremely competitive and much cheaper.")
    md.append("3. QK-MMD ZZ is simulated and has higher runtime.")
    md.append("4. The advantage changes by regime, which must be framed as a finding, not as inconsistency.")
    md.append("5. The utility analysis depends on cost assumptions.")
    md.append("")

    md.append("## Recommended title direction")
    md.append("")
    md.append(
        "Regime-Dependent Quantum-Kernel Drift Monitoring for Efficient Adaptive Intrusion Detection"
    )
    md.append("")
    md.append("Alternative:")
    md.append("")
    md.append(
        "Quantum-Kernel MMD for Progressive Drift Monitoring in Adaptive Intrusion Detection: "
        "A Cost-Sensitive Multi-Regime Study"
    )
    md.append("")

    md.append("## Recommended paper framing")
    md.append("")
    md.append(
        "Frame the paper as an adaptive drift-monitoring study, not as a universal quantum "
        "advantage paper. The contribution is the detailed characterization of when quantum "
        "kernel discrepancy signals are useful, how they compare to strong classical "
        "distributional baselines, and under which operational cost regimes they become "
        "preferable."
    )
    md.append("")

    md.append("## Recommended next step")
    md.append("")
    md.append(
        "At this point, do not add more CICIDS2017 scenarios. The next decision is strategic: "
        "either start drafting the paper with the current multi-scenario CICIDS2017 evidence, "
        "or add one external dataset if the goal is to maximize Q1 confidence."
    )
    md.append("")
    md.append(
        "If time is limited, start drafting. If Q1 confidence is the priority, add one external "
        "dataset after the paper structure is already outlined."
    )
    md.append("")

    out_path = NOTES_DIR / "paper2_final_q1_synthesis_checkpoint_003.md"
    out_path.write_text("\n".join(md), encoding="utf-8")

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
