"""Regression guards for the Scenario-A symmetric-pipeline rewrite.

Frozen source: notes/symmetric_pipeline_scenario_a_rewrite_protocol.md (forbidden claims)
and results/tables/symmetric_pipeline_dynamic_001/CLAIM_INTERPRETATION.json (the machine
verdict). These tests keep the manuscript permanently consistent with the frozen analysis:
no drift of headline numbers, no re-emergence of forbidden claims, no silent
reinterpretation of the scenario.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
SP = REPO / "results" / "tables" / "symmetric_pipeline_dynamic_001"

CLAIM_FILES = [
    "manuscript/main.tex", "manuscript/main_ieee.tex", "manuscript/supplement.tex",
    "README.md", "REPRODUCE.md", "manuscript/highlights.md",
]


def _texts():
    out = {}
    for p in CLAIM_FILES:
        f = REPO / p
        if f.exists():
            out[p] = re.sub(r"\s+", " ", f.read_text(encoding="utf-8").lower())
    for f in sorted((REPO / "manuscript" / "tables").glob("*.tex")):
        out[str(f)] = re.sub(r"\s+", " ", f.read_text(encoding="utf-8").lower())
    return out


def test_scenario_is_A_per_frozen_rules():
    ci = json.loads((SP / "CLAIM_INTERPRETATION.json").read_text(encoding="utf-8"))
    assert ci["scenario"] == "A"
    assert ci["rules_version"] == "protocol Appendix A"
    r = ci["rules_passed"]
    assert r["A1_material_harm_in_critical_cell"] is True
    assert r["A2_gate_win_ge_0p5_holm"] is True
    assert r["A3_guardrails_not_contradicted"] is True


def test_no_positive_security_improvement_language():
    for name, t in _texts().items():
        for m in re.finditer(r"security improvement", t):
            ctx = t[max(0, m.start() - 30): m.start()]
            assert ctx.endswith(("not a ", "d as a ")), (
                f"{name}: positive 'security improvement' language is forbidden "
                f"(unsw_zero strict fails recall NI); context: ...{ctx!r}")


def test_no_elimination_of_promotion_risk_claim():
    pat = re.compile(r"(?<!not )eliminat\w+ (?:all )?(?:the )?(?:harmful|promotion risk)")
    for name, t in _texts().items():
        assert not pat.search(t), f"{name}: claims elimination of harmful/promotion risk"


def test_fulldrift_nonpersistence_and_zero_drift_residual_stated():
    t = _texts()
    for doc in ("manuscript/main.tex", "manuscript/main_ieee.tex"):
        assert "full-drift harm does not persist" in t[doc], doc
        assert ("remains materially harmful" in t[doc]
                or "zero-drift promotion harm persists" in t[doc]), doc
        assert "under the historical frozen" in t[doc], (
            f"{doc}: QK/VBC-SG frozen-policy scope sentence missing")


def test_harmful_commits_marked_clustered():
    t = _texts()
    for doc in ("manuscript/main.tex", "manuscript/main_ieee.tex",
                "manuscript/supplement.tex"):
        assert ("not independent trials" in t[doc]
                or "no independence is assumed" in t[doc]), doc


def test_headline_numbers_match_frozen_csv():
    con = pd.read_csv(SP / "paired_contrasts.csv")

    def eff(name):
        return float(con[con.contrast == name].effect_pp.iloc[0])

    assert f"{eff('ps_full: own-naive vs never'):+.2f}" == "+7.21"
    assert f"{eff('unsw_full: own-naive vs never'):+.2f}" == "+2.55"
    assert f"{eff('ton_full: own-naive vs never'):+.2f}" == "+1.03"
    assert f"{eff('ton_full: own-naive vs frozen-naive'):+.2f}" == "+5.98"
    assert f"{eff('ps_zero: own-naive vs never'):+.2f}" == "-1.74"
    assert f"{eff('unsw_zero: own-naive vs never'):+.2f}" == "-0.65"
    main = (REPO / "manuscript" / "main.tex").read_text(encoding="utf-8")
    for s in ("+7.21", "+2.55", "+1.03", "+5.98", "-1.74", "-0.65", "+1.68"):
        assert s.replace("-", "$-") in main.replace("$-$", "$-") or s in main, (
            f"headline effect {s} missing from main.tex")


def test_zero_drift_gate_contrasts_positive_and_significant():
    mult = pd.read_csv(SP / "multiplicity.csv")
    f4 = mult[mult.family.str.startswith("F4")]
    gates = f4[f4.contrast.str.contains("own-point|own-strict")]
    assert len(gates) == 6
    assert (gates.effect_pp > 0).all()
    assert gates.significant_holm.all()


NEW_TITLE = ("Candidate Governance for Drift-Triggered Classifier Pipelines "
             "in Network Intrusion Detection")
OLD_TITLE_FRAGMENT = "Label-Efficient Commit Decisions for Drift-Triggered Classifier Updates"


def test_definitive_title_everywhere():
    """v1.21 sealing: the definitive title is on every live surface and the old title is
    gone from them (historical notes may keep it for literal v1.20.2 identification)."""
    live = ["manuscript/main.tex", "manuscript/main_ieee.tex", "manuscript/supplement.tex",
            "README.md", "CITATION.cff", ".zenodo.json"]
    for p in live:
        t = re.sub(r"\s+", " ", (REPO / p).read_text(encoding="utf-8"))
        if p != ".zenodo.json":   # zenodo carries the artifact title + description
            assert NEW_TITLE in t or NEW_TITLE.replace(" in Network", " in Network") in t, p
        assert OLD_TITLE_FRAGMENT not in t, f"{p}: old title still present"


def test_unsw_zero_strict_guardrail_recorded():
    sec = pd.read_csv(SP / "security_metrics.csv")
    row = sec[(sec.scenario == "unsw_zero") & (sec.policy == "strict")
              & (sec.transformer_policy == "own_transformer_per_model")].iloc[0]
    assert not row.recall_NI_principal          # fails the principal margin ...
    assert row.recall_NI_lax                    # ... passes the lax sensitivity
    assert row.fpr_NI_principal                 # FPR side is clean
