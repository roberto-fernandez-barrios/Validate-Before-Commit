"""final-q1 D4: aggregate the 7 new registered chronological replays x
{none, point, strict, vbc_sg-cohort}, seeds 601-630.

Output: results/tables/paper2_final_q1/chronological_replays.csv + console summary,
reporting BA gain vs no-adaptation (over two-class windows only, per the runner's metric-
homogeneity convention) and, where available, accuracy gain, commits, labels, and the
VBC-SG defer-step/delay statistics.
"""
from __future__ import annotations

import glob
import os

import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_final_q1"
STREAMS = ["tue_wedthufri", "wed_fri", "thu_fri", "wed_intraday", "thu_intraday",
          "unsw_20", "unsw_40"]
POLICIES = ["none", "point", "strict", "vbccoh"]


def paired(s, col):
    g = s[s.method == "ks_max"].set_index("seed")[col]
    b = s[s.method == "no_adaptation"].set_index("seed")[col]
    d = (g - b).dropna()
    if len(d) == 0:
        return (np.nan, np.nan, np.nan, 0)
    rng = np.random.default_rng(0)
    bs = rng.choice(d.to_numpy(), size=(10000, len(d)), replace=True).mean(1)
    return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), len(d))


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for sname in STREAMS:
        for pol in POLICIES:
            f = f"{RAW}/q1fd_{sname}_{pol}/paper2_progressive_readaptation_by_seed.csv"
            if not os.path.exists(f):
                continue
            s = pd.read_csv(f)
            gain_ba, lo, hi, n = paired(s, "mean_balanced_accuracy")
            gain_acc, alo, ahi, _ = paired(s, "mean_accuracy")
            arm = s[s.method == "ks_max"]
            noadapt_ba = float(s[s.method == "no_adaptation"].mean_balanced_accuracy.mean())
            noadapt_acc = float(s[s.method == "no_adaptation"].mean_accuracy.mean())
            row = dict(stream=sname, policy=pol, n_seeds_ba=n,
                      noadapt_ba=round(noadapt_ba, 4) if noadapt_ba == noadapt_ba else np.nan,
                      noadapt_acc=round(noadapt_acc, 4),
                      gain_ba=round(gain_ba, 4), ba_lo=round(lo, 4), ba_hi=round(hi, 4),
                      gain_acc=round(gain_acc, 4), acc_lo=round(alo, 4), acc_hi=round(ahi, 4),
                      commits_per_stream=round(float(arm.n_adaptations.mean()), 2),
                      labels_per_stream=round(float(arm.labels_used_total.mean()), 1)
                      if "labels_used_total" in arm else np.nan)
            if pol == "vbccoh" and "n_proposals" in arm:
                row["n_proposals_per_stream"] = round(float(arm.n_proposals.mean()), 2)
                row["vbc_steps_mean"] = round(float(arm.vbc_steps_mean.mean()), 2)
            rows.append(row)
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/chronological_replays.csv", index=False)
    print(R.to_string(index=False))

    # honest headline: does any stream show net harm (gate/naive below no-adapt) under the
    # obligatory strict baseline or the point gate?
    print("\n== net-harm scan (gain_ba < 0, CI excludes 0) ==")
    harmful = R[(R.policy.isin(["point", "strict", "vbccoh"])) & (R.gain_ba < 0) & (R.ba_hi < 0)]
    if len(harmful):
        print(harmful[["stream", "policy", "gain_ba", "ba_lo", "ba_hi"]].to_string(index=False))
    else:
        print("  none observed among the new replays (consistent with the six prior ones)")
    print("\n== gate premium on 'none' vs point/strict/vbccoh, per stream (BA) ==")
    for sname in STREAMS:
        base = R[(R.stream == sname) & (R.policy == "none")]
        if not len(base) or base.iloc[0].gain_ba != base.iloc[0].gain_ba:
            continue
        naive_gain = base.iloc[0].gain_ba
        for pol in ("point", "strict", "vbccoh"):
            g = R[(R.stream == sname) & (R.policy == pol)]
            if len(g) and g.iloc[0].gain_ba == g.iloc[0].gain_ba:
                premium = g.iloc[0].gain_ba - naive_gain
                print(f"  {sname:16s} {pol:8s}: gain {g.iloc[0].gain_ba:+.2f} vs naive "
                      f"{naive_gain:+.2f} (premium {premium:+.2f})")


if __name__ == "__main__":
    main()
