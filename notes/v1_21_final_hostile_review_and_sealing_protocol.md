# v1.21.0 — Final hostile review, limited compression and sealing protocol (FROZEN)

Date: 2026-07-22. Branch: `feature/symmetric-pipeline-replication` @ `49df32a`.
Authorization: "FINALIZACIÓN — Revisión hostil, compresión limitada y sellado v1.21.0".

## Definitive title (adopted on every live surface)

> Validate Before Commit: Candidate Governance for Drift-Triggered Classifier
> Pipelines in Network Intrusion Detection

Rationale (frozen): "Candidate Governance" names the central contribution;
"Classifier Pipelines" reflects the symmetric-pipeline experiment; no
end-to-end efficiency claim; no formal risk control attributed to all gates.
The former title ("...Label-Efficient Commit Decisions for Drift-Triggered
Classifier Updates...") is removed from every live surface; it may remain only
in historical notes that must identify v1.20.2 literally.

## Claim-scope corrections (C1–C7)

- C1 ownership: never "explains all"/"sole cause"; use "removes the observed
  mean full-drift harm and accounts for the large frozen-versus-own
  difference" + "a major amplifier, not a complete explanation".
- C2 zero-drift gates: "improve over naive in all six zero-drift comparisons,
  recovering much or nearly all of the loss depending on the cell"; never
  claim full recovery to never-adapt where a policy remains below it; the
  three recovery levels (vs-naive improvement / return-to-never /
  conversion-to-benefit) are never conflated.
- C3 full drift: naive-own beneficial ×3; frozen mean harm does not persist;
  ToN point > naive-own; PortScan gates immaterial; UNSW point small cost;
  no policy dominates.
- C4 harmful@H5: "descriptive fractions of future-negative committed
  proposals within the controlled trajectories"; never population prevalence,
  deployment probability, independent trials, or "common in production".
- C5 unsw_zero strict: BA and FPR improve, recall LCB crosses the
  preregistered 1-point NI margin; no "security improvement"/"improves all
  security metrics"/"no security trade-off".
- C6 scope: symmetric evidence = KS-max point/strict full+zero; QK-ZZ,
  VBC-SG/frontier and mild drift = historical frozen policy; no automatic
  transfer.
- C7 chronological: 13 replays, net harm unobserved, principal external
  limit; gate-above-naive without an adjusted paired contrast is phrased
  "achieves higher mean balanced accuracy" / "descriptively above", never
  "significantly outperforms".

## Compression target (limited)

Preferred: main 31–32 pages total, body ≈28–29; hard cap 33 if further cuts
damage clarity (documented). Supplement may stay at 27; IEEE preferably ≤24.
Priorities: shrink the historical frozen recap; de-duplicate symmetric
numbers across Abstract/Results/Discussion/Conclusion; shorten the two new
table captions; keep every load-bearing limitation and the frozen/own
distinction. Output: `notes/v1_21_final_compression_report.md`.

## Hostile checklist

The 20 questions of the authorization, answered with textual evidence and
table/CSV references in `notes/v1_21_final_hostile_review.md`; verdict
READY FOR v1.21.0 SEALING or a concrete scientific blocker. No optional
improvements invented afterwards.

## Files allowed to change

manuscript/* (tex, tables, highlights), README.md, REPRODUCE.md,
CITATION.cff, .zenodo.json, manuscript/references.bib (artifact entry),
docs/img/graphical_abstract.png (+ its generator), src/analysis/* (table/
figure/manifest/audit generators only), tests/*, notes/* (new), configs/
(none), results/tables/MANIFEST.sha256 (re-pin additive),
results/final_manifest.json (Commit B ONLY). FORBIDDEN: any experimental
runner, any raw output, margins/families/seeds/A-B-C rules, the pending
Paper 1 reference.

## Sealing procedure

- Commit A "Integrate symmetric-pipeline evidence and finalize KBS
  manuscript": everything above EXCEPT results/final_manifest.json,
  release_manifest.json, PDFs (repo keeps them untracked), the 2 personal
  files, temp/smoke outputs.
- `make_final_manifest` (v1.21.0 fields incl. symmetric summary) → Commit B
  "Stamp v1.21.0 final symmetric-pipeline artifact manifest" containing ONLY
  results/final_manifest.json.
- Verify main still at v1.20.2, `git switch main`, `git merge --ff-only`,
  annotated tag v1.21.0 ("Final KBS candidate-governance artifact with
  preregistered symmetric-pipeline replication."), GitHub Release with
  main.pdf, supplement.pdf, main_ieee.pdf, release_manifest.json,
  v1.21.0_symmetric_pipeline_artifacts.zip (protocol+Appendix A, config,
  run_completion, paired_contrasts, multiplicity, equivalence,
  security_metrics, transformer_interaction, harmful_commit_summary,
  CLAIM_INTERPRETATION.json, claim-scope audit, experiment ledger,
  MANIFEST.sha256, final_manifest.json; NO raw datasets).
- Zenodo version for v1.21.0 via the repository's GitHub–Zenodo integration;
  record the minted version DOI in release_manifest.json (release asset) and
  the release notes — never by post-hoc repo mutation.

## Stopping rule

After v1.21.0: no further scientific iteration, datasets, own-transformer
mild/QK/VBC-SG, new gates, frontier redo, title reopening, compression or
pre-submission review. Only the pending Paper 1 reference, editor
requirements, or official KBS reviewer comments may change the artifact.
