"""Guards for amendment 001 of the common-harness baselines protocol (B1 v2).

Pin the amended preregistration state: primary candidate size 2,000/class, the exact
policy list and per-policy origins/budgets, primary/secondary family status, the retained
(still-virgin) seed firewall, and the magnitude-aware outcome rules. The original v1
protocol/config stay frozen and unmodified.
"""
from __future__ import annotations

import json
import re

from tests.conftest import REPO

AMD = (REPO / "notes" / "post_kbs_common_harness_baselines_amendment_001.md"
       ).read_text(encoding="utf-8")
V1 = json.loads((REPO / "configs" / "post_kbs_common_harness_baselines_v1.json"
                 ).read_text(encoding="utf-8"))
V2 = json.loads((REPO / "configs" / "post_kbs_common_harness_baselines_v2.json"
                 ).read_text(encoding="utf-8"))

USED_SEED_RANGES = [
    (1, 30), (104, 133), (134, 163), (164, 164), (165, 194), (195, 195), (196, 225),
    (226, 226), (227, 256), (301, 330), (401, 430), (501, 530), (601, 630), (701, 730),
    (801, 830), (2001, 2100), (3001, 3030), (4001, 4030), (4242, 4243), (4401, 4402),
    (6001, 6030), (6401, 6402),
]


def test_v1_untouched_and_superseded_pointer():
    assert V2["supersedes"].endswith("post_kbs_common_harness_baselines_v1.json")
    assert "NOT authorized" in V1["implementation_status"]  # v1 keeps its freeze-time state
    assert V1["confirmatory_seeds"]["start"] == 5001


def test_primary_size_is_2000_and_secondary_512():
    assert V2["primary_candidate_size_per_class"] == 2000
    assert V2["secondary_candidate_size_per_class"] == 512
    assert V2["incumbent_train_size_per_class"] == 2000
    assert V2["transformer_policies"] == ["own_transformer_per_model"]
    f = re.sub(r"\s+", " ", AMD.lower())
    assert "primary condition (all registered inference): candidate size 2,000 flows/class" in f


def test_policy_list_and_origins():
    assert set(V2["primary_policies"]) == {"naive", "point", "strict", "atc", "doc",
                                           "enscal", "replay", "ddm", "adwin"}
    assert set(V2["secondary_policies_512"]) == {"naive", "point", "strict", "atc", "doc",
                                                 "enscal"}
    assert V2["policies"]["atc"]["origin"] == "published-generic"
    assert V2["policies"]["doc"]["origin"] == "published-generic"
    assert V2["policies"]["ddm"]["origin"] == "reference-implementation"
    assert V2["policies"]["adwin"]["origin"] == "reference-implementation"
    assert V2["policies"]["enscal"]["origin"] == "standard-baseline"
    assert V2["policies"]["replay"]["origin"] == "standard-baseline"
    # DDM/ADWIN/replay deliberately absent from the 512 block, with frozen rationale
    for k in ("ddm", "adwin", "replay"):
        assert k not in V2["secondary_policies_512"]
    assert "not duplicated at 512" in re.sub(r"\s+", " ", AMD.lower())


def test_evidence_budgets_documented():
    f = re.sub(r"\s+", " ", AMD.lower())
    assert "512-row labeled validation sample" in f          # ATC/DoC budget
    assert "800/stream" in f or "800 monitoring labels" in f  # DDM/ADWIN budget
    assert "not equalized" in f or "reported, not equalized" in f
    assert V2["policies"]["atc"]["flags"]["--gate-val-size"] == "512"
    assert V2["policies"]["ddm"]["flags"]["--monitor-labels"] == "8"


def test_families_primary_secondary_status():
    fams = V2["statistical_families"]
    assert fams["PF1_zero_drift_loss_avoidance_2000"]["status"] == "primary"
    assert fams["PF2_full_drift_benefit_retention_2000"]["status"] == "primary"
    assert fams["PF3_estimators_vs_point_2000"]["status"] == "primary"
    assert fams["SF4_512_sensitivity"]["status"] == "secondary"
    assert "secondary" in fams["SF5_method_x_size_interaction"]["status"]
    assert fams["PF1_zero_drift_loss_avoidance_2000"]["contrasts"] == 18
    assert fams["PF3_estimators_vs_point_2000"]["contrasts"] == 12
    assert fams["SF5_method_x_size_interaction"]["contrasts"] == 30
    assert "DESCRIPTIVE" in V2["anchor_contrasts_note"]


def test_no_sign_rate_and_magnitude_aware_rules():
    for text in (AMD, json.dumps(V2)):
        flat = re.sub(r"\s+", " ", text.lower())
        for m in re.finditer(r"sign[- ]rate", flat):
            w = flat[max(0, m.start() - 90): m.end() + 90]
            assert "no sign-rate" in w or "anywhere" in w, w
    assert "MATERIAL GAIN / MATERIAL COST / COMPATIBLE / UNRESOLVED" in V2["outcome_rules"]


def test_seed_block_retained_and_still_disjoint():
    conf = (V2["confirmatory_seeds"]["start"], V2["confirmatory_seeds"]["end"])
    assert conf == (5001, 5030)
    assert V2["smoke_seeds"] == [5401, 5402]
    for used in USED_SEED_RANGES:
        assert conf[1] < used[0] or used[1] < conf[0], (conf, used)
    assert "RESERVED" in V2["confirmatory_seeds"]["status"]
    f = re.sub(r"\s+", " ", AMD.lower())
    assert "never been executed" in f or "no run ever occurred" in f or \
        "no experimental run" in f


def test_arm_count_and_expected_arms():
    n = 6 * (1 + len(V2["primary_policies"]) + len(V2["secondary_policies_512"]))
    assert n == V2["expected_arms"] == 96


def test_amendment_precedes_implementation_and_execution():
    assert "frozen BEFORE any implementation" in AMD
    assert "AMENDED PREREGISTRATION" in V2["implementation_status"]
    # no implementation or results may exist at amendment-freeze time; after the B1
    # implementation commit these paths become legitimate, guarded by the fidelity gates
    pf = (REPO / "audits" / "post_kbs_common_harness_amendment_preflight.md"
          ).read_text(encoding="utf-8")
    assert "AMENDMENT PASSES" in pf
    assert "authorizes neither" in pf
