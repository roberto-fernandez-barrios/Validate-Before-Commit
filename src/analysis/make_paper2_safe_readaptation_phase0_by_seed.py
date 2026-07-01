from __future__ import annotations

from pathlib import Path
import json
import re

import numpy as np
import pandas as pd


RAW_ROOT = Path("results/raw")
OUT_DIR = Path("results/tables/paper2_safe_readaptation_phase0_regret_001")

BY_SEED_FILE_NAME = "paper2_progressive_readaptation_by_seed.csv"

METHOD_LABELS = {
    "energy_distance": "Energy distance",
    "mmd_rbf": "MMD-RBF",
    "ks_max": "KS-max",
    "jsd": "JSD",
    "qk_mmd_zz": "QK-MMD ZZ",
    "qk_mmd_pauli_xz": "QK-MMD PauliXZ",
    "no_adaptation": "No adaptation",
}


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


def find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    norm = {str(c).strip().lower(): c for c in df.columns}
    for c in candidates:
        k = c.strip().lower()
        if k in norm:
            return norm[k]
    return None


def standardize_by_seed(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    seed_col = find_col(df, ["seed", "random_seed"])
    method_col = find_col(df, ["method", "strategy"])

    ba_col = find_col(df, [
        "mean_balanced_accuracy",
        "balanced_accuracy",
        "post_balanced_accuracy",
        "post_balanced_accuracy_mean",
    ])

    gain_col = find_col(df, [
        "cumulative_gain_vs_no_adapt",
        "cumulative_gain_vs_no_adapt_mean",
        "adaptation_gain_vs_no_adapt",
        "adaptation_gain_vs_no_adapt_mean",
    ])

    error_col = find_col(df, [
        "cumulative_error_area",
        "cumulative_error_area_mean",
        "degradation_area",
        "degradation_area_mean",
    ])

    adapt_col = find_col(df, [
        "n_adaptations",
        "n_adaptations_mean",
        "adaptations",
        "adaptations_mean",
    ])

    runtime_col = find_col(df, [
        "detector_runtime_sec_total",
        "detector_runtime_sec_total_mean",
        "detector_runtime",
        "detector_runtime_mean",
    ])

    if seed_col is None or method_col is None:
        raise ValueError(f"Missing seed/method columns in {path}: {list(df.columns)}")

    if ba_col is None:
        raise ValueError(f"Missing BA column in {path}: {list(df.columns)}")

    out = pd.DataFrame()
    out["source"] = pretty_source(path)
    out["tier"] = classify_tier(path)
    out["path"] = str(path)
    out["seed"] = df[seed_col]
    out["method"] = df[method_col].map(normalize_method)
    out["method_label"] = out["method"].map(METHOD_LABELS).fillna(out["method"])
    out["mean_balanced_accuracy"] = pd.to_numeric(df[ba_col], errors="coerce")

    if gain_col is not None:
        out["gain_vs_noadapt"] = pd.to_numeric(df[gain_col], errors="coerce")
    else:
        out["gain_vs_noadapt"] = np.nan

    if error_col is not None:
        out["error_area"] = pd.to_numeric(df[error_col], errors="coerce")
    else:
        out["error_area"] = np.nan

    if adapt_col is not None:
        out["n_adaptations"] = pd.to_numeric(df[adapt_col], errors="coerce")
    else:
        out["n_adaptations"] = np.nan

    if runtime_col is not None:
        out["detector_runtime"] = pd.to_numeric(df[runtime_col], errors="coerce")
    else:
        out["detector_runtime"] = np.nan

    return out.dropna(subset=["seed", "method", "mean_balanced_accuracy"])


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "mean_balanced_accuracy",
        "gain_vs_noadapt",
        "error_area",
        "n_adaptations",
        "detector_runtime",
    ]

    agg_spec = {}
    for m in metrics:
        agg_spec[f"{m}_mean"] = (m, "mean")
        agg_spec[f"{m}_std"] = (m, "std")

    out = (
        df.groupby(["source", "tier", "method", "method_label"])
        .agg(n_seeds=("seed", "nunique"), **agg_spec)
        .reset_index()
    )

    out["positive_gain"] = out["gain_vs_noadapt_mean"] > 0
    out["negative_gain"] = out["gain_vs_noadapt_mean"] < 0

    return out.sort_values(
        ["tier", "source", "mean_balanced_accuracy_mean"],
        ascending=[True, True, False],
    )


