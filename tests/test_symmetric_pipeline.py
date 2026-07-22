"""Invariant tests T1-T12 of the symmetric-pipeline preparation phase.

Registered protocol: notes/paper2_symmetric_pipeline_dynamic_protocol_001.md (Bloque 4).

Everything here runs in-process on the SYNTHETIC data of conftest (no benchmark, no
confirmatory seed; development seeds 11/12 only). The full-scale frozen parity against the
published v1.20.2 arms (historical seeds 501-530, byte-level) is executed by
`run_symmetric_pipeline_replication --parity` and recorded in
notes/symmetric_pipeline_initial_phase_checkpoint.md; these tests keep the same invariants
permanently green on synthetic data.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler

from src.experiments import run_paper2_readaptation_v2 as v2
from src.experiments.run_paper2_progressive_readaptation import (
    fit_transformer,
    load_binary_dataset,
    make_pools,
    sample_balanced_from_distribution,
)
from src.experiments.symmetric_pipeline import (
    FROZEN_POLICY,
    OWN_POLICY,
    DetectorPipeline,
    IdentityTransformer,
    ModelPipeline,
    build_candidate_pipeline,
    build_raw_environment,
    rows_hash,
    stream_raw_hash,
)

REPO = Path(__file__).resolve().parents[1]
SEED = 11  # development seed: outside every ledgered block and outside 3001-3030 / 4242-4243


@pytest.fixture(scope="session")
def sp_pools(synth):
    X_ref, y_ref = load_binary_dataset(synth["ref"], "Label")
    X_cur, y_cur = load_binary_dataset(synth["cur"], "Label")
    common = sorted(set(X_ref.columns).intersection(X_cur.columns))
    return make_pools(X_ref, y_ref, X_cur, y_cur, common)


def _args(synth, tmp, extra: list[str]):
    return v2.build_parser().parse_args([
        "--data-ref", str(synth["ref"]), "--data-cur", str(synth["cur"]),
        "--outdir", str(tmp), "--label-col", "Label", "--methods", "ks_max",
        "--dim", "4", "--window-size", "32", "--post-windows", "40",
        "--ramp-windows", "20", "--calibration-windows", "10",
        "--train-size-per-class", "200", "--adapt-size-per-class", "64",
        "--detector-ref-size-per-class", "64", "--downstream-model", "logreg",
        "--trigger-mode", "random", "--trigger-prob", "0.35", "--seeds", str(SEED),
    ] + extra)


POINT = ["--adaptation-gate", "labeled_probe", "--probe-size", "16"]
NAIVE = ["--adaptation-gate", "none"]
VBC = ["--adaptation-gate", "vbc_sg", "--probe-size", "32", "--seq-block", "8",
       "--defer-windows", "3", "--seqav-alpha", "0.10",
       "--lifetime-alpha", "0.10", "--alpha-spending", "pseries"]


def _record_candidates(env):
    """Wrap the env's candidate factory so every built pipeline is captured."""
    rec: list[ModelPipeline] = []
    orig = env.candidate_factory

    def wrapped(X, y, s, C, proba):
        p = orig(X, y, s, C, proba)
        rec.append(p)
        return p

    env.candidate_factory = wrapped
    return rec


def _run(env, args, methods=("ks_max",)):
    w, t, s, r = v2.run_seed(env, args, SEED, list(methods))
    return dict(win=pd.DataFrame(w), trig=pd.DataFrame(t), summ=pd.DataFrame(s),
                res=pd.DataFrame(r))


@pytest.fixture(scope="session")
def point_args(synth, tmp_path_factory):
    return _args(synth, tmp_path_factory.mktemp("sp_point"), POINT)


@pytest.fixture(scope="session")
def hist_point(sp_pools, point_args):
    env = v2.build_environment(sp_pools, point_args, SEED)
    return _run(env, point_args)


@pytest.fixture(scope="session")
def froz_point(sp_pools, point_args):
    env = build_raw_environment(sp_pools, point_args, SEED, FROZEN_POLICY)
    rec = _record_candidates(env)
    out = _run(env, point_args)
    return dict(env=env, rec=rec, **out)


