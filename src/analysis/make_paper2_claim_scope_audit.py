"""q1-final-patch v1.20.1 (Block E): machine-readable claim-scope audit.

One row per load-bearing claim: what it says, what evidence tier backs it, the unit of
analysis, which multiplicity family (if any) covers it, its operational scope, and the
wording that is allowed vs forbidden for it. `status` is computed live where a structural
check is possible ("verified" = every allowed-wording anchor found and every forbidden
phrase absent across the scanned claim surfaces), else "declared".

Output: results/tables/paper2_final_q1/claim_scope_audit.csv
The main claims audit (audit_paper2_claims) requires every row to be verified.
"""
from __future__ import annotations

import os
import re

import pandas as pd

OUT = "results/tables/paper2_final_q1"
SURFACES = [
    "manuscript/main.tex", "manuscript/main_ieee.tex", "manuscript/supplement.tex",
    "manuscript/tables/table_budget_frontier.tex", "manuscript/tables/table_operational_e2e.tex",
    "manuscript/tables/table_chronological_q1.tex", "manuscript/tables/table_ab_equivalence.tex",
    "manuscript/tables_ieee/table_budget_frontier.tex",
    "manuscript/tables_ieee/table_operational_e2e.tex",
    "manuscript/highlights.md", "README.md", "REPRODUCE.md",
]


def load_texts() -> str:
    parts = []
    for p in SURFACES:
        if os.path.exists(p):
            parts.append(re.sub(r"\s+", " ", open(p, encoding="utf-8").read().lower()))
    return " \n ".join(parts)


