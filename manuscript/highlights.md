# Highlights

Elsevier format: 3–5 bullet points, each ≤ 85 characters (including spaces).
(Character counts shown for verification; remove before submission.)

- Drift alarms don't reveal if retraining helps; model degradation does (r≈-0.85)   [79]
- Naive drift-triggered retraining can be net-harmful; never adapting can win        [75]
- Validate before commit: deploy a retrained model only if a small probe confirms gain [84]
- The gate needs only tens of labels and fails safe under 40% poisoned labels         [75]
- Safe across two detectors and four classifiers; pre-registered, 30-seed CIs         [75]

## Graphical abstract

`docs/img/graphical_abstract.png` (rendered by `python -m src.analysis.make_paper2_graphical_abstract`;
2599×840 px, above Elsevier's 1328×531 minimum). Problem → insight (detection ≠ decision, r≈-0.85) →
solution (validate-before-commit gate) → result (safe, label-efficient), with a robustness badge strip.
