"""q1-final-patch v1.20.1: structural tests for claim scope, harm accounting and the
operational arm's declared semantics. These pin the corrections of the statistical/claims
patch so they cannot silently regress.
"""
from __future__ import annotations

import json
import re

import pandas as pd
import pytest

from tests.conftest import REPO

SURFACES = ["manuscript/main.tex", "manuscript/main_ieee.tex", "manuscript/supplement.tex",
            "manuscript/highlights.md", "README.md", "REPRODUCE.md",
            "manuscript/tables/table_budget_frontier.tex",
            "manuscript/tables/table_operational_e2e.tex",
            "manuscript/tables/table_chronological_q1.tex"]


def _text() -> str:
    parts = []
    for p in SURFACES:
        f = REPO / p
        if f.exists():
            parts.append(re.sub(r"\s+", " ", f.read_text(encoding="utf-8").lower()))
    return " \n ".join(parts)


def test_no_binomial_rate_bound_on_harm_count():
    t = _text()
    assert "0.726" not in t
    assert not re.search(r"0\.73\\?%", t), "the 0.73% population-rate bound must be gone"
    assert "clopper" not in t
    for f in ("manuscript/main.tex", "manuscript/main_ieee.tex"):
        tt = (REPO / f).read_text(encoding="utf-8").lower()
        assert "not treated as 506 independent bernoulli trials" in re.sub(r"\s+", " ", tt), (
            f"{f}: the clustering caveat must accompany the 0/506 count")


def test_operational_scope_fields_in_manifest():
    mf = REPO / "results" / "final_manifest.json"
    if not mf.exists():
        pytest.skip("final_manifest.json not generated")
    m = json.loads(mf.read_text(encoding="utf-8"))
    s = m.get("operational_arm_scope")
    assert s, "manifest must declare operational_arm_scope"
    assert s["evaluation_stream_prevalence"] == "balanced"
    assert s["detector_calibration_prevalence"] == "balanced"
    assert s["candidate_training_sampling"] == "balanced_per_class"
    assert s["candidate_training_inspection_cost_modeled"] is False
    assert s["adjudication_pool_prevalence"] == "operating"
    assert s["discovery_used_for_commit"] is False
    assert s["validation_sampling_policy"] == "uniform_at_operating_prevalence"
    assert s["validation_labels"] == 32
    assert s["decision_metric"] == "plain_accuracy"
    assert s["operational_scope"] == "acquisition_yield_and_delay_only"
    assert s["end_to_end_pipeline_cost_modeled"] is False
    hc = m["harmful_commits"]
    assert hc["binomial_upper_bound_reported"] is False
    assert "cluster" in hc["reason"]


def test_claim_scope_audit_table():
    f = REPO / "results" / "tables" / "paper2_final_q1" / "claim_scope_audit.csv"
    if not f.exists():
        pytest.skip("claim_scope_audit.csv not generated")
    a = pd.read_csv(f)
    assert len(a) >= 12
    for col in ("claim_id", "claim_text_short", "evidence_tier", "primary_source",
                "unit_of_analysis", "multiplicity_family", "operational_scope",
                "allowed_wording", "forbidden_wording", "status"):
        assert col in a.columns
    assert not a.status.str.startswith("FAIL").any(), (
        a[a.status.str.startswith("FAIL")][["claim_id", "status"]].to_string())


def test_cohort_and_affordable_and_labels_scoped():
    t = _text()
    assert "cohort-sim" in t, "Cohort must be presented as the Cohort-sim resampling simulation"
    assert "affordab" not in t, "'affordable' must not appear unqualified on claim surfaces"
    assert "non-vacuous within the evaluated" in t
    assert "both budgets are realistic" not in t
    assert "32 labels suffice" not in t
    assert "cheap and robust" not in t
    assert "validation costs little and protects" not in t
    assert "controlled balanced-probe" in t, "32-label claim must carry its scope"
    assert "zero probability of harm" not in t
    assert "eliminates harmful commits" not in t


def test_v1202_claim_scope_hardening():
    """v1.20.2: causal-inference language removed; scope qualifications present."""
    t = _text()
    for phrase in ("causal arm", "genuinely causal", "causal result", "causal experiment",
                   "realistic cost", "reliable safeguard", "identity is secondary",
                   "risk guarantee at tens of labels", "512-flow probe cap",
                   "operating point we recommend", "independent confirmation"):
        assert phrase not in t, f"forbidden phrase survives: {phrase!r}"
    for f in ("manuscript/main.tex", "manuscript/main_ieee.tex"):
        tt = re.sub(r"\s+", " ", (REPO / f).read_text(encoding="utf-8").lower())
        assert "leakage-free observed-data" in tt, f
        assert "free of simulator-oracle information" in tt, f
        assert "pooled sequential gate provides useful empirical risk control" in tt, f
        assert "formally aligned stratified guarantee" in tt, f
        assert "578" in tt and "deferral" in tt, f"{f}: cap-vs-total clarification missing"
        assert "conditional on a comparable proposal" in tt, f
        assert "adjudication count" in tt, f


def test_paper1_reference_removed():
    # KBS bibliographic ceiling (user decision): this paper is now "Paper 1", so the
    # companion-study reference to a separate Paper 1 was removed. Guard that neither the
    # citation nor the bib entry lingers anywhere.
    bib = (REPO / "manuscript" / "references.bib").read_text(encoding="utf-8")
    assert "fernandez_paper1" not in bib, "companion Paper 1 bib entry must be gone"
    assert "Authors' own prior work (Paper 1)" not in bib, "Paper 1 section marker must be gone"
    for name in ("manuscript/main.tex", "manuscript/main_ieee.tex"):
        t = (REPO / name).read_text(encoding="utf-8")
        assert "fernandez_paper1" not in t, f"{name}: dangling Paper 1 citation"
        assert "companion study" not in t.lower(), f"{name}: companion-study framing must be gone"


def test_no_broad_priority_claims():
    # KBS bibliographic ceiling: after adding active-testing / limited-label model-selection
    # and retraining-decision references, the paper must not claim priority over those
    # neighbours. The defensible novelty is the *combination* inside adaptive NIDS.
    import re
    forbidden = [
        r"first to (compare|select|evaluate) models? with (few|limited|scarce) labels",
        r"first (active[- ]testing|limited[- ]label model selection)",
        r"novel (active[- ]testing|model comparison with (few|limited) labels)",
        r"unlike all (previous|prior) work",
        r"no (previous|prior) work (has )?(studies|studied|compares|compared|considers|considered)",
        r"we (are the )?first to (decide|determine) (whether|when) retraining",
    ]
    for name in ("manuscript/main.tex", "manuscript/main_ieee.tex", "README.md",
                 "manuscript/highlights.md"):
        p = REPO / name
        if not p.exists():
            continue
        t = re.sub(r"\s+", " ", p.read_text(encoding="utf-8").lower())
        for pat in forbidden:
            assert not re.search(pat, t), f"{name}: broad priority claim {pat!r}"
    # the RW must position these literatures as prior work (cited, not claimed); the
    # statistical procedures used must carry their original sources.
    main = (REPO / "manuscript" / "main.tex").read_text(encoding="utf-8")
    for key in ("sawade2012active", "kossen2021active", "karimi2021online", "han2024model",
                "okanovic2025models", "zliobaite2015cost", "mahadevan2024cost",
                "regol2025retrain", "mcnemar1947note", "holm1979simple",
                "benjamini1995controlling", "schuirmann1987comparison"):
        assert ("\\cite{" in main) and key in main, f"expected reference {key} cited in main"
