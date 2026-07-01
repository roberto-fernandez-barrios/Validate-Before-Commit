from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


IN_PATH = Path("results/raw/paper2_progressive_thursday_webattacks_final_001/paper2_progressive_readaptation_by_seed.csv")
OUTDIR = Path("results/tables/paper2_progressive_thursday_webattacks_final_001")
OUTDIR.mkdir(parents=True, exist_ok=True)

BOOTSTRAP_SEED = 12345
N_BOOT = 10000

METHOD_LABELS = {
    "energy_distance": "Energy distance",
    "mmd_rbf": "MMD-RBF",
    "ks_max": "KS-max",
    "jsd": "JSD",
    "qk_mmd_zz": "QK-MMD ZZ",
    "qk_mmd_pauli_xz": "QK-MMD PauliXZ",
    "no_adaptation": "No adaptation",
}

METRICS = [
    "mean_balanced_accuracy",
    "cumulative_error_area",
    "cumulative_gain_vs_no_adapt",
    "n_adaptations",
    "detector_runtime_sec_total",
]

BASELINES = [
    "energy_distance",
    "mmd_rbf",
    "ks_max",
    "jsd",
    "qk_mmd_zz",
]


def ci95_paired_diff(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    diff = a - b
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    boots = []
    n = len(diff)

    for _ in range(N_BOOT):
        idx = rng.integers(0, n, size=n)
        boots.append(float(diff[idx].mean()))

    boots = np.asarray(boots)
    return float(diff.mean()), float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))


def main() -> None:
    df = pd.read_csv(IN_PATH)

    print("[LOAD]", IN_PATH)
    print(df.head())
    print(df.columns.tolist())

    summary = (
        df.groupby("method", dropna=False)
        .agg(
            n_seeds=("seed", "nunique"),
            mean_balanced_accuracy=("mean_balanced_accuracy", "mean"),
            cumulative_error_area=("cumulative_error_area", "mean"),
            cumulative_gain_vs_no_adapt=("cumulative_gain_vs_no_adapt", "mean"),
            n_adaptations=("n_adaptations", "mean"),
            detector_runtime_sec_total=("detector_runtime_sec_total", "mean"),
        )
        .reset_index()
    )

    summary["method_label"] = summary["method"].map(METHOD_LABELS).fillna(summary["method"])
    summary = summary.sort_values("mean_balanced_accuracy", ascending=False)

    paired_rows = []

    target = "qk_mmd_pauli_xz"

    for baseline in BASELINES:
        if baseline == target:
            continue

        a_df = df[df["method"] == target].sort_values("seed")
        b_df = df[df["method"] == baseline].sort_values("seed")

        common = sorted(set(a_df["seed"]).intersection(set(b_df["seed"])))
        a_df = a_df[a_df["seed"].isin(common)].sort_values("seed")
        b_df = b_df[b_df["seed"].isin(common)].sort_values("seed")

        for metric in METRICS:
            mean_diff, lo, hi = ci95_paired_diff(
                a_df[metric].to_numpy(dtype=float),
                b_df[metric].to_numpy(dtype=float),
            )

            paired_rows.append(
                {
                    "scenario": "Thursday WebAttacks",
                    "method_a": METHOD_LABELS[target],
                    "method_b": METHOD_LABELS[baseline],
                    "metric": metric,
                    "n_pairs": len(common),
                    "mean_diff_a_minus_b": mean_diff,
                    "ci95_low": lo,
                    "ci95_high": hi,
                    "ci_excludes_zero_positive": bool(lo > 0),
                    "ci_excludes_zero_negative": bool(hi < 0),
                }
            )

    paired = pd.DataFrame(paired_rows)

    summary_path = OUTDIR / "paper_table_thursday_webattacks_summary.csv"
    paired_path = OUTDIR / "paper_table_thursday_webattacks_qk_paulixz_paired.csv"

    summary.to_csv(summary_path, index=False)
    paired.to_csv(paired_path, index=False)

    print("Saved:", summary_path)
    print("Saved:", paired_path)

    print()
    print("=== SUMMARY ===")
    print(summary.to_string(index=False))

    print()
    print("=== PAIRED QK PauliXZ vs baselines ===")
    print(paired.to_string(index=False))


if __name__ == "__main__":
    main()
