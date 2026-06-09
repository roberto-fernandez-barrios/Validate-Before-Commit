from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler

from src.drift_detection.mmd_rbf_detector import MmdRbfDetector
from src.drift_detection.qk_mmd_detector import QkMmdDetector


def parse_csv_list(value: str, cast=str):
    return [cast(x.strip()) for x in value.split(",") if x.strip()]


def load_numeric_csv(
    path: Path,
    label_col: str | None,
    label_values: list[str] | None,
    max_rows: int | None,
) -> pd.DataFrame:
    df = pd.read_csv(path, nrows=max_rows)
    df.columns = [str(c).strip() for c in df.columns]

    if label_col and label_col in df.columns and label_values:
        before = len(df)
        allowed = {str(v).strip() for v in label_values}
        df = df[df[label_col].astype(str).str.strip().isin(allowed)].copy()
        print(f"[FILTER] {path.name}: {before} -> {len(df)} rows using {label_col} in {sorted(allowed)}")

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


def align_columns(a: pd.DataFrame, b: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    common = sorted(set(a.columns).intersection(set(b.columns)))
    if not common:
        raise ValueError("Reference and current datasets have no common numeric columns.")
    return a[common], b[common]


def sample_window(X: np.ndarray, size: int, rng: np.random.Generator) -> np.ndarray:
    if len(X) < size:
        raise ValueError(f"Not enough rows: requested {size}, available {len(X)}")
    idx = rng.choice(len(X), size=size, replace=False)
    return X[idx]


def sample_controlled_window(
    X_ref: np.ndarray,
    X_cur: np.ndarray,
    size: int,
    severity: float,
    rng: np.random.Generator,
) -> np.ndarray:
    n_cur = int(round(size * severity))
    n_ref = size - n_cur

    parts = []
    if n_ref > 0:
        parts.append(sample_window(X_ref, n_ref, rng))
    if n_cur > 0:
        parts.append(sample_window(X_cur, n_cur, rng))

    X = np.vstack(parts)
    rng.shuffle(X)
    return X


def build_preprocessor(
    X_fit: np.ndarray,
    dim: int,
    seed: int,
) -> tuple[StandardScaler, TruncatedSVD]:
    scaler = StandardScaler()
    X_fit_s = scaler.fit_transform(X_fit)

    n_components = min(dim, X_fit_s.shape[1] - 1)
    if n_components < 1:
        raise ValueError("Not enough features after preprocessing.")

    svd = TruncatedSVD(n_components=n_components, random_state=seed)
    svd.fit(X_fit_s)

    return scaler, svd


def transform(
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
    seed: int,
):
    if detector_name == "mmd_rbf":
        return MmdRbfDetector(
            alpha=alpha,
            n_permutations=n_permutations,
            random_state=seed,
        )

    if detector_name == "qk_mmd":
        return QkMmdDetector(
            feature_map=q_feature_map,
            reps=q_reps,
            alpha=alpha,
            n_permutations=n_permutations,
            random_state=seed,
            input_scaling=q_input_scaling,
        )

    raise ValueError(f"Unknown detector: {detector_name}")


def score_window(
    X_ref_z: np.ndarray,
    X_win_z: np.ndarray,
    detector_name: str,
    q_feature_map: str,
    q_reps: int,
    q_input_scaling: str,
    alpha: float,
    n_permutations: int,
    seed: int,
) -> float:
    detector = make_detector(
        detector_name=detector_name,
        q_feature_map=q_feature_map,
        q_reps=q_reps,
        q_input_scaling=q_input_scaling,
        alpha=alpha,
        n_permutations=n_permutations,
        seed=seed,
    )
    pred = detector.fit(X_ref_z).predict(X_win_z)
    return float(pred.score)


def first_consecutive_trigger(scores: list[float], threshold: float, k: int) -> int | None:
    run = 0
    for i, score in enumerate(scores):
        if score > threshold:
            run += 1
            if run >= k:
                return i - k + 1
        else:
            run = 0
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paper 2 adaptive monitor experiment after controlled streaming drift detection."
    )

    parser.add_argument("--data-ref", required=True)
    parser.add_argument("--data-cur", required=True)
    parser.add_argument("--label-col", default="Label")
    parser.add_argument("--label-values-ref", default="")
    parser.add_argument("--label-values-cur", default="")
    parser.add_argument("--dataset", default="cicids2017_tue_wed_benign_adaptive")
    parser.add_argument("--outdir", default="results/raw/paper2_adaptive_monitor_001")

    parser.add_argument("--dims", default="8")
    parser.add_argument("--window-size", type=int, default=256)
    parser.add_argument("--seeds", default="1,2,3")
    parser.add_argument("--max-rows", type=int, default=200000)

    parser.add_argument("--calibration-windows", type=int, default=20)
    parser.add_argument("--pre-windows", type=int, default=20)
    parser.add_argument("--post-windows", type=int, default=20)
    parser.add_argument("--adapt-calibration-windows", type=int, default=20)
    parser.add_argument("--adapt-eval-windows", type=int, default=20)

    parser.add_argument("--severities", default="0.1,0.25,0.5,0.75,1.0")
    parser.add_argument("--threshold-quantile", type=float, default=0.95)
    parser.add_argument("--consecutive-k", type=int, default=2)

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
    severities = parse_csv_list(args.severities, float)
    detectors = parse_csv_list(args.detectors, str)
    q_feature_maps = parse_csv_list(args.q_feature_maps, str)

    label_values_ref = parse_csv_list(args.label_values_ref, str) if args.label_values_ref else None
    label_values_cur = parse_csv_list(args.label_values_cur, str) if args.label_values_cur else None

    print(f"[LOAD] reference: {args.data_ref}")
    df_ref = load_numeric_csv(Path(args.data_ref), args.label_col, label_values_ref, args.max_rows)

    print(f"[LOAD] current:   {args.data_cur}")
    df_cur = load_numeric_csv(Path(args.data_cur), args.label_col, label_values_cur, args.max_rows)

    df_ref, df_cur = align_columns(df_ref, df_cur)

    X_ref_pool = df_ref.to_numpy(dtype=np.float64)
    X_cur_pool = df_cur.to_numpy(dtype=np.float64)

    print(f"[DATA] ref={X_ref_pool.shape} cur={X_cur_pool.shape} common_features={df_ref.shape[1]}")

    sequence_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for seed in seeds:
        rng = np.random.default_rng(seed)

        for dim in dims:
            for severity in severities:
                print(f"\n[SEED={seed}][DIM={dim}][SEVERITY={severity}]")

                anchor_ref_raw = sample_window(X_ref_pool, args.window_size, rng)

                calibration_raw = [
                    sample_window(X_ref_pool, args.window_size, rng)
                    for _ in range(args.calibration_windows)
                ]

                pre_raw = [
                    sample_window(X_ref_pool, args.window_size, rng)
                    for _ in range(args.pre_windows)
                ]

                post_raw = [
                    sample_controlled_window(
                        X_ref_pool,
                        X_cur_pool,
                        args.window_size,
                        severity,
                        rng,
                    )
                    for _ in range(args.post_windows)
                ]

                adapt_ref_raw = sample_controlled_window(
                    X_ref_pool,
                    X_cur_pool,
                    args.window_size,
                    severity,
                    rng,
                )

                adapt_calibration_raw = [
                    sample_controlled_window(
                        X_ref_pool,
                        X_cur_pool,
                        args.window_size,
                        severity,
                        rng,
                    )
                    for _ in range(args.adapt_calibration_windows)
                ]

                adapt_eval_raw = [
                    sample_controlled_window(
                        X_ref_pool,
                        X_cur_pool,
                        args.window_size,
                        severity,
                        rng,
                    )
                    for _ in range(args.adapt_eval_windows)
                ]

                scaler, svd = build_preprocessor(anchor_ref_raw, dim=dim, seed=seed)

                anchor_ref_z = transform(anchor_ref_raw, scaler, svd)
                calibration_z = [transform(x, scaler, svd) for x in calibration_raw]
                pre_z = [transform(x, scaler, svd) for x in pre_raw]
                post_z = [transform(x, scaler, svd) for x in post_raw]

                adapt_ref_z = transform(adapt_ref_raw, scaler, svd)
                adapt_calibration_z = [transform(x, scaler, svd) for x in adapt_calibration_raw]
                adapt_eval_z = [transform(x, scaler, svd) for x in adapt_eval_raw]

                detector_configs: list[tuple[str, str]] = []

                if "mmd_rbf" in detectors:
                    detector_configs.append(("mmd_rbf", ""))

                if "qk_mmd" in detectors:
                    for qmap in q_feature_maps:
                        detector_configs.append(("qk_mmd", qmap))

                for detector_name, qmap in detector_configs:
                    print(f"[RUN] detector={detector_name} qmap={qmap or '-'}")

                    cal_scores = [
                        score_window(
                            anchor_ref_z,
                            x,
                            detector_name,
                            qmap,
                            args.q_reps,
                            args.q_input_scaling,
                            args.alpha,
                            args.n_permutations,
                            seed,
                        )
                        for x in calibration_z
                    ]

                    threshold = float(np.quantile(cal_scores, args.threshold_quantile))

                    pre_scores = [
                        score_window(
                            anchor_ref_z,
                            x,
                            detector_name,
                            qmap,
                            args.q_reps,
                            args.q_input_scaling,
                            args.alpha,
                            args.n_permutations,
                            seed,
                        )
                        for x in pre_z
                    ]

                    post_scores = [
                        score_window(
                            anchor_ref_z,
                            x,
                            detector_name,
                            qmap,
                            args.q_reps,
                            args.q_input_scaling,
                            args.alpha,
                            args.n_permutations,
                            seed,
                        )
                        for x in post_z
                    ]

                    pre_trigger_idx = first_consecutive_trigger(
                        pre_scores,
                        threshold,
                        args.consecutive_k,
                    )

                    post_trigger_idx = first_consecutive_trigger(
                        post_scores,
                        threshold,
                        args.consecutive_k,
                    )

                    false_alarm_any = pre_trigger_idx is not None
                    post_detect_any = post_trigger_idx is not None

                    adapt_cal_scores = [
                        score_window(
                            adapt_ref_z,
                            x,
                            detector_name,
                            qmap,
                            args.q_reps,
                            args.q_input_scaling,
                            args.alpha,
                            args.n_permutations,
                            seed,
                        )
                        for x in adapt_calibration_z
                    ]

                    adapt_threshold = float(np.quantile(adapt_cal_scores, args.threshold_quantile))

                    adapt_eval_scores = [
                        score_window(
                            adapt_ref_z,
                            x,
                            detector_name,
                            qmap,
                            args.q_reps,
                            args.q_input_scaling,
                            args.alpha,
                            args.n_permutations,
                            seed,
                        )
                        for x in adapt_eval_z
                    ]

                    adapt_trigger_idx = first_consecutive_trigger(
                        adapt_eval_scores,
                        adapt_threshold,
                        args.consecutive_k,
                    )

                    post_adapt_alarm_any = adapt_trigger_idx is not None

                    pre_alarm_rate = float(np.mean([s > threshold for s in pre_scores]))
                    post_alarm_rate = float(np.mean([s > threshold for s in post_scores]))
                    post_adapt_alarm_rate = float(np.mean([s > adapt_threshold for s in adapt_eval_scores]))

                    post_score_mean = float(np.mean(post_scores))
                    post_adapt_score_mean = float(np.mean(adapt_eval_scores))
                    score_reduction = post_score_mean - post_adapt_score_mean

                    adaptation_success = bool(post_detect_any and not post_adapt_alarm_any)
                    clean_adaptation_success = bool(
                        (not false_alarm_any)
                        and post_detect_any
                        and (not post_adapt_alarm_any)
                    )

                    summary_rows.append(
                        {
                            "dataset": args.dataset,
                            "protocol": "paper2_adaptive_monitor",
                            "seed": seed,
                            "dim": dim,
                            "severity": severity,
                            "detector": detector_name,
                            "q_feature_map": qmap,
                            "q_reps": args.q_reps if detector_name == "qk_mmd" else 0,
                            "q_input_scaling": args.q_input_scaling if detector_name == "qk_mmd" else "",
                            "window_size": args.window_size,
                            "threshold_quantile": args.threshold_quantile,
                            "consecutive_k": args.consecutive_k,
                            "n_permutations": args.n_permutations,
                            "threshold": threshold,
                            "adapt_threshold": adapt_threshold,
                            "false_alarm_any": false_alarm_any,
                            "post_detect_any": post_detect_any,
                            "post_adapt_alarm_any": post_adapt_alarm_any,
                            "adaptation_success": adaptation_success,
                            "clean_adaptation_success": clean_adaptation_success,
                            "delay_windows": np.nan if post_trigger_idx is None else post_trigger_idx,
                            "pre_alarm_rate": pre_alarm_rate,
                            "post_alarm_rate": post_alarm_rate,
                            "post_adapt_alarm_rate": post_adapt_alarm_rate,
                            "cal_score_mean": float(np.mean(cal_scores)),
                            "pre_score_mean": float(np.mean(pre_scores)),
                            "post_score_mean": post_score_mean,
                            "adapt_cal_score_mean": float(np.mean(adapt_cal_scores)),
                            "post_adapt_score_mean": post_adapt_score_mean,
                            "score_reduction_after_adaptation": score_reduction,
                        }
                    )

                    for phase, scores, thr in [
                        ("pre", pre_scores, threshold),
                        ("post", post_scores, threshold),
                        ("post_adapt", adapt_eval_scores, adapt_threshold),
                    ]:
                        for window_index, score in enumerate(scores):
                            sequence_rows.append(
                                {
                                    "dataset": args.dataset,
                                    "protocol": "paper2_adaptive_monitor",
                                    "seed": seed,
                                    "dim": dim,
                                    "severity": severity,
                                    "detector": detector_name,
                                    "q_feature_map": qmap,
                                    "phase": phase,
                                    "window_index": window_index,
                                    "score": score,
                                    "threshold": thr,
                                    "alarm": bool(score > thr),
                                }
                            )

    sequence_df = pd.DataFrame(sequence_rows)
    summary_df = pd.DataFrame(summary_rows)

    agg_df = (
        summary_df
        .groupby(
            [
                "dataset",
                "protocol",
                "severity",
                "detector",
                "q_feature_map",
                "q_reps",
                "q_input_scaling",
                "dim",
                "window_size",
                "threshold_quantile",
                "consecutive_k",
                "n_permutations",
            ],
            dropna=False,
        )
        .agg(
            n_seeds=("seed", "nunique"),
            false_alarm_any_rate=("false_alarm_any", "mean"),
            post_detect_any_rate=("post_detect_any", "mean"),
            post_adapt_alarm_any_rate=("post_adapt_alarm_any", "mean"),
            adaptation_success_rate=("adaptation_success", "mean"),
            clean_adaptation_success_rate=("clean_adaptation_success", "mean"),
            delay_windows_mean=("delay_windows", "mean"),
            pre_alarm_rate_mean=("pre_alarm_rate", "mean"),
            post_alarm_rate_mean=("post_alarm_rate", "mean"),
            post_adapt_alarm_rate_mean=("post_adapt_alarm_rate", "mean"),
            pre_score_mean=("pre_score_mean", "mean"),
            post_score_mean=("post_score_mean", "mean"),
            post_adapt_score_mean=("post_adapt_score_mean", "mean"),
            score_reduction_after_adaptation_mean=("score_reduction_after_adaptation", "mean"),
        )
        .reset_index()
        .sort_values(["severity", "detector", "q_feature_map"], na_position="first")
    )

    sequence_out = outdir / "paper2_adaptive_monitor_window_results.csv"
    summary_out = outdir / "paper2_adaptive_monitor_by_seed.csv"
    agg_out = outdir / "paper2_adaptive_monitor_summary.csv"

    sequence_df.to_csv(sequence_out, index=False)
    summary_df.to_csv(summary_out, index=False)
    agg_df.to_csv(agg_out, index=False)

    print(f"\nSaved: {sequence_out}")
    print(f"Saved: {summary_out}")
    print(f"Saved: {agg_out}")

    print("\n=== ADAPTIVE MONITOR SUMMARY ===")
    print(
        agg_df[
            [
                "severity",
                "detector",
                "q_feature_map",
                "n_seeds",
                "false_alarm_any_rate",
                "post_detect_any_rate",
                "post_adapt_alarm_any_rate",
                "adaptation_success_rate",
                "clean_adaptation_success_rate",
                "delay_windows_mean",
                "post_alarm_rate_mean",
                "post_adapt_alarm_rate_mean",
                "score_reduction_after_adaptation_mean",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
