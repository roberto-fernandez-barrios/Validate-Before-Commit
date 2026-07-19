# Single-entry reproduction workflow (see REPRODUCE.md for the experiment commands that
# populate results/raw; these targets regenerate every derived table and re-verify claims).
#
#   make reproduce    -- analysis + manifest + audit (the original derived pipeline)
#   make final-paper  -- the final-kbs P10 workflow: hash verification, invariant tests,
#                        full analysis, final tables and figures, results/final_manifest.json,
#                        CAS + supplement + IEEE compilation, and the pinned-claims audit.
#
# PY selects the interpreter (e.g. `make final-paper PY=/path/to/conda/envs/paper2/python`).
# LaTeX compilation needs pdflatex + bibtex on PATH (MiKTeX / TeX Live).
PY ?= python

.PHONY: analysis audit manifest reproduce \
        verify-hashes final-analysis final-tables final-figures final-manifest test pdf final-paper

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

# ---- final-kbs P10 workflow -------------------------------------------------------------

verify-hashes:
	$(PY) -m src.analysis.verify_results_manifest

final-analysis: analysis
	$(PY) -m src.analysis.aggregate_paper2_amendment_006
	$(PY) -m src.analysis.aggregate_paper2_amendment_007
	$(PY) -m src.analysis.aggregate_paper2_amendment_008
	$(PY) -m src.analysis.aggregate_paper2_amendment_009
	$(PY) -m src.analysis.aggregate_paper2_amendment_009_tail
	$(PY) -m src.analysis.aggregate_paper2_amendment_011
	$(PY) -m src.analysis.aggregate_paper2_amendment_012
	$(PY) -m src.analysis.aggregate_paper2_amendment_013
	$(PY) -m src.analysis.aggregate_paper2_amendment_014
	$(PY) -m src.analysis.aggregate_paper2_final_kbs

final-tables:
	$(PY) -m src.analysis.make_paper2_amendment009_table
	$(PY) -m src.analysis.make_paper2_final_tables

final-figures:
	$(PY) -m src.analysis.make_paper2_pertrigger_figure
	$(PY) -m src.analysis.make_paper2_graphical_abstract_final

final-manifest:
	$(PY) -m src.analysis.make_final_manifest

test:
	$(PY) -m pytest tests -q

pdf:
	$(PY) -m src.analysis.build_pdfs

final-paper: verify-hashes final-analysis final-tables final-figures manifest final-manifest test pdf audit
	@echo "final-paper: all P10 steps completed"
