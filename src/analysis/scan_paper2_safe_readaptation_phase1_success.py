from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import json


IN_PATH = Path("results/tables/paper2_safe_readaptation_phase1_001/paper2_phase1_policy_vs_legacy.csv")
OUT_DIR = Path("results/tables/paper2_safe_readaptation_phase1_001")

SAFE_POLICIES = {
    "k2_of_3_cooldown0",
    "k3_of_5_cooldown0",
    "k2_of_3_cooldown3",
    "k3_of_5_cooldown5",
}


def as_num(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def main() -> None:
    if not IN_PATH.exists():
        raise SystemExit(f"Missing input: {IN_PATH}")

    df = pd.read_csv(IN_PATH)

    num_cols = [
        "mean_balanced_accuracy",
        "cumulative_gain_vs_no_adapt_mean",
        "n_adaptations_mean",
        "delta_ba_vs_legacy",
        "delta_gain_vs_legacy",
        "adaptation_reduction_vs_legacy",
        "gain_retention_vs_legacy",
        "harm_avoided_vs_legacy",
    ]
    df = as_num(df, num_cols)

    safe = df[df["policy_name"].isin(SAFE_POLICIES)].copy()

    # Criterion A: PortScan benefit preservation.
    # Need >=70% legacy gain retained and fewer adaptations.
    port = safe[safe["regime"] == "cicids_portscan"].copy()
    port["criterion_A_pass"] = (
        (port["gain_retention_vs_legacy"] >= 0.70)
        & (port["adaptation_reduction_vs_legacy"] > 0)
    )

    # Criterion B: ToN harm avoidance.
    # Need less harm than legacy and fewer adaptations.
    ton = safe[safe["regime"] == "ton_iot_scanning"].copy()
    ton["criterion_B_pass"] = (
        (ton["harm_avoided_vs_legacy"] > 0)
        & (ton["adaptation_reduction_vs_legacy"] > 0)
    )

    # Stronger B: tied with no-adaptation is not available here directly,
    # but harm_avoided > 0 tells whether it improved over legacy.
    # If no rows pass B, pivot is basically dead.

    # Criterion C: UNSW non-degradation.
    # Need BA delta >= -0.002.
    unsw = safe[safe["regime"] == "unsw_nb15_reconnaissance"].copy()
    unsw["criterion_C_pass"] = unsw["delta_ba_vs_legacy"] >= -0.002

    port_path = OUT_DIR / "paper2_phase1_criterion_A_portscan_candidates.csv"
    ton_path = OUT_DIR / "paper2_phase1_criterion_B_ton_candidates.csv"
    unsw_path = OUT_DIR / "paper2_phase1_criterion_C_unsw_candidates.csv"

    port.to_csv(port_path, index=False)
    ton.to_csv(ton_path, index=False)
    unsw.to_csv(unsw_path, index=False)

    summary = {
        "criterion_A_portscan_any_pass": bool(port["criterion_A_pass"].any()) if not port.empty else False,
        "criterion_B_ton_iot_any_pass": bool(ton["criterion_B_pass"].any()) if not ton.empty else False,
        "criterion_C_unsw_any_pass": bool(unsw["criterion_C_pass"].any()) if not unsw.empty else False,
        "n_A_pass": int(port["criterion_A_pass"].sum()) if not port.empty else 0,
        "n_B_pass": int(ton["criterion_B_pass"].sum()) if not ton.empty else 0,
        "n_C_pass": int(unsw["criterion_C_pass"].sum()) if not unsw.empty else 0,
        "phase1_passes": bool(
            (port["criterion_A_pass"].any() if not port.empty else False)
            and (ton["criterion_B_pass"].any() if not ton.empty else False)
            and (unsw["criterion_C_pass"].any() if not unsw.empty else False)
        ),
    }

    summary_path = OUT_DIR / "paper2_phase1_final_success_scan.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("[CRITERION A: PortScan candidates]")
    cols_A = [
        "regime",
        "policy_name",
        "method",
        "mean_balanced_accuracy",
        "cumulative_gain_vs_no_adapt_mean",
        "n_adaptations_mean",
        "gain_retention_vs_legacy",
        "adaptation_reduction_vs_legacy",
        "criterion_A_pass",
    ]
    print(port[cols_A].sort_values(["criterion_A_pass", "gain_retention_vs_legacy"], ascending=[False, False]).to_string(index=False))

    print()
    print("[CRITERION B: ToN-IoT candidates]")
    cols_B = [
        "regime",
        "policy_name",
        "method",
        "mean_balanced_accuracy",
        "cumulative_gain_vs_no_adapt_mean",
        "n_adaptations_mean",
        "harm_avoided_vs_legacy",
        "adaptation_reduction_vs_legacy",
        "criterion_B_pass",
    ]
    print(ton[cols_B].sort_values(["criterion_B_pass", "harm_avoided_vs_legacy"], ascending=[False, False]).to_string(index=False))

    print()
    print("[CRITERION C: UNSW candidates]")
    cols_C = [
        "regime",
        "policy_name",
        "method",
        "mean_balanced_accuracy",
        "cumulative_gain_vs_no_adapt_mean",
        "n_adaptations_mean",
        "delta_ba_vs_legacy",
        "adaptation_reduction_vs_legacy",
        "criterion_C_pass",
    ]
    print(unsw[cols_C].sort_values(["criterion_C_pass", "delta_ba_vs_legacy"], ascending=[False, False]).to_string(index=False))

    print()
    print("[FINAL SUMMARY]")
    print(json.dumps(summary, indent=2))
    print()
    print("[SAVED]")
    print(port_path)
    print(ton_path)
    print(unsw_path)
    print(summary_path)


if __name__ == "__main__":
    main()
