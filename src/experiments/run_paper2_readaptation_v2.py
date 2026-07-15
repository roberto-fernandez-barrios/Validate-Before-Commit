"""Harness v2: common streams, role-disjoint partitions, separate RNGs, per-trigger logging.

Fixes the three harness-level criticisms of the external review:
  1. COMMON STREAMS -- the evaluation stream (and calibration windows) are pre-generated from an
     environment RNG that depends only on the seed, before any policy runs. Every arm (gate,
     detector, baseline) with the same seed processes exactly the same windows in the same order;
     policy actions cannot perturb the environment.
  2. ROLE-DISJOINT PARTITIONS -- each per-class pool is split once per seed into window (50%),
     train (30%) and probe (20%) partitions. Stream/calibration windows draw only from `window`,
     the initial model, candidates and detector references only from `train`, probes only from
     `probe`. Train/probe/eval overlap is impossible by construction.
  3. SEPARATE RNGs -- environment, initial training, detector calibration, candidate training,
     probe draws and post-commit recalibration each use their own generator, seeded by (seed) or
     (seed, t) only, never by the policy's history.

Adds per-trigger logging (pre-trigger degradation, detector score, incumbent vs candidate on the
next 5 future windows) for the per-trigger mechanism analysis, and two new gates:
  labeled_probe_holdout -- the probe is carved out of the candidate's labeled training batch
     before training (zero incremental labels beyond the retraining data);
  labeled_probe_lcb     -- commit only if the one-sided lower confidence bound (alpha=0.10) of
     the mean per-flow correctness difference (candidate - incumbent) on the probe exceeds 0.

Outputs the same CSV formats as the v1 runner (window results, by-seed, summary) plus
paper2_v2_trigger_log.csv.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.experiments.run_paper2_progressive_readaptation import (
    Pools,
    build_detector,
    evaluate_model,
    fit_transformer,
    load_binary_dataset,
    make_pools,
    progressive_severity,
    sample_balanced_from_distribution,
    sample_binomial_prevalence,
    sample_prevalence_from_distribution,
    train_svc,
    transform_X,
    _labelfree_estimate,
)
from scipy.stats import binomtest

ROLE_FRACS = {"window": 0.5, "train": 0.3, "probe": 0.2}


class DDM:
    """Canonical Drift Detection Method (Gama et al., 2004) on a monitored error stream."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.n = 0; self.p = 0.0; self.p_min = np.inf; self.s_min = np.inf

    def update(self, err_rate: float, m: int) -> bool:
        # incorporate m Bernoulli observations with observed error rate err_rate
        for _ in range(m):
            self.n += 1
            self.p += (err_rate - self.p) / self.n
        s = np.sqrt(max(self.p * (1 - self.p), 1e-12) / max(self.n, 1))
        if self.n >= 30 and self.p + s < self.p_min + self.s_min:
            self.p_min, self.s_min = self.p, s
        return bool(self.n >= 30 and self.p + s > self.p_min + 3 * self.s_min)


class ADWIN:
    """Adaptive Windowing (Bifet & Gavalda, 2007), exact O(n^2) variant on window error rates."""
    def __init__(self, delta: float = 0.002):
        self.delta = delta; self.w: list[float] = []

    def reset(self):
        self.w = []

    def update(self, err_rate: float) -> bool:
        self.w.append(err_rate)
        n = len(self.w)
        if n < 6:
            return False
        for cut in range(3, n - 2):
            a, b = self.w[:cut], self.w[cut:]
            m_inv = 1 / len(a) + 1 / len(b)
            var = float(np.var(self.w))
            eps = np.sqrt(2 * m_inv * var * np.log(2 / self.delta)) + (2 / 3) * m_inv * np.log(2 / self.delta)
            if abs(float(np.mean(a)) - float(np.mean(b))) > eps:
                self.w = b
                return True
        return False


class EnsembleModel:
    """Soft incumbent+candidate ensemble (adaptive-update baseline)."""
    def __init__(self, a, b):
        self.a, self.b = a, b

    def _score(self, m, X):
        if hasattr(m, "predict_proba") and getattr(m, "probability", True):
            try:
                return m.predict_proba(X)[:, 1]
            except Exception:
                pass
        if hasattr(m, "decision_function"):
            d = m.decision_function(X)
            return 1 / (1 + np.exp(-d))
        return m.predict(X).astype(float)

    def predict(self, X):
        return ((self._score(self.a, X) + self._score(self.b, X)) / 2 >= 0.5).astype(int)


class EnsembleModelCal(EnsembleModel):
    """Calibrated soft ensemble (amendment 004): members are Platt-calibrated
    (SVC probability=True), and exposing predict_proba keeps nested ensembles
    probabilistic instead of degrading to hard votes."""
    def predict_proba(self, X):
        p1 = (self._score(self.a, X) + self._score(self.b, X)) / 2
        return np.column_stack([1 - p1, p1])


FUTURE_K = 5  # primary lookahead horizon for per-trigger delta-BA logging
FUTURE_HORIZONS = (1, 3, 5, 10)  # amendment 005: horizon-robust logging (logging ONLY)
LCB_ALPHA_Z = 1.2816  # one-sided 90% normal quantile


def cs_lower_bound(d, alpha, rho2):
    """Robbins normal-mixture LOWER confidence sequence for the mean of d in [-1,1].

    amendment 009. d is 1-sub-Gaussian on [-1,1] (sigma^2 <= 1). The mixture boundary
    (Howard, Ramdas, McAuliffe & Sekhon 2021, "Time-uniform Chernoff bounds") gives a
    lower bound that holds simultaneously for all sample sizes n:
        P( exists n : true_mean < LCB_n ) <= alpha.
    So a gate that commits only when LCB_n > 0 has harmful-commit probability
    P(commit | true_mean <= 0) <= alpha, uniformly over the inspection schedule -- a valid
    confidence sequence, not a repeatedly-inspected fixed-sample interval. rho2 tunes the
    mixture; set from the target probe size (predictable, fixed before seeing data)."""
    import numpy as _np
    n = len(d)
    if n == 0:
        return -_np.inf
    mean = float(_np.mean(d))
    s2 = 1.0  # sub-Gaussian variance proxy for the range [-1, 1]
    margin = _np.sqrt((2.0 * s2 * (n * rho2 + 1.0)) / (n * n * rho2)
                      * _np.log(_np.sqrt(n * rho2 + 1.0) / alpha))
    return mean - margin


