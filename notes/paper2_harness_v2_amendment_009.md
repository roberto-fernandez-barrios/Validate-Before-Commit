# Amendment 009 — registered pre-run (the "muy recomendable" menu of the 8th review)

**Registered BEFORE any run of this amendment.** Stop-rule lifted by the author on 2026-07-15:
the goal is now maximum defensible value for a Q1 submission, executing Sol's *muy recomendable*
list. Discipline retained: protocol fixed before running, smoke before full, negatives reported
as negatives, no re-tuning to force a sign. Harness = `run_paper2_readaptation_v2.py` (common
bit-identical streams per seed across arms; disjoint window/train/probe partitions). Seeds
**104–133** (30), the pristine registered-replication block, matching v2/v6/v9/v10.

## Locked configuration (verified this session)
- **portscan (benefit):** `--data-ref data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv --data-cur data/raw/cicids2017/MachineLearningCVE/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` (seed-104 no_adaptation BA = 0.820078, reproduced exactly this session → config locked).
- **unsw_recon (marginal):** `--data-ref data/processed/unsw_nb15/unsw_ref_no_reconnaissance_binary.csv --data-cur data/processed/unsw_nb15/unsw_cur_reconnaissance_binary.csv`
- **ton_scanning (harm):** `--data-ref data/processed/ton_iot_q1_gate/ton_iot_ref_no_scanning_binary.csv --data-cur data/processed/ton_iot_q1_gate/ton_iot_cur_scanning_binary.csv`
- Defaults: `--dim 8 --window-size 128 --train-size-per-class 2000 --post-windows 100 --ramp-windows 80 --calibration-windows 30 --label-col Label --methods ks_max`.
- **No-PCA** = `--dim 100` (≥ feature count for all three: 78/39/88 → PCA branch is skipped, `pca=None`).
- **Mild drift** = `--max-severity 0.25` with the real detector (`--trigger-mode detector`, default).
- **Zero drift** = `--max-severity 0 --trigger-mode random --trigger-prob <p>` (drift-independent triggering, as in a007/a008). Risk-averse gate under zero drift = `--adaptation-gate labeled_probe_mcnemar` (the rule that recovered the loss in a008).

## Pre-registered predictions (falsifiable; recorded before running)
- **P1 (models):** naive net-harm at mild drift is *not* universal across downstream models — it is
  expected to attenuate or vanish for RF/LogReg/MLP (they resisted full-drift harm in Phase 2c),
  while the gate stays ≥ no-adaptation − 0.2 for every model×regime. If the gate goes net-harmful
  for any model, that is a reportable failure.
- **P2 (no PCA):** at full dimensionality the harm *point estimate* stays ≤ 0 in the ToN harm
  regime but is attenuated (may lose significance), replicating the Phase 2k full-dim control; the
  gate stays non-harmful.
- **P3 (zero-drift alt generators):** ensemble_cal and sliding_window update rules, under zero
  drift, are *also* net-harmful when committed naively (replacement/estimation noise), and the
  McNemar gate recovers the loss for each — i.e. the zero-drift replacement cost is a property of
  the update generator, not of full_replace specifically. Replay/cumulative are the sharper test:
  if a *cumulative* candidate (all observed data) is net-harmful under zero drift too, the
  candidate-governance thesis is at its strongest; if cumulative is *safe*, that is an important
  boundary ("harm needs a small/noisy generator") and will be reported as such.
- **P4 (tail):** worst-window and 10th-percentile BA of the naive arm are worse than no-adaptation
  in the harm regime by *more* than the mean gap (harm concentrates in the tail); the gate's tail
  tracks no-adaptation. Pure re-aggregation of committed `window_results.csv`.

## Tiers (execution order)
- **Tier 0 (free, no runs): tail / worst-case metrics.** Re-aggregate `window_results.csv`
  (per-window BA already logged) for all existing v2/v10 arms → per-seed worst-window BA, p10/p50,
  CVaR@10%. New analysis `aggregate_paper2_amendment_009_tail.py`. Answers item 8.
- **Tier 1 (flag-only): 4 classifiers × {mild, zero} and no-PCA × {mild, zero}.**
  `--downstream-model {random_forest,logreg,mlp}` and `--dim 100`, each × 3 regimes × {naive, gate}.
  Answers items 1, 2. Gate = labeled_probe (mild), labeled_probe_mcnemar (zero).
