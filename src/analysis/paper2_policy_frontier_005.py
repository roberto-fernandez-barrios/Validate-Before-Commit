"""Policy frontier and operational-utility scenarios (amendment 005, G — locked pre-analysis).

Frontier per regime over the evaluated policies: gain vs no-adaptation, total labels
(amendment-004 accounting), commits, model growth, explicit no-deploy capability.
Utility in flow-error equivalents over N = 12,800 evaluated flows/stream:
  U = (gain/100) * N - c_L * total_labels - c_U * commits
Scenarios (c_L, c_U) in {(0.1, 50), (1, 50), (0.1, 500), (1, 500)}.
Outputs results/tables/paper2_policy_frontier_005/{frontier,utility_scenarios}.csv
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_policy_frontier_005"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
SEEDS = set(range(104, 134))
N_FLOWS = 12_800
SCENARIOS = [(0.1, 50), (1.0, 50), (0.1, 500), (1.0, 500)]

# policy -> (dirs template, method, monitor labels/stream, probe labels per trigger,
#            model growth, can reject)
POLICIES = {
    "naive": (["paper2_v2_{r}_ks_none", "paper2_v2_{r}_ks_none_top"], 0, 0, False, False),
    "labeled_probe_b32": (["paper2_v2_{r}_ks_lp32", "paper2_v2_{r}_ks_lp32_top"], 0, 32, False, True),
    "holdout_dedup": (["paper2_v2_{r}_ks_holdout32b"], 0, 0, False, True),
    "lcb_b64": (["paper2_v2_{r}_ks_lcb64", "paper2_v2_{r}_ks_lcb64_top"], 0, 64, False, True),
    "two_stage_split_d05": (["paper2_v7_{r}_twostage_d05"], 0, None, False, True),  # real counters
    "ensemble_cal": (["paper2_v6_{r}_enscal_none"], 0, 0, True, False),
    "ddm_river_b8": (["paper2_v6_{r}_ddmriver_none"], 800, 0, False, False),
    "sliding_window": (["paper2_v4_{r}_sliding_window_none"], 0, 0, False, False),
}


def by_seed(dirs, method, col="mean_balanced_accuracy"):
    parts = [pd.read_csv(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")
             for d in dirs if os.path.exists(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")]
    if not parts:
        return None
    d = pd.concat(parts)
    d = d[(d.method == method) & (d.seed.isin(SEEDS))]
    return d.set_index("seed")[col].sort_index() if len(d) else None


def means(dirs, cols):
    parts = [pd.read_csv(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")
             for d in dirs if os.path.exists(f"{RAW}/{d}/paper2_progressive_readaptation_by_seed.csv")]
    d = pd.concat(parts)
    d = d[(d.method == "ks_max") & (d.seed.isin(SEEDS))]
    return {c: float(d[c].mean()) for c in cols if c in d.columns}


def main():
    os.makedirs(OUT, exist_ok=True)
    frows, urows = [], []
    for reg in REGIMES:
        for pol, (tpl, mon, probe_b, grows, rejects) in POLICIES.items():
            dirs = [t.format(r=reg) for t in tpl]
            g = by_seed(dirs, "ks_max")
            b = by_seed(dirs, "no_adaptation")
            if g is None or b is None:
                print(f"[skip] {reg} {pol}"); continue
            gain = float(((g - b) * 100).mean())
            m = means(dirs, ["n_triggers", "n_adaptations", "n_candidates_trained",
                             "labels_candidate", "labels_probe", "labels_monitor"])
            if probe_b is None and "labels_candidate" in m:   # real counters (two_stage v7)
                cand_labels = m["labels_candidate"]; probe_labels = m["labels_probe"]
                monitor = m.get("labels_monitor", 0)
            else:
                cand_labels = m["n_triggers"] * 1024
                probe_labels = m["n_triggers"] * probe_b
                monitor = mon
            total = monitor + cand_labels + probe_labels
            frows.append(dict(regime=reg, policy=pol, gain=round(gain, 3),
                              commits=round(m["n_adaptations"], 2),
                              total_labels=round(total, 0),
                              model_grows=grows, can_reject=rejects))
            for cl, cu in SCENARIOS:
                u = (gain / 100) * N_FLOWS - cl * total - cu * m["n_adaptations"]
                urows.append(dict(regime=reg, policy=pol, c_label=cl, c_update=cu,
                                  utility=round(u, 0)))
    F, U = pd.DataFrame(frows), pd.DataFrame(urows)
    F.to_csv(f"{OUT}/frontier.csv", index=False)
    U.to_csv(f"{OUT}/utility_scenarios.csv", index=False)
    print("== frontier =="); print(F.to_string(index=False)); print()
    print("== utility winners per regime x scenario ==")
    W = U.loc[U.groupby(["regime", "c_label", "c_update"]).utility.idxmax()]
    print(W.to_string(index=False))


if __name__ == "__main__":
    main()
