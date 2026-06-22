from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


METHOD_LABELS = {
    "no_adaptation": "No adaptation",
    "mmd_rbf": "MMD-RBF",
    "qk_mmd_zz": "QK-MMD ZZ",
    "qk_mmd_pauli_xz": "QK-MMD PauliXZ",
}


def bootstrap_ci(values: np.ndarray, n_boot: int = 10000, seed: int = 123):
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0:
        return np.nan, np.nan, np.nan, np.nan

    rng = np.random.default_rng(seed)
    means = []

    for _ in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        means.append(np.mean(sample))

    means = np.asarray(means)

    return (
        float(np.mean(values)),
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
        float(np.mean(values > 0)),
    )


def paired_diff(
    df: pd.DataFrame,
    method_a: str,
    method_b: str,
    metric: str,
    interpretation: str,
    positive_means: str,
):
    a = df[df["method"] == method_a][["seed", metric]].rename(columns={metric: "a"})
    b = df[df["method"] == method_b][["seed", metric]].rename(columns={metric: "b"})

    merged = a.merge(b, on="seed", how="inner")
    merged["diff_a_minus_b"] = merged["a"] - merged["b"]

    mean, lo, hi, prob_gt0 = bootstrap_ci(merged["diff_a_minus_b"].to_numpy())

    return {
        "method_a": METHOD_LABELS.get(method_a, method_a),
        "method_b": METHOD_LABELS.get(method_b, method_b),
        "metric": metric,
        "n_pairs": int(len(merged)),
        "mean_diff_a_minus_b": mean,
        "ci95_low": lo,
        "ci95_high": hi,
        "prob_diff_gt_0": prob_gt0,
        "positive_means": positive_means,
        "interpretation": interpretation,
    }


def save_table(df: pd.DataFrame, path_no_ext: Path):
    path_no_ext.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path_no_ext.with_suffix(".csv"), index=False)

    try:
        df.to_latex(path_no_ext.with_suffix(".tex"), index=False, float_format="%.4f")
    except Exception as exc:
        print(f"[WARN] Could not write LaTeX table {path_no_ext}: {exc}")


def make_bar_plot(summary: pd.DataFrame, metric: str, ylabel: str, outpath: Path):
    plot_df = summary.copy()
    plot_df["method_label"] = plot_df["method"].map(METHOD_LABELS).fillna(plot_df["method"])

    order = ["No adaptation", "MMD-RBF", "QK-MMD PauliXZ", "QK-MMD ZZ"]
    plot_df["order"] = plot_df["method_label"].apply(lambda x: order.index(x) if x in order else 99)
    plot_df = plot_df.sort_values("order")

    plt.figure(figsize=(7, 4))
    plt.bar(plot_df["method_label"], plot_df[metric])
    plt.ylabel(ylabel)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()

    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outpath.with_suffix(".png"), dpi=300)
    plt.savefig(outpath.with_suffix(".pdf"))
    plt.close()


