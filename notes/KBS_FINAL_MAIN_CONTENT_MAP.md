# KBS FINAL MAIN CONTENT MAP

Every main-paper subsection, table and figure, its role, and its disposition in the focus cut.
Classification: **P**rimary / **B**oundary / **S**econdary / **H**istorical.

| Element | Scientific role | Class | Necessary in main? | Action | Destination |
|---|---|---|---|---|---|
| §1 Introduction | States the thesis (alarm ≠ superiority; construction precedes validation; validation conditional) | P | Yes | KEEP; strip later re-statements | main |
| §2 Related work (4 blocks) | Positions vs drift/detection, promotion, evaluation bias | P | Yes | KEEP; quantum → 1 short para | main |
| §3.1 Promotion as sequential decision | Defines the two decisions | P | Yes | KEEP | main |
| Fig. 1 decision pipeline | The decomposition figure | P | Yes | KEEP | main |
| §3.2 Drift monitors | Defines detectors incl. quantum | P/S | Yes | KEEP compact | main |
| §3.3 Progressive-drift protocol | Stream construction | P | Yes | KEEP compact | main |
| §3.4 Validate-before-commit gate (Alg 1A/1B) | Defines point/strict/observed gates | P | Yes | KEEP | main |
| §3.4 cost-sensitive reading | ε* derivation | S | Partly | KEEP (already compact) | main |
| §3.5 Risk-controlled gates + VBC-SG + Prop 1 | Formal option | S | Compact only | COMPRESS; move extended derivation/variants | main (compact) + Supp |
| §3.6 Self-contained pipeline method | Construction control 1 method | P | Yes | KEEP | main |
| §3.7 Size-matched control method | Construction control 2 method | P | Yes | KEEP | main |
| §3.8 Promotion policies / outcomes / inference | Estimands, endpoints | P | Yes | KEEP | main |
| §4 "Six tiers of evidence" para | Epistemic taxonomy narrative | H | No | REMOVE → single para | Supp S0 |
| §5.1 Preprocessing ownership + Table 2 + guardrails Table 3 | Primary mechanism 1 | P | Yes | KEEP; remove discovery narration | main |
| §5.2 Candidate evidence size + Table 4 | Primary mechanism 2 | P | Yes | KEEP; conclusion-first; ATTENUATION not the headline | main |
| §5.3 Conditional validation + Table 5 | Primary conditional effect | P | Yes | KEEP; drop frozen-policy history | main |
| §5.4 Chronological boundary + Table 6 | External boundary | B | Yes | KEEP | main |
| §5.5 Mechanism/formal/operational (4,111 w, 8 tables) | Secondary evidence | S | Compress hard | COMPRESS → 4 paras + 1 compact table | main (≤2 pp) |
| — per-trigger mechanism + Fig. 2 | Degradation/headroom | S(support of P) | Yes | KEEP as §5.5 Para A | main |
| — Table policy_frontier (downstream/generators) | Robustness | S | No | MOVE | Supp |
| — Table causal_probe (observed-data) | Feasibility | S | No | MOVE | Supp |
| — Table harm_generality (mild drift) | Robustness | S | No | MOVE | Supp |
| — Table zero_drift (frozen zero-drift) | Robustness/historical | S/H | No | MOVE | Supp |
| — Table ab_equivalence (A/B ownership) | Mechanism support | S | No | MOVE | Supp |
| — Table amendment009 (classifier/generator) | Robustness | S | No | MOVE | Supp |
| — Table budget_frontier (VBC-SG frontier) | Formal cost | S | No | MOVE | Supp |
| — Table operational_e2e (acquisition yield) | Operational | S | No | MOVE | Supp |
| NEW compact evidence-map table (≤6 rows, +Scope col) | Secondary at a glance | S | Yes | ADD | main |
| §6 Discussion (Q1–Q4, 1,077 w) | Synthesis | P | Yes | COMPRESS −20–30% | main |
| §6 conditional operating policy (5 steps) | Operational implication | B | Yes | KEEP as implication (not "validated policy") | main |
| §7 Limitations (1,093 w) | Scope | B | Yes | CONSOLIDATE → 5 blocks | main |
| §8 Conclusion (249 w) | Close | P | Yes | KEEP/slightly trim; substantive before ATTENUATION | main |

## Primary blocks (must remain central)
1. Candidate-governance decomposition (§3.1, Fig. 1).
2. Preprocessing ownership (§5.1).
3. Candidate-size control (§5.2).
4. Conditional validation (§5.3).
5. Chronological external boundary (§5.4).

## Historical content leaving the main body
Six-tier taxonomy narrative; harness v1/v2 chronology; amendment numbering; final-q1 markers;
`(i$'/(i$''` tier labels; pristine-seed narration; discovery-of-the-problem storytelling;
prior-erroneous-interpretation forensics. One methodological sentence remains in §4 stating the
controls were sequential and each registered before its own seeds. Full taxonomy + provenance →
Supplement **S0. Evidence hierarchy and provenance**.
