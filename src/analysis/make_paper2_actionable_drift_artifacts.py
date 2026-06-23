from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUTDIR = Path("results/tables/paper2_actionable_drift_wednesday_001")
NOTES_DIR = Path("notes")

ADVERSARIAL_BY_SEED = Path("results/raw/paper2_progressive_classical_baselines_final_001/paper2_progressive_readaptation_by_seed.csv")
BENIGN_WED_BY_SEED = Path("results/raw/paper2_nuisance_benign_wednesday_final_001/paper2_nuisance_benign_by_seed.csv")
NODRIFT_BY_SEED = Path("results/raw/paper2_nuisance_benign_tuesday_tuesday_final_001/paper2_nuisance_benign_by_seed.csv")

METHOD_LABELS = {
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


def load_inputs() -> pd.DataFrame:
    adv = pd.read_csv(ADVERSARIAL_BY_SEED)
    benign = pd.read_csv(BENIGN_WED_BY_SEED)
    nodrift = pd.read_csv(NODRIFT_BY_SEED)

    adv = adv.rename(
        columns={
            "cumulative_gain_vs_no_adapt": "adversarial_gain",
            "n_adaptations": "adversarial_readaptations",
            "detector_runtime_sec_total": "adversarial_runtime",
        }
    )

    benign = benign.rename(
        columns={
            "n_nuisance_triggers": "benign_nuisance_triggers",
            "nuisance_alarm_rate": "benign_alarm_rate",
            "nuisance_trigger_rate": "benign_trigger_rate",
            "detector_runtime_sec_total": "benign_runtime",
        }
    )

    nodrift = nodrift.rename(
        columns={
            "n_nuisance_triggers": "nodrift_nuisance_triggers",
            "nuisance_alarm_rate": "nodrift_alarm_rate",
            "nuisance_trigger_rate": "nodrift_trigger_rate",
            "detector_runtime_sec_total": "nodrift_runtime",
        }
    )

    cols_adv = [
        "seed",
        "method",
        "adversarial_gain",
        "adversarial_readaptations",
        "adversarial_runtime",
        "mean_balanced_accuracy",
        "cumulative_error_area",
    ]

    cols_benign = [
        "seed",
        "method",
        "benign_nuisance_triggers",
        "benign_alarm_rate",
        "benign_trigger_rate",
        "benign_runtime",
    ]

    cols_nodrift = [
        "seed",
        "method",
        "nodrift_nuisance_triggers",
        "nodrift_alarm_rate",
        "nodrift_trigger_rate",
        "nodrift_runtime",
    ]

    merged = (
        adv[cols_adv]
        .merge(benign[cols_benign], on=["seed", "method"], how="inner")
        .merge(nodrift[cols_nodrift], on=["seed", "method"], how="inner")
    )

    merged["excess_nuisance_triggers"] = (
        merged["benign_nuisance_triggers"] - merged["nodrift_nuisance_triggers"]
    )
    merged["excess_nuisance_triggers_clipped"] = merged["excess_nuisance_triggers"].clip(lower=0.0)

    merged["total_runtime_adv_plus_benign"] = (
        merged["adversarial_runtime"] + merged["benign_runtime"]
    )

    merged["method_label"] = merged["method"].map(METHOD_LABELS).fillna(merged["method"])

    return merged


def summarize_components(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["method", "method_label"], dropna=False)
        .agg(
            n_seeds=("seed", "nunique"),
            adversarial_gain_mean=("adversarial_gain", "mean"),
            adversarial_readaptations_mean=("adversarial_readaptations", "mean"),
            benign_nuisance_triggers_mean=("benign_nuisance_triggers", "mean"),
            nodrift_nuisance_triggers_mean=("nodrift_nuisance_triggers", "mean"),
            excess_nuisance_triggers_mean=("excess_nuisance_triggers", "mean"),
            excess_nuisance_triggers_clipped_mean=("excess_nuisance_triggers_clipped", "mean"),
            mean_balanced_accuracy=("mean_balanced_accuracy", "mean"),
            cumulative_error_area_mean=("cumulative_error_area", "mean"),
            total_runtime_adv_plus_benign_mean=("total_runtime_adv_plus_benign", "mean"),
        )
        .reset_index()
        .sort_values("excess_nuisance_triggers_mean")
    )


