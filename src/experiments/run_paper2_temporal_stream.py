"""Real chronological stream (review point: external validity beyond synthetic ramps).

CICIDS2017 Friday replayed in true temporal order (Morning/Botnet -> Afternoon-PortScan ->
Afternoon-DDoS, file order preserved), evaluated as consecutive row blocks with their natural
class composition. The incumbent trains on Tuesday (the temporal past). On a KS-max trigger,
the candidate retrains on the last 8 OBSERVED windows (labeled, already in the past); the
labeled probe is drawn from the window 9 steps back (disjoint from candidate training by
construction, strictly in the past). No pools, no severity ramp, no balancing anywhere.
Arms: --adaptation-gate {none, labeled_probe}. Seeds only affect subsampling stride phase and
model seeds; the stream order is fixed by the capture.
"""
from __future__ import annotations
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.experiments.run_paper2_progressive_readaptation import (
    load_binary_dataset, fit_transformer, transform_X, train_svc, evaluate_model)
from src.experiments.run_paper2_readaptation_v2 import DDM  # noqa: F401 (parity import)
from scipy.stats import ks_2samp


def ks_max(ref: np.ndarray, X: np.ndarray) -> float:
    return max(ks_2samp(ref[:, j], X[:, j]).statistic for j in range(ref.shape[1]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-train", type=Path, required=True)   # Tuesday (temporal past)
    p.add_argument("--data-stream", type=Path, nargs="+", required=True)  # Friday files, in order
    p.add_argument("--label-col", type=str, default="Label")
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--seeds", type=str, default="104")
    p.add_argument("--dim", type=int, default=8)
    p.add_argument("--window-rows", type=int, default=256)
    p.add_argument("--n-windows", type=int, default=200)
    p.add_argument("--train-size-per-class", type=int, default=2000)
    p.add_argument("--calibration-windows", type=int, default=30)
    p.add_argument("--threshold-quantile", type=float, default=0.95)
    p.add_argument("--consecutive-k", type=int, default=3)
    p.add_argument("--cooldown-windows", type=int, default=10)
    p.add_argument("--adaptation-gate", type=str, default="none", choices=["none", "labeled_probe"])
    p.add_argument("--probe-size", type=int, default=32)
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    Xtr_df, ytr_all = load_binary_dataset(args.data_train, args.label_col)
    parts = [load_binary_dataset(f, args.label_col) for f in args.data_stream]
    common = sorted(set(Xtr_df.columns).intersection(*[set(x.columns) for x, _ in parts]))
    Xs = np.vstack([x[common].to_numpy(float) for x, _ in parts])
    ys = np.concatenate([y.to_numpy() for _, y in parts])
    Xtr_all = Xtr_df[common].to_numpy(float)
    ytr_np = ytr_all.to_numpy()

    total = len(ys)
    stride = max(args.window_rows, total // args.n_windows)
    starts = list(range(0, total - args.window_rows, stride))[: args.n_windows]

    win_rows, sum_rows = [], []
    for seed in [int(s) for s in args.seeds.split(",") if s.strip()]:
        rng = np.random.default_rng(seed)
        # balanced Tuesday training sample (training-time balancing is standard practice)
        idx0 = rng.choice(np.where(ytr_np == 0)[0], args.train_size_per_class, replace=False)
        idx1 = rng.choice(np.where(ytr_np == 1)[0], min(args.train_size_per_class, (ytr_np == 1).sum()), replace=False)
        tr = np.concatenate([idx0, idx1])
        scaler, pca, Xt = fit_transformer(Xtr_all[tr], args.dim, seed)
        model0 = train_svc(Xt, ytr_np[tr], seed)
        # calibration: KS threshold from Tuesday-internal windows
        ref = transform_X(Xtr_all[rng.choice(len(Xtr_all), 512, replace=False)], scaler, pca)
        cal = []
        for _ in range(args.calibration_windows):
            blk = rng.choice(len(Xtr_all), args.window_rows, replace=False)
            cal.append(ks_max(ref, transform_X(Xtr_all[blk], scaler, pca)))
        thr = float(np.quantile(cal, args.threshold_quantile))

        for arm, model in [("no_adaptation", model0), ("ks_max", model0)]:
            alarms, cooldown, n_adapt, labels_used = [], 0, 0, 0
            m = model
            for t, st in enumerate(starts):
                Xw = transform_X(Xs[st:st + args.window_rows], scaler, pca)
                yw = ys[st:st + args.window_rows]
                pred = m.predict(Xw)
                acc = float((pred == yw).mean())
                two_class = len(np.unique(yw)) == 2
                # metric homogeneity (amendment 004): BA only where defined; plain accuracy
                # logged for every window; the headline averages BA over two-class windows only
                ba = evaluate_model(m, Xw, yw)["balanced_accuracy"] if two_class else np.nan
                fp = int(((pred == 1) & (yw == 0)).sum()); tn = int(((pred == 0) & (yw == 0)).sum())
                trigger = False
                if arm == "ks_max":
                    score = ks_max(ref, Xw)
                    alarms.append(score > thr)
                    trigger = len(alarms) >= args.consecutive_k and all(alarms[-args.consecutive_k:]) and cooldown <= 0
                    if trigger and t >= 9:
                        # amendment 004: the candidate trains ONLY on the last 8 OBSERVED
                        # windows (the stride made Xs[lo:st] span unobserved rows before)
                        obs = [(Xs[starts[k]:starts[k] + args.window_rows],
                                ys[starts[k]:starts[k] + args.window_rows]) for k in range(t - 8, t)]
                        Xa_raw = np.vstack([x for x, _ in obs]); ya = np.concatenate([y for _, y in obs])
                        if len(np.unique(ya)) == 2:
                            cand = train_svc(transform_X(Xa_raw, scaler, pca), ya, seed + t)
                            commit = True
                            if args.adaptation_gate == "labeled_probe":
                                pst = starts[t - 9]
                                pw = rng.choice(np.arange(pst, pst + args.window_rows), args.probe_size, replace=False)
                                Xp, yp = transform_X(Xs[pw], scaler, pca), ys[pw]
                                labels_used += args.probe_size
                                f = (lambda mm: float((mm.predict(Xp) == yp).mean()))
                                commit = f(cand) >= f(m)
                            if commit:
                                m = cand; n_adapt += 1
                                # detector reference from the same OBSERVED windows
                                ri = rng.choice(len(Xa_raw), min(512, len(Xa_raw)), replace=False)
                                ref = transform_X(Xa_raw[ri], scaler, pca)
                        alarms, cooldown = [], args.cooldown_windows
                    else:
                        cooldown = max(0, cooldown - 1)
                win_rows.append(dict(seed=seed, method=arm, window_idx=t,
                                     balanced_accuracy=ba, accuracy=acc, two_class=bool(two_class),
                                     fpr=fp / max(1, fp + tn), attack_frac=float((yw == 1).mean()),
                                     trigger=bool(trigger)))
            sub = [r for r in win_rows if r["seed"] == seed and r["method"] == arm]
            ba2 = [r["balanced_accuracy"] for r in sub if r["two_class"]]
            sum_rows.append(dict(seed=seed, method=arm, n_adaptations=n_adapt, labels_used_total=labels_used,
                                 n_two_class=len(ba2),
                                 mean_balanced_accuracy=float(np.mean(ba2)) if ba2 else np.nan,
                                 mean_accuracy=float(np.mean([r["accuracy"] for r in sub]))))
        print(f"[seed {seed}] done", flush=True)

    pd.DataFrame(win_rows).to_csv(args.outdir / "paper2_progressive_readaptation_window_results.csv", index=False)
    pd.DataFrame(sum_rows).to_csv(args.outdir / "paper2_progressive_readaptation_by_seed.csv", index=False)
    s = pd.DataFrame(sum_rows)
    print(s.groupby("method").mean_balanced_accuracy.mean())


if __name__ == "__main__":
    main()
