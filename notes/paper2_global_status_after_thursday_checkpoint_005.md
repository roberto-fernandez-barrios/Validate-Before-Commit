# Paper 2 Global Status After Thursday WebAttacks — Checkpoint 005

## Purpose

This checkpoint consolidates the current state of Paper 2 after adding:

- multi-scenario CICIDS2017 progressive drift results,
- benign/nuisance controls,
- actionable utility analysis,
- expensive downstream Random Forest test,
- feature-map sensitivity study,
- Thursday WebAttacks final experiment.

The goal is to determine whether the paper is still a collection of experiments or whether it now supports a coherent regime-dependent operational story.

---

## 1. Current thesis

The paper should not claim universal quantum advantage.

The strongest defensible thesis is:

> Quantum-kernel MMD detectors do not dominate classical drift detectors universally, but they define non-trivial, attack-dependent operating points for adaptive IDS readaptation under progressive drift. In some regimes they reduce readaptation frequency at comparable downstream performance; in others they improve raw recovery at the cost of more readaptations and higher monitoring runtime.

In Spanish:

> Los detectores QK-MMD no dominan universalmente a los detectores clásicos de drift, pero definen puntos operacionales no triviales y dependientes del régimen de ataque para la readaptación de IDS bajo drift progresivo. En algunos escenarios reducen la frecuencia de readaptación manteniendo rendimiento downstream comparable; en otros mejoran la recuperación bruta a costa de más readaptaciones y mayor coste de monitorización.

---

## 2. Main adversarial progressive-drift results

### Tuesday -> Wednesday

Main finding:

- QK-MMD ZZ and Energy distance are essentially tied in downstream performance.
- QK-MMD ZZ uses fewer readaptations.
- QK-MMD ZZ has better adaptation efficiency.
- QK-MMD ZZ is much slower.

Interpretation:

> Wednesday supports an efficiency-oriented QK-MMD ZZ story: comparable recovery with fewer readaptations.

---

### Tuesday -> Friday DDoS

Main finding:

- QK-MMD ZZ and Energy distance are close in downstream performance.
- QK-MMD ZZ uses fewer readaptations.
- QK-MMD ZZ has better adaptation efficiency.
- QK-MMD ZZ is much slower.

Interpretation:

> DDoS also supports an efficiency-oriented QK-MMD ZZ story.

---

### Tuesday -> Friday PortScan

Main finding:

- QK-MMD ZZ improves downstream balanced accuracy over Energy distance.
- QK-MMD ZZ reduces cumulative degradation.
- But QK-MMD ZZ uses more readaptations.
- Adaptation efficiency is worse than Energy distance.

Interpretation:

> PortScan supports a raw-recovery QK-MMD ZZ story, not an efficiency story.

---

### Tuesday -> Thursday WebAttacks

Final results, 30 seeds:

| method | BA | cumulative error | gain vs no adapt | adaptations | detector runtime |
|---|---:|---:|---:|---:|---:|
| QK-MMD PauliXZ | 0.919109 | 8.089063 | 7.648438 | 4.966667 | 7.344244 |
| QK-MMD ZZ | 0.913706 | 8.629427 | 7.108073 | 5.300000 | 6.996546 |
| MMD-RBF | 0.912453 | 8.754687 | 6.982812 | 2.166667 | 4.103174 |
| KS-max | 0.909310 | 9.069010 | 6.668490 | 3.400000 | 0.273006 |
| JSD | 0.902419 | 9.758073 | 5.979427 | 3.766667 | 0.027208 |
| Energy distance | 0.900076 | 9.992448 | 5.745052 | 2.766667 | 0.067458 |
| No adaptation | 0.842625 | 15.737500 | 0.000000 | 0.000000 | 0.000000 |

Paired CI interpretation for QK-MMD PauliXZ:

- Significantly better than Energy distance in BA/error.
- Significantly better than JSD in BA/error.
- Not significantly better than MMD-RBF.
- Not significantly better than KS-max.
- Not significantly better than QK-MMD ZZ.
- Requires significantly more adaptations and runtime than classical baselines.

Interpretation:

> WebAttacks supports a raw-recovery QK-MMD PauliXZ story against weaker/cheaper baselines, but not a clean dominance claim over the strongest classical baselines.

---

## 3. Benign/nuisance controls

