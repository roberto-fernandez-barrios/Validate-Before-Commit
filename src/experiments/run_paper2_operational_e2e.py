"""final-q1 D5 (P1.4): operational end-to-end evaluation with realistic label acquisition.

Pipeline: stream (at operating prevalence) -> KS-max trigger -> label acquisition -> candidate
training -> probe -> commit, with an explicit training-completion delay. Reuses the v2
harness's environment (bit-identical stream construction, disjoint role partitions) via
`build_environment`, so the trigger/candidate machinery is exactly the tested one; this
script adds only what P1.4 is actually about: WHICH flows get labeled.

Acquisition policies (registered, notes/q1_max_protocol.md D5), all honest -- they never read
true labels to decide what to inspect, only model PREDICTIONS (legitimate: a deployed
detector scores every flow without needing ground truth):
  random          uniform draw from the honest-prevalence pool (Binomial attack count).
  alert_enriched  prioritizes flows the INCUMBENT predicts positive (its alert queue).
  disagreement    prioritizes flows where incumbent and candidate predictions differ.
  hybrid          half alert_enriched quota, half disagreement quota.
A larger unlabeled pool (--pool-multiplier x probe_size) is drawn at the true operating
prevalence; the policy selects which probe_size of them to adjudicate (reveal labels for).
Labels used = probe_size in every policy (the acquisition COST is the same); what differs is
how many of those adjudicated labels are attacks, hence `inspected_flows_per_attack` =
probe_size / attacks_found -- the metric this delta is about.

Training-completion delay (--training-delay D, new flag): the candidate is BUILT at the
trigger window t (compute is instantaneous in the simulator, as elsewhere in this codebase),
but is not committable until window t+D -- an operational deployment lag distinct from label
latency (Table tab:latency in the manuscript). While a candidate is maturing, the loop is
pending and new triggers are absorbed, mirroring the v2 runner's registered policy.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.experiments.run_paper2_progressive_readaptation import (
    evaluate_model, load_binary_dataset, make_pools, sample_balanced_from_distribution,
    sample_binomial_prevalence, train_svc, transform_X,
)
from src.experiments.run_paper2_readaptation_v2 import build_detector, build_environment, calibrate


def sample_acquisition(pools, n_total, attack_frac, severity, rng, policy, scaler, pca,
                       incumbent=None, candidate=None, pool_multiplier=8):
    """Draw an honest-prevalence pool, score it with model PREDICTIONS only, and select
    `n_total` flows to adjudicate under `policy`. Returns (X_raw, y, n_attacks_selected)."""
    pool_n = max(n_total * pool_multiplier, n_total)
    Xraw, y = sample_binomial_prevalence(pools, pool_n, attack_frac, severity, rng)
    if policy == "random" or incumbent is None or (y == 1).sum() == 0:
        idx = rng.permutation(len(y))[:n_total]
    else:
        Xt = transform_X(Xraw, scaler, pca)
        inc_pred = incumbent.predict(Xt)
        cand_pred = candidate.predict(Xt) if candidate is not None else inc_pred
        if policy == "alert_enriched":
            priority = (inc_pred == 1)
        elif policy == "disagreement":
            priority = (cand_pred != inc_pred)
        elif policy == "hybrid":
            half = n_total // 2
            pos_a = np.where(inc_pred == 1)[0]; rng.shuffle(pos_a)
            pos_d = np.where(cand_pred != inc_pred)[0]; rng.shuffle(pos_d)
            picked = list(pos_a[:half])
            picked += [i for i in pos_d.tolist() if i not in picked][:n_total - len(picked)]
            if len(picked) < n_total:
                rest = np.setdiff1d(np.arange(len(y)), picked)
                rng.shuffle(rest)
                picked += rest[:n_total - len(picked)].tolist()
            idx = np.array(picked[:n_total], dtype=int)
            return Xraw[idx], y[idx], int((y[idx] == 1).sum())
        else:
            raise ValueError(f"unknown acquisition policy {policy}")
        pos = np.where(priority)[0]; rng.shuffle(pos)
        picked = list(pos[:n_total])
        if len(picked) < n_total:
            rest = np.setdiff1d(np.arange(len(y)), picked)
            rng.shuffle(rest)
            picked += rest[:n_total - len(picked)].tolist()
        idx = np.array(picked[:n_total], dtype=int)
    return Xraw[idx], y[idx], int((y[idx] == 1).sum())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-ref", type=Path, required=True)
    p.add_argument("--data-cur", type=Path, required=True)
    p.add_argument("--label-col", type=str, default="Label")
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--seeds", type=str, default="701")
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
    p.add_argument("--downstream-model", type=str, default="svc_rbf")
    p.add_argument("--stream-prevalence", type=float, default=0.5)
    p.add_argument("--probe-prevalence", type=float, required=True, help="operating pi")
    p.add_argument("--probe-size", type=int, default=32)
    p.add_argument("--probe-latency", type=int, default=0)
    p.add_argument("--candidate-latency", type=int, default=0)
    p.add_argument("--training-delay", type=int, default=0,
                   help="final-q1 D5: windows between trigger and candidate committability.")
    p.add_argument("--acquisition-policy", type=str, default="random",
                   choices=["random", "alert_enriched", "disagreement", "hybrid"])
    p.add_argument("--pool-multiplier", type=int, default=8)
    p.add_argument("--gate-margin", type=float, default=0.0,
                   help="0 = point gate, 0.001 = strict.")
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    # satisfy build_environment's / build_detector's getattr surface (v2 defaults for
    # everything not exposed on this script's own CLI)
    for k, v in dict(adaptation_gate="none", adapt_strategy="full_replace",
                     stream_disjoint_windows=False, disjoint_window_frac=0.5,
                     methods="ks_max", trigger_prob=0.0, ks_reduction="max",
                     jsd_bins=16, energy_reduction="mean", alpha=0.05, n_permutations=0,
                     q_reps=1, q_input_scaling="atan_standard").items():
        setattr(args, k, v)

    X_ref, y_ref = load_binary_dataset(args.data_ref, args.label_col)
    X_cur, y_cur = load_binary_dataset(args.data_cur, args.label_col)
    common = sorted(set(X_ref.columns) & set(X_cur.columns))
    pools = make_pools(X_ref, y_ref, X_cur, y_cur, common)

    win_rows, sum_rows = [], []
    for seed in [int(s) for s in args.seeds.split(",") if s.strip()]:
        env = build_environment(pools, args, seed)
        na_ba = [evaluate_model(env.initial_model, Xw, yw)["balanced_accuracy"]
                 for Xw, yw, _ in env.stream]
        sum_rows.append(dict(seed=seed, method="no_adaptation", n_triggers=0, n_adaptations=0,
                             labels_used=0, attacks_found_total=0,
                             inspected_flows_per_attack=np.nan,
                             mean_balanced_accuracy=float(np.mean(na_ba))))

        detector = build_detector("ks_max", args, seed)
        detector, threshold = calibrate(detector, env, 0.0, args, np.random.default_rng(seed + 888))
        model = env.initial_model
        alarms, cooldown = [], 0
        n_trig = n_adapt = labels_used = attacks_found_total = 0
        pending = None   # dict(cand, ready_at) while maturing (training-delay)
        ba_hist = []
        for t, (Xw, yw, sev) in enumerate(env.stream):
            # the window is served by whatever is deployed AT ITS START (production semantics:
            # a commit decided later in this same iteration cannot retroactively serve it)
            ba_hist.append(evaluate_model(model, Xw, yw)["balanced_accuracy"])
            score = float(detector.score(Xw))
            alarms.append(score > threshold)
            can_trigger = pending is None
            trigger = (len(alarms) >= args.consecutive_k
                      and all(alarms[-args.consecutive_k:]) and cooldown <= 0 and can_trigger)
            if trigger:
                n_trig += 1
                cand_rng = np.random.default_rng(seed * 100_003 + t)
                cl = args.candidate_latency
                sev_c = env.stream[max(0, t - cl)][2] if cl > 0 else sev
                Xa_raw, ya = sample_balanced_from_distribution(
                    env.train_pools, n_per_class=args.adapt_size_per_class, severity=sev_c,
                    rng=cand_rng)
                Xa = transform_X(Xa_raw, env.scaler, env.pca)
                cand = train_svc(Xa, ya, seed + t + 1, args.downstream_model)
                pending = dict(cand=cand, ready_at=t + args.training_delay, trig_t=t)
                alarms, cooldown = [], args.cooldown_windows
            else:
                cooldown = max(0, cooldown - 1)
            if pending is not None and t >= pending["ready_at"]:
                pl = args.probe_latency
                sev_p = env.stream[max(0, t - pl)][2] if pl > 0 else sev
                probe_rng = np.random.default_rng(seed * 200_003 + t)
                Xp_raw, yp, n_att = sample_acquisition(
                    env.probe_pools, args.probe_size, args.probe_prevalence, sev_p, probe_rng,
                    args.acquisition_policy, env.scaler, env.pca,
                    incumbent=model, candidate=pending["cand"],
                    pool_multiplier=args.pool_multiplier)
                Xp = transform_X(Xp_raw, env.scaler, env.pca)
                labels_used += args.probe_size; attacks_found_total += n_att
                if len(np.unique(yp)) == 2:
                    f = lambda mm: float((mm.predict(Xp) == yp).mean())
                    commit = f(pending["cand"]) >= f(model) + args.gate_margin
                else:
                    commit = float((pending["cand"].predict(Xp) == yp).mean()) >= \
                             float((model.predict(Xp) == yp).mean()) + args.gate_margin
                if commit:
                    model = pending["cand"]; n_adapt += 1
                    detector, threshold = calibrate(detector, env, sev, args,
                                                    np.random.default_rng(seed * 1_000 + 999 + t))
                pending = None
            win_rows.append(dict(seed=seed, window_idx=t, severity_t=sev, score=score,
                                 balanced_accuracy=ba_hist[-1], trigger=bool(trigger)))
        sum_rows.append(dict(
            seed=seed, method="ks_max", n_triggers=n_trig, n_adaptations=n_adapt,
            labels_used=labels_used, attacks_found_total=attacks_found_total,
            inspected_flows_per_attack=(labels_used / attacks_found_total
                                        if attacks_found_total else np.nan),
            mean_balanced_accuracy=float(np.mean(ba_hist))))
        print(f"[seed {seed}] triggers={n_trig} adapt={n_adapt} "
              f"attacks_found={attacks_found_total}/{labels_used}", flush=True)

    pd.DataFrame(win_rows).to_csv(args.outdir / "paper2_progressive_readaptation_window_results.csv",
                                  index=False)
    S = pd.DataFrame(sum_rows)
    S.to_csv(args.outdir / "paper2_progressive_readaptation_by_seed.csv", index=False)
    print(S.groupby("method").mean_balanced_accuracy.mean())


if __name__ == "__main__":
    main()
