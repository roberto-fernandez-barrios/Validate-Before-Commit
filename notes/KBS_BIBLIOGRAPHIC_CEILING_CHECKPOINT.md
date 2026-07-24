# KBS BIBLIOGRAPHIC CEILING CHECKPOINT

## A. Baseline

- **Branch:** `editorial/kbs-bibliographic-ceiling` (from `main` @ `87137dd`, post v1.22.5).
- **Source version:** v1.22.5.
- **Reference count:** 73 `.bib` entries before → 84 after (+12 added, −1 Paper 1 removed).
- **Printed bibliography (main paper):** 67 references (`main.bbl`).
- **Pages:** main 25 → **26** (+1, from the added references + two compact Related-Work paragraphs; within the accepted "+1 page for bibliography" budget); supplement 35; IEEE 18.
- **Gates:** 136 pytest, 630/630 audit, 185/185 hashes (baseline 135/630/185; +1 test from the new guards).

## B. References added (all web-verified)

| Key | Verified authors | Venue | Year | Pages | DOI / source | Cited at |
|---|---|---|---|---|---|---|
| `sawade2012active` | Christoph Sawade, Niels Landwehr, Tobias Scheffer | NeurIPS 25 | 2012 | 1763–1771 | NeurIPS proc. + DBLP | Related Work (active comparison), Contributions |
| `kossen2021active` | Jannik Kossen, Sebastian Farquhar, Yarin Gal, Tom Rainforth | ICML, PMLR 139 | 2021 | 5753–5763 | proceedings.mlr.press/v139/kossen21a | Related Work, Contributions, Limitations |
| `karimi2021online` | Mohammad Reza Karimi, Nezihe Merve Gürel, Bojan Karlaš, Johannes Rausch, Ce Zhang, Andreas Krause | AISTATS, PMLR 130 | 2021 | 307–315 | proceedings.mlr.press/v130/reza-karimi21a | Related Work, Contributions |
| `han2024model` | Elise Han, Chengpiao Huang, Kaizheng Wang | ICML, PMLR 235 | 2024 | 17374–17392 | proceedings.mlr.press/v235/han24b | Related Work, Contributions |
| `okanovic2025models` | Patrik Okanovic, Andreas Kirsch, Jannes Kasper, Torsten Hoefler, Andreas Krause, Nezihe Merve Gürel | AISTATS, PMLR 258 | 2025 | 2035–2043 | proceedings.mlr.press/v258/okanovic25a | Related Work, Contributions |
| `zliobaite2015cost` | Indrė Žliobaitė, Marcin Budka, Frederic Stahl | Neurocomputing 150 | 2015 | 240–249 | Crossref 10.1016/j.neucom.2014.05.084 | Intro, Related Work |
| `mahadevan2024cost` | Ananth Mahadevan, Michael Mathioudakis | Knowledge-Based Systems 293 | 2024 | art. 111610 | Crossref 10.1016/j.knosys.2024.111610 | Intro, Related Work |
| `regol2025retrain` | Florence Regol, Leo Schwinn, Kyle Sprague, Mark Coates, Thomas Markovich | ICML, PMLR 267 | 2025 | 51369–51404 | proceedings.mlr.press/v267/regol25a | Intro, Related Work |
| `mcnemar1947note` | Quinn McNemar | Psychometrika 12(2) | 1947 | 153–157 | Crossref 10.1007/BF02295996 | §3.5 exact-McNemar gate |
| `holm1979simple` | Sture Holm | Scand. J. Statist. 6(2) | 1979 | 65–70 | JSTOR 4615733 (no DOI) | §7 multiplicity |
| `benjamini1995controlling` | Yoav Benjamini, Yosef Hochberg | JRSS-B 57(1) | 1995 | 289–300 | Crossref 10.1111/j.2517-6161.1995.tb02031.x | §7 multiplicity |
| `schuirmann1987comparison` | Donald J. Schuirmann | J. Pharmacokinet. Biopharm. 15(6) | 1987 | 657–680 | Crossref 10.1007/BF01068419 | §4 equivalence/TOST |

## C. Statistical references

- **McNemar 1947** — added, cited at the exact-McNemar gate (§3.5). ✓
- **Holm 1979** — added, cited where the Holm families/adjustments are described (§7). ✓
- **Benjamini–Hochberg 1995** — added, cited where BH is applied (§7). ✓
- **Schuirmann 1987 (TOST)** — added, cited where equivalence is defined by CI-inclusion / two one-sided tests (§4). ✓

## D. References NOT added (per the "do not auto-add" list)

- Katariya 2012, Nguyen 2018, Kossen 2022 (Active Surrogate Estimators), MANDOLINE 2021, You 2019, Contextual Active Model Selection, further active-learning surveys, further concept-drift/NIDS/QML — **none added**: no concrete claim in the edited text lacked support from the eight core references. No exception was needed.

## E. Textual integration

