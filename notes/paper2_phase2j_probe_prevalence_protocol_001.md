# Phase 2j — Probe prevalence: does the gate survive realistic class imbalance? Protocol

**Date:** 2026-07-13 · **Status:** post-registration robustness; criteria fixed BEFORE analysis.
**Motivation:** external review point 4 — all probes so far are class-balanced, which presumes an
enrichment mechanism (alert queue). At attack prevalence π, a balanced probe of b flows costs
≈ b/(2π) inspections. The open question is whether the gate NEEDS balance, or works with probes
drawn at the traffic's natural prevalence. We test the probe's composition directly.

## Manipulation
- `--probe-prevalence π` (default 0.5 = balanced, exact backward compatibility): the probe of
  size b is drawn with n_attack = max(1, round(b·π)) attack flows and b − n_attack benign flows,
  both mixed at the probe severity as before. The floor of one attack flow reflects that a probe
  with zero attacks cannot compare attack behaviour at all. Everything else unchanged
  (KS-max, SVC-RBF, full-replacement retraining, legacy trigger, Phase-2 settings).

## Arms (3 regimes × 3 arms × 30 seeds = 9 runs)
- **p10_b32** — π = 0.10, b = 32 → ≈3 attack flows/probe. Realistic enriched-queue prevalence.
- **p01_b32** — π = 0.01, b = 32 → 1 attack flow/probe. Extreme stress case.
- **p01_b320** — π = 0.01, b = 320 → ≈3 attack flows/probe at 10× the inspection budget.
  Tests whether what matters is the absolute number of attack labels, at fixed low prevalence.

## Pre-fixed criteria (gains vs within-run no-adaptation; paired CIs)
- **P1 (decisive; π = 0.10, b = 32):** ToN-IoT gain ≥ −0.5 AND PortScan gain ≥ naive (7.79) − 0.3.
- **P2 (stress; π = 0.01, b = 32):** same thresholds, reported either way.
- **P3 (recovery; π = 0.01, b = 320):** if P2 fails its ToN threshold, does the 10× budget
  restore ToN ≥ −0.5?
- **G:** no arm is significantly below no-adaptation in any regime (ci_hi ≥ 0), except where
  P2 fails and is reported as the boundary.

## Interpretation rules (fixed before results)
- **P1 passes:** the balanced probe is a convenience, not a requirement — the gate works at
  realistic prevalence with ~3 attack labels per confirmed drift. Limitations soften from
  "budgets are post-enrichment costs" to a quantified operating point.
- **P2 also passes:** stronger still — a single attack flow per probe suffices; say so plainly.
- **P2 fails, P3 passes:** the requirement is an absolute number of attack labels (~3), not
  balance; inspection cost scales as ≈ n_att/π and is reported as the honest operating curve.
- **P1 fails:** the balanced-probe assumption is load-bearing; Limitations keep the strong
  caveat and the abstract's label-cost claim gets qualified. Report without spin.
