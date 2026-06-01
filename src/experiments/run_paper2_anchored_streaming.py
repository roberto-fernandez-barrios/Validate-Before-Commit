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


def reduce_pair_anchored(X_base: np.ndarray, X_cur: np.ndarray, dim: int, seed: int):
    scaler = StandardScaler()
    X_base_s = scaler.fit_transform(X_base)
    X_cur_s = scaler.transform(X_cur)

    max_dim = min(dim, X_base_s.shape[1] - 1)
    if max_dim < 1:
        raise ValueError("Not enough numeric features after preprocessing.")

    svd = TruncatedSVD(n_components=max_dim, random_state=seed)
    X_base_z = svd.fit_transform(X_base_s)
    X_cur_z = svd.transform(X_cur_s)

    return X_base_z.astype(np.float64), X_cur_z.astype(np.float64)


def pred_to_row(
    *,
    dataset,
    seed,
    dim,
    window_size,
    stride,
    alpha,
    n_permutations,
    detector_name,
    q_feature_map,
    q_reps,
    q_input_scaling,
    phase,
    monitor_index,
    score,
    runtime_sec,
):
    return {
        "dataset": dataset,
        "protocol": "paper2_anchored_streaming",
        "seed": seed,
        "detector": detector_name,
        "q_feature_map": q_feature_map,
        "q_reps": q_reps,
        "q_input_scaling": q_input_scaling,
        "dim": dim,
        "window_size": window_size,
        "stride": stride,
        "alpha": alpha,
        "n_permutations": n_permutations,
        "phase": phase,
        "monitor_index": monitor_index,
        "score": float(score),
        "runtime_sec": float(runtime_sec),
    }


def run_detector(detector_name, fmap, q_reps, q_input_scaling, alpha, n_permutations, seed, X_base, X_cur):
    if detector_name == "mmd_rbf":
        detector = MmdRbfDetector(
            alpha=alpha,
            n_permutations=n_permutations,
            random_state=seed,
        )
    elif detector_name == "qk_mmd":
        detector = QkMmdDetector(
            feature_map=fmap,
            reps=q_reps,
            alpha=alpha,
            n_permutations=n_permutations,
            random_state=seed,
            input_scaling=q_input_scaling,
        )
    else:
        raise ValueError(f"Unknown detector: {detector_name}")

    pred = detector.fit(X_base).predict(X_cur)
    return pred


def main():
    parser = argparse.ArgumentParser(description="Anchored baseline streaming drift benchmark for Paper 2.")

    parser.add_argument("--data-ref", required=True)
    parser.add_argument("--data-cur", required=True)
    parser.add_argument("--label-col", default="Label")
    parser.add_argument("--label-values-ref", default="")
    parser.add_argument("--label-values-cur", default="")
    parser.add_argument("--dataset", default="cicids2017")
    parser.add_argument("--outdir", default="results/raw/cicids_anchored_streaming_001")

    parser.add_argument("--dims", default="8")
    parser.add_argument("--window-size", type=int, default=256)
    parser.add_argument("--stride", type=int, default=256)
    parser.add_argument("--calibration-windows", type=int, default=10)
    parser.add_argument("--pre-eval-windows", type=int, default=10)
    parser.add_argument("--post-windows", type=int, default=10)
    parser.add_argument("--seeds", default="1,2,3")
    parser.add_argument("--max-rows", type=int, default=200000)

    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-permutations", type=int, default=100)
    parser.add_argument("--detectors", default="mmd_rbf,qk_mmd")
    parser.add_argument("--q-feature-maps", default="z,zz,pauli_xz")
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

    rows = []

    total_ref_windows = 1 + args.calibration_windows + args.pre_eval_windows

    for seed in seeds:
        rng = np.random.default_rng(seed)

        max_ref_start = max(0, len(X_ref_pool) - total_ref_windows * args.stride - args.window_size)
        max_cur_start = max(0, len(X_cur_pool) - args.post_windows * args.stride - args.window_size)

        ref_start = int(rng.integers(0, max_ref_start + 1)) if max_ref_start > 0 else 0
        cur_start = int(rng.integers(0, max_cur_start + 1)) if max_cur_start > 0 else 0

        ref_windows = make_windows(X_ref_pool, args.window_size, args.stride, total_ref_windows, ref_start)
        post_windows = make_windows(X_cur_pool, args.window_size, args.stride, args.post_windows, cur_start)

        X_base_raw = ref_windows[0]
        cal_windows = ref_windows[1:1 + args.calibration_windows]
        pre_eval_windows = ref_windows[1 + args.calibration_windows:]

        monitored = (
            [("calibration", i, w) for i, w in enumerate(cal_windows)] +
            [("pre_eval", i, w) for i, w in enumerate(pre_eval_windows)] +
            [("post", i, w) for i, w in enumerate(post_windows)]
        )

        for dim in dims:
            for detector_name in detectors:
                fmap_list = q_feature_maps if detector_name == "qk_mmd" else [""]

                for fmap in fmap_list:
                    for phase, monitor_index, X_cur_raw in monitored:
                        X_base, X_cur = reduce_pair_anchored(
                            X_base_raw,
                            X_cur_raw,
                            dim=dim,
                            seed=seed + monitor_index,
                        )

                        pred = run_detector(
                            detector_name=detector_name,
                            fmap=fmap,
                            q_reps=args.q_reps,
                            q_input_scaling=args.q_input_scaling,
                            alpha=args.alpha,
                            n_permutations=args.n_permutations,
                            seed=seed + monitor_index,
                            X_base=X_base,
                            X_cur=X_cur,
                        )

                        row = pred_to_row(
                            dataset=args.dataset,
                            seed=seed,
                            dim=X_base.shape[1],
                            window_size=args.window_size,
                            stride=args.stride,
                            alpha=args.alpha,
                            n_permutations=args.n_permutations,
                            detector_name=detector_name,
                            q_feature_map=fmap,
                            q_reps=args.q_reps if detector_name == "qk_mmd" else 0,
                            q_input_scaling=args.q_input_scaling if detector_name == "qk_mmd" else "",
                            phase=phase,
                            monitor_index=monitor_index,
                            score=pred.score,
                            runtime_sec=pred.runtime_sec,
                        )
                        rows.append(row)

                        print({
                            "seed": seed,
                            "detector": detector_name,
                            "q_feature_map": fmap,
                            "phase": phase,
                            "monitor_index": monitor_index,
                            "score": round(float(pred.score), 6),
                        })

    win = pd.DataFrame(rows)
    win_out = outdir / "paper2_anchored_streaming_window_results.csv"
    win.to_csv(win_out, index=False)

    print(f"\nSaved window results: {win_out}")


if __name__ == "__main__":
    main()
