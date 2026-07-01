from __future__ import annotations

from pathlib import Path
import csv
import json
import py_compile
import runpy
import shutil
import subprocess
import sys


CORE_SCRIPT = Path("src/experiments/run_paper2_progressive_readaptation.py")
RUNNER_SCRIPT = Path("src/experiments/run_paper2_safe_readaptation_phase1.py")
SMOKE_OUTDIR = Path("results/raw/paper2_safe_readaptation_phase1_preflight_smoke_001")
PHASE1_OUTDIR = Path("results/raw/paper2_safe_readaptation_phase1_001")

EXPECTED_POLICIES = [
    "legacy_consecutive3_cooldown10",
    "k2_of_3_cooldown0",
    "k3_of_5_cooldown0",
    "k2_of_3_cooldown3",
    "k3_of_5_cooldown5",
]

EXPECTED_REGIMES = [
    "cicids_portscan",
    "unsw_nb15_reconnaissance",
    "ton_iot_scanning",
]

EXPECTED_DETECTORS = ["qk_mmd_zz", "ks_max"]

REQUIRED_SUMMARY_COLUMNS = {
    "policy_name",
    "adaptation_policy",
    "policy_k",
    "policy_n",
    "cooldown_windows",
    "method",
    "n_seeds",
    "mean_balanced_accuracy",
    "cumulative_gain_vs_no_adapt_mean",
    "n_adaptations_mean",
}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def check_file_exists(path: Path) -> None:
    if not path.exists():
        fail(f"Missing file: {path}")
    ok(f"Exists: {path}")


def check_syntax(path: Path) -> None:
    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as exc:
        fail(f"Syntax error in {path}: {exc}")
    ok(f"Syntax OK: {path}")


def check_core_policy_patch() -> None:
    text = CORE_SCRIPT.read_text(encoding="utf-8")

    required_snippets = [
        '--adaptation-policy',
        '--policy-k',
        '--policy-n',
        '--policy-name',
        'policy_name = args.policy_name or',
        'trigger_condition',
        'args.adaptation_policy == "k_of_n"',
        '"policy_name": policy_name',
        '"adaptation_policy": args.adaptation_policy',
        '"policy_k": policy_k',
        '"policy_n": policy_n',
        '"cooldown_windows": args.cooldown_windows',
        '.groupby(["policy_name", "adaptation_policy", "policy_k", "policy_n", "cooldown_windows", "method"], dropna=False)',
    ]

    missing = [s for s in required_snippets if s not in text]
    if missing:
        fail("Core policy patch incomplete. Missing snippets:\n" + "\n".join(missing))

    ok("Core script contains policy arguments, k-of-n logic, metadata, and grouped summaries")


def check_runner_config() -> None:
    ns = runpy.run_path(str(RUNNER_SCRIPT))

    if "POLICIES" not in ns:
        fail("Runner has no POLICIES variable")

    policies = ns["POLICIES"]
    names = [p["name"] for p in policies]

    if names != EXPECTED_POLICIES:
        fail(
            "Runner policies do not match protocol.\n"
            f"Expected: {EXPECTED_POLICIES}\n"
            f"Found:    {names}"
        )

    for p in policies:
        for key in ["name", "adaptation_policy", "policy_k", "policy_n", "cooldown"]:
            if key not in p:
                fail(f"Policy missing key {key}: {p}")

        k = int(p["policy_k"])
        n = int(p["policy_n"])
        cd = int(p["cooldown"])

        if k <= 0 or n <= 0 or k > n:
            fail(f"Invalid policy k/n: {p}")

        if cd < 0:
            fail(f"Invalid negative cooldown: {p}")

        if p["adaptation_policy"] not in {"consecutive", "k_of_n"}:
            fail(f"Invalid adaptation_policy: {p}")

    ok("Runner policies match Phase 1 protocol")

    if "build_regimes" not in ns:
        fail("Runner has no build_regimes function")

    regimes = ns["build_regimes"]()
    regime_names = [r["name"] for r in regimes]

    if regime_names != EXPECTED_REGIMES:
        fail(
            "Runner regimes do not match protocol.\n"
            f"Expected: {EXPECTED_REGIMES}\n"
            f"Found:    {regime_names}"
        )

    for r in regimes:
        for key in ["name", "data_ref", "data_cur", "label_col"]:
            if key not in r:
                fail(f"Regime missing key {key}: {r}")

        if not Path(r["data_ref"]).exists():
            fail(f"Missing data_ref for {r['name']}: {r['data_ref']}")

        if not Path(r["data_cur"]).exists():
            fail(f"Missing data_cur for {r['name']}: {r['data_cur']}")

    ok("Runner regimes resolve to existing files")

    if "command_for" not in ns:
        fail("Runner has no command_for function")

    commands = []
    for r in regimes:
        for p in policies:
            cmd = ns["command_for"](r, p)
            joined = " ".join(str(x) for x in cmd)
            commands.append(joined)

            for detector in EXPECTED_DETECTORS:
                if detector not in joined:
                    fail(f"Detector {detector} missing from command: {joined}")

            for token in [
                "--adaptation-policy",
                "--policy-k",
                "--policy-n",
                "--policy-name",
                "--cooldown-windows",
            ]:
                if token not in joined:
                    fail(f"Missing token {token} in command: {joined}")

    expected_n = len(EXPECTED_REGIMES) * len(EXPECTED_POLICIES)
    if len(commands) != expected_n:
        fail(f"Expected {expected_n} commands, found {len(commands)}")

    ok(f"Runner builds {expected_n} commands with expected detectors and policy args")