def compute_actionable_utility(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    paired_rows = []

    lambdas = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0]
    etas = [0.0, 0.25, 0.5, 1.0, 2.0]
    gammas = [0.0, 0.01, 0.05, 0.1]

    baselines = ["energy_distance", "mmd_rbf", "ks_max", "jsd", "qk_mmd_pauli_xz"]

    for nuisance_mode in ["total", "excess_clipped"]:
        nuisance_col = (
            "benign_nuisance_triggers"
            if nuisance_mode == "total"
            else "excess_nuisance_triggers_clipped"
        )

        for lambda_cost in lambdas:
            for eta_cost in etas:
                for gamma_cost in gammas:
                    work = df.copy()

                    work["actionable_utility"] = (
                        work["adversarial_gain"]
                        - lambda_cost * work["adversarial_readaptations"]
                        - eta_cost * work[nuisance_col]
                        - gamma_cost * work["total_runtime_adv_plus_benign"]
                    )

                    summary = (
                        work.groupby(["method", "method_label"], dropna=False)
                        .agg(
                            n_seeds=("seed", "nunique"),
                            actionable_utility_mean=("actionable_utility", "mean"),
                        )
                        .reset_index()
                    )

                    summary["lambda_cost"] = lambda_cost
                    summary["eta_cost"] = eta_cost
                    summary["gamma_cost"] = gamma_cost
                    summary["nuisance_mode"] = nuisance_mode
                    rows.append(summary)

                    qk = work[work["method"] == "qk_mmd_zz"][["seed", "actionable_utility"]].rename(
                        columns={"actionable_utility": "qk"}
                    )

                    for baseline in baselines:
                        b = work[work["method"] == baseline][["seed", "actionable_utility"]].rename(
                            columns={"actionable_utility": "baseline"}
                        )

                        merged = qk.merge(b, on="seed", how="inner")
                        diff = merged["qk"].to_numpy() - merged["baseline"].to_numpy()
                        stats = bootstrap_ci(diff)

                        paired_rows.append(
                            {
                                "baseline": METHOD_LABELS[baseline],
                                "lambda_cost": lambda_cost,
                                "eta_cost": eta_cost,
                                "gamma_cost": gamma_cost,
                                "nuisance_mode": nuisance_mode,
                                "mean_actionable_utility_diff_qk_minus_baseline": stats["mean"],
                                "ci95_low": stats["ci95_low"],
                                "ci95_high": stats["ci95_high"],
                                "prob_diff_gt_0": stats["prob_gt_0"],
                                "qk_better_ci95": bool(stats["ci95_low"] > 0),
                            }
                        )

    utility_summary = pd.concat(rows, ignore_index=True)
    paired = pd.DataFrame(paired_rows)

    return utility_summary, paired


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_inputs()

    components = summarize_components(df)
    utility_summary, paired = compute_actionable_utility(df)

    strict = paired[paired["qk_better_ci95"]].copy()

    components.to_csv(OUTDIR / "paper_table_actionable_components.csv", index=False)
    utility_summary.to_csv(OUTDIR / "paper_table_actionable_utility_grid.csv", index=False)
    paired.to_csv(OUTDIR / "paper_table_actionable_utility_paired.csv", index=False)
    strict.to_csv(OUTDIR / "paper_table_actionable_utility_strict_positive.csv", index=False)

    note = []
    note.append("# Paper 2 actionable drift checkpoint 001")
    note.append("")
    note.append("## Purpose")
    note.append("")
    note.append(
        "This checkpoint evaluates whether adversarial drift benefits remain useful after "
        "penalizing nuisance/non-adversarial triggers measured on benign-only streams."
    )
    note.append("")
    note.append("## Component summary")
    note.append("")
    note.append(components.to_string(index=False))
    note.append("")
    note.append("## Strict positive actionable utility regions for QK-MMD ZZ")
    note.append("")
    if strict.empty:
        note.append("No strict positive actionable utility regions found.")
    else:
        note.append(strict.to_string(index=False))
    note.append("")
    note.append("## Interpretation guardrail")
    note.append("")
    note.append(
        "The benign control does not support the claim that QK-MMD ZZ universally reduces "
        "nuisance triggers. Its value must therefore be framed through cost-sensitive "
        "actionable utility rather than benign-trigger suppression alone."
    )
    note.append("")

    note_path = NOTES_DIR / "paper2_actionable_drift_checkpoint_001.md"
    note_path.write_text("\n".join(note), encoding="utf-8")

    print(f"Saved: {OUTDIR / 'paper_table_actionable_components.csv'}")
    print(f"Saved: {OUTDIR / 'paper_table_actionable_utility_grid.csv'}")
    print(f"Saved: {OUTDIR / 'paper_table_actionable_utility_paired.csv'}")
    print(f"Saved: {OUTDIR / 'paper_table_actionable_utility_strict_positive.csv'}")
    print(f"Saved: {note_path}")

    print()
    print("=== ACTIONABLE COMPONENT SUMMARY ===")
    print(components.to_string(index=False))

    print()
    print("=== STRICT POSITIVE ACTIONABLE UTILITY REGIONS ===")
    if strict.empty:
        print("No strict positive actionable utility regions found.")
    else:
        print(strict.to_string(index=False))


if __name__ == "__main__":
    main()
