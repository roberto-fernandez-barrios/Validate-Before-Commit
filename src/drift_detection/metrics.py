from __future__ import annotations

import numpy as np


def pairwise_sq_dists(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """
    Compute pairwise squared Euclidean distances between rows of X and Y.
    """
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)

    X_norm = np.sum(X * X, axis=1, keepdims=True)
    Y_norm = np.sum(Y * Y, axis=1, keepdims=True).T

    D = X_norm + Y_norm - 2.0 * (X @ Y.T)
    return np.maximum(D, 0.0)


def median_heuristic_gamma(X: np.ndarray, Y: np.ndarray) -> float:
    """
    RBF gamma using the median heuristic over the pooled sample.
    gamma = 1 / (2 * median_distance^2)
    """
    Z = np.vstack([X, Y])
    D = pairwise_sq_dists(Z, Z)

    upper = D[np.triu_indices_from(D, k=1)]
    upper = upper[upper > 0]

    if upper.size == 0:
        return 1.0

    median_sq_dist = float(np.median(upper))

    if median_sq_dist <= 0:
        return 1.0

    return 1.0 / (2.0 * median_sq_dist)


def rbf_kernel(X: np.ndarray, Y: np.ndarray, gamma: float) -> np.ndarray:
    """
    Compute RBF kernel matrix.
    """
    D = pairwise_sq_dists(X, Y)
    return np.exp(-gamma * D)


def mmd2_from_kernel(
    Kxx: np.ndarray,
    Kyy: np.ndarray,
    Kxy: np.ndarray,
    biased: bool = True,
) -> float:
    """
    Compute squared MMD from kernel matrices.

    Biased estimator is more stable for small windows.
    Unbiased estimator removes diagonal terms.
    """
    Kxx = np.asarray(Kxx, dtype=np.float64)
    Kyy = np.asarray(Kyy, dtype=np.float64)
    Kxy = np.asarray(Kxy, dtype=np.float64)

    if biased:
        return float(Kxx.mean() + Kyy.mean() - 2.0 * Kxy.mean())

    m = Kxx.shape[0]
    n = Kyy.shape[0]

    if m < 2 or n < 2:
        raise ValueError("Unbiased MMD requires at least 2 samples per window.")

    xx = (Kxx.sum() - np.trace(Kxx)) / (m * (m - 1))
    yy = (Kyy.sum() - np.trace(Kyy)) / (n * (n - 1))
    xy = Kxy.mean()

    return float(xx + yy - 2.0 * xy)


def mmd2_rbf(
    X: np.ndarray,
    Y: np.ndarray,
    gamma: float | None = None,
    biased: bool = True,
) -> float:
    """
    Compute squared MMD using an RBF kernel.
    """
    if gamma is None:
        gamma = median_heuristic_gamma(X, Y)

    Kxx = rbf_kernel(X, X, gamma)
    Kyy = rbf_kernel(Y, Y, gamma)
    Kxy = rbf_kernel(X, Y, gamma)

    return mmd2_from_kernel(Kxx, Kyy, Kxy, biased=biased)
