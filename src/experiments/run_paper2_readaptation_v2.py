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
    sample_prevalence_from_distribution,
    train_svc,
    transform_X,
    _labelfree_estimate,
)

ROLE_FRACS = {"window": 0.5, "train": 0.3, "probe": 0.2}
FUTURE_K = 5  # future windows for per-trigger delta-BA logging
LCB_ALPHA_Z = 1.2816  # one-sided 90% normal quantile


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


def build_environment(pools: Pools, args, seed: int) -> Environment:
    role = split_pools(pools, seed)
    train_rng = np.random.default_rng(seed + 777)
    X_tr_raw, y_tr = sample_balanced_from_distribution(
        role["train"], n_per_class=args.train_size_per_class, severity=0.0, rng=train_rng)
    scaler, pca, X_tr = fit_transformer(X_tr_raw, args.dim, seed)
    needs_proba = args.adaptation_gate in ("atc", "doc")
    initial_model = train_svc(X_tr, y_tr, seed, args.downstream_model, proba=needs_proba)

    env_rng = np.random.default_rng(seed)  # environment: depends on seed ONLY
    stream = []
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
    return Environment(scaler, pca, initial_model, stream, role["window"], role["train"], role["probe"])


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


def run_arm(method: str, env: Environment, args, seed: int):
    """One (detector, gate) arm over the shared pre-generated stream."""
    detector = build_detector(method, args, seed)
    detector, threshold = calibrate(detector, env, 0.0, args,
                                    np.random.default_rng(seed + 888))
    model = env.initial_model
    alarms: list[bool] = []
    cooldown = 0
    n_adapt = n_trig = n_reject = labels_used = 0
    adapt_windows: list[int] = []
    ba_hist: list[float] = []
    rows, trig_rows = [], []
    gate = args.adaptation_gate
    needs_proba = gate in ("atc", "doc")
    incumbent_val = None
    if needs_proba:
        Xv_raw, yv = sample_balanced_from_distribution(
            env.train_pools, n_per_class=max(1, args.gate_val_size // 2), severity=0.0,
            rng=np.random.default_rng(seed + 999))
        incumbent_val = (transform_X(Xv_raw, env.scaler, env.pca), yv)

    # performance-aware (DDM-style) trigger: labels spent on MONITORING the incumbent's error
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
        if args.trigger_mode == "performance":
            mon_rng = np.random.default_rng(seed * 400_009 + t)
            Xm_raw, ym = sample_balanced_from_distribution(
                env.probe_pools, n_per_class=max(1, args.monitor_labels // 2), severity=sev, rng=mon_rng)
            Xm = transform_X(Xm_raw, env.scaler, env.pca)
            err_hist.append(1.0 - float((model.predict(Xm) == ym).mean()))
            labels_used += args.monitor_labels
            alarms.append(len(err_hist) >= 1 and float(np.mean(err_hist[-3:])) > perf_thr)
        else:
            alarms.append(score > threshold)
        recent = alarms[-args.consecutive_k:]
        trigger = len(recent) == args.consecutive_k and all(recent) and cooldown <= 0
        adapted = False
        if trigger:
            n_trig += 1
            cand_rng = np.random.default_rng(seed * 100_003 + t)
            Xa_raw, ya = sample_balanced_from_distribution(
                env.train_pools, n_per_class=args.adapt_size_per_class, severity=sev, rng=cand_rng)
            Xa = transform_X(Xa_raw, env.scaler, env.pca)

            probe = None
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
            candidate = train_svc(Xa, ya, seed + t + 1, args.downstream_model, proba=needs_proba)

            commit, cand_val = True, None
            p_inc = p_cand = np.nan
            if gate in ("labeled_probe", "labeled_probe_lcb") or (gate == "labeled_probe_holdout"):
                if probe is None:
                    probe_rng = np.random.default_rng(seed * 200_003 + t)
                    Xp_raw, yp = sample_balanced_from_distribution(
                        env.probe_pools, n_per_class=max(1, args.probe_size // 2),
                        severity=sev, rng=probe_rng)
                    probe = (transform_X(Xp_raw, env.scaler, env.pca), yp)
                    labels_used += len(yp)
                Xp, yp = probe
                if gate == "labeled_probe_lcb":
                    d = (candidate.predict(Xp) == yp).astype(float) - (model.predict(Xp) == yp).astype(float)
                    se = float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else np.inf
                    commit = bool(d.mean() - LCB_ALPHA_Z * se > 0.0)
                    p_inc, p_cand = float((model.predict(Xp) == yp).mean()), float((candidate.predict(Xp) == yp).mean())
                else:
                    p_inc = evaluate_model(model, Xp, yp)["balanced_accuracy"]
                    p_cand = evaluate_model(candidate, Xp, yp)["balanced_accuracy"]
                    commit = bool(p_cand >= p_inc + args.gate_margin)
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

            # per-trigger mechanism log (lookahead is for LOGGING only, never for the policy)
            fut = env.stream[t + 1: t + 1 + FUTURE_K]
            inc_f = float(np.mean([evaluate_model(model, Xf, yf)["balanced_accuracy"] for Xf, yf, _ in fut])) if fut else np.nan
            cand_f = float(np.mean([evaluate_model(candidate, Xf, yf)["balanced_accuracy"] for Xf, yf, _ in fut])) if fut else np.nan
            trig_rows.append(dict(
                seed=seed, method=method, gate=gate, window_idx=t, severity_t=sev,
                score=score, threshold=threshold,
                deg_pre5=float(np.mean(ba_hist[-6:-1])) if len(ba_hist) > 1 else np.nan,
                inc_future5=inc_f, cand_future5=cand_f,
                delta_future5=cand_f - inc_f if fut else np.nan,
                probe_inc=p_inc, probe_cand=p_cand, committed=bool(commit)))

            if commit:
                n_adapt += 1
                adapt_windows.append(t)
                adapted = True
                model = candidate
                if cand_val is not None:
                    incumbent_val = cand_val
                detector = build_detector(method, args, seed + t + 1)
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
                            "unsup_disagree", "atc", "doc"])
    p.add_argument("--gate-val-size", type=int, default=256)
    p.add_argument("--probe-size", type=int, default=32)
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
    p.add_argument("--trigger-mode", type=str, default="detector", choices=["detector", "performance"],
                   help="performance = DDM-style trigger on the incumbent's monitored error "
                        "(labels spent on monitoring instead of gating).")
    p.add_argument("--monitor-labels", type=int, default=8,
                   help="Labels per window for the performance trigger.")
    p.add_argument("--stream-prevalence", type=float, default=0.5,
                   help="Attack fraction of EVALUATION windows (0.5 = balanced; natural-"
                        "prevalence streams report FPR/recall/alert volume).")
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
                             labels_used_total=0, adaptation_gate="none", harness="v2",
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
