from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


RNG = np.random.default_rng(12345)


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
    if strategy == "hybrid_or_triggered_adaptation":
        return "Hybrid OR"
    if strategy == "hybrid_vote_2of3_triggered_adaptation":
        return "Hybrid Vote 2/3"
    if strategy == "hybrid_and_triggered_adaptation":
        return "Hybrid AND"
    return strategy


def bootstrap_ci(values: np.ndarray, n_boot: int = 5000) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    if len(values) == 0:
        return np.nan, np.nan

    if len(values) == 1:
        return float(values[0]), float(values[0])

    idx = RNG.integers(0, len(values), size=(n_boot, len(values)))
    boot_means = values[idx].mean(axis=1)

    return (
        float(np.quantile(boot_means, 0.025)),
        float(np.quantile(boot_means, 0.975)),
    )


def summarize_metric(
    df: pd.DataFrame,
    experiment_block: str,
    metric: str,
) -> pd.DataFrame:
    rows = []

    group_cols = ["experiment_block", "severity", "strategy", "method"]

    for keys, g in df.groupby(group_cols, dropna=False):
        values = pd.to_numeric(g[metric], errors="coerce").dropna().to_numpy(dtype=float)

        if len(values) == 0:
            continue

        ci_low, ci_high = bootstrap_ci(values)

        rows.append(
            {
                "experiment_block": experiment_block,
                "severity": keys[1],
                "strategy": keys[2],
                "method": keys[3],
                "metric": metric,
                "n": len(values),
                "mean": float(np.mean(values)),
                "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                "ci95_low": ci_low,
                "ci95_high": ci_high,
            }
        )

    return pd.DataFrame(rows)


def load_block(path: Path, experiment_block: str) -> pd.DataFrame | None:
    if not path.exists():
        print(f"[MISSING] {path}")
        return None

    df = pd.read_csv(path)
    df["experiment_block"] = experiment_block
    df["method"] = df["strategy"].map(method_label)
    return df


def paired_difference(
    df: pd.DataFrame,
    experiment_block: str,
    severity: float,
    strategy_a: str,
    strategy_b: str,
    metric: str,
    interpretation: str,
) -> dict:
    subset = df[
        (df["experiment_block"] == experiment_block)
        & (df["severity"] == severity)
        & (df["strategy"].isin([strategy_a, strategy_b]))
    ].copy()

    if subset.empty:
        return {
            "experiment_block": experiment_block,
            "severity": severity,
            "strategy_a": strategy_a,
            "strategy_b": strategy_b,
            "metric": metric,
            "n_pairs": 0,
            "mean_diff_a_minus_b": np.nan,
            "ci95_low": np.nan,
            "ci95_high": np.nan,
            "prob_diff_gt_0": np.nan,
            "interpretation": interpretation,
        }

    pivot = subset.pivot_table(
        index="seed",
        columns="strategy",
        values=metric,
        aggfunc="mean",
    )

    if strategy_a not in pivot.columns or strategy_b not in pivot.columns:
        n_pairs = 0
        diff = np.array([])
    else:
        pair_df = pivot[[strategy_a, strategy_b]].dropna()
        n_pairs = len(pair_df)
        diff = (
            pair_df[strategy_a].to_numpy(dtype=float)
            - pair_df[strategy_b].to_numpy(dtype=float)
        )

    if n_pairs == 0:
        mean_diff = np.nan
        ci_low = np.nan
        ci_high = np.nan
        prob_gt_0 = np.nan
    else:
        mean_diff = float(np.mean(diff))
        ci_low, ci_high = bootstrap_ci(diff)
        prob_gt_0 = float(np.mean(diff > 0))

    return {
        "experiment_block": experiment_block,
        "severity": severity,
        "strategy_a": strategy_a,
        "strategy_b": strategy_b,
        "method_a": method_label(strategy_a),
        "method_b": method_label(strategy_b),
        "metric": metric,
        "n_pairs": n_pairs,
        "mean_diff_a_minus_b": mean_diff,
        "ci95_low": ci_low,
        "ci95_high": ci_high,
        "prob_diff_gt_0": prob_gt_0,
        "interpretation": interpretation,
    }


