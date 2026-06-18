from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
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


def format_latex_cell(value) -> str:
    if pd.isna(value):
        return ""

    if isinstance(value, float):
        return f"{value:.4f}"

    return escape_latex(str(value))


def write_latex_table(df: pd.DataFrame, path: Path) -> None:
    columns = list(df.columns)

    lines = []
    lines.append(r"\begin{tabular}{" + "l" * len(columns) + "}")
    lines.append(r"\toprule")
    lines.append(" & ".join(escape_latex(c) for c in columns) + r" \\")
    lines.append(r"\midrule")

    for _, row in df.iterrows():
        lines.append(" & ".join(format_latex_cell(row[c]) for c in columns) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def save_table(df: pd.DataFrame, out_base: Path) -> None:
    df.to_csv(out_base.with_suffix(".csv"), index=False)
    write_latex_table(df, out_base.with_suffix(".tex"))


def method_label(strategy: str) -> str:
    if strategy == "no_adaptation":
        return "No adaptation"
    if strategy == "oracle_adaptation":
        return "Oracle adaptation"
    if strategy == "mmd_rbf_triggered_adaptation":
        return "MMD-RBF"
    if strategy == "qk_mmd_zz_triggered_adaptation":
        return "QK-MMD ZZ"
    if strategy == "qk_mmd_pauli_xz_triggered_adaptation":
        return "QK-MMD PauliXZ"
    return strategy


def save_line_plot(
    df: pd.DataFrame,
    y_col: str,
    ylabel: str,
    title: str,
    out_base: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.4))

    for method, g in df.groupby("method", sort=False):
        g = g.sort_values("severity")
        ax.plot(g["severity"], g[y_col], marker="o", label=method)

    ax.set_xlabel("Severity")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()

    fig.savefig(out_base.with_suffix(".png"), dpi=300)
    fig.savefig(out_base.with_suffix(".pdf"))
    plt.close(fig)


def get_row(df: pd.DataFrame, severity: float, method: str) -> pd.Series:
    m = df[(df["severity"] == severity) & (df["method"].astype(str) == method)]
    if m.empty:
        raise ValueError(f"Missing row severity={severity}, method={method}")
    return m.iloc[0]


