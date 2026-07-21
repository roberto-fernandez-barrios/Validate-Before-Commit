"""final-q1 mandatory tests (protocol q1_max_protocol.md): defer-mode semantics, the D1
weak-null e-process validity, candidate-latency semantics, and the pending-candidate policy.

The e2e fixtures run vbc_sg on ZERO-DRIFT synthetic data (ref == cur) with a strictly
increasing severity ramp (ramp > post-windows), so (a) candidate ~ incumbent -> the initial
probe is almost always undecided -> deferrals are guaranteed, and (b) the numeric severity
differs at every window, which lets the sev0-counter discriminate cohort from accumulate.
"""
from __future__ import annotations

import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from src.experiments.run_paper2_readaptation_v2 import cs_lower_bound_eb

from tests.conftest import REPO

ALPHA = 0.10


def _run_vbc(synth, outdir, extra):
    cmd = [sys.executable, "-m", "src.experiments.run_paper2_readaptation_v2",
           "--data-ref", str(synth["ref"]), "--data-cur", str(synth["ref"]),  # zero drift
           "--outdir", str(outdir), "--label-col", "Label", "--methods", "ks_max",
           "--dim", "4", "--window-size", "32", "--post-windows", "40",
           "--ramp-windows", "60",              # strictly increasing severity, no plateau
           "--calibration-windows", "10", "--train-size-per-class", "200",
           "--adapt-size-per-class", "64", "--detector-ref-size-per-class", "64",
           "--downstream-model", "logreg", "--seeds", "1,2",
           "--adaptation-gate", "vbc_sg", "--probe-size", "32", "--seq-block", "8",
           "--defer-windows", "3", "--trigger-mode", "random", "--trigger-prob", "0.5"] + extra
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1200)
    assert r.returncode == 0, f"vbc arm failed:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}"
    return pd.read_csv(outdir / "paper2_progressive_readaptation_by_seed.csv")


@pytest.fixture(scope="session")
def defer_modes(synth, tmp_path_factory):
    out = {}
    for mode in ("accumulate", "cohort", "refresh"):
        d = tmp_path_factory.mktemp(f"defer_{mode}")
        s = _run_vbc(synth, d, ["--vbc-defer-mode", mode])
        out[mode] = s[s.method == "ks_max"]
    return out


def test_defer_does_not_mix_targets(defer_modes):
    coh = defer_modes["cohort"]
    assert int(coh.n_defer_continuations.sum()) > 0, "no deferral occurred -- not exercised"
    # cohort: every continuation draw comes from the proposal-time mixture
    assert int(coh.n_defer_continuations.sum()) == int(coh.n_defer_draws_at_sev0.sum())
    # accumulate: continuation draws follow the CURRENT window (severity strictly increasing,
    # so none can equal the proposal-time value)
    acc = defer_modes["accumulate"]
    assert int(acc.n_defer_continuations.sum()) > 0
    assert int(acc.n_defer_draws_at_sev0.sum()) == 0


def test_refresh_cs_restarts(defer_modes):
    ref = defer_modes["refresh"]
    assert int(ref.n_defer_continuations.sum()) > 0, "no deferral occurred -- not exercised"
    # refresh: the evidence set never exceeds one continuation block
    assert int(ref.defer_evidence_max.max()) <= 8
    # accumulate: the same sequence keeps the initial probe and grows past it
    assert int(defer_modes["accumulate"].defer_evidence_max.max()) >= 32 + 8


def test_pending_candidate_policy(synth, tmp_path_factory):
    # defer cap ABOVE the cooldown: without the registered pending-blocks-proposals rule the
    # runner would open overlapping proposals; with it, proposal count stays bounded by the
    # pending span. (defer 15 + cooldown 2 over 40 windows -> at most ~4 proposals/stream.)
    d = tmp_path_factory.mktemp("pending_policy")
    s = _run_vbc(synth, d, ["--vbc-defer-mode", "accumulate", "--defer-windows", "15",
                            "--cooldown-windows", "2", "--trigger-prob", "0.9"])
    assert int(s.n_defer_continuations.sum()) > 0
    assert (s.n_triggers <= 6).all(), f"pending did not block new proposals: {s.n_triggers.tolist()}"


def _strat_commit(d_by_class, alpha):
    lbs = [cs_lower_bound_eb(np.asarray(d_by_class[c]), alpha / 4.0) for c in (0, 1)]
    return 0.5 * (lbs[0] + lbs[1]) > 0.0


