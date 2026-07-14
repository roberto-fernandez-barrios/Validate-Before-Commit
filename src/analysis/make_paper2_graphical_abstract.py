"""Render a graphical abstract (Elsevier-style) summarizing the paper in one image.

Problem -> insight -> solution -> result, as a clean horizontal schematic. Output to docs/img/.
Amendment-004 revision: claims match the manuscript (no "fails safe"/"never significantly
worse"; v2 registered-replication numbers; boundary disclosed), larger fonts for legibility.
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
                                linewidth=1.8, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, weight=weight, zorder=3, wrap=True)


def arrow(ax, x1, y1, x2, y2, color=DARK):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=20,
                                 lw=2.4, color=color, zorder=1))


def main():
    os.makedirs(OUT, exist_ok=True)
    fig, ax = plt.subplots(figsize=(13.2, 5.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # Title / insight band
    ax.text(0.5, 0.955, "Validate Before Commit: label-efficient gating of drift-triggered classifier updates for NIDS",
            ha="center", va="center", fontsize=16, weight="bold", color=DARK)
    ax.text(0.5, 0.875,
            "Detection $\\neq$ decision: retraining restores accuracy to a nearly regime-invariant level, so an update's "
            "benefit is the incumbent's headroom — which detector scores do not measure (per-trigger r $\\approx$ 0).",
            ha="center", va="center", fontsize=11.5, color=DARK, style="italic")

    # Source box
    box(ax, 0.01, 0.40, 0.175, 0.20, "Concept drift\n→ alarm fires\n→ candidate retrains", LIGHT, DARK, DARK, 10.6, "bold")

    # Naive branch (top)
    arrow(ax, 0.185, 0.55, 0.30, 0.72)
    box(ax, 0.30, 0.63, 0.25, 0.18, "Always DEPLOY\n(the standard loop)", "#fdece7", RED, DARK, 11)
    arrow(ax, 0.55, 0.72, 0.63, 0.72, RED)
    box(ax, 0.63, 0.60, 0.355, 0.235,
        "✗  NET-HARMFUL when the incumbent\nis healthy — in ALL THREE benchmarks\n(registered prediction test)\n…and even with ZERO drift to detect",
        "#fdece7", RED, "#a63a24", 10.8, "bold")

    # Gate branch (bottom)
    arrow(ax, 0.185, 0.45, 0.30, 0.30)
    box(ax, 0.30, 0.17, 0.30, 0.24,
        "VALIDATE BEFORE COMMIT\ntest the candidate on ~32\nlabeled flows; deploy only if\nit beats the incumbent",
        "#e8f4f2", GREEN, DARK, 10.6, "bold")
    arrow(ax, 0.60, 0.29, 0.655, 0.29, GREEN)
    box(ax, 0.655, 0.155, 0.33, 0.26,
        "✓  Harm → net benefit ($+2.4$ vs naive)\n✓  Benefit preserved ($+9.1$ PortScan)\n✓  Holds with candidate, probe AND\n    recalibration from observed traffic only\nRegistered core (2 detectors) + registered\nextensions (4 downstream models)",
        "#e8f4f2", GREEN, "#1d6f64", 10.2, "bold")

    # Bottom badges: honest scope
    badges1 = "decision cost: tens of labels (candidates: ~1,024/trigger, accounted)  •  no policy dominates the accuracy–labels–updates frontier: we map it"
    badges2 = "boundary reported: pays a premium on deep-benefit chronological replays  •  7 registered amendments, public tags  •  auditable artifact (305 pinned claims)"
    ax.add_patch(FancyBboxPatch((0.03, 0.008), 0.94, 0.115, boxstyle="round,pad=0.004,rounding_size=0.02",
                                linewidth=1.2, edgecolor=GREY, facecolor="#f7f7f7", zorder=1))
    ax.text(0.5, 0.088, badges1, ha="center", va="center", fontsize=9.8, color=DARK)
    ax.text(0.5, 0.038, badges2, ha="center", va="center", fontsize=9.8, color=DARK)

    fig.savefig(f"{OUT}/graphical_abstract.png", dpi=220, bbox_inches="tight")
    fig.savefig(f"{OUT}/graphical_abstract.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", f"{OUT}/graphical_abstract.png")


if __name__ == "__main__":
    main()