def main() -> None:
    optimized_path = Path(
        "results/raw/paper2_downstream_adaptation_final_optimized_001/"
        "paper2_downstream_final_optimized_summary.csv"
    )

    global_path = Path(
        "results/raw/paper2_downstream_adaptation_final_global_001/"
        "paper2_downstream_final_global_summary.csv"
    )

    if not optimized_path.exists():
        raise FileNotFoundError(optimized_path)

    optimized = pd.read_csv(optimized_path)
    optimized["method"] = optimized["strategy"].map(method_label)
    optimized["policy_setting"] = "detector_specific_optimized"

    method_order = [
        "No adaptation",
        "MMD-RBF",
        "QK-MMD ZZ",
        "QK-MMD PauliXZ",
        "Oracle adaptation",
    ]

    optimized["method"] = pd.Categorical(
        optimized["method"],
        categories=method_order,
        ordered=True,
    )

    optimized = optimized.sort_values(["severity", "method"])

    figures_dir = Path("results/figures/paper2_downstream_adaptation_final_optimized_001")
    tables_dir = Path("results/tables/paper2_downstream_adaptation_final_optimized_001")
    notes_dir = Path("notes")

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    table_cols = [
        "severity",
        "method",
        "threshold_quantile",
        "consecutive_k",
        "n_seeds",
        "post_balanced_accuracy_mean",
        "degradation_area_mean",
        "adaptation_gain_vs_no_adapt_mean",
        "clean_downstream_adaptation_rate",
        "clean_adaptation_gain_mean",
        "triggered_post_rate",
        "false_alarm_any_rate",
        "trigger_delay_windows_mean",
    ]

    save_table(
        optimized[table_cols],
        tables_dir / "paper_table_downstream_optimized_summary",
    )

    triggered = optimized[
        optimized["strategy"].str.contains("triggered_adaptation", na=False)
    ].copy()

    save_table(
        triggered[table_cols],
        tables_dir / "paper_table_downstream_optimized_triggered_only",
    )

    best_by_severity = (
        triggered
        .sort_values(
            [
                "severity",
                "clean_adaptation_gain_mean",
                "clean_downstream_adaptation_rate",
                "false_alarm_any_rate",
                "trigger_delay_windows_mean",
            ],
            ascending=[True, False, False, True, True],
        )
        .groupby("severity", as_index=False)
        .head(1)
    )

    save_table(
        best_by_severity[table_cols],
        tables_dir / "paper_table_downstream_optimized_best_by_severity",
    )

    save_line_plot(
        optimized,
        y_col="post_balanced_accuracy_mean",
        ylabel="Post-drift balanced accuracy",
        title="Detector-specific optimized downstream adaptation",
        out_base=figures_dir / "optimized_post_balanced_accuracy_vs_severity",
    )

    save_line_plot(
        optimized,
        y_col="degradation_area_mean",
        ylabel="Degradation area",
        title="Detector-specific optimized degradation area",
        out_base=figures_dir / "optimized_degradation_area_vs_severity",
    )

    save_line_plot(
        triggered,
        y_col="clean_adaptation_gain_mean",
        ylabel="Clean adaptation gain",
        title="Detector-specific optimized clean adaptation gain",
        out_base=figures_dir / "optimized_clean_adaptation_gain_vs_severity",
    )

    save_line_plot(
        triggered,
        y_col="clean_downstream_adaptation_rate",
        ylabel="Clean adaptation rate",
        title="Detector-specific optimized clean adaptation rate",
        out_base=figures_dir / "optimized_clean_adaptation_rate_vs_severity",
    )

    save_line_plot(
        triggered,
        y_col="false_alarm_any_rate",
        ylabel="False alarm rate",
        title="Detector-specific optimized false alarm rate",
        out_base=figures_dir / "optimized_false_alarm_rate_vs_severity",
    )

    comparison_note = ""

    if global_path.exists():
        global_df = pd.read_csv(global_path)
        global_df["method"] = global_df["strategy"].map(method_label)
        global_df["policy_setting"] = "global_q0.95_k3"

        optimized_compare = triggered.copy()
        global_compare = global_df[
            global_df["strategy"].str.contains("triggered_adaptation", na=False)
        ].copy()

        compare_cols = [
            "severity",
            "method",
            "policy_setting",
            "threshold_quantile",
            "consecutive_k",
            "post_balanced_accuracy_mean",
            "degradation_area_mean",
            "clean_downstream_adaptation_rate",
            "clean_adaptation_gain_mean",
            "false_alarm_any_rate",
            "trigger_delay_windows_mean",
        ]

        comparison = pd.concat(
            [
                global_compare[compare_cols],
                optimized_compare[compare_cols],
            ],
            ignore_index=True,
        ).sort_values(["severity", "method", "policy_setting"])

        save_table(
            comparison,
            tables_dir / "paper_table_downstream_global_vs_optimized_triggered",
        )

        comparison_note = """
## Global vs detector-specific optimized policies

The global policy uses the same q/k trigger rule for all detectors. The
detector-specific optimized setting uses policies selected on tuning seeds for
each detector separately.

The optimized setting is useful as an operational upper-bound analysis, but the
global policy remains the cleaner main comparison because it avoids assigning
different trigger sensitivity rules to different detectors in the primary result.
"""

    mmd_025 = get_row(optimized, 0.25, "MMD-RBF")
    qkzz_025 = get_row(optimized, 0.25, "QK-MMD ZZ")
    qkpxz_025 = get_row(optimized, 0.25, "QK-MMD PauliXZ")

    mmd_10 = get_row(optimized, 1.0, "MMD-RBF")
    qkzz_10 = get_row(optimized, 1.0, "QK-MMD ZZ")
    qkpxz_10 = get_row(optimized, 1.0, "QK-MMD PauliXZ")

    note = f"""# Paper 2 downstream adaptation final optimized checkpoint 001

## Protocol

This checkpoint evaluates detector-specific optimized trigger policies.

Policy tuning seeds:

- 1-10

Final evaluation seeds:

- 11-40

Selected detector-specific policies:

- MMD-RBF:
  - threshold_quantile = 0.99
  - consecutive_k = 2

- QK-MMD ZZ:
  - threshold_quantile = 0.95
  - consecutive_k = 2

- QK-MMD PauliXZ:
  - threshold_quantile = 0.90
  - consecutive_k = 3

The final seeds are not used for policy selection.

{comparison_note}

## Main findings

At severity 0.25, MMD-RBF remains strongest:

- MMD-RBF:
  - balanced accuracy = {mmd_025["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {mmd_025["degradation_area_mean"]:.4f}
  - clean adaptation rate = {mmd_025["clean_downstream_adaptation_rate"]:.4f}
  - clean adaptation gain = {mmd_025["clean_adaptation_gain_mean"]:.4f}
  - false alarm rate = {mmd_025["false_alarm_any_rate"]:.4f}

- QK-MMD ZZ:
  - balanced accuracy = {qkzz_025["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {qkzz_025["degradation_area_mean"]:.4f}
  - clean adaptation rate = {qkzz_025["clean_downstream_adaptation_rate"]:.4f}
  - clean adaptation gain = {qkzz_025["clean_adaptation_gain_mean"]:.4f}
  - false alarm rate = {qkzz_025["false_alarm_any_rate"]:.4f}

- QK-MMD PauliXZ:
  - balanced accuracy = {qkpxz_025["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {qkpxz_025["degradation_area_mean"]:.4f}
  - clean adaptation rate = {qkpxz_025["clean_downstream_adaptation_rate"]:.4f}
  - clean adaptation gain = {qkpxz_025["clean_adaptation_gain_mean"]:.4f}
  - false alarm rate = {qkpxz_025["false_alarm_any_rate"]:.4f}

At severity 1.0:

- MMD-RBF:
  - balanced accuracy = {mmd_10["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {mmd_10["degradation_area_mean"]:.4f}
  - clean adaptation rate = {mmd_10["clean_downstream_adaptation_rate"]:.4f}
  - clean adaptation gain = {mmd_10["clean_adaptation_gain_mean"]:.4f}
  - false alarm rate = {mmd_10["false_alarm_any_rate"]:.4f}

- QK-MMD ZZ:
  - balanced accuracy = {qkzz_10["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {qkzz_10["degradation_area_mean"]:.4f}
  - clean adaptation rate = {qkzz_10["clean_downstream_adaptation_rate"]:.4f}
  - clean adaptation gain = {qkzz_10["clean_adaptation_gain_mean"]:.4f}
  - false alarm rate = {qkzz_10["false_alarm_any_rate"]:.4f}

- QK-MMD PauliXZ:
  - balanced accuracy = {qkpxz_10["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {qkpxz_10["degradation_area_mean"]:.4f}
  - clean adaptation rate = {qkpxz_10["clean_downstream_adaptation_rate"]:.4f}
  - clean adaptation gain = {qkpxz_10["clean_adaptation_gain_mean"]:.4f}
  - false alarm rate = {qkpxz_10["false_alarm_any_rate"]:.4f}

## Interpretation

Detector-specific optimization does not produce universal QK-MMD dominance.

Instead, it supports a regime-dependent interpretation:

- MMD-RBF is strongest in low-moderate downstream adaptation, especially at severity 0.25.
- QK-MMD ZZ is competitive with MMD-RBF in moderate-to-severe drift.
- QK-MMD PauliXZ provides the cleanest severe-drift adaptation behavior at severity 1.0, with high clean adaptation rate and low false alarm rate.
- The main paper should therefore emphasize complementarity and regime dependence, not universal quantum advantage.

## Recommended paper usage

Use the global policy result as the main downstream adaptation result.

Use this detector-specific optimized result as a secondary operational analysis or appendix.
"""

    note_path = notes_dir / "paper2_downstream_adaptation_final_optimized_checkpoint_001.md"
    note_path.write_text(note, encoding="utf-8")

    print(f"Saved figures in: {figures_dir}")
    print(f"Saved tables in: {tables_dir}")
    print(f"Saved note: {note_path}")


if __name__ == "__main__":
    main()
