"""q1-final-patch Block A: production temporal semantics of deferred commits.

A commit resolved in window t (immediate OR deferred) enters service at t+1. No decision
may retroactively rewrite window t's served performance, predictions, detector score, or
per-window logs. The bug these tests pin: the pending (deferred) block ran at the START of a
window and swapped `model`/`detector` BEFORE that window was served, so a deferred commit
retroactively "served" the very window whose arrival resolved it -- unlike immediate commits,
which serve from t+1.

The invariant is checked structurally through a per-window `served_model_version`: a monotone
counter of DEPLOYED models, captured at each window's serving point. A commit resolved at
window r must NOT be reflected in served_model_version[r] (it is at r+1). These tests FAIL on
the pre-reorder loop (deferred commits inflate served_model_version[r]) and PASS after it.
"""
from __future__ import annotations

import inspect
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from tests.conftest import REPO


@pytest.fixture(scope="module")
def temporal_run(synth, tmp_path_factory):
    """A defer-capable pooled EB-CS arm on RAMPING synthetic drift. Early (low-severity) probes
    are near-ties that defer; later (high-severity) probes resolve immediately. Both immediate
    and deferred commits therefore appear in the same run -- exactly what the symmetry and
    non-retroactivity tests need."""
    out = tmp_path_factory.mktemp("temporal")
    cmd = [sys.executable, "-m", "src.experiments.run_paper2_readaptation_v2",
           "--data-ref", str(synth["ref"]), "--data-cur", str(synth["cur"]),
           "--outdir", str(out), "--label-col", "Label", "--methods", "ks_max",
           "--dim", "4", "--window-size", "32", "--post-windows", "60",
           "--ramp-windows", "30", "--calibration-windows", "10",
           "--train-size-per-class", "200", "--adapt-size-per-class", "64",
           "--detector-ref-size-per-class", "64", "--downstream-model", "logreg",
           "--seeds", "1,2,3,4,5,6", "--adaptation-gate", "labeled_probe_ebcs_defer",
           "--probe-size", "256", "--seq-block", "16", "--defer-windows", "5",
           "--seqav-alpha", "0.10", "--lifetime-alpha", "0.10",
           "--trigger-mode", "random", "--trigger-prob", "0.3"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1800)
    assert r.returncode == 0, f"{r.stdout[-1500:]}\n{r.stderr[-1500:]}"
    win = pd.read_csv(out / "paper2_progressive_readaptation_window_results.csv")
    res = pd.read_csv(out / "paper2_v2_resolution_log.csv")
    return dict(win=win, res=res, dir=out)


def _served_vs_commits(win: pd.DataFrame, res: pd.DataFrame):
    """For every (seed, window) yield (served_version, expected_version) where expected is the
    number of commits that RESOLVED strictly before that window (i.e. take effect at r+1)."""
    w = win[win.method == "ks_max"]
    commits = res[res.resolution_type == "commit"]
    for seed, g in w.groupby("seed"):
        g = g.sort_values("window_idx")
        res_windows = np.sort(commits[commits.seed == seed].resolution_window.to_numpy())
        for _, row in g.iterrows():
            expected = int((res_windows < row.window_idx).sum())
            yield seed, int(row.window_idx), int(row.served_model_version), expected


def test_T1_no_retroactivity(temporal_run):
    """The model serving window t excludes any commit resolved at t: served_model_version[t]
    equals the number of commits resolved strictly before t. A deferred commit resolved at t
    therefore cannot have served (nor rewritten the balanced accuracy / predictions of) t."""
    win, res = temporal_run["win"], temporal_run["res"]
    assert "served_model_version" in win.columns
    bad = [(s, w, sv, ev) for s, w, sv, ev in _served_vs_commits(win, res) if sv != ev]
    assert not bad, ("served model version disagrees with the commit timeline at "
                     f"{bad[:5]} (served != expected) -- a commit rewrote its own window")


