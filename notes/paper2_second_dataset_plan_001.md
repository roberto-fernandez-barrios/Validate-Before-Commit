# Paper 2 — Plan para Segundo Dataset

**Prepared by:** Claude Sonnet 4.6  
**Date:** 2026-06-26  
**Estado del repositorio:** Solo CICIDS2017 disponible en `data/raw/`. No hay UNSW-NB15 ni CIC-IDS2018 descargados.

---

## Evaluación de opciones

### ¿Qué hay disponible ahora mismo?

`data/raw/cicids2017/MachineLearningCVE/` contiene los siguientes CSV (todos de 2018):

| Archivo | Tamaño | Contenido |
|---|---|---|
| Tuesday-WorkingHours.pcap_ISCX.csv | 129 MB | Referencia actual del paper |
| Wednesday-workingHours.pcap_ISCX.csv | 215 MB | DoS (Hulk, Slowloris, etc.) — scenario actual |
| Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv | 74 MB | DDoS — scenario actual |
| Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv | 74 MB | PortScan — scenario actual |
| **Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv** | **50 MB** | **WebAttacks (SQL Injection, XSS, Brute Force) — sin usar** |
| **Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv** | **80 MB** | **Infiltration — sin usar** |
| Friday-WorkingHours-Morning.pcap_ISCX.csv | 56 MB | HeartBleed + benign |
| Monday-WorkingHours.pcap_ISCX.csv | 169 MB | Solo benign |

**Observación crítica:** Los ficheros Thursday y Friday Morning están descargados y sin usar. Representan ataques de categoría diferente (web attacks, infiltration) que los escenarios actuales (volumétrico, escaneo). Esto permite **dos escenarios adicionales dentro de CICIDS2017** con coste computacional inmediato y sin descarga.

---

## 1. Dataset recomendado para "segundo dataset"

### Decisión: UNSW-NB15 (descarga pendiente) + extensión CICIDS2017-Thursday (inmediata)

**Estrategia en dos capas:**

**Capa 1 (inmediata, sin descarga):** Extender CICIDS2017 con los escenarios Thursday-WebAttacks y Thursday-Infiltration. Estos son ataques de tipo completamente diferente (capa aplicación vs volumétrico) que pueden revelar si el comportamiento de QK depende del tipo de ataque. Coste: ~1-3 días de cómputo.

**Capa 2 (requiere descarga, ~400 MB):** UNSW-NB15 como dataset verdaderamente independiente. Diferente red, diferente país, diferentes attack families. Esto es lo que convence a un revisor de Q1 de que el resultado no es específico de CICIDS2017.

---

## 2. Justificación de UNSW-NB15 como segundo dataset

| Criterio | UNSW-NB15 | CIC-IDS2018 |
|---|---|---|
| Compatibilidad con pipeline actual | Alta — CSV con features numéricos + Label | Alta — similar a CICIDS2017 |
| Labels benign/attack | Sí (binary + multi-class) | Sí |
| Drift progresivo construible | Sí — attack families diversas | Sí — 10 tipos de ataque |
| Diferencia respecto a CICIDS2017 | **Alta** — diferente laboratorio, país, red | Baja — mismo laboratorio (UNB) |
| Valor para Q1 | **Alto** — evidencia de generalización | Medio — mismo origen que CICIDS2017 |
| Tamaño | ~400 MB (4 CSV) | ~6–12 GB |
| Riesgo "más de lo mismo" | Bajo — UNSW es el benchmark alternativo canónico | Alto — es "CICIDS pero más grande" |
| Disponibilidad | Público en kaggle/UQ-repo sin registro | Requiere registro en UNB |

**Conclusión:** UNSW-NB15 es la opción correcta para Q1 porque es el dataset benchmark alternativo más citado en literature IDS (Moustafa & Slay 2015), con origen diferente y ataque families diferentes. CIC-IDS2018 viene del mismo laboratorio que CICIDS2017 y un revisor lo notará.

---

## 3. Escenarios de drift posibles

### Para CICIDS2017-Thursday (Capa 1, ya disponible):

| Scenario | Referencia | Drift |
|---|---|---|
| Thursday-WebAttacks | Tuesday BENIGN+attacks | → Thursday WebAttacks (SQL Inj., XSS, BruteForce) |
| Thursday-Infiltration | Tuesday BENIGN+attacks | → Thursday Infiltration |

**Hipótesis:** WebAttacks y Infiltration son ataques de tipo aplicación, con características de feature muy distintas a DDoS/PortScan. Si QK reduce readaptaciones también aquí, el claim se refuerza. Si no, la dependencia del tipo de ataque queda mejor documentada.

### Para UNSW-NB15 (Capa 2, requiere descarga):

El dataset tiene ~2.5M flows con 9 attack families: Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode, Worms.

