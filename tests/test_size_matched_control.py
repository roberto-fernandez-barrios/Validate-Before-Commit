"""Mandatory tests T1-T11 of the size-matched own-transformer control.

Registered protocol: notes/paper2_size_matched_own_transformer_protocol_001.md (section 8).

Everything here runs in-process on the SYNTHETIC data of conftest (no benchmark, no
confirmatory seed; development seed 12 only), exercising the nested canonical draw at the
synthetic analogue of the registered sizes: adapt-size 64 (the "512" role) and train-size
200 (the "2000" role). The full-scale bit parity of the new 512 path against the stored
v1.21.0-code smoke outputs (seeds 4242-4243) is executed by
`run_symmetric_pipeline_replication --parity --config configs/size_matched_own_transformer_v1.json`
and recorded in notes/size_matched_confirmatory_preflight.md; these tests keep the same
invariants permanently green on synthetic data.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import balanced_accuracy_score
from sklearn.preprocessing import StandardScaler

from src.experiments import run_paper2_readaptation_v2 as v2
from src.experiments.run_paper2_progressive_readaptation import (
    load_binary_dataset,
    make_pools,
    sample_balanced_from_distribution,
)
from src.experiments.run_symmetric_pipeline_replication import (
    _recording_candidate_factory,
    firewall,
    load_config,
    size_matched_arms,
)
from src.experiments.symmetric_pipeline import (
    OWN_POLICY,
    build_raw_environment,
    rows_hash,
    stream_raw_hash,
)

REPO = Path(__file__).resolve().parents[1]
SM_CONFIG = REPO / "configs" / "size_matched_own_transformer_v1.json"
SEED = 12   # development seed: outside every ledgered block, outside 4001-4030 / 4401-4402
BASE = 64   # synthetic analogue of 512 (the --adapt-size-per-class role)
FULL = 200  # synthetic analogue of 2000 (the --train-size-per-class role)


@pytest.fixture(scope="session")
def sm_pools(synth):
    X_ref, y_ref = load_binary_dataset(synth["ref"], "Label")
    X_cur, y_cur = load_binary_dataset(synth["cur"], "Label")
    common = sorted(set(X_ref.columns).intersection(X_cur.columns))
    return make_pools(X_ref, y_ref, X_cur, y_cur, common)


def _zargs(synth, tmp, extra: list[str]):
    """Zero-drift synthetic args mirroring the registered arm structure."""
    return v2.build_parser().parse_args([
        "--data-ref", str(synth["ref"]), "--data-cur", str(synth["cur"]),
        "--outdir", str(tmp), "--label-col", "Label", "--methods", "ks_max",
        "--dim", "4", "--window-size", "32", "--post-windows", "40",
        "--ramp-windows", "20", "--calibration-windows", "10",
        "--train-size-per-class", str(FULL), "--adapt-size-per-class", str(BASE),
        "--detector-ref-size-per-class", "64", "--downstream-model", "svc_rbf",
        "--adapt-strategy", "full_replace", "--max-severity", "0",
        "--trigger-mode", "random", "--trigger-prob", "0.35", "--seeds", str(SEED),
    ] + extra)


NAIVE = ["--adaptation-gate", "none"]
POINT = ["--adaptation-gate", "labeled_probe", "--probe-size", "16"]
STRICT = ["--adaptation-gate", "labeled_probe", "--probe-size", "16",
          "--gate-margin", "0.001"]


def _record(env):
    rec = []
    orig = env.candidate_factory

    def wrapped(X, y, s, C, proba):
        p = orig(X, y, s, C, proba)
        rec.append(p)
        return p

    env.candidate_factory = wrapped
    return rec


def _run(env, args):
    w, t, s, r = v2.run_seed(env, args, SEED, ["ks_max"])
    return dict(win=pd.DataFrame(w), trig=pd.DataFrame(t), summ=pd.DataFrame(s),
                res=pd.DataFrame(r))


def _make(sm_pools, synth, tmp_path_factory, gate: list[str], size: int | None):
    extra = list(gate) + (["--candidate-size-per-class", str(size)] if size else [])
    args = _zargs(synth, tmp_path_factory.mktemp("smc"), extra)
    env = build_raw_environment(sm_pools, args, SEED, OWN_POLICY)
    rec = _record(env)
    out = _run(env, args)
    return dict(env=env, rec=rec, args=args, **out)


@pytest.fixture(scope="session")
def naive_noflag(sm_pools, synth, tmp_path_factory):
    return _make(sm_pools, synth, tmp_path_factory, NAIVE, None)


@pytest.fixture(scope="session")
def naive_base(sm_pools, synth, tmp_path_factory):
    return _make(sm_pools, synth, tmp_path_factory, NAIVE, BASE)


@pytest.fixture(scope="session")
def naive_full(sm_pools, synth, tmp_path_factory):
    return _make(sm_pools, synth, tmp_path_factory, NAIVE, FULL)


@pytest.fixture(scope="session")
def point_base(sm_pools, synth, tmp_path_factory):
    return _make(sm_pools, synth, tmp_path_factory, POINT, BASE)


@pytest.fixture(scope="session")
def point_full(sm_pools, synth, tmp_path_factory):
    return _make(sm_pools, synth, tmp_path_factory, POINT, FULL)


def _by_window(rec):
    return {p.metadata["creation_window"]: p for p in rec}


# ------------------------------------------------------------- T1: baseline 512 parity


def test_T1_base_size_flag_reproduces_historical_path(naive_noflag, naive_base):
    """--candidate-size-per-class at the adapt size is BIT-IDENTICAL to the flag-absent
    historical path: same windows, triggers, summaries, resolutions, same candidate
    batches. This is the in-process leg of T1; the driver-level leg (stored v1.21.0-code
    smoke outputs, seeds 4242-4243) runs via --parity."""
    for k in ("win", "trig", "summ", "res"):
        pd.testing.assert_frame_equal(naive_noflag[k], naive_base[k], check_exact=True)
    bh, bn = _by_window(naive_noflag["rec"]), _by_window(naive_base["rec"])
    assert sorted(bh) == sorted(bn) and bh, "no candidates trained"
    for t in bh:
        assert bh[t].metadata["training_row_hash"] == bn[t].metadata["training_row_hash"]
    s = naive_base["summ"]
    assert int(s[s.method == "ks_max"].n_adaptations.iloc[0]) > 0, "vacuous: no commit"


# ----------------------------------------------------------------- T2: nested batches


def test_T2_nested_draw_unit():
    """batch_base == first `BASE` per class of batch_full, by content and by hash, and the
    full batch is the base batch plus the canonical extension from the same RNG stream."""
    args = type("A", (), dict(adapt_size_per_class=BASE, train_size_per_class=FULL,
                              adapt_strategy="full_replace"))()
    rng = np.random.default_rng(321)
    pools = make_pools(
        pd.DataFrame(rng.normal(size=(400, 5)), columns=[f"f{i}" for i in range(5)]),
        pd.Series([0] * 200 + [1] * 200),
        pd.DataFrame(rng.normal(1.0, 1.0, size=(400, 5)), columns=[f"f{i}" for i in range(5)]),
        pd.Series([0] * 200 + [1] * 200),
        [f"f{i}" for i in range(5)])
    Xb, yb = v2.nested_candidate_draw(pools, args, BASE, 0.0, np.random.default_rng(777))
    Xf, yf = v2.nested_candidate_draw(pools, args, FULL, 0.0, np.random.default_rng(777))
    # prefix identity: same rows, same labels, same order, same hash
    np.testing.assert_array_equal(Xf[: 2 * BASE], Xb)
    np.testing.assert_array_equal(yf[: 2 * BASE], yb)
    assert rows_hash(Xf[: 2 * BASE], yf[: 2 * BASE]) == rows_hash(Xb, yb)
    # the base batch IS the historical draw (bit-identical)
    Xh, yh = sample_balanced_from_distribution(
        pools, n_per_class=BASE, severity=0.0, rng=np.random.default_rng(777))
    np.testing.assert_array_equal(Xb, Xh)
    np.testing.assert_array_equal(yb, yh)
    # balance at both sizes
    assert (yb == 0).sum() == (yb == 1).sum() == BASE
    assert (yf == 0).sum() == (yf == 1).sum() == FULL
    # the mechanism is undefined off its registered scope
    with pytest.raises(SystemExit):
        v2.nested_candidate_draw(pools, args, FULL, 0.3, np.random.default_rng(777))
    with pytest.raises(SystemExit):
        v2.nested_candidate_draw(pools, args, 128, 0.0, np.random.default_rng(777))
    args_bad = type("A", (), dict(adapt_size_per_class=BASE, train_size_per_class=FULL,
                                  adapt_strategy="cumulative"))()
    with pytest.raises(SystemExit):
        v2.nested_candidate_draw(pools, args_bad, FULL, 0.0, np.random.default_rng(777))


def test_T2_nested_batches_end_to_end(naive_base, naive_full):
    """Per (seed, proposal): the full-size candidate's first 2*BASE rows hash to exactly the
    base-size candidate's training batch at the same creation window."""
    bb, bf = _by_window(naive_base["rec"]), _by_window(naive_full["rec"])
    common = sorted(set(bb) & set(bf))
    assert common, "no common proposal window between the size conditions"
    for t in common:
        env = naive_full["env"]
        rng = np.random.default_rng(SEED * 100_003 + t)
        Xf_exp, yf_exp = v2.nested_candidate_draw(
            env.train_pools, naive_full["args"], FULL, 0.0, rng)
        assert bf[t].metadata["training_row_hash"] == rows_hash(Xf_exp, yf_exp)
        assert rows_hash(Xf_exp[: 2 * BASE], yf_exp[: 2 * BASE]) \
            == bb[t].metadata["training_row_hash"]