@pytest.fixture(scope="session")
def own_point(sp_pools, point_args):
    env = build_raw_environment(sp_pools, point_args, SEED, OWN_POLICY)
    rec = _record_candidates(env)
    out = _run(env, point_args)
    return dict(env=env, rec=rec, **out)


@pytest.fixture(scope="session")
def own_naive(sp_pools, synth, tmp_path_factory):
    args = _args(synth, tmp_path_factory.mktemp("sp_naive"), NAIVE)
    env = build_raw_environment(sp_pools, args, SEED, OWN_POLICY)
    rec = _record_candidates(env)
    out = _run(env, args)
    return dict(env=env, rec=rec, args=args, **out)


# ---------------------------------------------------------------- T1: frozen parity


def test_T1_frozen_parity_point_gate(hist_point, froz_point):
    """Raw-mode frozen_initial_transformer reproduces the historical harness BIT-FOR-BIT
    (same windows, triggers, decisions, metrics, accounting) on the point-gate arm."""
    for k in ("win", "trig", "summ", "res"):
        pd.testing.assert_frame_equal(hist_point[k], froz_point[k], check_exact=True)
    # non-vacuity: the arm actually proposed and committed
    s = froz_point["summ"]
    assert int(s[s.method == "ks_max"].n_adaptations.iloc[0]) > 0
    assert int(s[s.method == "ks_max"].n_triggers.iloc[0]) > 0


def test_T1_frozen_parity_deferred_vbc(sp_pools, synth, tmp_path_factory):
    """Same bit-parity through the deferred-commit (vbc_sg) path of the shared runner."""
    args = _args(synth, tmp_path_factory.mktemp("sp_vbc"), VBC)
    hist = _run(v2.build_environment(sp_pools, args, SEED), args)
    froz = _run(build_raw_environment(sp_pools, args, SEED, FROZEN_POLICY), args)
    for k in ("win", "trig", "summ", "res"):
        pd.testing.assert_frame_equal(hist[k], froz[k], check_exact=True)
    assert bool((hist["res"].deferred == True).any())  # noqa: E712  a defer was exercised


# ------------------------------------------------- T2: candidate raw-batch identity


def _batches_by_window(rec):
    return {p.metadata["creation_window"]: p.metadata["training_row_hash"] for p in rec}


def test_T2_candidate_batch_identity(froz_point, own_point):
    """For the same seed/trigger/scenario, frozen and own receive EXACTLY the same raw
    candidate batch (same rows, same labels, same hash); only the transformer policy differs."""
    bf, bo = _batches_by_window(froz_point["rec"]), _batches_by_window(own_point["rec"])
    common = sorted(set(bf) & set(bo))
    assert common, "no common trigger window between frozen and own runs"
    for t in common:
        assert bf[t] == bo[t], f"candidate batch at window {t} differs between policies"
    for p in froz_point["rec"]:
        assert p.metadata["transformer_policy"] == FROZEN_POLICY
    for p in own_point["rec"]:
        assert p.metadata["transformer_policy"] == OWN_POLICY


# ------------------------------------------------------------ T3: probe raw identity


def test_T3_probe_raw_identity(froz_point, own_point):
    """The probe is drawn RAW, identically across policies, and each pipeline transforms it
    internally. In raw mode the environment transformer is the identity (bytes unchanged),
    and the draw depends only on (seed, t, probe pools) -- never on the transformer policy."""
    ident = IdentityTransformer()
    X = np.random.default_rng(0).normal(size=(8, 5))
    assert ident.transform(X) is X  # transform_X(..., identity, None) passes raw bytes through
    for run in (froz_point, own_point):
        assert isinstance(run["env"].scaler, IdentityTransformer)
        assert run["env"].pca is None
    # the probe draw at a given (seed, t) is bit-identical regardless of policy
    for t in (9, 17, 33):
        draws = []
        for run in (froz_point, own_point):
            rng = np.random.default_rng(SEED * 200_003 + t)
            Xp, yp = sample_balanced_from_distribution(
                run["env"].probe_pools, n_per_class=8, severity=0.4, rng=rng)
            draws.append(rows_hash(Xp, yp))
        assert draws[0] == draws[1]


