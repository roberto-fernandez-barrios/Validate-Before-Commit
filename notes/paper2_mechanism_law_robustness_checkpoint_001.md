# Mechanism-law robustness checkpoint — the law is not an aggregation artifact

**Date:** 2026-07-13 · Script: `src/analysis/make_paper2_mechanism_law_robustness.py`
Artifacts: `results/tables/paper2_mechanism_law_robustness_001/{summary.csv,per_seed_points.csv}`
**Re-aggregation of existing 30-seed artifacts only — no new experiments (stop-rule respected).**

Motivation: a reviewer can object that r = −0.89 is "just an aggregate correlation over 7 points".
Four analyses close that flank:

| Analysis | n | r |
|---|---|---|
| Regime-level (as published) | 7 | −0.888 |
| Seed-resampling bootstrap (30 seeds/regime, 5000×) | 7 | −0.889, CI95 [−0.900, −0.877] |
| **Stream-level, no aggregation (regime × seed)** | **210** | **−0.910** |
| Leave-one-regime-out | 6 | −0.716 … −0.922 (weakest: without DDoS) |
| Pooled 16 (SVC taxonomy + RF/LogReg/MLP) | 16 | −0.813 |
| — without ToN-IoT | 12 | −0.811 |
| — without UNSW-NB15 | 11 | −0.951 |
| — without CICIDS2017 | 9 | −0.524 |

Reading:
- **Headline:** disaggregated to individual streams the law is *stronger* (−0.91), not weaker —
  the aggregate r is not masking within-regime heterogeneity.
- Seed bootstrap CI is extremely tight: the 7 regime means are stable estimates.
- LORO worst case (−0.72 without DDoS) is expected: DDoS anchors the degraded end of the range.
- LODO worst case (−0.52 without CICIDS) is honest range restriction: removing all four benefit
  regimes at once removes most of the variance in deployed-model degradation; the sign persists.
  Reported as such in the manuscript — attenuation, not inversion.

Manuscript changes: robustness sentence in §5.2, Table 7 in the appendix (CAS + IEEE), scope
paragraph in Discussion (deployment-decision rule, not NIDS-specific fix), REPRODUCE.md updated.
Audit extended to 84 checks (10 pinned numbers + Table-7 freshness sentinel), all passing.