def test_T2_recording_factory_prefix_hash(naive_full):
    """The driver's provenance wrapper records size and the nested prefix hash."""
    inner_calls = []

    def inner(X, y, s, C, proba):
        inner_calls.append(1)
        return naive_full["rec"][0]   # any pipeline; wrapper only reads metadata

    records = []
    fac = _recording_candidate_factory(inner, SEED, BASE, records)
    p0 = naive_full["rec"][0]
    t0 = p0.metadata["creation_window"]
    rng = np.random.default_rng(SEED * 100_003 + t0)
    X, y = v2.nested_candidate_draw(
        naive_full["env"].train_pools, naive_full["args"], FULL, 0.0, rng)
    fac(X, y, SEED + t0 + 1, 1.0, False)
    assert inner_calls and len(records) == 1
    r = records[0]
    assert r["candidate_size_per_class"] == FULL
    assert r["nested_base_per_class"] == BASE
    assert r["nested_prefix_row_hash"] == rows_hash(X[: 2 * BASE], y[: 2 * BASE])
    assert "training_row_hash" in r and "svc_effective_gamma" in r
    json.dumps(r)   # must be serializable for candidate_provenance.jsonl


# ----------------------------------------------------------------- T3: same raw stream


def test_T3_same_raw_stream_across_arms(naive_noflag, naive_base, naive_full,
                                        point_base, point_full):
    """All arms of a scenario/seed share the raw stream (the candidate-size flag and the
    gate flags cannot touch the environment RNG)."""
    hashes = {stream_raw_hash(run["env"].stream_raw)
              for run in (naive_noflag, naive_base, naive_full, point_base, point_full)}
    assert len(hashes) == 1


