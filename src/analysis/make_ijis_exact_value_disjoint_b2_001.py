"""Frozen B2 analysis for the final IJIS exact-feature-disjoint sensitivity.

This wrapper reuses the sealed B2 inferential implementation, changing only the raw/output
locations, arm prefix and virgin seed block.  It then applies protocol sections 6.1--6.2,
including the independent-block G5 comparison with historical B2.  This file is committed
before any 7001--7030 result is executed or inspected.
"""
from __future__ import annotations

import hashlib
import json
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis import make_post_kbs_size_matched_drift_001 as base
from src.analysis.make_paper2_q1_multiplicity import BOOT_SEED, N_BOOT, holm

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "results" / "raw" / "ijis_exact_value_disjoint_b2"
OUT = REPO / "results" / "tables" / "ijis_exact_value_disjoint_b2_001"
CONFIG = REPO / "configs" / "ijis_exact_value_disjoint_b2_v1.json"
PROTOCOL = REPO / "notes" / "ijis_exact_value_disjoint_sensitivity_protocol_001.md"
HISTORICAL = REPO / "results" / "tables" / "post_kbs_size_matched_drift_001" / "by_seed.csv"
SCENARIOS = ("ps_full", "unsw_full", "ton_full")
SEEDS = list(range(7001, 7031))
MARGIN = 0.5


def arm_tag(scenario: str, policy: str, size: str | None) -> str:
    if policy == "never":
        return f"xvd_b2_{scenario}_never"
    return f"xvd_b2_{scenario}_{policy}_{size}"


def _size_diff(df: pd.DataFrame, scenario: str) -> np.ndarray:
    size = df["candidate_size"].astype(str)
    a = df[(df.scenario == scenario) & (df.policy == "naive") & (size == "2000")]
    b = df[(df.scenario == scenario) & (df.policy == "naive") & (size == "512")]
    a = a.set_index("seed").sort_index().ba
    b = b.set_index("seed").sort_index().ba
    assert len(a) == len(b) == 30 and list(a.index) == list(b.index)
    return (a.to_numpy() - b.to_numpy()) * 100.0


