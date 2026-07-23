"""Equivalence margin sensitivity for the size-matched own-transformer control (v1.22.1).

Editorial derived table only (protocol: notes/v1_22_1_editorial_scope_protocol.md).
Reads exclusively the sealed v1.22.0 outputs of the size-matched control --
by_seed.csv, paired_contrasts.csv and equivalence.csv -- and pivots the already
registered CI90 verdicts at the preregistered margins (+-0.2 / +-0.5 / +-1.0 pp)
into one row per contrast. No new margins, no new resamples, no new inference:
every verdict is re-derived from the recorded CI90 and asserted identical to the
sealed `equivalent` flag. The inferential unit remains the seed.

Output: results/tables/v1_22_1_editorial/equivalence_margin_sensitivity.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "results" / "tables" / "size_matched_own_transformer_001"
OUT = REPO / "results" / "tables" / "v1_22_1_editorial"

MARGINS = (0.2, 0.5, 1.0)
PRIMARY_MARGIN = 0.5

DATASET = {"ps_zero": "CICIDS2017-PortScan", "unsw_zero": "UNSW-NB15",
           "ton_zero": "ToN-IoT"}


def interpret(v: dict[float, bool]) -> str:
    if all(v.values()):
        return "equivalent at every preregistered margin (+-0.2, +-0.5, +-1.0 pp)"
    if v[0.5] and v[1.0] and not v[0.2]:
        return ("equivalent at the preregistered primary +-0.5 pp margin and at "
                "+-1.0 pp; not at the stricter +-0.2 pp sensitivity -- margin-sensitive")
    if v[1.0] and not v[0.5]:
        return "not equivalent at the primary +-0.5 pp margin; equivalent only at +-1.0 pp"
    if not any(v.values()):
        return "not equivalent at any preregistered margin"
    return ("mixed verdicts: " +
            ", ".join(f"+-{m} pp: {'yes' if v[m] else 'no'}" for m in MARGINS))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    by_seed = pd.read_csv(SRC / "by_seed.csv")
    assert by_seed.seed.nunique() == 30, "sealed by_seed.csv must carry 30 seeds"
    con = pd.read_csv(SRC / "paired_contrasts.csv").set_index("contrast")
    eq = pd.read_csv(SRC / "equivalence.csv")

    rows = []
    for contrast, g in eq.groupby("contrast", sort=False):
        assert sorted(g.margin_pp) == sorted(MARGINS), f"unexpected margins for {contrast}"
        lo = float(g.ci90_lo.iloc[0])
        hi = float(g.ci90_hi.iloc[0])
        assert (g.ci90_lo == g.ci90_lo.iloc[0]).all() and (g.ci90_hi == g.ci90_hi.iloc[0]).all()
        verdicts = {}
        for _, r in g.iterrows():
            derived = (-r.margin_pp <= lo) and (hi <= r.margin_pp)
            assert derived == bool(r.equivalent), (
                f"sealed verdict mismatch for {contrast} at +-{r.margin_pp}")
            verdicts[float(r.margin_pp)] = bool(r.equivalent)
        primary_kind = g[g.margin_pp == PRIMARY_MARGIN].margin_kind.iloc[0]
        assert primary_kind == "primary", "the +-0.5 pp margin must be the registered primary"
        c = con.loc[contrast]
        assert round(float(c.ci90_lo), 4) == round(lo, 4)
        assert round(float(c.ci90_hi), 4) == round(hi, 4)
        scenario = contrast.split(":")[0]
        rows.append(dict(
            dataset=DATASET[scenario],
            contrast=contrast,
            effect_pp=float(c.effect_pp),
            ci90_lo=lo, ci90_hi=hi,
            equivalent_pm0p2=verdicts[0.2],
            equivalent_pm0p5=verdicts[0.5],
            equivalent_pm1p0=verdicts[1.0],
            registered_primary_margin=PRIMARY_MARGIN,
            interpretation=interpret(verdicts)))

    out = pd.DataFrame(rows)
    out.to_csv(OUT / "equivalence_margin_sensitivity.csv", index=False)
    dmg = out[out.contrast.str.contains("naive-2000 vs never")]
    print(f"equivalence_margin_sensitivity: {len(out)} contrasts "
          f"({len(dmg)} F1 damage rows); primary margin +-{PRIMARY_MARGIN} pp")
    for _, r in dmg.iterrows():
        print(f"  {r.dataset}: effect {r.effect_pp:+.2f} pp, CI90 [{r.ci90_lo:.4f}, "
              f"{r.ci90_hi:.4f}] -> +-0.2: {r.equivalent_pm0p2}, "
              f"+-0.5: {r.equivalent_pm0p5}, +-1.0: {r.equivalent_pm1p0}")


if __name__ == "__main__":
    main()
