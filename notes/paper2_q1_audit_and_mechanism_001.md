# Paper 2 — Q1 Audit + Mechanism Law

**Trigger:** Two questions from the student: (1) does the oracle-regret / decision-framing work unlock Q1? (2) symmetrically to the naive-oracle trap I caught, could a *hidden* methodological flaw be *concealing* a Q1?
**Method:** ran real audits on existing data (no new experiments), plus a code read of the retraining procedure.

---

## TL;DR

- **No hidden Q1.** I audited the four strongest "could this be suppressing a positive?" candidates. Three doors closed cleanly; the fourth (retraining protocol) turned out to *inflate* the benefit results, not hide anything. The absence of a Q1 win is real, not an artifact.
- **The audit made the paper stronger:** a clean mechanistic law — `corr(base no-adapt BA, adaptation benefit) = −0.894` across 7 regimes × 3 datasets — unifies the whole story and blunts the "one dataset" attack on the harm finding.
- **Q1 is reachable, but only via one more genuine contribution** (a label-efficient policy that predicts adaptation benefit), which requires a bounded-but-risky Phase 2 and overrides the stop rule. The current evidence is a **strong Q2** and the foundation for that Q1 attempt.

---

## 1. The mechanism law (new main result)

Across all regimes, the benefit of adaptation is almost perfectly predicted by how degraded the deployed model already is:

| Regime | base no-adapt BA | best adaptation gain (pts) |
|---|---:|---:|
| CICIDS DDoS | 0.698 | +19.50 |
| CICIDS Wednesday | 0.766 | +11.89 |
| CICIDS WebAttacks | 0.843 | +7.65 |
| CICIDS PortScan | 0.877 | +6.20 |
| UNSW DoS | 0.840 | +1.39 |
| UNSW Recon | 0.846 | +0.34 |
| ToN-IoT Scanning | 0.920 | −0.62 |

**Pearson r = −0.894.** Interpretation: adaptation helps iff drift has degraded the deployed model below what a freshly-fit current-window model achieves. Retraining *replaces a well-generalized model with a narrowly-fit one*; that is a gain only when the deployed model has already fallen far enough. **The detector is blind to this** — it measures distribution change, not model degradation. This is the actionability gap, now quantified as a near-deterministic law rather than a per-dataset anecdote.

Promote this to a **main-paper result and figure** (scatter: base BA vs gain, r=−0.894). It is the single most general, most defensible finding in the campaign and it turns ToN-IoT from "one embarrassing dataset" into "the predicted endpoint of a cross-dataset law."

---

## 2. Audit: could a flaw be *hiding* a Q1? (four doors)

### Door A — Does the 100-window average dilute an early QK advantage? → CLOSED
Time-resolved (early w0–19 vs late w80–99): in CICIDS, QK-ZZ ≈ best classical in *both* bins (early gains ~0.2 pts for all; late gains within ±1 pt). No concentrated early edge hidden by averaging.

### Door B — Does QK trigger earlier (faster recovery) than the mean shows? → CLOSED (mildly anti-QK)
QK-ZZ first-adaptation window is *later* than the best classical (e.g. Wednesday 29.4 vs 12.0; DDoS 25.9 vs 9.9). QK's higher AUC on *synthetic* drift does **not** translate into earlier triggering on *real* progressive drift. Warns against overselling the AUC-by-severity motivation.

### Door C — Is QK handicapped by a mis-calibrated shared threshold? → CLOSED
Per-detector trigger-rate (0.02–0.05) and n_adaptations sit squarely inside the classical range in every regime; QK is never an outlier. No calibration handicap inflating or suppressing QK.

### Door D — Retraining protocol → NOT hiding a Q1; it *inflates* the benefit
Code (`run_paper2_progressive_readaptation.py:488–497`): on trigger, the model is refit via `sample_balanced_from_distribution(pools, …)` with **true labels, balanced classes, sampled at current severity**. Retraining is done under near-ideal, *supervised* conditions.
- This **strengthens the harm finding**: adaptation hurts in ToN-IoT *despite* ideal labels — it cannot be dismissed as bad pseudo-labels or imbalance. Real deployments (no labels) would fare equal or worse.
- This **weakens the benefit finding**: the +6…+19 pt CICIDS gains are an *optimistic* upper bound; realistic label-scarce retraining would help less.
- Net for the user's question: this confound cannot be *hiding* a Q1 — it flatters the positive results, not suppresses them.

