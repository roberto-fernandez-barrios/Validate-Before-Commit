"""Graphical abstract, KBS final scope reduction: a radically simplified three-step figure.

Three steps down the centre --- DRIFT ALARM proposes a challenger; IS THE CHALLENGER
COMPARABLE? (own preprocessing + adequate evidence); VALIDATE WHEN WARRANTED (fixed
policies evaluated; no online selector) --- over three result
messages. Six boxes, ~50 words inside the diagram, no confidence intervals, no secondary
numbers. The nominal size parity result is stated as mean compatibility under the
ZERO-DRIFT CONTROL within the 0.5-pp margin, with PortScan boundary-close and no
absence-of-effect claim. Output above Elsevier's 1328x531 minimum.

Style (September 2026): print-oriented monochrome matching Figure 1 of the main paper ---
white boxes, grey rules, serif type; the comparability step carries a light fill because it
is the layer the paper makes explicit. The wording inside every box is unchanged.
"""
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["font.family"] = "serif"
matplotlib.rcParams["font.serif"] = ["STIXGeneral", "Times New Roman", "DejaVu Serif"]
matplotlib.rcParams["mathtext.fontset"] = "stix"
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

W, H = 13.28, 5.31
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

INK, RULE, MUTED, FILL = "0.10", "0.30", "0.38", "0.93"


def box(x, y, w, h, text, fs=13.0, bold=False, fill="white", lw=1.0):
    ax.add_patch(Rectangle((x, y), w, h, fc=fill, ec=RULE, lw=lw, joinstyle="miter"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=INK, linespacing=1.28)


def arrow(x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=12, shrinkA=0, shrinkB=0,
                                 color=INK, lw=1.1))


# ---- title ----
ax.text(50, 95, "A drift alarm proposes a challenger; construction and evidence condition promotion",
        ha="center", fontsize=15.0, fontweight="bold", color=INK)

# ---- three central steps; connectors run from one box's bottom edge to the next box's top ----
cx, w = 26, 48
b1y, b1h = 76, 10
b2y, b2h = 57, 10
b3y, b3h = 33, 15
box(cx, b1y, w, b1h, "DRIFT ALARM\nproposes a challenger", fs=13, bold=True)
arrow(50, b1y - 0.3, 50, b2y + b2h + 0.3)
box(cx, b2y, w, b2h, "IS THE CHALLENGER COMPARABLE?\nown preprocessing + adequate evidence",
    fs=13, bold=True, fill=FILL, lw=1.3)
arrow(50, b2y - 0.3, 50, b3y + b3h + 0.3)
box(cx, b3y, w, b3h, "VALIDATE WHEN WARRANTED\nfixed policies evaluated;\nno online meta-controller",
    fs=12.2, bold=True)

# ---- three result messages ----
box(1.5, 3, 31, 24,
    "Frozen incumbent-owned\npreprocessing amplified\napparent promotion harm", fs=12)
box(34.5, 3, 31, 24,
    "Matched-size mean effects\ncompatible within 0.5 pp\n(ZERO-DRIFT CONTROL;\nPortScan boundary-close;\nnot absence of effect)",
    fs=10.8)
box(67.5, 3, 31, 24,
    "Exact-feature-disjoint sensitivity:\n512 to 2,000 positive in 3/3;\nmaterial in 2/3; policy\nconclusions partially robust",
    fs=12)

fig.savefig("docs/img/graphical_abstract.png", dpi=300, bbox_inches="tight",
            facecolor="white")
fig.savefig("docs/img/graphical_abstract.pdf", bbox_inches="tight",
            facecolor="white")
print("graphical abstract written (docs/img/graphical_abstract.png/.pdf)")
