"""Generate IJIS exact-feature-disjoint sensitivity tables from sealed CSVs.

Every numerical cell is read from a committed analysis output.  The script writes
identical copies for the canonical and IEEE ports; the Springer port uses the
canonical table directory.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
TABLES = REPO / "results" / "tables"
B2 = TABLES / "ijis_exact_value_disjoint_b2_001"
B1 = TABLES / "ijis_exact_value_disjoint_b1_001"
AUDIT = REPO / "audits" / "exact_feature_overlap_summary.csv"
OUT_DIRS = [REPO / "manuscript" / "tables", REPO / "manuscript" / "tables_ieee"]

SCENARIOS = ("ps_full", "unsw_full", "ton_full")
SC_NAME = {"ps_full": "PortScan", "unsw_full": "UNSW-Recon", "ton_full": "ToN-IoT"}


def _write(name: str, body: str) -> None:
    for directory in OUT_DIRS:
        (directory / name).write_text(body, encoding="utf-8", newline="\n")


def _f2(value: float) -> str:
    return f"{value:+.2f}"


def _ci(lo: float, hi: float) -> str:
    return f"[{lo:.2f}, {hi:.2f}]"


def _tex(value: str) -> str:
    return f"${value}$"


def make_overlap_table() -> None:
    data = pd.read_csv(AUDIT, low_memory=False)
    data = data[data.record_type == "dataset_global"].set_index("dataset")
    rows = []
    dataset_labels = (
        ("PortScan", "PortScan"),
        ("UNSW-Recon", "UNSW-NB15"),
        ("ToN-Scanning", "ToN-IoT"),
    )
    for dataset, label in dataset_labels:
        row = data.loc[dataset]
        rows.append(
            " & ".join(
                [
                    label,
                    f"{int(row.total_rows):,}".replace(",", r"\,"),
                    f"{int(row.unique_x_groups):,}".replace(",", r"\,"),
                    f"{int(row.duplicate_x_groups):,}".replace(",", r"\,"),
                    f"{int(row.duplicate_rows_beyond_first):,}".replace(",", r"\,"),
                    f"{float(row.duplicate_rows_beyond_first_pct):.2f}\\%",
                    f"{int(row.max_group_multiplicity):,}".replace(",", r"\,"),
                    f"{int(row.conflicting_label_x_groups):,}".replace(",", r"\,"),
                    f"{int(row.conflicting_label_rows):,}".replace(",", r"\,"),
                ]
            )
            + r" \\"
        )
    body = r"""\begin{table}[t]
\centering
\caption{Exact cleaned-raw-feature audit before the sensitivity. A duplicate row is a row
beyond the first member of an exact feature group; signed zero is canonicalized and no
feature is rounded. Conflicting-label groups retain every original row and label.}
\label{tab:value_disjoint_overlap}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{l r r r r r r r r}
\toprule
Dataset & Rows & Unique $X$ & Dup. groups & Dup. rows & Dup. rate & Max mult. & Conflict groups & Conflict rows \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
    _write("table_value_disjoint_overlap.tex", body)


def _security_cells(scenario: str) -> tuple[str, str]:
    """Always-deploy attack recall and FPR at 512 -> 2,000 per class (sealed B2 security_metrics)."""
    sec = pd.read_csv(B2 / "security_metrics.csv")
    sec = sec[(sec.scenario == scenario) & (sec.policy == "naive")].set_index("candidate_size")
    r512, r2000 = float(sec.loc[512, "attack_recall"]), float(sec.loc[2000, "attack_recall"])
    f512, f2000 = float(sec.loc[512, "fpr"]), float(sec.loc[2000, "fpr"])
    return (f"{r512:.2f}$\\to${r2000:.2f}", f"{f512:.2f}$\\to${f2000:.2f}")


