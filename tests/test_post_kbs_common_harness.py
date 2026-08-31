"""Implementation-fidelity tests for the amended common-harness baselines experiment (B1).

Protocol: notes/post_kbs_common_harness_baselines_protocol_001.md + amendment 001.
Runs in-process on conftest's SYNTHETIC data (development seed 14 only; no benchmark, no
confirmatory seed). Verifies: the 96-arm grid; ATC/DoC decisions against the published
definitions (traced equations) and their v1 implementation; river DDM/ADWIN as reference
objects fed per-flow Bernoulli errors; calibrated-ensemble and replay fidelity in raw
own-transformer mode; probability=True not changing .predict; budget accounting; the seed
firewall. Full-scale anchor byte-parity (stored smoke outputs, 4242-4243) runs via
`--parity --config configs/post_kbs_common_harness_baselines_v2.json`.
"""
from __future__ import annotations

import inspect
import json

import numpy as np
import pandas as pd
import pytest

from src.experiments import run_paper2_readaptation_v2 as v2
from src.experiments.run_paper2_progressive_readaptation import (
    _labelfree_estimate,
    load_binary_dataset,
    make_pools,
    sample_balanced_from_distribution,
    train_svc,
)
from src.experiments.run_symmetric_pipeline_replication import (
    common_harness_arms,
    firewall,
    load_config,
)
from src.experiments.symmetric_pipeline import (
    OWN_POLICY,
    ModelPipeline,
    build_raw_environment,
    rows_hash,
    stream_raw_hash,
)
from tests.conftest import REPO

BH_CONFIG = REPO / "configs" / "post_kbs_common_harness_baselines_v2.json"
SEED = 14   # development seed: outside every ledgered block and all reserved blocks
FULL = 200  # synthetic analogue of the 2,000/class primary size
BASE = 64   # synthetic analogue of the 512/class secondary size


@pytest.fixture(scope="session")
def bh_pools(synth):
    X_ref, y_ref = load_binary_dataset(synth["ref"], "Label")
    X_cur, y_cur = load_binary_dataset(synth["cur"], "Label")
    common = sorted(set(X_ref.columns).intersection(X_cur.columns))
    return make_pools(X_ref, y_ref, X_cur, y_cur, common)


def _bargs(synth, tmp, extra: list[str]):
    return v2.build_parser().parse_args([
        "--data-ref", str(synth["ref"]), "--data-cur", str(synth["cur"]),
        "--outdir", str(tmp), "--label-col", "Label", "--methods", "ks_max",
        "--dim", "4", "--window-size", "32", "--post-windows", "40",
        "--ramp-windows", "20", "--calibration-windows", "10",
        "--train-size-per-class", str(FULL), "--adapt-size-per-class", str(FULL),
        "--detector-ref-size-per-class", "64", "--downstream-model", "svc_rbf",
        "--adapt-strategy", "full_replace", "--max-severity", "1.0",
        "--trigger-mode", "random", "--trigger-prob", "0.35", "--seeds", str(SEED),
    ] + extra)


def _record(env):
    rec = []
    orig = env.candidate_factory

    def wrapped(X, y, s, C, proba):
        p = orig(X, y, s, C, proba)
        rec.append(p)
        return p

    env.candidate_factory = wrapped
    return rec


def _make(bh_pools, synth, tmp_path_factory, extra: list[str]):
    args = _bargs(synth, tmp_path_factory.mktemp("bh"), extra)
    env = build_raw_environment(bh_pools, args, SEED, OWN_POLICY)
    rec = _record(env)
    w, t, s, r = v2.run_seed(env, args, SEED, ["ks_max"])
    return dict(env=env, rec=rec, args=args, win=pd.DataFrame(w), trig=pd.DataFrame(t),
                summ=pd.DataFrame(s), res=pd.DataFrame(r))


