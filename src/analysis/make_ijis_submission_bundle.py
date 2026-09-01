"""Assemble dist/submission_ijis/ -- the upload set for the International Journal of Information
Security submission (Springer Nature).

Run after `python -m src.analysis.port_springer` and the pdflatex/bibtex passes for
main_springer and supplement_springer (see manuscript/README_latex.md). Nothing is submitted.

Contents produced:
  main_springer.pdf            compiled manuscript (Springer svjour3 two-column)
  ESM_1.pdf                    Online Resource 1 = the supplement with the IJIS front page
  latex_source/                editable sources: manuscript/ (tex, cls/clo/bst, bib, bbl, tables)
                               and docs/img/ (every figure the two tex files include)
  latex_source.zip             the same, zipped for the "source files" upload
  cover_letter.md              notes/ijis_cover_letter.md
  declarations.md              Statements and Declarations as plain text (for the submission form)
  author_metadata.md, artifact_citation.md   copied from dist/submission_candidate/
  README.md, SHA256SUMS.txt
"""
from __future__ import annotations

import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MS = REPO / "manuscript"
OUT = REPO / "dist" / "submission_ijis"
SRC = OUT / "latex_source"

MAIN = "main_springer"
SUPP = "supplement_springer"


def _pages(doc: str) -> str:
    log = (MS / f"{doc}.log").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Output written on .*\((\d+) pages", log)
    bad = re.findall(r"(Citation .* undefined|Reference .* undefined)", log)
    if bad:
        sys.exit(f"{doc}: unresolved references/citations -- rebuild before bundling:\n" + "\n".join(bad[:5]))
    return m.group(1) if m else "?"


def _referenced_files(tex: str) -> tuple[list[str], list[str]]:
    inputs = re.findall(r"\\input\{([^}]+)\}", tex)
    figs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex)
    return inputs, figs


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _section_numbers(doc: str) -> dict[str, str]:
    """label -> section number, read from the compiled document's .aux (\\newlabel entries)."""
    aux = (MS / f"{doc}.aux").read_text(encoding="utf-8", errors="replace")
    return {m.group(1): m.group(2)
            for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}", aux)}


def _tex_to_text(block: str, labels: dict[str, str]) -> str:
    t = block
    t = re.sub(r"\\paragraph\{([^}]*)\}", r"\n## \1\n", t)
    t = re.sub(r"\\href\{([^}]*)\}\{([^}]*)\}", r"\2 (\1)", t)
    t = re.sub(r"\\cite\{[^}]*\}", "", t)

    def _ref(m: re.Match) -> str:
        key = m.group(1)
        if key not in labels:
            sys.exit(f"declarations: unresolved \\ref{{{key}}} -- compile main_springer first")
        return "\u00a7" + labels[key]

    t = re.sub(r"\\S\\ref\{([^}]*)\}", _ref, t)
    t = re.sub(r"\\S\s*", "\u00a7", t)
    t = t.replace("~", " ").replace("---", "\u2014").replace("--", "\u2013").replace("\\&", "&")
    t = re.sub(r"\\emph\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\\textbf\{([^}]*)\}", r"\1", t)
    for acc, ch in (("a", "\u00e1"), ("e", "\u00e9"), ("i", "\u00ed"), ("o", "\u00f3"), ("u", "\u00fa")):
        t = t.replace("\\'" + acc, ch)
    t = "\n".join(line.strip() for line in t.splitlines())
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip() + "\n"


