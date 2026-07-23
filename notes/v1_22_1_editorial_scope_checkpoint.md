# CHECKPOINT — v1.22.1 editorial scope correction

Branch: `fix/v1.22.1-editorial-scope`. Date: 2026-07-24. Phase: editorial correction and
derived analysis only — no experiments, no science changed. STOPPED before merge/tag/
release/Zenodo per protocol.

## A. Baseline integrity

- Tag: `v1.22.0` on `main` = sealing commit `43d9c255af48db9bcc3c6eb341a153381b18c8e8`
  (source commit `cccc5e43c6769bc0b38f18370d45e44ef61c9f95`); branch created from it.
- Hashes: **183/183** pinned CSVs match `MANIFEST.sha256` throughout the phase
  (the only extras are the 2 deliberately unpinned editorial CSVs).
- `results/final_manifest.json` and `results/tables/MANIFEST.sha256` **byte-identical**
  to baseline (SHA-256 `1f7f1617…` / `132643ad…`), now pinned by pytest guard.
- pytest: 118/118 at baseline → **135/135** final (17 new guards).
  Audit: 586/586 at baseline → **625/625** final (39 new checks; 3 anchors updated to
  the authorized v1.22.1 formulations).
- Size-matched control **21/21** arms complete (seeds 4001–4030); symmetric-pipeline
  replication **42/42** (seeds 3001–3030). `results/raw/` untouched; no new seeds; no
  experimental runner executed; no background processes.

## B. Factual corrections

- **Data Availability before:** "…result manifest for artifact version v1.20.2 are
  archived at Zenodo; the concept DOI 10.5281/zenodo.21322256 resolves to the latest
  release…" (IEEE: concept DOI only).
- **After (CAS + IEEE):** artifact version **v1.22.0**; exact version DOI
  **10.5281/zenodo.21517899**; concept DOI 10.5281/zenodo.21322256 resolves to latest;
  tag `v1.22.0` → sealing commit `43d9c255af48db9bcc3c6eb341a153381b18c8e8`. No claim
  that v1.22.1 exists. Remaining v1.20.2 mentions are factual parity-baseline
  references only (main §3.6, README/REPRODUCE reproduce commands).
- README: DOI badge/citation keep the concept DOI (correct for "latest release");
  universal-gating wording corrected (§C); ATTENUATION gloss corrected.
- DOI URLs resolve via doi.org hyperlinks (`\href` in CAS); guards: 5 audit checks +
  2 pytest tests.

## C. Scope corrections (zero-drift limitation of the size-matched result)

- **Abstract:** control described as "isolates the challenger's nominal training size
  under zero drift (random proposals, balanced pools, self-contained SVC-RBF
  pipelines)"; equivalence "within the preregistered ±0.5-point CI90 margin"; gates
  "no measurable gain under this control"; 234 words.
- **Highlights (tex + md):** new 5-bullet set, all ≤ 85 chars, carrying "Under zero
  drift", "±0.5-pp margin", "Under that zero-drift control", "nominal evidence parity".
- **Graphical abstract:** rebuilt — flow Trigger ≠ superiority → check construction →
  check evidence conditions → nominal parity evaluated? (no/uncertain → validation may
  be useful; yes-under-zero-drift → ZERO-DRIFT CONTROL block: own preprocessing +
  2,000/class nominal size parity → mean BA equivalent within ±0.5 pp → no measurable
  point/strict gain in this control) + scope badge; no universal rule; legible in both
  PDFs and as GitHub thumbnail.
- **Introduction/contributions:** verdict and contribution (2)/(3) scoped to the
  zero-drift control at nominal parity.
