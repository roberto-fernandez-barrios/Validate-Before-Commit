from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DATASETS = {
    "wednesday": {
        "data_ref": "data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv",
        "data_cur": "data/raw/cicids2017/MachineLearningCVE/Wednesday-workingHours.pcap_ISCX.csv",
        "scenario_name": "tuesday_to_wednesday",
    },
    "portscan": {
        "data_ref": "data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv",
        "data_cur": "data/raw/cicids2017/MachineLearningCVE/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
        "scenario_name": "tuesday_to_friday_portscan",
    },
    "ddos": {
        "data_ref": "data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv",
        "data_cur": "data/raw/cicids2017/MachineLearningCVE/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
        "scenario_name": "tuesday_to_friday_ddos",
    },
}


CONFIGS = {
    "zz_r1": {
        "method": "qk_mmd_zz",
        "q_reps": 1,
        "feature_map_family": "ZZ",
    },
    "zz_r2": {
        "method": "qk_mmd_zz",
        "q_reps": 2,
        "feature_map_family": "ZZ",
    },
    "zz_r3": {
        "method": "qk_mmd_zz",
        "q_reps": 3,
        "feature_map_family": "ZZ",
    },
    "paulixz_r1": {
        "method": "qk_mmd_pauli_xz",
        "q_reps": 1,
        "feature_map_family": "PauliXZ",
    },
    "paulixz_r2": {
        "method": "qk_mmd_pauli_xz",
        "q_reps": 2,
        "feature_map_family": "PauliXZ",
    },
    "paulixz_r3": {
        "method": "qk_mmd_pauli_xz",
        "q_reps": 3,
        "feature_map_family": "PauliXZ",
    },
}


MODES = {
    "smoke": {
        "seeds": "1,2,3",
        "post_windows": "20",
        "ramp_windows": "20",
        "calibration_windows": "10",
        "n_permutations": "50",
    },
    "medium": {
        "seeds": ",".join(str(i) for i in range(1, 11)),
        "post_windows": "100",
        "ramp_windows": "100",
        "calibration_windows": "30",
        "n_permutations": "100",
    },
    "final": {
        "seeds": ",".join(str(i) for i in range(1, 31)),
        "post_windows": "100",
        "ramp_windows": "100",
        "calibration_windows": "30",
        "n_permutations": "100",
    },
}


def parse_csv(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def run_one(args, scenario_key: str, config_key: str) -> None:
    scenario = DATASETS[scenario_key]
    config = CONFIGS[config_key]
    mode = MODES[args.mode]

    outdir = (
        Path(args.out_root)
        / f"paper2_feature_map_sensitivity_{args.mode}_001"
        / scenario_key
        / config_key
    )

    outdir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "src.experiments.run_paper2_progressive_readaptation",
        "--data-ref",
        scenario["data_ref"],
        "--data-cur",
        scenario["data_cur"],
        "--label-col",
        args.label_col,
        "--outdir",
        str(outdir),
        "--seeds",
        mode["seeds"],
        "--methods",
        config["method"],
        "--post-windows",
        mode["post_windows"],
        "--ramp-windows",
        mode["ramp_windows"],
        "--calibration-windows",
        mode["calibration_windows"],
        "--n-permutations",
        mode["n_permutations"],
        "--q-reps",
        str(config["q_reps"]),
        "--q-input-scaling",
        args.q_input_scaling,
        "--ks-reduction",
        args.ks_reduction,
        "--jsd-bins",
        str(args.jsd_bins),
        "--energy-reduction",
        args.energy_reduction,
    ]

    print("=" * 100)
    print(f"[SCENARIO={scenario_key}][CONFIG={config_key}][MODE={args.mode}]")
    print(f"[OUTDIR] {outdir}")
    print("[CMD]")
    print(" ".join(cmd))
    print("=" * 100)

    if args.dry_run:
        return

    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--scenario", type=str, default="wednesday", choices=sorted(DATASETS))
    parser.add_argument("--configs", type=str, default="zz_r1,zz_r2,zz_r3,paulixz_r1,paulixz_r2,paulixz_r3")
    parser.add_argument("--mode", type=str, default="smoke", choices=sorted(MODES))
    parser.add_argument("--out-root", type=str, default="results/raw")
    parser.add_argument("--label-col", type=str, default="Label")

    parser.add_argument("--q-input-scaling", type=str, default="atan_standard", choices=["none", "atan_standard"])

    parser.add_argument("--ks-reduction", type=str, default="max", choices=["max", "mean"])
    parser.add_argument("--jsd-bins", type=int, default=20)
    parser.add_argument("--energy-reduction", type=str, default="mean", choices=["mean", "max"])

    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    configs = parse_csv(args.configs)

    unknown = sorted(set(configs) - set(CONFIGS))
    if unknown:
        raise ValueError(f"Unknown configs: {unknown}. Known configs: {sorted(CONFIGS)}")

    for config_key in configs:
        run_one(args, args.scenario, config_key)


if __name__ == "__main__":
    main()