def main() -> None:
    for doc in (MAIN, SUPP):
        if not (MS / f"{doc}.pdf").exists():
            sys.exit(f"{doc}.pdf missing -- compile it first (manuscript/README_latex.md)")
    if OUT.exists():
        shutil.rmtree(OUT)
    SRC.mkdir(parents=True)

    main_pages, supp_pages = _pages(MAIN), _pages(SUPP)
    _copy(MS / f"{MAIN}.pdf", OUT / f"{MAIN}.pdf")
    _copy(MS / f"{SUPP}.pdf", OUT / "ESM_1.pdf")

    # editable sources
    for name in (f"{MAIN}.tex", f"{SUPP}.tex", f"{MAIN}.bbl", f"{SUPP}.bbl", "references.bib",
                 "svjour3.cls", "svglov3.clo", "spmpsci.bst"):
        _copy(MS / name, SRC / "manuscript" / name)
    n_tables = n_figs = 0
    for doc in (MAIN, SUPP):
        tex = (MS / f"{doc}.tex").read_text(encoding="utf-8")
        inputs, figs = _referenced_files(tex)
        for p in inputs:
            f = MS / (p if p.endswith(".tex") else p + ".tex")
            _copy(f, SRC / "manuscript" / f.relative_to(MS))
            n_tables += 1
        for p in figs:
            cand = [MS / p, REPO / p]
            f = next((c for c in cand if c.exists()), None)
            if f is None:
                sys.exit(f"figure not found for {doc}: {p}")
            rel = f.relative_to(REPO) if f.is_relative_to(REPO / "docs") else Path("manuscript") / f.relative_to(MS)
            _copy(f, SRC / rel)
            n_figs += 1
    # Deterministic zip (fixed entry timestamps, sorted order) so the bundle is byte-reproducible
    # from the same committed sources.
    with zipfile.ZipFile(OUT / "latex_source.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(SRC.rglob("*")):
            if f.is_file():
                zi = zipfile.ZipInfo(f.relative_to(SRC).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = 0o644 << 16
                z.writestr(zi, f.read_bytes())

    # cover letter, declarations, metadata
    _copy(REPO / "notes" / "ijis_cover_letter.md", OUT / "cover_letter.md")
    for name in ("author_metadata.md", "artifact_citation.md"):
        src = REPO / "dist" / "submission_candidate" / name
        if src.exists():
            _copy(src, OUT / name)
    tex = (MS / f"{MAIN}.tex").read_text(encoding="utf-8")
    decl = tex[tex.index("\\section*{Statements and Declarations}") + len("\\section*{Statements and Declarations}"):
               tex.index("\\bibliographystyle")]
    (OUT / "declarations.md").write_text(
        "# Statements and Declarations (as typeset in main_springer.tex; paste into the submission form)\n"
        + _tex_to_text(decl, _section_numbers(MAIN)), encoding="utf-8", newline="\n")

    (OUT / "README.md").write_text(f"""# Submission set -- International Journal of Information Security (Springer Nature)

Artifact v1.23.0. Generated by `python -m src.analysis.make_ijis_submission_bundle`.

- `{MAIN}.pdf` -- manuscript, Springer svjour3 two-column, {main_pages} pp., 0 undefined refs/citations.
- `ESM_1.pdf` -- Online Resource 1 (supplement with the IJIS front page), {supp_pages} pp.
- `latex_source/` and `latex_source.zip` -- editable sources: `manuscript/` ({MAIN}.tex, {SUPP}.tex,
  svjour3.cls, svglov3.clo, spmpsci.bst, references.bib, .bbl files, {n_tables} table inputs) and
  `docs/img/` ({n_figs} figure files). Compile from `manuscript/`:
  `pdflatex {MAIN} && bibtex {MAIN} && pdflatex {MAIN} && pdflatex {MAIN}`, then the same for {SUPP}.
- `cover_letter.md`, `declarations.md` (texts for the submission form), `author_metadata.md`,
  `artifact_citation.md`, `SHA256SUMS.txt`.

Checklist: `notes/ijis_submission_checklist.md`. Nothing here has been submitted.
""", encoding="utf-8", newline="\n")

    lines = []
    for f in sorted(OUT.rglob("*")):
        if f.is_file() and f.name != "SHA256SUMS.txt":
            lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(OUT).as_posix()}")
    # LF line endings: `sha256sum -c SHA256SUMS.txt` cannot parse CRLF on Windows-written files.
    (OUT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"dist/submission_ijis: {MAIN}.pdf {main_pages} pp, ESM_1.pdf {supp_pages} pp, "
          f"{n_tables} table inputs, {n_figs} figures, {len(lines)} files hashed")


if __name__ == "__main__":
    main()
