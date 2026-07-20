# v1.18.0 — final-q1: mechanism decomposition, an affordable deployment-long guarantee, and the full chronological matrix

Closing release of the `final-q1` protocol (`notes/q1_max_protocol.md`, frozen with registered
deltas D1–D7 before any run). It answers the four quantitative blockers of the last external
review with experiments rather than wording, and closes the paper.

## New science

**A guarantee that is affordable, not vacuous (Fase C).** The previous release reported that
the maximally-stacked deployment-long configuration committed nothing at a 64-flow probe. A
registered budget frontier (5 probe caps × 2 spending schedules × 3 policies × 3 regimes,
pristine seeds 501–530, endpoints declared in advance) shows that was a statement about a
budget, not about the rule: **twelve configurations meet the pre-declared non-vacuity target**,
and a lifetime-budgeted gate recovers **93% of always-deploying's benefit at a 512-flow cap**
(81% for the fully stratified VBC-SG) while committing **nothing at all under zero drift, at
every cap**. Reported with its price: 74–86% abstention, ~4 windows of deferral, and the
zero-cost strict rule still buying most of the practical safety.

**The mechanism, decomposed and equivalence-tested (Fase C).** The symmetric A/B control was
re-run on **100 fresh confirmatory seeds** (2001–2100; the original 30 are re-labelled a
pilot). Per-model preprocessing is now shown **equivalent to zero** by bootstrap TOST at a
pre-registered ±1.0-point materiality margin on all three benchmarks — while the
independent-transformer condition on the two high-variance benchmarks remains *unresolved
rather than null*, which we say plainly. A registered decomposition localizes the effect: the
**feature standardizer** carries essentially the whole ownership advantage (−12.17 of −12.35)
and the PCA carries none (+0.16), consistent with a variance-scaled RBF bandwidth.

**The chronological matrix, enumerated in advance (Fase D).** Seven new replays — every
CICIDS train→future day pair with an attack-bearing training day, two intra-day splits, and
UNSW at two further training fractions — under `none/point/strict/VBC-SG`, seeds 601–630.
**Chronological net harm remains unobserved across all thirteen replays**, the paper's
principal external-validity limit. But where the incumbent stays healthy, **all gates beat
always-deploying** — the zero-cost strict rule by +2.78 and +1.34 points on non-overlapping
intervals — while the Wednesday intra-day split is reported as the counterexample that keeps
this a tendency rather than a law.

**The decision priced end to end (Fase D).** New runner with four label-acquisition policies
that rank by model *predictions* only. **Alert-guided inspection finds an attack 5–8× more
cheaply than random inspection** at every prevalence; disagreement sampling barely helps
(1.0–2.1×), reported as the negative it is. Latency and a new training-completion delay cost
~1 point each.

## New theory

**Proposition 1** (§3.5, proof in Supplement §S4): the commit rule's empirical-Bernstein
process is a nonnegative supermartingale under the *conditional* null, so the
accumulate-mode defer retains an anytime-valid bound against the weak null — stated with its
exact target, since rejecting it does not establish superiority at commit time. Two
alternative continuation modes with cleaner targets are implemented and evaluated
(`--vbc-defer-mode {accumulate,cohort,refresh}`).

## Corrections (independent hostile review, 9 defects)

The abstract had drifted to 533 words and described the pre-final-q1 paper (both fixed;
now 264 words); "six chronological replays" appeared where thirteen were meant; the
conclusion was stale; Limitations contradicted §5.5 on which streams keep a healthy incumbent;
a cross-document table reference was wrong; the abstract misattributed the frontier headline
to VBC-SG when it belongs to a pooled variant; and §3.5 framed VBC-SG as *the* contribution
where the frontier shows no member dominates. Full list in
`notes/q1_faseF_hostile_review_001.md`.

**Reproducibility defect fixed:** `port_ieee.py`, which regenerates `main_ieee.tex` from
`main.tex`, lived only in a session scratchpad — so the artifact could not rebuild that
manuscript and it had silently drifted. It is now `src/analysis/port_ieee.py` and runs as part
of `make final-paper`.

## Artifact

`make final-paper` now also runs the four final-q1 aggregators and the final-q1 table emitters.
New invariant tests cover the defer modes, the weak-null e-process under drifting conditional
means, candidate-latency semantics, the pending-candidate policy, TOST machinery, and the four
causality/restart/accounting/logging invariants that gated VBC-SG's entry into the
chronological matrix. Manuscript: 27 pages of content (target ≤27).

**Audit: 459 pinned checks. Tests: 33.**
