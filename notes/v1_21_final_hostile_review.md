# v1.21.0 — Final hostile review (closed checklist)

Date: 2026-07-22. Reviewer stance: adversarial; evidence = current manuscript text,
generated tables, and frozen CSVs under `results/tables/symmetric_pipeline_dynamic_001/`.
Scope: strictly the 20 registered questions; no optional improvements invented afterwards.

1. **¿El abstract deja claro que el daño medio full-drift desaparece con own-transformer?**
   YES. Abstract: "The mean full-drift harm does not persist: always-deploy becomes
   beneficial in all three benchmarks (+7.2, +2.5, +1.0 balanced-accuracy points)".
   Matches `paired_contrasts.csv` (F1: +7.21/+2.55/+1.03). Guard SP1 + SP7.

2. **¿El paper evita usar el resultado frozen como evidencia general?** YES. §5.1: the
   frozen table is "the motivating configuration rather than the paper's final word...
   should not be read as general evidence beyond that configuration"; tier (i) labeled
   "(frozen policy)"; Conclusion states the ToN full-drift harm "was, in its mean, an
   artifact of that update policy".

3. **¿Está demostrado daño material residual con own-transformer?** YES. F4:
   ps_zero −1.74 [−2.35, −0.96], unsw_zero −0.65 [−0.77, −0.55], both ≤ −0.5 pp
   (preregistered materiality) with Holm p ≤ 5.6e-4 (multiplicity.csv). Guard R2.

4. **¿Se distingue daño medio de propuestas futuras negativas?** YES. §5.2 "Harmful
   proposals remain common in the controlled trajectories" separates trajectory means
   from proposal-level fractions (65/61/46/42% @H5), with the cluster caveat inline;
   Discussion Finding 1 repeats the distinction. Table S7 harm gives H1/3/5/10 + censoring.

5. **¿Las gates solo se presentan como útiles donde los contrastes lo apoyan?** YES.
   Claims of usefulness cite the six Holm-significant F4 contrasts + ton_full point
   (+0.64, p_holm 0.015); ps_full gates reported n.s.; unsw_full point reported as a
   resolved cost (−0.21). Guard SP8 pins F4 positivity; the costs are in table and text.

6. **¿Se evita afirmar recuperación completa cuando solo hay mejora frente a naive?**
   YES. §5.2(4) states the three levels explicitly: improvements are vs always-deploy;
   strict returns to within 0.06–0.14 points of never-adapt; point remains 0.27–0.99
   below; "no zero-drift cell converts to a net benefit over never adapting". Abstract
   and Conclusion use "improves over always-deploy... recovering much or nearly all".
   Guards C2/C2b.

7. **¿Ownership como amplificador y no causa única?** YES. §5.2(2): "a major amplifier
   --- not a complete explanation of candidate-promotion risk" + the C1 sentence; §5.4:
   "scaling is the dominant identified amplifier in this pipeline, not the sole cause of
   harmful promotion". Guard C1 (positive-form phrasings forbidden).

8. **¿El trade-off unsw_zero strict se reporta donde corresponde?** YES. Abstract
   ("within preregistered recall and false-positive margins in every winning cell but
   one, reported as a trade-off"); Results §5.2 security paragraph (mandated C5
   sentence); table caption; Limitations (scope paragraph: "one cell failing recall
   non-inferiority"); Supplement S7 detail. Guards SP4/R4.

9. **¿QK y VBC-SG correctamente delimitados a frozen?** YES. Abstract final sentence;
   §5.2 closing paragraph; Limitations "Scope of the symmetric-pipeline replication"
   ("The symmetric-pipeline replication targets the primary KS-max point/strict
   question; the quantum detector and the full sequential frontier remain evaluated
   under the historical frozen-transformer policy"). Guard SP5.

10. **¿Se conserva la ausencia de net harm cronológico?** YES. Abstract, C4
    contribution, §5.6, Limitations, Conclusion; 13 replays, "net harm remains
    unobserved", principal external limit. Existing audit check (v122 E2 chronological
    boundary) still passes.

11. **¿El título describe el contenido sin overclaim?** YES. "Candidate Governance for
    Drift-Triggered Classifier Pipelines" claims the formulation (C1 contribution) and
    the pipeline-level evidence; no efficiency or universal-safety term. Old title
    removed from all live surfaces (guards T1/T2 + test).

12. **¿Candidate governance ≠ champion–challenger genérico?** YES. Related work §2.5
    positions champion–challenger/MLOps precedents and states the delta (quantified
    label cost, demonstrated necessity, preregistered replication of the failure mode);
    C1 separates trigger/construction/validation/deployment — the construction stage
    and its ownership interaction are absent from generic champion–challenger.

13. **¿La contribución novedosa correctamente identificada?** YES: preregistered
    dynamic evaluation (C2), preprocessing-ownership interaction (C2/C3), explicit
    promotion decision (C1), and the empirically+formally delimited frontier (C4) —
    the four contribution paragraphs match the authorization's list.

14. **¿Garantías formales limitadas a false superiority sobre el probe?** YES.
    §3.5 "What is and is not guaranteed" unchanged; Limitations: "VBC-SG's guarantee
    --- where it applies --- controls false probe-superiority, not guaranteed future
    harm"; Conclusion: "formal false-superiority control supplied only by the
    stratified sequential variants under their stated sampling and representativeness
    assumptions" (audit v122 E2 check).

15. **¿"Label-efficient" fuera de los claims principales o acotado?** YES. Removed from
    the title and highlights; the intro introduces it only "in a strictly bounded
    sense" with the 1,024-label candidate cost in the same sentence; §5 cost-accounting
    paragraph retains the exact scope ("means --- and only means ---").

16. **¿La unidad inferencial sigue siendo la seed?** YES. §3.6: "the inferential unit is
    the seed... windows, triggers and commits are never treated as independent units";
    all CIs/bootstrap at seed level (machinery reused from the published module).

17. **¿Commits harmful no tratados como ensayos independientes?** YES. §5.2 + S7 +
    Limitations carry the cluster caveat; guard SP6 requires it in main+ieee+supp;
    no binomial bound appears anywhere (C4 wording enforced).

18. **¿Recall/FPR concuerdan con BA?** YES. Winning cells improve FPR everywhere
    (up to −3.33) and pass recall NI except the one declared cell; no BA claim
    contradicts a guardrail (`security_metrics.csv`, table, guard R4). BA remains the
    registered primary; recall/FPR restrict language per Appendix A.

19. **¿La versión se entiende sin el historial de amendments?** YES. The symmetric
    replication is presented self-contained (§3.6 + §5.2 + S7); amendment history
    lives in the supplement; no new changelog narrative was added (compression rule 6);
    the frozen recap is explicitly labeled historical/motivating.

20. **¿Algún blocker que requiera nuevos experimentos?** NO. The primary question is
    answered with registered evidence; remaining gaps (own-transformer QK/VBC-SG/mild,
    chronological harm case, operational imbalance) are declared limits/future work,
    not blockers for the claims made.

## Verdict

**READY FOR v1.21.0 SEALING**
