from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd


RAW_ROOT = Path("results/raw/paper2_safe_readaptation_phase1_001")
OUT_DIR = Path("results/tables/paper2_safe_readaptation_phase1_001")

SUMMARY_NAME = "paper2_progressive_readaptation_summary.csv"

REGIME_LABELS = {
    "cicids_portscan": "CICIDS2017 PortScan",
    "unsw_nb15_reconnaissance": "UNSW-NB15 Reconnaissance",
    "ton_iot_scanning": "ToN-IoT Scanning",
}

POLICY_ORDER = [
    "legacy_consecutive3_cooldown10",
    "k2_of_3_cooldown0",
    "k3_of_5_cooldown0",
    "k2_of_3_cooldown3",
    "k3_of_5_cooldown5",
]

SAFE_POLICIES = [
    "k2_of_3_cooldown0",
    "k3_of_5_cooldown0",
    "k2_of_3_cooldown3",
    "k3_of_5_cooldown5",
]

METHOD_ORDER = [
    "no_adaptation",
    "ks_max",
    "qk_mmd_zz",
]


def load_all() -> pd.DataFrame:
    files = sorted(RAW_ROOT.rglob(SUMMARY_NAME))
    print("[SUMMARY FILES FOUND]", len(files))

    if not files:
        raise SystemExit(f"No {SUMMARY_NAME} files found under {RAW_ROOT}")

    frames = []

    for path in files:
        parts = path.parts
        # Expected:
        # results/raw/paper2_safe_readaptation_phase1_001/<regime>/<policy>/summary.csv
        regime = path.parent.parent.name
        policy_dir = path.parent.name

        df = pd.read_csv(path)
        df["regime"] = regime
        df["regime_label"] = REGIME_LABELS.get(regime, regime)
        df["policy_dir"] = policy_dir
        df["summary_path"] = str(path)

        frames.append(df)

    out = pd.concat(frames, ignore_index=True)

    numeric_cols = [
        "n_seeds",
        "policy_k",
        "policy_n",
        "cooldown_windows",
        "mean_balanced_accuracy",
        "std_balanced_accuracy",
        "cumulative_error_area_mean",
        "cumulative_error_area_std",
        "mean_gain_vs_no_adapt",
        "cumulative_gain_vs_no_adapt_mean",
        "n_adaptations_mean",
        "false_adaptations_mean",
        "first_adaptation_window_mean",
        "alarm_rate_mean",
        "trigger_rate_mean",
        "detector_runtime_sec_total_mean",
        "fit_runtime_sec_total_mean",
    ]

    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # Defensive fill: if older rows lack policy metadata, use directory.
    out["policy_name"] = out.get("policy_name", out["policy_dir"]).fillna(out["policy_dir"])

    return out


