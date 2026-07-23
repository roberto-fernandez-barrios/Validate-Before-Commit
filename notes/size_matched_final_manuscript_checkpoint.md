# CHECKPOINT — Final size-matched manuscript integration (pre-sealing, human gate)

Date: 2026-07-23
Branch: `feature/size-matched-own-transformer`
Commits this phase: `c7fca9d` (frozen rewrite protocol) → `d2de866` (integration) →
`6562fae` (hostile review + abstract fix) → this checkpoint.
`main` untouched at `7f9ea40` (v1.21.0). No experiment executed; no merge/tag/release/DOI.

## A. Scientific reframing

- **v1.21.0 thesis (replaced):** "Even self-contained candidate pipelines remain harmful
  when the incumbent is healthy."
- **Final thesis (live):** harmful promotion in the evaluated controlled setting is driven
  by candidate-construction asymmetries — frozen incumbent-owned preprocessing (full drift)
  and a fourfold per-class training-size disadvantage (zero drift). With ownership and size
  matched, promotion is mean-neutral and point/strict validation offers no measurable
  advantage. Kept: "a drift alarm does not establish challenger superiority." Never stated:
  "a drift alarm necessarily produces a harmful challenger."
- **Claims removed:** zero-drift harm as size-robust property of self-contained pipelines
  (now scoped to 512/frozen); "candidate governance remains materially useful with
  self-contained pipelines" as unconditional; gate value as universal; "harmful proposals
  remain common" as unqualified proposal-level harm; the universal-safeguard conclusion
  sentence.
- **Claims added:** 3/3 BA equivalence of naive_2000 vs never (±0.5, CI90); 3/3
  Holm-significant size effects (+1.89/+0.63/+0.23); 0/6 significant gate gains at 2000
  (all <0.14 pp); F4 interactions uniformly negative (gate value at 512 ≈ compensation for
  evidence asymmetry); conditional-validation recommendation; the three-stage control
  sequence as a methodological template.
- **Formal vs substantive (kept distinct everywhere):** registered outcome **ATTENUATION**
  (P fails: no material mean damage at 2000; E fails only on the preregistered sign-based
  H5 criterion, which fired at 0.4796/0.5204 in ps/unsw); substantively, size matching
  neutralizes the mean zero-drift harm (mean H5 future value −0.06…+0.03 pp at 2000 vs
  −0.13…−1.03 at 512). Never retro-classified (guards N10/P4; tests).

## B. Title and abstract

- **Proposed title (PROVISIONAL — awaiting your approval):**
  *Validate Before Commit: A Controlled Study of Pipeline Construction, Evidence
  Asymmetry, and Candidate Promotion in Network Intrusion Detection.*
  On all live surfaces (main, IEEE, supplement, README, REPRODUCE, CITATION.cff,
  .zenodo.json, GA script, tests, audits); v1.21.0 title survives only in historical notes
  (audit T1/T2/T3 green).
- **Abstract:** fully rewritten, 219 words (clean count; 230 whitespace-split; guard ≤290,
  target ≤240), in the frozen 9-step order with all load-bearing numbers
  (−1.70/−0.65/−0.24 · +0.19/−0.02/−0.01 + equivalence 3/3 · +1.89/+0.63/+0.23 Holm ·
  gates <0.14 n.s. · ATTENUATION with the H5 explanation · sequential-controls conclusion ·
  chronological + operational bounds).
- **Highlights (5, ≤85 chars, synced .tex + highlights.md):** frozen preprocessing can
  manufacture apparent harm; fourfold size asymmetry explains the residual loss;
  size-matched challengers mean-equivalent to never-adapt; gates help under asymmetric
  evidence, no measurable value once sizes match; construction and validation are
  complementary, conditional controls.
- **Graphical abstract:** regenerated (2247×857): trigger ≠ superiority → check candidate
  comparability (ownership, evidence) → comparable: direct promotion may be adequate /
  uncertain-asymmetric: validate before commit; three evidence badges; no universal claims.

## C. Manuscript structure

- **New:** method §3.7 "Size-matched self-contained challenger control" (design, nested
  batches, E1–E5/F1–F4, P/A/E); results §5.3 "Size-matched self-contained challengers:
  the decisive control" (+ `tab:size_matched`); supplement §S8 (guardrail panel + full
  F1–F4 + harm horizons + interactions + nesting provenance + outcome trace).
- **Reduced/reordered:** intro reframed (comparability first) and contributions 4 → 3;
  §5.1 re-labelled initial diagnostic; §5.2 scoped as "the first asymmetry" (512
  challengers); frozen zero-drift/mild-drift/classifier paragraphs frozen-scoped; anytime-
  valid, frontier, observed-data, monitors, ensemble, two-stage, hierarchical-model,
  acquisition-yield and Limitations prose compressed; Discussion rebuilt as three findings;
  conclusion replaced by the authorized paragraph; VBC-SG de-emphasized in abstract/
  contributions/conclusion with guarantees intact.
