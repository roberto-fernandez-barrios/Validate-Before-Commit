# Frontier driver forensic recovery report

Date: 2026-07-21. Context: `notes/q1_final_acceptance_patch_protocol.md` (Block B) requires
re-running the budget-frontier arms affected by the deferred-commit temporal fix, but the
driver that produced the published `results/raw/q1fc_*` arms (`run_q1_faseC.py`, referenced at
`src/analysis/make_paper2_q1_frontier.py:6`) was never committed to the repository.

## Outcome: DRIVER RECOVERED AND VALIDATED (Ruta A)

- **Recovered file:** `run_q1_faseC.py`, 113 lines,
  SHA256 `655309bfec1c01924fd8708b6bde4c2ee055021ba6461959aea5502df11737c7`.
- **Location found:** scratchpad of Claude Code session `68de88a2-0b70-4114-8d9f-69757ab336df`
  (`%LOCALAPPDATA%\Temp\claude\C--Users-masteria-DOMINE-RF-paper-2\68de88a2-…\scratchpad\`),
  alongside `run_q1_faseD.py` (chronological matrix) and `run_q1_faseD5.py` (operational arm),
  also copied out for provenance.
- **Verbatim copy preserved:** retained locally (unversioned; it embeds machine-specific
  absolute paths) and identified unambiguously by the SHA256 above; the canonical, committed
  form of the driver is `src/experiments/run_q1_budget_frontier.py` +
  `configs/q1_budget_frontier_v2.json`, validated bit-identical against the published arms.
- **Committed replacement:** `src/experiments/run_q1_budget_frontier.py` +
  `configs/q1_budget_frontier_v2.json` (all parameters explicit; per-arm `run_config.json`,
  `command.txt`, `environment.json`, completion marker, run ledger, `--dry-run/--list-arms/
  --only-arm/--range/--resume/--force/--validate-complete`).

## Places inspected (in order)

| # | Source | Method | Result |
|---|--------|--------|--------|
| 1 | Git history (all refs) | `git log --all --full-history --name-only` on `*faseC*`, `*frontier*`; `-S` pickaxe on `q1fc_`, `--lifetime-alpha`, `--vbc-defer-mode` | Only analysis/aggregator files; driver never committed |
| 2 | Git reflog | `git reflog --all` | Linear history, no deleted branches with the driver |
| 3 | Git object store | `git fsck --full --no-reflogs --unreachable`, `--lost-found`; inspected all 16 unreachable blobs, 1 dangling commit, 2 unreachable trees | No driver. (Side finding: dangling commit `390884f` = untracking of planning docs; unreachable trees hold old manuscript snapshots) |
| 4 | Gitignored files on disk | `git status --ignored` | `PLAN_Q1_CLAUDE_CODE.md` present but contains no frontier commands |
| 5 | Claude Code transcripts | grep over `~/.claude/projects/**/*.jsonl` for `q1fc_`, `run_q1_faseC` | Session `68de88a2` shows the driver being written and run (`frontier-range 0 50` / `50 99` from its scratchpad) |
| 6 | Claude Code file-history | `~/.claude/file-history/68de88a2-*/` | Snapshots of other edited files; driver was in scratchpad, not file-history |
| 7 | **Old session scratchpad** | direct listing | **`run_q1_faseC.py` found intact** (with `run_q1_faseD.py`, `run_q1_faseD5.py`) |
| 8 | Terminal history | PSReadLine `ConsoleHost_history.txt`, `~/.bash_history` | Not needed after (7); not inspected further |
| 9 | `__pycache__` / compiled copies | repo-wide glob | No `run_q1_faseC*.pyc` |
| 10 | Output evidence | 99 arm dirs + sibling `.log` files, by_seed/window CSVs | Logs record data files + seeds only (no argv); CSVs allowed parameter fingerprinting (below) |

## Why the earlier reconstruction failed

The driver passes **only the gate/policy flags** and relies on the runner's argparse defaults
for every fixed stream parameter. The failed reconstruction guessed `--window-size 256
--calibration-windows 30 --detector-ref-size-per-class 256` etc.; the actual values are the
runner defaults, notably **window-size 128**. BA quantization in 1/128 steps is consistent with
window 128 (the earlier 1/256-step reading of `0.96094 = 246/256` is equally `123/128`).

## Recovered configuration (parameter table)

| Parameter | Value | Source | Confidence |
|---|---|---|---|
| scenarios | ps_full, ton_full, ton_zero | driver `SCENARIOS` | exact |
| ps_full data | Tuesday → Friday-PortScan (CICIDS2017 CSVs) | driver `DATA` | exact |
| ton_* data | `data/processed/ton_iot_q1_gate/ton_iot_{ref_no,cur}_scanning_binary.csv` | driver `DATA` | exact |
| ton_zero extras | `--trigger-mode random --trigger-prob 0.05 --max-severity 0` | driver `SCENARIOS` | exact |
| anchors | none; point = labeled_probe b=32; strict = + `--gate-margin 0.001` | driver `ANCHORS` | exact |
| policies | ebcsdef / vbccoh / vbcref (gate + defer-mode flags) | driver `POLICIES` | exact |
| policy flags | `--probe-size {cap} --seq-block 16 --defer-windows 5 --seqav-alpha 0.10 --lifetime-alpha 0.10 --alpha-spending {sch}` | driver `frontier_arms()` | exact |
| caps / schedules | {64,128,256,512,1024} × {bonferroni,pseries} | driver | exact |
| seeds | 501–530, one process per arm | driver `SEEDS` | exact |
| methods | ks_max | driver `run_arm` | exact |
| all remaining params | runner argparse defaults (window 128, dim 8, train 2000/class, adapt 512/class, detector-ref 256/class, post 100, ramp 80, max-sev 1.0, calib 30, thr-q 0.95, k=3, cooldown 10, svc_rbf, ks max, full_replace, detector trigger, pools, prevalence 0.5, no-probe commit, lifetime-max-proposals 10) | absence of flags in driver + argparse | exact (validated by bit-identity) |

## Bit-identity validation (criterion for "recovered")

Arms without deferred commits are provably unaffected by the temporal fix (the loop reorder
changes behaviour only at deferred COMMIT resolution windows and downstream), so they must
reproduce bit-for-bit under the corrected runner.

- **Single-seed pre-check** — `q1fc_ps_full_vbcref_c512_bonf`, seed 501, corrected runner:
  `window_results` (200 rows × 14 shared cols), `trigger_log` (8 rows × 29 cols),
  `resolution_log` (7 rows × 20 cols), `by_seed` (33 shared cols) all **bit-identical** to the
  published arm (the only non-shared column is the new, documented `served_model_version`;
  a `vbc_defer_mode` flag initially reported as differing was a NaN-comparison artifact —
  equal under NaN-aware comparison).
- **Full-arm validation (30 seeds × 3 arms)** — `q1fc_ps_full_vbcref_c512_bonf` (PortScan,
  no deferred commits), `q1fc_ton_full_vbcref_c256_bonf` (ToN, no deferred commits),
  `q1fc_ton_zero_ebcsdef_c256_bonf` (zero drift): results recorded in the checkpoint
  (threshold, trigger count, adaptation count, labels, mean BA, summary/window CSVs).

## Affected-arm classification

From the published resolution logs: **27 of 99 arms** contain ≥1 deferred commit (19 in
ps_full: ebcsdef all 10 cells + vbccoh 9 cells; 8 in ton_full: ebcsdef 6 + vbccoh 2; 0 in
ton_zero; 0 in vbcref anywhere). Structural argument for the other 72: the reorder leaves
every window bit-identical unless a pending deferred decision resolves as COMMIT (pending
continuations that end in futility/cap-reject consume the same RNG draws, log the same
resolution rows, and never touch model/detector/alarms/cooldown), so an arm whose resolution
log has zero deferred commits is provably byte-equal under the fix. Those 72 published arms
are therefore **reused**, and the 27 affected arms are re-executed with the committed driver.