# ------------------------------------------------------------------ grid integrity
def test_G1_grid_96_arms_tags_flags_origins():
    cfg = load_config(BH_CONFIG)
    arms = common_harness_arms(cfg)
    assert len(arms) == 96 == cfg["expected_arms"]
    tags = {a["tag"] for a in arms}
    for sc in cfg["scenarios_list"]:
        assert f"bh_{sc}_never" in tags
        for pol in cfg["primary_policies"]:
            assert f"bh_{sc}_{pol}_2000" in tags
        for pol in cfg["secondary_policies_512"]:
            assert f"bh_{sc}_{pol}_512" in tags
        for pol in ("ddm", "adwin", "replay"):
            assert f"bh_{sc}_{pol}_512" not in tags, "frozen exclusion from the 512 block"
    by_tag = {a["tag"]: a for a in arms}
    a = by_tag["bh_ps_zero_ddm_2000"]
    assert a["flags"]["--trigger-mode"] == "ddm_river", "policy overrides scenario trigger"
    assert a["flags"]["--max-severity"] == "0"
    assert a["flags"]["--monitor-labels"] == "8"
    a = by_tag["bh_ton_full_atc_2000"]
    assert a["flags"]["--adaptation-gate"] == "atc"
    assert a["flags"]["--gate-val-size"] == "512"
    assert a["flags"]["--adapt-size-per-class"] == "2000"
    a = by_tag["bh_unsw_zero_enscal_512"]
    assert a["flags"]["--adapt-strategy"] == "ensemble_cal"
    assert a["flags"]["--adapt-size-per-class"] == "512"
    a = by_tag["bh_ton_full_replay_2000"]
    assert a["flags"]["--adapt-strategy"] == "replay"
    for arm in arms:
        if arm["policy"] != "never":
            assert arm["transformer_policy"] == "own_transformer_per_model"
            assert arm["origin"] in ("anchor", "anchor-ours", "published-generic",
                                     "standard-baseline", "reference-implementation")
    for smoke_tag in cfg["smoke_arms"]:
        assert smoke_tag in tags
    assert {p["tag"] for p in cfg["parity_arms"]} == {"parity_bh_ton_zero_naive_512"}


# ------------------------------------------------------------- firewall / seed hygiene
def test_G2_firewall_and_seed_hygiene():
    cfg = load_config(BH_CONFIG)
    assert (cfg["confirmatory_seeds"]["start"], cfg["confirmatory_seeds"]["end"]) == (5001, 5030)
    for mode in ("smoke", "parity", "development", "dry-run"):
        for s in (5001, 5015, 5030):
            with pytest.raises(SystemExit):
                firewall(cfg, [s], mode=mode, authorized=False)
    with pytest.raises(SystemExit):
        firewall(cfg, [5001], mode="smoke", authorized=True)
    with pytest.raises(SystemExit):
        firewall(cfg, [5001], mode="development", authorized=False)
    firewall(cfg, [5401, 5402], mode="smoke", authorized=False)
    firewall(cfg, [4242, 4243], mode="parity", authorized=False)


# --------------------------------------------------- ATC / DoC: published definitions
def test_F1_atc_doc_equations_traced():
    """ATC (Garg et al., ICLR 2022): threshold t s.t. fraction of source-val confidences
    above t equals source-val accuracy; estimate = fraction of target confidences above t.
    DoC (Guillory et al., ICCV 2021): est = acc_val - (mean_conf_val - mean_conf_target).
    The shipped implementation must equal an independent transcription of both."""
    rng = np.random.default_rng(99)
    Xv = rng.normal(size=(300, 4))
    yv = (Xv[:, 0] + 0.3 * rng.normal(size=300) > 0).astype(int)
    Xt = rng.normal(0.4, 1.1, size=(200, 4))
    model = train_svc(Xv, yv, seed=3, model_type="svc_rbf", proba=True)
    conf_v = model.predict_proba(Xv).max(axis=1)
    conf_t = model.predict_proba(Xt).max(axis=1)
    acc_v = float((model.predict(Xv) == yv).mean())
    # independent transcription
    thr = float(np.quantile(conf_v, 1.0 - acc_v)) if acc_v < 1.0 else float(conf_v.min())
    atc_ref = float((conf_t > thr).mean())
    doc_ref = acc_v - (float(conf_v.mean()) - float(conf_t.mean()))
    assert _labelfree_estimate("atc", model, (Xv, yv), Xt) == pytest.approx(atc_ref, abs=0)
    assert _labelfree_estimate("doc", model, (Xv, yv), Xt) == pytest.approx(doc_ref, abs=0)