def main():
    raw_dir = Path("results/raw/paper2_progressive_readaptation_final_002")
    tables_dir = Path("results/tables/paper2_progressive_readaptation_final_002")
    figures_dir = Path("results/figures/paper2_progressive_readaptation_final_002")
    notes_dir = Path("notes")

    by_seed_path = raw_dir / "paper2_progressive_readaptation_by_seed.csv"
    summary_path = raw_dir / "paper2_progressive_readaptation_summary.csv"
    window_path = raw_dir / "paper2_progressive_readaptation_window_results.csv"

    by_seed = pd.read_csv(by_seed_path)
    summary = pd.read_csv(summary_path)
    window = pd.read_csv(window_path)

    by_seed["adaptation_efficiency"] = np.where(
        by_seed["n_adaptations"] > 0,
        by_seed["cumulative_gain_vs_no_adapt"] / by_seed["n_adaptations"],
        np.nan,
    )

    efficiency_summary = (
        by_seed.groupby("method", dropna=False)
        .agg(
            adaptation_efficiency_mean=("adaptation_efficiency", "mean"),
            adaptation_efficiency_std=("adaptation_efficiency", "std"),
        )
        .reset_index()
    )

    summary = summary.merge(efficiency_summary, on="method", how="left")

    summary = summary.copy()
    summary["method_label"] = summary["method"].map(METHOD_LABELS).fillna(summary["method"])

    paper_summary = summary[
        [
            "method",
            "method_label",
            "n_seeds",
            "mean_balanced_accuracy",
            "cumulative_error_area_mean",
            "mean_gain_vs_no_adapt",
            "cumulative_gain_vs_no_adapt_mean",
            "adaptation_efficiency_mean",
            "adaptation_efficiency_std",
            "n_adaptations_mean",
            "false_adaptations_mean",
            "first_adaptation_window_mean",
            "alarm_rate_mean",
            "trigger_rate_mean",
            "detector_runtime_sec_total_mean",
        ]
    ].copy()

    save_table(
        paper_summary,
        tables_dir / "paper_table_progressive_readaptation_summary",
    )

    comparisons = []

    # QK vs MMD: direct metrics.
    for qk in ["qk_mmd_zz", "qk_mmd_pauli_xz"]:
        comparisons.append(
            paired_diff(
                by_seed,
                qk,
                "mmd_rbf",
                "mean_balanced_accuracy",
                "Positive means QK has higher mean balanced accuracy than MMD-RBF.",
                "QK better",
            )
        )

        comparisons.append(
            paired_diff(
                by_seed,
                "mmd_rbf",
                qk,
                "cumulative_error_area",
                "Positive means MMD-RBF has larger cumulative error area, so QK has lower degradation.",
                "QK better",
            )
        )

        comparisons.append(
            paired_diff(
                by_seed,
                qk,
                "mmd_rbf",
                "cumulative_gain_vs_no_adapt",
                "Positive means QK has larger cumulative gain versus no adaptation.",
                "QK better",
            )
        )

        comparisons.append(
            paired_diff(
                by_seed,
                "mmd_rbf",
                qk,
                "n_adaptations",
                "Positive means MMD-RBF uses more readaptations than QK.",
                "QK fewer readaptations",
            )
        )

        comparisons.append(
            paired_diff(
                by_seed,
                qk,
                "mmd_rbf",
                "detector_runtime_sec_total",
                "Positive means QK has higher detector runtime than MMD-RBF.",
                "QK more expensive",
            )
        )

    comp_df = pd.DataFrame(comparisons)

    save_table(
        comp_df,
        tables_dir / "paper_table_progressive_readaptation_paired_comparisons",
    )

    # Per-window trajectory by method.
    trajectory = (
        window.groupby(["method", "window_idx"], dropna=False)
        .agg(
            severity_t=("severity_t", "mean"),
            balanced_accuracy_mean=("balanced_accuracy", "mean"),
            gain_vs_no_adapt_mean=("gain_vs_no_adapt", "mean"),
            alarm_rate=("alarm", "mean") if "alarm" in window.columns else ("balanced_accuracy", "size"),
            trigger_rate=("trigger", "mean") if "trigger" in window.columns else ("balanced_accuracy", "size"),
        )
        .reset_index()
    )

    trajectory["method_label"] = trajectory["method"].map(METHOD_LABELS).fillna(trajectory["method"])

    save_table(
        trajectory,
        tables_dir / "paper_table_progressive_readaptation_trajectory",
    )

    make_bar_plot(
        paper_summary,
        "cumulative_error_area_mean",
        "Cumulative error area (lower is better)",
        figures_dir / "progressive_cumulative_error_area",
    )

    make_bar_plot(
        paper_summary,
        "mean_balanced_accuracy",
        "Mean balanced accuracy",
        figures_dir / "progressive_mean_balanced_accuracy",
    )

    make_bar_plot(
        paper_summary,
        "n_adaptations_mean",
        "Mean number of readaptations",
        figures_dir / "progressive_number_of_readaptations",
    )

    # Trajectory plot.
    plt.figure(figsize=(8, 4))
    for method_label, g in trajectory.groupby("method_label"):
        if method_label == "No adaptation":
            linewidth = 1.5
        else:
            linewidth = 2.0

        plt.plot(
            g["window_idx"],
            g["balanced_accuracy_mean"],
            label=method_label,
            linewidth=linewidth,
        )

    plt.xlabel("Progressive drift window")
    plt.ylabel("Balanced accuracy")
    plt.legend()
    plt.tight_layout()
    figures_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(figures_dir / "progressive_balanced_accuracy_trajectory.png", dpi=300)
    plt.savefig(figures_dir / "progressive_balanced_accuracy_trajectory.pdf")
    plt.close()

    preview_cols = [
        "method_a",
        "method_b",
        "metric",
        "n_pairs",
        "mean_diff_a_minus_b",
        "ci95_low",
        "ci95_high",
        "prob_diff_gt_0",
        "positive_means",
    ]

    note_lines = [
        "# Paper 2 progressive drift readaptation checkpoint 001",
        "",
        "## Purpose",
        "",
        "This checkpoint summarizes the progressive drift readaptation experiment.",
        "",
        "Unlike the single-change downstream adaptation setup, this experiment models",
        "a persistent progressive drift process where severity increases over time and",
        "detectors may trigger multiple readaptations with a cooldown.",
        "",
        "## Main summary",
        "",
        paper_summary.to_string(index=False),
        "",
        "## Main paired comparisons",
        "",
        comp_df[preview_cols].to_string(index=False),
        "",
        "## Interpretation",
        "",
        "- No adaptation performs worst, confirming that progressive drift degrades the initial IDS.",
        "- MMD-RBF substantially improves over no adaptation.",
        "- QK-MMD ZZ obtains the best mean balanced accuracy and the lowest cumulative error area.",
        "- QK-MMD PauliXZ is also better than MMD-RBF in the aggregate summary, but weaker than ZZ.",
        "- Both QK-MMD variants use fewer readaptations than MMD-RBF under the selected policy.",
        "- Runtime remains higher for QK-MMD, so the result should be framed as an adaptation-efficiency trade-off rather than a free improvement.",
        "",
        "## Paper-facing claim if paired CIs support the aggregate result",
        "",
        "Under progressive drift, QK-MMD ZZ reduces cumulative downstream degradation",
        "relative to MMD-RBF while requiring fewer readaptations, suggesting that",
        "quantum-kernel discrepancy signals can provide more efficient readaptation",
        "under persistent distribution shift.",
        "",
        "## Caveat",
        "",
        "The result is specific to the progressive drift/readaptation protocol and should",
        "not be generalized to universal QK-MMD superiority. Earlier single-change and",
        "long-stream experiments showed no clear QK downstream superiority when all",
        "detectors trigger the same adaptation point.",
        "",
        "## Generated artifacts",
        "",
        f"- `{tables_dir / 'paper_table_progressive_readaptation_summary.csv'}`",
        f"- `{tables_dir / 'paper_table_progressive_readaptation_paired_comparisons.csv'}`",
        f"- `{tables_dir / 'paper_table_progressive_readaptation_trajectory.csv'}`",
        f"- `{figures_dir / 'progressive_cumulative_error_area.png'}`",
        f"- `{figures_dir / 'progressive_mean_balanced_accuracy.png'}`",
        f"- `{figures_dir / 'progressive_number_of_readaptations.png'}`",
        f"- `{figures_dir / 'progressive_balanced_accuracy_trajectory.png'}`",
        "",
    ]

    notes_dir.mkdir(parents=True, exist_ok=True)
    note_path = notes_dir / "paper2_progressive_readaptation_checkpoint_001.md"
    note_path.write_text("\\n".join(note_lines), encoding="utf-8")

    print(f"Saved tables in: {tables_dir}")
    print(f"Saved figures in: {figures_dir}")
    print(f"Saved note: {note_path}")

    print()
    print("=== PROGRESSIVE READAPTATION SUMMARY ===")
    print(paper_summary.to_string(index=False))

    print()
    print("=== PAIRED COMPARISONS ===")
    print(comp_df[preview_cols].to_string(index=False))


if __name__ == "__main__":
    main()
