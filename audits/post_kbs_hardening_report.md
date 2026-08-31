# Post-KBS hardening report — branch `post-kbs-hardening`

Baseline: commit `57ef8e704436034cbf1eb71cc320e5d373134100` (main). Input: the hostile audit
`audits/post_kbs_hostile_referee_57ef8e7.md`, treated as a list of allegations to verify, not
as authoritative truth. Scope: Phase A of the hardening plan — textual, artifact, provenance
and presentation fixes only. **No experiment was run, no confirmatory seed was executed, no
sealed CSV byte was modified, no frozen protocol/preregistration note was edited.**

Validation state at the end of Phase A: `pytest` 169 passed (152 pre-existing + 17
new/updated guards), `audit_paper2_claims` 631/631, `verify_results_manifest` 185/185 with 0
unpinned extras, all three PDFs compile with zero undefined references/citations, and every
numeric token that left `main.tex` is accounted for (see §4).

---

## 1. Allegation-by-allegation verification

Legend: V = VERIFIED, PV = PARTLY VERIFIED, NV = NOT VERIFIED.

| # | Hostile-audit allegation | Verdict | Evidence found | Correction made | Interpretation changed? |
|---|---|---|---|---|---|
| R-1a | Zero-drift size-matched control is a null-by-construction (2,000/class own-pipeline challenger ≈ exchangeable re-draw of the incumbent) | **V** | `run_paper2_readaptation_v2.py`: incumbent drawn by `sample_balanced_from_distribution(role["train"], 2000, sev=0)`; candidate by the same sampler on `env.train_pools` at sev 0 (`nested_candidate_draw`) | §4.2.2 now states the exchangeability property in advance and says near-zero mean effects are the *expected* outcome of a correct implementation; §5.2 title and abstract/intro switched from "explains" to "accounts for … in the evaluated pool-based control" | Yes — claim strength reduced to what the design supports |
| R-1b | Preregistered ELIMINATION criterion E3 (sign-rate ≥ 0.4) unreachable under the very hypothesis it was meant to detect | **V** | `make_size_matched_own_transformer_001.py:385-396`; `size_matched_confirmatory_preflight.md:20`; sign rate ≈ 0.5 expected under exchangeability | §5.2 ATTENUATION paragraph now says the sign-rate rule is "structurally unable to certify elimination in exactly the situation it was registered to detect"; label kept mechanically, explicitly "not evidence of directional residual harm". P/A/E rules untouched; outcome remains ATTENUATION | Yes — the label is now explicitly a property of the frozen rule |
| R-2 | "Historical convention" (frozen incumbent-owned preprocessing) never shown to exist outside the authors' harness | **V** | No citation in `references.bib`/related work supports prevalence; all six "convention" occurrences refer to this program's harness | All "convention" wording replaced by "historical configuration"/"policy"; new §4.2.1 sentence: "we do not claim that frozen incumbent-owned preprocessing is a standard or widespread policy in published adaptive NIDS"; contribution reframed as an evaluation lesson | Yes — prevalence implication removed |
| R-3a | 144/185 manifest-pinned CSVs absent from the repository (gitignored) | **V** — and worse: the 41 *tracked* CSVs had LF blobs vs CRLF manifest hashes (`git ls-files --eol`: `i/lf w/crlf`), so a fresh clone failed `verify-hashes` for **all 185** | `.gitattributes`: `results/tables/** -text`; `.gitignore` narrowed to `!results/tables/**/*.csv` (+ verdict JSONs + ledger); all 185 pinned CSVs tracked; blobs renormalized to worktree bytes; staged-blob SHA-256 = manifest for 185/185; worktree bytes untouched (185/185 still match) | No scientific claim changed; artifact claims now true |
| R-3b | Zenodo v1.22.0 deposit has the same gaps | **V** (deposit zip listed: same 41 + manifest) | Cannot update Zenodo (out of scope, forbidden). README/REPRODUCE now state exactly what a fresh clone can do; Data Availability (which describes the deposit) untouched | No |
| R-3c | Protocol freeze commit SHAs (`114513f…`, `8838566`, `96576bb`, `0d280a5e…`, +) unresolvable in published history | **V** — 38 commit-context references across 20 files, 0 resolvable; no dangling objects (`git fsck` clean); full forms also unresolvable | `audits/protocol_commit_reachability.csv` (machine-readable, 38 rows); REPRODUCE.md and `docs/SCIENTIFIC_PROVENANCE.md` now say the identifiers predate repository curation and are not resolvable, and that the verifiable ordering evidence is this repository's own commit chronology. **No SHA fabricated or replaced; frozen notes/configs/sealed JSONs untouched** | Provenance claim weakened to what is verifiable |
| M3a | §5.6 "first stable pattern" false by the table's own numbers (ATC +0.40, DoC +1.16, ensemble +0.56 convert harm without target labels) | **V** | `phase2h`/`frontier.csv` | Paragraph rewritten: h′-vs-h rules convert harm *while preserving the benefit regime*; "label-free rules are not uniformly harmful" with the three counter-examples stated | Yes — false universal removed |
| M3b | DoC beats the point gate in the harm regime on the same harness; supplement S1.5 "only gate on the Pareto front" false | **V** (+1.16 vs +0.93) | §5.6 now states the DoC and ensemble wins explicitly ("no evaluated policy dominates … not global superiority"); S1.5 Pareto sentence replaced with the none-dominates formulation | Yes |
| M3c | Block II "Anytime-valid CS, b=64" is the superseded 4-look Bonferroni probe mislabeled as a confidence sequence | **V** (`amendment_008` §E arm `rz_seqav64`; S2.9 calls it subsumed) | Row relabeled "Sequential probe (4-look Bonferroni), b≤64" with guarantee "per-proposal (4 pre-declared looks; superseded by EB-CS, S2.9)" in the full matrix | Yes — superseded status disclosed |
| M3d | Strong external baselines only on exploratory v1; nothing external under the final harness | **V** | §5.6 now states both facts verbatim ("no external method has yet been evaluated under the final self-contained, size-matched harness"); Phase B experiment 1 designed to close it | Scope made explicit |
| M4/A4 | 32-row table at ~6 pt with 278-word caption; cross-block pseudo-ranking visually invited | **V** (rendered page inspected) | Main body now carries a 12-row compact table (paired v2 panel + clearly-separated exploratory ATC/DoC panel, origin column, ~130-word caption, `\footnotesize`, no `\resizebox`); the full 32-row matrix moved to Supplementary S2.12 as `table_baselines_full.tex` with origin tags on every row and evidence tiers in every block header. Nothing deleted — relocated | No numbers changed |
| M5a | Supplement `table_zero_drift` caption asserts the opposite of §5.2 without the frozen qualifier | **V** | Caption now scoped to "under this arm's frozen incumbent-owned transformer", labeled a frozen-policy result, with an explicit pointer that it must not be read as contradicting §5.2 (both `tables/` and `tables_ieee/`) | Yes — contradiction removed |
| M5b | S1.4 title "resolves the problem"; S1.6 "empirical safety property"; REPRODUCE "equivalent to zero" / "solves it"; README "Results at a glance"/"Key findings 3" unlabeled frozen-config headlines; `table_symmetric_security` cites nonexistent "Appendix A" | **V** (all five) | S1.4 → "the initial-study result"; S1.6 → "empirical harm-avoidance pattern — an observation … not a certified property"; REPRODUCE wordings fixed; README heading and finding 3 now carry "historical frozen-transformer configuration"; caption now cites "registered protocol, Appendix A, in the artifact" | Yes (supplement/README claims re-scoped) |
| M6a | VBC-SG forfeits ~96–100 % of recovery on CICIDS chronological streams; main text says only "abstains more" | **V** (recomputed from sealed `chronological_replays.csv`: retention 0–9 % on the five CICIDS replays at ≤1 commit and up to ~444 labels/stream; 91 %/129 % on UNSW at 1,232/1,634 labels; point/strict retain 73–100 %, 48 % for strict on Thu intra-day) | §5.4 now quantifies the "price of that conservatism" with those numbers; Discussion Q3 says VBC-SG "abstains almost entirely — retaining 0–9 % …"; framed as the operational price of the guarantee. No new experiment — derived from the sealed CSV | Yes — cost now explicit |
| M6b | VBC-SG narrative footprint vs "tertiary" label | **PV** | Footprint reduced incidentally (Block IV out of the main body); repository name is out of editorial scope | Partially addressed |
| M7a | Registered chronological family (strict vs never) structurally unfalsifiable on collapsed streams | **V** (family in `final_q1/multiplicity.csv`; +11.5…+28.8 vs collapsed baselines) | Family untouched (frozen); §5.4 and Supplement S6 now state it is "structurally easy to satisfy wherever the incumbent collapses", confining its confirmatory content to healthy-incumbent replays; interpretive role downgraded, not erased | Yes — interpretive role downgraded |
| M7b | ToN-IoT (harm benchmark) has no chronological counterpart | **V** (no timestamps) | §7 External validity now states it and classifies the chronological tier as boundary evidence, not a replication of the ToN harm phenomenon | Yes — scope sharpened |
| M8 | Readability metrics (50 paragraphs > 120 words; caveat repetition; abstract jargon) | **PV** (measured: 50 paragraphs > 120 w, "frozen"×53, "nominal"×33, caveat list ×5; verified) | Abstract de-jargonized ("PortScan boundary-close" → plain language) and kept ≤ 250 audit words; §5.3 dual-seed ambiguity resolved; four long paragraphs split; §5.6 completely restructured; caveat-list de-duplication limited — the §5.2 canonical list and its guard-pinned copies were kept because guard tests pin them and the science requires them | No |
| M9a | §5.3 quotes two seed sets for the same contrast without saying so | **V** | Both quote sites now name their runs and seed blocks (3001–3030 vs 4001–4030) and say the numbers are "close but not identical … from two registered runs" | No numbers changed |
| M9b | Percentile CI can exclude 0 while the centered-bootstrap p > 0.05 (ToN point₂₀₀₀ [0.00, 0.04], p=0.10) | **V** (CSV) | Not text-fixed in this pass (the table already prints both; the §4.4/S6 method text already distinguishes the procedures). Recorded here as a residual minor | No |
| M10 | Wall-clock ratios presented with a causal "because"; n=1 whole-arm timings dominated by fixed cost; own-faster-than-frozen physically implausible as a speedup | **V** (`pipeline_arm_wallclock_summary.csv`: never-arms ≈ 43 s of each 105–180 s arm; ToN own/frozen 0.89) | Causal "because" removed; paragraph now says the timings "do not isolate preprocessing overhead", that faster own-arms are "run-to-run noise, not a speedup caused by self-contained preprocessing"; 114× kept separate; ratios kept as labeled rough context (guard tests pin them) | Yes — causal reading removed |
| Minor: S1.1 cites S1.7 for downstream-dependence | **V** | Fixed to S1.6 | No |
| Minor: abstract "All results reproduce from a public artifact" | **PV** | Now true at the repository level after A12 (all sealed confirmatory CSVs ship; raw regeneration still needs public datasets, which Data Availability states). Left as is | No |
| Minor: Table 9 row count 32 vs report's 31; mixed label units; cryptic highlight bullet | **V/PV** | Units stated in full-matrix caption; highlight bullets left (85-char limit, guard-pinned); row-count discrepancy moot after restructure | No |
| Hostile verdicts A ("hard to read") / B ("no SoTA comparison") PARTIALLY JUSTIFIED | **Accepted** | — | Addressed via M8 and M3/M4 fixes; residual density is guard-pinned scope qualification | — |

