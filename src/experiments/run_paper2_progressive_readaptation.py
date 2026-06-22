from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.experiments.run_paper2_downstream_adaptation import (
    MmdRbfDetector,
    QkMmdDetector,
)


@dataclass
class Pools:
    ref_benign: np.ndarray
    ref_attack: np.ndarray
    cur_benign: np.ndarray
    cur_attack: np.ndarray


def parse_csv_list(value: str, cast=str):
    if value is None or value == "":
        return []
    return [cast(x.strip()) for x in value.split(",") if x.strip()]


def load_binary_dataset(path: Path, label_col: str) -> tuple[pd.DataFrame, pd.Series]:
    print(f"[LOAD] {path}")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    label_col = label_col.strip()
    if label_col not in df.columns:
        raise ValueError(f"Label column {label_col!r} not found. Available: {df.columns[:10].tolist()}...")

    y_raw = df[label_col].astype(str).str.strip()
    y = (y_raw != "BENIGN").astype(int)

    X = df.drop(columns=[label_col]).copy()

    # Keep numeric columns only.
    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0.0)

    print(
        f"[DATA] rows={len(df)} features={X.shape[1]} "
        f"benign={(y == 0).sum()} attack={(y == 1).sum()}"
    )

    return X, y


def make_pools(
    X_ref: pd.DataFrame,
    y_ref: pd.Series,
    X_cur: pd.DataFrame,
    y_cur: pd.Series,
    common_features: list[str],
) -> Pools:
    Xr = X_ref[common_features].to_numpy(dtype=float)
    Xc = X_cur[common_features].to_numpy(dtype=float)

    return Pools(
        ref_benign=Xr[y_ref.to_numpy() == 0],
        ref_attack=Xr[y_ref.to_numpy() == 1],
        cur_benign=Xc[y_cur.to_numpy() == 0],
        cur_attack=Xc[y_cur.to_numpy() == 1],
    )


