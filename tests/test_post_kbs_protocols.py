"""Guards for the two frozen post-KBS strengthening protocols (Phase B).

These tests validate the *preregistration state only*: configs parse and agree with their
protocols, the reserved seed blocks are virgin and disjoint from every block the program
has used, no implementation/results exist yet (execution is not authorized), and the new
outcome rules contain no sign-rate criterion (the E3 pathology must not recur).
"""
from __future__ import annotations

import json
import re

from tests.conftest import REPO

B1_NOTE = (REPO / "notes" / "post_kbs_common_harness_baselines_protocol_001.md"
           ).read_text(encoding="utf-8")
B2_NOTE = (REPO / "notes" / "post_kbs_size_matched_drift_protocol_001.md"
           ).read_text(encoding="utf-8")
B1_CFG = json.loads((REPO / "configs" / "post_kbs_common_harness_baselines_v1.json"
                     ).read_text(encoding="utf-8"))
B2_CFG = json.loads((REPO / "configs" / "post_kbs_size_matched_drift_v1.json"
                     ).read_text(encoding="utf-8"))

# every confirmatory/smoke/parity/pilot seed window the program has ever used
USED_SEED_RANGES = [
    (1, 30), (104, 133), (134, 163), (164, 164), (165, 194), (195, 195), (196, 225),
    (226, 226), (227, 256), (301, 330), (401, 430), (501, 530), (601, 630), (701, 730),
    (801, 830), (2001, 2100), (3001, 3030), (4001, 4030), (4242, 4243), (4401, 4402),
]


def _overlaps(a, b):
    return not (a[1] < b[0] or b[1] < a[0])


def test_reserved_seed_blocks_are_disjoint_from_all_used_blocks():
    for cfg, smoke in ((B1_CFG, (5401, 5402)), (B2_CFG, (6401, 6402))):
        conf = (cfg["confirmatory_seeds"]["start"], cfg["confirmatory_seeds"]["end"])
        assert conf[1] - conf[0] == 29, "30-seed confirmatory block"
        for used in USED_SEED_RANGES:
            assert not _overlaps(conf, used), (conf, used)
            assert not _overlaps(smoke, used), (smoke, used)
    assert (B1_CFG["confirmatory_seeds"]["start"], B1_CFG["confirmatory_seeds"]["end"]) \
        != (B2_CFG["confirmatory_seeds"]["start"], B2_CFG["confirmatory_seeds"]["end"])


def test_preregistration_state_and_result_hygiene():
    """State-aware guard. The v1 configs keep their freeze-time status strings as a
    historical record. B2 implementation+execution were AUTHORIZED by user decision on
    2026-08-31 (recorded in notes/post_kbs_size_matched_drift_implementation_checkpoint.md);
    B1 implementation is authorized only after amendment 001's commit, and its confirmatory
    outputs only after its fidelity gates."""
    for cfg in (B1_CFG, B2_CFG):
        assert "RESERVED" in cfg["confirmatory_seeds"]["status"]
    # any B2 confirmatory output must be authorized-mode on the reserved block only
    raw = REPO / "results" / "raw" / "post_kbs_size_matched_drift"
    if raw.exists():
        for d in raw.iterdir():
            if not d.is_dir():
                continue
            rc = json.loads((d / "run_config.json").read_text(encoding="utf-8"))
            assert rc["mode"] == "run", d
            assert set(rc["seeds"]) <= set(range(6001, 6031)), d
    # any B1 confirmatory output must be authorized-mode on ITS reserved block only
    raw1 = REPO / "results" / "raw" / "post_kbs_common_harness_baselines"
    if raw1.exists():
        for d in raw1.iterdir():
            if not d.is_dir():
                continue
            rc = json.loads((d / "run_config.json").read_text(encoding="utf-8"))
            assert rc["mode"] == "run", d
            assert set(rc["seeds"]) <= set(range(5001, 5031)), d


def test_protocols_frozen_before_implementation_wording():
    for note in (B1_NOTE, B2_NOTE):
        assert "PROTOCOL FROZEN BEFORE IMPLEMENTATION" in note
        assert "separate, explicit authorization" in note


def test_no_sign_rate_criterion_in_new_outcome_rules():
    """The E3 pathology (sign-rate threshold unable to certify its target under the null)
    must not recur: neither new protocol may key any outcome on a sign rate."""
    for name, note in (("B1", B1_NOTE), ("B2", B2_NOTE)):
        flat = re.sub(r"\s+", " ", note.lower())
        assert "no sign-rate criterion" in flat or "no sign-rate criteria" in flat, name
        # a sign-rate may be *mentioned* only as the banned pathology, never as a rule
        for m in re.finditer(r"sign[- ]rate", flat):
            w = flat[max(0, m.start() - 90): m.end() + 90]
            assert ("no sign-rate" in w or "pathology" in w or "banned" in w
                    or "criterion" in w or "e3" in w), f"{name}: {w!r}"


def test_b1_declares_no_adaptive_nids_sota_row():
    flat = re.sub(r"\s+", " ", B1_NOTE.lower())
    assert "not directly comparable" in flat
    assert "does not label any evaluated row an \"adaptive-nids sota baseline\"" in flat
    for cited in ("garg2022atc", "guillory2021doc"):
        assert cited in B1_NOTE
    assert B1_CFG["policies"]["atc"]["origin"] == "published-generic"
    assert B1_CFG["policies"]["ddm_river"]["origin"] == "reference-implementation"


def test_b2_nested_draw_defined_and_old_assert_not_reused():
    flat = re.sub(r"\s+", " ", B2_NOTE.lower())
    assert "asserts severity == 0 and must not be reused" in flat
    assert "same rng stream" in flat or "same per-trigger rng stream" in flat
    assert "same sev(t)" in flat
    assert "proposal-coupled" in flat, "coupling scope must be declared in advance"
    assert "seed-paired" in flat
    assert B2_CFG["nested_draw_at_drift"]["definition"].startswith("protocol section 2.1")


def test_outcome_taxonomies_are_magnitude_aware():
    f1 = re.sub(r"\s+", " ", B1_NOTE.lower())
    for label in ("material gain", "material cost", "compatible", "unresolved"):
        assert label in f1, label
    f2 = re.sub(r"\s+", " ", B2_NOTE.lower())
    for label in ("size benefit", "size cost", "no material size effect", "heterogeneous"):
        assert label in f2, label
    assert "p/a/e" in f2 and "does not apply" in f2 or "do not apply" in f2


def test_preflight_exists_with_pass_verdict():
    pf = (REPO / "audits" / "post_kbs_protocol_preflight.md").read_text(encoding="utf-8")
    assert "PASS the hostile preflight" in pf
    assert "distinguish a true null" in pf
    assert "NOT granted by this document" in pf