## 2. Corrections NOT made (deliberately)

- The registered P/A/E outcome rules, the frozen protocols, preregistration notes, configs,
  sealed CSVs and `CLAIM_INTERPRETATION.json` files: untouched (bytes verified).
- ATTENUATION was **not** relabeled ELIMINATION.
- No unresolvable SHA was replaced or invented; the frozen notes keep their recorded values.
- Zenodo, tags, releases: untouched (out of scope).
- The manuscript's Data Availability section still describes the v1.22.0 deposit accurately.

## 3. Files changed (Phase A)

- `manuscript/main.tex`, `manuscript/main_ieee.tex` (regenerated by `port_ieee`),
  `manuscript/supplement.tex`
- `manuscript/tables/table_baselines_full.tex` (new; relocated full matrix),
  `manuscript/tables{,_ieee}/table_zero_drift.tex`, `…/table_symmetric_security.tex`
- `README.md`, `REPRODUCE.md`, `docs/SCIENTIFIC_PROVENANCE.md`
- `.gitattributes`, `.gitignore`
- `results/tables/**` (144 pinned CSVs newly tracked; 41 blobs renormalized to the sealed
  bytes; **zero worktree bytes changed** — verified by re-hashing all 185 against the
  manifest before and after), `results/final_experiment_ledger.csv` (now tracked)