def sample_rows(pool: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    idx = rng.integers(0, len(pool), size=n)
    return pool[idx]


def sample_balanced_from_distribution(
    pools: Pools,
    n_per_class: int,
    severity: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Balanced binary sample. Each class is a mixture ref/current controlled by severity."""
    severity = float(np.clip(severity, 0.0, 1.0))

    n_cur = int(round(n_per_class * severity))
    n_ref = n_per_class - n_cur

    xb = np.vstack(
        [
            sample_rows(pools.ref_benign, n_ref, rng),
            sample_rows(pools.cur_benign, n_cur, rng),
        ]
    )

    xa = np.vstack(
        [
            sample_rows(pools.ref_attack, n_ref, rng),
            sample_rows(pools.cur_attack, n_cur, rng),
        ]
    )

    X = np.vstack([xb, xa])
    y = np.array([0] * n_per_class + [1] * n_per_class)

    perm = rng.permutation(len(y))
    return X[perm], y[perm]


def fit_transformer(X_train: np.ndarray, dim: int, seed: int):
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_train)

    if dim < Xs.shape[1]:
        pca = PCA(n_components=dim, random_state=seed)
        Xr = pca.fit_transform(Xs)
    else:
        pca = None
        Xr = Xs

    return scaler, pca, Xr


def transform_X(X: np.ndarray, scaler: StandardScaler, pca: PCA | None) -> np.ndarray:
    Xs = scaler.transform(X)
    if pca is not None:
        return pca.transform(Xs)
    return Xs


def train_svc(X: np.ndarray, y: np.ndarray, seed: int) -> SVC:
    model = SVC(
        kernel="rbf",
        gamma="scale",
        class_weight="balanced",
        random_state=seed,
    )
    model.fit(X, y)
    return model


def evaluate_model(model: SVC, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
    pred = model.predict(X)
    return {
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "f1": float(f1_score(y, pred, zero_division=0)),
    }


def build_detector(method: str, args, seed: int):
    if method == "mmd_rbf":
        return MmdRbfDetector(
            gamma=None,
            biased=True,
            alpha=args.alpha,
            n_permutations=args.n_permutations,
            random_state=seed,
        )

    if method == "qk_mmd_zz":
        return QkMmdDetector(
            feature_map="zz",
            reps=args.q_reps,
            biased=True,
            alpha=args.alpha,
            n_permutations=args.n_permutations,
            random_state=seed,
            input_scaling=args.q_input_scaling,
        )

    if method == "qk_mmd_pauli_xz":
        return QkMmdDetector(
            feature_map="pauli_xz",
            reps=args.q_reps,
            biased=True,
            alpha=args.alpha,
            n_permutations=args.n_permutations,
            random_state=seed,
            input_scaling=args.q_input_scaling,
        )

    raise ValueError(f"Unknown method={method}")


def calibrate_detector(
    detector,
    pools: Pools,
    scaler: StandardScaler,
    pca: PCA | None,
    severity: float,
    args,
    rng: np.random.Generator,
) -> tuple[object, float]:
    X_ref_raw, _ = sample_balanced_from_distribution(
        pools,
        n_per_class=args.detector_ref_size_per_class,
        severity=severity,
        rng=rng,
    )
    X_ref = transform_X(X_ref_raw, scaler, pca)

    detector.fit(X_ref)

    scores = []
    for _ in range(args.calibration_windows):
        Xw_raw, _ = sample_balanced_from_distribution(
            pools,
            n_per_class=args.window_size // 2,
            severity=severity,
            rng=rng,
        )
        Xw = transform_X(Xw_raw, scaler, pca)
        scores.append(float(detector.score(Xw)))

    threshold = float(np.quantile(scores, args.threshold_quantile))
    return detector, threshold


def progressive_severity(t: int, args) -> float:
    if args.ramp_windows <= 1:
        return args.max_severity

    raw = (t + 1) / args.ramp_windows * args.max_severity
    return float(min(args.max_severity, raw))


def run_strategy(
    method: str,
    pools: Pools,
    scaler: StandardScaler,
    pca: PCA | None,
    initial_model: SVC,
    no_adapt_window_metrics: list[dict[str, float]],
    args,
    seed: int,
) -> tuple[list[dict], dict]:
    method_seed_offsets = {
        "mmd_rbf": 101,
        "qk_mmd_zz": 202,
        "qk_mmd_pauli_xz": 303,
    }
    rng = np.random.default_rng(seed + 10000 + method_seed_offsets[method])

    current_model = initial_model
    current_reference_severity = 0.0

    detector = build_detector(method, args, seed)
    detector, threshold = calibrate_detector(
        detector,
        pools,
        scaler,
        pca,
        severity=current_reference_severity,
        args=args,
        rng=rng,
    )

    alarm_history: list[bool] = []
    cooldown_remaining = 0
    n_adaptations = 0
    false_adaptations = 0
    adaptation_windows: list[int] = []

    window_rows = []
    detector_runtime_sec_total = 0.0
    fit_runtime_sec_total = 0.0

    for t in range(args.post_windows):
        sev_t = progressive_severity(t, args)

        Xw_raw, yw = sample_balanced_from_distribution(
            pools,
            n_per_class=args.window_size // 2,
            severity=sev_t,
            rng=rng,
        )
        Xw = transform_X(Xw_raw, scaler, pca)

        eval_metrics = evaluate_model(current_model, Xw, yw)

        score_start = time.perf_counter()
        score = float(detector.score(Xw))
        detector_runtime_sec_total += time.perf_counter() - score_start

        alarm = bool(score > threshold)
        alarm_history.append(alarm)

        if len(alarm_history) > args.consecutive_k:
            recent = alarm_history[-args.consecutive_k:]
        else:
            recent = alarm_history

        trigger = (
            len(recent) == args.consecutive_k
            and all(recent)
            and cooldown_remaining <= 0
        )

        adapted_now = False

        if trigger:
            n_adaptations += 1
            adaptation_windows.append(t)
            adapted_now = True

            if sev_t < args.false_adaptation_severity_threshold:
                false_adaptations += 1

            Xa_raw, ya = sample_balanced_from_distribution(
                pools,
                n_per_class=args.adapt_size_per_class,
                severity=sev_t,
                rng=rng,
            )
            Xa = transform_X(Xa_raw, scaler, pca)

            fit_start = time.perf_counter()
            current_model = train_svc(Xa, ya, seed + t + 1)
            fit_runtime_sec_total += time.perf_counter() - fit_start

            # Reset detector reference to the current adapted regime.
            detector = build_detector(method, args, seed + t + 1)
            detector, threshold = calibrate_detector(
                detector,
                pools,
                scaler,
                pca,
                severity=sev_t,
                args=args,
                rng=rng,
            )

            alarm_history = []
            cooldown_remaining = args.cooldown_windows

        else:
            cooldown_remaining = max(0, cooldown_remaining - 1)

        no_adapt_ba = no_adapt_window_metrics[t]["balanced_accuracy"]

        window_rows.append(
            {
                "seed": seed,
                "method": method,
                "window_idx": t,
                "severity_t": sev_t,
                "score": score,
                "threshold": threshold,
                "alarm": alarm,
                "trigger": trigger,
                "adapted_now": adapted_now,
                "cooldown_remaining": cooldown_remaining,
                "balanced_accuracy": eval_metrics["balanced_accuracy"],
                "f1": eval_metrics["f1"],
                "no_adapt_balanced_accuracy": no_adapt_ba,
                "gain_vs_no_adapt": eval_metrics["balanced_accuracy"] - no_adapt_ba,
            }
        )

    df = pd.DataFrame(window_rows)

    summary = {
        "seed": seed,
        "method": method,
        "n_windows": args.post_windows,
        "n_adaptations": n_adaptations,
        "false_adaptations": false_adaptations,
        "first_adaptation_window": adaptation_windows[0] if adaptation_windows else np.nan,
        "mean_balanced_accuracy": float(df["balanced_accuracy"].mean()),
        "mean_f1": float(df["f1"].mean()),
        "cumulative_error_area": float((1.0 - df["balanced_accuracy"]).sum()),
        "mean_gain_vs_no_adapt": float(df["gain_vs_no_adapt"].mean()),
        "cumulative_gain_vs_no_adapt": float(df["gain_vs_no_adapt"].sum()),
        "alarm_rate": float(df["alarm"].mean()),
        "trigger_rate": float(df["trigger"].mean()),
        "detector_runtime_sec_total": detector_runtime_sec_total,
        "fit_runtime_sec_total": fit_runtime_sec_total,
    }

    return window_rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--data-ref", type=Path, required=True)
    parser.add_argument("--data-cur", type=Path, required=True)
    parser.add_argument("--label-col", type=str, default="Label")
    parser.add_argument("--outdir", type=Path, required=True)

    parser.add_argument("--seeds", type=str, default="1,2,3")
    parser.add_argument("--methods", type=str, default="mmd_rbf,qk_mmd_zz,qk_mmd_pauli_xz")

    parser.add_argument("--dim", type=int, default=8)
    parser.add_argument("--window-size", type=int, default=128)
    parser.add_argument("--train-size-per-class", type=int, default=2000)
    parser.add_argument("--adapt-size-per-class", type=int, default=512)
    parser.add_argument("--detector-ref-size-per-class", type=int, default=256)

    parser.add_argument("--post-windows", type=int, default=100)
    parser.add_argument("--ramp-windows", type=int, default=80)
    parser.add_argument("--max-severity", type=float, default=1.0)

    parser.add_argument("--calibration-windows", type=int, default=20)
    parser.add_argument("--threshold-quantile", type=float, default=0.95)
    parser.add_argument("--consecutive-k", type=int, default=3)
    parser.add_argument("--cooldown-windows", type=int, default=10)
    parser.add_argument("--false-adaptation-severity-threshold", type=float, default=0.1)

    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-permutations", type=int, default=100)

    parser.add_argument("--q-reps", type=int, default=1)
    parser.add_argument("--q-input-scaling", type=str, default="atan_standard")

    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    seeds = parse_csv_list(args.seeds, int)
    methods = parse_csv_list(args.methods, str)

    X_ref, y_ref = load_binary_dataset(args.data_ref, args.label_col)
    X_cur, y_cur = load_binary_dataset(args.data_cur, args.label_col)

    common_features = sorted(set(X_ref.columns).intersection(set(X_cur.columns)))
    print(f"[ALIGN] common_features={len(common_features)}")

    pools = make_pools(X_ref, y_ref, X_cur, y_cur, common_features)

    all_window_rows = []
    all_summary_rows = []

    for seed in seeds:
        print("=" * 100)
        print(f"[SEED={seed}]")
        print("=" * 100)

        rng = np.random.default_rng(seed)

        X_train_raw, y_train = sample_balanced_from_distribution(
            pools,
            n_per_class=args.train_size_per_class,
            severity=0.0,
            rng=rng,
        )

        scaler, pca, X_train = fit_transformer(X_train_raw, args.dim, seed)

        initial_model = train_svc(X_train, y_train, seed)

        no_adapt_rows = []

        for t in range(args.post_windows):
            sev_t = progressive_severity(t, args)

            Xw_raw, yw = sample_balanced_from_distribution(
                pools,
                n_per_class=args.window_size // 2,
                severity=sev_t,
                rng=rng,
            )
            Xw = transform_X(Xw_raw, scaler, pca)
            metrics = evaluate_model(initial_model, Xw, yw)

            no_adapt_rows.append(
                {
                    "seed": seed,
                    "method": "no_adaptation",
                    "window_idx": t,
                    "severity_t": sev_t,
                    "balanced_accuracy": metrics["balanced_accuracy"],
                    "f1": metrics["f1"],
                    "gain_vs_no_adapt": 0.0,
                }
            )

        no_adapt_df = pd.DataFrame(no_adapt_rows)

        all_window_rows.extend(no_adapt_rows)

        all_summary_rows.append(
            {
                "seed": seed,
                "method": "no_adaptation",
                "n_windows": args.post_windows,
                "n_adaptations": 0,
                "false_adaptations": 0,
                "first_adaptation_window": np.nan,
                "mean_balanced_accuracy": float(no_adapt_df["balanced_accuracy"].mean()),
                "mean_f1": float(no_adapt_df["f1"].mean()),
                "cumulative_error_area": float((1.0 - no_adapt_df["balanced_accuracy"]).sum()),
                "mean_gain_vs_no_adapt": 0.0,
                "cumulative_gain_vs_no_adapt": 0.0,
                "alarm_rate": 0.0,
                "trigger_rate": 0.0,
                "detector_runtime_sec_total": 0.0,
                "fit_runtime_sec_total": 0.0,
            }
        )

        for method in methods:
            print(f"[SEED={seed}][METHOD={method}]")
            rows, summary = run_strategy(
                method=method,
                pools=pools,
                scaler=scaler,
                pca=pca,
                initial_model=initial_model,
                no_adapt_window_metrics=no_adapt_rows,
                args=args,
                seed=seed,
            )

            all_window_rows.extend(rows)
            all_summary_rows.append(summary)

    window_df = pd.DataFrame(all_window_rows)
    summary_df = pd.DataFrame(all_summary_rows)

    window_path = args.outdir / "paper2_progressive_readaptation_window_results.csv"
    by_seed_path = args.outdir / "paper2_progressive_readaptation_by_seed.csv"

    window_df.to_csv(window_path, index=False)
    summary_df.to_csv(by_seed_path, index=False)

    agg = (
        summary_df
        .groupby("method", dropna=False)
        .agg(
            n_seeds=("seed", "nunique"),
            mean_balanced_accuracy=("mean_balanced_accuracy", "mean"),
            std_balanced_accuracy=("mean_balanced_accuracy", "std"),
            cumulative_error_area_mean=("cumulative_error_area", "mean"),
            cumulative_error_area_std=("cumulative_error_area", "std"),
            mean_gain_vs_no_adapt=("mean_gain_vs_no_adapt", "mean"),
            cumulative_gain_vs_no_adapt_mean=("cumulative_gain_vs_no_adapt", "mean"),
            n_adaptations_mean=("n_adaptations", "mean"),
            false_adaptations_mean=("false_adaptations", "mean"),
            first_adaptation_window_mean=("first_adaptation_window", "mean"),
            alarm_rate_mean=("alarm_rate", "mean"),
            trigger_rate_mean=("trigger_rate", "mean"),
            detector_runtime_sec_total_mean=("detector_runtime_sec_total", "mean"),
            fit_runtime_sec_total_mean=("fit_runtime_sec_total", "mean"),
        )
        .reset_index()
        .sort_values("method")
    )

    summary_path = args.outdir / "paper2_progressive_readaptation_summary.csv"
    agg.to_csv(summary_path, index=False)

    print(f"Saved: {window_path}")
    print(f"Saved: {by_seed_path}")
    print(f"Saved: {summary_path}")

    print()
    print("=== PROGRESSIVE READAPTATION SUMMARY ===")
    print(agg.to_string(index=False))


if __name__ == "__main__":
    main()
