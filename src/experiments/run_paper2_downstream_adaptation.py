from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.drift_detection.mmd_rbf_detector import MmdRbfDetector
from src.drift_detection.qk_mmd_detector import QkMmdDetector


@dataclass
class Preprocessor:
    scaler: StandardScaler
    reducer: TruncatedSVD | None
    dim: int

    def transform(self, X: np.ndarray) -> np.ndarray:
        Z = self.scaler.transform(X)
        if self.reducer is not None:
            Z = self.reducer.transform(Z)
        return np.asarray(Z, dtype=np.float64)


def parse_csv_list(value: str, cast=str) -> list:
    if value is None or str(value).strip() == "":
        return []
    return [cast(v.strip()) for v in str(value).split(",") if v.strip()]


def find_label_col(columns: list[str], requested: str) -> str:
    requested_clean = requested.strip().lower()
    for col in columns:
        if col.strip().lower() == requested_clean:
            return col
    raise ValueError(f"Could not find label column {requested!r}. Available tail: {columns[-10:]}")


def load_cicids_binary(path: Path, label_col: str, max_rows: int | None) -> tuple[pd.DataFrame, np.ndarray]:
    print(f"[LOAD] {path}")

    df = pd.read_csv(path, nrows=max_rows, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]

    label_col = find_label_col(list(df.columns), label_col)

    labels = df[label_col].astype(str).str.strip()
    y = (labels != "BENIGN").astype(np.int64).to_numpy()

    X_df = df.drop(columns=[label_col])
    X_df = X_df.apply(pd.to_numeric, errors="coerce")
    X_df = X_df.replace([np.inf, -np.inf], np.nan)

    valid_cols = [c for c in X_df.columns if not X_df[c].isna().all()]
    X_df = X_df[valid_cols]

    medians = X_df.median(numeric_only=True)
    X_df = X_df.fillna(medians).fillna(0.0)

    print(f"[DATA] rows={len(X_df)} features={X_df.shape[1]} benign={(y == 0).sum()} attack={(y == 1).sum()}")

    return X_df, y


