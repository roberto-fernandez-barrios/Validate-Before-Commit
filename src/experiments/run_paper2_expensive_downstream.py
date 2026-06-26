from __future__ import annotations

import argparse
import copy
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score
from sklearn.svm import SVC

from src.experiments.run_paper2_progressive_readaptation import (
    build_detector,
    fit_transformer,
    load_binary_dataset,
    parse_csv_list,
    progressive_severity,
    sample_rows,
    transform_X,
)


METHOD_SEED_OFFSETS = {
    "mmd_rbf": 101,
    "qk_mmd_zz": 202,
    "qk_mmd_pauli_xz": 303,
    "ks_max": 404,
    "jsd": 505,
    "energy_distance": 606,
}


def sample_pool_mixture(
    ref_pool: np.ndarray,
    cur_pool: np.ndarray,
    n: int,
    severity: float,
    rng: np.random.Generator,
) -> np.ndarray:
    severity = float(np.clip(severity, 0.0, 1.0))

    n_cur = int(round(n * severity))
    n_ref = n - n_cur

    parts = []

    if n_ref > 0:
        parts.append(sample_rows(ref_pool, n_ref, rng))

    if n_cur > 0:
        parts.append(sample_rows(cur_pool, n_cur, rng))

    X = np.vstack(parts)
    return X[rng.permutation(len(X))]


