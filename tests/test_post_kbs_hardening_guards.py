"""Post-KBS hardening guards (audits/post_kbs_hardening_report.md).

Pin the hostile-review fixes so they cannot silently regress: the artifact is
self-contained (every MANIFEST-pinned CSV is tracked and its committed blob byte-matches
the pin, so a fresh clone passes `make verify-hashes`), the size-matched interpretation
stays scoped (accounts-for wording, exchangeability statement, sign-rate gloss), the
frozen-preprocessing policy is never presented as a field convention, the baseline
comparison never claims a SoTA ranking, the supplement no longer contradicts section 5.2,
the VBC-SG chronological price stays visible, and the wall-clock figures stay non-causal.
"""
from __future__ import annotations

import hashlib
import re
import subprocess

from tests.conftest import REPO

MAIN = (REPO / "manuscript" / "main.tex").read_text(encoding="utf-8")
IEEE = (REPO / "manuscript" / "main_ieee.tex").read_text(encoding="utf-8")
SUPP = (REPO / "manuscript" / "supplement.tex").read_text(encoding="utf-8")
README = (REPO / "README.md").read_text(encoding="utf-8")
REPRO = (REPO / "REPRODUCE.md").read_text(encoding="utf-8")


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower())


def _pins() -> dict[str, str]:
    out = {}
    text = (REPO / "results" / "tables" / "MANIFEST.sha256").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.strip():
            h, p = line.split(None, 1)
            out[p.strip()] = h
    return out


# ---------------------------------------------------------------- artifact self-containment
def test_every_manifest_pin_is_tracked():
    pins = _pins()
    assert len(pins) == 185
    tracked = set(subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                                 text=True).stdout.split("\n"))
    missing = [p for p in pins if p not in tracked]
    assert not missing, f"manifest-pinned files not tracked in git: {missing[:5]}"


def test_every_tracked_pin_blob_is_byte_exact():
    """The committed blob (what a fresh clone checks out, under the -text attribute) must
    hash exactly to the manifest pin -- eol normalization would silently break this."""
    pins = _pins()
    bad = []
    for p, h in pins.items():
        blob = subprocess.run(["git", "cat-file", "blob", f":{p}"], cwd=REPO,
                              capture_output=True).stdout
        if hashlib.sha256(blob).hexdigest() != h:
            bad.append(p)
    assert not bad, f"committed blob differs from manifest pin: {bad[:5]}"


def test_results_tables_protected_from_eol_conversion():
    ga = (REPO / ".gitattributes").read_text(encoding="utf-8")
    assert "results/tables/** -text" in ga, (
        "sealed CSVs need the -text attribute or fresh clones check out different bytes")


def test_protocol_commit_reachability_audit_exists():
    csv = (REPO / "audits" / "protocol_commit_reachability.csv")
    assert csv.exists()
    head = csv.read_text(encoding="utf-8").splitlines()
    assert head[0] == "protocol_file,claimed_sha,object_exists,reachable_ref,status,action"
    assert len(head) > 20, "the reachability inventory should cover the known references"


# ---------------------------------------------------------------- size-matched interpretation
def test_size_matched_uses_accounts_for_not_explains():
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE)):
        f = _flat(t)
        assert "explains the residual zero-drift" not in f, name
        assert "accounts for the residual zero-drift mean harm" in f, name
    assert "explains residual zero-drift" not in _flat(SUPP)


def test_exchangeability_and_sign_rate_gloss_present():
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE)):
        f = _flat(t)
        assert "exchangeable re-draw" in f, name
        assert "structurally unable to certify elimination" in f, name
        assert "not as evidence of directional residual harm" in f, name


# ---------------------------------------------------------------- convention language
def test_frozen_preprocessing_never_called_a_field_convention():
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE)):
        f = _flat(t)
        assert "historical convention" not in f, name
        assert "common convention" not in f, name
        assert ("we do not claim that frozen incumbent-owned preprocessing is a standard "
                "or widespread policy") in f, name


# ---------------------------------------------------------------- baseline comparison framing
def test_baseline_comparison_not_presented_as_sota():
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE)):
        f = _flat(t)
        assert "comparison with strong baselines" not in f, name
        assert "registered common-harness comparison with published and reference baselines" in f, name
        # final integration: the external-baseline gap is closed for generic/reference
        # methods; the old 'not yet evaluated' scope sentence must be gone, and the
        # end-to-end-system limitation must be stated explicitly instead
        assert ("no external method has yet been evaluated under the final "
                "self-contained") not in f, name
        assert ("no faithfully reproducible end-to-end published adaptive-nids system") in f, name
        assert "not a state-of-the-art ranking" in f, name
    assert re.search(r"sota", _flat(README)) is None, "README must not advertise SoTA"


def test_patterns_paragraph_reports_docs_and_ensemble_wins():
    """Final integration: the exploratory DoC-beats-gate pattern is reported together with
    its confirmatory reversal, and the ensemble/ATC results are scoped as compatibility."""
    f = _flat(MAIN)
    assert "does not reproduce under the final harness at parity" in f
    assert "the value of every evaluated safeguard" in f
    assert "concentrates where candidate evidence is asymmetric" in f
    assert "not a demonstration of equality" in f


# ---------------------------------------------------------------- supplement consistency
def test_zero_drift_caption_no_longer_contradicts_5_2():
    for d in ("tables", "tables_ieee"):
        t = _flat((REPO / "manuscript" / d / "table_zero_drift.tex").read_text(encoding="utf-8"))
        assert "so the harm is not a small-candidate artifact" not in t, d
        assert "frozen-policy result" in t, d
        assert "must not be read as contradicting" in t, d


def test_supplement_initial_study_titles_scoped():
    f = _flat(SUPP)
    assert "gate resolves the problem" not in f
    assert "only gate on the benefit--safety pareto front" not in f
    assert "empirical safety property" not in f
    assert "an observation of this exploratory study, not a certified property" in f


# ---------------------------------------------------------------- chronological evidence
def test_vbcsg_chronological_price_stated():
    f = _flat(MAIN)
    assert "price of that conservatism" in f
    assert "0--9\\%" in MAIN, "the CICIDS retention range must stay quantified"
    assert "operational price of the guarantee" in f


def test_chronological_family_weakness_disclosed():
    for t in (MAIN, SUPP):
        assert "structurally easy to satisfy" in _flat(t)


def test_ton_iot_chronological_gap_stated():
    f = _flat(MAIN)
    assert ("ships no timestamps, so the controlled harm benchmark has no chronological "
            "counterpart") in f


# ---------------------------------------------------------------- wall-clock scoping
def test_wallclock_ratios_not_causal():
    f = _flat(MAIN)
    assert "do not isolate preprocessing overhead" in f
    assert "not a speedup caused by self-contained preprocessing" in f
    assert ", because svc-rbf training scales with the batch." not in f


# ---------------------------------------------------------------- stale doc wording
def test_reproduce_stale_wording_gone():
    f = _flat(REPRO)
    assert "equivalent to zero" not in f
    assert "gate solves it" not in f
    assert "verify-hashes` passes on a fresh clone" in f or \
        "verify-hashes passes on a fresh clone" in f
