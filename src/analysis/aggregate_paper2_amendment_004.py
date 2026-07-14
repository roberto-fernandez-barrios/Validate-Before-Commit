"""Aggregate the amendment-004 runs (v6): v2 robustness suite (budget/latency/corruption),
two-stage gate, calibrated ensemble, river reference monitors, corrected temporal streams,
and the label/compute cost accounting table.

Contrasts vs naive/lp32 use the common-stream property: arms with the same seed process
bit-identical windows, so cross-run per-seed differences are truly paired.
Outputs results/tables/paper2_amendment_004/*.csv
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_amendment_004"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
SEEDS = set(range(104, 134))
rng = np.random.default_rng(20260714)


def boot_ci(v, nb=5000):
    v = np.asarray(v); n = len(v)
    b = v[rng.integers(0, n, (nb, n))].mean(1)
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def by_seed(dirs, method, col="mean_balanced_accuracy", seeds=SEEDS):
    parts = []
    for d in dirs:
        f = f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv"
        if os.path.exists(f):
            parts.append(pd.read_csv(f))
    if not parts:
        return None
    d = pd.concat(parts)
    d = d[(d.method == method) & (d.seed.isin(seeds))]
    return d.set_index("seed")[col].sort_index() if len(d) else None


def summary_means(dirs, method, cols, seeds=SEEDS):
    parts = [pd.read_csv(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")
             for d in dirs if os.path.exists(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")]
    d = pd.concat(parts)
    d = d[(d.method == method) & (d.seed.isin(seeds))]
    return {c: float(d[c].mean()) for c in cols if c in d.columns}


def main():
    os.makedirs(OUT, exist_ok=True)
    naive = {r: by_seed([f"paper2_v2_{r}_ks_none", f"paper2_v2_{r}_ks_none_top"], "ks_max") for r in REGIMES}
    base = {r: by_seed([f"paper2_v2_{r}_ks_none", f"paper2_v2_{r}_ks_none_top"], "no_adaptation") for r in REGIMES}
    lp32 = {r: by_seed([f"paper2_v2_{r}_ks_lp32", f"paper2_v2_{r}_ks_lp32_top"], "ks_max") for r in REGIMES}

    # --- robustness suite + two-stage + enscal + river monitors ---
    arms = ["lp8", "lp16", "lp64b", "lp128", "lp32lat5", "lp32lat20",
            "lp32flip10", "lp32flip25", "lp32flip40", "twostage",
            "enscal_none", "ddmriver_none", "adwinriver_none"]
    rows = []
    for reg in REGIMES:
        for arm in arms:
            d = [f"paper2_v6_{reg}_{arm}"]
            g = by_seed(d, "ks_max")
            b = by_seed(d, "no_adaptation")
            if g is None or b is None:
                print(f"[skip] {reg} {arm}"); continue
            gain = (g - b) * 100
            lo, hi = boot_ci(gain.values)
            vs_n = (gain - (naive[reg] - base[reg]) * 100)
            nlo, nhi = boot_ci(vs_n.values)
            vs_l = (gain - (lp32[reg] - base[reg]) * 100)
            llo, lhi = boot_ci(vs_l.values)
            extra = summary_means(d, "ks_max",
                                  ["n_triggers", "n_adaptations", "n_gate_rejections",
                                   "n_candidates_trained", "n_train_skipped",
                                   "labels_probe", "labels_monitor", "labels_candidate"])
            rows.append(dict(regime=reg, arm=arm, n=len(gain),
                             gain=round(float(gain.mean()), 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                             vs_naive=round(float(vs_n.mean()), 3), vsn_lo=round(nlo, 3), vsn_hi=round(nhi, 3),
                             vs_lp32=round(float(vs_l.mean()), 3), vsl_lo=round(llo, 3), vsl_hi=round(lhi, 3),
                             **{k: round(v, 2) for k, v in extra.items()}))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/robustness.csv", index=False)
    print("== robustness/two-stage/enscal/river =="); print(R.to_string(index=False)); print()

    # --- label & compute cost accounting (Amendment D definitions) ---
    # reconstructed for pre-existing arms: candidates = n_triggers, candidate labels = 1024 each
    cost_rows = []
    legacy = [("none (naive)", "paper2_v2_{r}_ks_none", "ks_max", 32 * 0, "v2"),
              ("labeled_probe b=32", "paper2_v2_{r}_ks_lp32", "ks_max", 32, "v2"),
              ("holdout (dedup)", "paper2_v2_{r}_ks_holdout32b", "ks_max", 0, "v2"),
              ("lcb b=64", "paper2_v2_{r}_ks_lcb64", "ks_max", 64, "v2"),
              ("ddm (canonical)", "paper2_v4_{r}_ddm_none", "ks_max", 0, "v4"),
              ("sliding_window", "paper2_v4_{r}_sliding_window_none", "ks_max", 0, "v4"),
              ("ensemble", "paper2_v4_{r}_ensemble_none", "ks_max", 0, "v4")]
    for reg in REGIMES:
        for label, tpl, method, probe_b, harness in legacy:
            dirs = [tpl.format(r=reg)] + ([tpl.format(r=reg) + "_top"] if harness == "v2" else [])
            m = summary_means(dirs, method, ["n_triggers", "n_adaptations", "n_gate_rejections",
                                             "labels_used_total"])
            if not m:
                print(f"[skip cost] {reg} {label}"); continue
            n_trig = m["n_triggers"]
            cand_labels = n_trig * 1024 if label != "sliding_window" else n_trig * 1024  # 8x128 windows
            monitor = 800 if label.startswith("ddm") else 0
            probe = n_trig * probe_b
            cost_rows.append(dict(regime=reg, policy=label,
                                  triggers=round(n_trig, 2), commits=round(m["n_adaptations"], 2),
                                  rejected=round(m["n_gate_rejections"], 2),
                                  candidates_trained=round(n_trig, 2),
                                  monitor_labels=monitor, candidate_labels=round(cand_labels, 0),
                                  probe_labels=round(probe, 1),
                                  total_labels=round(monitor + cand_labels + probe, 0)))
        # two_stage from real counters
        m = summary_means([f"paper2_v6_{reg}_twostage"], "ks_max",
                          ["n_triggers", "n_adaptations", "n_gate_rejections", "n_candidates_trained",
                           "n_train_skipped", "labels_probe", "labels_monitor", "labels_candidate"])
        if m:
            cost_rows.append(dict(regime=reg, policy="two_stage b=32",
                                  triggers=round(m["n_triggers"], 2), commits=round(m["n_adaptations"], 2),
                                  rejected=round(m["n_gate_rejections"], 2),
                                  candidates_trained=round(m["n_candidates_trained"], 2),
                                  monitor_labels=round(m["labels_monitor"], 0),
                                  candidate_labels=round(m["labels_candidate"], 0),
                                  probe_labels=round(m["labels_probe"], 1),
                                  total_labels=round(m["labels_monitor"] + m["labels_candidate"] + m["labels_probe"], 0)))
    CO = pd.DataFrame(cost_rows)
    CO.to_csv(f"{OUT}/label_cost.csv", index=False)
    print("== label_cost =="); print(CO.to_string(index=False)); print()

    # --- corrected temporal streams (headline: BA over two-class windows) ---
    t_rows = []
    tseeds = dict(fri=set(range(165, 195)), wed=set(range(196, 226)), thu=set(range(227, 257)))
    for stream in ["fri", "wed", "thu"]:
        S = tseeds[stream]
        arms_t = {}
        for gate, dname in [("naive", f"paper2_v6_temporal_{stream}_none"),
                            ("gate", f"paper2_v6_temporal_{stream}_labeled_probe")]:
            for m, key in [("no_adaptation", f"{gate}_base"), ("ks_max", gate)]:
                for col, suffix in [("mean_balanced_accuracy", ""), ("mean_accuracy", "_acc")]:
                    arms_t[key + suffix] = by_seed([dname], m, col=col, seeds=S)
        n2c = by_seed([f"paper2_v6_temporal_{stream}_none"], "ks_max", col="n_two_class", seeds=S)
        for metric, sfx in [("BA_two_class", ""), ("accuracy_all", "_acc")]:
            base_t = arms_t["naive_base" + sfx]
            nv, gt = arms_t["naive" + sfx], arms_t["gate" + sfx]
            for name, v in [("no_adapt_level", base_t), ("naive_vs_noadapt", (nv - base_t) * 100),
                            ("gate_vs_noadapt", (gt - base_t) * 100), ("gate_vs_naive", (gt - nv) * 100)]:
                vals = v.dropna()
                lo, hi = boot_ci(vals.values)
                t_rows.append(dict(stream=stream, metric=metric, quantity=name,
                                   value=round(float(vals.mean()), 3) if name != "no_adapt_level"
                                   else round(float(vals.mean()) * 100, 2),
                                   ci_lo=round(lo if name != "no_adapt_level" else lo * 100, 3),
                                   ci_hi=round(hi if name != "no_adapt_level" else hi * 100, 3),
                                   n=len(vals)))
        t_rows.append(dict(stream=stream, metric="n_two_class_windows", quantity="mean",
                           value=round(float(n2c.mean()), 1), ci_lo=np.nan, ci_hi=np.nan, n=len(n2c)))
    T = pd.DataFrame(t_rows)
    T.to_csv(f"{OUT}/temporal.csv", index=False)
    print("== temporal (corrected runner) =="); print(T.to_string(index=False))


if __name__ == "__main__":
    main()
