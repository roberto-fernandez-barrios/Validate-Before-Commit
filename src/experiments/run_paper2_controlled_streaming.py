from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from src.drift_detection.mmd_rbf_detector import MmdRbfDetector
from src.drift_detection.qk_mmd_detector import QkMmdDetector


def parse_csv_list(value: str, cast=str):
    return [cast(x.strip()) for x in value.split(",") if x.strip()]


def parse_label_values(value: str | None) -> set[str] | None:
    if value is None or value.strip() == "":
        return None
    return {x.strip() for x in value.split(",") if x.strip()}


def load_numeric_csv(
    path: Path,
    label_col: str | None,
    label_values: set[str] | None,
    max_rows: int | None,
) -> pd.DataFrame:
    df = pd.read_csv(path, nrows=max_rows, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]

    if label_col:
        label_col = label_col.strip()

        if label_values is not None and label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found in {path}")

        if label_col in df.columns:
            if label_values is not None:
                before = len(df)
                labels = df[label_col].astype(str).str.strip()
                df = df[labels.isin(label_values)].copy()
                after = len(df)
                print(f"[FILTER] {path.name}: {before} -> {after} rows using {label_col} in {sorted(label_values)}")

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


def sample_mixed_window(
    X_ref: np.ndarray,
    X_cur: np.ndarray,
    size: int,
    severity: float,
    rng: np.random.Generator,
) -> np.ndarray:
    if severity < 0.0 or severity > 1.0:
        raise ValueError(f"severity must be in [0, 1], got {severity}")

    n_cur = int(round(size * severity))
    n_ref = size - n_cur

    parts = []
    if n_ref > 0:
        parts.append(sample_window(X_ref, n_ref, rng))
    if n_cur > 0:
        parts.append(sample_window(X_cur, n_cur, rng))

    X = np.vstack(parts)
    return X[rng.permutation(len(X))]


def fit_preprocessor(
    X_anchor_raw: np.ndarray,
    dim: int,
    seed: int,
) -> tuple[StandardScaler, TruncatedSVD]:
    scaler = StandardScaler()
    X_anchor_scaled = scaler.fit_transform(X_anchor_raw)

    max_dim = min(dim, X_anchor_scaled.shape[1] - 1, X_anchor_scaled.shape[0] - 1)
    if max_dim < 1:
        raise ValueError("Not enough data/features after preprocessing.")

    svd = TruncatedSVD(n_components=max_dim, random_state=seed)
    svd.fit(X_anchor_scaled)

    return scaler, svd


def transform_window(
    scaler: StandardScaler,
    svd: TruncatedSVD,
    X_raw: np.ndarray,
) -> np.ndarray:
    return svd.transform(scaler.transform(X_raw)).astype(np.float64)


def make_detector_configs(args: argparse.Namespace, seed: int) -> list[dict[str, Any]]:
    configs: list[dict[str, Any]] = []

    detectors = parse_csv_list(args.detectors, str)
    q_feature_maps = parse_csv_list(args.q_feature_maps, str)

    if "mmd_rbf" in detectors:
        configs.append(
            {
                "detector": "mmd_rbf",
                "q_feature_map": "",
                "q_reps": 0,
                "q_input_scaling": "",
                "model": MmdRbfDetector(
                    alpha=args.alpha,
                    n_permutations=args.n_permutations,
                    random_state=seed,
                ),
            }
        )

    if "qk_mmd" in detectors:
        for fmap in q_feature_maps:
            configs.append(
                {
                    "detector": "qk_mmd",
                    "q_feature_map": fmap,
                    "q_reps": args.q_reps,
                    "q_input_scaling": args.q_input_scaling,
                    "model": QkMmdDetector(
                        feature_map=fmap,
                        reps=args.q_reps,
                        alpha=args.alpha,
                        n_permutations=args.n_permutations,
                        random_state=seed,
                        input_scaling=args.q_input_scaling,
                    ),
                }
            )

    return configs


