## What changed since v1.1.0

Two new pre-fixed robustness phases close the last two experimental objections from an
external mock review, plus a statistics-hardening revision of the central analysis.

**Phase 2i — replay retraining baseline.** `--adapt-strategy replay` (retrain-current-plus-
replay, 50/50). Replay does NOT rescue naive triggering: significantly net-harmful in the harm
regime (−4.54 [−7.06, −2.34] vs no-adaptation; worse than full replacement's −1.36) and
benefit-lossy elsewhere (+6.59 vs +7.79). The gate composes with the update rule: on top of
replay it restores safety (ToN +0.59) and recovers the lost benefit (PortScan +8.26).

**Phase 2j — probe prevalence.** `--probe-prevalence` draws the labeled probe at the traffic's
natural attack prevalence. The gate is essentially indifferent: full safety and benefit at
π = 0.10 and even π = 0.01 (a single attack flow per probe); a 10× inspection budget changes
nothing. The operative requirement is one labeled attack flow per decision, not a balanced
sample.

**Coupling-aware §5.2.** The degradation–benefit correlation is mathematically coupled
(exhaustive re-pairing null: median r = −0.91; observed −0.89 not more extreme, p = 0.80) and
is withdrawn as evidence. Replaced by (1) restoration-to-ceiling (σ 3.5 vs 7.4 pts, slope
−0.87) and (2) the coupling-free contrast: within a deployment, detector scores are
uninformative about the gain (per-seed r median +0.06) while deployed BA tracks it (−0.68).

**Manuscript.** Overclaims softened (random label corruption, never *significantly* worse,
policy oracle, pre-registered non-inferiority margins stated); dangling appendix references
fixed; full protocol detail added (candidate trains at current severity, never the final
pool; train/probe disjointness; all sizes); Limitations rewritten. Claims audit extended to
112 checks, all passing.
