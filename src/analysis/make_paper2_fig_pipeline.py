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
    ("CANDIDATE\nCONSTRUCTION", "own preprocessing?\ntraining-evidence size?", "#e3f2fd", "#1565c0"),
    ("COMPARABILITY\nAUDIT", "is the comparison\ninformative?", "#e3f2fd", "#1565c0"),
    ("OPTIONAL\nVALIDATION", "probe-based\nsign estimate", "#ede7f6", "#4527a0"),
    ("COMMIT /\nREJECT / DEFER", "decision,\nnot reflex", "#f3e5f5", "#6a1b9a"),
    ("DEPLOYMENT\nMONITORING", "future value is\ndecided here", "#e8f5e9", "#1b5e20"),
]

n = len(STAGES)
bw, gap, x = 14.2, 2.6, 1.0
for i, (title, sub, fc, ec) in enumerate(STAGES):
    ax.add_patch(FancyBboxPatch((x, 34), bw, 52, boxstyle="round,pad=1.0",
                                fc=fc, ec=ec, lw=1.8, mutation_scale=1.0))
    ax.text(x + bw / 2, 72, title, ha="center", va="center",
            fontsize=10.5, fontweight="bold")
    ax.text(x + bw / 2, 46, sub, ha="center", va="center",
            fontsize=8.6, style="italic", color="0.25")
    if i < n - 1:
        ax.add_patch(FancyArrowPatch((x + bw + 0.4, 60), (x + bw + gap - 0.4, 60),
                                     arrowstyle="-|>", mutation_scale=16,
                                     color="0.25", lw=1.8))
    x += bw + gap

ax.text(50, 8, "A drift alarm proposes, but does not justify, promotion; "
               "construction and evidence comparability precede validation, "
               "which is conditional, not universal.",
        ha="center", fontsize=9.2, color="0.30")

fig.savefig("docs/img/fig_pipeline.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("pipeline figure written (docs/img/fig_pipeline.png)")