def score_window(
    *,
    model,
    row_base: dict[str, Any],
    phase: str,
    window_index: int,
    severity: float,
    true_drift: bool,
    X_window: np.ndarray,
) -> dict[str, Any]:
    pred = model.predict(X_window)

    row = dict(row_base)
    row.update(
        {
            "phase": phase,
            "window_index": window_index,
            "severity": severity,
            "true_drift": bool(true_drift),
            "score": float(pred.score),
            "permutation_threshold": float(pred.threshold),
            "p_value": float(pred.p_value),
            "drift_detected": bool(pred.drift_detected),
            "runtime_sec": float(pred.runtime_sec),
            "null_scores_mean": float(pred.null_scores_mean),
            "null_scores_std": float(pred.null_scores_std),
        }
    )

    return row


def first_consecutive_trigger(flags: np.ndarray, k: int) -> tuple[bool, float]:
    run = 0

    for i, flag in enumerate(flags):
        if flag:
            run += 1
            if run >= k:
                return True, float(i - k + 1)
        else:
            run = 0

    return False, np.nan


def build_policy_summary(
    window_df: pd.DataFrame,
    threshold_quantiles: list[float],
    consecutive_ks: list[int],
    outdir: Path,
) -> pd.DataFrame:
    policy_rows = []

    base_cols = [
        "dataset",
        "protocol",
        "seed",
        "detector",
        "q_feature_map",
        "q_reps",
        "q_input_scaling",
        "dim",
        "window_size",
        "alpha",
        "n_permutations",
    ]

    for key, g in window_df.groupby(base_cols, dropna=False):
        base = dict(zip(base_cols, key))

        cal = g[g["phase"] == "calibration"].sort_values("window_index")
        pre = g[g["phase"] == "pre_eval"].sort_values("window_index")

        if len(cal) == 0 or len(pre) == 0:
            continue

        cal_scores = cal["score"].to_numpy()
        pre_scores = pre["score"].to_numpy()

        for severity in sorted(g[g["phase"] == "post"]["severity"].unique()):
            post = g[(g["phase"] == "post") & (g["severity"] == severity)].sort_values("window_index")

            if len(post) == 0:
                continue

            post_scores = post["score"].to_numpy()

            y = np.array([0] * len(pre_scores) + [1] * len(post_scores))
            scores = np.concatenate([pre_scores, post_scores])

            try:
                auc = float(roc_auc_score(y, scores))
            except Exception:
                auc = np.nan

            for q in threshold_quantiles:
                threshold = float(np.quantile(cal_scores, q))

                pre_flags = pre_scores > threshold
                post_flags = post_scores > threshold

                for k in consecutive_ks:
                    false_alarm_any, false_alarm_delay = first_consecutive_trigger(pre_flags, k)
                    post_detect_any, delay_windows = first_consecutive_trigger(post_flags, k)

                    row = dict(base)
                    row.update(
                        {
                            "severity": float(severity),
                            "threshold_quantile": float(q),
                            "consecutive_k": int(k),
                            "threshold": threshold,
                            "false_alarm_any": bool(false_alarm_any),
                            "post_detect_any": bool(post_detect_any),
                            "false_alarm_delay_windows": false_alarm_delay,
                            "delay_windows": delay_windows,
                            "false_alarm_rate_pre": float(np.mean(pre_flags)),
                            "detection_rate_post": float(np.mean(post_flags)),
                            "cal_score_mean": float(np.mean(cal_scores)),
                            "pre_score_mean": float(np.mean(pre_scores)),
                            "post_score_mean": float(np.mean(post_scores)),
                            "score_gap": float(np.mean(post_scores) - np.mean(pre_scores)),
                            "pre_post_auc": auc,
                        }
                    )
                    policy_rows.append(row)

    policy_df = pd.DataFrame(policy_rows)

    by_seed_path = outdir / "controlled_streaming_policy_by_seed.csv"
    policy_df.to_csv(by_seed_path, index=False)

    group_cols = [
        "dataset",
        "protocol",
        "detector",
        "q_feature_map",
        "q_reps",
        "q_input_scaling",
        "dim",
        "window_size",
        "alpha",
        "n_permutations",
        "severity",
        "threshold_quantile",
        "consecutive_k",
    ]

    summary = (
        policy_df.groupby(group_cols, dropna=False)
        .agg(
            n_seeds=("seed", "nunique"),
            false_alarm_any_rate=("false_alarm_any", "mean"),
            post_detect_any_rate=("post_detect_any", "mean"),
            false_alarm_rate_pre_mean=("false_alarm_rate_pre", "mean"),
            detection_rate_post_mean=("detection_rate_post", "mean"),
            delay_windows_mean=("delay_windows", "mean"),
            false_alarm_delay_windows_mean=("false_alarm_delay_windows", "mean"),
            threshold_mean=("threshold", "mean"),
            cal_score_mean=("cal_score_mean", "mean"),
            pre_score_mean=("pre_score_mean", "mean"),
            post_score_mean=("post_score_mean", "mean"),
            score_gap_mean=("score_gap", "mean"),
            pre_post_auc_mean=("pre_post_auc", "mean"),
        )
        .reset_index()
    )

    summary["trigger_gain"] = summary["post_detect_any_rate"] - summary["false_alarm_any_rate"]
    summary["window_rate_gain"] = summary["detection_rate_post_mean"] - summary["false_alarm_rate_pre_mean"]

    summary = summary.sort_values(
        [
            "severity",
            "trigger_gain",
            "window_rate_gain",
            "post_detect_any_rate",
            "false_alarm_any_rate",
        ],
        ascending=[True, False, False, False, True],
    )

    summary_path = outdir / "controlled_streaming_policy_summary.csv"
    summary.to_csv(summary_path, index=False)

    print(f"Saved: {by_seed_path}")
    print(f"Saved: {summary_path}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paper 2 controlled streaming drift benchmark."
    )

    parser.add_argument("--data-ref", required=True)
    parser.add_argument("--data-cur", required=True)
    parser.add_argument("--label-col", default="Label")
    parser.add_argument("--label-values-ref", default="")
    parser.add_argument("--label-values-cur", default="")
    parser.add_argument("--dataset", default="cicids2017_controlled")
    parser.add_argument("--outdir", default="results/raw/cicids_controlled_streaming_001")

    parser.add_argument("--dims", default="8")
    parser.add_argument("--window-size", type=int, default=256)
    parser.add_argument("--seeds", default="1,2,3")
    parser.add_argument("--max-rows", type=int, default=200000)

    parser.add_argument("--calibration-windows", type=int, default=10)
    parser.add_argument("--pre-windows", type=int, default=10)
    parser.add_argument("--post-windows", type=int, default=10)
    parser.add_argument("--severities", default="0.1,0.25,0.5,0.75,1.0")

    parser.add_argument("--threshold-quantiles", default="0.95,0.975,0.99,1.0")
    parser.add_argument("--consecutive-ks", default="1,2,3")

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
    threshold_quantiles = parse_csv_list(args.threshold_quantiles, float)
    consecutive_ks = parse_csv_list(args.consecutive_ks, int)

    label_values_ref = parse_label_values(args.label_values_ref)
    label_values_cur = parse_label_values(args.label_values_cur)

    print(f"[LOAD] reference: {args.data_ref}")
    df_ref = load_numeric_csv(
        Path(args.data_ref),
        args.label_col,
        label_values_ref,
        args.max_rows,
    )

    print(f"[LOAD] current:   {args.data_cur}")
    df_cur = load_numeric_csv(
        Path(args.data_cur),
        args.label_col,
        label_values_cur,
        args.max_rows,
    )

    df_ref, df_cur = align_columns(df_ref, df_cur)

    X_ref_pool = df_ref.to_numpy(dtype=np.float64)
    X_cur_pool = df_cur.to_numpy(dtype=np.float64)

    print(f"[DATA] ref={X_ref_pool.shape} cur={X_cur_pool.shape} common_features={df_ref.shape[1]}")

    rows = []
    run_id = 0

    for seed in seeds:
        rng = np.random.default_rng(seed)

        for dim in dims:
            print(f"\n[SEED={seed}][DIM={dim}] preparing shared windows")

            X_anchor_raw = sample_window(X_ref_pool, args.window_size, rng)
            scaler, svd = fit_preprocessor(X_anchor_raw, dim=dim, seed=seed)
            X_anchor = transform_window(scaler, svd, X_anchor_raw)

            cal_windows = [
                transform_window(scaler, svd, sample_window(X_ref_pool, args.window_size, rng))
                for _ in range(args.calibration_windows)
            ]

            pre_windows = [
                transform_window(scaler, svd, sample_window(X_ref_pool, args.window_size, rng))
                for _ in range(args.pre_windows)
            ]

            post_windows_by_severity = {
                severity: [
                    transform_window(
                        scaler,
                        svd,
                        sample_mixed_window(
                            X_ref_pool,
                            X_cur_pool,
                            args.window_size,
                            severity,
                            rng,
                        ),
                    )
                    for _ in range(args.post_windows)
                ]
                for severity in severities
            }

            detector_configs = make_detector_configs(args, seed)

            for cfg in detector_configs:
                model = cfg["model"]
                model.fit(X_anchor)

                row_base = {
                    "dataset": args.dataset,
                    "protocol": "controlled_streaming_mixture",
                    "run_id": None,
                    "seed": seed,
                    "detector": cfg["detector"],
                    "q_feature_map": cfg["q_feature_map"],
                    "q_reps": cfg["q_reps"],
                    "q_input_scaling": cfg["q_input_scaling"],
                    "dim": X_anchor.shape[1],
                    "window_size": args.window_size,
                    "alpha": args.alpha,
                    "n_permutations": args.n_permutations,
                }

                print(
                    f"[RUN] seed={seed} dim={X_anchor.shape[1]} "
                    f"detector={cfg['detector']} qmap={cfg['q_feature_map'] or '-'}"
                )

                for i, Xw in enumerate(cal_windows):
                    run_id += 1
                    base = dict(row_base)
                    base["run_id"] = run_id
                    rows.append(
                        score_window(
                            model=model,
                            row_base=base,
                            phase="calibration",
                            window_index=i,
                            severity=0.0,
                            true_drift=False,
                            X_window=Xw,
                        )
                    )

                for i, Xw in enumerate(pre_windows):
                    run_id += 1
                    base = dict(row_base)
                    base["run_id"] = run_id
                    rows.append(
                        score_window(
                            model=model,
                            row_base=base,
                            phase="pre_eval",
                            window_index=i,
                            severity=0.0,
                            true_drift=False,
                            X_window=Xw,
                        )
                    )

                for severity, post_windows in post_windows_by_severity.items():
                    for i, Xw in enumerate(post_windows):
                        run_id += 1
                        base = dict(row_base)
                        base["run_id"] = run_id
                        rows.append(
                            score_window(
                                model=model,
                                row_base=base,
                                phase="post",
                                window_index=i,
                                severity=severity,
                                true_drift=severity > 0.0,
                                X_window=Xw,
                            )
                        )

    window_df = pd.DataFrame(rows)

    window_path = outdir / "paper2_controlled_streaming_window_results.csv"
    window_df.to_csv(window_path, index=False)
    print(f"\nSaved: {window_path}")

    summary = build_policy_summary(
        window_df=window_df,
        threshold_quantiles=threshold_quantiles,
        consecutive_ks=consecutive_ks,
        outdir=outdir,
    )

    view_cols = [
        "severity",
        "threshold_quantile",
        "consecutive_k",
        "detector",
        "q_feature_map",
        "n_seeds",
        "false_alarm_any_rate",
        "post_detect_any_rate",
        "trigger_gain",
        "false_alarm_rate_pre_mean",
        "detection_rate_post_mean",
        "window_rate_gain",
        "delay_windows_mean",
        "score_gap_mean",
        "pre_post_auc_mean",
    ]

    print("\n=== CONTROLLED STREAMING SUMMARY ===")
    print(summary[view_cols].to_string(index=False))


if __name__ == "__main__":
    main()
