# Cross-experiment hostile result audit — post-KBS strengthening experiments

Scope: adversarial reading of the two sealed confirmatory blocks, BEFORE any manuscript
editing. B2 = size-matched self-contained challengers under drift (seeds 6001–6030,
commit 61f5c5a). B1 = amended common-harness baselines (seeds 5001–5030, results at this
commit). Nothing here is softened to fit the current manuscript; every number is from the
frozen analyses.

## 1. B2 — hostile questions

**Does 2,000/class help, hurt or do nothing under drift?** It **helps, materially**:
G2 = +0.82 [0.67, 0.98] / +1.66 [1.51, 1.81] / +1.00 [0.60, 1.39] pp (ps/unsw/ton), all
Holm p≈3e-5, all above the +0.5 materiality margin. Registered outcome
**HOMOGENEOUS-SIZE BENEFIT**.

**Homogeneous?** Yes, 3/3 — no heterogeneity refuge was needed.

**Did larger candidates over-specialize under advancing drift?** **No.** The
frozen-transformer precedent (S1.5: size-matching *deepened* full-drift harm, ToN −5.34)
does not reproduce under self-contained pipelines. Over-specialization was a property of
the frozen incumbent-owned representation, not of candidate size. This is a genuinely new,
falsifiable-and-survived result.

**Does candidate size interact with gate value?** Negatively where resolved (G4 all ≤ 0;
unsw/strict −0.31 Holm-sig). At the matched size under drift the gates add **nothing**
(G3: 0/6 positive; strict on unsw_full a RESOLVED COST, −0.34 [−0.53, −0.15]).

**Does any result undermine "comparability before promotion"?** No — it removes the
hostile audit's strongest objection (the zero-drift control was null-by-construction):
the same nested intervention that was exchangeability-trivial at severity 0 produces a
material, homogeneous effect under drift. Evidence comparability is now a demonstrated,
non-trivial factor in the only regime where it is testable.

**Materially different from the zero-drift control?** Yes, in the informative direction:
≈0 at zero drift (expected under exchangeability), material positive under drift — the
zero-drift null was not insensitivity.

## 2. B1 — hostile questions

**Which external/generic baseline is strongest?** **Calibrated soft ensemble** (standard
baseline, internal implementation): COMPATIBLE with always-deploy in all three full-drift
scenarios and the only MATERIAL GAIN of the primary zero-drift family (+1.46, ps_zero) —
but it commits every trigger, the model grows, and it fails recall NI on ps_full/unsw_zero.
Among *published* methods: **ATC** — COMPATIBLE with naive at full drift (2/3, 1
unresolved) and COMPATIBLE with the point gate on 5/6 scenarios at zero target labels.

**Does any published/reference method dominate point/strict?** **No.** ATC *matches* the
point gate within ±0.5 pp on 5/6 (ps_full unresolved at −0.73, pointing the gate's way);
nothing beats it anywhere.

**Does DoC beat the gate?** **No — the exploratory-harness pattern reverses.** Under the
final harness at parity, DoC vs point is MATERIAL COST on ps_full (−2.67) and unsw_full
(−0.58), COMPATIBLE elsewhere (ton_full +0.01). The Block-III "DoC +1.16 vs gate +0.93"
reading does not survive the trusted configuration; the manuscript's honest §5.6 caveat
("evaluated only on the exploratory harness") is vindicated, and the sentence reporting
DoC's exploratory win must now be paired with this confirmatory reversal.

**Does the calibrated ensemble beat the gate?** Not materially. Descriptively it is the
only policy with a MATERIAL GAIN cell (ps_zero) where the point gate shows +0.24; at full
drift ensemble−naive is COMPATIBLE while point−naive is ≈0; no registered contrast puts
the ensemble materially above the gate, and it cannot decline an update.

**Are DDM/ADWIN competitive after accounting for monitoring labels?** **No.** At 800
monitoring labels/stream they are MATERIAL COST in all three full-drift scenarios
(DDM −0.78/−1.81/−2.67; ADWIN −8.73/−2.50/−4.06) with large FPR guardrail failures
(ADWIN ΔFPR up to +9.5 pp). Performance-aware triggering with always-deploy is dominated
in this harness even at evidence parity.

**Does ranking change between 512 and 2,000?** **Yes, in the registered S4 sense, for ATC
(ps_zero) and the ensemble (ps_full, ton_full):** MATERIAL GAIN at 512 collapsing to
COMPATIBLE at 2,000. All 15 resolved SF5 interactions are negative. The value of every
evaluated safeguard — labeled or label-free — concentrates where candidate evidence is
asymmetric. Not resolved for point/strict/DoC (S4 false).

**Can a reviewer still reasonably say there is no meaningful external baseline
comparison?** For *generic published methods and reference monitors*: **no longer** —
ATC, DoC, river-DDM, river-ADWIN, replay and the calibrated ensemble now have registered,
paired, common-harness results under the final trusted configuration at nominal evidence
parity, with a preregistered secondary size axis. For *published adaptive-NIDS systems*:
**yes, and permanently within this design** — no end-to-end system was reproduced, for
the frozen written reasons (different decision problems / unavailable inputs). Any future
reviewer sentence must be answered with that distinction, not with a SoTA claim.

**Is any cross-policy comparison unfair through information budgets?** Budgets differ by
definition and are documented, not equalized (amendment §3; `budget_table.csv`): ATC/DoC
consume 512-row training-time validation samples (outside the runner's counters —
reported analytically), DDM/ADWIN consume 800 monitoring labels/stream, the gates 32
target labels/decision. The PF families compare *complete policies*; no cell hides a
budget. The one asymmetry a hostile reader could press — ATC/DoC/enscal arms train all
models with probability=True — is neutralized by test_F10 (`.predict` unchanged).

## 3. Uncomfortable readings, stated plainly

1. **At full evidence parity, nothing beats always-deploy at full drift.** Not the gates
   (B2 G3; B1 anchors), not any label-free method (PF2: best case COMPATIBLE). Strict
   validation shows small RESOLVED COSTS (B2 unsw −0.34; B1 anchor unsw −0.23). The
   paper's conditional-validation thesis survives only in its already-stated form:
   validation earns its keep under construction/evidence asymmetry or uncertainty, and is
   otherwise a mild drag. Any residual pro-gate framing beyond that is now indefensible.
2. **The zero-drift "harm" story is now fully an evidence-asymmetry story.** naive₅₁₂
   harm replicated on a third fresh seed block (−1.66/−0.58/−0.35); at 2,000/class it is
   gone and even the label-free methods have nothing left to rescue (S1: none).
3. **The exploratory Block-III ATC/DoC numbers are superseded in the direction
   unfavourable to DoC** and must never again be quoted without the confirmatory
   counterpart.

## 4. Verdict

**STRENGTHENS CURRENT THESIS.**

Justification against the alternatives: no result contradicts a sealed registered claim
(naive₅₁₂ zero-drift harm replicates; full-drift self-contained benefit replicates; the
frozen-policy S1.5 size pattern was already scoped to the frozen representation, and B2
resolves that scoping in the paper's favour); the two results the manuscript scoped as
open questions (size under drift; external baselines under the final harness) both came
back supporting the comparability-before-promotion account and the conditionality of
validation. "REQUIRES THESIS REVISION" would overstate: what requires revision is
*scope wording* (several "not evaluated" limitations are now evaluated) and the
*gate-value narrative* must absorb the strict-gate resolved costs at parity — both are
incorporations of new evidence into an unchanged thesis, to be executed only in a
separately authorized manuscript phase.
