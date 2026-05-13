from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np

from src.drift_detection.calibration import permutation_calibration
from src.drift_detection.quantum_kernels import mmd2_quantum


@dataclass
class QkMmdPrediction:
    detector: str
    score: float
    threshold: float
    p_value: float
    drift_detected: bool
    q_feature_map: str
    q_reps: int
    n_qubits: int
    runtime_sec: float
    null_scores_mean: float
    null_scores_std: float


class QkMmdDetector:
    """
    Quantum Kernel MMD drift detector.

    First implementation uses a lightweight NumPy statevector feature map.
    Later, this can be validated against a Qiskit implementation.
    """

    def __init__(
        self,
        feature_map: str = "zz",
        reps: int = 1,
        biased: bool = True,
        alpha: float = 0.05,
        n_permutations: int = 100,
        random_state: int = 42,
    ) -> None:
        self.feature_map = feature_map
        self.reps = reps
        self.biased = biased
        self.alpha = alpha
        self.n_permutations = n_permutations
        self.random_state = random_state
        self.X_ref_: np.ndarray | None = None

    def fit(self, X_ref: np.ndarray) -> "QkMmdDetector":
        X_ref = np.asarray(X_ref, dtype=np.float64)

        if X_ref.ndim != 2:
            raise ValueError("X_ref must be a 2D array.")

        self.X_ref_ = X_ref
        return self

    def _check_fitted(self) -> None:
        if self.X_ref_ is None:
            raise RuntimeError("Detector is not fitted. Call fit(X_ref) first.")

    def score(self, X_cur: np.ndarray) -> float:
        self._check_fitted()
        assert self.X_ref_ is not None

        return mmd2_quantum(
            self.X_ref_,
            X_cur,
            feature_map=self.feature_map,
            reps=self.reps,
            biased=self.biased,
        )

    def predict(self, X_cur: np.ndarray) -> QkMmdPrediction:
        self._check_fitted()
        assert self.X_ref_ is not None

        X_cur = np.asarray(X_cur, dtype=np.float64)

        start = time.perf_counter()

        result = permutation_calibration(
            X_ref=self.X_ref_,
            X_cur=X_cur,
            score_fn=lambda A, B: mmd2_quantum(
                A,
                B,
                feature_map=self.feature_map,
                reps=self.reps,
                biased=self.biased,
            ),
            alpha=self.alpha,
            n_permutations=self.n_permutations,
            random_state=self.random_state,
        )

        runtime_sec = time.perf_counter() - start

        return QkMmdPrediction(
            detector="qk_mmd",
            score=result.observed_score,
            threshold=result.threshold,
            p_value=result.p_value,
            drift_detected=result.drift_detected,
            q_feature_map=self.feature_map,
            q_reps=int(self.reps),
            n_qubits=int(self.X_ref_.shape[1]),
            runtime_sec=float(runtime_sec),
            null_scores_mean=result.null_scores_mean,
            null_scores_std=result.null_scores_std,
        )