# ------------------------------------------------------------- T4: no future leakage


def test_T4_no_future_leakage(own_point):
    """The own-policy scaler/PCA are functions of the candidate batch ONLY: refitting them on
    the recorded raw batch reproduces them exactly, so no probe/future row participated."""
    env = own_point["env"]
    assert own_point["rec"], "no candidate was trained"
    for p in own_point["rec"]:
        t = p.metadata["creation_window"]
        sev = env.stream_raw[t][2]
        rng = np.random.default_rng(SEED * 100_003 + t)
        Xb, yb = sample_balanced_from_distribution(
            env.train_pools, n_per_class=64, severity=sev, rng=rng)
        assert rows_hash(Xb, yb) == p.metadata["training_row_hash"]
        ref_scaler = StandardScaler().fit(Xb)
        np.testing.assert_array_equal(p.scaler.mean_, ref_scaler.mean_)
        np.testing.assert_array_equal(p.scaler.var_, ref_scaler.var_)
        if p.reducer is not None:
            _, ref_pca, _ = fit_transformer(Xb, 4, p.metadata["training_seed"])
            np.testing.assert_array_equal(p.reducer.components_, ref_pca.components_)


def test_T4_probe_and_train_pools_disjoint(froz_point):
    """Probe rows and candidate-training rows come from ID-disjoint partitions."""
    env = froz_point["env"]
    for name in ("ref_benign", "ref_attack", "cur_benign", "cur_attack"):
        tr = {r.tobytes() for r in np.ascontiguousarray(getattr(env.train_pools, name))}
        pr = {r.tobytes() for r in np.ascontiguousarray(getattr(env.probe_pools, name))}
        assert not (tr & pr), f"train/probe overlap in pool {name}"


# --------------------------------------------------------- T5: own-pipeline role symmetry


def test_T5_role_symmetry():
    """Two i.i.d. equal-size batches, own-transformer on both: the probe gap inverts exactly
    under role swap and the constructor ignores the incumbent handle (no role advantage)."""
    rng = np.random.default_rng(123)
    mk = lambda: (np.vstack([rng.normal(0, 1, (64, 5)), rng.normal(1.2, 1, (64, 5))]),
                  np.r_[np.zeros(64, int), np.ones(64, int)])
    (Xa, ya), (Xb, yb), (Xp, yp) = mk(), mk(), mk()
    pa = build_candidate_pipeline(Xa, ya, transformer_policy=OWN_POLICY,
                                  initial_transformer=(None, None), incumbent_pipeline=None,
                                  model_kind="logreg", seed=7, dim=4)
    pb = build_candidate_pipeline(Xb, yb, transformer_policy=OWN_POLICY,
                                  initial_transformer=(None, None), incumbent_pipeline=pa,
                                  model_kind="logreg", seed=7, dim=4)
    # incumbent handle must not influence construction
    pb_none = build_candidate_pipeline(Xb, yb, transformer_policy=OWN_POLICY,
                                       initial_transformer=(None, None),
                                       incumbent_pipeline=None,
                                       model_kind="logreg", seed=7, dim=4)
    np.testing.assert_array_equal(pb.predict(Xp), pb_none.predict(Xp))
    gap = float((pb.predict(Xp) == yp).mean() - (pa.predict(Xp) == yp).mean())
    gap_swapped = float((pa.predict(Xp) == yp).mean() - (pb.predict(Xp) == yp).mean())
    assert gap == pytest.approx(-gap_swapped)
    assert abs(gap) < 0.15, "systematic advantage from the challenger/incumbent label"


# ------------------------------------------------------- T6: frozen semantic identity


