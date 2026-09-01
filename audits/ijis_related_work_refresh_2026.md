# IJIS related-work refresh: adaptive security systems
Search cutoff: 2026-09-01. Scope: 2024--2026 adaptive network-security systems whose
published interface is close enough to inform the paper's promotion-decision framing. This
is an interface audit, not an assertion that title-level use of *adaptive* makes a system
comparable.

## Included systems and inspected interfaces

| System | Trigger / update unit | Label interface | Retraining / replacement semantics | Incumbent--challenger promotion comparison | Preprocessing ownership | Published evaluation | Public artifact |
|---|---|---|---|---|---|---|---|
| CARAVAN (OSDI 2024) | Window-, event- and accuracy-driven online retraining | Labels supplied by configurable labeling agents | Balanced retraining; refreshed weights are installed as the in-network model | No held-out incumbent--challenger accept/reject probe | Fixed system feature pipeline; no per-challenger ownership experiment | Online in-network learning workloads | Yes; USENIX artifact badges and code link |
| SPIDER (INFOCOM 2024) | Semi-supervised continual update | At most 20% annotations plus pseudo-labels | Continual model update | No discrete candidate-promotion decision | Not evaluated as an incumbent/challenger factor | Published NIDS continual-learning evaluation | No public author artifact identified in the inspected proceedings record |
| NOCTOWL (IEEE Access 2025) | Incremental tree update | Delayed and sampled labels | Interpretable tree updated incrementally | No discrete replacement/promotion comparison | Not evaluated as an incumbent/challenger factor | Delayed/sampled-label NIDS streams | No code link found in the version of record |
| ADAWU-IDS (JKSUCIS 2026) | Chunk-level drift-aware adaptive weighting | Delayed chunk labels | Continuous ensemble reweighting; the selected CICIDS configuration disables hierarchical retraining | Not applicable: weights evolve rather than selecting between incumbent and challenger | Normalization fitted on training data; no promotion-time ownership intervention | Chronological held-out calibration and benchmark experiments | Anonymous public repository linked from the article |

Primary sources inspected:

- CARAVAN: [USENIX OSDI 2024 paper and artifact record](https://www.usenix.org/conference/osdi24/presentation/zhang-qizheng).
- SPIDER: [IEEE INFOCOM 2024 program record](https://infocom.info/day/1), DOI
  `10.1109/INFOCOM52122.2024.10621428`.
- NOCTOWL: [institutional copy of the IEEE Access version of record](https://iris.unimore.it/retrieve/79a63b13-7619-4d6b-81b9-3625afa8344c/NOCTOWL_Adaptive_Tree-Based_Model_for_Network_Anomaly_Detection_Under_Delayed_and_Sampled_Label_Availability.pdf),
  DOI `10.1109/ACCESS.2025.3633419`.
- ADAWU-IDS: [Springer version of record](https://link.springer.com/article/10.1007/s44443-026-00964-4),
  DOI `10.1007/s44443-026-00964-4`.

## Editorial consequence

All four systems are cited as related adaptive-security designs. Direct numerical ranking is
not decision-equivalent: CARAVAN immediately installs retrained weights; SPIDER and NOCTOWL
update incrementally; ADAWU changes ensemble weights. None supplies the paper's discrete
incumbent--challenger comparison on a held-out promotion probe with separately controlled
preprocessing ownership and candidate evidence. The manuscript therefore reports their
interfaces neutrally and does not claim state-of-the-art superiority or that no adaptive
system exists.
