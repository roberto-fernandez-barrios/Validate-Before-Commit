# Amendment 010 — empirical-Bernstein confidence-sequence gate (the a009 future-work item, closed)

**Registered/implemented this session.** The a009 CS gate (`labeled_probe_cs`, Robbins
normal-mixture) was anytime-valid but so conservative at probe $\le 64$ that it never committed
(gain $+0.00$ everywhere) — safe but power-less. a009 named an empirical-Bernstein successor as
future work; this amendment implements and evaluates it.

## Code (additive, existing paths unchanged; py_compile OK)
- `cs_lower_bound_eb(d, alpha)` in `run_paper2_readaptation_v2.py`: predictable-plug-in
  empirical-Bernstein LOWER confidence sequence (Waudby-Smith & Ramdas 2023) for the mean of the
  per-flow correctness difference $d\in[-1,1]$. Uses the EMPIRICAL variance (correctness diffs are
  mostly ties → low variance), so it is far tighter than the sub-Gaussian Robbins CS while keeping
  the same $\alpha$-uniform harmful-commit bound. Unit test: commits at 25% net-correct/75%-tie
  (LCB $+0.085>0$) where Robbins does not ($-0.157$); no-commit on all-ties.
- New gate `--adaptation-gate labeled_probe_ebcs` (probe 64, seq-block 16).

## Runs (9 arms, 30 seeds, 0 failures; `paper2_v11_{reg}_{full,mild,rz}_ebcs64`)
| Regime | EB-CS full | EB-CS mild | EB-CS zero | ref: fixed lp32 full | ref: naive full |
|---|---|---|---|---|---|
| PortScan | **+5.17** [3.64,6.70] | +0.00 | +0.00 | +8.70 | +7.77 |
| UNSW-Recon | +0.00 | +0.00 | +0.00 | +1.31 | +1.23 |
| ToN-IoT | +0.00 | +0.00 | +0.00 | +0.80 | −1.38 |

## Reading (honest)
- **EB-CS dominates the Robbins CS**: it captures the LARGE PortScan benefit (+5.17 vs Robbins
  +0.00), commits ~1 update, spends 63 labels/decision.
- **Still safe everywhere else**: ToN-IoT full-drift it commits nothing (+0.00 = +1.38 above the
  harmful naive), mild/zero +0.00.
- **But at b=64 it cannot resolve 1-point benefits** (UNSW +1.3, ToN full +0.8 → both +0.00): the
  anytime-valid guarantee, even at its tightest, hits the same wall as exact McNemar — the binding
  constraint is the LABEL BUDGET, not the rule. Consistent with the paper's frontier lesson.
- EB-CS is the recommended anytime-valid procedure (dominates Robbins). It sharpens, not overturns,
  the frontier.

## Integration
Manuscript §5 CS paragraph extended (EB-CS result + `\cite{waudbysmith2023betting}`, added to
references.bib). Aggregator `aggregate_paper2_amendment_009.py` cs_gate block extended (EB-CS
full/mild/zero + full-drift references + ebcs-vs-lp32/naive contrasts). Audit +5 checks → **350/350**.
Builds 35 pp CAS / 28 pp IEEE.
