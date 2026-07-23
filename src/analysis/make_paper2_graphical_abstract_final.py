"""Graphical abstract, v1.22.1 editorial-scope revision (protocol
notes/v1_22_1_editorial_scope_protocol.md; supersedes the size-matched rewrite spec).

Spec: Trigger != superiority -> check candidate construction -> check evidence
conditions -> nominal parity evaluated?  No/uncertain -> validation may be useful;
yes, under the ZERO-DRIFT CONTROL (own preprocessing + 2,000/class nominal size
parity) -> mean BA equivalent within +-0.5 pp, no measurable point/strict gain in
this control. No universal deployment rule. Output above Elsevier's 1328x531 minimum.
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
ax.text(50, 94.5, "A trigger proposes a challenger — it does not establish superiority",
        ha="center", fontsize=FS_BIG, fontweight="bold")

# ---- top flow: trigger -> construction check -> evidence check -> parity question ----
y0, h0 = 63, 22
box(1.5, y0 + 2, 14.5, h0 - 4, "Drift alarm\n(or schedule,\nor false alarm)",
    "#fff3e0", "#e65100", fs=11.5)
arrow(17.5, y0 + h0 / 2, 20.5, y0 + h0 / 2)
box(21, y0, 20, h0, "CHECK CANDIDATE\nCONSTRUCTION\nown preprocessing,\nnot the incumbent's",
    "#e3f2fd", "#1565c0", fs=11.5, bold=True)
arrow(42.5, y0 + h0 / 2, 45.5, y0 + h0 / 2)
box(46, y0, 20, h0, "CHECK EVIDENCE\nCONDITIONS\nnominal per-class\ntraining size",
    "#e3f2fd", "#1565c0", fs=11.5, bold=True)
arrow(67.5, y0 + h0 / 2, 70.5, y0 + h0 / 2)
box(71, y0, 27, h0, "NOMINAL PARITY\nEVALUATED?",
    "#f3e5f5", "#6a1b9a", fs=13.5, bold=True)

# ---- branches ----
arrow(74, y0 - 1.5, 28, 54, color="#4527a0")
arrow(92, y0 - 1.5, 86, 55.5, color="#1b5e20")
ax.text(49, 60.5, "no / uncertain", fontsize=11.5, ha="center", color="#4527a0",
        bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.5))
ax.text(83, 58.5, "yes, under zero drift", fontsize=11.5, ha="right", color="#1b5e20",
        bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.5))

box(2, 31, 44, 21,
    "VALIDATION MAY BE USEFUL\n"
    "validate before commit: gates recovered the\n"
    "loss where construction or evidence\n"
    "conditions were asymmetric",
    "#ede7f6", "#4527a0", fs=11.5, bold=True)
box(50, 27.5, 48.5, 26.5,
    "ZERO-DRIFT CONTROL\n"
    "own preprocessing + 2,000/class nominal size parity\n"
    "$\\rightarrow$ mean BA equivalent within $\\pm$0.5 pp\n"
    "$\\rightarrow$ no measurable point/strict gain in this control",
    "#e8f5e9", "#1b5e20", fs=FS_SM, bold=True)

# ---- three evidence badges (scoped; no universal deployment rule) ----
box(1.5, 3, 31.5, 19,
    "Frozen incumbent-owned\n"
    "preprocessing manufactured the\n"
    "full-drift harm (scaling, not projection)",
    "#fff8e1", "#795548", fs=11.5)
box(34, 3, 31.5, 19,
    "A 4× nominal candidate-size disadvantage\n"
    "explains the residual zero-drift loss\n"
    "(+1.89 / +0.63 / +0.23 pp, Holm-sig.)",
    "#f5f5f5", "#455a64", fs=11.5)
box(66.5, 3, 32, 19,
    "Scope: zero drift, balanced pools,\n"
    "SVC-RBF, random proposals;\n"
    "chronological net harm unobserved",
    "#eceff1", "#37474f", fs=11.5)

fig.savefig("docs/img/graphical_abstract.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("graphical abstract written (docs/img/graphical_abstract.png)")