def make_b2_main() -> None:
    outcome = pd.read_csv(B2 / "size_effect_outcome.csv").set_index("scenario")
    contrasts = pd.read_csv(B2 / "paired_contrasts.csv").set_index("contrast")
    historical = pd.read_csv(B2 / "robustness_vs_historical.csv").set_index("scenario")
    rows = []
    for scenario in SCENARIOS:
        new = outcome.loc[scenario]
        old = historical.loc[scenario]
        con = contrasts.loc[f"{scenario}: naive-2000 vs naive-512"]
        recall, fpr = _security_cells(scenario)
        rows.append(
            " & ".join(
                [
                    SC_NAME[scenario],
                    _tex(_f2(float(old.historical_effect_pp))),
                    _tex(_f2(float(new.effect_pp))) + " " + _ci(float(con.ci95_lo), float(con.ci95_hi)),
                    f"{float(new.p_holm):.5f}",
                    str(new.classification).lower().replace("size benefit", "material benefit"),
                    _tex(_f2(float(old.effect_pp))) + " " + _ci(float(old.ci95_lo), float(old.ci95_hi)),
                    str(old.classification).lower(),
                    recall,
                    fpr,
                ]
            )
            + r" \\"
        )
    body = r"""\begin{table*}[t]
\centering
\caption{\textbf{Exact-feature-disjoint sensitivity of the full-drift size effect.}
Always-deploy with 2{,}000/class minus always-deploy with 512/class, balanced-accuracy
points, 30 fresh seeds (7001--7030). Exact cleaned raw feature groups are assigned wholly
to window, candidate-training or probe roles; multiplicity and original labels are retained.
CI95 and Holm-adjusted $p$ are from the registered deterministic paired bootstrap. The
historical source-row-disjoint estimate is shown for context; ``change'' is sensitivity
minus historical, estimated between independent seed blocks and is not a causal duplicate-
leakage effect. The last two columns give always-deploy attack recall and false-positive
rate (\%) at 512 $\to$ 2{,}000 per class from the same sealed cells: the balanced-accuracy
advantage is driven mainly by the lower false-positive rate, with recall approximately
stable and slightly lower on UNSW-Recon.}
\label{tab:value_disjoint_main}
\scriptsize
\setlength{\tabcolsep}{2.5pt}
\begin{tabular}{l r l r l l l l l}
\toprule
Benchmark & Historical & Exact-feature-disjoint [CI95] & $p_{\mathrm{Holm}}$ & Class & Change [CI95] & Change class & Recall 512$\to$2{,}000 & FPR 512$\to$2{,}000 \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    _write("table_value_disjoint_main.tex", body)


def make_b2_supp() -> None:
    contrasts = pd.read_csv(B2 / "paired_contrasts.csv")
    multiplicity = pd.read_csv(B2 / "multiplicity.csv").set_index("contrast")
    classes = pd.read_csv(B2 / "size_effect_outcome.csv").set_index("contrast")
    rows = []
    for _, row in contrasts.iterrows():
        mult = multiplicity.loc[row.contrast]
        classification = ""
        if row.contrast in classes.index:
            classification = str(classes.loc[row.contrast, "classification"]).lower()
        rows.append(
            " & ".join(
                [
                    str(row.family).replace(" (primary)", "").replace(" (secondary)", ""),
                    str(row.contrast).replace("_", r"\_"),
                    _tex(_f2(float(row.effect_pp))),
                    _ci(float(row.ci95_lo), float(row.ci95_hi)),
                    _ci(float(row.ci90_lo), float(row.ci90_hi)),
                    f"{float(mult.p_holm):.5f}",
                    classification,
                ]
            )
            + r" \\"
        )
    body = r"""{\scriptsize
\setlength{\tabcolsep}{2pt}
\renewcommand{\arraystretch}{1.08}
\begin{longtable}{p{0.12\linewidth} p{0.27\linewidth} r p{0.11\linewidth} p{0.11\linewidth} r p{0.10\linewidth}}
\caption{Exact-feature-disjoint B2 sensitivity: every registered G1--G4 contrast.
Effects are balanced-accuracy points; seed is the inferential unit; Holm correction is
within the frozen family.}\label{tab:value_disjoint_b2_supp}\\
\toprule
Family & Contrast & Effect & CI95 & CI90 & $p_{\mathrm{Holm}}$ & G2 class \\
\midrule
\endfirsthead
\multicolumn{7}{l}{\small Table~\ref{tab:value_disjoint_b2_supp} continued}\\
\toprule
Family & Contrast & Effect & CI95 & CI90 & $p_{\mathrm{Holm}}$ & G2 class \\
\midrule
\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
}
"""
    _write("table_value_disjoint_b2_supp.tex", body)


def make_b1_summary() -> None:
    classification = pd.read_csv(B1 / "cell_classification.csv").set_index("contrast")
    contrasts = pd.read_csv(B1 / "paired_contrasts.csv").set_index("contrast")
    policies = (
        ("atc", "ATC"),
        ("doc", "DoC"),
        ("enscal", "Calibrated ensemble"),
        ("replay", "Replay"),
        ("ddm", "DDM"),
        ("adwin", "ADWIN"),
    )
    rows = []
    for policy, label in policies:
        cells = []
        for scenario in SCENARIOS:
            name = f"{scenario}: {policy}-2000 vs naive-2000"
            cells.append(
                _tex(_f2(float(contrasts.loc[name, "effect_pp"])))
                + " ("
                + str(classification.loc[name, "classification"]).lower()
                + ")"
            )
        rows.append(" & ".join([label] + cells) + r" \\")
    body = r"""\begin{table}[t]
