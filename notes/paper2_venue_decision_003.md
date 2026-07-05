# Venue decision (v3, final) — Knowledge-Based Systems

After reading the actual Aims & Scope + full Guide for Authors of four Q1 candidates, the decision is
**Knowledge-Based Systems (KBS, Elsevier)** as primary. Supersedes v2 (TNSM) and v1 (C&S, ruled out).

## Why KBS (verified against the guide, not just the scope blurb)
- **No scope exclusions that affect us.** Unlike Computers & Security (AI/ML moratorium -> hard veto) and
  Engineering Applications of AI (strict desk-reject gauntlet: metaphor-metaheuristics, mandatory
  AI/engineering split, no undefined acronyms in title/abstract), KBS has none of these.
- **Native fit for the paper's identity.** KBS's leading topics literally include "Machine learning theory,
  methodology and algorithms" and "Intelligent decision support systems, prediction/warning systems" -- which
  is exactly what this paper is (a decision-support method / retraining policy). KBS accepts methodology as a
  first-class contribution, resolving the one ESWA/EAAI risk (they lean "application").
- **Demonstrably publishes our topic:** KBS has recent concept-drift + IDS papers (Liu et al. 2021 active
  learning under concept drift; IGPC-MSOS concept drift in NIDS 2026).
- **Parallels / fallbacks:** ESWA and EAAI (applied-ML, equally viable), IEEE TDSC (security-branded backup,
  higher bar; uses IEEEtran = main_ieee.tex). C&S and TNSM ruled out.

## Guide-for-Authors compliance (checked)
- **Abstract <= 250 words** -> ours is 244. OK.
- **References: numbered [1], in order of appearance** -> `elsarticle-num` produces exactly this. OK.
- **Highlights: 3-5 x <= 85 chars** -> OK (manuscript/highlights.md). **Keywords 1-7** -> OK (6, KBS-aligned).
- **LaTeX:** Elsevier `elsarticle` -> `manuscript/main.tex` (regenerated with `\journal{Knowledge-Based Systems}`).
- **Required statements (added, templated, in main.tex tail):** CRediT, Declaration of competing interest,
  Funding, Data availability (Option C). **GenAI-use declaration** left as a TODO comment -- author's decision
  per publisher policy (must be a section before references if AI tools were used; AI must not be an author).
- **Research data Option C:** deposit the code artifact in a repository (Zenodo) and cite it (add DOI); the
  three benchmarks are already cited.
- **Single-anonymized (single-blind) review** -> author names appear; no anonymization needed.

## Soft caveat: length
KBS prefers **<= 20 double-spaced manuscript pages including tables and figures**. With ~6k words + 9 figures
+ 6 tables this may run over. Mitigation if page pressure arises at compile time: move secondary
figures/tables to an Appendix / supplementary material -- candidates: Fig 2b (pooled law), Fig 3 (oracle
regret), Fig 7 (label latency); Tables 4 (oracle regret) and 5 (Phase-1 negative). The core narrative (Figs
1, 2, 4, 5, 6, 8; Tables 1, 2, 3, 6) stands alone.

## Framing applied for KBS
- Foreground: an **intelligent decision-support method** (the validate-before-commit gate) + ML methodology
  for safe model updating under concept drift; the reframing thesis (degradation, not drift, governs value).
- Keywords shifted to KBS core: concept drift; intelligent decision support; safe model updating;
  label-efficient learning; machine learning; intrusion detection.
- Quantum kept backgrounded; security-robustness (adversarial-label fail-safe, latency) retained as strengths.

## Author to-do before submission
- Compile `main.tex` (elsarticle) and review the PDF and page count.
- Fill affiliation/co-authors/ORCID; complete CRediT; set funding; competing-interest statement.
- Deposit code on Zenodo, add the software DOI to Data availability + a software reference in `references.bib`.
- Fill the real Paper 1 reference (`fernandez_paper1`).
- Decide on the GenAI-use declaration.
- Cover letter for KBS (framed to "intelligent decision-support / ML methodology for safe adaptive detection").