def gate_summary(method_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for (source, tier), g in method_df.groupby(["source", "tier"]):
        adaptive = g[g["method"] != "no_adaptation"].copy()
        noadapt = g[g["method"] == "no_adaptation"].copy()

        if adaptive.empty:
            continue

        best_actual = g.sort_values("mean_balanced_accuracy_mean", ascending=False).iloc[0]
        best_adaptive = adaptive.sort_values("mean_balanced_accuracy_mean", ascending=False).iloc[0]
        best_gain = adaptive.sort_values("gain_vs_noadapt_mean", ascending=False).iloc[0]
        worst_gain = adaptive.sort_values("gain_vs_noadapt_mean", ascending=True).iloc[0]

        qk = adaptive[adaptive["method"].str.startswith("qk_")]
        if not qk.empty:
            best_qk = qk.sort_values("mean_balanced_accuracy_mean", ascending=False).iloc[0]
        else:
            best_qk = None

        n_positive = int((adaptive["gain_vs_noadapt_mean"] > 0).sum())
        n_negative = int((adaptive["gain_vs_noadapt_mean"] < 0).sum())

        best_noadapt_ba = float(noadapt["mean_balanced_accuracy_mean"].iloc[0]) if not noadapt.empty else np.nan

        rows.append(
            {
                "source": source,
                "tier": tier,
                "noadapt_ba": best_noadapt_ba,
                "best_actual_method": best_actual["method_label"],
                "best_actual_ba": best_actual["mean_balanced_accuracy_mean"],
                "best_adaptive_method": best_adaptive["method_label"],
                "best_adaptive_ba": best_adaptive["mean_balanced_accuracy_mean"],
                "best_gain_method": best_gain["method_label"],
                "best_gain_vs_noadapt": best_gain["gain_vs_noadapt_mean"],
                "worst_gain_method": worst_gain["method_label"],
                "worst_gain_vs_noadapt": worst_gain["gain_vs_noadapt_mean"],
                "n_adaptive_methods_positive_gain": n_positive,
                "n_adaptive_methods_negative_gain": n_negative,
                "best_qk_method": best_qk["method_label"] if best_qk is not None else "",
                "best_qk_ba": best_qk["mean_balanced_accuracy_mean"] if best_qk is not None else np.nan,
                "best_qk_gain_vs_noadapt": best_qk["gain_vs_noadapt_mean"] if best_qk is not None else np.nan,
                "policy_problem_signal": bool(n_negative >= 2 or worst_gain["gain_vs_noadapt_mean"] < -0.5),
                "policy_opportunity_signal": bool(n_positive >= 2 or best_gain["gain_vs_noadapt_mean"] > 0.5),
                "mixed_policy_signal": bool((n_positive >= 1) and (n_negative >= 1)),
            }
        )

    return pd.DataFrame(rows).sort_values(["tier", "source"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_ROOT.rglob(BY_SEED_FILE_NAME))
    print("[BY-SEED FILES FOUND]", len(files))

    frames = []
    errors = []

    for path in files:
        print("[LOAD]", path)
        try:
            frames.append(standardize_by_seed(path))
        except Exception as exc:
            print("[SKIP]", path, exc)
            errors.append({"path": str(path), "error": repr(exc)})

    if not frames:
        raise SystemExit("No usable by_seed files loaded.")

    all_df = pd.concat(frames, ignore_index=True)
    method_df = aggregate(all_df)
    gate_df = gate_summary(method_df)

    all_path = OUT_DIR / "paper2_phase0_by_seed_standardized.csv"
    method_path = OUT_DIR / "paper2_phase0_by_seed_method_summary.csv"
    gate_path = OUT_DIR / "paper2_phase0_by_seed_gate_summary.csv"
    qk_path = OUT_DIR / "paper2_phase0_by_seed_qk_only.csv"
    manifest_path = OUT_DIR / "paper2_phase0_by_seed_manifest.json"

    all_df.to_csv(all_path, index=False)
    method_df.to_csv(method_path, index=False)
    gate_df.to_csv(gate_path, index=False)
    method_df[method_df["method"].str.startswith("qk_")].to_csv(qk_path, index=False)

    manifest = {
        "description": "Phase 0 safe-readaptation gate based on existing by_seed files.",
        "interpretation": "This is not a window-level oracle. It is a cheap decision gate using per-seed gain/loss versus no-adaptation.",
        "files_loaded": [str(p) for p in files],
        "load_errors": errors,
        "outputs": {
            "all_by_seed": str(all_path),
            "method_summary": str(method_path),
            "gate_summary": str(gate_path),
            "qk_only": str(qk_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print()
    print("[SAVED]")
    print(all_path)
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
        "noadapt_ba",
        "best_actual_method",
        "best_actual_ba",
        "best_adaptive_method",
        "best_adaptive_ba",
        "best_gain_method",
        "best_gain_vs_noadapt",
        "worst_gain_method",
        "worst_gain_vs_noadapt",
        "n_adaptive_methods_positive_gain",
        "n_adaptive_methods_negative_gain",
        "policy_problem_signal",
        "policy_opportunity_signal",
        "mixed_policy_signal",
    ]

    print(reliable[cols].to_string(index=False))


if __name__ == "__main__":
    main()
