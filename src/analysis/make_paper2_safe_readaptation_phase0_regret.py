from __future__ import annotations

from pathlib import Path
import json
import re

import numpy as np
import pandas as pd


RAW_ROOT = Path("results/raw")
OUT_DIR = Path("results/tables/paper2_safe_readaptation_phase0_regret_001")

WINDOW_FILE_NAME = "paper2_progressive_readaptation_window_results.csv"

METHOD_LABELS = {
    "energy_distance": "Energy distance",
    "mmd_rbf": "MMD-RBF",
    "ks_max": "KS-max",
    "jsd": "JSD",
    "qk_mmd_zz": "QK-MMD ZZ",
    "qk_mmd_pauli_xz": "QK-MMD PauliXZ",
    "no_adaptation": "No adaptation",
}

BA_CANDIDATES = [
    "balanced_accuracy",
    "window_balanced_accuracy",
    "downstream_balanced_accuracy",
    "post_balanced_accuracy",
    "mean_balanced_accuracy",
    "ba",
]

SEED_CANDIDATES = ["seed", "random_seed"]
METHOD_CANDIDATES = ["method", "strategy"]
WINDOW_CANDIDATES = ["window", "window_idx", "window_id", "post_window", "t"]
SCENARIO_CANDIDATES = ["scenario", "regime", "attack", "dataset", "dataset_scenario"]

ADAPT_CANDIDATES = [
    "adapted",
    "did_adapt",
    "triggered",
    "trigger",
    "adaptation_triggered",
    "was_adapted",
    "readapted",
]


def normalize_name(s: str) -> str:
    return str(s).strip().lower()


def normalize_method(s: object) -> str:
    x = str(s).strip().lower()
    x = re.sub(r"[^0-9a-zA-Z]+", "_", x)
    x = re.sub(r"_+", "_", x).strip("_")

    aliases = {
        "no_adaptation": "no_adaptation",
        "noadaptation": "no_adaptation",
        "no_adapt": "no_adaptation",
        "none": "no_adaptation",

        "energy": "energy_distance",
        "energy_distance": "energy_distance",

        "mmd": "mmd_rbf",
        "mmd_rbf": "mmd_rbf",
        "rbf_mmd": "mmd_rbf",

        "ks": "ks_max",
        "ks_max": "ks_max",

        "jsd": "jsd",

        "qk_zz": "qk_mmd_zz",
        "qk_mmd_zz": "qk_mmd_zz",
        "qkmmd_zz": "qk_mmd_zz",

        "qk_pauli_xz": "qk_mmd_pauli_xz",
        "qk_mmd_pauli_xz": "qk_mmd_pauli_xz",
        "qkmmd_pauli_xz": "qk_mmd_pauli_xz",
        "qk_mmd_paulixz": "qk_mmd_pauli_xz",
        "qkmmd_paulixz": "qk_mmd_pauli_xz",
    }

    return aliases.get(x, x)


def find_exact_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    norm = {normalize_name(c): c for c in df.columns}
    for cand in candidates:
        key = normalize_name(cand)
        if key in norm:
            return norm[key]
    return None


def find_ba_col(df: pd.DataFrame) -> str:
    col = find_exact_col(df, BA_CANDIDATES)
    if col is not None:
        return col

    candidates = [
        c for c in df.columns
        if "balanced" in normalize_name(c) and "accuracy" in normalize_name(c)
    ]
    if len(candidates) == 1:
        return candidates[0]

    raise ValueError(
        "Could not identify balanced-accuracy column. "
        f"Columns found: {list(df.columns)}"
    )


def classify_tier(path: Path) -> str:
    s = str(path).lower()
    if "final" in s:
        return "final"
    if "medium" in s:
        return "medium"
    if "smoke" in s:
        return "smoke"
    return "other"


def pretty_source(path: Path) -> str:
    return path.parent.name


