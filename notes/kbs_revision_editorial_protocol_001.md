# Post-KBS editorial revision protocol (FROZEN, 2026-08-31)

Governs the editorial revision performed after the rejection of manuscript KNOSYS-D-26-17242
(Knowledge-Based Systems). Written before the manuscript edits of this phase; the completed
audit trail is `audits/kbs_rejection_revision_report.md` and
`audits/kbs_response_to_reviewers.md`.

## 1. Scope (exhaustive)

Editorial only. Authorized changes:

1. Abstract rewritten (problem → decomposition → three results → external scope → conclusion).
2. Introduction restructured: one message per paragraph; an explicit early paragraph stating
   that the net-harm findings are configuration-dependent, not universal properties; the
   contribution hierarchy made explicit (primary / secondary / tertiary).
3. §3.5 condensed to the minimum needed to read the results (point/strict, risk-controlled,
   pooled vs stratified, commit/reject/defer, what VBC-SG does and does not guarantee);
   implementation-level definitions relocated verbatim to Supplement S2.13.
4. §5.2: explicit statement, next to the matched-size result, that nominal sample-size parity
   is not effective information parity (effective sample size, temporal coverage/diversity,
   subtype support, duplication, label quality, prevalence, information content).
5. New §5.6 "Comparison with strong baselines and alternative update policies" with a table
   built exclusively from sealed outputs, grouped by registered block, descriptive across
   blocks; Related Work distinguishes conceptual positioning (Table 1) from this experimental
   comparison.
6. Discussion: Q1–Q4 condensed; a paragraph on the computational overhead of self-contained
   versus frozen pipelines, marked as an operational implication and reporting only the
   coarse per-arm wall-clock recorded in the completion markers (no new timing study).
7. Stale cross-references fixed (main → supplement S-numbers; supplement S0 table; README and
   REPRODUCE section pointers); a reviewer quick map added to README.

## 2. Hard rules

- No new experiments, seeds, arms, classifiers, datasets, gates, metrics or statistical
  families. Nothing under `results/raw/` or `results/tables/` changes; `MANIFEST.sha256`
  is not re-pinned.
- Every numeric value in the revised text is a value already present in a sealed CSV or
  generated table; the only additions are the descriptive wall-clock ratios computed by
  `src/analysis/make_kbs_revision_runtime_summary.py` from existing completion markers,
  written under `audits/` and labelled as coarse operational context.
- Preserved distinctions: exploratory / registered core / symmetric replication /
  size-matched control / registered follow-ups / feasibility / chronological boundary;
  fresh-seed, pairing and multiplicity statements; the PortScan boundary-close caveat; the
  registered ATTENUATION outcome; "no detectable average benefit" ≠ "no benefit"; "zero
  observed harmful commits" ≠ "eliminates"; commits/triggers/windows never treated as
  independent trials; no deployment-harm prevalence inferred from chronological replays;
  VBC-SG guarantees false probe-superiority control only and claims no mathematical novelty;
  no quantum-advantage claim; SVC-RBF full-drift harm not generalized to all classifiers.
- Title unchanged (pinned by `tests/test_scenario_a_claims.py`); alternative titles are
  proposed in the revision report only.
- All existing guard tests and the claim audit must pass unchanged, except where a test
  enumerates the main-body table set or section count and the new §5.6 requires an
  additive update (documented in the report).
