# Paper 2 — Storyline Propuesta

**Prepared by:** Claude Sonnet 4.6  
**Date:** 2026-06-26  
**Objetivo:** Definir una estructura de paper coherente que evite el efecto "cúmulo de experimentos"

---

## Problema narrativo actual

El paper acumula resultados en este orden cronológico:
controlled streaming → adaptive monitor → downstream single-change → progressive readaptation → utility analysis → nuisance controls → feature map sensitivity → expensive downstream RF

Esto hace que la pregunta central no esté clara hasta la sección 5. Un revisor de Q1 que lea solo el abstract, la introduction y los primeros párrafos de cada sección necesita entender el claim en 90 segundos.

La estructura propuesta reorganiza el material alrededor de una sola pregunta central y presenta los experimentos en orden lógico, no cronológico.

---

## Título tentativo

*QK-MMD as an Adaptive Trigger for Network Intrusion Detection Systems: An Operational Characterization Under Progressive Drift*

---

## 1. Introduction

**Función:** Plantear el problema operacional, no el problema cuántico.

**Estructura:**
1. Adaptive IDS: the retraining problem. Los IDS basados en ML degradan bajo drift de red. Reentrenar es costoso. Decidir cuándo reentrenar es un problema de detección de drift.
2. Existing approaches: detectores univariados, MMD-RBF, Energy distance. Limitación: todos tratan el trigger de reentrenamiento como un problema de detección, no de optimización operacional.
3. Gap: no hay estudio que evalúe trade-offs de frecuencia de readaptación vs rendimiento downstream vs coste detector en IDS bajo drift progresivo real.
4. This paper: evaluamos QK-MMD como alternativa con perfil operacional diferente. No afirmamos quantum advantage universal. Afirmamos un trade-off caracterizable.
5. Contributions (bulleted):
   - Protocolo de readaptación progresiva con métricas operacionales (adaptation efficiency, actionable utility).
   - Evaluación en 3 escenarios CICIDS2017 con CI95 sobre 30 seeds.
   - Marco de utilidad operacional parametrizable (λ, γ, η).
   - Estudio de sensibilidad al feature map cuántico (pre-registrado).

**Lo que NO entra:** Ninguna afirmación de quantum advantage. Ninguna referencia a "QK supera a los clásicos" en términos absolutos.

---

## 2. Related Work

**Función:** Posicionar la contribución respecto a tres cuerpos de literatura.

**Subsecciones:**
1. **Drift detection for adaptive classifiers.** ADWIN, DDM, KSWIN, etc. Limitación: diseñados para streams univariados, no para tráfico de red multivariado.
2. **Two-sample tests as drift detectors.** MMD-RBF, Energy distance, KS-max, JSD. Estado del arte más cercano al método propuesto.
3. **Quantum kernels for machine learning.** QK-MMD como extensión. Estado del arte en simulación, gap en aplicación IDS.
4. **Adaptive IDS under concept drift.** Trabajos que adaptan modelos IDS pero no evalúan el coste del trigger. Gap que este paper cierra.

**Lo que NO entra:** 
- Historia completa de quantum computing.
- Trabajos sobre hardware cuántico real (no es el scope).
- Literatura de IDS clásico no relacionada con drift.

---

## 3. Method

**Función:** Describir QK-MMD y el protocolo de evaluación como sistema completo.

**Subsecciones:**
1. **QK-MMD: definición.** ZZ y PauliXZ feature maps, kernel cuántico, statistic MMD. Sin sobrevender las propiedades cuánticas.
2. **Detección de drift como decisión de readaptación.** El detector no solo detecta drift — su output decide si el clasificador se reentrena. Esto crea un bucle: más triggers → más fit time → más coste, pero potencialmente mejor BA.
3. **Protocolo de readaptación progresiva.** 
   - 80 ventanas de ramp + 20 de plateau (drift progresivo hasta severidad 1.0).
   - Trigger: threshold_quantile=0.95, consecutive_k=3, cooldown=10.
   - Clasificador downstream: SVC-RBF con recalibración.
4. **Métricas.** 
   - `mean_balanced_accuracy`: rendimiento downstream.
   - `n_adaptations`: coste de reentrenamiento.
   - `adaptation_efficiency = cumulative_gain / n_adaptations`: ganancias por episodio.
   - `actionable_utility`: función compuesta con pesos λ, γ, η.
