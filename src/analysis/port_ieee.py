"""Regenerate manuscript/main_ieee.tex from manuscript/main.tex (IEEEtran backup format).

The CAS manuscript (`main.tex`, the KBS submission format) is the single source of truth for
the abstract and the body; the IEEE version is a mechanical port kept for a possible TDSC
submission. This script rebuilds it as: IEEE preamble (kept, with the abstract refreshed from
CAS) + transformed CAS body + IEEE tail.

Transformations applied to the body:
  * table inputs point at `tables_ieee/` (two-column variants emitted by the table scripts);
  * figures become starred floats (`figure*`) so they span both columns;
  * `width=\\linewidth` becomes `width=\\textwidth` for those spanning figures.

This lived as an ad-hoc helper script until final-q1; it is part of the artifact now
because otherwise `main_ieee.tex` silently drifts out of sync with `main.tex` (it had, by an
abstract rewrite and seven independent-verification corrections). `make final-paper` runs it before
compiling, so the two manuscripts cannot diverge again.
"""
from __future__ import annotations

import re
from pathlib import Path

MS = Path(__file__).resolve().parents[2] / "manuscript"


def main() -> None:
    cas = (MS / "main.tex").read_text(encoding="utf-8")
    ieee = (MS / "main_ieee.tex").read_text(encoding="utf-8")

    body = cas[cas.index("\\section{Introduction}"):
               cas.index("\\section*{Declaration of competing interest}")]
    head = ieee[:ieee.index("\\section{Introduction}")]
    tail = ieee[ieee.index("\\section*{Data Availability}"):]

    new_abs = re.search(r"\\begin\{abstract\}\n(.*?)\n\\end\{abstract\}", cas, re.S).group(1)
    head = re.sub(r"(\\begin\{abstract\}\n).*?(\n\\end\{abstract\})",
                  lambda m: m.group(1) + new_abs + m.group(2), head, flags=re.S)
    # v1.21: sync the title from main.tex too -- the IEEE head kept its own \title and had
    # silently retained the pre-rewrite title
    new_title = re.search(r"\\title\[mode=title\]\{(.*?)\}\n", cas, re.S).group(1)
    head = re.sub(r"\\title\{.*?\}\n", "\\\\title{" + new_title.replace("\\", "\\\\") + "}\n",
                  head, count=1, flags=re.S)

    body = body.replace("\\input{tables/", "\\input{tables_ieee/")
    body = body.replace("\\begin{figure}", "\\begin{figure*}")
    body = body.replace("\\end{figure}", "\\end{figure*}")
    body = body.replace("width=\\linewidth]{docs/img", "width=\\textwidth]{docs/img")

    out = head + body + tail
    (MS / "main_ieee.tex").write_text(out, encoding="utf-8", newline="\n")
    print(f"main_ieee.tex rebuilt from main.tex: {len(out.splitlines())} lines")


if __name__ == "__main__":
    main()
