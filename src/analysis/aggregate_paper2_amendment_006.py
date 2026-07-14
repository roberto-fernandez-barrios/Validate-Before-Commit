"""Aggregate the amendment-006 runs (v8): causal observed-data gate, honest binomial-prevalence
probes, per-incumbent health reference, exact-McNemar gate, the mild-drift prediction test,
harm breadth on v2, and the Wednesday->Thursday chronological attempt.

Outputs results/tables/paper2_amendment_006/*.csv
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_006"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
SEEDS = set(range(104, 134))
rng = np.random.default_rng(20260714)


def boot_ci(v, nb=5000):
    v = np.asarray(v); n = len(v)
    b = v[rng.integers(0, n, (nb, n))].mean(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def by_seed(dirs, method, col="mean_balanced_accuracy", seeds=SEEDS):
    parts = [pd.read_csv(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")
             for d in dirs if os.path.exists(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")]
    if not parts:
        return None
    d = pd.concat(parts)
    d = d[(d.method == method) & (d.seed.isin(seeds))]
    return d.set_index("seed")[col].sort_index() if len(d) else None


def means(dirs, cols, seeds=SEEDS):
    parts = [pd.read_csv(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")
             for d in dirs if os.path.exists(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")]
    if not parts:
        return {}
    d = pd.concat(parts)
    d = d[(d.method == "ks_max") & (d.seed.isin(seeds))]
    return {c: float(d[c].mean()) for c in cols if c in d.columns}


def contrast(a_dirs, b_dirs, label):
    """Paired gain contrast between two arms on the common streams."""
    ga, ba = by_seed(a_dirs, "ks_max"), by_seed(a_dirs, "no_adaptation")
    gb, bb = by_seed(b_dirs, "ks_max"), by_seed(b_dirs, "no_adaptation")
    if any(x is None for x in (ga, ba, gb, bb)):
        return None
    d = ((ga - ba) - (gb - bb)) * 100
    lo, hi = boot_ci(d.values)
    return dict(contrast=label, diff=round(float(d.mean()), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    arms = ["causal_none", "causal_gate", "binom10", "binom05", "binom01", "hrperinc",
            "mcnemar32", "mcnemar64", "sev025_none", "sev025_lp32", "sev050_none", "sev050_lp32"]
    for reg in REGIMES:
        for arm in arms:
            d = [f"paper2_v8_{reg}_{arm}"]
            g, b = by_seed(d, "ks_max"), by_seed(d, "no_adaptation")
            if g is None or b is None:
                print(f"[skip] {reg} {arm}"); continue
            gain = (g - b) * 100
            lo, hi = boot_ci(gain.values)
            m = means(d, ["n_triggers", "n_adaptations", "n_candidates_trained", "n_train_skipped",
                          "n_probes", "n_probes_zero_attack", "labels_probe", "labels_candidate"])
            zf = (m.get("n_probes_zero_attack", 0) / m["n_probes"]) if m.get("n_probes") else np.nan
            rows.append(dict(regime=reg, arm=arm, n=len(gain),
                             gain=round(float(gain.mean()), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                             zero_attack_probe_frac=round(zf, 3) if np.isfinite(zf) else np.nan,
                             **{k: round(v, 2) for k, v in m.items()}))
    # harm breadth (separate regimes)
    for reg in ["ton_ddos", "ton_injection"]:
        for arm in ["none", "lp32"]:
            d = [f"paper2_v8_{reg}_{arm}"]
            g, b = by_seed(d, "ks_max"), by_seed(d, "no_adaptation")
            if g is None or b is None:
                print(f"[skip] {reg} {arm}"); continue
            gain = (g - b) * 100
            lo, hi = boot_ci(gain.values)
            m = means(d, ["n_triggers", "n_adaptations"])
            rows.append(dict(regime=reg, arm=arm, n=len(gain), gain=round(float(gain.mean()), 3),
                             ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                             **{k: round(v, 2) for k, v in m.items()}))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/summary.csv", index=False)
    print("== amendment 006 summary =="); print(R.to_string(index=False)); print()

    # paired contrasts that carry the claims
    crows = []
    for reg in REGIMES:
        lp32 = [f"paper2_v2_{reg}_ks_lp32", f"paper2_v2_{reg}_ks_lp32_top"]   # incl. the top-up seeds
        for lbl, a, b in [
            ("causal_gate_vs_causal_naive", [f"paper2_v8_{reg}_causal_gate"], [f"paper2_v8_{reg}_causal_none"]),
            ("mcnemar32_vs_lp32", [f"paper2_v8_{reg}_mcnemar32"], lp32),
            ("mcnemar64_vs_lp32", [f"paper2_v8_{reg}_mcnemar64"], lp32),
            ("binom01_vs_lp32", [f"paper2_v8_{reg}_binom01"], lp32),
            ("binom05_vs_lp32", [f"paper2_v8_{reg}_binom05"], lp32),
            ("binom10_vs_lp32", [f"paper2_v8_{reg}_binom10"], lp32),
            ("causal_gate_vs_lp32(pools)", [f"paper2_v8_{reg}_causal_gate"], lp32),
            ("sev025_gate_vs_naive", [f"paper2_v8_{reg}_sev025_lp32"], [f"paper2_v8_{reg}_sev025_none"]),
            ("sev050_gate_vs_naive", [f"paper2_v8_{reg}_sev050_lp32"], [f"paper2_v8_{reg}_sev050_none"]),
        ]:
            c = contrast(a, b, lbl)
            if c:
                crows.append(dict(regime=reg, **c))
    for reg in ["ton_ddos", "ton_injection"]:
        c = contrast([f"paper2_v8_{reg}_lp32"], [f"paper2_v8_{reg}_none"], "gate_vs_naive")
        if c:
            crows.append(dict(regime=reg, **c))
    C = pd.DataFrame(crows)
    C.to_csv(f"{OUT}/paired_ci.csv", index=False)
    print("== paired contrasts =="); print(C.to_string(index=False)); print()

    # Wednesday -> Thursday chronological attempt
    t_rows = []
    S = set(range(401, 431))
    for col, mname in [("mean_balanced_accuracy", "BA_two_class"), ("mean_accuracy", "accuracy_all")]:
        nv = by_seed(["paper2_v8_temporal_wed2thu_none"], "ks_max", col=col, seeds=S)
        bs = by_seed(["paper2_v8_temporal_wed2thu_none"], "no_adaptation", col=col, seeds=S)
        gt = by_seed(["paper2_v8_temporal_wed2thu_labeled_probe"], "ks_max", col=col, seeds=S)
        if any(x is None for x in (nv, bs, gt)):
            print("[skip wed2thu]"); continue
        for name, v in [("no_adapt_level", bs * 100), ("naive_vs_noadapt", (nv - bs) * 100),
                        ("gate_vs_noadapt", (gt - bs) * 100), ("gate_vs_naive", (gt - nv) * 100)]:
            vals = v.dropna()
            lo, hi = boot_ci(vals.values)
            t_rows.append(dict(metric=mname, quantity=name, value=round(float(vals.mean()), 3),
                               ci_lo=round(lo, 3), ci_hi=round(hi, 3), n=len(vals)))
    T = pd.DataFrame(t_rows)
    T.to_csv(f"{OUT}/temporal_wed2thu.csv", index=False)
    print("== Wednesday -> Thursday chronological =="); print(T.to_string(index=False))


if __name__ == "__main__":
    main()
