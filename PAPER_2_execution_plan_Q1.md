# PAPER 2 — Execution Plan Q1-Oriented

## 0. Decisión de partida

Este paper se construirá como un trabajo de **drift-aware cybersecurity learning** basado en **Quantum Kernel MMD**.

La historia científica queda fijada así:

```text
Paper 1:
    El kernel importa cuando ya existe distribution shift.

Paper 2:
    Usamos la geometría inducida por kernels cuánticos para monitorizar drift
    y activar respuestas adaptativas que reduzcan degradación downstream.

Paper 3:
    Extendemos la adaptación a entornos adversariales/agentes.
```

La aportación no será “un detector cuántico más”, sino:

> Una capa calibrada de monitorización de drift basada en Quantum Kernel MMD, evaluada frente a detectores clásicos y conectada a un modelo downstream de ciberseguridad para medir utilidad operativa.

---

## 1. Criterio Q1

Para aspirar a un Q1, el paper no debe quedarse en:

```text
QK-MMD detecta drift.
```

Debe demostrar:

```text
1. QK-MMD se puede calibrar bajo no-drift.
2. QK-MMD tiene potencia de detección comparable o complementaria frente a detectores clásicos.
3. El comportamiento depende del feature map y de la dimensión.
4. La detección sirve para activar una respuesta adaptativa.
5. Esa respuesta reduce degradación downstream o tiempo bajo degradación.
6. El coste computacional se mide y se discute con honestidad.
```

---

## 2. Claim objetivo

Claim fuerte pero prudente:

> We propose and evaluate Quantum Kernel MMD as a calibrated drift-monitoring layer for cybersecurity learning systems. Rather than claiming universal quantum superiority, we show when quantum-induced discrepancy signals provide complementary drift sensitivity and whether they can trigger adaptive responses that reduce downstream performance degradation under non-stationary conditions.

Versión en español:

> Proponemos y evaluamos Quantum Kernel MMD como una capa calibrada de monitorización de drift para sistemas de aprendizaje en ciberseguridad. En lugar de afirmar una superioridad cuántica universal, estudiamos cuándo las señales inducidas por kernels cuánticos aportan sensibilidad complementaria y si permiten activar respuestas adaptativas que reduzcan la degradación del rendimiento bajo condiciones no estacionarias.

---

## 3. Lo que NO se mete en esta primera versión

Para no bifurcarnos:

```text
NO RL en la primera versión.
NO meta-learning.
NO defensa autónoma completa.
NO ranking de stealthiness.
NO auditability gap como contribución central.
NO muchos datasets al principio.
NO muchos modelos downstream al principio.
```

Eso puede venir después.

Primera versión fuerte:

```text
QK-MMD + calibración + comparación clásica + adaptación sencilla + coste.
```

---

## 4. MVP científico

El MVP del paper debe responder a esta pregunta:

> Si entreno un modelo de ciberseguridad en un régimen de referencia, ¿puede una señal QK-MMD detectar cuándo las ventanas entrantes cambian de distribución y activar una adaptación que reduzca la degradación?

MVP mínimo:

```text
Dataset:
    CICIDS2017 reducido

Detector propuesto:
    Quantum Kernel MMD

Detectores clásicos:
    KS
    JSD
    MMD-RBF

Modelo downstream:
    SVC-RBF

Adaptación:
    Recalibración de threshold o reentrenamiento sencillo

Métricas:
    FPR
    detection power
    AUROC de detección
    detection delay
    balanced accuracy post-drift
    degradation area
    runtime
```

---

## 5. Arquitectura técnica recomendada

Crear una carpeta separada para Paper 2:

```text
paper_2/
  README.md

  data/
    raw/
    processed/
    splits/

  results/
    raw/
    aggregated/
    figures/
    tables/
    logs/

  src/
    data/
      load_cicids.py
      preprocessing.py
      windowing.py

    drift_detection/
      base.py
      ks_detector.py
      jsd_detector.py
      mmd_rbf_detector.py
      qk_mmd_detector.py
      calibration.py
      metrics.py

    quantum/
      feature_maps.py
      quantum_kernel.py
      statevector_backend.py

    models/
      classical.py
      thresholding.py

    adaptation/
      recalibration.py
      retraining.py

    experiments/
      run_smoke.py
      run_calibration.py
      run_detection_power.py
      run_streaming.py
      run_downstream_adaptation.py
      aggregate_results.py
      make_plots.py

    utils/
      config.py
      logging.py
      seeds.py
      io.py

  manuscript/
    paper.md
    references.bib
```

Si ya existe un repo con `src/experiments`, no hace falta duplicarlo todo. Se puede empezar creando solo:

```text
src/drift_detection/
src/adaptation/
src/experiments/run_paper2_smoke.py
```

---

## 6. Primer commit recomendado

Desde la raíz del repo:

```powershell
git checkout -b paper2-qkmmd-drift

mkdir paper_2
mkdir paper_2\results
mkdir paper_2\results\raw
mkdir paper_2\results\aggregated
mkdir paper_2\results\figures
mkdir paper_2\results\tables
mkdir paper_2\results\logs

mkdir src\drift_detection
mkdir src\adaptation

New-Item src\drift_detection\__init__.py -ItemType File
New-Item src\adaptation\__init__.py -ItemType File

New-Item src\drift_detection\mmd_rbf_detector.py -ItemType File
New-Item src\drift_detection\qk_mmd_detector.py -ItemType File
New-Item src\drift_detection\ks_detector.py -ItemType File
New-Item src\drift_detection\jsd_detector.py -ItemType File
New-Item src\drift_detection\calibration.py -ItemType File
New-Item src\drift_detection\metrics.py -ItemType File
New-Item src\drift_detection\windowing.py -ItemType File

New-Item src\adaptation\recalibration.py -ItemType File
New-Item src\adaptation\retraining.py -ItemType File

New-Item src\experiments\run_paper2_smoke.py -ItemType File
```

Commit:

```powershell
git add .
git commit -m "Initialize Paper 2 drift detection modules"
```

---

## 7. Esquema de detector común

Todos los detectores deben seguir una interfaz parecida:

```python
class DriftDetector:
    def fit(self, X_ref):
        ...

    def score(self, X_cur) -> float:
        ...

    def calibrate(self, X_ref, alpha: float = 0.05):
        ...

    def predict(self, X_cur) -> dict:
        return {
            "score": score,
            "threshold": threshold,
            "drift_detected": bool,
            "p_value": optional,
            "runtime_sec": runtime,
        }
```

Esto permite comparar todos los detectores con el mismo runner.

---

## 8. Implementación inicial de MMD

La estadística MMD debe ser reusable para kernel clásico y cuántico.

Función base:

```python
def mmd2_from_kernel(Kxx, Kyy, Kxy, biased=True):
    if biased:
        return Kxx.mean() + Kyy.mean() - 2.0 * Kxy.mean()

    m = Kxx.shape[0]
    n = Kyy.shape[0]

    sum_xx = (Kxx.sum() - np.trace(Kxx)) / (m * (m - 1))
    sum_yy = (Kyy.sum() - np.trace(Kyy)) / (n * (n - 1))
    sum_xy = Kxy.mean()

    return sum_xx + sum_yy - 2.0 * sum_xy
```

Primero usar biased MMD por simplicidad y estabilidad. Luego se puede comparar con unbiased.

---

## 9. Calibración

La calibración debe convertir score en decisión.

Método inicial recomendado:

```text
Permutation calibration
```

Proceso:

```text
1. X_ref y X_cur se juntan.
2. Se permutan etiquetas de ventana.
3. Se recalcula MMD B veces.
4. Threshold = percentil 1-alpha de la distribución nula.
5. Si score_real > threshold → drift.
```

Parámetros iniciales:

```text
alpha = 0.05
B = 100 para smoke
B = 500/1000 para experimento final
```

CSV esperado:

```text
detector,alpha,B,threshold,score,drift_detected,p_value,runtime_sec
```

---

## 10. Primer smoke test

Objetivo:

> comprobar que el pipeline funciona de extremo a extremo.

Configuración:

```text
dataset: CICIDS reducido
reference window: 128 muestras
current window: 128 muestras
dimensions: 4, 6
drifts:
    no_drift
    mean_shift
    gaussian_noise
detectors:
    KS
    JSD
    MMD-RBF
    QK-MMD-ZZ-r1
seeds:
    42
```

Expected behaviour:

```text
no_drift:
    baja tasa de activación

mean_shift / gaussian_noise:
    score superior a no_drift
    detección más frecuente conforme aumenta severidad
```

No buscamos todavía resultados bonitos. Buscamos que todo funcione.

---

## 11. Comando objetivo del smoke test

Comando ideal cuando esté implementado:

```powershell
python -m src.experiments.run_paper2_smoke `
  --data data/processed/cicids_subset.csv `
  --outdir paper_2/results/raw/smoke_001 `
  --dims 4,6 `
  --window-size 128 `
  --detectors ks,jsd,mmd_rbf,qk_mmd `
  --q-feature-maps zz `
  --q-reps 1 `
  --drifts no_drift,mean_shift,gaussian_noise `
  --severities 0.1,0.3 `
  --seeds 42 `
  --alpha 0.05 `
  --n-permutations 100
```

---

## 12. CSV raw esperado

Cada ejecución debe generar filas con este esquema:

```text
run_id
dataset
protocol
seed
dim
window_size
detector
q_feature_map
q_reps
drift_type
severity
alpha
n_permutations
score
threshold
p_value
drift_detected
true_drift
runtime_sec
memory_mb
```

Más adelante, añadir downstream:

```text
model
adaptive_action
bal_acc_before
bal_acc_after
f1_before
f1_after
auc_before
auc_after
degradation_area
recovery_time
unnecessary_adaptation
```

---

## 13. Métricas agregadas

