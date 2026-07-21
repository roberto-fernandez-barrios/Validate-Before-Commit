"""final-q1 Fase F: the paper's one multiplicity table.

Three families, fixed IN ADVANCE and independent of any observed outcome (q1-final-patch
v1.20.1, Block B — the earlier commits-positive frontier filter was outcome-dependent
selection and is removed):

  * F1 CONFIRMATORY CORE — exactly 6 contrasts (2 detectors x 3 regimes, primary b=32 gate
    vs naive), the registered superiority family. HOLM step-down FWER control.
  * F2 BUDGET FRONTIER — exactly 15 contrasts (3 policies x 5 caps, PortScan full drift,
    Bonferroni schedule), INCLUDING cells that never commit (their per-seed gain is still a
    well-defined paired difference vs no-adaptation). BENJAMINI-HOCHBERG within the block.
  * F3 CHRONOLOGICAL MATRIX — exactly 7 strict-gate-vs-no-adaptation replays.
    BENJAMINI-HOCHBERG within the block.

Everything else in the paper is descriptive and is not corrected -- and, per the protocol,
must not carry confirmatory language. The audit cross-checks that the manuscript's stated
policy matches what this script actually applied.

p-values (q1-final-patch v1.20.1). The primary analysis is a DETERMINISTIC CENTERED PAIRED
BOOTSTRAP TEST computed directly from the seed-level paired differences d (n = 30 seeds is
the unit of inference; windows are never treated as units):

    observed = mean(d);  d0 = d - mean(d)            # impose H0: mean zero
    resample d0 with replacement, B = 100,000
    p = (#{ |mean(d0*)| >= |observed| } + 1) / (B + 1)   # two-sided, Monte-Carlo corrected

The per-contrast RNG is derived from the contrast label (CRC32), so results are bit
reproducible and independent of computation order. This is a bootstrap approximation of the
null distribution of the mean -- it is never described as an exact test. Two pre-declared
sensitivities are reported alongside (never substituted for the primary): a one-sample
paired t-test on d and a Wilcoxon signed-rank test on d (NaN when d is identically zero).
A normal-approximation inversion of the published interval exists only as a labelled
fallback for partial checkouts; the shipped CSV must contain zero fallback rows.

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
N_BOOT = 100_000
BOOT_SEED = 20260721
PRIMARY = (f"deterministic centered paired bootstrap test ({N_BOOT} resamples, "
           f"Monte-Carlo corrected, per-contrast seed base {BOOT_SEED})")
APPROX = "normal-approximation inversion of the published interval (fallback; not used in the shipped artifact)"

FRONTIER_POLICIES = ("ebcsdef", "vbccoh", "vbcref")
FRONTIER_CAPS = (64, 128, 256, 512, 1024)


def boot_p_centered(d: np.ndarray, label: str) -> float:
    """Two-sided deterministic centered paired bootstrap p for H0: mean(d) = 0."""
    d = np.asarray(d, float)
    n = len(d)
    observed = abs(d.mean())
    d0 = d - d.mean()
    rng = np.random.default_rng(BOOT_SEED + zlib.crc32(label.encode()))
    b = np.abs(d0[rng.integers(0, n, (N_BOOT, n))].mean(1))
    extreme = int((b >= observed - 1e-15).sum())
    return (extreme + 1) / (N_BOOT + 1)


def p_ttest(d: np.ndarray) -> float:
    """Sensitivity: one-sample paired t-test on the seed-level differences."""
    from scipy.stats import ttest_1samp
    d = np.asarray(d, float)
    if np.allclose(d.std(ddof=1), 0.0):
        return 1.0 if np.allclose(d.mean(), 0.0) else 0.0
    return float(ttest_1samp(d, 0.0).pvalue)


def p_wilcoxon(d: np.ndarray) -> float:
    """Sensitivity: Wilcoxon signed-rank on the seed-level differences (NaN if all zero)."""
    from scipy.stats import wilcoxon
    d = np.asarray(d, float)
    if np.allclose(d, 0.0):
        return float("nan")
    try:
        return float(wilcoxon(d).pvalue)
    except ValueError:
        return float("nan")


def boot_p(diff: float, lo: float, hi: float) -> float:
    """Fallback only (labelled APPROX): normal inversion of a published interval."""
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


def _row(family, fam_size, method, test, effect, lo, hi, d, label, approx=None):
    if d is not None:
        p = boot_p_centered(d, label)
        return dict(family=family, family_size=fam_size, method=method, test=test,
                    effect=effect, ci_lo=lo, ci_hi=hi, p_raw=p, p_method=PRIMARY,
                    p_ttest_sensitivity=round(p_ttest(d), 6),
                    p_wilcoxon_sensitivity=round(p_wilcoxon(d), 6))
    return dict(family=family, family_size=fam_size, method=method, test=test,
                effect=effect, ci_lo=lo, ci_hi=hi, p_raw=approx, p_method=APPROX,
                p_ttest_sensitivity=float("nan"), p_wilcoxon_sensitivity=float("nan"))


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    rows = []

    # ---- F1: confirmatory core (6 contrasts), Holm ----
    ci = pd.read_csv(f"{T}/paper2_v2_replication_001/paired_ci.csv")
    core = ci[ci.contrast == "lp32_vs_naive"].copy()
    assert len(core) == 6, f"core family must have exactly 6 contrasts, found {len(core)}"
    f1 = []
    for r in core.itertuples():
        label = f"core/{r.detector}/{r.regime}/lp32_vs_naive"
        d = _core_diff_per_seed(r.detector, r.regime)
        f1.append(_row("confirmatory core (gate vs naive)", 6, "Holm",
                       f"{r.detector}/{r.regime} lp32 vs naive",
                       r.diff, r.ci_lo, r.ci_hi, d, label,
                       approx=boot_p(r.diff, r.ci_lo, r.ci_hi)))
    adj = holm([r["p_raw"] for r in f1])
    for r, a in zip(f1, adj):
        r["p_adj"] = a
    rows += f1

    # ---- F2: budget frontier (15 pre-declared cells, zero-commit cells INCLUDED), BH ----
    bf = f"{OUT}/budget_frontier.csv"
    B = pd.read_csv(bf)
    f2 = []
    for pol in FRONTIER_POLICIES:
        for cap in FRONTIER_CAPS:
            cell = B[(B.scenario == "ps_full") & (B.policy == pol)
                     & (B.cap == cap) & (B.schedule == "bonf")]
            tag = f"q1fc_ps_full_{pol}_c{cap}_bonf"
            d = _arm_gain_per_seed(tag)
            eff = float(cell.iloc[0].gain) if len(cell) else float("nan")
            lo = float(cell.iloc[0].lo) if len(cell) else float("nan")
            hi = float(cell.iloc[0].hi) if len(cell) else float("nan")
            f2.append(_row("registered follow-up: budget frontier (PortScan full, Bonferroni)",
                           15, "Benjamini-Hochberg",
                           f"{pol}/cap{cap} gain vs no-adaptation",
                           eff, lo, hi, d, f"frontier/ps_full/{pol}/c{cap}/bonf",
                           approx=boot_p(eff, lo, hi) if lo == lo else 1.0))
    assert len(f2) == 15, f"frontier family must have exactly 15 cells, found {len(f2)}"
    adj = bh([r["p_raw"] for r in f2])
    for r, a in zip(f2, adj):
        r["p_adj"] = a
    rows += f2

    # ---- F3: chronological matrix (7 strict replays), BH ----
    ch = f"{OUT}/chronological_replays.csv"
    C = pd.read_csv(ch)
    c = C[C.policy == "strict"].copy()
    assert len(c) == 7, f"chronological family must have exactly 7 replays, found {len(c)}"
    f3 = []
    for r in c.itertuples():
        d = _arm_gain_per_seed(f"q1fd_{r.stream}_strict")
        f3.append(_row("registered follow-up: chronological matrix (strict)", 7,
                       "Benjamini-Hochberg",
                       f"{r.stream} strict gain vs no-adaptation",
                       round(r.gain_ba * 100, 3), round(r.ba_lo * 100, 3),
                       round(r.ba_hi * 100, 3), d, f"chrono/{r.stream}/strict",
                       approx=boot_p(r.gain_ba * 100, r.ba_lo * 100, r.ba_hi * 100)))
    adj = bh([r["p_raw"] for r in f3])
    for r, a in zip(f3, adj):
        r["p_adj"] = a
    rows += f3

    for r in rows:
        r["p_raw"] = round(r["p_raw"], 6)
        r["p_adj"] = round(r["p_adj"], 6)
        r["significant_adj"] = bool(r["p_adj"] < 0.05)
    M = pd.DataFrame(rows)[["family", "family_size", "method", "test", "effect",
                            "ci_lo", "ci_hi", "p_raw", "p_adj", "p_method",
                            "p_ttest_sensitivity", "p_wilcoxon_sensitivity",
                            "significant_adj"]]
    assert len(M) == 28, f"expected 28 total contrasts, found {len(M)}"
    M.to_csv(f"{OUT}/multiplicity.csv", index=False)
    print(M.to_string(index=False))
    print("\n== survival under adjustment, per family ==")
    for fam, g in M.groupby("family"):
        n_raw = int((g.p_raw < 0.05).sum()); n_adj = int(g.significant_adj.sum())
        print(f"  {fam}: {n_adj}/{len(g)} survive ({n_raw} were nominally significant)")
    n_ap = int((M.p_method == APPROX).sum())
    print(f"\np-value provenance: {len(M) - n_ap}/{len(M)} centered paired bootstrap, "
          f"{n_ap} normal-approximation fallback")
    if n_ap:
        print("WARNING: fallback rows present -- the shipped artifact must have zero")


if __name__ == "__main__":
    main()
