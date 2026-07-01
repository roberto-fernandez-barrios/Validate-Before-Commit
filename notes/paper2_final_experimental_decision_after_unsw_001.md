# Paper 2 Final Experimental Decision After UNSW-NB15

## Decision

Stop experiments and start manuscript writing.

## Reason

The experimental campaign now supports a coherent Q2-level paper based on operational characterization of QK-MMD drift monitors for adaptive IDS. However, the external UNSW-NB15 medium results do not support escalation toward a strong Q1 quantum-advantage claim.

## Current conclusion

The paper should not claim universal quantum advantage.

The final claim should be:

> Quantum-kernel MMD monitors do not universally outperform classical drift detectors, but they induce attack-regime-dependent operating profiles for adaptive IDS readaptation under progressive drift. In CICIDS2017, these profiles include reduced readaptation frequency at comparable downstream performance in Wednesday/DDoS, and higher raw recovery at higher operational cost in PortScan/WebAttacks. External UNSW-NB15 results show competitive but marginal QK behavior, confirming that QK advantages are not universal.

## Main evidence

### CICIDS2017

Four adversarial regimes:

1. Wednesday:
   - QK-MMD ZZ is comparable to Energy in BA.
   - QK-MMD ZZ uses fewer readaptations.
   - Interpretation: efficiency-oriented profile.

2. DDoS:
   - QK-MMD ZZ is comparable to Energy in BA.
   - QK-MMD ZZ uses fewer readaptations.
   - Interpretation: efficiency-oriented profile.

3. PortScan:
   - QK-MMD ZZ improves BA over Energy.
   - QK-MMD ZZ uses more readaptations.
   - Interpretation: raw-recovery profile with higher cost.

4. WebAttacks:
   - QK-MMD PauliXZ has the highest mean BA.
   - It significantly improves over Energy/JSD.
   - It does not significantly improve over MMD-RBF/KS.
   - Interpretation: competitive raw-recovery profile, not dominance.

### Controls and limitations

1. Benign/nuisance drift:
   - QK-MMD ZZ does not reduce nuisance triggers.
   - Therefore QK cannot be claimed as a cleaner benign-drift filter.

2. Expensive Random Forest downstream:
   - QK-MMD ZZ reduces readaptations and fit time.
   - But monitoring runtime dominates.
   - Therefore QK does not show real-cost advantage in this setting.

3. Feature-map sensitivity:
   - ZZ/PauliXZ with reps 1,2,3.
   - No deeper map unlocks a strong quantum advantage.
   - ZZ-r1 remains a reasonable operational compromise.

### UNSW-NB15

UNSW-NB15 was added as external validation.

Results:

1. UNSW DoS:
   - KS/JSD lead.
   - QK-PauliXZ is competitive with MMD-RBF but not better.
   - QK-ZZ does not show advantage.

2. UNSW Reconnaissance:
   - QK-ZZ leads in mean BA.
   - But it is not significantly better than Energy, MMD-RBF or KS.
   - It is only significantly better than JSD and PauliXZ.

Interpretation:

> UNSW-NB15 does not replicate the CICIDS efficiency story. It should be included as mixed external validation, preferably in appendix or a short limitations subsection.

## Strategic publication decision

### Q2-now

Recommended.

Target style:

- Computer Networks
- Expert Systems with Applications
- Journal of Information Security and Applications
- Applied Soft Computing, depending on framing

Strength:

- coherent operational story;
- multiple CICIDS2017 attack regimes;
- strong baselines;
- paired CIs;
- benign controls;
- feature-map sensitivity;
- external UNSW mixed validation.

### Q1-later

Not recommended at this stage.

Reason:

- UNSW does not provide strong external positive evidence.
- More experiments risk sprawl.
- A Q1 attempt would require a stronger external dataset result where at least one QK operational profile replicates significantly against strong classical baselines.

## Final recommendation

Do not run more CICIDS2017 experiments.

Do not scale UNSW to 30 seeds.

Do not redesign UNSW protocol now.

Start writing.

## Main paper vs appendix

### Main paper

- Motivation and problem formulation.
- Progressive readaptation protocol.
- CICIDS2017 four-regime results.
- Paired CI comparisons.
- Operational metrics: BA, degradation, gain, adaptations, runtime.
- Benign/nuisance controls.
- Cost/utility interpretation.
- Brief mention of UNSW-NB15 as external mixed validation.

### Appendix

- UNSW-NB15 medium details.
- Feature-map sensitivity.
- Expensive RF downstream.
- Additional negative results if needed.

### Exclude or minimize

- Long-stream single-change results.
- Hybrid OR/AND/vote unless briefly mentioned as negative.
- Geometry diagnostics unless needed for explanation.
- Overly speculative operational scaling.

## Immediate next action

Create manuscript skeleton and start drafting Introduction, Method and Experimental Protocol.