def test_F2_atc_doc_pipeline_vs_plain_bitagree():
    """The raw-mode ModelPipeline path must produce bit-identical ATC/DoC estimates to the
    plain-model v1-style path on the same underlying classifier and data."""
    rng = np.random.default_rng(5)
    X = rng.normal(size=(400, 4))
    y = (X[:, 1] > 0).astype(int)
    Xt = rng.normal(0.3, 1.0, size=(150, 4))
    from src.experiments.run_paper2_progressive_readaptation import fit_transformer
    scaler, pca, Xz = fit_transformer(X, 3, seed=2)
    clf = train_svc(Xz, y, seed=4, model_type="svc_rbf", proba=True)
    pipe = ModelPipeline(scaler, pca, clf)
    from src.experiments.run_paper2_progressive_readaptation import transform_X
    for kind in ("atc", "doc"):
        plain = _labelfree_estimate(kind, clf, (transform_X(X, scaler, pca), y),
                                    transform_X(Xt, scaler, pca))
        raw = _labelfree_estimate(kind, pipe, (X, y), Xt)
        assert plain == raw, kind


def test_F3_atc_e2e_own_transformer(bh_pools, synth, tmp_path_factory):
    run = _make(bh_pools, synth, tmp_path_factory,
                ["--adaptation-gate", "atc", "--gate-val-size", "64"])
    s = run["summ"]
    ks = s[s.method == "ks_max"]
    assert int(ks.n_triggers.iloc[0]) > 0
    assert int(ks.n_adaptations.iloc[0]) + int(ks.n_gate_rejections.iloc[0]) \
        == int(ks.n_triggers.iloc[0])
    for p in run["rec"]:
        assert p.metadata["classifier_config"]["probability"] is True
    assert hasattr(run["env"].initial_model, "predict_proba")


# --------------------------------------------------------- river reference monitors
def test_F4_river_reference_objects_and_input_granularity():
    src = inspect.getsource(v2.run_arm)
    assert "river_drift.binary.DDM()" in src and "river_drift.ADWIN(delta=0.002)" in src, \
        "must instantiate the river reference objects"
    assert "INDIVIDUAL Bernoulli outcomes" in src, \
        "documented input granularity: per-flow errors of the monitoring sample"
    import river
    assert river.__version__ == "0.25.0", "pinned by requirements-lock"


def test_F5_ddm_river_e2e(bh_pools, synth, tmp_path_factory):
    run = _make(bh_pools, synth, tmp_path_factory,
                ["--adaptation-gate", "none", "--trigger-mode", "ddm_river",
                 "--monitor-labels", "8"])
    s = run["summ"]
    ks = s[s.method == "ks_max"]
    assert int(ks.labels_monitor.iloc[0]) == 8 * 40, "8 monitoring labels per window"
    assert int(ks.n_gate_rejections.iloc[0]) == 0, "trigger policy: always-deploy on fire"


def test_F6_adwin_river_e2e(bh_pools, synth, tmp_path_factory):
    run = _make(bh_pools, synth, tmp_path_factory,
                ["--adaptation-gate", "none", "--trigger-mode", "adwin_river",
                 "--monitor-labels", "8"])
    s = run["summ"]
    ks = s[s.method == "ks_max"]
    assert int(ks.labels_monitor.iloc[0]) == 8 * 40


