"""final-kbs P0.1 / final-q1 P0.3: the symmetric-A/B mechanism control.

Fixes the two flaws external review found in the 013 version:
  1. DISJOINT samples: each class's reference pool is value-deduplicated globally, then a per-seed
     permutation is partitioned into four DISJOINT blocks -- T (transformer), M1, M2 (the two
     models) and E (evaluation). No row appears in two blocks (asserted).
  2. SYMMETRY: which of M1/M2 acts as the incumbent is randomized per seed, and we report the
     role-randomized gap BA(challenger) - BA(incumbent) plus both fixed directions.

final-q1 (D2/P0.3) additions, all additive:
  * per-seed output (symmetric_ab_perseed*.csv) -- required by the TOST equivalence analysis;
  * --seed-start/--seed-end: run an arbitrary seed block (pilot 104-133; confirmatory 2001-2100);
  * --decompose: the scaler/PCA decomposition conditions (ToN-IoT x SVC-RBF only, per protocol):
        inc_scaler_indep_pca   (incumbent standardizer, transformer-block PCA)
        indep_scaler_inc_pca   (transformer-block standardizer, incumbent PCA)
    which bracket the existing {independent, incumbent_fit, own_transformer} conditions;
  * --out-suffix: write to separate files so the pilot outputs are never overwritten.

Conditions: (a) independent transformer (fit on T); (b) incumbent-fit transformer;
(c) challenger-fit transformer; (d) own transformer per model. If per-class unique rows cannot
support 4 blocks of 2,000, N is scaled down to floor(min_unique/4) and reported.

Outputs results/tables/paper2_final_kbs/symmetric_ab{suffix}.csv (aggregates)
        results/tables/paper2_final_kbs/symmetric_ab_perseed{suffix}.csv (per-seed rows)
"""
import argparse
import os

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from src.experiments.run_paper2_progressive_readaptation import (
    load_binary_dataset, fit_transformer, transform_X, train_svc, evaluate_model,
)

OUT = "results/tables/paper2_final_kbs"
DIM = 8
SEEDS = range(104, 134)
CI = "data/raw/cicids2017/MachineLearningCVE"
DATASETS = {
    "portscan": (f"{CI}/Tuesday-WorkingHours.pcap_ISCX.csv",
                 f"{CI}/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv"),
    "unsw_recon": ("data/processed/unsw_nb15/unsw_ref_no_reconnaissance_binary.csv",
                   "data/processed/unsw_nb15/unsw_cur_reconnaissance_binary.csv"),
    "ton_scanning": ("data/processed/ton_iot_q1_gate/ton_iot_ref_no_scanning_binary.csv",
                     "data/processed/ton_iot_q1_gate/ton_iot_cur_scanning_binary.csv"),
}
BASE_CONDS = ("independent", "incumbent_fit", "challenger_fit", "own_transformer")
DECOMP_CONDS = ("inc_scaler_indep_pca", "indep_scaler_inc_pca")


def boot_ci(x, n=10000, seed=0):
    rng = np.random.default_rng(seed); x = np.asarray(x, float)
    bs = rng.choice(x, size=(n, x.size), replace=True).mean(1)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def unique_class_pools(ref):
    Xr, yr = load_binary_dataset(ref, "Label")
    Xr = np.asarray(Xr, dtype=float); yr = np.asarray(yr)
    out = {}
    for cls in (0, 1):
        a = Xr[yr == cls]
        _, uq = np.unique(a, axis=0, return_index=True)
        out[cls] = a[np.sort(uq)]
    return out


def _split_transformer(X_scaler_src, X_pca_src, dim, seed):
    """Scaler fit on one block, PCA fit on (scaled) another -- the decomposition conditions.
    Mirrors fit_transformer exactly (StandardScaler -> PCA(dim, random_state=seed))."""
    sc = StandardScaler().fit(X_scaler_src)
    if dim < X_pca_src.shape[1]:
        pca = PCA(n_components=dim, random_state=seed).fit(sc.transform(X_pca_src))
    else:
        pca = None
    return sc, pca


