## What changed since v1.10.0 (amendment 009 — the "highly recommended" experiment menu, executed)

With the stop-rule lifted, this release executes the reviewer's full *highly-recommended* list:
a registered program (predictions P1–P4 fixed before any run) of 92 arms, 30 seeds each, zero
failures. Claims audit **324 → 345/345**; builds **35 pp CAS / 28 pp IEEE**.

**The zero-drift harm is not a property of SVC-PCA8.** The strongest remaining objection was that
the harm was read off one fragile pipeline. Under zero drift, naive always-deploy is net-harmful
for **every** downstream model — random forest, logistic regression, MLP and full-feature SVC
(no PCA) alike, in all twelve model×regime cells — and the exact-McNemar gate recovers **all** of
it (+0.00). Mild-drift net-harm stays SVC-specific (robust models resist it), so the SVC caveat now
bounds only the *drift-driven* harm, not the healthy-incumbent *replacement* harm.

**The harm is a property of the update generator, not full replacement.** A registered sweep of
update generators under zero drift shows sliding-window (ToN −7.21), replay 50/50 (−4.03) and —
most tellingly — a **cumulative candidate trained on *all* observed windows (−9.46, the deepest
harm of any generator)** are all net-harmful; only the calibrated ensemble escapes. That the
all-data cumulative generator is the *worst* refutes the "just use more data" reading directly.
The McNemar gate recovers the loss for every generator. This is candidate governance at its
strongest: validate the *proposal*, whatever produced it.

**Where the harm hides: tail and worst-case metrics.** Averaging over 100 windows understates the
risk. In the ToN-IoT harm regime the naive arm's worst-window gap below no-adaptation is −5.24 and
its CVaR@10% is −4.74 — roughly 3–4× the −1.38 mean gap — while the gate keeps the entire lower
tail non-negative.

**An anytime-valid confidence-sequence gate.** A new gate (`labeled_probe_cs`, Robbins
normal-mixture) commits only when a lower confidence sequence on the per-flow correctness
difference exceeds zero, bounding the probability of *ever* committing a non-beneficial update by
α uniformly. At probe budgets ≤ 64 it is conservative enough to essentially never commit — correct
in low-headroom regimes, the risk-averse end of the point/LCB/McNemar/sequential frontier.

**A sixth chronological replay, reported as a negative.** ToN-IoT lacks timestamps
(chronological ordering infeasible; documented). An intra-day CICIDS Tuesday stream was staged
instead, but the incumbent collapses there too (its training window sees only FTP-Patator, the
stream only SSH-Patator — a new attack sub-type), so a healthy-incumbent chronological stream
remains confined to the external UNSW-NB15 timeline. Six chronological replays now, no
chronological net-harm observed — stated plainly as the outstanding external test.

**Code and reproducibility.** Additive runner options (`--adapt-strategy {cumulative,replay}`,
`--adaptation-gate labeled_probe_cs`) leave existing paths unchanged. New aggregators, a
CSV-emitted table (`tab:amendment009`), and the Tuesday staging script ship in the artifact;
manuscript, Limitations, abstract and `REPRODUCE.md` are synced; the claims audit gains 21 checks.
