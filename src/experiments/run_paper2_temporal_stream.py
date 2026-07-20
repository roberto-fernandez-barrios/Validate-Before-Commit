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
from src.experiments.run_paper2_readaptation_v2 import DDM, cs_lower_bound_eb  # noqa: F401
from scipy.stats import ks_2samp


def ks_max(ref: np.ndarray, X: np.ndarray) -> float:
    return max(ks_2samp(ref[:, j], X[:, j]).statistic for j in range(ref.shape[1]))


def vbc_sg_decide(t, starts, window_rows, Xs, ys, scaler, pca, model, cand, rng,
                  mode="cohort", seq_block=16, defer_windows=5, alpha=0.10):
    """final-q1 D4: VBC-SG ported to the chronological runner. Causally available evidence
    is acquired in blocks and tested with a stratified per-class empirical-Bernstein
    confidence sequence, exactly as in the core harness's vbc_sg gate -- but because every
    window before t is ALREADY OBSERVED (labeled) on a real capture, "deferring" here means
    acquiring more already-available historical evidence in one shot, not waiting for future
    real-time windows. Two continuation semantics (D1's cohort/refresh, restricted to the two
    modes with a clean guarantee -- the weak-null accumulate mode is not offered here since
    real drift is exactly where its caveat bites hardest):
      cohort:  all evidence from the SAME probe window (t-9), drawn WITHOUT replacement in
               blocks of `seq_block` per class, up to window_rows/seq_block blocks -- one
               e-process, one fixed target, tested at alpha/4 per class per look.
      refresh: continuation step k draws a FRESH block from window (t-9-k), a step further
               into the past each time -- never reusing a window -- tested at
               alpha/(1+defer_windows)/4 per class (Bonferroni over the <=1+defer_windows
               independent evidence sets a proposal may open).
    CAUSALITY (invariant 1): every window index used is asserted < t before it is touched.
    RESTART SEMANTICS (invariant 2): cohort tracks used row-indices per class so no row is
    drawn twice; refresh starts a fresh block (and a fresh d[]) at every step.
    LABEL ACCOUNTING (invariant 3): returns exactly the number of labels drawn.
    Returns: dict(commit, n_steps, labels, delay_windows) -- `delay_windows` is 0 for cohort
    (all evidence causally available in one shot) and the number of extra past windows
    consumed for refresh.
    """
    def class_idx(widx):
        return {c: widx[ys[widx] == c] for c in (0, 1)}

    d = {0: [], 1: []}
    used = {0: set(), 1: set()}
    commit = None
    labels = 0
    step = 0
    max_steps = defer_windows + 1
    while commit is None and step < max_steps:
        if mode == "cohort":
            src_t = t - 9
            assert src_t < t, "causality violated: cohort probe window must be strictly past"
            pst = starts[src_t]
            widx = np.arange(pst, pst + window_rows)
            ci = class_idx(widx)
            avail = {c: np.setdiff1d(ci[c], np.array(sorted(used[c]), dtype=int))
                    for c in (0, 1)}
            if any(len(avail[c]) == 0 for c in (0, 1)):
                break   # this window's evidence is exhausted -- reject rather than reuse rows
            blk = {c: rng.choice(avail[c], min(seq_block, len(avail[c])), replace=False)
                  for c in (0, 1)}
            for c in (0, 1):
                used[c].update(blk[c].tolist())
            a_step = alpha
        else:  # refresh
            src_t = t - 9 - step
            if src_t < 0:
                break   # no earlier window left -- reject
            assert src_t < t, "causality violated: refresh probe window must be strictly past"
            pst = starts[src_t]
            widx = np.arange(pst, pst + window_rows)
            ci = class_idx(widx)
            if any(len(ci[c]) == 0 for c in (0, 1)):
                step += 1
                continue    # single-class window: cannot test both classes here, skip it
            blk = {c: rng.choice(ci[c], min(seq_block, len(ci[c])), replace=False)
                  for c in (0, 1)}
            a_step = alpha / (1 + defer_windows)
        Xb = {c: transform_X(Xs[blk[c]], scaler, pca) for c in (0, 1)}
        yb = {c: ys[blk[c]] for c in (0, 1)}
        for c in (0, 1):
            dc = ((cand.predict(Xb[c]) == yb[c]).astype(float)
                  - (model.predict(Xb[c]) == yb[c]).astype(float))
            d[c] = d[c] + dc.tolist() if mode == "cohort" else dc.tolist()
            labels += len(blk[c])
        lbs = [cs_lower_bound_eb(np.asarray(d[c]), a_step / 4.0) for c in (0, 1)]
        ubs = [-cs_lower_bound_eb(-np.asarray(d[c]), a_step / 4.0) for c in (0, 1)]
        if 0.5 * (lbs[0] + lbs[1]) > 0.0:
            commit = True
        elif 0.5 * (ubs[0] + ubs[1]) < 0.0:
            commit = False
        step += 1
    if commit is None:
        commit = False   # unresolved at the deferral cap -> risk-averse reject
    return dict(commit=bool(commit), n_steps=step, labels=labels,
               delay_windows=(step - 1 if mode == "refresh" else 0))


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
    p.add_argument("--adaptation-gate", type=str, default="none",
                   choices=["none", "labeled_probe", "labeled_probe_strat", "vbc_sg"])
    p.add_argument("--probe-size", type=int, default=32)
    p.add_argument("--gate-margin", type=float, default=0.0,
                   help="final-q1 D4: commit iff probe(cand) >= probe(inc) + margin; "
                        "0.001 = the strict reject-ties gate (obligatory chronological baseline).")
    p.add_argument("--vbc-defer-mode", type=str, default="cohort", choices=["cohort", "refresh"],
                   help="final-q1 D4 VBC-SG port. cohort: draw more (without-replacement) rows "
                        "from the SAME causal probe window (t-9) in blocks of --seq-block, up to "
                        "--window-rows or --defer-windows blocks -- a fixed target, closed-form "
                        "cohort guarantee. refresh: each continuation step k draws a FRESH block "
                        "from window t-9-k (strictly earlier, never reused), tested at "
                        "alpha/(1+defer_windows) (Bonferroni over steps). Both are 100%% causal: "
                        "every drawn window index is < t, asserted at draw time.")
    p.add_argument("--seq-block", type=int, default=16,
                   help="vbc_sg: probe rows per class acquired per continuation step.")
    p.add_argument("--defer-windows", type=int, default=5,
                   help="vbc_sg: maximum continuation steps before a proposal is rejected.")
    p.add_argument("--vbc-alpha", type=float, default=0.10,
                   help="vbc_sg: per-proposal false-commit level (stratified EB-CS, alpha/2 "
                        "per class; alpha/4 with the two-sided commit/reject split).")
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
            n_proposals = 0
            vbc_steps_sum = vbc_delay_sum = vbc_resolved = 0
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
                            n_proposals += 1
                            if args.adaptation_gate == "vbc_sg":
                                res = vbc_sg_decide(
                                    t, starts, args.window_rows, Xs, ys, scaler, pca, m, cand,
                                    rng, mode=args.vbc_defer_mode, seq_block=args.seq_block,
                                    defer_windows=args.defer_windows, alpha=args.vbc_alpha)
                                commit = res["commit"]
                                labels_used += res["labels"]
                                vbc_steps_sum += res["n_steps"]
                                vbc_delay_sum += res["delay_windows"]
                                vbc_resolved += 1
                            elif args.adaptation_gate in ("labeled_probe", "labeled_probe_strat"):
                                pst = starts[t - 9]
                                widx = np.arange(pst, pst + args.window_rows)
                                if (args.adaptation_gate == "labeled_probe_strat"
                                        and len(np.unique(ys[widx])) == 2):
                                    # amendment 005: stratified probe (16 per class where
                                    # available) — causal test of the composition-inheritance
                                    # account of the deep-benefit premium
                                    halves = []
                                    for cls in (0, 1):
                                        ci = widx[ys[widx] == cls]
                                        take = min(args.probe_size // 2, len(ci))
                                        halves.append(rng.choice(ci, take, replace=False))
                                    pw = np.concatenate(halves)
                                    if len(pw) < args.probe_size:
                                        rest = np.setdiff1d(widx, pw)
                                        pw = np.concatenate([pw, rng.choice(rest, args.probe_size - len(pw), replace=False)])
                                else:
                                    pw = rng.choice(widx, args.probe_size, replace=False)
                                Xp, yp = transform_X(Xs[pw], scaler, pca), ys[pw]
                                labels_used += args.probe_size
                                f = (lambda mm: float((mm.predict(Xp) == yp).mean()))
                                commit = f(cand) >= f(m) + args.gate_margin
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
                                 n_two_class=len(ba2), n_proposals=n_proposals,
                                 vbc_defer_mode=args.vbc_defer_mode if args.adaptation_gate == "vbc_sg" else "",
                                 vbc_steps_mean=(vbc_steps_sum / vbc_resolved) if vbc_resolved else np.nan,
                                 vbc_delay_mean=(vbc_delay_sum / vbc_resolved) if vbc_resolved else np.nan,
                                 mean_balanced_accuracy=float(np.mean(ba2)) if ba2 else np.nan,
                                 mean_accuracy=float(np.mean([r["accuracy"] for r in sub]))))
        print(f"[seed {seed}] done", flush=True)

    pd.DataFrame(win_rows).to_csv(args.outdir / "paper2_progressive_readaptation_window_results.csv", index=False)
    pd.DataFrame(sum_rows).to_csv(args.outdir / "paper2_progressive_readaptation_by_seed.csv", index=False)
    s = pd.DataFrame(sum_rows)
    print(s.groupby("method").mean_balanced_accuracy.mean())


if __name__ == "__main__":
    main()
