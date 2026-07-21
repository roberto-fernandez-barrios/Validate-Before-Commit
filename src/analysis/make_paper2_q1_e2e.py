"""final-q1 D5 (P1.4): aggregate the operational end-to-end sweep.

Output: results/tables/paper2_final_q1/operational_e2e.csv + console summary. The headline
form fixed in the protocol: "b adjudicated labels required X inspected flows under policy Y
at prevalence pi" -- reported here as inspected_flows_per_attack = probe_size / attacks_found.
"""
from __future__ import annotations

import glob
import os

import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_final_q1"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for d in sorted(glob.glob(f"{RAW}/q1fd5b_*")):
        if not os.path.isdir(d):
            continue
        f = f"{d}/paper2_progressive_readaptation_by_seed.csv"
        if not os.path.exists(f):
            continue
        tag = os.path.basename(d)
        parts = tag[len("q1fd5b_"):].split("_")
        ds = parts[0]
        # tag encodes prevalence with 3 digits in the main grid (pi005 = 0.005, pi050 = 0.05)
        # and 2 digits in the latency/delay sensitivity arms (pi05 = 0.05)
        pidigits = parts[1][2:]
        pi = int(pidigits) / (1000.0 if len(pidigits) == 3 else 100.0)
        rest = "_".join(parts[2:])
        # rest = "<acquisition>_l<CL>d<TD>"
        acq, latdelay = rest.rsplit("_l", 1)
        cl = int(latdelay.split("d")[0]); td = int(latdelay.split("d")[1])
        s = pd.read_csv(f)
        arm = s[s.method == "ks_max"]
        na = s[s.method == "no_adaptation"]
        gain = float(arm.mean_balanced_accuracy.mean() - na.mean_balanced_accuracy.mean())
        rng = np.random.default_rng(0)
        pair = (arm.set_index("seed").mean_balanced_accuracy
                - na.set_index("seed").mean_balanced_accuracy).dropna()
        bs = (rng.choice(pair.to_numpy(), size=(10000, len(pair)), replace=True).mean(1)
              if len(pair) else np.array([np.nan]))
        attacks_total = float(arm.attacks_found_total.sum())
        labels_total = float(arm.labels_used.sum())
        rows.append(dict(
            dataset=ds, prevalence=pi, acquisition=acq, cand_latency=cl, train_delay=td,
            n_seeds=len(arm), noadapt_ba=round(float(na.mean_balanced_accuracy.mean()), 4),
            gain=round(gain, 4), lo=round(float(np.percentile(bs, 2.5)), 4),
            hi=round(float(np.percentile(bs, 97.5)), 4),
            triggers_per_stream=round(float(arm.n_triggers.mean()), 2),
            commits_per_stream=round(float(arm.n_adaptations.mean()), 2),
            attacks_found_total=int(attacks_total), labels_total=int(labels_total),
            inspected_flows_per_attack=(round(labels_total / attacks_total, 1)
                                        if attacks_total else np.nan),
            expected_random_ratio=round(1.0 / pi, 1),
            # final-q1 blocker D: acquisition COST (the enriched discovery half) is reported
            # separately from decision VALIDITY (the validation half is an independent
            # uniform draw at operating prevalence -- the only sample the gate ever sees).
            dual_sample=bool(arm.dual_sample.iloc[0]) if "dual_sample" in arm else False,
            discovery_attacks=int(arm.discovery_attacks.sum()) if "discovery_attacks" in arm else 0,
            validation_attacks=int(arm.validation_attacks.sum()) if "validation_attacks" in arm else 0,
            discovery_flows_per_attack=(
                round((labels_total / 2) / arm.discovery_attacks.sum(), 1)
                if "discovery_attacks" in arm and arm.discovery_attacks.sum() else np.nan),
        ))
    R = pd.DataFrame(rows).sort_values(["dataset", "prevalence", "acquisition"])
    R.to_csv(f"{OUT}/operational_e2e.csv", index=False)
    print(R.to_string(index=False))

    print("\n== acquisition enrichment vs random (main grid, l5d0) ==")
    base = R[(R.cand_latency == 5) & (R.train_delay == 0)]
    for ds in base.dataset.unique():
        for pi in sorted(base.prevalence.unique()):
            cell = base[(base.dataset == ds) & (base.prevalence == pi)]
            r = cell[cell.acquisition == "random"]
            if not len(r) or r.iloc[0].discovery_flows_per_attack != r.iloc[0].discovery_flows_per_attack:
                continue
            r_ratio = r.iloc[0].discovery_flows_per_attack
            for acq in ("alert_enriched", "disagreement", "hybrid"):
                a = cell[cell.acquisition == acq]
                if len(a) and a.iloc[0].discovery_flows_per_attack == a.iloc[0].discovery_flows_per_attack:
                    factor = r_ratio / a.iloc[0].discovery_flows_per_attack
                    print(f"  {ds}/pi={pi}: {acq} needs {a.iloc[0].discovery_flows_per_attack:.1f} "
                          f"flows/attack vs random's {r_ratio:.1f} ({factor:.1f}x)")

    print("\n== latency/training-delay sensitivity (pi=0.05, random) ==")
    sens = R[(R.prevalence == 0.05) & (R.acquisition == "random")]
    print(sens[["dataset", "cand_latency", "train_delay", "gain", "lo", "hi"]].to_string(index=False))


if __name__ == "__main__":
    main()
