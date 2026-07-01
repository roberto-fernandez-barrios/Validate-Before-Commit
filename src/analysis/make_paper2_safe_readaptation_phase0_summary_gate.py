from __future__ import annotations

from pathlib import Path
import json
import re

import numpy as np
import pandas as pd


RAW_ROOT = Path("results/raw")
OUT_DIR = Path("results/tables/paper2_safe_readaptation_phase0_summary_gate_001")

SUMMARY_FILE_NAME = "paper2_progressive_readaptation_summary.csv"

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


def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(
        s.astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    )


def standardize_summary(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    method_col = find_col(df, ["method", "strategy"])
    n_seeds_col = find_col(df, ["n_seeds"])
    ba_col = find_col(df, [
        "mean_balanced_accuracy",
        "post_balanced_accuracy_mean",
        "balanced_accuracy_mean",
        "balanced_accuracy",
    ])
    gain_col = find_col(df, [
        "cumulative_gain_vs_no_adapt_mean",
        "cumulative_gain_vs_no_adapt",
        "adaptation_gain_vs_no_adapt_mean",
        "adaptation_gain_vs_no_adapt",
    ])
    error_col = find_col(df, [
        "cumulative_error_area_mean",
        "cumulative_error_area",
        "degradation_area_mean",
        "degradation_area",
    ])
    adapt_col = find_col(df, [
        "n_adaptations_mean",
        "n_adaptations",
        "adaptations_mean",
        "adaptations",
    ])
    runtime_col = find_col(df, [
        "detector_runtime_sec_total_mean",
        "detector_runtime_sec_total",
        "detector_runtime_mean",
        "detector_runtime",
    ])

    if method_col is None or ba_col is None:
        raise ValueError(f"Missing method/BA columns in {path}: {list(df.columns)}")

    out = pd.DataFrame(index=df.index)
    out["source"] = pretty_source(path)
    out["tier"] = classify_tier(path)
    out["path"] = str(path)
    out["method"] = df[method_col].map(normalize_method)
    out["method_label"] = out["method"].map(METHOD_LABELS).fillna(out["method"])

    out["n_seeds"] = to_num(df[n_seeds_col]) if n_seeds_col is not None else np.nan
    out["mean_balanced_accuracy"] = to_num(df[ba_col])
    out["gain_vs_noadapt"] = to_num(df[gain_col]) if gain_col is not None else np.nan
    out["error_area"] = to_num(df[error_col]) if error_col is not None else np.nan
    out["n_adaptations"] = to_num(df[adapt_col]) if adapt_col is not None else np.nan
    out["detector_runtime"] = to_num(df[runtime_col]) if runtime_col is not None else np.nan

    return out.dropna(subset=["method", "mean_balanced_accuracy"])


def gate_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for (source, tier), g in df.groupby(["source", "tier"]):
        adaptive = g[g["method"] != "no_adaptation"].copy()
        noadapt = g[g["method"] == "no_adaptation"].copy()

        if adaptive.empty:
            continue

        best_actual = g.sort_values("mean_balanced_accuracy", ascending=False).iloc[0]
        best_adaptive = adaptive.sort_values("mean_balanced_accuracy", ascending=False).iloc[0]
        best_gain = adaptive.sort_values("gain_vs_noadapt", ascending=False).iloc[0]
        worst_gain = adaptive.sort_values("gain_vs_noadapt", ascending=True).iloc[0]

        noadapt_ba = float(noadapt["mean_balanced_accuracy"].iloc[0]) if not noadapt.empty else np.nan

        qk = adaptive[adaptive["method"].str.startswith("qk_")]
        best_qk = None
        if not qk.empty:
            best_qk = qk.sort_values("mean_balanced_accuracy", ascending=False).iloc[0]

        n_positive = int((adaptive["gain_vs_noadapt"] > 0).sum())
        n_negative = int((adaptive["gain_vs_noadapt"] < 0).sum())

        rows.append(
            {
                "source": source,
                "tier": tier,
                "noadapt_ba": noadapt_ba,

                "best_actual_method": best_actual["method_label"],
                "best_actual_ba": best_actual["mean_balanced_accuracy"],

                "best_adaptive_method": best_adaptive["method_label"],
                "best_adaptive_ba": best_adaptive["mean_balanced_accuracy"],

                "best_gain_method": best_gain["method_label"],
                "best_gain_vs_noadapt": best_gain["gain_vs_noadapt"],

                "worst_gain_method": worst_gain["method_label"],
                "worst_gain_vs_noadapt": worst_gain["gain_vs_noadapt"],

                "n_adaptive_methods_positive_gain": n_positive,
                "n_adaptive_methods_negative_gain": n_negative,

                "best_qk_method": "" if best_qk is None else best_qk["method_label"],
                "best_qk_ba": np.nan if best_qk is None else best_qk["mean_balanced_accuracy"],
                "best_qk_gain_vs_noadapt": np.nan if best_qk is None else best_qk["gain_vs_noadapt"],

                "policy_problem_signal": bool(
                    n_negative >= 2 or float(worst_gain["gain_vs_noadapt"]) < -0.5
                ),
                "policy_opportunity_signal": bool(
                    n_positive >= 2 or float(best_gain["gain_vs_noadapt"]) > 0.5
                ),
                "mixed_policy_signal": bool(n_positive >= 1 and n_negative >= 1),
            }
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values(["tier", "source"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_ROOT.rglob(SUMMARY_FILE_NAME))
    print("[SUMMARY FILES FOUND]", len(files))

    frames = []
    errors = []

    for path in files:
        print("[LOAD]", path)
        try:
            frames.append(standardize_summary(path))
        except Exception as exc:
            print("[SKIP]", path, exc)
            errors.append({"path": str(path), "error": repr(exc)})

    if not frames:
        raise SystemExit("No usable summary files loaded.")

    method_df = pd.concat(frames, ignore_index=True)
    gate_df = gate_summary(method_df)

    method_path = OUT_DIR / "paper2_phase0_summary_method_table.csv"
    gate_path = OUT_DIR / "paper2_phase0_summary_gate_table.csv"
    qk_path = OUT_DIR / "paper2_phase0_summary_qk_only.csv"
    manifest_path = OUT_DIR / "paper2_phase0_summary_manifest.json"

    method_df.to_csv(method_path, index=False)
    gate_df.to_csv(gate_path, index=False)
    method_df[method_df["method"].str.startswith("qk_")].to_csv(qk_path, index=False)

    manifest = {
        "description": "Phase 0 safe-readaptation gate using existing summary files only.",
        "warning": "This is not a window-level oracle. It is a cheap aggregate decision gate.",
        "files_loaded": [str(p) for p in files],
        "load_errors": errors,
        "outputs": {
            "method_table": str(method_path),
            "gate_table": str(gate_path),
            "qk_only": str(qk_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print()
    print("[SAVED]")
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