def main() -> None:
    tables_dir = Path("results/tables/paper2_statistical_summary_001")
    notes_dir = Path("notes")

    tables_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    blocks = []

    global_df = load_block(
        Path("results/raw/paper2_downstream_adaptation_final_global_001/paper2_downstream_final_global_by_seed.csv"),
        "downstream_global",
    )
    if global_df is not None:
        blocks.append(global_df)

    optimized_df = load_block(
        Path("results/raw/paper2_downstream_adaptation_final_optimized_001/paper2_downstream_final_optimized_by_seed.csv"),
        "downstream_optimized",
    )
    if optimized_df is not None:
        blocks.append(optimized_df)

    hybrid_df = load_block(
        Path("results/raw/paper2_downstream_hybrid_final_001/paper2_downstream_hybrid_final_by_seed.csv"),
        "hybrid_selected",
    )
    if hybrid_df is not None:
        blocks.append(hybrid_df)

    if not blocks:
        raise SystemExit("No by-seed downstream files found.")

    all_df = pd.concat(blocks, ignore_index=True)

    metrics = [
        "post_balanced_accuracy_mean",
        "degradation_area",
        "adaptation_gain_vs_no_adapt",
        "clean_downstream_adaptation",
        "clean_adaptation_gain",
        "false_alarm_any",
        "triggered_post",
        "trigger_delay_windows",
    ]

    metric_summaries = []

    for block_name, block_df in all_df.groupby("experiment_block"):
        for metric in metrics:
            if metric in block_df.columns:
                metric_summaries.append(
                    summarize_metric(block_df, block_name, metric)
                )

    metric_summary_df = pd.concat(metric_summaries, ignore_index=True)

    save_table(
        metric_summary_df,
        tables_dir / "paper_table_downstream_metric_bootstrap_ci",
    )

    comparisons = []

    # Global policy: adaptation vs no adaptation across relevant severities.
    for sev in [0.25, 0.5, 0.75, 1.0]:
        for strategy in [
            "mmd_rbf_triggered_adaptation",
            "qk_mmd_zz_triggered_adaptation",
            "qk_mmd_pauli_xz_triggered_adaptation",
        ]:
            comparisons.append(
                paired_difference(
                    all_df,
                    "downstream_global",
                    sev,
                    "no_adaptation",
                    strategy,
                    "degradation_area",
                    "Positive means no_adaptation has larger degradation area, so adaptation reduces degradation.",
                )
            )

    # MMD vs QK under global policy.
    comparisons.extend(
        [
            paired_difference(
                all_df,
                "downstream_global",
                0.25,
                "mmd_rbf_triggered_adaptation",
                "qk_mmd_pauli_xz_triggered_adaptation",
                "clean_adaptation_gain",
                "Positive means MMD-RBF has higher clean gain than QK-MMD PauliXZ.",
            ),
            paired_difference(
                all_df,
                "downstream_global",
                0.25,
                "mmd_rbf_triggered_adaptation",
                "qk_mmd_zz_triggered_adaptation",
                "clean_adaptation_gain",
                "Positive means MMD-RBF has higher clean gain than QK-MMD ZZ.",
            ),
            paired_difference(
                all_df,
                "downstream_global",
                1.0,
                "qk_mmd_pauli_xz_triggered_adaptation",
                "mmd_rbf_triggered_adaptation",
                "clean_adaptation_gain",
                "Positive means QK-MMD PauliXZ has higher clean gain than MMD-RBF.",
            ),
            paired_difference(
                all_df,
                "downstream_global",
                1.0,
                "qk_mmd_zz_triggered_adaptation",
                "mmd_rbf_triggered_adaptation",
                "clean_adaptation_gain",
                "Positive means QK-MMD ZZ has higher clean gain than MMD-RBF.",
            ),
        ]
    )

    # Hybrid selected final.
    comparisons.extend(
        [
            paired_difference(
                all_df,
                "hybrid_selected",
                0.25,
                "hybrid_or_triggered_adaptation",
                "mmd_rbf_triggered_adaptation",
                "clean_adaptation_gain",
                "Positive means Hybrid OR has higher clean gain than MMD-RBF.",
            ),
            paired_difference(
                all_df,
                "hybrid_selected",
                1.0,
                "qk_mmd_pauli_xz_triggered_adaptation",
                "hybrid_or_triggered_adaptation",
                "clean_adaptation_gain",
                "Positive means QK-MMD PauliXZ has higher clean gain than Hybrid OR.",
            ),
        ]
    )

    comparison_df = pd.DataFrame(comparisons)

    save_table(
        comparison_df,
        tables_dir / "paper_table_downstream_paired_comparisons",
    )

    # Compact paper-facing table: main comparisons only.
    compact = comparison_df[
        comparison_df["severity"].isin([0.25, 1.0])
    ].copy()

    save_table(
        compact,
        tables_dir / "paper_table_downstream_main_paired_comparisons",
    )

    note_lines = [
        "# Paper 2 statistical summary checkpoint 001",
        "",
        "## Purpose",
        "",
        "This note summarizes bootstrap confidence intervals and paired seed-level",
        "comparisons for the downstream adaptation experiments.",
        "",
        "The goal is to support paper claims with uncertainty estimates rather than",
        "only reporting means.",
        "",
        "## Generated tables",
        "",
        f"- `{tables_dir / 'paper_table_downstream_metric_bootstrap_ci.csv'}`",
        f"- `{tables_dir / 'paper_table_downstream_paired_comparisons.csv'}`",
        f"- `{tables_dir / 'paper_table_downstream_main_paired_comparisons.csv'}`",
        "",
        "## Interpretation guidelines",
        "",
        "- Bootstrap CIs are computed over seeds.",
        "- Paired comparisons are computed by matching the same seed, severity and experiment block.",
        "- `mean_diff_a_minus_b > 0` means strategy A has a larger value than strategy B.",
        "- For degradation area, larger is worse.",
        "- For clean adaptation gain, larger is better.",
        "",
        "## Important caveat",
        "",
        "These summaries are descriptive uncertainty estimates, not a substitute for",
        "a full statistical testing protocol across multiple datasets.",
        "",
        "They are appropriate for the current paper stage because the main objective",
        "is to quantify robustness and support regime-dependent claims.",
        "",
    ]

    # Add a compact preview of key comparisons.
    preview_cols = [
        "experiment_block",
        "severity",
        "method_a",
        "method_b",
        "metric",
        "n_pairs",
        "mean_diff_a_minus_b",
        "ci95_low",
        "ci95_high",
        "prob_diff_gt_0",
    ]

    note_lines.append("## Main paired comparisons")
    note_lines.append("")
    note_lines.append(compact[preview_cols].to_string(index=False))
    note_lines.append("")

    note_path = notes_dir / "paper2_statistical_summary_checkpoint_001.md"
    note_path.write_text("\n".join(note_lines), encoding="utf-8")

    print(f"Saved tables in: {tables_dir}")
    print(f"Saved note: {note_path}")

    print()
    print("=== MAIN PAIRED COMPARISONS ===")
    print(compact[preview_cols].to_string(index=False))


if __name__ == "__main__":
    main()
