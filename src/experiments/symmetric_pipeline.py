"""Self-contained predictive pipelines for the symmetric-pipeline replication.

Registered protocol: notes/paper2_symmetric_pipeline_dynamic_protocol_001.md.

The published v1.20.2 harness stores the evaluation stream ALREADY TRANSFORMED by the
initial scaler+PCA, and candidates are classifiers trained inside that fixed representation
(`frozen_initial_transformer`, the P0 policy). This module adds the machinery to run the
SAME scientific loop (`run_paper2_readaptation_v2.run_arm`, reused, not duplicated) over a
RAW stream, with models that are self-contained pipelines owning their preprocessing:

  * ModelPipeline      -- scaler + reducer + classifier + metadata; predicts on RAW features.
  * DetectorPipeline   -- the drift monitor with its OWN explicit representation, held at the
                          v1.20.2 semantics (initial transformer) under BOTH policies, so
                          changing the predictive pipeline cannot silently change monitoring.
  * build_candidate_pipeline -- the single candidate constructor implementing both
                          `frozen_initial_transformer` (exact v1.20.2 reproduction) and
                          `own_transformer_per_model` (challenger fits scaler/PCA on its own
                          candidate-training batch ONLY; commit deploys the complete bundle).
  * build_raw_environment -- wraps the historical build_environment (same RNG consumption,
                          bit-identical draws) and re-expresses it in raw-stream form.

Raw-mode contract: the Environment's scaler/pca are identity placeholders, so every
`transform_X(..., env.scaler, env.pca)` inside the historical run_arm is a no-op and every
array (stream window, probe, monitor draw, candidate batch) reaches models RAW; each
pipeline transforms internally with the components it owns. Under P0 this composes to
exactly the published computation (verified bit-for-bit by the parity suite).
"""
from __future__ import annotations

import hashlib
import pickle
from dataclasses import dataclass, field

import numpy as np

from src.experiments.run_paper2_progressive_readaptation import (
    build_detector,
    fit_transformer,
    train_svc,
    transform_X,
)
from src.experiments.run_paper2_readaptation_v2 import Environment, build_environment

FROZEN_POLICY = "frozen_initial_transformer"
OWN_POLICY = "own_transformer_per_model"
TRANSFORMER_POLICIES = (FROZEN_POLICY, OWN_POLICY)


def rows_hash(X: np.ndarray, y: np.ndarray | None = None) -> str:
    """Deterministic SHA-256 of the exact bytes of a row batch (and labels, if given)."""
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(X).tobytes())
    h.update(str(np.asarray(X).shape).encode())
    if y is not None:
        h.update(np.ascontiguousarray(np.asarray(y)).tobytes())
    return h.hexdigest()


def obj_hash(obj) -> str:
    """SHA-256 of an object's pickle bytes (fitted scaler/PCA/classifier identity)."""
    return hashlib.sha256(pickle.dumps(obj)).hexdigest()


def arr_hash(a) -> str:
    """SHA-256 of a fitted-parameter array's exact bytes ('none' when absent)."""
    if a is None:
        return "none"
    return hashlib.sha256(np.ascontiguousarray(np.asarray(a)).tobytes()).hexdigest()


def preprocessing_provenance(scaler, reducer, classifier, model_kind: str) -> dict:
    """Complete preprocessing/classifier provenance, so no gamma or PCA variation can hide
    inside 'own transformer' (confirmatory-phase requirement, protocol Appendix A phase)."""
    prov = dict(
        scaler_hash=obj_hash(scaler),
        scaler_mean_hash=arr_hash(getattr(scaler, "mean_", None)),
        scaler_scale_hash=arr_hash(getattr(scaler, "scale_", None)),
        pca_hash=obj_hash(reducer),
        pca_components_hash=arr_hash(getattr(reducer, "components_", None)),
        pca_explained_variance_hash=arr_hash(getattr(reducer, "explained_variance_", None)),
        pca_dim=(int(reducer.n_components_) if reducer is not None else None),
        classifier_params={k: repr(v) for k, v in sorted(classifier.get_params().items())},
        svc_configured_gamma=(repr(classifier.get_params().get("gamma"))
                              if model_kind == "svc_rbf" else None),
        svc_effective_gamma=(float(classifier._gamma)
                             if model_kind == "svc_rbf" and hasattr(classifier, "_gamma")
                             else None),
    )
    return prov


def stream_raw_hash(stream_raw: list[tuple[np.ndarray, np.ndarray, float]]) -> str:
    """Hash of the whole raw stream: every window's features, labels and severity."""
    h = hashlib.sha256()
    for Xw, yw, sev in stream_raw:
        h.update(rows_hash(Xw, yw).encode())
        h.update(repr(float(sev)).encode())
    return h.hexdigest()


class IdentityTransformer:
    """Placeholder for Environment.scaler in raw mode: transform_X becomes a no-op."""

    def transform(self, X):
        return X


@dataclass
class ModelPipeline:
    """A self-contained predictive pipeline: raw features in, predictions out."""
    scaler: object
    reducer: object | None
    classifier: object
    metadata: dict = field(default_factory=dict)

    def transform(self, X_raw: np.ndarray) -> np.ndarray:
        return transform_X(X_raw, self.scaler, self.reducer)

    def predict(self, X_raw: np.ndarray) -> np.ndarray:
        return self.classifier.predict(self.transform(X_raw))

    def predict_proba(self, X_raw: np.ndarray) -> np.ndarray:
        return self.classifier.predict_proba(self.transform(X_raw))


