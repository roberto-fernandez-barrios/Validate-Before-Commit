# Academic Repository Curation — Inventory & Classification

Branch: `maintenance/academic-repository-curation` (from `main` @ `a8d118a`).
Goal: the visible tree of `main` should contain only material with scientific,
reproducibility, technical, or documentary value. Conversation traces, editorial strategy,
internal red-team, and writing logistics are retired from the current tree. **No history is
rewritten**; every retired file remains recoverable from git history. Tags, GitHub Releases,
and Zenodo deposits are untouched.

Legend: **KEEP** (scientific/reproducibility value) · **CONSOLIDATE** (useful but duplicated
/ fragmented) · **REMOVE** (editorial/chat/development scaffolding) · **REVIEW** (dependency or
purpose flagged for the human reviewer).

## 0. Summary

| Bucket | Files | Notes |
|---|---|---|
| Tracked files before | 467 | baseline on branch HEAD `a8d118a` |
| notes/ KEEP | 109 | protocols, pre-registrations, amendments, audits, experimental checkpoints, interpretations, diagnostics, dataset docs |
| notes/ REMOVE | 45 | hostile reviews, editorial compression/focus-cut, narrative/storyline, bibliographic-ceiling, release/version logistics, per-version release notes |
| notes/ REVIEW (kept, flagged) | 5 | code-referenced "editorial-named" protocols-of-record + 1 narrative checkpoint cited by the claim audit |
| manuscript/ REMOVE | 5 | unused CAS template social-media thumbnails |
| manuscript/ REVIEW (kept) | 2 | `paper2_manuscript_draft_002.md` (claim-audit source of truth), `generated/` byte-dup (script output) |
| New docs | 2 | this audit + `docs/SCIENTIFIC_PROVENANCE.md` |
| Bytes removed | ~270.6 KiB | 246,984 B notes + 30,137 B thumbnails |

Verification of inertness (before any deletion):

- All 45 REMOVE-candidate notes are tracked and **referenced by zero non-`notes/` tracked
  files** (`git grep` of every basename over `:!notes/` → empty). Removing them breaks no
  script, build, manifest, or test.
- The 5 removed thumbnails are `\includegraphics`-referenced only inside conditional
  front-matter macros of `cas-common.sty` and **load in none of the three compilations**
  (only `thumbnails/cas-email.jpeg` appears in `main.log`).
- 16 of 17 per-version release notes are **byte-identical** to their GitHub Release bodies;
  the 17th (`v1.2.0`, which has no GitHub Release) is preserved verbatim in
  `docs/SCIENTIFIC_PROVENANCE.md`.

---

## 1. REMOVE — editorial / red-team / development scaffolding (45 notes)

None of these is referenced by any tracked script, table, manifest, or test. Load-bearing
numeric science they restate lives in the KEEP protocol/amendment/audit files, the sealed
`results/tables/MANIFEST.sha256` + `results/final_manifest.json`, and the GitHub Releases.

### 1.1 Hostile / red-team self-review (7)
| File | Purpose | Ref? | Manifest/builder? | Decision |
|---|---|---|---|---|
| `paper2_final_hostile_review_001.md` | internal adversarial review of the paper | no | no | REMOVE |
| `q1_faseF_hostile_review_001.md` | Q1 phase-F red-team pass | no | no | REMOVE |
| `size_matched_final_hostile_review.md` | red-team of the size-matched phase | no | no | REMOVE |
| `v1_21_final_hostile_review.md` | v1.21 red-team pass | no | no | REMOVE |
| `v1_21_final_hostile_review_and_sealing_protocol.md` | red-team + tag/Zenodo sealing steps (logistics; commit refs are in git) | no | no | REMOVE |
| `v1_22_1_final_editorial_hostile_review.md` | v1.22.1 editorial red-team | no | no | REMOVE |
| `paper2_safe_readaptation_rescue_review_001.md` | pre-pivot strategy ranking + reviewer-attack simulations + abstract drafts | no | no | REMOVE |