def _independent_bootstrap(a: np.ndarray, b: np.ndarray, label: str) -> dict:
    """Difference mean(a)-mean(b), with independent resampling of the two seed blocks."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    seed = BOOT_SEED + zlib.crc32(label.encode())
    rng = np.random.default_rng(seed)
    ia = rng.integers(0, len(a), (N_BOOT, len(a)))
    ib = rng.integers(0, len(b), (N_BOOT, len(b)))
    boot = a[ia].mean(axis=1) - b[ib].mean(axis=1)
    effect = float(a.mean() - b.mean())
    ci95 = tuple(float(x) for x in np.quantile(boot, (0.025, 0.975)))
    ci90 = tuple(float(x) for x in np.quantile(boot, (0.05, 0.95)))

    # Two-sample centered null: retain each block's distribution while imposing equal means.
    a0, b0 = a - a.mean(), b - b.mean()
    null = np.abs(a0[ia].mean(axis=1) - b0[ib].mean(axis=1))
    extreme = int((null >= abs(effect) - 1e-15).sum())
    p_raw = (extreme + 1) / (N_BOOT + 1)
    return dict(effect_pp=effect, ci95=ci95, ci90=ci90, p_raw=p_raw)


def _program_label(classes: list[str]) -> str:
    n_benefit = classes.count("SIZE BENEFIT")
    n_cost = classes.count("SIZE COST")
    if n_benefit == 3:
        return "ROBUST HOMOGENEOUS SIZE BENEFIT"
    if n_benefit >= 2 and n_cost == 0:
        return "PARTIAL ROBUSTNESS"
    if classes.count("NO MATERIAL SIZE EFFECT") == 3:
        return "NO MATERIAL SIZE EFFECT"
    if n_cost >= 2 and n_benefit == 0:
        return "SIZE COST"
    return "HETEROGENEOUS"


def _g5_class(effect: float, ci90: tuple[float, float], p_holm: float) -> str:
    if p_holm < 0.05 and effect <= -MARGIN:
        return "MATERIAL ATTENUATION"
    if p_holm < 0.05 and effect >= MARGIN:
        return "MATERIAL AMPLIFICATION"
    if -MARGIN < ci90[0] and ci90[1] < MARGIN:
        return "COMPATIBLE"
    return "UNRESOLVED"


def main() -> None:
    assert CONFIG.exists() and PROTOCOL.exists() and HISTORICAL.exists()
    # Reuse the sealed B2 code path. CONFIG remains the sealed base config while that code
    # reads budget metadata; this wrapper records the actual sensitivity config below.
    base.RAW = RAW
    base.OUT = OUT
    base.SEEDS = SEEDS
    base.arm_tag = arm_tag
    base.main()

    new = pd.read_csv(OUT / "by_seed.csv", dtype={"candidate_size": str}, keep_default_na=False)
    old = pd.read_csv(HISTORICAL, dtype={"candidate_size": str}, keep_default_na=False)
    outcome = pd.read_csv(OUT / "size_effect_outcome.csv")
    classes = outcome.set_index("scenario").classification.to_dict()
    program = _program_label([classes[sc] for sc in SCENARIOS])

    g5_rows = []
    for sc in SCENARIOS:
        stats = _independent_bootstrap(
            _size_diff(new, sc), _size_diff(old, sc), f"ijis-xvd-b2-g5|{sc}"
        )
        g5_rows.append(dict(
            scenario=sc,
            contrast="value-disjoint G2 minus historical G2",
            historical_effect_pp=round(float(_size_diff(old, sc).mean()), 4),
            value_disjoint_effect_pp=round(float(_size_diff(new, sc).mean()), 4),
            effect_pp=round(stats["effect_pp"], 4),
            ci95_lo=round(stats["ci95"][0], 4), ci95_hi=round(stats["ci95"][1], 4),
            ci90_lo=round(stats["ci90"][0], 4), ci90_hi=round(stats["ci90"][1], 4),
            p_raw=stats["p_raw"],
        ))
    g5 = pd.DataFrame(g5_rows)
    g5["p_holm"] = holm(g5.p_raw.tolist())
    g5["classification"] = [
        _g5_class(float(r.effect_pp), (float(r.ci90_lo), float(r.ci90_hi)), float(r.p_holm))
        for r in g5.itertuples()
    ]
    g5["n_value_disjoint_seeds"] = 30
    g5["n_historical_seeds"] = 30
    g5["correction"] = "Holm FWER, family size 3"
    g5["p_method"] = (
        f"deterministic centered independent-block bootstrap ({N_BOOT} resamples)"
    )
    g5.to_csv(OUT / "robustness_vs_historical.csv", index=False)

    original_materially_inflated = bool(
        (g5.classification == "MATERIAL ATTENUATION").sum() >= 2
        and not (g5.classification == "MATERIAL AMPLIFICATION").any()
    )
    prior = json.loads((OUT / "CLAIM_INTERPRETATION.json").read_text(encoding="utf-8"))
    payload = dict(
        outcome=program,
        per_scenario=prior["per_scenario"],
        historical_comparison=g5.to_dict(orient="records"),
        original_b2_materially_inflated=original_materially_inflated,
        protocol_file=str(PROTOCOL.relative_to(REPO)).replace("\\", "/"),
        protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        config_file=str(CONFIG.relative_to(REPO)).replace("\\", "/"),
        config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        confirmatory_seeds="7001-7030",
        taxonomy="protocol sections 6.1-6.2, applied mechanically",
        nesting_pairs_verified=prior["nesting_pairs_verified"],
        caveat=("G5 is an independent-block role-design contrast and is not a causal "
                "estimate of exact-duplicate leakage alone."),
        follow_up_authorized=False,
    )
    (OUT / "CLAIM_INTERPRETATION.json").write_text(
        json.dumps(payload, indent=2, default=float), encoding="utf-8"
    )
    print(f"REGISTERED B2 ROBUSTNESS VERDICT: {program}")
    print(g5[["scenario", "effect_pp", "ci95_lo", "ci95_hi", "p_holm",
              "classification"]].to_string(index=False))


if __name__ == "__main__":
    main()
