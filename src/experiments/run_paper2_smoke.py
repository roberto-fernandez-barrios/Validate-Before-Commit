from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from src.drift_detection.mmd_rbf_detector import MmdRbfDetector
from src.drift_detection.qk_mmd_detector import QkMmdDetector


def parse_csv_ints(value: str) -> list[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_floats(value: str) -> list[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def parse_csv_strings(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def make_windows(
    *,
    rng: np.random.Generator,
    window_size: int,
    dim: int,
    drift_type: str,
    severity: float,
) -> tuple[np.ndarray, np.ndarray, bool]:
    X_ref = rng.normal(loc=0.0, scale=1.0, size=(window_size, dim))
    X_cur = rng.normal(loc=0.0, scale=1.0, size=(window_size, dim))

    if drift_type == "no_drift":
        return X_ref, X_cur, False

    if drift_type == "mean_shift":
        n_shift = max(1, dim // 2)
        X_cur[:, :n_shift] += severity
        return X_ref, X_cur, True

    if drift_type == "gaussian_noise":
        X_cur += rng.normal(loc=0.0, scale=severity, size=X_cur.shape)
        return X_ref, X_cur, True

    if drift_type == "feature_dropout":
        dropout_prob = min(max(severity, 0.0), 1.0)
        mask = rng.random(size=X_cur.shape) < dropout_prob
        X_cur = X_cur.copy()
        X_cur[mask] = 0.0
        return X_ref, X_cur, True

    raise ValueError(f"Unknown drift_type: {drift_type}")


def add_common_row(
    *,
    rows: list[dict[str, object]],
    run_id: int,
    scenario_id: int,
    seed: int,
    dim: int,
    window_size: int,
    drift_type: str,
    severity: float,
    true_drift: bool,
    alpha: float,
    n_permutations: int,
    detector: str,
    score: float,
    threshold: float,
    p_value: float,
    drift_detected: bool,
    runtime_sec: float,
    null_scores_mean: float,
    null_scores_std: float,
    q_feature_map: str = "",
    q_reps: int = 0,
    n_qubits: int = 0,
    gamma: float | str = "",
) -> None:
    rows.append(
        {
            "run_id": run_id,
            "scenario_id": scenario_id,
            "dataset": "synthetic_smoke",
            "protocol": "paper2_smoke",
            "seed": seed,
            "dim": dim,
            "window_size": window_size,
            "detector": detector,
            "q_feature_map": q_feature_map,
            "q_reps": q_reps,
            "n_qubits": n_qubits,
            "drift_type": drift_type,
            "severity": severity,
            "true_drift": int(true_drift),
            "alpha": alpha,
            "n_permutations": n_permutations,
            "score": score,
            "threshold": threshold,
            "p_value": p_value,
            "drift_detected": int(drift_detected),
            "gamma": gamma,
            "runtime_sec": runtime_sec,
            "null_scores_mean": null_scores_mean,
            "null_scores_std": null_scores_std,
        }
    )


def run(args: argparse.Namespace) -> Path:
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []

    dims = parse_csv_ints(args.dims)
    seeds = parse_csv_ints(args.seeds)
    drift_types = parse_csv_strings(args.drifts)
    severities = parse_csv_floats(args.severities)
    detectors = parse_csv_strings(args.detectors)
    q_feature_maps = parse_csv_strings(args.q_feature_maps)

    run_id = 0
    scenario_id = 0

    for seed in seeds:
        for dim in dims:
            for drift_type in drift_types:
                active_severities = [0.0] if drift_type == "no_drift" else severities

                for severity in active_severities:
                    scenario_id += 1
                    rng = np.random.default_rng(seed + 10_000 * scenario_id)

                    X_ref, X_cur, true_drift = make_windows(
                        rng=rng,
                        window_size=args.window_size,
                        dim=dim,
                        drift_type=drift_type,
                        severity=severity,
                    )

                    if "mmd_rbf" in detectors:
                        run_id += 1

                        detector = MmdRbfDetector(
                            gamma=None,
                            biased=True,
                            alpha=args.alpha,
                            n_permutations=args.n_permutations,
                            random_state=seed,
                        )
                        detector.fit(X_ref)
                        pred = detector.predict(X_cur)

                        add_common_row(
                            rows=rows,
                            run_id=run_id,
                            scenario_id=scenario_id,
                            seed=seed,
                            dim=dim,
                            window_size=args.window_size,
                            drift_type=drift_type,
                            severity=severity,
                            true_drift=true_drift,
                            alpha=args.alpha,
                            n_permutations=args.n_permutations,
                            detector=pred.detector,
                            score=pred.score,
                            threshold=pred.threshold,
                            p_value=pred.p_value,
                            drift_detected=pred.drift_detected,
                            runtime_sec=pred.runtime_sec,
                            null_scores_mean=pred.null_scores_mean,
                            null_scores_std=pred.null_scores_std,
                            gamma=pred.gamma,
                        )

                        print(
                            {
                                "run_id": run_id,
                                "detector": pred.detector,
                                "dim": dim,
                                "drift_type": drift_type,
                                "severity": severity,
                                "score": round(pred.score, 6),
                                "threshold": round(pred.threshold, 6),
                                "p_value": round(pred.p_value, 4),
                                "detected": pred.drift_detected,
                                "true_drift": true_drift,
                            }
                        )

                    if "qk_mmd" in detectors:
                        for q_feature_map in q_feature_maps:
                            run_id += 1

                            detector = QkMmdDetector(
                                feature_map=q_feature_map,
                                reps=args.q_reps,
                                biased=True,
                                alpha=args.alpha,
                                n_permutations=args.n_permutations,
                                random_state=seed,
                            )
                            detector.fit(X_ref)
                            pred = detector.predict(X_cur)

                            add_common_row(
                                rows=rows,
                                run_id=run_id,
                                scenario_id=scenario_id,
                                seed=seed,
                                dim=dim,
                                window_size=args.window_size,
                                drift_type=drift_type,
                                severity=severity,
                                true_drift=true_drift,
                                alpha=args.alpha,
                                n_permutations=args.n_permutations,
                                detector=pred.detector,
                                q_feature_map=pred.q_feature_map,
                                q_reps=pred.q_reps,
                                n_qubits=pred.n_qubits,
                                score=pred.score,
                                threshold=pred.threshold,
                                p_value=pred.p_value,
                                drift_detected=pred.drift_detected,
                                runtime_sec=pred.runtime_sec,
                                null_scores_mean=pred.null_scores_mean,
                                null_scores_std=pred.null_scores_std,
                            )

                            print(
                                {
                                    "run_id": run_id,
                                    "detector": pred.detector,
                                    "q_feature_map": pred.q_feature_map,
                                    "dim": dim,
                                    "drift_type": drift_type,
                                    "severity": severity,
                                    "score": round(pred.score, 6),
                                    "threshold": round(pred.threshold, 6),
                                    "p_value": round(pred.p_value, 4),
                                    "detected": pred.drift_detected,
                                    "true_drift": true_drift,
                                }
                            )

    output_path = outdir / "paper2_smoke_results.csv"

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved: {output_path}")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Paper 2 smoke test: classical and quantum MMD drift detectors."
    )

    parser.add_argument("--outdir", type=str, default="results/raw/smoke_001")
    parser.add_argument("--dims", type=str, default="4,6")
    parser.add_argument("--window-size", type=int, default=128)
    parser.add_argument(
        "--drifts",
        type=str,
        default="no_drift,mean_shift,gaussian_noise",
    )
    parser.add_argument("--severities", type=str, default="0.25,0.5,1.0")
    parser.add_argument("--seeds", type=str, default="42")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-permutations", type=int, default=100)

    parser.add_argument(
        "--detectors",
        type=str,
        default="mmd_rbf",
        help="Comma-separated detectors: mmd_rbf,qk_mmd",
    )
    parser.add_argument(
        "--q-feature-maps",
        type=str,
        default="zz",
        help="Comma-separated quantum feature maps: z,zz,pauli_xz",
    )
    parser.add_argument("--q-reps", type=int, default=1)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    run(parser.parse_args())
