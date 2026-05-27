from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler

from src.drift_detection.mmd_rbf_detector import MmdRbfDetector
from src.drift_detection.qk_mmd_detector import QkMmdDetector


def parse_csv_list(value: str, cast=str):
    return [cast(x.strip()) for x in value.split(",") if x.strip()]


def parse_label_values(value: str) -> set[str] | None:
    values = {x.strip() for x in value.split(",") if x.strip()}
    return values or None


def load_numeric_csv(
    path: Path,
    label_col: str | None,
    max_rows: int | None,
    label_values: set[str] | None = None,
) -> pd.DataFrame:
    df = pd.read_csv(path, nrows=max_rows)
    df.columns = [str(c).strip() for c in df.columns]

    if label_values is not None:
        if not label_col:
            raise ValueError("--label-values-* requires --label-col")
        if label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found in {path}")

        before = len(df)
        labels = df[label_col].astype(str).str.strip()
        df = df[labels.isin(label_values)].copy()
        after = len(df)

        print(f"[FILTER] {path.name}: {label_col} in {sorted(label_values)} -> {after}/{before} rows")

        if after == 0:
            raise ValueError(f"No rows left after filtering {path} with labels {sorted(label_values)}")

    if label_col and label_col in df.columns:
        df = df.drop(columns=[label_col])

    df = df.replace([np.inf, -np.inf], np.nan)

    numeric = df.select_dtypes(include=[np.number]).copy()
    numeric = numeric.dropna(axis=1, how="all")
    numeric = numeric.fillna(numeric.median(numeric_only=True))
    numeric = numeric.fillna(0.0)

    # Remove constant columns; they add noise and can break scaling.
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