Escenarios de drift progresivo propuestos:
- **Ref: Normal traffic** → **Drift: DoS** (análogo a DDoS en CICIDS2017)
- **Ref: Normal traffic** → **Drift: Reconnaissance** (análogo a PortScan en CICIDS2017)
- **Ref: Normal traffic** → **Drift: Exploits** (nuevo tipo sin análogo directo)

---

## 4. Columnas y labels a usar

### CICIDS2017-Thursday:
- Mismas 78 features ya preprocesadas en el pipeline actual.
- Label column: ` Label` (con espacio inicial — igual que los otros CSV).
- Clases benignas: 'BENIGN'. Clases atacantes: 'Web Attack – Brute Force', 'Web Attack – XSS', 'Web Attack – Sql Injection', 'Infiltration'.
- **Verificar:** que el script de preprocesamiento actual (`run_paper2_dataset.py` o similar) admite estos labels sin modificación.

### UNSW-NB15:
- 49 features numéricas + categorical (proto, service, state).
- Label binaria: `label` (0=benign, 1=attack) o multi-class `attack_cat`.
- Requiere: alinear nombre de columnas con el pipeline actual o añadir un adaptador.
- **Atención:** Las features no son idénticas a CICIDS2017 (diferente flujo de captura). Habrá que seleccionar un subconjunto compatible o tratar el dataset como dominio separado con su propia normalización.

---

## 5. Preprocesamiento necesario

### CICIDS2017-Thursday (mínimo):
1. Verificar que los Thursday CSV tienen la misma estructura de columnas que los ya procesados.
2. Verificar que el script de progressive readaptation acepta un `--data-cur` apuntando a Thursday.
3. Si hay clases muy minoritarias (Infiltration tiene muy pocos samples), puede ser necesario filtrar o binarizar el label.

**Comando de verificación (ejecutar manualmente antes del smoke):**
```powershell
python -c "
import pandas as pd
df = pd.read_csv('data/raw/cicids2017/MachineLearningCVE/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv', nrows=5)
print(df.columns.tolist())
print(df[' Label'].value_counts())
"
```

### UNSW-NB15:
1. Descargar los 4 ficheros CSV de la fuente oficial (UNSW o Kaggle).
2. Concatenar y crear train/test splits temporales.
3. Mapear features al formato esperado por el pipeline: o bien adaptar el preprocessor, o seleccionar features análogas.
4. Crear script `run_paper2_dataset_unsw.py` o añadir flag `--dataset unsw` al script existente.

---

## 6. Smoke test mínimo

### Capa 1 (CICIDS2017-Thursday) — ejecutar ahora:

**Condición previa:** Verificar que las columnas del Thursday CSV son compatibles con el pipeline.

```powershell
python -m src.experiments.run_paper2_progressive_readaptation `
  --data-ref data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv `
  --data-cur data/raw/cicids2017/MachineLearningCVE/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv `
  --label-col " Label" `
  --outdir results/raw/paper2_thursday_webattacks_smoke_001 `
  --scenario ThursdayWebAttacks `
  --seeds 1,2,3 `
  --methods energy_distance,mmd_rbf,qk_mmd_zz `
  --dim 8 --window-size 128 `
  --n-post-windows 20 `
  --n-ramp-windows 20
```

**Criterio de éxito:** El script completa sin error. El CSV de salida tiene las columnas esperadas (`method`, `seed`, `mean_balanced_accuracy`, `n_adaptations`, `adaptation_efficiency`, `detector_runtime_sec_total`). Las clases no-BENIGN del Thursday CSV son suficientes para construir los streams de drift.

**Criterio de fallo:** Si el pipeline falla porque el Thursday CSV tiene demasiados samples de clase minoritaria o una label inesperada, documentar el error y evaluar si vale la pena parchear el preprocessor.

### Capa 2 (UNSW-NB15) — solo después de descarga:

```powershell
python -m src.experiments.run_paper2_progressive_readaptation `
  --data-ref data/raw/unsw_nb15/UNSW_NB15_training-set.csv `
  --data-cur data/raw/unsw_nb15/UNSW_NB15_testing-set.csv `
  --label-col label `
  --outdir results/raw/paper2_unsw_nb15_smoke_001 `
  --scenario UNSW_DoS `
  --seeds 1,2,3 `
  --methods energy_distance,mmd_rbf,qk_mmd_zz `
  --dim 8 --window-size 128 `
  --n-post-windows 20 `
  --n-ramp-windows 20
```

**Nota:** Este comando es tentativo. Requiere que el preprocesador acepte el formato UNSW o un adaptador previo.

---

## 7. Experimento completo (si smoke funciona)

### Capa 1 — CICIDS2017-Thursday:

```powershell
python -m src.experiments.run_paper2_progressive_readaptation `
  --data-ref data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv `
  --data-cur data/raw/cicids2017/MachineLearningCVE/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv `
  --label-col " Label" `
  --outdir results/raw/paper2_thursday_webattacks_full_001 `
  --scenario ThursdayWebAttacks `
  --seeds 1..30 `
  --methods energy_distance,mmd_rbf,ks_max,jsd,qk_mmd_zz,qk_mmd_pauli_xz `
  --dim 8 --window-size 128 `
  --n-post-windows 100 `
  --n-ramp-windows 80
```

Y análogamente para Thursday-Infiltration.

### Capa 2 — UNSW-NB15 completo:

2–3 escenarios, 30 seeds, 100 ventanas, todos los detectores. Runtime estimado: similar a CICIDS2017 (~15–20 horas por escenario para QK-ZZ).

---

## 8. Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Thursday CSV tiene labels mal balanceadas (Infiltration < 50 samples/ventana) | Media | Alta | Binarizar a BENIGN vs ATTACK; si insuficiente, descartar ese scenario |
| Pipeline no acepta label column diferente | Baja | Media | Parche de una línea en el preprocessor |
| UNSW-NB15 requiere feature engineering extenso (features no numéricas) | Media | Alta | Seleccionar solo features numéricas (35 de 49); pérdida de información pero smoke rápido |
| QK-ZZ más lento en UNSW (más features, distinta distribución) | Baja | Baja | Runtime análogo si dim=8 |
| Resultado en UNSW completamente negativo (QK pierde en todos los scenarios) | Media | Media | Ver sección 10 |
| UNSW-NB15 download no disponible sin VPN/registro especial | Baja | Alta | Usar Kaggle mirror (no requiere registro institucional) |

---

## 9. Qué resultado en Capa 1 (Thursday) reforzaría Q1

El resultado más útil para Q1 sería:

**Escenario Thursday-WebAttacks:** QK-ZZ dispara **más** readaptaciones que Energy (como en PortScan), pero con mayor BA. Esto confirmaría que la disociación no es accidental: QK es más sensible en ataques distribuidos en feature space (web attacks tienen features textuales/discretas que afectan más al kernel cuántico) y más conservador en ataques volumétricos (DDoS, Wednesday).

Si esto ocurre, la explicación geométrica gana credibilidad y el paper puede proponer una hipótesis de trabajo: "QK-MMD ZZ es más eficiente en drift con señal distribucional concentrada (volumétrico/protocolo) y más trigger-activo en drift con señal dispersa (web/scan)."

**Escenario Thursday-Infiltration:** Resultado esperado menos claro. La infiltración en CICIDS2017 tiene muy pocos samples; si los streams son suficientes para construir drift progresivo, el resultado podría ser ruidoso.

---

## 10. Qué resultado negativo en UNSW-NB15 seguiría siendo publicable

Un resultado donde QK-ZZ **no** reduce readaptaciones en ningún escenario UNSW-NB15 sería publicable si:

1. Se reporta honestamente: "En UNSW-NB15, el patrón de eficiencia observado en CICIDS2017 Wednesday y DDoS no se replica. QK-ZZ no produce menos readaptaciones que Energy distance en ninguno de los X escenarios evaluados."

2. Se usa como evidencia de la hipótesis de dependencia de dataset/tipo de ataque: "La ventaja de eficiencia de QK-MMD no generaliza entre datasets de redes distintas, lo que limita las afirmaciones de ventaja operacional universal."

3. El claim se reencuadra: "Caracterización empírica de QK-MMD como detector de drift en IDS: condiciones de utilidad y limitaciones de generalización."

Este framing sigue siendo publicable en Q2 fuerte y posiblemente en Q1 venues que valoran la honestidad metodológica (como IEEE T-IFS, que pide evaluación en múltiples datasets).

**Lo que NO se puede hacer:** Suprimir el resultado UNSW negativo si se lanza el experimento. Si se ejecuta, se reporta.

---

## 11. Orden de actuación recomendado

1. **Inmediato (esta semana):** Verificar columnas del Thursday CSV con el comando Python de la sección 5.
2. **Si columnas OK, lanzar smoke Thursday-WebAttacks** (3 seeds, 20 ventanas). Duración estimada: 30–60 minutos.
3. **Si smoke OK, lanzar experimento completo Thursday** (30 seeds, 100 ventanas, todos los detectores). Duración estimada: 12–24 horas.
4. **En paralelo:** Descargar UNSW-NB15 (fuente: https://research.unsw.edu.au/projects/unsw-nb15-dataset o Kaggle mirror). Verificar formato.
5. **Smoke UNSW** (3 seeds, 20 ventanas). Solo si el Thursday experiment ya tiene resultados y el pipeline es estable.
6. **Experimento completo UNSW** solo si el smoke pasa y el director aprueba el coste computacional adicional.