5. **Baselines:** Energy distance, MMD-RBF, KS-max, JSD.

**Lo que NO entra:** Adaptive monitor (supersedido). Hybrid OR combination (resultado negativo, va a apéndice). Long-stream single-change (supersedido). Derivaciones teóricas de ventaja cuántica.

---

## 4. Experimental Protocol

**Función:** Establecer credibilidad del diseño experimental.

**Subsecciones:**
1. **Dataset: CICIDS2017.** Preprocesamiento, extracción de features, normalización. Referencia: Tuesday BENIGN + attacks.
2. **Tres escenarios de drift adversarial progresivo:**
   - Tuesday → Wednesday (Hulk, Slowloris, Heartbleed)
   - Tuesday → Friday PortScan
   - Tuesday → Friday DDoS
3. **Control benigno.** Tuesday BENIGN → Wednesday BENIGN. Diseñado para medir nuisance triggers sin drift adversarial.
4. **Reproducibilidad.** 30 seeds. CI95 por bootstrap pareado. Pre-registro del protocolo de sensibilidad al feature map.

**Lo que NO entra:** Descripción técnica detallada de circuitos cuánticos (va a apéndice o material suplementario). Justificación post-hoc de parámetros del protocolo.

---

## 5. Results

**Estructura propuesta: cuatro subsecciones ordenadas lógicamente.**

### 5.1 Motivación: poder de detección controlado

Tabla AUC por severidad para los 5 detectores. QK ZZ y PauliXZ superan a MMD-RBF en severidades altas (AUC 0.918 vs 0.800). Esto motiva la diferencia de trigger timing en el experimento principal.

**Lo que NO entra aquí:** Ningún resultado de downstream. Esta subsección es solo motivación.

### 5.2 Readaptación progresiva bajo drift adversarial real

**Tabla principal:** n_adaptations, adaptation_efficiency, mean_BA, cumulative_error_area, detector_runtime para 6 detectores × 3 escenarios. Con n_seeds=30.

**Texto:** 
- Wednesday y DDoS: QK-ZZ usa 2.10 y 1.83 readaptaciones menos que Energy (CI95 estricto). BA comparable.
- PortScan: QK-ZZ usa 1.37 readaptaciones MÁS que Energy (CI95 estricto). Pero BA más alta (+0.006, CI [0.001, 0.013]).
- La disociación PortScan vs Wednesday/DDoS es el resultado más informativo del paper. No se oculta.

**Tabla CI95:** Diferencias pareadas estrictas por escenario y métrica.

**Lo que NO entra:** Adaptive monitor. Long-stream single-change. RF downstream (va a apéndice).

### 5.3 Análisis de utilidad operacional

Función de utilidad parametrizable. Grid λ ∈ {0.25, 0.5, 1.0, 2.0} × γ ∈ {0, 0.01, 0.05} × η ∈ {0, 0.25, 0.5}. Zonas de strict positive CI.

Resultado: QK-ZZ domina operacionalmente cuando λ≥0.5 y γ≤0.05. Por encima de γ=0.05 la ventaja desaparece o se invierte.

Este análisis bridge el resultado estadístico (adaptations) con la utilidad operacional (deployment decisions).

### 5.4 Control benigno: nuisance triggers

Tabla nuisance triggers por detector en Wednesday BENIGN.

Resultado honesto: QK-ZZ (1.40) > Energy (1.03) > MMD-RBF (0.70). QK tiene mayor sensibilidad al drift benigno. Esto reduce parcialmente la ventaja de adaptation efficiency cuando se contabilizan falsos triggers.

---

## 6. Discussion

**Función:** Unificar los resultados en una historia coherente y declarar las implicaciones.

