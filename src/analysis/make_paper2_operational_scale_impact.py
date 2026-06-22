from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def save_table(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def safe_read(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def main() -> None:
    outdir = Path("results/tables/paper2_operational_scale_impact_001")
    notes_dir = Path("notes")

    outdir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    geometry_path = Path(
        "results/tables/paper2_geometry_diagnostics_001/"
        "paper_table_geometry_vs_downstream.csv"
    )

    paired_path = Path(
        "results/tables/paper2_statistical_summary_001/"
        "paper_table_downstream_main_paired_comparisons.csv"
    )

    geometry = safe_read(geometry_path)
    paired = safe_read(paired_path)

    traffic_volumes = [
        10_000,
        100_000,
        1_000_000,
        10_000_000,
        100_000_000,
    ]

    window_size = 128

    methods = [
        "MMD-RBF",
        "QK-MMD ZZ",
        "QK-MMD PauliXZ",
    ]

    geometry = geometry[geometry["method"].isin(methods)].copy()

    rows = []

    for severity, sev_df in geometry.groupby("severity"):
        mmd_rows = sev_df[sev_df["method"] == "MMD-RBF"]

        if mmd_rows.empty:
            continue

        mmd = mmd_rows.iloc[0]

        for _, row in sev_df.iterrows():
            for traffic_volume in traffic_volumes:
                total_windows = traffic_volume / window_size

                post_alarm_rate = float(row["alarm_rate_post"])
                false_alarm_rate = float(row["false_alarm_any_rate"])
                clean_gain = float(row["clean_adaptation_gain_mean"])
                degradation_area = float(row["degradation_area_mean"])

                mmd_post_alarm_rate = float(mmd["alarm_rate_post"])
                mmd_false_alarm_rate = float(mmd["false_alarm_any_rate"])
                mmd_clean_gain = float(mmd["clean_adaptation_gain_mean"])
                mmd_degradation_area = float(mmd["degradation_area_mean"])

                post_alarm_delta_vs_mmd = post_alarm_rate - mmd_post_alarm_rate
                false_alarm_delta_vs_mmd = false_alarm_rate - mmd_false_alarm_rate
                clean_gain_delta_vs_mmd = clean_gain - mmd_clean_gain
                degradation_area_delta_vs_mmd = degradation_area - mmd_degradation_area

                additional_detected_flow_equiv_vs_mmd = (
                    post_alarm_delta_vs_mmd * traffic_volume
                )

                missed_drift_flow_equiv = (
                    (1.0 - post_alarm_rate) * traffic_volume
                )

                detected_drift_flow_equiv = (
                    post_alarm_rate * traffic_volume
                )

                scaled_clean_gain_units = clean_gain * traffic_volume
                scaled_degradation_units = degradation_area * traffic_volume

                clean_gain_units_delta_vs_mmd = (
                    clean_gain_delta_vs_mmd * traffic_volume
                )

                # Positive means this method has lower degradation than MMD-RBF.
                degradation_units_saved_vs_mmd = (
                    (mmd_degradation_area - degradation_area) * traffic_volume
                )

                false_alarm_flow_equiv_delta_vs_mmd = (
                    false_alarm_delta_vs_mmd * traffic_volume
                )

                is_quantum = row["method"].startswith("QK-MMD")

                # Candidate zone:
                # QK-MMD must provide a non-trivial post-drift alarm persistence gain
                # without materially hurting clean downstream gain or false alarms.
                quantum_candidate_zone = (
                    is_quantum
                    and post_alarm_delta_vs_mmd >= 0.05
                    and clean_gain_delta_vs_mmd >= -0.01
                    and false_alarm_delta_vs_mmd <= 0.05
                )

                # Strong operational zone:
                # The monitoring advantage must also become large at scale.
                quantum_strong_operational_zone = (
                    quantum_candidate_zone
                    and additional_detected_flow_equiv_vs_mmd >= 100_000
                )

                # Strict zone for paper-facing claims:
                # more monitoring coverage, no clean-gain loss, no false-alarm penalty,
                # and large enough effect at scale.
                quantum_strict_operational_zone = (
                    quantum_strong_operational_zone
                    and clean_gain_delta_vs_mmd >= 0.0
                    and false_alarm_delta_vs_mmd <= 0.0
                )

                rows.append(
                    {
                        "severity": severity,
                        "method": row["method"],
                        "traffic_volume": traffic_volume,
                        "window_size": window_size,
                        "estimated_total_windows": total_windows,
                        "post_alarm_rate": post_alarm_rate,
                        "false_alarm_rate": false_alarm_rate,
                        "clean_adaptation_gain": clean_gain,
                        "degradation_area": degradation_area,
                        "detected_drift_flow_equiv": detected_drift_flow_equiv,
                        "missed_drift_flow_equiv": missed_drift_flow_equiv,
                        "scaled_clean_gain_units": scaled_clean_gain_units,
                        "scaled_degradation_units": scaled_degradation_units,
                        "post_alarm_delta_vs_mmd": post_alarm_delta_vs_mmd,
                        "false_alarm_delta_vs_mmd": false_alarm_delta_vs_mmd,
                        "clean_gain_delta_vs_mmd": clean_gain_delta_vs_mmd,
                        "degradation_area_delta_vs_mmd": degradation_area_delta_vs_mmd,
                        "additional_detected_flow_equiv_vs_mmd": additional_detected_flow_equiv_vs_mmd,
                        "clean_gain_units_delta_vs_mmd": clean_gain_units_delta_vs_mmd,
                        "degradation_units_saved_vs_mmd": degradation_units_saved_vs_mmd,
                        "false_alarm_flow_equiv_delta_vs_mmd": false_alarm_flow_equiv_delta_vs_mmd,
                        "quantum_candidate_zone": quantum_candidate_zone,
                        "quantum_strong_operational_zone": quantum_strong_operational_zone,
                        "quantum_strict_operational_zone": quantum_strict_operational_zone,
                    }
                )

    scale_df = pd.DataFrame(rows)

    save_table(
        scale_df,
        outdir / "paper_table_operational_scale_by_method.csv",
    )

    advantage_zones = scale_df[
        scale_df["quantum_candidate_zone"]
    ].copy()

    advantage_zones = advantage_zones.sort_values(
        [
            "quantum_strong_operational_zone",
            "severity",
            "traffic_volume",
            "additional_detected_flow_equiv_vs_mmd",
        ],
        ascending=[False, True, True, False],
    )

    save_table(
        advantage_zones,
        outdir / "paper_table_quantum_operational_advantage_zones.csv",
    )

    strong_zones = scale_df[
        scale_df["quantum_strong_operational_zone"]
    ].copy()

    save_table(
        strong_zones,
        outdir / "paper_table_quantum_strong_operational_zones.csv",
    )

    strict_zones = scale_df[
        scale_df["quantum_strict_operational_zone"]
    ].copy()

    save_table(
        strict_zones,
        outdir / "paper_table_quantum_strict_operational_zones.csv",
    )

    # Scale paired differences from statistical summary.
    pair_rows = []

    for _, row in paired.iterrows():
        for traffic_volume in traffic_volumes:
            mean_diff = float(row["mean_diff_a_minus_b"])
            ci_low = float(row["ci95_low"])
            ci_high = float(row["ci95_high"])

            pair_rows.append(
                {
                    "experiment_block": row["experiment_block"],
                    "severity": row["severity"],
                    "method_a": row["method_a"],
                    "method_b": row["method_b"],
                    "metric": row["metric"],
                    "traffic_volume": traffic_volume,
                    "mean_diff_a_minus_b": mean_diff,
                    "ci95_low": ci_low,
                    "ci95_high": ci_high,
                    "scaled_mean_diff": mean_diff * traffic_volume,
                    "scaled_ci95_low": ci_low * traffic_volume,
                    "scaled_ci95_high": ci_high * traffic_volume,
                    "prob_diff_gt_0": row["prob_diff_gt_0"],
                }
            )

    pair_scale_df = pd.DataFrame(pair_rows)

    save_table(
        pair_scale_df,
        outdir / "paper_table_operational_scale_paired_differences.csv",
    )

    # Key readable subset.
    key_pairs = pair_scale_df[
        (
            (pair_scale_df["severity"].isin([0.25, 1.0]))
            & (pair_scale_df["traffic_volume"].isin([1_000_000, 10_000_000, 100_000_000]))
            & (pair_scale_df["metric"].isin(["clean_adaptation_gain", "degradation_area"]))
        )
    ].copy()

    save_table(
        key_pairs,
        outdir / "paper_table_operational_scale_key_paired_differences.csv",
    )

    # Write interpretation note.
    note_lines = [
        "# Paper 2 operational scale impact checkpoint 001",
        "",
        "## Purpose",
        "",
        "This analysis evaluates whether small detector/adaptation differences can",
        "become operationally meaningful at high traffic volume.",
        "",
        "It does not claim exact numbers of additional correct classifications.",
        "Instead, it defines flow-equivalent operational impact proxies.",
        "",
        "## Metrics",
        "",
        "- detected_drift_flow_equiv = post_alarm_rate * traffic_volume",
        "- missed_drift_flow_equiv = (1 - post_alarm_rate) * traffic_volume",
        "- additional_detected_flow_equiv_vs_mmd = (post_alarm_rate_method - post_alarm_rate_mmd) * traffic_volume",
        "- scaled_clean_gain_units = clean_adaptation_gain * traffic_volume",
        "- degradation_units_saved_vs_mmd = (degradation_mmd - degradation_method) * traffic_volume",
        "",
        "## Quantum candidate zone criterion",
        "",
        "A QK-MMD method is marked as a candidate operational advantage zone when:",
        "",
        "- post_alarm_rate_qk > post_alarm_rate_mmd",
        "- clean_gain_qk is not worse than MMD-RBF by more than 0.01",
        "- false_alarm_qk is not higher than MMD-RBF by more than 0.05",
        "",
        "A strong operational zone additionally requires:",
        "",
        "- additional_detected_flow_equiv_vs_mmd >= 100000",
        "",
        "## Generated tables",
        "",
        f"- `{outdir / 'paper_table_operational_scale_by_method.csv'}`",
        f"- `{outdir / 'paper_table_quantum_operational_advantage_zones.csv'}`",
        f"- `{outdir / 'paper_table_quantum_strong_operational_zones.csv'}`",
        f"- `{outdir / 'paper_table_quantum_strict_operational_zones.csv'}`",
        f"- `{outdir / 'paper_table_operational_scale_paired_differences.csv'}`",
        f"- `{outdir / 'paper_table_operational_scale_key_paired_differences.csv'}`",
        "",
    ]

    if strong_zones.empty:
        note_lines.extend(
            [
                "## Main result",
                "",
                "No strong quantum operational zone was found under the current criterion.",
                "",
            ]
        )
    else:
        preview_cols = [
            "severity",
            "method",
            "traffic_volume",
            "post_alarm_delta_vs_mmd",
            "additional_detected_flow_equiv_vs_mmd",
            "clean_gain_delta_vs_mmd",
            "false_alarm_delta_vs_mmd",
        ]

        note_lines.extend(
            [
                "## Main result",
                "",
                "Strong quantum operational zones were found under the current criterion.",
                "",
                strong_zones[preview_cols].to_string(index=False),
                "",
            ]
        )

    note_lines.extend(
        [
            "## Paper interpretation",
            "",
            "This analysis should be presented as an operational scaling proxy.",
            "It supports the question of whether small monitoring gains can matter",
            "at high traffic volume.",
            "",
            "It should not be presented as direct proof of more correctly classified",
            "samples unless a later experiment computes sample-level errors directly.",
            "",
        ]
    )

    note_path = notes_dir / "paper2_operational_scale_impact_checkpoint_001.md"
    note_path.write_text("\n".join(note_lines), encoding="utf-8")

    print(f"Saved tables in: {outdir}")
    print(f"Saved note: {note_path}")

    print()
    print("=== QUANTUM OPERATIONAL ADVANTAGE ZONES ===")
    if advantage_zones.empty:
        print("No candidate zones found.")
    else:
        cols = [
            "severity",
            "method",
            "traffic_volume",
            "post_alarm_delta_vs_mmd",
            "additional_detected_flow_equiv_vs_mmd",
            "clean_gain_delta_vs_mmd",
            "false_alarm_delta_vs_mmd",
            "quantum_strong_operational_zone",
        ]
        print(advantage_zones[cols].to_string(index=False))

    print()
    print("=== KEY PAIRED DIFFERENCES AT SCALE ===")
    print(key_pairs.to_string(index=False))


if __name__ == "__main__":
    main()
