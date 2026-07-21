"""final-q1 Fase F: the paper's one multiplicity table.

Two families, treated differently and labelled as such:

  * CONFIRMATORY CORE -- the registered gate-vs-naive contrasts of the hardened replication
    (the primary gate, both detectors, three regimes). This is a genuine inferential family
    of 6 pre-declared tests, so it gets HOLM step-down control of the family-wise error.
  * REGISTERED FOLLOW-UPS -- BENJAMINI-HOCHBERG within each block that makes several
    inferential statements at once. This script corrects exactly two such families: the
    selected budget-frontier configurations (PortScan full, Bonferroni, committing arms) and
    the strict-gate-versus-no-adaptation family across the seven chronological replays. Other
    point/VBC-SG/naive comparisons are descriptive and are not automatically corrected here.

Everything else in the paper is descriptive and is not corrected -- and, per the protocol,
must not carry confirmatory language. The audit cross-checks that the manuscript's stated
policy matches what this script actually applied.

p-values come from the per-seed paired bootstrap already used for the intervals: a two-sided
bootstrap p is 2*min(P(diff<=0), P(diff>=0)), floored at 1/n_boot.

Output: results/tables/paper2_final_q1/multiplicity.csv
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

T = "results/tables"
OUT = f"{T}/paper2_final_q1"
N_BOOT = 20000


def boot_p(diff: float, lo: float, hi: float) -> float:
    """Two-sided p implied by a symmetric-ish bootstrap interval.

    We do not have the raw resamples in the published CSVs, so we invert the reported 95%
    interval under a normal approximation -- adequate here because every contrast is a mean
    over 30 seeds. Stated as an approximation rather than an exact bootstrap p.
    """
    se = (hi - lo) / (2 * 1.959964)
    if se <= 0:
        return 1.0
    from scipy.stats import norm
    return float(2 * norm.sf(abs(diff) / se))


def holm(ps: list[float]) -> list[float]:
    m = len(ps)
    order = np.argsort(ps)
    adj = np.empty(m, float)
    running = 0.0
    for rank, idx in enumerate(order):
        val = (m - rank) * ps[idx]
        running = max(running, val)
        adj[idx] = min(1.0, running)
    return adj.tolist()


def bh(ps: list[float]) -> list[float]:
    m = len(ps)
    order = np.argsort(ps)[::-1]
    adj = np.empty(m, float)
    running = 1.0
    for rank, idx in enumerate(order):
        val = m / (m - rank) * ps[idx]
        running = min(running, val)
        adj[idx] = min(1.0, running)
    return adj.tolist()


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    rows = []

    # ---- family 1: confirmatory core, Holm ----
    ci = pd.read_csv(f"{T}/paper2_v2_replication_001/paired_ci.csv")
    core = ci[ci.contrast == "lp32_vs_naive"].copy()
    ps = [boot_p(r.diff, r.ci_lo, r.ci_hi) for r in core.itertuples()]
    core["p_raw"] = ps
    core["p_adj"] = holm(ps)
    core["family"] = "confirmatory core (gate vs naive)"
    core["method"] = "Holm"
    for r in core.itertuples():
        rows.append(dict(family=r.family, method=r.method,
                         test=f"{r.detector}/{r.regime} lp32 vs naive",
                         effect=r.diff, ci_lo=r.ci_lo, ci_hi=r.ci_hi,
                         p_raw=round(r.p_raw, 5), p_adj=round(r.p_adj, 5),
                         significant_adj=bool(r.p_adj < 0.05)))

    # ---- family 2: registered follow-up blocks, BH within block ----
    bf = f"{OUT}/budget_frontier.csv"
    if os.path.exists(bf):
        B = pd.read_csv(bf)
        b = B[(B.scenario == "ps_full") & (B.schedule == "bonf") & (B.commits_total > 0)].copy()
        if len(b):
            ps2 = [boot_p(r.gain, r.lo, r.hi) for r in b.itertuples()]
            b["p_raw"] = ps2; b["p_adj"] = bh(ps2)
            for r in b.itertuples():
                rows.append(dict(family="registered follow-up: budget frontier (PortScan full)",
                                 method="Benjamini-Hochberg",
                                 test=f"{r.policy}/cap{r.cap} gain vs no-adaptation",
                                 effect=r.gain, ci_lo=r.lo, ci_hi=r.hi,
                                 p_raw=round(r.p_raw, 5), p_adj=round(r.p_adj, 5),
                                 significant_adj=bool(r.p_adj < 0.05)))

    ch = f"{OUT}/chronological_replays.csv"
    if os.path.exists(ch):
        C = pd.read_csv(ch)
        c = C[C.policy == "strict"].copy()
        if len(c):
            ps3 = [boot_p(r.gain_ba * 100, r.ba_lo * 100, r.ba_hi * 100) for r in c.itertuples()]
            c["p_raw"] = ps3; c["p_adj"] = bh(ps3)
            for r in c.itertuples():
                rows.append(dict(family="registered follow-up: chronological matrix (strict)",
                                 method="Benjamini-Hochberg",
                                 test=f"{r.stream} strict gain vs no-adaptation",
                                 effect=round(r.gain_ba * 100, 3),
                                 ci_lo=round(r.ba_lo * 100, 3), ci_hi=round(r.ba_hi * 100, 3),
                                 p_raw=round(r.p_raw, 5), p_adj=round(r.p_adj, 5),
                                 significant_adj=bool(r.p_adj < 0.05)))

    M = pd.DataFrame(rows)
    M.to_csv(f"{OUT}/multiplicity.csv", index=False)
    print(M.to_string(index=False))
    print("\n== survival under adjustment, per family ==")
    for fam, g in M.groupby("family"):
        n_raw = int((g.p_raw < 0.05).sum()); n_adj = int(g.significant_adj.sum())
        print(f"  {fam}: {n_adj}/{len(g)} survive ({n_raw} were nominally significant)")


if __name__ == "__main__":
    main()
