# Target venue, framing strategy, and cover-letter draft

Based on the deep-research venue search (2026-07). Full shortlist and metrics kept there; this note records
the decision and the submission assets.

## Decision

- **Top choice:** **Computers & Security** (Elsevier). Best thematic fit — applied IT-security research and
  operational security decisions; publishes concept-drift/adaptive-IDS work; broad empirical evaluation
  welcomed. IF ~5.4 (ScienceDirect) / Q1 IF ~6.8 (public JCR mirror). Hybrid OA (APC ~USD 3,190) or no-fee
  subscription route. Fast desk screen (~2 days to first decision reported).
- **Safe fallback:** **Journal of Information Security and Applications (JISA)** (Elsevier). Explicitly
  practice-driven; network security + security policies in scope; recent close precedents. Q2 IF ~3.7–4.4.
- **Aspirational:** **IEEE TDSC** (Q1 IF ~6.8) — reachable only if the gate reads as a *security mechanism*,
  not "careful evaluation". Higher novelty bar.
- **Operational-network reframe:** **IEEE TNSM** (Q1 IF ~5.7) — competitive if reframed as an operational
  network/service-management problem (overhead, window cadence, label latency, probe cost, stability).
- **Only if it reads as a security *method*:** IEEE TIFS (Q1 IF ~8). High novelty expectation; risk of
  "systems-evaluation, not forensics-method".
- **Applied-ML alternatives:** Expert Systems with Applications, Engineering Applications of AI,
  Knowledge-Based Systems — good, but require abstracting the gate beyond NIDS.
- **Conference alternatives (sharper, faster):** RAID, ACSAC, USENIX Security (highest bar).

Realistic self-assessment: modest algorithmic novelty + strong rigor/robustness/honest-negatives → this is a
**security-systems / applied-security** paper, best home a **security venue** rather than a pure applied-ML one.

## Framing strategy (applied to the manuscript)

1. **Title** centred on the deployment decision: *"Validate Before Commit: …"* (done; "Knowing When Not to
   Retrain" kept as alternative hook).
2. **Abstract opens with the strong negative:** *drift alarms are not a sufficient signal for safe retraining;
   the operative variable is incumbent-model degradation, which drift detectors cannot observe.* (done)
3. **Front-load deployability** before the detector: tens of labeled flows, stale probes up to 20 windows,
   robust to 40% label flips, four classifiers, two detectors, pre-registered 30-seed CIs, reproducible
   artifact. (done in abstract + should headline §1)
4. **Background the quantum-kernel component.** It is NOT in the title or keywords; in the abstract it appears
   only as a one-line "even changing the detector family does not change the conclusion". Keep it as an
   instrument/ablation in §3.2/§5.3. Avoid any "quantum advantage" language (there is none, by design) to
   prevent "quantum-washing" perception.

## Cover letter draft — Computers & Security

> Dear Editor-in-Chief,
>
> Please consider our manuscript, *"Validate Before Commit: Label-Efficient Safe Readaptation for Adaptive
> Network Intrusion Detection under Concept Drift,"* for publication in *Computers & Security*.
>
> Adaptive network intrusion detection systems retrain their classifiers to cope with concept drift, and the
> field treats the decision of *when* to retrain as a drift-detection problem. Our central finding is that this
> framing is incomplete and can be operationally harmful: across three public benchmarks (CICIDS2017,
> UNSW-NB15, ToN-IoT) drift-triggered retraining ranges from strongly beneficial to net-harmful, and — for a
> fragile deployed model — no adaptation outperforms every triggered strategy. We show the sign of the effect
> is governed by how degraded the deployed model already is (a correlation with confidence intervals across
> four downstream classifiers), a quantity drift detectors cannot observe; consequently the detector is not the
> operative lever.
>
> Our contribution is a deployable, label-efficient *validate-before-commit* gate that retrains a candidate but
> commits it only if it beats the incumbent on a small labeled probe. It needs only tens of labeled flows,
> tolerates label latency, and fails safe under adversarial validation labels; it is pre-registered, evaluated
> with 30-seed confidence intervals across two detectors and four downstream classifiers, and released as a
> reproducible artifact. We also report honest negatives — simple confirmation/cooldown policies and a
> zero-label variant both fail — that delimit the method.
>
> We believe this operational, evidence-driven contribution on safe adaptive deployment under imperfect
> supervision fits the aims and scope of *Computers & Security*. The work is original, not under review
> elsewhere, and all authors approve the submission. We have no conflicts of interest to declare.
>
> Sincerely,
> Roberto Fernández Barrios, on behalf of all authors.

## Pre-submission checklist

- [ ] Fill real Paper 1 reference (`@misc{fernandez_paper1}`) and proofread flagged refs.
- [ ] Convert manuscript Markdown → Elsevier LaTeX (elsarticle); ensure Fig 1–8 + 2b and Tables 1–6 render.
- [ ] Confirm C&S submission format (structured highlights, ~5 keywords, graphical abstract optional).
- [ ] Author list, affiliations, ORCIDs, funding/conflict statements, data-availability statement.
- [ ] Decide OA vs subscription (no-fee) route.
- [ ] Add LICENSE (MIT code / CC-BY-4.0 text) before making the repo public.