- **Results §5.3:** heading "…the decisive zero-drift control"; finding (3) scoped.
- **Discussion:** Findings 1–2 scoped; permitted general conclusion added ("the
  measured value of the gate disappears when the evaluated representation and nominal
  sample-size asymmetries are removed"); prohibited "when comparability is already
  guaranteed" removed here and in practitioner guidance.
- **Conclusion:** rewritten with the authorized conditional formulation and scope.
- **README:** description, blockquote, method bullet and TL;DR scoped; conditional
  recommendation + zero-drift no-gain note added.

## D. Terminology

- "Nominal per-class sample-size parity" / "matched nominal per-class training size"
  used for the 512-vs-2,000 control; "Evidence Asymmetry" kept in the title.
- Method §3.7 caveat: matching nominal size does not establish equivalence in temporal
  coverage, diversity, subtype support, label quality, duplication, prevalence or
  effective sample size. Discussion: comparability "not a consequence of equal row
  counts alone".
- Detector score: "Within triggered decisions under the evaluated detectors, score
  magnitude provided no consistent incremental information…" (Intro, README,
  REPRODUCE); "not the lever"/"uninformative" absolutes removed; pre-threshold and
  performance-aware-detector caveats retained.
- ATTENUATION: abstract carries exactly one taxonomy sentence ("The registered taxonomy
  returned ATTENUATION because its sign-based future-value criterion remained
  inconclusive despite the near-zero mean"); banned glosses absent everywhere.

## E. Equivalence sensitivity (F1 naive-2000 vs never; CI90; margins preregistered)

| dataset | effect (pp) | CI90 | ±0.2 | ±0.5 (primary) | ±1.0 |
|---|---|---|---|---|---|
| CICIDS2017-PortScan | +0.185 | [−0.0995, +0.4940] | **not equivalent** | equivalent (by 0.006 pp — stated) | equivalent |
| UNSW-NB15 | −0.021 | [−0.0904, +0.0474] | equivalent | equivalent | equivalent |
| ToN-IoT | −0.009 | [−0.0471, +0.0289] | equivalent | equivalent | equivalent |

Source: `results/tables/v1_22_1_editorial/equivalence_margin_sensitivity.csv` (18
contrasts, pivoted from the sealed `equivalence.csv`; verdicts asserted identical to the
sealed flags and re-derived from the CI90). PortScan presented as margin-sensitive in
abstract and §5.3; conclusion stated as margin-dependent; no "identical"/"equal
performance" language.

## F. Evidence–validation trade-off (per proposal, nominal adjudicated labels)

BA-vs-never in pp [CI95]; naive-2000 = registered F1; 512-side and gate-vs-never cells
descriptive/uncorrected; gate gains at 2000 = registered F3 (0/6 Holm-significant).

| dataset | policy | cand. | probe | total | BA vs never [CI95] | gate gain vs naive [CI95] | commits/seed |
|---|---|---|---|---|---|---|---|
| PortScan | naive_512 | 1024 | 0 | 1024 | −1.70 [−2.05, −1.36] | — | 3.70 |
| PortScan | point_512 | 1024 | 32 | 1056 | −0.73 [−1.10, −0.38] | +0.97 [0.67, 1.31] | 1.87 |
| PortScan | strict_512 | 1024 | 32 | 1056 | −0.03 [−0.24, +0.16] | +1.67 [1.36, 2.00] | 0.23 |
| PortScan | naive_2000 | 4000 | 0 | 4000 | +0.19 [−0.15, +0.55] | — | 3.70 |
| UNSW | naive_512 | 1024 | 0 | 1024 | −0.65 [−0.77, −0.55] | — | 3.70 |
| UNSW | point_512 | 1024 | 32 | 1056 | −0.47 [−0.61, −0.33] | +0.19 [0.10, 0.30] | 2.27 |
| UNSW | strict_512 | 1024 | 32 | 1056 | −0.19 [−0.30, −0.10] | +0.46 [0.35, 0.58] | 0.67 |
| UNSW | naive_2000 | 4000 | 0 | 4000 | −0.02 [−0.10, +0.06] | — | 3.70 |
| ToN | naive_512 | 1024 | 0 | 1024 | −0.24 [−0.39, −0.10] | — | 3.70 |
| ToN | point_512 | 1024 | 32 | 1056 | −0.12 [−0.24, −0.01] | +0.12 [0.04, 0.23] | 3.13 |
| ToN | strict_512 | 1024 | 32 | 1056 | +0.00 [−0.08, +0.06] | +0.24 [0.12, 0.38] | 0.27 |
| ToN | naive_2000 | 4000 | 0 | 4000 | −0.01 [−0.05, +0.04] | — | 3.70 |

Supplementary block (point/strict-2000): all gate gains < 0.14 pp, 0/6 Holm-significant,
CI90-equivalent to naive-2000 within ±0.5 pp; commits/seed 3.07/0.50, 2.87/0.70,
3.50/0.07. Guardrails: all matched-size gate cells pass recall/FPR non-inferiority; at
512 the UNSW strict cell fails recall NI (replicated trade-off, stated).

**The comparison:** 512/class + gate = 1,056 nominal adjudicated labels/proposal vs
2,000/class + no gate = 4,000; the size upgrade costs 2×1,488 = **2,976 additional
candidate-training labels per proposal** against the 32-label probe. **Caveat (in
caption and text):** counts, not costs — inspected-flow acquisition of balanced attack
labels is not modeled; no economic dominance claimed in either direction; candidate and
probe labels not assumed equally costly to acquire.

Sources: 5 sealed `size_matched_own_transformer_001` CSVs + frozen config; sealed cells
asserted byte-identical; probe/candidate counts derived from config AND logs
(118.4/3.7 = 32; 3,788.8/3.7 = 1,024; 14,800/3.7 = 4,000).

## G. Editorial restructuring

- Historical `table_v2_confirmatory` re-captioned "Historical frozen-policy diagnostic"
  and relocated to new Supplementary §S2.11 (compact summary remains in §5.1/§5.5);
  decision-quality paragraph relocated to new §S2.10.
- VBC-SG compacted in main; framed as "a sequential decision-support instantiation for
  settings in which validation is chosen"; supplement retains full details.
- Pages: main 33 (=budget), supplement 30 (29+1, allowed), IEEE 25 (=budget).
- Words: abstract 234 (210–235); body 17,742 vs 17,889 baseline under the identical
  counting method (recorded v1.22.0 figure 18,088 under the prior method — budget met
  under any consistent convention). Details: `notes/v1_22_1_editorial_compression_report.md`.
- No scientific figure changed; prose-dropped CIs remain in tables/supplement/artifact.

## H. Tests and audits

- pytest **135/135** (new: `tests/test_v1_22_1_editorial_guards.py`, 17 tests;
  `test_claims.py` table sets updated for the two relocations).
- audit **625/625** (39 new v1221 checks: DA/scope/README/terminology/equivalence/cost
  table/historical/detector/ATTENUATION; 3 anchors updated).
- `verify_results_manifest`: 183/183 pinned match; 2 unpinned editorial extras
  (allowed until sealing); 0 orphans.
- PDFs: 0 undefined references, 0 undefined citations (main, supplement, IEEE).
- v1.22.0 integrity: manifest + hash-pin byte-identical (pytest-pinned); 21/21; 42/42;
  no new folder under `results/raw/`; no new seeds; no runner executed.

## I. Hostile review

`notes/v1_22_1_final_editorial_hostile_review.md`: **20/20 questions answered, 0
blockers.** Remaining asks that would need new matrices (full/mild-drift size-matched,
observed-data size-matched, VBC-SG under own-transformer, other classifiers at parity)
are declared future work / official-review scope.

## J. Recommendation

**READY FOR v1.22.1 SEALING**

---

STOP. Per protocol: no merge, no tag, no GitHub Release, no Zenodo, no new DOI, no
`results/final_manifest.json` update, no `MANIFEST.sha256` re-pin, no experiments.
Human checkpoint decides sealing.
