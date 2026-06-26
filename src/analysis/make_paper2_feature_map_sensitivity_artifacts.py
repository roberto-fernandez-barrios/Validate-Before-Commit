from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


CONFIGS = {
    "zz_r1": {
        "method": "qk_mmd_zz",
        "feature_map_family": "ZZ",
        "q_reps": 1,
    },
    "zz_r2": {
        "method": "qk_mmd_zz",
        "feature_map_family": "ZZ",
        "q_reps": 2,
    },
    "zz_r3": {
        "method": "qk_mmd_zz",
        "feature_map_family": "ZZ",
        "q_reps": 3,
    },
    "paulixz_r1": {
        "method": "qk_mmd_pauli_xz",
        "feature_map_family": "PauliXZ",
        "q_reps": 1,
    },
    "paulixz_r2": {
        "method": "qk_mmd_pauli_xz",
        "feature_map_family": "PauliXZ",
        "q_reps": 2,
    },
    "paulixz_r3": {
        "method": "qk_mmd_pauli_xz",
        "feature_map_family": "PauliXZ",
        "q_reps": 3,
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--mode", type=str, default="smoke")
    parser.add_argument("--scenario", type=str, default="wednesday")
    parser.add_argument("--raw-root", type=Path, default=Path("results/raw"))
    parser.add_argument("--out-root", type=Path, default=Path("results/tables"))

    args = parser.parse_args()

    raw_root = args.raw_root / f"paper2_feature_map_sensitivity_{args.mode}_001" / args.scenario
    outdir = args.out_root / f"paper2_feature_map_sensitivity_{args.mode}_001"
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []

    for config_key, meta in CONFIGS.items():
        path = raw_root / config_key / "paper2_progressive_readaptation_summary.csv"

        if not path.exists():
            print(f"[WARN] Missing: {path}")
            continue

        df = pd.read_csv(path)

        df["scenario"] = args.scenario
        df["feature_map_config"] = config_key
        df["feature_map_family"] = meta["feature_map_family"]
        df["q_reps"] = meta["q_reps"]

        rows.append(df)

    if not rows:
        raise RuntimeError(f"No result files found under {raw_root}")

    out = pd.concat(rows, ignore_index=True)

    if "adaptation_efficiency_mean" not in out.columns:
        out["adaptation_efficiency_mean"] = out["cumulative_gain_vs_no_adapt_mean"] / out["n_adaptations_mean"].replace(0, pd.NA)

    sort_cols = [
        "scenario",
        "cumulative_error_area_mean",
        "n_adaptations_mean",
        "detector_runtime_sec_total_mean",
    ]
    sort_cols = [c for c in sort_cols if c in out.columns]

    out = out.sort_values(sort_cols)

    out_path = outdir / f"paper_table_feature_map_sensitivity_{args.scenario}_{args.mode}.csv"
    out.to_csv(out_path, index=False)

    compact_cols = [
        "scenario",
        "feature_map_config",
        "feature_map_family",
        "q_reps",
        "method",
        "n_seeds",
        "mean_balanced_accuracy",
        "cumulative_error_area_mean",
        "cumulative_gain_vs_no_adapt_mean",
        "n_adaptations_mean",
        "adaptation_efficiency_mean",
        "alarm_rate_mean",
        "trigger_rate_mean",
        "detector_runtime_sec_total_mean",
    ]

    compact_cols = [c for c in compact_cols if c in out.columns]

    print(f"Saved: {out_path}")
    print()
    print("=== FEATURE MAP SENSITIVITY SUMMARY ===")
    print(out[compact_cols].to_string(index=False))


if __name__ == "__main__":
    main()
