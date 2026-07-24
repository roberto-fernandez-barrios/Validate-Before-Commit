"""v1.22.1 editorial scope correction guards (notes/v1_22_1_editorial_scope_protocol.md).

Pin the factual, scope, terminology and derived-table corrections of the v1.22.1
editorial phase so they cannot silently regress: exact artifact identity in Data
Availability, zero-drift scoping of every size-matched claim, conditional (not
universal) gating recommendations, nominal-parity terminology, the +-0.2/0.5/1.0
equivalence sensitivities, the evidence-validation trade-off table, the historical
re-captioning, detector-score scoping, and v1.22.0 artifact integrity.
"""
from __future__ import annotations

import hashlib
import json
import re

import pandas as pd

from tests.conftest import REPO

MAIN = (REPO / "manuscript" / "main.tex").read_text(encoding="utf-8")
IEEE = (REPO / "manuscript" / "main_ieee.tex").read_text(encoding="utf-8")
README = (REPO / "README.md").read_text(encoding="utf-8")
HIGHLIGHTS = (REPO / "manuscript" / "highlights.md").read_text(encoding="utf-8")
EDT = REPO / "results" / "tables" / "v1_22_1_editorial"
SM = REPO / "results" / "tables" / "size_matched_own_transformer_001"


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower())


# ---------------------------------------------------------------- data availability
def test_data_availability_declares_exact_v1_22_0_identity():
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE)):
        f = _flat(t)
        assert "10.5281/zenodo.21517899" in f, f"{name}: exact version DOI missing"
        assert "10.5281/zenodo.21322256" in f, f"{name}: concept DOI missing"
        assert "43d9c255af48db9bcc3c6eb341a153381b18c8e8" in f, f"{name}: sealing commit missing"
        assert "artifact version v1.22.0" in f, f"{name}: artifact version declaration missing"
        assert not re.search(r"artifact version\s*v?1\.20\.2", f), (
            f"{name}: stale v1.20.2 artifact declaration must be gone")
        assert "v1.22.1" not in f, f"{name}: must not claim v1.22.1 exists yet"


def test_version_doi_and_tag_declared_together():
    for t in (MAIN, IEEE):
        f = _flat(t)
        i = f.index("10.5281/zenodo.21517899")
        window = f[max(0, i - 400): i + 400]
        assert "v1.22.0" in window, "version DOI must be declared alongside tag v1.22.0"


# ---------------------------------------------------------------- highlights
def test_highlights_scoped_and_within_limit():
    m = re.search(r"\\begin\{highlights\}(.*?)\\end\{highlights\}", MAIN, re.S)
    assert m, "highlights block missing from main.tex"
    block = m.group(1).lower()
    assert "zero drift" in block, "highlights must carry the zero-drift scope"
    assert "0.5" in block, "highlights must carry the +-0.5 margin"
    assert "once sizes match" not in block, "unscoped once-sizes-match highlight banned"
    bullets = re.findall(r"^- (.+?)\s+\[\d+\]$", HIGHLIGHTS, re.M)
    assert len(bullets) == 5, "highlights.md must list 5 bullets with char counts"
    for b in bullets:
        assert len(b) <= 85, f"highlight exceeds 85 chars: {b!r} ({len(b)})"
    joined = " ".join(bullets).lower()
    assert "zero drift" in joined or "zero-drift" in joined
    assert "±0.5" in " ".join(bullets) or "\\pm" in joined or "0.5-pp" in joined


# ---------------------------------------------------------------- graphical abstract
def test_graphical_abstract_scoped():
    src = (REPO / "src" / "analysis" / "make_paper2_graphical_abstract_final.py"
           ).read_text(encoding="utf-8")
    assert "ZERO-DRIFT CONTROL" in src
    assert "nominal size parity" in src
    assert "0.5" in src
    assert (REPO / "docs" / "img" / "graphical_abstract.png").exists()


# ---------------------------------------------------------------- scope of claims
def test_no_unscoped_size_matched_generalizations():
    for name in ("manuscript/main.tex", "manuscript/main_ieee.tex",
                 "manuscript/supplement.tex", "README.md", "REPRODUCE.md",
                 "manuscript/highlights.md"):
        f = _flat((REPO / name).read_text(encoding="utf-8"))
        assert "no measurable value once sizes match" not in f, name
        assert not re.search(r"comparability is (already )?guaranteed", f), name
        assert "gate value disappears whenever evidence is comparable" not in f, name


def test_size_matched_scope_limits_retained():
    for t in (MAIN, IEEE):
        f = _flat(t)
        assert "only under zero drift" in f, "zero-drift-only limitation must stay"
        assert "sample-size parity" in f, "nominal parity terminology required"
        assert "temporal coverage, diversity, subtype support, label quality" in f, (
            "nominal-vs-effective evidence caveat required")
        assert "not a consequence of equal row counts alone" in f


