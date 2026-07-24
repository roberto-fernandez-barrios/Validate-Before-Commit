# Building the Elsevier (elsarticle) manuscript

`main.tex` is a compilable Elsevier `elsarticle` document generated from the Markdown source. It pulls in the
bibliography (`references.bib`), the six result tables (`tables/*.tex`), and the figures (`../docs/img/*.png`,
via `\graphicspath{{../}}`).

## Two targets
- **`main.tex` — Elsevier CAS single-column (`cas-sc`)** — **primary: Knowledge-Based Systems** (the official
  Elsevier template; also fits ESWA / EAAI). Uses `\title[mode=title]`, `\author...[orcid=]`, `\credit` +
  `\printcredits`, `highlights` + `graphicalabstract` environments, numbered refs via `natbib[numbers]`.
- **`main_ieee.tex` (IEEEtran)** — security-branded backup: **IEEE TDSC** (two-column, `figure*`/`table*`).

The CAS class files (`cas-sc.cls`, `cas-dc.cls`, `cas-common.sty`, `cas-model2-names.bst`) are included in this
folder so `main.tex` compiles here. Bibliography defaults to `\bibliographystyle{unsrtnat}` (numbered, in order
of appearance = KBS style, and ships with natbib). For Elsevier's exact CAS numbered style, switch to
`cas-model1-num-names` (obtain that `.bst` from the full Elsevier CAS bundle / CTAN `els-cas-templates`).

Compile: `cd manuscript && latexmk -pdf main.tex` (or `pdflatex main; bibtex main; pdflatex main; pdflatex main`).

## Regenerate the LaTeX from source
```bash
python -m src.analysis.make_paper2_latex_tables    # result tables -> tables/ (Elsevier) and tables_ieee/ (IEEE)
python -m src.analysis.port_ieee                   # regenerate manuscript/main_ieee.tex from main.tex
# manuscript/main.tex is the hand-maintained Elsevier CAS source (not generated).
```
Compile IEEE with `latexmk -pdf main_ieee.tex` (needs `IEEEtran.cls`, standard in TeX Live/MiKTeX).

## Compile (needs a TeX distribution: TeX Live / MiKTeX; elsarticle.cls is standard)
```bash
cd manuscript
latexmk -pdf main.tex          # preferred; runs pdflatex + bibtex as needed
# or manually:
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## Notes / author to-do
- **Author metadata:** fill `\affiliation`, co-authors, ORCIDs, and funding/conflict statements in the
  front matter.
- **Paper 1 citation:** replace the `@misc{fernandez_paper1}` stub in `references.bib`.
- **Algorithm 1** is emitted as a `verbatim` block; optionally reformat with the `algorithm`/`algpseudocode`
  packages for typeset pseudocode.
- **Wide tables** (Tables 2–3) use `\small`; if any row still overflows, wrap the `tabular` in
  `\resizebox{\linewidth}{!}{...}`.
- **Highlights** are a separate submission file — see `manuscript/highlights.md` (Elsevier submits highlights
  outside the main PDF).
- **Graphical abstract:** `../docs/img/graphical_abstract.png`.
- **Title:** default is "Validate Before Commit: …"; the alternative hook "Knowing When Not to Retrain: …" is
  in a comment/notes if you prefer it.
- The document uses `\documentclass[preprint,11pt]{elsarticle}`; switch to `[review]` for double-spaced review
  copy, or the journal's required option.
