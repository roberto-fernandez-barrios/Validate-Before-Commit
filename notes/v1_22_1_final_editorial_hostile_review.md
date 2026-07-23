# v1.22.1 Final Editorial Hostile Review (bounded)

Scope: editorial/scope corrections and derived analyses only. Twenty questions, answered
against the final build (pytest 135/135, audit 625/625, hashes 183/183, main 33 pp /
supplement 30 pp / IEEE 25 pp, 0 undefined refs/citations).

1. **¿El PDF cita la versión, DOI y commit correctos?** Sí. Data Availability (CAS e
   IEEE) declara artifact version v1.22.0, version DOI 10.5281/zenodo.21517899, concept
   DOI 10.5281/zenodo.21322256, tag v1.22.0 y sealing commit
   43d9c255af48db9bcc3c6eb341a153381b18c8e8. La declaración v1.20.2 obsoleta desapareció
   (las menciones restantes de v1.20.2 son referencias factuales a los baselines de
   parity, no declaraciones de versión). Guards: 5 audit checks + 2 pytest tests. No se
   afirma que exista v1.22.1.
2. **¿Todos los claims size-matched están limitados a zero drift?** Sí. Abstract,
   contribuciones, §5.3 (heading incluido), Discussion, practitioner guidance,
   conclusión, highlights, README y REPRODUCE llevan el alcance zero-drift /
   random-proposal / balanced-pools / SVC-RBF / own-transformer / nominal parity; la
   limitación "only under zero drift" de Limitations se conserva. Barridos de frases
   prohibidas ejecutados y guardados en tests/audit.
3. **¿El graphical abstract muestra ese alcance?** Sí: bloque "ZERO-DRIFT CONTROL" con
   "own preprocessing + 2,000/class nominal size parity → mean BA equivalent within
   ±0.5 pp → no measurable point/strict gain in this control", flujo condicional
   (nominal parity evaluated? → no/uncertain vs yes-under-zero-drift) y badge de scope;
   sin regla universal de despliegue. Legibilidad verificada en el PNG (2129×857) y en
   ambos PDFs.
4. **¿El README dejó de recomendar gating universal?** Sí. La recomendación es
   condicional ("When candidate construction or evidence conditions remain asymmetric or
   uncertain, validate the challenger…") seguida inmediatamente del resultado zero-drift
   sin ganancia medible a paridad nominal. Guards en audit y pytest impiden la
   reaparición.
5. **¿Se distingue nominal size parity de evidencia plenamente comparable?** Sí:
   "nominal per-class sample-size parity" en las superficies; caveat de Method (temporal
   coverage, diversity, subtype support, label quality, duplication, prevalence,
   effective sample size); Discussion: "not a consequence of equal row counts alone".
6. **¿La equivalencia se expresa siempre con margen?** Sí; "identical/equal performance"
   ausentes (test); cada claim de equivalencia nombra ±0.5 pp CI90.
7. **¿Se reportan ±0.2, ±0.5 y ±1.0?** Sí: `equivalence_margin_sensitivity.csv` (18
   contrastes), sentencia de margin-dependence en §5.3, y la sensibilidad ±0.2 en el
   abstract. ±0.5 identificado como primario preregistrado.
8. **¿PortScan se presenta con su sensibilidad al margen?** Sí: no equivalente a ±0.2
   (CI90 [−0.0995, 0.494]), equivalente a ±0.5 (por 0.006 pp, declarado) y ±1.0;
   pinneado por audit y pytest contra el CSV.
9. **¿La tabla 512+gate vs 2.000+naive usa solo outputs existentes?** Sí: fuentes
   exclusivas = 5 CSVs sellados de `size_matched_own_transformer_001` + config
   congelado; celdas selladas asserted byte-idénticas; las únicas cifras nuevas son
   CI95 descriptivos gate-vs-never con el bootstrap determinista idéntico, etiquetadas
   descriptive/uncorrected. 2,976 = 2×1,488 derivado de config y verificado.
10. **¿La tabla evita claims económicos no soportados?** Sí: "counts, not costs",
    inspected-flow no modelado, "no economic dominance is claimed" en caption y texto;
    guards presentes. No se equiparan costes de adquisición de labels.
11. **¿La evidencia frozen está etiquetada como diagnóstico histórico?** Sí: caption
    "Historical frozen-policy diagnostic" (ambos formatos), heading §5.1 renombrado,
    tabla completa reubicada a S2.11 con resumen compacto en main; números intactos.
12. **¿VBC-SG aparece como extensión scoped y secundaria?** Sí: "a sequential
    decision-support instantiation for settings in which validation is chosen", "not
    the source of the paper's final verdict"; frozen-transformer scope y no-reevaluación
    bajo size-matched conservados; párrafos de capas/frontera comprimidos en main.
13. **¿Los claims sobre detector score están condicionados a triggered decisions?** Sí:
    "within triggered decisions under the evaluated detectors…" en Intro y README;
    "not the lever" / "score is uninformative" eliminados (guards); caveats de
    pre-umbral y detectores performance-aware intactos (Related Work §2 los cita sin
    invalidarlos).
14. **¿ATTENUATION sigue registrado sin dominar la narrativa?** Sí: registrado en
    Method, Results, supplement, artifact y claim map (audit v122sm P4 intacto); una
    sola frase de taxonomía en el abstract (test); "near-elimination" /
    "effectively ELIMINATION" / "formal elimination" / "residual mean harm under
    ATTENUATION" ausentes (guards).
15. **¿El cuerpo principal refleja la identidad final del paper?** Sí: decomposición →
    controles de construcción → control decisivo zero-drift → gates condicionales, con
    la tabla coste–evidencia integrada en §5.3 y los límites load-bearing intactos.
16. **¿Se modificó algún resultado científico?** No. `results/raw/` intacto; 183/183
    hashes pinneados idénticos; `results/final_manifest.json` y `MANIFEST.sha256`
    byte-idénticos al baseline (pinneados por test); protocolos, seeds, familias,
    P/A/E y ATTENUATION sin cambios.
17. **¿Se ejecutó algún experimento?** No. Solo: dos generadores derivados
    deterministas, port IEEE, compilación LaTeX, pytest, audit, verify-manifest y el
    generador del graphical abstract. Ningún runner experimental, ninguna seed nueva,
    ningún proceso en background.
18. **¿Queda algún blocker textual o factual antes de KBS?** No. Presupuestos: main 33,
    IEEE 25, abstract 234, cuerpo por debajo del nivel v1.22.0; 0 refs/citas
    indefinidas; supplement 29→30 (crecimiento permitido).
19. **¿Alguna petición restante requeriría una nueva matriz?** Sí, y queda declarada
    como trabajo futuro / revisión oficial: full-drift y mild-drift size-matched,
    observed-data size-matched, VBC-SG bajo own-transformer/size-matched, otros
    clasificadores a paridad own-transformer, prevalencia operacional del control.
    Nada de eso pertenece a esta fase.
20. **¿La versión actual puede enviarse sin otra iteración científica?** Sí: la
    corrección es editorial y el contenido científico es el sellado en v1.22.0.

## Veredicto

**READY FOR v1.22.1 SEALING**