# ---------------------------------------------------------------- README
def test_readme_conditional_recommendation():
    f = _flat(README)
    assert "the challenger should be validated before it replaces" not in f, (
        "universal validation recommendation must be gone")
    assert "asymmetric or uncertain, validate the challenger" in f, (
        "conditional recommendation must be present")
    assert "point and strict validation provided no measurable gain" in f
    assert "nominal 2,000-per-class parity" in f


# ---------------------------------------------------------------- equivalence margins
def test_equivalence_margin_sensitivity_pinned():
    out = pd.read_csv(EDT / "equivalence_margin_sensitivity.csv").set_index("contrast")
    src = pd.read_csv(SM / "equivalence.csv")
    assert len(out) == src.contrast.nunique()
    assert (out.registered_primary_margin == 0.5).all()
    for contrast, r in out.iterrows():
        g = src[src.contrast == contrast].set_index("margin_pp")
        for m, col in ((0.2, "equivalent_pm0p2"), (0.5, "equivalent_pm0p5"),
                       (1.0, "equivalent_pm1p0")):
            assert bool(r[col]) == bool(g.loc[m, "equivalent"]), (contrast, m)
            derived = (-m <= r.ci90_lo) and (r.ci90_hi <= m)
            assert derived == bool(r[col]), (contrast, m)
    ps = out.loc["ps_zero: naive-2000 vs never"]
    assert not ps.equivalent_pm0p2 and ps.equivalent_pm0p5 and ps.equivalent_pm1p0, (
        "PortScan must be margin-sensitive: fails +-0.2, passes +-0.5 and +-1.0")
    for sc in ("unsw_zero", "ton_zero"):
        r = out.loc[f"{sc}: naive-2000 vs never"]
        assert r.equivalent_pm0p2 and r.equivalent_pm0p5 and r.equivalent_pm1p0, sc


def test_margin_language_in_text():
    f = _flat(MAIN)
    assert "margin-dependent" in f
    assert "margin-sensitive at" in f
    for t in (MAIN, IEEE):
        ff = _flat(t)
        assert "identical performance" not in ff
        assert "equal performance" not in ff


# ---------------------------------------------------------------- trade-off table
def test_tradeoff_counts_from_config_and_logs():
    cfg = json.loads((REPO / "configs" / "size_matched_own_transformer_v1.json"
                      ).read_text(encoding="utf-8"))
    out = pd.read_csv(EDT / "evidence_validation_tradeoff.csv")
    probe = int(cfg["policies"]["point"]["--probe-size"])
    sizes = sorted(int(s) for s in cfg["candidate_sizes_per_class"])
    incumbent = int(cfg["incumbent_train_size_per_class"])
    assert (incumbent - sizes[0]) * 2 == 2976, "1,488/class x 2 = 2,976"
    assert (out.additional_candidate_labels_512_to_2000 == 2976).all()
    assert sorted(out.candidate_labels_per_proposal.unique()) == [2 * s for s in sizes]
    gates = out[out.policy.str.startswith(("point", "strict"))]
    assert (gates.probe_labels_per_proposal == probe).all()
    assert (out[out.policy.str.startswith("naive")].probe_labels_per_proposal == 0).all()
    assert (out.total_adjudicated_labels_per_proposal
            == out.candidate_labels_per_proposal + out.probe_labels_per_proposal).all()


def test_tradeoff_matches_sealed_outputs():
    out = pd.read_csv(EDT / "evidence_validation_tradeoff.csv")
    main_rows = out[out.block == "main"]
    assert len(main_rows) == 12
    assert not main_rows.duplicated(["dataset", "policy"]).any()
    assert set(main_rows.policy) == {"naive_512", "point_512", "strict_512", "naive_2000"}
    assert set(out[out.block == "supplementary"].policy) == {"point_2000", "strict_2000"}
    con = pd.read_csv(SM / "paired_contrasts.csv").set_index("contrast")
    desc = pd.read_csv(SM / "descriptive_contrasts.csv").set_index("contrast")
    summ = pd.read_csv(SM / "summary.csv", keep_default_na=False, na_values=[""])
    for _, r in out.iterrows():
        pol, size = r.policy.rsplit("_", 1)
        if pol == "naive" and size == "2000":
            s = con.loc[f"{r.scenario}: naive-2000 vs never"]
            assert abs(r.ba_vs_never_pp - s.effect_pp) < 1e-9
            assert abs(r.ba_vs_never_ci95_lo - s.ci95_lo) < 1e-9
            assert abs(r.ba_vs_never_ci95_hi - s.ci95_hi) < 1e-9
        if pol == "naive" and size == "512":
            s = desc.loc[f"{r.scenario}: naive-512 vs never"]
            assert abs(r.ba_vs_never_pp - s.effect_pp) < 1e-9
        if pol in ("point", "strict"):
            name = (f"{r.scenario}: {pol}-{size} vs naive-{size}")
            s = con.loc[name] if size == "2000" else desc.loc[name]
            assert abs(r.gate_gain_vs_naive_pp - s.effect_pp) < 1e-9
            if size == "2000":
                assert "registered F3" in r.gate_gain_status
                assert "Holm n.s." in r.gate_gain_status, (
                    "all six registered gate contrasts at 2000 are non-significant")
        m = summ[(summ.scenario == r.scenario) & (summ.policy == pol)
                 & (summ.candidate_size.astype(str) == size)]
        assert abs(float(m.commits_mean.iloc[0]) - r.commits_per_seed) < 5e-4