def standardize_frame(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    seed_col = find_exact_col(df, SEED_CANDIDATES)
    method_col = find_exact_col(df, METHOD_CANDIDATES)
    window_col = find_exact_col(df, WINDOW_CANDIDATES)
    scenario_col = find_exact_col(df, SCENARIO_CANDIDATES)
    ba_col = find_ba_col(df)
    adapt_col = find_exact_col(df, ADAPT_CANDIDATES)

    if seed_col is None:
        raise ValueError(f"No seed column found in {path}")

    if method_col is None:
        raise ValueError(f"No method column found in {path}")

    out = pd.DataFrame()
    out["source"] = pretty_source(path)
    out["tier"] = classify_tier(path)
    out["path"] = str(path)
    out["seed"] = df[seed_col]
    out["method"] = df[method_col].map(normalize_method)

    if scenario_col is not None:
        out["scenario"] = df[scenario_col].astype(str).str.strip()
    else:
        out["scenario"] = pretty_source(path)

    if window_col is not None:
        out["window"] = df[window_col]
    else:
        out["window"] = (
            df.groupby([seed_col, method_col], sort=False)
            .cumcount()
            .astype(int)
        )

    out["balanced_accuracy"] = pd.to_numeric(df[ba_col], errors="coerce")

    if adapt_col is not None:
        out["adapted"] = pd.to_numeric(df[adapt_col], errors="coerce").fillna(0).astype(float)
    else:
        out["adapted"] = np.nan

    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=["seed", "method", "window", "balanced_accuracy"])

    return out


