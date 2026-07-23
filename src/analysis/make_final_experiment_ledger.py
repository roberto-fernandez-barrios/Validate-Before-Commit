"""final-q1 Fase A2: results/final_experiment_ledger.csv -- one row per experiment block that
feeds a MAIN-paper table, so every headline number traces to a directory, a script, a seed
window and a registered protocol.

The ledger is generated, not hand-written: the arm directories are discovered from the raw
results and cross-checked against the block definitions below, so a block that was never run
(or a directory that no block claims) shows up instead of passing silently.
"""
from __future__ import annotations

import glob
import os
import sys

import pandas as pd

RAW = "results/raw"
OUT = "results/final_experiment_ledger.csv"

# --- M3: orphan detection ----------------------------------------------------------------
# Every raw directory that belongs to a FINAL-q1 experiment family must be claimed by exactly
# one block. Scope is the `q1*` families created for this paper (the deliverable); the many
# historical / sibling paper2_* experiments are out of scope by construction. Within scope, a
# DECLARED exclusion list covers pilots, smokes and superseded runs, so the check fails loudly
# on a genuine orphan -- a new family with no block, or a superseded run not declared as such --
# instead of passing silently (the earlier ledger built a `claimed` set and never used it).
FINAL_SCOPE_GLOBS = ["q1*"]
SUPERSEDED_GLOBS = [
    "q1fd5_*",        # pre-blocker-D operational pilot (seeds 701-730), superseded by q1fd5b_*
    "*_superseded*",  # explicitly archived runs
    "*smoke*", "*pilot*",
]


def _arm_dirs(pat: str) -> set:
    """Raw directories matching `pat` that actually carry a per-seed result CSV."""
    return {d for d in glob.glob(f"{RAW}/{pat}")
            if os.path.isdir(d)
            and os.path.exists(f"{d}/paper2_progressive_readaptation_by_seed.csv")}


def _claimed_dirs() -> set:
    claimed = set()
    for _bid, _tier, pat, *_rest in BLOCKS:
        if pat:
            claimed |= _arm_dirs(pat)
    return claimed


def compute_orphans() -> list:
    """Directories in a final-q1 family that no block claims and that are not declared
    superseded/pilot/smoke. A non-empty result is a hard error for the release."""
    in_scope: set = set()
    for g in FINAL_SCOPE_GLOBS:
        in_scope |= _arm_dirs(g)
    superseded: set = set()
    for g in SUPERSEDED_GLOBS:
        superseded |= _arm_dirs(g)
    orphans = in_scope - superseded - _claimed_dirs()
    return sorted(os.path.basename(d) for d in orphans)

