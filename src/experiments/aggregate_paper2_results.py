from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def aggregate_detection_results(input_csv: Path, output_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(input_csv)

    group_cols = [
        "dataset",
        "protocol",
        "detector",
        "drift_type",
        "severity",
        "dim",
        "window_size",
        "alpha",
        "n_permutations",
    ]

    agg = (
        df.groupby(group_cols, dropna=False)
        .agg(
            n_runs=("run_id", "count"),
            true_drift_mean=("true_drift", "mean"),
            detection_rate=("drift_detected", "mean"),
            score_mean=("score", "mean"),
            score_std=("score", "std"),
            threshold_mean=("threshold", "mean"),
            threshold_std=("threshold", "std"),
            p_value_mean=("p_value", "mean"),
            runtime_sec_mean=("runtime_sec", "mean"),
            runtime_sec_std=("runtime_sec", "std"),
        )
        .reset_index()
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(output_csv, index=False)

    return agg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate Paper 2 drift detection CSV results."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    agg = aggregate_detection_results(args.input, args.output)
    print(f"Saved: {args.output}")
    print(agg.to_string(index=False))