Benign controls:

- Tuesday BENIGN -> Tuesday BENIGN
- Tuesday BENIGN -> Wednesday BENIGN

Important result:

- QK-MMD ZZ does not reduce nuisance triggers.
- In Wednesday BENIGN, QK-MMD ZZ has more nuisance triggers than MMD-RBF, KS-max and Energy distance.

Interpretation:

> QK-MMD cannot be claimed to be inherently more actionable by filtering benign drift. Its value must be framed through adversarial recovery/readaptation trade-offs, not benign-drift selectivity.

---

## 4. Actionable utility

Utility:

actionable_utility =
    adversarial_gain
    - lambda * adversarial_readaptations
    - eta * benign_nuisance_triggers
    - gamma * runtime

Main interpretation:

- QK-MMD ZZ can be preferred when readaptation cost is non-negligible and runtime is not dominant.
- The utility analysis is conditional and operational.
- It should not be presented as universal proof of superiority.

---

## 5. Expensive downstream Random Forest

Random Forest 500 trees, Wednesday, 5 seeds, 100 windows:

Energy distance:

- BA ≈ 0.9858
- adaptations ≈ 8.0
- detector runtime ≈ 0.087 s
- fit runtime ≈ 4.929 s
- total runtime ≈ 5.016 s

QK-MMD ZZ:

- BA ≈ 0.9781
- adaptations ≈ 4.8
- detector runtime ≈ 10.772 s
- fit runtime ≈ 2.965 s
- total runtime ≈ 13.737 s

Interpretation:

> QK-MMD ZZ reduces the number of readaptations and fit time, but its monitoring runtime dominates. The RF result does not support a real-cost advantage for QK. This should be treated as a limitation or appendix result, not as a main claim.

---

## 6. Feature-map sensitivity

Pre-registered study:

- ZZ reps 1, 2, 3
- PauliXZ reps 1, 2, 3
- Wednesday development scenario
- smoke and medium completed

Medium Wednesday, 10 seeds:

| config | BA | cumulative error | gain | adaptations | efficiency | runtime |
|---|---:|---:|---:|---:|---:|---:|
| PauliXZ-r3 | 0.886672 | 11.332813 | 12.563281 | 3.7 | 3.395481 | 13.491980 |
| ZZ-r1 | 0.886656 | 11.334375 | 12.561719 | 3.1 | 4.052167 | 5.695984 |
| ZZ-r3 | 0.883141 | 11.685938 | 12.210156 | 3.3 | 3.700047 | 12.130083 |
| PauliXZ-r1 | 0.880727 | 11.927344 | 11.968750 | 3.2 | 3.740234 | 6.234160 |
| PauliXZ-r2 | 0.878930 | 12.107031 | 11.789063 | 3.7 | 3.186233 | 9.630510 |
| ZZ-r2 | 0.877156 | 12.284375 | 11.611719 | 3.2 | 3.628662 | 9.190042 |

Interpretation:

> Increasing feature-map depth does not unlock a clearly superior quantum configuration. ZZ-r1 remains the best operational compromise in the development scenario. PauliXZ-r3 obtains a negligible BA edge but with more adaptations and much higher runtime.

---

## 7. Current story by attack regime

| Regime | Best QK behavior | Interpretation |
|---|---|---|
| Wednesday | QK-MMD ZZ comparable BA with fewer readaptations | efficiency-oriented |
| DDoS | QK-MMD ZZ comparable BA with fewer readaptations | efficiency-oriented |
| PortScan | QK-MMD ZZ better BA but more readaptations | raw-recovery-oriented |
| WebAttacks | QK-MMD PauliXZ highest mean BA, significant vs Energy/JSD, not vs MMD/KS | raw-recovery but not dominance |

This is the coherent story:

> QK-MMD is attack-regime and feature-map dependent. It does not dominate all classical baselines, but it provides competitive operating points that trade monitoring cost and readaptation frequency for downstream recovery.

---

## 8. Is this a cumulative pile of experiments?

It can look like a pile if presented chronologically.

It becomes coherent if presented as the following evaluation chain:

