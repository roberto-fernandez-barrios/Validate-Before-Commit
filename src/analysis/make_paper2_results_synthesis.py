from __future__ import annotations

from pathlib import Path

import pandas as pd


def _md_cell(value) -> str:
    if pd.isna(value):
        return "NA"

    if isinstance(value, float):
        return f"{value:.4f}"

    text = str(value)
    text = text.replace("|", "\\|")
    text = text.replace("\n", " ")
    return text


def df_to_markdown(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "No rows."

    table = df.copy()
    cols = [str(c) for c in table.columns]

    rows = []
    for _, row in table.iterrows():
        rows.append([_md_cell(row[c]) for c in table.columns])

    widths = []
    for i, col in enumerate(cols):
        max_row_width = max([len(r[i]) for r in rows], default=0)
        widths.append(max(len(col), max_row_width))

    header = "| " + " | ".join(col.ljust(widths[i]) for i, col in enumerate(cols)) + " |"
    sep = "| " + " | ".join("-" * widths[i] for i in range(len(cols))) + " |"

    body = [
        "| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(cols))) + " |"
        for row in rows
    ]

    return "\n".join([header, sep] + body)


def _to_markdown_no_tabulate(self, index: bool = False, **kwargs) -> str:
    table = self.copy()
    if index:
        table = table.reset_index()
    return df_to_markdown(table)


pd.DataFrame.to_markdown = _to_markdown_no_tabulate


def safe_read(path: str | Path) -> pd.DataFrame | None:
    path = Path(path)
    if not path.exists():
        print(f"[MISSING] {path}")
        return None
    return pd.read_csv(path)


def fmt(value, ndigits: int = 4) -> str:
    if value is None or pd.isna(value):
        return "NA"
    if isinstance(value, float):
        return f"{value:.{ndigits}f}"
    return str(value)


def method_label_from_strategy(strategy: str) -> str:
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


def row_by(df: pd.DataFrame, **kwargs) -> pd.Series | None:
    if df is None or df.empty:
        return None

    mask = pd.Series(True, index=df.index)

    for col, value in kwargs.items():
        if col not in df.columns:
            return None
        mask &= df[col] == value

    out = df[mask]
    if out.empty:
        return None
    return out.iloc[0]


def best_by_severity(df: pd.DataFrame, metric: str, maximize: bool = True) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    if metric not in df.columns:
        return pd.DataFrame()

    sort_ascending = not maximize

    return (
        df.sort_values(["severity", metric], ascending=[True, sort_ascending])
        .groupby("severity", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )


def append_table_preview(md: list[str], title: str, df: pd.DataFrame | None, cols: list[str]) -> None:
    md.append(f"## {title}")
    md.append("")

    if df is None or df.empty:
        md.append("Not available.")
        md.append("")
        return

    existing = [c for c in cols if c in df.columns]
    md.append(df[existing].to_markdown(index=False))
    md.append("")


def main() -> None:
    notes_dir = Path("notes")
    notes_dir.mkdir(parents=True, exist_ok=True)

    controlled_auc = safe_read(
        "results/tables/paper2_controlled_streaming_final_001/paper_table_auc_by_severity.csv"
    )

    controlled_best = safe_read(
        "results/tables/paper2_controlled_streaming_final_001/paper_table_best_low_fa_policy_overall.csv"
    )

    adaptive_best = safe_read(
        "results/tables/paper2_adaptive_monitor_final_001/paper_table_best_clean_adaptation_by_severity.csv"
    )

    downstream_global = safe_read(
        "results/raw/paper2_downstream_adaptation_final_global_001/paper2_downstream_final_global_summary.csv"
    )

    downstream_optimized = safe_read(
        "results/raw/paper2_downstream_adaptation_final_optimized_001/paper2_downstream_final_optimized_summary.csv"
    )

    hybrid_final = safe_read(
        "results/raw/paper2_downstream_hybrid_final_001/paper2_downstream_hybrid_final_summary.csv"
    )

    geometry_vs_downstream = safe_read(
        "results/tables/paper2_geometry_diagnostics_001/paper_table_geometry_vs_downstream.csv"
    )

    geometry_corr = safe_read(
        "results/tables/paper2_geometry_diagnostics_001/paper_table_geometry_downstream_correlations.csv"
    )

    # Add method labels where useful.
    for df in [downstream_global, downstream_optimized, hybrid_final]:
        if df is not None and "strategy" in df.columns:
            df["method"] = df["strategy"].map(method_label_from_strategy)

    md: list[str] = []

    md.append("# Paper 2 results synthesis checkpoint 001")
    md.append("")
    md.append("## Purpose")
    md.append("")
    md.append(
        "This note synthesizes the current experimental evidence for Paper 2. "
        "It separates supported claims from unsupported claims and identifies "
        "which results should be used as main paper evidence."
    )
    md.append("")

    md.append("## Experimental blocks completed")
    md.append("")
    md.append("- Controlled streaming drift detection.")
    md.append("- Adaptive monitor update.")
    md.append("- Downstream adaptation with global trigger policy.")
    md.append("- Downstream adaptation with detector-specific optimized policies.")
    md.append("- Hybrid classical-quantum monitor analysis.")
    md.append("- Geometry diagnostics linking score behavior and downstream utility.")
    md.append("")

    md.append("## High-level verdict")
    md.append("")
    md.append(
        "The current evidence does not support a universal quantum advantage claim. "
        "QK-MMD does not dominate MMD-RBF across all regimes or downstream settings."
    )
    md.append("")
    md.append(
        "The evidence does support a more careful and scientifically defensible claim: "
        "quantum-kernel drift monitors provide regime-dependent and complementary "
        "drift evidence. MMD-RBF is stronger in low-moderate downstream adaptation, "
        "whereas QK-MMD provides stronger high-severity post-drift alarm persistence "
        "and competitive downstream recovery."
    )
    md.append("")

    # Controlled streaming summary.
    md.append("## Block 1: Controlled streaming drift detection")
    md.append("")

    if controlled_auc is not None and not controlled_auc.empty:
        best_auc = best_by_severity(controlled_auc, "pre_post_auc_mean", maximize=True)
        md.append("Best pre/post AUC by severity:")
        md.append("")
        md.append(
            best_auc[
                [c for c in ["severity", "method", "n_seeds", "pre_post_auc_mean", "score_gap_mean"] if c in best_auc.columns]
            ].to_markdown(index=False)
        )
        md.append("")

    if controlled_best is not None and not controlled_best.empty:
        md.append("Best low-false-alarm policy by severity:")
        md.append("")
        md.append(
            controlled_best[
                [c for c in controlled_best.columns if c in [
                    "severity",
                    "method",
                    "threshold_quantile",
                    "consecutive_k",
                    "false_alarm_any_rate",
                    "post_detect_any_rate",
                    "trigger_gain",
                    "trigger_delay_windows_mean",
                ]]
            ].to_markdown(index=False)
        )
        md.append("")

    md.append(
        "Interpretation: the controlled streaming block is the strongest evidence "
        "that quantum-kernel geometries, especially PauliXZ/ZZ in earlier results, "
        "can produce useful drift-monitoring signals. This is where the quantum "
        "contribution is most visible."
    )
    md.append("")

    # Adaptive monitor.
    md.append("## Block 2: Adaptive monitor")
    md.append("")

    if adaptive_best is not None and not adaptive_best.empty:
        md.append("Best clean adaptation by severity:")
        md.append("")
        md.append(
            adaptive_best[
                [c for c in adaptive_best.columns if c in [
                    "severity",
                    "method",
                    "n_seeds",
                    "false_alarm_any_rate",
                    "post_detect_any_rate",
                    "adaptation_success_rate",
                    "clean_adaptation_success_rate",
                    "score_reduction_after_adaptation_mean",
                ]]
            ].to_markdown(index=False)
        )
        md.append("")

    md.append(
        "Interpretation: the adaptive monitor block shows that drift alarms can be "
        "connected to an adaptive update of the monitoring reference/calibration. "
        "It supports operational utility at the monitor level, but not by itself "
        "a downstream IDS performance claim."
    )
    md.append("")

    # Downstream global.
    md.append("## Block 3: Downstream adaptation with global policy")
    md.append("")

    if downstream_global is not None and not downstream_global.empty:
        sev = 1.0

        rows = []
        for strategy in [
            "no_adaptation",
            "mmd_rbf_triggered_adaptation",
            "qk_mmd_zz_triggered_adaptation",
            "qk_mmd_pauli_xz_triggered_adaptation",
            "oracle_adaptation",
        ]:
            r = row_by(downstream_global, severity=sev, strategy=strategy)
            if r is not None:
                rows.append(
                    {
                        "severity": sev,
                        "method": method_label_from_strategy(strategy),
                        "balanced_accuracy": r.get("post_balanced_accuracy_mean"),
                        "degradation_area": r.get("degradation_area_mean"),
                        "clean_rate": r.get("clean_downstream_adaptation_rate"),
                        "clean_gain": r.get("clean_adaptation_gain_mean"),
                        "false_alarm": r.get("false_alarm_any_rate"),
                    }
                )

        if rows:
            md.append("Severity 1.0 downstream global-policy summary:")
            md.append("")
            md.append(pd.DataFrame(rows).to_markdown(index=False))
            md.append("")

        sev = 0.25
        rows = []
        for strategy in [
            "mmd_rbf_triggered_adaptation",
            "qk_mmd_zz_triggered_adaptation",
            "qk_mmd_pauli_xz_triggered_adaptation",
        ]:
            r = row_by(downstream_global, severity=sev, strategy=strategy)
            if r is not None:
                rows.append(
                    {
                        "severity": sev,
                        "method": method_label_from_strategy(strategy),
                        "balanced_accuracy": r.get("post_balanced_accuracy_mean"),
                        "degradation_area": r.get("degradation_area_mean"),
                        "clean_rate": r.get("clean_downstream_adaptation_rate"),
                        "clean_gain": r.get("clean_adaptation_gain_mean"),
                        "false_alarm": r.get("false_alarm_any_rate"),
                    }
                )

        if rows:
            md.append("Severity 0.25 downstream global-policy summary:")
            md.append("")
            md.append(pd.DataFrame(rows).to_markdown(index=False))
            md.append("")

    md.append(
        "Interpretation: the global downstream block shows that drift-triggered "
        "adaptation substantially reduces degradation relative to no adaptation. "
        "However, under the common global policy, MMD-RBF is stronger at severity "
        "0.25, all methods are competitive at moderate drift, and QK-MMD variants "
        "are slightly cleaner in severe drift."
    )
    md.append("")

    # Optimized policies.
    md.append("## Block 4: Detector-specific optimized policies")
    md.append("")

    if downstream_optimized is not None and not downstream_optimized.empty:
        triggered = downstream_optimized[
            downstream_optimized["strategy"].str.contains("triggered_adaptation", na=False)
        ].copy()

        best_opt = (
            triggered.sort_values(
                [
                    "severity",
                    "clean_adaptation_gain_mean",
                    "clean_downstream_adaptation_rate",
                    "false_alarm_any_rate",
                ],
                ascending=[True, False, False, True],
            )
            .groupby("severity", as_index=False)
            .head(1)
        )

        md.append("Best detector-specific optimized method by severity:")
        md.append("")
        md.append(
            best_opt[
                [c for c in [
                    "severity",
                    "method",
                    "threshold_quantile",
                    "consecutive_k",
                    "post_balanced_accuracy_mean",
                    "degradation_area_mean",
                    "clean_downstream_adaptation_rate",
                    "clean_adaptation_gain_mean",
                    "false_alarm_any_rate",
                ] if c in best_opt.columns]
            ].to_markdown(index=False)
        )
        md.append("")

    md.append(
        "Interpretation: detector-specific optimization does not produce universal "
        "QK-MMD dominance. MMD-RBF remains strong in low-moderate drift, QK-MMD ZZ "
        "is competitive in moderate-to-severe drift, and QK-MMD PauliXZ is strongest "
        "in clean adaptation behavior at severity 1.0."
    )
    md.append("")

    # Hybrid.
    md.append("## Block 5: Hybrid classical-quantum monitor")
    md.append("")

    if hybrid_final is not None and not hybrid_final.empty:
        for sev in [0.25, 1.0]:
            rows = []
            for strategy in [
                "hybrid_or_triggered_adaptation",
                "mmd_rbf_triggered_adaptation",
                "qk_mmd_zz_triggered_adaptation",
                "qk_mmd_pauli_xz_triggered_adaptation",
            ]:
                r = row_by(hybrid_final, severity=sev, strategy=strategy)
                if r is not None:
                    rows.append(
                        {
                            "severity": sev,
                            "method": method_label_from_strategy(strategy),
                            "balanced_accuracy": r.get("post_balanced_accuracy_mean"),
                            "degradation_area": r.get("degradation_area_mean"),
                            "clean_rate": r.get("clean_downstream_adaptation_rate"),
                            "clean_gain": r.get("clean_adaptation_gain_mean"),
                            "false_alarm": r.get("false_alarm_any_rate"),
                        }
                    )

            if rows:
                md.append(f"Hybrid comparison at severity {sev}:")
                md.append("")
                md.append(pd.DataFrame(rows).to_markdown(index=False))
                md.append("")

    md.append(
        "Interpretation: the selected Hybrid OR monitor improves low-moderate "
        "adaptation at severity 0.25, but it does not improve global robustness "
        "relative to the best individual detector. It should be used as a robustness "
        "or negative/partial result, not as the main Q1 claim."
    )
    md.append("")

    # Geometry diagnostics.
    md.append("## Block 6: Geometry diagnostics")
    md.append("")

    if geometry_vs_downstream is not None and not geometry_vs_downstream.empty:
        rows = geometry_vs_downstream[
            geometry_vs_downstream["severity"].isin([0.25, 1.0])
        ].copy()

        md.append("Geometry/downstream examples at severity 0.25 and 1.0:")
        md.append("")
        md.append(
            rows[
                [c for c in [
                    "severity",
                    "method",
                    "score_ratio_gap_post_minus_pre",
                    "alarm_rate_post",
                    "clean_downstream_adaptation_rate",
                    "clean_adaptation_gain_mean",
                    "degradation_area_mean",
                    "false_alarm_any_rate",
                ] if c in rows.columns]
            ].to_markdown(index=False)
        )
        md.append("")

    if geometry_corr is not None and not geometry_corr.empty:
        md.append("Geometry/downstream correlations:")
        md.append("")
        md.append(geometry_corr.to_markdown(index=False))
        md.append("")

    md.append(
        "Interpretation: geometry diagnostics explain the regime dependence. "
        "MMD-RBF has stronger low-moderate score separation, matching its better "
        "downstream behavior at severity 0.25. QK-MMD has stronger high-severity "
        "post-drift alarm persistence, matching its cleaner severe-drift adaptation."
    )
    md.append("")

    # Supported / unsupported claims.
    md.append("## Claims supported")
    md.append("")
    md.append("1. Drift-triggered adaptation reduces downstream degradation relative to no adaptation.")
    md.append("2. QK-MMD provides competitive and complementary drift signals.")
    md.append("3. Detector behavior is regime-dependent.")
    md.append("4. QK-MMD variants provide stronger high-severity post-drift alarm persistence.")
    md.append("5. MMD-RBF is stronger in low-moderate downstream adaptation.")
    md.append("6. Geometry diagnostics explain why no universal dominance is observed.")
    md.append("")

    md.append("## Claims not supported")
    md.append("")
    md.append("1. Universal QK-MMD superiority over MMD-RBF.")
    md.append("2. Universal hybrid classical-quantum superiority.")
    md.append("3. A broad quantum advantage claim.")
    md.append("4. A claim that downstream improvement is uniquely caused by QK-MMD.")
    md.append("")

    md.append("## Recommended paper narrative")
    md.append("")
    md.append(
        "The recommended narrative is not `quantum beats classical`. "
        "The stronger and more defensible narrative is:"
    )
    md.append("")
    md.append(
        "> Quantum-kernel MMD provides regime-dependent drift geometry for "
        "cybersecurity adaptation. While it does not universally dominate a "
        "classical RBF-MMD baseline, its feature-map-induced discrepancy signals "
        "are complementary, especially in high-severity drift where QK-MMD yields "
        "more persistent post-drift alarms and cleaner downstream adaptation."
    )
    md.append("")

    md.append("## Q1 assessment")
    md.append("")
    md.append(
        "The experimental base is now substantially stronger than a simple detector "
        "comparison. However, the paper should avoid claiming universal quantum "
        "advantage. For a Q1-oriented submission, the contribution should be framed "
        "around calibrated drift monitoring, downstream adaptation utility, regime "
        "dependence, and geometry-based explanation."
    )
    md.append("")

    md.append("## Recommended main figures/tables")
    md.append("")
    md.append("Main figures:")
    md.append("")
    md.append("- Controlled streaming AUC / detection sensitivity vs severity.")
    md.append("- Low-false-alarm post-drift detection vs severity.")
    md.append("- Downstream degradation area vs severity.")
    md.append("- Clean adaptation gain vs severity.")
    md.append("- Geometry score gap vs severity.")
    md.append("- Geometry score gap or alarm rate vs downstream clean gain.")
    md.append("")
    md.append("Main tables:")
    md.append("")
    md.append("- Controlled streaming best low-false-alarm policy.")
    md.append("- Downstream global policy summary.")
    md.append("- Detector-specific optimized policy summary.")
    md.append("- Geometry vs downstream table.")
    md.append("")

    md.append("## Next work")
    md.append("")
    md.append("No further large downstream policy sweeps are recommended at this stage.")
    md.append("")
    md.append("Useful remaining work:")
    md.append("")
    md.append("- Statistical summaries / confidence intervals for the main tables.")
    md.append("- Runtime/cost discussion.")
    md.append("- Optional lightweight KS/JSD baseline for detection-only comparison.")
    md.append("- Manuscript Results and Discussion drafting.")
    md.append("")

    out_path = notes_dir / "paper2_results_synthesis_checkpoint_001.md"
    out_path.write_text("\n".join(md), encoding="utf-8")

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
