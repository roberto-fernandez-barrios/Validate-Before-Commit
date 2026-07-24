# KBS FINAL REFERENCE AUDIT

Every added reference verified against an official source (PMLR proceedings pages, NeurIPS
proceedings, DBLP, Crossref REST API). No BibTeX copied verbatim from external reports; author
names, pages, volumes and DOIs checked individually.

| Ref | Already present? | Key | Official source checked | DOI / pages | Metadata status | Scientific role | Action |
|---|---|---|---|---|---|---|---|
| R1 Sawade, Landwehr, Scheffer — Active Comparison of Prediction Models | No | `sawade2012active` | NeurIPS proceedings + DBLP | NeurIPS 25, pp 1763–1771 | verified (DBLP pages) | direct antecedent: baseline–challenger comparison under limited labels | added |
| R2 Kossen, Farquhar, Gal, Rainforth — Active Testing: Sample-Efficient Model Evaluation | No | `kossen2021active` | proceedings.mlr.press/v139/kossen21a | PMLR 139, pp 5753–5763 | verified (Rainforth spelling confirmed) | labels-for-evaluation vs labels-for-training | added |
| R3 Karimi, Gürel, Karlaš, Rausch, Zhang, Krause — Online Active Model Selection for Pre-trained Classifiers | No | `karimi2021online` | proceedings.mlr.press/v130/reza-karimi21a | PMLR 130, pp 307–315 | verified (Karlaš/Gürel/Rausch names corrected vs. prior report) | online limited-query selection among pre-trained models | added |
| R4 Han, Huang, Wang — Model Assessment and Selection under Temporal Distribution Shift | No | `han2024model` | proceedings.mlr.press/v235/han24b | PMLR 235, pp 17374–17392 | verified (full given names) | evaluation/selection under temporal shift; nearest neighbour to the framing | added |
| R5 Žliobaitė, Budka, Stahl — Towards cost-sensitive adaptation… | No (distinct from `zliobaite2011active`) | `zliobaite2015cost` | Crossref 10.1016/j.neucom.2014.05.084 | Neurocomputing 150, pp 240–249 | verified (three authors, Frederic Stahl) | updating as a cost/benefit decision | added |
| R6 Mahadevan, Mathioudakis — Cost-aware retraining for machine learning | No | `mahadevan2024cost` | Crossref 10.1016/j.knosys.2024.111610 | KBS 293, art. 111610 | verified | strategic in-venue (KBS) retraining-utility reference | added |
| R7 Okanovic, Kirsch, Kasper, Hoefler, Krause, Gürel — All models are wrong, some are useful… | No | `okanovic2025models` | proceedings.mlr.press/v258/okanovic25a | PMLR 258, pp 2035–2043 | verified (title capitalization + names) | recent limited-label deployment model selection | added |
| R8 Regol, Schwinn, Sprague, Coates, Markovich — When to retrain a machine learning model | No | `regol2025retrain` | proceedings.mlr.press/v267/regol25a | PMLR 267, pp 51369–51404 | verified (full author list) | modern when-to-retrain under uncertain shift/cost | added |
| McNemar 1947 — Note on the Sampling Error… | No | `mcnemar1947note` | Crossref 10.1007/BF02295996 | Psychometrika 12(2), pp 153–157 | verified | source for the exact-McNemar gate | added |
| Holm 1979 — A Simple Sequentially Rejective Multiple Test Procedure | No | `holm1979simple` | Scand. J. Statist. (JSTOR 4615733) | 6(2), pp 65–70 (no DOI) | verified (no Crossref DOI; canonical vol/pages) | source for Holm correction | added |
| Benjamini–Hochberg 1995 — Controlling the False Discovery Rate | No | `benjamini1995controlling` | Crossref 10.1111/j.2517-6161.1995.tb02031.x | JRSS-B 57(1), pp 289–300 | verified | source for BH correction | added |
| Schuirmann 1987 — TOST | No | `schuirmann1987comparison` | Crossref 10.1007/BF01068419 | J. Pharmacokinet. Biopharm. 15(6), pp 657–680 | verified | source for equivalence/TOST | added |

## Duplicate / collision checks

- Normalized-title, DOI, and author+year checks against the existing 73 entries: **no duplicates**.
- `zliobaite2011active` (2011 active learning for streams) ≠ `zliobaite2015cost` (2015 cost-sensitive adaptation): distinct works, both legitimately citable; the new entry does not duplicate.
- No DOI appears twice after the additions.

## Corrections applied vs. the prior external report

- R3: correct spellings **Bojan Karlaš, Johannes Rausch, Nezihe Merve Gürel** (not the garbled names in the earlier report).
- R2: author is **Tom Rainforth** (confirmed via the same group's NeurIPS 2022 record).
- R5: third author **Frederic Stahl**; volume 150; pp 240–249.
- No page numbers invented; Holm carries no DOI (JSTOR only), per the "URL/no-DOI only when none exists" rule.
