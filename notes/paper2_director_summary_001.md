# Paper 2 — Director Summary

**Prepared by:** Claude Sonnet 4.6  
**Date:** 2026-06-26  
**Branch:** paper2-expensive-downstream  
**Status:** Pre-submission review — single dataset completed, second dataset pending

---

## 1. Objetivo del paper

Evaluar si QK-MMD (Quantum Kernel Maximum Mean Discrepancy) puede actuar como detector de drift en sistemas IDS adaptativos, con el objetivo de decidir cuándo reentrenar el clasificador de intrusiones. Se compara frente a cuatro baselines clásicos: Energy distance, MMD-RBF, KS-max y JSD.

La contribución central no es demostrar que QK es mejor en rendimiento bruto, sino que define un **perfil operacional diferente**: con distintos trade-offs entre frecuencia de readaptación, rendimiento downstream y coste computacional.

---

## 2. Pregunta científica

**¿Proporciona QK-MMD un punto operativo superior o complementario frente a detectores clásicos para decidir cuándo reentrenar un clasificador IDS adaptativo bajo drift progresivo?**

Reformulada de forma falsable: ¿Consigue QK-MMD ZZ reducir el número de readaptaciones necesarias manteniendo rendimiento downstream comparable, en regímenes de drift progresivo adversarial?

---

## 3. Experimentos realizados, agrupados por pregunta

### Pregunta 1: ¿Detecta QK mejor el drift artificial controlado?

**Experimento:** Controlled streaming con drift sintético a 5 niveles de severidad (0.2 → 1.0).  
**Resultado:** QK PauliXZ y ZZ alcanzan AUC 0.918 en severidad máxima vs MMD-RBF 0.800.  
**Uso en el paper:** Motivación. Justifica por qué QK puede producir un timing de triggers diferente.

### Pregunta 2: ¿Traduce esa mejor detección en mejor rendimiento downstream bajo drift progresivo real?

**Experimento:** Progressive readaptation en CICIDS2017, 3 escenarios (Wednesday, PortScan, DDoS), 30 seeds, 100 ventanas post-drift.  
**Resultado:** Ver sección 4.  
**Uso en el paper:** Resultado principal.

### Pregunta 3: ¿Es el beneficio robusto frente a distintos regímenes de coste operacional?

**Experimento:** Actionable utility analysis (Wednesday). Grid sobre λ (coste de readaptación), γ (coste de runtime detector), η (coste de nuisance triggers).  
**Resultado:** QK supera a Energy distance con CI95 estricto cuando λ≥0.5 y γ≤0.05.  
**Uso en el paper:** Marco operacional. Delimita en qué condiciones QK es preferible.

### Pregunta 4: ¿Dispara QK más alarmas falsas frente a drift benigno?

**Experimento:** Nuisance benign controls — Tuesday BENIGN → Wednesday BENIGN, 30 seeds.  
**Resultado:** QK-ZZ: 1.40 triggers benignos. Energy: 1.03. JSD: 1.63.  
**Uso en el paper:** Control honesto. Limitación a reportar.

### Pregunta 5: ¿Es el resultado artefacto de la configuración del feature map?

**Experimento:** Feature-map sensitivity sobre ZZ y PauliXZ reps=1,2,3. Wednesday, 10 seeds.  
**Resultado:** No hay configuración claramente superior. ZZ-r1 sigue siendo el punto operacional más razonable.  
**Uso en el paper:** Apéndice. Cierra el ataque de reviewer sobre cherry-picking del mapa cuántico.

### Pregunta 6: ¿La ventaja de eficiencia resiste un downstream caro (Random Forest)?

**Experimento:** RF 500 árboles, Tuesday→Wednesday, 5 seeds.  
**Resultado:** QK reduce readaptaciones (4.8 vs 8.0 Energy) y fit time (2.97s vs 4.93s), pero pierde en BA (0.978 vs 0.986) y su runtime total (13.74s) triplica el de Energy (5.02s).  
**Uso en el paper:** NO entra en el cuerpo principal. Es un resultado negativo para el claim de coste total. Va a apéndice o se suprime.

---

## 4. Resultados positivos (con soporte CI95 estricto)