def add_policy_rank(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    policy_rank = {p: i for i, p in enumerate(POLICY_ORDER)}
    method_rank = {m: i for i, m in enumerate(METHOD_ORDER)}

    df["policy_rank"] = df["policy_name"].map(policy_rank).fillna(999).astype(int)
    df["method_rank"] = df["method"].map(method_rank).fillna(999).astype(int)

    return df.sort_values(["regime", "policy_rank", "method_rank"])


def build_vs_legacy(df: pd.DataFrame) -> pd.DataFrame:
    adaptive = df[df["method"] != "no_adaptation"].copy()

    legacy = adaptive[adaptive["policy_name"] == "legacy_consecutive3_cooldown10"].copy()
    legacy = legacy[
        [
            "regime",
            "method",
            "mean_balanced_accuracy",
            "cumulative_gain_vs_no_adapt_mean",
            "n_adaptations_mean",
            "cumulative_error_area_mean",
            "trigger_rate_mean",
        ]
    ].rename(
        columns={
            "mean_balanced_accuracy": "legacy_ba",
            "cumulative_gain_vs_no_adapt_mean": "legacy_gain",
            "n_adaptations_mean": "legacy_adaptations",
            "cumulative_error_area_mean": "legacy_error_area",
            "trigger_rate_mean": "legacy_trigger_rate",
        }
    )

    out = adaptive.merge(legacy, on=["regime", "method"], how="left")

    out["delta_ba_vs_legacy"] = out["mean_balanced_accuracy"] - out["legacy_ba"]
    out["delta_gain_vs_legacy"] = out["cumulative_gain_vs_no_adapt_mean"] - out["legacy_gain"]
    out["adaptation_reduction_vs_legacy"] = out["legacy_adaptations"] - out["n_adaptations_mean"]
    out["trigger_reduction_vs_legacy"] = out["legacy_trigger_rate"] - out["trigger_rate_mean"]

    out["gain_retention_vs_legacy"] = np.where(
        out["legacy_gain"] > 0,
        out["cumulative_gain_vs_no_adapt_mean"] / out["legacy_gain"],
        np.nan,
    )

    # In harm regimes, gain is negative. Higher gain means less harm.
    out["harm_avoided_vs_legacy"] = np.where(
        out["legacy_gain"] < 0,
        out["cumulative_gain_vs_no_adapt_mean"] - out["legacy_gain"],
        np.nan,
    )

    return add_policy_rank(out)


def best_safe_by_regime_method(vs_legacy: pd.DataFrame) -> pd.DataFrame:
    safe = vs_legacy[vs_legacy["policy_name"].isin(SAFE_POLICIES)].copy()

    rows = []

    for (regime, method), g in safe.groupby(["regime", "method"]):
        # Primary selection: highest BA. Tie-breaker: fewer adaptations.
        best = g.sort_values(
            ["mean_balanced_accuracy", "n_adaptations_mean"],
            ascending=[False, True],
        ).iloc[0]

        rows.append(best)

    return add_policy_rank(pd.DataFrame(rows))


def gate_summary(df: pd.DataFrame, vs_legacy: pd.DataFrame, best_safe: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for regime in sorted(df["regime"].unique()):
        g = df[df["regime"] == regime].copy()
        safe_regime = best_safe[best_safe["regime"] == regime].copy()

        noadapt_ba = (
            g[g["method"] == "no_adaptation"]
            .sort_values("policy_rank")
            ["mean_balanced_accuracy"]
            .iloc[0]
        )

        best_overall = g.sort_values(
            ["mean_balanced_accuracy", "n_adaptations_mean"],
            ascending=[False, True],
        ).iloc[0]

        best_safe_row = safe_regime.sort_values(
            ["mean_balanced_accuracy", "n_adaptations_mean"],
            ascending=[False, True],
        ).iloc[0]

        rows.append(
            {
                "regime": regime,
                "regime_label": REGIME_LABELS.get(regime, regime),
                "noadapt_ba": noadapt_ba,
                "best_overall_policy": best_overall["policy_name"],
                "best_overall_method": best_overall["method"],
                "best_overall_ba": best_overall["mean_balanced_accuracy"],
                "best_overall_gain": best_overall["cumulative_gain_vs_no_adapt_mean"],
                "best_overall_adaptations": best_overall["n_adaptations_mean"],
                "best_safe_policy": best_safe_row["policy_name"],
                "best_safe_method": best_safe_row["method"],
                "best_safe_ba": best_safe_row["mean_balanced_accuracy"],
                "best_safe_gain": best_safe_row["cumulative_gain_vs_no_adapt_mean"],
                "best_safe_adaptations": best_safe_row["n_adaptations_mean"],
                "best_safe_delta_ba_vs_legacy": best_safe_row["delta_ba_vs_legacy"],
                "best_safe_delta_gain_vs_legacy": best_safe_row["delta_gain_vs_legacy"],
                "best_safe_adaptation_reduction_vs_legacy": best_safe_row["adaptation_reduction_vs_legacy"],
                "best_safe_gain_retention_vs_legacy": best_safe_row["gain_retention_vs_legacy"],
                "best_safe_harm_avoided_vs_legacy": best_safe_row["harm_avoided_vs_legacy"],
            }
        )

    gate = pd.DataFrame(rows)

    # Protocol-specific checks
    port = gate[gate["regime"] == "cicids_portscan"]
    ton = gate[gate["regime"] == "ton_iot_scanning"]
    unsw = gate[gate["regime"] == "unsw_nb15_reconnaissance"]

    checks = []

    if not port.empty:
        r = port.iloc[0]
        checks.append(
            {
                "criterion": "A_benefit_preservation_portscan",
                "passed": bool(
                    pd.notna(r["best_safe_gain_retention_vs_legacy"])
                    and r["best_safe_gain_retention_vs_legacy"] >= 0.70
                    and r["best_safe_adaptation_reduction_vs_legacy"] > 0
                ),
                "value_1": r["best_safe_gain_retention_vs_legacy"],
                "value_2": r["best_safe_adaptation_reduction_vs_legacy"],
                "interpretation": "Need >=70% legacy gain retained and fewer adaptations.",
            }
        )

    if not ton.empty:
        r = ton.iloc[0]
        checks.append(
            {
                "criterion": "B_harm_avoidance_ton_iot",
                "passed": bool(
                    pd.notna(r["best_safe_harm_avoided_vs_legacy"])
                    and r["best_safe_harm_avoided_vs_legacy"] > 0
                    and r["best_safe_adaptation_reduction_vs_legacy"] > 0
                ),
                "value_1": r["best_safe_harm_avoided_vs_legacy"],
                "value_2": r["best_safe_adaptation_reduction_vs_legacy"],
                "interpretation": "Need less harm than legacy and fewer adaptations.",
            }
        )

    if not unsw.empty:
        r = unsw.iloc[0]
        checks.append(
            {
                "criterion": "C_mixed_regime_non_degradation_unsw_recon",
                "passed": bool(r["best_safe_delta_ba_vs_legacy"] >= -0.002),
                "value_1": r["best_safe_delta_ba_vs_legacy"],
                "value_2": r["best_safe_adaptation_reduction_vs_legacy"],
                "interpretation": "Need not materially underperform legacy. Threshold: BA delta >= -0.002.",
            }
        )

    checks_df = pd.DataFrame(checks)

    return gate, checks_df


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_all()
    df = add_policy_rank(df)

    vs_legacy = build_vs_legacy(df)
    best_safe = best_safe_by_regime_method(vs_legacy)
    gate, checks = gate_summary(df, vs_legacy, best_safe)

    method_path = OUT_DIR / "paper2_phase1_all_policy_method_summary.csv"
    vs_legacy_path = OUT_DIR / "paper2_phase1_policy_vs_legacy.csv"
    best_safe_path = OUT_DIR / "paper2_phase1_best_safe_by_regime_method.csv"
    gate_path = OUT_DIR / "paper2_phase1_gate_summary.csv"
    checks_path = OUT_DIR / "paper2_phase1_success_checks.csv"
    manifest_path = OUT_DIR / "paper2_phase1_aggregate_manifest.json"

    df.to_csv(method_path, index=False)
    vs_legacy.to_csv(vs_legacy_path, index=False)
    best_safe.to_csv(best_safe_path, index=False)
    gate.to_csv(gate_path, index=False)
    checks.to_csv(checks_path, index=False)

    manifest = {
        "description": "Aggregate tables for Paper 2 safe-readaptation Phase 1.",
        "raw_root": str(RAW_ROOT),
        "outputs": {
            "all_policy_method_summary": str(method_path),
            "policy_vs_legacy": str(vs_legacy_path),
            "best_safe_by_regime_method": str(best_safe_path),
            "gate_summary": str(gate_path),
            "success_checks": str(checks_path),
        },
    }

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print()
    print("[SAVED]")
    print(method_path)
    print(vs_legacy_path)
    print(best_safe_path)
    print(gate_path)
    print(checks_path)
    print(manifest_path)

    print()
    print("[GATE SUMMARY]")
    print(gate.to_string(index=False))

    print()
    print("[SUCCESS CHECKS]")
    print(checks.to_string(index=False))


if __name__ == "__main__":
    main()