### 1.2 Editorial compression / focus-cut / scope-trim (11)
| File | Purpose | Ref? | Decision |
|---|---|---|---|
| `q1_final_editorial_compression_checkpoint.md` | word-count compression pass | no | REMOVE |
| `q1_final_editorial_compression_protocol.md` | compression procedure | no | REMOVE |
| `q1_final_editorial_compression_report.md` | compression outcome report | no | REMOVE |
| `v1_21_final_compression_report.md` | v1.21 compression report | no | REMOVE |
| `v1_22_1_editorial_compression_report.md` | v1.22.1 compression report | no | REMOVE |
| `v1_22_1_editorial_scope_baseline.md` | pre-patch editorial snapshot | no | REMOVE |
| `v1_22_1_editorial_scope_checkpoint.md` | post-patch editorial snapshot | no | REMOVE |
| `KBS_FINAL_FOCUS_AUDIT.md` | focus-cut triage audit | no | REMOVE |
| `KBS_FINAL_FOCUS_CUT_BASELINE.md` | focus-cut baseline | no | REMOVE |
| `KBS_FINAL_FOCUS_CUT_CHECKPOINT.md` | focus-cut checkpoint | no | REMOVE |
| `KBS_FINAL_MAIN_CONTENT_MAP.md` | keep/compress/move section triage | no | REMOVE |

> The corresponding **`v1_22_1_editorial_scope_protocol.md` is KEPT** (§3): it is cited by
> `src/analysis/make_evidence_validation_tradeoff.py`,
> `make_size_matched_equivalence_sensitivity.py` and the claim-audit guards as the
> protocol-of-record for two deterministic derived tables.

### 1.3 Narrative / storyline framing (2)
| File | Purpose | Ref? | Decision |
|---|---|---|---|
| `paper2_storyline_001.md` | proposed manuscript storyline/section flow | no | REMOVE |
| `Q1_FINAL_NARRATIVE_BASELINE.md` | pre-rebuild narrative baseline snapshot | no | REMOVE |

> `Q1_FINAL_NARRATIVE_REBUILD_CHECKPOINT.md` is **KEPT + flagged** (§3): it is cited in a
> comment in `src/analysis/audit_paper2_claims.py` as the provenance for the final claim
> surface.

### 1.4 Bibliographic-ceiling exercises (3)
| File | Purpose | Ref? | Decision |
|---|---|---|---|
| `KBS_BIBLIOGRAPHIC_CEILING_BASELINE.md` | reference-count baseline + release scope | no | REMOVE |
| `KBS_BIBLIOGRAPHIC_CEILING_CHECKPOINT.md` | reference-count patch checkpoint | no | REMOVE |
| `KBS_FINAL_REFERENCE_AUDIT.md` | bibliographic metadata verification of 12 added citations | no | REMOVE |

### 1.5 Release / version logistics (3)
| File | Purpose | Ref? | Decision |
|---|---|---|---|
| `FINAL_KBS_RELEASE_CHECKPOINT.md` | tag/DOI chain, asset SHA-256s, history-rewrite log | no | REMOVE |
| `FINAL_RELEASE_VERSION_RESOLUTION.md` | SemVer reasoning for editorial-only releases | no | REMOVE |
| `v1_22_2_final_microcorrections.md` | five wording microcorrections + submission package list | no | REMOVE |

> Version DOIs and release-asset hashes from these files are preserved via the Zenodo concept
> record and GitHub Releases, and summarized in `docs/SCIENTIFIC_PROVENANCE.md`.

### 1.6 Manuscript-integration editorial checkpoints (2) — BORDERLINE
| File | Purpose | Ref? | Decision |
|---|---|---|---|
| `size_matched_final_manuscript_checkpoint.md` | manuscript reframing + hostile-review response for the size-matched integration | no | REMOVE (flagged) |
| `symmetric_pipeline_scenario_a_manuscript_checkpoint.md` | Scenario-A rewrite framing + hostile-review response | no | REMOVE (flagged) |

> These are **MIXED**: manuscript-rewrite narrative plus recorded gate outcomes and sealed
> config/manifest hashes. The experimental effect sizes they cite live in the KEPT
> `*_rewrite_protocol.md` files; the hashes live in the sealed manifests. Flagged so the human
> reviewer can veto if they prefer to keep the integration record in-tree.

### 1.7 Per-version internal release notes (17) — CONSOLIDATE → REMOVE
`release_notes_v1.2.0.md` … `release_notes_v1.18.0.md`.

- `v1.3.0`–`v1.18.0` (16 files): **byte-identical** to their GitHub Release bodies
  (canonical, permanent channel). REMOVE — pure duplication.
