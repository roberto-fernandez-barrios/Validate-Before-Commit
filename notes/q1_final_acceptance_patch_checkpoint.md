# CHECKPOINT — recuperación/reemplazo del budget frontier (q1-final-patch)

Fecha: 2026-07-21. Rama `main`, HEAD `cb9040c` (v1.19.1), working tree con el patch sin
commitear. Ningún commit/push/tag/release/DOI ejecutado.

## A. Recuperación forense

- Lugares inspeccionados (trail completo en `docs/SCIENTIFIC_PROVENANCE.md`):
  git history/pickaxe, reflog, fsck (16 blobs no alcanzables + 1 commit colgante + 2 trees),
  ficheros gitignorados en disco, file-history, el directorio de trabajo local recuperado,
  `__pycache__`, y fingerprinting de los 99 outputs publicados.
- **Driver recuperado: SÍ** — `run_q1_faseC.py` intacto en el directorio de trabajo local
  recuperado (SHA256 `655309bf…`; copia verbatim conservada localmente sin versionar, identificada por ese SHA256;
  también `run_q1_faseD.py` y `run_q1_faseD5.py`).
- **Configuración exacta recuperada: SÍ** — los parámetros fijos son los defaults del runner
  (window 128, dim 8, train 2000/clase, adapt 512/clase, detector-ref 256, calib 30, thr-q
  0.95, k=3, cooldown 10, svc_rbf, ks max, trigger detector); ton_zero añade
  `--trigger-mode random --trigger-prob 0.05 --max-severity 0`; anchors point/strict a b=32.
- **Evidencia de bit-identidad** (criterio del protocolo, bajo el runner CORREGIDO):
  - `q1fc_ps_full_vbcref_c512_bonf` (PortScan, 0 diferidos): 5/5 CSVs bit-idénticos, 30 seeds.
  - `q1fc_ton_full_vbcref_c256_bonf` (ToN, 0 diferidos): 5/5 bit-idénticos.
  - `q1fc_ton_zero_ebcsdef_c256_bonf` (zero drift): 5/5 bit-idénticos.
  (Única columna nueva documentada: `served_model_version`.)

## B. Ruta seguida

**RUTA A — targeted rerun.** 72 arms sin commits diferidos reutilizados (provably bit-safe;
reutilización registrada en su `run_config.json`); 27 arms con ≥1 commit diferido
re-ejecutados con el driver versionado. Backup pre-fix completo en
`results/raw/_v1191_frontier_backup_pre_temporal_fix/` (27 dirs + derivados publicados).

## C. Configuración

Fuente canónica: `configs/q1_budget_frontier_v2.json` (todos los parámetros explícitos, con
provenance y nota de que igualan byte a byte los defaults del argparse validados por
bit-identidad). Driver: `src/experiments/run_q1_budget_frontier.py`. Tabla parámetro→
fuente→confianza en `docs/SCIENTIFIC_PROVENANCE.md` (todo "exact").

## D. Ejecución

- Esperadas: 99 (enumeración del driver == tags publicados, verificado por diff).
  Desglose exacto: **90 celdas risk-controlled** (3 escenarios × 3 políticas
  {ebcsdef, vbccoh, vbcref} × 5 caps {64,128,256,512,1024} × 2 schedules {bonf, pser})
  **+ 9 anchors/controles** (3 escenarios × {none = always-deploy, point = labeled_probe
  b=32, strict = labeled_probe b=32 con margen 0.001}); los anchors proveen la referencia
  naive del endpoint e2 y los controles de coste cero, y no forman parte del grid
  risk-controlled de 90 configuraciones.
- Completadas: 99/99 — `--validate-complete` PASS (27 frescas + 72 reutilizadas marcadas).
- Seeds: 501–530 por arm (verificado por el marker de completitud).
- Comandos: por-arm en `results/raw/q1fc_*/command.txt` + `run_config.json` +
  `environment.json`; ledger en `results/raw/budget_frontier_run_ledger.csv` (27 `done`,
  0 fallos/reintentos, ~280–330 s/arm, 5 carriles paralelos, ~75 min).

## E. Old vs new (v1.19.1 → corregido)

Accounting del frontier (90 celdas policy): **IDÉNTICO** —
commits 520→520, immediate 340→340, deferred 180→180, evaluable H5 506→506, censored 14→14,
harmful H5 0→0, harmful-until-next 0→0, CP95 upper bound 0.726% (~0.73%, igual).
Decisiones y ventanas de resolución de los 27 arms re-ejecutados: idénticas fila a fila
(verificado). Abstención, delay, labels/proposal, zero-drift commits (0), nº de propuestas:
sin cambio. **Lo único que cambia es la served BA** de los arms con commits diferidos
(≤0.14 pts a la baja — el crédito retroactivo eliminado):

| celda (ps_full/bonf) | gain old → new | %naive old → new |
|---|---|---|
| ebcsdef c64  | +3.843 → +3.728 | 53% → 52% |
| ebcsdef c128 | +5.106 → +5.022 | 71% → 70% |
| ebcsdef c256 | +5.907 → +5.883 | 82% → 81% |
| ebcsdef c512 | +6.741 → +6.730 | **93% → 93%** |
| ebcsdef c1024| +7.310 → +7.299 | 101% → 101% |
| vbccoh c512  | +5.843 → +5.825 | **81% → 81%** |
| vbcref c512  | +4.916 (sin cambio) | **68%** |