CLAIMS = [
    dict(claim_id="gate_vs_naive_ton",
         claim_text_short="b=32 gate beats always-deploying on ToN (both detectors)",
         evidence_tier="registered confirmatory core",
         primary_source="results/tables/paper2_v2_replication_001/paired_ci.csv",
         unit_of_analysis="seed-level paired difference (30 seeds)",
         multiplicity_family="confirmatory core (Holm, 6 tests)",
         operational_scope="balanced pool-based streams",
         allowed=["lp32"], forbidden=[]),
    dict(claim_id="benefit_preservation",
         claim_text_short="benefit/marginal regimes: gate preserves naive's benefit",
         evidence_tier="registered confirmatory core (non-inferiority)",
         primary_source="results/tables/paper2_v2_replication_001/verdict.csv",
         unit_of_analysis="seed-level paired difference vs pre-registered margin (-0.3)",
         multiplicity_family="CI/margin criterion, pre-registered (not a p-value family)",
         operational_scope="balanced pool-based streams",
         allowed=[], forbidden=[]),
    dict(claim_id="degradation_headroom",
         claim_text_short="incumbent health predicts update value (registered prediction)",
         evidence_tier="registered prediction test + per-trigger hierarchical model",
         primary_source="results/tables/paper2_decision_quality_005/hierarchical_model.csv",
         unit_of_analysis="per-trigger, cluster (seed) bootstrap",
         multiplicity_family="descriptive/registered-prediction (no family)",
         operational_scope="balanced pool-based streams; SVC-RBF generator family",
         allowed=[], forbidden=[]),
    dict(claim_id="preprocessing_ownership",
         claim_text_short="harm mechanism = preprocessing ownership (standardizer)",
         evidence_tier="registered A/B control + decomposition",
         primary_source="results/tables/paper2_final_kbs/ab_equivalence.csv",
         unit_of_analysis="seed-level role-randomized gap",
         multiplicity_family="pre-declared sign criteria (4)",
         operational_scope="evaluated SVC-RBF pipeline",
         allowed=[], forbidden=[]),
    dict(claim_id="own_transformer_equivalence",
         claim_text_short="own-transformer gap equivalent to zero (+/-1.0 BA)",
         evidence_tier="registered follow-up, bootstrap CI-based equivalence",
         primary_source="results/tables/paper2_final_kbs/ab_equivalence.csv",
         unit_of_analysis="seed-level gap, 100 confirmatory seeds",
         multiplicity_family="pre-registered margin criterion (interval-inclusion TOST)",
         operational_scope="evaluated SVC-RBF pipeline, three benchmarks",
         allowed=["bootstrap ci-based equivalence"],
         forbidden=["exact tost p-value"]),
    dict(claim_id="point_gate_32_labels",
         claim_text_short="32-label point gate converts avg harm to avg benefit",
         evidence_tier="registered confirmatory core",
         primary_source="results/tables/paper2_v2_replication_001/summary.csv",
         unit_of_analysis="seed-level paired difference (30 seeds)",
         multiplicity_family="confirmatory core (Holm)",
         operational_scope="controlled balanced-probe confirmatory setting ONLY",
         allowed=["controlled balanced-probe confirmatory setting"],
         forbidden=["32 labels suffice", "a few labels are enough",
                    "both budgets are realistic", "cheap and robust",
                    "validation costs little and protects"]),
    dict(claim_id="vbc_sg_formal_guarantee",
         claim_text_short="VBC-SG: stratified anytime-valid per-class guarantee",
         evidence_tier="design + registered budget frontier",
         primary_source="results/tables/paper2_final_q1/budget_frontier.csv",
         unit_of_analysis="per-proposal confidence sequences (alpha spending)",
         multiplicity_family="formal CS guarantee (not a sample p-value)",
         operational_scope="balanced stratified probes; Cohort-sim resampling",
         allowed=[], forbidden=["zero probability of harm"]),
    dict(claim_id="deployment_long_budget",
         claim_text_short="deployment-long guarantee non-vacuous within evaluated budget",
         evidence_tier="registered budget frontier (BH, 15 cells)",
         primary_source="results/tables/paper2_final_q1/budget_frontier.csv",
         unit_of_analysis="seed-level paired gain (30 seeds/cell)",
         multiplicity_family="frontier block (BH, 15)",
         operational_scope="balanced-probe adjudication budget; acquisition cost not measured",
         allowed=["non-vacuous within the evaluated balanced-probe adjudication budget"],
         forbidden=["affordable rather than vacuous", "guarantee is affordable"]),
    dict(claim_id="zero_observed_harmful",
         claim_text_short="0 harmful among 506 H5-evaluable commits (14 censored)",
         evidence_tier="registered frontier, complete resolution-log accounting",
         primary_source="results/raw/q1fc_*/paper2_v2_resolution_log.csv",
         unit_of_analysis="factual count; commits clustered in seeds/scenarios/configs",
         multiplicity_family="none (descriptive count; no binomial bound)",
         operational_scope="registered frontier sweep only",
         allowed=["not treated as 506 independent bernoulli trials"],
         forbidden=["0.73", "0.726", "clopper", "eliminates harmful commits",
                    "zero probability of harm"]),
    dict(claim_id="chronological_boundary",
         claim_text_short="13 replays: no net harm; UNSW healthy: point/strict win; Wed unresolved",
         evidence_tier="external boundary (chronological)",
         primary_source="results/tables/paper2_final_q1/chronological_replays.csv",
         unit_of_analysis="seed-level paired gain per replay (30 seeds)",
         multiplicity_family="chronological block (BH, 7; strict only)",
         operational_scope="subsampled chronological replays",
         allowed=["unresolved counterexample"],
         forbidden=["every gate beats"]),
    dict(claim_id="table11_acquisition_yield",
         claim_text_short="Table 11: attack-label acquisition yield, discovery only",
         evidence_tier="feasibility (pool-based operational sensitivity)",
         primary_source="results/tables/paper2_final_q1/operational_e2e.csv",
         unit_of_analysis="per-arm mean inspected flows per attack found",
         multiplicity_family="descriptive (no family)",
         operational_scope=("balanced eval stream/calibration/candidate; adjudication pool "
                            "at operating prevalence; discovery never decides; 32 uniform "
                            "validation adjudications; plain accuracy; pipeline cost not "
                            "modeled"),
         allowed=["acquisition yield"],
         forbidden=["what the commit decision costs", "all labels sit at operating",
                    "cheapens the commit decision"]),
    dict(claim_id="detector_invariance",
         claim_text_short="gate effect holds under classical and quantum-kernel detectors",
         evidence_tier="registered confirmatory core (criterion I)",
         primary_source="results/tables/paper2_v2_replication_001/verdict.csv",
         unit_of_analysis="seed-level paired difference (30 seeds)",
         multiplicity_family="confirmatory core (Holm)",
         operational_scope="balanced pool-based streams",
         allowed=[], forbidden=[]),
    dict(claim_id="cohort_sim_naming",
         claim_text_short="VBC-SG-Cohort = proposal-target resampling simulation",
         evidence_tier="design clarification",
         primary_source="src/experiments/run_paper2_readaptation_v2.py (--vbc-defer-mode)",
         unit_of_analysis="n/a",
         multiplicity_family="n/a",
         operational_scope="simulator resampling of the proposal-time target distribution",
         allowed=["cohort-sim"],
         forbidden=["retained cohort", "literal production cohort is retained"]),
    dict(claim_id="multiplicity_method",
         claim_text_short="centered paired bootstrap; families 6/15/7 outcome-independent",
         evidence_tier="analysis methodology",
         primary_source="results/tables/paper2_final_q1/multiplicity.csv",
         unit_of_analysis="seed-level paired difference (30 seeds)",
         multiplicity_family="Holm (6) + BH (15) + BH (7) = 28",
         operational_scope="all registered inferential families",
         allowed=["centered paired bootstrap"],
         forbidden=["exact paired bootstrap", "exact bootstrap p-value"]),
]


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    text = load_texts()
    rows = []
    for c in CLAIMS:
        missing = [a for a in c["allowed"] if a.lower() not in text]
        present = [f for f in c["forbidden"] if f.lower() in text]
        if not c["allowed"] and not c["forbidden"]:
            status = "declared"
        elif not missing and not present:
            status = "verified"
        else:
            status = ("FAIL: " + "; ".join([f"missing anchor '{m}'" for m in missing]
                                           + [f"forbidden '{p}' present" for p in present]))
        rows.append(dict(claim_id=c["claim_id"], claim_text_short=c["claim_text_short"],
                         evidence_tier=c["evidence_tier"], primary_source=c["primary_source"],
                         unit_of_analysis=c["unit_of_analysis"],
                         multiplicity_family=c["multiplicity_family"],
                         operational_scope=c["operational_scope"],
                         allowed_wording="; ".join(c["allowed"]) or "n/a",
                         forbidden_wording="; ".join(c["forbidden"]) or "n/a",
                         status=status))
    A = pd.DataFrame(rows)
    A.to_csv(f"{OUT}/claim_scope_audit.csv", index=False)
    n_fail = int(A.status.str.startswith("FAIL").sum())
    print(A[["claim_id", "status"]].to_string(index=False))
    print(f"\nclaim-scope audit: {len(A)} claims, {n_fail} failing")
    if n_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