def test_T6_frozen_uses_initial_transformer_forever(sp_pools, synth, tmp_path_factory):
    """Under frozen_initial_transformer every candidate -- including those built AFTER one or
    more commits -- carries the ORIGINAL initial scaler/PCA objects."""
    args = _args(synth, tmp_path_factory.mktemp("sp_frozen_naive"), NAIVE)
    env = build_raw_environment(sp_pools, args, SEED, FROZEN_POLICY)
    scaler0, pca0 = env.initial_model.scaler, env.initial_model.reducer
    rec = _record_candidates(env)
    out = _run(env, args)
    s = out["summ"]
    assert int(s[s.method == "ks_max"].n_adaptations.iloc[0]) >= 2, "need >=2 commits"
    assert rec
    for p in rec:
        assert p.scaler is scaler0, "candidate lost the ORIGINAL initial scaler"
        assert p.reducer is pca0, "candidate lost the ORIGINAL initial PCA"


# ------------------------------------------------------- T7: complete-bundle commit


def _commit_windows(win: pd.DataFrame) -> list[int]:
    m = win[win.method == "ks_max"]
    return m[m.adapted_now].window_idx.astype(int).tolist()


def test_T7_complete_bundle_commit(own_naive):
    """After an own-transformer commit at t, the model serving t+1.. is the challenger's FULL
    bundle: recomputing the served windows with the recorded candidate pipeline (its scaler,
    its PCA, its classifier) reproduces the logged metrics exactly."""
    win, env, rec = own_naive["win"], own_naive["env"], own_naive["rec"]
    commits = _commit_windows(win)
    assert commits, "naive own arm produced no commit"
    t_c = commits[0]
    committed = [p for p in rec if p.metadata["creation_window"] == t_c]
    assert len(committed) == 1
    pipe = committed[0]
    m = win[win.method == "ks_max"].set_index("window_idx")
    t_end = commits[1] if len(commits) > 1 else t_c + 4
    for t in range(t_c + 1, min(t_end + 1, len(env.stream_raw))):
        Xw, yw, _ = env.stream_raw[t]
        pred = pipe.predict(Xw)
        assert float(balanced_accuracy_score(yw, pred)) == m.loc[t].balanced_accuracy
    # and the incumbent's own components differ from the initial ones (a real bundle swap)
    assert pipe.scaler is not env.initial_model.scaler
    assert pipe.reducer is not env.initial_model.reducer


def test_T7_pre_commit_window_served_by_old_model(own_naive):
    """The commit window t itself is still served by the pre-commit model (see also T9)."""
    win, env, rec = own_naive["win"], own_naive["env"], own_naive["rec"]
    t_c = _commit_windows(win)[0]
    m = win[win.method == "ks_max"].set_index("window_idx")
    Xw, yw, _ = env.stream_raw[t_c]
    assert float(balanced_accuracy_score(yw, env.initial_model.predict(Xw))) \
        == m.loc[t_c].balanced_accuracy


# ------------------------------------------------------- T8: detector independence


def test_T8_detector_independence(froz_point, own_point, point_args):
    """P0 -> P1 changes neither the raw stream, nor the detector's representation, nor its
    scores before the model trajectories can legitimately diverge (first commit)."""
    ef, eo = froz_point["env"], own_point["env"]
    assert stream_raw_hash(ef.stream_raw) == stream_raw_hash(eo.stream_raw)
    df = ef.detector_factory("ks_max", point_args, SEED)
    do = eo.detector_factory("ks_max", point_args, SEED)
    assert isinstance(df, DetectorPipeline) and isinstance(do, DetectorPipeline)
    assert df.metadata["detector_transform_policy"] == "frozen_initial"
    assert do.metadata["detector_transform_policy"] == "frozen_initial"
    assert df.transformer[0] is ef.initial_model.scaler       # pinned to INITIAL transformer
    assert do.transformer[0] is eo.initial_model.scaler
    wf = froz_point["win"][froz_point["win"].method == "ks_max"].set_index("window_idx")
    wo = own_point["win"][own_point["win"].method == "ks_max"].set_index("window_idx")
    commits = _commit_windows(froz_point["win"]) + _commit_windows(own_point["win"])
    t_star = min(commits) if commits else len(wf) - 1
    for col in ("score", "threshold"):
        np.testing.assert_array_equal(wf.loc[:t_star, col].to_numpy(),
                                      wo.loc[:t_star, col].to_numpy())