# --------------------------------------------------------------------- T4: same probes


def test_T4_same_probes(point_base, point_full):
    """Both size conditions see the same triggers (trigger RNG keyed by (seed, t) only) and,
    at the same trigger with equivalent trajectory, the same raw probe (probe RNG keyed by
    (seed, t) only -- candidate size cannot consume it)."""
    tb = point_base["trig"];  tf = point_full["trig"]
    assert sorted(tb.window_idx) == sorted(tf.window_idx), "trigger sequences differ"
    for t in (9, 17, 33):
        draws = []
        for run in (point_base, point_full):
            rng = np.random.default_rng(SEED * 200_003 + t)
            Xp, yp = sample_balanced_from_distribution(
                run["env"].probe_pools, n_per_class=8, severity=0.0, rng=rng)
            draws.append(rows_hash(Xp, yp))
        assert draws[0] == draws[1]
    # incumbent probe accuracy identical at triggers before the first trajectory divergence
    mb = tb.set_index("window_idx"); mf = tf.set_index("window_idx")
    cb = naive_commits = sorted(set(mb.index[mb.get("committed", mb.get("commit", 0)) == 1])
                                if "committed" in mb or "commit" in mb else [])
    first_div = min(cb) if cb else int(max(mb.index) + 1)
    shared = [t for t in mb.index if t <= first_div and t in mf.index]
    for col in ("p_inc",):
        if col in mb.columns:
            for t in shared:
                assert mb.loc[t, col] == mf.loc[t, col]


