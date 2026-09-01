# IJIS exact-value-disjoint B1 confirmatory checkpoint

Date: 2026-09-01

## Execution integrity

- protocol commit: `f8a02d4fe4e7b96d81e1695e094a2e708cd1960b`;
- implementation commit: `48e6f70b659b5ad036d0d14190f22e3e4658c1e9`;
- immediately preceding B2 result commit and recorded B1 source commit:
  `93967ca2f1a20d1c654ca29e622daa5a4012b1cc`;
- frozen config: `configs/ijis_exact_value_disjoint_b1_v1.json`, SHA-256
  `bd2c0e14b6c3bae2524749160300f1aa35ab6c508ee93883964b87d634b39815`;
- seeds: exactly 8001--8030, once;
- matrix: 96/96 arms complete in authorized `run` mode;
- wall time: 11,564.9 s (20:08:28.032--23:21:12.953 Europe/Madrid);
- aggregate per-arm duration: 11,535.6 s;
- dirty runs, substituted seeds, retries, removed policies or parameter changes: 0.

All 2,880 arm-seed role audits are PASS. Exact-X overlap is zero for window/train,
window/probe and train/probe throughout; all input rows and multiplicity are preserved;
the largest absolute stratum-role deviation is 0.005721 pp. Raw-stream hashes agree across
all arms within each of the six scenarios.

## Registered B1 robustness verdict

Mechanical verdict: **PARTIALLY ROBUST** (4/6 predicates, no direct primary
`MATERIAL GAIN` <-> `MATERIAL COST` reversal relative to historical B1).

| Frozen predicate | Result | Evidence summary |
|---|---|---|
| ATC_RETENTION | FAIL | Full drift: PortScan UNRESOLVED, UNSW UNRESOLVED, ToN COMPATIBLE; only one of three is compatible/gain. |
| ENSEMBLE_RETENTION | FAIL | Full drift: PortScan UNRESOLVED, UNSW MATERIAL COST, ToN COMPATIBLE. |
| COST_ALTERNATIVES | PASS | DoC, replay, DDM and ADWIN each have at least one full-drift MATERIAL COST. |
| ATC_VS_POINT | PASS | Five COMPATIBLE and one UNRESOLVED; no MATERIAL COST. |
| SIZE_DEPENDENT_ORDERING | PASS | Registered S4 fires for ATC and ensemble (and also DoC). |
| NO_GLOBAL_DOMINANCE | PASS | No policy with registered PF1/PF2 comparisons is MATERIAL GAIN in all six scenarios. |

## Policy detail

Effects below are policy minus naive at 2,000/class, in balanced-accuracy percentage
points. Primary p-values use the frozen centered paired bootstrap with Holm correction in
PF1/PF2; confidence intervals are 95% bootstrap intervals.

- **ATC:** full drift PortScan -1.5435 pp, CI [-2.7573,-0.5833], Holm p=0.08070,
  UNRESOLVED; UNSW -0.3094 pp, CI [-0.5560,-0.0602], Holm p=0.11672,
  UNRESOLVED; ToN -0.2154 pp, CI [-0.4372,-0.0518], Holm p=0.16662,
  COMPATIBLE. Against point, five of six cells are COMPATIBLE and PortScan full is
  UNRESOLVED; hence the weaker registered `ATC_VS_POINT` predicate survives, while the
  ATC-retention headline does not.
- **DoC:** full drift PortScan -2.4211 pp (Holm p=0.00744) and UNSW -0.8310 pp
  (Holm p=0.000180) are MATERIAL COST; ToN -0.1708 pp is COMPATIBLE.
- **Calibrated ensemble:** zero-drift PortScan +0.7250 and UNSW +0.5578 pp are MATERIAL
  GAIN (both Holm p=0.000180), but full-drift UNSW -0.6651 pp is MATERIAL COST
  (Holm p=0.000180); PortScan is UNRESOLVED and ToN COMPATIBLE. Thus its previously
  favorable retention interpretation is not robust.
- **Replay:** full-drift UNSW -2.5068 pp is MATERIAL COST (Holm p=0.000180); PortScan
  and ToN are COMPATIBLE.
- **river-DDM:** full-drift UNSW -2.9362 pp is MATERIAL COST (Holm p=0.000180);
  PortScan and ToN are UNRESOLVED. This is only under the registered reference parameters.
- **river-ADWIN:** MATERIAL COST in all three full-drift cells: PortScan -7.3279,
  UNSW -3.9089, ToN -3.0208 pp (Holm p=0.000180, 0.000180 and 0.04048). This is only
  under the registered reference parameters.
- **Point/strict:** remain descriptive anchors versus naive outside PF1/PF2. They are
  retained in all scenario/size cells and must not be promoted to globally superior
  policies. The registered estimator-versus-point family classifies ATC as five
  COMPATIBLE plus one UNRESOLVED; DoC has two full-drift MATERIAL COST cells and four
  COMPATIBLE cells.

The registered S4 ordering-change rule fires for ATC at PortScan/UNSW zero, DoC at
PortScan/UNSW zero, and ensemble at UNSW full. It does not fire for point or strict. The
scientific interpretation that ordering depends on candidate size therefore survives,
but the stronger historical readings for ATC and the calibrated ensemble require honest
narrowing.

No rescue experiment, policy removal, detector tuning or follow-up analysis is authorized.
