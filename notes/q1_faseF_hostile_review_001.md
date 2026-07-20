# final-q1 — Fase F: independent hostile review (protocol step 29)

Date: 2026-07-20. Branch `final-q1`. NOT committed. Reviewer stance: read the manuscript as
an adversarial KBS referee who has NOT followed the development, cross-checking every claim
against the artifacts and against the rest of the document. Only verifiable errors corrected
(step 30).

## Findings (7 defects, all corrected)

### F1 — The abstract described the pre-Fase-C/D paper (SEVERE)

The abstract still ended on "no policy dominates the frontier ... the gate pays a premium on
deep-benefit chronological replays" and mentioned none of the work that answers the reviewer's
own blockers: the budget frontier (non-vacuity), the equivalence testing, the standardizer
decomposition, the chronological matrix, the operational end-to-end. A referee reads the
abstract first; ours advertised a weaker paper than the one behind it. Rewritten around the
final contribution set.

### F2 — The abstract was 533 words (SEVERE, desk-reject risk)

More than double the ~250-word norm for the venue, having grown accumulatively across
amendments (it was ~250 in earlier versions). Rewritten to **264** words. Residual: still
~5\% over the guideline; acceptable, but worth a final pass if the venue enforces it strictly.

### F3 — "Six chronological replays" throughout, now thirteen

The contribution list, the evidence-tier paragraph and Limitations all still said six. Updated
to thirteen everywhere the total is meant; the three surviving mentions of "these six" now
explicitly scope themselves to the first set, which is correct.

### F4 — The conclusion was stale

No mention of the identified mechanism, the frontier, VBC-SG, the strict rule, or the
chronological result. Rewritten with three closing findings (mechanism named; guarantee
priced; boundary shaped), keeping the honest negative (no chronological net harm) in place.

### F5 — Limitations contradicted \S5.5 on a matter of fact

Limitations asserted that the UNSW timeline "is the only one that keeps its incumbent healthy"
and that the gate "costs nothing there" --- both false after the new matrix: the Wednesday
intra-day split is also healthy (84.7\%), and on the UNSW timelines the gates *beat*
always-deploying rather than merely tie. Corrected.

### F6 — Broken cross-document reference

The body pointed to "Supplementary Table~S8" for the per-replay chronological numbers; that
table is the fifth in the supplement (S5). Replaced with a pointer to \S S2.6, which is robust
to float reordering. A full sweep confirmed every other supplement reference (S1.1--S1.6,
S2.1--S2.9, S4) resolves to an existing subsection.

### F7 — The abstract misattributed the frontier headline (OVERCLAIM)

"VBC-SG ... at a 512-flow probe cap it recovers 93\%" --- but 93\% is the **pooled** EB-CS
variant; the fully stratified VBC-SG reaches **81\%**. Exactly the class of overclaim the
protocol's P0.4 sweep exists to prevent. Corrected in the abstract, the conclusion and the
README to quote both figures.

### F8 — The IEEE port script was not in the artifact, and the IEEE manuscript had drifted

`main_ieee.tex` is generated mechanically from `main.tex`, but the generator lived only in a
session scratchpad --- so the published artifact could not rebuild it, and it silently fell out
of sync whenever the CAS manuscript changed without a manual re-run (it had, by the abstract
rewrite and findings F1--F7 above). Promoted to `src/analysis/port_ieee.py` and wired into the
`pdf` target, so `make final-paper` regenerates it before compiling and the two manuscripts
cannot diverge again. This is a reproducibility defect, not a content one, but it is exactly
the kind a referee checking the artifact would hit.

### F9 — \S3.5 framed VBC-SG as "the paper's algorithmic contribution" while the frontier shows it is not dominant

