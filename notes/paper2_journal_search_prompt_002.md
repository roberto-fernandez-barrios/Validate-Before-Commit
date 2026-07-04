# Deep-research prompt v2 — find a target journal (ML-for-security aware)

Supersedes v1. **Reason:** Computers & Security (the v1 top pick) is ruled out — its Guide for Authors states
an explicit *moratorium (since early 2024) on submissions that feature AI or ML as significant components*,
which desk-rejects "applying an AI/ML technique to system security" work. Our paper is exactly that. The v2
prompt below forces the model to check each candidate for such exclusions and to target venues that welcome
ML-for-security / applied-ML empirical papers.

Paste the block below into a deep-research model.

---

```
ROLE: You are a scholarly publishing advisor. Recommend peer-reviewed JOURNALS that are the best real,
currently-active home for the paper described below. CRITICAL, non-negotiable requirement: this is an
ML-for-security / applied-ML paper, so you MUST verify, from each candidate venue's official Guide for
Authors / Aims & Scope / recent editorials, that the venue does NOT exclude or place a moratorium on
"AI/ML as a significant component" or on "applying ML techniques to security". Exclude any venue that does.
(Cautionary example: Elsevier's *Computers & Security* has, since early 2024, a moratorium on submissions
featuring AI/ML as significant components and will not consider ML-applied-to-security papers — do NOT
recommend it, and screen every candidate for a similar policy.) For every metric you report, give the year
and flag if approximate/unverified; never fabricate impact factors, acceptance rates, DOIs, or scopes.

PAPER (accurate one-paragraph description):
Title: "Validate Before Commit: Label-Efficient Safe Readaptation for Adaptive Network Intrusion Detection
under Concept Drift."
What it is: an empirical, methodological machine-learning paper with a network-security application. It
studies WHEN to retrain a deployed ML classifier under concept drift. Core finding: the field frames this as
a drift-DETECTION problem, but the operative variable is INCUMBENT-MODEL DEGRADATION (benefit of retraining
correlates with no-adaptation accuracy at r ~= -0.82 to -0.89, with CIs), which drift detectors cannot
observe; so drift-triggered retraining can be net-harmful. Contribution: a deployable, label-efficient
"validate-before-commit" decision gate — retrain a candidate but deploy it only if it beats the incumbent on
a small labeled probe (tens of labeled flows). It is pre-registered, evaluated with 30-seed 95% CIs across
two drift detectors and four downstream classifiers, tolerates label latency, fails safe under adversarial
(poisoned) validation labels, and beats both naive retraining and never-adapting where retraining is harmful.
Includes honest negatives (simple confirmation/cooldown policies and a zero-label variant both fail).
Evaluation: three public IDS benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT). ~6,000-word manuscript, reproducible
public artifact, Elsevier-style highlights + graphical abstract ready.
Character: MODEST algorithmic novelty; the value is the reframing, the decision-policy method, the
label-efficiency, and heavy rigor/robustness. One of the two drift detectors is a quantum-kernel MMD monitor,
used only as an ablation to show the detector family is not the lever (can be foregrounded as mild ML novelty
or kept minor, depending on venue).
The contribution generalizes beyond NIDS to "label-efficient safe model updating under concept drift", if
that broadens venue fit.

TASK: Return a RANKED shortlist of 8-12 venues in tiers:
  (A) best-fit Q1 that WELCOME ML/applied-ML for security (verified no AI/ML moratorium),
  (B) strong Q1/Q2 fallbacks,
  (C) 2-3 top-tier ML-security or systems-security CONFERENCE alternatives.
Consider APPLIED-ML journals (e.g. Expert Systems with Applications, Engineering Applications of Artificial
Intelligence, Knowledge-Based Systems, Machine Learning, Data Mining and Knowledge Discovery, Neurocomputing,
Applied Soft Computing, IEEE Transactions on Neural Networks and Learning Systems) AND security/network
journals that accept ML work (e.g. IEEE Transactions on Network and Service Management, IEEE Transactions on
Dependable and Secure Computing, IEEE Transactions on Information Forensics and Security, Journal of
Information Security and Applications, Computer Networks, IEEE Transactions on Information Forensics).
Screen EACH for AI/ML scope exclusions; state explicitly for each "no AI/ML moratorium found (source: ...)".

FOR EACH VENUE report:
  - Exact name + publisher.
  - JCR quartile + latest Impact Factor (and/or Scopus CiteScore + SJR quartile); year; flag if unverified.
  - AI/ML policy check: does it accept ML-applied-to-security empirical papers? cite the scope/guide.
  - Scope-fit rationale (2-3 sentences) for a decision-policy + label-efficiency paper with honest negatives.
  - Typical time-to-first-decision / review speed if known (flag if unknown).
  - Open-access model + approximate APC, and whether a no-fee route exists.
  - 1-2 recent (<=3 years) representative papers in that venue on adaptive IDS / concept drift / ML for
    intrusion detection / label-efficient learning (real titles + year).
  - Fit risks (e.g. "wants broader ML generality", "wants stronger algorithmic novelty", "prefers detection
    over policy", "security venue may see it as too ML / ML venue may see it as too security-specific").

ALSO ADVISE:
  - Realistic tier this paper lands in, given modest algorithmic novelty but strong rigor, reproducibility,
    robustness, honest negatives, and a reframing thesis. Be candid.
  - For the top pick: whether to foreground or background the quantum-kernel component, and 2-3 concrete
    title/abstract framing tweaks to maximize acceptance there.
  - Whether an applied-ML venue or a security venue is the better home for THIS paper, and why.
  - Any currently-open, verifiable special issue / CFP that matches (else say none found).
  - Submission-format notes for the top pick (LaTeX class, word limit, abstract length, highlights,
    graphical abstract, required statements: CRediT, data availability, competing interests, GenAI use).

FORMAT: tiered sections (A/B/C), ranked within each, then a short "recommendation" paragraph naming a single
top choice and a single safe fallback, each with a one-line justification and an explicit "AI/ML policy: OK"
confirmation. Prioritize venues indexed in JCR and Scopus. Prefer specificity and verifiability over breadth.
```
