# CHECKPOINT FINAL — Statistical and claim-scope patch for KBS (v1.20.1 candidate)

Fecha: 2026-07-21. Protocolo congelado: `notes/q1_final_statistical_claims_patch_protocol.md`.
Sin commit/push/tag/release/DOI. Sin experimentos ejecutados. Paper 1 intacto.

## A. Git state

- Branch `main`, HEAD `5fed4b9c8106795822c466527de27c6880fb1424` (= Commit B de v1.20.0).
- Modificados (19): README.md, REPRODUCE.md, main.tex, main_ieee.tex (portado), supplement.tex,
  6 tablas generadas (ambas ediciones), final_manifest.json, MANIFEST.sha256,
  audit_paper2_claims.py, make_final_manifest.py, make_paper2_q1_frontier.py (docstring),
  make_paper2_q1_multiplicity.py, make_paper2_q1_tables.py, test_q1_statistics.py.
- Nuevos (4 a versionar): este protocolo + checkpoint, make_paper2_claim_scope_audit.py,
  tests/test_q1_claim_scope.py. (Excluidos como siempre: PLAN_Q1_DEFINITIVO_VBC.md,
  notes/recovered_run_q1_faseC.py.txt.)
- Diffstat: 19 ficheros, +581/−334.

## B. Harm-rate correction (Bloque A)

- **Antes:** "among the 506 H5-evaluable commits zero were harmful (two-sided exact 95%
  upper bound ≈0.73%)" (×2 en main, ×2 en IEEE); "reported with exact (Clopper–Pearson)
  intervals" + CIs por-benchmark del gate ε=0; "zero observed with a bounded rate".
