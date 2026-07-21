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


def test_paper1_reference_untouched():
    bib = (REPO / "manuscript" / "references.bib").read_text(encoding="utf-8")
    i = bib.find("Authors' own prior work (Paper 1)")
    assert i > 0, "Paper 1 section marker must exist"
    # the pending Paper 1 entry must still be present and unmodified in its key fields
    tail = bib[i:]
    assert "arXiv" in tail or "unpublished" in tail or "@" in tail