Configuraciones no-vacuas: **12 → 12** (mismas celdas). Primer cap no-vacuo: ebcsdef 64,
vbccoh 256, vbcref 512 (sin cambio). Conclusión científica: **sobrevive íntegra**; el efecto
del bug era una inflación ≤0.14 pts de la served BA, sin efecto en decisiones ni en harm.

## F. Reproducibilidad

Driver + config versionados; command logs y run_config por arm; ledger; hashes
`MANIFEST.sha256` 163/163; `final_experiment_ledger.csv` 10 bloques / 499 dirs / **0
huérfanos**; manifest `final_manifest.json` consistente (harm block = CSV = manuscrito).

## G. Trabajo editorial no dependiente

- **Operacional (Bloque C):** Table 11 → "Attack-label acquisition yield under operational
  prevalence" (ambas ediciones, generador incluido); §5.5 reescrito (stream/calibración
  balanceados declarados, candidate batch balanceada y no costeada, discovery no decide,
  validation uniforme 32 adjudicaciones por plain accuracy, sin garantía BA a prevalencia
  extrema); abstract y contribución 4 reformulados; README/REPRODUCE alineados;
  instrumentación de scope en el runner (11 campos explícitos).
- **Cronología (Bloque D):** formulación exacta en abstract/contribuciones/README (point y
  strict ganan en las dos UNSW sanas; VBC-SG en la 20% pero no la 40%; Wednesday intra-day =
  contraejemplo sano no resuelto; cero net harm en 13 replays); overclaim del README
  ("every gate beats") eliminado.
- **Equivalencia (Bloque E):** renombrada "bootstrap CI-based equivalence assessment"
  (forma interval-inclusion de TOST) en script/caption/manuscrito; `p_low/p_high` →
  `boot_frac_*` (diagnósticos, no p-values); veredictos sin cambio.
- **Multiplicidad (Bloque E):** p-values pareados exactos (bootstrap determinista 20.000
  resamples, seed por-contraste) en **26/26 contrastes** (0 fallbacks); familias Holm/BH sin
  cambio; supervivencias sin cambio (core 3/6 nominales, las 3 sobreviven; frontier 13/13;
  chrono 7/7); columna `p_method`; supplement §S5 actualizado.
- **Guards (Bloque G):** +18 checks del audit (C1–C3 operacional, D1 cronológico universal,
  G1 semántica temporal estructural, README/highlights ahora escaneados) + 3 tests nuevos de
  estadística + 6 tests temporales T1–T6.
- **Pulido (Bloque F):** abstract 288→~230 palabras (81% conservado por guard de no-
  misatribución); sin lenguaje "safe/guaranteed"; "zero observed harmful … bounded rate"
  intacto; trazabilidad íntegra en supplement/notas.

## H. Validación

| gate | resultado |
|---|---|
| pytest | **56/56** (47 base + 6 temporales + 3 estadística) |
| audit | **495/495** (477 base + 18 guards nuevos) |
| hashes | **163/163** (0 extras sin fijar) |
| orphan dirs | **0** |
| refs indefinidas | **0** en los tres PDFs |
| PDFs | main 31 pp, supplement 24 pp, IEEE 24 pp (23→24 por captions/scope ampliados) |
| manifest | consistente; versión 1.19.1 sin bump (pendiente de sellado) |
| números obsoletos | 0 (barrido de 3.84/6.74/8.67/53%/frases prohibidas) |
| frontera 99 arms | `--validate-complete` PASS |

Corrección temporal (Bloque A): bug reproducido con tests que fallaban (T1/T2/T3/T5 rojos
sobre el código original), loop reestructurado (servir→evidencia→resolución→trigger; commits
efectivos en t+1, misma regla immediate/deferred), invariante verificado también sobre datos
reales re-ejecutados (30 seeds × 100 ventanas, 17 commits todos diferidos: PASS).

## I. Dictamen

- **BLOQUEANTES RESTANTES: ninguno load-bearing.**
- Correcciones menores/observaciones honestas:
  1. `main_ieee.pdf` pasa de 23 a 24 páginas (más disclosure; sin límite editorial violado).
  2. El manifest conserva `source_commit_sha = cb9040c` + árbol sucio: **tras el commit de
     sellado hay que re-ejecutar `make final-manifest`** (y idealmente `make final-paper`)
     para estampar el SHA definitivo, como en sellados anteriores.
  3. Los `run_config.json` de las 27 reruns registran `working_tree_dirty: true` (honesto:
     se ejecutaron con el patch sin commitear). Si se desea, pueden re-ejecutarse tras el
     commit con `--force` para registrar el SHA sellado — científicamente innecesario
     (outputs deterministas ya verificados).
  4. La nota histórica `notes/q1_faseC_checkpoint_001.md` conserva los números pre-fix
     (registro congelado de la fase original; intencionado).
- **VEREDICTO: LISTO PARA SELLADO v1.20.0** (a falta únicamente de los pasos de git/release
  reservados al autor).

## Comandos exactos para el sellado (NO ejecutados; requieren tu autorización)

```bash
git add -A
git commit -m "q1-final-patch: deferred-commit temporal semantics, frontier rerun, scope-accurate operational claims, exact bootstrap statistics"
# re-estampar manifest con el SHA del commit anterior y sellar:
make final-paper PY=C:/Users/masteria.DOMINE/AppData/Local/miniconda3/envs/paper2/python.exe
git add -A && git commit -m "Stamp v1.20.0 artifact manifest"
git tag v1.20.0 && git push && git push --tags
# después: GitHub Release + Zenodo/DOI + actualizar CITATION.cff/.zenodo.json a 1.20.0
```