def cs_lower_bound_eb(d, alpha):
    """Predictable-plug-in empirical-Bernstein LOWER confidence sequence for the mean of
    d in [-1,1] (Waudby-Smith & Ramdas 2023, "Estimating means of bounded random variables
    by betting"; Howard et al. 2021).

    amendment 010. Maps d to x=(d+1)/2 in [0,1] and returns a lower bound on E[d] that holds
    uniformly over all n: P(exists n : E[d] < LCB_n) <= alpha. Unlike the sub-Gaussian Robbins
    mixture (which must budget for the worst-case variance 1), this uses the EMPIRICAL variance
    of the correctness differences -- which are mostly ties (d=0), hence low-variance -- so the
    interval is far tighter and the gate can actually commit when a candidate is genuinely
    better, while still bounding the harmful-commit probability by alpha. Predictable betting
    fractions lambda_i and a 1/2, 1/4 prior on the running mean/variance keep it anytime-valid."""
    import numpy as _np
    x = (_np.asarray(d, float) + 1.0) / 2.0        # map [-1,1] -> [0,1]
    t = len(x)
    if t == 0:
        return -_np.inf
    loginv = _np.log(1.0 / alpha)
    num = den = s_x = s_v = 0.0
    for i in range(1, t + 1):
        muhat = (0.5 + s_x) / i                    # predictable mean (data before i)
        sighat = (0.25 + s_v) / i                  # predictable variance
        lam = min(0.75, _np.sqrt(2.0 * loginv / max(sighat * i * _np.log(i + 1), 1e-12)))
        xi = float(x[i - 1])
        v = (xi - muhat) ** 2
        psi = -_np.log(1.0 - lam) - lam            # psi_E(lambda)
        num += lam * xi - psi * v
        den += lam
        s_x += xi
        s_v += v
    lcb_x = (num - loginv) / den if den > 0 else -_np.inf
    return 2.0 * lcb_x - 1.0                        # convert E[x] bound to E[d] bound
HEALTH_REF_PER_CLASS = 32     # two_stage: severity-0 health reference size per class (64 labels)


def split_pools(pools: Pools, seed: int) -> dict[str, Pools]:
    """Deterministic per-seed split of every class pool into disjoint role partitions."""
    part_rng = np.random.default_rng(seed + 500_000)
    parts: dict[str, dict[str, np.ndarray]] = {r: {} for r in ROLE_FRACS}
    for name in ("ref_benign", "ref_attack", "cur_benign", "cur_attack"):
        pool = getattr(pools, name)
        idx = part_rng.permutation(len(pool))
        a = int(len(pool) * ROLE_FRACS["window"])
        b = a + int(len(pool) * ROLE_FRACS["train"])
        parts["window"][name] = pool[idx[:a]]
        parts["train"][name] = pool[idx[a:b]]
        parts["probe"][name] = pool[idx[b:]]
    return {role: Pools(**parts[role]) for role in ROLE_FRACS}


@dataclass
class Environment:
    """Everything shared across arms for one seed: transformer, initial model, stream."""
    scaler: object
    pca: object
    initial_model: object
    stream: list[tuple[np.ndarray, np.ndarray, float]]   # (X transformed, y, severity)
    cal_scores_pools: Pools                                # window pools (for recalibration)
    train_pools: Pools
    probe_pools: Pools
    init_train: tuple = None                               # (X_tr, y_tr) of the incumbent (amend 011)


