# Amendment preflight — common-harness baselines amendment 001

Scope: hostile logic audit of `notes/post_kbs_common_harness_baselines_amendment_001.md` +
`configs/post_kbs_common_harness_baselines_v2.json`, performed BEFORE any implementation of
this experiment and with zero experimental information (seeds 5001–5030 never executed;
repository re-scanned at freeze). Rules only; no experimental data exists to audit.

## 1. Pre-execution status

- No `results/raw/post_kbs_common_harness*` or `results/tables/post_kbs_common_harness*`
  path exists; no runner code for this matrix exists. The amendment is therefore
  pre-implementation and pre-result by construction, and retaining seed block 5001–5030 is
  valid (nothing was ever run on it).
- The v1 protocol file is unmodified; v1 config retained with a `supersedes` pointer in v2.

## 2. Null-distinguishability of the amended rules

Per-cell rule unchanged in form (MATERIAL GAIN/COST need Holm-significant |Δ| ≥ 0.5 pp;
COMPATIBLE needs CI90 ⊂ ±0.5; UNRESOLVED absorbs the rest): two-sided, magnitude-aware,
attainable in both directions, no sign-rate criterion. Under a true null with symmetric
noise, GAIN/COST are FWER-controlled; COMPATIBLE is reached when precision suffices (the
sealed own-transformer runs put seed-level CI90 half-widths at 0.03–0.6 pp for these
contrasts at 30 seeds). S4 (ordering change) additionally requires BOTH a Holm-significant
material interaction AND a material classification flip — under a true null this is doubly
FWER-protected and cannot fire mechanically. **Pass.**

## 3. Specific risks checked

| Risk | Finding |
|---|---|
| Amendment conditioned on results | None exist; verified by path scan and seed scan at freeze |
| Double-testing B2's estimands | Prevented: anchor-vs-anchor contrasts (naive−never, gate−naive) are declared DESCRIPTIVE here; the registered hypotheses live in B2 (full drift) and the sealed zero-drift control |
| Hidden dependence across sizes | Disclosed: 512 arms use the plain draw; cross-size contrasts are seed-paired only; no proposal-coupling claimed (that is B2's mechanism) |
| Budget unfairness | Budgets documented per policy (amendment §3), not equalized; ATC/DoC keep their published zero-target-label definition with a 512-row training-time validation sample; DDM/ADWIN keep their 800 monitoring labels/stream; differences are reported, not hidden |
| probability=True side effects | sklearn binary SVC `.predict` is unchanged by the Platt layer and environment RNGs are separate, so never/naive references stay bit-comparable across arms; recorded as a fidelity test obligation |
| DDM/ADWIN not duplicated at 512 | Rationale frozen (their candidate construction equals naive's; trigger reads no candidate); the naive size contrast carries the size effect |
| Family bloat | 96 contrasts total across five Holm families, each family pre-declared with fixed membership; nothing conditions on observed outcomes |
| Seed reuse | 5001–5030/5401–5402 still virgin (re-scan at freeze); 4242–4243 parity-comparison only |
| Multiplicity omission | Every confirmatory sentence (S1–S4) maps to a pre-declared family; all else descriptive |

## 4. Verdict

**AMENDMENT PASSES the hostile preflight as a design.** Implementation may begin only after
the amendment commit exists; confirmatory execution only after every fidelity gate in
config §`fidelity_gates` is green. This document authorizes neither.
