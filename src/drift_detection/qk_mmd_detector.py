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
    q_input_scaling: str
    runtime_sec: float
    null_scores_mean: float
    null_scores_std: float


class QkMmdDetector:
    """
    Quantum Kernel MMD drift detector.

    Uses a lightweight NumPy statevector feature map and a reference-fitted
    angle scaling step. The scaler is fitted only on X_ref to avoid leaking
    current-window information into the detector.
    """

    def __init__(
        self,
        feature_map: str = "zz",
        reps: int = 1,
        biased: bool = True,
        alpha: float = 0.05,
        n_permutations: int = 100,
        random_state: int = 42,
        input_scaling: str = "atan_standard",
    ) -> None:
        self.feature_map = feature_map
        self.reps = reps
        self.biased = biased
        self.alpha = alpha
        self.n_permutations = n_permutations
        self.random_state = random_state
        self.input_scaling = input_scaling

        self.X_ref_: np.ndarray | None = None
        self.X_ref_angles_: np.ndarray | None = None
        self.mean_: np.ndarray | None = None
        self.std_: np.ndarray | None = None

    def fit(self, X_ref: np.ndarray) -> "QkMmdDetector":
        X_ref = np.asarray(X_ref, dtype=np.float64)

        if X_ref.ndim != 2:
            raise ValueError("X_ref must be a 2D array.")

        self.X_ref_ = X_ref

        if self.input_scaling == "none":
            self.X_ref_angles_ = X_ref

        elif self.input_scaling == "atan_standard":
            self.mean_ = X_ref.mean(axis=0)
            self.std_ = X_ref.std(axis=0, ddof=0)
            self.std_ = np.where(self.std_ <= 1e-12, 1.0, self.std_)
            self.X_ref_angles_ = self._to_angles(X_ref)

        else:
            raise ValueError(
                f"Unknown input_scaling={self.input_scaling}. "
                "Supported: none, atan_standard."
            )

        return self

    def _check_fitted(self) -> None:
        if self.X_ref_ is None or self.X_ref_angles_ is None:
            raise RuntimeError("Detector is not fitted. Call fit(X_ref) first.")

    def _to_angles(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)

        if self.input_scaling == "none":
            return X

        if self.mean_ is None or self.std_ is None:
            raise RuntimeError("Angle scaler is not fitted.")

        Z = (X - self.mean_) / self.std_

        # Maps real-valued standardized features to (0, pi).
        # This avoids hard clipping while keeping valid angular inputs.
        return (np.pi / 2.0) + np.arctan(Z)

    def score(self, X_cur: np.ndarray) -> float:
        self._check_fitted()
        assert self.X_ref_angles_ is not None

        X_cur_angles = self._to_angles(X_cur)

        return mmd2_quantum(
            self.X_ref_angles_,
            X_cur_angles,
            feature_map=self.feature_map,
            reps=self.reps,
            biased=self.biased,
        )

    def predict(self, X_cur: np.ndarray) -> QkMmdPrediction:
        self._check_fitted()
        assert self.X_ref_angles_ is not None

        X_cur_angles = self._to_angles(X_cur)

        start = time.perf_counter()

        result = permutation_calibration(
            X_ref=self.X_ref_angles_,
            X_cur=X_cur_angles,
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
            n_qubits=int(self.X_ref_angles_.shape[1]),
            q_input_scaling=self.input_scaling,
            runtime_sec=float(runtime_sec),
            null_scores_mean=result.null_scores_mean,
            null_scores_std=result.null_scores_std,
        )
