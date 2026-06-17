from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def method_label(row: pd.Series) -> str:
    strategy = row["strategy"]

    if strategy == "no_adaptation":
        return "No adaptation"

    if strategy == "oracle_adaptation":
        return "Oracle adaptation"

    if strategy == "mmd_rbf_triggered_adaptation":
        return "MMD-RBF"

    if strategy == "qk_mmd_zz_triggered_adaptation":
        return "QK-MMD ZZ"

    if strategy == "qk_mmd_pauli_xz_triggered_adaptation":
        return "QK-MMD PauliXZ"

    return strategy


def save_line_plot(
    df: pd.DataFrame,
    y_col: str,
    ylabel: str,
    title: str,
    out_base: Path,
    include_methods: list[str] | None = None,
) -> None:
    plot_df = df.copy()

    if include_methods is not None:
        plot_df = plot_df[plot_df["method"].isin(include_methods)].copy()

    fig, ax = plt.subplots(figsize=(7.2, 4.4))

    for method, g in plot_df.groupby("method", sort=False):
        g = g.sort_values("severity")
        ax.plot(g["severity"], g[y_col], marker="o", label=method)

    ax.set_xlabel("Severity")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()

    fig.savefig(out_base.with_suffix(".png"), dpi=300)
    fig.savefig(out_base.with_suffix(".pdf"))
    plt.close(fig)


def escape_latex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    out = str(value)
    for old, new in replacements.items():
        out = out.replace(old, new)
    return out


def format_latex_cell(value) -> str:
    if pd.isna(value):
        return ""

    if isinstance(value, float):
        return f"{value:.4f}"

    return escape_latex(str(value))


