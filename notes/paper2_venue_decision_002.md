# Venue decision (v2) and TNSM adaptation

Based on the ML-for-security-aware deep-research (v2 prompt). Supersedes the C&S plan
(`paper2_venue_and_cover_letter_001.md`, ruled out by the AI/ML moratorium).

## Decision
- **Primary target: IEEE Transactions on Network and Service Management (TNSM).** JCR Q1 (IF ~5.4, 2024
  data), no AI/ML moratorium, explicitly welcomes *applied contributions (experiences/experiments with actual
  systems)* and lists "AI in Network Management" and "Network Security and Privacy" in scope. Adaptive-NIDS
  retraining is a network-operations decision — a natural fit; tolerant of modest algorithmic novelty.
- **Fallback ladder:** IEEE TDSC (if reviewers signal the security/dependability angle is strong) →
  Expert Systems with Applications (applied-ML, safe/faster) → Knowledge-Based Systems / Engineering
  Applications of AI → JISA (lower-bar security). Conferences on the same cycle: RAID (best cultural fit),
  DIMVA (~24% accept), ACSAC.
- **Avoid:** Computers & Security (AI/ML moratorium), IEEE TIFS (forensics/algorithmic-novelty bar).

## Framing tweaks applied for TNSM
1. **Lead with the decision + operational angle.** Abstract now opens on the operational retraining decision
   and the degradation-not-drift reframing, with r ~= -0.82 to -0.89 as headline evidence. Title already
   decision-centred ("Validate Before Commit").
2. **Background the quantum kernel** to a single methods sentence (one of two interchangeable detectors);
   "quantum" is out of the title, keywords, and abstract. It is a negative result, not a contribution.
3. **Elevate the security-systems contribution:** adversarial/poisoned-label fail-safe (robust to 40% flipped
   probe labels) and label-latency tolerance are foregrounded — these differentiate it from a generic drift
   paper and are what TNSM/security reviewers reward.

## Submission format (TNSM / IEEE)
- **LaTeX:** IEEEtran, `manuscript/main_ieee.tex` (two-column, `figure*`/`table*` full-width floats,
  `\bibliographystyle{IEEEtran}`). Build via `src.analysis.make_paper2_latex ieee`.
- **Abstract:** trimmed to 244 words (IEEE prefers ~150-250; Elsevier hard cap was 250 — satisfied).
- **Index Terms / keywords:** set (network management, not "network security", to match TNSM).
- **Required statements to add before submission:** author CRediT/contributions, funding, declaration of
  competing interests, data availability, and — per publisher policy — a generative-AI-use declaration if
  applicable (author's responsibility/decision).
- **Length:** IEEE Transactions have no hard word cap but levy overlength page charges beyond the regular
  page count; current draft (~6k words + 9 figures + 6 tables) may exceed the free page count — consider
  moving Tables 4-5 / Figs 2b, 3, 7 to an appendix or supplementary material if page pressure arises.
- **Author bio/vitae + photo:** IEEE requests a short biography per author.

## Elsevier fallback kept
`manuscript/main.tex` (elsarticle) remains ready for ESWA/JISA if TNSM rejects; regenerate both with
`make_paper2_latex_tables` then `make_paper2_latex elsevier|ieee`.
