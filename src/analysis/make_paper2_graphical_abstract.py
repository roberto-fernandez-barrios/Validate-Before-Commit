"""Render a graphical abstract (Elsevier-style) summarizing the paper in one image.

Problem -> insight -> solution -> result, as a clean horizontal schematic. Output to docs/img/.
"""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = "docs/img"
GREEN = "#2a9d8f"
RED = "#e76f51"
DARK = "#264653"
GREY = "#adb5bd"
LIGHT = "#f4f1de"


def box(ax, x, y, w, h, text, fc, ec, tc="black", fs=10, weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.02",
                                linewidth=1.6, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, weight=weight, zorder=3, wrap=True)


def arrow(ax, x1, y1, x2, y2, color=DARK):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=18,
                                 lw=2.2, color=color, zorder=1))


def main():
    os.makedirs(OUT, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12.8, 5.2))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # Title / insight band
    ax.text(0.5, 0.955, "Validate Before Commit: label-efficient gating of drift-triggered classifier updates for NIDS",
            ha="center", va="center", fontsize=14.5, weight="bold", color=DARK)
    ax.text(0.5, 0.88,
            "Detection $\\neq$ decision: retraining restores accuracy to a nearly regime-invariant level, so its "
            "benefit is the deployed model's headroom — a quantity detector scores cannot see (per-trigger r $\\approx$ 0).",
            ha="center", va="center", fontsize=10.5, color=DARK, style="italic")

    # Source box
    box(ax, 0.015, 0.40, 0.15, 0.20, "Concept drift\n→ alarm fires", LIGHT, DARK, DARK, 10.5, "bold")

    # Naive branch (top)
    arrow(ax, 0.165, 0.55, 0.30, 0.72)
    box(ax, 0.30, 0.63, 0.26, 0.18, "Naive\nretrain & deploy\non every alarm", "#fdece7", RED, DARK, 10)
    arrow(ax, 0.56, 0.72, 0.635, 0.72, RED)
    box(ax, 0.635, 0.62, 0.35, 0.20,
        "✗  Can be NET-HARMFUL\nToN-IoT:  $-1.4$ to $-3.7$ BA pts\n(no adaptation can win)", "#fdece7", RED, "#a63a24", 10.5, "bold")

    # Gate branch (bottom)
    arrow(ax, 0.165, 0.45, 0.30, 0.30)
    box(ax, 0.30, 0.17, 0.31, 0.24,
        "VALIDATE-BEFORE-COMMIT gate\nretrain a candidate →\ntest on ~32 labeled flows →\ncommit only if it beats the incumbent",
        "#e8f4f2", GREEN, DARK, 9.6, "bold")
    arrow(ax, 0.61, 0.29, 0.66, 0.29, GREEN)
    box(ax, 0.66, 0.19, 0.325, 0.20,
        "✓  Empirically safe & label-efficient\n$+0.9$ to $+1.1$ BA pts; never\nsignificantly worse than either baseline", "#e8f4f2", GREEN, "#1d6f64", 10.5, "bold")

    # Bottom robustness badges
    badges1 = "~8 labels / confirmed drift    •    probes 20 windows stale or natural prevalence    •    fails safe under 40% random label flips"
    badges2 = "2 detectors × 4 downstream classifiers    •    pre-specified criteria, 30-seed 95% CIs    •    reproducible artifact"
    ax.add_patch(FancyBboxPatch((0.03, 0.008), 0.94, 0.12, boxstyle="round,pad=0.004,rounding_size=0.02",
                                linewidth=1.2, edgecolor=GREY, facecolor="#f7f7f7", zorder=1))
    ax.text(0.5, 0.092, badges1, ha="center", va="center", fontsize=8.5, color=DARK)
    ax.text(0.5, 0.042, badges2, ha="center", va="center", fontsize=8.5, color=DARK)

    fig.savefig(f"{OUT}/graphical_abstract.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{OUT}/graphical_abstract.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", f"{OUT}/graphical_abstract.png")


if __name__ == "__main__":
    main()
