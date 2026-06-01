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


def load_numeric_csv(path: Path, label_col: str | None, label_values: str | None, max_rows: int | None) -> pd.DataFrame:
    df = pd.read_csv(path, nrows=max_rows)
    df.columns = [str(c).strip() for c in df.columns]

    if label_col and label_col in df.columns and label_values:
        allowed = set(parse_csv_list(label_values, str))
        df[label_col] = df[label_col].astype(str).str.strip()
        df = df[df[label_col].isin(allowed)].copy()

    if label_col and label_col in df.columns:
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


def align_columns(a: pd.DataFrame, b: pd.DataFrame):
    common = sorted(set(a.columns).intersection(set(b.columns)))
    if not common:
        raise ValueError("Reference and current datasets have no common numeric columns.")
    return a[common], b[common]


def make_windows(X: np.ndarray, window_size: int, stride: int, n_windows: int, start: int = 0):
    windows = []
    for i in range(n_windows):
        s = start + i * stride
        e = s + window_size
        if e > len(X):
            break
        windows.append(X[s:e])
    return windows


def reduce_pair(X_ref: np.ndarray, X_cur: np.ndarray, dim: int, seed: int):
    scaler = StandardScaler()
    X_ref_s = scaler.fit_transform(X_ref)
    X_cur_s = scaler.transform(X_cur)

    max_dim = min(dim, X_ref_s.shape[1] - 1)
    if max_dim < 1:
        raise ValueError("Not enough numeric features after preprocessing.")

    svd = TruncatedSVD(n_components=max_dim, random_state=seed)
    X_ref_z = svd.fit_transform(X_ref_s)
    X_cur_z = svd.transform(X_cur_s)

    return X_ref_z.astype(np.float64), X_cur_z.astype(np.float64)


def pred_to_row(
    *,
    dataset,
    seed,
    dim,
    window_size,
    stride,
    alpha,
    n_permutations,
    transition_type,
    transition_index,
    phase,
    pred,
):
    return {
        "dataset": dataset,
        "protocol": "paper2_rolling_streaming_delay",
        "seed": seed,
        "detector": pred.detector,
        "q_feature_map": getattr(pred, "q_feature_map", ""),
        "q_reps": getattr(pred, "q_reps", 0),
        "q_input_scaling": getattr(pred, "q_input_scaling", ""),
        "dim": dim,
        "window_size": window_size,
        "stride": stride,
        "alpha": alpha,
        "n_permutations": n_permutations,
        "transition_type": transition_type,
        "transition_index": transition_index,
        "phase": phase,
        "score": float(pred.score),
        "threshold": float(pred.threshold),
        "p_value": float(pred.p_value),
        "drift_detected": bool(pred.drift_detected),
        "detected": bool(pred.drift_detected),
        "runtime_sec": float(pred.runtime_sec),
        "null_scores_mean": float(pred.null_scores_mean),
        "null_scores_std": float(pred.null_scores_std),
    }


