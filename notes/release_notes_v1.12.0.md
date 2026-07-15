## What changed since v1.11.0 (amendment 010 — the empirical-Bernstein confidence-sequence gate)

This release closes the one item v1.11.0 left as future work: a tighter, still anytime-valid
commit gate. Claims audit **345 → 350/350**; builds **36 pp CAS / 28 pp IEEE**.

**A tighter anytime-valid gate that actually captures benefit.** The Robbins normal-mixture
confidence-sequence gate of v1.11.0 was anytime-valid but so conservative at small probe budgets
that it essentially never committed (safe, but power-less). We add a predictable-plug-in
**empirical-Bernstein confidence sequence** (Waudby-Smith & Ramdas 2023): because the per-flow
correctness differences are mostly ties, their empirical variance is far below the sub-Gaussian
worst case, so the interval is much tighter — with the *same* α-uniform harmful-commit bound.

**Result (9 arms, 30 seeds, 0 failures).** The empirical-Bernstein gate dominates the Robbins one:
it captures the large deep-benefit PortScan gain at full drift (+5.17 [3.64, 6.70], vs the Robbins
CS's +0.00 and the fixed 32-probe gate's +8.70), while staying safe everywhere else — it commits
nothing under mild or zero drift, and at full-drift ToN-IoT it avoids the harmful naive update
(+0.00, i.e. +1.38 above naive). But at 64 labels it still cannot resolve the 1-point benefits of
UNSW-Reconnaissance or full-drift ToN-IoT (both +0.00): the anytime-valid guarantee, even at its
tightest, hits the same wall as the exact McNemar test — **the binding constraint is the label
budget, not the decision rule**. The empirical-Bernstein gate is the recommended anytime-valid
procedure, and it sharpens rather than overturns the frontier's central lesson.

**Code.** New additive option `--adaptation-gate labeled_probe_ebcs` and helper
`cs_lower_bound_eb` (existing paths unchanged). Manuscript CS paragraph and reference list updated;
aggregator and claims audit extended.