def run_dry_run() -> None:
    cmd = [sys.executable, "-m", "src.experiments.run_paper2_safe_readaptation_phase1"]
    proc = subprocess.run(cmd, text=True, capture_output=True)

    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        fail("Phase 1 runner dry-run failed")

    out = proc.stdout + proc.stderr

    for name in EXPECTED_POLICIES:
        if name not in out:
            fail(f"Dry-run output missing policy: {name}")

    for name in EXPECTED_REGIMES:
        if name not in out:
            fail(f"Dry-run output missing regime: {name}")

    if "--execute" in out:
        fail("Dry-run output unexpectedly includes execution mode confusion")

    ok("Runner dry-run works and prints expected regimes/policies")


def run_metadata_smoke() -> None:
    if SMOKE_OUTDIR.exists():
        shutil.rmtree(SMOKE_OUTDIR)

    cmd = [
        sys.executable,
        "-m",
        "src.experiments.run_paper2_progressive_readaptation",
        "--data-ref",
        "data/processed/ton_iot_q1_gate/ton_iot_ref_no_scanning_binary.csv",
        "--data-cur",
        "data/processed/ton_iot_q1_gate/ton_iot_cur_scanning_binary.csv",
        "--label-col",
        "Label",
        "--outdir",
        str(SMOKE_OUTDIR),
        "--seeds",
        "1",
        "--methods",
        "ks_max",
        "--post-windows",
        "5",
        "--ramp-windows",
        "5",
        "--calibration-windows",
        "3",
        "--n-permutations",
        "10",
        "--adaptation-policy",
        "k_of_n",
        "--policy-k",
        "2",
        "--policy-n",
        "3",
        "--policy-name",
        "preflight_k2_of_3_cooldown1",
        "--cooldown-windows",
        "1",
        "--ks-reduction",
        "max",
    ]

    proc = subprocess.run(cmd, text=True, capture_output=True)

    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        fail("Metadata smoke run failed")

    summary_path = SMOKE_OUTDIR / "paper2_progressive_readaptation_summary.csv"
    by_seed_path = SMOKE_OUTDIR / "paper2_progressive_readaptation_by_seed.csv"
    window_path = SMOKE_OUTDIR / "paper2_progressive_readaptation_window_results.csv"

    for p in [summary_path, by_seed_path, window_path]:
        if not p.exists():
            fail(f"Smoke did not create expected output: {p}")

    with summary_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = set(reader.fieldnames or [])
        rows = list(reader)

    missing_cols = REQUIRED_SUMMARY_COLUMNS - cols
    if missing_cols:
        fail(f"Summary missing required metadata columns: {sorted(missing_cols)}")

    if not rows:
        fail("Smoke summary has no rows")

    policy_names = {r.get("policy_name", "") for r in rows}
    if policy_names != {"preflight_k2_of_3_cooldown1"}:
        fail(f"Unexpected policy names in smoke summary: {policy_names}")

    methods = {r.get("method", "") for r in rows}
    if not {"ks_max", "no_adaptation"}.issubset(methods):
        fail(f"Smoke summary missing ks_max or no_adaptation rows: {methods}")

    for r in rows:
        if r.get("adaptation_policy") != "k_of_n":
            fail(f"Unexpected adaptation_policy row: {r}")
        if str(r.get("policy_k")) not in {"2", "2.0"}:
            fail(f"Unexpected policy_k row: {r}")
        if str(r.get("policy_n")) not in {"3", "3.0"}:
            fail(f"Unexpected policy_n row: {r}")
        if str(r.get("cooldown_windows")) not in {"1", "1.0"}:
            fail(f"Unexpected cooldown row: {r}")

    ok("Metadata smoke run works and summary contains policy metadata")


def check_phase1_not_accidentally_started() -> None:
    if not PHASE1_OUTDIR.exists():
        ok("Phase 1 output directory does not exist yet")
        return

    summaries = list(PHASE1_OUTDIR.rglob("paper2_progressive_readaptation_summary.csv"))
    if summaries:
        print("[WARN] Phase 1 output summaries already exist:")
        for p in summaries:
            print(f"  - {p}")
        print("[WARN] This is not fatal, but be careful not to mix old/partial Phase 1 runs.")
    else:
        ok("Phase 1 directory exists but no summary files found")


def main() -> None:
    print("=" * 100)
    print("PAPER 2 SAFE READAPTATION PHASE 1 PREFLIGHT")
    print("=" * 100)

    check_file_exists(CORE_SCRIPT)
    check_file_exists(RUNNER_SCRIPT)

    check_syntax(CORE_SCRIPT)
    check_syntax(RUNNER_SCRIPT)

    check_core_policy_patch()
    check_runner_config()
    run_dry_run()
    run_metadata_smoke()
    check_phase1_not_accidentally_started()

    print()
    print("=" * 100)
    print("[PASS] PREFLIGHT PASSED")
    print("=" * 100)
    print()
    print("You can now run:")
    print("python -m src.experiments.run_paper2_safe_readaptation_phase1 --execute")


if __name__ == "__main__":
    main()
