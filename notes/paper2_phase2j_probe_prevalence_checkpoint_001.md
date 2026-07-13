# Phase 2j checkpoint — the probe need not be balanced: full safety and benefit at natural prevalence

**Date:** 2026-07-13 · Protocol: `paper2_phase2j_probe_prevalence_protocol_001.md` (criteria pre-fixed).
Artifacts: `results/tables/paper2_phase2j_probe_prevalence_001/{summary,paired_ci,verdict}.csv`.
Runs: 9 (3 regimes × {p10_b32, p01_b32, p01_b320} × KS-max × SVC-RBF × 30 seeds, parallel).

## Verdict: P1, P2, P3 ALL PASS; G passes on all 12 contrasts — the strongest outcome

Gains vs within-run no-adaptation (BA pts); balanced lp32 reference in parentheses:

| regime | π=0.10, b=32 (~3 attacks) | π=0.01, b=32 (1 attack) | π=0.01, b=320 | balanced |
|---|---|---|---|---|
| PortScan (benefit) | +7.93 | +7.62 | +8.00 | (+8.27; naive +7.79) |
| UNSW Recon (mixed) | +1.26 [1.00, 1.51] | +1.28 [1.03, 1.54] | +1.50 | (+1.13) |
| ToN-IoT (harm) | **+1.00 [0.66, 1.39]** | **+1.01 [0.69, 1.40]** | +0.68 | (+0.93) |

- Even with a **single labeled attack flow per probe** (π=0.01, b=32) the gate keeps full
  safety (significantly above no-adaptation in the harm regime) and full benefit (within the
  pre-fixed 0.3-pt margin of naive in PortScan).
- The 10× inspection budget at π=0.01 adds nothing — absolute attack-label count ≥1 suffices.

## Mechanism
The commit decision is a **paired sign comparison on a shared probe**, not a precise accuracy
estimate: incumbent and candidate are evaluated on the same flows, so most estimation noise
cancels, and the mostly-benign probe already ranks the two models; the single attack flow adds
the minority-class signal. Balance was a convenience of the earlier design, not a requirement.

## Consequence for the claims
- Review point 4 (balanced probes unrealistic) is closed **with data**, not with a caveat: the
  b/(2π)-inspections concern dissolves — the operative requirement is ≥1 labeled attack flow
  per decision (≈1/π random inspections at low prevalence, ~100 at π=1%).
- Limitations rewritten accordingly (evaluation windows remain balanced; alert-volume/FPR under
  extreme operational imbalance still untested — the remaining honest caveat).
- §5.6 extensions count 8 → 9; abstract now says "stale ... or drawn at natural attack
  prevalence". Audit extended to 112 checks.
