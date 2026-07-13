from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import energy_distance, ks_2samp
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.experiments.run_paper2_downstream_adaptation import (
    MmdRbfDetector,
    QkMmdDetector,
)


@dataclass
class Pools:
    ref_benign: np.ndarray
    ref_attack: np.ndarray
    cur_benign: np.ndarray
    cur_attack: np.ndarray


def parse_csv_list(value: str, cast=str):
    if value is None or value == "":
        return []
    return [cast(x.strip()) for x in value.split(",") if x.strip()]


def load_binary_dataset(path: Path, label_col: str) -> tuple[pd.DataFrame, pd.Series]:
    print(f"[LOAD] {path}")
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    label_col = label_col.strip()
    if label_col not in df.columns:
        raise ValueError(f"Label column {label_col!r} not found. Available: {df.columns[:10].tolist()}...")

    y_raw = df[label_col].astype(str).str.strip()
    y = (y_raw != "BENIGN").astype(int)

    X = df.drop(columns=[label_col]).copy()

    # Keep numeric columns only.
    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0.0)

    print(
        f"[DATA] rows={len(df)} features={X.shape[1]} "
        f"benign={(y == 0).sum()} attack={(y == 1).sum()}"
    )

    return X, y


def make_pools(
    X_ref: pd.DataFrame,
    y_ref: pd.Series,
    X_cur: pd.DataFrame,
    y_cur: pd.Series,
    common_features: list[str],
) -> Pools:
    Xr = X_ref[common_features].to_numpy(dtype=float)
    Xc = X_cur[common_features].to_numpy(dtype=float)

    return Pools(
        ref_benign=Xr[y_ref.to_numpy() == 0],
        ref_attack=Xr[y_ref.to_numpy() == 1],
        cur_benign=Xc[y_cur.to_numpy() == 0],
        cur_attack=Xc[y_cur.to_numpy() == 1],
    )


def sample_rows(pool: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    idx = rng.integers(0, len(pool), size=n)
    return pool[idx]


def sample_balanced_from_distribution(
    pools: Pools,
    n_per_class: int,
    severity: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Balanced binary sample. Each class is a mixture ref/current controlled by severity."""
    severity = float(np.clip(severity, 0.0, 1.0))

    n_cur = int(round(n_per_class * severity))
    n_ref = n_per_class - n_cur

    xb = np.vstack(
        [
            sample_rows(pools.ref_benign, n_ref, rng),
            sample_rows(pools.cur_benign, n_cur, rng),
        ]
    )

    xa = np.vstack(
        [
            sample_rows(pools.ref_attack, n_ref, rng),
            sample_rows(pools.cur_attack, n_cur, rng),
        ]
    )

    X = np.vstack([xb, xa])
    y = np.array([0] * n_per_class + [1] * n_per_class)

    perm = rng.permutation(len(y))
    return X[perm], y[perm]


def sample_prevalence_from_distribution(
    pools: Pools,
    n_total: int,
    attack_frac: float,
    severity: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Binary sample at a given attack prevalence (Phase 2j probes). Each class is the same
    ref/current mixture as sample_balanced_from_distribution; at least one attack flow is
    always included (a probe with zero attacks cannot compare attack behaviour)."""
    severity = float(np.clip(severity, 0.0, 1.0))
    n_att = max(1, int(round(n_total * attack_frac)))
    n_ben = max(1, n_total - n_att)

    def mixed(pool_ref, pool_cur, n):
        n_cur = int(round(n * severity))
        return np.vstack([sample_rows(pool_ref, n - n_cur, rng), sample_rows(pool_cur, n_cur, rng)])

    X = np.vstack([mixed(pools.ref_benign, pools.cur_benign, n_ben),
                   mixed(pools.ref_attack, pools.cur_attack, n_att)])
    y = np.array([0] * n_ben + [1] * n_att)
    perm = rng.permutation(len(y))
    return X[perm], y[perm]


def fit_transformer(X_train: np.ndarray, dim: int, seed: int):
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X_train)

    if dim < Xs.shape[1]:
        pca = PCA(n_components=dim, random_state=seed)
        Xr = pca.fit_transform(Xs)
    else:
        pca = None
        Xr = Xs

    return scaler, pca, Xr


def transform_X(X: np.ndarray, scaler: StandardScaler, pca: PCA | None) -> np.ndarray:
    Xs = scaler.transform(X)
    if pca is not None:
        return pca.transform(Xs)
    return Xs


def train_svc(X: np.ndarray, y: np.ndarray, seed: int, model_type: str = "svc_rbf", proba: bool = False):
    """Fit the downstream classifier. Name kept for backward compatibility.

    `proba=True` enables predict_proba on SVC (Platt scaling) for confidence-based gates (ATC/DoC).
    """
    if model_type == "svc_rbf":
        model = SVC(kernel="rbf", gamma="scale", class_weight="balanced", random_state=seed,
                    probability=proba)
    elif model_type == "random_forest":
        model = RandomForestClassifier(
            n_estimators=200, class_weight="balanced", random_state=seed, n_jobs=-1
        )
    elif model_type == "logreg":
        model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=seed)
    elif model_type == "mlp":
        model = MLPClassifier(hidden_layer_sizes=(64,), max_iter=300, random_state=seed)
    else:
        raise ValueError(f"Unknown downstream model: {model_type}")
    model.fit(X, y)
    return model


