from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler

from src.drift_detection.mmd_rbf_detector import MmdRbfDetector
from src.drift_detection.qk_mmd_detector import QkMmdDetector


def parse_csv_list(value: str, cast=str):
    return [cast(x.strip()) for x in value.split(",") if x.strip()]


def parse_label_values(value: str | None) -> set[str] | None:
    if value is None or not str(value).strip():
        return None
    return {x.strip() for x in value.split(",") if x.strip()}


def load_numeric_csv(
    path: Path,
    label_col: str | None,
    label_values: set[str] | None,
    max_rows: int | None,
) -> pd.DataFrame:
    df = pd.read_csv(path, nrows=max_rows)
    df.columns = [str(c).strip() for c in df.columns]

    if label_col and label_col in df.columns:
        if label_values:
            labels = df[label_col].astype(str).str.strip()
            df = df[labels.isin(label_values)].copy()
        df = df.drop(columns=[label_col])

    df = df.replace([np.inf, -np.inf], np.nan)

    numeric = df.select_dtypes(include=[np.number]).copy()
    numeric = numeric.dropna(axis=1, how="all")
    numeric = numeric.fillna(numeric.median(numeric_only=True))
    numeric = numeric.fillna(0.0)

    nunique = numeric.nunique(dropna=False)
    numeric = numeric.loc[:, nunique > 1]

    if numeric.shape[1] == 0:
        raise ValueError(f"No usable numeric columns found in {path}")

    return numeric.astype(np.float64)


