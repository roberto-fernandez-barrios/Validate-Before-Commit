# Building the Elsevier (elsarticle) manuscript

`main.tex` is a compilable Elsevier `elsarticle` document generated from the Markdown source. It pulls in the
bibliography (`references.bib`), the six result tables (`tables/*.tex`), and the figures (`../docs/img/*.png`,
via `\graphicspath{{../}}`).

## Two targets
- **`main.tex` (elsarticle)** — **primary: Knowledge-Based Systems** (Elsevier; single-column, numbered refs
  via `elsarticle-num`; parallels ESWA / EAAI).
- **`main_ieee.tex` (IEEEtran)** — security-branded backup: **IEEE TDSC** (two-column, `figure*`/`table*`).

See `notes/paper2_venue_decision_003.md` for the venue decision, guide compliance, and the length caveat.

## Regenerate the LaTeX from source
```bash
python -m src.analysis.make_paper2_latex_tables    # tables -> tables/ (Elsevier) and tables_ieee/ (IEEE)
python -m src.analysis.make_paper2_latex ieee      # manuscript/main_ieee.tex   (TNSM, primary)
python -m src.analysis.make_paper2_latex elsevier  # manuscript/main.tex        (fallback)
```
Compile IEEE with `latexmk -pdf main_ieee.tex` (needs `IEEEtran.cls`, standard in TeX Live/MiKTeX).
See `notes/paper2_venue_decision_002.md` for the venue decision and required submission statements.

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
