# IJIS exact-value-disjoint protocol preflight

Date: 2026-09-01

Baseline: `5bb5c5336448e941d1bb7aba6b1793fe4b18cac8`

Frozen inputs:

- protocol SHA-256: `ee559f802badd302f79c9371bfb4c194cef9df55b163afa3ee5d381c510bd699`
- B2 config SHA-256: `330e73d77c017a369765927c53e84d59acac449c7c00eebdcba75d3931d4399e`
- B1 config SHA-256: `bd2c0e14b6c3bae2524749160300f1aa35ab6c508ee93883964b87d634b39815`
- forensic CSV SHA-256: `83014444149ff5da3e56ebf48f339f9f69003276e80c37de8dcfa5fea8b28f08`

This preflight sees the historical overlap diagnostics but no output from the new
sensitivity. It evaluates whether the registered design can distinguish its outcomes and
whether implementation can proceed without discretionary scientific choices.

## Attack matrix

| Threat | Hostile check | Frozen control | Verdict |
|---|---|---|---|
| Group-assignment bias | Can model performance, labels or policy history affect which role receives a group? | Assignment reads only seed, exact feature hash and the group's four stratum counts. It is completed before model construction. | PASS |
| Hash ambiguity | Could two unequal vectors be treated as one group? | SHA-256 matches require actual canonical-vector equality; a mismatch aborts. | PASS |
| Signed-zero / dtype drift | Could irrelevant byte differences defeat grouping? | Exact little-endian float64 after the existing cleaner; only signed zero canonicalized; no rounding. | PASS |
| Contradictory labels | Could label conflict be hidden by `(X,y)` grouping, deletion or voting? | Key is X only. All original rows and labels remain together. The forensic audit reports 403 conflicting-X groups / 1,828 rows in UNSW. | PASS |
| Empirical-frequency deletion | Does the design globally deduplicate repeated flows? | No. Multiplicity is preserved inside the assigned role and sampling remains with replacement. | PASS |
| Insufficient strata | Could whole-group placement empty a required pool or prevent registered draws? | Smallest source stratum is UNSW current attack (3,496 rows; nominal probe target about 699). All sampling is with replacement. The algorithm must additionally meet <=0.50-pp deviation and non-empty checks for every stratum/role before any model run; failure is a blocker. | PASS |
| Hidden exact-X overlap | Is absence of crossing assumed rather than tested? | Postcondition computes exact-X intersections for all three role pairs and requires zero before environment construction. | PASS |
| Source-row loss/duplication | Can grouping drop or duplicate rows? | Row-index accounting requires each original row exactly once; per-stratum and total multiplicity must match input. | PASS |
| Replacement sampling | Could removing replacement silently change B512/B2000 semantics? | Replacement remains unchanged within role. Only role assignment changes. | PASS |
| Nested candidates | Could B512 cease to be the exact prefix of B2000? | Same B512 then E1488 RNG construction and provenance-hash assertion are mandatory. | PASS |
| Proposal-time domain | Could sizes sample different severity mixtures? | Both nested draws use the same frozen proposal-time severity; equality is asserted. | PASS |
| Historical regression | Could the new splitter silently alter v1.23.0 paths? | New explicit mode only; flag-off byte-parity test is mandatory and old splitter remains present. | PASS |
| Seed reuse | Are 7001-7030 / 8001-8030 virgin? | All stored `run_config.json` seed arrays and configs/ledgers were scanned. No collisions. Smoke blocks 7401-7402 / 8401-8402 are also unused. | PASS |
| Confirmatory leakage into smoke | Can the CLI execute reserved seeds in a development mode? | Existing firewall plus new-config tests must reject confirmatory seeds outside authorized run mode. | PASS |
| Multiplicity | Can conclusions be selected from many contrasts? | B2 G1-G5 and B1 PF1/PF2/PF3/SF4/SF5 are fixed, Holm-corrected within their original scientific families. Anchor/descriptive results remain labelled. | PASS |
| Null distinguishability | Can a null result receive a non-material label? | Both B2 and B1 retain CI90-inside-+/-0.5 COMPATIBLE/NO-MATERIAL rules. Historical standard errors show these regions are attainable with 30 seeds; sign frequency is never an outcome rule. | PASS |
| Post-hoc taxonomy | Could a disappointing pattern trigger a new rule? | Ordered B2 and B1 robustness classifications are fully machine-evaluable and frozen here. Every pattern has an allowed terminal interpretation; no follow-up experiment is authorized. | PASS |
| Original-result comparison | Could numerical change be called causal duplicate bias? | G5 is explicitly an independent-block design sensitivity. It may show attenuation/amplification, not isolate duplicate exposure causally. | PASS |
| Policy cherry-picking | Could unfavorable B1 rows be removed? | Complete amended 96-arm policy matrix is frozen; no policy removal or tuning is authorized. | PASS |
| DDM/ADWIN tuning | Could reference parameters be optimized after inspection? | Original registered reference parameters are retained; no sweep or delta change. | PASS |
| Partial-run recovery | Could failed runs lead to selective retries? | Only invariant-restoring bug recovery is permitted, with quarantine, committed diagnosis and one complete same-seed restart. No parameter/seed substitution. | PASS |

## Design feasibility and stop boundary

The forensic audit establishes that the allegation is measurable on the exact cleaned raw
representation and that all three datasets have ample rows in every registered stratum.
The group assignment is outcome-blind and the 0.50-pp fraction tolerance is an explicit
implementation gate, not a target that may be relaxed. The preflight therefore authorizes
implementation and smoke only. It does not authorize confirmatory execution until all 15
implementation gates and the frozen analysis scripts are committed.

## Verdict

**PASS**

