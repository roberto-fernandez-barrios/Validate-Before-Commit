"""Compile the three PDFs (CAS main, supplement, IEEE) -- final-kbs P10 steps 7-8.

Runs pdflatex/bibtex in manuscript/ (pdflatex + bibtex must be on PATH), fails on LaTeX
errors, and refuses undefined references or citations in any of the three logs.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

MS = Path(__file__).resolve().parents[2] / "manuscript"
DOCS = ["main", "supplement", "main_ieee"]


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=MS, capture_output=True, text=True, timeout=600)


def build(doc: str) -> None:
    for step in ([f"pdflatex", "-interaction=nonstopmode", f"{doc}.tex"],
                 ["bibtex", doc],
                 ["pdflatex", "-interaction=nonstopmode", f"{doc}.tex"],
                 ["pdflatex", "-interaction=nonstopmode", f"{doc}.tex"]):
        r = run(step)
        if step[0] == "pdflatex" and r.returncode != 0:
            tail = "\n".join(r.stdout.splitlines()[-30:])
            sys.exit(f"pdflatex failed on {doc}.tex:\n{tail}")
    log = (MS / f"{doc}.log").read_text(encoding="utf-8", errors="replace")
    bad = re.findall(r"(Citation .* undefined|Reference .* undefined)", log)
    if bad:
        sys.exit(f"{doc}: unresolved references/citations:\n" + "\n".join(bad[:10]))
    m = re.search(r"Output written on .*\((\d+) pages", log)
    print(f"  {doc}.pdf: {m.group(1) if m else '?'} pages, 0 undefined refs/citations")


def main() -> None:
    for doc in DOCS:
        build(doc)


if __name__ == "__main__":
    main()
