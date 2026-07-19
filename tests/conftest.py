"""Shared fixtures for the final-paper invariant tests (final-kbs protocol, P10).

Two kinds of evidence:
  * direct unit/property tests against the v2 runner's building blocks (imported in-process);
  * two small end-to-end runs of the v2 runner on SYNTHETIC data (no benchmark download needed),
    whose per-seed counters and trigger logs encode the invariants the paper claims
    (zero collisions, no unvalidated commits, per-proposal alpha spending).

Synthetic data: two Gaussian classes, continuous features (rows unique with probability 1),
label column "Label" with BENIGN vs ATTACK -- the exact contract of load_binary_dataset.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]


def _write_synthetic(path: Path, shift: float, seed: int, n_per_class: int = 4000) -> None:
    rng = np.random.default_rng(seed)
    f = 5
    ben = rng.normal(0.0 + shift, 1.0, size=(n_per_class, f))
    att = rng.normal(1.5 + shift, 1.2, size=(n_per_class, f))
    df = pd.DataFrame(np.vstack([ben, att]), columns=[f"f{i}" for i in range(f)])
    df["Label"] = ["BENIGN"] * n_per_class + ["ATTACK"] * n_per_class
    df.to_csv(path, index=False)


@pytest.fixture(scope="session")
def synth(tmp_path_factory) -> dict[str, Path]:
    d = tmp_path_factory.mktemp("synth")
    ref, cur = d / "ref.csv", d / "cur.csv"
    _write_synthetic(ref, shift=0.0, seed=7)
    _write_synthetic(cur, shift=0.8, seed=8)
    return {"ref": ref, "cur": cur, "dir": d}


BASE_ARGS = [
    "--label-col", "Label", "--methods", "ks_max", "--dim", "4",
    "--window-size", "32", "--post-windows", "40", "--ramp-windows", "20",
    "--calibration-windows", "10", "--train-size-per-class", "200",
    "--adapt-size-per-class", "64", "--detector-ref-size-per-class", "64",
    "--downstream-model", "logreg", "--seeds", "1,2",
]


def _run_v2(synth: dict[str, Path], outdir: Path, extra: list[str]) -> Path:
    cmd = [sys.executable, "-m", "src.experiments.run_paper2_readaptation_v2",
           "--data-ref", str(synth["ref"]), "--data-cur", str(synth["cur"]),
           "--outdir", str(outdir)] + BASE_ARGS + extra
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=1200)
    assert r.returncode == 0, f"v2 runner failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    return outdir


@pytest.fixture(scope="session")
def causal_run(synth, tmp_path_factory) -> Path:
    """The final leakage-free causal configuration on synthetic data."""
    out = tmp_path_factory.mktemp("causal")
    return _run_v2(synth, out, [
        "--adaptation-gate", "labeled_probe", "--probe-size", "16",
        "--probe-source", "observed", "--adapt-strategy", "sliding_window",
        "--recal-source", "observed", "--stream-disjoint-windows",
        "--no-probe-policy", "reject", "--min-calib-windows", "10",
        "--trigger-mode", "random", "--trigger-prob", "0.35",
    ])


@pytest.fixture(scope="session")
def vbc_run(synth, tmp_path_factory) -> Path:
    """VBC-SG with the p-series deployment-long alpha budget, on synthetic data."""
    out = tmp_path_factory.mktemp("vbc")
    return _run_v2(synth, out, [
        "--adaptation-gate", "vbc_sg", "--probe-size", "32", "--seq-block", "8",
        "--defer-windows", "3", "--seqav-alpha", "0.10",
        "--lifetime-alpha", "0.10", "--alpha-spending", "pseries",
        "--trigger-mode", "random", "--trigger-prob", "0.35",
    ])


@pytest.fixture(scope="session")
def causal_by_seed(causal_run) -> pd.DataFrame:
    return pd.read_csv(causal_run / "paper2_progressive_readaptation_by_seed.csv")


@pytest.fixture(scope="session")
def vbc_trigger_log(vbc_run) -> pd.DataFrame:
    return pd.read_csv(vbc_run / "paper2_v2_trigger_log.csv")
