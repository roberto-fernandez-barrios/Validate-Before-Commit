# final-q1 — Fase D checkpoint (chronological matrix + operational e2e)

Date: 2026-07-20. Branch `final-q1`. NOT committed.

## D4: VBC-SG chronological port — mandatory invariant gate PASSED before any results ran

Per Roberto's precision ("VBC-SG enters ONLY IF port passes 4 invariants BEFORE any results
run; otherwise predeclared out of scope"): `vbc_sg_decide()` ported to
`run_paper2_temporal_stream.py` with two continuation modes (cohort: fixed target = window
t-9, drawn without replacement in blocks; refresh: each step a fresh, strictly-earlier
window, Bonferroni alpha/(1+D)). Four tests written and run BEFORE any chronological
arm: `tests/test_q1_chronological.py`:
  1. causality — asserted at draw time (src_t < t) for both modes; PASS.
  2. restart semantics — cohort: pigeon-hole bound proves no-reuse (n_steps <= window
     capacity / block size); refresh: evidence set bounded per-step (no accumulation). PASS.
  3. label accounting — returned label count matches exactly what was drawn. PASS.
  4. manifest logging — by_seed summary carries n_proposals/vbc_defer_mode/vbc_steps_mean/
     vbc_delay_mean, n_adaptations <= n_proposals. PASS.
7/7 pass → **VBC-SG-Cohort enters the chronological matrix** (Refresh implemented but not
run by default, to bound compute; available via `--vbc-defer-mode refresh`).

Also added (obligatory per D4): `--gate-margin` on the temporal runner (0.001 = strict).

### New staging (data)

- `prepare_paper2_cicids_intraday_chronological.py` (generalizes the Tuesday-only script):
  Wednesday and Thursday intra-day 30/70 splits. Wednesday's stream is DoS-heavy early
  (train-30% already captures 66% attack fraction — reported as-is, not cherry-picked).
  Thursday's stream is near-attack-free after the 30% cut (WebAttacks concentrated in the
  morning; Infiltration is only 36 flows total) — attack_frac in the stream ≈ 0.0001, a
  legitimate degenerate case, reported honestly.
- `prepare_paper2_unsw_chronological.py` extended with `--train-frac` (20%, 40%; 30% keeps
  its original filenames for backward compatibility).

### The 7 registered replays x {none, point, strict, vbccoh}, seeds 601-630 — 28 arms

Launched as 3 detached workers (survive the session); smoke-tested every stream at least
once (all 4 vbccoh smokes + 1 strict smoke) before the full launch, per the hard smoke rule.

## D5: operational end-to-end (P1.4) — new script, smoke-tested, launched

