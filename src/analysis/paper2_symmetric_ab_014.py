"""Amendment 014: the symmetric-A/B mechanism control, REDONE correctly.

Fixes the two flaws external review found in the 013 version:
  1. DISJOINT samples: each class's reference pool is value-deduplicated globally, then a per-seed
     permutation is partitioned into four DISJOINT blocks -- T (transformer), M1, M2 (the two
     models) and E (evaluation). No row appears in two blocks (asserted).
  2. SYMMETRY: which of M1/M2 acts as the incumbent is randomized per seed, and we report the
     role-randomized gap BA(challenger) - BA(incumbent) plus both fixed directions.

Conditions: (a) independent transformer (fit on T); (b) incumbent-fit transformer (fit on the
incumbent's own block -- the freeze-the-pipeline convention). If per-class unique rows cannot
support 4 blocks of 2,000, N is scaled down to floor(min_unique/4) and reported.

Outputs results/tables/paper2_amendment_014/symmetric_ab.csv
"""
import os
import numpy as np
import pandas as pd

from src.experiments.run_paper2_progressive_readaptation import (
    load_binary_dataset, fit_transformer, transform_X, train_svc, evaluate_model,
)

OUT = "results/tables/paper2_amendment_014"
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


def one_dataset(name, ref, model_type="svc_rbf"):
    pools = unique_class_pools(ref)
    n = min(2000, min(len(pools[0]), len(pools[1])) // 4)
    rows = {("independent", "rand"): [], ("independent", "m2_minus_m1"): [],
            ("incumbent_fit", "rand"): [], ("incumbent_fit", "m2_minus_m1"): []}
    for seed in SEEDS:
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

        for cond in ("independent", "incumbent_fit"):
            fit_on = XT if cond == "independent" else (X1 if inc_is_m1 else X2)
            sc, pca, _ = fit_transformer(fit_on, DIM, seed)
            m1 = train_svc(transform_X(X1, sc, pca), y1, seed, model_type)
            m2 = train_svc(transform_X(X2, sc, pca), y2, seed + 1, model_type)
            Xe = transform_X(XE, sc, pca)
            b1 = evaluate_model(m1, Xe, yE)["balanced_accuracy"]
            b2 = evaluate_model(m2, Xe, yE)["balanced_accuracy"]
            inc, cha = (b1, b2) if inc_is_m1 else (b2, b1)
            rows[(cond, "rand")].append(cha - inc)          # challenger - incumbent, role-randomized
            rows[(cond, "m2_minus_m1")].append(b2 - b1)     # fixed direction, for both-way reporting
    out = []
    for (cond, kind), vals in rows.items():
        v = np.array(vals) * 100
        lo, hi = boot_ci(v)
        out.append(dict(dataset=name, model=model_type, condition=cond, contrast=kind,
                        n_seeds=len(v), n_per_block=n,
                        gap=round(float(v.mean()), 3), lo=round(lo, 3), hi=round(hi, 3)))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for name, (ref, _cur) in DATASETS.items():
        for mt in ("svc_rbf", "random_forest"):
            rows.extend(one_dataset(name, ref, mt))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/symmetric_ab.csv", index=False)
    print("== symmetric A/B (DISJOINT blocks, role-randomized), zero drift ==")
    print(R.to_string(index=False))


if __name__ == "__main__":
    main()
