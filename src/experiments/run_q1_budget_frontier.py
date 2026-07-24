"""Registered budget-frontier driver (q1_max_protocol.md D3) -- committed, reproducible form.

History. The original Fase C driver (`run_q1_faseC.py`, 113 lines,
SHA256 655309bfec1c01924fd8708b6bde4c2ee055021ba6461959aea5502df11737c7) produced the 99
published `results/raw/q1fc_*` arms but was never committed; it relied on the runner's argparse
defaults for every fixed stream parameter and was validated bit-for-bit against the published
deferred-commit-free arms (see notes/frontier_driver_recovery_report.md). This driver replaces it: the grid
and every fixed parameter now live in configs/q1_budget_frontier_v2.json (nothing relies on
argparse defaults), each arm records its exact command, resolved configuration, environment and
source commit, and completed arms are protected against silent overwrite.

Usage:
  python -m src.experiments.run_q1_budget_frontier --list-arms
  python -m src.experiments.run_q1_budget_frontier --dry-run [--only-arm TAG | --range I J]
  python -m src.experiments.run_q1_budget_frontier --run [--only-arm TAG | --range I J]
                                                   [--resume] [--force] [--outroot DIR]
  python -m src.experiments.run_q1_budget_frontier --validate-complete

Per-arm outputs (in addition to the runner's CSVs):
  run_config.json   resolved flags, seeds, tag, source commit, runner module, timestamps
  command.txt       the exact argv executed
  environment.json  interpreter + key package versions + platform
  _COMPLETE         completion marker, written only after the output CSVs are verified

A run ledger is appended at results/raw/budget_frontier_run_ledger.csv.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import platform
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_PATH = os.path.join(ROOT, "configs", "q1_budget_frontier_v2.json")
MARKER = "_COMPLETE"
RUNNER_OUTPUTS = [
    "paper2_progressive_readaptation_by_seed.csv",
    "paper2_progressive_readaptation_window_results.csv",
    "paper2_progressive_readaptation_summary.csv",
]


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def seeds_csv(cfg: dict) -> str:
    s = cfg["seeds"]
    return ",".join(str(x) for x in range(s["start"], s["end"] + 1))


def _merge(*flag_dicts: dict) -> list[str]:
    """Merge flag dicts left-to-right (later overrides earlier), emit each flag once,
    in first-seen order -- so scenario overrides REPLACE fixed flags instead of
    duplicating them on the command line."""
    merged: dict[str, str] = {}
    for d in flag_dicts:
        merged.update(d)
    out: list[str] = []
    for k, v in merged.items():
        out += [k, v]
    return out


def frontier_arms(cfg: dict) -> list[dict]:
    """The registered 99-arm grid, in the ORIGINAL driver's enumeration order
    (anchors first, then policies x caps x schedules, per scenario)."""
    arms = []
    for sc, sdef in cfg["scenarios"].items():
        data = cfg["data"][sdef["data"]]
        for name, aflags in cfg["anchors"].items():
            arms.append(dict(tag=f"q1fc_{sc}_{name}", data=data,
                             flags=_merge(cfg["fixed_flags"], sdef["override_flags"], aflags)))
        for pol, pflags in cfg["policies"].items():
            for cap in cfg["caps"]:
                for sch in cfg["schedules"]:
                    tag = f"q1fc_{sc}_{pol}_c{cap}_{sch[:4]}"
                    arm_flags = dict(pflags)
                    arm_flags.update(cfg["policy_common_flags"])
                    arm_flags["--probe-size"] = str(cap)
                    arm_flags["--alpha-spending"] = sch
                    arms.append(dict(tag=tag, data=data,
                                     flags=_merge(cfg["fixed_flags"], sdef["override_flags"],
                                                  arm_flags)))
    if len(arms) != cfg["expected_arms"]:
        raise SystemExit(f"grid enumerates {len(arms)} arms, expected {cfg['expected_arms']}")
    tags = [a["tag"] for a in arms]
    if len(set(tags)) != len(tags):
        raise SystemExit("duplicate arm tags in grid")
    return arms


def build_cmd(cfg: dict, arm: dict, outdir: str) -> list[str]:
    return [sys.executable, "-m", cfg["runner_module"],
            "--data-ref", os.path.join(ROOT, arm["data"]["ref"]),
            "--data-cur", os.path.join(ROOT, arm["data"]["cur"]),
            "--outdir", outdir,
            "--seeds", seeds_csv(cfg),
            "--methods", cfg["methods"]] + arm["flags"]


def git_source() -> dict:
    def _git(*a):
        try:
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                                  text=True, timeout=30).stdout.strip()
        except Exception:
            return "unknown"
    return dict(source_commit_sha=_git("rev-parse", "HEAD"),
                working_tree_dirty=bool(_git("status", "--porcelain")))


def environment_info() -> dict:
    info = dict(python=sys.version, executable=sys.executable,
                platform=platform.platform())
    for mod in ("numpy", "pandas", "sklearn", "scipy"):
        try:
            info[mod] = __import__(mod).__version__
        except Exception:
            info[mod] = "unavailable"
    return info


def arm_complete(outdir: str, cfg: dict) -> bool:
    """Complete = marker present AND every runner CSV present AND the ks_max seed set in
    by_seed matches the registered seeds exactly."""
    if not os.path.exists(os.path.join(outdir, MARKER)):
        return False
    for f in RUNNER_OUTPUTS:
        if not os.path.exists(os.path.join(outdir, f)):
            return False
    try:
        import pandas as pd
        s = pd.read_csv(os.path.join(outdir, RUNNER_OUTPUTS[0]))
        want = set(range(cfg["seeds"]["start"], cfg["seeds"]["end"] + 1))
        return set(s[s.method == cfg["methods"]].seed) == want
    except Exception:
        return False


def ledger_append(outroot: str, row: dict) -> None:
    path = os.path.join(outroot, "budget_frontier_run_ledger.csv")
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp_utc", "tag", "status",
                                          "duration_s", "source_commit_sha", "outdir"])
        if not exists:
            w.writeheader()
        w.writerow(row)


def run_arm(cfg: dict, arm: dict, outroot: str, resume: bool, force: bool) -> str:
    outdir = os.path.join(outroot, arm["tag"])
    if os.path.isdir(outdir):
        if arm_complete(outdir, cfg):
            if resume:
                print(f"[skip] {arm['tag']} (complete)")
                return "skipped_complete"
            if not force:
                raise SystemExit(f"{arm['tag']}: output already COMPLETE at {outdir}; "
                                 f"re-running would overwrite it (use --force, or --resume "
                                 f"to skip completed arms)")
        else:
            if not force:
                raise SystemExit(f"{arm['tag']}: PARTIAL output at {outdir} (no completion "
                                 f"marker / seed mismatch); use --force to overwrite it")
        mpath = os.path.join(outdir, MARKER)
        if os.path.exists(mpath):
            os.remove(mpath)     # invalidate before overwrite so a crash leaves it partial
    os.makedirs(outdir, exist_ok=True)
    cmd = build_cmd(cfg, arm, outdir)
    src = git_source()
    t0 = datetime.datetime.now(datetime.timezone.utc)
    with open(os.path.join(outdir, "command.txt"), "w", encoding="utf-8") as f:
        f.write(" ".join(cmd) + "\n")
    with open(os.path.join(outdir, "environment.json"), "w", encoding="utf-8") as f:
        json.dump(environment_info(), f, indent=2)
    print(f"[run ] {arm['tag']}", flush=True)
    env = dict(os.environ, PYTHONPATH=ROOT)
    with open(os.path.join(outroot, arm["tag"] + ".log"), "w", encoding="utf-8") as log:
        r = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    t1 = datetime.datetime.now(datetime.timezone.utc)
    status = "done" if r.returncode == 0 else f"failed_rc{r.returncode}"
    if r.returncode == 0:
        with open(os.path.join(outdir, "run_config.json"), "w", encoding="utf-8") as f:
            json.dump(dict(tag=arm["tag"], config_version=cfg["config_version"],
                           config_file=os.path.relpath(CONFIG_PATH, ROOT),
                           runner_module=cfg["runner_module"], methods=cfg["methods"],
                           seeds=seeds_csv(cfg), data=arm["data"],
                           resolved_flags=arm["flags"], command=cmd,
                           started_utc=t0.isoformat(), finished_utc=t1.isoformat(),
                           **src), f, indent=2)
        # verify outputs + seed set BEFORE declaring completion
        with open(os.path.join(outdir, MARKER), "w", encoding="utf-8") as f:
            f.write(t1.isoformat() + "\n")
        if not arm_complete(outdir, cfg):
            os.remove(os.path.join(outdir, MARKER))
            status = "failed_incomplete_outputs"
    ledger_append(outroot, dict(timestamp_utc=t1.isoformat(), tag=arm["tag"], status=status,
                                duration_s=round((t1 - t0).total_seconds(), 1),
                                source_commit_sha=src["source_commit_sha"], outdir=outdir))
    print(f"[{status}] {arm['tag']} ({(t1 - t0).total_seconds():.0f}s)", flush=True)
    if status != "done":
        raise SystemExit(f"{arm['tag']} did not complete cleanly: {status}")
    return status


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--list-arms", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="print the exact commands, run nothing")
    p.add_argument("--run", action="store_true")
    p.add_argument("--only-arm", type=str, default=None, help="run/inspect a single tag")
    p.add_argument("--range", type=int, nargs=2, default=None, metavar=("I", "J"),
                   help="arm index range [I, J) in registered enumeration order")
    p.add_argument("--resume", action="store_true", help="skip arms whose output is COMPLETE")
    p.add_argument("--force", action="store_true", help="overwrite complete/partial outputs")
    p.add_argument("--outroot", type=str, default=os.path.join(ROOT, "results", "raw"))
    p.add_argument("--validate-complete", action="store_true",
                   help="verify every registered arm is present and complete; exit 1 otherwise")
    args = p.parse_args()

    cfg = load_config()
    arms = frontier_arms(cfg)
    sel = arms
    if args.only_arm is not None:
        sel = [a for a in arms if a["tag"] == args.only_arm]
        if not sel:
            raise SystemExit(f"unknown arm tag {args.only_arm}")
    elif args.range is not None:
        sel = arms[args.range[0]:args.range[1]]

    if args.list_arms:
        for i, a in enumerate(arms):
            print(i, a["tag"])
        return
    if args.validate_complete:
        missing = [a["tag"] for a in arms
                   if not arm_complete(os.path.join(args.outroot, a["tag"]), cfg)]
        if missing:
            print(f"INCOMPLETE: {len(missing)}/{len(arms)} arms missing or partial:")
            for t in missing:
                print(" ", t)
            raise SystemExit(1)
        print(f"COMPLETE: all {len(arms)} registered arms present and verified")
        return
    if args.dry_run:
        for a in sel:
            print(" ".join(build_cmd(cfg, a, os.path.join(args.outroot, a["tag"]))))
        return
    if args.run:
        for a in sel:
            run_arm(cfg, a, args.outroot, resume=args.resume, force=args.force)
        return
    p.print_help()


if __name__ == "__main__":
    main()
