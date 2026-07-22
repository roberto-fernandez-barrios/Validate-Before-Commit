# Symmetric-pipeline confirmatory phase — technical pre-flight

Date: 2026-07-22, immediately BEFORE authorizing seeds 3001-3030.
Branch: `feature/symmetric-pipeline-replication`.

## Commit state

| commit | content |
|---|---|
| `8838566` | Frozen protocol (unmodified) |
| `2d93fe4` | Architecture (unmodified) |
| `bd6bcbb` | Driver + config + T1-T12 tests + parity PASS (unmodified) |
| `96576bb` | Appendix A: human-approved margins + machine-evaluable A/B/C rules |
| `29c55c6` | Manifest side-effect fix (tests no longer mutate the sealed manifest) |
| `a33837f` | Complete preprocessing provenance in ModelPipeline metadata + 3 tests |

Pre-existing protocol commits were NOT amended; margins/decision rules were
added as the dated Appendix A per instruction.

## Gates (all executed at `a33837f`)

| gate | result |
|---|---|
| `pytest tests -q` | **87/87** (83 previous + 3 provenance + 1 manifest-mutation guard) |
| `audit_paper2_claims` | **538/538** |
| `verify_results_manifest` | **164/164** pinned CSVs, 0 unpinned extras |
| sealed `results/final_manifest.json` | byte-identical after full pytest run (`11474601...052a5b12`) — side effect fixed |
| tracked working tree | clean (only the 2 excluded personal untracked files) |
| `--list-arms` | **42 confirmatory arms**, reserved seeds 3001-3030 reported |
| `--dry-run` | 42 arms enumerated, nothing executed, firewall confirmed |
| config hash | `configs/symmetric_pipeline_dynamic_v1.json` = `52794778...893d40e8` |

## Seed hygiene

- Confirmatory seeds 3001-3030: absent from every existing output (seed-column
  scan over all smoke/parity by_seed CSVs: parity uses 501-530, smoke 4242-4243).
- Smoke seeds (4242-4243) are outside the reserved block.
- `results/raw/symmetric_pipeline/` did not exist at pre-flight.

## Process hygiene

- No background processes launched; all runs in this phase are synchronous.

## Verdict

PRE-FLIGHT PASS — authorized to execute the frozen 42-arm confirmatory matrix
with seeds 3001-3030 via
`run_symmetric_pipeline_replication --run --confirmatory-authorized`.
