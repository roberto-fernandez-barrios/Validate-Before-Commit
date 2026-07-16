## What changed since v1.13.0 (amendment 012 — fourth-round code review, executed)

A code inspection by the reviewer found three real bugs (all verified) plus a size-matching
confound. A registered program (predictions P1–P6 before any run): 24 arms, 30 seeds, zero
failures. Claims audit **367 → 380/380**; builds **38 pp CAS / 30 pp IEEE**.

**Three code bugs, fixed.**
- *Cumulative `cn` regularization was inverted.* The control scaled `C ∝ n` (weakening
  regularization as the cumulative set grows), the opposite of the documented `C ∝ 1/n`. Corrected
  to `C = 2·train_size/n_unique`. The zero-drift cumulative harm persists and slightly deepens under
  the correct (stronger) regularization (ToN-IoT −10.62 vs −9.46 at fixed C=1), so it is not a
  regularization artifact — the claim now holds in the documented direction.
- *McNemar α mismatch.* The manuscript said all three risk gates use α=0.10; the exact-McNemar
  gate's registered and runner default is α=0.05 (a stricter level). We corrected the text and, to
  rule out an artifact, additionally ran McNemar at α=0.10: still zero commits under zero drift.
- *The causal gate committed without a probe at early triggers.* When the observed probe is
  unavailable (t<9) the gate previously fell back to committing. A new `--no-probe-policy reject`
  keeps the incumbent instead; such triggers are rare (0.6–1.0 per stream), the causal arm now makes
  zero unvalidated commits, and the harm-regime result strengthens (ToN-IoT gate−naive +3.24
  [1.68, 4.93]). Every committed causal update is now probe-backed.

**An honest retraction.** The four-classifier zero-drift arms kept a 2000-vs-512 incumbent/candidate
sample-size asymmetry. Size-matching the candidate to 2000/class **removes** the zero-drift harm for
random forest, logistic regression and MLP (all within ±0.1 of zero) and **deepens** it for SVC-RBF.
So the size-robust replacement harm is specific to the fragile SVC-RBF learner; for robust learners
the default-budget harm was largely the candidate-size asymmetry. The claim that the harm
"generalizes across four classifiers" is retracted and reframed throughout (abstract, §5, Table 10
caption, Limitations).

**Also.** A strict-inequality (reject-ties) baseline recovers 50–88% of the ε=0 zero-drift harm at
zero cost, quantifying how much the statistical gates add beyond it; harmful-commit rates now carry
exact (Clopper–Pearson) intervals (ε=0 excludes zero; the risk-controlled gates report "zero
observed, upper bound 0.12–0.17", not "eliminates"); the replacement-variance reading is downgraded
to a hypothesis with an explicit frozen-transformer caveat and a symmetric-preprocessing A/B named
as the decisive future control; and the highlights and abstract are reworded to avoid a
factorial misreading of the model and generator sweeps.
