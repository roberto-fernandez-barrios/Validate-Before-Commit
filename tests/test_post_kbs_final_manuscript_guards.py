"""Guards for the post-KBS final manuscript integration (B2 + B1 evidence).

These tests pin the final thesis hierarchy and the way the two registered post-v1.22
blocks are reported: every B2/B1 number quoted in the manuscript is re-derived from the
confirmatory CSVs, the validation framing is conditional (never universal), the
external-baseline scope sentences are the final ones, and the main body / IEEE port /
supplement / docs carry the same structure.
"""
import json
import re

import pandas as pd

from tests.conftest import REPO

T = REPO / "results" / "tables"
B2 = T / "post_kbs_size_matched_drift_001"
B1 = T / "post_kbs_common_harness_baselines_001"
MAIN = (REPO / "manuscript" / "main.tex").read_text(encoding="utf-8")
IEEE = (REPO / "manuscript" / "main_ieee.tex").read_text(encoding="utf-8")
SUPP = (REPO / "manuscript" / "supplement.tex").read_text(encoding="utf-8")
README = (REPO / "README.md").read_text(encoding="utf-8")
NEW_TABLES = ("table_synthesis", "table_size_matched_drift", "table_common_harness",
              "table_size_matched_drift_supp", "table_size_matched_drift_security",
              "table_common_harness_supp_primary", "table_common_harness_supp_secondary",
              "table_common_harness_supp_statements")


def _flat(t: str) -> str:
    return re.sub(r"\s+", " ", t).lower()


def _abstract(t: str) -> str:
    return re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", t, re.S).group(1)


# ---------------------------------------------------------------- abstract
def test_abstract_rewritten_length_and_thesis():
    a = _abstract(MAIN)
    n = len(a.split())
    assert 185 <= n <= 235, f"abstract has {n} words (target 190-220, audit cap 250)"
    f = _flat(a)
    for s in ("drift alarm only detects change", "comparability", "+0.82", "+1.66", "+1.00",
              "homogeneous size benefit", "validation is conditional",
              "no evaluated policy dominates", "should therefore precede"):
        assert s in f, s
    for s in ("boundary-close", "vbc-sg", "quantum", "attenuation", "cohort", "chronolog",
              "protocol", "e-process", "supermartingale"):
        assert s not in f, f"abstract must not carry {s!r}"


# ---------------------------------------------------------------- B2 numbers sourced from CSVs
def test_b2_numbers_and_outcome_match_csvs():
    con = pd.read_csv(B2 / "paired_contrasts.csv").set_index("contrast")
    mult = pd.read_csv(B2 / "multiplicity.csv").set_index("contrast")
    interp = json.loads((B2 / "CLAIM_INTERPRETATION.json").read_text(encoding="utf-8"))
    assert interp["outcome"] == "HOMOGENEOUS-SIZE BENEFIT"
    for t in (MAIN, IEEE):
        f = _flat(t)
        assert "homogeneous-size benefit" in f
        for sc in ("ps", "unsw", "ton"):
            r = con.loc[f"{sc}_full: naive-2000 vs naive-512"]
            assert f"{float(r.effect_pp):+.2f}" in t, (sc, r.effect_pp)
            assert interp["per_scenario"][f"{sc}_full"]["classification"] == "SIZE BENEFIT"
            for arm in ("512", "2000"):
                r1 = con.loc[f"{sc}_full: naive-{arm} vs never"]
                assert f"{float(r1.effect_pp):+.2f}" in t, (sc, arm)
        g3 = mult[mult.index.str.contains(r"-2000 vs naive-2000")]
        assert len(g3) == 6
        assert int(((g3.effect_pp > 0) & g3.significant_holm).sum()) == 0
        assert "0/6" in f
        strict = con.loc["unsw_full: strict-2000 vs naive-2000"]
        assert bool(mult.loc["unsw_full: strict-2000 vs naive-2000", "significant_holm"])
        assert f"{float(strict.effect_pp):+.2f}" in t
        assert "resolved cost" in f


def test_b2_claim_guards():
    for t in (MAIN, IEEE):
        f = _flat(t)
        assert "size matching only evaluated at zero drift" not in f
        assert "only under zero drift" not in f
        assert "does not retroactively change" in f
        assert "attenuation" in f, "the historical zero-drift registered outcome must stay"
        assert "effective information parity" in f and "not" in f
        for s in ("universal monotonic benefit", "larger training windows improve arbitrary"):
            assert s in f, f"B2 non-claim {s!r} must be stated"
        assert "always help" in f  # 'no claim that larger candidate batches always help'


