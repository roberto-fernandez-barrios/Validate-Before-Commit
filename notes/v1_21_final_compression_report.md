# v1.21.0 — Limited editorial compression report

Date: 2026-07-22. Scope: authorization section D (limited compression, no new
percentage target, no removal of load-bearing limits).

## Pages / words

| artifact | before this pass | after |
|---|---|---|
| main.pdf | 33 pages (body 30, refs p.31–33) | **33 pages (body 30, refs p.31–33)** |
| supplement.pdf | 27 pages | 27 pages |
| main_ieee.pdf | 25 pages | 25 pages |
| main body words (macro-stripped approx.) | ~14,332 | ~14,340 |
| abstract | 232 words | **238 words** |

Net body words are flat because the phase had two opposing mandates: the C1–C7
claim-scope corrections ADDED text (the mandated recovery-level distinction, the
C5 guardrail sentence, the "amplifier, not a complete explanation" sentence,
"within the controlled trajectories" qualifiers), while the compression pass
REMOVED an equivalent volume of recapitulation.

## Material condensed

- Intro gate paragraph (§1): merged the cost-accounting and label-efficiency
  sentences; "label-efficient" now introduced only "in a strictly bounded
  sense" with the candidate-batch cost in the same sentence.
- §5.1 lead: harness recap compressed (~30%); roadmap sentence tightened.
- Six-tiers paragraph: redundant clauses removed (tier markers preserved —
  pinned by tests).
- §3.6 Design paragraph: policy semantics merged into one sentence chain.
- §5.2 v1-summary: figure/table enumeration clause removed.
- Both new table captions shortened (~40% and ~35%).
- Abstract held at 238 words after absorbing the C2 rewording.

## Material moved to the supplement

Nothing additional in this pass — the S7 move (all 24 family contrasts,
harmful H1/3/5/10 + censoring, interactions, provenance detail) was already
done in the rewrite phase; the main body keeps exactly the items the
authorization requires (full own result, zero own result, own-vs-frozen
interaction, principal gate contrasts, the problematic guardrail, the
chronological limit).

## Why 33 pages are retained (frozen rule applied)

Reaching 31–32 total pages requires freeing ~1 full body page beyond the ~65
lines already cut. The only blocks of that size left are: the zero-drift /
risk-gate registered-results paragraphs, the frontier account, the mechanism
equivalence/decomposition paragraph, and the Limitations section — all of
which carry registered numbers, load-bearing limits, or the frozen/own
distinction the authorization forbids sacrificing. Per the frozen rule ("if
reaching 31–32 forces removing a limit, a necessary figure, or the frozen/own
distinction, keep 33 and document"), 33 pages (30-page body) are retained.
IEEE at 25 pages (preferred ≤24) follows the same trade-off: it is generated
from the same source by `port_ieee` and shares the same body.

## Confirmation

No scientific number changed in this pass: edits were prose-only; tables were
regenerated from the same frozen CSVs (caption text changed, cell values
byte-identical inputs); audit numeric pins (SP7/SP8) and
`test_headline_numbers_match_frozen_csv` pass unchanged.
