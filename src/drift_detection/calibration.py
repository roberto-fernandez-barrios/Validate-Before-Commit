from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class PermutationCalibrationResult:
    observed_score: float
    threshold: float
    p_value: float
    drift_detected: bool
    null_scores_mean: float
    null_scores_std: float
    n_permutations: int
    alpha: float


def permutation_calibration(
    X_ref: np.ndarray,
    X_cur: np.ndarray,
    score_fn: Callable[[np.ndarray, np.ndarray], float],
    alpha: float = 0.05,
    n_permutations: int = 100,
    random_state: int = 42,
) -> PermutationCalibrationResult:
    """
    Calibrate a two-sample drift statistic using permutation testing.

    H0: X_ref and X_cur come from the same distribution.
    Drift is detected if observed_score > threshold.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1).")

    X_ref = np.asarray(X_ref, dtype=np.float64)
    X_cur = np.asarray(X_cur, dtype=np.float64)

    if X_ref.ndim != 2 or X_cur.ndim != 2:
        raise ValueError("X_ref and X_cur must be 2D arrays.")

    if X_ref.shape[1] != X_cur.shape[1]:
        raise ValueError("X_ref and X_cur must have the same number of features.")

    rng = np.random.default_rng(random_state)

    n_ref = X_ref.shape[0]
    Z = np.vstack([X_ref, X_cur])

    observed_score = float(score_fn(X_ref, X_cur))
    null_scores = np.empty(n_permutations, dtype=np.float64)

    for i in range(n_permutations):
        perm = rng.permutation(Z.shape[0])
        Xp = Z[perm[:n_ref]]
        Yp = Z[perm[n_ref:]]
        null_scores[i] = float(score_fn(Xp, Yp))

    threshold = float(np.quantile(null_scores, 1.0 - alpha))

    # Conservative permutation p-value.
    p_value = float((1.0 + np.sum(null_scores >= observed_score)) / (n_permutations + 1.0))

    return PermutationCalibrationResult(
        observed_score=observed_score,
        threshold=threshold,
        p_value=p_value,
        drift_detected=bool(observed_score > threshold),
        null_scores_mean=float(null_scores.mean()),
        null_scores_std=float(null_scores.std(ddof=1)) if n_permutations > 1 else 0.0,
        n_permutations=int(n_permutations),
        alpha=float(alpha),
    )
