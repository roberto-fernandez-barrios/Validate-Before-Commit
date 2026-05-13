from __future__ import annotations

import numpy as np


def bit_signs(n_qubits: int) -> np.ndarray:
    """
    Return computational-basis signs for Z eigenvalues.

    Shape:
        (2**n_qubits, n_qubits)

    Values:
        +1 for bit 0
        -1 for bit 1
    """
    if n_qubits < 1:
        raise ValueError("n_qubits must be >= 1.")

    if n_qubits > 12:
        raise ValueError(
            "This lightweight statevector implementation is intended for <= 12 qubits."
        )

    basis = np.arange(2**n_qubits, dtype=np.uint64)
    bit_positions = np.arange(n_qubits, dtype=np.uint64)

    bits = ((basis[:, None] >> bit_positions[None, :]) & 1).astype(np.float64)
    signs = 1.0 - 2.0 * bits

    return signs


def z_phase(X: np.ndarray, signs: np.ndarray) -> np.ndarray:
    """
    Diagonal Z-style phase.
    """
    return X @ signs.T


def zz_phase(X: np.ndarray, signs: np.ndarray) -> np.ndarray:
    """
    Diagonal ZZ-style phase with pairwise interactions.
    """
    phase = X @ signs.T
    n_features = X.shape[1]

    for i in range(n_features):
        for j in range(i + 1, n_features):
            x_pair = (X[:, i] * X[:, j])[:, None]
            z_pair = (signs[:, i] * signs[:, j])[None, :]
            phase += x_pair * z_pair

    return phase


def quantum_feature_states(
    X: np.ndarray,
    feature_map: str = "zz",
    reps: int = 1,
) -> np.ndarray:
    """
    Lightweight statevector feature map.

    This is a NumPy implementation of a diagonal quantum-inspired feature map.
    It is designed for fast experimentation before validating/porting to Qiskit.

    Supported feature maps:
        - z
        - zz
        - pauli_xz

    Returns:
        states with shape (n_samples, 2**n_features)
    """
    X = np.asarray(X, dtype=np.float64)

    if X.ndim != 2:
        raise ValueError("X must be a 2D array.")

    if reps < 1:
        raise ValueError("reps must be >= 1.")

    n_qubits = X.shape[1]
    signs = bit_signs(n_qubits)

    phase = np.zeros((X.shape[0], signs.shape[0]), dtype=np.float64)

    for _ in range(reps):
        if feature_map == "z":
            phase += z_phase(X, signs)

        elif feature_map == "zz":
            phase += zz_phase(X, signs)

        elif feature_map == "pauli_xz":
            # Simple additional nonlinear phase term for early ablations.
            phase += z_phase(X, signs)
            phase += z_phase(np.sin(X), signs)
            phase += zz_phase(X, signs)

        else:
            raise ValueError(
                f"Unknown feature_map={feature_map}. "
                "Supported: z, zz, pauli_xz."
            )

    norm = np.sqrt(signs.shape[0])
    states = np.exp(1j * phase) / norm

    return states.astype(np.complex128)


def quantum_fidelity_kernel(
    X: np.ndarray,
    Y: np.ndarray,
    feature_map: str = "zz",
    reps: int = 1,
) -> np.ndarray:
    """
    Fidelity kernel:

        K(x, y) = |<phi(x)|phi(y)>|^2
    """
    psi_x = quantum_feature_states(X, feature_map=feature_map, reps=reps)
    psi_y = quantum_feature_states(Y, feature_map=feature_map, reps=reps)

    overlaps = psi_x @ psi_y.conj().T
    return np.abs(overlaps) ** 2


def mmd2_quantum(
    X: np.ndarray,
    Y: np.ndarray,
    feature_map: str = "zz",
    reps: int = 1,
    biased: bool = True,
) -> float:
    """
    Quantum Kernel MMD using the lightweight fidelity kernel.
    """
    from src.drift_detection.metrics import mmd2_from_kernel

    Kxx = quantum_fidelity_kernel(X, X, feature_map=feature_map, reps=reps)
    Kyy = quantum_fidelity_kernel(Y, Y, feature_map=feature_map, reps=reps)
    Kxy = quantum_fidelity_kernel(X, Y, feature_map=feature_map, reps=reps)

    return mmd2_from_kernel(Kxx, Kyy, Kxy, biased=biased)
