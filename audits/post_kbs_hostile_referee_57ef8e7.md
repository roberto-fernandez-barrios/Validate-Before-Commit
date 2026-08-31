# Hostile referee report — post-KBS revision, commit `57ef8e7`

Manuscript: *Candidate Comparability Before Promotion: Conditional Validation in Adaptive Network Intrusion Detection*
Repository: `roberto-fernandez-barrios/Validate-Before-Commit`, audit commit `57ef8e704436034cbf1eb71cc320e5d373134100` (`main`, working tree clean at start).
Date: 2026-08-31. Mode: read-only adversarial review. Nothing was edited, committed or pushed; this file is the only output.

Evidence base (all read directly, not via commit messages or the authors' audit files): `manuscript/main.tex` (608 lines, full), `manuscript/supplement.tex` (627 lines, full), all 16 `manuscript/tables/*.tex` referenced from the main text and the eight relocated supplement tables, `README.md`, `REPRODUCE.md`, `docs/SCIENTIFIC_PROVENANCE.md`, `manuscript/highlights.md`, the sealed CSVs under `results/tables/` (tracked and local-only), the two `CLAIM_INTERPRETATION.json` verdict files, the protocol/preflight/rewrite notes for both controls with their git chronology, `src/experiments/run_paper2_readaptation_v2.py` (sampling and nested-draw code), `src/analysis/make_size_matched_own_transformer_001.py` (E3 rule), `src/analysis/make_kbs_revision_runtime_summary.py` + `audits/pipeline_arm_wallclock_summary.csv`, `tests/test_kbs_revision_guards.py` (run), `verify_results_manifest` (run), the locally compiled post-revision `manuscript/main.pdf` (29 pp; page 21 rendered to image), and the archived Zenodo deposits (record 21517899 = v1.22.0, the DOI the manuscript cites; the 2.4 MB zip was downloaded and listed). The authors' `audits/kbs_rejection_revision_report.md` and `kbs_response_to_reviewers.md` were read last and treated as assertions; where they make checkable claims (zero numeric tokens removed; 152 tests; 185 hashes) I re-verified them independently.

---

## 1. Executive verdict

**MAJOR REVISION** — with a material probability of outright **REJECT** at a strong Q1 venue on *novelty/significance* grounds rather than on the two criticisms that sank it at KBS.

The revision is honest, internally consistent and numerically verifiable to an unusual degree. It fixes the *form* of Reviewer #1's complaints. It does not fix the two things a stronger reviewer will attack next: (i) the paper's "decisive" primary result is a null that holds essentially by construction, and its other primary result corrects an evaluation convention that the paper never shows anyone outside the authors' own harness uses; (ii) the new "comparison with strong baselines" is a descriptive collage across five harness generations in which the genuinely external baselines were never run on the harness the paper itself trusts.

---

## 2. Can Reviewer #1 still legitimately write…

### A. "The paper is not well-written and hard to read." — **PARTIALLY JUSTIFIED**

The complaint has changed nature, not disappeared. The previous version was hard to read because claims and caveats were interleaved; this version is hard to read because it is *over-qualified and long*. Measured on `main.tex` at `57ef8e7`:

| Measure | Value |
|---|---|
| Abstract | 232 words; contains "PortScan is boundary-close" — a dataset-specific caveat a first-time reader cannot decode from the abstract |
| Introduction | 39 sentences, median 29 words, 7 sentences > 40 words, longest 82 words; 21 parentheticals; 13 em-dash asides |
| Paragraphs > 120 words | 50 (8 above 200 words; longest prose paragraph 239 words, §1 ¶6) |
| Body (Intro→Conclusion, tables included) | ≈ 13,150 words; Results alone 4,266 words; 27 numbered pages + 36-page supplement |
| Table 9 (baselines) caption | 278 words — longer than the abstract; 32 data rows × 9 columns typeset via `\resizebox` at ≈ 6 pt (rendered page 21 verified: the table is legible only with zoom) |
| Repeated qualifiers | "frozen" ×53, "nominal" ×33, "preregistered/registered" ×65, "Holm" ×16, "compatible with" ×11–13, "boundary-close" ×8, "absence of an effect" ×7, "design hypothesis" ×5, "descriptive" ×11 |
| Same caveat list ("nominal parity does not equate effective sample size, temporal coverage, diversity, subtype support, duplication, label quality, prevalence, information content") | stated in §4.2.2, §5.2, §6 Q1, §7 ¶2 and §7 ¶6 |

Concrete readability defects a time-pressed reviewer will hit:

- **§5.3 quotes two different seed sets for the same contrast one paragraph apart without saying so.** The text gives gate-over-naive at 512/class as "+1.68 / +0.51 / +0.34 (point +0.75 / +0.19 / +0.11)" — these are the symmetric replication (seeds 3001–3030, `symmetric_pipeline_dynamic_001/paired_contrasts.csv`). The table immediately below (`tab:evidence_validation_tradeoff`) gives "+1.67 / +0.46 / +0.24 (point +0.97 / +0.19 / +0.12)" — the size-matched run (seeds 4001–4030). A reader sees +0.75 in the text and +0.97 in the table for "point 512, PortScan" and concludes there is an error.
- **§5.5 is still a wall**: seven bold-lead paragraphs (historical diagnostic, mechanism, robustness ×2, VBC-SG, operational feasibility) plus an evidence-map table, each mixing three to six numbers with two to four caveats. Its main message is not recoverable after one reading.
- **§3.5 (A)–(F)** is better structured but still spends a labelled six-item block, two displayed inequalities and a Proposition on an instrument the same section calls "secondary" and "not the source of the paper's main conclusion".
- **Discussion Q4** is a 250-word paragraph with First/Second/Third and a five-item list following it; **§7** has seven paragraphs of 150–250 words that restate §5.2, §5.3 and §8.
- Jargon before motivation: "incumbent-owned frozen preprocessing", "self-contained challenger pipelines", "size-matched zero-drift control", "point and strict validation", "chronological replays" all appear in the abstract before any of them is defined.
- **Table 9 creates a new readability problem** (see §8 below): mixed units in one column ("Labels" = per-stream in Block I, per-proposal in Block IV, "—" elsewhere), compound cells ("0; 800/stream monitoring", "16 + 16 (split)", "+6.73 (93%)", "0 commits"), a footnote marker, and five block headers each carrying seeds and harness identifiers.

What is no longer justified: the paper is not *sloppy*. Every sentence is precise and every number I checked is right. A reviewer writing "not well-written" today would mean "exhausting, defensive and repetitive", and would be right.

### B. "There is no results comparison with state-of-the-art / strong baselines." — **PARTIALLY JUSTIFIED**

Literally false now: §5.6 and Table 9 exist, and every cell I traced resolves to a sealed CSV (details in §8). But the reviewer's complaint survives in three defensible forms:

1. **No published adaptive-NIDS or retraining-decision method is evaluated.** CARA, Regol, IGPC-MSOS, INSOMNIA, CADE, Transcend(ent), the active-testing and limited-label selection methods are positioned conceptually in Table 1, which states outright "this paper reports no head-to-head superiority claim against them". The experimental comparison is against *generic* update rules and estimators (sliding window, ensemble, replay, DDM, ADWIN, ATC, DoC, McNemar, confidence sequences).
2. **The genuinely external baselines were never run on the harness the paper trusts.** ATC, DoC, replay and the disagreement gate exist only in Block III — the exploratory v1 harness with unpaired stream realizations that §4.1 itself says produced "exploratory context" whose "numbers were re-established on the hardened harness" for every claim the paper rests on. They were not re-established. Nothing in Blocks I–IV was run under self-contained pipelines, the configuration the paper concludes is the fair one.
3. **20 of the 32 rows are the authors' own gate variants** (point, strict, holdout, LCB, McNemar-as-gate, two-stage, pooled EB-CS, VBC-SG ×2, replay+gate, point in every block). The "strong baselines" are 12 rows, 7 of them in the exploratory block.

A reviewer could therefore still write "there is no comparison with state-of-the-art adaptive intrusion-detection methods, and the strong generic baselines are compared only on a superseded harness". "No comparison with strong baselines at all" would now be unfair.

---

## 3. Three strongest rejection arguments

**R-1. The primary "decisive" result is a null by construction, and the preregistered rule that was supposed to certify it could not fire.**
At zero drift the incumbent is trained on `sample_balanced_from_distribution(role["train"], n_per_class=2000, severity=0.0)` (`run_paper2_readaptation_v2.py:236-241`) and the size-matched challenger on `nested_candidate_draw(env.train_pools, …, 2000, sev_c=0.0)` (`:851-852`, `:366-397`) — the same partition, the same with-replacement sampler, the same hyperparameters (§4.2.2), each fitting its own scaler/PCA. The 2,000/class own-pipeline challenger is an exchangeable re-draw of the incumbent. Under exchangeability, E[naive₂₀₀₀ − never] ≈ 0 and the future-negative sign rate of committed proposals ≈ 50 % are *predictions*, not findings. The registered ELIMINATION criterion E3 — operationalized in `size_matched_confirmatory_preflight.md:20` and `make_size_matched_own_transformer_001.py:387-396` as "harmful_rate_h5 ≥ 0.4 with ≥ 5 evaluable commits ⇒ contradiction" — therefore fires under the very hypothesis it was meant to detect; ELIMINATION was unreachable by design. The paper reports ATTENUATION, explains the ≈50 % rate as "within-trajectory variability", but never states that the rule was mis-specified. Combined with the 512-vs-2,000 contrast (F2), the primary contribution at zero drift reduces to: *a model trained on a quarter of the data from the same distribution is worse; a model trained on the same amount is not*. That is the learning curve. The section title "Candidate evidence size **explains** the residual zero-drift mean harm" and the abstract's "is explained, in mean, by a candidate evidence disadvantage" claim more than an exchangeability check warrants.

**R-2. The other primary result corrects a convention the paper never shows exists outside the authors' own harness.**
"Historical convention", "frozen convention" (main.tex lines 309, 318, 344, 348, 525, 539) refer to the authors' v1/v2 harness (`frozen_initial_transformer`, "reproducing the historical harness bit-for-bit against the published v1.20.2 outputs"). No cited adaptive-NIDS system is shown to freeze the incumbent's scaler/PCA for retrained challengers. Without that, Contribution (2)-first-half is "our earlier design handicapped challengers", and the "template for evaluating adaptive pipelines beyond intrusion detection" (§6 Q4) rests on an artifact of one lab's harness. The generalizable lesson — that train/serve representation skew can reverse an evaluation's sign — is real but is a known phenomenon in MLOps and continual learning, and the paper's own §2 already frames it that way.

**R-3. The artifact does not deliver what the manuscript and README promise, and the provenance chain has holes.**
- `results/tables/MANIFEST.sha256` pins 185 CSVs; **41 are tracked in git, 144 are gitignored** (`.gitignore:45 results/**`). Absent from the repository at `57ef8e7`: `paper2_final_q1/{chronological_replays,budget_frontier,multiplicity,frontier_anchors,claim_scope_audit,operational_e2e}.csv`, all of `paper2_amendment_006…014`, `paper2_phase2h_labelfree_gates_001`, `paper2_phase2i_replay_baseline_001`, `v1_22_1_editorial/`, `results/final_experiment_ledger.csv`. These are the sources of Table 9 Blocks II, III, IV, the McNemar row of Block I, the chronological matrix (Table 8), the budget frontier, the multiplicity table (S6 gives its path explicitly), the derived Table 6, and the ledger the provenance map calls the "table → protocol → config" source of truth.
- The archived deposit the manuscript cites (DOI 10.5281/zenodo.21517899, v1.22.0) was downloaded and listed: 54 `results/tables` entries covering exactly the same 41 CSVs + manifest. **The archived artifact has the same gaps.** `make verify-hashes` (the first step of `make final-paper`) exits 1 on any missing pinned file (`verify_results_manifest.py:27-38`), so the documented one-command reproduction fails on a fresh clone or on the Zenodo zip.
- README "Reviewer quick map" rows 4, 7, 8 and 9 and REPRODUCE §5 rows 7, 8, 10 point a reviewer to files that do not exist in what was released. REPRODUCE.md line 282 states "the small confirmatory CSVs are committed under results/tables/"; only 22 % are.
- The "frozen protocol commit" SHAs cited as evidence of preregistration — `114513f…` (in `size_matched_own_transformer_001/CLAIM_INTERPRETATION.json`, the preflight note and REPRODUCE), `8838566` and `96576bb` (REPRODUCE.md, symmetric protocol), `0d280a5e…` (rewrite protocol) — **do not resolve in the repository history** (`git cat-file -e` fails; `git log --all` finds none). The verdict file therefore names a protocol commit no reader can inspect.
- The manuscript's Data Availability names v1.22.0 (2026-07-23). The revised text under review post-dates both v1.22.0 and the latest deposit v1.22.9 (2026-07-27). The archived manuscript is not the submitted manuscript.

---

## 4. Three strongest aspects

1. **Numerical integrity.** Every cell I checked in Tables 3, 4, 6, 8, 9 and the supplement tables traces bit-for-bit to a sealed CSV (symmetric and size-matched `paired_contrasts.csv`/`summary.csv`/`harmful_commit_summary.csv`; `paper2_v2_replication_001`; `policy_frontier_005/frontier.csv`; `amendment_004/{robustness,temporal,label_cost}.csv`; `amendment_005/twostage_and_monitors.csv`; `amendment_006/summary.csv`; `amendment_008/summary.csv`; `phase2h`, `phase2i`; `final_q1/{chronological_replays,budget_frontier,frontier_anchors,multiplicity}.csv`). The authors' claim that the revision removed zero numeric tokens from `main.tex` was verified by an independent token-multiset diff of `HEAD~1:manuscript/main.tex` vs `HEAD` (no token count decreased). The 16 guard tests pass; 185/185 hashes match locally.
2. **Statistical discipline that most applied-ML papers lack.** Seed as the inferential unit throughout; Holm within preregistered families; interval-inclusion TOST with ±0.2/±1.0 sensitivities; non-inferiority guardrails that gate language rather than verdicts; censoring made explicit in harmful-commit accounting; explicit refusal to convert clustered commit counts into population rates; an e-process proof whose novelty is disclaimed and whose weak-null scope is stated. The preregistration chronology of both controls is verifiable in git (protocol → config → run start → results within one afternoon; the symmetric protocol's last edit at 09:52 UTC precedes the first arm's start at ≈09:56 UTC — tight, but before).
3. **A visible self-correction record.** The π = 0.01 claim is retracted (S2.3); "8 labels suffice" is corrected (S2.2); the chronological premium against the gate (−5.0 to −15.1 points) is reported prominently; DoC and the calibrated ensemble beating the point gate in specific regimes are in the tables; the Wednesday intra-day counterexample is named. Few papers report this much against themselves.

---

## 5. Major issues, ranked by severity

**M1 (R-1).** Zero-drift size-matched control is a null-by-construction; E3 unreachable; "explains" and "decisive final result" overstated. Affects Abstract, §1 contribution (2), §5.2 title and text, §6 Q1, README TL;DR. *Fix:* state exchangeability explicitly; retitle §5.2 ("…accounts for the residual zero-drift mean harm, as exchangeability predicts"); say plainly that E3 was mis-specified and that ATTENUATION is procedural, or drop the P/A/E verdict from the main text.

**M2 (R-2).** No external evidence that frozen incumbent-owned preprocessing is a convention in the adaptive-NIDS literature. *Fix:* cite systems that freeze preprocessing, or reframe Contribution (2a) as an evaluation-hygiene finding about the authors' harness and about any pipeline that reuses a fitted representation.

**M3 (Attack 1).** §5.6 does not deliver an experimental comparison on a common harness:
- ATC, DoC, replay, disagreement: v1 harness only (unpaired), never re-run on v2 or under self-contained pipelines. Sliding window, calibrated ensemble, DDM, ADWIN, LCB, McNemar, two-stage: v2 harness under the frozen policy the paper calls artifact-amplifying. No external baseline exists under Block V conditions.
- "Three patterns are stable across blocks. First, every rule that converts the harm regime from net loss to net gain compares the challenger against the incumbent on target labels" — **false by the table's own numbers**: ATC (+0.40), DoC (+1.16) and the calibrated ensemble (+0.56) convert ToN-IoT from net loss to net gain with zero target labels. The next two sentences list those exceptions, so the paragraph contradicts itself.
- **DoC beats the point gate in the harm regime on the same harness** (Block III: +1.16 vs +0.93; `phase2h/paper2_labelfree_gates_summary.csv`). Supplement S1.5's "the labeled probe is thus the only gate on the benefit–safety Pareto front among those evaluated" is therefore incorrect: DoC is not dominated (better on ToN-IoT, worse on PortScan/UNSW). The calibrated ensemble likewise beats the gate on UNSW-Recon (+1.72 vs +1.35; ensemble − naive +0.51 [0.38, 0.66] significant, gate − naive +0.14 n.s.).
- **Block II "Anytime-valid CS, b=64" is mislabeled.** Its source (`amendment_008/summary.csv`, arm `rz_seqav64`) is the Bonferroni-over-four-looks sequential probe of amendment 008 §E, which Supplement S2.9 describes as *superseded* and *dominated* ("The confidence sequences of §3.5 subsume it"). It is presented in the main table under the current name "confidence sequence" with guarantee "per-proposal (AV)".
- Cross-block reading is visually invited and quantitatively unsafe: the same point-gate policy reads +9.12 (Block I), +8.27 (Block III), +7.65 (Block IV) on PortScan; always-deploy reads +8.25 / +7.79 / +7.22 / +7.21. Between-harness/seed-set drift of ≈1–2 points exceeds most within-block gate contrasts the text emphasizes (+0.19, +0.05, −0.21, +0.13).
- The exploratory Block III sits in a main-body table with the same column alignment as the confirmatory blocks; the caption's "descriptive, not inferential" disclaimer is in a 278-word caption at 6 pt.

**M4 (R-3).** Artifact incompleteness and broken provenance pointers (details in §9).

**M5 (Attack 3, consistency).** Surfaces that still read as "harm persists / adaptation is harmful" or contradict §5.2:
- `manuscript/tables/table_zero_drift.tex` (Supplement S2.12) caption: "**size-matching the candidate to the incumbent's 2,000 flows/class does not remove it** (row 2, often deeper) — so the harm is not a small-candidate artifact." Stated without the frozen-transformer qualifier; it asserts the negation of §5.2's headline in the authors' own supplement.
- Supplement S1.4 title: "A label-efficient validate-before-commit gate **resolves the problem**"; S1.6: "the gate avoids material harm in all twelve settings… This **empirical safety property** holds…"; S1.5: Pareto claim (above).
- `REPRODUCE.md:217`: "mean zero-drift harm **equivalent to zero** within the preregistered ±0.5-pp margin" — wording the manuscript itself abandoned; `REPRODUCE.md:315`: "Label-efficient gate **solves it**".
- `README.md` "Results at a glance" (line 180) leads with the frozen-policy ToN-IoT rescue (−1.64 → +0.79) under a heading that says only "registered replication, harness v2", and "Key findings 3" ("preserves benefit, avoids net harm, and beats naive retraining in the harm regime") carries no configuration label. The README still sells the story the paper now says was configuration-dependent.
- `manuscript/tables/table_symmetric_security.tex` caption cites "(Appendix A)" — there is no Appendix A in the manuscript; it is the protocol note's appendix.

**M6 (Attack 5).** VBC-SG: no guarantee inflation found in §3.5(E)/(F), §5.5 or Table 1 — the scoping is careful. Two other problems:
- **Understated failure on real streams.** `final_q1/chronological_replays.csv`: VBC-SG-Cohort commits 0.03 / 1.0 / 0.8 / 0.63 / 0.0 times per stream on the five CICIDS replays and recovers +0.16 / +0.91 / +1.56 / +0.56 / 0.00 points where always-deploy recovers +14.8 / +35.3 / +36.1 / +6.5 / +0.9 — forfeiting 96–100 % of the recovery, at 122–1,634 labels per stream (1,232 and 1,634 on UNSW). The main text's entire treatment is "VBC-SG abstains more and pays more, and the maximally-guaranteed configurations commit nothing at small budgets" (§6 Q3). Table 8 shows the numbers without comment.
- **Narrative footprint vs declared tier.** "Tertiary" in §1, yet: repository and artifact are named *Validate-Before-Commit*; §3.5 (A)–(F) with a Proposition; S2.8, S2.9, S2.13, S4; Block IV; a Table 1 row; a column in Table 8; the longest README bullet. The paper has two identities — the title's and the artifact's — and a reviewer will ask which one is being submitted.

**M7 (Attacks 6, 10).** Chronological evidence:
- The registered chronological family tests **strict vs never-adapt** on seven replays (`final_q1/multiplicity.csv`). On streams where the incumbent collapses to 48–59 % BA, that contrast is unfalsifiable (+11.5 to +28.8 points). The scientifically live contrasts — gate vs always-deploy — are left "descriptive" although paired per-seed data exist for all of them (non-overlapping CI95s on both UNSW timelines). A pre-declared family that cannot fail is not evidence of discipline.
- "Thirteen replays" ≈ two datasets with heavy reuse (Friday is the evaluation target in four replays; UNSW is one timeline at three training fractions). **ToN-IoT — the harm-regime dataset — has no chronological evidence at all** (no timestamps). The harmful-update finding's only real-time-ordered counterpart is therefore absent, which §7 should say in those words.
- Boundary evidence only: the manuscript correctly avoids prevalence/probability inference everywhere I looked (abstract, §5.4, §6 Q4, §7, §8, README "Honest boundary"). No overclaim found here.

**M8 (Attack 7).** Readability as measured in §2A; Table 9 as a new readability problem.

**M9 (Attack 10).** Statistical presentation:
- Percentile CI95 and the centered-bootstrap test disagree in the size-matched F3 cells: ToN point₂₀₀₀ − naive₂₀₀₀ = +0.02 **[0.00, 0.04]** with p_raw = 0.103; PortScan point = +0.05 [−0.00, 0.12], p = 0.073. Table 4 prints a CI excluding zero next to "none Holm-significant". State that the interval and the test are different procedures, or use one.
- The ±0.5-point equivalence margin is wider than effects the paper itself treats as resolved harm (ToN-IoT 512: −0.24 [−0.39, −0.10] and −0.38 [−0.53, −0.25]). The PortScan matched-size CI95 [−0.15, +0.55] is also compatible with a +0.5-point *benefit*. "Compatible with the margin" is used correctly; the margin's adequacy is not discussed.
- "Holm-significant in all three benchmarks" is significance over 30 seeds within each of three environments; §7 says so once, but the headline sentences read as cross-environment generality.
- Block I / Block II "Labels" and "Labels at decision" mix per-stream and per-proposal units in one column.

**M10 (Attack 8).** Wall-clock paragraph: correctly labelled "operational context, not a benchmark" and correctly separated from the 114× monitor figure. But the numbers are close to uninformative: n = 1 sequential run per arm on one machine; each arm includes ≈42–48 s of fixed stream/evaluation cost (the never-adapt arms), i.e. 35–40 % of a 110–140 s arm; own-transformer arms run *faster* than frozen on ToN-IoT (0.89×), which is physically implausible for added work and shows noise dominates; the 1.2–1.5× size ratio is attributed to SVC training "because SVC-RBF training scales with the batch" — asserted, not measured (a 2,000/class SVC also has more support vectors and scores every window more slowly, so part of the ratio is inference cost). Confounders that block any causal reading: run order, background load, per-arm trigger counts differing between policies, and hashing of 4× larger provenance batches. Either reduce the paragraph to its qualitative content or run the trivial micro-benchmark (§11, O1).

---

## 6. Minor issues

1. Supplement S1.1 cites "Supplementary §S1.7" for downstream-dependence of net harm; the content is in S1.6 (S1.7 is "Controls").
2. README "Reproducing the results" comments still say "Tables 1–6", "Figures 1–4" — the initial-study numbering now living in the supplement as S-tables/figures.
3. `table_symmetric_security.tex` caption: "Appendix A" (nonexistent in the manuscript).
4. Table 9 has 32 data rows; the revision report says 31.
5. Block IV "Labels" column shows 0 / 32 / 32 for naive/point/strict against 578–580 for the sequential gates — per-proposal probe labels vs per-proposal labels after deferral; units are stated only in the caption.
6. §5.3: "strict returns to within 0.06–0.14 points of never-adapt" — from `summary.csv` the UNSW gap is 0.148 (89.09 − 88.94), i.e. 0.15 at two decimals.
7. Highlights bullet 3, "Under zero drift, means fit ±0.5 points", is cryptic without the paper.
8. Abstract: "All results reproduce from a public artifact" — not true for the 144 absent CSVs without re-running experiments on undistributed raw data (see §9).
9. Data Availability cites v1.22.0 while the repository is at v1.22.9 and the manuscript post-dates both; the deposit's README/REPRODUCE differ from the ones the manuscript describes.
10. Table 8's VBC-SG column has no commits/labels context; Table 8's caption asserts "no stream shows net harm" for always-deploy but the Thursday intra-day row (no-adapt 48.3 %, naive +0.88) is a stream where nothing recovers — worth one sentence.
11. §5.6 Block III header: "30 seeds; seed-matched but unpaired realizations" — the block also includes the 20-seed random-forest ATC/DoC arms in the source CSV; the table shows only SVC rows, fine, but the header seed count is for SVC only.
12. `main_ieee.tex` was not audited; the README calls `main.tex` "the single source of truth", acceptable.
13. Keywords include "intelligent decision support" and "risk-aware model updating" — venue-tuned; harmless.
14. S6 says the multiplicity CSV is "in the artifact" — it is neither in git nor in the Zenodo zip.
15. The revision report §10 item 1 says the physical page count is 29 (27 numbered): confirmed.

---

## 7. Claim-overreach audit (surface by surface)

| Surface | Status | Evidence / note |
|---|---|---|
| Abstract | Mostly clean; "is **explained**, in mean, by a candidate evidence disadvantage" overreaches (M1); "All results reproduce from a public artifact" overreaches (M4) | — |
| Highlights | Clean | 5 bullets, all ≤ 85 chars (68–81) |
| §1 Intro | Clean on generality (explicit "Scope of the net-harm findings" paragraph; "configuration-dependent"); overreaches on "explains the residual zero-drift mean harm" and on "historical convention" as if external (M1, M2) | lines 79–101 |
| §2 Related work | "show it can be net-harmful" — acceptable ("can") | — |
| §5.1 | Clean; correctly says the frozen convention "had been handicapping every challenger" | — |
| §5.2 | Title "explains" (M1); the "what nominal parity does and does not match" paragraph is good | — |
| §5.3 | "have nothing left to recover" is slightly stronger than "no detectable average benefit" used elsewhere; two seed sets unlabeled (§2A) | — |
| §5.4 | Clean; no prevalence inference; "we do not round this into a law" | — |
| §5.5 | Clean on VBC-SG guarantees; "zero observed harmful updates over 520 commits" properly disclaimed | — |
| §5.6 | Pattern 1 false; CS row mislabeled; "strong baselines" in the title overstates (M3) | — |
| §6 Discussion | Clean on harm generality; Q3 understates VBC-SG's chronological failure (M6); overhead paragraph asserts a cause it did not measure (M10) | — |
| §7 Limitations | Clean and thorough; should add "no chronological evidence exists for ToN-IoT" | — |
| §8 Conclusion | Clean | — |
| Supplement | `table_zero_drift` caption contradicts §5.2 (M5); S1.4 "resolves the problem"; S1.5 Pareto claim false; S1.6 "empirical safety property" | — |
| README | "Results at a glance" and "Key findings 3" unlabeled frozen-policy headline; TL;DR otherwise well-scoped | lines 173–218 |
| REPRODUCE | "equivalent to zero" (l. 217), "solves it" (l. 315), "small confirmatory CSVs are committed" (l. 282) | — |

No surface says or implies "adaptive updating is generally harmful"; the guard test for that wording is real and passes. The residual overgeneralization risk is in the *supplement and artifact docs*, not the main text.

**Size matching (Attack 4).** The paper now lists everything nominal parity does not equate (§5.2, §7) and says "with replacement" four times. What it does not say is the decisive fact: at zero drift the matched challenger is an exchangeable copy of the incumbent, so parity of *any* kind is guaranteed in expectation and the experiment cannot distinguish "size explains harm" from "identical training procedure yields identical models". The strongest legitimate objection: *"The control demonstrates the learning curve of SVC-RBF between 512 and 2,000 i.i.d. draws, not a property of adaptive promotion; the only setting in which evidence comparability is a non-trivial hypothesis — a challenger trained on different (drifted) data — was not run."*

---

## 8. SoTA comparison audit (Table 9 / §5.6)

**Row-by-row provenance (verified):**

| Block | Rows | Source CSV | In repo? | Harness | Pairing | Status |
|---|---|---|---|---|---|---|
| I | naive, sliding, ensemble, DDM, ADWIN, point, holdout, LCB, two-stage | `policy_frontier_005/frontier.csv`, `amendment_004/robustness.csv`, `amendment_005/twostage_and_monitors.csv`, `v2_replication_001` | yes | v2 + amendments 003–005 (three code revisions) | paired | registered core + registered follow-ups |
| I | exact McNemar | `amendment_006/summary.csv` (ton: 222.93 + 7,133.87 = 7,357 labels ✓) | **no** | amendment 006 | paired | registered follow-up |
| II | all five | `amendment_008/summary.csv` | **no** | amendment 008 | paired | registered control; "Anytime-valid CS" = superseded Bonferroni 4-look probe (`rz_seqav64`) |
| III | all seven | `phase2h_labelfree_gates_001/*.csv`, `phase2i_replay_baseline_001/*.csv` | **no** | v1 | unpaired | exploratory |
| IV | all six | `final_q1/{frontier_anchors,budget_frontier}.csv` | **no** | final-q1 (v1.18 driver recovered; 27/99 arms re-executed) | paired | registered follow-up (BH over strict/VBC families only) |
| V | all four | `symmetric_pipeline_dynamic_001`, `size_matched_own_transformer_001` | yes | v1.21 / v1.22 | paired | registered confirmatory |

**Classification of the compared methods:**
- Genuinely strong contemporary baselines: ATC, DoC (label-free accuracy estimation), DDM/ADWIN (reference `river` implementations), calibrated soft ensemble, replay retraining, sliding window. Six families, all evaluated only under the frozen policy, four of them only on v1.
- Internal variants of the authors' method: point, strict, holdout, LCB, McNemar-gate, two-stage, disagreement gate, pooled EB-CS, VBC-SG-Cohort, VBC-SG-Refresh, replay+point — 20 rows.
- Bit-identical/paired streams: Blocks I, II, IV, V within block. Block III: no.
- Descriptive only: every cross-block comparison, and all of Block III.
- Representation accuracy: ATC/DoC as gates with a training-time labeled validation sample — fair; DDM/ADWIN with 8 labels/window and a budget sweep to 8,000 — fair and generous; replay at a fixed 50/50 — a weak instantiation (no ratio sweep), acknowledged in S1.5; calibrated ensemble — fair and shown beating the gate where it does; "statistical gates" — the Block II CS row is not what its label says (M3).
- Does the table encourage unsupported comparisons? Yes: identical column alignment across blocks; the Block V zero-drift always-deploy row (+0.19) sits under the Block II always-deploy row (−2.76) inviting a "harm went away" reading across two harnesses and two seed sets; the caption disclaimers are the only guard and are typeset at 6 pt.
- Implicit rankings found in the text: "the statistical commit rules are the only policies that commit nothing under zero drift" (true within Block II); "First, every rule that converts the harm regime… compares the challenger against the incumbent on target labels" (false, M3); "Choosing among these policies is a cost decision rather than a ranking" — correct and then the sentence ranks anyway ("the cheapest policies… win the utility in almost every cell, while the point gate is the accuracy maximizer").
- Is "comparison with strong baselines" defensible? As a *descriptive summary of previously evaluated policies*, yes. As the section title's "comparison with strong baselines", only partially. A reviewer can reasonably demand one common-harness head-to-head (§11, R1).
- Is the existing evidence sufficient for the paper's actual claim (conditional value of validation, comparability before promotion)? Largely yes — that claim is carried by Block V, not by Table 9. Table 9 was added to answer a reviewer, and it answers a different question (which policy wins) than the paper asks.

---

## 9. Reproducibility audit

Attempted path: README quick map → table → sealed CSV → protocol/config → reproduction command.

| # | Manuscript claim | Table | Sealed CSV | Present at 57ef8e7 | Present in Zenodo v1.22.0 zip | Protocol/config | Command documented | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | naive-own − never = +7.21/+2.55/+1.03 (§5.1) | Tab. 3 | `symmetric_pipeline_dynamic_001/paired_contrasts.csv` (7.2122/2.5461/1.0289) | yes | yes | `paper2_symmetric_pipeline_dynamic_protocol_001.md` (git-dated before run), `configs/symmetric_pipeline_dynamic_v1.json` | yes (`run_symmetric_pipeline_replication --run --confirmatory-authorized`) | **passes** |
| 2 | naive₂₀₀₀ − never = +0.19 [−0.15, +0.55], CI90 hi 0.494 (§5.2) | Tab. 4 | `size_matched_own_transformer_001/paired_contrasts.csv` (0.1854; ci90 0.494) | yes | yes | protocol note present; **its cited "frozen commit 114513f" does not exist in history** | yes | passes numerically; provenance pointer broken |
| 3 | ATTENUATION via E3 sign rate (§5.2) | — | `CLAIM_INTERPRETATION.json` | yes | yes | 0.4 threshold not in the protocol note; in preflight note + code, committed one minute before the run started | — | preregistration claim technically holds; rule mis-specified (M1) |
| 4 | Chronological matrix (Tab. 8; +14.78 … +6.92) | Tab. 8 | `final_q1/chronological_replays.csv` | **no (gitignored)** | **no** | `q1_max_protocol.md` D4 | yes (`run_paper2_temporal_stream`, 7 streams × 4 policies × 30 seeds) | numbers match the local file; **not reproducible from the release without re-running** |
| 5 | Budget frontier 93 %/81 %/68 %, 578 labels (§5.5, Tab. 9 Block IV) | S2.12 table | `final_q1/budget_frontier.csv` | **no** | **no** | `configs/q1_budget_frontier_v2.json` (present) | yes (99 arms) | same |
| 6 | Block II zero-drift rows | Tab. 9 | `amendment_008/summary.csv` | **no** | **no** | amendment 008 note (present) | flags documented | same |
| 7 | Block III ATC/DoC/replay rows | Tab. 9 | `phase2h…`, `phase2i…` | **no** | **no** | phase2h/2i protocol notes present | v1 runner documented | same |
| 8 | Multiplicity table (S6) | — | `final_q1/multiplicity.csv` ("in the artifact") | **no** | **no** | — | `make_paper2_q1_multiplicity` | same |
| 9 | Table 6 trade-off | Tab. 6 | `v1_22_1_editorial/evidence_validation_tradeoff.csv` | **no** | **no** | derived | `make_evidence_validation_tradeoff` | derivable from tracked CSVs |
| 10 | Wall-clock 0.97× / 1.2–1.5× (§6) | — | `audits/pipeline_arm_wallclock_summary.csv` | yes | n/a | reads `results/raw/**/completion_marker.json` — **raw not redistributed** | script present; skips without raw | numbers recomputed from the CSV: mean 0.970, range 0.893–1.061; size 1.21–1.54 ✓ |

Other findings:
- `make verify-hashes` / `make final-paper` fail on a fresh clone (144 missing pins → exit 1).
- Stale references: S1.1 → "S1.7" (should be S1.6); README "Tables 1–6 / Figures 1–4"; Table caption "Appendix A". All main → supplement `\S S<n>.<m>` pointers I checked resolve (S0, S1.1–S1.6, S2.1, S2.3, S2.6, S2.7, S2.9–S2.13, S3–S8).
- Superseded material without warning: Table 9 Block II CS row (M3); `REPRODUCE.md:217` "equivalent to zero".
- The `harness-v2-protocol` tag exists. The size-matched and symmetric protocol notes are in git *before* their results, but the specific SHAs the artifact cites for "frozen before run" are not.
- Bibliography: all 75 cite keys resolve in `references.bib`. Build log: no undefined references; one overfull box (title block).

---

## 10. Exact changes that would neutralize each surviving criticism

**Readability (2A / M8)**
1. Abstract: delete "PortScan is boundary-close, so this is compatibility with a margin, not absence of an effect" and replace the second result sentence with: "Under zero drift, challengers trained on a quarter of the incumbent's data degrade it; at nominal parity the mean effect is within ±0.5 points in all three benchmarks (one at the margin's edge)."
2. Move §5.5's mechanism, robustness and operational-feasibility paragraphs to the supplement, leaving one 120-word summary and the evidence-map table.
3. §5.3: label the two seed sets ("symmetric replication, seeds 3001–3030" / "size-matched control, seeds 4001–4030") or quote only the Table 6 numbers.
4. Cut the caveat list to one canonical location (§5.2) and point to it from §4.2.2, §6 and §7; cap "boundary-close" at three occurrences (abstract, §5.2, §7).
5. Split Table 9 into (a) a properties table (labels at decision, h′ vs h, reject, guarantee) and (b) an outcomes table per block; move Block III to the supplement; cut the caption to ≤ 80 words and put the block definitions in the text.
6. Reduce §3.5 to (A), (B), (E), (F) in prose (≈ 300 words); relocate (C), (D), the displayed inequalities and Proposition 1 to S2.13/S4.

**SoTA comparison (2B / M3)**
7. Retitle §5.6 "Descriptive comparison with previously evaluated update policies" unless R1 (§11) is run.
8. Rewrite pattern 1: "Every rule that converts the harm regime to net gain *and* preserves the benefit regime compares h′ against h on target labels; the label-free rules that avoid harm (ATC, DoC, calibrated ensemble) forfeit 1.9–4.6 points of benefit or cannot decline an update."
9. Relabel the Block II CS row "Bonferroni 4-look sequential probe (superseded by EB-CS; S2.9)" or replace it with the EB-CS zero-drift result.
10. Correct S1.5's Pareto sentence: "the labeled probe and DoC are both undominated among the evaluated gates; the probe is the only one that preserves the full benefit-regime gain."

**Novelty / size matching (M1, M2)**
11. §5.2: add, before the results, "At severity 0 the 2,000-per-class challenger is drawn from the same partition by the same sampler as the incumbent; it is an exchangeable re-draw, so nominal parity is expected to be mean-neutral. The control tests whether the harness and the 512-versus-2,000 contrast behave as exchangeability predicts." Retitle §5.2 accordingly and replace "explains" by "accounts for … as expected under exchangeability" in abstract, §1, §6.
12. State that E3 could not pass under exchangeability, and that ATTENUATION is a procedural label; move the P/A/E trace to S8.
13. §4.2.1 / §2: either cite adaptive-NIDS or MLOps systems that freeze a fitted representation across retrains, or rewrite "historical convention" as "the convention of our earlier harness (and of any pipeline that reuses a fitted representation)".

**Artifact (M4)**
14. Track the 144 CSVs (they are small; the manifest already pins them) or remove their pins and every pointer to them; regenerate the Zenodo deposit for the submitted text; replace the nonexistent SHAs in `CLAIM_INTERPRETATION.json`, the preflight notes and REPRODUCE.md with SHAs that exist on `main`, or state that they belong to a squashed feature branch.
15. Fix REPRODUCE.md l. 217/282/315, README l. 180–218 labels ("historical frozen-transformer configuration"), `table_zero_drift.tex` caption ("under the frozen transformer of this arm; the own-transformer control of §5.2 finds the opposite"), S1.4 title, S1.6 "safety property", `table_symmetric_security.tex` "Appendix A", S1.1 "S1.7".

**VBC-SG (M6)**
16. §5.4 or §6 Q3: add one sentence with the numbers: "On the five CICIDS replays VBC-SG-Cohort commits 0.0–1.0 times per stream and recovers 0–4 % of always-deploy's gain at 122–444 labels per stream; on UNSW it recovers most of it at 1,232–1,634 labels."
17. Decide the paper's identity: either rename the artifact to match the title or state in §1 that the artifact name predates the reframing.

**Chronological / statistics (M7, M9)**
18. Report the paired strict-vs-naive and point-vs-naive contrasts on the seven replays (data exist), labelled exploratory, instead of leaving the "point estimates exceed" phrasing.
19. §7: add "ToN-IoT ships no timestamps; the harm-regime benchmark has no chronological counterpart."
20. Table 4 and S8: note that CI95 brackets are percentile bootstrap intervals and p-values are centered-bootstrap tests, so a bracket can exclude zero while p > 0.05 (ToN point₂₀₀₀).

**Overhead (M10)**
21. Reduce the paragraph to the qualitative description plus "whole-arm wall-clock differed by < 10 % between policies (n = 1 per arm; not a benchmark)"; drop the causal "because".

---

## 11. Experiments genuinely required

**REQUIRED to support an existing claim (as currently worded)**

- **R1 — common-harness baselines (supports §5.6's title and Contribution (3)'s "all evaluated in the same harness").** Run ATC, DoC, replay 50/50, calibrated soft ensemble, sliding window and river-DDM on the self-contained (own-transformer) harness, seeds 3001–3030, full and zero drift, paired against naive/point/strict. ≈ 6 policies × 6 scenarios × 30 seeds at ≈ 2 min per arm — about 12 machine-hours. Without it, retitle §5.6 (change 7) and soften Contribution (3).
- **R2 — size-matched self-contained challengers under drift (supports "candidate evidence comparability" as a primary contribution rather than a zero-drift exchangeability check).** Own-transformer, 2,000/class candidates at mild (0.25) and full drift on the three benchmarks, seeds fresh, paired against 512/class. This is the only configuration in which "evidence comparability" is a non-trivial hypothesis, and it is the configuration where the frozen-policy precedent (S1.5: size-matching *deepened* harm) makes the outcome genuinely uncertain. If the authors prefer not to run it, the primary contribution must be rescoped to "under zero drift" everywhere, including the title of §5.2 and the abstract.

**OPTIONAL but useful for reviewer resilience**

- **O1 — micro-benchmark** of scaler+PCA fit time, bundle size and per-flow inference latency for 512 vs 2,000/class, frozen vs own (minutes of compute; replaces M10 entirely).
- **O2 — effective-sample-size accounting**: unique rows per candidate batch at 512 and 2,000 with replacement (a one-line addition to the provenance log); directly answers Attack 4's duplication question with numbers instead of caveats.
- **O3 — paired gate-vs-naive analysis on the chronological matrix** (no new runs; data exist).
- **O4 — one non-SVC learner (random forest or logistic regression) in the symmetric replication**, to show the ownership effect is not SVC-RBF-specific at trajectory scale (S1.6 covers only the zero-drift replacement harm).
- **O5 — VBC-SG at cap 512 under own-transformer 512/class on one full-drift scenario**, so Block IV and Block V share at least one cell.

---

## 12. If this exact manuscript were submitted tomorrow to a strong Q1 journal, what is the most likely reason it would still be rejected?

**Insufficient novelty and significance relative to its length.** A strong reviewer will summarize the primary contribution as: *a model retrained on a quarter of the data from the same distribution is worse than the incumbent; a model retrained on the same amount from the same distribution is not; and an earlier version of the authors' own harness handicapped challengers by freezing the incumbent's scaler.* They will note that the "decisive" zero-drift control is a null predicted by exchangeability, that its preregistered ELIMINATION rule could never fire, that the interesting case (comparable challengers under real drift) was not run, that the strong baselines were evaluated only on a harness the paper itself supersedes, and that the only real time-ordered evidence never exhibits the phenomenon the paper is about. The 27 + 36 pages of careful qualification will be read as evidence that the authors know the effect is small and configuration-bound. The reproducibility gaps (144 undistributed sealed CSVs; protocol SHAs that do not exist; a DOI that predates the text) will be the second reason, and the one most likely to be phrased as a request for clarification rather than rejection.

The two KBS criticisms would, on their own, no longer justify rejection; they would justify a request for shortening and for one common-harness table.

---

## Read-only proof

Executed at the end of the audit, after this file was written:

```
$ git rev-parse HEAD
57ef8e704436034cbf1eb71cc320e5d373134100
$ git status --short
?? audits/post_kbs_hostile_referee_57ef8e7.md
```

The only change to the working tree is this untracked report. No file was modified, staged, committed or pushed. (Pytest was run with `-p no:cacheprovider`; `__pycache__/` and `.pytest_cache/` are gitignored and do not appear in `git status`.)
