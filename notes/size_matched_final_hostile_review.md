# Final hostile review — size-matched integration and definitive rewrite

Date: 2026-07-23
Branch: `feature/size-matched-own-transformer` (post-integration commit `d2de866` + abstract
operational-bounds fix)
Reviewer stance: adversarial; every answer verified against the compiled PDFs, the audit
(586/586) and the frozen CSVs, not against intentions.

## The fifteen questions

**1. ¿El daño medio persiste cuando se iguala el tamaño?**
No, y el paper lo dice sin ambages: naive$_{2000}$−never = +0.19/−0.02/−0.01 pp, CI90 dentro
de ±0.5 en 3/3 (tab:size_matched, guard v122sm P1); F1 sin ningún contraste Holm-significativo.
El texto nunca afirma persistencia size-matched (guards N1/N1b: cero hits; la única mención de
"size-robust" queda acotada a la convención frozen).

**2. ¿El outcome formal y la interpretación sustantiva están diferenciados?**
Sí, en cuatro superficies: abstract ("The registered outcome is ATTENUATION, because a
preregistered sign-based future-value criterion blocks formal ELIMINATION; substantively,
size matching neutralizes the mean harm"), el párrafo "Registered outcome: ATTENUATION ---
and what it does and does not mean" de §5.3, la Conclusión, y el trace S8. Guard v122sm P9
exige ambas mitades en main+ieee. En ninguna parte se reclasifica: guard N10 y
test_outcome_never_stated_as_elimination.

**3. ¿Se explica por qué ATTENUATION no significa daño medio residual?**
Sí: §5.3 declara que PERSISTENCE falla precisamente porque NO hay daño medio material a 2000,
y que E3 dispara por tasa de signo, no por magnitud; el valor futuro medio H5 a 2000 es
≈0 pp (−0.06…+0.03) frente a −0.13…−1.03 a 512. Guard N4 impide que "attenuation" aparezca
junto a "mean harm remains".

**4. ¿Las tasas H5 se interpretan correctamente?**
Sí. Terminología en todas las superficies: "future-negative signs", "proposal-level
variability", "near-zero mean future value". Nunca probabilidad de daño ni riesgo de
despliegue (guards N5, P10; test_sign_rate_never_a_probability); la tabla S8 de harm repite
el caveat de clustering y prohíbe cotas binomiales.

**5. ¿Las gates dejan de presentarse como universalmente útiles?**
Sí. Abstract: "conditional tools … not a universal requirement"; intro C3; Finding 2
("the recommendation is therefore not 'gate every adaptation'"); practitioner guidance
reescrita (validar cuando la evidencia es limitada/ruidosa/incierta); Conclusión autorizada.
Guard N3 bloquea "universally required/necessary" y "gate every adaptation" sin negación.

**6. ¿El paper reconoce que su valor a 512 compensaba una asimetría?**
Sí, con el estimando registrado: las interacciones F4 son uniformemente negativas y
Holm-significativas (p.ej. strict/PortScan −1.54 [−1.89, −1.20]) y el texto lo enuncia en
§5.3(3), Finding 2 y la caption de la tabla S8 de interacciones.

**7. ¿Se distinguen preprocessing ownership y sample-size asymmetry?**
Sí, estructuralmente: C2 las presenta como dos réplicas preregistradas separadas; §5.2 es
"the first asymmetry" (ownership, mecanismo = scaling, seeds 3001–3030) y §5.3 el control
decisivo (evidence size, seeds 4001–4030, batches anidados); Finding 1 las nombra por
separado con sus magnitudes; Limitations las escopa por separado.

**8. ¿La contribución sigue siendo suficiente para KBS?**
Sí, defendible: (i) una descomposición del loop de adaptación con dos asimetrías
identificadas mediante réplicas preregistradas con batches anidados y equivalencia formal —
metodológicamente inusual en seguridad; (ii) la familia VBC-SG y su frontera
accuracy–labels–risk intactas como formalización condicional; (iii) Finding 3 convierte la
trayectoria de resultado-negativo en una plantilla de evaluación (construcción →
comparabilidad → validación) directamente accionable para sistemas basados en conocimiento
adaptativos. El paper gana en honestidad sin perder el aparato técnico.

**9. ¿VBC-SG está correctamente reposicionado?**
Sí: fuera del abstract y de la conclusión como evidencia central; C3 lo presenta como
formalización para cuando se decide validar; el cierre de §5.6 declara explícitamente que
no se re-evaluó bajo pipelines size-matched y que nada demuestra que sea necesario ahí;
Limitations lo repite; garantías, coste, abstención, delay y scope frozen intactos.
Guard N7.

**10. ¿El título describe el resultado real?**
Sí: "A Controlled Study of Pipeline Construction, Evidence Asymmetry, and Candidate
Promotion…" nombra exactamente los tres objetos del estudio final. Está en las 10
superficies vivas (audit T1 = 5/5 en las principales, T3 verifica ausencia del título
v1.21); queda PROVISIONAL hasta aprobación humana en el checkpoint, como exige la fase.

**11. ¿El abstract contiene los tres stages de evidencia?**
Sí, en el orden congelado: frozen (daño full-drift) → own-transformer (elimina la media
full-drift; residual 512: −1.70/−0.65/−0.24) → size-matched (equivalencia 3/3;
+1.89/+0.63/+0.23 Holm; gates <0.14 n.s.) → ATTENUATION/H5 → conclusión secuencial →
límites cronológicos y operacionales. 219–230 palabras (≤240).

**12. ¿La introducción comienza con la conclusión final, no con una narrativa superseded?**
Sí: arranca con trigger≠promoción, calidad de la propuesta = construcción+evidencia,
"evaluations that are not symmetric… can produce apparent promotion harm", y la frase
mandatada ("deploying candidates whose construction or evidence differs materially…").
No queda ninguna variante de "deploying drift-triggered candidates is intrinsically
dangerous" (guard N11); el único uso de "intrinsically dangerous" es la negación explícita
de Finding 1.

**13. ¿Las recomendaciones prácticas siguen de los resultados?**
Sí: (i) pipeline autocontenida [de §5.2]; (ii) igualar evidencia o tratar el déficit como
razón para validar [de §5.3]; (iii) gate cuando la evidencia sea limitada/ruidosa/incierta,
esperando poco de ella con comparabilidad garantizada [de F3/F4]. Cada paso cita su
subsección.

**14. ¿La equivalencia se presenta como media, no identidad?**
Sí: Limitations declara que la equivalencia media no implica que ningún candidato individual
pueda ser peor ni identidad de outcomes por clase; guard N6 y el caveat de S8. La tabla
central etiqueta "eq" como criterio CI90-dentro-de-margen, no como identidad.

**15. ¿Queda algún blocker que requiera otro experimento?**
No. Las preguntas abiertas restantes (full-drift size-matched, observed-data+size-matched,
VBC-SG bajo size-matched, validación externa amplia) están declaradas como límites de
alcance en Limitations, no como requisitos pre-submission; CLAIM_INTERPRETATION.json
registra follow_up_authorized=false y el guard P5 lo vigila.

## Defects found during this review (and fixed before the verdict)

- F1: the v1-summary `\subsection` heading was accidentally dropped during an earlier edit
  (orphan `\label{sec:v1summary}`), silently renumbering §5.4–5.7 and killing the
  supplement's S5.x pointers → restored; test_main_supplement_consistency green.
- F2: `table_amendment009` caption still claimed the zero-drift harm "size-robust … specific
  to the fragile SVC-RBF learner" without the frozen-transformer scope → caption regenerated
  with the scope and the forward pointer to §5.3; guard N1b added so it cannot return.
- F3: the abstract's mandated closing item ("límites cronológicos y operacionales") lacked
  the operational half → added the acquisition-yield clause (abstract 219–230 words).
- F4: main.pdf transiently at 34 pages after F1's restoration → compressed Related Work,
  mechanism, frontier and Limitations prose; final 33 pages with body word count 18.1k
  (< v1.21.0's 18.5k).
- F5: `git add -A` had staged the user's two personal untracked files → unstaged before
  committing; they remain untracked.

## Verification snapshot at verdict time

pytest 118/118 · audit 586/586 (0 FAIL) · verify-hashes 173/173 (10 unpinned = new tables,
to be pinned only at sealing) · 21/21 and 42/42 COMPLETE · v1.21.0 manifests byte-identical ·
main 33pp / supplement 29pp / IEEE 25pp, 0 undefined refs/citations · abstract ≤240 ·
no runner executed in this phase · no background processes.

## Verdict

**READY FOR FINAL v1.22.0 SEALING**

(No new experiment is recommended; the title remains provisional pending human approval at
the checkpoint.)
