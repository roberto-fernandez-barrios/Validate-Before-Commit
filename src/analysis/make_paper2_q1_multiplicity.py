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

p-values (q1-final-patch, Block E). Wherever the per-seed files are on disk, the paired
contrast is bootstrapped DIRECTLY: a deterministic seed-level paired bootstrap with
N_BOOT = 20000 resamples, two-sided p = 2*min(P(mean<=0), P(mean>=0)), floored at 1/N_BOOT,
with a per-contrast RNG derived from the contrast label (order-independent, exactly
reproducible; see tests/test_q1_temporal_semantics.py's sibling reproducibility test).
Where a family's per-seed data are NOT available, the p is a NORMAL-APPROXIMATION INVERSION
OF THE PUBLISHED INTERVAL and is labelled as such in the `p_method` column -- it is never
called an exact bootstrap p-value. No conclusion in the manuscript depends on the
approximate branch: it exists only as a fallback for re-runs on partial checkouts.

Output: results/tables/paper2_final_q1/multiplicity.csv
"""
from __future__ import annotations

import os
import zlib

import numpy as np
import pandas as pd

T = "results/tables"
RAW = "results/raw"
OUT = f"{T}/paper2_final_q1"
N_BOOT = 20000
BOOT_SEED = 20260721
EXACT = f"exact paired bootstrap ({N_BOOT} resamples, deterministic seed {BOOT_SEED})"
APPROX = "normal-approximation inversion of the published interval"


def boot_p_exact(d: np.ndarray, label: str) -> float:
    """Deterministic two-sided seed-level paired bootstrap p for mean(d) = 0."""
    d = np.asarray(d, float)
    n = len(d)
    rng = np.random.default_rng(BOOT_SEED + zlib.crc32(label.encode()))
    b = d[rng.integers(0, n, (N_BOOT, n))].mean(1)
    p = 2.0 * min(float((b <= 0).mean()), float((b >= 0).mean()))
    return max(p, 1.0 / N_BOOT)


def boot_p(diff: float, lo: float, hi: float) -> float:
    """Fallback only: two-sided p implied by a symmetric-ish bootstrap interval, inverted
    under a normal approximation. Labelled APPROX in the output; never used when the
    per-seed files are present."""
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


def _arm_gain_per_seed(tag: str) -> np.ndarray | None:
    """Per-seed paired gain (ks_max - no_adaptation, in BA points) for one raw arm dir."""
    f = f"{RAW}/{tag}/paper2_progressive_readaptation_by_seed.csv"
    if not os.path.exists(f):
        return None
    s = pd.read_csv(f)
    g = s[s.method == "ks_max"].set_index("seed")["mean_balanced_accuracy"]
    n = s[s.method == "no_adaptation"].set_index("seed")["mean_balanced_accuracy"]
    d = ((g - n) * 100).dropna()
    return d.values if len(d) else None


def _core_diff_per_seed(det: str, reg: str) -> np.ndarray | None:
    """Per-seed paired lp32-vs-naive difference for the confirmatory core, built from the
    same raw by_seed files the replication aggregator uses."""
    from src.analysis.aggregate_paper2_v2_replication import arm_dirs, read_by_seed
    method = "ks_max" if det == "ks" else "qk_mmd_zz"
    out = {}
    for arm in ("lp32", "none"):
        dirs = arm_dirs(reg, det, arm)
        na = read_by_seed(dirs, "no_adaptation")
        g = read_by_seed(dirs, method)
        if na is None or g is None:
            return None
        out[arm] = (g - na) * 100
    idx = out["lp32"].index.intersection(out["none"].index)
    if len(idx) < 25:
        return None
    return (out["lp32"][idx] - out["none"][idx]).values


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    rows = []

    # ---- family 1: confirmatory core, Holm ----
    ci = pd.read_csv(f"{T}/paper2_v2_replication_001/paired_ci.csv")
    core = ci[ci.contrast == "lp32_vs_naive"].copy()
    ps, methods = [], []
    for r in core.itertuples():
        label = f"core/{r.detector}/{r.regime}/lp32_vs_naive"
        d = _core_diff_per_seed(r.detector, r.regime)
        if d is not None:
            ps.append(boot_p_exact(d, label)); methods.append(EXACT)
        else:
            ps.append(boot_p(r.diff, r.ci_lo, r.ci_hi)); methods.append(APPROX)
    core["p_raw"], core["p_method"] = ps, methods
    core["p_adj"] = holm(ps)
    for r in core.itertuples():
        rows.append(dict(family="confirmatory core (gate vs naive)", method="Holm",
                         test=f"{r.detector}/{r.regime} lp32 vs naive",
                         effect=r.diff, ci_lo=r.ci_lo, ci_hi=r.ci_hi,
                         p_raw=round(r.p_raw, 5), p_adj=round(r.p_adj, 5),
                         p_method=r.p_method,
                         significant_adj=bool(r.p_adj < 0.05)))

    # ---- family 2: registered follow-up blocks, BH within block ----
    bf = f"{OUT}/budget_frontier.csv"
    if os.path.exists(bf):
        B = pd.read_csv(bf)
        b = B[(B.scenario == "ps_full") & (B.schedule == "bonf") & (B.commits_total > 0)].copy()
        if len(b):
            ps2, m2 = [], []
            for r in b.itertuples():
                sch = "bonf" if r.schedule == "bonf" else r.schedule
                d = _arm_gain_per_seed(f"q1fc_{r.scenario}_{r.policy}_c{r.cap}_{sch}")
                label = f"frontier/{r.scenario}/{r.policy}/c{r.cap}/{sch}"
                if d is not None:
                    ps2.append(boot_p_exact(d, label)); m2.append(EXACT)
                else:
                    ps2.append(boot_p(r.gain, r.lo, r.hi)); m2.append(APPROX)
            b["p_raw"], b["p_method"] = ps2, m2
            b["p_adj"] = bh(ps2)
            for r in b.itertuples():
                rows.append(dict(family="registered follow-up: budget frontier (PortScan full)",
                                 method="Benjamini-Hochberg",
                                 test=f"{r.policy}/cap{r.cap} gain vs no-adaptation",
                                 effect=r.gain, ci_lo=r.lo, ci_hi=r.hi,
                                 p_raw=round(r.p_raw, 5), p_adj=round(r.p_adj, 5),
                                 p_method=r.p_method,
                                 significant_adj=bool(r.p_adj < 0.05)))

    ch = f"{OUT}/chronological_replays.csv"
    if os.path.exists(ch):
        C = pd.read_csv(ch)
        c = C[C.policy == "strict"].copy()
        if len(c):
            ps3, m3 = [], []
            for r in c.itertuples():
                d = _arm_gain_per_seed(f"q1fd_{r.stream}_strict")
                label = f"chrono/{r.stream}/strict"
                if d is not None:
                    ps3.append(boot_p_exact(d, label)); m3.append(EXACT)
                else:
                    ps3.append(boot_p(r.gain_ba * 100, r.ba_lo * 100, r.ba_hi * 100))
                    m3.append(APPROX)
            c["p_raw"], c["p_method"] = ps3, m3
            c["p_adj"] = bh(ps3)
            for r in c.itertuples():
                rows.append(dict(family="registered follow-up: chronological matrix (strict)",
                                 method="Benjamini-Hochberg",
                                 test=f"{r.stream} strict gain vs no-adaptation",
                                 effect=round(r.gain_ba * 100, 3),
                                 ci_lo=round(r.ba_lo * 100, 3), ci_hi=round(r.ba_hi * 100, 3),
                                 p_raw=round(r.p_raw, 5), p_adj=round(r.p_adj, 5),
                                 p_method=r.p_method,
                                 significant_adj=bool(r.p_adj < 0.05)))

    M = pd.DataFrame(rows)
    M.to_csv(f"{OUT}/multiplicity.csv", index=False)
    print(M.to_string(index=False))
    print("\n== survival under adjustment, per family ==")
    for fam, g in M.groupby("family"):
        n_raw = int((g.p_raw < 0.05).sum()); n_adj = int(g.significant_adj.sum())
        print(f"  {fam}: {n_adj}/{len(g)} survive ({n_raw} were nominally significant)")
    n_ap = int((M.p_method == APPROX).sum())
    print(f"\np-value provenance: {len(M) - n_ap}/{len(M)} exact paired bootstrap, "
          f"{n_ap} normal-approximation fallback")


if __name__ == "__main__":
    main()
