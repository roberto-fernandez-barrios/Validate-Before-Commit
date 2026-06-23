from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCENARIOS = {
    "Wednesday": Path("results/raw/paper2_progressive_classical_baselines_final_001"),
    "PortScan": Path("results/raw/paper2_progressive_cicids_tuesday_friday_portscan_final_001"),
    "DDoS": Path("results/raw/paper2_progressive_cicids_tuesday_friday_ddos_final_001"),
}

TABLES_DIR = Path("results/tables/paper2_progressive_multi_scenario_cicids_001")
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


def paired(df: pd.DataFrame, scenario: str, method_a: str, method_b: str, metric: str, positive_means: str) -> dict:
    a = df[df["method"] == method_a][["seed", metric]].rename(columns={metric: "a"})
    b = df[df["method"] == method_b][["seed", metric]].rename(columns={metric: "b"})

    merged = a.merge(b, on="seed", how="inner")
    diff = merged["a"].to_numpy() - merged["b"].to_numpy()
    stats = bootstrap_ci(diff)

    return {
        "scenario": scenario,
        "method_a": METHOD_LABELS.get(method_a, method_a),
        "method_b": METHOD_LABELS.get(method_b, method_b),
        "metric": metric,
        "n_pairs": stats["n"],
        "mean_diff_a_minus_b": stats["mean"],
        "ci95_low": stats["ci95_low"],
        "ci95_high": stats["ci95_high"],
        "prob_diff_gt_0": stats["prob_gt_0"],
        "positive_means": positive_means,
        "ci_excludes_zero_positive": bool(stats["ci95_low"] > 0),
    }


def add_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["adaptation_efficiency"] = np.where(
        out["n_adaptations"] > 0,
        out["cumulative_gain_vs_no_adapt"] / out["n_adaptations"],
        np.nan,
    )
    return out


