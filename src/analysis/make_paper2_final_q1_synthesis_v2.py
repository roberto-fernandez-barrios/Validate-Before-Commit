from __future__ import annotations

from pathlib import Path

import pandas as pd


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

    controlled_auc = safe_read(
        "results/tables/paper2_controlled_streaming_final_001/paper_table_auc_by_severity.csv"
    )

    progressive_original_summary = safe_read(
        "results/tables/paper2_progressive_readaptation_final_002/paper_table_progressive_readaptation_summary.csv"
    )

    progressive_original_pairs = safe_read(
        "results/tables/paper2_progressive_readaptation_final_002/paper_table_progressive_readaptation_paired_comparisons.csv"
    )

    classical_summary = safe_read(
        "results/tables/paper2_progressive_classical_baselines_final_001/paper_table_progressive_classical_baselines_summary.csv"
    )

    classical_paired = safe_read(
        "results/tables/paper2_progressive_classical_baselines_final_001/paper_table_progressive_classical_baselines_paired.csv"
    )

    classical_utility = safe_read(
        "results/tables/paper2_progressive_classical_baselines_final_001/paper_table_progressive_classical_baselines_utility_strict_positive.csv"
    )

    runtime_ratio = safe_read(
        "results/tables/paper2_runtime_cost_001/paper_table_runtime_ratio_vs_mmd.csv"
    )

    downstream_global = safe_read(
        "results/raw/paper2_downstream_adaptation_final_global_001/paper2_downstream_final_global_summary.csv"
    )

    long_stream = safe_read(
        "results/tables/paper2_downstream_long_stream_final_001/paper_table_long_stream_summary_compact.csv"
    )

    md = []

    md.append("# Paper 2 final Q1-oriented synthesis checkpoint 002")
    md.append("")
    md.append("## Executive summary")
    md.append("")
    md.append(
        "This checkpoint updates the Paper 2 synthesis after adding strong classical "
        "distributional baselines to the progressive drift readaptation experiment."
    )
    md.append("")
    md.append(
        "The final defensible story is not universal quantum advantage. The strongest "
        "claim is that QK-MMD provides regime-dependent monitoring advantages and, "
        "under progressive drift, QK-MMD ZZ matches the best classical distributional "
        "baseline in downstream performance while requiring significantly fewer "
        "readaptations and achieving significantly higher adaptation efficiency."
    )
    md.append("")
    md.append(
        "The cost-sensitive utility analysis further shows that QK-MMD ZZ becomes "
        "preferable when readaptation costs are non-negligible, despite higher "
        "monitoring runtime."
    )
    md.append("")
    md.append(
        "This significantly strengthens the Q1 positioning because the paper no longer "
        "depends only on comparison against MMD-RBF."
    )
    md.append("")

    md.append("## Final core claim")
    md.append("")
    md.append(
        "Under progressive drift, QK-MMD ZZ is competitive with strong classical "
        "distributional baselines and provides a favorable operational trade-off when "
        "readaptation cost is explicitly modeled."
    )
    md.append("")
    md.append("More precisely:")
    md.append("")
    md.append(
        "QK-MMD ZZ matches Energy distance in downstream balanced accuracy, cumulative "
        "degradation, and cumulative gain, but requires significantly fewer "
        "readaptations and achieves significantly higher gain per readaptation."
    )
    md.append("")

    md.append("## What changed since checkpoint 001")
    md.append("")
    md.append("Checkpoint 001 compared QK-MMD mainly against MMD-RBF.")
    md.append("")
    md.append("Checkpoint 002 adds:")
    md.append("")
    md.append("1. KS-max detector.")
    md.append("2. Histogram Jensen-Shannon divergence detector.")
    md.append("3. Energy-distance detector.")
    md.append("4. Paired comparisons between QK-MMD ZZ and all baselines.")
    md.append("5. Cost-sensitive utility against all baselines.")
    md.append("")
    md.append(
        "The key result is that Energy distance is a very strong classical baseline, "
        "but QK-MMD ZZ remains competitive and uses substantially fewer readaptations."
    )
    md.append("")

    md.append("## Evidence block 1: controlled streaming")
    md.append("")
    md.append(
        "Controlled streaming remains the main evidence that QK-MMD has regime-dependent "
        "monitoring sensitivity, especially under moderate-to-severe drift."
    )
    md.append("")
    md.append(preview(
        controlled_auc,
        cols=["severity", "method", "n_seeds", "score_gap_mean", "pre_post_auc_mean"],
    ))
    md.append("")
    md.append(
        "Interpretation: QK-MMD improves monitoring sensitivity in moderate-to-severe "
        "drift regimes, but the paper should not claim universal earlier detection."
    )
    md.append("")

    md.append("## Evidence block 2: single-change downstream adaptation")
    md.append("")
    md.append(
        "Single-change downstream adaptation shows that triggered adaptation is useful, "
        "but QK-MMD does not robustly improve final downstream accuracy over MMD-RBF when "
        "both trigger adaptation in similar windows."
    )
    md.append("")
    md.append(preview(
        downstream_global,
        cols=[
            "severity",
            "strategy",
            "post_balanced_accuracy_mean",
            "degradation_area_mean",
            "adaptation_gain_vs_no_adapt_mean",
            "false_alarm_any_rate",
        ],
        n=40,
    ))
    md.append("")
    md.append(
        "Interpretation: the value of QK-MMD should not be framed as better retrained "
        "accuracy after a single drift event. The adaptation mechanism is the same SVC-RBF."
    )
    md.append("")

    md.append("## Evidence block 3: long-stream validation")
    md.append("")
    md.append(
        "Long-stream validation showed that when MMD-RBF and QK-MMD trigger in the same "
        "window, downstream results converge."
    )
    md.append("")
    md.append(preview(long_stream))
    md.append("")
    md.append(
        "Interpretation: the contribution is not simply earlier single-trigger adaptation, "
        "but monitoring behavior and scheduling efficiency under progressive drift."
    )
    md.append("")

    md.append("## Evidence block 4: progressive drift without extra classical baselines")
    md.append("")
    md.append(
        "The original progressive drift experiment showed that QK-MMD ZZ improves "
        "adaptation efficiency over MMD-RBF, but absolute accuracy/degradation gains "
        "were not statistically conclusive."
    )
    md.append("")
    md.append(preview(
        progressive_original_summary,
        cols=[
            "method_label",
            "n_seeds",
            "mean_balanced_accuracy",
            "cumulative_error_area_mean",
            "cumulative_gain_vs_no_adapt_mean",
            "adaptation_efficiency_mean",
            "n_adaptations_mean",
            "detector_runtime_sec_total_mean",
        ],
    ))
    md.append("")
    md.append(preview(
        progressive_original_pairs,
        cols=[
            "method_a",
            "method_b",
            "metric",
            "n_pairs",
            "mean_diff_a_minus_b",
            "ci95_low",
            "ci95_high",
            "positive_means",
        ],
    ))
    md.append("")

    md.append("## Evidence block 5: progressive drift with classical baselines")
    md.append("")
    md.append(
        "This is the new key robustness block. It compares QK-MMD ZZ against Energy "
        "distance, JSD, KS-max, MMD-RBF, and QK-MMD PauliXZ under the same progressive "
        "readaptation protocol."
    )
    md.append("")
    md.append("### Ranking by cumulative degradation")
    md.append("")
    md.append(preview(
        classical_summary,
        cols=[
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
    md.append("### Key paired comparisons")
    md.append("")
    if classical_paired is not None and not classical_paired.empty:
        focus = classical_paired[
            classical_paired["method_b"].isin(["Energy distance", "JSD", "MMD-RBF"])
            | classical_paired["method_a"].isin(["Energy distance", "JSD", "MMD-RBF"])
        ].copy()
    else:
        focus = classical_paired

    md.append(preview(
        focus,
        cols=[
            "method_a",
            "method_b",
            "metric",
            "n_pairs",
            "mean_diff_a_minus_b",
            "ci95_low",
            "ci95_high",
            "positive_means",
        ],
    ))
    md.append("")
    md.append("Interpretation:")
    md.append("")
    md.append(
        "- QK-MMD ZZ and Energy distance are statistically tied in raw downstream "
        "performance metrics."
    )
    md.append(
        "- QK-MMD ZZ requires significantly fewer readaptations than Energy distance."
    )
    md.append(
        "- QK-MMD ZZ has significantly higher adaptation efficiency than Energy distance."
    )
    md.append(
        "- QK-MMD ZZ has much higher detector runtime than Energy distance."
    )
    md.append("")

    md.append("## Evidence block 6: cost-sensitive utility against all baselines")
    md.append("")
    md.append(
        "Utility is defined as `cumulative_gain_vs_no_adapt - lambda * n_adaptations - "
        "gamma * detector_runtime_sec_total`."
    )
    md.append("")
    md.append(
        "Strict positive utility regions indicate settings where QK-MMD ZZ has a "
        "positive bootstrap CI lower bound over the corresponding baseline."
    )
    md.append("")
    md.append(preview(
        classical_utility,
        cols=[
            "baseline",
            "lambda_cost",
            "gamma_cost",
            "mean_utility_diff_qk_minus_baseline",
            "ci95_low",
            "ci95_high",
            "qk_better_ci95",
        ],
        n=80,
    ))
    md.append("")
    md.append("Interpretation:")
    md.append("")
    md.append(
        "QK-MMD ZZ becomes preferable to Energy distance once readaptation cost is "
        "non-negligible, e.g. lambda >= 0.5 for low/moderate runtime penalty settings."
    )
    md.append("")
    md.append(
        "This supports the operational claim: QK-MMD ZZ is not necessarily cheaper or "
        "more accurate, but it can provide higher net utility when readaptation is costly."
    )
    md.append("")

    md.append("## Runtime and cost caveat")
    md.append("")
    md.append(
        "QK-MMD is consistently more expensive in monitoring runtime. This must be "
        "explicitly framed as a trade-off rather than hidden."
    )
    md.append("")
    md.append(preview(
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
        ],
        n=50,
    ))
    md.append("")

    md.append("## Supported claims")
    md.append("")
    md.append("1. QK-MMD provides regime-dependent monitoring advantages under moderate-to-severe drift.")
    md.append("2. Triggered adaptation reduces downstream degradation compared with no adaptation.")
    md.append("3. QK-MMD does not universally dominate MMD-RBF or classical baselines in raw accuracy.")
    md.append("4. QK-MMD ZZ matches Energy distance in progressive downstream performance.")
    md.append("5. QK-MMD ZZ requires significantly fewer readaptations than Energy distance.")
    md.append("6. QK-MMD ZZ has significantly higher adaptation efficiency than Energy distance.")
    md.append("7. QK-MMD ZZ has higher monitoring runtime.")
    md.append("8. Cost-sensitive utility favors QK-MMD ZZ when readaptation cost is non-negligible.")
    md.append("")

    md.append("## Claims to avoid")
    md.append("")
    md.append("1. Universal quantum advantage.")
    md.append("2. QK-MMD always detects earlier.")
    md.append("3. QK-MMD significantly improves raw downstream accuracy over Energy distance.")
    md.append("4. QK-MMD is computationally cheaper.")
    md.append("5. Classical baselines are weak.")
    md.append("")

    md.append("## Q1 readiness after classical baselines")
    md.append("")
    md.append(
        "The paper is now materially stronger than in checkpoint 001. The addition of "
        "Energy distance, JSD, and KS-max directly addresses the reviewer criticism "
        "that MMD-RBF alone is insufficient as a classical comparator."
    )
    md.append("")
    md.append(
        "The result is still not a universal quantum-advantage paper. It is better "
        "framed as an adaptive monitoring and operational utility paper."
    )
    md.append("")
    md.append(
        "Current readiness: Q1 possible and substantially better defended than before; "
        "Q2 strong if the target venue is highly skeptical of simulated quantum-kernel "
        "methods or requires multiple datasets."
    )
    md.append("")

    md.append("## Final recommended paper narrative")
    md.append("")
    md.append(
        "This paper proposes quantum-kernel MMD as a regime-dependent drift monitoring "
        "mechanism for adaptive IDS. QK-MMD does not universally dominate classical "
        "detectors in raw downstream accuracy. However, QK-MMD ZZ matches the strongest "
        "classical distributional baseline under progressive drift while requiring "
        "substantially fewer readaptations. When operational readaptation costs are "
        "modeled explicitly, QK-MMD ZZ achieves higher net utility across meaningful "
        "cost regimes, despite higher monitoring runtime."
    )
    md.append("")

    md.append("## Recommended next step")
    md.append("")
    md.append(
        "Do not add more detector variants immediately. The next step is to merge the "
        "classical-baselines branch back into the main paper branch, then start drafting "
        "the paper structure, figures, tables, Results, and Discussion."
    )
    md.append("")

    out_path = NOTES_DIR / "paper2_final_q1_synthesis_checkpoint_002.md"
    out_path.write_text("\n".join(md), encoding="utf-8")

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
