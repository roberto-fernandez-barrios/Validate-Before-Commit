# Deep-research prompt — find a target journal for the paper

Paste the block below into a deep-research model. It is grounded in the actual paper so the model returns
real, verifiable venues rather than invented ones.

---

```
ROLE: You are a scholarly publishing advisor. Recommend peer-reviewed JOURNALS (with a few top-tier
security/ML conferences as alternatives) that are the best fit for the paper described below. Accuracy is
critical: only real, currently-active venues. For every venue give verifiable metadata; if you are unsure of
a number, say so rather than inventing it. Do NOT fabricate impact factors, acceptance rates, or scopes.

PAPER (one-paragraph summary):
Title: "Knowing When Not to Retrain: Label-Efficient Safe Readaptation for Adaptive Network Intrusion
Detection under Concept Drift."
Field: machine learning for network security / intrusion detection (NIDS), concept drift, adaptive model
retraining, label-efficient (active-learning-adjacent) methods.
Core thesis: the field frames adaptive IDS as a DRIFT-DETECTION problem, but that is the wrong object. We
show, across three public benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) and multiple attack regimes, that the
value of drift-triggered retraining ranges from strongly beneficial to net-harmful; it is governed by how
degraded the deployed model already is (correlation r ≈ −0.82 to −0.89, with CI), a quantity drift detectors
cannot observe. The choice of detector (classical two-sample tests OR quantum-kernel MMD) is not the lever.
Contribution/solution: a deployable, label-efficient "validate-before-commit" gate — on each triggered drift
it retrains a candidate but deploys it only if the candidate beats the incumbent on a small labeled probe
(~tens of labeled flows). It is pre-registered, evaluated with 30-seed CI95, generalizes across two drift
detectors and four downstream classifiers, tolerates label latency (probes up to 20 windows stale), fails
safe under adversarial/poisoned validation labels (up to 40% flipped), and significantly beats both naive
retraining and never-adapting where retraining is harmful. Includes honest negative results (simple
confirmation/cooldown policies fail; a zero-label variant fails).
Methodological character: empirical systems/ML security paper; pre-registration; strong statistical rigor;
reproducible artifact; honest-negative and robustness-heavy; a security angle ("safe readaptation under
adversarial supervision"); modest algorithmic novelty (the contribution is the necessity + characterization +
label-efficiency of the decision gate, not a flashy new model).
Not: a quantum-advantage paper (quantum kernels appear only as one instrument that is shown NOT to be
decisive); not a theory paper; not a brand-new-dataset paper.

TASK: Return a RANKED shortlist of 8–12 venues in three tiers:
  (A) best-fit Q1 journals, (B) strong Q1/Q2 fallbacks, (C) 2–3 top-tier conference alternatives.
Consider BOTH security venues (e.g. Computers & Security, IEEE TDSC, IEEE TIFS, Journal of Information
Security and Applications, IEEE TNSM) AND applied-ML venues (e.g. Expert Systems with Applications,
Knowledge-Based Systems, Engineering Applications of AI, Machine Learning, Data Mining and Knowledge
Discovery). Judge fit specifically for: an empirical ML-for-security decision-policy paper with honest
negatives, robustness breadth, and pre-registration — not a pure detection or pure theory paper.

FOR EACH VENUE report, in a table or per-entry list:
  - Exact name + publisher.
  - JCR quartile + latest Impact Factor (and/or Scopus CiteScore + SJR quartile); state the year and flag if
    approximate/unverified.
  - Scope-fit rationale (2–3 sentences): why this paper fits the aims & scope; cite the venue's stated scope.
  - Typical time-to-first-decision / review speed if known (flag if unknown).
  - Open-access model and APC (approx.), and whether a no-fee option exists.
  - 1–2 recent (last ~3 years) representative papers in that venue on adaptive IDS / concept drift / ML for
    intrusion detection, to demonstrate topical fit (real titles + year).
  - Any fit risks (e.g. "expects stronger algorithmic novelty", "prefers detection over policy", "quantum
    framing may confuse reviewers").

ALSO ADVISE:
  - Which tier this paper realistically lands in given: modest algorithmic novelty but strong rigor,
    reproducibility, robustness, honest negatives, and a security-decision framing. Be candid.
  - Whether the quantum-kernel element helps or hurts venue fit, and whether to foreground or background it.
  - Whether a security venue or an applied-ML venue is the better home, and why.
  - 2–3 concrete framing tweaks (title/abstract emphasis) that would improve acceptance odds at the top pick.
  - Any special-issue / call-for-papers currently open that matches (only if you can verify it is real and
    current; otherwise say none found).

FORMAT: three tiered sections (A/B/C), ranked within each, then a short "recommendation" paragraph naming a
single top choice and a single safe fallback with one-line justifications. Prioritize venues indexed in JCR
and Scopus. Prefer specificity and verifiability over breadth.
```
