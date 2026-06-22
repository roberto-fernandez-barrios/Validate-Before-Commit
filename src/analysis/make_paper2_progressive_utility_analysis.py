from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


METHOD_LABELS = {
    "mmd_rbf": "MMD-RBF",
    "qk_mmd_zz": "QK-MMD ZZ",
    "qk_mmd_pauli_xz": "QK-MMD PauliXZ",
}


def bootstrap_ci(values: np.ndarray, n_boot: int = 10000, seed: int = 123):
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


def paired_utility_diff(df: pd.DataFrame, qk_method: str, lambda_adapt: float, gamma_runtime: float):
    work = df.copy()

    work["utility"] = (
        work["cumulative_gain_vs_no_adapt"]
        - lambda_adapt * work["n_adaptations"]
        - gamma_runtime * work["detector_runtime_sec_total"]
    )

    qk = work[work["method"] == qk_method][["seed", "utility"]].rename(columns={"utility": "qk"})
    mmd = work[work["method"] == "mmd_rbf"][["seed", "utility"]].rename(columns={"utility": "mmd"})

    merged = qk.merge(mmd, on="seed", how="inner")
    diff = merged["qk"].to_numpy() - merged["mmd"].to_numpy()

    stats = bootstrap_ci(diff)

    return {
        "method": METHOD_LABELS[qk_method],
        "lambda_adaptation_cost": lambda_adapt,
        "gamma_runtime_cost": gamma_runtime,
        "n_pairs": stats["n"],
        "mean_utility_diff_qk_minus_mmd": stats["mean"],
        "ci95_low": stats["ci95_low"],
        "ci95_high": stats["ci95_high"],
        "prob_diff_gt_0": stats["prob_gt_0"],
        "qk_utility_better_ci95": bool(stats["ci95_low"] > 0),
    }


def break_even_lambda(df: pd.DataFrame, qk_method: str, gamma_runtime: float):
    qk = df[df["method"] == qk_method].copy()
    mmd = df[df["method"] == "mmd_rbf"].copy()

    merged = qk.merge(mmd, on="seed", suffixes=("_qk", "_mmd"))

    gain_delta = (
        merged["cumulative_gain_vs_no_adapt_qk"]
        - merged["cumulative_gain_vs_no_adapt_mmd"]
    ).mean()

    adaptation_saving = (
        merged["n_adaptations_mmd"]
        - merged["n_adaptations_qk"]
    ).mean()

    runtime_extra = (
        merged["detector_runtime_sec_total_qk"]
        - merged["detector_runtime_sec_total_mmd"]
    ).mean()

    if adaptation_saving <= 0:
        raw_break_even = np.nan
    else:
        raw_break_even = (gamma_runtime * runtime_extra - gain_delta) / adaptation_saving

    return {
        "method": METHOD_LABELS[qk_method],
        "gamma_runtime_cost": gamma_runtime,
        "mean_gain_delta_qk_minus_mmd": float(gain_delta),
        "mean_adaptation_saving_vs_mmd": float(adaptation_saving),
        "mean_runtime_extra_vs_mmd": float(runtime_extra),
        "lambda_break_even_raw": float(raw_break_even) if not np.isnan(raw_break_even) else np.nan,
        "lambda_break_even_nonnegative": float(max(0.0, raw_break_even)) if not np.isnan(raw_break_even) else np.nan,
    }


def make_heatmap(grid: pd.DataFrame, method: str, figures_dir: Path):
    sub = grid[grid["method"] == method].copy()

    lambdas = sorted(sub["lambda_adaptation_cost"].unique())
    gammas = sorted(sub["gamma_runtime_cost"].unique())

    matrix = np.zeros((len(gammas), len(lambdas)))

    for i, gamma in enumerate(gammas):
        for j, lamb in enumerate(lambdas):
            row = sub[
                (sub["lambda_adaptation_cost"] == lamb)
                & (sub["gamma_runtime_cost"] == gamma)
            ]

            if row.empty:
                matrix[i, j] = np.nan
            else:
                matrix[i, j] = row.iloc[0]["ci95_low"]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(matrix, aspect="auto", origin="lower")

    ax.set_xticks(range(len(lambdas)))
    ax.set_xticklabels([str(x) for x in lambdas], rotation=45, ha="right")

    ax.set_yticks(range(len(gammas)))
    ax.set_yticklabels([str(x) for x in gammas])

    ax.set_xlabel("λ adaptation cost")
    ax.set_ylabel("γ runtime cost")
    ax.set_title(f"Utility CI95 lower bound: {method} vs MMD-RBF")

    fig.colorbar(im, ax=ax, label="CI95 lower bound of utility diff")
    fig.tight_layout()

    safe_name = method.lower().replace(" ", "_").replace("-", "_")
    figures_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(figures_dir / f"utility_heatmap_{safe_name}.png", dpi=300)
    fig.savefig(figures_dir / f"utility_heatmap_{safe_name}.pdf")
    plt.close(fig)


