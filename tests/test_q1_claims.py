"""final-q1 mandatory tests: evidence tiers, strict baseline, latency documentation, and
main/supplement consistency (protocol q1_max_protocol.md)."""
from __future__ import annotations

import json
import re

import pytest

from tests.conftest import REPO

MAIN = (REPO / "manuscript" / "main.tex")
SUPP = (REPO / "manuscript" / "supplement.tex")


def test_evidence_tier_labels():
    text = MAIN.read_text(encoding="utf-8")
    assert "Five tiers of evidence" in text
    for marker in ("Registered confirmatory core", "Registered follow-ups",
                   "Causal and operational feasibility", "External boundary", "Exploratory"):
        assert marker in text, f"evidence tier missing: {marker}"
    # the confirmatory replication must be labeled internal; "external replication" may only
    # appear negated ("not an external replication")
    assert re.search(r"\\emph\{internal\} replication", text)
    lowered = text.lower().replace("not an external replication", "")
    assert "external replication" not in lowered


def test_strict_baseline_present():
    causal = (REPO / "manuscript" / "tables" / "table_causal_probe.tex").read_text(encoding="utf-8")
    assert "strict" in causal.lower(), "strict gate missing from the causal comparison table"
    zero = (REPO / "manuscript" / "tables" / "table_zero_drift.tex").read_text(encoding="utf-8")
    main = MAIN.read_text(encoding="utf-8")
    assert "reject-ties" in main or "strict" in zero.lower()


def test_latency_manifest_matches_manuscript():
    text = MAIN.read_text(encoding="utf-8")
    assert "tab:latency" in text, "latency semantics table missing from the manuscript"
    for knob in ("--probe-latency", "--candidate-latency", "--defer-windows"):
        assert knob.replace("--", "") in text.replace("-", "").replace("\\", "") or knob in text
    mf = REPO / "results" / "final_manifest.json"
    if not mf.exists():
        pytest.skip("final_manifest.json not yet generated in this checkout")
    m = json.loads(mf.read_text(encoding="utf-8"))
    lat = m["label_latencies"]
    assert set(lat["probe"]) >= {0, 5, 20}
    assert set(lat["candidate"]) >= {0, 5, 20}


def test_main_supplement_consistency():
    main = MAIN.read_text(encoding="utf-8")
    supp = SUPP.read_text(encoding="utf-8")
    # every "S5.x of the main paper" pointer must target an existing main subsection of Sec. 5
    n_results_subsecs = len(re.findall(r"\\subsection\{", main.split(r"\section{Results}")[1]
                                       .split(r"\section{Discussion}")[0]))
    for m in re.finditer(r"\\S5\.(\d+) of the main paper", supp):
        assert int(m.group(1)) <= n_results_subsecs, f"dead pointer: S5.{m.group(1)}"
    # Proposition 1's proof must exist in the supplement and be referenced from the main body
    assert "Proposition 1" in main and "Proof of Proposition 1" in supp
    assert "S4" in main.split("Proposition 1")[1][:2000]


def test_abstract_length_within_venue_limit():
    """Fase-F regression guard (finding F2): the abstract had grown to 533 words across
    amendments, more than double the venue norm, which is a desk-reject risk. It is rewritten
    to ~265; this test fails if it drifts materially above the limit again."""
    text = MAIN.read_text(encoding="utf-8")
    abstract = text.split(r"\begin{abstract}")[1].split(r"\end{abstract}")[0]
    stripped = re.sub(r"\\[a-zA-Z]+\*?", " ", abstract)
    stripped = re.sub(r"[{}$\\]", " ", stripped)
    stripped = re.sub(r"-{2,}", " ", stripped)
    n = len(stripped.split())
    assert n <= 290, f"abstract is {n} words; the venue norm is ~250 (hard guard at 290)"


def test_chronological_replay_count_consistent():
    """Fase-F regression guard (finding F3): 'six replays' lingered in the contributions,
    the evidence tiers and Limitations after the matrix grew to thirteen. Any mention of a
    replay TOTAL must say thirteen; 'these six' scoping the first set is allowed."""
    text = MAIN.read_text(encoding="utf-8")
    scoping = ("these", "initial", "above", "first set")
    bad = []
    for m in re.finditer(r"\b[Ss]ix (?:registered |real )?(?:chronological )?replays", text):
        window = text[max(0, m.start() - 60): m.end() + 60].lower()
        if not any(w in window for w in scoping):
            bad.append(text[m.start():m.end()])
    assert not bad, (f"unscoped mention(s) of six replays: {bad} — the matrix has thirteen; "
                     "a mention of the first set must scope itself ('these', 'initial', 'above')")


def test_frontier_headline_not_misattributed():
    """Fase-F regression guard (finding F7): 93% of naive's benefit is the POOLED EB-CS
    variant; the fully stratified VBC-SG reaches 81%. Wherever the 93% headline appears
    outside the results section, the 81% qualifier must appear nearby."""
    for doc in ("manuscript/main.tex", "README.md"):
        text = (REPO / doc).read_text(encoding="utf-8")
        for m in re.finditer(r"93\\?%", text):
            window = text[max(0, m.start() - 400): m.start() + 400]
            assert "81" in window, (
                f"{doc}: the 93% frontier headline appears without the 81% stratified "
                "qualifier nearby — that misattributes a pooled result to VBC-SG")


def test_lifetime_policy_nonvacuity_reported():
    frontier = REPO / "results" / "tables" / "paper2_final_q1" / "budget_frontier.csv"
    if not frontier.exists():
        pytest.skip("budget frontier (Fase C) not yet run")
    text = MAIN.read_text(encoding="utf-8")
    assert ("formal risk endpoint" in text) or ("non-vacuous" in text) or \
           ("nonvacuous" in text), \
        "Fase C ran but the manuscript reports neither a non-vacuous operating point nor " \
        "the registered endpoint sentence"
