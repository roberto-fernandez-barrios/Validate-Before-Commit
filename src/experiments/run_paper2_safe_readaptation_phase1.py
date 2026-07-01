from __future__ import annotations

from pathlib import Path
import argparse
import json
import subprocess
import sys


OUT_ROOT = Path("results/raw/paper2_safe_readaptation_phase1_001")


POLICIES = [
    {
        "name": "legacy_consecutive3_cooldown10",
        "adaptation_policy": "consecutive",
        "policy_k": 3,
        "policy_n": 3,
        "cooldown": 10,
    },
    {
        "name": "k2_of_3_cooldown0",
        "adaptation_policy": "k_of_n",
        "policy_k": 2,
        "policy_n": 3,
        "cooldown": 0,
    },
    {
        "name": "k3_of_5_cooldown0",
        "adaptation_policy": "k_of_n",
        "policy_k": 3,
        "policy_n": 5,
        "cooldown": 0,
    },
    {
        "name": "k2_of_3_cooldown3",
        "adaptation_policy": "k_of_n",
        "policy_k": 2,
        "policy_n": 3,
        "cooldown": 3,
    },
    {
        "name": "k3_of_5_cooldown5",
        "adaptation_policy": "k_of_n",
        "policy_k": 3,
        "policy_n": 5,
        "cooldown": 5,
    },
]


def first_existing(patterns: list[str]) -> Path:
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(Path(".").glob(pattern))

    matches = [p for p in matches if p.exists() and p.is_file()]
    if not matches:
        raise FileNotFoundError(f"No file found for patterns: {patterns}")

    matches = sorted(set(matches), key=lambda p: str(p).lower())
    return matches[0]


def build_regimes() -> list[dict[str, object]]:
    cicids_ref = first_existing([
        "data/raw/cicids2017/**/Tuesday-WorkingHours*.csv",
        "data/raw/cicids2017/**/Tuesday*.csv",
    ])
    cicids_portscan = first_existing([
        "data/raw/cicids2017/**/*PortScan*.csv",
    ])

    unsw_ref_recon = first_existing([
        "data/processed/unsw_nb15/*ref*recon*binary.csv",
        "data/processed/unsw_nb15/*ref*reconnaissance*binary.csv",
    ])
    unsw_cur_recon = first_existing([
        "data/processed/unsw_nb15/*cur*recon*binary.csv",
        "data/processed/unsw_nb15/*cur*reconnaissance*binary.csv",
    ])

    ton_ref_scan = Path("data/processed/ton_iot_q1_gate/ton_iot_ref_no_scanning_binary.csv")
    ton_cur_scan = Path("data/processed/ton_iot_q1_gate/ton_iot_cur_scanning_binary.csv")

    if not ton_ref_scan.exists() or not ton_cur_scan.exists():
        raise FileNotFoundError("ToN-IoT scanning processed files not found.")

    return [
        {
            "name": "cicids_portscan",
            "data_ref": cicids_ref,
            "data_cur": cicids_portscan,
            "label_col": "Label",
        },
        {
            "name": "unsw_nb15_reconnaissance",
            "data_ref": unsw_ref_recon,
            "data_cur": unsw_cur_recon,
            "label_col": "Label",
        },
        {
            "name": "ton_iot_scanning",
            "data_ref": ton_ref_scan,
            "data_cur": ton_cur_scan,
            "label_col": "Label",
        },
    ]


def command_for(regime: dict[str, object], policy: dict[str, object]) -> list[str]:
    outdir = OUT_ROOT / str(regime["name"]) / str(policy["name"])

    return [
        sys.executable,
        "-m",
        "src.experiments.run_paper2_progressive_readaptation",
        "--data-ref",
        str(regime["data_ref"]),
        "--data-cur",
        str(regime["data_cur"]),
        "--label-col",
        str(regime["label_col"]),
        "--outdir",
        str(outdir),
        "--seeds",
        "1,2,3,4,5,6,7,8,9,10",
        "--methods",
        "qk_mmd_zz,ks_max",
        "--post-windows",
        "100",
        "--ramp-windows",
        "100",
        "--calibration-windows",
        "30",
        "--n-permutations",
        "100",
        "--q-reps",
        "1",
        "--q-input-scaling",
        "atan_standard",
        "--ks-reduction",
        "max",
        "--adaptation-policy",
        str(policy["adaptation_policy"]),
        "--policy-k",
        str(policy["policy_k"]),
        "--policy-n",
        str(policy["policy_n"]),
        "--policy-name",
        str(policy["name"]),
        "--cooldown-windows",
        str(policy["cooldown"]),
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    regimes = build_regimes()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    manifest = {
        "description": "Paper 2 safe-readaptation Phase 1 closed runner.",
        "regimes": [
            {
                "name": r["name"],
                "data_ref": str(r["data_ref"]),
                "data_cur": str(r["data_cur"]),
                "label_col": r["label_col"],
            }
            for r in regimes
        ],
        "policies": POLICIES,
        "detectors": ["qk_mmd_zz", "ks_max"],
        "seeds": "1,2,3,4,5,6,7,8,9,10",
        "post_windows": 100,
        "ramp_windows": 100,
        "calibration_windows": 30,
        "n_permutations": 100,
    }

    manifest_path = OUT_ROOT / "phase1_runner_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("[MANIFEST]", manifest_path)
    print("[MODE]", "EXECUTE" if args.execute else "DRY RUN")

    for regime in regimes:
        print()
        print("=" * 100)
        print("[REGIME]", regime["name"])
        print("[REF]", regime["data_ref"])
        print("[CUR]", regime["data_cur"])

        for policy in POLICIES:
            cmd = command_for(regime, policy)
            print("-" * 100)
            print("[POLICY]", policy["name"])
            print(" ".join(cmd))

            if args.execute:
                subprocess.run(cmd, check=True)

    print()
    print("[DONE]")


if __name__ == "__main__":
    main()
