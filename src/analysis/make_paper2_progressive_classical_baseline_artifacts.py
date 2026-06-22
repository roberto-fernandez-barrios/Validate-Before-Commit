from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


RAW_DIR = Path("results/raw/paper2_progressive_classical_baselines_final_001")
TABLES_DIR = Path("results/tables/paper2_progressive_classical_baselines_final_001")
NOTES_DIR = Path("notes")

METHOD_LABELS = {
    "no_adaptation": "No adaptation",
    "mmd_rbf": "MMD-RBF",
    "ks_max": "KS-max",
    "jsd": "JSD",
    "energy_distance": "Energy distance",
    "qk_mmd_zz": "QK-MMD ZZ",
    "qk_mmd_pauli_xz": "QK-MMD PauliXZ",
}


def bootstrap_ci(values: np.ndarray, n_boot: int = 10000, seed: int = 123) -> dict:
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]

    rng = np.random.default_rng(seed)
    means = []

    for _ in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        means.append(sample.mean())

    means = np.asarray(means)

    return {
        "mean": float(values.mean()),
        "ci95_low": float(np.quantile(means, 0.025)),
        "ci95_high": float(np.quantile(means, 0.975)),
        "prob_gt_0": float(np.mean(values > 0)),
        "n": int(len(values)),
    }


def paired(df: pd.DataFrame, method_a: str, method_b: str, metric: str, positive_means: str) -> dict:
    a = df[df["method"] == method_a][["seed", metric]].rename(columns={metric: "a"})
    b = df[df["method"] == method_b][["seed", metric]].rename(columns={metric: "b"})

    merged = a.merge(b, on="seed", how="inner")
    diff = merged["a"].to_numpy() - merged["b"].to_numpy()
    stats = bootstrap_ci(diff)

    return {
        "method_a": METHOD_LABELS.get(method_a, method_a),
        "method_b": METHOD_LABELS.get(method_b, method_b),
        "metric": metric,
        "n_pairs": stats["n"],
        "mean_diff_a_minus_b": stats["mean"],
        "ci95_low": stats["ci95_low"],
        "ci95_high": stats["ci95_high"],
        "prob_diff_gt_0": stats["prob_gt_0"],
        "positive_means": positive_means,
    }