- **Ahora:** "Across the registered frontier, zero harmful commits were observed among the
  506 H5-evaluable commits; fourteen additional commits were right-censored. These commits
  are clustered within shared seeds, scenarios and policy grids, so they are not treated as
  506 independent Bernoulli trials and no binomial population-rate bound is inferred from
  this count." La garantía formal queda separada: confidence sequences por-proposal +
  deployment-long alpha spending, "a design property, not an inference from this sweep".
  Las fracciones ε=0 pasan a descriptivas sin CIs ("clustered within shared seeds ... not
  independent trials"). "bounded rate" → "zero observed harmful commits".
- Ubicaciones: main.tex (2 sitios + ε=0 + Limitations), main_ieee (portado), generador del
  frontier (docstring: columnas e6_cp_* declaradas descriptivas, nunca citadas como rates).
- **Sensibilidad cluster-aware: NO se realizó** — opción preferida del protocolo adoptada
  (eliminar el bound del main); con todos los clusters a cero, un bootstrap no paramétrico
  fabricaría un límite degenerado, prohibido por la misión.
- Manifest: `harmful_commits` ahora incluye `binomial_upper_bound_reported: false` +
  `reason` (clustering) y renombra la proporción observada a
  `observed_harmful_proportion_h5` (0.0). **No se infiere ningún 0,73%.**

## C. Multiplicity (Bloque B)

- **Antes:** remuestreo de las diferencias observadas etiquetado "exact paired bootstrap"
  (20.000 resamples, p de colas, floor 1/B); familia frontier filtrada por
  `commits_total > 0` (13 celdas, outcome-dependent); main.tex afirmaba inversión normal
  (contradicción paper–código detectada y eliminada).
- **Ahora:** **deterministic centered paired bootstrap test** — d0 = d − mean(d); B =
  **100.000**; p = (extremos+1)/(B+1) bicola; RNG por contraste = seed base 20260721 +
  CRC32(etiqueta) (bit-reproducible, independiente del orden); nunca llamado exacto.
  Sensibilidades pre-declaradas en el CSV (t-test pareado; Wilcoxon, NaN si d≡0), nunca
  sustituyen al principal.
- **Familias fijas sin filtros:** core 6 (Holm) · frontier **15** = 3 políticas × 5 caps,
  PortScan-full/Bonferroni, **incluyendo las 2 celdas sin commits** (BH) · chronological 7
  (BH). Total **28**, 0 fallbacks normal-approximation (el fallback existe etiquetado, no
  usado). Asserts de tamaño en el generador + tests + guards.
- **Resultados:** core 3/6 sobreviven Holm (sin cambio); frontier **13/15** sobreviven BH —
  los 2 no-supervivientes son exactamente vbcref c64/c128 (0 commits, gain ≡ 0, p = 1.0);
  chronological 7/7. **Ningún veredicto científico cambió**; el único cambio de conteo
  (13/13 → 13/15) es la incorporación honesta de las celdas nulas a la familia.
- Paper=código: la frase mandada aparece en main (Limitations), supplement §S5 (método
  completo con fórmula) e IEEE. Columnas nuevas: family_size, p_ttest_sensitivity,
  p_wilcoxon_sensitivity.

## D. Operational semantics (Bloque C)

Arm de Table 11 (D5, seeds 801–830): evaluation stream **balanced** · detector calibration
**balanced** · candidate training **balanced_per_class**, coste de adquisición **no
modelado** · adjudication pool **operating prevalence** · discovery auxiliar (política
random/alert_enriched/disagreement/hybrid), **nunca decide** · validation **uniforme a
prevalencia operativa**, **32 adjudicaciones**, **plain accuracy** (puede evaluar mayoritaria
o totalmente benignos; sin garantía de BA) · alcance = **acquisition_yield_and_delay_only**,
end-to-end **no** modelado. Todo declarado en caption (recortada), §5.5, README, REPRODUCE y
`final_manifest.json → operational_arm_scope` (12 campos), con tests estructurales.
**Desviación documentada en el protocolo:** el párrafo "With the stream and the probe at
operating prevalence…" describía el arm *lite* (`paper2_fk_*_e2e*`), cuyo stream y probe SÍ
están a π (verificado empíricamente: alerts 11.09 vs 11.29 predicho a π=0.01; 20.62 vs 20.46
a π=0.10) — reescribirlo como "balanced" habría sido falso. Se **desambiguó**: el párrafo
nombra el arm, declara su composición exacta (stream+probe a π; calibración y candidate
balanceados; coste no modelado) y elimina "end-to-end claim" y "validation costs little and
protects".

## E. Cohort and affordability (Bloque D)

- **Cohort:** renombrada en paper/tablas/captions a **"VBC-SG-Cohort-sim"** / "a
  proposal-target resampling simulation (Cohort-sim)"; definición en §3.5 con el disclaimer
  mandado ("does not model retention and delayed adjudication of a literal production
  cohort; not claimed to be directly deployable"); flag interno `--vbc-defer-mode cohort`
  intacto.
- **Affordable:** eliminado en todas las superficies (0 restos). Abstract, contribución 3,
  heading de §5.4, párrafo frontier, README → "non-vacuous within the evaluated
  balanced-probe adjudication budget" + "its inspected-flow acquisition cost under
  operational class imbalance is not measured".
- **32 labels:** contribución reescrita ("In the controlled balanced-probe confirmatory
  setting … formal risk control, severe imbalance and stratified deployment-long guarantees
  require larger or differently acquired samples"); "both budgets are realistic" → frase
  mandada sobre workflows asistidos + coste no evaluado; conclusión y "few target labels"
  delimitados; supplement "suffice" calificado "in this balanced-probe setting". El
  resultado de 32 labels NO se borró: queda delimitado.

## F. Claim audit (Bloque E)

- Nuevo generador `make_paper2_claim_scope_audit.py` →
  `results/tables/paper2_final_q1/claim_scope_audit.csv`: **14 claims**, columnas mandadas,
  status computado en vivo (anchors requeridos presentes + frases prohibidas ausentes sobre
  9 superficies); **0 FAIL**.
- Guards añadidos al audit (+26 checks, ahora **521**): sin 0.73/0.726/Clopper; caveat de
  clustering presente; sin "exact paired bootstrap"; frase del bootstrap centrado presente
  en 3 superficies; multiplicity 28 = 6/15/7 con 0 fallbacks y columnas de sensibilidad;
  sin filtro outcome-dependent en el código; sin "stream and the probe at operating
  prevalence" sin desambiguar; sin end-to-end aplicado al commit; manifest con los 12 campos
  de scope; Cohort-sim + disclaimer; sin "affordable"; calificación non-vacuous presente;
  32-labels con scope; sin "zero probability of harm"/"eliminates harmful commits";
  claim_scope_audit ≥12 filas y 0 FAIL. `_texts` ampliado a REPRODUCE.md y a las tablas
  generadas de ambas ediciones.
- Expresiones obsoletas restantes: **0** (barrido final; único hit "both budgets" es la
  frase técnica inocua "across both detectors and both budgets" en supplement §S1).

## G. Technical gates

| gate | resultado |
|---|---|
| pytest | **66/66** (56 + 5 estadística + 5 claim-scope) |
| audit | **521/521** (495 + 26 guards nuevos) |
| hashes | **164/164** (163 + claim_scope_audit.csv) |
| orphan dirs | **0** (ledger 10 bloques / 499 dirs) |
| undefined refs/citations | **0** en los tres PDFs |
| PDFs | **main 32 pp** (+1 por los caveats), supplement 24, IEEE 24 |
| manifest | consistente; audit embebido 521/521; versión aún 1.20.0 (bump en el sellado) |
| multiplicity | 28 = 6/15/7, 0 fallbacks |
| runners científicos ejecutados | **0** |

## H. Files

Ver §A. CSVs científicos regenerados (solo por script): multiplicity.csv (28 filas, método
nuevo), claim_scope_audit.csv (nuevo), MANIFEST.sha256, final_experiment_ledger.csv,
final_manifest.json, 8 tablas .tex. **Ningún experimento ejecutado; ningún CSV primario
tocado.** Incidente reparado y documentado: 3 caracteres U+0007 introducidos por un colapso
de backslashes del heredoc al editar `\approx`; detectados por pdflatex, reparados, PDFs
verificados limpios (0 control chars).

## I. Hostile-review verdict

1. ¿Commits como réplicas independientes? **No** — caveat explícito, sin bound; ε=0
   descriptivo.
2. ¿Rate bound excesivamente preciso? **No** — 0.73%/Clopper/0.116 ausentes de todas las
   superficies.
3. ¿Paper describe el método del código? **Sí** — centered paired bootstrap idéntico en
   main/supplement/código; la contradicción previa (inversión normal vs exacto) eliminada.
4. ¿Familias sin outcome-dependent selection? **Sí** — 6/15/7 fijas; celdas nulas incluidas;
   filtro prohibido por guard+test.
5. ¿Contradicciones de prevalencia? **No** — dos arms desambiguados con scope exacto cada
   uno; manifest field-by-field.
6. ¿Labels adjudicadas vs inspected flows confundidas? **No** — validación = 32
   adjudicaciones (32 inspecciones por construcción); 1/π solo para encontrar ataques
   (discovery); candidate no costeado, declarado.
7. ¿Cohort-sim como cohorte real? **No** — renombrada + disclaimer + no-deployable.
8. ¿32 labels generalizado? **No** — delimitado al controlled balanced-probe setting en
   contribución, discusión y conclusión.
9. ¿Overclaim load-bearing restante? **Ninguno detectado** tras el barrido y los 521 checks.
10. ¿Bloqueante real para KBS? **NINGUNO.**

- BLOCKERS: **ninguno**.
- MINOR ISSUES: (i) main pasa de 31 a 32 pp; (ii) la versión del manifest sigue 1.20.0
  hasta el sellado (bump de .zenodo.json/CITATION.cff/references.bib + re-stamp del manifest
  y del data-availability al autorizar v1.20.1); (iii) las notas históricas conservan las
  cifras antiguas (registro congelado, intencionado).
- **READY FOR v1.20.1 SEALING.**

## Sellado propuesto (NO ejecutado; requiere tu autorización)

1. Bump 1.20.1 (.zenodo.json, CITATION.cff, references.bib nota, data-availability main.tex)
   + port + PDFs. 2. Commit A' científico (todo salvo final_manifest.json). 3. Regenerar y
   verificar manifest sobre A'. 4. Commit B' solo manifest. 5. Tag v1.20.1 → Release →
   Zenodo → release_manifest.json con el nuevo DOI de versión.