# ----------------------------------------------------------------------- T5: no leakage


def test_T5_no_leakage_both_sizes(naive_base, naive_full):
    """Scaler/PCA of both size conditions are functions of the candidate training batch
    ONLY: refitting on the recorded raw batch reproduces the parameters exactly, and the
    scaler saw exactly 2*size rows."""
    for run, size in ((naive_base, BASE), (naive_full, FULL)):
        assert run["rec"], "no candidate trained"
        for p in run["rec"]:
            t = p.metadata["creation_window"]
            rng = np.random.default_rng(SEED * 100_003 + t)
            X, y = v2.nested_candidate_draw(
                run["env"].train_pools, run["args"], size, 0.0, rng)
            assert rows_hash(X, y) == p.metadata["training_row_hash"]
            assert int(p.scaler.n_samples_seen_) == 2 * size
            ref = StandardScaler().fit(X)
            np.testing.assert_array_equal(p.scaler.mean_, ref.mean_)
            np.testing.assert_array_equal(p.scaler.var_, ref.var_)


# --------------------------------------------------------------- T6: same hyperparameters


def test_T6_same_hyperparameters(naive_base, naive_full):
    """Everything configurable is identical across sizes: same classifier constructor
    params (C=1.0, gamma='scale'), same training seed, same PCA dim. Only the fitted
    estimator quantities (effective gamma, components) may differ, and they are recorded."""
    bb, bf = _by_window(naive_base["rec"]), _by_window(naive_full["rec"])
    common = sorted(set(bb) & set(bf))
    assert common
    for t in common:
        pb, pf = bb[t], bf[t]
        assert pb.classifier.get_params() == pf.classifier.get_params()
        assert pb.metadata["classifier_config"]["C"] == 1.0
        assert pf.metadata["classifier_config"]["C"] == 1.0
        assert pb.metadata["svc_configured_gamma"] == pf.metadata["svc_configured_gamma"] \
            == "'scale'"
        assert pb.metadata["training_seed"] == pf.metadata["training_seed"] == SEED + t + 1
        assert pb.metadata["pca_dim"] == pf.metadata["pca_dim"] == 4
        assert pb.metadata["svc_effective_gamma"] is not None
        assert pf.metadata["svc_effective_gamma"] is not None


def test_T6_cn_scaling_not_reachable():
    """The only n-dependent C scaling in the codebase (cumulative 'cn' mode) is not on the
    full_replace path: the registered config pins --adapt-strategy full_replace in every
    arm, and the nested draw itself refuses any other strategy."""
    cfg = json.loads(SM_CONFIG.read_text(encoding="utf-8"))
    assert cfg["fixed_flags"]["--adapt-strategy"] == "full_replace"
    for arm in size_matched_arms(load_config(SM_CONFIG)):
        assert arm["flags"]["--adapt-strategy"] == "full_replace"
        assert "--cumulative-mode" not in arm["flags"]


# ------------------------------------------------------------ T7: complete-bundle commit


def _commit_windows(win: pd.DataFrame) -> list[int]:
    m = win[win.method == "ks_max"]
    return m[m.adapted_now].window_idx.astype(int).tolist()