- `v1.2.0` (1 file): **no GitHub Release exists** → orphan. Its unique content (Phase 2i
  replay baseline, Phase 2j probe prevalence, coupling-aware §5.2 revision) is additionally
  covered by the KEPT `paper2_phase2i_*`, `paper2_phase2j_*`, and
  `paper2_coupling_and_overclaim_revision_001.md`, and is preserved **verbatim** in
  `docs/SCIENTIFIC_PROVENANCE.md`. REMOVE after consolidation.

---

## 2. REMOVE — manuscript / template artifacts (5 files)

| File | Purpose | Loaded in any compile? | Decision |
|---|---|---|---|
| `manuscript/thumbnails/cas-url.jpeg` | Elsevier CAS "homepage" front-matter icon | no | REMOVE |
| `manuscript/thumbnails/cas-facebook.jpeg` | CAS social icon | no | REMOVE |
| `manuscript/thumbnails/cas-twitter.jpeg` | CAS social icon | no | REMOVE |
| `manuscript/thumbnails/cas-gplus.jpeg` | CAS social icon | no | REMOVE |
| `manuscript/thumbnails/cas-linkedin.jpeg` | CAS social icon | no | REMOVE |

`thumbnails/cas-email.jpeg` **is loaded** by `main.pdf` (corresponding-author email marker)
and is KEPT. The 5 above are referenced only inside conditional social/homepage macros in
`cas-common.sty` that the manuscript never triggers; compilation is re-verified after removal.

---

## 3. REVIEW — kept despite an editorial-sounding name (flagged for human)

| File | Why kept |
|---|---|
| `v1_22_1_editorial_scope_protocol.md` | protocol-of-record cited by `make_evidence_validation_tradeoff.py`, `make_size_matched_equivalence_sensitivity.py`, and the claim-audit guards; holds the ±0.2/±0.5/±1.0 margins and label arithmetic the derived tables depend on. Removing dangles code references. |
| `size_matched_final_rewrite_protocol.md` | cited by `audit_paper2_claims.py` / `make_paper2_claim_scope_audit.py`; frozen claim-scope contract with the load-bearing size-matched effect sizes. |
| `symmetric_pipeline_scenario_a_rewrite_protocol.md` | cited as the Scenario-A registered rewrite contract; holds the symmetric-pipeline effect sizes and forbidden-claim list. |
| `Q1_FINAL_NARRATIVE_REBUILD_CHECKPOINT.md` | cited in a comment in `audit_paper2_claims.py` as the provenance for the final claim surface; removing would require editing a scientific gate file. |
| `manuscript/generated/table_evidence_validation_tradeoff.tex` | byte-identical to `manuscript/tables/…`, but **both are written by `make_evidence_validation_tradeoff.py`** (one is the canonical output, one the `\input` copy). Not stray; removing it would need a change to a derived-table generator. Only `manuscript/tables/…` is `\input` by `main.tex`. |
| `manuscript/paper2_manuscript_draft_002.md` | **not an old draft** — it is opened directly by `audit_paper2_claims.py` (source of every numeric claim check) and by `make_paper2_latex.py`. Hard dependency; KEEP. |

---

## 4. KEEP — scientific / reproducibility material (109 notes)

Retained in full. Grouped for orientation; each is a registered protocol, pre-registration,
experiment amendment, claims/results audit, experimental-phase checkpoint, interpretation,
diagnostic, or dataset/planning document that fixed a scientific decision or records an
experimental outcome.

**Registered protocols & pre-registrations (21):** `final_kbs_protocol`,
`paper2_downstream_policy_selection_protocol_001`, `paper2_feature_map_sensitivity_protocol_001`,
`paper2_harness_v2_registered_replication_protocol_001`, `paper2_nf_ton_iot_q1_gate_protocol_001`,
`paper2_phase2_gated_readaptation_preregistration_001`, `paper2_phase2h_labelfree_gates_protocol_001`,
`paper2_phase2i_replay_baseline_protocol_001`, `paper2_phase2j_probe_prevalence_protocol_001`,
`paper2_phase3_extras_protocol_001`, `paper2_safe_readaptation_phase1_protocol_001`,
`paper2_size_matched_own_transformer_protocol_001`, `paper2_symmetric_pipeline_dynamic_protocol_001`,
`paper2_temporal_stream_protocol_001`, `paper2_unsw_nb15_smoke_protocol_001`,
`q1_final_acceptance_patch_protocol`, `q1_final_statistical_claims_patch_protocol`, `q1_max_protocol`,
`size_matched_final_rewrite_protocol`, `symmetric_pipeline_scenario_a_rewrite_protocol`,
`v1_22_1_editorial_scope_protocol`. Many are cited by `make_final_experiment_ledger.py` as the
per-table provenance column.

