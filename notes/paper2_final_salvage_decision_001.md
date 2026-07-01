# Paper 2 Final Salvage Decision 001

## Final verdict

Q1 is no longer a credible target for the current Paper 2.

The universal or robust quantum-advantage claim is not supported.

The safe-readaptation pivot was scientifically legitimate, but the pre-registered Phase 1 did not pass.

The project remains publishable as a strong Q2 paper if framed as an operational characterization of the limits of drift-triggered IDS readaptation.

## Final framing

Working title:

When Drift Detection Should Not Trigger Readaptation:
Operational Limits of Quantum-Kernel MMD for Adaptive Intrusion Detection

## Central claim

Detector-triggered IDS readaptation is regime-dependent. It can help, marginally help, or harm downstream IDS performance. QK-MMD provides useful operating profiles in selected CICIDS2017 regimes but does not show robust external quantum advantage. Simple k-of-n/cooldown policies are insufficient to guarantee safe readaptation.

## Stop rule

No more datasets.
No more feature maps.
No more policy grids.
No more Q1 rescue attempts.

Proceed to manuscript writing.

## Final route

Write a Q2-strong paper.

Main narrative:

1. Motivation: adaptive IDS needs drift monitoring, but drift detection is not the same as safe readaptation.
2. Method: compare QK-MMD and classical drift monitors as readaptation triggers.
3. CICIDS2017: QK-MMD shows useful regime-dependent profiles.
4. External validation: UNSW weak/mixed, ToN-IoT harm regime.
5. Safe-readaptation diagnostic: simple policies fail to reliably prevent harm.
6. Conclusion: future adaptive IDS needs decision-level readaptation policies, not just more sensitive drift detectors.

## Final research questions

RQ1. Do QK-MMD drift monitors provide robust operational advantages for IDS readaptation across network attack regimes?

RQ2. When does detector-triggered readaptation improve, marginally affect, or harm downstream IDS performance?

RQ3. Are simple safe-readaptation policies sufficient to prevent harmful updates?

RQ4. What are the operational limits of using drift detectors as readaptation triggers in adaptive IDS?

## Final contributions

C1. Multi-regime evaluation of QK-MMD and classical drift monitors as readaptation triggers for IDS.

C2. Evidence of useful QK-MMD operating profiles in selected CICIDS2017 regimes.

C3. External validation showing no robust QK advantage across UNSW-NB15 and ToN-IoT.

C4. Identification of beneficial, mixed, and harmful readaptation regimes.

C5. Pre-registered diagnostic showing that simple k-of-n/cooldown policies do not reliably solve harmful readaptation.

## Message to director

Hemos cerrado honestamente la ruta Q1. La ventaja cuántica robusta no replica externamente y el pivote de safe-readaptation, aunque científicamente legítimo, no superó los criterios pre-registrados. Pero el proyecto sigue siendo sólido como paper Q2 y como capítulo de tesis: muestra una caracterización operacional amplia, con resultados positivos y negativos, y evidencia que el problema real no es solo detectar drift sino decidir cuándo readaptar sin dañar el IDS. Mi recomendación es parar experimentos y escribir el paper con ese framing, sin sobreprometer ventaja cuántica.