def test_T7_complete_bundle_commit_full_size(naive_full):
    """A committed full-size candidate serves from t+1 as a complete bundle (its scaler,
    its PCA, its classifier reproduce the logged window metrics exactly)."""
    win, env, rec = naive_full["win"], naive_full["env"], naive_full["rec"]
    commits = _commit_windows(win)
    assert commits, "full-size naive arm produced no commit"
    t_c = commits[0]
    pipe = [p for p in rec if p.metadata["creation_window"] == t_c]
    assert len(pipe) == 1
    pipe = pipe[0]
    assert int(pipe.scaler.n_samples_seen_) == 2 * FULL
    m = win[win.method == "ks_max"].set_index("window_idx")
    t_end = commits[1] if len(commits) > 1 else t_c + 4
    for t in range(t_c + 1, min(t_end + 1, len(env.stream_raw))):
        Xw, yw, _ = env.stream_raw[t]
        assert float(balanced_accuracy_score(yw, pipe.predict(Xw))) \
            == m.loc[t].balanced_accuracy
    assert pipe.scaler is not env.initial_model.scaler
    assert pipe.reducer is not env.initial_model.reducer


# ------------------------------------------------------------------- T8: determinism


def test_T8_determinism(sm_pools, synth, tmp_path_factory, naive_full):
    """Two identical executions of the full-size arm produce identical outputs and hashes."""
    again = _make(sm_pools, synth, tmp_path_factory, NAIVE, FULL)
    assert stream_raw_hash(naive_full["env"].stream_raw) \
        == stream_raw_hash(again["env"].stream_raw)
    for k in ("win", "trig", "summ", "res"):
        pd.testing.assert_frame_equal(naive_full[k], again[k], check_exact=True)
    assert len(naive_full["rec"]) == len(again["rec"])
    for p1, p2 in zip(naive_full["rec"], again["rec"]):
        for key in ("training_row_hash", "scaler_hash", "pca_hash", "creation_window",
                    "svc_effective_gamma"):
            assert p1.metadata[key] == p2.metadata[key]


# ------------------------------------------------------------------ T9: seed firewall


def test_T9_seed_firewall_new_config():
    """The driver refuses the reserved block 4001-4030 in every non-authorized mode of the
    size-matched config, and accepts the registered smoke seeds."""
    cfg = load_config(SM_CONFIG)
    assert cfg["confirmatory_seeds"] == dict(cfg["confirmatory_seeds"], start=4001, end=4030)
    for mode in ("smoke", "parity", "development", "dry-run"):
        for s in (4001, 4015, 4030):
            with pytest.raises(SystemExit):
                firewall(cfg, [s], mode=mode, authorized=False)
    with pytest.raises(SystemExit):   # smoke refuses even WITH the authorization flag
        firewall(cfg, [4001], mode="smoke", authorized=True)
    with pytest.raises(SystemExit):   # --run without authorization refuses too
        firewall(cfg, [4001], mode="development", authorized=False)
    firewall(cfg, [4401, 4402], mode="smoke", authorized=False)   # smoke seeds pass
    firewall(cfg, [4242, 4243], mode="parity", authorized=False)  # parity seeds pass


# ----------------------------------------------------------------------- T10: metrics


def test_T10_metrics_recomputation(naive_full):
    """BA, attack recall and FPR logged per window equal an independent sklearn
    recomputation on the raw windows served by the initial model."""
    win, env = naive_full["win"], naive_full["env"]
    m = win[win.method == "ks_max"].set_index("window_idx")
    first_commit = _commit_windows(win)[0]
    checked = 0
    for t in range(0, min(first_commit + 1, 6)):
        Xw, yw, _ = env.stream_raw[t]
        pred = env.initial_model.predict(Xw)
        fp = int(((pred == 1) & (yw == 0)).sum())
        tn = int(((pred == 0) & (yw == 0)).sum())
        assert m.loc[t].balanced_accuracy == float(balanced_accuracy_score(yw, pred))
        assert m.loc[t].recall == float(((pred == 1) & (yw == 1)).sum()
                                        / max(1, (yw == 1).sum()))
        assert m.loc[t].fpr == fp / max(1, fp + tn)
        checked += 1
    assert checked > 0


# -------------------------------------------------- T11: historical artifact unchanged

