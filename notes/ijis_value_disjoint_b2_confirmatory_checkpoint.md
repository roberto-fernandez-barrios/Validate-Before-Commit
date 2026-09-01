# IJIS exact-value-disjoint B2 confirmatory checkpoint

Date: 2026-09-01

## Execution integrity

- protocol commit: `f8a02d4fe4e7b96d81e1695e094a2e708cd1960b`;
- implementation commit: `48e6f70b659b5ad036d0d14190f22e3e4658c1e9`;
- frozen config: `configs/ijis_exact_value_disjoint_b2_v1.json`, SHA-256
  `330e73d77c017a369765927c53e84d59acac449c7c00eebdcba75d3931d4399e`;
- seeds: exactly 7001--7030, once;
- matrix: 21/21 arms complete in authorized `run` mode;
- wall time: 2,749.6 s (19:20:09.995--20:05:59.629 Europe/Madrid);
- aggregate per-arm duration: 2,742.2 s;
- recorded source commit: implementation commit in all 21 arms;
- dirty runs, substituted seeds, retries or parameter changes: 0.

All 630 arm-seed role audits are PASS. Exact-X overlap is zero for window/train,
window/probe and train/probe in every audit; input/output row counts and multiplicity agree;
the maximum stratum-role deviation is 0.005721 pp. Raw-stream hashes agree across all
seven arms within each scenario. The frozen analysis verified 698 nested candidate pairs
and equal proposal-time severities; all 90 naive seed-scenario pairs remained exactly
proposal-coupled.

## Registered B2 result

Inferential unit: seed (`n=30`). Effects are `naive_2000 - naive_512` in balanced-accuracy
percentage points. Primary p-values are deterministic centered paired-bootstrap p-values
(100,000 resamples) with Holm correction over the three G2 cells.

| Scenario | Effect (pp) | 95% CI | 90% CI | Holm p | Registered cell |
|---|---:|---:|---:|---:|---|
| CICIDS2017 PortScan | +0.5276 | [0.2745, 0.7862] | [0.3125, 0.7461] | 0.000180 | SIZE BENEFIT |
| UNSW-NB15 Reconnaissance | +1.6734 | [1.4703, 1.8867] | [1.5000, 1.8510] | 0.000030 | SIZE BENEFIT |
| ToN-IoT Scanning | +0.3815 | [0.2068, 0.5695] | [0.2341, 0.5367] | 0.000180 | RESOLVED SUB-MATERIAL |

Mechanical program verdict: **PARTIAL ROBUSTNESS**. The historical
`HOMOGENEOUS-SIZE-BENEFIT` label does not survive exact-feature-disjoint roles because the
resolved ToN-IoT effect is below the registered +0.5-pp materiality threshold. The
directional positive size effect persists in all three datasets, but a homogeneous
material-benefit claim is no longer permitted.

The other registered primary estimands are in `paired_contrasts.csv` and
`multiplicity.csv`: both candidate sizes improve on never materially for PortScan and
UNSW; for ToN, the 2,000/class arm improves on never (+1.0643 pp, Holm p=0.01688), while
the 512/class arm is unresolved (+0.6828 pp, Holm p=0.07359). At 2,000/class the point
gate is not resolved against always-deploy in any dataset. Strict versus always-deploy is
resolved but sub-material for UNSW (-0.4208 pp, Holm p=0.01800) and unresolved elsewhere.
The only Holm-resolved gate-by-size interaction is strict in UNSW (-0.4776 pp,
Holm p=0.03660), also sub-material relative to the 0.5-pp margin.

## Independent comparison with historical B2

G5 is `new G2 - historical G2`, using independent seed-block bootstrap inference and Holm
correction across three scenarios. It is a role-design contrast, not a causal estimate of
duplicate leakage alone.

| Scenario | Historical | New | Change (pp) | 95% CI | Holm p | Classification |
|---|---:|---:|---:|---:|---:|---|
| PortScan | +0.8224 | +0.5276 | -0.2948 | [-0.5979, 0.0070] | 0.11166 | UNRESOLVED |
| UNSW | +1.6617 | +1.6734 | +0.0117 | [-0.2430, 0.2763] | 0.92971 | COMPATIBLE |
| ToN | +0.9984 | +0.3815 | -0.6169 | [-1.0435, -0.1867] | 0.01485 | MATERIAL ATTENUATION |

Only one scenario shows registered material attenuation and none shows material
amplification. Therefore the frozen rule returns
`original_b2_materially_inflated = false`: the data do not license the claim that exact
duplicate exposure materially inflated the original B2 program as a whole. They do
require removal of the homogeneous-material-benefit headline and explicit reporting of
the ToN attenuation.

No rescue experiment or follow-up analysis is authorized.
