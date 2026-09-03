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
  cover_letter.md              notes/ijis_cover_letter.md (text for the submission form)
  cover_letter.pdf             the same letter typeset (pdflatex) for the file-upload slot
  declarations.md              Statements and Declarations as plain text (for the submission form)
  author_metadata.md, artifact_citation.md   copied from dist/submission_candidate/
  README.md, SHA256SUMS.txt
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MS = REPO / "manuscript"
OUT = REPO / "dist" / "submission_ijis"
SRC = OUT / "latex_source"

MAIN = "main_springer"
SUPP = "supplement_springer"
JOURNAL = "International Journal of Information Security"


def _artifact_version() -> str:
    bib = (MS / "references.bib").read_text(encoding="utf-8")
    m = re.search(r"note\s*=\s*\{Version ([0-9.]+)\}", bib)
    if not m:
        sys.exit("artifact version missing from manuscript/references.bib")
    return m.group(1)


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


def _md_to_latex(text: str) -> str:
    """The cover letter's Markdown subset (bold, italics, arrows, middle dots) as LaTeX."""
    esc = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
           "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    t = "".join(esc.get(c, c) for c in text)
    for old, new in (("\u2192", r"$\to$"), ("\u00b7", r"~$\cdot$~"), ("\u2014", "---"), ("\u2013", "--"),
                     ("\u2248", r"$\approx$"), ("\u2264", r"$\le$"), ("\u2265", r"$\ge$"), ("\u00d7", r"$\times$"),
                     ("\u201c", "``"), ("\u201d", "''"), ("\u2018", "`"), ("\u2019", "'")):
        t = t.replace(old, new)
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t, flags=re.S)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\\emph{\1}", t, flags=re.S)
    return t


def _cover_letter_pdf(md: Path, pdf: Path) -> None:
    """Typeset the cover letter (the Markdown text pasted into the submission form) as a
    one-page letter for the file-upload slot: affiliation and date, addressee, subject line,
    the body paragraphs verbatim, closing and signature block. Same source, no second text."""
    body = md.read_text(encoding="utf-8").split("\n---\n", 1)[1]
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
    title = re.search(r"\\title\[mode=title\]\{(.*?)\}\n",
                      (MS / "main.tex").read_text(encoding="utf-8"), re.S).group(1)
    date = paras.pop(0) if not paras[0].startswith("Dear") else ""
    closing = next(i for i, p in enumerate(paras) if p.startswith("Sincerely"))
    letter, signature = paras[:closing + 1], paras[closing + 1:]
    tex_paras = "\n\n".join(_md_to_latex(p) for p in letter)
    tex_sig = "\n\n".join(_md_to_latex(p).replace("\n", r"\\" + "\n") for p in signature)
    preamble = "\n".join([
        r"\documentclass[11pt,a4paper]{article}",
        r"\usepackage[T1]{fontenc}", r"\usepackage[utf8]{inputenc}", r"\usepackage{mathptmx}",
        r"\usepackage[a4paper,margin=22mm,top=17mm,bottom=16mm]{geometry}",
        r"\usepackage{microtype}", r"\usepackage[hidelinks]{hyperref}",
        r"\setlength{\parindent}{0pt}\setlength{\parskip}{0.42\baselineskip}",
        r"\pagestyle{empty}",
        r"\hypersetup{pdftitle={Cover letter: " + title + r"},pdfauthor={Roberto Fern\'andez-Barrios}}",
        r"\begin{document}", r"\fontsize{10.5}{12.6}\selectfont"])
    # every block is its own paragraph (blank line between them), so spacing commands take effect
    blocks = [
        r"\noindent\begin{minipage}[t]{0.62\textwidth}\textbf{Faculty of Engineering, University of Deusto}\\" "\n"
        r"Avda.\ de las Universidades 24, 48007 Bilbao, Spain\end{minipage}\hfill" "\n"
        r"\begin{minipage}[t]{0.34\textwidth}\raggedleft " + _md_to_latex(date) + r"\end{minipage}",
        r"\vspace{0.6em}",
        r"Editor-in-Chief\\ \emph{" + JOURNAL + r"}\\ Springer Nature",
        r"\vspace{0.3em}",
        r"\textbf{Subject:} submission of the original research article ``" + title + "''",
        tex_paras,
        r"\vspace{0.8em}",
        tex_sig,
        r"\end{document}"]
    tex = preamble + "\n\n" + "\n\n".join(blocks) + "\n"
    tex_path = pdf.with_suffix(".tex")
    tex_path.write_text(tex, encoding="utf-8", newline="\n")
    for _ in range(2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_path.name], cwd=pdf.parent,
                           capture_output=True, text=True, errors="replace", timeout=300)
        if r.returncode != 0:
            sys.exit("cover letter: pdflatex failed:\n" + "\n".join(r.stdout.splitlines()[-25:]))
    log = pdf.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Output written on .*\((\d+) pages?", log)
    for ext in (".tex", ".aux", ".log", ".out"):
        pdf.with_suffix(ext).unlink(missing_ok=True)
    print(f"cover_letter.pdf: {m.group(1) if m else '?'} page(s)")


def main() -> None:
    for doc in (MAIN, SUPP):
        if not (MS / f"{doc}.pdf").exists():
            sys.exit(f"{doc}.pdf missing -- compile it first (manuscript/README_latex.md)")
    if OUT.exists():
        shutil.rmtree(OUT)
    SRC.mkdir(parents=True)

    main_pages, supp_pages = _pages(MAIN), _pages(SUPP)
    artifact_version = _artifact_version()
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
    _cover_letter_pdf(OUT / "cover_letter.md", OUT / "cover_letter.pdf")
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

Artifact v{artifact_version}. Generated by `python -m src.analysis.make_ijis_submission_bundle`.

- `{MAIN}.pdf` -- manuscript, Springer svjour3 two-column, {main_pages} pp., 0 undefined refs/citations.
- `ESM_1.pdf` -- Online Resource 1 (supplement with the IJIS front page), {supp_pages} pp.
- `latex_source/` and `latex_source.zip` -- editable sources: `manuscript/` ({MAIN}.tex, {SUPP}.tex,
  svjour3.cls, svglov3.clo, spmpsci.bst, references.bib, .bbl files, {n_tables} table inputs) and
  `docs/img/` ({n_figs} figure files). Compile from `manuscript/`:
  `pdflatex {MAIN} && bibtex {MAIN} && pdflatex {MAIN} && pdflatex {MAIN}`, then the same for {SUPP}.
- `cover_letter.pdf` (typeset letter for the file-upload slot) and `cover_letter.md` (the same text, for the
  form field); `declarations.md` (texts for the submission form), `author_metadata.md`,
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