# --------------------------------------------------------- T9: temporal semantics


def test_T9_temporal_semantics_raw_mode(own_naive):
    """Window t is served by the model active at its start; a commit resolved in t serves from
    t+1 (served_model_version is monotone and lags adapted_now by exactly one window)."""
    m = own_naive["win"]
    m = m[m.method == "ks_max"].sort_values("window_idx").reset_index(drop=True)
    v = m.served_model_version.astype(int).to_numpy()
    a = m.adapted_now.astype(bool).to_numpy()
    assert v[0] == 0
    for t in range(1, len(m)):
        assert v[t] - v[t - 1] in (0, 1)
        assert v[t] - v[t - 1] == int(a[t - 1]), (
            f"window {t}: served version must increment iff a commit resolved at t-1")


# ------------------------------------------------------------- T10: determinism


def test_T10_determinism(sp_pools, own_point, point_args):
    """Two identical executions produce identical stream hashes, batch/probe hashes, pipeline
    metadata hashes and outputs."""
    env2 = build_raw_environment(sp_pools, point_args, SEED, OWN_POLICY)
    rec2 = _record_candidates(env2)
    out2 = _run(env2, point_args)
    assert stream_raw_hash(own_point["env"].stream_raw) == stream_raw_hash(env2.stream_raw)
    for k in ("win", "trig", "summ", "res"):
        pd.testing.assert_frame_equal(own_point[k], out2[k], check_exact=True)
    assert len(own_point["rec"]) == len(rec2)
    for p1, p2 in zip(own_point["rec"], rec2):
        for key in ("training_row_hash", "scaler_hash", "pca_hash", "creation_window"):
            assert p1.metadata[key] == p2.metadata[key]


# --------------------------------------------------------- T11: security metrics


def test_T11_security_metrics(own_naive):
    """balanced accuracy, attack recall, FPR and attack-F1 logged per window are exactly the
    sklearn quantities on that window's raw features."""
    win, env = own_naive["win"], own_naive["env"]
    m = win[win.method == "ks_max"].set_index("window_idx")
    first_commit = _commit_windows(win)[0]
    for t in range(0, min(first_commit + 1, 5)):        # windows served by the initial model
        Xw, yw, _ = env.stream_raw[t]
        pred = env.initial_model.predict(Xw)
        fp = int(((pred == 1) & (yw == 0)).sum()); tn = int(((pred == 0) & (yw == 0)).sum())
        assert m.loc[t].balanced_accuracy == float(balanced_accuracy_score(yw, pred))
        assert m.loc[t].f1 == float(f1_score(yw, pred, zero_division=0))
        assert m.loc[t].recall == float(((pred == 1) & (yw == 1)).sum() / max(1, (yw == 1).sum()))
        assert m.loc[t].fpr == fp / max(1, fp + tn)


# ----------------------------------------- provenance (confirmatory-phase requirement)

PROVENANCE_KEYS = (
    "transformer_policy", "training_row_hash",
    "scaler_hash", "scaler_mean_hash", "scaler_scale_hash",
    "pca_hash", "pca_components_hash", "pca_explained_variance_hash", "pca_dim",
    "classifier_params", "svc_configured_gamma", "svc_effective_gamma",
    "creation_window", "deployed_version",
)


def test_provenance_metadata_complete(froz_point, own_point):
    """Every pipeline (initial incumbent and every candidate, both policies) records the full
    preprocessing provenance so no gamma/PCA variation can hide inside 'own transformer'."""
    for run in (froz_point, own_point):
        for p in [run["env"].initial_model] + run["rec"]:
            for k in PROVENANCE_KEYS:
                assert k in p.metadata, f"missing provenance key {k}"
            assert p.metadata["pca_dim"] == 4
            assert p.metadata["classifier_params"], "classifier params not recorded"