def main():
    parser = argparse.ArgumentParser(description="Rolling/local-reference streaming drift benchmark for Paper 2.")

    parser.add_argument("--data-ref", required=True)
    parser.add_argument("--data-cur", required=True)
    parser.add_argument("--label-col", default="Label")
    parser.add_argument("--label-values-ref", default="")
    parser.add_argument("--label-values-cur", default="")
    parser.add_argument("--dataset", default="cicids2017")
    parser.add_argument("--outdir", default="results/raw/cicids_rolling_streaming_001")

    parser.add_argument("--dims", default="8")
    parser.add_argument("--window-size", type=int, default=256)
    parser.add_argument("--stride", type=int, default=256)
    parser.add_argument("--pre-windows", type=int, default=20)
    parser.add_argument("--post-windows", type=int, default=10)
    parser.add_argument("--seeds", default="1,2,3")
    parser.add_argument("--max-rows", type=int, default=200000)

    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-permutations", type=int, default=100)
    parser.add_argument("--detectors", default="mmd_rbf,qk_mmd")
    parser.add_argument("--q-feature-maps", default="zz,pauli_xz")
    parser.add_argument("--q-reps", type=int, default=1)
    parser.add_argument("--q-input-scaling", choices=["none", "atan_standard"], default="atan_standard")

    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    dims = parse_csv_list(args.dims, int)
    seeds = parse_csv_list(args.seeds, int)
    detectors = parse_csv_list(args.detectors, str)
    q_feature_maps = parse_csv_list(args.q_feature_maps, str)

    print(f"[LOAD] reference: {args.data_ref}")
    df_ref = load_numeric_csv(Path(args.data_ref), args.label_col, args.label_values_ref, args.max_rows)

    print(f"[LOAD] current:   {args.data_cur}")
    df_cur = load_numeric_csv(Path(args.data_cur), args.label_col, args.label_values_cur, args.max_rows)

    df_ref, df_cur = align_columns(df_ref, df_cur)

    X_ref_pool = df_ref.to_numpy(dtype=np.float64)
    X_cur_pool = df_cur.to_numpy(dtype=np.float64)

    print(f"[DATA] ref={X_ref_pool.shape} cur={X_cur_pool.shape} common_features={df_ref.shape[1]}")
    print(f"[ROLLING] pre_windows={args.pre_windows} post_windows={args.post_windows} window_size={args.window_size} stride={args.stride}")

    rows = []

    for seed in seeds:
        rng = np.random.default_rng(seed)

        max_pre_start = max(0, len(X_ref_pool) - args.pre_windows * args.stride - args.window_size)
        max_post_start = max(0, len(X_cur_pool) - args.post_windows * args.stride - args.window_size)

        pre_start = int(rng.integers(0, max_pre_start + 1)) if max_pre_start > 0 else 0
        post_start = int(rng.integers(0, max_post_start + 1)) if max_post_start > 0 else 0

        pre_windows = make_windows(X_ref_pool, args.window_size, args.stride, args.pre_windows, pre_start)
        post_windows = make_windows(X_cur_pool, args.window_size, args.stride, args.post_windows, post_start)

        stream_windows = pre_windows + post_windows

        for dim in dims:
            for i in range(1, len(stream_windows)):
                X_prev_raw = stream_windows[i - 1]
                X_cur_raw = stream_windows[i]

                phase = "pre" if i < len(pre_windows) else "post"
                transition_type = "pre_to_pre" if phase == "pre" else ("pre_to_post" if i == len(pre_windows) else "post_to_post")

                X_prev, X_cur = reduce_pair(X_prev_raw, X_cur_raw, dim=dim, seed=seed + i)

                if "mmd_rbf" in detectors:
                    detector = MmdRbfDetector(
                        alpha=args.alpha,
                        n_permutations=args.n_permutations,
                        random_state=seed + i,
                    )
                    pred = detector.fit(X_prev).predict(X_cur)
                    row = pred_to_row(
                        dataset=args.dataset,
                        seed=seed,
                        dim=X_prev.shape[1],
                        window_size=args.window_size,
                        stride=args.stride,
                        alpha=args.alpha,
                        n_permutations=args.n_permutations,
                        transition_type=transition_type,
                        transition_index=i,
                        phase=phase,
                        pred=pred,
                    )
                    rows.append(row)
                    print({k: row[k] for k in ["seed", "detector", "phase", "transition_type", "transition_index", "score", "threshold", "p_value", "detected"]})

                if "qk_mmd" in detectors:
                    for fmap in q_feature_maps:
                        detector = QkMmdDetector(
                            feature_map=fmap,
                            reps=args.q_reps,
                            alpha=args.alpha,
                            n_permutations=args.n_permutations,
                            random_state=seed + i,
                            input_scaling=args.q_input_scaling,
                        )
                        pred = detector.fit(X_prev).predict(X_cur)
                        row = pred_to_row(
                            dataset=args.dataset,
                            seed=seed,
                            dim=X_prev.shape[1],
                            window_size=args.window_size,
                            stride=args.stride,
                            alpha=args.alpha,
                            n_permutations=args.n_permutations,
                            transition_type=transition_type,
                            transition_index=i,
                            phase=phase,
                            pred=pred,
                        )
                        rows.append(row)
                        print({k: row[k] for k in ["seed", "detector", "q_feature_map", "phase", "transition_type", "transition_index", "score", "threshold", "p_value", "detected"]})

    win = pd.DataFrame(rows)
    win_out = outdir / "paper2_rolling_streaming_window_results.csv"
    win.to_csv(win_out, index=False)

    print(f"\nSaved window results: {win_out}")


if __name__ == "__main__":
    main()
