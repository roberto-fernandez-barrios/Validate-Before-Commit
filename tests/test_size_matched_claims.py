"""Regression guards for the size-matched final rewrite.

Frozen sources: notes/size_matched_final_rewrite_protocol.md (allowed/forbidden claims)
and results/tables/size_matched_own_transformer_001/CLAIM_INTERPRETATION.json (the machine
verdict). These tests keep the manuscript permanently consistent with the frozen analysis:
the registered outcome stays ATTENUATION (never retro-classified), the headline numbers
never drift, and no forbidden claim re-emerges on a claim surface.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SM = REPO / "results" / "tables" / "size_matched_own_transformer_001"

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


def test_registered_outcome_is_attenuation():
    ci = json.loads((SM / "CLAIM_INTERPRETATION.json").read_text(encoding="utf-8"))
    assert ci["outcome"] == "ATTENUATION"
    assert ci["follow_up_authorized"] is False
    assert ci["confirmatory_seeds"] == "4001-4030"


def test_outcome_never_stated_as_elimination():
    for name, t in _texts().items():
        assert "formally elimination" not in t, name
        assert "outcome is elimination" not in t, name
        assert re.search(r"classified as elimination(?! classification)", t) is None, name


def test_no_size_matched_harm_persistence_claim():
    for name, t in _texts().items():
        assert re.search(r"harm persists[^.]{0,80}size-matched", t) is None, name
        assert ("persists even for self-contained challengers trained with the same"
                not in t), name


def test_no_universal_gate_claims():
    for name, t in _texts().items():
        assert "universally required" not in t, name
        assert "universally beneficial" not in t, name
        assert re.search(r"(?<!not a )universal requirement", t) is None, name
        assert re.search(r"gates? (?:are|remain) useful at (?:the matched size|2)", t) \
            is None, name


def test_sign_rate_never_a_probability():
    for name, t in _texts().items():
        for m in re.finditer(r"(?:48|50|52)\\?%|sign rate", t):
            w = t[max(0, m.start() - 120): m.end() + 120]
            assert "probability of harm" not in w and "deployment risk" not in w, name


def test_headline_numbers_match_frozen_csv():
    con = pd.read_csv(SM / "paired_contrasts.csv")
    mult = pd.read_csv(SM / "multiplicity.csv")
    eq = pd.read_csv(SM / "equivalence.csv")

    def eff(name):
        return float(con[con.contrast == name].effect_pp.iloc[0])

    # F1: no material mean damage at 2000; all equivalent at +-0.5 (CI90)
    for s in ("ps_zero", "unsw_zero", "ton_zero"):
        assert abs(eff(f"{s}: naive-2000 vs never")) < 0.5
        assert bool(eq[(eq.contrast == f"{s}: naive-2000 vs never")
                       & (eq.margin_kind == "primary")].equivalent.iloc[0])
    # F2: size effects positive and Holm-significant, matching the quoted magnitudes
    assert round(eff("ps_zero: naive-2000 vs naive-512"), 2) == 1.89
    assert round(eff("unsw_zero: naive-2000 vs naive-512"), 2) == 0.63
    assert round(eff("ton_zero: naive-2000 vs naive-512"), 2) == 0.23
    f2 = mult[mult.family.str.startswith("F2")]
    assert f2.significant_holm.all()
    # F3: no significant gate gain at 2000; every effect below 0.14 pp
    f3 = mult[mult.family.str.startswith("F3")]
    assert len(f3) == 6 and not f3.significant_holm.any()
    assert (f3.effect_pp.abs() < 0.14).all()


def test_scope_negations_present():
    """VBC-SG / observed-data / full-drift size-matched are declared NOT evaluated."""
    main = _texts()["manuscript/main.tex"]
    assert "vbc-sg was not re-run under size-matched own pipelines" in main
    assert "only under zero drift" in main
    assert re.search(r"full-drift size-matched[^.]{0,80}not run", main)


def test_v121_sealed_artifact_pointers_untouched():
    """The size-matched rewrite never edits the sealed v1.21.0 analysis outputs."""
    import hashlib
    manifest = REPO / "results" / "tables" / "MANIFEST.sha256"
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() \
        == "8500c6e2e241a34bca1001f7f312e3e3ab663aab1d9bd537288469a7cd3cdc43"