External review warned specifically against presenting VBC-SG as if it dominated the frontier.
\S5.4 was already honest (pooled EB-CS + deferral recovers 93\% against the fully stratified
VBC-SG's 81\%, and the zero-cost strict rule is competitive), but the Method still introduced
VBC-SG as *the* algorithmic contribution, which primes the reader the wrong way. Reframed: the
contribution is the **family of commit rules and the frontier it spans**, with VBC-SG named as
its maximally-guaranteed member, and an explicit forward pointer that a less stratified sibling
--- or the zero-cost strict rule --- is the better buy at some operating points.

## Checked and found sound (no action)

- Every pinned number against its CSV: audit passes (see final count below).
- The frontier write-up already distinguished pooled from stratified correctly in \S5.4 ---
  only the abstract had collapsed them.
- The chronological write-up already stated the Wednesday-intra-day counterexample rather than
  rounding the healthy-incumbent finding into a law.
- The e2e write-up reports the disagreement-sampling negative as it came out.
- Proposition 1 and its \S S4 proof correspond to the implemented `cs_lower_bound_eb`.
- Body table set == the nine final tables; no superseded table is input in the body.
- Evidence tiers, latency table, defer-mode semantics, and the P0.4 vocabulary are consistent
  between \S3--\S4, \S5 and the artifact's flags.

### F10 — `make final-paper` was broken by an indented comment (found by running it)

The final-q1 additions to the `final-analysis` and `pdf` recipes carried explanatory `#`
comments on tab-indented lines. Every line of a make recipe is handed to the shell, so those
are not comments: on Windows the shell tried to execute `#` and the target died with
`Error 2` --- after the expensive analysis steps had already run. Comments moved to column 0,
and the Makefile now carries a note saying why. Only an end-to-end run surfaces this class of
defect, which is the argument for step 28 of the protocol existing at all.

*Known limitation, not fixed:* `make final-paper` has no file-based dependencies, so it
re-runs the whole chain (including the ~30-minute mixed-effects fits) even when only the last
steps changed. Correct but wasteful; converting the targets to real file rules is a refactor
we judged too risky to attempt at freeze time, and it is recorded here as future work.

### F11 — Artifact metadata still used retired vocabulary

`.zenodo.json` listed "safe model updating" among its keywords --- the unqualified "safe" the
P0.4 sweep removed from the paper. Aligned with the manuscript's own keywords
("risk-aware model updating"), and "candidate governance" added, since that is the thesis the
artifact now supports. A sweep of the remaining metadata (`CITATION.cff`, README badges) found
no other retired vocabulary.

## Regression guards added (so these defects cannot come back)

Three of the nine findings were *drift* defects --- they appeared because the manuscript was
edited many times without a check --- so they are now enforced by tests rather than by care:

- `test_abstract_length_within_venue_limit` — fails if the abstract drifts materially above
  the venue norm again (hard guard at 290 words; it had reached 533).
- `test_chronological_replay_count_consistent` — any mention of "six replays" must scope
  itself to the first set ("these", "initial", "above"); an unscoped one fails, because the
  matrix now has thirteen.
- `test_frontier_headline_not_misattributed` — wherever the 93% frontier headline appears,
  the 81% fully-stratified qualifier must appear nearby, so a pooled result can never again
  be attributed to VBC-SG.

Written after the corrections and verified to fail on the pre-correction text (the replay
guard caught a genuine unscoped mention that the manual pass had left, which is why the
opening of the first chronological paragraph now reads "An initial six registered replays").

## Verification after corrections — FASE F CLOSED

`make final-paper` ran end to end on the corrected Makefile and passed every step:

| step | result |
|---|---|
| verify-hashes | **157 pinned CSVs match**, 0 unpinned extras |
| invariant tests | **36 passed** (33 + the 3 new regression guards) |
| analysis + tables + figures | all regenerated from raw |
| `results/final_manifest.json` | written; causal-64 collisions **0 / 0 / 0** (probe, candidate-future, commits-without-probe) |
| PDFs | main **31 pp (27 pp of body**, references from p. 28), supplement 23 pp, IEEE 23 pp — **0 undefined references or citations** in all three |
| claims audit | **459/459** |

IEEE abstract verified byte-identical to the CAS abstract, i.e. the F8 drift is closed by the
`pdf` target rather than by discipline.

**Protocol submission criteria (\S10 of `q1_max_protocol.md`): all met.** The DEFER guarantee
has an unambiguous target (Proposition 1 + cohort/refresh); candidate latency agrees across
code, manuscript and manifest; the A/B uses equivalence testing; the mechanism is attributed
only to the pipeline that supports it; strict appears as a main baseline everywhere; the
lifetime policy is shown useful rather than declared vacuous; label acquisition is operational;
the chronological matrix is complete and pre-enumerated; no unjustified "safe" survives;
"label-efficient" always means the incremental cost of the decision; the evidence tiers are
separated; the body is 27 pp; audit and invariants pass at 100%; and PDF, code, CSV, manifest
and README carry no contradiction we could find.

Fase F is closed. Nothing is committed: `final-q1` remains a local branch awaiting Roberto's
authorization for commit/push, release v1.18.0 + Zenodo (v1.17.0 stays frozen), and submission.
