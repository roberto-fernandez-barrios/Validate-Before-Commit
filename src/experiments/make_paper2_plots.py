from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_detection_power(agg_csv: Path, outdir: Path) -> None:
    df = pd.read_csv(agg_csv)
    outdir.mkdir(parents=True, exist_ok=True)

    df = df[df["drift_type"] != "no_drift"].copy()

    for drift_type in sorted(df["drift_type"].unique()):
        subset = df[df["drift_type"] == drift_type]

        plt.figure(figsize=(8, 5))

        for dim in sorted(subset["dim"].unique()):
            s = subset[subset["dim"] == dim].sort_values("severity")
            plt.plot(
                s["severity"],
                s["detection_rate"],
                marker="o",
                label=f"dim={dim}",
            )

        plt.xlabel("Drift severity")
        plt.ylabel("Detection rate")
        plt.title(f"RBF-MMD detection power — {drift_type}")
        plt.ylim(-0.05, 1.05)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        output = outdir / f"detection_power_mmd_rbf_{drift_type}.png"
        plt.savefig(output, dpi=200)
        plt.close()

        print(f"Saved: {output}")


def plot_fpr(agg_csv: Path, outdir: Path) -> None:
    df = pd.read_csv(agg_csv)
    outdir.mkdir(parents=True, exist_ok=True)

    subset = df[df["drift_type"] == "no_drift"].copy()
    subset = subset.sort_values("dim")

    plt.figure(figsize=(7, 5))
    plt.bar(subset["dim"].astype(str), subset["detection_rate"])
    plt.axhline(float(subset["alpha"].iloc[0]), linestyle="--", label="target alpha")

    plt.xlabel("Dimension")
    plt.ylabel("Empirical FPR")
    plt.title("RBF-MMD calibration under no-drift")
    plt.ylim(0, max(0.2, subset["detection_rate"].max() + 0.05))
    plt.legend()
    plt.tight_layout()

    output = outdir / "fpr_calibration_mmd_rbf.png"
    plt.savefig(output, dpi=200)
    plt.close()

    print(f"Saved: {output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Make Paper 2 baseline plots.")
    parser.add_argument("--agg", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    plot_detection_power(args.agg, args.outdir)
    plot_fpr(args.agg, args.outdir)