def evaluate_model(model: SVC, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
    pred = model.predict(X)
    return {
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "f1": float(f1_score(y, pred, zero_division=0)),
    }


def _model_conf(model, X: np.ndarray) -> np.ndarray:
    """Max class probability per row (confidence), for ATC/DoC gates."""
    return model.predict_proba(X).max(axis=1)


def _labelfree_estimate(kind: str, model, val: tuple[np.ndarray, np.ndarray], X_target: np.ndarray) -> float:
    """Label-free target-accuracy estimate from labeled SOURCE validation data + unlabeled target.

    atc: Average Thresholded Confidence (Garg et al., ICLR 2022) -- learn threshold t on val so that
         the fraction of val confidences above t equals val accuracy; estimate = fraction of target
         confidences above t.
    doc: Difference of Confidences (Guillory et al., ICCV 2021) --
         est = acc_val - (mean_conf_val - mean_conf_target).
    """
    valX, valy = val
    acc_val = float((model.predict(valX) == valy).mean())
    conf_val = _model_conf(model, valX)
    conf_t = _model_conf(model, X_target)
    if kind == "atc":
        thr = float(np.quantile(conf_val, 1.0 - acc_val)) if acc_val < 1.0 else float(conf_val.min())
        return float((conf_t > thr).mean())
    return acc_val - (float(conf_val.mean()) - float(conf_t.mean()))


class KsWindowDetector:
    """Classical per-feature Kolmogorov-Smirnov window detector.

    The score is the maximum or mean KS statistic across features.
    Higher means stronger distribution shift.
    """

    def __init__(self, reduction: str = "max"):
        self.reduction = reduction
        self.X_ref: np.ndarray | None = None

    def fit(self, X_ref: np.ndarray):
        self.X_ref = np.asarray(X_ref, dtype=float)
        return self

    def score(self, X: np.ndarray) -> float:
        if self.X_ref is None:
            raise RuntimeError("Detector must be fitted before scoring.")

        X = np.asarray(X, dtype=float)

        stats = []
        for j in range(self.X_ref.shape[1]):
            stat = ks_2samp(
                self.X_ref[:, j],
                X[:, j],
                alternative="two-sided",
                mode="auto",
            ).statistic
            stats.append(float(stat))

        stats = np.asarray(stats, dtype=float)

        if self.reduction == "mean":
            return float(np.mean(stats))

        if self.reduction == "max":
            return float(np.max(stats))

        raise ValueError(f"Unknown KS reduction={self.reduction!r}")


class JsdHistogramDetector:
    """Classical histogram Jensen-Shannon divergence window detector.

    Per feature, quantile bins are fitted on the reference window. The score is
    the mean Jensen-Shannon divergence across features.
    """

    def __init__(self, n_bins: int = 20, eps: float = 1e-12):
        self.n_bins = int(n_bins)
        self.eps = float(eps)
        self.edges_: list[np.ndarray] | None = None
        self.ref_hist_: list[np.ndarray] | None = None

    def _make_edges(self, x: np.ndarray) -> np.ndarray:
        quantiles = np.linspace(0.0, 1.0, self.n_bins + 1)
        edges = np.quantile(x, quantiles)
        edges = np.unique(edges)

        if len(edges) < 3:
            center = float(np.mean(x))
            span = float(np.std(x))
            if span <= 0:
                span = 1.0
            edges = np.linspace(center - span, center + span, self.n_bins + 1)

        edges = edges.astype(float)
        edges[0] = -np.inf
        edges[-1] = np.inf

        return edges

    def _hist(self, x: np.ndarray, edges: np.ndarray) -> np.ndarray:
        counts, _ = np.histogram(x, bins=edges)
        p = counts.astype(float) + self.eps
        p /= p.sum()
        return p

    def fit(self, X_ref: np.ndarray):
        X_ref = np.asarray(X_ref, dtype=float)

        self.edges_ = []
        self.ref_hist_ = []

        for j in range(X_ref.shape[1]):
            edges = self._make_edges(X_ref[:, j])
            self.edges_.append(edges)
            self.ref_hist_.append(self._hist(X_ref[:, j], edges))

        return self

    def score(self, X: np.ndarray) -> float:
        if self.edges_ is None or self.ref_hist_ is None:
            raise RuntimeError("Detector must be fitted before scoring.")

        X = np.asarray(X, dtype=float)

        values = []
        for j, edges in enumerate(self.edges_):
            p = self.ref_hist_[j]
            q = self._hist(X[:, j], edges)
            m = 0.5 * (p + q)

            jsd = 0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m))
            values.append(float(jsd))

        return float(np.mean(values))


