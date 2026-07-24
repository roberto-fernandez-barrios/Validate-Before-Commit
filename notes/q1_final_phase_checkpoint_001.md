# final-q1 — closing phase: the reviewer's five blockers + low-cost recommendables

Date: 2026-07-20. Branch `final-q1`. NOT committed, NO release, NO DOI (v1.17.0 and v1.18.0
stay frozen). Scope agreed with the reviewer; explicitly out of scope: rebuilding the
operational runner as causal, new datasets/models/gates/seeds/runners.

## Blocker 1 — harmful value of EVERY commit, deferred included

**The defect, verified before acting.** Harm was scored only for commits resolved at their
proposal window, off the proposal-time lookahead. Across the sweep that left **35% of commits
unevaluated**, and in `ebcsdef cap 64` --- the cheapest non-vacuous operating point the paper
cites --- *all 17 commits were deferred and none was scored*.

**Implementation.** `paper2_v2_resolution_log.csv`: one row per resolved proposal with its
**real resolution window**, type (commit / futility / cap-reject), immediate-vs-deferred,
delay, and incumbent-vs-challenger balanced accuracy over the windows following the
**resolution** at horizons 1/3/5/10 and until the next decision. Horizons running past the end
of the stream are **censored**, never scored short. Verified bit-identical on by-seed outputs
(logging only), and the re-run reproduced all twelve non-vacuous frontier configurations
exactly --- so the gains are untouched and only the evaluation is new.

**Audit change.** The check that certified "zero harmful commits" is replaced by a
**completeness invariant** (evaluable + censored = commits): the audit can no longer certify
zero from partial data. A stale frontier CSV is reported as a FAILING check rather than
crashing, so a half-updated artifact never looks like a pass.

**Result — the claim survives, now on complete data.**

| policy | commits | deferred | evaluable | censored | harmful@H5 | rate |
|---|---:|---:|---:|---:|---:|---:|
| naive | 273 | 0 | 267 | 6 | 105 | 39.3% |
| point | 211 | 0 | 208 | 3 | 54 | 26.0% |
| strict | 93 | 0 | 92 | 1 | 8 | **8.7%** |
| risk gates (all) | **518** | **180** | 504 | 14 | **0** | **0.0%** |

Zero harmful commits across all 518 risk-gate commits, 180 of which took effect after a
deferral, and zero harmful "until the next decision" over 515 evaluable. The gradient
(39.3% -> 26.0% -> 8.7% -> 0%) is new information the paper did not have: rejecting ties
alone removes two thirds of the point gate's harm at no label cost.

Five mandated tests pass. Six numbers pinned in the audit.

## Blocker 2 — acquisition separated from validation

`--dual-sample`: enriched **discovery** half measures acquisition cost only; an independent
uniform **validation** half at operating prevalence is the only sample the commit rule sees.
Seeds **801--830** (701--730 declared a pilot: inspected before the redesign). Alert-enriched
inspection finds an attack 5--8x more cheaply than random; hybrid 3--6x; disagreement
1.1--1.3x, reported as the negative it is.

## Blocker 3 — A/B reproducibility, and a real contamination found

`hash()` (salted per process) replaced by a SHA-256 seed, recorded in the output, with a test
that checks stability **in a separate interpreter**. Deduplication made global with a declared
conflict rule; all six T/M1/M2/E intersections asserted per class and globally.

**What it found:** PortScan and ToN have zero label conflicts and byte-identical pools, but
**UNSW-NB15 has 230 feature vectors carrying both labels**, which per-class deduplication kept
in both classes. UNSW re-run on the confirmatory window: **every equivalence verdict
unchanged**; only magnitudes move (+0.04 -> +0.00). The hardening confirms the prior result.

## Blocker 4 — artifact synchronization

Ledger and manifest regenerated from the final state: 10 blocks / 498 arm directories, no
missing block; MANIFEST.sha256 re-pinned (163 files); `final_manifest.json` now carries
**pi=0.005**, **training delays {0,5}**, the immediate/deferred/censored harm split, the
acquisition policies, the defer modes and the ledger summary. A new test enforces every one of
those fields and the arithmetic between them.

## Blocker 5 — operational wording

Renamed *"operational label-acquisition and delay simulation, run within the pool-based
harness"*; the paper states plainly it still draws from the pools and is **not** leakage-free.
"Causal"/"observed-data" now denote only the arm reading neither `sev(t)` nor the pools, with
a guard over manuscript, README and REPRODUCE.

## Recommendables

Ledger (above). Multiplicity: Holm on the confirmatory core, BH within follow-up blocks,
Supplementary \S S5 --- **no conclusion depends on the correction**, plus a guard that fails if
the stated policy and the applied analysis disagree either way. Data-backed guards on the
chronological claims.

## Editorial

Body held at **27 pages** while absorbing all the new material, by moving to the supplement:
the label-cost table (now \S S5), the amendment-by-amendment history of the causal arm
(\S S2.7), the superseded budget sweep (\S S2.8) and risk-gate implementations (\S S2.9); and
by compressing \S5.2 and the conclusion.

## What the checks caught that reading did not

- The **230 label conflicts** in UNSW.
- The audit **crashing** on a stale CSV instead of reporting it.
- A false claim ("every gate beats always-deploy on healthy timelines") in **three** places ---
  abstract, conclusion and \S5.5 --- where the review had spotted one.

And the guard for that claim had to be written **three times**: version one was blinded by a
backslash a shell heredoc ate; version two by splitting the search window on "." when
"82.9\%" contains one. Both passed silently on text that was wrong. Every guard here is now
verified against the defect it exists to catch, not only against the corrected text.

## Final state

`audit 465/465`, `tests 46/46`, body 27 pp, supplement 24 pp, IEEE 23 pp, 0 undefined
references or citations in any of the three PDFs.

Pending: independent verification of this phase, then authorization for commit, release and
submission.