@dataclass
class DetectorPipeline:
    """The drift monitor with its OWN explicit representation.

    Primary semantics (registered): the detector representation stays the v1.20.2 one
    (initial scaler+PCA) under both P0 and P1 -- candidate-construction policy is isolated
    from drift-monitoring policy. `fit`/`score` accept RAW windows and transform internally,
    so run_arm's calibrate()/score() calls compose to exactly the published computation.
    """
    transformer: tuple            # (scaler, reducer) the detector representation
    detector: object              # the wrapped v1.20.2 detector (KS-max, ...)
    threshold: float | None = None
    metadata: dict = field(default_factory=dict)

    def _t(self, X_raw: np.ndarray) -> np.ndarray:
        return transform_X(X_raw, self.transformer[0], self.transformer[1])

    def fit(self, X_raw: np.ndarray):
        return self.detector.fit(self._t(X_raw))

    def score(self, X_raw: np.ndarray) -> float:
        return self.detector.score(self._t(X_raw))


def build_candidate_pipeline(
    X_train_raw: np.ndarray,
    y_train: np.ndarray,
    *,
    transformer_policy: str,
    initial_transformer: tuple,
    incumbent_pipeline: ModelPipeline | None,
    model_kind: str,
    seed: int,
    dim: int,
    probability: bool = False,
    svc_C: float = 1.0,
    arm_seed: int | None = None,
) -> ModelPipeline:
    """The single candidate constructor for both transformer policies.

    frozen_initial_transformer: reuses EXACTLY the initial scaler/PCA (never the current
    incumbent's, even if that were different) and never refits preprocessing -- reproducing
    v1.20.2. own_transformer_per_model: fits scaler on X_train_raw only, PCA on the scaled
    X_train_raw only (same dim/solver/config as the initial fit), then the same classifier
    type and hyperparameters. The probe and future windows participate in NO fit: this
    function receives only the candidate-training batch, and it is the only place a
    candidate is ever constructed.
    """
    if transformer_policy == FROZEN_POLICY:
        scaler, reducer = initial_transformer
        X_train = transform_X(X_train_raw, scaler, reducer)
    elif transformer_policy == OWN_POLICY:
        scaler, reducer, X_train = fit_transformer(X_train_raw, dim, seed)
    else:
        raise ValueError(f"unknown transformer policy: {transformer_policy}")
    clf = train_svc(X_train, y_train, seed, model_kind, proba=probability, C=svc_C)
    meta = dict(
        transformer_policy=transformer_policy,
        training_seed=int(seed),
        creation_window=(int(seed - arm_seed - 1) if arm_seed is not None else None),
        training_row_hash=rows_hash(X_train_raw, y_train),
        classifier_config=dict(model_kind=model_kind, C=float(svc_C),
                               probability=bool(probability), dim=int(dim)),
        deployed_version=None,   # assigned by the runner's serving log on commit
        **preprocessing_provenance(scaler, reducer, clf, model_kind),
    )
    return ModelPipeline(scaler, reducer, clf, meta)


def build_raw_environment(pools, args, seed: int, transformer_policy: str) -> Environment:
    """Historical environment re-expressed in raw-stream, self-contained-pipeline form.

    Calls the UNCHANGED historical build_environment (identical RNG consumption, so the raw
    stream and every derived draw are bit-identical to v1.20.2 for the same seed/args), then
    swaps in: a raw stream, an initial ModelPipeline that owns the initial transformer, a
    DetectorPipeline factory pinned to the initial transformer, and a candidate factory for
    the requested transformer policy.
    """
    if transformer_policy not in TRANSFORMER_POLICIES:
        raise ValueError(f"unknown transformer policy: {transformer_policy}")
    hist = build_environment(pools, args, seed)
    scaler0, pca0 = hist.scaler, hist.pca
    initial = ModelPipeline(
        scaler0, pca0, hist.initial_model,
        metadata=dict(transformer_policy=FROZEN_POLICY, training_seed=int(seed),
                      creation_window=None, role="initial_incumbent",
                      training_row_hash=rows_hash(*hist.init_train_raw),
                      classifier_config=dict(model_kind=args.downstream_model, C=1.0,
                                             dim=int(args.dim)),
                      deployed_version=0,
                      **preprocessing_provenance(scaler0, pca0, hist.initial_model,
                                                 args.downstream_model)))

    def detector_factory(method, dargs, dseed):
        return DetectorPipeline(
            transformer=(scaler0, pca0),
            detector=build_detector(method, dargs, dseed),
            metadata=dict(detector_transform_policy="frozen_initial", seed=int(dseed)))

    def candidate_factory(X_raw, y, cseed, C, proba):
        return build_candidate_pipeline(
            X_raw, y,
            transformer_policy=transformer_policy,
            initial_transformer=(scaler0, pca0),
            incumbent_pipeline=None,   # frozen NEVER takes the current incumbent's transformer
            model_kind=args.downstream_model, seed=cseed, dim=args.dim,
            probability=proba, svc_C=C, arm_seed=seed)

    return Environment(
        scaler=IdentityTransformer(), pca=None, initial_model=initial,
        stream=hist.stream_raw, cal_scores_pools=hist.cal_scores_pools,
        train_pools=hist.train_pools, probe_pools=hist.probe_pools,
        init_train=hist.init_train_raw,
        stream_raw=hist.stream_raw, init_train_raw=hist.init_train_raw,
        detector_factory=detector_factory, candidate_factory=candidate_factory)