def test_T2_immediate_deferred_symmetry(temporal_run):
    """Both an immediate and a deferred commit resolved at r begin serving at r+1: the served
    version strictly increases from r to r+1 for every commit, regardless of `deferred`."""
    win, res = temporal_run["win"], temporal_run["res"]
    c = res[res.resolution_type == "commit"]
    assert (c.deferred.astype(bool)).any(), "no deferred commit -- symmetry not exercised"
    assert (~c.deferred.astype(bool)).any(), "no immediate commit -- symmetry not exercised"
    w = win[win.method == "ks_max"]
    for _, row in c.iterrows():
        seed, r = row.seed, int(row.resolution_window)
        g = w[w.seed == seed].set_index("window_idx")["served_model_version"]
        if r not in g.index or (r + 1) not in g.index:
            continue                       # resolved at the last window: nothing serves r+1
        assert g.loc[r + 1] > g.loc[r], (
            f"commit (deferred={bool(row.deferred)}) at window {r} did not begin serving at "
            f"{r + 1}: version {int(g.loc[r])} -> {int(g.loc[r + 1])}")


def test_T3_detector_score_precedes_resolution():
    """Structural guard: in the per-window loop the detector SCORE of the window is computed
    before any pending-resolution block can rebuild the detector, so W_t's score/alarm use the
    detector in force at the start of t, not the post-commit one."""
    from src.experiments import run_paper2_readaptation_v2 as R
    src = inspect.getsource(R.run_arm)
    body = src[src.index("for t, (Xw, yw, sev) in enumerate(env.stream):"):]
    i_score = body.index("score = float(detector.score(Xw))")
    i_pending = body.index("if pending is not None:")
    i_rebuild = body.index("detector = build_detector(method, args, seed + t + 1)")
    assert i_score < i_pending < i_rebuild, (
        "the window's detector score must be computed BEFORE the pending-resolution block "
        "rebuilds the detector (found score@%d, pending@%d, rebuild@%d)"
        % (i_score, i_pending, i_rebuild))


def test_T4_resolution_horizon_starts_after_resolution(temporal_run):
    """delta_resH is measured from resolution_window+1: n_future_windows equals the number of
    windows strictly after the resolution, capped at the max horizon -- it never includes W_t."""
    from src.experiments.run_paper2_readaptation_v2 import FUTURE_HORIZONS
    res = temporal_run["res"]
    n_windows = int(temporal_run["win"].window_idx.max()) + 1
    maxH = max(FUTURE_HORIZONS)
    for _, row in res.iterrows():
        avail = max(0, n_windows - 1 - int(row.resolution_window))
        assert int(row.n_future_windows) == min(maxH, avail)
        for h in FUTURE_HORIZONS:
            assert bool(row[f"censored_h{h}"]) == (int(row.n_future_windows) < h)


def test_T5_deferred_changes_future_not_resolution_window(temporal_run):
    """A deferred decision may change the future trajectory but must never rewrite its own
    resolution window: the served-version invariant holds even on the deferred subset, and a
    deferred commit's model is absent from its resolution window yet present just after."""
    win, res = temporal_run["win"], temporal_run["res"]
    dc = res[(res.resolution_type == "commit") & (res.deferred.astype(bool))]
    assert len(dc) > 0
    w = win[win.method == "ks_max"]
    for _, row in dc.iterrows():
        seed, r = row.seed, int(row.resolution_window)
        g = w[w.seed == seed].set_index("window_idx")["served_model_version"]
        before = int((np.sort(res[(res.seed == seed) & (res.resolution_type == "commit")]
                              .resolution_window.to_numpy()) < r).sum())
        assert int(g.loc[r]) == before, "deferred commit rewrote its own resolution window"


def test_T6_end_of_stream_censoring(temporal_run):
    """Commits resolved near the end of the stream censor exactly the horizons that run past
    the stream, and a censored horizon has no delta while an evaluable one does."""
    from src.experiments.run_paper2_readaptation_v2 import FUTURE_HORIZONS
    res = temporal_run["res"]
    c = res[res.resolution_type == "commit"]
    for _, row in c.iterrows():
        for h in FUTURE_HORIZONS:
            if bool(row[f"censored_h{h}"]):
                assert pd.isna(row[f"delta_res{h}"]), "censored horizon has a delta"
            else:
                assert not pd.isna(row[f"delta_res{h}"]), "evaluable horizon has no delta"
