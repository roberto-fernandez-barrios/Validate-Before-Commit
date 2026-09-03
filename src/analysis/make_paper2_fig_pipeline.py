"""Figure 1 of the main paper: candidate promotion as a decision pipeline.

Six stages -- drift signal -> candidate construction -> comparability audit ->
optional validation -> commit/reject/defer -> deployment monitoring -- with the
question each stage answers. Pure editorial figure; no result data is drawn.

Style: print-oriented monochrome (white boxes, grey rules, serif type matching the
manuscript); the two comparability stages the paper adds are marked by a light fill
and a labelled bracket. The caption in main.tex carries the interpretive sentence, so
the figure repeats none of it.
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

W, H = 10.0, 1.8
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

INK, RULE, MUTED, FILL = "0.10", "0.30", "0.38", "0.93"

# (title, sub-question, part of the comparability layer this paper makes explicit)
STAGES = [
    ("Drift\nsignal", "proposes\nan update", False),
    ("Candidate\nconstruction", "own preprocessing?\nevidence size?", True),
    ("Comparability\naudit", "is the comparison\ninformative?", True),
    ("Optional\nvalidation", "fixed policies;\nno meta-controller", False),
    ("Commit /\nreject / defer", "decision,\nnot reflex", False),
    ("Deployment\nmonitoring", "future value is\ndecided here", False),
]

n = len(STAGES)
bw, gap, x0 = 13.6, 3.4, 0.7
y0, bh = 8, 62
xs = []
for i, (title, sub, layer) in enumerate(STAGES):
    x = x0 + i * (bw + gap)
    xs.append(x)
    ax.add_patch(Rectangle((x, y0), bw, bh, fc=FILL if layer else "white",
                           ec=RULE, lw=0.9, joinstyle="miter"))
    ax.text(x + bw / 2, y0 + bh * 0.68, title, ha="center", va="center",
            fontsize=9.4, fontweight="bold", color=INK, linespacing=1.15)
    ax.text(x + bw / 2, y0 + bh * 0.25, sub, ha="center", va="center",
            fontsize=7.6, style="italic", color=MUTED, linespacing=1.15)
    if i < n - 1:
        ax.add_patch(FancyArrowPatch((x + bw + 0.5, y0 + bh / 2),
                                     (x + bw + gap - 0.5, y0 + bh / 2),
                                     arrowstyle="-|>", mutation_scale=9,
                                     shrinkA=0, shrinkB=0, color=INK, lw=0.9))

# Bracket over the two comparability stages (the layer the paper makes explicit).
left, right = xs[1], xs[2] + bw
yb = y0 + bh + 9
ax.plot([left, left, right, right], [yb - 4, yb, yb, yb - 4], color=RULE, lw=0.8,
        solid_capstyle="butt")
ax.text((left + right) / 2, yb + 9, "comparability layer made explicit in this paper",
        ha="center", va="center", fontsize=7.8, color=MUTED)

fig.savefig("docs/img/fig_pipeline.png", dpi=300, bbox_inches="tight",
            facecolor="white")
fig.savefig("docs/img/fig_pipeline.pdf", bbox_inches="tight",
            facecolor="white")
print("pipeline figure written (docs/img/fig_pipeline.png/.pdf)")
