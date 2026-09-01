# v1.24.0 — final exact-feature-disjoint IJIS integrity sensitivity

This minor release adds the last authorized confirmatory science before IJIS submission.
It preserves v1.23.0 and its 207 sealed CSVs byte-for-byte.

## Scientific result

- A forensic audit verifies that source-row disjointness did not guarantee exact cleaned
  feature-value disjointness in the historical role splitter.
- A new opt-in splitter assigns every exact cleaned raw feature group wholly to evaluation,
  candidate-training or probe while preserving all rows, original labels and within-role
  multiplicity. Historical mode is unchanged.
- The preregistered B2 sensitivity uses seeds 7001--7030 and 21 arms. The 512-to-2,000
  candidate-size effect remains positive and Holm-resolved in all three benchmarks
  (+0.53/+1.67/+0.38 balanced-accuracy points), but the material effect is
  benchmark-dependent rather than homogeneous (`PARTIAL ROBUSTNESS`).
- The preregistered B1 sensitivity uses seeds 8001--8030 and the complete 96-arm amended
  common harness. Four of six robustness predicates hold (`PARTIALLY ROBUST`): ordering
  remains candidate-size-dependent and no evaluated policy globally dominates, while the
  earlier ATC and calibrated-ensemble retention statements are narrowed.
- No rescue experiment, policy tuning or post-result design change was performed.

## Reproducibility and submission material

- 230 result CSVs are sealed in `results/tables/MANIFEST.sha256`; none of the prior 207
  hashes changed and there are zero unpinned release-result CSVs.
- The release includes the frozen protocol and configs, forensic audit, implementation and
  role-integrity tests, B2/B1 checkpoints, full machine-readable inference, updated ledger,
  manifest and claim audit.
- Manuscript and ESM distinguish historical source-row-disjoint evidence from the governing
  exact-feature-disjoint sensitivity, use pool-constructed progressive-drift terminology,
  narrow operational claims, and refresh related work through September 2026.
- Result figures encode key distinctions by marker/line style or hatch in addition to color.

The GitHub--Zenodo integration assigns the immutable version DOI after this tag is released.
The concept DOI is `10.5281/zenodo.21322256`; no version DOI is guessed in the tag.
