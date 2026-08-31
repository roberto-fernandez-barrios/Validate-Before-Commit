# Hostile statistical preflight — post-KBS strengthening protocols

Scope: adversarial inspection of
`notes/post_kbs_common_harness_baselines_protocol_001.md` (B1) and
`notes/post_kbs_size_matched_drift_protocol_001.md` (B2), performed BEFORE any
implementation or execution. Checklist per the Phase B requirements; the E3 sign-rate
failure of the previous program is the reference pathology to avoid.

## 1. Can the registered rules distinguish a true null from small symmetric noise?

**B1.** The per-cell rule is two-sided and magnitude-aware: MATERIAL GAIN/COST require a
Holm-significant effect of |Δ| ≥ 0.5 pp; COMPATIBLE requires CI90 ⊂ ±0.5. Under a true
null with symmetric noise, GAIN/COST each require a ≥0.5-pp Holm-significant excursion
(FWER-controlled ≤ α per family), and COMPATIBLE is reached once precision suffices.
Attainability: the sealed own-transformer runs give seed-level SEs of 0.03–0.35 pp for
these contrasts (CI90 half-widths 0.06–0.6); all but the noisiest PortScan cells resolve
within ±0.5 at 30 seeds, and the UNRESOLVED label exists precisely for the remainder — it
can never be converted into a directional claim. **Verdict: rule is null-distinguishing;
no forced verdict; no sign-rate pathology.**

**B2.** Same structure on G2 (the size effect). Under the exchangeability concern that
invalidated a sign-based rule at zero drift: at full drift the challenger is NOT an
exchangeable copy of the incumbent (it samples the proposal-time mixture), so the null is
not forced by construction; and the classification is CI/margin-based, symmetric, with an
explicit SUB-MATERIAL/UNRESOLVED bucket. A true null lands in NO MATERIAL SIZE EFFECT
when precision allows and nowhere else. **Verdict: pass. The E3 problem is not repeated:
no criterion in either protocol references a sign rate, and future-value summaries are
locked to descriptive status.**

## 2. Checklist findings

| Risk | B1 | B2 |
|---|---|---|
| Outcome rules impossible to satisfy | None found: all four labels attainable (GAIN/COST by 0.5-pp effects seen in sealed analogues; COMPATIBLE by observed precision) | Same; SIZE COST is attainable (the frozen-policy S1.5 analogue was −4 to −5 pp) and SIZE BENEFIT likewise (+1.9 pp at zero drift) |
| Null conditions mechanically forcing one verdict | No: zero-drift cells could go any way for ATC/DoC (never evaluated there) | No: the drift cell is the genuinely open one; §1 above |
| Sign-only criteria pathological near zero | None present | None present (explicitly banned) |
| Hidden dependence between candidate sizes | n/a (single size) | **Identified and disclosed in the protocol itself (§2.2):** naive pair exactly proposal-coupled; gated cross-size contrasts only seed-paired. Analysis is bound to that statement |
| Leakage | Harness inherits the registered role-disjoint partitions; ATC/DoC validation samples drawn from the train partition at training time, disjoint from candidate batches by draw; no method reads sev(t) | Nested draw uses train pools only; probes/evaluation partitions unchanged |
| Non-comparable information budgets | Stated per policy (§3); DDM/ADWIN monitoring labels declared and reported; ATC/DoC use zero target labels by definition — a *different* budget, reported as a property, never hidden | Identical budgets across sizes except the size axis itself |
| Post-hoc method selection | Selection criteria frozen before results; Category C exclusions justified per method, in writing, before any run | n/a |
| Seed reuse | 5001–5030/5401–5402 virgin (repo-wide scan); one-pass stop rule | 6001–6030/6401–6402 virgin; 4242–4243 used for byte-parity comparison only, never evidence |
| Unfair baselines | ATC/DoC get the same instantiation as their published definitions and their v1 fidelity check; DDM/ADWIN are the `river` reference objects with a declared budget (the budget sweep precedent exists at S2.1); replay/ensemble are the strongest label-free rules from prior blocks, not straw men | Anchors byte-identical to the registered machinery |
| Multiplicity omissions | Three Holm families cover every confirmatory contrast; everything else labelled descriptive | Four Holm families; everything else descriptive |
| Future-value overinterpretation | Not used | Locked to descriptive |

## 3. Weaknesses accepted knowingly (stated so a reviewer does not discover them)

1. **B1 evaluates baselines at 512/class only.** Deliberate orthogonality with B2; a
   joint size × policy matrix would quadruple compute and entangle the two questions. The
   protocol says so and forbids transferring B1 conclusions to other sizes.
2. **B1's ATC/DoC target-label budget is zero by definition** — F3 (vs the point gate)
   therefore compares different information budgets; the protocol frames F3 as a trade-off
   mapping, and any "matches the point gate" statement requires COMPATIBLE on all six
   scenarios, not a win.
3. **B2's gated cross-size contrasts lose proposal-level coupling** after decision
   histories diverge; only seed-level pairing is claimed for them. G2 (the primary) is
   unaffected.
4. **Both protocols inherit the pool-based simulator's scope** (balanced batches at
   proposal-time severity); neither adds observed-data arms. This is stated in both scope
   sections; external-validity limits of the main paper apply unchanged.

## 4. Verdict

**Both protocols PASS the hostile preflight as designs.** No rule is unsatisfiable, none
is forced under the null, none uses sign frequencies, seed blocks are virgin, budgets and
coupling scopes are declared in advance, and each protocol pre-commits the sentence
templates its outcomes license. Authorization to implement and run remains a separate,
explicit decision and is NOT granted by this document.
