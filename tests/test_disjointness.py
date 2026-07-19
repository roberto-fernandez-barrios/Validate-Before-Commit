"""P10 mandatory tests: sampling disjointness invariants.

test_symmetric_ab_disjoint     -- the A/B mechanism control's T/M1/M2/E blocks share no row.
test_global_stream_disjoint    -- --stream-disjoint-windows: no row appears in two stream windows.
test_probe_candidate_disjoint  -- observed probe excludes candidate-training rows (0 collisions
                                  under the disjoint stream).
test_candidate_future_disjoint -- candidate-training rows never recur in future eval windows.
test_no_probe_never_commits    -- --no-probe-policy reject: early triggers without a probe never commit.
"""
from __future__ import annotations

import argparse

import numpy as np


def test_symmetric_ab_disjoint(synth, monkeypatch):
    import src.analysis.paper2_symmetric_ab_final as ab

    # (a) explicit T/M1/M2/E disjointness using the module's own dedup + partition scheme
    pools = ab.unique_class_pools(str(synth["ref"]))
    n = min(2000, min(len(pools[0]), len(pools[1])) // 4)
    assert n > 0
    for seed in (104, 105):
        rng = np.random.default_rng(seed)
        for cls in (0, 1):
            perm = rng.permutation(len(pools[cls]))
            blocks = [pools[cls][perm[i * n:(i + 1) * n]] for i in range(4)]
            sets = [{r.tobytes() for r in np.ascontiguousarray(b)} for b in blocks]
            for i in range(4):
                for j in range(i + 1, 4):
                    assert not (sets[i] & sets[j]), f"blocks {i}/{j} overlap (seed {seed}, class {cls})"

    # (b) the script's own path (its internal asserts run) on two seeds
    monkeypatch.setattr(ab, "SEEDS", range(104, 106))
    monkeypatch.setattr(ab, "DIM", 4)   # synthetic data has 5 features; PCA dim must fit
    rows = ab.one_dataset("synthetic", str(synth["ref"]), "svc_rbf")
    assert rows and all(r["n_per_block"] == n for r in rows)


def _disjoint_env(synth, seed=1):
    from src.experiments.run_paper2_progressive_readaptation import load_binary_dataset, make_pools
    from src.experiments.run_paper2_readaptation_v2 import build_environment

    X_ref, y_ref = load_binary_dataset(synth["ref"], "Label")
    X_cur, y_cur = load_binary_dataset(synth["cur"], "Label")
    common = sorted(set(X_ref.columns) & set(X_cur.columns))
    pools = make_pools(X_ref, y_ref, X_cur, y_cur, common)
    args = argparse.Namespace(
        stream_disjoint_windows=True, disjoint_window_frac=0.5,
        train_size_per_class=200, dim=4, adaptation_gate="none",
        adapt_strategy="full_replace", downstream_model="logreg",
        stream_prevalence=0.5, window_size=32, post_windows=40,
        ramp_windows=20, max_severity=1.0)
    return build_environment(pools, args, seed)


def test_global_stream_disjoint(synth):
    env = _disjoint_env(synth)
    seen: set[bytes] = set()
    for Xw, _, _ in env.stream:
        for r in np.ascontiguousarray(Xw):
            h = r.tobytes()
            assert h not in seen, "row appears in two stream windows under --stream-disjoint-windows"
            seen.add(h)
    assert len(seen) == sum(len(Xw) for Xw, _, _ in env.stream)


def test_probe_candidate_disjoint(causal_by_seed):
    arm = causal_by_seed[causal_by_seed.method == "ks_max"]
    assert len(arm) > 0
    assert int(arm.n_probes.sum()) > 0, "no probes drawn -- test not exercised"
    assert int(arm.probe_row_collisions.sum()) == 0


def test_candidate_future_disjoint(causal_by_seed):
    arm = causal_by_seed[causal_by_seed.method == "ks_max"]
    assert int(arm.cand_future_collisions.sum()) == 0


def test_no_probe_never_commits(causal_by_seed):
    arm = causal_by_seed[causal_by_seed.method == "ks_max"]
    assert int(arm.n_no_probe.sum()) > 0, "no early no-probe trigger occurred -- test not exercised"
    assert int(arm.n_commit_no_probe.sum()) == 0
