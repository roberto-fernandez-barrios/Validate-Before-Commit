# Single-entry reproduction workflow (see REPRODUCE.md for the experiment commands that
# populate results/raw; these targets regenerate every derived table and re-verify claims).
PY ?= python

.PHONY: analysis audit manifest reproduce

analysis:
	$(PY) -m src.analysis.aggregate_paper2_v2_replication
	$(PY) -m src.analysis.aggregate_paper2_amendment_004
	$(PY) -m src.analysis.aggregate_paper2_amendment_005
	$(PY) -m src.analysis.paper2_decision_quality_004
	$(PY) -m src.analysis.paper2_decision_quality_005
	$(PY) -m src.analysis.paper2_policy_frontier_005
	$(PY) -m src.analysis.validate_monitors_vs_river

manifest:
	$(PY) -m src.analysis.make_results_manifest

audit:
	$(PY) -m src.analysis.audit_paper2_claims

reproduce: analysis manifest audit
