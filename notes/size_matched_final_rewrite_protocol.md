# FROZEN — Final size-matched manuscript rewrite protocol

Date: 2026-07-23
Branch: `feature/size-matched-own-transformer` @ `0d280a5e65bd87c74086631ba874f6b420e21289`
Preflight: pytest 110/110; audit 561 PASS / 0 FAIL (checks_passed == checks_total == 561;
the earlier "561/0" notation meant passed/failed, not a typo); manifest 173/173 pinned
(10 unpinned extras = the unsealed size-matched tables); 21/21 size-matched COMPLETE;
42/42 symmetric-pipeline COMPLETE; v1.21.0 manifests byte-identical
(`5f8a1e43…`, `8500c6e2…`); no background processes.

## Scope of this phase

Text/artifact integration ONLY. No experiment, no new analysis, no rule change, no
merge/tag/release/Zenodo/DOI, no modification of `main` before the human checkpoint.
Registered outcome stays **ATTENUATION** (never retro-classified as ELIMINATION).

## New framing (frozen)

Final thesis replacing the v1.21.0 thesis ("even self-contained candidate pipelines
remain harmful when the incumbent is healthy"):

> Harmful promotion in the evaluated controlled setting is driven by
> candidate-construction asymmetries. Frozen incumbent-owned preprocessing amplifies harm
> under full drift, while training challengers with one quarter of the incumbent's
> per-class sample size explains the residual zero-drift harm. When preprocessing
> ownership and training size are matched, promotion is mean-neutral and point/strict
> validation offers no measurable advantage.

Kept: "A drift alarm does not establish challenger superiority."
Never stated: "A drift alarm necessarily produces a harmful challenger."

Formal vs substantive (both must appear, clearly distinguished):
- Registered outcome: ATTENUATION (P fails: no material mean harm at 2000; E fails only
  on the preregistered sign-based H5 criterion E3; A assigned mechanically).
- Substantive: naive_2000 ≡ never in 3/3 (±0.5 pp, CI90); gates at 2000 all <0.14 pp,
  0/6 Holm-significant; mean future value at 2000 ≈ 0; H5 sign rates ≈48–52% are
  proposal-level variability around a ≈0 mean, not systematic net harm; the practical
  result sits one preregistered criterion away from ELIMINATION.

## Allowed claims

- Size effect is the dominant, Holm-significant driver of residual zero-drift harm
  (+1.89 / +0.63 / +0.23 pp; 3/3).
- naive_512 − never replicates the v1.21.0 residual harm on fresh seeds
  (−1.70 / −0.65 / −0.24 pp).
- BA equivalence of naive_2000 vs never within ±0.5 pp in 3/3 (CI90).
- 0/6 significant gate gains at 2000; gate value at 512 compensated evidence asymmetry.
- All 2000 cells pass recall/FPR NI guardrails; unsw strict_512 recall-NI failure
  replicates.
- Gates are conditional tools: valuable under construction/evidence asymmetry, no
  measurable value once pipelines are comparable ("attributable in the evaluated
  setting" phrasing).
- VBC-SG: formalization of a gate when one decides to validate; evaluated under the
  historical frozen policy; not shown necessary under size-matched conditions.

## Forbidden claims (guarded by audits/tests where checkable)

- "harm persists with size-matched challengers" (unqualified).
- "gates remain useful at size 2000" / "candidate governance is universally required".
- "ATTENUATION means mean harm remains".
- "H5 ~50% means ~50% deployment/harm risk"; harmful@H5 as a probability of harm.
- "size matching proves no individual candidate can be worse".
- "VBC-SG validated under size-matched own pipelines".
- "observed-data evidence transfers automatically"; "full-drift size-matched was
  evaluated".
- "the result is formally ELIMINATION".
- "deploying drift-triggered candidates is intrinsically dangerous".

## Title (proposed, NOT sealed — shown at checkpoint for approval)

> Validate Before Commit: A Controlled Study of Pipeline Construction, Evidence
> Asymmetry, and Candidate Promotion in Network Intrusion Detection

Updated on all live surfaces (main, IEEE, supplement, GA, highlights, README,
REPRODUCE, CITATION.cff, .zenodo.json, references.bib self-note, generators,
tests/audits); the v1.21.0 title survives only in historical notes and explicit
references to the previous release.

## Structural plan

- Abstract: full rewrite, 210–240 words, the frozen 9-step order, load-bearing numbers
  as listed in the phase instructions.
- Contributions: reduced to three (C1 decomposition of promotion; C2 controlled
  identification of the two asymmetries; C3 conditional value of commit gates).
- Method: new subsection "Size-matched self-contained challenger control" right after
  the symmetric-pipeline replication subsection (question, design, nesting rationale,
  E1–E5, F1–F4, margins, P/A/E, seed as inferential unit; not observed-data, not
  deployment-realistic).
- Results order: frozen historical (diagnostic) → own-transformer replication →
  size-matched control (decisive) → conditional gate value → VBC-SG/frontier
  (frozen-only) → chronological/operational boundaries.
- New central table `tab:size_matched` (3 rows × {naive512−never, naive2000−never,
  size effect, equivalence, point/strict at 2000, Holm}); security summary; future-value
  signs reported as "future-negative signs / proposal-level sign variability /
  near-zero mean future value" (never "persistent harmful proposals" or a probability).
- Discussion: three findings (comparability precedes promotion testing; the need for
  gating is conditional; negative results improve adaptive-system evaluation).
- Conclusion: the authorized paragraph verbatim (phase instructions §12).
- Limitations: the ten declared items (§13); no experiment proposals.
- VBC-SG: guarantees/scope/cost kept intact in Method + risk section; de-emphasized in
  abstract/contributions/conclusion.
- GA + highlights: comparability-flow diagram; 5 highlights within the repo's existing
  character limit (85 chars, guarded by the existing test).

## Tables replaced / moved

- Main gains `tab:size_matched` (from frozen CSVs via a new generator
  `make_size_matched_tables.py`; no hand-typed numbers).
- Moved/kept to supplement: complete F1–F4 contrast table, equivalence sensitivities,
  H1/H3/H10 horizons, nesting provenance/hashes, complete 512 tables.
- Reduced in main: ToN frozen headline, prior harmful@H5 framing, Scenario-A
  repetition, frontier detail, amendment history.

## Budgets

- main ≤ 33 pages (target 31–32); body word count must not exceed v1.21.0's;
  abstract ≤ 240 words; supplement may grow.

## Artifact (candidate v1.22.0 — NO release in this phase)

Update: manuscript, supplement, README, REPRODUCE, claim map, experiment ledger,
MANIFEST generator (pins the size-matched tables at sealing time only), tests, audits,
candidate metadata (CITATION.cff / .zenodo.json version 1.22.0, no DOI minted).
Record: protocol commit, config hash, seeds 4001–4030, 21/21, nesting 999/999, outputs,
P/A/E result, equivalence, size effects, gate effects, guardrails, v1.21.0 unchanged.

## Stop rule

After `notes/size_matched_final_manuscript_checkpoint.md` and
`notes/size_matched_final_hostile_review.md`: STOP. No merge, no tag, no release, no
Zenodo, no experiment. Verdict is exactly one of READY FOR FINAL v1.22.0 SEALING or
NOT READY — TEXTUAL/TECHNICAL BLOCKER.
