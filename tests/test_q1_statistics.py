"""q1-final-patch Block E: exact reproducibility of the statistical machinery.

The multiplicity table's p-values are deterministic seed-level paired bootstraps (per-contrast
RNG derived from the contrast label, order-independent), and the A/B equivalence output is a
bootstrap CI-based assessment whose tail-fraction diagnostics are no longer named p-values.
These tests pin both facts so they cannot silently regress.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pytest

from tests.conftest import REPO


def test_boot_p_exact_deterministic_and_order_independent():
    from src.analysis.make_paper2_q1_multiplicity import boot_p_exact, N_BOOT
    rng = np.random.default_rng(12345)
    d = rng.normal(0.4, 1.0, 30)
    p1 = boot_p_exact(d, "core/ks/portscan/lp32_vs_naive")
    p2 = boot_p_exact(d, "core/ks/portscan/lp32_vs_naive")
    assert p1 == p2, "same data + same label must give the identical p-value"
    # interleaving other contrasts must not perturb a label's p (order independence)
    boot_p_exact(rng.normal(0, 1, 30), "some/other/contrast")
    assert boot_p_exact(d, "core/ks/portscan/lp32_vs_naive") == p1
    # different labels draw different resamples (no accidental seed collision to a constant)
    p3 = boot_p_exact(d, "core/qk/portscan/lp32_vs_naive")
    assert 1.0 / N_BOOT <= p1 <= 1.0 and 1.0 / N_BOOT <= p3 <= 1.0
    # floored, two-sided
    big = np.full(30, 5.0)
    assert boot_p_exact(big, "sure/thing") == pytest.approx(1.0 / N_BOOT)


def test_multiplicity_table_declares_p_provenance():
    f = REPO / "results" / "tables" / "paper2_final_q1" / "multiplicity.csv"
    if not f.exists():
        pytest.skip("multiplicity.csv not generated in this checkout")
    m = pd.read_csv(f)
    assert "p_method" in m.columns, "each row must declare its p-value provenance"
    assert m.p_method.notna().all()
    ok = m.p_method.str.contains("exact paired bootstrap") | \
        m.p_method.str.contains("normal-approximation inversion")
    assert ok.all(), "p_method must be one of the two declared provenances"
    # the three families keep their registered correction methods
    fams = dict(m.groupby("family")["method"].first())
    assert fams.get("confirmatory core (gate vs naive)") == "Holm"
    for k, v in fams.items():
        if k != "confirmatory core (gate vs naive)":
            assert v == "Benjamini-Hochberg", (k, v)


def test_equivalence_output_has_no_pseudo_p_values():
    f = REPO / "results" / "tables" / "paper2_final_kbs" / "ab_equivalence.csv"
    if not f.exists():
        pytest.skip("ab_equivalence.csv not generated in this checkout")
    e = pd.read_csv(f)
    assert "p_low" not in e.columns and "p_high" not in e.columns, (
        "bootstrap tail fractions must not be presented as TOST p-values")
    assert {"boot_frac_below_neg_margin", "boot_frac_above_pos_margin",
            "ci90_lo", "ci90_hi", "equivalent", "bootstrap_seed"} <= set(e.columns)
    # registered design intact: primary margin 1.0 on confirmatory seeds, sensitivities kept
    assert set(e.margin.unique()) == {0.5, 1.0, 2.0}
    prim = e[e.primary.astype(bool)]
    assert (prim.margin == 1.0).all()
    assert (prim.analysis == "primary_confirmatory").all()
    # verdicts are the published ones: own_transformer equivalent on all three benchmarks;
    # independent-transformer not established on the two high-variance SVC benchmarks
    ot = prim[prim.condition == "own_transformer"]
    assert bool(ot.equivalent.all()), "own-transformer equivalence must hold as published"
    ind = prim[(prim.condition == "independent")
               & (prim.dataset.isin(["ton_scanning", "portscan"]))]
    assert not bool(ind.equivalent.any()), (
        "independent-transformer equivalence must remain 'not established' on ToN/PortScan")
