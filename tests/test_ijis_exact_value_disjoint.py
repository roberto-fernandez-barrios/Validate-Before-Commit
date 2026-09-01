"""Invariant tests for the final IJIS exact-feature-group-disjoint sensitivity."""
from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from src.experiments.run_paper2_progressive_readaptation import Pools
from src.experiments import run_paper2_readaptation_v2 as v2
from src.experiments import run_symmetric_pipeline_replication as driver


def _synthetic_pools() -> Pools:
    # Thousands of one-row groups make the frozen 0.50-pp tolerance attainable. The first
    # exact X appears with contradictory labels and ref/current membership.
    rng = np.random.default_rng(991)
    arrays = [rng.normal(loc=10 * i, size=(1200, 5)) for i in range(4)]
    shared = np.array([0.0, -0.0, 7.0, 8.0, 9.0])
    arrays[0][0] = shared
    arrays[1][0] = shared              # same X, opposite label
    arrays[2][0] = shared              # same X, current membership
    arrays[0][1:8] = arrays[0][0]      # within-group multiplicity must survive
    return Pools(*arrays)


def _key_rows(a: np.ndarray) -> set[bytes]:
    return {v2._canonical_feature_digest(row) for row in a}


def test_historical_source_row_split_is_bit_identical_to_reference():
    pools = _synthetic_pools()
    seed = 17
    actual = v2.split_pools(pools, seed)
    rng = np.random.default_rng(seed + 500_000)
    for name in ("ref_benign", "ref_attack", "cur_benign", "cur_attack"):
        source = getattr(pools, name)
        idx = rng.permutation(len(source))
        a = int(len(source) * 0.5)
        b = a + int(len(source) * 0.3)
        for role, expected in (
            ("window", source[idx[:a]]),
            ("train", source[idx[a:b]]),
            ("probe", source[idx[b:]]),
        ):
            assert np.array_equal(getattr(actual[role], name), expected)


def test_exact_group_split_zero_overlap_preserves_rows_labels_and_multiplicity():
    pools = _synthetic_pools()
    roles, audit = v2.split_pools_feature_group_disjoint(pools, 7401)
    assert audit["verdict"] == "PASS"
    assert audit["total_input_rows"] == audit["total_output_rows"] == 4800
    assert audit["multiplicity_preserved"] is True
    assert audit["conflicting_label_x_groups"] >= 1
    assert audit["conflicting_label_rows"] >= 9
    assert audit["max_abs_fraction_deviation_pp"] <= 0.5
    for pair in ("window_train", "window_probe", "train_probe"):
        assert audit[f"exact_x_overlap_groups_{pair}"] == 0

    role_keys = []
    for role in ("window", "train", "probe"):
        role_keys.append(set().union(*[
            _key_rows(getattr(roles[role], name))
            for name in ("ref_benign", "ref_attack", "cur_benign", "cur_attack")
        ]))
    assert role_keys[0].isdisjoint(role_keys[1])
    assert role_keys[0].isdisjoint(role_keys[2])
    assert role_keys[1].isdisjoint(role_keys[2])

    # The contradictory-label shared group is wholly retained in exactly one role.
    shared = v2._canonical_feature_digest(np.array([0.0, 0.0, 7.0, 8.0, 9.0]))
    containing = [r for r, keys in zip(("window", "train", "probe"), role_keys) if shared in keys]
    assert len(containing) == 1
    chosen = roles[containing[0]]
    counts = []
    for name in ("ref_benign", "ref_attack", "cur_benign", "cur_attack"):
        counts.append(sum(v2._canonical_feature_digest(x) == shared for x in getattr(chosen, name)))
    assert counts == [8, 1, 1, 0]


def test_exact_group_split_is_deterministic_and_seed_dependent():
    pools = _synthetic_pools()
    one, audit1 = v2.split_pools_feature_group_disjoint(pools, 8401)
    two, audit2 = v2.split_pools_feature_group_disjoint(pools, 8401)
    other, _ = v2.split_pools_feature_group_disjoint(pools, 8402)
    assert audit1 == audit2
    for role in ("window", "train", "probe"):
        for name in ("ref_benign", "ref_attack", "cur_benign", "cur_attack"):
            assert np.array_equal(getattr(one[role], name), getattr(two[role], name))
    assert any(
        not np.array_equal(getattr(one[r], n), getattr(other[r], n))
        for r in ("window", "train", "probe")
        for n in ("ref_benign", "ref_attack", "cur_benign", "cur_attack")
    )


def test_signed_zero_is_canonical_but_no_rounding_occurs():
    a = np.array([-0.0, 1.0, 2.0])
    b = np.array([+0.0, 1.0, 2.0])
    c = np.array([+0.0, 1.0, np.nextafter(2.0, 3.0)])
    assert v2._canonical_feature_digest(a) == v2._canonical_feature_digest(b)
    assert v2._canonical_feature_digest(a) != v2._canonical_feature_digest(c)


def test_nested_candidate_prefix_and_severity_are_unchanged():
    pools = _synthetic_pools()
    roles, _ = v2.split_pools_feature_group_disjoint(pools, 7402)
    args = SimpleNamespace(
        adapt_size_per_class=512,
        train_size_per_class=2000,
        nested_draw_domain="drift",
        adapt_strategy="full_replace",
    )
    severity = 0.625
    x512, y512 = v2.nested_candidate_draw(
        roles["train"], args, 512, severity, np.random.default_rng(12345)
    )
    x2000, y2000 = v2.nested_candidate_draw(
        roles["train"], args, 2000, severity, np.random.default_rng(12345)
    )
    assert np.array_equal(x2000[: len(x512)], x512)
    assert np.array_equal(y2000[: len(y512)], y512)
    assert len(x512) == 1024 and len(x2000) == 4000


def test_registered_configs_enumerate_complete_matrices_and_firewalls():
    b2 = driver.load_config("configs/ijis_exact_value_disjoint_b2_v1.json")
    b1 = driver.load_config("configs/ijis_exact_value_disjoint_b1_v1.json")
    assert len(driver.confirmatory_arms(b2)) == 21
    assert len(driver.confirmatory_arms(b1)) == 96
    assert all(a["flags"]["--role-split-mode"] == "exact_feature_group"
               for a in driver.confirmatory_arms(b2) + driver.confirmatory_arms(b1))
    assert {a["tag"] for a in driver.smoke_arms(b2)} == set(b2["smoke_arms"])
    assert {a["tag"] for a in driver.smoke_arms(b1)} == set(b1["smoke_arms"])
    with pytest.raises(SystemExit, match="CONFIRMATORY SEED FIREWALL"):
        driver.firewall(b2, [7001], mode="smoke", authorized=False)
    with pytest.raises(SystemExit, match="CONFIRMATORY SEED FIREWALL"):
        driver.firewall(b1, [8001], mode="development", authorized=False)


def test_parser_defaults_to_historical_mode_and_accepts_explicit_new_mode(tmp_path):
    parser = v2.build_parser()
    common = [
        "--data-ref", "ref.csv", "--data-cur", "cur.csv", "--outdir", str(tmp_path),
    ]
    assert parser.parse_args(common).role_split_mode == "source_row"
    assert parser.parse_args(common + ["--role-split-mode", "exact_feature_group"]).role_split_mode \
        == "exact_feature_group"
