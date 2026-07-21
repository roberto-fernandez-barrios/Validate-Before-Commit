"""final-q1 D3: aggregate the budget-frontier arms into the registered endpoints e1-e6.

Input : results/raw/q1fc_* (by_seed summaries + trigger logs; driver run_q1_faseC.py)
Output: results/tables/paper2_final_q1/budget_frontier.csv
        results/tables/paper2_final_q1/frontier_anchors.csv
        console: the registered non-vacuity verdict (protocol q1_max_protocol.md, D3)

Endpoints, per (scenario, policy, cap, schedule):
  e1 smallest cap with >= 1 commit (table-level, per policy x schedule x scenario)
  e2 fraction of the naive benefit recovered (only where naive gain > 0)
  e3 probe labels per commit
  e4 abstention rate: deferral-cap rejections / proposals (neither commit nor futility)
  e5 decision delay: mean windows from proposal to resolution (0 for immediate)
  e6 harmful-commit rate with Clopper-Pearson 95% CI. Immediate commits are judged by the
     trigger log's five-window lookahead at the proposal; commits that happen at a deferred
     resolution have no lookahead row and are counted separately (n_commits_deferred) --
     a documented proxy, not hidden.
"""
from __future__ import annotations

import os
import re

import numpy as np
import pandas as pd
from scipy.stats import beta

RAW = "results/raw"
OUT = "results/tables/paper2_final_q1"
SCENARIOS = ("ps_full", "ton_full", "ton_zero")
POLICIES = ("ebcsdef", "vbccoh", "vbcref")
CAPS = (64, 128, 256, 512, 1024)
SCHEDULES = ("bonf", "pser")
NAIVE_TRAIN_LABELS = 1024   # candidate training cost per proposal (512/class)


def load(tag):
    f = f"{RAW}/{tag}/paper2_progressive_readaptation_by_seed.csv"
    return pd.read_csv(f) if os.path.exists(f) else None


def paired_gain(s):
    g = s[s.method == "ks_max"].set_index("seed")["mean_balanced_accuracy"]
    b = s[s.method == "no_adaptation"].set_index("seed")["mean_balanced_accuracy"]
    d = ((g - b) * 100).dropna()
    rng = np.random.default_rng(0)
    bs = rng.choice(d.to_numpy(), size=(10000, len(d)), replace=True).mean(1)
    return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))


def harm_from_resolution_log(tag: str) -> dict:
    """final-q1 blocker B: harmful-commit accounting over ALL resolved commits.

    Reads the per-proposal resolution log, keeps the commits (immediate and deferred alike),
    and scores each from the window where it actually took effect. A commit whose horizon
    runs off the end of the stream is CENSORED, never silently scored short and never
    counted as harmless. Returns the counts the manuscript and the manifest both quote.
    """
    f = f"{RAW}/{tag}/paper2_v2_resolution_log.csv"
    out = dict(n_immediate=0, n_deferred=0, n_commits=0, n_evaluable_h5=0, n_censored_h5=0,
               harmful_h5=0, harmful_h5_immediate=0, harmful_h5_deferred=0,
               n_evaluable_until_next=0, harmful_until_next=0, mean_delta_h5=float("nan"))
    if not os.path.exists(f):
        return out
    r = pd.read_csv(f)
    c = r[r.resolution_type == "commit"]
    if not len(c):
        return out
    ev = c[~c.censored_h5.astype(bool)]
    evn = c[~c.censored_until_next.astype(bool)] if "censored_until_next" in c else c.iloc[:0]
    out.update(
        n_commits=len(c),
        n_immediate=int((~c.deferred.astype(bool)).sum()),
        n_deferred=int(c.deferred.astype(bool).sum()),
        n_evaluable_h5=len(ev), n_censored_h5=int(c.censored_h5.astype(bool).sum()),
        harmful_h5=int((ev.delta_res5 < 0).sum()),
        harmful_h5_immediate=int(((ev.delta_res5 < 0) & (~ev.deferred.astype(bool))).sum()),
        harmful_h5_deferred=int(((ev.delta_res5 < 0) & (ev.deferred.astype(bool))).sum()),
        n_evaluable_until_next=len(evn),
        harmful_until_next=int((evn.delta_until_next < 0).sum()) if len(evn) else 0,
        mean_delta_h5=round(float(ev.delta_res5.mean()), 4) if len(ev) else float("nan"),
    )
    return out


