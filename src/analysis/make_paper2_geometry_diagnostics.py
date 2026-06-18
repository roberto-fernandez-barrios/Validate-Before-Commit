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


def detector_method_label(row: pd.Series) -> str:
    detector = str(row.get("detector", ""))
    qmap = row.get("q_feature_map", "")

    if pd.isna(qmap):
        qmap = ""

    qmap = str(qmap)

    if detector == "mmd_rbf":
        return "MMD-RBF"

    if detector == "qk_mmd" and qmap == "zz":
        return "QK-MMD ZZ"

    if detector == "qk_mmd" and qmap == "pauli_xz":
        return "QK-MMD PauliXZ"

    return f"{detector}:{qmap}"


def downstream_method_label(strategy: str) -> str:
    if strategy == "mmd_rbf_triggered_adaptation":
        return "MMD-RBF"

    if strategy == "qk_mmd_zz_triggered_adaptation":
        return "QK-MMD ZZ"

    if strategy == "qk_mmd_pauli_xz_triggered_adaptation":
        return "QK-MMD PauliXZ"

    if strategy == "hybrid_or_triggered_adaptation":
        return "Hybrid OR"

    if strategy == "hybrid_vote_2of3_triggered_adaptation":
        return "Hybrid Vote 2/3"

    if strategy == "hybrid_and_triggered_adaptation":
        return "Hybrid AND"

    return strategy


def find_score_window_file() -> Path:
    candidates = [
        Path("results/raw/paper2_adaptive_monitor_final_001/paper2_adaptive_monitor_window_results.csv"),
        Path("results/raw/paper2_controlled_streaming_final_001/paper2_controlled_streaming_window_results.csv"),
    ]

    for path in candidates:
        if path.exists():
            return path

    # Fallback: search for a window file with score/threshold/phase.
    for path in sorted(Path("results/raw").glob("**/*window_results.csv")):
        try:
            header = pd.read_csv(path, nrows=0)
        except Exception:
            continue

        cols = set(header.columns)
        if {"score", "threshold", "phase", "severity", "detector"}.issubset(cols):
            return path

    raise FileNotFoundError("Could not find a score window results file.")


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


def save_scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    xlabel: str,
    ylabel: str,
    title: str,
    out_base: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.6))

    for method, g in df.groupby("method", sort=False):
        ax.scatter(g[x_col], g[y_col], label=method)
        for _, row in g.iterrows():
            ax.annotate(
                str(row["severity"]),
                (row[x_col], row[y_col]),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
            )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()

    fig.savefig(out_base.with_suffix(".png"), dpi=300)
    fig.savefig(out_base.with_suffix(".pdf"))
    plt.close(fig)


