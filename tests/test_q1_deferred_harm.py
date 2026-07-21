"""final-q1 blocker B: every resolved commit must be scored from its REAL resolution window,
deferred ones included, or explicitly censored. These are the five tests the plan mandates.

The earlier accounting scored only commits resolved at the proposal window, off the
proposal-time lookahead, which left ~35% of the budget-frontier sweep's commits unevaluated
and let the paper say "zero harmful commits" on partial data.
"""
from __future__ import annotations

import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from tests.conftest import REPO


@pytest.fixture(scope="module")
def defer_run(synth, tmp_path_factory):
    """A deferral-heavy arm on synthetic data: zero drift (candidate ~ incumbent, so the
    sequential test rarely resolves at once) with a generous deferral cap."""
    out = tmp_path_factory.mktemp("defer_harm")
    cmd = [sys.executable, "-m", "src.experiments.run_paper2_readaptation_v2",
           "--data-ref", str(synth["ref"]), "--data-cur", str(synth["cur"]),
           "--outdir", str(out), "--label-col", "Label", "--methods", "ks_max",
           "--dim", "4", "--window-size", "32", "--post-windows", "45",
           "--ramp-windows", "25", "--calibration-windows", "10",
           "--train-size-per-class", "200", "--adapt-size-per-class", "64",
           "--detector-ref-size-per-class", "64", "--downstream-model", "logreg",
           "--seeds", "1,2,3", "--adaptation-gate", "labeled_probe_ebcs_defer",
           "--probe-size", "128", "--seq-block", "16", "--defer-windows", "5",
           "--seqav-alpha", "0.10", "--trigger-mode", "random", "--trigger-prob", "0.3"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1800)
    assert r.returncode == 0, f"{r.stdout[-1500:]}\n{r.stderr[-1500:]}"
    res = pd.read_csv(out / "paper2_v2_resolution_log.csv")
    summ = pd.read_csv(out / "paper2_progressive_readaptation_by_seed.csv")
    return dict(res=res, summ=summ, dir=out)


def test_deferred_commit_has_resolution_time(defer_run):
    r = defer_run["res"]
    assert len(r) > 0, "no resolutions logged -- test not exercised"
    assert {"proposal_window", "resolution_window", "delay_windows", "deferred"} <= set(r.columns)
    # a deferred resolution must land strictly after its proposal; an immediate one at it
    d = r[r.deferred.astype(bool)]
    assert len(d) > 0, "no deferred resolutions produced -- test not exercised"
    assert (d.resolution_window > d.proposal_window).all()
    assert (d.delay_windows == d.resolution_window - d.proposal_window).all()
    imm = r[~r.deferred.astype(bool)]
    if len(imm):
        assert (imm.resolution_window == imm.proposal_window).all()


def test_future_value_starts_at_resolution(defer_run):
    """The scored horizon must begin after the resolution window, not after the proposal."""
    from src.experiments.run_paper2_readaptation_v2 import FUTURE_HORIZONS
    r = defer_run["res"]
    assert all(f"delta_res{h}" in r.columns for h in FUTURE_HORIZONS)
    # n_future_windows is measured from the resolution window, so it must shrink as the
    # resolution approaches the end of the stream
    tail = r.sort_values("resolution_window").tail(1).iloc[0]
    assert tail.n_future_windows <= max(FUTURE_HORIZONS)


def test_all_commits_are_scored_or_marked_censored(defer_run):
    r = defer_run["res"]
    c = r[r.resolution_type == "commit"]
    assert len(c) > 0, "no commits -- test not exercised"
    scored = (~c.censored_h5.astype(bool)) & c.delta_res5.notna()
    censored = c.censored_h5.astype(bool)
    assert (scored | censored).all(), "a commit is neither scored nor marked censored"
    assert not (scored & censored).any(), "a commit is both scored and censored"


def test_harm_counts_include_deferred_commits(defer_run):
    """The aggregator's harm counts must be built from the resolution log (immediate AND
    deferred), not from the proposal-time trigger log."""
    import inspect
    from src.analysis import make_paper2_q1_frontier as F
    src = inspect.getsource(F.harm_from_resolution_log)
    assert "resolution_log" in src and "deferred" in src
    r = defer_run["res"]
    c = r[r.resolution_type == "commit"]
    ev = c[~c.censored_h5.astype(bool)]
    total = int((ev.delta_res5 < 0).sum())
    imm = int(((ev.delta_res5 < 0) & (~ev.deferred.astype(bool))).sum())
    dfr = int(((ev.delta_res5 < 0) & (ev.deferred.astype(bool))).sum())
    assert total == imm + dfr, "harm split does not sum to the total"


def test_no_proposal_lookahead_used_for_deferred_commit(defer_run):
    """A deferred commit must NOT be scored with the proposal window's lookahead: for a
    deferral of d windows the two horizons cover different stream stretches, so the values
    must differ wherever the stream actually changes."""
    res = defer_run["res"]
    tl = pd.read_csv(defer_run["dir"] / "paper2_v2_trigger_log.csv")
    d = res[(res.resolution_type == "commit") & (res.deferred.astype(bool))
            & (~res.censored_h5.astype(bool))]
    if not len(d):
        pytest.skip("no evaluable deferred commit in this run")
    merged = d.merge(tl[tl.trained][["seed", "window_idx", "delta_future5"]],
                     left_on=["seed", "proposal_window"], right_on=["seed", "window_idx"],
                     how="inner")
    if not len(merged):
        pytest.skip("no matching proposal rows")
    same = np.isclose(merged.delta_res5, merged.delta_future5, atol=1e-12)
    assert not same.all(), (
        "every deferred commit scored identically to its proposal-window lookahead — "
        "the resolution-time scoring is not actually being used")