**Experiment amendments (18):** `paper2_amendment_004_checkpoint_001`,
`paper2_amendment_005_checkpoint_001`, `paper2_amendment_006_checkpoint_001`,
`paper2_amendment_007_checkpoint_001`, `paper2_amendment_008_checkpoint_001`,
`paper2_harness_v2_amendment_002` … `paper2_harness_v2_amendment_014` (013 files 002–014).

**Claims / results / evidence audits (8):** `Q1_FINAL_CLAIM_AUDIT`, `Q1_FINAL_EVIDENCE_MAP`,
`paper2_coupling_and_overclaim_revision_001`, `paper2_leakage_verification_001`,
`paper2_q1_audit_and_mechanism_001`, `paper2_mechanism_law_robustness_checkpoint_001`,
`q1_final_statistical_claims_patch_checkpoint`, `q1_final_statistical_claims_patch_protocol`.

**Experimental-phase checkpoints (≈54):** `q1_faseB/C/D/E_checkpoint_001`,
`paper2_phase2b/2c/2h/2i/2j/2k_*_checkpoint_001`, `paper2_progressive_*`, `paper2_downstream_*`,
`paper2_controlled_streaming_*`, `paper2_final_q1_synthesis_checkpoint_001..004`,
`paper2_gate_robustness_checkpoint_001`, `paper2_operational_*`, `paper2_multi_scenario_cicids_*`,
`paper2_thursday_webattacks_*`, `paper2_ton_iot_q1_gate_*`, `paper2_unsw_nb15_medium_*`,
`paper2_global_status_after_thursday_checkpoint_005`, `size_matched_own_transformer_*_checkpoint`,
`symmetric_pipeline_{baseline,confirmatory,initial_phase}_checkpoint`,
`{size_matched,symmetric_pipeline}_confirmatory_preflight`, `q1_final_phase_checkpoint_001`, etc.

**Interpretations / diagnostics / syntheses (≈9):** `paper2_statistical_interpretation_001`,
`paper2_geometry_diagnostics_interpretation_001`, `paper2_long_stream_downstream_interpretation_001`,
`paper2_strict_operational_advantage_interpretation_001`, `paper2_anchored_streaming_cal30_diagnostic_001`,
`paper2_statistical_summary_checkpoint_001`, `paper2_results_synthesis_checkpoint_001`,
`paper2_runtime_cost_checkpoint_001`, `paper2_controlled_streaming_results_draft_001`.

**Dataset / experimental planning & decisions (4):** `paper2_second_dataset_plan_001`,
`paper2_final_experimental_decision_after_unsw_001` (records the campaign-stop decision),
plus the two confirmatory preflights above.

**Manifest-referenced provenance (1):** `frontier_driver_recovery_report.md` — referenced by
`make_final_manifest.py` (`recovery_report=…`); documents the bit-for-bit recovery of the
budget-frontier driver. KEEP.

---

## 5. notes/ reorganization — PROPOSAL ONLY (not executed)

A cleaner layout would be:

```
notes/protocols/    # *_protocol.md, *_preregistration_*.md, q1_max_protocol.md, amendments
notes/audits/       # Q1_FINAL_CLAIM_AUDIT, Q1_FINAL_EVIDENCE_MAP, leakage/mechanism audits
notes/provenance/   # experimental-phase checkpoints, interpretations, diagnostics
```

**Not executed**, by design. Dozens of `src/` scripts and `make_final_experiment_ledger.py`
embed exact `notes/<file>.md` paths as provenance strings, and the ledger writes those paths
into `results/final_experiment_ledger.csv`. Moving files would dangle every such reference and
corrupt the ledger. Per the task's own rule (garbage removal first; no reference-breaking
reorg), the moves are deferred to a follow-up that also rewrites the references atomically.

---

## 6. Validation

All gates run with the `paper2` conda env (Python 3.11.15) on the curated tree; baseline
values captured on `main` @ `a8d118a` before any removal.

