from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def has_k_consecutive(flags, k: int) -> bool:
    count = 0
    for flag in flags:
        if bool(flag):
            count += 1
            if count >= k:
                return True
        else:
            count = 0
    return False


def first_k_consecutive_index(flags, k: int):
    count = 0
    for i, flag in enumerate(flags):
        if bool(flag):
            count += 1
            if count >= k:
                return i - k + 1
        else:
            count = 0
    return np.nan


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Policy sweep over anchored streaming window scores."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--quantiles", default="0.95,0.99,1.0")
    parser.add_argument("--ks", default="1,2,3")

    args = parser.parse_args()

    inp = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    quantiles = [float(x.strip()) for x in args.quantiles.split(",") if x.strip()]
    ks = [int(x.strip()) for x in args.ks.split(",") if x.strip()]

    df = pd.read_csv(inp)

    group_cols = [
        "dataset", "protocol", "seed", "detector", "q_feature_map",
        "q_input_scaling", "dim", "window_size", "stride", "alpha",
        "n_permutations",
    ]

    rows = []

    for q in quantiles:
        for k in ks:
            for keys, g in df.groupby(group_cols, dropna=False):
                base = dict(zip(group_cols, keys))

                cal = g[g["phase"] == "calibration"].sort_values("monitor_index")
                pre = g[g["phase"] == "pre_eval"].sort_values("monitor_index")
                post = g[g["phase"] == "post"].sort_values("monitor_index")

                if len(cal) < 3 or len(pre) == 0 or len(post) == 0:
                    continue

                threshold = float(cal["score"].quantile(q))

                pre_flags = (pre["score"] > threshold).to_list()
                post_flags = (post["score"] > threshold).to_list()

                pre_any = has_k_consecutive(pre_flags, k)
                post_any = has_k_consecutive(post_flags, k)

                delay = first_k_consecutive_index(post_flags, k) if post_any else np.nan

                row = dict(base)
                row.update({
                    "threshold_quantile": q,
                    "consecutive_k": k,
                    "empirical_threshold": threshold,

                    "false_alarm_any_pre": pre_any,
                    "false_alarm_rate_pre": float(np.mean(pre_flags)),

                    "post_detect_any": post_any,
                    "detection_rate_post": float(np.mean(post_flags)),
                    "detection_delay_windows": delay,

                    "cal_score_mean": float(cal["score"].mean()),
                    "pre_score_mean": float(pre["score"].mean()),
                    "post_score_mean": float(post["score"].mean()),
                    "score_gap_post_vs_pre": float(post["score"].mean() - pre["score"].mean()),
                })

                rows.append(row)

    seq = pd.DataFrame(rows)
    seq_out = outdir / "anchored_streaming_policy_sequence_summary.csv"
    seq.to_csv(seq_out, index=False)

    summary = (
        seq.groupby(
            [
                "threshold_quantile", "consecutive_k",
                "detector", "q_feature_map", "dim", "window_size", "stride",
            ],
            dropna=False,
        )
        .agg(
            n_sequences=("seed", "count"),
            false_alarm_any_rate=("false_alarm_any_pre", "mean"),
            false_alarm_rate_pre_mean=("false_alarm_rate_pre", "mean"),
            post_detect_any_rate=("post_detect_any", "mean"),
            detection_rate_post_mean=("detection_rate_post", "mean"),
            delay_windows_mean=("detection_delay_windows", "mean"),
            score_gap_mean=("score_gap_post_vs_pre", "mean"),
            threshold_mean=("empirical_threshold", "mean"),
        )
        .reset_index()
    )

    summary_out = outdir / "anchored_streaming_policy_sweep_summary.csv"
    summary.to_csv(summary_out, index=False)

    print("\n=== ANCHORED STREAMING POLICY SWEEP ===")
    print(summary.to_string(index=False))

    print(f"\nSaved: {seq_out}")
    print(f"Saved: {summary_out}")


if __name__ == "__main__":
    main()