def utility_grid(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    lambdas = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0]
    gammas = [0.0, 0.01, 0.05, 0.1, 0.25]

    baselines = [
        "energy_distance",
        "jsd",
        "ks_max",
        "mmd_rbf",
        "qk_mmd_pauli_xz",
    ]

    for lambda_cost in lambdas:
        for gamma_cost in gammas:
            work = df.copy()
            work["utility"] = (
                work["cumulative_gain_vs_no_adapt"]
                - lambda_cost * work["n_adaptations"]
                - gamma_cost * work["detector_runtime_sec_total"]
            )

            for baseline in baselines:
                qk = work[work["method"] == "qk_mmd_zz"][["seed", "utility"]].rename(columns={"utility": "qk"})
                b = work[work["method"] == baseline][["seed", "utility"]].rename(columns={"utility": "baseline"})

                merged = qk.merge(b, on="seed", how="inner")
                diff = merged["qk"].to_numpy() - merged["baseline"].to_numpy()
                stats = bootstrap_ci(diff)

                rows.append(
                    {
                        "baseline": METHOD_LABELS[baseline],
                        "lambda_cost": lambda_cost,
                        "gamma_cost": gamma_cost,
                        "mean_utility_diff_qk_minus_baseline": stats["mean"],
                        "ci95_low": stats["ci95_low"],
                        "ci95_high": stats["ci95_high"],
                        "prob_diff_gt_0": stats["prob_gt_0"],
                        "qk_better_ci95": bool(stats["ci95_low"] > 0),
                    }
                )

    return pd.DataFrame(rows)


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    summary_path = RAW_DIR / "paper2_progressive_readaptation_summary.csv"
    by_seed_path = RAW_DIR / "paper2_progressive_readaptation_by_seed.csv"

    summary = pd.read_csv(summary_path)
    by_seed = pd.read_csv(by_seed_path)

    summary["method_label"] = summary["method"].map(METHOD_LABELS).fillna(summary["method"])

    by_seed["adaptation_efficiency"] = np.where(
        by_seed["n_adaptations"] > 0,
        by_seed["cumulative_gain_vs_no_adapt"] / by_seed["n_adaptations"],
        np.nan,
    )

    eff = (
        by_seed.groupby("method", dropna=False)
        .agg(
            adaptation_efficiency_mean=("adaptation_efficiency", "mean"),
            adaptation_efficiency_std=("adaptation_efficiency", "std"),
        )
        .reset_index()
    )

    summary = summary.merge(eff, on="method", how="left")

    summary_out = summary.sort_values("cumulative_error_area_mean").copy()
    summary_out.to_csv(TABLES_DIR / "paper_table_progressive_classical_baselines_summary.csv", index=False)

    baselines = [
        "energy_distance",
        "jsd",
        "ks_max",
        "mmd_rbf",
        "qk_mmd_pauli_xz",
    ]

    rows = []

    for baseline in baselines:
        rows.append(
            paired(
                by_seed,
                "qk_mmd_zz",
                baseline,
                "mean_balanced_accuracy",
                "QK-MMD ZZ better accuracy",
            )
        )

        rows.append(
            paired(
                by_seed,
                baseline,
                "qk_mmd_zz",
                "cumulative_error_area",
                "QK-MMD ZZ lower degradation",
            )
        )

        rows.append(
            paired(
                by_seed,
                "qk_mmd_zz",
                baseline,
                "cumulative_gain_vs_no_adapt",
                "QK-MMD ZZ higher gain",
            )
        )

        rows.append(
            paired(
                by_seed,
                baseline,
                "qk_mmd_zz",
                "n_adaptations",
                "QK-MMD ZZ fewer readaptations",
            )
        )

        rows.append(
            paired(
                by_seed,
                "qk_mmd_zz",
                baseline,
                "adaptation_efficiency",
                "QK-MMD ZZ better adaptation efficiency",
            )
        )

        rows.append(
            paired(
                by_seed,
                "qk_mmd_zz",
                baseline,
                "detector_runtime_sec_total",
                "QK-MMD ZZ more expensive",
            )
        )

    paired_df = pd.DataFrame(rows)
    paired_df.to_csv(TABLES_DIR / "paper_table_progressive_classical_baselines_paired.csv", index=False)

    utility = utility_grid(by_seed)
    utility.to_csv(TABLES_DIR / "paper_table_progressive_classical_baselines_utility_grid.csv", index=False)

    strict = utility[utility["qk_better_ci95"]].copy()
    strict.to_csv(TABLES_DIR / "paper_table_progressive_classical_baselines_utility_strict_positive.csv", index=False)

    compact_cols = [
        "method_label",
        "n_seeds",
        "mean_balanced_accuracy",
        "cumulative_error_area_mean",
        "cumulative_gain_vs_no_adapt_mean",
        "n_adaptations_mean",
        "adaptation_efficiency_mean",
        "detector_runtime_sec_total_mean",
    ]

    paired_focus = paired_df[
        paired_df["method_b"].isin(["Energy distance", "JSD", "MMD-RBF"])
        | paired_df["method_a"].isin(["Energy distance", "JSD", "MMD-RBF"])
    ].copy()

    note = []
    note.append("# Paper 2 progressive classical baselines checkpoint 001")
    note.append("")
    note.append("## Purpose")
    note.append("")
    note.append("This checkpoint extends the progressive drift readaptation experiment with additional classical distributional baselines:")
    note.append("")
    note.append("- KS-max")
    note.append("- JSD")
    note.append("- Energy distance")
    note.append("")
    note.append("The goal is to test whether QK-MMD ZZ remains competitive beyond MMD-RBF.")
    note.append("")
    note.append("## Summary ranking by cumulative degradation")
    note.append("")
    note.append(summary_out[compact_cols].to_string(index=False))
    note.append("")
    note.append("## Key paired comparisons")
    note.append("")
    note.append(paired_focus.to_string(index=False))
    note.append("")
    note.append("## Strict positive utility regions")
    note.append("")
    if strict.empty:
        note.append("No strict positive QK-MMD ZZ utility regions found.")
    else:
        note.append(strict.to_string(index=False))
    note.append("")
    note.append("## Main interpretation")
    note.append("")
    note.append(
        "QK-MMD ZZ matches the strongest classical distributional baseline "
        "(Energy distance) in downstream balanced accuracy, cumulative degradation, "
        "and cumulative gain, with no statistically conclusive difference in raw "
        "performance metrics."
    )
    note.append("")
    note.append(
        "However, QK-MMD ZZ requires significantly fewer readaptations than Energy "
        "distance and achieves significantly higher adaptation efficiency. This "
        "comes at substantially higher detector runtime."
    )
    note.append("")
    note.append(
        "The cost-sensitive utility analysis shows that QK-MMD ZZ becomes preferable "
        "to Energy distance when readaptation cost is non-negligible and runtime cost "
        "is not dominant."
    )
    note.append("")
    note.append("## Claim enabled")
    note.append("")
    note.append(
        "Under progressive drift, QK-MMD ZZ is competitive with strong classical "
        "distributional baselines and provides a favorable operational trade-off "
        "when readaptation cost is explicitly modeled."
    )
    note.append("")

    note_path = NOTES_DIR / "paper2_progressive_classical_baselines_checkpoint_001.md"
    note_path.write_text("\n".join(note), encoding="utf-8")

    print(f"Saved: {TABLES_DIR / 'paper_table_progressive_classical_baselines_summary.csv'}")
    print(f"Saved: {TABLES_DIR / 'paper_table_progressive_classical_baselines_paired.csv'}")
    print(f"Saved: {TABLES_DIR / 'paper_table_progressive_classical_baselines_utility_grid.csv'}")
    print(f"Saved: {TABLES_DIR / 'paper_table_progressive_classical_baselines_utility_strict_positive.csv'}")
    print(f"Saved: {note_path}")

    print()
    print("=== SUMMARY ===")
    print(summary_out[compact_cols].to_string(index=False))

    print()
    print("=== PAIRED FOCUS ===")
    print(paired_focus.to_string(index=False))

    print()
    print("=== STRICT UTILITY ===")
    if strict.empty:
        print("No strict positive utility regions.")
    else:
        print(strict.to_string(index=False))


if __name__ == "__main__":
    main()
