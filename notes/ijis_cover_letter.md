# Cover letter — International Journal of Information Security (Springer Nature)

Local file, not part of the scientific artifact. Paste into the "Cover Letter" field of the
submission system; the manuscript files are listed in `notes/ijis_submission_checklist.md`.

---

Bilbao, 3 September 2026

Dear Editor-in-Chief,

We submit the manuscript *Candidate Comparability Before Promotion: Conditional Validation in
Adaptive Network Intrusion Detection* for consideration as an original research article in the
*International Journal of Information Security*.

**The question.** A drift alarm identifies change; it does not establish that the challenger it
triggers should replace the deployed network intrusion detector. Promotion is a security-relevant
integrity decision, because it changes the model that will face the next attack, and we show that
conclusions about it are conditional on two upstream conditions: how the challenger is constructed
and how much training evidence supports it.

**What the paper establishes.** On CICIDS2017, UNSW-NB15 and ToN-IoT, with bit-identical streams
and protocols frozen in version control before each confirmatory block, we find that
(i) incumbent-owned frozen preprocessing amplified apparent promotion harm, and the mean full-drift
harm did not persist with self-contained challenger pipelines; (ii) an exact-cleaned-feature-disjoint
sensitivity, which confines every identical feature vector to a single evaluation, training or probe
role, preserved a positive 512→2,000-per-class evidence effect in all three benchmarks (+0.53, +1.67
and +0.38 balanced-accuracy points) while showing that its materiality is benchmark-dependent and
that the gain is mainly a lower false-positive rate at approximately unchanged attack recall;
(iii) in a common-harness comparison of nine update policies, including label-free accuracy
estimators, a calibrated ensemble, replay and reference drift monitors, the apparent policy ranking
changed with candidate comparability and no policy globally dominated; and (iv) validation had
conditional value, helping evidence-disadvantaged challengers and adding no average benefit at
parity. Thirteen replays on real, chronologically ordered traffic showed no net harm from always
deploying, which delimits the external support of the controlled results without estimating harm
frequency.

**Contribution and fit.** The contribution is evaluation methodology for adaptive network-security
systems: challenger construction, training evidence and exact-value role separation should be
controlled and reported before harm, benefit or a policy ranking is attributed. Attack recall and
false-positive rate are carried as guardrails throughout, the trust assumptions of the evaluation are
stated explicitly, and adversarial manipulation of candidate data, alarms and probes is scoped as
future work rather than claimed as a defense. Related work covers recent adaptive NIDS
(CARAVAN, SPIDER, NOCTOWL, ADAWU-IDS) and the security literature on pragmatic NIDS assessment,
benchmark dataset artifacts and continuous model updating.

**Reproducibility.** Every reported number is generated from hash-pinned result files in the public
artifact, version v1.24.0 (exact DOI 10.5281/zenodo.22239106; concept DOI 10.5281/zenodo.21322256):
frozen protocols and configurations, the experiment runner, implementation tests, analysis scripts,
the sealed manifest and an automated claim audit. Public benchmark data are not redistributed; the
pipeline regenerates all outputs from them.

**Declarations.** The manuscript has not been published previously and is not under consideration
elsewhere; it is not an extension of a conference paper. All authors approved the submission and
have no competing interests. No funding was received for this study. The use of generative-AI
tools for drafting and editing support and for implementation and review of analysis scripts is
disclosed in the manuscript's declarations; all content was verified by the authors, who take full
responsibility for it.

We would be glad to suggest independent reviewers if useful to the editorial office.

Sincerely,

Roberto Fernández-Barrios (corresponding author), on behalf of all authors
Faculty of Engineering, University of Deusto, Avda. de las Universidades 24, 48007 Bilbao, Spain
roberto.fernandez.b@deusto.es · ORCID 0009-0003-5312-2634

Co-authors: Iker Pastor-López, Amaia Pikatza-Huerga, Pablo García Bringas (University of Deusto)