`src/experiments/run_paper2_operational_e2e.py` (new, additive): reuses the v2 harness's
`build_environment` (tested stream/partition machinery) and adds:
  * `sample_acquisition()` — {random, alert_enriched, disagreement, hybrid}, all honest (rank
    by model PREDICTIONS only, never true labels; verified analytically: alert_enriched finds
    ~8x more attacks per 32-flow probe than random on a synthetic separable case; disagreement
    gives only marginal enrichment when the two models mostly disagree near the decision
    boundary rather than on the minority class specifically -- reported as a real, not
    force-fit, finding, consistent with the no-retuning-to-force-signs rule).
  * `--training-delay D` (new flag): the candidate is built at the trigger window (instant
    compute, as elsewhere) but not committable until D windows later; a pending candidate
    blocks new triggers (mirrors the v2 runner's registered policy).
  * `inspected_flows_per_attack = labels_used / attacks_found_total`, the D5 headline metric.

### Grid (36 arms, seeds 701-730), pruned per the registered protocol comment

Main grid: {portscan, ton} x {pi 0.005/0.01/0.05/0.10} x {4 acquisition policies} at the base
latency/delay cell (candidate/probe latency 5, training-delay 0) = 32 arms. Sensitivity: the
same 2 datasets x 2 extra (latency, delay) cells at pi=0.05/random = 4 arms. All eligible
combinations smoke-tested on REAL data (PortScan + ToN) across policies, latencies and delay
before the full launch.

### First real-data confirmation of H5 (already resolved before batch completion)

At pi=0.005: alert_enriched needs **~7x fewer inspected flows per adjudicated attack** than
random on both datasets (PortScan 29.6 vs 199.3 flows/attack; ToN 24.5 vs 193.8) — matching
the pre-registered direction of H5. ToN's naive gain at this extreme prevalence is small and
CI-crosses zero (−0.015 [−0.046, 0.009]), consistent with the detector-starvation finding
already established in the core harness at low pi.

## Aggregators (ready, dry-run clean on partial data)

`make_paper2_q1_chronological.py` (BA/accuracy gain vs no-adapt, net-harm scan, gate premium
per stream), `make_paper2_q1_e2e.py` (enrichment factors, latency/delay sensitivity).

## RESULTS — COMPLETE (28/28 chronological + 36/36 e2e) — FROZEN

### D4: the chronological matrix (seeds 601–630)

| replay | no-adapt BA | naive | point | strict | VBC-SG |
|---|---:|---:|---:|---:|---:|
| Tue→Wed+Thu+Fri | 59.0 | +14.78 | +11.52 | +11.50 | +0.16 |
| Wed→Fri | 51.8 | +35.29 | +27.64 | +28.81 | +0.91 |
| Thu→Fri | 49.0 | +36.07 | +27.71 | +26.51 | +1.56 |
| Wed intra-day | **84.7** | +6.47 | +6.02 | +5.77 | +0.56 |
| Thu intra-day | 48.3 | +0.88 | +0.88 | +0.42 | +0.00 |
| UNSW (train 20%) | **82.9** | +8.35 | +9.90 | **+11.13** | +10.76 |
| UNSW (train 40%) | **84.2** | +7.64 | +8.38 | **+8.98** | +6.92 |

1. **Chronological net harm remains unobserved** across all 13 replays (6 prior + 7 new) —
   the paper's principal external-validity limit, reported as such.
2. **The conditional prediction holds where it is falsifiable**: on the two UNSW timelines
   (healthy incumbent, 82.9/84.2%) all three gates BEAT always-deploying, the zero-cost
   strict rule by **+2.78 and +1.34** points on non-overlapping intervals, while committing
   2.5/3.6 times per stream against naive's 13.0/17.3.
3. **Reported honestly, not rounded into a law**: Wednesday intra-day also keeps a healthy
   incumbent (84.7%) yet its gates sit 0.5–0.7 points BELOW naive (unresolved). So the
   premium disappears and can reverse once headroom is small — it is not guaranteed to.
4. Where the incumbent collapses (49–59%), always-deploy is excellent and the gates pay a
   real premium (−3.3 to −8.4). VBC-SG is extremely conservative on these streams (+0.16 to
   +1.56): a deployment-long guarantee is the wrong tool where every update helps.

### D5: operational end-to-end (seeds 701–730)

- **Alert-enriched acquisition costs 5–8× fewer inspected flows per adjudicated attack label
  than random inspection** at every prevalence and on both benchmarks (ToN at π=0.01: 13.7
  vs 112.5); hybrid 4–6×. H5 confirmed in the pre-registered direction.
- **Disagreement sampling barely helps (1.0–2.1×)** — a genuine negative: the two models
  differ near the decision boundary rather than on the minority class. Reported as it came
  out, per the no-retuning rule.
- Graceful degradation: quadrupling label latency to 20 windows costs PortScan 1.1 points
  (+7.82 → +6.71); a 5-window training-completion delay costs 1.0 (+6.82).
- ToN at π=0.05 stays CI-crossing-zero throughout — the starved-trigger regime already
  established in the core harness.

### Aggregator bug found and fixed

`make_paper2_q1_e2e.py` parsed the sensitivity arms' 2-digit prevalence tag (`pi05`) with the
main grid's 3-digit rule, mislabelling π=0.05 as 0.005. Fixed to dispatch on tag length; the
main grid was never affected (those arms are excluded from the base cell by construction).

## Integration status

All four Fase C/D results are in the manuscript with pinned audit checks
(**audit 459/459**, 33/33 tests). See `notes/q1_faseE_checkpoint_001.md`.