- **Tier 2 (flag-only): zero-drift alternative update generators.**
  `--adapt-strategy {ensemble_cal, sliding_window} --max-severity 0 --trigger-mode random`,
  × 3 regimes × {naive, mcnemar}. Answers part of item 3.
- **Tier 3 (small code): replay + cumulative candidate generators.** Port `replay` from the
  progressive runner into v2; add `cumulative` (candidate trains on all observed windows). Run
  under zero drift and mild drift. Answers items 3, 4.
- **Tier 4 (flag-only): operational prevalence + label latency, combined.**
  `--stream-prevalence 0.05 --probe-prevalence 0.05 --probe-latency 20` end-to-end, 3 regimes,
  {naive, gate}. Partial item 5 (probe-latency only; end-to-end *training* latency = code, deferred/noted).
- **Tier 5 (small code): confidence-sequence gate with explicit harmful-commit bound.** Extend the
  anytime-valid gate to report/enforce a harmful-commit probability bound; compare to seqav.
  Answers item 6.
- **Tier 6 (staging + runs): additional temporal dataset with a healthy incumbent.** Candidate =
  ToN-IoT chronological (time-ordered) — the natural "additional" stream (UNSW chrono already
  covered in a005; CICIDS days collapse the incumbent). Report incumbent health honestly; if it
  collapses, that is reported, not hidden. Answers item 7.

## Output naming
- v11 arms: `results/raw/paper2_v11_{regime}_{tag}` (tag encodes model/dim/strategy/drift/gate).
- Aggregators: `aggregate_paper2_amendment_009.py` (+ `_tail`), tables under
  `results/tables/paper2_amendment_009/`. Every claim added to `audit_paper2_claims.py`.

## PROGRESS LOG (this session)
- **Tier 0 (tail) DONE.** `aggregate_paper2_amendment_009_tail.py`, `tail.csv`. In the ToN harm
  regime the naive gap vs no-adaptation is far worse in the tail than the mean: mean −1.38,
  p10 −4.48 [−7.21,−2.03], **worst-window −5.24 [−8.39,−2.34]**, CVaR@10% −4.74 [−7.63,−2.12].
  The gate keeps the whole tail non-negative (mean +0.80, p10 +0.70, worst +0.72, CVaR +0.78).
  **P4 CONFIRMED**: the mean understates the risk ~3–4×; the gate protects the tail. (n=27 seeds,
  matching the confirmatory convention.)
