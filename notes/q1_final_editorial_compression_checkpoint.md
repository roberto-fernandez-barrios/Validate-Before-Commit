# Checkpoint — v1.20.2 editorial compression & final claim scope (hostile review)

Protocolo: `notes/q1_final_editorial_compression_protocol.md`. Informe:
`notes/q1_final_editorial_compression_report.md`. Base v1.20.1 (`8f1a431`).

## Respuestas a la revisión hostil interna

1. **¿Queda alguna afirmación de inferencia causal?** No. "causal arm/experiment/result/
   genuinely causal" eliminadas de todas las superficies (main, IEEE, supplement, README,
   REPRODUCE, captions); sobreviven solo el label LaTeX `tab:causal_probe`, la negación
   "not as a causal proof" y el sentido temporal "causal-information availability".
   Guard v122 E1 lo fija (audit 538/538).
2. **¿Se diferencia pooled empirical de stratified formal?** Sí — frase mandada en §5.4
   (main+IEEE), guard positivo v122 E2; el pooled nunca porta la garantía per-class.
3. **¿Está claro que cap 512 ≠ 512 labels totales?** Sí — abstract ("configured probe cap of
   512, corresponding to about 578 adjudicated probe labels per proposal after deferrals"),
   §5.4 (578/580/579, "per-block ceiling, not the total cost"), conclusión y README; guard
   prohíbe "512-flow probe cap" sin aclaración.
4. **¿Se llama coste realista a una adjudication count?** No — "realistic cost" eliminado;
   §7 usa "incremental adjudication count under the evaluated protocol" + "not an estimate
   of inspected-flow acquisition cost in an operationally imbalanced deployment".
5. **¿Detector identity solo secundaria conditional on proposal?** Sí — §6: "conditional on
   a comparable proposal being generated… at extreme class imbalance, however, detector
   calibration and alarm starvation determine whether the gate is invoked at all."
6. **¿Point gate sin garantía formal?** Sí — §5.4 ("commits on a point comparison, which is
   not a statistical guarantee --- 23% of its commits have negative realized value") y §6/§8
   ("formal false-superiority control supplied only by the stratified sequential variants").
7. **¿Mecanismo del scaler limitado al SVC-RBF evaluado?** Sí — §5.4, §7 y conclusión
   ("dominant mechanism in the evaluated SVC-RBF pipeline"); guard B-existente lo mantiene.
8. **¿Hierarchical model como supporting predictive evidence?** Sí — "strong \emph{predictive}
   support … not as a causal proof"; caveats íntegros (colinealidad severidad/tiempo,
   varianza en frontera, excepción QK, fallo de transferencia de escala a UNSW). Sin
   "independent confirmation" (guard).
9. **¿Ausencia de chronological net harm como principal límite?** Sí — abstract, §5.5, §7
   (bloque External validity) y conclusión ("our principal limit on external validity").
10. **¿Toda limitación load-bearing conservada?** Sí — lista verificada en el informe de
    compresión; §7 reagrupado temáticamente sin eliminar ninguna.
11. **¿Main 8–12% menos extenso?** Sí — 19,413 → 17,827 palabras (−8.2%); main.pdf 32→30 pp,
    IEEE 24→22 pp.
12. **¿Narrativa de amendments/changelog reducida?** Sí — "first implementation/external
    review/an earlier version" a 0 en main; historias de iteraciones condensadas con
    punteros a Supplement/notes (trazabilidad íntegra allí).
13. **¿Resultados científicos byte-idénticos?** Sí — 164/164 CSVs con SHA-256 idéntico al
    baseline v1.20.1 (0 diffs, 0 nuevos); harm 520/340/180/506/14/0; multiplicity 28=6/15/7,
    supervivientes 3/6·13/15·7/7, 0 fallbacks.
14. **¿Se ejecutó algún runner?** No — solo generadores de tablas, port_ieee, build_pdfs,
    claim-scope audit, audit, verify-hashes, ledger, pytest.
15. **¿Queda alguna razón científica para otra iteración?** No. Los cambios restantes
    posibles son puramente estilísticos y de rendimiento decreciente; el ciclo queda cerrado
    salvo peticiones de editor/revisores.

## Gates

pytest **67/67** · audit **538/538** · hashes **164/164** · orphan dirs **0** · refs/citas
indefinidas **0** · control chars **0** · PDFs **30/24/22** · claim-scope audit **14 claims,
0 FAIL** · CSVs científicos **byte-idénticos** · runners **0**.

## Veredicto

**READY FOR v1.20.2 SEALING.**