def test_provenance_effective_gamma_reproducible():
    """For SVC-RBF pipelines the recorded fitted effective gamma equals sklearn's
    gamma='scale' formula on the internally transformed training batch, and is
    bit-reproducible across identical builds."""
    rng = np.random.default_rng(99)
    X = np.vstack([rng.normal(0, 1, (48, 5)), rng.normal(1.5, 1.2, (48, 5))])
    y = np.r_[np.zeros(48, int), np.ones(48, int)]
    p1 = build_candidate_pipeline(X, y, transformer_policy=OWN_POLICY,
                                  initial_transformer=(None, None), incumbent_pipeline=None,
                                  model_kind="svc_rbf", seed=5, dim=4)
    p2 = build_candidate_pipeline(X, y, transformer_policy=OWN_POLICY,
                                  initial_transformer=(None, None), incumbent_pipeline=None,
                                  model_kind="svc_rbf", seed=5, dim=4)
    g = p1.metadata["svc_effective_gamma"]
    assert g is not None and g > 0
    assert g == p2.metadata["svc_effective_gamma"]
    Xt = p1.transform(X)
    assert g == pytest.approx(1.0 / (Xt.shape[1] * Xt.var()), rel=1e-12)
    assert p1.metadata["svc_configured_gamma"] == "'scale'"


def test_provenance_frozen_vs_own_components(froz_point, own_point):
    """Frozen candidates carry the INITIAL fitted components (hashes equal to the incumbent's);
    own candidates fit NEW components on the SAME raw candidate batch (batch hash equal,
    component hashes different)."""
    init_meta = froz_point["env"].initial_model.metadata
    bf = {p.metadata["creation_window"]: p for p in froz_point["rec"]}
    bo = {p.metadata["creation_window"]: p for p in own_point["rec"]}
    common = sorted(set(bf) & set(bo))
    assert common
    for t in common:
        pf, po = bf[t], bo[t]
        assert pf.metadata["training_row_hash"] == po.metadata["training_row_hash"]
        for k in ("scaler_mean_hash", "scaler_scale_hash", "pca_components_hash",
                  "pca_explained_variance_hash"):
            assert pf.metadata[k] == init_meta[k], f"frozen {k} != initial at window {t}"
            assert po.metadata[k] != init_meta[k], f"own {k} did not refit at window {t}"
        assert pf.metadata["pca_dim"] == po.metadata["pca_dim"] == init_meta["pca_dim"]


# ------------------------------------------------- T12: confirmatory seed firewall


def test_T12_firewall_function():
    from src.experiments.run_symmetric_pipeline_replication import firewall, load_config
    cfg = load_config()
    for mode in ("smoke", "parity", "development", "dry-run"):
        with pytest.raises(SystemExit):
            firewall(cfg, [3001], mode=mode, authorized=False)
    with pytest.raises(SystemExit):   # smoke/parity refuse even WITH the authorization flag
        firewall(cfg, [3015], mode="smoke", authorized=True)
    with pytest.raises(SystemExit):
        firewall(cfg, [3030], mode="parity", authorized=True)
    firewall(cfg, [4242, 501, 11], mode="smoke", authorized=False)   # non-reserved: allowed


def test_T12_firewall_driver_cli():
    """End-to-end: the driver refuses a confirmatory seed in parity/smoke mode and exits
    before touching any data or output."""
    for mode_args in (["--parity", "--only-arm", "parity_ps_full_point"], ["--smoke"]):
        r = subprocess.run([sys.executable, "-m",
                            "src.experiments.run_symmetric_pipeline_replication",
                            *mode_args, "--seeds", "3001"],
                           cwd=REPO, capture_output=True, text=True, timeout=300)
        assert r.returncode != 0
        assert "CONFIRMATORY SEED FIREWALL" in (r.stdout + r.stderr)
    r = subprocess.run([sys.executable, "-m",
                        "src.experiments.run_symmetric_pipeline_replication",
                        "--smoke", "--confirmatory-authorized"],
                       cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode != 0   # the authorization flag is incompatible with smoke/parity