def paired_oracle_regret(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    missing_noadapt = []

    group_cols = ["source", "tier", "scenario", "seed"]

    for keys, g in df.groupby(group_cols):
        source, tier, scenario, seed = keys

        noadapt = g[g["method"] == "no_adaptation"].copy()
        if noadapt.empty:
            missing_noadapt.append(
                {
                    "source": source,
                    "tier": tier,
                    "scenario": scenario,
                    "seed": seed,
                    "methods_present": ",".join(sorted(g["method"].unique())),
                }
            )
            continue

        noadapt = noadapt[["window", "balanced_accuracy"]].rename(
            columns={"balanced_accuracy": "ba_noadapt"}
        )

        for method, mg in g.groupby("method"):
            if method == "no_adaptation":
                continue

            cur = mg[["window", "balanced_accuracy", "adapted"]].rename(
                columns={"balanced_accuracy": "ba_method"}
            )

            merged = cur.merge(noadapt, on="window", how="inner")
            if merged.empty:
                continue

            diff = merged["ba_method"].to_numpy(dtype=float) - merged["ba_noadapt"].to_numpy(dtype=float)

            useful = np.clip(diff, 0.0, None)
            harmful = np.clip(-diff, 0.0, None)

            adapted = merged["adapted"].to_numpy(dtype=float)
            adapted_known = np.isfinite(adapted).any()

            rows.append(
                {
                    "source": source,
                    "tier": tier,
                    "scenario": scenario,
                    "seed": seed,
                    "method": method,
                    "method_label": METHOD_LABELS.get(method, method),
                    "n_windows": int(len(merged)),
                    "ba_method_mean": float(merged["ba_method"].mean()),
                    "ba_noadapt_mean": float(merged["ba_noadapt"].mean()),
                    "ba_oracle_switch_mean": float(np.maximum(merged["ba_method"], merged["ba_noadapt"]).mean()),
                    "actual_gain_vs_noadapt_area": float(diff.sum()),
                    "useful_adaptation_area": float(useful.sum()),
                    "avoidable_harm_area": float(harmful.sum()),
                    "oracle_gain_vs_noadapt_area": float(useful.sum()),
                    "regret_vs_oracle_area": float(harmful.sum()),
                    "harmful_window_rate": float((diff < 0).mean()),
                    "useful_window_rate": float((diff > 0).mean()),
                    "mean_window_diff_vs_noadapt": float(diff.mean()),
                    "adaptations_observed": float(np.nansum(adapted)) if adapted_known else np.nan,
                    "adaptation_rate_observed": float(np.nanmean(adapted)) if adapted_known else np.nan,
                }
            )

    return pd.DataFrame(rows), pd.DataFrame(missing_noadapt)


def aggregate_by_method(seed_df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "n_windows",
        "ba_method_mean",
        "ba_noadapt_mean",
        "ba_oracle_switch_mean",
        "actual_gain_vs_noadapt_area",
        "useful_adaptation_area",
        "avoidable_harm_area",
        "oracle_gain_vs_noadapt_area",
        "regret_vs_oracle_area",
        "harmful_window_rate",
        "useful_window_rate",
        "mean_window_diff_vs_noadapt",
        "adaptations_observed",
        "adaptation_rate_observed",
    ]

    agg_spec = {}
    for m in metrics:
        agg_spec[f"{m}_mean"] = (m, "mean")
        agg_spec[f"{m}_std"] = (m, "std")

    out = (
        seed_df.groupby(["source", "tier", "scenario", "method", "method_label"])
        .agg(n_seeds=("seed", "nunique"), **agg_spec)
        .reset_index()
    )

    out = out.sort_values(
        ["tier", "source", "scenario", "ba_method_mean_mean"],
        ascending=[True, True, True, False],
    )

    return out


def scenario_gate_summary(method_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for keys, g in method_df.groupby(["source", "tier", "scenario"]):
        source, tier, scenario = keys

        best_actual = g.sort_values("ba_method_mean_mean", ascending=False).iloc[0]
        best_oracle = g.sort_values("ba_oracle_switch_mean_mean", ascending=False).iloc[0]
        max_harm = g.sort_values("avoidable_harm_area_mean", ascending=False).iloc[0]
        max_useful = g.sort_values("useful_adaptation_area_mean", ascending=False).iloc[0]

        best_qk = g[g["method"].str.startswith("qk_")]
        if not best_qk.empty:
            best_qk_row = best_qk.sort_values("ba_method_mean_mean", ascending=False).iloc[0]
            best_qk_method = best_qk_row["method_label"]
            best_qk_ba = best_qk_row["ba_method_mean_mean"]
            best_qk_gain = best_qk_row["actual_gain_vs_noadapt_area_mean"]
            best_qk_harm = best_qk_row["avoidable_harm_area_mean"]
        else:
            best_qk_method = ""
            best_qk_ba = np.nan
            best_qk_gain = np.nan
            best_qk_harm = np.nan

        rows.append(
            {
                "source": source,
                "tier": tier,
                "scenario": scenario,
                "best_actual_method": best_actual["method_label"],
                "best_actual_ba": best_actual["ba_method_mean_mean"],
                "best_actual_gain_vs_noadapt_area": best_actual["actual_gain_vs_noadapt_area_mean"],
                "best_oracle_switch_method": best_oracle["method_label"],
                "best_oracle_switch_ba": best_oracle["ba_oracle_switch_mean_mean"],
                "best_oracle_gain_vs_noadapt_area": best_oracle["oracle_gain_vs_noadapt_area_mean"],
                "max_avoidable_harm_method": max_harm["method_label"],
                "max_avoidable_harm_area": max_harm["avoidable_harm_area_mean"],
                "max_harmful_window_rate": max_harm["harmful_window_rate_mean"],
                "max_useful_method": max_useful["method_label"],
                "max_useful_adaptation_area": max_useful["useful_adaptation_area_mean"],
                "best_qk_method": best_qk_method,
                "best_qk_ba": best_qk_ba,
                "best_qk_gain_vs_noadapt_area": best_qk_gain,
                "best_qk_avoidable_harm_area": best_qk_harm,
                "policy_problem_signal": bool(
                    (max_harm["avoidable_harm_area_mean"] > 0.5)
                    or (max_harm["harmful_window_rate_mean"] > 0.20)
                ),
                "policy_opportunity_signal": bool(
                    (best_oracle["oracle_gain_vs_noadapt_area_mean"] > 0.5)
                    or (max_useful["useful_adaptation_area_mean"] > 0.5)
                ),
            }
        )

    return pd.DataFrame(rows).sort_values(["tier", "source", "scenario"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_ROOT.rglob(WINDOW_FILE_NAME))
    print("[WINDOW FILES FOUND]", len(files))

    if not files:
        raise SystemExit(f"No {WINDOW_FILE_NAME} files found under {RAW_ROOT}")

    frames = []
    errors = []

    for path in files:
        print("[LOAD]", path)
        try:
            frames.append(standardize_frame(path))
        except Exception as exc:
            errors.append({"path": str(path), "error": repr(exc)})
            print("[SKIP]", path, exc)

    if not frames:
        raise SystemExit("No usable window-results files were loaded.")

    all_df = pd.concat(frames, ignore_index=True)

    methods_path = OUT_DIR / "paper2_phase0_method_values_seen.csv"
    (
        all_df.groupby(["source", "tier", "scenario"])["method"]
        .apply(lambda s: ",".join(sorted(s.unique())))
        .reset_index()
        .to_csv(methods_path, index=False)
    )

    seed_df, missing_noadapt_df = paired_oracle_regret(all_df)

    missing_path = OUT_DIR / "paper2_phase0_missing_noadapt_groups.csv"
    missing_noadapt_df.to_csv(missing_path, index=False)

    if seed_df.empty:
        all_path = OUT_DIR / "paper2_phase0_all_standardized_windows.csv"
        all_df.to_csv(all_path, index=False)

        manifest = {
            "description": "Phase 0 failed because no paired no_adaptation groups were found.",
            "files_loaded": [str(p) for p in files],
            "load_errors": errors,
            "debug_outputs": {
                "standardized_windows": str(all_path),
                "method_values_seen": str(methods_path),
                "missing_noadapt_groups": str(missing_path),
            },
        }
        manifest_path = OUT_DIR / "paper2_phase0_regret_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        print("[ERROR] No paired no_adaptation groups found.")
        print("Saved debug files:")
        print(all_path)
        print(methods_path)
        print(missing_path)
        print(manifest_path)
        raise SystemExit(1)

    method_df = aggregate_by_method(seed_df)
    gate_df = scenario_gate_summary(method_df)

    all_path = OUT_DIR / "paper2_phase0_all_standardized_windows.csv"
    seed_path = OUT_DIR / "paper2_phase0_oracle_regret_by_seed.csv"
    method_path = OUT_DIR / "paper2_phase0_oracle_regret_by_method.csv"
    gate_path = OUT_DIR / "paper2_phase0_regret_gate_summary.csv"
    qk_path = OUT_DIR / "paper2_phase0_qk_only_regret.csv"
    manifest_path = OUT_DIR / "paper2_phase0_regret_manifest.json"

    all_df.to_csv(all_path, index=False)
    seed_df.to_csv(seed_path, index=False)
    method_df.to_csv(method_path, index=False)
    gate_df.to_csv(gate_path, index=False)
    method_df[method_df["method"].str.startswith("qk_")].to_csv(qk_path, index=False)

    manifest = {
        "description": "Phase 0 safe-readaptation oracle-regret diagnostic using existing window results only.",
        "definition": {
            "oracle_switch": "For each detector/method and each seed/window, choose max(detector-triggered BA, no-adaptation BA).",
            "regret_vs_oracle_area": "Sum over windows of max(no-adaptation BA - method BA, 0). This is avoidable harm if a safe policy had refused harmful updates.",
            "oracle_gain_vs_noadapt_area": "Sum over windows of max(method BA - no-adaptation BA, 0). This is the maximum recoverable gain from using that detector only when beneficial.",
        },
        "files_loaded": [str(p) for p in files],
        "load_errors": errors,
        "outputs": {
            "standardized_windows": str(all_path),
            "by_seed": str(seed_path),
            "by_method": str(method_path),
            "gate_summary": str(gate_path),
            "qk_only": str(qk_path),
            "method_values_seen": str(methods_path),
            "missing_noadapt_groups": str(missing_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print()
    print("[SAVED]")
    print(seed_path)
    print(method_path)
    print(gate_path)
    print(qk_path)
    print(manifest_path)

    print()
    print("[GATE SUMMARY: medium/final only]")
    reliable = gate_df[gate_df["tier"].isin(["medium", "final"])]
    if reliable.empty:
        reliable = gate_df

    cols = [
        "source",
        "tier",
        "scenario",
        "best_actual_method",
        "best_actual_ba",
        "best_actual_gain_vs_noadapt_area",
        "best_oracle_switch_method",
        "best_oracle_gain_vs_noadapt_area",
        "max_avoidable_harm_method",
        "max_avoidable_harm_area",
        "max_harmful_window_rate",
        "policy_problem_signal",
        "policy_opportunity_signal",
    ]
    print(reliable[cols].to_string(index=False))


if __name__ == "__main__":
    main()