class EnergyWindowDetector:
    """Classical per-feature energy-distance window detector.

    The score is the mean or maximum energy distance across features.
    Higher means stronger distribution shift.
    """

    def __init__(self, reduction: str = "mean"):
        self.reduction = reduction
        self.X_ref: np.ndarray | None = None

    def fit(self, X_ref: np.ndarray):
        self.X_ref = np.asarray(X_ref, dtype=float)
        return self

    def score(self, X: np.ndarray) -> float:
        if self.X_ref is None:
            raise RuntimeError("Detector must be fitted before scoring.")

        X = np.asarray(X, dtype=float)

        values = []
        for j in range(self.X_ref.shape[1]):
            values.append(float(energy_distance(self.X_ref[:, j], X[:, j])))

        values = np.asarray(values, dtype=float)

        if self.reduction == "mean":
            return float(np.mean(values))

        if self.reduction == "max":
            return float(np.max(values))

        raise ValueError(f"Unknown energy reduction={self.reduction!r}")



def build_detector(method: str, args, seed: int):
    if method == "mmd_rbf":
        return MmdRbfDetector(
            gamma=None,
            biased=True,
            alpha=args.alpha,
            n_permutations=args.n_permutations,
            random_state=seed,
        )

    if method == "qk_mmd_zz":
        return QkMmdDetector(
            feature_map="zz",
            reps=args.q_reps,
            biased=True,
            alpha=args.alpha,
            n_permutations=args.n_permutations,
            random_state=seed,
            input_scaling=args.q_input_scaling,
        )

    if method == "qk_mmd_pauli_xz":
        return QkMmdDetector(
            feature_map="pauli_xz",
            reps=args.q_reps,
            biased=True,
            alpha=args.alpha,
            n_permutations=args.n_permutations,
            random_state=seed,
            input_scaling=args.q_input_scaling,
        )

    if method == "ks_max":
        return KsWindowDetector(reduction=args.ks_reduction)

    if method == "jsd":
        return JsdHistogramDetector(n_bins=args.jsd_bins)

    if method == "energy_distance":
        return EnergyWindowDetector(reduction=args.energy_reduction)

    raise ValueError(f"Unknown method={method}")


def calibrate_detector(
    detector,
    pools: Pools,
    scaler: StandardScaler,
    pca: PCA | None,
    severity: float,
    args,
    rng: np.random.Generator,
) -> tuple[object, float]:
    X_ref_raw, _ = sample_balanced_from_distribution(
        pools,
        n_per_class=args.detector_ref_size_per_class,
        severity=severity,
        rng=rng,
    )
    X_ref = transform_X(X_ref_raw, scaler, pca)

    detector.fit(X_ref)

    scores = []
    for _ in range(args.calibration_windows):
        Xw_raw, _ = sample_balanced_from_distribution(
            pools,
            n_per_class=args.window_size // 2,
            severity=severity,
            rng=rng,
        )
        Xw = transform_X(Xw_raw, scaler, pca)
        scores.append(float(detector.score(Xw)))

    threshold = float(np.quantile(scores, args.threshold_quantile))
    return detector, threshold


