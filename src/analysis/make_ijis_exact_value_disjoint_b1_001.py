"""Frozen B1 analysis for the final IJIS exact-feature-disjoint sensitivity.

The sealed common-harness implementation regenerates all registered families and S1--S4.
This wrapper then applies the six robustness predicates in protocol section 7.1.  It is
committed before any 8001--8030 result is executed or inspected.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from src.analysis import make_post_kbs_common_harness_001 as base

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "results" / "raw" / "ijis_exact_value_disjoint_b1"
OUT = REPO / "results" / "tables" / "ijis_exact_value_disjoint_b1_001"
CONFIG = REPO / "configs" / "ijis_exact_value_disjoint_b1_v1.json"
PROTOCOL = REPO / "notes" / "ijis_exact_value_disjoint_sensitivity_protocol_001.md"
HISTORICAL = (REPO / "results" / "tables" / "post_kbs_common_harness_baselines_001"
              / "cell_classification.csv")
SEEDS = list(range(8001, 8031))
FULL = ("ps_full", "unsw_full", "ton_full")
ALL_SCENARIOS = ("ps_full", "unsw_full", "ton_full", "ps_zero", "unsw_zero", "ton_zero")
COMPARED = ("atc", "doc", "enscal", "replay", "ddm", "adwin")


def arm_tag(scenario: str, policy: str, size: str | None) -> str:
    if policy == "never":
        return f"xvd_b1_{scenario}_never"
    return f"xvd_b1_{scenario}_{policy}_{size}"


def _truth(value) -> bool:
    return value is True or str(value).strip().lower() == "true"


def main() -> None:
    assert CONFIG.exists() and PROTOCOL.exists() and HISTORICAL.exists()
    base.RAW = RAW
    base.OUT = OUT
    base.SEEDS = SEEDS
    base.arm_tag = arm_tag
    # The sealed base config supplies policy-origin/budget metadata to the reused code.
    base.main()

    cells = pd.read_csv(OUT / "cell_classification.csv")
    statements = pd.read_csv(OUT / "statements.csv", keep_default_na=False)
    historical = pd.read_csv(HISTORICAL)

    def cls(sc: str, pol: str, comparator: str = "naive") -> str:
        name = f"{sc}: {pol}-2000 vs {comparator}-2000"
        hit = cells[cells.contrast == name]
        assert len(hit) == 1, name
        return str(hit.classification.iloc[0])

    atc_full = [cls(sc, "atc") for sc in FULL]
    ensemble_full = [cls(sc, "enscal") for sc in FULL]
    atc_retention = (
        "MATERIAL COST" not in atc_full
        and sum(x in ("COMPATIBLE", "MATERIAL GAIN") for x in atc_full) >= 2
    )
    ensemble_retention = (
        "MATERIAL COST" not in ensemble_full
        and all(x in ("COMPATIBLE", "MATERIAL GAIN") for x in ensemble_full)
    )
    alternative_detail = {
        pol: [cls(sc, pol) for sc in FULL] for pol in ("doc", "replay", "ddm", "adwin")
    }
    cost_alternatives = all(
        "MATERIAL COST" in values for values in alternative_detail.values()
    )
    atc_point = [cls(sc, "atc", "point") for sc in ALL_SCENARIOS]
    atc_vs_point = (
        sum(x in ("COMPATIBLE", "MATERIAL GAIN") for x in atc_point) >= 5
        and "MATERIAL COST" not in atc_point
    )
    size_ordering = any(
        _truth(r.holds)
        for r in statements.itertuples()
        if r.statement == "S4 method ordering changes with candidate size"
        and r.policy in ("atc", "enscal")
    )
    dominance_detail = {
        pol: [cls(sc, pol) for sc in ALL_SCENARIOS] for pol in COMPARED
    }
    no_global_dominance = not any(
        all(x == "MATERIAL GAIN" for x in values) for values in dominance_detail.values()
    )

    primary_new = cells[cells.family.str.startswith(("PF1", "PF2"))].set_index("contrast")
    primary_old = historical[historical.family.str.startswith(("PF1", "PF2"))].set_index("contrast")
    common = sorted(set(primary_new.index) & set(primary_old.index))
    reversals = []
    for name in common:
        old_cls = str(primary_old.loc[name, "classification"])
        new_cls = str(primary_new.loc[name, "classification"])
        if {old_cls, new_cls} == {"MATERIAL GAIN", "MATERIAL COST"}:
            reversals.append(dict(contrast=name, historical=old_cls, value_disjoint=new_cls))

    predicates = {
        "ATC_RETENTION": bool(atc_retention),
        "ENSEMBLE_RETENTION": bool(ensemble_retention),
        "COST_ALTERNATIVES": bool(cost_alternatives),
        "ATC_VS_POINT": bool(atc_vs_point),
        "SIZE_DEPENDENT_ORDERING": bool(size_ordering),
        "NO_GLOBAL_DOMINANCE": bool(no_global_dominance),
    }
    n_holds = sum(predicates.values())
    if n_holds == 6 and not reversals:
        verdict = "POLICY CONCLUSIONS ROBUST"
    elif n_holds >= 4 and not reversals:
        verdict = "PARTIALLY ROBUST"
    else:
        verdict = "MATERIALLY CHANGED"

    detail = dict(
        atc_full_drift=atc_full,
        ensemble_full_drift=ensemble_full,
        cost_alternatives_full_drift=alternative_detail,
        atc_vs_point_all_scenarios=atc_point,
        dominance_scope=("policies with registered PF1/PF2 comparisons: "
                         + ", ".join(COMPARED)),
        dominance_cells=dominance_detail,
    )
    payload = dict(
        outcome=verdict,
        predicates=predicates,
        predicates_holding=n_holds,
        direct_primary_material_reversals=reversals,
        detail=detail,
        protocol_file=str(PROTOCOL.relative_to(REPO)).replace("\\", "/"),
        protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        config_file=str(CONFIG.relative_to(REPO)).replace("\\", "/"),
        config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        confirmatory_seeds="8001-8030",
        taxonomy="protocol section 7.1, applied mechanically",
        numeric_replication_required=False,
        follow_up_authorized=False,
    )
    (OUT / "ROBUSTNESS_INTERPRETATION.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    prior = json.loads((OUT / "CLAIM_INTERPRETATION.json").read_text(encoding="utf-8"))
    prior.update(
        exact_value_disjoint_robustness=verdict,
        robustness_file="ROBUSTNESS_INTERPRETATION.json",
        protocol_file=str(PROTOCOL.relative_to(REPO)).replace("\\", "/"),
        config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        confirmatory_seeds="8001-8030",
    )
    (OUT / "CLAIM_INTERPRETATION.json").write_text(
        json.dumps(prior, indent=2), encoding="utf-8"
    )
    print(f"REGISTERED B1 ROBUSTNESS VERDICT: {verdict} ({n_holds}/6 predicates)")
    for name, value in predicates.items():
        print(f"  {name}: {value}")
    print(f"  direct primary material reversals: {len(reversals)}")


if __name__ == "__main__":
    main()
