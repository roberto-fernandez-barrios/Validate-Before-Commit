"""Decision-quality and mechanism analyses, amendment-005 specification (supersedes 004 where noted).

Upgrades locked in notes/paper2_harness_v2_amendment_005.md (F):
- pooled MixedLM clusters = regime x seed (a seed is not one experimental unit across regimes);
- VIFs for deg_pre5 / score / severity_t / window_idx;
- random slope on deg_pre5 attempted (reported if it converges);
- the per-trigger mechanism + MixedLM repeated on the QK-ZZ trigger logs;
- local per-decision regret at horizons {1,3,5,10} from the `_hz` logging reruns
  (terminology: "local per-decision regret on the gate policy's trigger states").
Outputs results/tables/paper2_decision_quality_005/*.csv
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

RAW = "results/raw"
OUT = "results/tables/paper2_decision_quality_005"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
SEEDS = set(range(104, 134))
HORIZONS = (1, 3, 5, 10)
rng = np.random.default_rng(20260714)


def read_trig(reg: str, det: str, arm: str, hz: bool = False) -> pd.DataFrame:
    base = f"paper2_v7_{reg}_{det}_{arm}_hz" if hz else f"paper2_v2_{reg}_{det}_{arm}"
    dirs = [base] if hz else [base, base + "_top"]
    parts = []
    for d in dirs:
        f = f"{RAW}/{d}/paper2_v2_trigger_log.csv"
        if os.path.exists(f):
            parts.append(pd.read_csv(f))
    if not parts:
        return pd.DataFrame()
    d = pd.concat(parts)
    d = d[d.seed.isin(SEEDS)].dropna(subset=["delta_future5"])
    d["regime"] = reg
    d["cluster"] = reg + "_" + d.seed.astype(str)
    return d


def cluster_boot(d: pd.DataFrame, fn, key: str = "cluster", nb: int = 2000):
    units = d[key].unique()
    vals = []
    for _ in range(nb):
        pick = rng.choice(units, len(units), replace=True)
        db = pd.concat([d[d[key] == u] for u in pick])
        v = fn(db)
        if v is not None and np.isfinite(v):
            vals.append(v)
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def fit_block(N: pd.DataFrame, tag: str) -> list[dict]:
    rows = []
    feats = ["deg_pre5", "score", "severity_t", "window_idx"]
    for reg in REGIMES + ["POOLED"]:
        d = N if reg == "POOLED" else N[N.regime == reg]
        if not len(d):
            continue
        groups = d["cluster"] if reg == "POOLED" else d["seed"]
        formula = "delta_future5 ~ deg_pre5 + score + severity_t + window_idx"
        if reg == "POOLED":
            formula += " + C(regime)"
        try:
            fit = smf.mixedlm(formula, d, groups=groups).fit(reml=False)
            for term in fit.fe_params.index:
                if term == "Intercept" or term.startswith("C(regime)"):
                    continue
                ci = fit.conf_int().loc[term]
                lo, hi, src = float(ci[0]), float(ci[1]), "mixedlm"
                if not (np.isfinite(lo) and np.isfinite(hi)):
                    key = "cluster" if reg == "POOLED" else "seed"
                    blo, bhi = cluster_boot(d, lambda db, t=term, f=formula: float(
                        smf.ols(f, db).fit().params.get(t, np.nan)), key=key)
                    lo, hi, src = blo, bhi, "cluster_boot_ols"
                rows.append(dict(detector=tag, regime=reg, term=term,
                                 beta=round(float(fit.fe_params[term]), 4),
                                 ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                                 n=len(d), ci_source=src))
        except Exception as e:
            rows.append(dict(detector=tag, regime=reg, term="FIT_FAILED", beta=np.nan,
                             ci_lo=np.nan, ci_hi=np.nan, n=len(d), ci_source=str(e)[:60]))
        # VIFs (pooled and per regime)
        Xv = sm.add_constant(d[feats].dropna())
        for j, f in enumerate(feats):
            rows.append(dict(detector=tag, regime=reg, term=f"VIF_{f}",
                             beta=round(float(variance_inflation_factor(Xv.values, j + 1)), 2),
                             ci_lo=np.nan, ci_hi=np.nan, n=len(Xv), ci_source="vif"))
    # random slope attempt (pooled)
    try:
        fit = smf.mixedlm("delta_future5 ~ deg_pre5 + score + severity_t + window_idx + C(regime)",
                          N, groups=N["cluster"], re_formula="~deg_pre5").fit(reml=False)
        ci = fit.conf_int().loc["deg_pre5"]
        rows.append(dict(detector=tag, regime="POOLED", term="deg_pre5_randslope",
                         beta=round(float(fit.fe_params["deg_pre5"]), 4),
                         ci_lo=round(float(ci[0]), 4), ci_hi=round(float(ci[1]), 4),
                         n=len(N), ci_source="mixedlm_randslope" + ("" if fit.converged else "_NOCONV")))
    except Exception as e:
        rows.append(dict(detector=tag, regime="POOLED", term="deg_pre5_randslope", beta=np.nan,
                         ci_lo=np.nan, ci_hi=np.nan, n=len(N), ci_source=str(e)[:60]))
    return rows


def mech_corr(N: pd.DataFrame, tag: str) -> list[dict]:
    def pear(d, x):
        return float(np.corrcoef(d[x], d["delta_future5"])[0, 1])
    rows = []
    for reg in REGIMES + ["POOLED"]:
        d = N if reg == "POOLED" else N[N.regime == reg]
        if len(d) < 10:
            continue
        key = "cluster" if reg == "POOLED" else "seed"
        dlo, dhi = cluster_boot(d, lambda db: pear(db, "deg_pre5"), key=key)
        slo, shi = cluster_boot(d, lambda db: pear(db, "score"), key=key)
        rows.append(dict(detector=tag, regime=reg, n_triggers=len(d),
                         r_deg=round(pear(d, "deg_pre5"), 3), r_deg_lo=round(dlo, 3), r_deg_hi=round(dhi, 3),
                         r_score=round(pear(d, "score"), 3), r_score_lo=round(slo, 3), r_score_hi=round(shi, 3)))
    return rows


def regret(d: pd.DataFrame, h: int) -> dict:
    col = f"delta_future{h}"
    dd = d.dropna(subset=[col])
    gate = float((dd[col].clip(lower=0) * (~dd.committed)
                  + (-dd[col]).clip(lower=0) * dd.committed).mean())
    always = float((-dd[col]).clip(lower=0).mean())
    return dict(horizon=h, n=len(dd), regret_gate=round(gate, 4),
                regret_always_commit=round(always, 4),
                ratio=round(always / gate, 1) if gate > 0 else np.inf)


def main():
    os.makedirs(OUT, exist_ok=True)

    # mechanism + hierarchical model, KS and QK (naive logs, same convention as 004)
    all_h, all_m = [], []
    for det in ("ks", "qk"):
        N = pd.concat([read_trig(r, det, "none") for r in REGIMES]).dropna(
            subset=["deg_pre5", "score"]).reset_index(drop=True)
        all_m += mech_corr(N, det)
        all_h += fit_block(N, det)
    pd.DataFrame(all_m).to_csv(f"{OUT}/mechanism_by_detector.csv", index=False)
    pd.DataFrame(all_h).to_csv(f"{OUT}/hierarchical_model.csv", index=False)
    print("== mechanism_by_detector =="); print(pd.DataFrame(all_m).to_string(index=False)); print()
    print("== hierarchical_model (incl. VIF/randslope) ==")
    print(pd.DataFrame(all_h).to_string(index=False)); print()

    # horizon-wise LOCAL regret on the gate policy's trigger states (from _hz reruns)
    rrows = []
    T = pd.concat([read_trig(r, "ks", "lp32", hz=True) for r in REGIMES])
    if len(T):
        for reg in REGIMES + ["POOLED"]:
            d = T if reg == "POOLED" else T[T.regime == reg]
            for h in HORIZONS:
                if f"delta_future{h}" in d.columns:
                    rrows.append(dict(regime=reg, **regret(d, h)))
        R = pd.DataFrame(rrows)
        R.to_csv(f"{OUT}/regret_by_horizon.csv", index=False)
        print("== local per-decision regret by horizon =="); print(R.to_string(index=False))
    else:
        print("[hz logs not present yet - horizon regret skipped]")


if __name__ == "__main__":
    main()