def build_environment(pools: Pools, args, seed: int) -> Environment:
    role = split_pools(pools, seed)
    train_rng = np.random.default_rng(seed + 777)
    X_tr_raw, y_tr = sample_balanced_from_distribution(
        role["train"], n_per_class=args.train_size_per_class, severity=0.0, rng=train_rng)
    scaler, pca, X_tr = fit_transformer(X_tr_raw, args.dim, seed)
    needs_proba = args.adaptation_gate in ("atc", "doc") or args.adapt_strategy == "ensemble_cal"
    initial_model = train_svc(X_tr, y_tr, seed, args.downstream_model, proba=needs_proba)

    env_rng = np.random.default_rng(seed)  # environment: depends on seed ONLY
    stream = []
    if getattr(args, "stream_disjoint_windows", False):
        # amendment 011: draw every stream window WITHOUT replacement within the window pool, so
        # no original row appears in more than one window. Because the candidate (sliding_window)
        # and the observed probe are built from stream windows, and train/probe pools are already
        # ID-disjoint (split_pools), a candidate-training row can then never recur in a future
        # evaluation window -- eliminating the train/future-test overlap the reviewer flagged. The
        # stream still depends on seed + flag only, so it is bit-identical across arms.
        if args.stream_prevalence != 0.5:
            raise ValueError("stream_disjoint_windows currently supports balanced streams only")
        wp = role["window"]
        # dedup each window pool by VALUE first: the raw benchmarks contain distinct flows with
        # identical feature vectors (~9-16%), so index-disjoint alone would still let a training
        # row's VALUE recur downstream. Deduping makes each unique feature vector appear in at most
        # one window, so a candidate-training row can never recur (by value) in a future window.
        pool_arrays = {}
        for n in ("ref_benign", "ref_attack", "cur_benign", "cur_attack"):
            a = getattr(wp, n)
            _, uq = np.unique(a, axis=0, return_index=True)
            pool_arrays[n] = a[np.sort(uq)]
        cur = {n: [pool_arrays[n], env_rng.permutation(len(pool_arrays[n])), 0]
               for n in pool_arrays}
        npc = args.window_size // 2

        def take(name, n):
            arr, order, pos = cur[name]
            if n <= 0:
                return arr[order[:0]]
            if pos + n > len(order):                 # pool exhausted: reshuffle (should not happen
                order = env_rng.permutation(len(arr))  # for the causal full/mild runs; pools >> need)
                cur[name][1] = order; pos = 0
            cur[name][2] = pos + n
            return arr[order[pos:pos + n]]

        for t in range(args.post_windows):
            sev = float(np.clip(progressive_severity(t, args), 0.0, 1.0))
            n_cur = int(round(npc * sev)); n_ref = npc - n_cur
            X = np.vstack([take("ref_benign", n_ref), take("cur_benign", n_cur),
                           take("ref_attack", n_ref), take("cur_attack", n_cur)])
            y = np.array([0] * npc + [1] * npc)
            perm = env_rng.permutation(len(y))
            stream.append((transform_X(X[perm], scaler, pca), y[perm], sev))
        return Environment(scaler, pca, initial_model, stream, role["window"], role["train"], role["probe"], (X_tr, y_tr))
    for t in range(args.post_windows):
        sev = progressive_severity(t, args)
        if args.stream_prevalence != 0.5:
            Xw_raw, yw = sample_prevalence_from_distribution(
                role["window"], n_total=args.window_size, attack_frac=args.stream_prevalence,
                severity=sev, rng=env_rng)
        else:
            Xw_raw, yw = sample_balanced_from_distribution(
                role["window"], n_per_class=args.window_size // 2, severity=sev, rng=env_rng)
        stream.append((transform_X(Xw_raw, scaler, pca), yw, sev))
    return Environment(scaler, pca, initial_model, stream, role["window"], role["train"], role["probe"], (X_tr, y_tr))


def calibrate(detector, env: Environment, severity: float, args, rng) -> tuple[object, float]:
    """Reference from TRAIN pools; calibration scores on dedicated WINDOW-pool draws.
    Reference and calibration windows follow the stream's operating prevalence, so a
    natural-prevalence deployment is calibrated at natural prevalence (review point)."""
    prev = args.stream_prevalence
    if prev != 0.5:
        X_ref_raw, _ = sample_prevalence_from_distribution(
            env.train_pools, n_total=2 * args.detector_ref_size_per_class, attack_frac=prev,
            severity=severity, rng=rng)
    else:
        X_ref_raw, _ = sample_balanced_from_distribution(
            env.train_pools, n_per_class=args.detector_ref_size_per_class, severity=severity, rng=rng)
    detector.fit(transform_X(X_ref_raw, env.scaler, env.pca))
    scores = []
    for _ in range(args.calibration_windows):
        if prev != 0.5:
            Xc_raw, _ = sample_prevalence_from_distribution(
                env.cal_scores_pools, n_total=args.window_size, attack_frac=prev,
                severity=severity, rng=rng)
        else:
            Xc_raw, _ = sample_balanced_from_distribution(
                env.cal_scores_pools, n_per_class=args.window_size // 2, severity=severity, rng=rng)
        scores.append(float(detector.score(transform_X(Xc_raw, env.scaler, env.pca))))
    return detector, float(np.quantile(scores, args.threshold_quantile))


def calibrate_observed(detector, seen: list[tuple[np.ndarray, np.ndarray]], args):
    """Amendment 007: post-commit recalibration from OBSERVED traffic only.

    The reference is built from the last 8 observed windows (the rows the candidate itself
    trained on -- a deployment has them), and the threshold is the 0.95 quantile of the
    detector's scores on the preceding observed windows scored against that reference.
    Reads no severity and touches no pool. The `pools` path (calibrate) remains the default
    so every pre-amendment-007 run reproduces bit-for-bit.
    """
    ref = np.vstack([x for x, _ in seen[-8:]])
    detector.fit(ref)
    hist = seen[-(8 + args.calibration_windows):-8]
    scores = [float(detector.score(x)) for x, _ in hist]
    if not scores:                       # too early in the stream: fall back to the ref windows
        scores = [float(detector.score(x)) for x, _ in seen[-8:]]
    return detector, float(np.quantile(scores, args.threshold_quantile))


def run_arm(method: str, env: Environment, args, seed: int):
    """One (detector, gate) arm over the shared pre-generated stream."""
    detector = build_detector(method, args, seed)
    detector, threshold = calibrate(detector, env, 0.0, args,
                                    np.random.default_rng(seed + 888))
    model = env.initial_model
    alarms: list[bool] = []
    cooldown = 0
    n_adapt = n_trig = n_reject = labels_used = 0
    labels_probe = labels_monitor = labels_candidate = 0   # amendment 004 accounting
    n_cand_trained = n_skip_train = 0
    probe_zero_attack = n_probes = 0                       # amendment 006 (honest prevalence)
    probe_row_collisions = 0                               # amendment 007 (row-identity audit)
    probe_labels_seq: list[int] = []                       # amendment 007 (sequential gate)
    cand_future_collisions = 0                             # amendment 008 (train/future-eval audit)
    cand_rows_total = cand_unique_total = 0                # amendment 011 (unique-row accounting)
    # amendment 008: exact feature identity of every future evaluation window's rows, so we can
    # both AUDIT candidate-training overlap with the future and (optionally) drop it
    future_row_sets = [ {r.tobytes() for r in np.ascontiguousarray(Xf)} for Xf, _, _ in env.stream ]
    adapt_windows: list[int] = []
    ba_hist: list[float] = []
    rows, trig_rows = [], []
    gate = args.adaptation_gate
    needs_proba = gate in ("atc", "doc")
    wants_proba = needs_proba or args.adapt_strategy == "ensemble_cal"
    incumbent_val = None
    if needs_proba:
        Xv_raw, yv = sample_balanced_from_distribution(
            env.train_pools, n_per_class=max(1, args.gate_val_size // 2), severity=0.0,
            rng=np.random.default_rng(seed + 999))
        incumbent_val = (transform_X(Xv_raw, env.scaler, env.pca), yv)

    def draw_probe(t: int, sev_probe: float):
        """Probe draw. With default flags this reproduces the original draw bit-for-bit.
        Amendment 004: --probe-latency / --probe-flip-frac. Amendment 006:
          --probe-source observed : 32 rows sampled uniformly from the OBSERVED window t-9
              (strictly past, disjoint from the sliding-window candidate's training windows,
              whatever class composition that window has). Reads no severity, no pools.
          --probe-prevalence p    : pool probe whose attack count is Binomial(b, p) --- zero
              attacks allowed (honest random inspection at prevalence p).
        """
        probe_rng = np.random.default_rng(seed * 200_003 + t)
        if args.probe_source == "observed":
            nonlocal probe_row_collisions
            k = t - 9
            if k < 0 or k >= len(seen):
                return None
            Xw_obs, yw_obs = seen[k]
            # amendment 007: ROW-IDENTITY disjointness. Stream windows are drawn from the pools
            # with replacement, so the same pool row can appear both here and in the candidate's
            # training windows (window-disjoint is not row-disjoint). Exclude, by exact
            # feature-vector identity, every row that also occurs in those eight windows.
            train_rows = np.vstack([x for x, _ in seen[-8:]])
            train_set = {r.tobytes() for r in np.ascontiguousarray(train_rows)}
            keep = np.array([r.tobytes() not in train_set
                             for r in np.ascontiguousarray(Xw_obs)], dtype=bool)
            probe_row_collisions += int((~keep).sum())
            pool_idx = np.where(keep)[0]
            if len(pool_idx) < 8:                     # cannot form an informative probe
                return None
            idx = probe_rng.choice(pool_idx, min(args.probe_size, len(pool_idx)), replace=False)
            return Xw_obs[idx], np.asarray(yw_obs)[idx].copy()
        if args.probe_prevalence is not None:
            Xp_raw, yp = sample_binomial_prevalence(
                env.probe_pools, n_total=args.probe_size, attack_frac=args.probe_prevalence,
                severity=sev_probe, rng=probe_rng)
        else:
            Xp_raw, yp = sample_balanced_from_distribution(
                env.probe_pools, n_per_class=max(1, args.probe_size // 2),
                severity=sev_probe, rng=probe_rng)
        yp = np.asarray(yp).copy()
        if args.probe_flip_frac > 0:
            flip_rng = np.random.default_rng(seed * 500_009 + t)
            k = int(round(args.probe_flip_frac * len(yp)))
            if k:
                fi = flip_rng.choice(len(yp), k, replace=False)
                yp[fi] = 1 - yp[fi]
        return transform_X(Xp_raw, env.scaler, env.pca), yp

    # two_stage gate: severity-0 health reference for the incumbent (64 labels, once per arm)
    health_ref = None
    if gate == "two_stage":
        hr_rng = np.random.default_rng(seed + 887)
        Xh_raw, yh = sample_balanced_from_distribution(
            env.probe_pools, n_per_class=HEALTH_REF_PER_CLASS, severity=0.0, rng=hr_rng)
        Xh = transform_X(Xh_raw, env.scaler, env.pca)
        health_ref = float((model.predict(Xh) == yh).mean())
        labels_probe += 2 * HEALTH_REF_PER_CLASS
        labels_used += 2 * HEALTH_REF_PER_CLASS

    # canonical performance-aware monitors (labels spent on MONITORING the incumbent's error)
    ddm = DDM() if args.trigger_mode == "ddm" else None
    adwin = ADWIN() if args.trigger_mode == "adwin" else None
    riv = None   # reference implementations (river), amendment 004 validation
    if args.trigger_mode in ("ddm_river", "adwin_river"):
        from river import drift as river_drift
        riv = (river_drift.binary.DDM() if args.trigger_mode == "ddm_river"
               else river_drift.ADWIN(delta=0.002))
    # per-arm history of observed stream windows (for sliding-window retraining)
    seen: list[tuple[np.ndarray, np.ndarray]] = []
    # legacy custom performance trigger
    perf_thr, err_hist = None, []
    if args.trigger_mode == "performance":
        mc_rng = np.random.default_rng(seed + 889)
        errs = []
        for _ in range(args.calibration_windows):
            Xm_raw, ym = sample_balanced_from_distribution(
                env.probe_pools, n_per_class=max(1, args.monitor_labels // 2), severity=0.0, rng=mc_rng)
            Xm = transform_X(Xm_raw, env.scaler, env.pca)
            errs.append(1.0 - float((model.predict(Xm) == ym).mean()))
        perf_thr = float(np.mean(errs) + 3.0 * (np.std(errs) if np.std(errs) > 0 else 0.02))

    for t, (Xw, yw, sev) in enumerate(env.stream):
        m = evaluate_model(model, Xw, yw)
        pred = model.predict(Xw)
        fp = int(((pred == 1) & (yw == 0)).sum()); tn = int(((pred == 0) & (yw == 0)).sum())
        m["fpr"] = fp / max(1, fp + tn)
        m["recall"] = float(((pred == 1) & (yw == 1)).sum() / max(1, (yw == 1).sum()))
        m["alerts"] = int((pred == 1).sum())
        ba_hist.append(m["balanced_accuracy"])
        score = float(detector.score(Xw))
        if args.trigger_mode in ("performance", "ddm", "adwin", "ddm_river", "adwin_river"):
            mon_rng = np.random.default_rng(seed * 400_009 + t)
            Xm_raw, ym = sample_balanced_from_distribution(
                env.probe_pools, n_per_class=max(1, args.monitor_labels // 2), severity=sev, rng=mon_rng)
            Xm = transform_X(Xm_raw, env.scaler, env.pca)
            err = 1.0 - float((model.predict(Xm) == ym).mean())
            labels_used += args.monitor_labels
            labels_monitor += args.monitor_labels
            if args.trigger_mode == "ddm":
                alarms.append(ddm.update(err, args.monitor_labels))
            elif args.trigger_mode == "adwin":
                alarms.append(adwin.update(err))
            elif args.trigger_mode in ("ddm_river", "adwin_river"):
                # reference implementations receive the SAME monitoring labels as
                # INDIVIDUAL Bernoulli outcomes (their canonical input granularity)
                fired = False
                for e in (model.predict(Xm) != ym):
                    riv.update(bool(e) if args.trigger_mode == "ddm_river" else int(e))
                    fired = fired or bool(riv.drift_detected)
                alarms.append(fired)
            else:
                err_hist.append(err)
                alarms.append(len(err_hist) >= 1 and float(np.mean(err_hist[-3:])) > perf_thr)
        elif args.trigger_mode == "random":
            # amendment 007 control: triggers fired at a fixed rate, independent of any drift
            # signal (isolates "harm from replacing a model" from "harm from drift")
            alarms.append(bool(np.random.default_rng(seed * 700_001 + t).random() < args.trigger_prob))
        else:
            alarms.append(score > threshold)
        if args.trigger_mode in ("ddm", "adwin", "ddm_river", "adwin_river", "random"):
            trigger = bool(alarms[-1]) and cooldown <= 0   # self-confirming triggers
        else:
            recent = alarms[-args.consecutive_k:]
            trigger = len(recent) == args.consecutive_k and all(recent) and cooldown <= 0
        seen.append((Xw, yw))
        adapted = False
        if trigger:
            n_trig += 1
            # --probe-latency L: the probe reflects the stream as of window t-L (stale labels)
            sev_probe = env.stream[max(0, t - args.probe_latency)][2] if args.probe_latency > 0 else sev

            # two_stage gate (amendment 004): FIRST spend the probe on the incumbent alone;
            # train a candidate only if the incumbent's probe accuracy fell >= TWO_STAGE_DELTA
            # below its severity-0 health reference. Skipping saves ALL candidate labels/compute.
            probe = None
            skip_train = False
            inc_hacc = np.nan
            if gate == "two_stage":
                # amendment 005: the 32-label draw is PARTITIONED per class into a health
                # half and a commit half; no sample feeds both decisions (the amendment-004
                # variant reused the full probe, inducing selection optimism)
                Xp_all, yp_all = draw_probe(t, sev_probe)
                labels_used += len(yp_all); labels_probe += len(yp_all)
                h_idx, c_idx = [], []
                for cls in (0, 1):
                    ci = np.where(yp_all == cls)[0]
                    h_idx.extend(ci[: len(ci) // 2]); c_idx.extend(ci[len(ci) // 2:])
                h_idx, c_idx = np.asarray(h_idx), np.asarray(c_idx)
                inc_hacc = float((model.predict(Xp_all[h_idx]) == yp_all[h_idx]).mean())
                skip_train = bool(inc_hacc >= health_ref - args.two_stage_delta)
                probe = (Xp_all[c_idx], yp_all[c_idx])

            candidate = None
            commit, cand_val = True, None
            p_inc = p_cand = np.nan
            if skip_train:
                commit = False
                n_skip_train += 1
                p_inc = inc_hacc
            else:
                cand_rng = np.random.default_rng(seed * 100_003 + t)
                svc_C = 1.0  # amendment 011: cumulative `cn` control may override below
                if args.adapt_strategy == "sliding_window":
                    # retrain on the last 8 OBSERVED (already-seen, labeled) stream windows
                    hist = seen[-8:]
                    Xa = np.vstack([x for x, _ in hist]); ya = np.concatenate([y for _, y in hist])
                elif args.adapt_strategy == "cumulative":
                    # amendment 009: candidate trains on ALL observed (labeled) windows so far,
                    # not only the last 8 -- the "use every available data point" generator.
                    # amendment 011 adds controls (--cumulative-mode) requested by review:
                    #   observed             = all observed windows (a009 default);
                    #   initial_plus_observed= incumbent's initial training set + all observed;
                    #   dedup                = row-identity dedup before fit;
                    #   cn                   = C scaled ~ n_unique/512 so effective regularization
                    #                          is not silently changed as the set grows (SVC only).
                    hist = seen if len(seen) else [seen[-1]]
                    Xa = np.vstack([x for x, _ in hist]); ya = np.concatenate([y for _, y in hist])
                    if args.cumulative_mode == "initial_plus_observed" and env.init_train is not None:
                        Xa = np.vstack([env.init_train[0], Xa])
                        ya = np.concatenate([env.init_train[1], ya])
                    if args.cumulative_mode in ("dedup", "cn"):
                        _, uq = np.unique(Xa, axis=0, return_index=True)
                        uq = np.sort(uq); Xa, ya = Xa[uq], ya[uq]
                    if args.cumulative_mode == "cn":
                        svc_C = max(1e-3, len(np.unique(Xa, axis=0)) / float(args.train_size_per_class))
                elif args.adapt_strategy == "replay":
                    # amendment 009: retrain on a current-severity sample plus an equal-size
                    # replay from the reference (severity-0) regime, 50/50 (mirrors Phase 2i's
                    # replay, but inside the v2 causal-capable harness).
                    n_half = max(1, args.adapt_size_per_class // 2)
                    Xc_raw, yc = sample_balanced_from_distribution(
                        env.train_pools, n_per_class=n_half, severity=sev, rng=cand_rng)
                    Xr_raw, yr = sample_balanced_from_distribution(
                        env.train_pools, n_per_class=n_half, severity=0.0, rng=cand_rng)
                    Xa = np.vstack([transform_X(Xc_raw, env.scaler, env.pca),
                                    transform_X(Xr_raw, env.scaler, env.pca)])
                    ya = np.concatenate([yc, yr])
                else:
                    Xa_raw, ya = sample_balanced_from_distribution(
                        env.train_pools, n_per_class=args.adapt_size_per_class, severity=sev, rng=cand_rng)
                    Xa = transform_X(Xa_raw, env.scaler, env.pca)

                if gate == "labeled_probe_holdout":
                    # carve the probe out of the labeled training batch (zero incremental labels).
                    # Deduplicate first: with-replacement draws can place copies of one flow in
                    # both halves; training proceeds on rows that are identity-disjoint from the
                    # held-out probe.
                    _, uniq = np.unique(Xa, axis=0, return_index=True)
                    uniq = np.sort(uniq)
                    Xa, ya = Xa[uniq], ya[uniq]
                    nb = max(1, args.probe_size // 2)
                    ben = np.where(ya == 0)[0][:nb]
                    att = np.where(ya == 1)[0][:nb]
                    hold = np.concatenate([ben, att])
                    mask = np.ones(len(ya), bool); mask[hold] = False
                    probe = (Xa[hold], ya[hold])
                    Xa, ya = Xa[mask], ya[mask]
                candidate = train_svc(Xa, ya, seed + t + 1, args.downstream_model,
                                      proba=wants_proba, C=svc_C)
                n_cand_trained += 1
                labels_candidate += int(len(ya))
                if args.adapt_strategy == "cumulative":   # amendment 011: unique-row accounting
                    cand_rows_total += int(len(ya))
                    cand_unique_total += int(len(np.unique(Xa, axis=0)))

                if gate == "labeled_probe_seq":
                    # amendment 007: sequential probe. Buy labels in blocks of 16 and stop as
                    # soon as the one-sided 90% CI of the per-flow correctness difference
                    # resolves the sign; only near-ties cost the full budget. The McNemar result
                    # showed the label budget is the binding constraint -- this spends it where
                    # it matters instead of uniformly.
                    Xp_all, yp_all = draw_probe(t, sev_probe) or (None, None)
                    if Xp_all is None:
                        commit = True
                    else:
                        spent = 0
                        commit = None
                        while spent < min(args.probe_size, len(yp_all)):
                            spent = min(spent + args.seq_block, len(yp_all))
                            Xs_, ys_ = Xp_all[:spent], yp_all[:spent]
                            d = ((candidate.predict(Xs_) == ys_).astype(float)
                                 - (model.predict(Xs_) == ys_).astype(float))
                            se = float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else np.inf
                            if np.isfinite(se) and se > 0:
                                if d.mean() - LCB_ALPHA_Z * se > 0:
                                    commit = True; break
                                if d.mean() + LCB_ALPHA_Z * se < 0:
                                    commit = False; break
                            elif d.mean() != 0:      # zero variance: the sign is unambiguous
                                commit = bool(d.mean() > 0); break
                        p_inc = float((model.predict(Xp_all[:spent]) == yp_all[:spent]).mean())
                        p_cand = float((candidate.predict(Xp_all[:spent]) == yp_all[:spent]).mean())
                        if commit is None:           # never resolved: fall back to the point rule
                            commit = bool(p_cand >= p_inc)
                        labels_used += spent; labels_probe += spent
                        probe_labels_seq.append(spent)
                        n_probes += 1
                        probe_zero_attack += int(not np.any(yp_all[:spent] == 1))
                elif gate in ("labeled_probe", "labeled_probe_lcb", "labeled_probe_holdout",
                              "two_stage", "labeled_probe_mcnemar", "labeled_probe_seqav",
                              "labeled_probe_cs", "labeled_probe_ebcs"):
                    if probe is None:
                        probe = draw_probe(t, sev_probe)
                        if probe is None:      # observed-source probe not available yet (t < 9)
                            commit = True      # no evidence: behave as the naive loop
                            probe = (np.empty((0, Xa.shape[1])), np.empty(0, int))
                        else:
                            labels_used += len(probe[1]); labels_probe += len(probe[1])
                    Xp, yp = probe
                    if len(yp) == 0:
                        pass                   # commit already set (no probe available)
                    elif gate == "labeled_probe_lcb":
                        d = (candidate.predict(Xp) == yp).astype(float) - (model.predict(Xp) == yp).astype(float)
                        se = float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else np.inf
                        commit = bool(d.mean() - LCB_ALPHA_Z * se > 0.0)
                        p_inc, p_cand = float((model.predict(Xp) == yp).mean()), float((candidate.predict(Xp) == yp).mean())
                    elif gate == "labeled_probe_mcnemar":
                        # amendment 006: commit only on statistically resolved superiority
                        # (exact one-sided McNemar on discordant pairs); ties never commit.
                        ci = (model.predict(Xp) == yp)
                        cc = (candidate.predict(Xp) == yp)
                        b = int(np.sum(~cc & ci))   # candidate wrong, incumbent right
                        c = int(np.sum(cc & ~ci))   # candidate right, incumbent wrong
                        p_inc, p_cand = float(ci.mean()), float(cc.mean())
                        commit = bool(b + c > 0 and
                                      binomtest(c, b + c, 0.5, alternative="greater").pvalue
                                      <= args.mcnemar_alpha)
                    elif gate == "labeled_probe_seqav":
                        # amendment 008: ANYTIME-VALID sequential test. Look at 16/32/48/64
                        # flows; each of the K=4 looks tests at alpha/K (Bonferroni over looks),
                        # so the family-wise error is controlled and stopping is valid. Commit
                        # on a resolved positive LCB, reject on a resolved negative UCB;
                        # undecided at 64 -> reject (risk-averse default).
                        from scipy.stats import norm
                        K = max(1, args.probe_size // args.seq_block)
                        z = float(norm.ppf(1 - args.seqav_alpha / K))
                        commit = False
                        seen_n = 0
                        while seen_n < len(yp):
                            seen_n = min(seen_n + args.seq_block, len(yp))
                            dd = ((candidate.predict(Xp[:seen_n]) == yp[:seen_n]).astype(float)
                                  - (model.predict(Xp[:seen_n]) == yp[:seen_n]).astype(float))
                            se = float(dd.std(ddof=1) / np.sqrt(len(dd))) if len(dd) > 1 else np.inf
                            if np.isfinite(se) and se > 0:
                                if dd.mean() - z * se > 0:
                                    commit = True; break
                                if dd.mean() + z * se < 0:
                                    commit = False; break
                            elif dd.mean() != 0:
                                commit = bool(dd.mean() > 0); break
                        p_inc = float((model.predict(Xp[:seen_n]) == yp[:seen_n]).mean())
                        p_cand = float((candidate.predict(Xp[:seen_n]) == yp[:seen_n]).mean())
                        probe_labels_seq.append(seen_n)
                    elif gate == "labeled_probe_cs":
                        # amendment 009: a genuine anytime-valid CONFIDENCE SEQUENCE (Robbins
                        # normal-mixture, Howard et al. 2021) on the per-flow correctness
                        # difference d in [-1,1]. The lower CS holds UNIFORMLY over all n, so
                        # committing only when it exceeds 0 bounds the harmful-commit probability
                        # P(commit | mean d <= 0) <= seqav-alpha at EVERY inspection point -- the
                        # explicit risk control the reviewer asked for, unlike repeated
                        # fixed-sample intervals (optional stopping). Risk-averse default: no commit.
                        d = ((candidate.predict(Xp) == yp).astype(float)
                             - (model.predict(Xp) == yp).astype(float))
                        commit = False
                        n_look = 0
                        while n_look < len(d):
                            n_look = min(n_look + args.seq_block, len(d))
                            if cs_lower_bound(d[:n_look], args.seqav_alpha,
                                              rho2=1.0 / max(1, args.probe_size)) > 0.0:
                                commit = True; break
                        p_inc = float((model.predict(Xp) == yp).mean())
                        p_cand = float((candidate.predict(Xp) == yp).mean())
                        probe_labels_seq.append(n_look)
                    elif gate == "labeled_probe_ebcs":
                        # amendment 010: the same anytime-valid guarantee, but a TIGHTER
                        # predictable-plug-in empirical-Bernstein confidence sequence (Waudby-Smith
                        # & Ramdas 2023) that uses the empirical variance of the correctness
                        # differences. Because those differences are mostly ties, the interval is
                        # far tighter than the sub-Gaussian Robbins CS, so the gate keeps the same
                        # alpha-uniform harmful-commit bound yet can actually commit when the
                        # candidate is genuinely better. Sequential looks; risk-averse default.
                        d = ((candidate.predict(Xp) == yp).astype(float)
                             - (model.predict(Xp) == yp).astype(float))
                        commit = False
                        n_look = 0
                        while n_look < len(d):
                            n_look = min(n_look + args.seq_block, len(d))
                            if cs_lower_bound_eb(d[:n_look], args.seqav_alpha) > 0.0:
                                commit = True; break
                        p_inc = float((model.predict(Xp) == yp).mean())
                        p_cand = float((candidate.predict(Xp) == yp).mean())
                        probe_labels_seq.append(n_look)
                    else:
                        # balanced-accuracy comparison where both classes are present; plain
                        # accuracy otherwise (observed / binomial-prevalence probes may be
                        # single-class -- amendment 006 reports this honestly rather than
                        # forcing a minority-class flow into the probe)
                        if len(np.unique(yp)) == 2:
                            p_inc = evaluate_model(model, Xp, yp)["balanced_accuracy"]
                            p_cand = evaluate_model(candidate, Xp, yp)["balanced_accuracy"]
                        else:
                            p_inc = float((model.predict(Xp) == yp).mean())
                            p_cand = float((candidate.predict(Xp) == yp).mean())
                        commit = bool(p_cand >= p_inc + args.gate_margin)
                    if len(yp):
                        probe_zero_attack += int(not np.any(yp == 1))
                        n_probes += 1
                elif gate == "unsup_disagree":
                    commit = bool(float(np.mean(model.predict(Xw) != candidate.predict(Xw)))
                                  >= args.gate_disagree_threshold)
                elif gate in ("atc", "doc"):
                    Xv_raw, yv = sample_balanced_from_distribution(
                        env.train_pools, n_per_class=max(1, args.gate_val_size // 2), severity=sev,
                        rng=np.random.default_rng(seed * 300_007 + t))
                    cand_val = (transform_X(Xv_raw, env.scaler, env.pca), yv)
                    commit = bool(_labelfree_estimate(gate, candidate, cand_val, Xw)
                                  >= _labelfree_estimate(gate, model, incumbent_val, Xw) + args.gate_margin)
                elif gate != "none":
                    raise ValueError(f"Unknown gate: {gate}")

            # per-trigger mechanism log (lookahead is for LOGGING only, never for the policy);
            # amendment 005 logs every horizon in FUTURE_HORIZONS (h=5 keeps the legacy names)
            fut10 = env.stream[t + 1: t + 1 + max(FUTURE_HORIZONS)]
            inc_seq = [evaluate_model(model, Xf, yf)["balanced_accuracy"] for Xf, yf, _ in fut10]
            cand_seq = ([evaluate_model(candidate, Xf, yf)["balanced_accuracy"] for Xf, yf, _ in fut10]
                        if candidate is not None else [])
            trow = dict(
                seed=seed, method=method, gate=gate, window_idx=t, severity_t=sev,
                score=score, threshold=threshold,
                deg_pre5=float(np.mean(ba_hist[-6:-1])) if len(ba_hist) > 1 else np.nan,
                probe_inc=p_inc, probe_cand=p_cand, committed=bool(commit),
                trained=bool(candidate is not None))
            for h in FUTURE_HORIZONS:
                inc_h = float(np.mean(inc_seq[:h])) if inc_seq else np.nan
                cand_h = float(np.mean(cand_seq[:h])) if cand_seq else np.nan
                trow[f"inc_future{h}"] = inc_h
                trow[f"cand_future{h}"] = cand_h
                trow[f"delta_future{h}"] = cand_h - inc_h if (inc_seq and cand_seq) else np.nan
            trig_rows.append(trow)

            if commit:
                n_adapt += 1
                adapt_windows.append(t)
                adapted = True
                # amendment 008: audit candidate-training rows that recur in FUTURE evaluation
                # windows (the pools are sampled with replacement, so a training row can be
                # scored again). Logging only; reported as evidence the effect is negligible.
                if args.adapt_strategy == "sliding_window" and candidate is not None:
                    train_ids = {r.tobytes() for x, _ in seen[-8:]
                                 for r in np.ascontiguousarray(x)}
                    for fset in future_row_sets[t + 1:]:
                        cand_future_collisions += len(train_ids & fset)
                if args.adapt_strategy == "ensemble":
                    model = EnsembleModel(model, candidate)
                elif args.adapt_strategy == "ensemble_cal":
                    model = EnsembleModelCal(model, candidate)
                else:
                    model = candidate
                if ddm is not None:
                    ddm.reset()
                if adwin is not None:
                    adwin.reset()
                if riv is not None:
                    riv = riv.clone()
                if cand_val is not None:
                    incumbent_val = cand_val
                if gate == "two_stage" and args.health_ref_mode == "per_incumbent":
                    # amendment 006: the health reference belongs to the DEPLOYED model, so it
                    # is reset to the new incumbent's accuracy on the (already labeled) commit
                    # half -- zero extra labels. Under `static` it keeps the initial model's
                    # severity-0 reference (the amendment-005 behaviour), which drifts away
                    # from the incumbent after the first commit.
                    if len(probe[1]):
                        health_ref = float((model.predict(probe[0]) == probe[1]).mean())
                detector = build_detector(method, args, seed + t + 1)
                if args.recal_source == "observed":
                    # amendment 007: recalibrate from observed traffic only (no sev, no pools)
                    detector, threshold = calibrate_observed(detector, seen, args)
                else:
                    detector, threshold = calibrate(detector, env, sev, args,
                                                    np.random.default_rng(seed * 1_000 + 999 + t))
            else:
                n_reject += 1
            alarms = []
            cooldown = args.cooldown_windows
        else:
            cooldown = max(0, cooldown - 1)

        rows.append(dict(seed=seed, method=method, window_idx=t, severity_t=sev,
                         balanced_accuracy=m["balanced_accuracy"], f1=m["f1"],
                         fpr=m["fpr"], recall=m["recall"], alerts=m["alerts"],
                         score=score, threshold=threshold, alarm=bool(alarms[-1]) if alarms else False,
                         trigger=bool(trigger), adapted_now=bool(adapted)))

    summary = dict(seed=seed, method=method, n_windows=args.post_windows, n_adaptations=n_adapt,
                   n_triggers=n_trig, n_gate_rejections=n_reject, labels_used_total=labels_used,
                   labels_probe=labels_probe, labels_monitor=labels_monitor,
                   labels_candidate=labels_candidate, n_candidates_trained=n_cand_trained,
                   n_train_skipped=n_skip_train,
                   n_probes=n_probes, n_probes_zero_attack=probe_zero_attack,
                   probe_row_collisions=probe_row_collisions,
                   cand_future_collisions=cand_future_collisions,
                   cand_rows_total=cand_rows_total, cand_unique_total=cand_unique_total,
                   seq_labels_mean=float(np.mean(probe_labels_seq)) if probe_labels_seq else np.nan,
                   adaptation_gate=gate, harness="v2",
                   first_adaptation_window=adapt_windows[0] if adapt_windows else np.nan,
                   mean_balanced_accuracy=float(np.mean([r["balanced_accuracy"] for r in rows])),
                   mean_f1=float(np.mean([r["f1"] for r in rows])))
    return rows, trig_rows, summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-ref", type=Path, required=True)
    p.add_argument("--data-cur", type=Path, required=True)
    p.add_argument("--label-col", type=str, default="Label")
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--seeds", type=str, default="101")
    p.add_argument("--methods", type=str, default="ks_max")
    p.add_argument("--dim", type=int, default=8)
    p.add_argument("--window-size", type=int, default=128)
    p.add_argument("--train-size-per-class", type=int, default=2000)
    p.add_argument("--adapt-size-per-class", type=int, default=512)
    p.add_argument("--detector-ref-size-per-class", type=int, default=256)
    p.add_argument("--post-windows", type=int, default=100)
    p.add_argument("--ramp-windows", type=int, default=80)
    p.add_argument("--max-severity", type=float, default=1.0)
    p.add_argument("--calibration-windows", type=int, default=30)
    p.add_argument("--threshold-quantile", type=float, default=0.95)
    p.add_argument("--consecutive-k", type=int, default=3)
    p.add_argument("--cooldown-windows", type=int, default=10)
    p.add_argument("--adaptation-gate", type=str, default="none",
                   choices=["none", "labeled_probe", "labeled_probe_holdout", "labeled_probe_lcb",
                            "labeled_probe_mcnemar", "labeled_probe_seq", "labeled_probe_seqav",
                            "labeled_probe_cs", "labeled_probe_ebcs", "unsup_disagree",
                            "atc", "doc", "two_stage"])
    p.add_argument("--seqav-alpha", type=float, default=0.10,
                   help="labeled_probe_seqav: family-wise alpha, split across looks (Bonferroni).")
    p.add_argument("--recal-source", type=str, default="pools", choices=["pools", "observed"],
                   help="observed = rebuild the post-commit detector reference/threshold from "
                        "observed windows only (no severity, no pools).")
    p.add_argument("--seq-block", type=int, default=16,
                   help="labeled_probe_seq: probe labels bought per sequential block.")
    p.add_argument("--trigger-prob", type=float, default=0.05,
                   help="trigger-mode random: per-window trigger probability (drift-independent).")
    p.add_argument("--probe-source", type=str, default="pools", choices=["pools", "observed"],
                   help="observed = 32 rows of the OBSERVED window t-9 (no severity, no pools, "
                        "natural composition); pools = simulator sample at the true severity.")
    p.add_argument("--probe-prevalence", type=float, default=None,
                   help="Pool probe with attack count ~ Binomial(b, p); zero attacks allowed.")
    p.add_argument("--health-ref-mode", type=str, default="static",
                   choices=["static", "per_incumbent"],
                   help="two_stage: recalibrate the health reference on each commit.")
    p.add_argument("--mcnemar-alpha", type=float, default=0.05)
    p.add_argument("--gate-val-size", type=int, default=256)
    p.add_argument("--probe-size", type=int, default=32)
    p.add_argument("--probe-latency", type=int, default=0,
                   help="Probe reflects the stream as of window t-L (stale validation labels).")
    p.add_argument("--probe-flip-frac", type=float, default=0.0,
                   help="Fraction of probe labels flipped after drawing (label-noise robustness).")
    p.add_argument("--two-stage-delta", type=float, default=0.05,
                   help="two_stage gate: train a candidate only if incumbent health-half "
                        "accuracy fell >= delta below the severity-0 reference.")
    p.add_argument("--gate-margin", type=float, default=0.0)
    p.add_argument("--gate-disagree-threshold", type=float, default=0.15)
    p.add_argument("--downstream-model", type=str, default="svc_rbf",
                   choices=["svc_rbf", "random_forest", "logreg", "mlp"])
    # quantum detector knobs (parsed by build_detector)
    p.add_argument("--ks-reduction", type=str, default="max", choices=["max", "mean"])
    p.add_argument("--jsd-bins", type=int, default=16)
    p.add_argument("--energy-reduction", type=str, default="mean", choices=["mean", "max"])
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--n-permutations", type=int, default=0)
    p.add_argument("--q-reps", type=int, default=1)
    p.add_argument("--q-input-scaling", type=str, default="atan_standard")
    p.add_argument("--adaptation-policy", type=str, default="consecutive")
    p.add_argument("--policy-k", type=int, default=None)
    p.add_argument("--policy-n", type=int, default=None)
    p.add_argument("--policy-name", type=str, default=None)
    p.add_argument("--adapt-strategy", type=str, default="full_replace",
                   choices=["full_replace", "ensemble", "ensemble_cal", "sliding_window",
                            "cumulative", "replay"],
                   help="Update rule on commit: replace the incumbent, soft incumbent+candidate "
                        "ensemble (ensemble_cal = Platt-calibrated members, probabilistic "
                        "nesting), retrain on the last 8 observed stream windows, cumulative "
                        "(retrain on ALL observed windows), or replay (current-severity sample "
                        "+ equal-size severity-0 reference replay, 50/50).")
    p.add_argument("--trigger-mode", type=str, default="detector",
                   choices=["detector", "performance", "ddm", "adwin", "ddm_river", "adwin_river",
                            "random"],
                   help="performance = DDM-style trigger on the incumbent's monitored error "
                        "(labels spent on monitoring instead of gating).")
    p.add_argument("--monitor-labels", type=int, default=8,
                   help="Labels per window for the performance trigger.")
    p.add_argument("--stream-prevalence", type=float, default=0.5,
                   help="Attack fraction of EVALUATION windows (0.5 = balanced; natural-"
                        "prevalence streams report FPR/recall/alert volume).")
    p.add_argument("--stream-disjoint-windows", action="store_true",
                   help="amendment 011: draw stream windows WITHOUT replacement within the window "
                        "pool, so no row recurs across windows (removes candidate-train/future-eval "
                        "overlap for the causal arm). Balanced streams only.")
    p.add_argument("--cumulative-mode", type=str, default="observed",
                   choices=["observed", "initial_plus_observed", "dedup", "cn"],
                   help="amendment 011 cumulative controls: observed = all observed windows (a009 "
                        "default); initial_plus_observed = incumbent training set + all observed; "
                        "dedup = row-identity dedup before fit; cn = C scaled ~1/n_unique.")
    args = p.parse_args()

    seeds = [int(s) for s in str(args.seeds).split(",") if s.strip()]
    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    args.outdir.mkdir(parents=True, exist_ok=True)

    X_ref, y_ref = load_binary_dataset(args.data_ref, args.label_col)
    X_cur, y_cur = load_binary_dataset(args.data_cur, args.label_col)
    common = sorted(set(X_ref.columns).intersection(X_cur.columns))
    pools = make_pools(X_ref, y_ref, X_cur, y_cur, common)

    win_rows, trig_rows, sum_rows = [], [], []
    for seed in seeds:
        print(f"[v2 SEED={seed}]", flush=True)
        env = build_environment(pools, args, seed)
        # no-adaptation on the SAME shared stream
        na = [dict(seed=seed, method="no_adaptation", window_idx=t, severity_t=sev,
                   balanced_accuracy=evaluate_model(env.initial_model, Xw, yw)["balanced_accuracy"],
                   f1=evaluate_model(env.initial_model, Xw, yw)["f1"], score=np.nan,
                   threshold=np.nan, alarm=False, trigger=False, adapted_now=False)
              for t, (Xw, yw, sev) in enumerate(env.stream)]
        win_rows.extend(na)
        sum_rows.append(dict(seed=seed, method="no_adaptation", n_windows=args.post_windows,
                             n_adaptations=0, n_triggers=0, n_gate_rejections=0,
                             labels_used_total=0, labels_probe=0, labels_monitor=0,
                             labels_candidate=0, n_candidates_trained=0, n_train_skipped=0,
                             n_probes=0, n_probes_zero_attack=0, probe_row_collisions=0,
                             cand_future_collisions=0, seq_labels_mean=np.nan,
                             adaptation_gate="none", harness="v2",
                             first_adaptation_window=np.nan,
                             mean_balanced_accuracy=float(np.mean([r["balanced_accuracy"] for r in na])),
                             mean_f1=float(np.mean([r["f1"] for r in na]))))
        for method in methods:
            rows, trows, summary = run_arm(method, env, args, seed)
            win_rows.extend(rows); trig_rows.extend(trows); sum_rows.append(summary)

    pd.DataFrame(win_rows).to_csv(args.outdir / "paper2_progressive_readaptation_window_results.csv", index=False)
    pd.DataFrame(sum_rows).to_csv(args.outdir / "paper2_progressive_readaptation_by_seed.csv", index=False)
    if trig_rows:
        pd.DataFrame(trig_rows).to_csv(args.outdir / "paper2_v2_trigger_log.csv", index=False)
    s = pd.DataFrame(sum_rows)
    agg = s.groupby("method").agg(n_seeds=("seed", "nunique"),
                                  mean_balanced_accuracy=("mean_balanced_accuracy", "mean"),
                                  n_adaptations_mean=("n_adaptations", "mean")).reset_index()
    s.to_csv(args.outdir / "paper2_progressive_readaptation_summary.csv", index=False)
    print(agg.to_string(index=False))


if __name__ == "__main__":
    main()
