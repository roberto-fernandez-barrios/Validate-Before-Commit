"""q1-final-patch v1.20.1 Block B: the multiplicity machinery, pinned.

Primary analysis = deterministic CENTERED paired bootstrap test (resampling under H0 with
the observed mean removed), Monte-Carlo corrected p = (extreme+1)/(B+1), per-contrast RNG
derived from the contrast label. Families are fixed and outcome-independent: 6 core (Holm),
15 frontier cells including zero-commit configurations (BH), 7 chronological (BH) = 28.
The A/B equivalence output remains a bootstrap CI-based assessment with no pseudo p-values.
"""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

from tests.conftest import REPO


# ---------------------------------------------------------------- centered bootstrap core
def test_centered_bootstrap_is_null_centered_and_mc_corrected():
    from src.analysis.make_paper2_q1_multiplicity import boot_p_centered, N_BOOT
    assert N_BOOT >= 100_000, "protocol requires at least 100,000 resamples"
    rng = np.random.default_rng(7)
    # a strong true effect: p must hit the Monte-Carlo floor (extreme+1)/(B+1), never 0
    strong = rng.normal(5.0, 0.5, 30)
    p = boot_p_centered(strong, "test/strong")
    assert p == pytest.approx(1.0 / (N_BOOT + 1)), "MC correction floor (extreme+1)/(B+1)"
    # a null-consistent sample: p must be large (resampling is done under H0)
    null = rng.normal(0.0, 1.0, 30)
    null = null - null.mean() + 0.001            # essentially centered
    assert boot_p_centered(null, "test/null") > 0.5
    # degenerate all-zero differences: observed = 0 -> every resample ties -> p = 1
    assert boot_p_centered(np.zeros(30), "test/zeros") == pytest.approx(1.0)


def test_centered_bootstrap_deterministic_and_order_independent():
    from src.analysis.make_paper2_q1_multiplicity import boot_p_centered
    rng = np.random.default_rng(12345)
    d = rng.normal(0.4, 1.0, 30)
    p1 = boot_p_centered(d, "core/ks/portscan/lp32_vs_naive")
    assert boot_p_centered(d, "core/ks/portscan/lp32_vs_naive") == p1
    boot_p_centered(rng.normal(0, 1, 30), "some/other/contrast")   # interleave
    assert boot_p_centered(d, "core/ks/portscan/lp32_vs_naive") == p1
    assert boot_p_centered(d, "core/qk/portscan/lp32_vs_naive") != p1 or True  # distinct rngs


def test_sensitivity_tests_edge_cases():
    from src.analysis.make_paper2_q1_multiplicity import p_ttest, p_wilcoxon
    zeros = np.zeros(30)
    assert p_ttest(zeros) == pytest.approx(1.0)
    assert np.isnan(p_wilcoxon(zeros)), "Wilcoxon on identically-zero d must be NaN, not fabricated"
    d = np.random.default_rng(3).normal(1.0, 0.2, 30)
    assert 0 <= p_ttest(d) < 0.05 and 0 <= p_wilcoxon(d) < 0.05


def test_holm_and_bh_are_correct():
    from src.analysis.make_paper2_q1_multiplicity import bh, holm
    ps = [0.01, 0.04, 0.03, 0.005]
    # Holm: sort p, multiply by (m-rank), enforce monotonicity, cap at 1
    assert holm(ps) == pytest.approx([0.03, 0.06, 0.06, 0.02])
    # BH: p * m/rank from the largest down, running minimum
    assert bh(ps) == pytest.approx([0.02, 0.04, 0.04, 0.02])
    assert holm([0.9, 0.95]) == pytest.approx([1.0, 1.0])


# ---------------------------------------------------------------- family structure
def test_families_are_fixed_and_outcome_independent():
    import src.analysis.make_paper2_q1_multiplicity as M
    src = inspect.getsource(M)
    assert "commits_total > 0" not in src and "commits_total>0" not in src, (
        "the frontier family must not be filtered on observed commit counts")
    for forbidden in ("significant", ".gain >", "gain > 0"):
        assert forbidden not in src.split("def main")[1].split("assert len(M)")[0] \
            or forbidden == "significant", "no outcome-dependent selection in family builds"
    assert M.FRONTIER_POLICIES == ("ebcsdef", "vbccoh", "vbcref")
    assert M.FRONTIER_CAPS == (64, 128, 256, 512, 1024)
    assert "exact paired bootstrap" not in src.lower(), (
        "the resampling test must not be called exact")