| Resultado | Escenarios | CI95 |
|---|---|---|
| QK-ZZ usa −2.10 readaptaciones vs Energy | Wednesday | [−2.43, −1.73] |
| QK-ZZ usa −1.83 readaptaciones vs Energy | DDoS | [−2.13, −1.53] |
| QK-ZZ mejor adaptation efficiency vs todos | Wednesday, DDoS | estricto en todos |
| QK-ZZ mejor BA vs Energy en PortScan (+0.006) | PortScan | [+0.001, +0.013] |
| QK-ZZ mejor BA vs MMD-RBF en PortScan (+0.033) | PortScan | [+0.014, +0.056] |
| QK-ZZ utility positivo vs Energy cuando λ≥0.5, γ≤0.05 | Wednesday | estricto |

---

## 5. Resultados negativos (deben ir en el paper)

| Resultado | Implicación |
|---|---|
| QK-ZZ dispara +1.37 readaptaciones MÁS que Energy en PortScan | La eficiencia no es universal. Depende del tipo de ataque. |
| QK-ZZ runtime 114× mayor que Energy (6.05s vs 0.05s) | El coste detector elimina la utilidad cuando γ≥0.25. |
| QK-ZZ no filtra mejor drift benigno (1.40 vs 1.03 nuisance triggers) | No hay ventaja en falsos positivos. |
| QK-ZZ pierde BA y utility total frente a Energy con RF downstream | El argumento de "downstream caro" no se sostiene con runtime real incluido. |
| Feature maps más profundos (reps=2,3) no mejoran QK | No hay hiperparámetro cuántico que desbloquee ventaja fuerte. |

---

## 6. Claim defendible

> QK-MMD ZZ no proporciona una ventaja cuántica universal sobre detectores clásicos para la monitorización de drift en IDS adaptativos. Sin embargo, en regímenes de drift progresivo volumétrico y de protocolo (DDoS, Wednesday), reduce el número de readaptaciones necesarias en 1.8–2.1 episodios por serie de 100 ventanas (CI95 estricto) manteniendo rendimiento downstream estadísticamente equivalente, a costa de un overhead de detección de 114×. En regímenes PortScan, el patrón se invierte: QK dispara más pero con mayor precisión de clasificación. Esta disociación sugiere que QK-MMD define un punto operativo diferente, no superior, cuya utilidad depende del tipo de ataque y del coste relativo de reentrenamiento frente al overhead del detector.

---

## 7. Limitaciones principales

1. **Dataset único.** Todos los resultados son sobre CICIDS2017. Los tres escenarios comparten la misma distribución de referencia (Tuesday). Esto limita las afirmaciones de generalización.
2. **Runtime cuántico prohibitivo.** 114× overhead frente a Energy distance. En sistemas de tiempo real, esto elimina la ventaja operacional salvo que el reentrenamiento sea extremadamente caro.
3. **Comportamiento inconsistente en PortScan.** QK dispara más, no menos, que Energy en PortScan. No hay explicación mecanística probada, solo hipótesis geométrica.
4. **Downstream limitado a SVC-RBF.** Los resultados con RF muestran que el argumento de "downstream caro" no mejora el balance cuando se contabiliza el runtime total.
5. **Hardware cuántico no evaluado.** Todo es simulación clásica de circuitos cuánticos. El runtime en hardware cuántico real es desconocido.

---

## 8. Decisión recomendada

**Q2 fuerte ahora** (Computer Networks, Expert Systems with Applications, JISA): publicable con los materiales actuales. Riesgo de una ronda de revisión por la inconsistencia PortScan y el dataset único, pero no rechazo.

**Q1 posible con segundo dataset** (IEEE TDSC, Computers & Security CiteScore ~9): necesita un segundo dataset con al menos dos escenarios que repliquen o contradigan el patrón. Si replica → evidencia de generalización. Si contradice → la historia de "caracterización por tipo de ataque" se refuerza. Sin segundo dataset, un revisor de Q1 pedirá la revisión mayor.

---

## 9. Siguiente paso recomendado

Descargar UNSW-NB15 (CSV disponible públicamente, ~250–400 MB) y ejecutar smoke test de 3 seeds, 20 ventanas con Energy, MMD-RBF y QK-ZZ para verificar que el pipeline funciona. Si el smoke pasa, lanzar experimento completo (30 seeds, 100 ventanas, 2–3 escenarios de drift). La decisión de venue depende del resultado: si el patrón se replica parcialmente, se puede intentar TDSC; si es completamente negativo, se mantiene el claim de caracterización y se va a Q2 con más honestidad.
