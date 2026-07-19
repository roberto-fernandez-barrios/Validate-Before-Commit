# PLAN.md — Techo máximo del paper *Validate Before Commit*

## 0. Misión

Convertir el trabajo actual en la versión científicamente más fuerte que permite este set de datos, código y resultados, con **Knowledge-Based Systems** como objetivo principal.

El resultado final no debe ser “la versión con más experimentos”, sino un paper compacto y difícil de atacar que aporte:

1. una tesis clara de **candidate governance**;
2. un algoritmo de decisión con novedad suficiente para KBS;
3. garantías estadísticas que coincidan exactamente con el muestreo y el código;
4. una evaluación causal, temporal y operacional;
5. un artifact completamente trazable.

El techo realista de este trabajo es un **KBS fuerte**. No se convertirá en un paper metodológico de primer nivel añadiendo amendments infinitos. Para elevar el techo hay que consolidar el paper alrededor de una contribución algorítmica y una validación externa limpia.

---

# 1. Regla de parada

Este será el **último plan de ampliación**.

No crear nuevos amendments para responder a cada comentario aislado. Crear una única rama/fase final, por ejemplo:

```text
final-kbs
```

y un protocolo congelado:

```text
notes/final_kbs_protocol.md
```

El paper queda cerrado cuando:

- todos los bloqueantes P0 estén resueltos;
- se complete el experimento externo P1;
- la historia principal se pueda contar con un máximo de seis tablas/figuras centrales;
- no haya resultados superseded en el cuerpo;
- el audit pase al 100%;
- un revisor interno hostil no encuentre contradicciones entre PDF, código, tablas y README.

Si un resultado final contradice la historia actual, se cambia la historia. No se abre otro experimento para “rescatarla”.

No hacer `commit`, `push`, tag, release ni Zenodo sin autorización explícita de Roberto.

---

# 2. Tesis final recomendada

La tesis más resistente no es:

> Los detectores de drift no sirven.

Ni:

> La degradación gobierna universalmente el valor de actualizar.

Ni:

> El gate hace segura la adaptación.

La tesis final debe ser:

> A drift alarm proposes a challenger; it does not justify deployment. Under fixed candidate-generation pipelines, recent incumbent health is a stronger commit signal than the evaluated scalar drift scores. Commit-time validation reduces harmful replacement, and a stratified sequential gate exposes an explicit accuracy–labels–risk trade-off.

Versión operativa:

> Detect → propose → validate → commit/defer.

La contribución se vende como **intelligent decision support for model-update governance**, no como un nuevo drift detector.

---

# 3. P0 — Bloqueantes de validez

## P0.1. Rehacer correctamente el control simétrico A/B

### Problema actual

El script `paper2_symmetric_ab_013.py` afirma que T, A, B y E son muestras disjuntas, pero utiliza `sample_balanced_from_distribution`, que muestrea con reemplazo.

Además:

- A es siempre incumbent y B challenger;
- no se aleatoriza el rol;
- no se informa de las intersecciones reales;
- T, A, B y E pueden compartir filas;
- el valor ToN `+4.99` no es compatible sin más con afirmar “gap ≈ 0”;
- el mecanismo se declara “identificado” con más fuerza de la permitida.

### Implementación correcta

Crear:

```text
src/analysis/paper2_symmetric_ab_final.py
```

Para cada dataset y seed:

1. Deduplicar globalmente por hash de features.
2. Dividir sin reemplazo en:
   - T: transformer;
   - A: modelo A;
   - B: modelo B;
   - E: evaluación.
3. Verificar:
   ```text
   T ∩ A ∩ B ∩ E = ∅
   ```
   mediante asserts explícitos.
4. Mantener:
   - mismo tamaño A/B;
   - mismo hiperparámetro;
   - mismo transformer;
   - misma evaluación.
5. Aleatorizar cuál es incumbent en cada seed o asignarlo con una moneda predefinida.
6. Ejecutar condiciones:
   - transformer independiente T;
   - transformer ajustado en A;
   - transformer ajustado en B;
   - transformer propio por candidato;
   - sin PCA, como sensibilidad.
7. Reportar por condición:
   - BA(A);
   - BA(B);
   - B−A;
   - CI;
   - número de filas únicas;
   - hashes/intersecciones.
