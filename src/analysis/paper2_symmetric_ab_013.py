"""Amendment 013: the decisive symmetric-A/B control for the zero-drift replacement harm.

The reviewer's mechanism objection: under zero drift the standardizer+PCA are fit on the
incumbent's training data and reused for every challenger, and the incumbent is the first (and,
by default, larger) draw -- so incumbent and challenger are not exchangeable, and the observed
"replacement harm" may be that asymmetry rather than pure re-estimation variance.

This standalone experiment isolates it. From the reference (zero-drift) distribution we draw four
disjoint, equal-size, balanced samples per seed: T (transformer), A, B (two candidates), E (eval).
We fit SVC-RBF models A and B on the SAME independent transformer and compare BA(B)-BA(A) on E --
a fully symmetric replacement (A and B exchangeable). We also fit the transformer on A's data (the
frozen-incumbent-transformer condition of the main harness) and re-measure BA(B)-BA(A).

Reading:
  - independent transformer, gap ~ 0  => symmetric replacement is harmless; the main zero-drift
    harm was the preprocessing/first-draw asymmetry, NOT pure replacement variance (reviewer right);
  - independent transformer, gap < 0  => a symmetric re-estimate is still systematically worse,
    i.e. replacement variance is real even under full symmetry (our reading).
  - gap(A-fit) more negative than gap(independent) quantifies the transformer-asymmetry component.

Outputs results/tables/paper2_amendment_013/symmetric_ab.csv
"""
import os
import numpy as np
import pandas as pd

from src.experiments.run_paper2_progressive_readaptation import (
    make_pools, sample_balanced_from_distribution, fit_transformer, transform_X, train_svc,
    evaluate_model,
)

OUT = "results/tables/paper2_amendment_013"
DATASETS = {
    "portscan": None,  # CICIDS PortScan uses raw Tuesday/Friday; handled below
    "unsw_recon": ("data/processed/unsw_nb15/unsw_ref_no_reconnaissance_binary.csv",
                   "data/processed/unsw_nb15/unsw_cur_reconnaissance_binary.csv"),
    "ton_scanning": ("data/processed/ton_iot_q1_gate/ton_iot_ref_no_scanning_binary.csv",
                     "data/processed/ton_iot_q1_gate/ton_iot_cur_scanning_binary.csv"),
}
N = 2000       # per class, matches the incumbent budget
DIM = 8
SEEDS = range(104, 134)


def boot_ci(x, n=10000, seed=0):
    rng = np.random.default_rng(seed); x = np.asarray(x, float)
    bs = rng.choice(x, size=(n, x.size), replace=True).mean(1)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def one_dataset(name, ref, cur, model_type="svc_rbf"):
    pools = make_pools_from(ref, cur)
    rows_indep, rows_afit = [], []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        # four disjoint balanced draws from the REFERENCE (zero-drift) distribution (severity 0)
        XT, yT = sample_balanced_from_distribution(pools, N, 0.0, rng)
        XA, yA = sample_balanced_from_distribution(pools, N, 0.0, rng)
        XB, yB = sample_balanced_from_distribution(pools, N, 0.0, rng)
        XE, yE = sample_balanced_from_distribution(pools, N, 0.0, rng)
        # (1) INDEPENDENT transformer (fit on T)
        sc, pca, _ = fit_transformer(XT, DIM, seed)
        A = train_svc(transform_X(XA, sc, pca), yA, seed, model_type)
        B = train_svc(transform_X(XB, sc, pca), yB, seed + 1, model_type)
        Xe = transform_X(XE, sc, pca)
        rows_indep.append(evaluate_model(B, Xe, yE)["balanced_accuracy"]
                          - evaluate_model(A, Xe, yE)["balanced_accuracy"])
        # (2) A-FIT transformer (fit on A's data -- the frozen-incumbent condition)
        sc2, pca2, _ = fit_transformer(XA, DIM, seed)
        A2 = train_svc(transform_X(XA, sc2, pca2), yA, seed, model_type)
        B2 = train_svc(transform_X(XB, sc2, pca2), yB, seed + 1, model_type)
        Xe2 = transform_X(XE, sc2, pca2)
        rows_afit.append(evaluate_model(B2, Xe2, yE)["balanced_accuracy"]
                         - evaluate_model(A2, Xe2, yE)["balanced_accuracy"])
    out = []
    for cond, vals in [("independent_transformer", rows_indep), ("A_fit_transformer", rows_afit)]:
        v = np.array(vals) * 100
        lo, hi = boot_ci(v)
        out.append(dict(dataset=name, model=model_type, condition=cond, n=len(v),
                        gap_B_minus_A=round(float(v.mean()), 3), lo=round(lo, 3), hi=round(hi, 3)))
    return out


def make_pools_from(ref, cur):
    from src.experiments.run_paper2_progressive_readaptation import load_binary_dataset
    Xr, yr = load_binary_dataset(ref, "Label")
    Xc, yc = load_binary_dataset(cur, "Label")
    common = [c for c in Xr.columns if c in Xc.columns]
    return make_pools(Xr[common], yr, Xc[common], yc, common)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    CI = "data/raw/cicids2017/MachineLearningCVE"
    ds = dict(DATASETS)
    ds["portscan"] = (f"{CI}/Tuesday-WorkingHours.pcap_ISCX.csv",
                      f"{CI}/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv")
    for name, (ref, cur) in ds.items():
        for mt in ("svc_rbf", "random_forest"):
            rows.extend(one_dataset(name, ref, cur, mt))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/symmetric_ab.csv", index=False)
    print("== symmetric A/B: BA(challenger B) - BA(incumbent A) on independent eval, zero drift ==")
    print(R.to_string(index=False))


if __name__ == "__main__":
    main()