- **Tables:** main gains `tab:size_matched` (generator `make_size_matched_tables.py`, no
  hand-typed numbers); `table_size_matched_security` + 3 full matrices to S8;
  `table_amendment009` caption re-scoped. Nothing hand-edited.
- **Budgets:** main.pdf **33 pages** (≤33), supplement 29 (may grow), IEEE 25;
  body word count **18,088 < 18,511** (v1.21.0); 0 undefined refs/citations.

## D. Size-matched evidence (as integrated)

| dataset | 512−never (desc.) | 2000−never (F1) | eq ±0.5 | size effect (F2) | point/strict −naive @2000 (F3) |
|---|---|---|---|---|---|
| ps_zero | −1.70 [−2.05,−1.36] | +0.19 [−0.15,+0.55] | yes (CI90 hi 0.494, stated) | +1.89† | +0.05 / +0.13 (n.s.) |
| unsw_zero | −0.65 [−0.77,−0.55] | −0.02 [−0.10,+0.06] | yes | +0.63† | +0.01 / +0.06 (n.s.) |
| ton_zero | −0.24 [−0.39,−0.10] | −0.01 [−0.05,+0.04] | yes | +0.23† | +0.02 / +0.03 (n.s.) |

Guardrails: 6/6 matched-size cells pass recall/FPR NI; unsw strict_512 recall-NI failure
replicates (trade-off language only). H5: sign rates 48–52% at 2000 presented as
proposal-level variability around a ≈0 mean — never a probability, never "harmful
proposals" unqualified; no binomial bound.

## E. Scope (declared, guarded)

Size matching tested only under zero drift; zero-drift trigger is a random proposal rate,
not a real alarm; balanced pools throughout (own+size-matched+observed-data not combined);
VBC-SG not re-run under size-matched own pipelines; full-drift size-matched not run;
QK/mild-drift remain frozen-scope; 13 chronological replays with no net harm remain the
external boundary; SVC-RBF concentration and three-benchmark scope declared.

## F. Artifact (v1.22.0 candidate — NO release, NO seal)

- Updated: main.tex, main_ieee.tex (regenerated), supplement.tex, README.md, REPRODUCE.md,
  highlights (.tex + .md), GA generator + PNG, CITATION.cff (1.22.0), .zenodo.json
  (1.22.0), references.bib artifact note (1.22.0), experiment ledger generator (+
  size-matched block; regenerated: 12 blocks, 562 arm dirs, 0 orphans), claim-map
  generator (+4 rows; **not run** — its CSV is pinned by the sealed MANIFEST),
  final-manifest generator (+`size_matched_control_v1_22_summary`; **not run** — sealed
  JSON untouched), MANIFEST generator untouched (generic; will pin the 10 new tables at
  sealing).
- Recorded in artifact surfaces: protocol commit 114513f, config SHA 6873cc1a…, seeds
  4001–4030, 21/21, nesting 999/999 (+ parity 5/5 BIT_IDENTICAL), P/A/E result,
  equivalence, size effects, gate effects, guardrails, v1.21.0 unchanged.
- **Guards added:** 25 audit checks (v122sm N1–N11 forbidden claims + P1–P11 frozen
  results/wording; audit now **586/586**) and 8 pytest guards
  (`tests/test_size_matched_claims.py`; suite now **118/118**); title tests updated
  (new title everywhere; both retired titles absent).

## G. Hostile review

`notes/size_matched_final_hostile_review.md`: 15/15 questions answered affirmatively
against compiled surfaces and frozen CSVs; 5 defects found and fixed during the review
(lost subsection heading; unscoped "size-robust" caption; missing operational clause in
the abstract; transient 34-page overrun; staging of personal files). **No blocker; no new
experiment recommended.**

## H. Gates (at checkpoint)

- pytest **118/118** · audit **586/586, 0 FAIL** · verify-hashes **173/173** pinned
  (10 unpinned extras = the new, not-yet-sealed size-matched tables) · refs/citations
  undefined **0** · orphans **0** (ledger) · size-matched **21/21 COMPLETE** ·
  symmetric **42/42 COMPLETE**.
- Historical results intact: `results/final_manifest.json` = `5f8a1e43…`,
  `results/tables/MANIFEST.sha256` = `8500c6e2…` (byte-identical to v1.21.0);
  size-matched confirmatory raw outputs untouched since their run (freeze-commit source
  `c4df062` recorded in every arm).
- No runner executed this phase; no background processes; working tree clean except the
  two known personal untracked files.
- Pages: main 33 / supplement 29 / IEEE 25. Abstract 219 words. Body 18,088 words.

## I. Recommendation

**READY FOR FINAL v1.22.0 SEALING**

Awaiting your decisions at this gate: (1) approve or amend the provisional title;
(2) authorize the v1.22.0 sealing sequence (re-pin MANIFEST with the 10 new tables,
regenerate claim-scope CSV and final_manifest.json, commit A/B, merge, tag, release,
Zenodo). Per the absolute stop rule, none of that has been started: no merge, no tag,
no release, no Zenodo, no experiment.
