"""P10 mandatory tests: statistical validity of the risk gates and the lifetime budget.

test_stratified_gate_type      -- null simulation: the stratified EB-CS commit rule's
                                  false-commit rate stays below its nominal alpha, at several
                                  tie ratios, under sequential looks (the sampling the gate uses).
test_lifetime_alpha_budget     -- the p-series spending schedule allocates alpha_j = 6a/(pi^2 j^2)
                                  per proposal and never spends more than the lifetime budget.
test_effective_alpha_manifest  -- the effective per-proposal alpha is recorded in the run
                                  trigger log, and results/final_manifest.json records the
                                  alpha/spending configuration of the final arms.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from src.experiments.run_paper2_readaptation_v2 import cs_lower_bound, cs_lower_bound_eb

from tests.conftest import REPO

ALPHA = 0.10
LOOKS = (8, 16, 24, 32)          # per-class sequential looks (blocks of 8 up to 32)


def _null_rate(tie_p: float, n_props: int, mean_shift: float, seed: int) -> float:
    """Fraction of proposals where the stratified rule commits.

    Per class: d_i in {-1,0,1}, P(+1)=p+shift, P(-1)=p-... constructed so E[d]=mean_shift.
    Commit iff 0.5*(LCB_ben + LCB_att) > 0 at any look (each class at ALPHA/2) -- exactly
    the labeled_probe_ebcs_strat composition.
    """
    rng = np.random.default_rng(seed)
    p_plus = (1.0 - tie_p) / 2.0 + mean_shift / 2.0
    p_minus = (1.0 - tie_p) / 2.0 - mean_shift / 2.0
    assert p_plus >= 0 and p_minus >= 0
    commits = 0
    for _ in range(n_props):
        d = {c: rng.choice([-1, 0, 1], size=max(LOOKS),
                           p=[p_minus, tie_p, p_plus]) for c in (0, 1)}
        for n in LOOKS:
            lcb = [cs_lower_bound_eb(d[c][:n], ALPHA / 2.0) for c in (0, 1)]
            if 0.5 * (lcb[0] + lcb[1]) > 0.0:
                commits += 1
                break
    return commits / n_props


@pytest.mark.parametrize("tie_p", [0.2, 0.6, 0.9])
def test_stratified_gate_type(tie_p):
    n = 2000
    rate = _null_rate(tie_p, n, mean_shift=0.0, seed=int(tie_p * 100))
    bound = ALPHA + 3.0 * np.sqrt(ALPHA * (1 - ALPHA) / n)
    assert rate <= bound, f"stratified EB-CS false-commit rate {rate:.4f} > {bound:.4f} at ties={tie_p}"


def test_stratified_gate_has_power_and_robbins_is_valid():
    # sanity: a real per-class improvement is detected far above the null rate (the EB-CS is
    # deliberately conservative at 32 samples/class -- what we check is power >> alpha, and
    # near-certain detection under a strong effect)
    rate_mid = _null_rate(0.6, 400, mean_shift=0.35, seed=42)
    assert rate_mid > 3 * ALPHA, f"no usable power under a moderate effect (rate={rate_mid:.2f})"
    rate_strong = _null_rate(0.3, 400, mean_shift=0.6, seed=43)
    assert rate_strong > 0.7, f"weak detection of a strong effect (rate={rate_strong:.2f})"
    # and the Robbins normal-mixture CS is also alpha-valid on the same null
    rng = np.random.default_rng(3)
    n_props, commits = 2000, 0
    for _ in range(n_props):
        d = rng.choice([-1, 0, 1], size=64, p=[0.2, 0.6, 0.2])
        if any(cs_lower_bound(d[:n], ALPHA, rho2=0.1) > 0 for n in (16, 32, 48, 64)):
            commits += 1
    assert commits / n_props <= ALPHA + 3.0 * np.sqrt(ALPHA * (1 - ALPHA) / n_props)


def test_lifetime_alpha_budget(vbc_trigger_log):
    log = vbc_trigger_log[vbc_trigger_log.trained]
    assert len(log) > 0, "no proposals were trained -- test not exercised"
    a_life = 0.10
    for seed, g in log.groupby("seed"):
        per_prop = g.drop_duplicates("proposal_idx")[["proposal_idx", "alpha_allocated"]]
        assert (per_prop.proposal_idx >= 1).all()
        expected = a_life * 6.0 / (np.pi ** 2 * per_prop.proposal_idx.to_numpy() ** 2)
        np.testing.assert_allclose(per_prop.alpha_allocated.to_numpy(), expected, atol=2e-6)
        assert per_prop.alpha_allocated.sum() <= a_life + 1e-9, f"seed {seed} overspent the budget"


def test_effective_alpha_manifest(vbc_trigger_log, tmp_path):
    # (a) the run log records the effective alpha of every proposal
    assert {"proposal_idx", "alpha_allocated"} <= set(vbc_trigger_log.columns)
    assert vbc_trigger_log.alpha_allocated.between(0, 1).all()
    # (b) the final manifest records the risk configuration of the final arms.
    # Written to tmp_path: the test exercises the generator WITHOUT mutating the
    # sealed results/final_manifest.json (see test_manifest_generator_does_not_mutate_sealed).
    from src.analysis import make_final_manifest
    sealed = (REPO / "results" / "final_manifest.json").read_bytes()
    make_final_manifest.main(out=tmp_path / "final_manifest.json")
    assert (REPO / "results" / "final_manifest.json").read_bytes() == sealed, (
        "running the manifest generator in tests must NOT touch the sealed manifest")
    m = json.loads((tmp_path / "final_manifest.json").read_text(encoding="utf-8"))
    risk = m["risk_control"]
    assert risk["per_proposal_alpha_cs"] == 0.10
    assert risk["mcnemar_alpha"] == 0.05
    assert set(risk["alpha_spending_schedules"]) == {"bonferroni", "pseries"}
    assert risk["lifetime_alpha"] == 0.10
    for key in ("source_commit_sha", "manifest_schema_version", "generated_at_utc",
                "artifact_version", "datasets", "seeds", "window_sizes",
                "prevalences", "label_latencies", "models", "generators", "gates",
                "collision_counts", "outputs", "audit"):
        assert key in m, f"final_manifest.json missing field {key}"
    # the legacy circular-reference field must not come back
    assert "commit_sha" not in m, "commit_sha renamed to source_commit_sha (no self-reference)"


def test_manifest_generator_does_not_mutate_sealed(tmp_path):
    """Symmetric-pipeline confirmatory phase fix: the sealed results/final_manifest.json is a
    version-controlled artifact; exercising the generator (as this suite does) must leave the
    working tree untouched -- git must report the file unmodified afterwards."""
    import subprocess
    from src.analysis import make_final_manifest
    sealed = (REPO / "results" / "final_manifest.json").read_bytes()
    make_final_manifest.main(out=tmp_path / "m.json")
    assert (tmp_path / "m.json").exists()
    assert (REPO / "results" / "final_manifest.json").read_bytes() == sealed
    r = subprocess.run(["git", "status", "--porcelain", "results/final_manifest.json"],
                       cwd=REPO, capture_output=True, text=True, timeout=60)
    assert r.stdout.strip() == "", f"sealed manifest modified in working tree: {r.stdout}"