# ------------------------------------------------------- calibrated ensemble / replay
def test_F7_enscal_members_and_nesting_raw_mode():
    rng = np.random.default_rng(11)
    X = rng.normal(size=(300, 4))
    y = (X[:, 0] > 0).astype(int)
    from src.experiments.run_paper2_progressive_readaptation import fit_transformer
    s1, p1, Xz1 = fit_transformer(X, 3, seed=1)
    a = ModelPipeline(s1, p1, train_svc(Xz1, y, seed=1, model_type="svc_rbf", proba=True))
    s2, p2, Xz2 = fit_transformer(X + 0.1, 3, seed=2)
    b = ModelPipeline(s2, p2, train_svc(Xz2, y, seed=2, model_type="svc_rbf", proba=True))
    ens = v2.EnsembleModelCal(a, b)
    Xq = rng.normal(size=(64, 4))
    proba = ens.predict_proba(Xq)
    assert proba.shape == (64, 2)
    np.testing.assert_allclose(proba.sum(axis=1), 1.0)
    expected = ((a.predict_proba(Xq)[:, 1] + b.predict_proba(Xq)[:, 1]) / 2 >= 0.5).astype(int)
    np.testing.assert_array_equal(ens.predict(Xq), expected)
    nest = v2.EnsembleModelCal(ens, a)          # nested ensemble stays probabilistic
    assert nest.predict_proba(Xq).shape == (64, 2)


def test_F8_enscal_e2e(bh_pools, synth, tmp_path_factory):
    run = _make(bh_pools, synth, tmp_path_factory,
                ["--adaptation-gate", "none", "--adapt-strategy", "ensemble_cal"])
    s = run["summ"]
    ks = s[s.method == "ks_max"]
    assert int(ks.n_adaptations.iloc[0]) >= 1, "ensemble commits every trigger"
    assert int(ks.n_gate_rejections.iloc[0]) == 0, "cannot decline an update"


def test_F9_replay_5050_rule_preserved(bh_pools, synth, tmp_path_factory):
    run = _make(bh_pools, synth, tmp_path_factory,
                ["--adaptation-gate", "none", "--adapt-strategy", "replay"])
    assert run["rec"], "no replay candidate trained"
    env, args = run["env"], run["args"]
    for p in run["rec"]:
        t = p.metadata["creation_window"]
        sev = env.stream_raw[t][2]
        rng = np.random.default_rng(SEED * 100_003 + t)
        n_half = max(1, args.adapt_size_per_class // 2)
        Xc, yc = sample_balanced_from_distribution(
            env.train_pools, n_per_class=n_half, severity=sev, rng=rng)
        Xr, yr = sample_balanced_from_distribution(
            env.train_pools, n_per_class=n_half, severity=0.0, rng=rng)
        Xa = np.vstack([Xc, Xr])
        ya = np.concatenate([yc, yr])
        assert p.metadata["training_row_hash"] == rows_hash(Xa, ya), \
            "frozen 50/50 replay rule (half sev(t), half severity-0) must be preserved"


# ------------------------------------------------ probability=True predict invariance
def test_F10_platt_layer_does_not_change_predict():
    rng = np.random.default_rng(21)
    X = rng.normal(size=(400, 4))
    y = (X[:, 0] + 0.2 * rng.normal(size=400) > 0).astype(int)
    Xq = rng.normal(size=(200, 4))
    m0 = train_svc(X, y, seed=6, model_type="svc_rbf", proba=False)
    m1 = train_svc(X, y, seed=6, model_type="svc_rbf", proba=True)
    np.testing.assert_array_equal(m0.predict(Xq), m1.predict(Xq)), \
        "streams/anchors stay bit-comparable across proba arms"


# ------------------------------------------------------------- shared raw stream
def test_F11_same_raw_stream_across_policy_arms(bh_pools, synth, tmp_path_factory):
    runs = [
        _make(bh_pools, synth, tmp_path_factory, ["--adaptation-gate", "none"]),
        _make(bh_pools, synth, tmp_path_factory,
              ["--adaptation-gate", "atc", "--gate-val-size", "64"]),
        _make(bh_pools, synth, tmp_path_factory,
              ["--adaptation-gate", "none", "--adapt-strategy", "replay"]),
    ]
    hashes = {stream_raw_hash(r["env"].stream_raw) for r in runs}
    assert len(hashes) == 1, "policy flags must not perturb the environment RNG"
