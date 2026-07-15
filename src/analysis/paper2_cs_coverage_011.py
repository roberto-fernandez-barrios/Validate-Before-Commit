"""Amendment 011: empirical coverage of the confidence-sequence commit gates.

Standalone Monte-Carlo (no pipeline). For a single proposal, the CS gates promise
    P(ever commit | E_probe[d] <= 0) <= alpha
on the PROBE distribution. We measure the empirical false-commit rate of the Robbins and the
empirical-Bernstein sequences under four regimes, at nominal alpha=0.10, b=64 (looks every 16):

  iid              : d_i i.i.d., mean 0                          -> should be <= alpha
  no_replacement   : d_i drawn WITHOUT replacement from a finite
                     population whose mean is exactly 0          -> should be <= alpha
  autocorrelated   : d_i block-correlated (AR-like), mean 0      -> may EXCEED alpha (iid broken)
  stale_mismatch   : probe mean +0.05 but the FUTURE mean is
                     -0.05 (a stale probe); we report the future
                     -harm commit rate                           -> not bounded by the probe guarantee

The point is to make the manuscript's scope caveat quantitative: the guarantee holds for iid /
exchangeable probe draws, and probe representativeness (not the CS) is what can fail.

Outputs results/tables/paper2_amendment_011/cs_coverage.csv
"""
import os
import numpy as np
import pandas as pd

from src.experiments.run_paper2_readaptation_v2 import cs_lower_bound, cs_lower_bound_eb

OUT = "results/tables/paper2_amendment_011"
ALPHA = 0.10
B = 64
BLOCK = 16
N_TRIAL = 20000
TIE = 0.7        # fraction of ties (d=0); the rest split between +1 and -1


def commit(d, method):
    n = 0
    while n < len(d):
        n = min(n + BLOCK, len(d))
        lcb = (cs_lower_bound_eb(d[:n], ALPHA) if method == "eb"
               else cs_lower_bound(d[:n], ALPHA, rho2=1.0 / B))
        if lcb > 0:
            return True
    return False


def draw_iid(rng, mean, n=B, tie=TIE):
    # P(+1)-P(-1) = mean; P(+1)+P(-1) = 1-tie
    nz = 1.0 - tie
    p_pos = (nz + mean) / 2.0
    p_neg = (nz - mean) / 2.0
    p_pos, p_neg = max(p_pos, 0), max(p_neg, 0)
    p_tie = max(1 - p_pos - p_neg, 0)
    return rng.choice([-1.0, 0.0, 1.0], size=n, p=np.array([p_neg, p_tie, p_pos]) /
                      (p_neg + p_tie + p_pos))


def draw_noreplace(rng, mean, n=B, pop=4000, tie=TIE):
    pool = draw_iid(rng, mean, n=pop, tie=tie)
    pool = pool - pool.mean() + mean          # force population mean exactly = mean
    pool = np.clip(np.round(pool), -1, 1)
    return rng.permutation(pool)[:n]


def draw_autocorr(rng, mean, n=B, tie=TIE, block=8):
    # correlated: draw one value per block of `block` flows (positive within-block correlation),
    # which inflates the effective variance the iid CS does not budget for.
    reps = int(np.ceil(n / block))
    base = draw_iid(rng, mean, n=reps, tie=tie)
    return np.repeat(base, block)[:n]


def rate(method, drawer, mean, seed=0):
    rng = np.random.default_rng(seed)
    c = sum(commit(drawer(rng, mean), method) for _ in range(N_TRIAL))
    return c / N_TRIAL


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for method in ("robbins", "eb"):
        rows.append(dict(method=method, regime="iid_mean0", target="false-commit",
                         rate=round(rate(method, draw_iid, 0.0, 1), 4), nominal=ALPHA))
        rows.append(dict(method=method, regime="noreplace_mean0", target="false-commit",
                         rate=round(rate(method, draw_noreplace, 0.0, 2), 4), nominal=ALPHA))
        rows.append(dict(method=method, regime="autocorr_mean0", target="false-commit",
                         rate=round(rate(method, draw_autocorr, 0.0, 3), 4), nominal=ALPHA))
        # stale/mismatch: probe looks slightly good (+0.05) but future is bad (-0.05); the commit
        # rate here is future-harm, which the probe-distribution guarantee does NOT bound.
        rows.append(dict(method=method, regime="stale_probe+0.05_future-0.05", target="future-harm",
                         rate=round(rate(method, draw_iid, 0.05, 4), 4), nominal=float("nan")))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/cs_coverage.csv", index=False)
    print("== CS coverage (empirical commit rate; nominal alpha =", ALPHA, ") ==")
    print(R.to_string(index=False))


if __name__ == "__main__":
    main()