def write_latex_table(df: pd.DataFrame, path: Path) -> None:
    columns = list(df.columns)

    lines = []
    lines.append(r"\begin{tabular}{" + "l" * len(columns) + "}")
    lines.append(r"\toprule")
    lines.append(" & ".join(escape_latex(c) for c in columns) + r" \\")
    lines.append(r"\midrule")

    for _, row in df.iterrows():
        lines.append(" & ".join(format_latex_cell(row[c]) for c in columns) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def save_table(df: pd.DataFrame, out_base: Path) -> None:
    df.to_csv(out_base.with_suffix(".csv"), index=False)
    write_latex_table(df, out_base.with_suffix(".tex"))


def main() -> None:
    input_path = Path(
        "results/raw/paper2_downstream_adaptation_final_global_001/"
        "paper2_downstream_final_global_summary.csv"
    )

    if not input_path.exists():
        raise FileNotFoundError(input_path)

    df = pd.read_csv(input_path)
    df["method"] = df.apply(method_label, axis=1)

    figures_dir = Path("results/figures/paper2_downstream_adaptation_final_global_001")
    tables_dir = Path("results/tables/paper2_downstream_adaptation_final_global_001")
    notes_dir = Path("notes")

    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    method_order = [
        "No adaptation",
        "MMD-RBF",
        "QK-MMD ZZ",
        "QK-MMD PauliXZ",
        "Oracle adaptation",
    ]

    df["method"] = pd.Categorical(df["method"], categories=method_order, ordered=True)
    df = df.sort_values(["severity", "method"])

    table_cols = [
        "severity",
        "method",
        "n_seeds",
        "post_balanced_accuracy_mean",
        "post_balanced_accuracy_std",
        "degradation_area_mean",
        "degradation_area_std",
        "adaptation_gain_vs_no_adapt_mean",
        "clean_downstream_adaptation_rate",
        "clean_adaptation_gain_mean",
        "triggered_post_rate",
        "false_alarm_any_rate",
        "trigger_delay_windows_mean",
        "detector_runtime_sec_mean",
    ]

    table = df[table_cols].copy()
    save_table(table, tables_dir / "paper_table_downstream_global_summary")

    triggered = df[
        df["strategy"].str.contains("triggered_adaptation", na=False)
    ].copy()

    triggered_table_cols = [
        "severity",
        "method",
        "n_seeds",
        "post_balanced_accuracy_mean",
        "degradation_area_mean",
        "adaptation_gain_vs_no_adapt_mean",
        "clean_downstream_adaptation_rate",
        "clean_adaptation_gain_mean",
        "triggered_post_rate",
        "false_alarm_any_rate",
        "trigger_delay_windows_mean",
    ]

    save_table(
        triggered[triggered_table_cols],
        tables_dir / "paper_table_downstream_triggered_only",
    )

    best_by_severity = (
        triggered
        .sort_values(
            [
                "severity",
                "clean_adaptation_gain_mean",
                "clean_downstream_adaptation_rate",
                "false_alarm_any_rate",
                "trigger_delay_windows_mean",
            ],
            ascending=[True, False, False, True, True],
        )
        .groupby("severity", as_index=False)
        .head(1)
    )

    save_table(
        best_by_severity[triggered_table_cols],
        tables_dir / "paper_table_downstream_best_clean_by_severity",
    )

    save_line_plot(
        df,
        y_col="post_balanced_accuracy_mean",
        ylabel="Post-drift balanced accuracy",
        title="Downstream balanced accuracy under global trigger policy",
        out_base=figures_dir / "post_balanced_accuracy_vs_severity",
    )

    save_line_plot(
        df,
        y_col="degradation_area_mean",
        ylabel="Degradation area",
        title="Downstream degradation area under global trigger policy",
        out_base=figures_dir / "degradation_area_vs_severity",
    )

    save_line_plot(
        triggered,
        y_col="clean_adaptation_gain_mean",
        ylabel="Clean adaptation gain",
        title="Clean downstream adaptation gain",
        out_base=figures_dir / "clean_adaptation_gain_vs_severity",
    )

    save_line_plot(
        triggered,
        y_col="clean_downstream_adaptation_rate",
        ylabel="Clean adaptation rate",
        title="Clean downstream adaptation success rate",
        out_base=figures_dir / "clean_adaptation_rate_vs_severity",
    )

    save_line_plot(
        triggered,
        y_col="false_alarm_any_rate",
        ylabel="False alarm rate",
        title="False alarm rate before drift",
        out_base=figures_dir / "false_alarm_rate_vs_severity",
    )

    save_line_plot(
        triggered,
        y_col="trigger_delay_windows_mean",
        ylabel="Trigger delay, windows",
        title="Post-drift trigger delay",
        out_base=figures_dir / "trigger_delay_vs_severity",
    )

    # Extract key numbers for note.
    def get_row(severity: float, method: str) -> pd.Series:
        m = df[(df["severity"] == severity) & (df["method"].astype(str) == method)]
        if m.empty:
            raise ValueError(f"Missing row severity={severity}, method={method}")
        return m.iloc[0]

    no_10 = get_row(1.0, "No adaptation")
    oracle_10 = get_row(1.0, "Oracle adaptation")
    mmd_10 = get_row(1.0, "MMD-RBF")
    qkzz_10 = get_row(1.0, "QK-MMD ZZ")
    qkpxz_10 = get_row(1.0, "QK-MMD PauliXZ")

    mmd_025 = get_row(0.25, "MMD-RBF")
    qkzz_025 = get_row(0.25, "QK-MMD ZZ")
    qkpxz_025 = get_row(0.25, "QK-MMD PauliXZ")

    note = f"""# Paper 2 downstream adaptation final global checkpoint 001

## Protocol

Dataset:

- CICIDS2017 Tuesday vs Wednesday.
- Binary IDS task: BENIGN=0, ATTACK=1.
- Balanced-prior windows.
- Initial downstream model: SVC-RBF.
- Reference regime: Tuesday.
- Shifted regime: controlled mixtures toward Wednesday.

Policy selection:

- Policy tuning seeds: 1-10.
- Final evaluation seeds: 11-40.
- Final global trigger policy:
  - threshold_quantile = 0.95
  - consecutive_k = 3

The final seeds are not used for policy selection.

## Main result

Drift-triggered adaptation substantially reduces downstream degradation relative
to no adaptation.

At severity 1.0:

- No adaptation:
  - balanced accuracy = {no_10["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {no_10["degradation_area_mean"]:.4f}

- Oracle adaptation:
  - balanced accuracy = {oracle_10["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {oracle_10["degradation_area_mean"]:.4f}

- MMD-RBF triggered adaptation:
  - balanced accuracy = {mmd_10["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {mmd_10["degradation_area_mean"]:.4f}
  - clean adaptation rate = {mmd_10["clean_downstream_adaptation_rate"]:.4f}
  - clean adaptation gain = {mmd_10["clean_adaptation_gain_mean"]:.4f}
  - false alarm rate = {mmd_10["false_alarm_any_rate"]:.4f}

- QK-MMD ZZ triggered adaptation:
  - balanced accuracy = {qkzz_10["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {qkzz_10["degradation_area_mean"]:.4f}
  - clean adaptation rate = {qkzz_10["clean_downstream_adaptation_rate"]:.4f}
  - clean adaptation gain = {qkzz_10["clean_adaptation_gain_mean"]:.4f}
  - false alarm rate = {qkzz_10["false_alarm_any_rate"]:.4f}

- QK-MMD PauliXZ triggered adaptation:
  - balanced accuracy = {qkpxz_10["post_balanced_accuracy_mean"]:.4f}
  - degradation area = {qkpxz_10["degradation_area_mean"]:.4f}
  - clean adaptation rate = {qkpxz_10["clean_downstream_adaptation_rate"]:.4f}
  - clean adaptation gain = {qkpxz_10["clean_adaptation_gain_mean"]:.4f}
  - false alarm rate = {qkpxz_10["false_alarm_any_rate"]:.4f}

## Regime-level interpretation

At severity 0.25:

- MMD-RBF is stronger:
  - clean adaptation rate = {mmd_025["clean_downstream_adaptation_rate"]:.4f}
  - clean gain = {mmd_025["clean_adaptation_gain_mean"]:.4f}

- QK-MMD ZZ:
  - clean adaptation rate = {qkzz_025["clean_downstream_adaptation_rate"]:.4f}
  - clean gain = {qkzz_025["clean_adaptation_gain_mean"]:.4f}

- QK-MMD PauliXZ:
  - clean adaptation rate = {qkpxz_025["clean_downstream_adaptation_rate"]:.4f}
  - clean gain = {qkpxz_025["clean_adaptation_gain_mean"]:.4f}

At severities 0.5 and 0.75, all triggered adaptation strategies recover a
large fraction of the oracle gain.

At severity 1.0, QK-MMD variants achieve slightly higher clean adaptation rates
than MMD-RBF under the selected global policy, while all triggered strategies
substantially reduce degradation.

## Paper claim supported

The downstream block supports the claim that drift-triggered adaptation can
substantially reduce IDS degradation under temporal distribution shift.

The evidence does not support universal QK-MMD dominance in downstream adaptation.
Instead, it supports a regime-dependent and complementary claim:

- MMD-RBF is stronger in low-moderate downstream adaptation at severity 0.25.
- QK-MMD is competitive in moderate-to-high drift.
- QK-MMD variants show slightly better clean adaptation behavior at severity 1.0.
- Combined with the controlled streaming monitor results, quantum-kernel drift
  monitors provide useful complementary geometry for drift-aware adaptation.
"""

    note_path = notes_dir / "paper2_downstream_adaptation_final_global_checkpoint_001.md"
    note_path.write_text(note, encoding="utf-8")

    print(f"Saved figures in: {figures_dir}")
    print(f"Saved tables in: {tables_dir}")
    print(f"Saved note: {note_path}")


if __name__ == "__main__":
    main()