def test_weak_null_drifting_means():
    """D1(iv): accumulate-mode e-process false-commit <= alpha under TIME-VARYING conditional
    means (all <= 0; oscillating and trending) and time-varying variances (tie probability
    changes across blocks). Evaluation cadence mirrors the gate: initial 16/class, then up to
    3 continuation blocks of 4/class, tested after each block."""
    rng = np.random.default_rng(11)
    n_props, commits = 1500, 0
    for _ in range(n_props):
        d = {0: [], 1: []}
        committed = False
        # per-block (mean, tie_p) schedules: means oscillate/trend but never exceed 0
        schedules = [(0.0, 0.6), (-0.3, 0.2), (-0.1, 0.9), (0.0, 0.3)]
        for b, (mu, tie) in enumerate(schedules):
            n_cls = 16 if b == 0 else 4
            p_plus = max(0.0, (1 - tie) / 2 + mu / 2)
            p_minus = max(0.0, (1 - tie) / 2 - mu / 2)
            probs = np.array([p_minus, tie, p_plus]); probs /= probs.sum()
            for c in (0, 1):
                d[c].extend(rng.choice([-1, 0, 1], size=n_cls, p=probs).tolist())
            if _strat_commit(d, ALPHA):
                committed = True
                break
        commits += int(committed)
    rate = commits / n_props
    bound = ALPHA + 3 * np.sqrt(ALPHA * (1 - ALPHA) / n_props)
    assert rate <= bound, f"weak-null false-commit {rate:.4f} > {bound:.4f}"


def test_cohort_cs_validity():
    """Cohort variant: all evidence from ONE fixed null distribution, sequential looks."""
    rng = np.random.default_rng(12)
    n_props, commits = 1500, 0
    for _ in range(n_props):
        d = {c: rng.choice([-1, 0, 1], size=28, p=[0.2, 0.6, 0.2]) for c in (0, 1)}
        if any(_strat_commit({c: d[c][:n] for c in (0, 1)}, ALPHA) for n in (16, 20, 24, 28)):
            commits += 1
    rate = commits / n_props
    assert rate <= ALPHA + 3 * np.sqrt(ALPHA * (1 - ALPHA) / n_props)


def test_candidate_latency_semantics(synth, tmp_path_factory):
    d = tmp_path_factory.mktemp("cand_latency")
    cmd = [sys.executable, "-m", "src.experiments.run_paper2_readaptation_v2",
           "--data-ref", str(synth["ref"]), "--data-cur", str(synth["cur"]),
           "--outdir", str(d), "--label-col", "Label", "--methods", "ks_max",
           "--dim", "4", "--window-size", "32", "--post-windows", "40",
           "--ramp-windows", "20", "--calibration-windows", "10",
           "--train-size-per-class", "200", "--adapt-size-per-class", "64",
           "--detector-ref-size-per-class", "64", "--downstream-model", "logreg",
           "--seeds", "1", "--adaptation-gate", "labeled_probe", "--probe-size", "16",
           "--candidate-latency", "5", "--trigger-mode", "random", "--trigger-prob", "0.35"]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1200)
    assert r.returncode == 0, r.stderr[-1500:]
    log = pd.read_csv(d / "paper2_v2_trigger_log.csv")
    trained = log[log.trained]
    assert len(trained) > 0
    assert (trained.cand_latency == 5).all()
    # full_replace: the candidate batch reflects the mixture of window t-5, and under a ramp
    # its severity is strictly below the current window's
    assert (trained.cand_newest_window == (trained.window_idx - 5).clip(lower=0)).all()
    ramping = trained[trained.window_idx < 20]
    if len(ramping):
        assert (ramping.cand_sev_used < ramping.severity_t).all()


def test_ab_equivalence_margin():
    # q1-final-patch Block E: renamed from tost() -- the rule is a bootstrap CI-based
    # equivalence assessment (90% CI inside the margin, the interval-inclusion form of TOST)
    from src.analysis.paper2_ab_equivalence import equivalence_ci
    rng = np.random.default_rng(5)
    tight = rng.normal(0.02, 0.4, size=100)      # near-zero, tight -> equivalent at 1.0
    assert equivalence_ci(tight, 1.0)["equivalent"]
    wide = rng.normal(0.0, 15.0, size=100)       # zero mean, huge SD -> NOT equivalent
    assert not equivalence_ci(wide, 1.0)["equivalent"]
    shifted = rng.normal(2.5, 0.4, size=100)     # materially nonzero -> NOT equivalent
    assert not equivalence_ci(shifted, 1.0)["equivalent"]