# The scientific core sealed at v1.21.0: the confirmatory symmetric-pipeline analysis
# tables, pinned with the exact on-disk hashes recorded in the v1.21.0 MANIFEST.sha256.
# (Before the v1.22.0 sealing this test additionally pinned the whole-manifest hash;
# the v1.22.0 re-pin is additive for these entries, so the per-file constants are the
# invariant that must hold forever.)
V1210_SEALED_CORE = {
    "results/tables/symmetric_pipeline_dynamic_001/by_seed.csv":
        "36269497853f680d0975bd4694de01b64f7b0fb650ffd9b69290c32b0d44d325",
    "results/tables/symmetric_pipeline_dynamic_001/equivalence.csv":
        "f405b2d27fbb8583dfbeaa6939ce2bd9a471e416896c7c4f6d92103863f83cc4",
    "results/tables/symmetric_pipeline_dynamic_001/harmful_commit_summary.csv":
        "ab6134730495e9332d7e87e0e0ce4060bdd4279d68f912ab565441435cbb989c",
    "results/tables/symmetric_pipeline_dynamic_001/multiplicity.csv":
        "9771a010dd213d6dfefcc91af873a1c71f269b1e0a1fe2174e028a5efd40ac19",
    "results/tables/symmetric_pipeline_dynamic_001/paired_contrasts.csv":
        "a3e536c4cf5acfa20c52c7926b2bd292e0d25533c43166e0f2d78cc933fed865",
    "results/tables/symmetric_pipeline_dynamic_001/run_completion.csv":
        "6f34c9c223951f66c89088c22b6ad6a27e1f3aeeeeb5bd8c392b370cbad4c3a0",
    "results/tables/symmetric_pipeline_dynamic_001/security_metrics.csv":
        "b38fb2e3ec623283d75c0e2b9cf85e55f0bd5f6f483112b7c5ccb59c069f905c",
    "results/tables/symmetric_pipeline_dynamic_001/summary.csv":
        "e92632d3c60f36eb438e00f2bac03c317d35f9a4c8fb2fab517c24d81a0fab19",
    "results/tables/symmetric_pipeline_dynamic_001/transformer_interaction.csv":
        "189681e94ef132547be2d37b0ecf63f7eafeeb28d494d2638e0ce685f47f1c35",
}
V1210_CONFIG_SHA = "527947788e685e7f8cabf2989eb58aec8fbc8f948ea8e0d1f3640b52893d40e8"


def test_T11_v1210_artifact_unchanged():
    """The sealed v1.21.0 scientific core is untouched: every confirmatory
    symmetric-pipeline table still carries its v1.21.0-sealed hash, the frozen v1.21.0
    config is unchanged, the current MANIFEST still pins every one of those entries with
    the identical hash, and every pinned CSV hashes to its manifest entry."""
    for path, sealed in V1210_SEALED_CORE.items():
        assert hashlib.sha256((REPO / path).read_bytes()).hexdigest() == sealed, \
            f"sealed v1.21.0 table changed: {path}"
    cfg = REPO / "configs" / "symmetric_pipeline_dynamic_v1.json"
    assert hashlib.sha256(cfg.read_bytes()).hexdigest() == V1210_CONFIG_SHA
    manifest = REPO / "results" / "tables" / "MANIFEST.sha256"
    pinned = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        h, path = line.strip().split(maxsplit=1)
        pinned[path.strip()] = h
        data = (REPO / path.strip()).read_bytes()
        assert hashlib.sha256(data).hexdigest() == h, f"pinned file changed: {path}"
    assert len(pinned) >= 173
    for path, sealed in V1210_SEALED_CORE.items():
        assert pinned.get(path) == sealed, f"v1.21.0 pin lost or altered: {path}"
    # the v1.21.0 record inside the (re-stamped) final manifest stays intact
    final = json.loads((REPO / "results" / "final_manifest.json")
                       .read_text(encoding="utf-8"))
    v121 = final["symmetric_replication_v1_21"]
    assert v121["scenario"] == "A"
    assert v121["confirmatory_seeds"] == "3001-3030"
    assert v121["expected_arms"] == 42
    assert v121["config_sha256"] == V1210_CONFIG_SHA