def main() -> None:
    figures_dir = Path("results/figures/paper2_geometry_diagnostics_001")
    tables_dir = Path("results/tables/paper2_geometry_diagnostics_001")
    notes_dir = Path("notes")

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    score_path = find_score_window_file()
    print(f"Using score window file: {score_path}")

    score_df = pd.read_csv(score_path)

    required_cols = {"severity", "detector", "phase", "score", "threshold", "alarm"}
    missing = required_cols - set(score_df.columns)

    if missing:
        raise ValueError(f"Score file is missing required columns: {sorted(missing)}")

    score_df["method"] = score_df.apply(detector_method_label, axis=1)
    score_df["score_ratio"] = score_df["score"] / score_df["threshold"].replace(0, pd.NA)
    score_df["score_ratio"] = pd.to_numeric(score_df["score_ratio"], errors="coerce")

    # Keep only pre/post drift phases for separation.
    phase_values = set(score_df["phase"].astype(str).unique())
    print(f"Detected phases: {sorted(phase_values)}")

    usable_phases = [p for p in ["pre", "post"] if p in phase_values]

    if len(usable_phases) < 2:
        raise ValueError(
            "Need both 'pre' and 'post' phases for score separation. "
            f"Available phases: {sorted(phase_values)}"
        )

    score_phase_summary = (
        score_df[score_df["phase"].isin(["pre", "post"])]
        .groupby(["severity", "method", "phase"], dropna=False)
        .agg(
            n_windows=("score", "size"),
            score_mean=("score", "mean"),
            score_std=("score", "std"),
            threshold_mean=("threshold", "mean"),
            score_ratio_mean=("score_ratio", "mean"),
            score_ratio_std=("score_ratio", "std"),
            alarm_rate=("alarm", "mean"),
        )
        .reset_index()
    )

    save_table(
        score_phase_summary,
        tables_dir / "paper_table_geometry_score_phase_summary",
    )

    pivot = score_phase_summary.pivot_table(
        index=["severity", "method"],
        columns="phase",
        values=["score_ratio_mean", "alarm_rate"],
    )

    pivot.columns = [f"{a}_{b}" for a, b in pivot.columns]
    pivot = pivot.reset_index()

    pivot["score_ratio_gap_post_minus_pre"] = (
        pivot["score_ratio_mean_post"] - pivot["score_ratio_mean_pre"]
    )

    pivot["alarm_rate_gap_post_minus_pre"] = (
        pivot["alarm_rate_post"] - pivot["alarm_rate_pre"]
    )

    score_separation = pivot.sort_values(["severity", "method"])

    save_table(
        score_separation,
        tables_dir / "paper_table_geometry_score_separation",
    )

    save_line_plot(
        score_separation,
        y_col="score_ratio_gap_post_minus_pre",
        ylabel="Post-pre score/threshold gap",
        title="Geometry score separation across drift severity",
        out_base=figures_dir / "score_ratio_gap_vs_severity",
    )

    save_line_plot(
        score_separation,
        y_col="alarm_rate_post",
        ylabel="Post-drift alarm rate",
        title="Post-drift alarm rate across severity",
        out_base=figures_dir / "post_alarm_rate_vs_severity",
    )

    save_line_plot(
        score_separation,
        y_col="alarm_rate_pre",
        ylabel="Pre-drift alarm rate",
        title="Pre-drift false alarm rate across severity",
        out_base=figures_dir / "pre_alarm_rate_vs_severity",
    )

    # Join with downstream final global summary.
    downstream_path = Path(
        "results/raw/paper2_downstream_adaptation_final_global_001/"
        "paper2_downstream_final_global_summary.csv"
    )

    if downstream_path.exists():
        downstream = pd.read_csv(downstream_path)
        downstream = downstream[
            downstream["strategy"].str.contains("triggered_adaptation", na=False)
        ].copy()

        downstream["method"] = downstream["strategy"].map(downstream_method_label)

        downstream = downstream[
            downstream["method"].isin(["MMD-RBF", "QK-MMD ZZ", "QK-MMD PauliXZ"])
        ].copy()

        downstream_cols = [
            "severity",
            "method",
            "post_balanced_accuracy_mean",
            "degradation_area_mean",
            "adaptation_gain_vs_no_adapt_mean",
            "clean_downstream_adaptation_rate",
            "clean_adaptation_gain_mean",
            "false_alarm_any_rate",
            "trigger_delay_windows_mean",
        ]

        joined = score_separation.merge(
            downstream[downstream_cols],
            on=["severity", "method"],
            how="inner",
        )

        save_table(
            joined,
            tables_dir / "paper_table_geometry_vs_downstream",
        )

        save_scatter_plot(
            joined,
            x_col="score_ratio_gap_post_minus_pre",
            y_col="clean_adaptation_gain_mean",
            xlabel="Post-pre score/threshold gap",
            ylabel="Clean downstream adaptation gain",
            title="Geometry score separation vs downstream gain",
            out_base=figures_dir / "score_gap_vs_clean_gain",
        )

        save_scatter_plot(
            joined,
            x_col="alarm_rate_post",
            y_col="clean_adaptation_gain_mean",
            xlabel="Post-drift alarm rate",
            ylabel="Clean downstream adaptation gain",
            title="Post-drift alarm rate vs downstream gain",
            out_base=figures_dir / "post_alarm_rate_vs_clean_gain",
        )

        corr_rows = []

        for method, g in joined.groupby("method"):
            if len(g) >= 3:
                corr_rows.append(
                    {
                        "method": method,
                        "n": len(g),
                        "spearman_score_gap_vs_clean_gain": g[
                            "score_ratio_gap_post_minus_pre"
                        ].corr(g["clean_adaptation_gain_mean"], method="spearman"),
                        "pearson_score_gap_vs_clean_gain": g[
                            "score_ratio_gap_post_minus_pre"
                        ].corr(g["clean_adaptation_gain_mean"], method="pearson"),
                        "spearman_alarm_rate_vs_clean_gain": g[
                            "alarm_rate_post"
                        ].corr(g["clean_adaptation_gain_mean"], method="spearman"),
                        "pearson_alarm_rate_vs_clean_gain": g[
                            "alarm_rate_post"
                        ].corr(g["clean_adaptation_gain_mean"], method="pearson"),
                    }
                )

        corr_df = pd.DataFrame(corr_rows)
        save_table(
            corr_df,
            tables_dir / "paper_table_geometry_downstream_correlations",
        )

    else:
        joined = pd.DataFrame()
        corr_df = pd.DataFrame()
        print(f"Downstream summary not found: {downstream_path}")

    # Join with controlled streaming AUC if present.
    auc_path = Path(
        "results/tables/paper2_controlled_streaming_final_001/"
        "paper_table_auc_by_severity.csv"
    )

    if auc_path.exists():
        auc_df = pd.read_csv(auc_path)

        if {"severity", "method", "pre_post_auc_mean"}.issubset(auc_df.columns):
            auc_joined = score_separation.merge(
                auc_df[["severity", "method", "pre_post_auc_mean", "score_gap_mean"]],
                on=["severity", "method"],
                how="inner",
            )

            save_table(
                auc_joined,
                tables_dir / "paper_table_geometry_vs_auc",
            )

            save_scatter_plot(
                auc_joined,
                x_col="score_ratio_gap_post_minus_pre",
                y_col="pre_post_auc_mean",
                xlabel="Post-pre score/threshold gap",
                ylabel="Pre/post AUC",
                title="Geometry score gap vs pre/post AUC",
                out_base=figures_dir / "score_gap_vs_auc",
            )

    note_lines = [
        "# Paper 2 geometry diagnostics checkpoint 001",
        "",
        "## Objective",
        "",
        "This diagnostic block connects detector score geometry with downstream",
        "adaptive utility.",
        "",
        "The main quantities are:",
        "",
        "- score_ratio = score / threshold",
        "- score_ratio_gap = post_score_ratio_mean - pre_score_ratio_mean",
        "- post-drift alarm rate",
        "- clean downstream adaptation gain",
        "- degradation area",
        "",
        f"Score window source: `{score_path}`",
        "",
        "## Generated artifacts",
        "",
        f"- Figures: `{figures_dir}`",
        f"- Tables: `{tables_dir}`",
        "",
    ]

    if not joined.empty:
        note_lines.extend(
            [
                "## Geometry/downstream interpretation",
                "",
                "The table `paper_table_geometry_vs_downstream.csv` joins detector",
                "score separation with downstream adaptation metrics.",
                "",
                "Use this to assess whether detectors with stronger post/pre score",
                "separation also produce higher clean adaptation gain or lower",
                "degradation area.",
                "",
            ]
        )

    if not corr_df.empty:
        note_lines.extend(
            [
                "## Correlations",
                "",
                "Correlation values are stored in:",
                "",
                "- `paper_table_geometry_downstream_correlations.csv`",
                "",
                "These values should be interpreted cautiously because the number of",
                "severity points per detector is small.",
                "",
            ]
        )

    note_lines.extend(
        [
            "## Paper usage",
            "",
            "This block should not be presented as a standalone performance claim.",
            "It is an explanatory diagnostic supporting the regime-dependent",
            "interpretation of QK-MMD and MMD-RBF behavior.",
            "",
        ]
    )

    note_path = notes_dir / "paper2_geometry_diagnostics_checkpoint_001.md"
    note_path.write_text("\n".join(note_lines), encoding="utf-8")

    print(f"Saved figures in: {figures_dir}")
    print(f"Saved tables in: {tables_dir}")
    print(f"Saved note: {note_path}")


if __name__ == "__main__":
    main()
