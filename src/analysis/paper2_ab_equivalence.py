"""final-q1 P0.3 / D2: bootstrap CI-based equivalence assessment for the symmetric A/B control.

Question: are the {independent, own_transformer} conditions' role-randomized gaps
PRACTICALLY EQUIVALENT to zero, at pre-registered margins -- not merely unresolved?

Registered design (notes/q1_max_protocol.md, D2):
  * PRIMARY analysis: confirmatory seeds 2001-2100 ONLY (the pilot 104-133 generated the
    hypothesis and is excluded from the confirmatory verdict).
  * SECONDARY analysis: pooled pilot+confirmatory (labeled as such, precision only).
  * Margins: primary +/-1.0 BA (the P1.7 materiality threshold); sensitivity +/-0.5, +/-2.0.
  * Decision rule (q1-final-patch, Block E -- named for exactly what it is): a BOOTSTRAP
    CI-BASED EQUIVALENCE ASSESSMENT using the pre-registered margin. Equivalence at margin m
    is declared iff the 90% seed-level bootstrap CI of the mean gap lies inside (-m, +m) --
    the interval-inclusion form of TOST. The `boot_frac_*` columns report the fraction of
    bootstrap resamples whose mean falls at or beyond each margin; they are DESCRIPTIVE
    diagnostics of the bootstrap distribution, not p-values of boundary-null hypothesis
    tests, and are not presented as such anywhere. (Earlier output named them p_low/p_high;
    that naming overstated them and is retired.)
  * MANDATORY fallback wording if equivalence is not established (protocol D2).

Input : results/tables/paper2_final_kbs/symmetric_ab_perseed*.csv
Output: results/tables/paper2_final_kbs/ab_equivalence.csv + console verdicts.
"""
from __future__ import annotations

import glob
import hashlib

import numpy as np
import pandas as pd


def stable_seed(*parts) -> int:
    """Deterministic seed from a key, reproducible ACROSS PROCESSES.

    Python's built-in hash() is salted per interpreter run (PYTHONHASHSEED), so seeding a
    bootstrap with hash(...) makes the output non-reproducible -- the defect this replaces.
    SHA-256 of the joined key is stable everywhere.
    """
    key = "|".join(str(p) for p in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big") % (2 ** 32)

OUT = "results/tables/paper2_final_kbs"
MARGINS = (0.5, 1.0, 2.0)
PRIMARY_MARGIN = 1.0
PILOT = set(range(104, 134))
CONFIRMATORY = set(range(2001, 2101))
CONDITIONS = ("independent", "own_transformer", "inc_scaler_indep_pca", "indep_scaler_inc_pca")


def equivalence_ci(gaps: np.ndarray, margin: float, n_boot: int = 20000, seed: int = 0):
    """Bootstrap CI-based equivalence assessment: equivalent iff the 90% bootstrap CI of the
    mean lies inside (-m, m) (interval-inclusion form of TOST). The boot_frac_* outputs are
    descriptive bootstrap-distribution tail fractions, not boundary-null p-values."""
    rng = np.random.default_rng(seed)
    bs = rng.choice(gaps, size=(n_boot, len(gaps)), replace=True).mean(1)
    lo90, hi90 = float(np.percentile(bs, 5)), float(np.percentile(bs, 95))
    frac_low = float(np.mean(bs <= -margin))    # descriptive: resample means at/below -m
    frac_high = float(np.mean(bs >= margin))    # descriptive: resample means at/above +m
    return dict(ci90_lo=round(lo90, 3), ci90_hi=round(hi90, 3),
                equivalent=bool(-margin < lo90 and hi90 < margin),
                boot_frac_below_neg_margin=round(frac_low, 5),
                boot_frac_above_pos_margin=round(frac_high, 5))


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
                sd = stable_seed(ds, mt, cond, label, m)
                r = equivalence_ci(gaps, m, seed=sd)
                rows.append(dict(dataset=ds, model=mt, condition=cond, analysis=label,
                                 n_seeds=len(gg), margin=m, mean_gap=round(gaps.mean(), 3),
                                 **r, bootstrap_seed=sd,
                                 primary=(m == PRIMARY_MARGIN and
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