def compute_utility(df: pd.DataFrame, scenario: str) -> pd.DataFrame:
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
                        "scenario": scenario,
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

    summary_rows = []
    paired_rows = []
    utility_frames = []

    for scenario, raw_dir in SCENARIOS.items():
        summary = pd.read_csv(raw_dir / "paper2_progressive_readaptation_summary.csv")
        by_seed = pd.read_csv(raw_dir / "paper2_progressive_readaptation_by_seed.csv")
        by_seed = add_efficiency(by_seed)

        eff = (
            by_seed.groupby("method", dropna=False)
            .agg(
                adaptation_efficiency_mean=("adaptation_efficiency", "mean"),
                adaptation_efficiency_std=("adaptation_efficiency", "std"),
            )
            .reset_index()
        )

        summary = summary.merge(eff, on="method", how="left")
        summary["scenario"] = scenario
        summary["method_label"] = summary["method"].map(METHOD_LABELS).fillna(summary["method"])
        summary_rows.append(summary)

        baselines = [
            "energy_distance",
            "jsd",
            "ks_max",
            "mmd_rbf",
            "qk_mmd_pauli_xz",
        ]

        for baseline in baselines:
            paired_rows.append(
                paired(
                    by_seed,
                    scenario,
                    "qk_mmd_zz",
                    baseline,
                    "mean_balanced_accuracy",
                    "QK-MMD ZZ better accuracy",
                )
            )
            paired_rows.append(
                paired(
                    by_seed,
                    scenario,
                    baseline,
                    "qk_mmd_zz",
                    "cumulative_error_area",
                    "QK-MMD ZZ lower degradation",
                )
            )
            paired_rows.append(
                paired(
                    by_seed,
                    scenario,
                    "qk_mmd_zz",
                    baseline,
                    "cumulative_gain_vs_no_adapt",
                    "QK-MMD ZZ higher gain",
                )
            )
            paired_rows.append(
                paired(
                    by_seed,
                    scenario,
                    baseline,
                    "qk_mmd_zz",
                    "n_adaptations",
                    "QK-MMD ZZ fewer readaptations",
                )
            )
            paired_rows.append(
                paired(
                    by_seed,
                    scenario,
                    "qk_mmd_zz",
                    baseline,
                    "adaptation_efficiency",
                    "QK-MMD ZZ better adaptation efficiency",
                )
            )
            paired_rows.append(
                paired(
                    by_seed,
                    scenario,
                    "qk_mmd_zz",
                    baseline,
                    "detector_runtime_sec_total",
                    "QK-MMD ZZ more expensive",
                )
            )

        utility_frames.append(compute_utility(by_seed, scenario))

    summary_all = pd.concat(summary_rows, ignore_index=True)
    paired_all = pd.DataFrame(paired_rows)
    utility_all = pd.concat(utility_frames, ignore_index=True)
    utility_strict = utility_all[utility_all["qk_better_ci95"]].copy()

    summary_all.to_csv(TABLES_DIR / "paper_table_multi_scenario_summary.csv", index=False)
    paired_all.to_csv(TABLES_DIR / "paper_table_multi_scenario_paired.csv", index=False)
    utility_all.to_csv(TABLES_DIR / "paper_table_multi_scenario_utility_grid.csv", index=False)
    utility_strict.to_csv(TABLES_DIR / "paper_table_multi_scenario_utility_strict_positive.csv", index=False)

    qk_vs_energy = paired_all[
        (
            (paired_all["method_a"] == "QK-MMD ZZ")
            & (paired_all["method_b"] == "Energy distance")
        )
        | (
            (paired_all["method_a"] == "Energy distance")
            & (paired_all["method_b"] == "QK-MMD ZZ")
        )
    ].copy()

    qk_summary = summary_all[
        summary_all["method"].isin(["qk_mmd_zz", "energy_distance", "mmd_rbf", "jsd", "ks_max"])
    ].copy()

    qk_summary = qk_summary.sort_values(["scenario", "cumulative_error_area_mean"])

    compact_cols = [
        "scenario",
        "method_label",
        "n_seeds",
        "mean_balanced_accuracy",
        "cumulative_error_area_mean",
        "cumulative_gain_vs_no_adapt_mean",
        "n_adaptations_mean",
        "adaptation_efficiency_mean",
        "detector_runtime_sec_total_mean",
    ]

    note = []
    note.append("# Paper 2 multi-scenario CICIDS progressive drift checkpoint 001")
    note.append("")
    note.append("## Purpose")
    note.append("")
    note.append(
        "This checkpoint consolidates the progressive readaptation results across three CICIDS2017 regimes:"
    )
    note.append("")
    note.append("- Tuesday -> Wednesday")
    note.append("- Tuesday -> Friday PortScan")
    note.append("- Tuesday -> Friday DDoS")
    note.append("")
    note.append("## Multi-scenario summary")
    note.append("")
    note.append(qk_summary[compact_cols].to_string(index=False))
    note.append("")
    note.append("## QK-MMD ZZ vs Energy distance paired comparisons")
    note.append("")
    note.append(qk_vs_energy.to_string(index=False))
    note.append("")
    note.append("## Strict positive utility regions")
    note.append("")
    if utility_strict.empty:
        note.append("No strict positive utility regions found.")
    else:
        note.append(utility_strict.to_string(index=False))
    note.append("")
    note.append("## Interpretation")
    note.append("")
    note.append(
        "Across three CICIDS2017 drift regimes, QK-MMD ZZ is consistently competitive with "
        "the strongest classical distributional baselines. The type of advantage is "
        "regime-dependent."
    )
    note.append("")
    note.append(
        "In Wednesday and DDoS, QK-MMD ZZ obtains comparable downstream performance to Energy "
        "distance while requiring fewer readaptations and achieving higher adaptation "
        "efficiency. Cost-sensitive utility favors QK-MMD ZZ when readaptation cost is "
        "non-negligible."
    )
    note.append("")
    note.append(
        "In PortScan, QK-MMD ZZ significantly improves downstream performance over Energy "
        "distance, but it requires more readaptations and therefore only dominates utility "
        "under low readaptation/runtime penalty settings."
    )
    note.append("")
    note.append(
        "The paper should therefore frame the contribution as regime-dependent quantum-kernel "
        "monitoring and operational trade-off analysis, not as universal quantum advantage."
    )
    note.append("")

    note_path = NOTES_DIR / "paper2_multi_scenario_cicids_checkpoint_001.md"
    note_path.write_text("\n".join(note), encoding="utf-8")

    print(f"Saved: {TABLES_DIR / 'paper_table_multi_scenario_summary.csv'}")
    print(f"Saved: {TABLES_DIR / 'paper_table_multi_scenario_paired.csv'}")
    print(f"Saved: {TABLES_DIR / 'paper_table_multi_scenario_utility_grid.csv'}")
    print(f"Saved: {TABLES_DIR / 'paper_table_multi_scenario_utility_strict_positive.csv'}")
    print(f"Saved: {note_path}")

    print()
    print("=== MULTI-SCENARIO SUMMARY ===")
    print(qk_summary[compact_cols].to_string(index=False))

    print()
    print("=== QK-MMD ZZ VS ENERGY DISTANCE ===")
    print(qk_vs_energy.to_string(index=False))


if __name__ == "__main__":
    main()
