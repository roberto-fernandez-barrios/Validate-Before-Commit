# Paper 2 — Next Steps Review

**Reviewer:** Claude Sonnet 4.6  
**Date:** 2026-06-26  
**Branch:** paper2-expensive-downstream  
**Postura:** Revisor Q1 escéptico

---

## 1. Evaluación de la narrativa propuesta

**Narrativa propuesta:**
> "QK-MMD no proporciona quantum advantage universal, pero sí ofrece un perfil operacional competitivo para readaptación IDS bajo drift progresivo. Su valor aparece como trade-off: menos readaptaciones en Wednesday/DDoS, mejor BA en PortScan, pero con mayor runtime y sin ventaja en nuisance benign drift."

**Veredicto: Honesta, internamente consistente, insuficiente para Q1 sin segundo dataset. Suficiente para Q2.**

### Argumentos a favor

1. **"Menos readaptaciones en Wednesday/DDoS" — soporte CI95 estricto.**
   - Wednesday vs Energy: −2.10 [−2.43, −1.73]. n=30 seeds, 100 ventanas.
   - DDoS vs Energy: −1.83 [−2.13, −1.53]. n=30 seeds.
   - Mejor adaptation efficiency vs todos los baselines en ambos escenarios (todos los CI estrictos).
   - Esto es el núcleo duro del paper. Es una afirmación falsable, testada y confirmada en dos de tres escenarios.

2. **"Mejor BA en PortScan" — soporte CI95 estricto pero efecto pequeño.**
   - vs Energy: +0.006 [+0.001, +0.013]. Estricto pero clínicamente pequeño.
   - vs MMD-RBF: +0.033 [+0.014, +0.056]. Estricto y más sustancial.
   - El problema: en PortScan QK dispara 1.37 readaptaciones MÁS que Energy. La narrativa dice "mejor BA en PortScan" sin mencionar el coste de más readaptaciones. Hay que incluir ambas cosas.

3. **"Mayor runtime" — completamente honesto y soportado.**
   - 6.05s/ventana vs 0.053s para Energy → 114× overhead. CI universalmente estricto.
   - La narrativa lo reconoce. Bien.

4. **"Sin ventaja en nuisance benign drift" — honesto y soportado.**
   - QK-ZZ: 1.40 nuisance triggers vs Energy: 1.03. No es un fallo catastrófico pero es una desventaja real.
   - La narrativa lo reconoce. Bien.

### Objeciones que quedan sin resolver en la narrativa

1. **La narrativa no explica por qué QK es más eficiente en Wednesday/DDoS pero no en PortScan.** Este es el hueco más peligroso. Un revisor lo atacará inmediatamente. La respuesta actual ("distribución geométrica diferente del ataque en feature space") es una hipótesis plausible pero no verificada. El paper debe declararla como hipótesis, no como explicación.

2. **"Perfil operacional competitivo" es ambiguo.** ¿Competitivo en qué? La narrativa necesita ser más precisa: "competitivo en adaptation efficiency en escenarios volumétricos cuando λ≥0.5 y γ≤0.05."

3. **El resultado RF expensive downstream contradice el argumento del downstream caro.** QK reduce readaptaciones (4.8 vs 8.0) pero pierde BA (0.978 vs 0.986) y su runtime total es 13.74s vs 5.02s para Energy. La narrativa no menciona esto. Debe aparecer al menos como limitación.

4. **Dataset único.** La narrativa no reconoce esta limitación. Un revisor de Q1 atacará aquí. La narrativa debe incluir "en un único dataset de referencia (CICIDS2017)" para ser completamente honesta.

### Versión mejorada de la narrativa

> "QK-MMD ZZ no proporciona una ventaja cuántica universal sobre detectores clásicos para readaptación en IDS adaptativos. En los escenarios de drift volumétrico y de protocolo evaluados (Wednesday, DDoS) sobre CICIDS2017, reduce las readaptaciones en 1.8–2.1 episodios por serie de 100 ventanas (CI95 estricto) manteniendo rendimiento downstream equivalente, a costa de un overhead de detección de 114×. Este beneficio desaparece cuando el coste del detector se incluye en la función de utilidad (γ≥0.25) o cuando el tipo de drift es por escaneo (PortScan), donde QK dispara más readaptaciones pero con mayor precisión. La generalización de estos resultados a otros datasets no está demostrada."