def align_features(
    X_ref_df: pd.DataFrame,
    X_cur_df: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    common = [c for c in X_ref_df.columns if c in set(X_cur_df.columns)]
    if not common:
        raise ValueError("No common numeric features between reference and current data.")

    X_ref = X_ref_df[common].to_numpy(dtype=np.float64)
    X_cur = X_cur_df[common].to_numpy(dtype=np.float64)

    print(f"[ALIGN] common_features={len(common)}")

    return X_ref, X_cur, common


def class_indices(y: np.ndarray) -> dict[int, np.ndarray]:
    return {
        0: np.flatnonzero(y == 0),
        1: np.flatnonzero(y == 1),
    }


def sample_from_indices(indices: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    if n <= 0:
        return np.empty(0, dtype=np.int64)

    replace = len(indices) < n
    return rng.choice(indices, size=n, replace=replace)


def sample_balanced(
    X: np.ndarray,
    y: np.ndarray,
    n_per_class: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    idx = class_indices(y)

    parts_X = []
    parts_y = []

    for cls in [0, 1]:
        chosen = sample_from_indices(idx[cls], n_per_class, rng)
        parts_X.append(X[chosen])
        parts_y.append(y[chosen])

    X_out = np.vstack(parts_X)
    y_out = np.concatenate(parts_y)

    perm = rng.permutation(len(y_out))
    return X_out[perm], y_out[perm]


def sample_mixed_balanced(
    X_ref: np.ndarray,
    y_ref: np.ndarray,
    X_cur: np.ndarray,
    y_cur: np.ndarray,
    n_per_class: int,
    severity: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    if not 0.0 <= severity <= 1.0:
        raise ValueError("severity must be in [0, 1].")

    idx_ref = class_indices(y_ref)
    idx_cur = class_indices(y_cur)

    n_cur = int(round(n_per_class * severity))
    n_ref = n_per_class - n_cur

    parts_X = []
    parts_y = []

    for cls in [0, 1]:
        if n_ref > 0:
            ref_chosen = sample_from_indices(idx_ref[cls], n_ref, rng)
            parts_X.append(X_ref[ref_chosen])
            parts_y.append(y_ref[ref_chosen])

        if n_cur > 0:
            cur_chosen = sample_from_indices(idx_cur[cls], n_cur, rng)
            parts_X.append(X_cur[cur_chosen])
            parts_y.append(y_cur[cur_chosen])

    X_out = np.vstack(parts_X)
    y_out = np.concatenate(parts_y)

    perm = rng.permutation(len(y_out))
    return X_out[perm], y_out[perm]


def fit_preprocessor(X_train: np.ndarray, dim: int, random_state: int) -> Preprocessor:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    if dim <= 0:
        raise ValueError("dim must be positive.")

    if dim > X_scaled.shape[1]:
        raise ValueError(f"Requested dim={dim}, but only {X_scaled.shape[1]} features are available.")

    reducer = None
    if dim < X_scaled.shape[1]:
        reducer = TruncatedSVD(n_components=dim, random_state=random_state)
        reducer.fit(X_scaled)

    return Preprocessor(scaler=scaler, reducer=reducer, dim=dim)


def make_model(model_name: str, svc_c: float, svc_gamma: str | float):
    if model_name == "svc_rbf":
        return SVC(
            kernel="rbf",
            C=svc_c,
            gamma=svc_gamma,
            class_weight="balanced",
        )

    if model_name == "logreg":
        return LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            solver="lbfgs",
        )

    raise ValueError(f"Unknown model={model_name}")


def fit_model(
    model_name: str,
    X: np.ndarray,
    y: np.ndarray,
    svc_c: float,
    svc_gamma: str | float,
):
    model = make_model(model_name, svc_c=svc_c, svc_gamma=svc_gamma)
    start = time.perf_counter()
    model.fit(X, y)
    runtime = time.perf_counter() - start
    return model, runtime


def eval_model(model, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
    pred = model.predict(X)

    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()

    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "false_positive_rate": float(fpr),
        "false_negative_rate": float(fnr),
    }


def make_detector(
    detector: str,
    q_feature_map: str | None,
    args: argparse.Namespace,
    random_state: int,
):
    if detector == "mmd_rbf":
        return MmdRbfDetector(
            gamma=None,
            biased=True,
            alpha=args.alpha,
            n_permutations=args.n_permutations,
            random_state=random_state,
        )

    if detector == "qk_mmd":
        if q_feature_map is None:
            raise ValueError("q_feature_map is required for qk_mmd.")

        return QkMmdDetector(
            feature_map=q_feature_map,
            reps=args.q_reps,
            biased=True,
            alpha=args.alpha,
            n_permutations=args.n_permutations,
            random_state=random_state,
            input_scaling=args.q_input_scaling,
        )

    raise ValueError(f"Unknown detector={detector}")


def first_consecutive_trigger(alarms: list[bool], k: int) -> int | None:
    if k <= 1:
        for i, alarm in enumerate(alarms):
            if alarm:
                return i
        return None

    for i in range(0, len(alarms) - k + 1):
        if all(alarms[i : i + k]):
            return i + k - 1

    return None


def score_detector_sequence(
    detector,
    windows: list[np.ndarray],
) -> tuple[list[float], float]:
    scores = []
    start = time.perf_counter()

    for X_window in windows:
        scores.append(float(detector.score(X_window)))

    runtime = time.perf_counter() - start
    return scores, runtime


def recovery_time(
    strategy_scores: list[float],
    oracle_scores: list[float],
    recovery_fraction: float,
) -> int | None:
    for i, (score, oracle) in enumerate(zip(strategy_scores, oracle_scores)):
        target = recovery_fraction * oracle
        if score >= target:
            return i
    return None


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--data-ref", type=Path, required=True)
    parser.add_argument("--data-cur", type=Path, required=True)
    parser.add_argument("--label-col", type=str, default="Label")
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--outdir", type=Path, required=True)

    parser.add_argument("--protocol", type=str, default="balanced_prior")
    parser.add_argument("--model", type=str, default="svc_rbf", choices=["svc_rbf", "logreg"])
    parser.add_argument("--svc-c", type=float, default=1.0)
    parser.add_argument("--svc-gamma", type=str, default="scale")

    parser.add_argument("--dim", type=int, default=8)
    parser.add_argument("--window-size", type=int, default=128)
    parser.add_argument("--train-size-per-class", type=int, default=1500)
    parser.add_argument("--adapt-size-per-class", type=int, default=256)

    parser.add_argument("--calibration-windows", type=int, default=10)
    parser.add_argument("--pre-windows", type=int, default=10)
    parser.add_argument("--post-windows", type=int, default=10)

    parser.add_argument("--seeds", type=str, default="1,2,3")
    parser.add_argument("--severities", type=str, default="0.5,0.75,1.0")

    parser.add_argument("--threshold-quantile", type=float, default=0.95)
    parser.add_argument("--consecutive-k", type=int, default=2)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-permutations", type=int, default=100)

    parser.add_argument("--detectors", type=str, default="mmd_rbf,qk_mmd")
    parser.add_argument("--q-feature-maps", type=str, default="zz,pauli_xz")
    parser.add_argument("--q-reps", type=int, default=1)
    parser.add_argument("--q-input-scaling", type=str, default="atan_standard")

    parser.add_argument("--recovery-fraction", type=float, default=0.95)
    parser.add_argument("--max-rows", type=int, default=0)

    args = parser.parse_args()

    if args.window_size % 2 != 0:
        raise ValueError("window-size must be even for balanced-prior sampling.")

    if args.protocol != "balanced_prior":
        raise ValueError("This first runner currently supports only --protocol balanced_prior.")

    seeds = parse_csv_list(args.seeds, int)
    severities = parse_csv_list(args.severities, float)
    detectors = parse_csv_list(args.detectors, str)
    q_feature_maps = parse_csv_list(args.q_feature_maps, str)

    max_rows = args.max_rows if args.max_rows and args.max_rows > 0 else None

    args.outdir.mkdir(parents=True, exist_ok=True)

    X_ref_df, y_ref = load_cicids_binary(args.data_ref, args.label_col, max_rows=max_rows)
    X_cur_df, y_cur = load_cicids_binary(args.data_cur, args.label_col, max_rows=max_rows)

    X_ref, X_cur, common_features = align_features(X_ref_df, X_cur_df)

    if (y_ref == 1).sum() == 0 or (y_cur == 1).sum() == 0:
        raise ValueError("Both reference and current datasets must contain ATTACK samples.")

    n_per_window_class = args.window_size // 2

    window_rows: list[dict[str, Any]] = []
    by_seed_rows: list[dict[str, Any]] = []

    for seed in seeds:
        rng = np.random.default_rng(seed)

        print()
        print("=" * 100)
        print(f"[SEED={seed}]")
        print("=" * 100)

        X_train_raw, y_train = sample_balanced(
            X_ref,
            y_ref,
            n_per_class=args.train_size_per_class,
            rng=rng,
        )

        preprocessor = fit_preprocessor(
            X_train_raw,
            dim=args.dim,
            random_state=seed,
        )

        X_train = preprocessor.transform(X_train_raw)

        initial_model, initial_fit_runtime = fit_model(
            args.model,
            X_train,
            y_train,
            svc_c=args.svc_c,
            svc_gamma=args.svc_gamma,
        )

        for severity in severities:
            print()
            print(f"[SEED={seed}][SEVERITY={severity}]")

            anchor_raw, _ = sample_balanced(
                X_ref,
                y_ref,
                n_per_class=n_per_window_class,
                rng=rng,
            )

            calibration_raw = [
                sample_balanced(
                    X_ref,
                    y_ref,
                    n_per_class=n_per_window_class,
                    rng=rng,
                )[0]
                for _ in range(args.calibration_windows)
            ]

            pre_raw = [
                sample_balanced(
                    X_ref,
                    y_ref,
                    n_per_class=n_per_window_class,
                    rng=rng,
                )
                for _ in range(args.pre_windows)
            ]

            post_raw = [
                sample_mixed_balanced(
                    X_ref,
                    y_ref,
                    X_cur,
                    y_cur,
                    n_per_class=n_per_window_class,
                    severity=severity,
                    rng=rng,
                )
                for _ in range(args.post_windows)
            ]

            X_adapt_raw, y_adapt = sample_mixed_balanced(
                X_ref,
                y_ref,
                X_cur,
                y_cur,
                n_per_class=args.adapt_size_per_class,
                severity=severity,
                rng=rng,
            )

            X_adapt = preprocessor.transform(X_adapt_raw)
            X_adapt_train = np.vstack([X_train, X_adapt])
            y_adapt_train = np.concatenate([y_train, y_adapt])

            adapted_model, adapted_fit_runtime = fit_model(
                args.model,
                X_adapt_train,
                y_adapt_train,
                svc_c=args.svc_c,
                svc_gamma=args.svc_gamma,
            )

            post_X = [preprocessor.transform(Xw) for Xw, _ in post_raw]
            post_y = [yw for _, yw in post_raw]

            no_adapt_metrics = [
                eval_model(initial_model, Xw, yw)
                for Xw, yw in zip(post_X, post_y)
            ]

            oracle_metrics = [
                eval_model(adapted_model, Xw, yw)
                for Xw, yw in zip(post_X, post_y)
            ]

            no_adapt_bal_acc = [m["balanced_accuracy"] for m in no_adapt_metrics]
            oracle_bal_acc = [m["balanced_accuracy"] for m in oracle_metrics]

            detector_infos: dict[str, dict[str, Any]] = {}

            detector_specs: list[tuple[str, str | None]] = []
            if "mmd_rbf" in detectors:
                detector_specs.append(("mmd_rbf", None))
            if "qk_mmd" in detectors:
                for qmap in q_feature_maps:
                    detector_specs.append(("qk_mmd", qmap))

            anchor = preprocessor.transform(anchor_raw)
            calibration = [preprocessor.transform(Xw) for Xw in calibration_raw]
            pre_windows = [preprocessor.transform(Xw) for Xw, _ in pre_raw]
            post_windows = post_X

            for detector_name, qmap in detector_specs:
                method_name = "mmd_rbf" if detector_name == "mmd_rbf" else f"qk_mmd_{qmap}"

                print(f"[DETECTOR] {method_name}")

                detector = make_detector(
                    detector_name,
                    qmap,
                    args=args,
                    random_state=seed,
                )
                detector.fit(anchor)

                calibration_scores, runtime_cal = score_detector_sequence(detector, calibration)
                threshold = float(np.quantile(calibration_scores, args.threshold_quantile))

                pre_scores, runtime_pre = score_detector_sequence(detector, pre_windows)
                post_scores, runtime_post = score_detector_sequence(detector, post_windows)

                pre_alarms = [s > threshold for s in pre_scores]
                post_alarms = [s > threshold for s in post_scores]

                pre_trigger = first_consecutive_trigger(pre_alarms, args.consecutive_k)
                post_trigger = first_consecutive_trigger(post_alarms, args.consecutive_k)

                detector_infos[method_name] = {
                    "detector": detector_name,
                    "q_feature_map": qmap,
                    "threshold": threshold,
                    "pre_scores": pre_scores,
                    "post_scores": post_scores,
                    "pre_alarms": pre_alarms,
                    "post_alarms": post_alarms,
                    "pre_trigger": pre_trigger,
                    "post_trigger": post_trigger,
                    "runtime": runtime_cal + runtime_pre + runtime_post,
                }

            strategy_specs: list[dict[str, Any]] = [
                {
                    "strategy": "no_adaptation",
                    "detector": None,
                    "q_feature_map": None,
                    "trigger_delay": None,
                    "false_alarm_any": False,
                    "adaptation_start": None,
                    "detector_runtime": 0.0,
                    "threshold": np.nan,
                },
                {
                    "strategy": "oracle_adaptation",
                    "detector": "oracle",
                    "q_feature_map": None,
                    "trigger_delay": 0,
                    "false_alarm_any": False,
                    "adaptation_start": 0,
                    "detector_runtime": 0.0,
                    "threshold": np.nan,
                },
            ]

            for method_name, info in detector_infos.items():
                post_trigger = info["post_trigger"]
                adaptation_start = None
                if post_trigger is not None:
                    adaptation_start = post_trigger + 1
                    if adaptation_start >= args.post_windows:
                        adaptation_start = None

                strategy_specs.append(
                    {
                        "strategy": f"{method_name}_triggered_adaptation",
                        "detector": info["detector"],
                        "q_feature_map": info["q_feature_map"],
                        "trigger_delay": post_trigger,
                        "false_alarm_any": info["pre_trigger"] is not None,
                        "adaptation_start": adaptation_start,
                        "detector_runtime": info["runtime"],
                        "threshold": info["threshold"],
                    }
                )

            strategy_window_metrics: dict[str, list[dict[str, float]]] = {}

            for spec in strategy_specs:
                strategy = spec["strategy"]
                adaptation_start = spec["adaptation_start"]

                metrics_seq = []

                for i, (Xw, yw) in enumerate(zip(post_X, post_y)):
                    use_adapted = adaptation_start is not None and i >= adaptation_start
                    model = adapted_model if use_adapted else initial_model

                    metrics = eval_model(model, Xw, yw)
                    metrics_seq.append(metrics)

                    oracle_gap = max(oracle_bal_acc[i] - metrics["balanced_accuracy"], 0.0)

                    window_rows.append(
                        {
                            "dataset": args.dataset,
                            "protocol": args.protocol,
                            "model": args.model,
                            "seed": seed,
                            "severity": severity,
                            "strategy": strategy,
                            "detector": spec["detector"],
                            "q_feature_map": spec["q_feature_map"],
                            "dim": args.dim,
                            "window_size": args.window_size,
                            "window_index": i,
                            "adapted": bool(use_adapted),
                            "balanced_accuracy": metrics["balanced_accuracy"],
                            "f1": metrics["f1"],
                            "precision": metrics["precision"],
                            "recall": metrics["recall"],
                            "false_positive_rate": metrics["false_positive_rate"],
                            "false_negative_rate": metrics["false_negative_rate"],
                            "oracle_balanced_accuracy": oracle_bal_acc[i],
                            "no_adapt_balanced_accuracy": no_adapt_bal_acc[i],
                            "oracle_gap": oracle_gap,
                        }
                    )

                strategy_window_metrics[strategy] = metrics_seq

                bal_acc_seq = [m["balanced_accuracy"] for m in metrics_seq]
                f1_seq = [m["f1"] for m in metrics_seq]

                rec_time = recovery_time(
                    bal_acc_seq,
                    oracle_bal_acc,
                    recovery_fraction=args.recovery_fraction,
                )

                adaptation_gain = float(np.mean(bal_acc_seq) - np.mean(no_adapt_bal_acc))
                degradation_area = float(np.mean([max(o - s, 0.0) for s, o in zip(bal_acc_seq, oracle_bal_acc)]))

                triggered_post = spec["trigger_delay"] is not None
                false_alarm_any = bool(spec["false_alarm_any"])
                adapted_any = spec["adaptation_start"] is not None

                is_triggered_strategy = strategy not in {"no_adaptation", "oracle_adaptation"}

                clean_downstream_adaptation = bool(
                    is_triggered_strategy
                    and triggered_post
                    and not false_alarm_any
                    and adaptation_gain > 0.0
                )

                clean_adaptation_gain = adaptation_gain if clean_downstream_adaptation else 0.0

                by_seed_rows.append(
                    {
                        "dataset": args.dataset,
                        "protocol": args.protocol,
                        "model": args.model,
                        "seed": seed,
                        "severity": severity,
                        "strategy": strategy,
                        "detector": spec["detector"],
                        "q_feature_map": spec["q_feature_map"],
                        "dim": args.dim,
                        "window_size": args.window_size,
                        "train_size_per_class": args.train_size_per_class,
                        "adapt_size_per_class": args.adapt_size_per_class,
                        "post_balanced_accuracy_mean": float(np.mean(bal_acc_seq)),
                        "post_f1_mean": float(np.mean(f1_seq)),
                        "degradation_area": degradation_area,
                        "adaptation_gain_vs_no_adapt": adaptation_gain,
                        "clean_downstream_adaptation": clean_downstream_adaptation,
                        "clean_adaptation_gain": clean_adaptation_gain,
                        "recovery_time": rec_time,
                        "triggered_post": triggered_post,
                        "trigger_delay_windows": spec["trigger_delay"],
                        "false_alarm_any": false_alarm_any,
                        "adapted_any": adapted_any,
                        "adaptation_start_window": spec["adaptation_start"],
                        "threshold": spec["threshold"],
                        "initial_fit_runtime_sec": initial_fit_runtime,
                        "adapted_fit_runtime_sec": adapted_fit_runtime,
                        "detector_runtime_sec": spec["detector_runtime"],
                    }
                )

    window_df = pd.DataFrame(window_rows)
    by_seed_df = pd.DataFrame(by_seed_rows)

    group_cols = [
        "dataset",
        "protocol",
        "model",
        "severity",
        "strategy",
        "detector",
        "q_feature_map",
        "dim",
        "window_size",
        "train_size_per_class",
        "adapt_size_per_class",
    ]

    summary_df = (
        by_seed_df
        .groupby(group_cols, dropna=False)
        .agg(
            n_seeds=("seed", "nunique"),
            post_balanced_accuracy_mean=("post_balanced_accuracy_mean", "mean"),
            post_balanced_accuracy_std=("post_balanced_accuracy_mean", "std"),
            post_f1_mean=("post_f1_mean", "mean"),
            post_f1_std=("post_f1_mean", "std"),
            degradation_area_mean=("degradation_area", "mean"),
            degradation_area_std=("degradation_area", "std"),
            adaptation_gain_vs_no_adapt_mean=("adaptation_gain_vs_no_adapt", "mean"),
            clean_downstream_adaptation_rate=("clean_downstream_adaptation", "mean"),
            clean_adaptation_gain_mean=("clean_adaptation_gain", "mean"),
            recovery_time_mean=("recovery_time", "mean"),
            triggered_post_rate=("triggered_post", "mean"),
            false_alarm_any_rate=("false_alarm_any", "mean"),
            adapted_any_rate=("adapted_any", "mean"),
            trigger_delay_windows_mean=("trigger_delay_windows", "mean"),
            initial_fit_runtime_sec_mean=("initial_fit_runtime_sec", "mean"),
            adapted_fit_runtime_sec_mean=("adapted_fit_runtime_sec", "mean"),
            detector_runtime_sec_mean=("detector_runtime_sec", "mean"),
        )
        .reset_index()
        .sort_values(["severity", "strategy"])
    )

    window_path = args.outdir / "paper2_downstream_window_results.csv"
    by_seed_path = args.outdir / "paper2_downstream_by_seed.csv"
    summary_path = args.outdir / "paper2_downstream_summary.csv"

    window_df.to_csv(window_path, index=False)
    by_seed_df.to_csv(by_seed_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    print()
    print(f"Saved: {window_path}")
    print(f"Saved: {by_seed_path}")
    print(f"Saved: {summary_path}")

    print()
    print("=== DOWNSTREAM SUMMARY ===")
    cols = [
        "severity",
        "strategy",
        "n_seeds",
        "post_balanced_accuracy_mean",
        "post_f1_mean",
        "degradation_area_mean",
        "adaptation_gain_vs_no_adapt_mean",
        "clean_downstream_adaptation_rate",
        "clean_adaptation_gain_mean",
        "recovery_time_mean",
        "triggered_post_rate",
        "false_alarm_any_rate",
        "trigger_delay_windows_mean",
    ]
    print(summary_df[cols].to_string(index=False))


if __name__ == "__main__":
    main()
