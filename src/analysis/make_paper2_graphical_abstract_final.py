"""Graphical abstract, KBS final focus cut: a radically simplified three-step figure.

Three steps down the centre --- DRIFT ALARM proposes a challenger; IS THE CHALLENGER
COMPARABLE? (own preprocessing + adequate evidence); VALIDATE CONDITIONALLY (when
construction, evidence or incumbent health remain uncertain) --- over three result
messages. Six boxes, ~50 words inside the diagram, no confidence intervals, no secondary
numbers. The nominal size parity result is stated under the ZERO-DRIFT CONTROL within the
0.5-pp margin. Output above Elsevier's 1328x531 minimum.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

W, H = 13.28, 5.31
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box(x, y, w, h, text, fc, ec, fs=13.0, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.1",
                                fc=fc, ec=ec, lw=2.0, mutation_scale=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", linespacing=1.28)


def arrow(x0, y0, x1, y1, color="0.3"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=20, color=color, lw=2.4))


# ---- title ----
ax.text(50, 95, "A drift alarm proposes a challenger; comparability and conditional validation decide",
        ha="center", fontsize=15.0, fontweight="bold")

# ---- three central steps ----
cx, w = 26, 48
box(cx, 74, w, 12, "DRIFT ALARM\nproposes a challenger", "#fff3e0", "#e65100", fs=13, bold=True)
arrow(50, 73.5, 50, 69)
box(cx, 55, w, 13, "IS THE CHALLENGER COMPARABLE?\nown preprocessing + adequate evidence",
    "#e3f2fd", "#1565c0", fs=13, bold=True)
arrow(50, 54.5, 50, 50)
box(cx, 34, w, 15, "VALIDATE CONDITIONALLY\nwhen construction, evidence or\nincumbent health remain uncertain",
    "#ede7f6", "#4527a0", fs=13, bold=True)

# ---- three result messages ----
box(1.5, 3, 31, 24,
    "Frozen incumbent-owned\npreprocessing amplified\napparent promotion harm",
    "#fff8e1", "#795548", fs=12)
box(34.5, 3, 31, 24,
    "Nominal size parity removed\nthe detectable mean zero-drift\nharm (ZERO-DRIFT CONTROL,\nwithin the 0.5-pp margin)",
    "#e8f5e9", "#1b5e20", fs=12)
box(67.5, 3, 31, 24,
    "Chronological replays:\nvalidation can protect a healthy\nincumbent but delay recovery\nafter incumbent collapse",
    "#eceff1", "#37474f", fs=12)

fig.savefig("docs/img/graphical_abstract.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("graphical abstract written (docs/img/graphical_abstract.png)")