1. Progressive drift degrades IDS performance.
2. Triggered readaptation recovers performance.
3. Different drift monitors induce different readaptation profiles.
4. QK-MMD produces competitive but regime-dependent profiles.
5. Benign controls show QK-MMD does not simply filter nuisance drift better.
6. Utility analysis clarifies the operating regimes where QK may be preferred.
7. Feature-map sensitivity shows the conclusions are not an obvious artifact of a single shallow map.
8. Thursday WebAttacks broadens the adversarial regimes and shows PauliXZ can be competitive in application-layer attacks.

---

## 9. What should be claimed

Supported:

1. Triggered readaptation substantially improves downstream IDS performance under progressive drift.
2. QK-MMD detectors can be competitive with strong classical drift monitors.
3. QK-MMD ZZ reduces readaptations at comparable performance in Wednesday and DDoS.
4. QK-MMD ZZ improves raw recovery in PortScan but uses more readaptations.
5. QK-MMD PauliXZ obtains the highest mean WebAttacks BA and significantly improves over Energy/JSD, but not over MMD-RBF/KS.
6. QK-MMD behavior is map- and attack-dependent.
7. Runtime overhead remains a major limitation.
8. QK-MMD does not reduce benign nuisance triggers.

Not supported:

1. Universal quantum advantage.
2. QK-MMD always better than Energy distance.
3. QK-MMD always better than MMD-RBF or KS.
4. QK-MMD always reduces readaptations.
5. QK-MMD is cheaper.
6. QK-MMD filters benign drift better.
7. QK-MMD PauliXZ clearly dominates WebAttacks over all baselines.

---

## 10. Publication potential

Current status:

- Q2: strong, if framed honestly.
- Q1: possible but not guaranteed.
- Top Q1: unlikely without an external dataset and a very careful narrative.

Main Q1 blocker:

- all current evidence is still CICIDS2017, even if multiple attack regimes are evaluated.

Thursday WebAttacks improves attack diversity, but it is not a second dataset.

---

## 11. Strategic next decision

Options:

### Option A: Stop CICIDS2017 and write

Pros:

- avoids experiment sprawl;
- current story is coherent enough for Q2;
- prevents further dilution.

Cons:

- Q1 risk remains due to single dataset.

### Option B: External dataset smoke

Recommended if aiming Q1.

Candidate datasets:

- UNSW-NB15: more independent from CICIDS2017, stronger external validation.
- CIC-IDS2018: more compatible, but less independent because same CIC ecosystem.

Pros:

- addresses the main Q1 blocker;
- even mixed results can strengthen the regime-dependent claim.

Cons:

- may require preprocessing;
- may introduce new inconsistencies;
- may extend timeline substantially.

### Option C: More CICIDS2017 scenarios

Not recommended unless there is a very specific question.

CICIDS2017 already covers Wednesday, DDoS, PortScan, WebAttacks. Additional CICIDS2017 scenarios may look like more of the same.

---

## 12. Recommended next step

Do not launch more CICIDS2017 experiments immediately.

First:

1. Ask a reviewer to evaluate this updated checkpoint.
2. Decide whether the target is Q2-now or Q1-later.
3. If Q1-later, start an external dataset smoke, preferably UNSW-NB15 if available.
4. If Q2-now, start writing the manuscript from the storyline.

---

## 13. Files and checkpoints related to current state

Important notes:

- notes/paper2_director_summary_001.md
- notes/paper2_storyline_001.md
- notes/paper2_second_dataset_plan_001.md
- notes/paper2_next_steps_review.md
- notes/paper2_rescue_review.md
- notes/paper2_feature_map_sensitivity_protocol_001.md
- notes/paper2_feature_map_sensitivity_checkpoint_001.md
- notes/paper2_thursday_webattacks_checkpoint_001.md

Important results:

- results/tables/paper2_progressive_multi_scenario_cicids_001/
- results/tables/paper2_actionable_drift_wednesday_001/
- results/tables/paper2_feature_map_sensitivity_medium_001/
- results/tables/paper2_progressive_thursday_webattacks_final_001/

Important scripts:

- src/experiments/run_paper2_progressive_readaptation.py
- src/experiments/run_paper2_nuisance_benign_drift.py
- src/experiments/run_paper2_feature_map_sensitivity.py
- src/experiments/run_paper2_expensive_downstream.py
- src/analysis/make_paper2_feature_map_sensitivity_artifacts.py
- src/analysis/make_paper2_thursday_webattacks_artifacts.py