# ---------------------------------------------------------------- B1 numbers and framing
def test_b1_framing_and_statements_match_csvs():
    st = pd.read_csv(B1 / "statements.csv")
    s4 = st[st.statement.str.startswith("S4") & st.holds.astype(bool)]
    assert set(s4.policy) == {"atc", "enscal"}
    s2 = st[st.statement.str.startswith("S2") & st.holds.astype(bool)]
    assert set(s2.policy) == {"doc", "replay", "ddm", "adwin"}
    assert not st[st.statement.str.startswith(("S1", "S3"))].holds.astype(bool).any()
    cls = pd.read_csv(B1 / "cell_classification.csv")
    full = cls[cls.family.str.startswith("PF2")]
    for pol, expect in (("atc", {"COMPATIBLE", "UNRESOLVED"}), ("enscal", {"COMPATIBLE"}),
                        ("replay", {"MATERIAL COST"}), ("ddm", {"MATERIAL COST"}),
                        ("adwin", {"MATERIAL COST"})):
        got = set(full[full.contrast.str.contains(f": {pol}-2000 vs naive-2000")].classification)
        assert got == expect, (pol, got)
    mult = pd.read_csv(B1 / "multiplicity.csv")
    sf5 = mult[mult.family.str.startswith("SF5") & mult.significant_holm.astype(bool)]
    assert len(sf5) == 15 and (sf5.effect_pp < 0).all()
    for t in (MAIN, IEEE):
        f = _flat(t)
        for s in ("registered common-harness comparison with published and reference baselines",
                  "no faithfully reproducible end-to-end published adaptive-nids system",
                  "atc", "doc", "river-ddm", "river-adwin", "calibrated ensemble",
                  "material cost", "compatible", "unresolved", "fifteen holm-significant",
                  "fires for atc", "calibrated ensemble (portscan and ton-iot full drift",
                  "budgets differ legitimately", "not a state-of-the-art ranking"):
            assert s in f, s
        for s in ("state-of-the-art adaptive", "sota", "outperforms the state of the art",
                  "no prior work", "the first to", "beats all baselines"):
            assert s not in f, s


# ---------------------------------------------------------------- validation framing
def test_validation_is_conditional_never_universal():
    for t in (MAIN, IEEE):
        f = _flat(t)
        assert ("we do not call validation necessary, generally safer, superior, or the "
                "recommended default") in f
        for s in ("validation is necessary", "validation is generally safer",
                  "validation is superior", "validation is the recommended default",
                  "we recommend validating", "always validate", "the gate rescues",
                  "rescued by the gate", "validation should always"):
            assert s not in f, s
        assert "validate when upstream comparability cannot be established cheaply" in f
        assert "extrapolates beyond the fixed-policy evidence" in f
        assert "0/6" in f


# ---------------------------------------------------------------- structure and tables
def test_results_structure_and_generated_tables():
    results = MAIN.split("\\section{Results}")[1].split("\\section{Discussion}")[0]
    subs = re.findall(r"\\subsection\{([^}]*)\}", results)
    prefixes = ["The historical frozen configuration", "Candidate construction",
                "Candidate evidence at zero drift", "Candidate evidence under real drift",
                "Validation has conditional average value",
                "Registered common-harness comparison", "Mechanism, formal instruments"]
    assert len(subs) == 7
    for s, p in zip(subs, prefixes):
        assert s.startswith(p), (s, p)
    assert "\\input{tables/table_synthesis.tex}" in MAIN
    syn = (REPO / "manuscript" / "tables" / "table_synthesis.tex").read_text(encoding="utf-8")
    assert "not evaluated under a registered protocol" in syn
    con = pd.read_csv(B2 / "paired_contrasts.csv").set_index("contrast")
    for sc in ("ps", "unsw", "ton"):
        assert f"{float(con.loc[f'{sc}_full: naive-2000 vs never', 'effect_pp']):+.2f}" in syn
    for name in NEW_TABLES:
        a = (REPO / "manuscript" / "tables" / f"{name}.tex").read_bytes()
        b = (REPO / "manuscript" / "tables_ieee" / f"{name}.tex").read_bytes()
        assert a == b, name
    assert "\\label{sec:supp_sizematched_drift}" in SUPP
    assert "\\label{sec:supp_common_harness}" in SUPP
    for name in NEW_TABLES[3:]:
        assert f"\\input{{tables/{name}.tex}}" in SUPP, name
    assert "\\input{tables/table_symmetric_security.tex}" in SUPP
    assert "\\input{tables/table_symmetric_security.tex}" not in MAIN


def test_docs_carry_post_kbs_blocks():
    for p in ("results/tables/post_kbs_size_matched_drift_001/",
              "results/tables/post_kbs_common_harness_baselines_001/",
              "notes/post_kbs_size_matched_drift_protocol_001.md",
              "notes/post_kbs_common_harness_baselines_amendment_001.md",
              "configs/post_kbs_size_matched_drift_v1.json",
              "configs/post_kbs_common_harness_baselines_v2.json"):
        assert p in README, p
        assert (REPO / p.rstrip("/")).exists(), p
    for rel in ("REPRODUCE.md", "docs/SCIENTIFIC_PROVENANCE.md"):
        t = (REPO / rel).read_text(encoding="utf-8")
        assert "post_kbs_size_matched_drift_001" in t, rel
        assert "post_kbs_common_harness_baselines_001" in t, rel
    resp = (REPO / "audits" / "kbs_response_to_reviewers.md").read_text(encoding="utf-8")
    assert "common-harness" in resp and "ATC" in resp and "river" in resp
    assert "state-of-the-art" not in resp.lower() or "not" in resp.lower()