Archivo agregado:

```text
paper_2/results/aggregated/smoke_001_agg.csv
```

Columnas:

```text
detector
dim
drift_type
severity
power_mean
power_std
fpr_mean
score_mean
score_std
threshold_mean
threshold_std
runtime_mean
runtime_std
```

---

## 14. Figuras mínimas del primer ciclo

Después del smoke test:

```text
1. score_by_drift_type.png
2. detection_rate_by_severity.png
3. runtime_by_detector.png
```

No hacer figuras complejas hasta validar resultados.

---

## 15. Segundo experimento: calibración seria

Cuando el smoke funcione:

```text
protocol: no_drift
window_size: 64, 128, 256
dims: 4, 6, 8
detectors: KS, JSD, MMD-RBF, QK-MMD-ZZ, QK-MMD-PauliXZ
seeds: 42, 123, 999
alpha: 0.01, 0.05, 0.10
permutations: 500
```

Objetivo:

```text
target alpha ≈ empirical FPR
```

Figura:

```text
target_alpha vs empirical_fpr
```

---

## 16. Tercer experimento: detection power

```text
drifts:
    mean_shift
    scaling_drift
    gaussian_noise
    feature_dropout
    feature_sign_flip

severities:
    low, medium, high

dims:
    4, 6, 8, 10, 12

detectors:
    KS
    JSD
    MMD-RBF
    QK-MMD-ZZ
    QK-MMD-Z
    QK-MMD-PauliXZ
```

Objetivo:

```text
power curves por detector y drift type
```

Figura clave:

```text
detection_power_vs_severity.png
```

---

## 17. Cuarto experimento: streaming / delay

```text
reference window fixed
current window sliding
drift point known
abrupt drift
gradual drift
```

Métricas:

```text
detection_delay
missed_detection_rate
false_alarm_count
```

Figura clave:

```text
drift_signal_over_time_with_threshold.png
```

---

## 18. Quinto experimento: downstream adaptation

Estrategias:

```text
A. no_monitoring_no_adaptation
B. classical_detector_adaptation
C. qk_mmd_detector_adaptation
D. oracle_adaptation
```

Acción inicial:

```text
recalibrate threshold
```

Modelo inicial:

```text
svc_rbf
```

Métricas:

```text
balanced_accuracy_over_time
degradation_area
recovery_time
unnecessary_adaptations
```

Figura clave:

```text
downstream_performance_over_time.png
```

Esta es la figura que más acerca el paper a Q1.

---

## 19. Orden de trabajo recomendado

No hacer todo a la vez.

Orden correcto:

```text
1. Implementar MMD-RBF.
2. Implementar QK-MMD reutilizando quantum kernel del Paper 1 si existe.
3. Implementar calibración por permutación.
4. Implementar smoke test.
5. Agregar resultados.
6. Hacer 3 figuras básicas.
7. Revisar si la señal tiene sentido.
8. Añadir detección power.
9. Añadir streaming delay.
10. Añadir downstream adaptation.
```

---

## 20. Definition of Done del primer milestone

El primer milestone queda completado cuando exista:

```text
src/drift_detection/mmd_rbf_detector.py
src/drift_detection/qk_mmd_detector.py
src/drift_detection/calibration.py
src/experiments/run_paper2_smoke.py

paper_2/results/raw/smoke_001/*.csv
paper_2/results/aggregated/smoke_001_agg.csv
paper_2/results/figures/score_by_drift_type.png
paper_2/results/figures/detection_rate_by_severity.png
paper_2/results/figures/runtime_by_detector.png
```

Y se pueda decir:

> El pipeline Paper 2 funciona de extremo a extremo para no-drift y drift sintético simple.

---

## 21. Primer texto de manuscrito que se puede empezar ya

Párrafo inicial:

> Cybersecurity learning systems are rarely deployed under the same distributional regime in which they were trained. Network traffic evolves, attack behaviours change, logging pipelines are modified, and the statistical relationship between features and labels may drift over time. Under these conditions, evaluating a model only by its initial predictive performance provides an incomplete picture of reliability. A model may remain accurate for a time, degrade silently, or require adaptation once the incoming data no longer resembles the reference regime. This makes drift monitoring a necessary component of robust cybersecurity learning systems.

Segundo párrafo:

> Recent evidence suggests that kernel-induced geometry can materially affect robustness under distribution shift. This motivates a complementary question: if kernel geometry affects how models behave once shift has occurred, can kernel-induced discrepancy signals also help monitor when the data regime itself is changing? In this work, we study Quantum Kernel Maximum Mean Discrepancy as a drift-monitoring layer for cybersecurity models.

---

## 22. Toque de atención

No desviarse ahora a RL, meta-learning o más datasets.

La prioridad es construir el núcleo:

```text
QK-MMD detector calibrado
+
comparación clásica
+
adaptación downstream sencilla
```

Cuando eso exista, ya decidimos si merece añadir RL, más datasets o modelos cuánticos downstream.