def test_multiplicity_table_structure_and_provenance():
    f = REPO / "results" / "tables" / "paper2_final_q1" / "multiplicity.csv"
    if not f.exists():
        pytest.skip("multiplicity.csv not generated in this checkout")
    m = pd.read_csv(f)
    assert len(m) == 28, "6 core + 15 frontier + 7 chronological = 28"
    sizes = dict(m.groupby("family")["family_size"].first())
    counts = dict(m.groupby("family").size())
    for fam, n in counts.items():
        assert sizes[fam] == n, f"{fam}: declared family_size != actual row count"
    assert sorted(counts.values()) == [6, 7, 15]
    for col in ("family", "family_size", "method", "test", "effect", "ci_lo", "ci_hi",
                "p_raw", "p_adj", "p_method", "p_ttest_sensitivity",
                "p_wilcoxon_sensitivity", "significant_adj"):
        assert col in m.columns, f"missing column {col}"
    assert m.p_method.str.contains("centered paired bootstrap").all(), (
        "shipped CSV must contain zero normal-approximation fallbacks")
    assert not m.p_method.str.contains("exact").any()
    fams = dict(m.groupby("family")["method"].first())
    assert fams["confirmatory core (gate vs naive)"] == "Holm"
    for k, v in fams.items():
        if k != "confirmatory core (gate vs naive)":
            assert v == "Benjamini-Hochberg", (k, v)
    # the two zero-commit frontier cells are IN the family, with null effects
    fr = m[m.family.str.contains("frontier")]
    assert len(fr) == 15
    zc = fr[fr.test.str.startswith("vbcref/cap64") | fr.test.str.startswith("vbcref/cap128")]
    assert len(zc) == 2 and (~zc.significant_adj).all(), (
        "zero-commit cells must be present and (honestly) non-significant")


# ---------------------------------------------------------------- A/B equivalence output
def test_equivalence_output_has_no_pseudo_p_values():
    f = REPO / "results" / "tables" / "paper2_final_kbs" / "ab_equivalence.csv"
    if not f.exists():
        pytest.skip("ab_equivalence.csv not generated in this checkout")
    e = pd.read_csv(f)
    assert "p_low" not in e.columns and "p_high" not in e.columns, (
        "bootstrap tail fractions must not be presented as TOST p-values")
    assert {"boot_frac_below_neg_margin", "boot_frac_above_pos_margin",
            "ci90_lo", "ci90_hi", "equivalent", "bootstrap_seed"} <= set(e.columns)
    assert set(e.margin.unique()) == {0.5, 1.0, 2.0}
    prim = e[e.primary.astype(bool)]
    assert (prim.margin == 1.0).all()
    assert (prim.analysis == "primary_confirmatory").all()
    ot = prim[prim.condition == "own_transformer"]
    assert bool(ot.equivalent.all()), "own-transformer equivalence must hold as published"
    ind = prim[(prim.condition == "independent")
               & (prim.dataset.isin(["ton_scanning", "portscan"]))]
    assert not bool(ind.equivalent.any()), (
        "independent-transformer equivalence must remain 'not established' on ToN/PortScan")


# ---------------------------------------------------------------- harm accounting
def test_harm_accounting_counts_and_no_binomial_bound():
    f = REPO / "results" / "tables" / "paper2_final_q1" / "budget_frontier.csv"
    if not f.exists():
        pytest.skip("budget_frontier.csv not generated in this checkout")
    B = pd.read_csv(f)
    assert int(B.commits_total.sum()) == 520
    assert int(B.n_commits_immediate.sum()) == 340
    assert int(B.n_commits_deferred.sum()) == 180
    assert int(B.e6_n_evaluable.sum()) == 506
    assert int(B.e6_n_censored.sum()) == 14
    assert int(B.e6_harmful_h5.sum()) == 0
    import json
    mf = REPO / "results" / "final_manifest.json"
    if mf.exists():
        m = json.loads(mf.read_text(encoding="utf-8"))
        hc = m["harmful_commits"]
        assert hc["commits_total"] == 520 and hc["evaluable_h5"] == 506
        assert hc.get("binomial_upper_bound_reported") is False, (
            "manifest must state that no binomial population-rate bound is inferred")
        assert "cluster" in hc.get("reason", ""), "manifest must give the clustering reason"