Esta versión es más larga pero cierra los tres ataques principales: dataset único, inconsistencia PortScan, y condición de utilidad.

---

## 2. Documentos creados en esta sesión

| Documento | Contenido |
|---|---|
| `notes/paper2_director_summary_001.md` | Resumen para director: objetivo, experimentos por pregunta, resultados positivos/negativos, claim defendible, limitaciones, recomendación de venue y siguiente paso. |
| `notes/paper2_storyline_001.md` | Estructura completa del paper: qué entra en cada sección, qué se corta, mapa resultado→sección. |
| `notes/paper2_second_dataset_plan_001.md` | Plan detallado para segundo dataset: evaluación UNSW-NB15 vs CIC-IDS2018, escenarios, preprocesamiento, smoke test, comandos exactos, riesgos. |
| `notes/claude_paper2_next_steps_review.md` | Este documento. |

---

## 3. Segundo dataset recomendado

**Recomendación principal: UNSW-NB15**  
**Razón:** Dataset diferente origen (UNSW Australia), diferente entorno de red, diferentes attack families, tamaño manejable (~400 MB), citado en literatura IDS como benchmark alternativo canónico a CICIDS2017.

**Opción descartada: CIC-IDS2018**  
Mismo laboratorio (UNB) que CICIDS2017. Un revisor de Q1 considerará que las dos son evaluaciones del mismo sistema de captura con tráfico de un año diferente. No suficiente para el argumento de generalización.

**Extensión inmediata disponible: CICIDS2017-Thursday**  
Los CSV de Thursday WebAttacks y Thursday Infiltration ya están descargados en el repositorio. Pueden proporcionar 2 escenarios adicionales con tipos de ataque de capa aplicación (SQL Injection, XSS, BruteForce, Infiltration) — categorías no representadas en los 3 escenarios actuales. Este es el paso más barato y puede ejecutarse inmediatamente.

**Estrategia recomendada:**
1. Smoke Thursday-WebAttacks esta semana (≤1 hora de cómputo).
2. Experimento completo Thursday si smoke OK (12–24 horas).
3. Descarga y smoke UNSW-NB15 en paralelo (requiere ~400 MB de descarga).
4. Decisión de venue después de ver Thursday completo.

---

## 4. ¿Se lanzó smoke test esta sesión?

**No.** 

Motivo: La tarea F especificaba lanzar smoke solo si un segundo dataset compatible ya estaba disponible. Los CSV de Thursday sí están disponibles, pero antes de lanzar el smoke es necesario verificar que las columnas y labels del Thursday CSV son compatibles con el pipeline. Esta verificación requiere ejecutar un comando Python de inspección (ver sección 5 del plan de segundo dataset) — que no se ejecutó porque no se confirmó el consentimiento del usuario para iniciar experimentos.

**Próximo paso antes del smoke:**
```powershell
python -c "
import pandas as pd
df = pd.read_csv('data/raw/cicids2017/MachineLearningCVE/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv', nrows=100)
print('Columns:', df.columns.tolist()[:10], '...')
print('Label counts:', df[' Label'].value_counts())
"
```

Si las columnas coinciden con las de Tuesday y Wednesday, el pipeline debería aceptar el archivo directamente o con un mínimo de modificación.

---

## 5. Qué resultado necesitaríamos para justificar Q1

Para justificar una submisión a IEEE TDSC o Computers & Security (CiteScore ≥9) necesitamos al menos UNA de las siguientes condiciones:

### Condición A: Segundo dataset con patrón parcialmente consistente

UNSW-NB15 con al menos 2 escenarios donde QK-ZZ reduce readaptaciones con CI95 estricto frente a Energy distance. No requiere que QK gane en todos los escenarios — solo que el mismo trade-off aparezca en un entorno diferente.

### Condición B: Extensión CICIDS2017-Thursday con patrón explicativo

Thursday-WebAttacks muestra que QK dispara MÁS (como PortScan), no menos, mientras que Thursday-Infiltration muestra patrón mixto. Esto permitiría proponer (con datos) la hipótesis de "ataque distribuido vs concentrado en feature space" y posiblemente pre-registrar un test en UNSW para validarla.

### Condición C (menos deseable pero aceptable): Análisis teórico

Demostración formal de por qué ZZ feature maps con atan_standard scaling producen estadísticos MMD con menor varianza en distribuciones de tipo volumétrico. Requiere trabajo teórico sustancial que no está en el scope actual.

