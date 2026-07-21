"""P10 mandatory tests: manuscript/tables/README consistency.

test_main_tables_final_only  -- the main body inputs exactly the final table set (no superseded
                                or v1 tables); the v1 tables live only in the supplement.
test_no_superseded_claims    -- the living documents carry none of the retracted/stale claims
                                the final hostile review removed.
test_claim_table_consistency -- every pinned numeric claim matches the artifacts (the 439-check
                                audit passes end to end).
"""
from __future__ import annotations

import re
import subprocess
import sys

from tests.conftest import REPO

FINAL_BODY_TABLES = {
    "table_v2_confirmatory", "table_policy_frontier",
    "table_causal_probe", "table_zero_drift", "table_amendment009",
    "table_harm_generality",
    # final-q1 additions (table_symmetric_ab and table_temporal_streams moved to the
    # supplement: superseded in scope by the merged mechanism table and the pre-enumerated
    # chronological matrix respectively)
    "table_budget_frontier", "table_ab_equivalence",
    "table_chronological_q1", "table_operational_e2e",
}
V1_SUPPLEMENT_TABLES = {
    "table1_regime_taxonomy", "table2_phase2_gate_summary", "table3_phase2_paired_ci",
    "table4_oracle_regret", "table5_phase1_negative", "table6_downstream_generalization",
    "table7_mechanism_law_robustness", "table_temporal_streams",
    # final-q1: moved out of the body to hold it at 27 pages; the text keeps the summary
    "table_label_cost",
}


def _inputs(tex: str, folder: str) -> set[str]:
    return set(re.findall(r"\\input\{" + folder + r"/([\w]+)\.tex\}", tex))


def test_main_tables_final_only():
    main = (REPO / "manuscript" / "main.tex").read_text(encoding="utf-8")
    supp = (REPO / "manuscript" / "supplement.tex").read_text(encoding="utf-8")
    ieee = (REPO / "manuscript" / "main_ieee.tex").read_text(encoding="utf-8")
    assert _inputs(main, "tables") == FINAL_BODY_TABLES
    assert _inputs(ieee, "tables_ieee") == FINAL_BODY_TABLES
    assert _inputs(supp, "tables") == V1_SUPPLEMENT_TABLES
    assert "\\appendix" not in main


SUPERSEDED_PATTERNS = [
    (r"which we do not implement", "lifetime budget IS implemented (VBC-SG)"),
    (r"class-imbaled", "typo fixed in the final review"),
    (r"1\.17,\s*[-−]0\.87", "stale 004-spec hierarchical CI (regime x seed CI is [-1.61,-0.43])"),
    (r"74\\?% fewer", "probe-reuse two-stage figure; the split variant trains 69% fewer"),
    (r"§5\.10|\\S5\.10", "pre-Fase-E section numbering"),
    (r"fails safe", "banned claim (amendment 008)"),
    (r"full safety/benefit at natural prevalence", "retracted claim (amendment 006)"),
    (r"all 240\+", "stale audit count"),
    (r"19\.5 to [-−]4\.5[^0-9]", "worst adaptive gain is -4.6"),
    # final-q1 P0.4 overclaim sweep (protocol q1_max_protocol.md)
    (r"empirically,? safe across", "point gate is harm-reducing, not 'safe' (Sol blocker 4)"),
    (r"is fully safe", "banned: risk gates 'commit nothing', they are not 'fully safe'"),
    (r"gap statistically zero", "D2: non-significance is not equivalence"),
    (r"mechanism we (now )?identify\b", "D2: representation-ownership interaction wording"),
    (r"so we say ``identified''", "D2: equivalence not established at pilot precision"),
    (r"modeled for the probe but not for the candidate", "P0.2: candidate latency IS modeled"),
    (r"anytime validity permits continuation", "D1: replaced by the three continuation modes"),
    (r"universally safe", "banned vocabulary (P0.4)"),
    (r"predicts nothing", "banned since amendment 011"),
]

LIVING_DOCS = ["manuscript/main.tex", "manuscript/main_ieee.tex", "manuscript/supplement.tex",
               "manuscript/highlights.md", "README.md", "REPRODUCE.md"]


def test_no_superseded_claims():
    hits = []
    for doc in LIVING_DOCS:
        text = (REPO / doc).read_text(encoding="utf-8")
        for pat, why in SUPERSEDED_PATTERNS:
            for m in re.finditer(pat, text):
                hits.append(f"{doc}: {m.group(0)!r} ({why})")
    assert not hits, "superseded/retracted claims found:\n" + "\n".join(hits)


def test_claim_table_consistency():
    r = subprocess.run([sys.executable, "-m", "src.analysis.audit_paper2_claims"],
                       cwd=REPO, capture_output=True, text=True, timeout=600)
    m = re.search(r"AUDIT: (\d+)/(\d+) checks pass", r.stdout)
    assert m, f"audit produced no verdict:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}"
    assert r.returncode == 0 and m.group(1) == m.group(2), \
        f"audit failed: {m.group(0)}\n" + "\n".join(
            l for l in r.stdout.splitlines() if "FAIL" in l)
