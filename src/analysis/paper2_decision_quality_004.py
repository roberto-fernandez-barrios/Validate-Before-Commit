"""Decision-quality metrics and hierarchical per-trigger model (amendment 004, E & F).

E. From the lp32 gate arms' per-trigger logs (seeds 104-133): ground truth per trigger is
   delta5 = cand_future5 - inc_future5 (logged lookahead, never a policy input).
   harmful-commit rate, beneficial-rejection rate, gate precision/recall, per-trigger regret,
   vs the always-commit baseline ON THE SAME TRIGGERS. Cluster (per-seed) bootstrap CIs.
F. MixedLM: delta5 ~ deg_pre5 + score + severity_t + window_idx, random intercept per seed;
   per regime and pooled (regime fixed effects); leave-one-regime-out predictive R^2 of the
   fixed part. Fit on the naive (ks_none) logs, the same table as the mechanism analysis.
Outputs results/tables/paper2_decision_quality_004/*.csv
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd

RAW = "results/raw"
OUT = "results/tables/paper2_decision_quality_004"
REGIMES = ["portscan", "unsw_recon", "ton_scanning"]
SEEDS = set(range(104, 134))
rng = np.random.default_rng(20260714)


def read_trig(reg: str, arm: str) -> pd.DataFrame:
    parts = []
    for d in [f"paper2_v2_{reg}_ks_{arm}", f"paper2_v2_{reg}_ks_{arm}_top"]:
        f = f"{RAW}/{d}/paper2_v2_trigger_log.csv"
        if os.path.exists(f):
            parts.append(pd.read_csv(f))
    d = pd.concat(parts)
    d = d[d.seed.isin(SEEDS)].dropna(subset=["delta_future5"])
    d["regime"] = reg
    return d


def cluster_boot(d: pd.DataFrame, fn, nb=2000):
    seeds = d.seed.unique()
    vals = []
    for _ in range(nb):
        pick = rng.choice(seeds, len(seeds), replace=True)
        db = pd.concat([d[d.seed == s] for s in pick])
        v = fn(db)
        if v is not None and np.isfinite(v):
            vals.append(v)
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def metrics(d: pd.DataFrame) -> dict:
    com, rej = d[d.committed], d[~d.committed]
    pos = d[d.delta_future5 > 0]
    def rate(num, den): return float(num) / den if den else np.nan
    regret_gate = float((d.delta_future5.clip(lower=0) * (~d.committed)
                         + (-d.delta_future5).clip(lower=0) * d.committed).mean())
    regret_always = float((-d.delta_future5).clip(lower=0).mean())
    return dict(
        n_triggers=len(d), n_commits=len(com), n_rejects=len(rej),
        harmful_commit_rate=rate((com.delta_future5 < 0).sum(), len(com)),
        beneficial_rejection_rate=rate((rej.delta_future5 > 0).sum(), len(rej)),
        gate_precision=rate((com.delta_future5 > 0).sum(), len(com)),
        gate_recall=rate((com.delta_future5 > 0).sum(), len(pos)),
        regret_gate=regret_gate, regret_always_commit=regret_always)


def main():
    os.makedirs(OUT, exist_ok=True)

    # E. decision-quality of the lp32 gate
    T = pd.concat([read_trig(r, "lp32") for r in REGIMES])
    rows = []
    for reg in REGIMES + ["POOLED"]:
        d = T if reg == "POOLED" else T[T.regime == reg]
        m = metrics(d)
        for k in ("harmful_commit_rate", "beneficial_rejection_rate", "gate_precision",
                  "gate_recall", "regret_gate", "regret_always_commit"):
            lo, hi = cluster_boot(d, lambda db, kk=k: metrics(db)[kk])
            m[f"{k}_lo"], m[f"{k}_hi"] = round(lo, 4), round(hi, 4)
            m[k] = round(m[k], 4) if np.isfinite(m[k]) else m[k]
        rows.append(dict(regime=reg, **m))
    D = pd.DataFrame(rows)
    D.to_csv(f"{OUT}/decision_metrics.csv", index=False)
    print("== decision_metrics (lp32) =="); print(D.to_string(index=False)); print()

    # F. hierarchical model on the naive logs (same table as the mechanism analysis)
    import statsmodels.formula.api as smf
    N = pd.concat([read_trig(r, "none") for r in REGIMES]).dropna(
        subset=["deg_pre5", "score"]).reset_index(drop=True)
    hrows = []
    for reg in REGIMES + ["POOLED"]:
        d = N if reg == "POOLED" else N[N.regime == reg]
        formula = "delta_future5 ~ deg_pre5 + score + severity_t + window_idx"
        if reg == "POOLED":
            formula += " + C(regime)"
        try:
            fit = smf.mixedlm(formula, d, groups=d["seed"]).fit(reml=False)
            for term in fit.fe_params.index:
                if term == "Intercept" or term.startswith("C(regime)"):
                    continue
                ci = fit.conf_int().loc[term]
                lo, hi, src = float(ci[0]), float(ci[1]), "mixedlm"
                if not (np.isfinite(lo) and np.isfinite(hi)):
                    # boundary MLE (singular random-effect variance): fall back to a
                    # per-seed cluster bootstrap of the OLS coefficient
                    import statsmodels.formula.api as smf2
                    seeds_r = d.seed.unique(); betas = []
                    for _ in range(2000):
                        pick = rng.choice(seeds_r, len(seeds_r), replace=True)
                        db = pd.concat([d[d.seed == s] for s in pick])
                        try:
                            betas.append(float(smf2.ols(formula, db).fit().params[term]))
                        except Exception:
                            pass
                    lo, hi, src = float(np.percentile(betas, 2.5)), float(np.percentile(betas, 97.5)), "cluster_boot_ols"
                hrows.append(dict(regime=reg, term=term, beta=round(float(fit.fe_params[term]), 4),
                                  ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                                  n=len(d), converged=bool(fit.converged), ci_source=src))
        except Exception as e:
            hrows.append(dict(regime=reg, term="FIT_FAILED", beta=np.nan, ci_lo=np.nan,
                              ci_hi=np.nan, n=len(d), converged=str(e)[:80], ci_source="none"))
    H = pd.DataFrame(hrows)
    H.to_csv(f"{OUT}/hierarchical_model.csv", index=False)
    print("== hierarchical_model =="); print(H.to_string(index=False)); print()

    # LORO predictive R^2 of the fixed part (OLS fit on 2 regimes, predict the third)
    import statsmodels.api as sm
    lrows = []
    feats = ["deg_pre5", "score", "severity_t", "window_idx"]
    for reg in REGIMES:
        tr, te = N[N.regime != reg], N[N.regime == reg]
        ols = sm.OLS(tr["delta_future5"], sm.add_constant(tr[feats])).fit()
        pred = ols.predict(sm.add_constant(te[feats]))
        ss_res = float(((te["delta_future5"] - pred) ** 2).sum())
        ss_tot = float(((te["delta_future5"] - te["delta_future5"].mean()) ** 2).sum())
        lrows.append(dict(held_out=reg, n_test=len(te), r2=round(1 - ss_res / ss_tot, 3)))
        # ablation: same model without deg_pre5 (is degradation the load-bearing predictor?)
        f2 = [f for f in feats if f != "deg_pre5"]
        ols2 = sm.OLS(tr["delta_future5"], sm.add_constant(tr[f2])).fit()
        pred2 = ols2.predict(sm.add_constant(te[f2]))
        lrows[-1]["r2_without_deg"] = round(1 - float(((te["delta_future5"] - pred2) ** 2).sum()) / ss_tot, 3)
    L = pd.DataFrame(lrows)
    L.to_csv(f"{OUT}/loro_r2.csv", index=False)
    print("== LORO predictive R^2 =="); print(L.to_string(index=False))


if __name__ == "__main__":
    main()