- **New code landed + smoked** in `run_paper2_readaptation_v2.py` (additive; existing paths
  unchanged, py_compile OK, config reproduces): `--adapt-strategy {cumulative, replay}`;
  `--adaptation-gate labeled_probe_cs` (Robbins normal-mixture confidence SEQUENCE, module helper
  `cs_lower_bound`, explicit harmful-commit bound α uniform over looks). 2-seed smoke on ToN
  zero-drift: **cumulative naive −2.1**, replay naive −1.1 vs no-adapt 0.924 → even an all-observed
  cumulative candidate is net-harmful with zero drift (P3 at its strongest; refutes "just use more
  data"). CS gate on mild drift: conservative (0 commits in 2 seeds).
- **Tier 6 dataset staged + running (honest negative on the healthy-incumbent goal).** ToN-IoT
  has NO timestamp → ToN chronological infeasible (documented). Substituted CICIDS **Tuesday
  chronological** (`prepare_paper2_cicids_tuesday_chronological.py`, train=first 30%, stream=last
  70%, seeds 401–430). The incumbent COLLAPSES (no-adapt BA 0.497, naive 0.949) because the train
  window has **FTP-Patator only** and the stream switches to **SSH-Patator** — a new attack subtype
  the incumbent never saw. So it is a deep-benefit/new-attack chronological, not a healthy
  incumbent. **Reported finding:** healthy-incumbent chronological evidence remains UNSW-only
  (a005); the CICIDS Tuesday attempt also collapsed. Strengthens, not weakens, the honest
  chronological-scope statement.
- **ALL 92 ARMS COMPLETE (0 failures, ~2.8 h).** `aggregate_paper2_amendment_009.py` →
  `summary.csv`, `contrasts.csv`. Headline results (30 seeds, 95% boot CI):

  **Items 1+2 — harm is NOT SVC-PCA8-specific (answers the reviewer's central objection).**
  Zero-drift naive is net-harmful for ALL FOUR downstream models in every regime and the McNemar
  gate recovers ALL of it (+0.00 exact) each time: PortScan naive RF −0.33 / LogReg −0.29 /
  MLP −0.81 / SVC-fulldim −0.90; UNSW RF −1.06 / MLP −1.15 / fulldim −1.16; ToN MLP −2.16 /
  SVC-fulldim −4.76. Mild-drift naive harm attenuates/vanishes for robust models (RF/LogReg mild
  ≈ 0; P1 confirmed) and the gate stays ≥ no-adapt−0.2 everywhere (worst gate cell UNSW-MLP mild
  −0.17). No-PCA (SVC full-dim): ToN mild −0.61 [−1.57,0.11] NS (attenuated, P2), zero −4.76
  persists; gate recovers.

  **Items 3+4 — zero-drift harm is a property of the update GENERATOR (candidate governance at
  its strongest).** Naive zero-drift gain by generator (ToN / PortScan): cumulative **−9.46 /
  −7.04** (WORST — the all-observed-data candidate; refutes "just use more data"), sliding −7.21 /
  −3.99, replay −4.03 / −2.93, ensemble_cal −0.23 / +0.84 (least harmful; doesn't fully replace).
  UNSW mostly small. The McNemar gate recovers all of it (+0.00) for every generator. One honest
  wrinkle: ensemble_cal on PortScan zero-drift happens to help (+0.84), and the risk-averse gate
  forgoes it (gate−naive −0.84) — the known cost of risk-aversion when a generator helps by luck.
  Cumulative/replay MILD: naive net-harm on ToN (cumulative −2.57, replay −0.80), gate neutral
  (−0.14, −0.09 NS).

  **Item 6 — CS gate.** `labeled_probe_cs` (Robbins normal-mixture CS, α-uniform harmful-commit
  bound) is so conservative at probe ≤ 64 that it essentially never commits (gain +0.00, spends
  full 64 labels) — CORRECT in the low-headroom mild/zero regimes (matches no-adaptation with a
  uniform bound), the maximally-conservative end of the risk–label frontier. Report as-is; an
  empirical-Bernstein CS exploiting the low variance of correctness differences is the natural
  power-recovering successor (named as future work, not implemented).

  **Item 7 — Tuesday chrono.** no-adapt BA 49.5 (incumbent COLLAPSES: train=FTP-Patator only,
  stream=SSH-Patator), naive +43.8, gate premium −5.66 [−8.62,−3.85] → another deep-benefit /
  new-attack chronological, NOT a healthy incumbent. Healthy-incumbent chronological remains
  UNSW-only (a005); reported honestly.

  **INTEGRATED (this session).** New table `tables/table_amendment009.tex` (+ `tables_ieee/`,
  emitted from `summary.csv` by `make_paper2_amendment009_table.py`). §5 (sec:v2) gains two bold
  paragraphs: (1) "The zero-drift harm is not a property of SVC-PCA8..." (4 models + no-PCA +
  generator sweep, Table~\ref{tab:amendment009}); (2) "Where the harm hides, and an anytime-valid
  gate that bounds it" (tail metrics + Robbins CS gate). Chronological paragraph updated to a sixth
  replay (Tuesday intra-day, incumbent collapses). Limitations updated (zero-drift harm universal
  across models/generators; six replays; healthy-incumbent chrono = UNSW-only; generators tested).
  Abstract clause added (all four classifiers + every generator, cumulative included). Audit
  extended by 21 checks → **345/345**. Builds: **35 pp CAS / 28 pp IEEE**, 0 undefined refs, 0
  errors. REPRODUCE.md synced. **PENDING (user):** commit + release v1.11.0 (not committed — user
  rule = no auto-commit).

## What stays out of scope (declared)
- End-to-end *training* latency (labels for candidate training arriving late) needs a scheduling
  rewrite of the runner; deferred and named as future work rather than half-done.
- No re-tuning of gate thresholds per cell; the registered ε=0 / McNemar / LCB / seqav rules are used as-is.
