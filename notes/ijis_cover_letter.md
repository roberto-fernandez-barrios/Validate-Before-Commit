# Cover letter — International Journal of Information Security (Springer Nature)

Local file, not part of the scientific artifact. Paste into the "Cover Letter" field of the
submission system; the manuscript files are listed in `notes/ijis_submission_checklist.md`.

---

Dear Editor-in-Chief,

We submit the manuscript *Candidate Comparability Before Promotion: Conditional Validation in
Adaptive Network Intrusion Detection* for consideration as an original research article in the
*International Journal of Information Security*.

**The scientific proposition.** Promoting an adaptive network-intrusion-detection challenger is
a security-relevant integrity decision because it changes the model responsible for subsequent
attack detection. Conclusions about that decision — and rankings of promotion policies — are
conditional on how the challenger is constructed and how much evidence supports it. The
manuscript isolates those conditions with registered controls on three public benchmarks and
offers evaluation discipline and design guidance, not a universally validated deployment stack.

**What the paper establishes.** Using a bit-identical harness on CICIDS2017, UNSW-NB15 and
ToN-IoT, with protocols and magnitude-aware rules frozen before each block, we find that
(i) incumbent-owned frozen preprocessing amplified apparent promotion harm; with self-contained
challenger pipelines the mean full-drift harm did not persist; (ii) at zero drift the mean
deficit of 512-per-class challengers disappeared at nominal 2,000-per-class parity; and
(iii) under pool-constructed progressive drift, the final exact-cleaned-feature-disjoint
sensitivity retained positive, statistically resolved 512→2,000 effects of +0.53, +1.67 and
+0.38 balanced-accuracy points. The last effect is sub-material under the registered 0.5-point
rule, so the defensible result is benchmark-dependent, not homogeneous. The policy sensitivity
was partially robust: size-dependent ordering and absence of a globally dominant policy
survived, while earlier compatibility statements for one label-free estimator and the
calibrated ensemble required narrowing. No rescue experiment followed. Validation remains
conditional rather than universally beneficial.

**Fit with the journal.** The work is technical information-security research about evaluation
of adaptive network-security systems. It addresses when evidence supports replacing a deployed
detector, retains explicit attack-recall and false-positive-rate guardrails, and scopes
adversarial manipulation of candidate data, alarms and probes as future work rather than
claiming a poisoning defense. Related work is current through September 2026 and distinguishes
the decision interface from recent systems including CARAVAN, SPIDER, NOCTOWL and ADAWU-IDS.

**Reproducibility.** Every reported number is generated from hash-pinned result files in public
artifact version v1.24.0 (concept DOI 10.5281/zenodo.21322256; exact version DOI recorded in the
final submission metadata): frozen protocols/configs, the source-row overlap audit, the
experiment runner, implementation tests, confirmatory checkpoints, analysis scripts, manifest
and automated claim audit. The prior v1.23.0 release remains immutable. Public benchmark data
are not redistributed; the pipeline regenerates the outputs from them.

**Declarations.** The manuscript has not been published previously and is not under
consideration elsewhere; it is not an extension of a conference paper. All authors approved
the submission and have no competing interests. No funding was received for this study. The
use of an AI assistant for drafting/editing support and for analysis-script implementation is
disclosed in the manuscript's declarations, as the journal's policy requires; all content was
verified by the authors, who take full responsibility for it.

We would be glad to suggest independent reviewers if useful to the editorial office.

Sincerely,

Roberto Fernández-Barrios (corresponding author), on behalf of all authors
Faculty of Engineering, University of Deusto, Avda. de las Universidades 24, 48007 Bilbao, Spain
roberto.fernandez.b@deusto.es · ORCID 0009-0003-5312-2634

Co-authors: Iker Pastor-López, Amaia Pikatza-Huerga, Pablo García Bringas (University of Deusto)
