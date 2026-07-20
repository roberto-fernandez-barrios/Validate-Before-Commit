"""final-q1 P0.3 / D2: TOST equivalence analysis for the symmetric A/B control.

Question: are the {independent, own_transformer} conditions' role-randomized gaps
PRACTICALLY EQUIVALENT to zero, at pre-registered margins -- not merely unresolved?

Registered design (notes/q1_max_protocol.md, D2):
  * PRIMARY analysis: confirmatory seeds 2001-2100 ONLY (the pilot 104-133 generated the
    hypothesis and is excluded from the confirmatory verdict).
  * SECONDARY analysis: pooled pilot+confirmatory (labeled as such, precision only).
  * Margins: primary +/-1.0 BA (the P1.7 materiality threshold); sensitivity +/-0.5, +/-2.0.
  * TOST via paired per-seed bootstrap: equivalence at margin m is declared iff the
    two one-sided bootstrap p-values (P[mean <= -m], P[mean >= +m]) are both < 0.05 --
    equivalently the bootstrap 90% CI of the mean lies inside (-m, +m).
  * MANDATORY fallback wording if equivalence is not established (protocol D2).

Input : results/tables/paper2_final_kbs/symmetric_ab_perseed*.csv
Output: results/tables/paper2_final_kbs/ab_equivalence.csv + console verdicts.
"""
from __future__ import annotations

import glob

import numpy as np
import pandas as pd

OUT = "results/tables/paper2_final_kbs"
MARGINS = (0.5, 1.0, 2.0)
PRIMARY_MARGIN = 1.0
PILOT = set(range(104, 134))
CONFIRMATORY = set(range(2001, 2101))
CONDITIONS = ("independent", "own_transformer", "inc_scaler_indep_pca", "indep_scaler_inc_pca")


def tost(gaps: np.ndarray, margin: float, n_boot: int = 20000, seed: int = 0):
    """Bootstrap TOST: equivalent iff the 90% bootstrap CI of the mean is inside (-m, m)."""
    rng = np.random.default_rng(seed)
    bs = rng.choice(gaps, size=(n_boot, len(gaps)), replace=True).mean(1)
    lo90, hi90 = float(np.percentile(bs, 5)), float(np.percentile(bs, 95))
    p_low = float(np.mean(bs <= -margin))    # one-sided: mean at or below -m
    p_high = float(np.mean(bs >= margin))    # one-sided: mean at or above +m
    return dict(ci90_lo=round(lo90, 3), ci90_hi=round(hi90, 3),
                equivalent=bool(-margin < lo90 and hi90 < margin),
                p_low=round(p_low, 5), p_high=round(p_high, 5))


def main() -> None:
    frames = [pd.read_csv(f) for f in glob.glob(f"{OUT}/symmetric_ab_perseed*.csv")]
    if not frames:
        raise SystemExit("no per-seed A/B output found; run paper2_symmetric_ab_final first")
    d = pd.concat(frames, ignore_index=True).drop_duplicates(
        subset=["dataset", "model", "condition", "seed"])
    rows = []
    for (ds, mt, cond), g in d.groupby(["dataset", "model", "condition"]):
        if cond not in CONDITIONS:
            continue
        for label, seeds in (("primary_confirmatory", CONFIRMATORY),
                             ("secondary_pilot_plus_confirmatory", PILOT | CONFIRMATORY)):
            gg = g[g.seed.isin(seeds)]
            if len(gg) < 20:
                continue
            gaps = gg.gap_rand.to_numpy(float)
            for m in MARGINS:
                r = tost(gaps, m, seed=hash((ds, mt, cond, label, m)) % (2**31))
                rows.append(dict(dataset=ds, model=mt, condition=cond, analysis=label,
                                 n_seeds=len(gg), margin=m, mean_gap=round(gaps.mean(), 3),
                                 **r, primary=(m == PRIMARY_MARGIN and
                                               label == "primary_confirmatory")))
    R = pd.DataFrame(rows)
    R.to_csv(f"{OUT}/ab_equivalence.csv", index=False)
    print(R.to_string(index=False))
    prim = R[R.primary]
    for _, r in prim.iterrows():
        verdict = ("EQUIVALENT within +/-1.0 BA" if r.equivalent else
                   "NOT established -> use protocol D2 fallback wording")
        print(f"[PRIMARY] {r.dataset}/{r.model}/{r.condition}: mean {r.mean_gap:+.2f} "
              f"CI90 [{r.ci90_lo}, {r.ci90_hi}] -> {verdict}")


if __name__ == "__main__":
    main()
