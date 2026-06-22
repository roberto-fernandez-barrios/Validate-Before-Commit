from __future__ import annotations

from pathlib import Path

import pandas as pd


def safe_read(path: str | Path) -> pd.DataFrame | None:
    path = Path(path)
    if not path.exists():
        print(f"[WARN] Missing: {path}")
        return None
    return pd.read_csv(path)


def df_preview(df: pd.DataFrame | None, cols: list[str] | None = None, n: int | None = None) -> str:
    if df is None or df.empty:
        return "No rows."

    out = df.copy()

    if cols is not None:
        out = out[[c for c in cols if c in out.columns]]

    if n is not None:
        out = out.head(n)

    return out.to_string(index=False)


def main():
    notes_dir = Path("notes")
    notes_dir.mkdir(parents=True, exist_ok=True)

    controlled_auc = safe_read(
        "results/tables/paper2_controlled_streaming_final_001/paper_table_auc_by_severity.csv"
    )

    downstream_global = safe_read(
        "results/raw/paper2_downstream_adaptation_final_global_001/paper2_downstream_final_global_summary.csv"
    )

    statistical_pairs = safe_read(
        "results/tables/paper2_statistical_summary_001/paper_table_downstream_main_paired_comparisons.csv"
    )

    geometry = safe_read(
        "results/tables/paper2_geometry_diagnostics_001/paper_table_geometry_vs_downstream.csv"
    )

    long_stream = safe_read(
        "results/tables/paper2_downstream_long_stream_final_001/paper_table_long_stream_summary_compact.csv"
    )

    progressive_summary = safe_read(
        "results/tables/paper2_progressive_readaptation_final_002/paper_table_progressive_readaptation_summary.csv"
    )

    progressive_pairs = safe_read(
        "results/tables/paper2_progressive_readaptation_final_002/paper_table_progressive_readaptation_paired_comparisons.csv"
    )

    utility_strict = safe_read(
        "results/tables/paper2_progressive_utility_analysis_001/paper_table_progressive_utility_strict_positive.csv"
    )

    utility_break_even = safe_read(
        "results/tables/paper2_progressive_utility_analysis_001/paper_table_progressive_utility_break_even.csv"
    )

    runtime_ratio = safe_read(
        "results/tables/paper2_runtime_cost_001/paper_table_runtime_ratio_vs_mmd.csv"
    )

    md = []

    md.append("# Paper 2 final Q1-oriented synthesis checkpoint 001")
    md.append("")
    md.append("## Executive summary")
    md.append("")
    md.append(
        "This synthesis consolidates the full Paper 2 experimental story after adding "
        "progressive drift readaptation and cost-sensitive utility analysis."
    )
    md.append("")
    md.append(
        "The main conclusion is not universal quantum superiority. The defensible "
        "claim is that QK-MMD provides regime-dependent drift monitoring advantages "
        "under moderate-to-severe drift and enables more efficient readaptation under "
        "progressive drift."
    )
    md.append("")
    md.append(
        "In single-change downstream adaptation, QK-MMD does not significantly improve "
        "absolute downstream accuracy over MMD-RBF because all detectors can trigger "
        "adaptation at similar points and then use the same SVC-RBF retraining loop."
    )
    md.append("")
    md.append(
        "In progressive drift, however, QK-MMD reaches comparable downstream performance "
        "with significantly fewer readaptations and significantly higher adaptation "
        "efficiency. A cost-sensitive utility analysis further shows that QK-MMD ZZ "
        "achieves higher net utility than MMD-RBF across meaningful readaptation-cost "
        "regions, despite higher detector runtime."
    )
    md.append("")

    md.append("## What has been done")
    md.append("")
    md.append("1. Synthetic/calibration smoke experiments for QK-MMD and MMD-RBF.")
    md.append("2. CICIDS2017 real-data drift experiments.")
    md.append("3. BENIGN-only temporal shift analysis.")
    md.append("4. Controlled streaming detection experiments across drift severities.")
    md.append("5. Adaptive monitor experiments.")
    md.append("6. Single-change downstream adaptation with SVC-RBF.")
    md.append("7. Detector-specific policy optimization.")
    md.append("8. Hybrid classical-quantum monitor experiments.")
    md.append("9. Geometry diagnostics linking detector behavior to downstream outcomes.")
    md.append("10. Statistical uncertainty summaries.")
    md.append("11. Runtime and cost-benefit analysis.")
    md.append("12. Operational-scale proxy analysis.")
    md.append("13. Long-stream downstream validation.")
    md.append("14. Progressive drift readaptation.")
    md.append("15. Cost-sensitive progressive utility analysis.")
    md.append("")

    md.append("## Block 1: Controlled streaming detection")
    md.append("")
    md.append(
        "Controlled streaming is the strongest pure monitoring evidence. QK-MMD, "
        "especially PauliXZ and ZZ, improves pre/post drift AUC in moderate-to-severe "
        "regimes."
    )
    md.append("")
    md.append(df_preview(
        controlled_auc,
        cols=["severity", "method", "n_seeds", "score_gap_mean", "pre_post_auc_mean"],
    ))
    md.append("")
    md.append(
        "Interpretation: QK-MMD provides stronger drift-monitoring sensitivity in "
        "moderate-to-severe regimes, but this should not be phrased as universal "
        "earlier triggering."
    )
    md.append("")

    md.append("## Block 2: Single-change downstream adaptation")
    md.append("")
    md.append(
        "Single-change downstream adaptation confirms that drift-triggered adaptation "
        "reduces degradation, but QK-MMD does not robustly outperform MMD-RBF in final "
        "downstream accuracy."
    )
    md.append("")
    md.append(df_preview(
        downstream_global,
        cols=[
            "severity",
            "strategy",
            "post_balanced_accuracy_mean",
            "degradation_area_mean",
            "adaptation_gain_vs_no_adapt_mean",
            "clean_downstream_adaptation_rate",
            "clean_adaptation_gain_mean",
            "false_alarm_any_rate",
        ],
    ))
    md.append("")
    md.append("Main paired comparisons:")
    md.append("")
    md.append(df_preview(statistical_pairs))
    md.append("")
    md.append(
        "Interpretation: adaptation itself is valuable, but single-change downstream "
        "experiments do not support a strong QK-MMD downstream-superiority claim."
    )
    md.append("")

    md.append("## Block 3: Geometry diagnostics")
    md.append("")
    md.append(
        "Geometry diagnostics explain why the behavior is regime-dependent: MMD-RBF "
        "is stronger in low/moderate drift, while QK-MMD has stronger severe-drift "
        "post-alarm persistence."
    )
    md.append("")
    if geometry is not None and not geometry.empty:
        geo_sel = geometry[geometry["severity"].isin([0.25, 1.0])].copy()
    else:
        geo_sel = geometry
    md.append(df_preview(
        geo_sel,
        cols=[
            "severity",
            "method",
            "score_ratio_gap_post_minus_pre",
            "alarm_rate_post",
            "clean_downstream_adaptation_rate",
            "clean_adaptation_gain_mean",
            "false_alarm_any_rate",
        ],
    ))
    md.append("")

    md.append("## Block 4: Long-stream validation")
    md.append("")
    md.append(
        "The long-stream experiment validates that when MMD-RBF and QK-MMD trigger in "
        "the same window, downstream metrics become identical because the same "
        "adaptation mechanism is used."
    )
    md.append("")
    md.append(df_preview(long_stream))
    md.append("")
    md.append(
        "Interpretation: QK-MMD's value is not final retrained accuracy under a fixed "
        "single-change trigger; it lies in monitoring coverage and adaptation scheduling."
    )
    md.append("")

    md.append("## Block 5: Progressive drift readaptation")
    md.append("")
    md.append(
        "Progressive drift models a more realistic scenario in which drift evolves "
        "over time and the system can readapt multiple times."
    )
    md.append("")
    md.append(df_preview(
        progressive_summary,
        cols=[
            "method_label",
            "n_seeds",
            "mean_balanced_accuracy",
            "cumulative_error_area_mean",
            "cumulative_gain_vs_no_adapt_mean",
            "adaptation_efficiency_mean",
            "adaptation_efficiency_std",
            "n_adaptations_mean",
            "false_adaptations_mean",
            "first_adaptation_window_mean",
            "detector_runtime_sec_total_mean",
        ],
    ))
    md.append("")
    md.append("Progressive paired comparisons:")
    md.append("")
    md.append(df_preview(
        progressive_pairs,
        cols=[
            "method_a",
            "method_b",
            "metric",
            "n_pairs",
            "mean_diff_a_minus_b",
            "ci95_low",
            "ci95_high",
            "prob_diff_gt_0",
            "positive_means",
        ],
    ))
    md.append("")
    md.append(
        "Interpretation: QK-MMD does not significantly improve absolute balanced "
        "accuracy, but it requires significantly fewer readaptations and achieves "
        "significantly higher adaptation efficiency."
    )
    md.append("")

    md.append("## Block 6: Cost-sensitive utility")
    md.append("")
    md.append(
        "The cost-sensitive utility analysis formalizes why fewer readaptations matter. "
        "The utility is defined as:"
    )
    md.append("")
    md.append("`utility = cumulative_gain_vs_no_adapt - lambda * n_adaptations - gamma * detector_runtime_sec_total`")
    md.append("")
    md.append("Strict positive utility regions:")
    md.append("")
    md.append(df_preview(
        utility_strict,
        cols=[
            "method",
            "lambda_adaptation_cost",
            "gamma_runtime_cost",
            "mean_utility_diff_qk_minus_mmd",
            "ci95_low",
            "ci95_high",
            "prob_diff_gt_0",
            "qk_utility_better_ci95",
        ],
        n=40,
    ))
    md.append("")
    md.append("Break-even lambda values:")
    md.append("")
    md.append(df_preview(
        utility_break_even,
        cols=[
            "method",
            "gamma_runtime_cost",
            "mean_gain_delta_qk_minus_mmd",
            "mean_adaptation_saving_vs_mmd",
            "mean_runtime_extra_vs_mmd",
            "lambda_break_even_raw",
            "lambda_break_even_nonnegative",
        ],
    ))
    md.append("")
    md.append(
        "Interpretation: QK-MMD ZZ obtains higher net utility than MMD-RBF across "
        "meaningful readaptation-cost regions. PauliXZ is also positive, but requires "
        "higher adaptation cost to overcome runtime penalties."
    )
    md.append("")

    md.append("## Block 7: Runtime/cost")
    md.append("")
    md.append(
        "QK-MMD is more expensive than MMD-RBF. The paper must state this explicitly."
    )
    md.append("")
    md.append(df_preview(
        runtime_ratio,
        cols=[
            "severity",
            "method",
            "detector_runtime_sec_mean",
            "mmd_runtime_sec_mean",
            "runtime_ratio_vs_mmd",
            "extra_runtime_sec_vs_mmd",
            "clean_gain_delta_vs_mmd",
            "false_alarm_delta_vs_mmd",
            "trigger_delay_delta_vs_mmd",
        ],
    ))
    md.append("")
    md.append(
        "Interpretation: the QK-MMD result is a trade-off: higher monitoring cost in "
        "exchange for fewer readaptations and higher utility when adaptation is costly."
    )
    md.append("")

    md.append("## Claims supported")
    md.append("")
    md.append("1. Drift-triggered adaptation reduces downstream degradation relative to no adaptation.")
    md.append("2. QK-MMD provides stronger monitoring sensitivity under moderate-to-severe drift.")
    md.append("3. QK-MMD provides stronger severe-drift post-alarm persistence.")
    md.append("4. QK-MMD does not universally dominate MMD-RBF.")
    md.append("5. QK-MMD does not significantly improve absolute downstream accuracy under single-change drift.")
    md.append("6. Under progressive drift, QK-MMD achieves comparable downstream performance with significantly fewer readaptations.")
    md.append("7. Under progressive drift, QK-MMD achieves significantly higher adaptation efficiency.")
    md.append("8. Under cost-sensitive utility, QK-MMD ZZ achieves higher net utility than MMD-RBF across meaningful readaptation-cost regions.")
    md.append("")

    md.append("## Claims not supported")
    md.append("")
    md.append("1. Universal quantum advantage.")
    md.append("2. Universal QK-MMD superiority over MMD-RBF.")
    md.append("3. QK-MMD always detects earlier than MMD-RBF.")
    md.append("4. QK-MMD significantly improves final downstream accuracy in all regimes.")
    md.append("5. Hybrid classical-quantum monitoring universally improves over the best individual detector.")
    md.append("")

    md.append("## Final recommended narrative")
    md.append("")
    md.append(
        "The final narrative should be: QK-MMD provides regime-dependent drift geometry "
        "for adaptive IDS monitoring. It is not universally better than MMD-RBF and "
        "does not reliably improve final accuracy under a single retraining event. "
        "However, it provides stronger monitoring signals under moderate-to-severe drift "
        "and, under progressive drift, supports more efficient readaptation. When "
        "readaptation cost is explicitly modeled, QK-MMD ZZ achieves higher net utility "
        "than MMD-RBF in meaningful cost regimes."
    )
    md.append("")

    md.append("## Q1 assessment")
    md.append("")
    md.append(
        "The paper is now stronger than a simple QK-vs-classical detector comparison. "
        "It can plausibly target Q1 venues if framed around calibrated monitoring, "
        "progressive drift readaptation, and cost-sensitive operational utility. "
        "It should not be framed as broad quantum advantage."
    )
    md.append("")
    md.append(
        "The remaining main risks are: single primary dataset, simulated quantum kernels, "
        "higher QK runtime, lack of statistically significant absolute accuracy gains, "
        "and limited classical detector diversity beyond MMD-RBF."
    )
    md.append("")

    md.append("## Recommended next step")
    md.append("")
    md.append(
        "No further large experiments are recommended before drafting. The next step is "
        "to update the paper structure and start drafting Results and Discussion around "
        "the regime-dependent monitoring and cost-sensitive adaptation-efficiency claim."
    )
    md.append("")

    out_path = notes_dir / "paper2_final_q1_synthesis_checkpoint_001.md"
    out_path.write_text("\n".join(md), encoding="utf-8")

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