**Estructura:**
1. **Interpretación de la disociación PortScan.** Hipótesis: PortScan genera señal distribuida en feature space (muchos puertos → varianza en distribución de puertos), que QK interpreta como drift continuo. Wednesday/DDoS producen cambios volumétricos coherentes que QK detecta de forma más selectiva. Esto es una hipótesis, no una prueba. Declararlo así.
2. **Implicaciones para el practitioner.** QK-ZZ tiene sentido en despliegues donde: (a) el downstream es moderadamente caro de reentrenar, (b) el tipo de ataque es volumétrico/protocolo, (c) el overhead de 114× es aceptable. No tiene sentido en sistemas de tiempo real con modelos ligeros.
3. **El marco de utilidad operacional como contribución.** Independientemente de si QK gana, el framework λ/γ/η es una contribución metodológica para cualquier evaluación de detectores de drift en IDS adaptativos.

---

## 7. Limitations

**Función:** Ser los primeros en atacar el paper antes que el revisor.

1. **Dataset único.** Todos los resultados son CICIDS2017. La generalización no está demostrada.
2. **Simulación clásica de circuitos cuánticos.** El runtime 114× es simulación, no hardware cuántico. En hardware real, podría ser mejor (aceleración) o peor (ruido).
3. **Inconsistencia PortScan.** No hay mecanismo probado. La hipótesis geométrica es especulativa.
4. **SVC-RBF como único downstream en el experimento principal.** Resultados con RF muestran que con downstream caro, el balance de runtime total puede revertirse (ver Appendix B).
5. **Protocolo offline.** El umbral del detector se estima sobre un stream histórico, no online.

---

## 8. Conclusion

**Función:** Una afirmación directa del claim defendible, sin exagerar.

QK-MMD ZZ no proporciona ventaja cuántica universal sobre detectores clásicos para readaptación IDS. En los escenarios volumétricos evaluados (Wednesday, DDoS), define un punto operativo distinto: readaptación menos frecuente con rendimiento equivalente, a costa de un overhead de detección de 114×. La disociación observada en PortScan indica que el perfil operacional de QK-MMD es atacable-dependiente. El marco de utilidad operacional propuesto ofrece una herramienta general para comparar detectores de drift en sistemas IDS adaptativos bajo restricciones de coste heterogéneas.

---

## Apéndices

### Apéndice A: Feature-map sensitivity study

ZZ y PauliXZ reps=1,2,3 en el escenario de desarrollo (Wednesday, 10 seeds). Ninguna configuración más profunda supera consistentemente a ZZ-r1. La elección de reps=1 no es cherry-picking.

### Apéndice B: Expensive downstream — Random Forest

RF 500 árboles, Wednesday, 5 seeds. QK reduce fit time (2.97s vs 4.93s) y readaptaciones (4.8 vs 8.0), pero pierde BA y el runtime total es 13.74s vs 5.02s para Energy. Resultado negativo: el argumento de "downstream caro" no salva el balance cuando se contabiliza el runtime del detector.

### Apéndice C (opcional): Detalles de circuitos cuánticos

Diagramas ZZ y PauliXZ. Solo si hay espacio y los revisores de la venue son familiarizados con ML cuántico.

---

## Experimentos que NO entran en ningún sitio

| Experimento | Razón de exclusión |
|---|---|
| Adaptive monitor | Supersedido por el protocolo de readaptación progresiva. Resultados previos, no añaden información incremental. |
| Single-change downstream (sev=1.0) | Todos los detectores disparan al mismo tiempo, downstream idéntico. No informativo. |
| Hybrid OR combination | Resultado negativo: el hybrid es peor que QK individual. No hay historia útil que contar. |
| Geometry diagnostics | Diagnóstico especulativo. Score separation plots no son evidencia publicable. |
| Operational scale proxy | "1M flows/day → 336k extra attacks detectados" no es resultado experimental. Parece motivated reasoning. |
| Long-stream downstream validation | Supersedido por progressive readaptation. |

---

## Mapa de resultados → secciones

| Resultado | Sección | Rol |
|---|---|---|
| AUC por severidad (controlled streaming) | 5.1 | Motivación |
| n_adaptations, BA, efficiency (3 escenarios, 30 seeds) | 5.2 | Resultado principal |
| CI95 pareados (paired table) | 5.2 | Soporte estadístico |
| Utility grid (λ/γ/η) | 5.3 | Marco operacional |
| Nuisance triggers en benign | 5.4 | Control honesto |
| Feature map sensitivity | Apéndice A | Robustez a hiperparámetro |
| RF expensive downstream | Apéndice B | Limitación honesta |