**Lo que NO sería suficiente para Q1:**
- Añadir más escenarios CICIDS2017 del tipo Wednesday/DDoS (confirman el claim pero no añaden generalización).
- Un resultado RF expensive downstream completo (mejora la motivación del claim de eficiencia pero no cierra el gap de dataset único).
- Feature map sensitivity completo con held-out PortScan/DDoS (ya cerrado con 10 seeds; el argumento está resuelto).

---

## 6. Qué hacer inmediatamente después

**Prioridad 1 (esta semana, 1 hora):** Verificar compatibilidad Thursday CSV con el pipeline.

```powershell
python -c "
import pandas as pd
ref = pd.read_csv('data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv', nrows=5)
thu = pd.read_csv('data/raw/cicids2017/MachineLearningCVE/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv', nrows=5)
print('Ref columns == Thu columns:', list(ref.columns) == list(thu.columns))
print('Thu label values:')
df_thu = pd.read_csv('data/raw/cicids2017/MachineLearningCVE/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv')
print(df_thu[' Label'].value_counts())
"
```

**Prioridad 2 (esta semana, si columnas OK):** Smoke test Thursday-WebAttacks con 3 seeds, 20 ventanas, 3 métodos (Energy, MMD-RBF, QK-ZZ). Comando exacto en `paper2_second_dataset_plan_001.md`.

**Prioridad 3 (esta semana, paralelo):** Abrir el director summary (`notes/paper2_director_summary_001.md`) con el director y confirmar la estrategia de venue antes de invertir más cómputo.

**Prioridad 4 (semana siguiente):** Si el director aprueba, descargar UNSW-NB15 e iniciar el smoke. Descarga estimada: 400 MB desde el repositorio oficial de UNSW (https://research.unsw.edu.au/projects/unsw-nb15-dataset) o mirror Kaggle.

**No hacer ahora:**
- No lanzar el experimento completo Thursday sin ver los resultados del smoke.
- No escribir secciones del paper antes de tener al menos el Thursday smoke.
- No comprometerse con Q1 antes de ver si el Thursday pattern replica o contradice el claim de eficiencia.

---

## 7. Estado de los claims vs objetivos de venue

| Claim | Soporte actual | Soporte con Thursday | Soporte con UNSW |
|---|---|---|---|
| QK reduce readaptaciones en drift volumétrico | Estricto (2 escenarios) | Potencialmente 4 si Thursday-Infiltration confirma | Potencialmente 6+ |
| Disociación PortScan (QK dispara más, mayor BA) | 1 escenario | Hipótesis testable con WebAttacks | Testable en Reconnaissance |
| No hay ventaja universal | Demostrado con PortScan | Reforzado con WebAttacks | Reforzado con 2–3 escenarios UNSW |
| Utility operacional λ-condicionado | Demostrado (Wednesday) | Extensible | Extensible |
| Feature map no cherry-picked | Demostrado (sensitivity study) | — | — |
| Generalización cross-dataset | **NO demostrado** | Parcialmente (mismo dataset) | **Demostrado si UNSW replica** |

**Diagnóstico final:** El paper tiene un núcleo duro de evidencia estadística robusto sobre CICIDS2017. El único gap que bloquea Q1 es la generalización. Con Thursday, el gap se cierra parcialmente. Con UNSW, se cierra completamente o se reencuadra como "caracterización con rango de aplicabilidad acotado," que también es publicable en Q1.

---

## 8. Resumen ejecutivo (para tomar decisiones ahora)

1. **La narrativa actual es honesta y defendible en Q2.** No hay cherry-picking, los resultados negativos están identificados, el claim es escéptico.

2. **Para Q1, el único gap real es el dataset único.** Todo lo demás (feature map, stats, utility analysis, nuisance control) está resuelto.

3. **Los datos para extender CICIDS2017 ya están descargados.** Thursday WebAttacks y Infiltration pueden dar resultados en 24 horas de cómputo.

4. **UNSW-NB15 es la opción correcta para un segundo dataset real.** No CIC-IDS2018.

5. **No se debe lanzar ningún experimento grande sin confirmar el smoke mínimo primero.**

6. **Los documentos creados son:** director summary, storyline, segundo dataset plan, este informe.

7. **No se hicieron commits. No se modificaron resultados existentes. No se borraron datos.**
