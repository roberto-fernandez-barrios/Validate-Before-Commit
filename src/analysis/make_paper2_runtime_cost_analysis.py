from __future__ import annotations

from pathlib import Path

import pandas as pd


def escape_latex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    out = str(value)
    for old, new in replacements.items():
        out = out.replace(old, new)
    return out


def format_cell(value) -> str:
    if pd.isna(value):
        return ""

    if isinstance(value, float):
        return f"{value:.4f}"

    return escape_latex(str(value))


def write_latex_table(df: pd.DataFrame, path: Path) -> None:
    cols = list(df.columns)
    lines = []
    lines.append(r"\begin{tabular}{" + "l" * len(cols) + "}")
    lines.append(r"\toprule")
    lines.append(" & ".join(escape_latex(c) for c in cols) + r" \\")
    lines.append(r"\midrule")

    for _, row in df.iterrows():
        lines.append(" & ".join(format_cell(row[c]) for c in cols) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def save_table(df: pd.DataFrame, base: Path) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(base.with_suffix(".csv"), index=False)
    write_latex_table(df, base.with_suffix(".tex"))


def method_label(strategy: str) -> str:
    if strategy == "mmd_rbf_triggered_adaptation":
        return "MMD-RBF"
    if strategy == "qk_mmd_zz_triggered_adaptation":
        return "QK-MMD ZZ"
    if strategy == "qk_mmd_pauli_xz_triggered_adaptation":
        return "QK-MMD PauliXZ"
    if strategy == "hybrid_or_triggered_adaptation":
        return "Hybrid OR"
    return strategy


def main() -> None:
    outdir = Path("results/tables/paper2_runtime_cost_001")
    notes_dir = Path("notes")
    outdir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    summary_path = Path(
        "results/raw/paper2_downstream_adaptation_final_global_001/"
        "paper2_downstream_final_global_summary.csv"
    )

    strict_path = Path(
        "results/tables/paper2_operational_scale_impact_001/"
        "paper_table_quantum_strict_operational_zones.csv"
    )

    if not summary_path.exists():
        raise FileNotFoundError(summary_path)

    summary = pd.read_csv(summary_path)
    summary["method"] = summary["strategy"].map(method_label)

    runtime = summary[
        summary["strategy"].isin(
            [
                "mmd_rbf_triggered_adaptation",
                "qk_mmd_zz_triggered_adaptation",
                "qk_mmd_pauli_xz_triggered_adaptation",
            ]
        )
    ].copy()

    runtime_cols = [
        "severity",
        "strategy",
        "method",
        "n_seeds",
        "detector_runtime_sec_mean",
        "initial_fit_runtime_sec_mean",
        "adapted_fit_runtime_sec_mean",
        "post_balanced_accuracy_mean",
        "degradation_area_mean",
        "clean_downstream_adaptation_rate",
        "clean_adaptation_gain_mean",
        "false_alarm_any_rate",
        "trigger_delay_windows_mean",
    ]

    runtime = runtime[[c for c in runtime_cols if c in runtime.columns]].sort_values(
        ["severity", "method"]
    )

    save_table(runtime, outdir / "paper_table_runtime_by_method")

    # Runtime ratios vs MMD-RBF per severity.
    ratio_rows = []

    for severity, g in runtime.groupby("severity"):
        mmd = g[g["method"] == "MMD-RBF"]

        if mmd.empty:
            continue

        mmd_row = mmd.iloc[0]
        mmd_runtime = float(mmd_row["detector_runtime_sec_mean"])

        for _, row in g.iterrows():
            method_runtime = float(row["detector_runtime_sec_mean"])

            ratio_rows.append(
                {
                    "severity": severity,
                    "method": row["method"],
                    "detector_runtime_sec_mean": method_runtime,
                    "mmd_runtime_sec_mean": mmd_runtime,
                    "runtime_ratio_vs_mmd": method_runtime / mmd_runtime
                    if mmd_runtime > 0
                    else pd.NA,
                    "extra_runtime_sec_vs_mmd": method_runtime - mmd_runtime,
                    "clean_gain_delta_vs_mmd": float(row["clean_adaptation_gain_mean"])
                    - float(mmd_row["clean_adaptation_gain_mean"]),
                    "false_alarm_delta_vs_mmd": float(row["false_alarm_any_rate"])
                    - float(mmd_row["false_alarm_any_rate"]),
                    "trigger_delay_delta_vs_mmd": float(row["trigger_delay_windows_mean"])
                    - float(mmd_row["trigger_delay_windows_mean"]),
                }
            )

    ratio_df = pd.DataFrame(ratio_rows)
    save_table(ratio_df, outdir / "paper_table_runtime_ratio_vs_mmd")

    # Join strict operational zones with runtime.
    if strict_path.exists():
        strict = pd.read_csv(strict_path)

        strict_join = strict.merge(
            ratio_df[
                [
                    "severity",
                    "method",
                    "detector_runtime_sec_mean",
                    "mmd_runtime_sec_mean",
                    "runtime_ratio_vs_mmd",
                    "extra_runtime_sec_vs_mmd",
                ]
            ],
            on=["severity", "method"],
            how="left",
        )

        strict_join["additional_detected_per_extra_runtime_sec"] = (
            strict_join["additional_detected_flow_equiv_vs_mmd"]
            / strict_join["extra_runtime_sec_vs_mmd"].replace(0, pd.NA)
        )

        paper_cols = [
            "severity",
            "method",
            "traffic_volume",
            "post_alarm_delta_vs_mmd",
            "additional_detected_flow_equiv_vs_mmd",
            "clean_gain_delta_vs_mmd",
            "false_alarm_delta_vs_mmd",
            "runtime_ratio_vs_mmd",
            "extra_runtime_sec_vs_mmd",
            "additional_detected_per_extra_runtime_sec",
        ]

        strict_paper = strict_join[[c for c in paper_cols if c in strict_join.columns]]
        strict_paper = strict_paper.sort_values(
            ["severity", "method", "traffic_volume"]
        )

        save_table(strict_paper, outdir / "paper_table_runtime_cost_benefit_strict_zones")

    note_lines = [
        "# Paper 2 runtime/cost analysis checkpoint 001",
        "",
        "## Purpose",
        "",
        "This analysis summarizes detector runtime and compares the operational",
        "monitoring benefit of QK-MMD against its additional detector runtime cost.",
        "",
        "## Generated tables",
        "",
        f"- `{outdir / 'paper_table_runtime_by_method.csv'}`",
        f"- `{outdir / 'paper_table_runtime_ratio_vs_mmd.csv'}`",
        f"- `{outdir / 'paper_table_runtime_cost_benefit_strict_zones.csv'}`",
        "",
        "## Interpretation",
        "",
        "The paper should not claim that QK-MMD is computationally cheaper than",
        "MMD-RBF. Instead, the correct cost-benefit claim is that QK-MMD may be",
        "worth using as a specialized severe-drift monitor when the operational",
        "cost of missing drift is high enough to justify the additional detector",
        "runtime.",
        "",
        "The strict operational zones should therefore be discussed together with",
        "runtime ratios, not in isolation.",
        "",
    ]

    note_path = notes_dir / "paper2_runtime_cost_checkpoint_001.md"
    note_path.write_text("\n".join(note_lines), encoding="utf-8")

    print(f"Saved tables in: {outdir}")
    print(f"Saved note: {note_path}")

    print()
    print("=== RUNTIME RATIO VS MMD ===")
    print(ratio_df.to_string(index=False))


if __name__ == "__main__":
    main()
