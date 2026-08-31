# CHECKPOINT — Confirmatory result of the amended common-harness baselines experiment (B1)

Date: 2026-08-31. Branch: `post-kbs-hardening`.
Protocol: `post_kbs_common_harness_baselines_protocol_001.md` (a68c90e) + amendment 001
(5a4ce6f, pre-implementation). Implementation: commit 9f58b6c. Analysis
(`make_post_kbs_common_harness_001.py`): committed before the run; executed once,
unmodified, paper2 environment.

## A. Execution record

- Seeds: exactly 5001–5030 (n=30). Arms: **96/96 COMPLETE** (`--validate-complete`);
  zero FAIL lines from any worker.
- Provenance: every arm `mode=run`, `working_tree_dirty=false`, source commit 9f58b6c.
- Runtime: 228 min summed arm time across 3 parallel workers (registered `--only-arm`
  CLI; wall-clock ≈ 80–95 min); 38–298 s per arm.
- One launch defect, fully documented: the first combined launcher started only the
  PortScan worker (a shell-function scoping error killed the other two BEFORE any arm of
  theirs ran — "command not found", nothing partial executed); the UNSW and ToN groups
  were immediately relaunched with self-contained loops. No arm was retried, no seed
  substituted, no parameter changed; the arm set and seeds are exactly the registered
  ones and every completion marker is first-execution.

## B. Registered primary results (@2,000/class; Holm within family; 30 seeds)

**PF1 — zero-drift loss avoidance (policy − naive):** at nominal evidence parity there is
essentially NO zero-drift loss left to avoid (descriptive naive₂₀₀₀−never = +0.25/+0.07/
+0.02, while naive₅₁₂−never replicates the sealed residual harm on a third fresh seed
block: −1.66/−0.58/−0.35). All PF1 cells COMPATIBLE/UNRESOLVED except calibrated ensemble
on ps_zero (**+1.46, MATERIAL GAIN**). Consequently **no policy attains statement S1** —
the loss the label-free alternatives were previously priced against disappears at parity.

**PF2 — full-drift benefit retention (policy − naive):**
- **ATC: COMPATIBLE ×2, UNRESOLVED ×1** (−0.65 ps / +0.10 ton / −0.22 unsw) — retains the
  full-drift benefit within the margin.
- **Calibrated ensemble: COMPATIBLE ×3** (−0.09/−0.23/−0.42).
- **DoC: MATERIAL COST ps (−2.59) and unsw (−0.59); COMPATIBLE ton (+0.21)** → S2 holds.
- **Replay 50/50: MATERIAL COST ×3** (−0.89/−1.22/−2.07) → S2 holds.
- **river-DDM: MATERIAL COST ×3** (−0.78/−1.81/−2.67) → S2 holds.
- **river-ADWIN: MATERIAL COST ×3** (−8.73/−2.50/−4.06; barely fires) → S2 holds.

**PF3 — published estimators vs the point gate:** ATC vs point **COMPATIBLE on 5/6**
(UNRESOLVED ps_full, −0.73) → S3 narrowly not attained; **DoC vs point MATERIAL COST on
ps_full (−2.67) and unsw_full (−0.58)**, COMPATIBLE ×4. The exploratory-harness pattern
"DoC beats the gate in the harm regime" does NOT reproduce under the final harness at
parity (ton_full DoC−point = +0.01, COMPATIBLE).

## C. Registered secondary results

**SF4 (512/class):** with under-evidenced challengers every label-free alternative gains
at zero drift (enscal +2.93/+0.36/+0.20; doc +1.93/+0.44/+0.40; atc +1.65/+0.26/+0.25 —
because naive₅₁₂ is harmful there), and ATC/DoC surrender full-drift benefit on ps
(−1.82/−3.63) while gaining on ton (+0.48/+0.78) — the Block-III texture, now on the
final harness.

**SF5 + S4 (ordering change with size):** interactions are uniformly ≤ 0 where resolved
(15 Holm-significant cells, all negative). **S4 fires for ATC** (ps_zero: MATERIAL GAIN at
512 → COMPATIBLE at 2,000) **and for the calibrated ensemble** (ps_full and ton_full:
MATERIAL GAIN at 512 → COMPATIBLE at 2,000). **S4 does NOT fire for point, strict, or
DoC.** Reading: the measurable value of every evaluated safeguard — labeled gates and
label-free alternatives alike — concentrates where candidate evidence is asymmetric.

**Descriptive anchors (@2,000, uncorrected):** point−naive: +0.08/−0.00/+0.20 (full),
+0.24/+0.02/+0.01 (zero); strict−naive: −0.16/−0.23/−0.22 (full; unsw resolved negative),
+0.39/−0.01/−0.03 (zero). Consistent with B2's registered G3.

## D. Guardrails (language-gating only; principal NI margins)

Numerous FPR non-inferiority failures at full drift for the always-deploy-on-fire and
label-free policies (worst: ADWIN ΔFPR +9.5 pp on unsw_full; replay +4.8; DDM +6.4), and
recall failures for ATC/DoC/enscal/ADWIN on ps_full (ADWIN Δrecall −15.0). Full panel in
`security_metrics.csv`; no safety language is licensed for the failing cells.

## E. Statements (frozen S1–S4, evaluated literally)

S1: none. S2: DoC, replay, DDM, ADWIN. S3: none (ATC misses only via one UNRESOLVED
cell). S4: ATC, enscal. Everything else: "no material ordering change was resolved".

## F. Scope

Pool-based harness, SVC-RBF, KS-max, balanced streams, 30 seeds; anchors descriptive by
amendment; no SoTA ranking, no adaptive-NIDS-system row, no cross-experiment pooling. The
manuscript is NOT modified in this phase.