def sample_two_windows(X: np.ndarray, size: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    if len(X) < 2 * size:
        raise ValueError(f"Need at least {2 * size} rows for no_drift split, available {len(X)}")
    idx = rng.choice(len(X), size=2 * size, replace=False)
    return X[idx[:size]], X[idx[size:]]


def reduce_dim_reference_fitted(
    X_ref: np.ndarray,
    X_cur: np.ndarray,
    dim: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
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


def prediction_to_row(
    *,
    run_id: int,
    dataset: str,
    protocol: str,
    seed: int,
    dim: int,
    window_size: int,
    alpha: float,
    n_permutations: int,
    drift_type: str,
    severity: float,
    true_drift: bool,
    pred,
) -> dict:
    return {
        "dataset": dataset,
        "protocol": protocol,
        "run_id": run_id,
        "seed": seed,
        "detector": pred.detector,
        "q_feature_map": getattr(pred, "q_feature_map", ""),
        "q_reps": getattr(pred, "q_reps", 0),
        "q_input_scaling": getattr(pred, "q_input_scaling", ""),
        "drift_type": drift_type,
        "severity": severity,
        "dim": dim,
        "window_size": window_size,
        "alpha": alpha,
        "n_permutations": n_permutations,
        "score": float(pred.score),
        "threshold": float(pred.threshold),
        "p_value": float(pred.p_value),
        "drift_detected": bool(pred.drift_detected),
        "detected": bool(pred.drift_detected),
        "true_drift": bool(true_drift),
        "runtime_sec": float(pred.runtime_sec),
        "null_scores_mean": float(pred.null_scores_mean),
        "null_scores_std": float(pred.null_scores_std),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paper 2 real-dataset drift benchmark for classical MMD and QK-MMD."
    )

    parser.add_argument("--data-ref", required=True)
    parser.add_argument("--data-cur", required=True)
    parser.add_argument("--label-col", default="Label")
    parser.add_argument("--label-values-ref", default="")
    parser.add_argument("--label-values-cur", default="")
    parser.add_argument("--dataset", default="cicids2017")
    parser.add_argument("--outdir", default="results/raw/paper2_cicids_smoke_001")

    parser.add_argument("--dims", default="4,6,8")
    parser.add_argument("--window-size", type=int, default=128)
    parser.add_argument("--seeds", default="1,2,3,4,5")
    parser.add_argument("--max-rows", type=int, default=200000)

    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-permutations", type=int, default=200)
    parser.add_argument("--detectors", default="mmd_rbf,qk_mmd")
    parser.add_argument("--q-feature-maps", default="z,zz,pauli_xz")
    parser.add_argument("--q-reps", type=int, default=1)
    parser.add_argument("--q-input-scaling", choices=["none", "atan_standard"], default="atan_standard")

    args = parser.parse_args()

    data_ref_path = Path(args.data_ref)
    data_cur_path = Path(args.data_cur)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    dims = parse_csv_list(args.dims, int)
    seeds = parse_csv_list(args.seeds, int)
    detectors = parse_csv_list(args.detectors, str)
    q_feature_maps = parse_csv_list(args.q_feature_maps, str)
    label_values_ref = parse_label_values(args.label_values_ref)
    label_values_cur = parse_label_values(args.label_values_cur)

    print(f"[LOAD] reference: {data_ref_path}")
    df_ref = load_numeric_csv(data_ref_path, args.label_col, args.max_rows, label_values_ref)

    print(f"[LOAD] current:   {data_cur_path}")
    df_cur = load_numeric_csv(data_cur_path, args.label_col, args.max_rows, label_values_cur)

    df_ref, df_cur = align_columns(df_ref, df_cur)

    X_ref_pool = df_ref.to_numpy(dtype=np.float64)
    X_cur_pool = df_cur.to_numpy(dtype=np.float64)

    print(f"[DATA] ref={X_ref_pool.shape} cur={X_cur_pool.shape} common_features={df_ref.shape[1]}")

    rows = []
    run_id = 0

    for seed in seeds:
        rng = np.random.default_rng(seed)

        for dim in dims:
            cases = []

            # Control: same dataset, two independent windows.
            X_ref_nd, X_cur_nd = sample_two_windows(X_ref_pool, args.window_size, rng)
            cases.append(("no_drift", 0.0, False, X_ref_nd, X_cur_nd))

            # Real distribution shift: reference day vs current day.
            X_ref_nat = sample_window(X_ref_pool, args.window_size, rng)
            X_cur_nat = sample_window(X_cur_pool, args.window_size, rng)
            cases.append(("natural_shift", 1.0, True, X_ref_nat, X_cur_nat))

            for drift_type, severity, true_drift, X_ref_raw, X_cur_raw in cases:
                X_ref, X_cur = reduce_dim_reference_fitted(
                    X_ref_raw,
                    X_cur_raw,
                    dim=dim,
                    seed=seed,
                )

                if "mmd_rbf" in detectors:
                    detector = MmdRbfDetector(
                        alpha=args.alpha,
                        n_permutations=args.n_permutations,
                        random_state=seed,
                    )
                    pred = detector.fit(X_ref).predict(X_cur)

                    run_id += 1
                    row = prediction_to_row(
                        run_id=run_id,
                        dataset=args.dataset,
                        protocol="paper2_dataset",
                        seed=seed,
                        dim=X_ref.shape[1],
                        window_size=args.window_size,
                        alpha=args.alpha,
                        n_permutations=args.n_permutations,
                        drift_type=drift_type,
                        severity=severity,
                        true_drift=true_drift,
                        pred=pred,
                    )
                    rows.append(row)
                    print({
                        "run_id": run_id,
                        "detector": row["detector"],
                        "dim": row["dim"],
                        "drift_type": drift_type,
                        "score": round(row["score"], 6),
                        "threshold": round(row["threshold"], 6),
                        "p_value": round(row["p_value"], 4),
                        "detected": row["detected"],
                        "true_drift": true_drift,
                    })

                if "qk_mmd" in detectors:
                    for fmap in q_feature_maps:
                        detector = QkMmdDetector(
                            feature_map=fmap,
                            reps=args.q_reps,
                            alpha=args.alpha,
                            n_permutations=args.n_permutations,
                            random_state=seed,
                            input_scaling=args.q_input_scaling,
                        )
                        pred = detector.fit(X_ref).predict(X_cur)

                        run_id += 1
                        row = prediction_to_row(
                            run_id=run_id,
                            dataset=args.dataset,
                            protocol="paper2_dataset",
                            seed=seed,
                            dim=X_ref.shape[1],
                            window_size=args.window_size,
                            alpha=args.alpha,
                            n_permutations=args.n_permutations,
                            drift_type=drift_type,
                            severity=severity,
                            true_drift=true_drift,
                            pred=pred,
                        )
                        rows.append(row)
                        print({
                            "run_id": run_id,
                            "detector": row["detector"],
                            "q_feature_map": row["q_feature_map"],
                            "dim": row["dim"],
                            "drift_type": drift_type,
                            "score": round(row["score"], 6),
                            "threshold": round(row["threshold"], 6),
                            "p_value": round(row["p_value"], 4),
                            "detected": row["detected"],
                            "true_drift": true_drift,
                        })

    out = outdir / "paper2_dataset_results.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
