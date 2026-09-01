# IJIS exact-value-disjoint results audit

Date: 2026-09-01

## Integrity basis

- Frozen protocol commit: `f8a02d4fe4e7b96d81e1695e094a2e708cd1960b`.
- Implementation commit: `48e6f70b659b5ad036d0d14190f22e3e4658c1e9`.
- B2 result commit: `93967ca2f1a20d1c654ca29e622daa5a4012b1cc`.
- B1 result commit: `e19ac3f362fa11799ed6de24015b7a840f73b01d`.
- B2: 21/21 arms, seeds 7001--7030, 630/630 role audits PASS.
- B1: 96/96 arms, seeds 8001--8030, 2,880/2,880 role audits PASS.
- Cross-role exact-X overlap groups: zero in every B2 and B1 arm-seed audit.
- All source rows, original labels and within-role multiplicity preserved.
- Maximum role/stratum deviation: 0.005721 percentage points, below the frozen 0.50-pp
  limit.
- Confirmatory runs with dirty trees, retries, substituted seeds or changed parameters: 0.

## Decision questions

### A. Does the 512 -> 2,000 effect survive exact-value-disjoint roles?

**Partially.** The effect remains positive and statistically resolved in all three
benchmarks. It is a registered `SIZE BENEFIT` for PortScan (+0.5276 pp, 95% CI
[0.2745,0.7862], Holm p=0.000180) and UNSW (+1.6734 pp, [1.4703,1.8867], Holm
p=0.000030). ToN is positive but `RESOLVED SUB-MATERIAL` (+0.3815 pp,
[0.2068,0.5695], Holm p=0.000180). The frozen B2 program verdict is
`PARTIAL ROBUSTNESS`.

### B. Is the effect homogeneous across the three benchmarks?

**No at the registered materiality threshold.** All directions are positive, but ToN does
not reach +0.5 pp. The historical `HOMOGENEOUS-SIZE-BENEFIT` label is falsified under
exact-feature-disjoint roles and must be removed as a headline claim.

### C. Does the conditional-validation conclusion survive?

**Yes, in a narrower form.** No evaluated policy globally dominates, policy behavior
still depends on candidate construction/evidence, and ATC remains non-material-cost
against point in five compatible cells plus one unresolved cell. However, validation is
not itself a universal safeguard: ATC retention against always-deploy is unresolved in
two full-drift datasets, and the calibrated ensemble incurs a material full-drift cost in
UNSW. The paper may retain “validation remains conditional,” but not a broad favorable
ATC/ensemble recommendation.

### D. Does policy ordering / ATC / ensemble interpretation survive?

**Partially.** The registered S4 ordering-change rule still fires for ATC and the
calibrated ensemble (and DoC), so the conclusion that policy ordering depends on candidate
size survives. The B1 aggregate verdict is `PARTIALLY ROBUST` (4/6 predicates, no direct
material gain/cost reversal). `ATC_RETENTION` and `ENSEMBLE_RETENTION` fail and all
affected text must be narrowed. DoC, replay, DDM and ADWIN each retain at least one
full-drift material-cost cell; DDM/ADWIN statements remain qualified as applying only
under registered reference parameters.

### E. Did exact duplicate exposure materially inflate the original effect?

**Not as a program-wide conclusion under the frozen rule.** The independent-block G5
comparison is compatible in UNSW (+0.0117 pp change), unresolved in PortScan (-0.2948 pp)
and shows material attenuation only in ToN (-0.6169 pp, 95% CI [-1.0435,-0.1867], Holm
p=0.01485). The preregistered “original B2 materially inflated” criterion required at
least two material attenuations and no amplification; it is not met. G5 compares two role
designs and is not a causal estimate of duplicate leakage alone.

### F. Is any core manuscript statement falsified?

**Yes, but a narrower publishable thesis remains.** Any statement that the candidate-size
benefit is materially homogeneous across all three benchmarks is falsified. Any statement
that the earlier favorable ATC or calibrated-ensemble retention interpretation is robust
is also unsupported. The following claims survive:

- candidate construction and evidence can materially alter promotion behavior;
- the 512 -> 2,000 direction persists under exact-feature-disjoint roles, with material
  benefit in two benchmarks and a resolved sub-material benefit in the third;
- policy ordering remains candidate-size dependent;
- validation remains conditional and no evaluated policy globally dominates;
- promotion evaluation is security-relevant because it affects the integrity of the
  deployed detector, without constituting a poisoning-defense claim.

## Required manuscript thesis

The defensible thesis is:

> Conclusions and policy rankings in adaptive-NIDS promotion are conditional on candidate
> construction and evidence. Registered controls show that these factors materially alter
> observed promotion behavior. Under exact-cleaned-feature-disjoint roles, increasing
> candidate evidence retains a positive resolved effect in all three benchmarks, but the
> material benefit is benchmark-dependent rather than homogeneous. Validation remains
> conditional, policy ordering remains size-dependent, and no evaluated update policy
> globally dominates.

No causal claim about exact duplicate exposure, no homogeneous-size-benefit label, and no
integrated operational-stack validation claim is permitted.

## Decision-gate verdict

**THESIS REQUIRES REVISION**

A narrower publishable thesis survives. No rescue experiment or additional scientific
development is authorized.
