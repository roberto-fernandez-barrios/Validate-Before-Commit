# KBS BIBLIOGRAPHIC CEILING — BASELINE

Recorded before the focal bibliographic patch, on branch `editorial/kbs-bibliographic-ceiling`
(from `main` @ `87137dd3b91cad531e1c3a201aa31081ef87ca65`, post v1.22.5 Zenodo publication).

## State

- **Source version:** v1.22.5 (latest tag; sealing `e9449ca`).
- **References in `references.bib`:** 73 `@`-entries.
- **Pages:** main 25, supplement 35, IEEE 18.
- **Gates (green):** pytest 135, audit 630/630, hashes 185/185; PDFs 0 undefined refs/citations.
- **Untracked, left untouched:** `PLAN_Q1_DEFINITIVO_VBC.md`, `notes/recovered_run_q1_faseC.py.txt`, `dist/`.

## Scope of this phase (fused, per user decision)

1. Add the eight core references (active comparison/testing, limited-label & temporal model selection, cost-sensitive/-aware retraining, modern when-to-retrain) and the four statistical classics (McNemar, Holm, Benjamini–Hochberg, Schuirmann/TOST).
2. Minimal textual integration (Intro sentence, ~2 Related-Work paragraphs, one contribution sentence, one Limitations sentence) with narrowed novelty claims.
3. **Remove the companion "Paper 1" reference** (`fernandez_paper1`) — this paper is now Paper 1 (user decision; overrides the template's "do not touch" rule and the earlier `test_paper1_reference_untouched` guard, which will be updated).
4. Seal + release **v1.22.6** (GitHub + Zenodo).
5. Rewrite history to strip `Co-Authored-By: Claude` trailers and force-push (user-authorized, with recorded caveats: breaks the sealing-SHA the paper cites and diverges from the permanent Zenodo deposits).

## Statistical references already present / absent

| Ref | Present? | Note |
|---|---|---|
| McNemar 1947 | **absent** | exact-McNemar gate is used but uncited |
| Holm 1979 | **absent** | Holm correction used throughout; ("Holm" grep hits are surnames Holmes) |
| Benjamini–Hochberg 1995 | **absent** | BH used on frontier/chronological blocks |
| Schuirmann 1987 (TOST) | **absent** | equivalence/CI-inclusion used |
| Confidence sequences (Howard, Waudby-Smith) | present | keep |

## Target references vs existing keys

- `zliobaite2011active` present — the 2011 active-learning-for-streams paper, **distinct** from R5 (Žliobaitė 2015 cost-sensitive adaptation); no duplicate.
- R1 Sawade, R2 Kossen, R3 Karimi, R4 Han, R5 Žliobaitė-2015, R6 Mahadevan, R7 Okanovic, R8 Regol — **all absent**.

## Size expectation (honest)

Adding 12 refs and removing 1 (Paper 1) → ~84 entries. The task's 70–74 "reasonable objective" is not
reachable without deleting fundamental NIDS/security/temporal/confidence-sequence refs, which the task
forbids; only clearly-redundant peripheral entries (1–2) will be removed. Final count ~82–83, with the
bibliography possibly +1 page (explicitly accepted by the task). Body prose net change kept < ~350 words.