- **Introduction:** one sentence added ("Prior work has likewise framed model updating and retraining as cost–benefit decisions rather than automatic responses to detected change" + 3 cites). No new paragraph. Does not claim first-to-frame-updating-as-decision.
- **Related Work:** two compact paragraphs added — "Retraining as a decision" (Žliobaitė, Mahadevan, Regol) and "Active comparison and limited-label model selection" (Sawade, Kossen, Karimi, Han, Okanovic). The "unlike prior work" phrase in the existing when-to-retrain block was removed (novelty narrowed).
- **Contributions:** one lead sentence added positioning the work relative to active-testing / limited-label model-selection research (non-defensive). No new contribution.
- **Limitations:** one sentence added (balanced probes vs optimized active-testing acquisition; cites Kossen). No future-experiment promise.
- **Discussion:** unchanged.
- **Net main-body prose:** 10,607 → 10,833 words (**+226**, within the ≤350 target).

## F. Novelty alignment

- **Claims narrowed:** "unlike prior work" removed from the when-to-retrain block.
- **Scan result:** no "first to…", "for the first time", "no previous work", or "unlike all prior work" claims remain; the only "novel" is "novel attacks" (describing attacks, not the paper).
- **Retained novelty (combinatorial, defensible):** integrating candidate construction, evidence comparability, paired promotion validation, future-value analysis and chronological boundaries inside adaptive NIDS.
- **Guards:** `test_no_broad_priority_claims` (forbids broad priority phrasing; requires the twelve neighbour/statistical references to be cited); `test_paper1_reference_removed` (companion Paper 1 gone).

## G. Metadata quality

- Duplicate keys: none. Duplicate DOIs: none (56 DOIs, all unique).
- All 12 new keys cited in main and present in the final `main.bbl`.
- No `TODO`, no `et al.`, no tracking-parameter URLs, no invented pages, no omitted volumes in the new entries.
- Author special characters correct (Žliobaitė, Gürel, Karlaš).
- `zliobaite2015cost` is distinct from the pre-existing `zliobaite2011active` (no duplicate).

## H. Size impact

- References (`.bib`): 73 → 84 (net +11). Printed in main: ~67.
- Words (main body): 10,607 → 10,833 (+226).
- Pages: main 25 → 26; supplement 35 → 35; IEEE 18 → 18.
- Nine pre-existing uncited `.bib` entries (`chouchen2023intrusion`, `dimonda2024fewshot`, `qahtan2015pca`, `gretton2007kernel`, `yan2023kernel`, `kim2024quantum`, `hinder2024one`, `french1999catastrophic`, `zliobaite2011active`) are orphaned from the earlier focus cut; they appear in **no** compiled bibliography and were left as-is (harmless; not fundamental-reference removal).

## I. Gates

- pytest **136 passed**; audit **630/630**; hashes **185/185**.
- PDFs: main 26 pp, supplement 35 pp, IEEE 18 pp — **0 undefined refs/citations**.
- `results/raw/**`, `results/tables/MANIFEST.sha256`, `results/final_manifest.json`, all results and ATTENUATION unchanged; no seed touched; no experiment run; no background process.
- Working tree clean except the three excluded items.

## J. Answers to the ceiling audit

1. Active comparison covered? **PASS** (Sawade).
2. Active testing covered? **PASS** (Kossen).
3. Limited-label model selection covered? **PASS** (Karimi, Okanovic).
4. Temporal model selection covered? **PASS** (Han).
5. Cost-sensitive adaptation covered? **PASS** (Žliobaitė 2015).
6. Cost-aware retraining in KBS covered? **PASS** (Mahadevan, in-venue).
7. Modern when-to-retrain covered? **PASS** (Regol 2025).
8. Novelty delimited correctly? **PASS** (combinatorial novelty only; "unlike prior work" removed).
9. Candidate comparability still a defensible own contribution? **PASS** (the construction→comparability→validation decomposition and its controls are not in the cited neighbours).
10. McNemar cited? **PASS**.
11. Holm/BH cited where used? **PASS**.
12. Equivalence/TOST supported? **PASS** (Schuirmann).
13. Any author/volume/page/DOI error? **PASS** (all web-verified; no error).
14. Related Work defensive or redundant? **PASS** (two compact paragraphs; neutral tone; no "we do not claim novelty").
15. Any bibliographic gap that could produce a serious objection?
    - *Existing related work now covered:* active comparison/testing, limited-label & temporal model selection, cost-sensitive/-aware retraining, modern when-to-retrain, and the statistical sources.
    - *Material gap:* none identified capable of a serious novelty/positioning objection.
    - *Desirable future extension (not a gap):* optimized active-testing acquisition for the probe (noted in Limitations), and broader model-selection baselines — future work, not required citations.

## K. Verdict

**PRACTICAL BIBLIOGRAPHIC CEILING REACHED — READY FOR HUMAN REVIEW**

All neighbours capable of a serious novelty or positioning objection are now cited and correctly
positioned as prior work; the paper's defensible contribution is the combination inside adaptive
NIDS; every statistical procedure carries its original source; and no scientific result, seed,
margin, family, estimand or the registered ATTENUATION outcome changed.