| Gate | Baseline | Curated tree | Status |
|---|---|---|---|
| `pytest tests` | 136 passed | 136 passed | ✅ unchanged |
| Claim audit (`audit_paper2_claims`) | 630 PASS / 0 FAIL | 630 PASS / 0 FAIL | ✅ unchanged |
| Manifest verify (`verify_results_manifest`) | 185/185, 0 unpinned | 185/185, 0 unpinned | ✅ unchanged |
| `main.pdf` | 26 pp, 0 undef | 26 pp, 0 undef | ✅ unchanged |
| `supplement.pdf` | 35 pp, 0 undef | 35 pp, 0 undef | ✅ unchanged |
| `main_ieee.pdf` (committed source) | 18 pp, 0 undef | 18 pp, 0 undef | ✅ unchanged |

Notes:

- **IEEE page count**: the committed `main_ieee.tex` compiles to **18 pp**. (A baseline run
  that first invoked `src.analysis.port_ieee` produced 19 pp because `port_ieee` regenerates
  `main_ieee.tex` from `main.tex` and would overwrite the committed file's manual
  `figure*`/listing tweaks — a **pre-existing** drift, out of scope here. The committed source
  was restored; curation touched no IEEE file, and `main_ieee.tex` is byte-identical to its
  committed blob.)
- **Thumbnails**: after removal, `main.pdf` still loads `thumbnails/cas-email.jpeg` (5×) with
  no missing-file errors; the 5 removed thumbnails load in no compilation.
- **Release builders**: `make_results_manifest`, `make_final_experiment_ledger`, and
  `make_final_manifest` all run clean (manifest 185 files; ledger 12 blocks / 562 arm dirs;
  final manifest audit 630/630). `results/tables/MANIFEST.sha256` regenerates **byte-identical**.
  `results/final_manifest.json` regenerated identically except for `generated_at_utc` and
  `source_commit_sha` provenance fields; it was **restored to its committed bytes** so no
  scientific manifest is modified.
- **`results/raw/**`**: untouched; no tracked `results/` file was modified (only the transient
  `final_manifest.json` provenance fields, since restored). **No experiment script was run** —
  only analysis/audit/verify/compile over existing artifacts.
- **ATTENUATION**: intact — asserted by the claim-audit guard
  "v1221 A: registered ATTENUATION outcome retained (main+ieee)" (PASS) and present unchanged
  in `main.tex`, `main_ieee.tex`, `supplement.tex`.
- **Elsevier AI-usage declaration**: retained verbatim in `main.tex` §"Declaration of
  generative AI…", `main_ieee.tex`, `supplement.tex`, and its generator
  `make_paper2_latex.py`.

### Residual editorial/conversational term scan

Every remaining hit is legitimate:

| Term | Remaining in | Why legitimate |
|---|---|---|
| `Claude` | `main.tex`/`main_ieee.tex`/`supplement.tex`, `make_paper2_latex.py` | mandatory Elsevier generative-AI declaration |
| `Claude` / `scratchpad` | `run_q1_budget_frontier.py`, `frontier_driver_recovery_report.md` | reproducibility provenance of the recovered budget-frontier driver (with SHA-256) |
| `scratchpad` | `port_ieee.py` | technical: temp build directory |
| `PLAN_Q1_CLAUDE_CODE.md` | `.gitignore`, `REPRODUCE.md` | the file is intentionally git-ignored; `.gitignore` lists it and `REPRODUCE.md` cites it as a flag's origin (minor soft reference — left as-is, REPRODUCE.md not rewritten) |
| `final verdict` | `main.tex`/`main_ieee.tex`, `make_paper2_final_q1_synthesis_v3.py`, kept synthesis checkpoints | scientific prose ("the program's final verdict bounds the gate itself"), not editorial workflow |
| `hostile review` | `tests/test_claims.py`, kept protocols/checkpoints (`q1_max_protocol`, `q1_faseE_checkpoint`, rewrite protocols, etc.) | scientific-process references to the review *rounds* that motivated registered experiments; the hostile-review *documents* themselves were removed |
| `ready for human review`, `hostile review` | `Q1_FINAL_NARRATIVE_REBUILD_CHECKPOINT.md` | borderline-KEEP file (cited by the claim audit); flagged in §3 for human veto |
| `hostile review`, `red-team`, `focus cut`, … | `ACADEMIC_REPOSITORY_CURATION_AUDIT.md`, `SCIENTIFIC_PROVENANCE.md` | this audit and the provenance map necessarily name what was retired |

No `ChatGPT`, `red team` (spaced), `ready for submission`, or stray conversation dumps remain.

### Verdict

**READY FOR HUMAN REVIEW — ACADEMIC REPOSITORY CURATION COMPLETE.** Branch not merged; no
tag, release, version bump, history rewrite, or Zenodo change performed.