# block_id -> (evidence tier, glob, script, seeds, protocol note, manuscript target)
BLOCKS = [
    ("size_matched_own_transformer", "registered confirmatory control",
     "size_matched_own_transformer/sm_*",
     "src.experiments.run_symmetric_pipeline_replication", "4001-4030",
     "notes/paper2_size_matched_own_transformer_protocol_001.md (protocol 114513f frozen "
     "BEFORE implementation; config configs/size_matched_own_transformer_v1.json, SHA-256 "
     "6873cc1a in every run_config.json; nested 512-in-2000 candidate batches, 999 pairs "
     "verified; per-arm source commit, candidate size, raw-stream hash and completion in "
     "results/tables/size_matched_own_transformer_001/run_completion.csv; per-candidate "
     "provenance in candidate_provenance.jsonl, validated by "
     "tests/test_size_matched_control.py; registered outcome ATTENUATION)",
     "tab:size_matched"),
    ("symmetric_pipeline_dynamic", "registered confirmatory replication",
     "symmetric_pipeline/sp_*",
     "src.experiments.run_symmetric_pipeline_replication", "3001-3030",
     "notes/paper2_symmetric_pipeline_dynamic_protocol_001.md (protocol 8838566 + "
     "Appendix A 96576bb; per-arm source commit, transformer policy, raw-stream hash and "
     "completion in results/tables/symmetric_pipeline_dynamic_001/run_completion.csv; "
     "scaler/PCA/effective-gamma provenance in pipeline metadata, validated by "
     "tests/test_symmetric_pipeline.py)", "tab:symmetric_pipeline"),
    ("confirmatory_v2", "registered confirmatory core", "paper2_v2_*",
     "src.experiments.run_paper2_readaptation_v2", "104-133",
     "notes/paper2_harness_v2_registered_replication_protocol_001.md", "tab:v2_confirmatory"),
    ("causal_matrix_64", "registered follow-up", "paper2_fk_*_c64_*",
     "src.experiments.run_paper2_readaptation_v2", "104-133",
     "notes/final_kbs_protocol.md", "tab:causal_probe"),
    ("zero_drift", "registered follow-up", "paper2_v1*_rz_*",
     "src.experiments.run_paper2_readaptation_v2", "104-133",
     "notes/paper2_harness_v2_amendment_009.md", "tab:zero_drift"),
    ("generators_classifiers", "registered follow-up", "paper2_v11_*",
     "src.experiments.run_paper2_readaptation_v2", "104-133",
     "notes/paper2_harness_v2_amendment_009.md", "tab:amendment009"),
    ("mild_drift_prediction", "registered follow-up", "paper2_v8_*_sev025_*",
     "src.experiments.run_paper2_readaptation_v2", "104-133",
     "notes/paper2_harness_v2_amendment_006.md", "tab:harm_generality"),
    ("budget_frontier", "registered follow-up", "q1fc_*",
     "src.experiments.run_paper2_readaptation_v2", "501-530",
     "notes/q1_max_protocol.md (D3)", "tab:budget_frontier"),
    ("symmetric_ab_confirmatory", "registered follow-up", None,
     "src.analysis.paper2_symmetric_ab_final", "2001-2100 (pilot 104-133)",
     "notes/q1_max_protocol.md (D2)", "tab:ab_equivalence"),
    ("chronological_matrix", "external boundary", "q1fd_*",
     "src.experiments.run_paper2_temporal_stream", "601-630",
     "notes/q1_max_protocol.md (D4)", "tab:chronological_q1"),
    ("operational_simulation", "feasibility (pool-based)", "q1fd5b_*",
     "src.experiments.run_paper2_operational_e2e", "801-830 (pilot 701-730)",
     "notes/q1_max_protocol.md (D5) + blocker D", "tab:operational_e2e"),
    ("policy_frontier_costs", "registered follow-up", "paper2_v6_*",
     "src.experiments.run_paper2_readaptation_v2", "104-133",
     "notes/paper2_harness_v2_amendment_005.md", "tab:policy_frontier, tab:label_cost"),
]


def main() -> None:
    rows, claimed = [], set()
    for bid, tier, pat, script, seeds, proto, target in BLOCKS:
        dirs = []
        if pat:
            dirs = sorted(d for d in glob.glob(f"{RAW}/{pat}")
                          if os.path.isdir(d)
                          and os.path.exists(f"{d}/paper2_progressive_readaptation_by_seed.csv"))
            claimed.update(dirs)
        rows.append(dict(
            block_id=bid, evidence_tier=tier, script=script, seed_window=seeds,
            registered_protocol=proto, manuscript_target=target,
            output_glob=pat or "(analysis-only; reads processed pools directly)",
            n_arm_dirs=len(dirs),
            status="present" if (dirs or pat is None) else "MISSING",
        ))
    L = pd.DataFrame(rows)
    L.to_csv(OUT, index=False)
    print(L.to_string(index=False))
    missing = L[L.status == "MISSING"]
    if len(missing):
        print("\n[WARN] blocks with no arm directories:",
              ", ".join(missing.block_id.tolist()))
    print(f"\nwrote {OUT} ({len(L)} blocks, {int(L.n_arm_dirs.sum())} arm directories)")

    # M3: a final-family directory that no block claims (and that is not declared superseded)
    # is a hard error -- it means a run feeds nothing, or a block glob missed it.
    orphans = compute_orphans()
    if orphans:
        print(f"\n[FAIL] {len(orphans)} orphan directory(ies) in a final-q1 family claimed by "
              f"no block (and not declared superseded):")
        for o in orphans:
            print(f"    {o}")
        print("  -> add a block in BLOCKS, or add the pattern to SUPERSEDED_GLOBS.")
        sys.exit(1)
    print("orphan check: 0 unclaimed final-q1 directories "
          f"(scope {FINAL_SCOPE_GLOBS}, superseded {SUPERSEDED_GLOBS})")


if __name__ == "__main__":
    main()
