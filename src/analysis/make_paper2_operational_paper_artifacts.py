from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


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


def format_cell(value) -> str:
    if pd.isna(value):
        return ""

    if isinstance(value, float):
        return f"{value:.4f}"

    return escape_latex(str(value))


def write_latex_table(df: pd.DataFrame, path: Path) -> None:
    cols = list(df.columns)
    lines = []
    lines.append(r"\begin{tabular}{" + "l" * len(cols) + "}")
    lines.append(r"\toprule")
    lines.append(" & ".join(escape_latex(c) for c in cols) + r" \\")
    lines.append(r"\midrule")

    for _, row in df.iterrows():
        lines.append(" & ".join(format_cell(row[c]) for c in cols) + r" \\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def save_table(df: pd.DataFrame, base: Path) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(base.with_suffix(".csv"), index=False)
    write_latex_table(df, base.with_suffix(".tex"))


def main() -> None:
    tables_dir = Path("results/tables/paper2_operational_paper_artifacts_001")
    figures_dir = Path("results/figures/paper2_operational_paper_artifacts_001")
    notes_dir = Path("notes")

    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    strict_path = Path(
        "results/tables/paper2_operational_scale_impact_001/"
        "paper_table_quantum_strict_operational_zones.csv"
    )

    if not strict_path.exists():
        raise FileNotFoundError(strict_path)

    strict = pd.read_csv(strict_path)

    compact = strict[
        strict["traffic_volume"].isin([1_000_000, 10_000_000, 100_000_000])
    ].copy()

    compact = compact[
        [
            "severity",
            "method",
            "traffic_volume",
            "post_alarm_delta_vs_mmd",
            "additional_detected_flow_equiv_vs_mmd",
            "clean_gain_delta_vs_mmd",
            "false_alarm_delta_vs_mmd",
        ]
    ].sort_values(["severity", "method", "traffic_volume"])

    save_table(
        compact,
        tables_dir / "paper_table_strict_operational_quantum_zones_compact",
    )

    # Figure 1: additional detected flow-equivalent samples vs traffic volume.
    fig, ax = plt.subplots(figsize=(7.2, 4.6))

    for (severity, method), g in strict.groupby(["severity", "method"]):
        g = g.sort_values("traffic_volume")
        label = f"{method}, severity={severity}"
        ax.plot(
            g["traffic_volume"],
            g["additional_detected_flow_equiv_vs_mmd"],
            marker="o",
            label=label,
        )

    ax.set_xscale("log")
    ax.set_xlabel("Traffic volume")
    ax.set_ylabel("Additional drift-affected flow-equivalent samples flagged vs MMD-RBF")
    ax.set_title("Strict operational QK-MMD advantage zones")
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()

    fig.savefig(figures_dir / "strict_operational_additional_detected_vs_volume.png", dpi=300)
    fig.savefig(figures_dir / "strict_operational_additional_detected_vs_volume.pdf")
    plt.close(fig)

    # Figure 2: post-alarm delta by severity/method at largest relevant volume.
    largest = strict[strict["traffic_volume"] == strict["traffic_volume"].max()].copy()

    fig, ax = plt.subplots(figsize=(6.8, 4.4))

    labels = [
        f"{row.method}\nsev={row.severity}"
        for row in largest.itertuples(index=False)
    ]

    ax.bar(labels, largest["post_alarm_delta_vs_mmd"])
    ax.set_ylabel("Post-drift alarm coverage gain vs MMD-RBF")
    ax.set_title("QK-MMD post-drift alarm coverage gain")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()

    fig.savefig(figures_dir / "strict_operational_post_alarm_gain.png", dpi=300)
    fig.savefig(figures_dir / "strict_operational_post_alarm_gain.pdf")
    plt.close(fig)

    note_lines = [
        "# Paper 2 operational paper artifacts checkpoint 001",
        "",
        "## Purpose",
        "",
        "This script creates compact paper-facing tables and figures for the strict",
        "operational QK-MMD advantage zones.",
        "",
        "## Generated artifacts",
        "",
        f"- `{tables_dir / 'paper_table_strict_operational_quantum_zones_compact.csv'}`",
        f"- `{tables_dir / 'paper_table_strict_operational_quantum_zones_compact.tex'}`",
        f"- `{figures_dir / 'strict_operational_additional_detected_vs_volume.png'}`",
        f"- `{figures_dir / 'strict_operational_additional_detected_vs_volume.pdf'}`",
        f"- `{figures_dir / 'strict_operational_post_alarm_gain.png'}`",
        f"- `{figures_dir / 'strict_operational_post_alarm_gain.pdf'}`",
        "",
        "## Paper claim",
        "",
        "Use these artifacts to support the claim that QK-MMD provides a strict",
        "operational monitoring advantage in high-severity/high-volume regimes,",
        "not universal downstream superiority.",
        "",
    ]

    note_path = notes_dir / "paper2_operational_paper_artifacts_checkpoint_001.md"
    note_path.write_text("\n".join(note_lines), encoding="utf-8")

    print(f"Saved tables in: {tables_dir}")
    print(f"Saved figures in: {figures_dir}")
    print(f"Saved note: {note_path}")


if __name__ == "__main__":
    main()
