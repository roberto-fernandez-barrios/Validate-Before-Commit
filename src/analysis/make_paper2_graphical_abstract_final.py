"""Graphical abstract, redesigned for the final size-matched framing (registered rewrite
protocol notes/size_matched_final_rewrite_protocol.md).

Spec: Trigger != superiority -> check candidate comparability (preprocessing ownership +
training evidence) -> comparable? yes -> direct promotion may be adequate; uncertain or
asymmetric -> validate before commit. Three evidence badges, no universal claims.
Output above Elsevier's 1328x531 minimum.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

W, H = 13.28, 5.31  # inches at 100 dpi -> 1328x531; render at 200 dpi
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

FS_BIG, FS_MED, FS_SM = 20, 14.5, 12.5


def box(x, y, w, h, text, fc, ec, fs=FS_MED, tc="black", bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.2",
                                fc=fc, ec=ec, lw=2.2, mutation_scale=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(x0, y0, x1, y1, color="0.25", lw=2.6, style="-|>"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style,
                                 mutation_scale=22, color=color, lw=lw))


# ---- title strip ----
ax.text(50, 94, "A drift alarm proposes a challenger — it does not establish superiority",
        ha="center", fontsize=FS_BIG, fontweight="bold")

# ---- flow: trigger -> comparability check -> two branches ----
y0, h0 = 52, 24
box(2, y0 + 4, 15, h0 - 8, "Drift alarm\n(or schedule,\nor false alarm)", "#fff3e0", "#e65100", fs=FS_SM)
arrow(18.5, y0 + h0 / 2, 23.5, y0 + h0 / 2)
box(24, y0, 25, h0,
    "CHECK CANDIDATE\nCOMPARABILITY\n"
    "— preprocessing ownership\n— training evidence (size)",
    "#e3f2fd", "#1565c0", fs=FS_SM, bold=True)

arrow(50.5, y0 + h0 * 0.72, 57.5, 74)
arrow(50.5, y0 + h0 * 0.28, 57.5, 40)
ax.text(54, 70, "comparable", fontsize=11, ha="center", rotation=18, color="#1b5e20")
ax.text(54, 48, "uncertain /\nasymmetric", fontsize=11, ha="center", rotation=-18, color="#4527a0")

box(58, 64, 40, 20,
    "Direct promotion may be adequate\n"
    "size-matched self-contained challengers:\n"
    "always-deploy ≡ never-adapt (3/3 benchmarks)",
    "#e8f5e9", "#1b5e20", fs=FS_SM)
box(58, 30, 40, 20,
    "VALIDATE BEFORE COMMIT\n"
    "gates recover the loss where evidence\n"
    "is limited, noisy or uncertain",
    "#ede7f6", "#4527a0", fs=FS_SM, bold=True)

# ---- three evidence badges ----
box(1.5, 4, 31.5, 21,
    "Frozen incumbent-owned\n"
    "preprocessing manufactured the\n"
    "full-drift harm (scaling, not projection)",
    "#fff8e1", "#795548", fs=12)
box(34, 4, 31.5, 21,
    "A 4× candidate-size disadvantage\n"
    "explains the residual zero-drift loss\n"
    "(+1.89 / +0.63 / +0.23 pp, Holm-sig.)",
    "#f5f5f5", "#455a64", fs=12)
box(66.5, 4, 32, 21,
    "At matched size, gates add no\n"
    "measurable value; chronological\n"
    "net harm remains unobserved",
    "#eceff1", "#37474f", fs=12)

fig.savefig("docs/img/graphical_abstract.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("graphical abstract written (docs/img/graphical_abstract.png)")
