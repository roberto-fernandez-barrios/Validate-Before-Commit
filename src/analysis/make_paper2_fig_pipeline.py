"""Figure 1 of the main paper: candidate promotion as a decision pipeline.

Six stages -- drift signal -> candidate construction -> comparability audit ->
optional validation -> commit/reject/defer -> deployment monitoring -- with the
question each stage answers. Pure editorial figure; no result data is drawn.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

W, H = 13.0, 2.3
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

STAGES = [
    ("DRIFT\nSIGNAL", "proposes\nan update", "#fff3e0", "#e65100"),
    ("CANDIDATE\nCONSTRUCTION", "own preprocessing?\nevidence size?", "#e3f2fd", "#1565c0"),
    ("COMPARABILITY\nAUDIT", "is the comparison\ninformative?", "#e3f2fd", "#1565c0"),
    ("OPTIONAL\nVALIDATION", "probe-based\nsign estimate", "#ede7f6", "#4527a0"),
    ("COMMIT /\nREJECT / DEFER", "decision,\nnot reflex", "#f3e5f5", "#6a1b9a"),
    ("DEPLOYMENT\nMONITORING", "future value is\ndecided here", "#e8f5e9", "#1b5e20"),
]

n = len(STAGES)
# The rounded boxes carry PAD units of padding beyond their nominal rectangle, so
# connectors start/end PAD+margin clear of each edge to avoid being covered, and the
# gap is wide enough that a visible shaft remains between the arrowheads.
PAD = 1.0
bw, gap, x = 11.7, 5.5, 1.0
for i, (title, sub, fc, ec) in enumerate(STAGES):
    ax.add_patch(FancyBboxPatch((x, 34), bw, 52, boxstyle=f"round,pad={PAD}",
                                fc=fc, ec=ec, lw=1.8, mutation_scale=1.0))
    ax.text(x + bw / 2, 72, title, ha="center", va="center",
            fontsize=10.0, fontweight="bold")
    ax.text(x + bw / 2, 46, sub, ha="center", va="center",
            fontsize=8.0, style="italic", color="0.25")
    if i < n - 1:
        x0 = x + bw + PAD + 0.5          # clear of this box's right padding
        x1 = x + bw + gap - PAD - 0.5    # clear of the next box's left padding
        ax.add_patch(FancyArrowPatch((x0, 60), (x1, 60), arrowstyle="-|>",
                                     mutation_scale=11, shrinkA=0, shrinkB=0,
                                     color="0.3", lw=2.2))
    x += bw + gap

ax.text(50, 8, "A drift alarm proposes, but does not justify, promotion; "
               "construction and evidence comparability precede validation, "
               "which is conditional, not universal.",
        ha="center", fontsize=9.2, color="0.30")

fig.savefig("docs/img/fig_pipeline.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("pipeline figure written (docs/img/fig_pipeline.png)")
