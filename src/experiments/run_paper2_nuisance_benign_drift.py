from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

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


def sample_benign_from_distribution(
    ref_benign: np.ndarray,
    cur_benign: np.ndarray,
    n: int,
    severity: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Benign-only mixture. severity=0 uses reference benign; severity=1 uses current benign."""
    severity = float(np.clip(severity, 0.0, 1.0))

    n_cur = int(round(n * severity))
    n_ref = n - n_cur

    parts = []

    if n_ref > 0:
        parts.append(sample_rows(ref_benign, n_ref, rng))

    if n_cur > 0:
        parts.append(sample_rows(cur_benign, n_cur, rng))

    X = np.vstack(parts)
    return X[rng.permutation(len(X))]


def calibrate_detector_benign(
    detector,
    ref_benign: np.ndarray,
    cur_benign: np.ndarray,
    scaler,
    pca,
    severity: float,
    args,
    rng: np.random.Generator,
):
    X_ref_raw = sample_benign_from_distribution(
        ref_benign=ref_benign,
        cur_benign=cur_benign,
        n=args.detector_ref_size,
        severity=severity,
        rng=rng,
    )
    X_ref = transform_X(X_ref_raw, scaler, pca)

    detector.fit(X_ref)

    scores = []

    for _ in range(args.calibration_windows):
        Xw_raw = sample_benign_from_distribution(
            ref_benign=ref_benign,
            cur_benign=cur_benign,
            n=args.window_size,
            severity=severity,
            rng=rng,
        )
        Xw = transform_X(Xw_raw, scaler, pca)
        scores.append(float(detector.score(Xw)))

    threshold = float(np.quantile(scores, args.threshold_quantile))

    return detector, threshold


def run_nuisance_strategy(
    method: str,
    ref_benign: np.ndarray,
    ref_attack: np.ndarray,
    cur_benign: np.ndarray,
    args,
    seed: int,
) -> tuple[list[dict], dict]:
    method_seed = seed + 10000 + METHOD_SEED_OFFSETS[method]
    rng = np.random.default_rng(method_seed)

    # Fit the same kind of representation as the downstream IDS setting:
    # reference benign + reference attack. The nuisance stream itself is benign-only.
    X_train_raw = np.vstack(
        [
            sample_rows(ref_benign, args.train_size_per_class, rng),
            sample_rows(ref_attack, args.train_size_per_class, rng),
        ]
    )

    scaler, pca, _ = fit_transformer(X_train_raw, dim=args.dim, seed=seed)

    current_reference_severity = 0.0

    detector = build_detector(method, args, seed)
    detector, threshold = calibrate_detector_benign(
        detector=detector,
        ref_benign=ref_benign,
        cur_benign=cur_benign,
        scaler=scaler,
        pca=pca,
        severity=current_reference_severity,
        args=args,
        rng=rng,
    )

    consecutive_alarm_count = 0
    cooldown_remaining = 0
    n_nuisance_triggers = 0
    first_trigger_window = None

    detector_runtime_sec_total = 0.0
    window_rows = []

    for t in range(args.post_windows):
        sev_t = progressive_severity(t, args)

        Xw_raw = sample_benign_from_distribution(
            ref_benign=ref_benign,
            cur_benign=cur_benign,
            n=args.window_size,
            severity=sev_t,
            rng=rng,
        )
        Xw = transform_X(Xw_raw, scaler, pca)

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
            n_nuisance_triggers += 1

            if first_trigger_window is None:
                first_trigger_window = t

            # Operationally, this represents a non-adversarial nuisance trigger/reference update
            # caused by benign nuisance drift. We reset the detector to the current
            # benign regime exactly as an adaptive monitor would do.
            current_reference_severity = sev_t

            detector = build_detector(method, args, seed + t + 1)
            detector, threshold = calibrate_detector_benign(
                detector=detector,
                ref_benign=ref_benign,
                cur_benign=cur_benign,
                scaler=scaler,
                pca=pca,
                severity=current_reference_severity,
                args=args,
                rng=rng,
            )

            consecutive_alarm_count = 0
            cooldown_remaining = args.cooldown_windows

        window_rows.append(
            {
                "seed": seed,
                "scenario": args.scenario,
                "method": method,
                "window_idx": t,
                "severity_t": sev_t,
                "current_reference_severity": current_reference_severity,
                "score": score,
                "threshold": threshold,
                "alarm": alarm,
                "trigger": trigger,
                "consecutive_alarm_count": consecutive_alarm_count,
                "cooldown_remaining": cooldown_remaining,
            }
        )

    window_df = pd.DataFrame(window_rows)

    summary = {
        "seed": seed,
        "scenario": args.scenario,
        "method": method,
        "n_windows": args.post_windows,
        "n_nuisance_triggers": n_nuisance_triggers,
        "first_trigger_window": np.nan if first_trigger_window is None else first_trigger_window,
        "nuisance_alarm_rate": float(window_df["alarm"].mean()),
        "nuisance_trigger_rate": float(window_df["trigger"].mean()),
        "detector_runtime_sec_total": detector_runtime_sec_total,
        "final_reference_severity": current_reference_severity,
    }

    return window_rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--data-ref", type=Path, required=True)
    parser.add_argument("--data-cur", type=Path, required=True)
    parser.add_argument("--label-col", type=str, default="Label")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--scenario", type=str, required=True)

    parser.add_argument("--seeds", type=str, default="1,2,3")
    parser.add_argument(
        "--methods",
        type=str,
        default="mmd_rbf,ks_max,jsd,energy_distance,qk_mmd_zz,qk_mmd_pauli_xz",
    )

    parser.add_argument("--dim", type=int, default=8)
    parser.add_argument("--window-size", type=int, default=256)
    parser.add_argument("--train-size-per-class", type=int, default=2000)
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

    parser.add_argument("--nodrift-ref-fraction", type=float, default=0.5)
    parser.add_argument("--nodrift-split-seed", type=int, default=12345)

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

    print(
        f"[POOLS] ref_benign={len(ref_benign)} ref_attack={len(ref_attack)} "
        f"cur_benign={len(cur_benign)}"
    )

    same_source = args.data_ref.resolve() == args.data_cur.resolve()
    if same_source:
        split_rng = np.random.default_rng(args.nodrift_split_seed)
        perm = split_rng.permutation(len(ref_benign))

        cut = int(round(len(ref_benign) * args.nodrift_ref_fraction))
        cut = min(max(cut, 1), len(ref_benign) - 1)

        ref_benign_full = ref_benign
        ref_benign = ref_benign_full[perm[:cut]]
        cur_benign = ref_benign_full[perm[cut:]]

        print(
            f"[NO-DRIFT SPLIT] ref_benign_pool={len(ref_benign)} "
            f"stream_benign_pool={len(cur_benign)} "
            f"split_seed={args.nodrift_split_seed}"
        )

    if len(ref_benign) == 0 or len(ref_attack) == 0 or len(cur_benign) == 0:
        raise ValueError("Not enough samples to run nuisance benign drift experiment.")

    all_windows = []
    all_summary = []

    for seed in seeds:
        print("=" * 100)
        print(f"[SEED={seed}]")
        print("=" * 100)

        for method in methods:
            print(f"[SEED={seed}][METHOD={method}]")

            rows, summary = run_nuisance_strategy(
                method=method,
                ref_benign=ref_benign,
                ref_attack=ref_attack,
                cur_benign=cur_benign,
                args=args,
                seed=seed,
            )

            all_windows.extend(rows)
            all_summary.append(summary)

    window_df = pd.DataFrame(all_windows)
    by_seed_df = pd.DataFrame(all_summary)

    agg = (
        by_seed_df.groupby(["scenario", "method"], dropna=False)
        .agg(
            n_seeds=("seed", "nunique"),
            n_nuisance_triggers_mean=("n_nuisance_triggers", "mean"),
            n_nuisance_triggers_std=("n_nuisance_triggers", "std"),
            nuisance_alarm_rate_mean=("nuisance_alarm_rate", "mean"),
            nuisance_alarm_rate_std=("nuisance_alarm_rate", "std"),
            nuisance_trigger_rate_mean=("nuisance_trigger_rate", "mean"),
            nuisance_trigger_rate_std=("nuisance_trigger_rate", "std"),
            first_trigger_window_mean=("first_trigger_window", "mean"),
            detector_runtime_sec_total_mean=("detector_runtime_sec_total", "mean"),
            final_reference_severity_mean=("final_reference_severity", "mean"),
        )
        .reset_index()
        .sort_values(["scenario", "n_nuisance_triggers_mean", "nuisance_trigger_rate_mean"])
    )

    window_path = args.outdir / "paper2_nuisance_benign_window_results.csv"
    by_seed_path = args.outdir / "paper2_nuisance_benign_by_seed.csv"
    summary_path = args.outdir / "paper2_nuisance_benign_summary.csv"

    window_df.to_csv(window_path, index=False)
    by_seed_df.to_csv(by_seed_path, index=False)
    agg.to_csv(summary_path, index=False)

    print(f"Saved: {window_path}")
    print(f"Saved: {by_seed_path}")
    print(f"Saved: {summary_path}")

    print()
    print("=== NUISANCE BENIGN DRIFT SUMMARY ===")
    print(agg.to_string(index=False))


if __name__ == "__main__":
    main()