def test_tradeoff_table_wired_and_caveated():
    assert "\\input{tables/table_evidence_validation_tradeoff.tex}" in MAIN
    for d in ("tables", "tables_ieee", "generated"):
        p = REPO / "manuscript" / d / "table_evidence_validation_tradeoff.tex"
        assert p.exists(), f"{d} variant missing"
        t = _flat(p.read_text(encoding="utf-8"))
        assert "2{,}976" in t or "2,976" in t
        assert "economic dominance" in t, "no-economic-dominance caveat required"
        assert "nominal" in t
    f = _flat(MAIN)
    assert "establishes no economic dominance" in f or "not establish economic dominance" in f


# ---------------------------------------------------------------- historical framing
def test_historical_table_recaptioned():
    for d in ("tables", "tables_ieee"):
        t = _flat((REPO / "manuscript" / d / "table_v2_confirmatory.tex"
                   ).read_text(encoding="utf-8"))
        assert "historical frozen-policy diagnostic" in t
        assert "main confirmatory result" not in t
    # KBS final scope reduction: the frozen-policy diagnostic is subordinated into the §5.5
    # supporting block (no longer its own headline subsection); the label survives in main.
    assert "historical frozen-policy diagnostic" in MAIN.lower()


# ---------------------------------------------------------------- detector claims
def test_detector_score_claims_scoped():
    for name in ("manuscript/main.tex", "manuscript/main_ieee.tex", "README.md"):
        f = _flat((REPO / name).read_text(encoding="utf-8"))
        assert "not the lever" not in f, name
        assert "score is uninformative" not in f, name
        assert "optimizes the wrong object" not in f, name
    assert "within triggered decisions" in _flat(MAIN)
    assert "within triggered decisions" in _flat(README)


# ---------------------------------------------------------------- ATTENUATION wording
def test_attenuation_registered_but_not_dominant():
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE)):
        f = _flat(t)
        assert "attenuation" in f, f"{name}: registered outcome must stay"
        assert "near-elimination" not in f, name
        assert "effectively elimination" not in f, name
        assert "formal elimination" not in f, name
        assert "residual mean harm under attenuation" not in f, name
    abstract = re.search(r"\\begin\{abstract\}\n(.*?)\n\\end\{abstract\}", MAIN, re.S).group(1)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", abstract) if "ATTENUATION" in s]
    assert len(sentences) == 1, "abstract: exactly one sentence on the taxonomy"


# ---------------------------------------------------------------- artifact integrity
def test_v1_22_1_manifest_pinning():
    """v1.22.1 sealing: the MANIFEST re-pin is additive — every v1.22.0 pin survives
    (183 non-editorial CSVs, byte-verified by verify_results_manifest) plus exactly the
    two derived editorial CSVs (185 total)."""
    ms = (REPO / "results" / "tables" / "MANIFEST.sha256").read_text(encoding="utf-8")
    pinned = [ln for ln in ms.splitlines() if ln.strip()]
    assert len(pinned) == 185, "185 pinned CSVs at v1.22.1 (183 + 2 editorial)"
    editorial = [ln for ln in pinned if "v1_22_1_editorial/" in ln]
    assert len(editorial) == 2, "exactly the two editorial CSVs are the additive pins"
    for f in ("equivalence_margin_sensitivity.csv", "evidence_validation_tradeoff.csv"):
        assert any(ln.endswith(f"v1_22_1_editorial/{f}") for ln in pinned), f
        h = hashlib.sha256((EDT / f).read_bytes()).hexdigest()
        assert any(ln.startswith(h) for ln in editorial), (
            f"pinned hash must match the on-disk editorial CSV: {f}")


def test_no_editorial_raw_outputs():
    assert not (REPO / "results" / "raw" / "v1_22_1_editorial").exists()
    for f in ("equivalence_margin_sensitivity.csv", "evidence_validation_tradeoff.csv"):
        assert (EDT / f).exists(), f"derived editorial output missing: {f}"