def one_dataset(name, ref, model_type="svc_rbf", seeds=None, conds=BASE_CONDS):
    seeds = list(seeds if seeds is not None else SEEDS)
    pools = unique_class_pools(ref)
    n = min(2000, min(len(pools[0]), len(pools[1])) // 4)
    rows = {(c, k): [] for c in conds for k in ("rand", "m2_minus_m1")}
    perseed = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        blocks = {}
        for cls in (0, 1):
            perm = rng.permutation(len(pools[cls]))
            for i, b in enumerate(("T", "M1", "M2", "E")):
                blocks.setdefault(b, {})[cls] = pools[cls][perm[i * n:(i + 1) * n]]
        # disjointness assertion (by construction of the permutation, but verify on values)
        h = lambda a: {r.tobytes() for r in np.ascontiguousarray(a)}
        assert not (h(blocks["M1"][0]) & h(blocks["M2"][0])), "M1/M2 benign overlap"
        assert not (h(blocks["M1"][1]) & h(blocks["E"][1])), "M1/E attack overlap"

        def xy(b):
            X = np.vstack([blocks[b][0], blocks[b][1]])
            y = np.array([0] * n + [1] * n)
            p = rng.permutation(len(y))
            return X[p], y[p]

        XT, yT = xy("T"); X1, y1 = xy("M1"); X2, y2 = xy("M2"); XE, yE = xy("E")
        inc_is_m1 = bool(rng.random() < 0.5)   # randomized role assignment
        X_inc = X1 if inc_is_m1 else X2

        for cond in conds:
            if cond == "own_transformer":
                sc1, p1_, _ = fit_transformer(X1, DIM, seed)
                sc2, p2_, _ = fit_transformer(X2, DIM, seed + 1)
                m1 = train_svc(transform_X(X1, sc1, p1_), y1, seed, model_type)
                m2 = train_svc(transform_X(X2, sc2, p2_), y2, seed + 1, model_type)
                b1 = evaluate_model(m1, transform_X(XE, sc1, p1_), yE)["balanced_accuracy"]
                b2 = evaluate_model(m2, transform_X(XE, sc2, p2_), yE)["balanced_accuracy"]
            else:
                if cond in BASE_CONDS:
                    fit_on = (XT if cond == "independent"
                              else (X_inc if cond == "incumbent_fit"
                                    else (X2 if inc_is_m1 else X1)))
                    sc, pca, _ = fit_transformer(fit_on, DIM, seed)
                elif cond == "inc_scaler_indep_pca":
                    sc, pca = _split_transformer(X_inc, XT, DIM, seed)
                elif cond == "indep_scaler_inc_pca":
                    sc, pca = _split_transformer(XT, X_inc, DIM, seed)
                else:
                    raise ValueError(cond)
                m1 = train_svc(transform_X(X1, sc, pca), y1, seed, model_type)
                m2 = train_svc(transform_X(X2, sc, pca), y2, seed + 1, model_type)
                Xe = transform_X(XE, sc, pca)
                b1 = evaluate_model(m1, Xe, yE)["balanced_accuracy"]
                b2 = evaluate_model(m2, Xe, yE)["balanced_accuracy"]
            inc, cha = (b1, b2) if inc_is_m1 else (b2, b1)
            rows[(cond, "rand")].append(cha - inc)          # challenger - incumbent, role-randomized
            rows[(cond, "m2_minus_m1")].append(b2 - b1)     # fixed direction, for both-way reporting
            perseed.append(dict(dataset=name, model=model_type, condition=cond, seed=seed,
                                n_per_block=n, inc_is_m1=inc_is_m1,
                                ba_incumbent=round(inc * 100, 4), ba_challenger=round(cha * 100, 4),
                                gap_rand=round((cha - inc) * 100, 4),
                                gap_m2_minus_m1=round((b2 - b1) * 100, 4)))
    out = []
    for (cond, kind), vals in rows.items():
        v = np.array(vals) * 100
        lo, hi = boot_ci(v)
        out.append(dict(dataset=name, model=model_type, condition=cond, contrast=kind,
                        n_seeds=len(v), n_per_block=n,
                        gap=round(float(v.mean()), 3), lo=round(lo, 3), hi=round(hi, 3)))
    return out, perseed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-start", type=int, default=104)
    ap.add_argument("--seed-end", type=int, default=133, help="inclusive")
    ap.add_argument("--datasets", type=str, default="portscan,unsw_recon,ton_scanning")
    ap.add_argument("--models", type=str, default="svc_rbf,random_forest")
    ap.add_argument("--decompose", action="store_true",
                    help="final-q1 P0.3: add the scaler/PCA split conditions "
                         "(protocol scope: ton_scanning x svc_rbf)")
    ap.add_argument("--conditions", type=str, default="",
                    help="comma-separated subset of the base conditions (default: all four); "
                         "condition order never consumes RNG, so subsets stay deterministic")
    ap.add_argument("--out-suffix", type=str, default="",
                    help="e.g. _confirmatory2001_2100 -- never overwrite the pilot files")
    args = ap.parse_args()
    seeds = range(args.seed_start, args.seed_end + 1)

    os.makedirs(OUT, exist_ok=True)
    rows, perseed = [], []
    for name in [d.strip() for d in args.datasets.split(",") if d.strip()]:
        ref, _cur = DATASETS[name]
        for mt in [m.strip() for m in args.models.split(",") if m.strip()]:
            conds = (tuple(c.strip() for c in args.conditions.split(",") if c.strip())
                     if args.conditions else BASE_CONDS)
            if args.decompose and name == "ton_scanning" and mt == "svc_rbf":
                conds = conds + DECOMP_CONDS
            r, p = one_dataset(name, ref, mt, seeds=seeds, conds=conds)
            rows.extend(r); perseed.extend(p)
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/symmetric_ab{args.out_suffix}.csv", index=False)
    pd.DataFrame(perseed).to_csv(f"{OUT}/symmetric_ab_perseed{args.out_suffix}.csv", index=False)
    print(f"== symmetric A/B (DISJOINT blocks, role-randomized), seeds "
          f"{args.seed_start}-{args.seed_end} ==")
    print(R.to_string(index=False))


if __name__ == "__main__":
    main()
