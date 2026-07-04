# Building the Elsevier (elsarticle) manuscript

`main.tex` is a compilable Elsevier `elsarticle` document generated from the Markdown source. It pulls in the
bibliography (`references.bib`), the six result tables (`tables/*.tex`), and the figures (`../docs/img/*.png`,
via `\graphicspath{{../}}`).

## Regenerate the LaTeX from source
```bash
python -m src.analysis.make_paper2_latex_tables   # sanitized tables -> manuscript/tables/
python -m src.analysis.make_paper2_latex          # manuscript/main.tex
```

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
