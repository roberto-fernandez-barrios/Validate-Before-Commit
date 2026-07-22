"""final-kbs P9: graphical abstract, redesigned from scratch per the frozen protocol.

Spec: show Alarm -> Challenger -> Validation -> Commit / Reject / Defer; two policy lines
(point/strict = power; risk gate = control + labels); an explicit "Controlled SVC-RBF harm case"
badge; large typography; no universal claims. Output above Elsevier's 1328x531 minimum.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

W, H = 13.28, 5.31  # inches at 100 dpi -> 1328x531; render at 200 dpi
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

BOX = dict(boxstyle="round,pad=0.6", lw=2)
FS_BIG, FS_MED, FS_SM = 21, 15, 12.5


def box(x, y, w, h, text, fc, ec, fs=FS_MED, tc="black", bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.2",
                                fc=fc, ec=ec, lw=2.2, mutation_scale=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(x0, y0, x1, y1, color="0.25", lw=2.6, style="-|>"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style,
                                 mutation_scale=22, color=color, lw=lw))


# ---- title strip ----
ax.text(50, 94, "A drift alarm proposes a challenger — it does not justify deployment",
        ha="center", fontsize=FS_BIG, fontweight="bold")

# ---- pipeline: Alarm -> Challenger -> Validation -> three actions ----
y0, h0 = 58, 17
box(2, y0, 16, h0, "Drift alarm\n(or schedule,\nor false alarm)", "#fff3e0", "#e65100")
arrow(19.5, y0 + h0 / 2, 24.5, y0 + h0 / 2)
box(25, y0, 16, h0, "Challenger\ntrained\n(a proposal)", "#e3f2fd", "#1565c0")
arrow(42.5, y0 + h0 / 2, 47.5, y0 + h0 / 2)
box(48, y0, 21, h0, "VALIDATE\nsmall labeled probe,\ncandidate vs incumbent", "#e8f5e9", "#1b5e20", bold=True)

arrow(70.5, y0 + h0 * 0.83, 76.5, 78)
arrow(70.5, y0 + h0 / 2, 76.5, y0 + h0 / 2)
arrow(70.5, y0 + h0 * 0.17, 76.5, 46)
box(77, 73, 21, 11, "COMMIT\nevidence of improvement", "#e8f5e9", "#1b5e20", fs=FS_SM)
box(77, y0 + 2.0, 21, 11, "REJECT\nkeep the incumbent", "#ffebee", "#b71c1c", fs=FS_SM)
box(77, 41, 21, 11, "DEFER\nbuy more labels later", "#ede7f6", "#4527a0", fs=FS_SM)

# ---- three messages (final-q1: simplified per external review -- one sentence each, no
# crowded caveat strip; larger type, generous spacing) ----
box(1.5, 7, 31.5, 27,
    "Controlled harm case\n\n"
    "Healthy SVC-RBF incumbent:\n"
    "swapping hurts, even with\n"
    "self-contained pipelines",
    "#fff8e1", "#795548", fs=14)
box(34, 7, 31.5, 27,
    "The trade-off\n\n"
    "Point / strict: most benefit\n"
    "Risk gates: control, more labels",
    "#f5f5f5", "#455a64", fs=14)
box(66.5, 7, 32, 27,
    "The boundary\n\n"
    "On real chronological streams\n"
    "net harm was not observed",
    "#eceff1", "#37474f", fs=14)

fig.savefig("docs/img/graphical_abstract.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("graphical abstract written (docs/img/graphical_abstract.png)")
