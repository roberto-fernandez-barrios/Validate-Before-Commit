"""Forensic audit of exact cleaned-raw-X exposure across historical harness roles.

This is a diagnostic only.  It reproduces the source-row splitter used by the
registered 3001--3030, 4001--4030, 5001--5030 and 6001--6030 blocks and asks a
strictly narrower question: can the exact same cleaned raw feature vector occur
in more than one role even though source row indices are disjoint?

Equality is defined on canonical little-endian float64 bytes after the existing
loader's numeric coercion, non-finite-to-zero handling and common-feature sort.
Only signed zero is canonicalized.  No rounding or approximate matching is used.
SHA-256 is the deterministic feature key; every repeated digest is verified
against the underlying canonical vector, so a cryptographic collision aborts.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from src.experiments.run_paper2_progressive_readaptation import (
    load_binary_dataset,
    make_pools,
    progressive_severity,
)


ROOT = Path(__file__).resolve().parents[2]
OUT_CSV = ROOT / "audits" / "exact_feature_overlap_summary.csv"
OUT_MD = ROOT / "audits" / "exact_feature_overlap_audit.md"
STRATA = ("ref_benign", "ref_attack", "cur_benign", "cur_attack")
ROLES = ("window", "train", "probe")
ROLE_FRACS = {"window": 0.5, "train": 0.3, "probe": 0.2}
ROLE_BITS = {"window": 1, "train": 2, "probe": 4}

DATASETS = {
    "PortScan": {
        "key": "portscan",
        "ref": "data/raw/cicids2017/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv",
        "cur": "data/raw/cicids2017/MachineLearningCVE/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    },
    "UNSW-Recon": {
        "key": "unsw_recon",
        "ref": "data/processed/unsw_nb15/unsw_ref_no_reconnaissance_binary.csv",
        "cur": "data/processed/unsw_nb15/unsw_cur_reconnaissance_binary.csv",
    },
    "ToN-Scanning": {
        "key": "ton_scanning",
        "ref": "data/processed/ton_iot_q1_gate/ton_iot_ref_no_scanning_binary.csv",
        "cur": "data/processed/ton_iot_q1_gate/ton_iot_cur_scanning_binary.csv",
    },
}

BLOCKS = {
    "symmetric_3001_3030": {
        "seeds": range(3001, 3031),
        "scenarios": "full+zero drift x three benchmarks",
    },
    "size_zero_4001_4030": {
        "seeds": range(4001, 4031),
        "scenarios": "zero drift x three benchmarks",
    },
    "B1_5001_5030": {
        "seeds": range(5001, 5031),
        "scenarios": "full+zero drift x three benchmarks",
    },
    "B2_6001_6030": {
        "seeds": range(6001, 6031),
        "scenarios": "full drift x three benchmarks",
    },
}


def canonical_float64(a: np.ndarray) -> np.ndarray:
    """Canonical bytes used for exact X identity; signed zero is immaterial."""
    out = np.array(a, dtype="<f8", order="C", copy=True)
    out[out == 0.0] = 0.0
    if not np.isfinite(out).all():
        raise AssertionError("loader contract broken: non-finite value after cleaning")
    return out


def sha256_rows(a: np.ndarray) -> np.ndarray:
    keys = np.empty(len(a), dtype="V32")
    for i, row in enumerate(a):
        keys[i] = np.void(hashlib.sha256(memoryview(row)).digest())
    return keys


def _pct(num: int, den: int) -> float:
    return 100.0 * float(num) / float(den) if den else 0.0


@dataclass
class DatasetAudit:
    name: str
    arrays: dict[str, np.ndarray]
    keys: dict[str, np.ndarray]
    all_x: np.ndarray
    all_keys: np.ndarray
    group_inverse: np.ndarray
    group_counts: np.ndarray
    offsets: dict[str, tuple[int, int]]
    global_row: dict

    @classmethod
    def load(cls, name: str, spec: dict) -> "DatasetAudit":
        X_ref, y_ref = load_binary_dataset(ROOT / spec["ref"], "Label")
        X_cur, y_cur = load_binary_dataset(ROOT / spec["cur"], "Label")
        common = sorted(set(X_ref.columns).intersection(X_cur.columns))
        pools = make_pools(X_ref, y_ref, X_cur, y_cur, common)
        arrays = {s: canonical_float64(getattr(pools, s)) for s in STRATA}
        offsets: dict[str, tuple[int, int]] = {}
        pos = 0
        for s in STRATA:
            offsets[s] = (pos, pos + len(arrays[s]))
            pos += len(arrays[s])
        all_x = np.vstack([arrays[s] for s in STRATA])
        all_keys = sha256_rows(all_x)
        keys = {s: all_keys[slice(*offsets[s])] for s in STRATA}
        unique_keys, inv, counts = np.unique(all_keys, return_inverse=True, return_counts=True)

        # Collision-safe verification: every repeated digest must be one exact vector.
        order = np.argsort(inv, kind="stable")
        starts = np.r_[0, np.cumsum(counts[:-1])]
        for gid in np.flatnonzero(counts > 1):
            idx = order[starts[gid] : starts[gid] + counts[gid]]
            if not np.all(all_x[idx] == all_x[idx[0]]):
                raise RuntimeError(
                    f"SHA-256 collision for {name}, digest {bytes(unique_keys[gid]).hex()}"
                )

        labels = np.concatenate(
            [
                np.zeros(len(arrays["ref_benign"]), dtype=np.uint8),
                np.ones(len(arrays["ref_attack"]), dtype=np.uint8),
                np.zeros(len(arrays["cur_benign"]), dtype=np.uint8),
                np.ones(len(arrays["cur_attack"]), dtype=np.uint8),
            ]
        )
        membership = np.concatenate(
            [
                np.ones(len(arrays["ref_benign"]), dtype=np.uint8),
                np.ones(len(arrays["ref_attack"]), dtype=np.uint8),
                np.full(len(arrays["cur_benign"]), 2, dtype=np.uint8),
                np.full(len(arrays["cur_attack"]), 2, dtype=np.uint8),
            ]
        )
        label_mask = np.zeros(len(counts), dtype=np.uint8)
        membership_mask = np.zeros(len(counts), dtype=np.uint8)
        np.bitwise_or.at(label_mask, inv, np.where(labels == 0, 1, 2).astype(np.uint8))
        np.bitwise_or.at(membership_mask, inv, membership)
        conflicting_label = label_mask == 3
        ref_current = membership_mask == 3
        dup_groups = counts > 1
        global_row = dict(
            record_type="dataset_global",
            dataset=name,
            n_features=int(all_x.shape[1]),
            total_rows=int(len(all_x)),
            unique_x_groups=int(len(counts)),
            duplicate_x_groups=int(dup_groups.sum()),
            duplicate_rows_beyond_first=int(len(all_x) - len(counts)),
            duplicate_rows_beyond_first_pct=_pct(len(all_x) - len(counts), len(all_x)),
            singleton_x_groups=int((counts == 1).sum()),
            max_group_multiplicity=int(counts.max()),
            p95_group_multiplicity=float(np.quantile(counts, 0.95)),
            p99_group_multiplicity=float(np.quantile(counts, 0.99)),
            conflicting_label_x_groups=int(conflicting_label.sum()),
            conflicting_label_rows=int(counts[conflicting_label].sum()),
            conflicting_ref_current_x_groups=int(ref_current.sum()),
            conflicting_ref_current_rows=int(counts[ref_current].sum()),
            sha256_collision_count=0,
            exact_equality="canonical cleaned raw float64; signed zero canonicalized; no rounding",
        )
        for s in STRATA:
            global_row[f"rows_{s}"] = int(len(arrays[s]))
        return cls(name, arrays, keys, all_x, all_keys, inv, counts, offsets, global_row)

    def split(self, seed: int) -> tuple[dict[str, dict[str, np.ndarray]], np.ndarray]:
        """Reproduce the historical per-stratum row-index splitter exactly."""
        rng = np.random.default_rng(seed + 500_000)
        role_keys = {r: {} for r in ROLES}
        row_roles = np.empty(len(self.all_keys), dtype=np.uint8)
        for stratum in STRATA:
            a0, a1 = self.offsets[stratum]
            n = a1 - a0
            idx = rng.permutation(n)
            cut_a = int(n * ROLE_FRACS["window"])
            cut_b = cut_a + int(n * ROLE_FRACS["train"])
            selections = {
                "window": idx[:cut_a],
                "train": idx[cut_a:cut_b],
                "probe": idx[cut_b:],
            }
            for ridx, role in enumerate(ROLES):
                role_keys[role][stratum] = self.keys[stratum][selections[role]]
                row_roles[a0 + selections[role]] = ridx
        return role_keys, row_roles

    def role_audit_row(self, block: str, scenarios: str, seed: int) -> dict:
        role_keys, row_roles = self.split(seed)
        role_counts = [
            np.bincount(self.group_inverse[row_roles == ridx], minlength=len(self.group_counts))
            for ridx in range(3)
        ]
        masks = np.zeros(len(self.group_counts), dtype=np.uint8)
        for ridx, role in enumerate(ROLES):
            masks[role_counts[ridx] > 0] |= ROLE_BITS[role]
        row = dict(
            record_type="seed_role_overlap",
            block=block,
            scenario_scope=scenarios,
            dataset=self.name,
            seed=int(seed),
        )
        pairs = (("window", 0, "train", 1), ("window", 0, "probe", 2), ("train", 1, "probe", 2))
        for ra, ia, rb, ib in pairs:
            shared = (role_counts[ia] > 0) & (role_counts[ib] > 0)
            prefix = f"{ra}_{rb}"
            row[f"{prefix}_unique_x_groups"] = int(shared.sum())
            row[f"{prefix}_sample_weighted_rows"] = int(
                (role_counts[ia][shared] + role_counts[ib][shared]).sum()
            )
            row[f"{ra}_rows_with_{rb}_x"] = int(role_counts[ia][shared].sum())
            row[f"{rb}_rows_with_{ra}_x"] = int(role_counts[ib][shared].sum())
        triple = masks == 7
        row["window_train_probe_unique_x_groups"] = int(triple.sum())
        row["window_train_probe_sample_weighted_rows"] = int(
            sum(c[triple].sum() for c in role_counts)
        )
        for ridx, role in enumerate(ROLES):
            row[f"rows_{role}"] = int((row_roles == ridx).sum())
            row[f"unique_x_{role}"] = int((role_counts[ridx] > 0).sum())
        for stratum in STRATA:
            a0, a1 = self.offsets[stratum]
            n = a1 - a0
            for ridx, role in enumerate(ROLES):
                actual = int((row_roles[a0:a1] == ridx).sum())
                row[f"frac_{stratum}_{role}"] = actual / n
                row[f"dev_pp_{stratum}_{role}"] = 100.0 * (
                    actual / n - ROLE_FRACS[role]
                )
        return row


def sample_balanced_keys(
    pools: dict[str, np.ndarray], n_per_class: int, severity: float, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    severity = float(np.clip(severity, 0.0, 1.0))
    n_cur = int(round(n_per_class * severity))
    n_ref = n_per_class - n_cur

    def draw(name: str, n: int) -> np.ndarray:
        idx = rng.integers(0, len(pools[name]), size=n)
        return pools[name][idx]

    xb = np.concatenate([draw("ref_benign", n_ref), draw("cur_benign", n_cur)])
    xa = np.concatenate([draw("ref_attack", n_ref), draw("cur_attack", n_cur)])
    X = np.concatenate([xb, xa])
    y = np.array([0] * n_per_class + [1] * n_per_class)
    perm = rng.permutation(len(y))
    return X[perm], y[perm]


def stream_keys(role_window: dict[str, np.ndarray], seed: int, max_severity: float) -> list[np.ndarray]:
    args = SimpleNamespace(ramp_windows=80, max_severity=max_severity)
    rng = np.random.default_rng(seed)
    result = []
    for t in range(100):
        sev = progressive_severity(t, args)
        keys, _ = sample_balanced_keys(role_window, 64, sev, rng)
        result.append(keys)
    return result


def nested_candidate_keys(
    train: dict[str, np.ndarray], seed: int, t: int, severity: float, size: int
) -> np.ndarray:
    rng = np.random.default_rng(seed * 100_003 + t)
    base, _ = sample_balanced_keys(train, 512, severity, rng)
    ext, _ = sample_balanced_keys(train, 1488, severity, rng)
    return base if size == 512 else np.concatenate([base, ext])


def plain_candidate_keys(
    train: dict[str, np.ndarray], seed: int, t: int, severity: float, size: int
) -> np.ndarray:
    keys, _ = sample_balanced_keys(
        train, size, severity, np.random.default_rng(seed * 100_003 + t)
    )
    return keys


def replay_candidate_keys(
    train: dict[str, np.ndarray], seed: int, t: int, severity: float, size: int
) -> np.ndarray:
    rng = np.random.default_rng(seed * 100_003 + t)
    cur, _ = sample_balanced_keys(train, max(1, size // 2), severity, rng)
    ref, _ = sample_balanced_keys(train, max(1, size // 2), 0.0, rng)
    return np.concatenate([cur, ref])


def exposure_counts(source: np.ndarray, target: np.ndarray) -> tuple[int, int, int, int]:
    source_unique = np.unique(source)
    target_unique = np.unique(target)
    source_hit = np.isin(source, target_unique)
    target_hit = np.isin(target, source_unique)
    return int(source_hit.sum()), len(source), int(target_hit.sum()), len(target)


def _dataset_from_scenario(scenario: str) -> str:
    if scenario.startswith("ps_"):
        return "PortScan"
    if scenario.startswith("unsw_"):
        return "UNSW-Recon"
    if scenario.startswith("ton_"):
        return "ToN-Scanning"
    raise ValueError(scenario)


def proposal_rows(datasets: dict[str, DatasetAudit]) -> list[dict]:
    """Reconstruct exact-X exposure for every stored B2/B1 trained proposal."""
    result: list[dict] = []
    roots = (
        ("B2", ROOT / "results/raw/post_kbs_size_matched_drift", True),
        ("B1", ROOT / "results/raw/post_kbs_common_harness_baselines", False),
    )
    split_cache: dict[tuple[str, int], dict] = {}
    stream_cache: dict[tuple[str, int, float], list[np.ndarray]] = {}
    for block, root, nested in roots:
        for arm_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            rc_path = arm_dir / "run_config.json"
            trig_path = arm_dir / "paper2_v2_trigger_log.csv"
            if not rc_path.exists() or not trig_path.exists():
                continue
            rc = json.loads(rc_path.read_text(encoding="utf-8"))
            if rc.get("policy") == "never":
                continue
            flags = rc["resolved_flags"]
            scenario = rc["scenario"]
            dataset_name = _dataset_from_scenario(scenario)
            ds = datasets[dataset_name]
            policy = rc["policy"]
            size = int(
                flags.get(
                    "--candidate-size-per-class",
                    flags.get("--adapt-size-per-class", 512),
                )
            )
            strategy = flags.get("--adapt-strategy", "full_replace")
            gate = flags.get("--adaptation-gate", "none")
            probe_size = int(flags.get("--probe-size", 32))
            max_sev = float(flags.get("--max-severity", 1.0))
            tr = pd.read_csv(trig_path)
            if "trained" in tr:
                tr = tr[tr["trained"].astype(str).str.lower().eq("true")]
            for rec in tr.to_dict("records"):
                seed = int(rec["seed"])
                t = int(rec["window_idx"])
                sev = float(rec.get("cand_sev_used", np.nan))
                if not np.isfinite(sev):
                    # Replay logs the generic candidate-severity field as NaN, but its
                    # registered code draws the current half at the trigger severity.
                    sev = float(rec.get("severity_t", 0.0))
                cache_key = (dataset_name, seed)
                if cache_key not in split_cache:
                    split_cache[cache_key] = ds.split(seed)[0]
                roles = split_cache[cache_key]
                skey = (dataset_name, seed, max_sev)
                if skey not in stream_cache:
                    stream_cache[skey] = stream_keys(roles["window"], seed, max_sev)
                stream = stream_cache[skey]
                future = np.concatenate(stream[t + 1 :]) if t + 1 < len(stream) else stream[t][:0]
                future10 = (
                    np.concatenate(stream[t + 1 : t + 11])
                    if t + 1 < len(stream)
                    else stream[t][:0]
                )
                if strategy == "replay":
                    cand = replay_candidate_keys(roles["train"], seed, t, sev, size)
                elif nested:
                    cand = nested_candidate_keys(roles["train"], seed, t, sev, size)
                else:
                    cand = plain_candidate_keys(roles["train"], seed, t, sev, size)
                c_future, nc, f_cand, nf = exposure_counts(cand, future)
                c_h10, _, h10_cand, nh10 = exposure_counts(cand, future10)
                row = dict(
                    record_type="candidate_proposal_exposure",
                    block=block,
                    arm=arm_dir.name,
                    scenario=scenario,
                    dataset=dataset_name,
                    policy=policy,
                    gate=gate,
                    adapt_strategy=strategy,
                    candidate_size_per_class=size,
                    seed=seed,
                    proposal_window=t,
                    proposal_severity=sev,
                    candidate_rows=nc,
                    candidate_unique_x=int(len(np.unique(cand))),
                    candidate_rows_x_in_future=c_future,
                    candidate_rows_x_in_future_pct=_pct(c_future, nc),
                    future_rows=future.size,
                    future_rows_x_in_candidate=f_cand,
                    future_rows_x_in_candidate_pct=_pct(f_cand, nf),
                    candidate_rows_x_in_future_h10=c_h10,
                    candidate_rows_x_in_future_h10_pct=_pct(c_h10, nc),
                    future_h10_rows=nh10,
                    future_h10_rows_x_in_candidate=h10_cand,
                    future_h10_rows_x_in_candidate_pct=_pct(h10_cand, nh10),
                )
                if gate == "labeled_probe":
                    probe, _ = sample_balanced_keys(
                        roles["probe"],
                        max(1, probe_size // 2),
                        float(rec.get("severity_t", sev)),
                        np.random.default_rng(seed * 200_003 + t),
                    )
                    c_probe, _, p_cand, npb = exposure_counts(cand, probe)
                    row.update(
                        probe_rows=npb,
                        candidate_rows_x_in_probe=c_probe,
                        candidate_rows_x_in_probe_pct=_pct(c_probe, nc),
                        probe_rows_x_in_candidate=p_cand,
                        probe_rows_x_in_candidate_pct=_pct(p_cand, npb),
                    )
                result.append(row)
    return result


def aggregate_proposals(detail: pd.DataFrame) -> pd.DataFrame:
    if detail.empty:
        return pd.DataFrame()
    keys = ["block", "dataset", "scenario", "policy", "candidate_size_per_class"]
    rows = []
    for group, g in detail.groupby(keys, dropna=False):
        row = dict(zip(keys, group), record_type="candidate_exposure_aggregate")
        row["n_proposals"] = len(g)
        for num, den, stem in (
            ("candidate_rows_x_in_future", "candidate_rows", "candidate_x_future"),
            ("future_rows_x_in_candidate", "future_rows", "future_x_candidate"),
            ("candidate_rows_x_in_future_h10", "candidate_rows", "candidate_x_future_h10"),
            ("future_h10_rows_x_in_candidate", "future_h10_rows", "future_h10_x_candidate"),
            ("candidate_rows_x_in_probe", "candidate_rows", "candidate_x_probe"),
            ("probe_rows_x_in_candidate", "probe_rows", "probe_x_candidate"),
        ):
            if num not in g or g[num].notna().sum() == 0:
                continue
            numerator = int(g[num].fillna(0).sum())
            denominator = int(g.loc[g[num].notna(), den].sum())
            row[f"{stem}_rows"] = numerator
            row[f"{stem}_denominator"] = denominator
            row[f"{stem}_weighted_pct"] = _pct(numerator, denominator)
            pct_col = num + "_pct"
            if pct_col in g:
                row[f"{stem}_proposal_median_pct"] = float(g[pct_col].median())
                row[f"{stem}_proposal_max_pct"] = float(g[pct_col].max())
        rows.append(row)
    return pd.DataFrame(rows)


def write_report(all_rows: pd.DataFrame) -> None:
    global_df = all_rows[all_rows.record_type == "dataset_global"].copy()
    role_df = all_rows[all_rows.record_type == "seed_role_overlap"].copy()
    detail = all_rows[all_rows.record_type == "candidate_proposal_exposure"].copy()
    agg = aggregate_proposals(detail)

    lines = [
        "# Exact cleaned-feature overlap audit",
        "",
        "## Question and equality definition",
        "",
        "The historical splitter is source-row-disjoint: it permutes source row indices within each of the four strata and assigns 50/30/20% to window/train/probe. This audit tests the narrower hostile allegation that exact cleaned raw feature vectors can nevertheless cross roles.",
        "",
        "Feature identity uses the exact representation consumed before scaling/PCA: common columns sorted identically to the runner, numeric coercion, infinities and NaNs mapped to 0.0 by the existing loader, little-endian float64, and signed zero canonicalized. The key is SHA-256 of the complete raw vector. No feature is rounded and no approximate matching is performed. Every repeated digest is checked against the actual canonical vector; collision count is zero.",
        "",
        "`sample-weighted rows` is the sum of all rows in the two named roles belonging to an X-group that spans both roles. Directional columns in the CSV give the exposed rows in each role separately.",
        "",
        "## Dataset-level multiplicity",
        "",
        global_df[
            [
                "dataset",
                "total_rows",
                "unique_x_groups",
                "duplicate_x_groups",
                "duplicate_rows_beyond_first",
                "duplicate_rows_beyond_first_pct",
                "max_group_multiplicity",
                "conflicting_label_x_groups",
                "conflicting_label_rows",
                "conflicting_ref_current_x_groups",
            ]
        ].to_markdown(index=False, floatfmt=".3f"),
        "",
        "Contradictory-label groups are grouped by X only. No row is removed, relabelled or majority-voted in this audit.",
        "",
        "## Historical role overlap across all confirmatory seeds",
        "",
    ]
    role_summary = (
        role_df.groupby(["block", "dataset"])
        .agg(
            seeds=("seed", "nunique"),
            window_train_groups_min=("window_train_unique_x_groups", "min"),
            window_train_groups_median=("window_train_unique_x_groups", "median"),
            window_train_groups_max=("window_train_unique_x_groups", "max"),
            window_probe_groups_median=("window_probe_unique_x_groups", "median"),
            train_probe_groups_median=("train_probe_unique_x_groups", "median"),
            triple_groups_median=("window_train_probe_unique_x_groups", "median"),
            window_train_rows_median=("window_train_sample_weighted_rows", "median"),
        )
        .reset_index()
    )
    lines.extend([role_summary.to_markdown(index=False, floatfmt=".1f"), ""])
    if not agg.empty:
        compact = agg[
            [
                c
                for c in [
                    "block",
                    "dataset",
                    "scenario",
                    "policy",
                    "candidate_size_per_class",
                    "n_proposals",
                    "candidate_x_future_weighted_pct",
                    "future_x_candidate_weighted_pct",
                    "candidate_x_future_h10_weighted_pct",
                    "probe_x_candidate_weighted_pct",
                ]
                if c in agg.columns
            ]
        ]
        lines.extend(
            [
                "## Candidate/future-evaluation and probe exposure",
                "",
                "The stored B2 and B1 trigger logs were replayed diagnostically with their original proposal RNG, proposal-time severity, role split and sampling rule. `future` means all post-proposal evaluation windows; H10 is reported separately. These are exposure diagnostics, not causal estimates.",
                "",
                compact.to_markdown(index=False, floatfmt=".4f"),
                "",
            ]
        )
    finding = bool(
        (role_df["window_train_unique_x_groups"] > 0).any()
        or (role_df["window_probe_unique_x_groups"] > 0).any()
        or (role_df["train_probe_unique_x_groups"] > 0).any()
    )
    lines.extend(
        [
            "## Forensic verdict",
            "",
            (
                "**ALLEGATION REPRODUCED.** Source-row disjointness did not imply exact-feature-value disjointness in any of the three benchmark constructions. This audit does not establish performance bias or causality; it establishes exposure and motivates the frozen group-disjoint sensitivity."
                if finding
                else "**ALLEGATION NOT REPRODUCED.** Stop and diagnose before any sensitivity design."
            ),
            "",
            "The CSV contains every seed-level overlap row, every reconstructed proposal exposure row, and the aggregate rows used above.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    datasets: dict[str, DatasetAudit] = {}
    rows: list[dict] = []
    for name, spec in DATASETS.items():
        print(f"[dataset] {name}", flush=True)
        ds = DatasetAudit.load(name, spec)
        datasets[name] = ds
        rows.append(ds.global_row)
        for block, bdef in BLOCKS.items():
            for seed in bdef["seeds"]:
                rows.append(ds.role_audit_row(block, bdef["scenarios"], seed))
    print("[proposals] reconstructing stored B2/B1 exact-X exposure", flush=True)
    rows.extend(proposal_rows(datasets))
    df = pd.DataFrame(rows)
    agg = aggregate_proposals(df[df.record_type == "candidate_proposal_exposure"])
    df = pd.concat([df, agg], ignore_index=True, sort=False)
    df.to_csv(OUT_CSV, index=False)
    write_report(df)
    print(f"wrote {OUT_CSV.relative_to(ROOT)} ({len(df)} rows)")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
