"""v1.23.0 immutability and additive v1.24.0 integrity-sensitivity sealing guards.

The 185 historical manifest entries must be byte-identical to their state at the final
manuscript-integration commit (19d5a80), the 22 post-KBS CSVs must be pinned with their exact
on-disk hashes, the verifier must report no unpinned extras, and every version surface must
agree on 1.24.0. Hash verification is never weakened here; these tests only add pins.
"""
import hashlib
import json
import re
import subprocess

import pytest

from tests.conftest import REPO

MANIFEST = REPO / "results" / "tables" / "MANIFEST.sha256"
POST_KBS_DIRS = ("results/tables/post_kbs_size_matched_drift_001",
                 "results/tables/post_kbs_common_harness_baselines_001")
SENSITIVITY_DIRS = ("results/tables/ijis_exact_value_disjoint_b2_001",
                    "results/tables/ijis_exact_value_disjoint_b1_001")
INTEGRATION_COMMIT = "19d5a8039d9122b0315fa15e27d8f1e00ce58d52"


def _pins(text: str) -> dict[str, str]:
    out = {}
    for line in text.splitlines():
        if line.strip():
            h, p = line.split(None, 1)
            out[p.strip()] = h
    return out


def test_manifest_is_207_plus_23():
    pins = _pins(MANIFEST.read_text(encoding="utf-8"))
    assert len(pins) == 230
    post = [p for p in pins if any(p.startswith(d + "/") for d in POST_KBS_DIRS)]
    sensitivity = [p for p in pins if any(p.startswith(d + "/") for d in SENSITIVITY_DIRS)]
    assert len(post) == 22
    assert len(sensitivity) == 23
    assert len(pins) - len(sensitivity) == 207


def test_post_kbs_pins_match_disk_and_are_tracked():
    pins = _pins(MANIFEST.read_text(encoding="utf-8"))
    tracked = set(subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                                 text=True).stdout.split("\n"))
    for d in POST_KBS_DIRS:
        csvs = sorted((REPO / d).glob("*.csv"))
        assert csvs, d
        for f in csvs:
            p = f.relative_to(REPO).as_posix()
            assert p in pins, f"post-KBS CSV not pinned: {p}"
            assert hashlib.sha256(f.read_bytes()).hexdigest() == pins[p], p
            assert p in tracked, p
        assert (d + "/CLAIM_INTERPRETATION.json") in tracked, d


def test_v1_23_pins_unchanged_since_immutable_tag():
    r = subprocess.run(["git", "show", "v1.23.0:results/tables/MANIFEST.sha256"],
                       cwd=REPO, capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("v1.23.0 tag not available in this checkout (shallow clone)")
    old = _pins(r.stdout)
    assert len(old) == 207
    new = _pins(MANIFEST.read_text(encoding="utf-8"))
    changed = [p for p, h in old.items() if new.get(p) != h]
    assert not changed, f"historical pins changed at sealing: {changed[:5]}"


def test_verifier_reports_zero_unpinned_extras():
    r = subprocess.run(["python", "-m", "src.analysis.verify_results_manifest"], cwd=REPO,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-500:]
    assert "230 pinned CSVs match" in r.stdout and "(0 unpinned extras)" in r.stdout, r.stdout[-300:]


def test_version_surfaces_agree_on_1_24_0():
    cff = (REPO / "CITATION.cff").read_text(encoding="utf-8")
    zen = json.loads((REPO / ".zenodo.json").read_text(encoding="utf-8"))
    bib = (REPO / "manuscript" / "references.bib").read_text(encoding="utf-8")
    assert 'version: "1.24.0"' in cff
    assert zen["version"] == "1.24.0"
    assert re.search(r"note\s*=\s*\{Version 1\.24\.0\}", bib)
    assert "10.5281/zenodo.21322256" in cff and "zenodo.21322256" in bib, "concept DOI retained"
    for name in ("main.tex", "main_ieee.tex"):
        t = re.sub(r"\s+", " ", (REPO / "manuscript" / name).read_text(encoding="utf-8"))
        assert "artifact version v1.24.0" in t, name
        assert "previous v1.23.0 release remains immutable" in t, name


def test_ledger_and_final_manifest_register_historical_and_sensitivity_b1_b2():
    led = (REPO / "results" / "final_experiment_ledger.csv").read_text(encoding="utf-8")
    for bid, seeds in (("post_kbs_size_matched_drift", "6001-6030"),
                       ("post_kbs_common_harness_baselines", "5001-5030"),
                       ("ijis_exact_value_disjoint_b2", "7001-7030"),
                       ("ijis_exact_value_disjoint_b1", "8001-8030")):
        assert bid in led, bid
        assert seeds in led, seeds
    for tag in ("tab:size_matched_drift", "tab:common_harness", "tab:synthesis"):
        assert tag in led, tag
    m = json.loads((REPO / "results" / "final_manifest.json").read_text(encoding="utf-8"))
    assert m["artifact_version"] == "1.24.0"
    pk = m["post_kbs_confirmatory_v1_23"]
    assert pk["b2_size_matched_drift"]["registered_outcome"] == "HOMOGENEOUS-SIZE BENEFIT"
    assert pk["b2_size_matched_drift"]["confirmatory_seeds"] == "6001-6030"
    assert pk["b1_common_harness"]["confirmatory_seeds"] == "5001-5030"
    assert pk["b1_common_harness"]["state_of_the_art_claim"] is False
    assert pk["b1_common_harness"]["end_to_end_adaptive_nids_system_reproduced"] is False
    assert pk["sealing"]["total_pinned_csvs"] == 207
    assert pk["sealing"]["historical_pinned_csvs"] == 185
    assert set(pk["b1_common_harness"]["statements_holding"].get("S4", [])) == {"atc", "enscal"}
    assert m["size_matched_control_v1_22"]["registered_outcome"] == "ATTENUATION"
    x = m["exact_value_disjoint_v1_24"]
    assert x["b2"]["registered_outcome"] == "PARTIAL ROBUSTNESS"
    assert x["b1"]["registered_robustness"] == "PARTIALLY ROBUST"
    assert x["role_integrity"]["exact_x_cross_role_overlap_groups"] == 0
    assert x["sealing"]["historical_v1_23_pinned_csvs"] == 207
    assert x["sealing"]["sensitivity_pinned_csvs"] == 23
    assert x["sealing"]["total_pinned_csvs"] == 230