def main():
    raw_dir = Path("results/raw/paper2_progressive_readaptation_final_002")
    tables_dir = Path("results/tables/paper2_progressive_utility_analysis_001")
    figures_dir = Path("results/figures/paper2_progressive_utility_analysis_001")
    notes_dir = Path("notes")

    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    by_seed_path = raw_dir / "paper2_progressive_readaptation_by_seed.csv"
    df = pd.read_csv(by_seed_path)

    methods = ["qk_mmd_zz", "qk_mmd_pauli_xz"]

    lambda_grid = [
        0.0,
        0.05,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        1.5,
        2.0,
    ]

    gamma_grid = [
        0.0,
        0.01,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
    ]

    utility_rows = []

    for method in methods:
        for lamb in lambda_grid:
            for gamma in gamma_grid:
                utility_rows.append(
                    paired_utility_diff(
                        df,
                        qk_method=method,
                        lambda_adapt=lamb,
                        gamma_runtime=gamma,
                    )
                )

    utility = pd.DataFrame(utility_rows)

    utility_path = tables_dir / "paper_table_progressive_utility_grid.csv"
    utility.to_csv(utility_path, index=False)

    strict = utility[utility["qk_utility_better_ci95"]].copy()
    strict_path = tables_dir / "paper_table_progressive_utility_strict_positive.csv"
    strict.to_csv(strict_path, index=False)

    break_even_rows = []

    for method in methods:
        for gamma in gamma_grid:
            break_even_rows.append(
                break_even_lambda(
                    df,
                    qk_method=method,
                    gamma_runtime=gamma,
                )
            )

    break_even = pd.DataFrame(break_even_rows)
    break_even_path = tables_dir / "paper_table_progressive_utility_break_even.csv"
    break_even.to_csv(break_even_path, index=False)

    for method_label in utility["method"].unique():
        make_heatmap(utility, method_label, figures_dir)

    compact_cols = [
        "method",
        "lambda_adaptation_cost",
        "gamma_runtime_cost",
        "mean_utility_diff_qk_minus_mmd",
        "ci95_low",
        "ci95_high",
        "prob_diff_gt_0",
        "qk_utility_better_ci95",
    ]

    representative = utility[
        utility["lambda_adaptation_cost"].isin([0.0, 0.25, 0.5, 1.0])
        & utility["gamma_runtime_cost"].isin([0.0, 0.05, 0.1])
    ].copy()

    note_lines = [
        "# Paper 2 progressive utility analysis checkpoint 001",
        "",
        "## Purpose",
        "",
        "This analysis converts the progressive readaptation result into a cost-sensitive",
        "operational utility comparison.",
        "",
        "The utility is defined as:",
        "",
        "`utility = cumulative_gain_vs_no_adapt - lambda * n_adaptations - gamma * detector_runtime_sec_total`",
        "",
        "where `lambda` is the cost of each readaptation and `gamma` is the cost of",
        "monitoring runtime.",
        "",
        "## Motivation",
        "",
        "The progressive drift experiment showed that QK-MMD does not significantly",
        "improve absolute balanced accuracy over MMD-RBF, but it does achieve comparable",
        "performance with significantly fewer readaptations and significantly higher",
        "gain per readaptation.",
        "",
        "This analysis tests whether that efficiency translates into higher net utility",
        "when readaptations have nonzero operational cost.",
        "",
        "## Representative utility grid",
        "",
        representative[compact_cols].to_string(index=False),
        "",
        "## Strict positive utility regions",
        "",
        strict[compact_cols].to_string(index=False) if not strict.empty else "No strict positive regions found.",
        "",
        "## Break-even lambda by runtime cost",
        "",
        break_even.to_string(index=False),
        "",
        "## Interpretation",
        "",
        "- If `lambda = 0`, the comparison reduces mostly to cumulative gain minus runtime cost.",
        "- As `lambda` increases, fewer readaptations become operationally valuable.",
        "- A strict positive CI95 lower bound means QK-MMD has higher utility than MMD-RBF under that cost setting.",
        "- This should be presented as a cost-sensitive operational analysis, not as universal accuracy superiority.",
        "",
        "## Generated artifacts",
        "",
        f"- `{utility_path}`",
        f"- `{strict_path}`",
        f"- `{break_even_path}`",
        f"- `{figures_dir}`",
        "",
    ]

    note_path = notes_dir / "paper2_progressive_utility_analysis_checkpoint_001.md"
    note_path.write_text("\n".join(note_lines), encoding="utf-8")

    print(f"Saved: {utility_path}")
    print(f"Saved: {strict_path}")
    print(f"Saved: {break_even_path}")
    print(f"Saved figures in: {figures_dir}")
    print(f"Saved note: {note_path}")

    print()
    print("=== REPRESENTATIVE UTILITY GRID ===")
    print(representative[compact_cols].to_string(index=False))

    print()
    print("=== STRICT POSITIVE UTILITY REGIONS ===")
    if strict.empty:
        print("No strict positive regions found.")
    else:
        print(strict[compact_cols].to_string(index=False))

    print()
    print("=== BREAK-EVEN LAMBDA ===")
    print(break_even.to_string(index=False))


if __name__ == "__main__":
    main()
