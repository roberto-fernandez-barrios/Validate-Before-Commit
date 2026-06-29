from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


SCENARIOS = {
    "unsw_dos": {
        "label": "UNSW-NB15 DoS",
        "in_path": Path("results/raw/paper2_unsw_nb15_dos_medium_001/paper2_progressive_readaptation_by_seed.csv"),
        "outdir": Path("results/tables/paper2_unsw_nb15_dos_medium_001"),
        "targets": ["qk_mmd_pauli_xz", "qk_mmd_zz"],
    },
    "unsw_reconnaissance": {
        "label": "UNSW-NB15 Reconnaissance",
        "in_path": Path("results/raw/paper2_unsw_nb15_reconnaissance_medium_001/paper2_progressive_readaptation_by_seed.csv"),
        "outdir": Path("results/tables/paper2_unsw_nb15_reconnaissance_medium_001"),
        "targets": ["qk_mmd_zz", "qk_mmd_pauli_xz"],
    },
}

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
    "qk_mmd_pauli_xz",
]

BOOTSTRAP_SEED = 12345
N_BOOT = 10000


def ci95_paired_diff(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    diff = a - b
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    n = len(diff)
    boots = np.empty(N_BOOT, dtype=float)

    for i in range(N_BOOT):
        idx = rng.integers(0, n, size=n)
        boots[i] = diff[idx].mean()

    return float(diff.mean()), float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    cols = {
        "n_seeds": ("seed", "nunique"),
        "mean_balanced_accuracy": ("mean_balanced_accuracy", "mean"),
        "cumulative_error_area": ("cumulative_error_area", "mean"),
        "cumulative_gain_vs_no_adapt": ("cumulative_gain_vs_no_adapt", "mean"),
        "n_adaptations": ("n_adaptations", "mean"),
        "detector_runtime_sec_total": ("detector_runtime_sec_total", "mean"),
    }

    out = df.groupby("method").agg(**cols).reset_index()
    out["method_label"] = out["method"].map(METHOD_LABELS).fillna(out["method"])
    out = out.sort_values("mean_balanced_accuracy", ascending=False)
    return out


def paired_for_target(df: pd.DataFrame, scenario_label: str, target: str) -> pd.DataFrame:
    rows = []

    for baseline in BASELINES:
        if baseline == target:
            continue

        a_df = df[df["method"] == target].sort_values("seed")
        b_df = df[df["method"] == baseline].sort_values("seed")

        common = sorted(set(a_df["seed"]).intersection(set(b_df["seed"])))
        if not common:
            continue

        a_df = a_df[a_df["seed"].isin(common)].sort_values("seed")
        b_df = b_df[b_df["seed"].isin(common)].sort_values("seed")

        for metric in METRICS:
            mean_diff, lo, hi = ci95_paired_diff(
                a_df[metric].to_numpy(dtype=float),
                b_df[metric].to_numpy(dtype=float),
            )

            rows.append(
                {
                    "scenario": scenario_label,
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

    return pd.DataFrame(rows)


def main() -> None:
    for scenario_key, cfg in SCENARIOS.items():
        in_path = cfg["in_path"]
        outdir = cfg["outdir"]
        outdir.mkdir(parents=True, exist_ok=True)

        print("=" * 120)
        print("[SCENARIO]", scenario_key)
        print("[LOAD]", in_path)

        df = pd.read_csv(in_path)

        summary = summarize(df)
        summary_path = outdir / f"paper_table_{scenario_key}_medium_summary.csv"
        summary.to_csv(summary_path, index=False)

        print("[SUMMARY]")
        print(summary.to_string(index=False))
        print("Saved:", summary_path)

        all_paired = []

        for target in cfg["targets"]:
            paired = paired_for_target(df, cfg["label"], target)
            target_safe = target.replace("qk_mmd_", "qk_")
            paired_path = outdir / f"paper_table_{scenario_key}_medium_{target_safe}_paired.csv"
            paired.to_csv(paired_path, index=False)
            all_paired.append(paired)

            print()
            print(f"[PAIRED] {METHOD_LABELS[target]}")
            print(paired.to_string(index=False))
            print("Saved:", paired_path)

        combined = pd.concat(all_paired, ignore_index=True)
        combined_path = outdir / f"paper_table_{scenario_key}_medium_qk_paired_all.csv"
        combined.to_csv(combined_path, index=False)
        print("Saved:", combined_path)


if __name__ == "__main__":
    main()
