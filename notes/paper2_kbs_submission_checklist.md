# KBS submission checklist — Editorial Manager, step by step

Target: **Knowledge-Based Systems** (Elsevier, Editorial Manager). Complete section A first; B–D on
submission day. Corresponding author: Roberto Fernández-Barrios (roberto.fernandez.b@deusto.es).

## A) Before compiling (fill the TODOs)

- [x] **Paper 1 reference** — filled (2026-07-12): "Quantum and Classical Kernels under Distribution
      Shift: Kernel Geometry Governs Out-of-Distribution Robustness", Fernández-Barrios, Pastor-López,
      González-Santocildes, García Bringas; preprint, submitted to EPJ Quantum Technology.
      **Remaining sub-TODO:** insert the arXiv identifier in the bib `note` once the preprint is posted
      (KBS requires preprints to be marked and carry their identifier/DOI).
- [ ] **Zenodo deposit** — upload the code artifact (tag a release of the repo), get the DOI, then:
      - [ ] insert it in the `fernandezbarrios2026artifact` entry in `references.bib`;
      - [ ] insert it in the *Data availability* paragraph (search `TODO -- deposit on Zenodo` in
            `src/analysis/make_paper2_latex.py`, regenerate).
- [x] **Funding** — finalized (2026-07-12): no funding; the standard Elsevier no-grant sentence is in.
- [x] **Generative-AI declaration** — added (2026-07-12) as the required section before the references
      (standard Elsevier wording; tool named; authors take full responsibility). Mandatory in this case —
      the "nothing to disclose" path only covers grammar/spell-check-level tooling.
- [ ] **ORCID check** — Roberto's is set; confirm the other three authors' ORCIDs render correctly.
- [ ] **Reference proofread** — verify the 3–4 `confidence: medium` entries flagged in the
      `references.bib` header (Chouchen & Jemili 2023; EDDM 1970s-style workshop ref; few-shot NIDS 2024)
      against the publisher pages.
- [ ] **Prose pass in your own voice** — especially Introduction, Related Work, Discussion.

## B) Build + QA (local)

- [ ] Regenerate everything from source:
      `python -m src.analysis.make_paper2_latex_tables && python -m src.analysis.make_paper2_latex elsevier`
- [ ] **Claims audit** (must print 65/65): `python -m src.analysis.audit_paper2_claims`
- [ ] Compile clean: `cd manuscript && latexmk -C && latexmk -pdf main.tex`
      - [ ] zero `!` errors in `main.log`; citations/refs resolved (no "undefined").
- [ ] Visual pass on the PDF: title page (4 authors, ORCID icons, Deusto), abstract, highlights,
      graphical abstract, Figs 1–8 (+2b) legible, Tables 1–6 inside margins, Appendix A present,
      CRediT printed, statements present.
- [ ] Page count sanity vs. KBS's "preferably ≤ 20 double-spaced pages incl. tables+figures"
      (Appendix A already offloads Figs 2b/3/7 + Tables 4/5; move more to supplementary if needed).

## C) Files to prepare (Elsevier wants editable sources; PDF alone is not acceptable)

| # | File | Notes |
|---|---|---|
| 1 | Cover letter | from `notes/paper2_kbs_cover_letter.md` (fill affiliation/funding) |
| 2 | Manuscript source | `main.tex` + `references.bib` + `tables/*.tex` + `cas-sc.cls`, `cas-common.sty`, `cas-model2-names.bst`, `thumbnails/` |
| 3 | Figures | each as a **separate file**, logical names (`Figure_1.png` … from `docs/img/`), ≥300 dpi ✓ |
| 4 | Highlights | separate editable file, **"highlights" in the filename**, 3–5 bullets ≤85 chars (from `manuscript/highlights.md`) |
| 5 | Graphical abstract | separate file, `docs/img/graphical_abstract.png` (2030×840 ≥ 531×1328 min) |
| 6 | Title page | authors, affiliations, corresponding author + full contact details |
| 7 | Declaration of competing interests | generated with Elsevier's **declarations tool** → upload the .docx |
| 8 | (Optional) Supplementary | `REPRODUCE.md` / extended tables if page pressure |

## D) Editorial Manager steps

1. Log in / register at KBS's Editorial Manager with the Deusto email; select **Original research paper**.
2. Enter metadata: title, abstract (244 words), **1–7 keywords** (ours: 6), all four authors **in order**
   with affiliations + ORCIDs (order cannot change after acceptance).
3. Upload files in the order of section C; EM builds the review PDF — **check the built PDF carefully**
   (fonts, figures, tables) before approving.
4. Complete the questionnaires: competing interests (declarations tool), **funding**, **data availability**
   (Option C — link the Zenodo DOI), GenAI declaration as applicable.
5. (Optional) Suggest 3–5 reviewers (concept-drift / adaptive-IDS / streaming-ML authors; no recent
   co-authors or Deusto colleagues) and opposed reviewers if any.
6. (Optional) SSRN free preprint posting offer at submission — decide (does not affect review).
7. Approve the PDF → **Submit**. Save the manuscript number.

## E) After submitting

- [ ] Archive the exact submitted bundle (tag the repo: `git tag kbs-submission-v1 && git push --tags`).
- [ ] Note the manuscript number + submission date in `notes/`.
- [ ] If desk-transfer is offered (Article Transfer Service) after a reject, our own fallback ladder is:
      **EAAI → ESWA → TDSC (IEEEtran build ready) → JISA** (see `notes/paper2_venue_decision_003.md`).
