from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


SUMMARY_PATH = Path("results/raw/paper2_adaptive_monitor_final_001/paper2_adaptive_monitor_summary.csv")
FIG_DIR = Path("results/figures/paper2_adaptive_monitor_final_001")
TABLE_DIR = Path("results/tables/paper2_adaptive_monitor_final_001")

FIG_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


def method_label(row: pd.Series) -> str:
    detector = str(row["detector"])
    qmap = row.get("q_feature_map")

    if detector == "mmd_rbf":
        return "MMD-RBF"

    if detector == "qk_mmd":
        if pd.isna(qmap) or str(qmap).strip() == "":
            return "QK-MMD"
        if str(qmap) == "pauli_xz":
            return "QK-MMD PauliXZ"
        return f"QK-MMD {str(qmap).upper()}"

    return detector


def latex_escape(value: object) -> str:
    text = str(value)
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
    for old, new_value in replacements.items():
        text = text.replace(old, new_value)
    return text


def format_latex_value(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return latex_escape(value)


def save_latex_table(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    col_spec = "l" * len(df.columns)

    lines = [
        r"\begin{table}",
        r"\centering",
        rf"\caption{{{latex_escape(caption)}}}",
        rf"\label{{{latex_escape(label)}}}",
        rf"\begin{{tabular}}{{{col_spec}}}",
        r"\toprule",
        " & ".join(latex_escape(col) for col in df.columns) + r" \\",
        r"\midrule",
    ]

    for _, row in df.iterrows():
        lines.append(" & ".join(format_latex_value(row[col]) for col in df.columns) + r" \\")

    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def plot_metric(df: pd.DataFrame, metric: str, ylabel: str, filename: str) -> None:
    plt.figure(figsize=(7, 4.5))

    for method, group in df.groupby("method", sort=False):
        group = group.sort_values("severity")
        plt.plot(group["severity"], group[metric], marker="o", label=method)

    plt.xlabel("Controlled drift severity")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(FIG_DIR / f"{filename}.png", dpi=300)
    plt.savefig(FIG_DIR / f"{filename}.pdf")
    plt.close()


def main() -> None:
    df = pd.read_csv(SUMMARY_PATH)
    df["method"] = df.apply(method_label, axis=1)

    columns = [
        "severity",
        "method",
        "n_seeds",
        "false_alarm_any_rate",
        "post_detect_any_rate",
        "post_adapt_alarm_any_rate",
        "adaptation_success_rate",
        "clean_adaptation_success_rate",
        "delay_windows_mean",
        "post_alarm_rate_mean",
        "post_adapt_alarm_rate_mean",
        "score_reduction_after_adaptation_mean",
    ]

    table = df[columns].copy()
    table = table.sort_values(["severity", "method"])

    table_csv = TABLE_DIR / "paper_table_adaptive_monitor_summary.csv"
    table_tex = TABLE_DIR / "paper_table_adaptive_monitor_summary.tex"

    table.to_csv(table_csv, index=False)
    save_latex_table(
        table,
        table_tex,
        caption="Adaptive monitor performance under controlled benign-only temporal drift.",
        label="tab:paper2_adaptive_monitor_summary",
    )

    best = (
        table
        .sort_values(
            [
                "severity",
                "clean_adaptation_success_rate",
                "false_alarm_any_rate",
                "delay_windows_mean",
            ],
            ascending=[True, False, True, True],
        )
        .groupby("severity", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )

    best_csv = TABLE_DIR / "paper_table_best_clean_adaptation_by_severity.csv"
    best_tex = TABLE_DIR / "paper_table_best_clean_adaptation_by_severity.tex"

    best.to_csv(best_csv, index=False)
    save_latex_table(
        best,
        best_tex,
        caption="Best clean adaptive-monitoring policy by drift severity.",
        label="tab:paper2_best_clean_adaptation",
    )

    plot_metric(
        df,
        metric="clean_adaptation_success_rate",
        ylabel="Clean adaptation success rate",
        filename="clean_adaptation_success_vs_severity",
    )

    plot_metric(
        df,
        metric="post_detect_any_rate",
        ylabel="Post-drift detection rate",
        filename="post_detection_rate_vs_severity",
    )

    plot_metric(
        df,
        metric="post_adapt_alarm_any_rate",
        ylabel="Post-adaptation alarm rate",
        filename="post_adapt_alarm_rate_vs_severity",
    )

    plot_metric(
        df,
        metric="score_reduction_after_adaptation_mean",
        ylabel="Mean score reduction after adaptation",
        filename="score_reduction_after_adaptation_vs_severity",
    )

    print("Saved figures:")
    for path in sorted(FIG_DIR.iterdir()):
        print(f" - {path}")

    print()
    print("Saved tables:")
    for path in sorted(TABLE_DIR.iterdir()):
        print(f" - {path}")


if __name__ == "__main__":
    main()