def sample_binary_distribution(
    ref_benign: np.ndarray,
    ref_attack: np.ndarray,
    cur_benign: np.ndarray,
    cur_attack: np.ndarray,
    n_per_class: int,
    severity: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    X_b = sample_pool_mixture(ref_benign, cur_benign, n_per_class, severity, rng)
    X_a = sample_pool_mixture(ref_attack, cur_attack, n_per_class, severity, rng)

    X = np.vstack([X_b, X_a])
    y = np.concatenate(
        [
            np.zeros(len(X_b), dtype=int),
            np.ones(len(X_a), dtype=int),
        ]
    )

    perm = rng.permutation(len(y))
    return X[perm], y[perm]


def build_downstream_classifier(args, seed: int):
    if args.downstream_model == "svc_rbf":
        return SVC(
            kernel="rbf",
            gamma="scale",
            class_weight="balanced",
            random_state=seed,
        )

    if args.downstream_model == "random_forest":
        max_depth = None if args.rf_max_depth <= 0 else args.rf_max_depth

        return RandomForestClassifier(
            n_estimators=args.rf_n_estimators,
            max_depth=max_depth,
            min_samples_leaf=args.rf_min_samples_leaf,
            class_weight="balanced_subsample",
            n_jobs=args.n_jobs,
            random_state=seed,
        )

    raise ValueError(f"Unknown downstream_model={args.downstream_model}")


def fit_downstream(
    args,
    X_raw: np.ndarray,
    y: np.ndarray,
    scaler,
    pca,
    seed: int,
):
    X = transform_X(X_raw, scaler, pca)
    clf = build_downstream_classifier(args, seed)

    start = time.perf_counter()
    clf.fit(X, y)
    fit_runtime = time.perf_counter() - start

    return clf, fit_runtime


def evaluate_downstream(clf, X_raw: np.ndarray, y: np.ndarray, scaler, pca) -> float:
    X = transform_X(X_raw, scaler, pca)
    pred = clf.predict(X)
    return float(balanced_accuracy_score(y, pred))


def calibrate_detector(
    method: str,
    args,
    seed: int,
    severity: float,
    ref_benign: np.ndarray,
    ref_attack: np.ndarray,
    cur_benign: np.ndarray,
    cur_attack: np.ndarray,
    scaler,
    pca,
    rng: np.random.Generator,
):
    detector = build_detector(method, args, seed)

    n_ref_per_class = max(1, args.detector_ref_size // 2)

    X_ref_raw, _ = sample_binary_distribution(
        ref_benign=ref_benign,
        ref_attack=ref_attack,
        cur_benign=cur_benign,
        cur_attack=cur_attack,
        n_per_class=n_ref_per_class,
        severity=severity,
        rng=rng,
    )

    X_ref = transform_X(X_ref_raw, scaler, pca)
    detector.fit(X_ref)

    scores = []

    for _ in range(args.calibration_windows):
        Xw_raw, _ = sample_binary_distribution(
            ref_benign=ref_benign,
            ref_attack=ref_attack,
            cur_benign=cur_benign,
            cur_attack=cur_attack,
            n_per_class=args.window_size_per_class,
            severity=severity,
            rng=rng,
        )

        Xw = transform_X(Xw_raw, scaler, pca)
        scores.append(float(detector.score(Xw)))

    threshold = float(np.quantile(scores, args.threshold_quantile))

    return detector, threshold


def make_stream_windows(
    args,
    seed: int,
    ref_benign: np.ndarray,
    ref_attack: np.ndarray,
    cur_benign: np.ndarray,
    cur_attack: np.ndarray,
) -> list[dict]:
    rng = np.random.default_rng(seed + 70000)

    windows = []

    for t in range(args.post_windows):
        severity_t = progressive_severity(t, args)

        Xw_raw, yw = sample_binary_distribution(
            ref_benign=ref_benign,
            ref_attack=ref_attack,
            cur_benign=cur_benign,
            cur_attack=cur_attack,
            n_per_class=args.window_size_per_class,
            severity=severity_t,
            rng=rng,
        )

        windows.append(
            {
                "window_idx": t,
                "severity_t": severity_t,
                "X_raw": Xw_raw,
                "y": yw,
            }
        )

    return windows


def run_no_adaptation(
    args,
    seed: int,
    initial_clf,
    windows: list[dict],
    scaler,
    pca,
) -> tuple[list[dict], dict, np.ndarray]:
    rows = []
    ba_values = []

    for item in windows:
        ba = evaluate_downstream(
            clf=initial_clf,
            X_raw=item["X_raw"],
            y=item["y"],
            scaler=scaler,
            pca=pca,
        )

        ba_values.append(ba)

        rows.append(
            {
                "seed": seed,
                "scenario": args.scenario,
                "downstream_model": args.downstream_model,
                "method": "no_adaptation",
                "window_idx": item["window_idx"],
                "severity_t": item["severity_t"],
                "balanced_accuracy": ba,
                "score": np.nan,
                "threshold": np.nan,
                "alarm": False,
                "trigger": False,
                "n_adaptations_so_far": 0,
            }
        )

    ba_arr = np.asarray(ba_values, dtype=float)

    summary = {
        "seed": seed,
        "scenario": args.scenario,
        "downstream_model": args.downstream_model,
        "method": "no_adaptation",
        "mean_balanced_accuracy": float(ba_arr.mean()),
        "cumulative_error_area": float(np.sum(1.0 - ba_arr)),
        "cumulative_gain_vs_no_adapt": 0.0,
        "n_adaptations": 0,
        "detector_runtime_sec_total": 0.0,
        "fit_runtime_sec_total": 0.0,
        "total_operational_runtime_sec": 0.0,
        "initial_fit_runtime_sec": np.nan,
        "first_adaptation_window": np.nan,
        "alarm_rate": 0.0,
        "trigger_rate": 0.0,
    }

    return rows, summary, ba_arr


def run_detector_strategy(
    method: str,
    args,
    seed: int,
    initial_clf,
    no_adapt_ba: np.ndarray,
    windows: list[dict],
    ref_benign: np.ndarray,
    ref_attack: np.ndarray,
    cur_benign: np.ndarray,
    cur_attack: np.ndarray,
    scaler,
    pca,
) -> tuple[list[dict], dict]:
    method_seed = seed + 90000 + METHOD_SEED_OFFSETS[method]
    rng = np.random.default_rng(method_seed)

    clf = copy.deepcopy(initial_clf)

    detector, threshold = calibrate_detector(
        method=method,
        args=args,
        seed=method_seed,
        severity=0.0,
        ref_benign=ref_benign,
        ref_attack=ref_attack,
        cur_benign=cur_benign,
        cur_attack=cur_attack,
        scaler=scaler,
        pca=pca,
        rng=rng,
    )

    consecutive_alarm_count = 0
    cooldown_remaining = 0

    n_adaptations = 0
    first_adaptation_window = None

    detector_runtime_sec_total = 0.0
    fit_runtime_sec_total = 0.0

    rows = []
    ba_values = []

    current_reference_severity = 0.0

    for item in windows:
        t = item["window_idx"]
        severity_t = item["severity_t"]

        # Evaluate with the model available before reacting to this window.
        ba = evaluate_downstream(
            clf=clf,
            X_raw=item["X_raw"],
            y=item["y"],
            scaler=scaler,
            pca=pca,
        )
        ba_values.append(ba)

        Xw = transform_X(item["X_raw"], scaler, pca)

        start = time.perf_counter()
        score = float(detector.score(Xw))
        detector_runtime_sec_total += time.perf_counter() - start

        alarm = bool(score > threshold)

        if alarm:
            consecutive_alarm_count += 1
        else:
            consecutive_alarm_count = 0

        trigger = False

        if cooldown_remaining > 0:
            cooldown_remaining -= 1
        elif consecutive_alarm_count >= args.consecutive_k:
            trigger = True
            n_adaptations += 1

            if first_adaptation_window is None:
                first_adaptation_window = t

            # Adapt for following windows.
            X_adapt_raw, y_adapt = sample_binary_distribution(
                ref_benign=ref_benign,
                ref_attack=ref_attack,
                cur_benign=cur_benign,
                cur_attack=cur_attack,
                n_per_class=args.train_size_per_class,
                severity=severity_t,
                rng=rng,
            )

            clf, fit_runtime = fit_downstream(
                args=args,
                X_raw=X_adapt_raw,
                y=y_adapt,
                scaler=scaler,
                pca=pca,
                seed=method_seed + t + 1,
            )

            fit_runtime_sec_total += fit_runtime
            current_reference_severity = severity_t

            detector, threshold = calibrate_detector(
                method=method,
                args=args,
                seed=method_seed + t + 1,
                severity=current_reference_severity,
                ref_benign=ref_benign,
                ref_attack=ref_attack,
                cur_benign=cur_benign,
                cur_attack=cur_attack,
                scaler=scaler,
                pca=pca,
                rng=rng,
            )

            consecutive_alarm_count = 0
            cooldown_remaining = args.cooldown_windows

        rows.append(
            {
                "seed": seed,
                "scenario": args.scenario,
                "downstream_model": args.downstream_model,
                "method": method,
                "window_idx": t,
                "severity_t": severity_t,
                "balanced_accuracy": ba,
                "score": score,
                "threshold": threshold,
                "alarm": alarm,
                "trigger": trigger,
                "n_adaptations_so_far": n_adaptations,
            }
        )

    ba_arr = np.asarray(ba_values, dtype=float)

    alarm_rate = float(np.mean([r["alarm"] for r in rows]))
    trigger_rate = float(np.mean([r["trigger"] for r in rows]))

    cumulative_gain_vs_no_adapt = float(np.sum(ba_arr - no_adapt_ba))

    summary = {
        "seed": seed,
        "scenario": args.scenario,
        "downstream_model": args.downstream_model,
        "method": method,
        "mean_balanced_accuracy": float(ba_arr.mean()),
        "cumulative_error_area": float(np.sum(1.0 - ba_arr)),
        "cumulative_gain_vs_no_adapt": cumulative_gain_vs_no_adapt,
        "n_adaptations": n_adaptations,
        "detector_runtime_sec_total": detector_runtime_sec_total,
        "fit_runtime_sec_total": fit_runtime_sec_total,
        "total_operational_runtime_sec": detector_runtime_sec_total + fit_runtime_sec_total,
        "initial_fit_runtime_sec": np.nan,
        "first_adaptation_window": np.nan if first_adaptation_window is None else first_adaptation_window,
        "alarm_rate": alarm_rate,
        "trigger_rate": trigger_rate,
    }

    return rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--data-ref", type=Path, required=True)
    parser.add_argument("--data-cur", type=Path, required=True)
    parser.add_argument("--label-col", type=str, default="Label")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--scenario", type=str, required=True)

    parser.add_argument("--seeds", type=str, default="1,2,3")
    parser.add_argument("--methods", type=str, default="energy_distance,mmd_rbf,qk_mmd_zz")

    parser.add_argument("--downstream-model", type=str, default="random_forest", choices=["svc_rbf", "random_forest"])

    parser.add_argument("--dim", type=int, default=8)
    parser.add_argument("--train-size-per-class", type=int, default=2000)
    parser.add_argument("--window-size-per-class", type=int, default=128)
    parser.add_argument("--detector-ref-size", type=int, default=512)

    parser.add_argument("--post-windows", type=int, default=100)
    parser.add_argument("--ramp-windows", type=int, default=100)
    parser.add_argument("--max-severity", type=float, default=1.0)

    parser.add_argument("--calibration-windows", type=int, default=30)
    parser.add_argument("--threshold-quantile", type=float, default=0.95)
    parser.add_argument("--consecutive-k", type=int, default=2)
    parser.add_argument("--cooldown-windows", type=int, default=5)

    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-permutations", type=int, default=100)

    parser.add_argument("--q-reps", type=int, default=2)
    parser.add_argument("--q-input-scaling", type=str, default="atan_standard", choices=["none", "atan_standard"])

    parser.add_argument("--ks-reduction", type=str, default="max", choices=["max", "mean"])
    parser.add_argument("--jsd-bins", type=int, default=20)
    parser.add_argument("--energy-reduction", type=str, default="mean", choices=["mean", "max"])

    parser.add_argument("--rf-n-estimators", type=int, default=500)
    parser.add_argument("--rf-max-depth", type=int, default=0)
    parser.add_argument("--rf-min-samples-leaf", type=int, default=1)
    parser.add_argument("--n-jobs", type=int, default=-1)

    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    seeds = parse_csv_list(args.seeds, int)
    methods = parse_csv_list(args.methods, str)

    X_ref_df, y_ref = load_binary_dataset(args.data_ref, args.label_col)
    X_cur_df, y_cur = load_binary_dataset(args.data_cur, args.label_col)

    common_features = sorted(set(X_ref_df.columns).intersection(set(X_cur_df.columns)))

    print(f"[ALIGN] common_features={len(common_features)}")

    X_ref = X_ref_df[common_features].to_numpy(dtype=float)
    X_cur = X_cur_df[common_features].to_numpy(dtype=float)

    y_ref_arr = y_ref.to_numpy()
    y_cur_arr = y_cur.to_numpy()

    ref_benign = X_ref[y_ref_arr == 0]
    ref_attack = X_ref[y_ref_arr == 1]
    cur_benign = X_cur[y_cur_arr == 0]
    cur_attack = X_cur[y_cur_arr == 1]

    print(
        f"[POOLS] ref_benign={len(ref_benign)} ref_attack={len(ref_attack)} "
        f"cur_benign={len(cur_benign)} cur_attack={len(cur_attack)}"
    )

    if min(len(ref_benign), len(ref_attack), len(cur_benign), len(cur_attack)) == 0:
        raise ValueError("One or more class pools are empty.")

    all_windows = []
    all_summary = []

    for seed in seeds:
        print("=" * 100)
        print(f"[SEED={seed}]")
        print("=" * 100)

        rng = np.random.default_rng(seed + 50000)

        X_initial_raw, y_initial = sample_binary_distribution(
            ref_benign=ref_benign,
            ref_attack=ref_attack,
            cur_benign=cur_benign,
            cur_attack=cur_attack,
            n_per_class=args.train_size_per_class,
            severity=0.0,
            rng=rng,
        )

        scaler, pca, _ = fit_transformer(X_initial_raw, dim=args.dim, seed=seed)

        initial_clf, initial_fit_runtime = fit_downstream(
            args=args,
            X_raw=X_initial_raw,
            y=y_initial,
            scaler=scaler,
            pca=pca,
            seed=seed,
        )

        print(f"[SEED={seed}] initial_fit_runtime_sec={initial_fit_runtime:.6f}")

        windows = make_stream_windows(
            args=args,
            seed=seed,
            ref_benign=ref_benign,
            ref_attack=ref_attack,
            cur_benign=cur_benign,
            cur_attack=cur_attack,
        )

        rows, summary, no_adapt_ba = run_no_adaptation(
            args=args,
            seed=seed,
            initial_clf=initial_clf,
            windows=windows,
            scaler=scaler,
            pca=pca,
        )

        summary["initial_fit_runtime_sec"] = initial_fit_runtime

        all_windows.extend(rows)
        all_summary.append(summary)

        for method in methods:
            print(f"[SEED={seed}][METHOD={method}]")

            rows, summary = run_detector_strategy(
                method=method,
                args=args,
                seed=seed,
                initial_clf=initial_clf,
                no_adapt_ba=no_adapt_ba,
                windows=windows,
                ref_benign=ref_benign,
                ref_attack=ref_attack,
                cur_benign=cur_benign,
                cur_attack=cur_attack,
                scaler=scaler,
                pca=pca,
            )

            summary["initial_fit_runtime_sec"] = initial_fit_runtime

            all_windows.extend(rows)
            all_summary.append(summary)

    window_df = pd.DataFrame(all_windows)
    by_seed_df = pd.DataFrame(all_summary)

    agg = (
        by_seed_df.groupby(["scenario", "downstream_model", "method"], dropna=False)
        .agg(
            n_seeds=("seed", "nunique"),
            mean_balanced_accuracy=("mean_balanced_accuracy", "mean"),
            std_balanced_accuracy=("mean_balanced_accuracy", "std"),
            cumulative_error_area_mean=("cumulative_error_area", "mean"),
            cumulative_error_area_std=("cumulative_error_area", "std"),
            cumulative_gain_vs_no_adapt_mean=("cumulative_gain_vs_no_adapt", "mean"),
            cumulative_gain_vs_no_adapt_std=("cumulative_gain_vs_no_adapt", "std"),
            n_adaptations_mean=("n_adaptations", "mean"),
            n_adaptations_std=("n_adaptations", "std"),
            detector_runtime_sec_total_mean=("detector_runtime_sec_total", "mean"),
            fit_runtime_sec_total_mean=("fit_runtime_sec_total", "mean"),
            total_operational_runtime_sec_mean=("total_operational_runtime_sec", "mean"),
            initial_fit_runtime_sec_mean=("initial_fit_runtime_sec", "mean"),
            first_adaptation_window_mean=("first_adaptation_window", "mean"),
            alarm_rate_mean=("alarm_rate", "mean"),
            trigger_rate_mean=("trigger_rate", "mean"),
        )
        .reset_index()
        .sort_values(["scenario", "downstream_model", "cumulative_error_area_mean"])
    )

    window_path = args.outdir / "paper2_expensive_downstream_window_results.csv"
    by_seed_path = args.outdir / "paper2_expensive_downstream_by_seed.csv"
    summary_path = args.outdir / "paper2_expensive_downstream_summary.csv"

    window_df.to_csv(window_path, index=False)
    by_seed_df.to_csv(by_seed_path, index=False)
    agg.to_csv(summary_path, index=False)

    print(f"Saved: {window_path}")
    print(f"Saved: {by_seed_path}")
    print(f"Saved: {summary_path}")

    print()
    print("=== EXPENSIVE DOWNSTREAM SUMMARY ===")
    print(agg.to_string(index=False))


if __name__ == "__main__":
    main()