**Conclusion:** no methodological flaw is concealing a Q1. The one unresolved confound (ToN-IoT 88-dim / atan_standard / q_reps=1 scaling possibly handicapping QK externally) cannot overturn the harm result, because **classical detectors also lose to no-adaptation there** — the harm is detector-agnostic.

---

## 3. Does the decision-framing work unlock Q1? (precise answer)

**It raises the floor and the ceiling, but does not cross into safe-Q1 on its own.**

- Upgrades: oracle-regret (honest, CI-bounded) + the −0.894 mechanism law + metric-robustness (F1) + detector-invariance move the paper from "clear Q2" to **strong Q2 / Q1-borderline** at measurement/diagnostic-friendly venues.
- Ceiling blockers that remain: (i) **no deployable solution** — top venues reward methods, and Phase 1 heuristics failed; (ii) benefit magnitudes rest on **optimistic true-label retraining**; (iii) the *positive* half is still CICIDS-heavy.

**Revised probabilities:** Q2 ~75–80% (up). Q1 as-is ~20–25% (up from ~10–20%, thanks to the mechanism law). Q1 ~40–50% **iff** a label-efficient decision policy works (see §4).

*(This is a genuine, honest update to the flat "Q1 dead" in `paper2_final_salvage_review_001.md` §2. The student's Socratic push was correct: the mechanism law is a real, general contribution that narrows the gap.)*

---

## 4. The one honest Q1 path (well-motivated now, but risky)

The −0.894 law says: **adapt iff the deployed model has degraded.** So the deployable contribution that would earn Q1 is a policy that estimates *deployed-model degradation* (not distribution change) without labels, and gates adaptation on it.

- **Why it's principled, not another arbitrary grid:** it targets the exact quantity the mechanism law identifies, unlike the failed Phase-1 k-of-n/cooldown heuristics.
- **Why it's hard (the honest catch):** in the current setup labels exist at adaptation time, so a validation gate would work *trivially and circularly*. A real contribution needs a **label-scarce / unsupervised proxy** for "will retraining help" (e.g. deployed-model confidence collapse, agreement between deployed and candidate models on unlabeled current data, or a tiny labeled probe budget). This is a genuine open research problem — it might not work.
- **Cost:** a bounded Phase 2 on the 3 representative regimes (benefit/marginal/harm) reusing the existing pipeline. **It breaks the pre-registered stop rule** — do it only as a deliberate, eyes-open Q1 bet, pre-registered, with a hard stop.

**Decision fork for the student + director:**
- **Path 1 (safe):** write the strong Q2 now (mechanism law as centerpiece). Floor guaranteed (~75–80%).
- **Path 2 (Q1 bet):** one pre-registered Phase 2 on a label-efficient degradation-gated policy. If it captures meaningful regret without harming benefit regimes → real Q1 shot (~40–50% conditional). If it fails → fall back to Path 1 with an even stronger negative. Overrides the stop rule; real risk of another null.

---

## 5. What to change in the manuscript plan

1. **Add the mechanism law (r=−0.894) as a main result + figure.** It is now the paper's spine, sharper than the qualitative taxonomy.
2. **Add a Threats-to-Validity subsection** stating the true-label retraining confound explicitly (benefits optimistic, harm conservative) — pre-empts the strongest honest attack and turns it into a strength for the harm claim.
3. **Do not oversell the AUC-by-severity motivation** — QK triggers *later* on real drift; frame detection power as motivation-only, not a practical advantage.
4. Keep the Q1-vs-Q2 fork (§4) explicit in the project decision record.

*No commit. No experiments. All audits are re-aggregations of existing window data + one code read.*
