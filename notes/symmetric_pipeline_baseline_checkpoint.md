# Symmetric-pipeline initial phase — baseline checkpoint (Bloque 0)

Date: 2026-07-22
Purpose: record the exact state of the sealed v1.20.2 baseline BEFORE any
symmetric-pipeline refactor work begins, so the phase can prove at its end that
nothing scientific changed.

## Baseline identity

| item | value |
|---|---|
| branch at audit time | `main` |
| HEAD | `3b00cc406ed22e7e8fbbdd0f4f517f2d0353888c` (matches sealed baseline) |
| tag at HEAD | `v1.20.2` |
| source commit (sealed) | `031f86f3eb094f9569f3e5f0b3c420954ef9a9bb` |
| version DOI | `10.5281/zenodo.21481392` |
| concept DOI | `10.5281/zenodo.21322256` |

## Working tree at audit time (`git status --short`)

```
?? PLAN_Q1_DEFINITIVO_VBC.md
?? notes/recovered_run_q1_faseC.py.txt
```

Both are pre-existing PERSONAL / recovery files, untracked, expressly excluded
from this phase. They are not modified, not versioned, and not part of any
commit of this phase.

## Baseline gates (executed at HEAD, before any change)

Interpreter: conda env `paper2`
(`C:\Users\masteria.DOMINE\AppData\Local\miniconda3\envs\paper2\python.exe`,
Python 3.11.15).

| command | result |
|---|---|
| `$PY -m pytest tests -q` | **67 passed** (67/67) |
| `$PY -m src.analysis.audit_paper2_claims` | **AUDIT: 538/538 checks pass** |
| `$PY -m src.analysis.verify_results_manifest` | **164 pinned CSVs match MANIFEST.sha256 (0 unpinned extras)** — no orphan/unpinned dirs |

## Scientific artifact hashes (SHA-256, at baseline)

| file | sha256 |
|---|---|
| `results/final_manifest.json` | `5f0fb6bf5c9edea8988dc79825a083762e23318cc186f7ed7b9394f3d13642c0` |
| `results/tables/MANIFEST.sha256` | `dcf322681f5863d120ebda03a76abd0d17825f9f93fdd3aa96f491d0e4420c36` |

`results/tables/MANIFEST.sha256` itself pins the SHA-256 of every one of the
164 scientific CSVs; `verify_results_manifest` PASSED against it at baseline,
so these two hashes transitively freeze the entire scientific CSV set. Any
change to any scientific CSV during this phase will be detected by re-running
`verify_results_manifest` plus re-hashing these two files at the end of the
phase.

## Seed-ledger snapshot (from `results/final_experiment_ledger.csv`)

Seed windows already consumed by published evidence blocks:
`104-133`, `501-530`, `601-630`, `701-730` (pilot), `801-830`,
`2001-2100` (pilot `104-133`). Runner default seed `101` also used historically.

The proposed confirmatory block **3001-3030** does not appear in any ledger,
config, note, source file, or test (grep audit executed 2026-07-22, no hits).
Proposed smoke seeds **4242, 4243** likewise have no hits anywhere.

## Confirmation

- v1.20.2 is intact at audit time: HEAD equals the sealing commit, the tag
  resolves to HEAD, all three gates pass, and the manifest hashes above match
  the sealed artifact.
- No tracked file had uncommitted modifications at audit time.
- Work proceeds exclusively on `feature/symmetric-pipeline-replication`.