def align_columns(a: pd.DataFrame, b: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    common = sorted(set(a.columns).intersection(set(b.columns)))
    if not common:
        raise ValueError("Reference and current datasets have no common numeric columns.")
    return a[common], b[common]


def sample_contiguous_window(
    X: np.ndarray,
    window_size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if len(X) < window_size:
        raise ValueError(f"Need at least {window_size} rows, available {len(X)}")
    start = int(rng.integers(0, len(X) - window_size + 1))
    return X[start:start + window_size]


def sample_contiguous_stream(
    X: np.ndarray,
    n_windows: int,
    window_size: int,
    stride: int,
    rng: np.random.Generator,
) -> tuple[list[np.ndarray], int]:
    total = window_size + (n_windows - 1) * stride
    if len(X) < total:
        raise ValueError(f"Need at least {total} rows for stream, available {len(X)}")

    start = int(rng.integers(0, len(X) - total + 1))
    windows = [
        X[start + i * stride:start + i * stride + window_size]
        for i in range(n_windows)
    ]
    return windows, start


def fit_reference_reducer(
    X_ref: np.ndarray,
    dim: int,
    seed: int,
):
    scaler = StandardScaler()
    X_ref_s = scaler.fit_transform(X_ref)

    max_dim = min(dim, X_ref_s.shape[1] - 1, X_ref_s.shape[0] - 1)
    if max_dim < 1:
        raise ValueError("Not enough features/samples after preprocessing.")

    svd = TruncatedSVD(n_components=max_dim, random_state=seed)
    X_ref_z = svd.fit_transform(X_ref_s)

    return scaler, svd, X_ref_z.astype(np.float64)


def transform_window(
    X: np.ndarray,
    scaler: StandardScaler,
    svd: TruncatedSVD,
) -> np.ndarray:
    return svd.transform(scaler.transform(X)).astype(np.float64)


def make_detector(
    detector_name: str,
    q_feature_map: str,
    q_reps: int,
    q_input_scaling: str,
    alpha: float,
    n_permutations: int,
    random_state: int,
):
    if detector_name == "mmd_rbf":
        return MmdRbfDetector(
            alpha=alpha,
            n_permutations=n_permutations,
            random_state=random_state,
        )

    if detector_name == "qk_mmd":
        return QkMmdDetector(
            feature_map=q_feature_map,
            reps=q_reps,
            alpha=alpha,
            n_permutations=n_permutations,
            random_state=random_state,
            input_scaling=q_input_scaling,
        )

    raise ValueError(f"Unknown detector: {detector_name}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paper 2 streaming detection-delay benchmark."
    )

    parser.add_argument("--data-ref", required=True)
    parser.add_argument("--data-cur", required=True)
    parser.add_argument("--label-col", default="Label")
    parser.add_argument("--label-values-ref", default="")
    parser.add_argument("--label-values-cur", default="")
    parser.add_argument("--dataset", default="cicids2017")
    parser.add_argument("--outdir", default="results/raw/paper2_streaming_delay_001")

    parser.add_argument("--dims", default="8")
    parser.add_argument("--window-size", type=int, default=256)
    parser.add_argument("--stride", type=int, default=0)
    parser.add_argument("--pre-windows", type=int, default=3)
    parser.add_argument("--post-windows", type=int, default=5)
    parser.add_argument("--seeds", default="1,2,3")

    parser.add_argument("--max-rows", type=int, default=200000)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-permutations", type=int, default=200)

    parser.add_argument("--detectors", default="mmd_rbf,qk_mmd")
    parser.add_argument("--q-feature-maps", default="zz,pauli_xz")
    parser.add_argument("--q-reps", type=int, default=1)
    parser.add_argument("--q-input-scaling", choices=["none", "atan_standard"], default="atan_standard")

    args = parser.parse_args()

    stride = args.stride if args.stride > 0 else args.window_size

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    dims = parse_csv_list(args.dims, int)
    seeds = parse_csv_list(args.seeds, int)
    detectors = parse_csv_list(args.detectors, str)
    q_feature_maps = parse_csv_list(args.q_feature_maps, str)

    label_values_ref = parse_label_values(args.label_values_ref)
    label_values_cur = parse_label_values(args.label_values_cur)

    print(f"[LOAD] reference: {args.data_ref}")
    df_ref = load_numeric_csv(Path(args.data_ref), args.label_col, label_values_ref, args.max_rows)

    print(f"[LOAD] current:   {args.data_cur}")
    df_cur = load_numeric_csv(Path(args.data_cur), args.label_col, label_values_cur, args.max_rows)

    df_ref, df_cur = align_columns(df_ref, df_cur)

    X_ref_pool = df_ref.to_numpy(dtype=np.float64)
    X_cur_pool = df_cur.to_numpy(dtype=np.float64)

    print(f"[DATA] ref={X_ref_pool.shape} cur={X_cur_pool.shape} common_features={df_ref.shape[1]}")
    print(f"[STREAM] pre_windows={args.pre_windows} post_windows={args.post_windows} window_size={args.window_size} stride={stride}")

    window_rows = []

    for seed in seeds:
        rng = np.random.default_rng(seed)

        for dim in dims:
            X_ref_base_raw = sample_contiguous_window(X_ref_pool, args.window_size, rng)

            pre_raw, pre_start = sample_contiguous_stream(
                X_ref_pool,
                args.pre_windows,
                args.window_size,
                stride,
                rng,
            )

            post_raw, post_start = sample_contiguous_stream(
                X_cur_pool,
                args.post_windows,
                args.window_size,
                stride,
                rng,
            )

            scaler, svd, X_ref_base = fit_reference_reducer(
                X_ref_base_raw,
                dim=dim,
                seed=seed,
            )

            stream = []

            for i, Xw in enumerate(pre_raw):
                stream.append({
                    "phase": "pre",
                    "time_index": i,
                    "post_index": -1,
                    "true_drift": False,
                    "source_start": pre_start + i * stride,
                    "X": transform_window(Xw, scaler, svd),
                })

            for j, Xw in enumerate(post_raw):
                stream.append({
                    "phase": "post",
                    "time_index": args.pre_windows + j,
                    "post_index": j,
                    "true_drift": True,
                    "source_start": post_start + j * stride,
                    "X": transform_window(Xw, scaler, svd),
                })

            detector_configs = []

            if "mmd_rbf" in detectors:
                detector_configs.append(("mmd_rbf", "", ""))

            if "qk_mmd" in detectors:
                for fmap in q_feature_maps:
                    detector_configs.append(("qk_mmd", fmap, args.q_input_scaling))

            for cfg_idx, (det_name, fmap, scaling) in enumerate(detector_configs):
                random_state = seed * 100000 + dim * 1000 + cfg_idx

                detector = make_detector(
                    detector_name=det_name,
                    q_feature_map=fmap,
                    q_reps=args.q_reps,
                    q_input_scaling=scaling,
                    alpha=args.alpha,
                    n_permutations=args.n_permutations,
                    random_state=random_state,
                )

                detector.fit(X_ref_base)

                for item in stream:
                    pred = detector.predict(item["X"])

                    row = {
                        "dataset": args.dataset,
                        "protocol": "paper2_streaming_delay",
                        "seed": seed,
                        "detector": det_name,
                        "q_feature_map": fmap,
                        "q_reps": args.q_reps if det_name == "qk_mmd" else 0,
                        "q_input_scaling": scaling,
                        "dim": X_ref_base.shape[1],
                        "window_size": args.window_size,
                        "stride": stride,
                        "alpha": args.alpha,
                        "n_permutations": args.n_permutations,
                        "pre_windows": args.pre_windows,
                        "post_windows": args.post_windows,
                        "phase": item["phase"],
                        "time_index": item["time_index"],
                        "post_index": item["post_index"],
                        "source_start": item["source_start"],
                        "true_drift": item["true_drift"],
                        "score": float(pred.score),
                        "threshold": float(pred.threshold),
                        "margin": float(pred.score - pred.threshold),
                        "p_value": float(pred.p_value),
                        "drift_detected": bool(pred.drift_detected),
                        "runtime_sec": float(pred.runtime_sec),
                        "null_scores_mean": float(pred.null_scores_mean),
                        "null_scores_std": float(pred.null_scores_std),
                    }

                    window_rows.append(row)

                    print({
                        "seed": seed,
                        "dim": row["dim"],
                        "detector": det_name,
                        "q_feature_map": fmap,
                        "phase": item["phase"],
                        "t": item["time_index"],
                        "score": round(row["score"], 6),
                        "threshold": round(row["threshold"], 6),
                        "p_value": round(row["p_value"], 4),
                        "detected": row["drift_detected"],
                    })

    win_df = pd.DataFrame(window_rows)

    window_out = outdir / "paper2_streaming_window_results.csv"
    win_df.to_csv(window_out, index=False)

    group_cols = [
        "dataset", "protocol", "seed", "detector", "q_feature_map",
        "q_input_scaling", "dim", "window_size", "stride", "alpha",
        "n_permutations", "pre_windows", "post_windows",
    ]

    seq_rows = []

    for keys, g in win_df.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, keys))

        pre = g[g["phase"] == "pre"]
        post = g[g["phase"] == "post"]

        post_detected = post[post["drift_detected"] == True]

        detected_after_change = len(post_detected) > 0

        if detected_after_change:
            first_post_index = int(post_detected["post_index"].iloc[0])
            first_alarm_time_index = int(post_detected["time_index"].iloc[0])
            detection_delay_windows = first_post_index
            detection_delay_rows = first_post_index * int(base["stride"])
        else:
            first_post_index = np.nan
            first_alarm_time_index = np.nan
            detection_delay_windows = np.nan
            detection_delay_rows = np.nan

        base.update({
            "false_alarm_before_change_any": bool(pre["drift_detected"].any()),
            "false_alarm_rate_pre": float(pre["drift_detected"].mean()) if len(pre) else np.nan,
            "detected_after_change_any": bool(detected_after_change),
            "detection_rate_post": float(post["drift_detected"].mean()) if len(post) else np.nan,
            "first_post_detection_index": first_post_index,
            "first_alarm_time_index": first_alarm_time_index,
            "detection_delay_windows": detection_delay_windows,
            "detection_delay_rows": detection_delay_rows,
            "pre_score_mean": float(pre["score"].mean()) if len(pre) else np.nan,
            "post_score_mean": float(post["score"].mean()) if len(post) else np.nan,
            "pre_margin_mean": float(pre["margin"].mean()) if len(pre) else np.nan,
            "post_margin_mean": float(post["margin"].mean()) if len(post) else np.nan,
            "runtime_sec_sum": float(g["runtime_sec"].sum()),
            "runtime_sec_mean": float(g["runtime_sec"].mean()),
        })

        seq_rows.append(base)

    seq_df = pd.DataFrame(seq_rows)

    sequence_out = outdir / "paper2_streaming_sequence_results.csv"
    seq_df.to_csv(sequence_out, index=False)

    summary_cols = [
        "detector", "q_feature_map", "dim", "window_size", "stride",
        "false_alarm_before_change_any", "false_alarm_rate_pre",
        "detected_after_change_any", "detection_rate_post",
        "detection_delay_windows", "runtime_sec_sum",
    ]

    print("\n=== STREAMING SEQUENCE SUMMARY ===")
    print(seq_df[summary_cols].to_string(index=False))

    print(f"\nSaved window results:   {window_out}")
    print(f"Saved sequence results: {sequence_out}")


if __name__ == "__main__":
    main()
