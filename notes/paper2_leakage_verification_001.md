# Label-leakage verification (external datasets) — verified clean

**Date:** 2026-07-08 · **Trigger:** the authors' parallel paper found that UNSW ships a binary `label`
column and a sequential `id`, and ToN-IoT ships `label`/`type` — total leakage if they enter the feature
pipeline. Question: did Paper 2's staging handle this? **Answer: yes — verified three ways below** (not
assumed; the experiment loader only drops the `Label` target column, so the protection must live in staging).

## 1. Header / staging audit

- **UNSW processed** (`data/processed/unsw_nb15/*_binary.csv`): 39 numeric features + `Label`.
  `id`, binary `label`, and `attack_cat` are **absent** (removed at staging; raw has 45 columns).
- **ToN-IoT processed** (`data/processed/ton_iot_q1_gate/*_binary.csv`): 88 features + `Label`.
  `label`, `type`, `ts`, `uid`, `src_ip`/`dst_ip` **absent**; the staging manifest
  (`ton_iot_q1_gate_manifest.json`) documents the feature policy (numeric + selected low-cardinality
  categoricals one-hot; identifiers dropped).
- **CICIDS2017**: the `MachineLearningCVE` variant used has **no** Flow ID / Source IP / Destination IP /
  Timestamp columns (verified on Tuesday header); only ` Label` (stripped and dropped by the loader).

## 2. Index-like column probe

For every processed *current* file: no column is index-like (near-all-unique and monotonically
increasing). NONE found in UNSW DoS / UNSW Recon / ToN Scanning.

## 3. Single-feature AUC probe (would expose any residual answer-encoding column)

Max single-column AUC over all features, per current file:

| File | top column | AUC | verdict |
|---|---|---|---|
| UNSW cur DoS | `ct_state_ttl` | 0.78 | legitimate, well-known discriminative UNSW feature |
| UNSW cur Recon | `sttl` | 0.80 | legitimate |
| ToN cur Scanning | `proto_tcp` | 0.81 | legitimate traffic feature |

No column approaches the ~0.99+ signature of a leaked label/id. Consistent corroboration: downstream
no-adaptation operating points are sane (UNSW 0.84, ToN 0.92, CICIDS 0.70–0.88), not the ~1.0 that label
leakage produces.

Probe script: single-feature `roc_auc_score` per numeric column + monotone-unique index check
(see session scratch; can be promoted to `src/analysis/` if a reviewer asks).

## Manuscript integration

One sentence added to §4 (Experimental protocol) stating that identifier and label-derived columns are
removed at staging and that no single feature exceeds AUC ≈ 0.81 — pre-empts the leakage question.