\centering
\caption{Exact-feature-disjoint B1 sensitivity at the primary 2{,}000/class condition:
policy minus always-deploy under full pool-constructed progressive drift. Effects are
balanced-accuracy points; parenthetical classes apply the frozen CI/magnitude/Holm rule.
DDM and ADWIN are qualified throughout as their registered reference-parameter settings.}
\label{tab:value_disjoint_b1_summary}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{l l l l}
\toprule
Policy & PortScan & UNSW-Recon & ToN-IoT \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
    _write("table_value_disjoint_b1_summary.tex", body)


def make_b1_robustness() -> None:
    interpretation = json.loads((B1 / "ROBUSTNESS_INTERPRETATION.json").read_text(encoding="utf-8"))
    labels = {
        "ATC_RETENTION": "ATC full-drift retention",
        "ENSEMBLE_RETENTION": "Calibrated-ensemble full-drift retention",
        "COST_ALTERNATIVES": "Costs remain among alternatives",
        "ATC_VS_POINT": "ATC remains compatible with point in at least five cells",
        "SIZE_DEPENDENT_ORDERING": "Policy ordering remains candidate-size-dependent",
        "NO_GLOBAL_DOMINANCE": "No evaluated policy globally dominates",
    }
    rows = []
    for key, value in interpretation["predicates"].items():
        rows.append(f"{labels[key]} & " + (r"\textbf{holds}" if value else "does not hold") + r" \\")
    body = r"""\begin{table}[t]
\centering
\caption{Pre-registered B1 robustness predicates under exact-feature-disjoint roles.
Four of six hold and no direct historical material-gain/material-cost reversal occurs;
the mechanical verdict is \textsc{partially robust}.}
\label{tab:value_disjoint_b1_robustness}
\small
\begin{tabular}{p{0.72\linewidth} l}
\toprule
Predicate & Result \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
    _write("table_value_disjoint_b1_robustness.tex", body)


def main() -> None:
    make_overlap_table()
    make_b2_main()
    make_b2_supp()
    make_b1_summary()
    make_b1_robustness()
    print("IJIS exact-feature-disjoint tables written to canonical and IEEE directories")


if __name__ == "__main__":
    main()
