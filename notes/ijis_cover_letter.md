# Cover letter — International Journal of Information Security (Springer Nature)

Local file, not part of the scientific artifact. Paste into the "Cover Letter" field of the
submission system; the manuscript files are listed in `notes/ijis_submission_checklist.md`.

---

Dear Editor-in-Chief,

We submit the manuscript *Candidate Comparability Before Promotion: Conditional Validation in
Adaptive Network Intrusion Detection* for consideration as an original research article in the
*International Journal of Information Security*.

**The scientific proposition.** Published conclusions about adaptive network intrusion
detection — whether promoting a retrained challenger harms the deployed detector, and which
update policy is preferable — can change materially when the incumbent and the challenger are
not comparable in how they were constructed or in how much evidence supports them. The
manuscript isolates two such asymmetries under preregistered controls and shows that
controlling them changes those conclusions on three public NIDS benchmarks. The contribution
is a methodological result about how adaptive security systems must be evaluated before a
promotion decision is interpreted or automated; it is not a new detector, a new drift monitor
or an incremental application of an existing learner to standard datasets.

**What the paper establishes.** Using a common bit-identical harness on CICIDS2017, UNSW-NB15
and ToN-IoT, with protocols frozen in version control before each block ran, we find that
(i) incumbent-owned frozen preprocessing amplified the apparent harm of promotion: with
self-contained challenger pipelines the mean full-drift harm does not persist; (ii) nominal
candidate-evidence size matters in both regimes: at zero drift the mean deficit of
512-per-class challengers disappears at 2,000-per-class parity, and under real drift the same
nested intervention improves promotion outcomes by +0.82, +1.66 and +1.00 balanced-accuracy
points across the three benchmarks (a registered, homogeneous effect); (iii) a registered
common-harness comparison of published label-free accuracy estimators (ATC, DoC), reference
drift monitors (river DDM and ADWIN), a calibrated ensemble, replay retraining and labeled-probe
validation finds that no policy dominates and that the apparent ordering of policies itself
depends on whether the candidate generator is comparable. Validation therefore emerges as
conditional: labeled-probe gates help when challengers are evidence-disadvantaged, add no
average benefit at evidence parity, and can impose a measurable cost. We do not claim that any
evaluated policy is state of the art, and we state explicitly that no end-to-end published
adaptive-NIDS system matched the decision problem closely enough to be reproduced faithfully.

**Fit with the journal.** The work is technical information-security research on the
operation of deployed network-security systems; it belongs to the evaluation-discipline
lineage the journal's readership knows (TESSERACT, "dos and don'ts" of ML in security) and it
addresses a decision — when to replace a deployed detector — that security operators face
directly. The manuscript follows the journal's format: Springer two-column LaTeX template,
numbered references with DOI links, a 212-word abstract, six keywords, and a complete
Statements and Declarations section. A 46-page supplement (Online Resource 1) carries the
full tables, protocols and robustness analyses.

**Reproducibility.** Every number in the manuscript is generated from sealed result files in
a public artifact (concept DOI 10.5281/zenodo.21322256; version 1.23.0): frozen protocols and
amendments, the experiment runner and analysis scripts, 207 hash-pinned result CSVs, an
experiment ledger and an automated claim audit that re-checks the manuscript against the
artifact. The public benchmark datasets are not redistributed; the pipeline regenerates all
outputs from them. The Data Availability Statement in the manuscript gives the identifiers.

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