- `tests/test_kbs_revision_guards.py` (adapted to the new table layout; compact-core test
  added), `tests/test_claims.py` (supplement table set), new
  `tests/test_post_kbs_hardening_guards.py` (13 guards)
- `audits/protocol_commit_reachability.csv` (new), this report, and the hostile audit
  `audits/post_kbs_hostile_referee_57ef8e7.md` (preserved as received)

## 4. Numeric accounting (required by A15)

Token-multiset diff of `manuscript/main.tex` vs `57ef8e7`:

- **Every removed numeric token** belongs to the old in-body Table 9 (cells, seed ranges and
  block headers), which moved verbatim into `manuscript/tables/table_baselines_full.tex`;
  guard tests re-verify every relocated cell against its sealed CSV. No number left the
  project.
- **Added tokens**: (i) VBC-SG chronological retention/label figures (+14.78, +35.29,
  +36.07, +6.47, +0.88, +0.16, +0.91, +1.56, +0.56, 444, 1,232, 1,634, 0–9 %, 73–100 %,
  48 %, 91 %, 129 %) — all derived from the sealed `paper2_final_q1/chronological_replays.csv`;
  (ii) +1.72/+1.35/+1.16/+0.93 in the §5.6 patterns paragraph — from
  `frontier.csv`/`phase2h` sealed CSVs; (iii) seed-block labels 3001–3030/4001–4030 in §5.3.
- Abstract: 216 → ~242 audit-counted words (limit 250).

## 5. Unresolved blockers / residual risks

1. **Zenodo deposits (v1.22.0 cited, v1.22.9 latest) still lack the 144 CSVs** — fixing
   requires a new authorized release, which is forbidden in this phase.
2. **Development-history SHAs remain unverifiable** — documented, not fixable without the
   pre-curation history.
3. External baselines still absent from the final harness, and the size-matched control
   still zero-drift-only — Phase B protocols address both; no text now overclaims either.
4. Minor: the percentile-CI-vs-bootstrap-p display mismatch (M9b) remains a presentational
   quirk; both quantities are correctly labeled where they appear.
