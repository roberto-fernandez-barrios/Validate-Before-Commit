# IJIS submission checklist — International Journal of Information Security (Springer Nature)

Local working document (gitignored). Source of requirements: `guide/Submission guidelines _
International Journal of Information Security _ Springer Nature Link.pdf` and `guide/Journal
policies _ Springer.pdf` (both saved 2026-09-01). Nothing below has been submitted.

## 0. Regenerate everything (from the repository root)
```bash
python -m src.analysis.port_springer                 # main_springer.tex, tables_springer/, supplement_springer.tex
cd manuscript
pdflatex main_springer && bibtex main_springer && pdflatex main_springer && pdflatex main_springer
pdflatex supplement_springer && bibtex supplement_springer && pdflatex supplement_springer && pdflatex supplement_springer
cd ..
python -m src.analysis.make_ijis_submission_bundle   # -> dist/submission_ijis/
```
Expected: main_springer.pdf 28 pp., supplement_springer.pdf (= ESM_1.pdf) 48 pp., 0 undefined
references/citations in both logs (the bundle script refuses otherwise).
For byte-identical PDFs across rebuilds, export `SOURCE_DATE_EPOCH=1756684800 FORCE_SOURCE_DATE=1`
before the pdflatex passes (pdfTeX then fixes the embedded dates and trailer ID); the zip inside the
bundle is already deterministic.

## 1. Files to upload (all in `dist/submission_ijis/`)
| Upload slot | File | Notes |
|---|---|---|
| Manuscript (PDF) | `main_springer.pdf` | svjour3 `twocolumn`, as the guidelines require |
| Source files | `latex_source.zip` | tex + cls/clo/bst + bib + bbl + tables + figures; "failing to submit a complete set of editable source files will result in your article not being considered for review" |
| Supplementary Information | `ESM_1.pdf` | caption to enter: *Online Resource 1 — Supplementary Material: exploratory study, registered protocols, complete result matrices, proofs, label ledger and robustness analyses (PDF)* |
| Cover letter | `cover_letter.md` | paste as text |

## 2. Metadata to enter in the submission system
- Title: *Candidate Comparability Before Promotion: Conditional Validation in Adaptive Network Intrusion Detection*
- Article type: original research article.
- Abstract: paste from `main_springer.tex` (233 words; limit 150–250; no undefined abbreviations).
- Keywords (4–6 required; 6 provided): distribution drift; candidate comparability; risk-aware
  model updating; adaptive model updating; machine learning; intrusion detection.
- Authors, in order, with affiliation *Faculty of Engineering, University of Deusto, Avda. de las
  Universidades 24, 48007 Bilbao, Spain* and ORCIDs (see `author_metadata.md`):
  Roberto Fernández-Barrios (corresponding, roberto.fernandez.b@deusto.es), Iker Pastor-López,
  Amaia Pikatza-Huerga, Pablo García Bringas.
- Corresponding author must use the institutional e-mail (also required for the Deusto/CRUE APC).
- Declarations entered **in the interface** (IJIS: "Author Contribution information and Competing
  Interest information must be provided at submission via the submission interface"): texts in
  `declarations.md` — Funding (none), Competing interests (none), Ethics approval (not applicable),
  Data availability, Code availability, Author contributions (CRediT), Generative-AI use.
- Reviewer suggestions: optional; to be selected manually with conflict-of-interest screening
  before submission (independent, different countries/institutions, institutional e-mails; never
  co-authors or collaborators). **PENDING — none selected.**

## 3. Compliance already built into the port (verify once in the PDF)
- [x] Springer LaTeX macro package (svjour3) with `twocolumn`; source + PDF supplied.
- [x] Title page: title, authors, affiliation, corresponding e-mail, ORCIDs.
- [x] Abstract 150–250 words; 4–6 keywords.
- [x] Decimal headings, ≤3 levels; footnotes not endnotes (the manuscript has none).
- [x] References numbered in square brackets, consecutive; DOIs as full `https://doi.org/` links
      (spmpsci + `\doi` override); only cited, published works (+ the Zenodo data citation, as the
      research-data policy recommends).
- [x] Tables and figures numbered in Arabic, cited in order, captions in the text file, figures
      inside the body (vector PDF).
- [x] "Statements and Declarations" section before the references: Funding, Competing interests,
      Ethics approval, Data availability, Code availability, Author contributions, Generative-AI use.
- [x] Supplement cited as "Online Resource 1" throughout (body and captions); ESM front page with
      article title, journal name, authors, affiliation and corresponding e-mail.
- [x] Single-blind: no anonymisation; repository/DOI links stay.
- [x] LLM use documented in the manuscript (Springer AI policy).

## 4. Left as-is on purpose (production retypesets; change only if Roberto wants)
- Figure captions end with a period (Springer house style omits it) — cosmetic, fixed at typesetting.
- Figure files are not renamed `Fig1.eps` etc.; the LaTeX source references `docs/img/*.pdf`, which is
  acceptable for LaTeX submissions.
- `main.tex` first-line comment still names the original Elsevier target (comment only, no effect).
- The inherited keyword "intelligent decision support" was replaced one-for-one by "candidate
  comparability" in the canonical `main.tex` keyword block (editorial metadata only; the ports were
  regenerated from it).

## 5. Open access / APC
- IJIS is fully OA since 1 Jan 2026: APC £2,690 / US$3,690 / €2,990 (+VAT) on acceptance; licence CC BY.
- Cost is not a constraint (Roberto, 2026-09-01). Still worth claiming: Deusto holds 16 Springer
  Nature APCs for 2026 under the CRUE–Springer agreement (first-come; flipped journals eligible in
  2026) — e-mail dit.transferencia@deusto.es with the manuscript details once submitted.

## 6. After clicking submit
- Record the manuscript ID and date in `audits/post_kbs_target_venue_plan.md` and in memory.
- No other submission of this work anywhere while IJIS is reviewing it (journal policy).
