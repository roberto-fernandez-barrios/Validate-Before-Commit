from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


SUMMARY_DIR = Path("results/summary/cicids_controlled_streaming_final_001")
FIG_DIR = Path("results/figures/paper2_controlled_streaming_final_001")
TABLE_DIR = Path("results/tables/paper2_controlled_streaming_final_001")

FIG_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


def detector_label(row: pd.Series) -> str:
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
    lines: list[str] = []

    col_spec = "l" * len(df.columns)

    lines.append(r"\begin{table}")
    lines.append(r"\centering")
    lines.append(rf"\caption{{{latex_escape(caption)}}}")
    lines.append(rf"\label{{{latex_escape(label)}}}")
    lines.append(rf"\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"\toprule")

    header = " & ".join(latex_escape(col) for col in df.columns)
    lines.append(header + r" \\")
    lines.append(r"\midrule")

    for _, row in df.iterrows():
        values = " & ".join(format_latex_value(row[col]) for col in df.columns)
        lines.append(values + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    auc = pd.read_csv(SUMMARY_DIR / "auc_by_severity_detector.csv")
    best_by_detector = pd.read_csv(SUMMARY_DIR / "best_low_fa_policy_by_detector.csv")
    best_overall = pd.read_csv(SUMMARY_DIR / "best_low_fa_policy_overall.csv")

    auc["method"] = auc.apply(detector_label, axis=1)
    best_by_detector["method"] = best_by_detector.apply(detector_label, axis=1)
    best_overall["method"] = best_overall.apply(detector_label, axis=1)

    # -----------------------------
    # Figure 1: AUC vs severity
    # -----------------------------
    plt.figure(figsize=(7.0, 4.2))

    for method, g in auc.sort_values("severity").groupby("method"):
        plt.plot(
            g["severity"],
            g["pre_post_auc_mean"],
            marker="o",
            linewidth=2,
            label=method,
        )

    plt.axhline(0.5, linestyle="--", linewidth=1)
    plt.xlabel("Controlled drift severity")
    plt.ylabel("Pre/post AUC")
    plt.title("Streaming drift score separability")
    plt.legend()
    plt.tight_layout()

    plt.savefig(FIG_DIR / "auc_vs_severity.png", dpi=300)
    plt.savefig(FIG_DIR / "auc_vs_severity.pdf")
    plt.close()

    # -----------------------------
    # Figure 2: best low-FA trigger gain
    # -----------------------------
    plt.figure(figsize=(7.0, 4.2))

    for method, g in best_by_detector.sort_values("severity").groupby("method"):
        plt.plot(
            g["severity"],
            g["trigger_gain"],
            marker="o",
            linewidth=2,
            label=method,
        )

    plt.axhline(0.0, linestyle="--", linewidth=1)
    plt.xlabel("Controlled drift severity")
    plt.ylabel("Trigger gain")
    plt.title("Best low-false-alarm trigger gain")
    plt.legend()
    plt.tight_layout()

    plt.savefig(FIG_DIR / "low_fa_trigger_gain_vs_severity.png", dpi=300)
    plt.savefig(FIG_DIR / "low_fa_trigger_gain_vs_severity.pdf")
    plt.close()

    # -----------------------------
    # Figure 3: post-detect rate under best low-FA policy
    # -----------------------------
    plt.figure(figsize=(7.0, 4.2))

    for method, g in best_by_detector.sort_values("severity").groupby("method"):
        plt.plot(
            g["severity"],
            g["post_detect_any_rate"],
            marker="o",
            linewidth=2,
            label=method,
        )

    plt.xlabel("Controlled drift severity")
    plt.ylabel("Post-drift detection rate")
    plt.title("Best low-false-alarm post-drift detection")
    plt.legend()
    plt.tight_layout()

    plt.savefig(FIG_DIR / "low_fa_post_detection_vs_severity.png", dpi=300)
    plt.savefig(FIG_DIR / "low_fa_post_detection_vs_severity.pdf")
    plt.close()

    # -----------------------------
    # Paper-ready tables
    # -----------------------------
    auc_table = (
        auc[["severity", "method", "n_seeds", "score_gap_mean", "pre_post_auc_mean"]]
        .sort_values(["severity", "pre_post_auc_mean"], ascending=[True, False])
    )

    policy_table = (
        best_by_detector[
            [
                "severity",
                "method",
                "threshold_quantile",
                "consecutive_k",
                "false_alarm_any_rate",
                "post_detect_any_rate",
                "trigger_gain",
                "delay_windows_mean",
                "pre_post_auc_mean",
            ]
        ]
        .sort_values(["severity", "trigger_gain"], ascending=[True, False])
    )

    overall_table = (
        best_overall[
            [
                "severity",
                "method",
                "threshold_quantile",
                "consecutive_k",
                "false_alarm_any_rate",
                "post_detect_any_rate",
                "trigger_gain",
                "delay_windows_mean",
                "pre_post_auc_mean",
            ]
        ]
        .sort_values("severity")
    )

    auc_table.to_csv(TABLE_DIR / "paper_table_auc_by_severity.csv", index=False)
    policy_table.to_csv(TABLE_DIR / "paper_table_best_low_fa_policy_by_detector.csv", index=False)
    overall_table.to_csv(TABLE_DIR / "paper_table_best_low_fa_policy_overall.csv", index=False)

    save_latex_table(
        auc_table,
        TABLE_DIR / "paper_table_auc_by_severity.tex",
        caption="Pre/post score separability under controlled streaming drift.",
        label="tab:paper2_auc_by_severity",
    )

    save_latex_table(
        policy_table,
        TABLE_DIR / "paper_table_best_low_fa_policy_by_detector.tex",
        caption="Best low-false-alarm streaming trigger policies by detector.",
        label="tab:paper2_low_fa_policy_by_detector",
    )

    save_latex_table(
        overall_table,
        TABLE_DIR / "paper_table_best_low_fa_policy_overall.tex",
        caption="Best overall low-false-alarm streaming trigger policy by drift severity.",
        label="tab:paper2_best_low_fa_policy_overall",
    )

    print("Saved figures:")
    for p in sorted(FIG_DIR.glob("*")):
        print(f" - {p}")

    print("\nSaved tables:")
    for p in sorted(TABLE_DIR.glob("*")):
        print(f" - {p}")


if __name__ == "__main__":
    main()
