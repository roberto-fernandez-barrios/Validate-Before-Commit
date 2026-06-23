from __future__ import annotations

from pathlib import Path

import pandas as pd


NOTES_DIR = Path("notes")

MULTI_SCENARIO_DIR = Path("results/tables/paper2_progressive_multi_scenario_cicids_001")
ACTIONABLE_DIR = Path("results/tables/paper2_actionable_drift_wednesday_001")


def read_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        print(f"[WARN] Missing: {path}")
        return None
    return pd.read_csv(path)


def table(df: pd.DataFrame | None, cols: list[str] | None = None, n: int | None = None) -> str:
    if df is None or df.empty:
        return "No rows."

    out = df.copy()

    if cols is not None:
        keep = [c for c in cols if c in out.columns]
        out = out[keep]

    if n is not None:
        out = out.head(n)

    return out.to_string(index=False)


def main() -> None:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    multi_summary = read_csv(MULTI_SCENARIO_DIR / "paper_table_multi_scenario_summary.csv")
    multi_paired = read_csv(MULTI_SCENARIO_DIR / "paper_table_multi_scenario_paired.csv")

    actionable_components = read_csv(ACTIONABLE_DIR / "paper_table_actionable_components.csv")
    actionable_strict = read_csv(ACTIONABLE_DIR / "paper_table_actionable_utility_strict_positive.csv")

    qk_energy = None
    if multi_paired is not None and not multi_paired.empty:
        qk_energy = multi_paired[
            (
                (multi_paired["method_a"] == "QK-MMD ZZ")
                & (multi_paired["method_b"] == "Energy distance")
            )
            | (
                (multi_paired["method_a"] == "Energy distance")
                & (multi_paired["method_b"] == "QK-MMD ZZ")
            )
        ].copy()

    compact_multi = None
    if multi_summary is not None and not multi_summary.empty:
        compact_multi = multi_summary[
            multi_summary["method"].isin(
                ["qk_mmd_zz", "energy_distance", "mmd_rbf", "ks_max", "jsd", "qk_mmd_pauli_xz"]
            )
        ].copy()
        compact_multi = compact_multi.sort_values(["scenario", "cumulative_error_area_mean"])

    strict_focus = None
    if actionable_strict is not None and not actionable_strict.empty:
        strict_focus = actionable_strict[
            actionable_strict["baseline"].isin(["Energy distance", "MMD-RBF", "KS-max", "JSD"])
        ].copy()
        strict_focus = strict_focus.sort_values(
            ["nuisance_mode", "baseline", "lambda_cost", "eta_cost", "gamma_cost"]
        )

    md = []

    md.append("# Paper 2 final Q1-oriented synthesis checkpoint 004")
    md.append("")
    md.append("## Executive verdict")
    md.append("")
    md.append(
        "This checkpoint supersedes checkpoint_003. The paper should no longer be framed as "
        "a simple quantum-vs-classical detector comparison. The strongest framing is a "
        "cost-sensitive actionable drift study for adaptive intrusion detection."
    )
    md.append("")
    md.append("Final positioning:")
    md.append("")
    md.append("- Q2 strong: yes.")
    md.append("- Q1 possible: yes, with careful venue targeting.")
    md.append("- Q1 guaranteed: no.")
    md.append("- Universal quantum advantage: no.")
    md.append("- Strongest contribution: operational trade-off characterization under progressive adversarial and benign/non-adversarial drift.")
    md.append("")
    md.append(
        "The paper is substantially stronger after adding multi-regime CICIDS validation and "
        "nuisance benign controls. However, the final claim must remain nuanced: QK-MMD ZZ "
        "does not universally suppress benign nuisance triggers and is computationally more "
        "expensive. Its value appears in cost regimes where readaptation is expensive relative "
        "to monitoring runtime."
    )
    md.append("")

    md.append("## Final core claim")
    md.append("")
    md.append(
        "QK-MMD ZZ provides regime-dependent operational benefits for adaptive IDS drift "
        "monitoring. Across multiple CICIDS2017 progressive adversarial drift regimes, it is "
        "competitive with strong classical distributional baselines. In Wednesday and DDoS, "
        "it achieves comparable downstream performance with fewer readaptations and higher "
        "adaptation efficiency; in PortScan, it significantly improves downstream performance "
        "at the cost of more readaptations. Benign-only controls show that QK-MMD ZZ does not "
        "universally reduce nuisance triggers, but actionable utility analysis indicates that "
        "its adversarial readaptation savings can compensate for nuisance-trigger penalties "
        "when readaptation cost is non-negligible."
    )
    md.append("")

    md.append("## One-sentence paper thesis")
    md.append("")
    md.append(
        "Quantum-kernel MMD is not a universally superior drift detector, but it can alter the "
        "operational trade-off between adversarial recovery, readaptation frequency, benign "
        "nuisance triggers, and monitoring cost in adaptive intrusion detection."
    )
    md.append("")

    md.append("## Multi-scenario adversarial evidence")
    md.append("")
    md.append(table(
        compact_multi,
        cols=[
            "scenario",
            "method_label",
            "n_seeds",
            "mean_balanced_accuracy",
            "cumulative_error_area_mean",
            "cumulative_gain_vs_no_adapt_mean",
            "n_adaptations_mean",
            "adaptation_efficiency_mean",
            "detector_runtime_sec_total_mean",
        ],
    ))
    md.append("")

    md.append("## QK-MMD ZZ vs Energy distance")
    md.append("")
    md.append(table(
        qk_energy,
        cols=[
            "scenario",
            "method_a",
            "method_b",
            "metric",
            "n_pairs",
            "mean_diff_a_minus_b",
            "ci95_low",
            "ci95_high",
            "positive_means",
            "ci_excludes_zero_positive",
        ],
    ))
    md.append("")

    md.append("## Actionable drift component summary")
    md.append("")
    md.append(
        "The actionable analysis combines adversarial progressive drift benefits with benign-only "
        "nuisance triggers. This avoids claiming that every distributional alarm is useful."
    )
    md.append("")
    md.append(table(
        actionable_components,
        cols=[
            "method_label",
            "n_seeds",
            "adversarial_gain_mean",
            "adversarial_readaptations_mean",
            "benign_nuisance_triggers_mean",
            "nodrift_nuisance_triggers_mean",
            "excess_nuisance_triggers_mean",
            "mean_balanced_accuracy",
            "cumulative_error_area_mean",
            "total_runtime_adv_plus_benign_mean",
        ],
    ))
    md.append("")

    md.append("## Actionable utility")
    md.append("")
    md.append(
        "Actionable utility is defined as adversarial gain minus readaptation cost, nuisance-trigger "
        "cost, and runtime cost. Two nuisance modes are tracked: total benign nuisance triggers "
        "and clipped excess nuisance triggers relative to the no-drift benign control."
    )
    md.append("")
    md.append(
        "The strict positive regions below indicate settings where QK-MMD ZZ has a positive "
        "bootstrap CI lower bound against a baseline."
    )
    md.append("")
    md.append(table(
        strict_focus,
        cols=[
            "baseline",
            "lambda_cost",
            "eta_cost",
            "gamma_cost",
            "nuisance_mode",
            "mean_actionable_utility_diff_qk_minus_baseline",
            "ci95_low",
            "ci95_high",
            "qk_better_ci95",
        ],
        n=160,
    ))
    md.append("")

    md.append("## Interpretation by experimental block")
    md.append("")
    md.append("### 1. Progressive adversarial drift")
    md.append("")
    md.append(
        "Triggered readaptation clearly reduces degradation relative to no adaptation. QK-MMD ZZ "
        "is competitive with Energy distance across Wednesday, PortScan, and DDoS."
    )
    md.append("")
    md.append("### 2. Regime-dependent advantage")
    md.append("")
    md.append(
        "In Wednesday and DDoS, QK-MMD ZZ mainly improves adaptation efficiency. In PortScan, "
        "it improves downstream performance but requires more readaptations. This should be "
        "presented as regime-dependent behavior, not inconsistency."
    )
    md.append("")
    md.append("### 3. Benign/non-adversarial drift")
    md.append("")
    md.append(
        "Benign-only controls do not support the claim that QK-MMD ZZ universally suppresses "
        "nuisance triggers. In Wednesday BENIGN, QK-MMD ZZ triggers more often than Energy, "
        "MMD-RBF, and KS-max. This must be reported as a limitation and as motivation for "
        "cost-sensitive actionability."
    )
    md.append("")
    md.append("### 4. Actionable utility")
    md.append("")
    md.append(
        "When readaptation cost is meaningful and runtime cost is not dominant, QK-MMD ZZ can "
        "remain preferable even after nuisance-trigger penalties. When runtime is heavily "
        "penalized, Energy distance remains a very strong classical baseline."
    )
    md.append("")

    md.append("## Claims supported")
    md.append("")
    md.append("1. Triggered readaptation reduces degradation relative to no adaptation.")
    md.append("2. QK-MMD ZZ is competitive with strong classical distributional baselines across multiple CICIDS2017 drift regimes.")
    md.append("3. QK-MMD ZZ provides fewer readaptations and higher adaptation efficiency in Wednesday and DDoS.")
    md.append("4. QK-MMD ZZ significantly improves downstream performance in PortScan.")
    md.append("5. QK-MMD ZZ does not universally reduce benign nuisance triggers.")
    md.append("6. QK-MMD ZZ has substantially higher monitoring runtime.")
    md.append("7. Cost-sensitive actionable utility can favor QK-MMD ZZ when readaptation is expensive relative to monitoring.")
    md.append("")

    md.append("## Claims to avoid")
    md.append("")
    md.append("1. Universal quantum advantage.")
    md.append("2. QK-MMD always detects earlier.")
    md.append("3. QK-MMD always improves downstream accuracy.")
    md.append("4. QK-MMD is computationally cheaper.")
    md.append("5. QK-MMD filters benign drift better in general.")
    md.append("6. Every benign drift trigger is a false alarm.")
    md.append("")

    md.append("## Recommended title")
    md.append("")
    md.append(
        "Quantum-Kernel MMD for Cost-Sensitive Actionable Drift Monitoring in Adaptive Intrusion Detection"
    )
    md.append("")
    md.append("Alternative:")
    md.append("")
    md.append(
        "Regime-Dependent Quantum-Kernel Drift Monitoring for Adaptive Intrusion Detection under Adversarial and Benign Distribution Shift"
    )
    md.append("")

    md.append("## Recommended abstract direction")
    md.append("")
    md.append(
        "The abstract should emphasize progressive drift, adaptive IDS readaptation, strong "
        "classical baselines, nuisance benign controls, and cost-sensitive actionable utility. "
        "It should explicitly avoid claiming universal quantum advantage."
    )
    md.append("")

    md.append("## Recommended next step")
    md.append("")
    md.append(
        "Stop adding new experiments for now. The next step should be paper structuring: "
        "define research questions, map each experiment to a research question, and draft "
        "the Results narrative around operational trade-offs."
    )
    md.append("")

    out = NOTES_DIR / "paper2_final_q1_synthesis_checkpoint_004.md"
    out.write_text("\n".join(md), encoding="utf-8")

    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
