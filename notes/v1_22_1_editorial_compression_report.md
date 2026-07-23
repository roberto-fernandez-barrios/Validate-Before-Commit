# v1.22.1 Editorial Compression Report

Scope: the evidence–validation trade-off table had to replace material, not accumulate
(protocol §5). All numbers below verified on the final build of this branch.

## Page budgets

| document | v1.22.0 | v1.22.1 | budget |
|---|---|---|---|
| main.pdf | 33 pp | **33 pp** | ≤ 33 (target 32–33) |
| supplement.pdf | 29 pp | **30 pp** | may grow moderately |
| main_ieee.pdf | 25 pp | **25 pp** | ≤ 25 |

0 undefined references / 0 undefined citations in all three PDFs.

## Word budgets

Measured with one consistent method (regex-stripped LaTeX, `\section{Introduction}` →
`Declaration of competing interest`; script in the session scratchpad), applied to both
the v1.22.0 baseline source and the v1.22.1 source:

| quantity | v1.22.0 (same method) | v1.22.1 | budget |
|---|---|---|---|
| abstract | 219–230 (recorded) | **234** | 210–235 |
| body | 17,889 | **17,742** (−147) | ≤ v1.22.0 level (recorded 18,088 under the prior method) |

The body shrank under the identical method, so the ≤ 18,088 recorded budget is met under
any consistent counting convention.

## Material moved to the supplement

- **Decision-quality of the lp32 gate** (per-trigger operating point, regret ratios,
  precision/recall, horizon stability) — main §5.5 paragraph → new Supplementary §S2.10;
  a two-sentence summary with the 22×/5-fold regret reductions and the 23% harmful-commit
  fraction stays in main.
- **Historical frozen-policy diagnostic table** (`table_v2_confirmatory`) — main §5.1 →
  new Supplementary §S2.11 (with framing paragraph); main §5.1 keeps the full compact
  summary of its essential effects (§5.5 quotes the key cells: ToN −1.64 → +0.79,
  +2.43 [1.53, 3.43] vs naive; PortScan/UNSW preserved; QK-ZZ invariance). All six
  in-text references updated; caption renamed "Historical frozen-policy diagnostic".

## Material condensed (no numbers changed; prose CIs that were dropped remain in the
referenced tables, supplement sections or sealed artifact CSVs)

- §5.1 genealogy/roadmap sentences; six-tiers block trimmed.
- ATTENUATION block (§5.3): duplicate formal-vs-substantive sentence removed;
  "formal ELIMINATION" phrasing retired.
- VBC-SG: §3.5 assembly framed as "a sequential decision-support instantiation for
  settings in which validation is chosen"; §5.6 layer-cost and budget-frontier
  paragraphs compressed; risk-axis paragraph compressed (details already in S2.9).
- Future-negative signs (§5.2), classifier sweep, cumulative-generator controls,
  zero-drift control (iii), harm-generality CIs (in `tab:harm_generality`),
  hierarchical-model and mechanism-test prose CIs, observed-data iteration history
  (in S2.7), chronological replays intro, acquisition-yield intro, v1-summary,
  Limitations (A/B numbers already in `tab:ab_equivalence`), two-stage and robustness
  envelope details (S2.2/S2.4).

## Material added

- Evidence–validation trade-off table + interpretation paragraph (§5.3).
- Margin-sensitivity sentences (±0.2/±0.5/±1.0; PortScan margin-sensitive).
- Zero-drift scope qualifiers, nominal-parity terminology and caveats, corrected
  Data Availability block, updated highlights and graphical abstract.

## Confirmation

- No scientific figure, CI, seed, protocol, family, margin or outcome changed; edits are
  presentational (scope wording, relocation, condensation) plus the two derived tables
  built exclusively from sealed v1.22.0 outputs.
- pytest 135/135; audit 625/625; verify-hashes 183/183 pinned CSVs intact
  (2 deliberately unpinned editorial extras); 21/21 and 42/42 arm counts unchanged;
  `results/raw/` untouched.