def progressive_severity(t: int, args) -> float:
    if args.ramp_windows <= 1:
        return args.max_severity

    raw = (t + 1) / args.ramp_windows * args.max_severity
    return float(min(args.max_severity, raw))


def run_strategy(
    method: str,
    pools: Pools,
    scaler: StandardScaler,
    pca: PCA | None,
    initial_model: SVC,
    no_adapt_window_metrics: list[dict[str, float]],
    args,
    seed: int,
) -> tuple[list[dict], dict]:
    method_seed_offsets = {
        "mmd_rbf": 101,
        "qk_mmd_zz": 202,
        "qk_mmd_pauli_xz": 303,
        "ks_max": 404,
        "jsd": 505,
        "energy_distance": 606,
    }
    rng = np.random.default_rng(seed + 10000 + method_seed_offsets[method])

    current_model = initial_model
    current_reference_severity = 0.0

    detector = build_detector(method, args, seed)
    detector, threshold = calibrate_detector(
        detector,
        pools,
        scaler,
        pca,
        severity=current_reference_severity,
        args=args,
        rng=rng,
    )

    policy_k = int(args.policy_k) if args.policy_k is not None else int(args.consecutive_k)
    policy_n = int(args.policy_n) if args.policy_n is not None else int(args.consecutive_k)

    if policy_k <= 0 or policy_n <= 0 or policy_k > policy_n:
        raise ValueError(f"Invalid adaptation policy parameters: k={policy_k}, n={policy_n}")

    policy_name = args.policy_name or f"{args.adaptation_policy}_k{policy_k}_n{policy_n}_cd{args.cooldown_windows}"

    alarm_history: list[bool] = []
    cooldown_remaining = 0
    n_adaptations = 0
    false_adaptations = 0
    adaptation_windows: list[int] = []
    n_triggers = 0
    n_gate_rejections = 0
    labels_used_total = 0

    # ATC/DoC gates: labeled SOURCE validation sample for the incumbent, drawn at its training severity
    # (0.0 for the initial model). Zero target-window labels are ever used by these gates.
    incumbent_val = None
    if args.adaptation_gate in ("atc", "doc"):
        Xv_raw, yv = sample_balanced_from_distribution(
            pools, n_per_class=max(1, args.gate_val_size // 2), severity=0.0, rng=rng,
        )
        incumbent_val = (transform_X(Xv_raw, scaler, pca), yv)

    window_rows = []
    detector_runtime_sec_total = 0.0
    fit_runtime_sec_total = 0.0

    for t in range(args.post_windows):
        sev_t = progressive_severity(t, args)

        Xw_raw, yw = sample_balanced_from_distribution(
            pools,
            n_per_class=args.window_size // 2,
            severity=sev_t,
            rng=rng,
        )
        Xw = transform_X(Xw_raw, scaler, pca)

        eval_metrics = evaluate_model(current_model, Xw, yw)

        score_start = time.perf_counter()
        score = float(detector.score(Xw))
        detector_runtime_sec_total += time.perf_counter() - score_start

        alarm = bool(score > threshold)
        alarm_history.append(alarm)

        if len(alarm_history) > policy_n:
            recent = alarm_history[-policy_n:]
        else:
            recent = alarm_history

        if args.adaptation_policy == "consecutive":
            trigger_condition = len(recent) == policy_n and all(recent)
        elif args.adaptation_policy == "k_of_n":
            trigger_condition = len(recent) == policy_n and sum(bool(x) for x in recent) >= policy_k
        else:
            raise ValueError(f"Unknown adaptation policy: {args.adaptation_policy}")

        trigger = bool(trigger_condition and cooldown_remaining <= 0)

        adapted_now = False
        gate_evaluated = False

        if trigger:
            n_triggers += 1
            gate_evaluated = True

            # Build a CANDIDATE model on a freshly sampled adapt set (true labels).
            Xa_raw, ya = sample_balanced_from_distribution(
                pools,
                n_per_class=args.adapt_size_per_class,
                severity=sev_t,
                rng=rng,
            )
            if args.adapt_strategy == "replay":
                # Phase 2i: retrain-current-plus-replay — augment the current-severity sample
                # with an equal-size (by default) replay sample from the reference regime.
                replay_n = args.replay_size_per_class or args.adapt_size_per_class
                Xr_raw, yr = sample_balanced_from_distribution(
                    pools, n_per_class=replay_n, severity=0.0, rng=rng,
                )
                Xa_raw = np.vstack([Xa_raw, Xr_raw])
                ya = np.concatenate([ya, yr])
            Xa = transform_X(Xa_raw, scaler, pca)

            fit_start = time.perf_counter()
            needs_proba = args.adaptation_gate in ("atc", "doc")
            candidate_model = train_svc(Xa, ya, seed + t + 1, args.downstream_model, proba=needs_proba)
            fit_runtime_sec_total += time.perf_counter() - fit_start

            # Safe/cost-aware gate: decide whether to COMMIT (deploy) the candidate.
            commit = True
            cand_val = None
            gate = args.adaptation_gate
            if gate == "labeled_probe":
                n_probe = max(1, args.probe_size // 2)
                # Realistic label latency: the probe comes from traffic labeled `probe_lag`
                # windows ago (its severity), not from the current window.
                probe_sev = progressive_severity(max(0, t - args.probe_lag), args)
                if args.probe_prevalence != 0.5:
                    # Phase 2j: probe drawn at the traffic's natural attack prevalence.
                    Xp_raw, yp = sample_prevalence_from_distribution(
                        pools, n_total=args.probe_size, attack_frac=args.probe_prevalence,
                        severity=probe_sev, rng=rng,
                    )
                else:
                    Xp_raw, yp = sample_balanced_from_distribution(
                        pools, n_per_class=n_probe, severity=probe_sev, rng=rng,
                    )
                Xp = transform_X(Xp_raw, scaler, pca)
                # Adversarial / noisy probe: an attacker (or faulty labeler) flips a
                # fraction of the validation labels the gate relies on.
                if args.probe_poison > 0.0:
                    flip = rng.random(len(yp)) < args.probe_poison
                    yp = np.where(flip, 1 - yp, yp)
                ba_dep = evaluate_model(current_model, Xp, yp)["balanced_accuracy"]
                ba_cand = evaluate_model(candidate_model, Xp, yp)["balanced_accuracy"]
                commit = bool(ba_cand >= ba_dep + args.gate_margin)
                labels_used_total += len(yp)
            elif gate == "unsup_disagree":
                pred_dep = current_model.predict(Xw)
                pred_cand = candidate_model.predict(Xw)
                disagree = float(np.mean(pred_dep != pred_cand))
                commit = bool(disagree >= args.gate_disagree_threshold)
            elif gate in ("atc", "doc"):
                # Label-free gate: estimate target accuracy of incumbent and candidate from their
                # own labeled source-validation samples + the UNLABELED current window.
                Xv_raw, yv = sample_balanced_from_distribution(
                    pools, n_per_class=max(1, args.gate_val_size // 2), severity=sev_t, rng=rng,
                )
                cand_val = (transform_X(Xv_raw, scaler, pca), yv)
                est_dep = _labelfree_estimate(gate, current_model, incumbent_val, Xw)
                est_cand = _labelfree_estimate(gate, candidate_model, cand_val, Xw)
                commit = bool(est_cand >= est_dep + args.gate_margin)
            elif gate != "none":
                raise ValueError(f"Unknown adaptation gate: {gate}")

            if commit:
                n_adaptations += 1
                adaptation_windows.append(t)
                adapted_now = True
                if sev_t < args.false_adaptation_severity_threshold:
                    false_adaptations += 1
                current_model = candidate_model
                if cand_val is not None:
                    incumbent_val = cand_val
                # Reset detector reference to the current adapted regime.
                detector = build_detector(method, args, seed + t + 1)
                detector, threshold = calibrate_detector(
                    detector,
                    pools,
                    scaler,
                    pca,
                    severity=sev_t,
                    args=args,
                    rng=rng,
                )
            else:
                # Gate rejected: keep deployed model AND detector reference so that a
                # later window can re-propose once drift becomes actionable.
                n_gate_rejections += 1

            alarm_history = []
            cooldown_remaining = args.cooldown_windows

        else:
            cooldown_remaining = max(0, cooldown_remaining - 1)

        no_adapt_ba = no_adapt_window_metrics[t]["balanced_accuracy"]

        window_rows.append(
            {
                "seed": seed,
                "method": method,
                "policy_name": policy_name,
                "adaptation_policy": args.adaptation_policy,
                "policy_k": policy_k,
                "policy_n": policy_n,
                "cooldown_windows": args.cooldown_windows,
                "window_idx": t,
                "severity_t": sev_t,
                "score": score,
                "threshold": threshold,
                "alarm": alarm,
                "trigger": trigger,
                "gate_evaluated": gate_evaluated,
                "adapted_now": adapted_now,
                "cooldown_remaining": cooldown_remaining,
                "balanced_accuracy": eval_metrics["balanced_accuracy"],
                "f1": eval_metrics["f1"],
                "no_adapt_balanced_accuracy": no_adapt_ba,
                "gain_vs_no_adapt": eval_metrics["balanced_accuracy"] - no_adapt_ba,
            }
        )

    df = pd.DataFrame(window_rows)

    summary = {
        "seed": seed,
        "method": method,
        "downstream_model": args.downstream_model,
        "n_windows": args.post_windows,
        "n_adaptations": n_adaptations,
        "n_triggers": n_triggers,
        "n_gate_rejections": n_gate_rejections,
        "labels_used_total": labels_used_total,
        "adaptation_gate": args.adaptation_gate,
        "adapt_strategy": args.adapt_strategy,
        "probe_size": args.probe_size if args.adaptation_gate == "labeled_probe" else 0,
        "probe_lag": args.probe_lag if args.adaptation_gate == "labeled_probe" else 0,
        "probe_poison": args.probe_poison if args.adaptation_gate == "labeled_probe" else 0.0,
        "probe_prevalence": args.probe_prevalence if args.adaptation_gate == "labeled_probe" else 0.5,
        "gate_margin": args.gate_margin if args.adaptation_gate == "labeled_probe" else 0.0,
        "false_adaptations": false_adaptations,
        "first_adaptation_window": adaptation_windows[0] if adaptation_windows else np.nan,
        "mean_balanced_accuracy": float(df["balanced_accuracy"].mean()),
        "mean_f1": float(df["f1"].mean()),
        "cumulative_error_area": float((1.0 - df["balanced_accuracy"]).sum()),
        "mean_gain_vs_no_adapt": float(df["gain_vs_no_adapt"].mean()),
        "cumulative_gain_vs_no_adapt": float(df["gain_vs_no_adapt"].sum()),
        "alarm_rate": float(df["alarm"].mean()),
        "trigger_rate": float(df["trigger"].mean()),
        "detector_runtime_sec_total": detector_runtime_sec_total,
        "fit_runtime_sec_total": fit_runtime_sec_total,
    }

    return window_rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--data-ref", type=Path, required=True)
    parser.add_argument("--data-cur", type=Path, required=True)
    parser.add_argument("--label-col", type=str, default="Label")
    parser.add_argument("--outdir", type=Path, required=True)

    parser.add_argument("--seeds", type=str, default="1,2,3")
    parser.add_argument("--methods", type=str, default="mmd_rbf,qk_mmd_zz,qk_mmd_pauli_xz")

    parser.add_argument("--ks-reduction", type=str, default="max", choices=["max", "mean"])
    parser.add_argument("--jsd-bins", type=int, default=20)
    parser.add_argument("--energy-reduction", type=str, default="mean", choices=["mean", "max"])

    parser.add_argument("--dim", type=int, default=8)
    parser.add_argument("--window-size", type=int, default=128)
    parser.add_argument("--train-size-per-class", type=int, default=2000)
    parser.add_argument("--adapt-size-per-class", type=int, default=512)
    parser.add_argument("--detector-ref-size-per-class", type=int, default=256)

    parser.add_argument("--post-windows", type=int, default=100)
    parser.add_argument("--ramp-windows", type=int, default=80)
    parser.add_argument("--max-severity", type=float, default=1.0)

    parser.add_argument("--calibration-windows", type=int, default=20)
    parser.add_argument("--threshold-quantile", type=float, default=0.95)
    parser.add_argument("--consecutive-k", type=int, default=3)
    parser.add_argument("--adaptation-policy", type=str, default="consecutive", choices=["consecutive", "k_of_n"])
    parser.add_argument("--policy-k", type=int, default=None)
    parser.add_argument("--policy-n", type=int, default=None)
    parser.add_argument("--policy-name", type=str, default=None)
    parser.add_argument("--cooldown-windows", type=int, default=10)
    parser.add_argument("--false-adaptation-severity-threshold", type=float, default=0.1)

    # Safe/cost-aware adaptation gate (Phase 2): validate a candidate before committing.
    parser.add_argument(
        "--adaptation-gate",
        type=str,
        default="none",
        choices=["none", "labeled_probe", "unsup_disagree", "atc", "doc"],
    )
    parser.add_argument("--gate-val-size", type=int, default=256)
    parser.add_argument("--probe-size", type=int, default=64)
    parser.add_argument("--probe-lag", type=int, default=0)
    parser.add_argument("--probe-poison", type=float, default=0.0)
    parser.add_argument("--probe-prevalence", type=float, default=0.5,
                        help="Attack fraction of the labeled probe (0.5 = balanced, default; "
                             "Phase 2j draws the probe at the traffic's natural prevalence).")
    parser.add_argument("--gate-margin", type=float, default=0.0)
    parser.add_argument("--adapt-strategy", type=str, default="full_replace",
                        choices=["full_replace", "replay"],
                        help="Candidate training data: current-severity sample only "
                             "(full_replace, default) or current + reference-regime replay "
                             "sample (replay; Phase 2i).")
    parser.add_argument("--replay-size-per-class", type=int, default=None,
                        help="Replay sample size per class (default: adapt-size-per-class).")
    parser.add_argument("--gate-disagree-threshold", type=float, default=0.15)

    parser.add_argument(
        "--downstream-model",
        type=str,
        default="svc_rbf",
        choices=["svc_rbf", "random_forest", "logreg", "mlp"],
    )

    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-permutations", type=int, default=100)

    parser.add_argument("--q-reps", type=int, default=1)
    parser.add_argument("--q-input-scaling", type=str, default="atan_standard")

    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    seeds = parse_csv_list(args.seeds, int)
    methods = parse_csv_list(args.methods, str)

    X_ref, y_ref = load_binary_dataset(args.data_ref, args.label_col)
    X_cur, y_cur = load_binary_dataset(args.data_cur, args.label_col)

    common_features = sorted(set(X_ref.columns).intersection(set(X_cur.columns)))
    print(f"[ALIGN] common_features={len(common_features)}")

    pools = make_pools(X_ref, y_ref, X_cur, y_cur, common_features)

    all_window_rows = []
    all_summary_rows = []

    for seed in seeds:
        print("=" * 100)
        print(f"[SEED={seed}]")
        print("=" * 100)

        rng = np.random.default_rng(seed)

        X_train_raw, y_train = sample_balanced_from_distribution(
            pools,
            n_per_class=args.train_size_per_class,
            severity=0.0,
            rng=rng,
        )

        scaler, pca, X_train = fit_transformer(X_train_raw, args.dim, seed)

        initial_model = train_svc(
            X_train, y_train, seed, args.downstream_model,
            proba=args.adaptation_gate in ("atc", "doc"),
        )

        no_adapt_rows = []

        for t in range(args.post_windows):
            sev_t = progressive_severity(t, args)

            Xw_raw, yw = sample_balanced_from_distribution(
                pools,
                n_per_class=args.window_size // 2,
                severity=sev_t,
                rng=rng,
            )
            Xw = transform_X(Xw_raw, scaler, pca)
            metrics = evaluate_model(initial_model, Xw, yw)

            no_adapt_rows.append(
                {
                    "seed": seed,
                    "method": "no_adaptation",
                    "policy_name": args.policy_name or f"{args.adaptation_policy}_k{int(args.policy_k) if args.policy_k is not None else int(args.consecutive_k)}_n{int(args.policy_n) if args.policy_n is not None else int(args.consecutive_k)}_cd{args.cooldown_windows}",
                    "adaptation_policy": args.adaptation_policy,
                    "policy_k": int(args.policy_k) if args.policy_k is not None else int(args.consecutive_k),
                    "policy_n": int(args.policy_n) if args.policy_n is not None else int(args.consecutive_k),
                    "cooldown_windows": args.cooldown_windows,
                    "window_idx": t,
                    "severity_t": sev_t,
                    "balanced_accuracy": metrics["balanced_accuracy"],
                    "f1": metrics["f1"],
                    "gain_vs_no_adapt": 0.0,
                }
            )

        no_adapt_df = pd.DataFrame(no_adapt_rows)

        all_window_rows.extend(no_adapt_rows)

        all_summary_rows.append(
            {
                "seed": seed,
                "method": "no_adaptation",
                "n_windows": args.post_windows,
                "n_adaptations": 0,
                "false_adaptations": 0,
                "first_adaptation_window": np.nan,
                "mean_balanced_accuracy": float(no_adapt_df["balanced_accuracy"].mean()),
                "mean_f1": float(no_adapt_df["f1"].mean()),
                "cumulative_error_area": float((1.0 - no_adapt_df["balanced_accuracy"]).sum()),
                "mean_gain_vs_no_adapt": 0.0,
                "cumulative_gain_vs_no_adapt": 0.0,
                "alarm_rate": 0.0,
                "trigger_rate": 0.0,
                "detector_runtime_sec_total": 0.0,
                "fit_runtime_sec_total": 0.0,
            }
        )

        for method in methods:
            print(f"[SEED={seed}][METHOD={method}]")
            rows, summary = run_strategy(
                method=method,
                pools=pools,
                scaler=scaler,
                pca=pca,
                initial_model=initial_model,
                no_adapt_window_metrics=no_adapt_rows,
                args=args,
                seed=seed,
            )

            all_window_rows.extend(rows)
            all_summary_rows.append(summary)

    window_df = pd.DataFrame(all_window_rows)
    effective_policy_k = int(args.policy_k) if args.policy_k is not None else int(args.consecutive_k)
    effective_policy_n = int(args.policy_n) if args.policy_n is not None else int(args.consecutive_k)
    effective_policy_name = args.policy_name or f"{args.adaptation_policy}_k{effective_policy_k}_n{effective_policy_n}_cd{args.cooldown_windows}"

    for _rows in (all_window_rows, all_summary_rows):
        for _row in _rows:
            _row.setdefault("policy_name", effective_policy_name)
            _row.setdefault("adaptation_policy", args.adaptation_policy)
            _row.setdefault("policy_k", effective_policy_k)
            _row.setdefault("policy_n", effective_policy_n)
            _row.setdefault("cooldown_windows", args.cooldown_windows)

    summary_df = pd.DataFrame(all_summary_rows)

    window_path = args.outdir / "paper2_progressive_readaptation_window_results.csv"
    by_seed_path = args.outdir / "paper2_progressive_readaptation_by_seed.csv"

    window_df.to_csv(window_path, index=False)
    summary_df.to_csv(by_seed_path, index=False)

    agg = (
        summary_df
        .groupby(["policy_name", "adaptation_policy", "policy_k", "policy_n", "cooldown_windows", "method"], dropna=False)
        .agg(
            n_seeds=("seed", "nunique"),
            mean_balanced_accuracy=("mean_balanced_accuracy", "mean"),
            std_balanced_accuracy=("mean_balanced_accuracy", "std"),
            cumulative_error_area_mean=("cumulative_error_area", "mean"),
            cumulative_error_area_std=("cumulative_error_area", "std"),
            mean_gain_vs_no_adapt=("mean_gain_vs_no_adapt", "mean"),
            cumulative_gain_vs_no_adapt_mean=("cumulative_gain_vs_no_adapt", "mean"),
            n_adaptations_mean=("n_adaptations", "mean"),
            false_adaptations_mean=("false_adaptations", "mean"),
            first_adaptation_window_mean=("first_adaptation_window", "mean"),
            alarm_rate_mean=("alarm_rate", "mean"),
            trigger_rate_mean=("trigger_rate", "mean"),
            detector_runtime_sec_total_mean=("detector_runtime_sec_total", "mean"),
            fit_runtime_sec_total_mean=("fit_runtime_sec_total", "mean"),
        )
        .reset_index()
        .sort_values("method")
    )

    summary_path = args.outdir / "paper2_progressive_readaptation_summary.csv"
    agg.to_csv(summary_path, index=False)

    print(f"Saved: {window_path}")
    print(f"Saved: {by_seed_path}")
    print(f"Saved: {summary_path}")

    print()
    print("=== PROGRESSIVE READAPTATION SUMMARY ===")
    print(agg.to_string(index=False))


if __name__ == "__main__":
    main()