def clopper_pearson(k, n, a=0.05):
    if n == 0:
        return (np.nan, np.nan)
    lo = beta.ppf(a / 2, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(1 - a / 2, k + 1, n - k) if k < n else 1.0
    return (float(lo), float(hi))


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    anchors, rows = [], []
    naive_gain = {}
    for sc in SCENARIOS:
        for name in ("none", "point", "strict"):
            s = load(f"q1fc_{sc}_{name}")
            if s is None:
                continue
            gain, lo, hi = paired_gain(s)
            arm = s[s.method == "ks_max"]
            anchors.append(dict(scenario=sc, policy=name, gain=round(gain, 3),
                                lo=round(lo, 3), hi=round(hi, 3),
                                commits=round(float(arm.n_adaptations.mean()), 2),
                                labels_probe=round(float(arm.labels_probe.mean()), 1)))
            if name == "none":
                naive_gain[sc] = gain
    for sc in SCENARIOS:
        for pol in POLICIES:
            for cap in CAPS:
                for sch in SCHEDULES:
                    tag = f"q1fc_{sc}_{pol}_c{cap}_{sch}"
                    s = load(tag)
                    if s is None:
                        continue
                    gain, lo, hi = paired_gain(s)
                    arm = s[s.method == "ks_max"]
                    commits = int(arm.n_adaptations.sum())
                    props = int(arm.n_candidates_trained.sum())
                    lp = int(arm.labels_probe.sum())
                    cap_rej = int(arm.get("n_defer_cap_reject", pd.Series([0])).fillna(0).sum())
                    delay = float(arm.get("defer_delay_sum", pd.Series([0])).fillna(0).sum())
                    # e6 (final-q1 blocker B): score EVERY resolved commit -- immediate AND
                    # deferred -- from its REAL resolution window, with explicit censoring for
                    # commits whose horizon runs past the end of the stream. The earlier
                    # version scored only immediate commits off the proposal-time lookahead,
                    # which left ~35% of the sweep's commits unevaluated.
                    h = harm_from_resolution_log(tag)
                    n_imm, n_def = h["n_immediate"], h["n_deferred"]
                    k_harm, n_eval = h["harmful_h5"], h["n_evaluable_h5"]
                    cp_lo, cp_hi = clopper_pearson(k_harm, n_eval)
                    ng = naive_gain.get(sc, np.nan)
                    rows.append(dict(
                        scenario=sc, policy=pol, cap=cap, schedule=sch,
                        gain=round(gain, 3), lo=round(lo, 3), hi=round(hi, 3),
                        naive_gain=round(ng, 3) if ng == ng else np.nan,
                        e2_frac_naive=(round(gain / ng, 3) if ng == ng and ng > 0 else np.nan),
                        commits_total=commits, proposals=props,
                        commits_per_stream=round(commits / max(1, arm.seed.nunique()), 2),
                        e3_labels_per_commit=(round(lp / commits, 1) if commits else np.nan),
                        labels_probe_per_proposal=(round(lp / props, 1) if props else np.nan),
                        labels_probe_per_stream=round(float(arm.labels_probe.mean()), 1),
                        e4_abstention=(round(cap_rej / props, 3) if props else np.nan),
                        e5_delay_windows=(round(delay / props, 2) if props else np.nan),
                        n_commits_immediate=n_imm, n_commits_deferred=n_def,
                        e6_n_evaluable=n_eval, e6_n_censored=h["n_censored_h5"],
                        e6_harmful_h5=k_harm,
                        e6_harmful_immediate=h["harmful_h5_immediate"],
                        e6_harmful_deferred=h["harmful_h5_deferred"],
                        e6_rate=(round(k_harm / n_eval, 3) if n_eval else np.nan),
                        e6_cp_lo=round(cp_lo, 3) if cp_lo == cp_lo else np.nan,
                        e6_cp_hi=round(cp_hi, 3) if cp_hi == cp_hi else np.nan,
                        e6_harmful_until_next=h["harmful_until_next"],
                        e6_n_eval_until_next=h["n_evaluable_until_next"],
                        e6_mean_delta_h5=h["mean_delta_h5"],
                    ))
    A = pd.DataFrame(anchors); R = pd.DataFrame(rows)
    A.to_csv(f"{OUT}/frontier_anchors.csv", index=False)
    R.to_csv(f"{OUT}/budget_frontier.csv", index=False)
    print(A.to_string(index=False)); print(); print(R.to_string(index=False))

    # e1 + the registered non-vacuity verdict
    if len(R):
        print("\n== e1: smallest cap with >= 1 commit ==")
        for (sc, pol, sch), g in R.groupby(["scenario", "policy", "schedule"]):
            gc = g[g.commits_total > 0]
            e1 = int(gc.cap.min()) if len(gc) else None
            print(f"  {sc}/{pol}/{sch}: {e1 if e1 else 'never commits (<=1024)'}")
        print("\n== registered non-vacuity target (PortScan full) ==")
        ps = R[(R.scenario == "ps_full") & (R.commits_total > 0)]
        ng = naive_gain.get("ps_full", np.nan)
        ok = ps[(ps.e2_frac_naive >= 0.5) & (ps.labels_probe_per_proposal < NAIVE_TRAIN_LABELS)]
        if len(ok):
            harm_zero = []
            for _, r in ok.iterrows():
                z = R[(R.scenario == "ton_zero") & (R.policy == r.policy)
                      & (R.cap == r.cap) & (R.schedule == r.schedule)]
                if len(z) and int(z.iloc[0].commits_total) == 0:
                    harm_zero.append(r)
            if harm_zero:
                print("  NON-VACUOUS operating point(s) found:")
                for r in harm_zero:
                    print(f"    {r.policy}/cap{r.cap}/{r.schedule}: gain {r.gain:+.2f} "
                          f"({r.e2_frac_naive:.0%} of naive {ng:+.2f}), "
                          f"{r.labels_probe_per_proposal:.0f} probe labels/proposal, "
                          f"ton_zero commits 0")
            else:
                print("  candidates recover >=50% but none is zero-commit under zero drift")
        else:
            print("  NO lifetime configuration meets the target at cap <= 1024 ->")
            print("  use the registered endpoint sentence (protocol D3): 'formal risk endpoint,")
            print("  not the recommended practical policy at these budgets'")


if __name__ == "__main__":
    main()
