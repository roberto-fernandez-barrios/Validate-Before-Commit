from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np

from src.drift_detection.calibration import permutation_calibration
from src.drift_detection.metrics import median_heuristic_gamma, mmd2_rbf


@dataclass
class MmdRbfPrediction:
    detector: str
    score: float
    threshold: float
    p_value: float
    drift_detected: bool
    gamma: float
    runtime_sec: float
    null_scores_mean: float
    null_scores_std: float


class MmdRbfDetector:
    """
    RBF-MMD two-sample drift detector.

    This is the classical kernel baseline that the Quantum Kernel MMD detector
    will later be compared against.
    """

    def __init__(
        self,
        gamma: float | None = None,
        biased: bool = True,
        alpha: float = 0.05,
        n_permutations: int = 100,
        random_state: int = 42,
    ) -> None:
        self.gamma = gamma
        self.biased = biased
        self.alpha = alpha
        self.n_permutations = n_permutations
        self.random_state = random_state
        self.X_ref_: np.ndarray | None = None
        self.gamma_: float | None = None

    def fit(self, X_ref: np.ndarray) -> "MmdRbfDetector":
        X_ref = np.asarray(X_ref, dtype=np.float64)

        if X_ref.ndim != 2:
            raise ValueError("X_ref must be a 2D array.")

        self.X_ref_ = X_ref
        self.gamma_ = self.gamma
        return self

    def _check_fitted(self) -> None:
        if self.X_ref_ is None:
            raise RuntimeError("Detector is not fitted. Call fit(X_ref) first.")

    def _score_between(self, X_a: np.ndarray, X_b: np.ndarray) -> float:
        gamma = self.gamma_
        if gamma is None:
            gamma = median_heuristic_gamma(X_a, X_b)

        return mmd2_rbf(X_a, X_b, gamma=gamma, biased=self.biased)

    def score(self, X_cur: np.ndarray) -> float:
        self._check_fitted()
        assert self.X_ref_ is not None

        return self._score_between(self.X_ref_, X_cur)

    def predict(self, X_cur: np.ndarray) -> MmdRbfPrediction:
        self._check_fitted()
        assert self.X_ref_ is not None

        X_cur = np.asarray(X_cur, dtype=np.float64)

        if self.gamma_ is None:
            self.gamma_ = median_heuristic_gamma(self.X_ref_, X_cur)

        start = time.perf_counter()

        result = permutation_calibration(
            X_ref=self.X_ref_,
            X_cur=X_cur,
            score_fn=lambda A, B: mmd2_rbf(A, B, gamma=self.gamma_, biased=self.biased),
            alpha=self.alpha,
            n_permutations=self.n_permutations,
            random_state=self.random_state,
        )

        runtime_sec = time.perf_counter() - start

        return MmdRbfPrediction(
            detector="mmd_rbf",
            score=result.observed_score,
            threshold=result.threshold,
            p_value=result.p_value,
            drift_detected=result.drift_detected,
            gamma=float(self.gamma_),
            runtime_sec=float(runtime_sec),
            null_scores_mean=result.null_scores_mean,
            null_scores_std=result.null_scores_std,
        )
