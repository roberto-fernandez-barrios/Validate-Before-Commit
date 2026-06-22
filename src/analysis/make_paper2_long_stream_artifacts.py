from __future__ import annotations

from pathlib import Path

import pandas as pd


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


def main() -> None:
    seed_dirs = sorted(Path("results/raw").glob("paper2_downstream_long_stream_final_001_seed_*"))

    if not seed_dirs:
        raise SystemExit("No long-stream seed directories found.")

    by_seed_rows = []
    window_rows = []

    for d in seed_dirs:
        by_seed_path = d / "paper2_downstream_by_seed.csv"
        window_path = d / "paper2_downstream_window_results.csv"

        if not by_seed_path.exists():
            print(f"[MISSING] {by_seed_path}")
            continue

        by_seed = pd.read_csv(by_seed_path)
        by_seed["source_dir"] = str(d)
        by_seed["experiment_block"] = "long_stream_final"
        by_seed["post_windows"] = 100
        by_seed["threshold_quantile"] = 0.95
        by_seed["consecutive_k"] = 3
        by_seed["method"] = by_seed["strategy"].map(method_label)
        by_seed_rows.append(by_seed)

        if window_path.exists():
            window = pd.read_csv(window_path)
            window["source_dir"] = str(d)
            window["experiment_block"] = "long_stream_final"
            window["post_windows"] = 100
            window["threshold_quantile"] = 0.95
            window["consecutive_k"] = 3
            window["method"] = window["strategy"].map(method_label)
            window_rows.append(window)

    if not by_seed_rows:
        raise SystemExit("No completed by-seed files found.")

    out_raw = Path("results/raw/paper2_downstream_long_stream_final_001")
    out_tables = Path("results/tables/paper2_downstream_long_stream_final_001")
    notes_dir = Path("notes")

    out_raw.mkdir(parents=True, exist_ok=True)
    out_tables.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    by_seed_df = pd.concat(by_seed_rows, ignore_index=True)
    by_seed_out = out_raw / "paper2_downstream_long_stream_final_by_seed.csv"
    by_seed_df.to_csv(by_seed_out, index=False)

    if window_rows:
        window_df = pd.concat(window_rows, ignore_index=True)
        window_out = out_raw / "paper2_downstream_long_stream_final_window_results.csv"
        window_df.to_csv(window_out, index=False)
    else:
        window_df = pd.DataFrame()
        window_out = None

    group_cols = [
        "dataset",
        "protocol",
        "model",
        "severity",
        "strategy",
        "method",
        "detector",
        "q_feature_map",
        "dim",
        "window_size",
        "train_size_per_class",
        "adapt_size_per_class",
        "post_windows",
        "threshold_quantile",
        "consecutive_k",
    ]

    group_cols = [c for c in group_cols if c in by_seed_df.columns]

    summary = (
        by_seed_df
        .groupby(group_cols, dropna=False)
        .agg(
            n_seeds=("seed", "nunique"),
            post_balanced_accuracy_mean=("post_balanced_accuracy_mean", "mean"),
            post_balanced_accuracy_std=("post_balanced_accuracy_mean", "std"),
            post_f1_mean=("post_f1_mean", "mean"),
            post_f1_std=("post_f1_mean", "std"),
            degradation_area_mean=("degradation_area", "mean"),
            degradation_area_std=("degradation_area", "std"),
            adaptation_gain_vs_no_adapt_mean=("adaptation_gain_vs_no_adapt", "mean"),
            adaptation_gain_vs_no_adapt_std=("adaptation_gain_vs_no_adapt", "std"),
            clean_downstream_adaptation_rate=("clean_downstream_adaptation", "mean"),
            clean_adaptation_gain_mean=("clean_adaptation_gain", "mean"),
            clean_adaptation_gain_std=("clean_adaptation_gain", "std"),
            triggered_post_rate=("triggered_post", "mean"),
            false_alarm_any_rate=("false_alarm_any", "mean"),
            adapted_any_rate=("adapted_any", "mean"),
            trigger_delay_windows_mean=("trigger_delay_windows", "mean"),
            trigger_delay_windows_std=("trigger_delay_windows", "std"),
            detector_runtime_sec_mean=("detector_runtime_sec", "mean"),
        )
        .reset_index()
        .sort_values(["severity", "strategy"])
    )

    summary_out = out_raw / "paper2_downstream_long_stream_final_summary.csv"
    summary.to_csv(summary_out, index=False)

    # Paired comparisons vs MMD-RBF.
    triggered = by_seed_df[
        by_seed_df["strategy"].isin(
            [
                "mmd_rbf_triggered_adaptation",
                "qk_mmd_zz_triggered_adaptation",
                "qk_mmd_pauli_xz_triggered_adaptation",
            ]
        )
    ].copy()

    comparison_rows = []

    metrics = [
        "post_balanced_accuracy_mean",
        "degradation_area",
        "clean_adaptation_gain",
        "trigger_delay_windows",
        "false_alarm_any",
        "triggered_post",
    ]

    for severity in sorted(triggered["severity"].unique()):
        sev_df = triggered[triggered["severity"] == severity]

        for q_strategy in [
            "qk_mmd_zz_triggered_adaptation",
            "qk_mmd_pauli_xz_triggered_adaptation",
        ]:
            pair = sev_df[
                sev_df["strategy"].isin(
                    ["mmd_rbf_triggered_adaptation", q_strategy]
                )
            ].pivot_table(
                index="seed",
                columns="strategy",
                values=metrics,
                aggfunc="mean",
            )

            for metric in metrics:
                if (
                    (metric, "mmd_rbf_triggered_adaptation") not in pair.columns
                    or (metric, q_strategy) not in pair.columns
                ):
                    continue

                values = pair[
                    [
                        (metric, q_strategy),
                        (metric, "mmd_rbf_triggered_adaptation"),
                    ]
                ].dropna()

                if values.empty:
                    continue

                diff = (
                    values[(metric, q_strategy)]
                    - values[(metric, "mmd_rbf_triggered_adaptation")]
                )

                comparison_rows.append(
                    {
                        "severity": severity,
                        "method_a": method_label(q_strategy),
                        "method_b": "MMD-RBF",
                        "metric": metric,
                        "n_pairs": len(diff),
                        "mean_diff_a_minus_b": diff.mean(),
                        "std_diff": diff.std(),
                        "min_diff": diff.min(),
                        "max_diff": diff.max(),
                        "prob_diff_gt_0": (diff > 0).mean(),
                    }
                )

    comparisons = pd.DataFrame(comparison_rows)
    comparisons_out = out_tables / "paper_table_long_stream_qk_vs_mmd_paired.csv"
    comparisons.to_csv(comparisons_out, index=False)

    # Compact summary table.
    compact_cols = [
        "severity",
        "method",
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

    compact = summary[[c for c in compact_cols if c in summary.columns]]
    compact_out = out_tables / "paper_table_long_stream_summary_compact.csv"
    compact.to_csv(compact_out, index=False)

    note_lines = [
        "# Paper 2 long-stream downstream validation checkpoint 001",
        "",
        "## Protocol",
        "",
        "- post_windows: 100",
        "- severities: 0.75, 1.0",
        "- seeds: final seed directories found in `results/raw/paper2_downstream_long_stream_final_001_seed_*`",
        "- trigger policy: q=0.95, k=3",
        "",
        "## Generated artifacts",
        "",
        f"- `{by_seed_out}`",
        f"- `{summary_out}`",
        f"- `{compact_out}`",
        f"- `{comparisons_out}`",
        "",
        "## Interpretation guideline",
        "",
        "This experiment tests whether a longer downstream stream makes the QK-MMD",
        "monitoring advantage translate into direct downstream performance gains.",
        "",
        "If MMD-RBF and QK-MMD trigger at the same window, downstream metrics will",
        "be nearly identical because all methods use the same retraining mechanism.",
        "",
        "In that case, the operational QK-MMD claim should remain focused on",
        "post-drift monitoring coverage rather than final retrained accuracy.",
        "",
    ]

    note_path = notes_dir / "paper2_long_stream_downstream_validation_checkpoint_001.md"
    note_path.write_text("\n".join(note_lines), encoding="utf-8")

    print(f"Saved: {by_seed_out}")
    if window_out:
        print(f"Saved: {window_out}")
    print(f"Saved: {summary_out}")
    print(f"Saved: {compact_out}")
    print(f"Saved: {comparisons_out}")
    print(f"Saved: {note_path}")

    print()
    print("=== LONG-STREAM SUMMARY COMPACT ===")
    print(compact.to_string(index=False))

    print()
    print("=== QK VS MMD PAIRED COMPARISONS ===")
    print(comparisons.to_string(index=False))


if __name__ == "__main__":
    main()
