"""Copy the rendered LaTeX result tables into manuscript/tables/, LaTeX-safe.

Replaces Unicode symbols with math commands and removes the redundant "Table N:"/"Appendix Table:"
prefix from captions (LaTeX adds "Table N:" itself). Output: manuscript/tables/*.tex.
"""
from __future__ import annotations
import glob
import os
import re

SRC = "results/tables/paper2_paper_tables_001"
DST = "manuscript/tables"
REPL = [("−", "$-$"), ("≈", r"$\approx$"), ("×", r"$\times$"),
        ("±", r"$\pm$"), ("≥", r"$\ge$"), ("≤", r"$\le$"),
        ("≠", r"$\neq$"), ("Δ", r"$\Delta$"), ("ε", r"$\varepsilon$"),
        ("λ", r"$\lambda$"), ("γ", r"$\gamma$"), ("η", r"$\eta$"),
        ("—", "---"), ("–", "--"), ("→", r"$\to$")]
CAP_PREFIX = re.compile(r"(\\caption\{)(?:Table \d+:\s*|Appendix Table:\s*)")


def main():
    os.makedirs(DST, exist_ok=True)
    for f in sorted(glob.glob(f"{SRC}/*.tex")):
        s = open(f, encoding="utf-8").read()
        for a, b in REPL:
            s = s.replace(a, b)
        s = CAP_PREFIX.sub(r"\1", s)
        s = s.replace(r"\begin{tabular}", "\\small\n\\begin{tabular}")  # keep wide tables in the margin
        out = os.path.join(DST, os.path.basename(f))
        open(out, "w", encoding="utf-8").write(s)
        print("wrote", out)
    # verify ascii-clean
    bad = {}
    for f in glob.glob(f"{DST}/*.tex"):
        cs = sorted({hex(ord(c)) for c in open(f, encoding="utf-8").read() if ord(c) > 127})
        if cs:
            bad[os.path.basename(f)] = cs
    print("remaining non-ascii:", bad if bad else "NONE")


if __name__ == "__main__":
    main()