8. Incluir SVC-RBF y Random Forest.

### Interpretación

Solo usar “mecanismo identificado” si:

- el transformer independiente produce un gap centrado en cero;
- el transformer ajustado al incumbent produce una ventaja sistemática para el incumbent;
- el efecto se invierte cuando se ajusta en B;
- el transformer propio elimina o reduce el efecto.

De no cumplirse todo, escribir:

> The control is consistent with a representation-induced incumbent advantage, but does not uniquely identify the mechanism.

### Salidas

```text
results/final_kbs/symmetric_ab.csv
results/final_kbs/symmetric_ab_manifest.json
tables/table_symmetric_ab.tex
```

---

## P0.2. Implementar una garantía estratificada realmente válida

### Problema actual

El paper afirma que las reglas risk-controlled están en forma estratificada per-class. El código solo implementa `labeled_probe_strat` mediante un LCB normal fijo por clase.

No existe en el código una EB-CS estratificada anytime-valid completa, y el LCB normal con 16 observaciones por clase no constituye por sí solo una garantía exacta.

### Nuevo algoritmo principal

Implementar:

```text
labeled_probe_ebcs_stratified
```

La métrica objetivo es:

\[
\Delta BA =
\frac{1}{2}\mu_{\mathrm{benign}}+
\frac{1}{2}\mu_{\mathrm{attack}}.
\]

Para cada clase:

\[
d_i^{(c)} =
1[h' \text{ correct}]-
1[h \text{ correct}].
\]

Mantener un e-process o confidence sequence válido por estrato.

Usar una de estas soluciones, preferentemente en este orden:

1. e-process / betting CS por clase;
2. empirical-Bernstein CS por clase con condiciones verificadas;
3. bounds exactos para variables acotadas.

Combinar con:

- Bonferroni \(\alpha/2\) por clase; o
- producto de e-values con una prueba combinada formalmente justificada.

Commit cuando el lower bound global de \(\Delta BA\) sea positivo.

### Requisitos

- Válido bajo el orden de muestreo real.
- Rechazar por defecto si falta una clase.
- No usar un LCB normal como “exact risk control”.
- Test unitario mediante simulación nula:
  - 100.000 propuestas;
  - \(\alpha\in\{0.01,0.05,0.10\}\);
  - distintos ratios de empates;
  - distintas mejoras por clase.
- Verificar cobertura bajo:
  - i.i.d.;
  - sin reemplazo;
  - dependencia por bloques.
- Declarar claramente dónde se pierde el nivel nominal.

### Gate exacto fijo

Implementar además un baseline fijo estratificado:

```text
labeled_probe_exact_stratified
```

Puede usar:

- McNemar por clase + Bonferroni;
- o test exacto/permutación estratificada de \(\Delta BA\).

### Resultado esperado

La contribución algorítmica principal pasa a ser:

> Stratified sequential commit validation with adaptive label acquisition.

No utilizar como principal el pooled McNemar ni la pooled EB-CS.

---

## P0.3. Garantía deployment-long, no solo por propuesta

### Problema actual

Las garantías actuales se reinician para cada challenger. Con \(M\) propuestas, el riesgo acumulado puede crecer aproximadamente como \(M\alpha\).

### Implementación

Añadir un controlador de presupuesto de riesgo:

```text
DeploymentRiskBudget
```

Opciones predefinidas:

- alpha spending:
  \[
  \alpha_j = \frac{6\alpha_{\mathrm{life}}}{\pi^2 j^2};
  \]
- e-process global;
- wealth-based allocation.

Parámetros:

```text
--lifetime-alpha 0.10
--alpha-spending pseries
```

Registrar por propuesta:

- `proposal_idx`;
- `alpha_allocated`;
- `alpha_spent`;
- `e_value`;
- `decision`;
- `labels_used`.

### Claim permitido

> The gate controls false probe-superiority over a deployment sequence under the stated sampling assumptions and spending schedule.

No convertirlo en garantía sobre BA futura.

---

## P0.4. Consolidar el brazo causal como experimento principal secundario

### Configuración definitiva

Usar:

- datos observados;
- stream sin reemplazo;
- deduplicación global;
- cero colisiones;
- no probe → reject/defer;
- threshold anterior hasta disponer de 30 ventanas;
- candidato = últimas 8 ventanas observadas;
- probe = ventana pasada disjunta;
- mismos tamaños de ventana en los tres datasets.

### Problema de UNSW

El brazo actual usa 64 flujos para UNSW y 128 para los demás. Para comparabilidad:

- ejecutar los tres datasets con ventana 64;
- mantener una sensibilidad a 128 donde sea posible.

No mezclar tamaños de ventana dentro de la tabla principal.

### Políticas finales

Comparar:

- no adaptation;
- naive;
- point `>=`;
- strict `>`;
- lifetime stratified gate;
- calibrated ensemble.

### Reportar

- BA;
- attack F1;
- PR-AUC si es posible;
- FPR;
- commits;
- labels;
- compute;
- harmful-commit rate;
- CI;
- zero collisions.

### Reencuadre obligatorio

El brazo causal no “reproduce todos los criterios” si UNSW queda por debajo de no-adaptation.

Redacción:

> The observed-data arm reproduces the harmful-regime rescue and the qualitative benefit/harm ordering, while exposing a marginal-regime boundary.

---

## P0.5. Limpiar claims incompatibles

Buscar y revisar todas las apariciones de:

```text
safe
fails safe
eliminates
governs
essentially headroom
predicts nothing
every
all classifiers
all generators
causal
deployable
label-efficient
current traffic
adversarial
```

Reglas:

- `safe` → `risk-controlled under ...` o `harm-reducing`.
- `eliminates` → `zero observed`, con CI.
- `all classifiers` → separar presupuesto 512 y size-matched.
- `current traffic` → diferenciar pool oracle y observed-data.
- `causal` → causal respecto al orden y disponibilidad asumida de etiquetas.
- `label-efficient` → eficiencia incremental de la decisión.
- `adversarial` → random corruption, salvo ataque adaptativo real.
- `headroom` → señal predictiva condicionada al generador.

---

# 4. P1 — La contribución algorítmica que eleva el techo

## P1.1. Gate secuencial adaptativo de tres acciones

Crear una política propia y claramente nombrada:

```text
VBC-SG: Validate-Before-Commit Sequential Gate
```

Acciones:

```text
COMMIT
REJECT
DEFER / BUY_MORE_LABELS
```

Procedimiento:

1. Empieza con 16 etiquetas estratificadas.
2. Actualiza bounds por clase.
3. Si el lower bound de utilidad > 0:
   - commit.
4. Si el upper bound < 0:
   - reject.
5. En otro caso:
   - adquirir otro bloque;
   - hasta presupuesto máximo.
6. Si sigue indeciso:
   - reject o defer según el coste configurado.

### Utilidad cost-sensitive

No usar únicamente BA:

\[
U(h)=
-\lambda_{FN}FN
-\lambda_{FP}FP
-\lambda_L L
-\lambda_U I_{\mathrm{commit}}
-\lambda_C C_{\mathrm{train}}.
\]

El coste de candidato es sunk en el gate de commit, pero entra en la política de dos etapas.

Implementar:

- `VBC-SG-commit`;
- `VBC-SG-two-stage`.

### Novedad

La novedad no será “comparar champion y challenger”, sino:

- inferencia estratificada;
- adquisición secuencial de labels;
- lifetime risk budget;
- utilidad operacional;
- decisión commit/reject/defer;
- integración con un stage previo de health para evitar entrenar.

### Teoría mínima

Incluir proposiciones:

1. garantía per-proposal;
2. garantía deployment-long con alpha spending;
3. coste esperado de labels;
4. condiciones necesarias para trasladar probe superiority a utilidad futura.

No prometer más de lo demostrado.

---

# 5. P1 — Validación operacional end-to-end

## P1.2. Prevalencia real, adquisición de etiquetas y latencia

Este es el experimento que más eleva la validez externa.

### Pipeline

\[
\text{stream desbalanceado}
\rightarrow
\text{trigger}
\rightarrow
\text{label acquisition}
\rightarrow
\text{candidate}
\rightarrow
\text{probe}
\rightarrow
\text{commit}.
\]

### Prevalencias

```text
0.1%, 0.5%, 1%, 5%, 10%
```

### Métodos de adquisición

- muestreo aleatorio;
- alert-enriched;
- uncertainty sampling;
- disagreement candidate/incumbent;
- estratificación basada en cola de alertas.

No usar ground-truth para seleccionar clases.

### Latencias

- labels del candidate: `{0, 5, 10, 20}` ventanas;
- labels del probe: `{0, 5, 10, 20}`;
- combinación de ambas.

### Métricas

- número total de flujos inspeccionados;
- labels benignos/ataques;
- tiempo hasta decisión;
- candidate freshness;
- BA;
- PR-AUC;
- attack recall;
- FPR;
- alert burden;
- commit rate;
- harmful commits;
- utility.

### Interpretación

A prevalencia baja, el headline no puede ser “32 labels”. Debe ser:

> 32 adjudicated probe labels, requiring X inspected flows under acquisition policy Y.

---

## P1.3. Replay cronológico externo definitivo

No buscar manualmente un stream que produzca harm. Pre-registrar todos los replays posibles.

### Prioridad

1. reconstruir ToN-IoT cronológicamente usando timestamps como metadata, nunca como features;
2. UNSW completo ordenado temporalmente;
3. CICIDS completo;
4. otro dataset temporal disponible en el proyecto, solo si la preparación es razonable.

### Requisitos

- procesar el máximo de captura posible, no 200 ventanas dispersas;
- conservar timestamps;
- no seleccionar el ataque después de ver resultados;
- candidate/probe solo con datos causalmente disponibles;
- label latency;
- prevalencia natural;
- reportar todos los regímenes, produzcan beneficio o daño.

### Éxito

El paper no necesita que aparezca net harm.

Dos desenlaces son válidos:

- aparece net harm cronológico → gran validación;
- no aparece → el paper se formula como controlled existence study y cuantifica cuándo no se observa.

---

# 6. P1 — Diseño experimental final

## Matriz principal

### Modelos

- SVC-RBF: learner frágil y caso de daño.
- Random Forest: learner robusto.
- Logistic Regression: baseline estable.

MLP solo en suplemento salvo que aporte una conclusión diferente.

### Generadores

- full replacement;
- sliding window;
- calibrated ensemble;
- cumulative + initial replay.

### Gates

- none;
- point `>=`;
- strict `>`;
- fixed exact stratified;
- VBC-SG lifetime;
- two-stage VBC-SG.

### Regímenes

- full drift;
- mild drift;
- zero drift;
- causal observed;
- chronological;
- operational prevalence.

No ejecutar el factorial completo si no responde una pregunta. Predefinir las celdas necesarias para cada claim.

---

# 7. P1 — Estadística final

## Confirmatory hierarchy

Separar:

1. confirmatory core;
2. final registered validation;
3. exploratory/supplementary.

No llamar “replication” a extensiones internas en los mismos datasets sin aclarar `internal`.

## Unidad experimental

- trigger dentro de stream;
- stream = dataset × regime × seed;
- dataset/regime como unidad externa.

Usar:

- cluster bootstrap por stream;
- mixed effects con `regime × seed`;
- random slope si converge;
- CIs de no-inferioridad;
- margins prácticos predefinidos.

## Multiplicidad

- Holm para comparaciones confirmatorias;
- FDR para matrices exploratorias;
- no corrección necesaria para tablas puramente descriptivas, pero etiquetarlas.

## Magnitud práctica

Distinguir:

- signo;
- significación;
- materialidad.

Márgenes recomendados:

```text
0.2 BA
0.5 BA
1.0 BA
```

## Harmful commit

Reportar:

- numerador;
- denominador;
- Clopper–Pearson CI;
- magnitud media;
- CVaR;
- worst commit;
- horizon `{1,3,5,10,next-trigger}`.

---

# 8. P2 — Reescritura del paper

## P2.1. Reducir el cuerpo

Objetivo:

```text
24–28 páginas de contenido principal
```

Mover al suplemento:

- harness v1;
- correlación matemáticamente acoplada;
- resultados superseded;
- historia amendment por amendment;
- tablas completas de quantum sensitivity;
- implementaciones antiguas;
- todos los sweeps secundarios.

El cuerpo actual de 38 páginas perjudica la claridad.

## P2.2. Estructura final

1. Introduction.
2. Related work.
3. Candidate-governance formulation.
4. VBC-SG method and guarantees.
5. Final experimental design.
6. Confirmatory controlled results.
7. Causal and operational evaluation.
8. Policy frontier.
9. Chronological boundary.
10. Limitations.
11. Conclusion.

## P2.3. Contribuciones finales

Máximo cuatro:

1. candidate-governance formulation;
2. degradation/headroom evidence, condicionada al generador;
3. stratified lifetime-risk sequential gate;
4. causal/operational evaluation and policy frontier.

No contar cada amendment como una contribución.

## P2.4. Quantum

Reducir el componente quantum a:

- una comprobación de detector invariance;
- una tabla/figura secundaria;
- suplemento para detalles.

No dejar que parezca un paper quantum negativo incrustado dentro del paper principal.

---

# 9. P2 — Graphical abstract y figuras

## Graphical abstract

Rediseñar desde cero.

Debe mostrar:

```text
Alarm → Challenger → Validation → Commit / Reject / Defer
```

Dos líneas:

- point/strict gate: más potencia;
- risk gate: más control, más labels.

Añadir explícitamente:

```text
Controlled SVC-RBF harm case
```

No poner texto diminuto ni claims universales.

## Figuras principales

Mantener solo:

1. candidate-governance pipeline;
2. per-trigger health vs update value;
3. policy frontier;
4. causal/operational result;
5. chronological boundary.

Cada figura debe tener una conclusión visual inequívoca.

---

# 10. P2 — Artifact final

## Workflow

Crear:

```text
make final-paper
```

Debe:

1. verificar hashes;
2. ejecutar tests;
3. ejecutar análisis;
4. generar tablas;
5. generar figuras;
6. generar manifest;
7. compilar CAS;
8. compilar suplemento;
9. ejecutar audit;
10. comparar claims contra outputs.

## Tests obligatorios

```text
test_symmetric_ab_disjoint
test_global_stream_disjoint
test_probe_candidate_disjoint
test_candidate_future_disjoint
test_no_probe_never_commits
test_stratified_gate_type
test_lifetime_alpha_budget
test_effective_alpha_manifest
test_main_tables_final_only
test_no_superseded_claims
test_claim_table_consistency
```

## Manifest

Crear:

```text
results/final_manifest.json
```

Campos:

- commit SHA;
- artifact version;
- dataset hashes;
- seeds;
- window sizes;
- prevalence;
- latency;
- model;
- generator;
- gate;
- alpha;
- spending rule;
- collision counts;
- labels;
- outputs;
- audit status.

---

# 11. Priorización y orden exacto para Claude Code

## Fase A — Congelar

1. Crear `notes/final_kbs_protocol.md`.
2. Copiar este plan.
3. Registrar configuraciones, seeds y stopping rule.
4. No ejecutar todavía.

## Fase B — Corregir bloqueantes

5. Rehacer symmetric A/B verdaderamente disjoint.
6. Implementar exact/CS estratificada.
7. Implementar lifetime alpha spending.
8. Unificar brazo causal a window 64.
9. Ejecutar tests de colisiones.
10. Corregir claims.

## Fase C — Método final

11. Implementar VBC-SG.
12. Implementar VBC-SG two-stage.
13. Validar cobertura por simulación.
14. Ejecutar matriz controlada final.

## Fase D — Techo externo

15. Ejecutar prevalencia + latencia end-to-end.
16. Ejecutar replay cronológico ToN-IoT/UNSW/CICIDS.
17. Congelar resultados.

## Fase E — Paper

18. Reestructurar manuscrito.
19. Mover v1 y amendments al suplemento.
20. Rediseñar graphical abstract.
21. Generar tablas/figuras finales.
22. Actualizar README y REPRODUCE.
23. Ejecutar audit.
24. Revisión interna hostil final.
25. Corregir únicamente errores verificables.
26. Parar.

---

# 12. Criterio de envío

El paper queda listo cuando se pueda responder “sí” a todo:

- [ ] La garantía corresponde al probe realmente usado.
- [ ] Existe control lifetime, no solo por proposal.
- [ ] El A/B es realmente disjoint.
- [ ] El causal arm usa una configuración comparable.
- [ ] No hay tablas superseded.
- [ ] El strict gate está en la frontera principal.
- [ ] La validez operacional está evaluada end-to-end.
- [ ] El net harm cronológico se reporta honestamente, aparezca o no.
- [ ] La historia menciona SVC-RBF donde corresponde.
- [ ] El cuerpo tiene una historia única y compacta.
- [ ] El audit pasa al 100%.
- [ ] No quedan claims más fuertes que sus CIs.

---

# 13. Resultado esperado

## Versión mínima publicable

Un KBS sólido con:

- candidate governance;
- causal harness;
- strict gate;
- stratified risk gate;
- claims estrechos;
- suplemento completo.

## Techo máximo

Un KBS muy fuerte con:

- VBC-SG como contribución algorítmica;
- deployment-long risk control;
- label acquisition adaptativa;
- utilidad cost-sensitive;
- causal operational-prevalence experiment;
- chronological validation;
- artifact reproducible.

Ese es el techo máximo que ofrece este set sin convertirlo en otro paper completamente distinto.

---
# ANEXO DE CONGELACIÓN (Fase A, registrado antes de ejecutar el delta)
- Copiado de plan_max_q1.md el 2026-07-17. Seeds: 104–133 (30) en todas las celdas nuevas.
- Ya en vuelo desde amendment 014 (registrado antes de recibir este archivo): A/B disjunto
  role-randomized (SVC+RF), labeled_probe_ebcs_strat, ebcs_defer, lifetime Bonferroni,
  e2e-lite pi=0.05/lat5. Este protocolo los ABSORBE y añade el delta:
  P0.1 completo (condiciones fit-on-B, own-transformer, no-PCA), P0.2 exact stratified +
  simulación nula 100k, P0.3 pseries spending + logging por propuesta, P0.4 matriz causal
  unificada a window 64 (none/point/strict/VBC-SG × full/mild × 3 datasets; 128 = sensibilidad),
  P1.1 VBC-SG nombrado (estratificado+defer+lifetime) + proposiciones, P1.2 sweep de prevalencia
  {0.01,0.05,0.10} y latencia {5,20}, P2 reestructura + suplemento.
- P1.3 ToN cronológico: INVIABLE con los datos en disco (train_test_network.csv no conserva
  timestamps; verificado amendment 009). UNSW completo ordenado ya existe (amendment 005).
  Se declara, no se fabrica.
- Stopping rule aceptada: este es el último plan de ampliación. Sin commit/push/tag/release/Zenodo
  sin autorización explícita de Roberto.

---
# FASE E — PROGRESO (2026-07-19)
- Graphical abstract REDISEÑADO desde cero (`make_paper2_graphical_abstract_final.py`): pipeline
  Alarm→Challenger→Validate→Commit/Reject/Defer, dos líneas de política, badge "Controlled
  SVC-RBF harm case", scope honesto, tipografía grande, 2299×857.
- Contribuciones reescritas a las 4 del plan (candidate governance / cuenta condicional /
  VBC-SG / evaluación causal+operacional con frontera).
- SUPLEMENTO creado (`manuscript/supplement.tex`, standalone, 9 pp): recibe el estudio
  exploratorio v1 completo (antes §5.2–5.9, figs 1/4/5/6/8, tablas 1/2/3/6); el cuerpo lo
  sustituye por un resumen de 1 párrafo (\S sec:v1summary) con los 3 hechos que se re-establecen
  en v2. fig:9 (per-trigger) se queda en el cuerpo. 24 refs textuales \S5.x re-apuntadas a
  Supplementary S1.x. Cuerpo: 39 → **33 pp CAS / 26 pp IEEE**, 0 refs indefinidas, audit 415/415.
- PENDIENTE de la Fase E (próxima pasada): extraer del §sec:v2 los párrafos históricos
  (monitor-validation vs river, v1-robustness-envelope, two-stage history, natural-prevalence
  retraction) → supplement S2 (~2 pp más), recorte quantum, consolidación §5 → objetivo 24–28 pp;
  revisión interna hostil final; make final-paper + tests.
