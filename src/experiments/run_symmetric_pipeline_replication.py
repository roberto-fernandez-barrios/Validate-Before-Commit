"""Registered driver for the symmetric-pipeline dynamic replication.

Protocol: notes/paper2_symmetric_pipeline_dynamic_protocol_001.md
Config:   configs/symmetric_pipeline_dynamic_v1.json

Usage (preparation phase — the ONLY authorized modes):
  python -m src.experiments.run_symmetric_pipeline_replication --list-arms
  python -m src.experiments.run_symmetric_pipeline_replication --dry-run
  python -m src.experiments.run_symmetric_pipeline_replication --parity [--only-arm TAG]
  python -m src.experiments.run_symmetric_pipeline_replication --smoke
  python -m src.experiments.run_symmetric_pipeline_replication --validate-complete --parity

Confirmatory execution (FUTURE phase only, after human approval of the frozen
protocol and margins):
  ... --run --confirmatory-authorized

Firewall: the confirmatory seed block (3001-3030) is refused in every mode of this
phase. --smoke and --parity refuse it unconditionally (even with the authorization
flag); --run refuses it without --confirmatory-authorized. Smoke outputs are labelled
SMOKE_ONLY_DO_NOT_ANALYZE and live under results/smoke/, outside the scientific
artifact paths.

Science is NOT reimplemented here: streams, gates, logging, temporal semantics and
harm accounting come from run_paper2_readaptation_v2 (run_seed / run_arm /
write_outputs), driven over raw-stream environments from symmetric_pipeline.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "symmetric_pipeline_dynamic_v1.json"
RUNNER_OUTPUTS = [
    "paper2_progressive_readaptation_by_seed.csv",
    "paper2_progressive_readaptation_window_results.csv",
    "paper2_progressive_readaptation_summary.csv",
]
SMOKE_MARKER = "SMOKE_ONLY_DO_NOT_ANALYZE"
POLICY_SHORT = {"frozen_initial_transformer": "froz", "own_transformer_per_model": "own"}


def load_config(path: Path | None = None) -> dict:
    path = Path(path) if path is not None else CONFIG_PATH
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["_config_path"] = str(path.resolve().relative_to(ROOT)).replace(os.sep, "/")
    if cfg.get("matrix_kind") in ("ijis_exact_value_disjoint_b2",
                                  "ijis_exact_value_disjoint_b1"):
        # The final IJIS sensitivity inherits every scientific constant from the sealed
        # B2/B1 config and changes only the seed blocks, outputs and explicit role mode.
        sensitivity = cfg
        base = load_config(ROOT / sensitivity["base_config"])
        base_scenarios = base["scenarios"]
        base_policies = base["policies"]
        base_fixed = dict(base["fixed_flags"])
        base.update(sensitivity)
        cfg = base
        cfg["_config_path"] = str(path.resolve().relative_to(ROOT)).replace(os.sep, "/")
        cfg["_derived_operational_from"] = (
            sensitivity["base_config"] + "@sha256:" + sensitivity["base_config_sha256"])
        base_fixed["--role-split-mode"] = "exact_feature_group"
        cfg["fixed_flags"] = base_fixed
        cfg["policies"] = base_policies
        selected = sensitivity["scenarios"]
        cfg["scenarios"] = {name: base_scenarios[name] for name in selected}
        cfg["parity_arms"] = []
        if sensitivity["matrix_kind"] == "ijis_exact_value_disjoint_b2":
            cfg["_tag_prefix"] = "xvd_b2"
            cfg["tag_pattern"] = "xvd_b2_{scenario}_{policy}_{512|2000}; never: xvd_b2_{scenario}_never"
        else:
            cfg["_tag_prefix"] = "xvd_b1"
            cfg["scenarios_list"] = list(selected)
            cfg["tag_pattern"] = "xvd_b1_{scenario}_{policy}_{2000|512}; never: xvd_b1_{scenario}_never"
    if cfg.get("matrix_kind") == "post_kbs_size_matched_drift" and "fixed_flags" not in cfg:
        # post-KBS B2: the frozen preregistration config pins every fixed parameter BY
        # REFERENCE (fixed_flags_source = the sealed symmetric-pipeline config); derive
        # the runnable keys here so the frozen JSON never has to be edited. The base
        # config's SHA-256 is recorded so the derivation is auditable per arm.
        base_path = ROOT / "configs" / "symmetric_pipeline_dynamic_v1.json"
        with open(base_path, encoding="utf-8") as bf:
            base = json.load(bf)
        cfg["_derived_operational_from"] = (
            "configs/symmetric_pipeline_dynamic_v1.json@sha256:" + sha256_file(base_path))
        sc_list = list(cfg["scenarios"])
        cfg["fixed_flags"] = base["fixed_flags"]
        cfg["data"] = base["data"]
        cfg["scenarios"] = {sc: base["scenarios"][sc] for sc in sc_list}
        cfg["policies"] = base["policies"]
        cfg["output_paths"] = {
            "confirmatory_outroot": "results/raw/post_kbs_size_matched_drift",
            "smoke_outroot": "results/smoke/post_kbs_size_matched_drift",
            "parity_outroot": "results/smoke/post_kbs_size_matched_drift/parity",
            "tables_outdir": "results/tables/post_kbs_size_matched_drift_001"}
        cfg["smoke_arms"] = ["smd_ps_full_naive_512", "smd_ps_full_naive_2000",
                             "smd_ton_full_strict_2000"]
        cfg["parity_arms"] = [
            dict(tag="parity_smd_ps_full_point_own", scenario="ps_full", policy="point",
                 transformer_policy="own_transformer_per_model",
                 published_dir="results/smoke/symmetric_pipeline/sp_ps_full_point_own",
                 note="flag-off own-transformer full-drift path reproduces the stored "
                      "v1.21.0-code smoke outputs bit-for-bit (seeds 4242-4243)"),
            dict(tag="parity_smd_ps_full_point_own_nested512", scenario="ps_full",
                 policy="point", transformer_policy="own_transformer_per_model",
                 policy_flags={"--adaptation-gate": "labeled_probe", "--probe-size": "32",
                               "--candidate-size-per-class": "512",
                               "--nested-draw-domain": "drift"},
                 published_dir="results/smoke/symmetric_pipeline/sp_ps_full_point_own",
                 note="the nested drift-domain 512 path must ALSO reproduce those stored "
                      "outputs bit-for-bit: the extension consumes per-trigger RNG only "
                      "after the training batch, and nothing downstream reads it")]
        cfg["tag_pattern"] = "smd_{scenario}_{policy}_{512|2000}; never: smd_{scenario}_never"
    return cfg


def reserved_seeds(cfg: dict) -> set[int]:
    s = cfg["confirmatory_seeds"]
    return set(range(s["start"], s["end"] + 1))


def seed_range(d: dict) -> list[int]:
    return list(range(d["start"], d["end"] + 1))


def _merge(*flag_dicts: dict) -> dict:
    merged: dict[str, str] = {}
    for d in flag_dicts:
        merged.update({k: v for k, v in d.items() if k.startswith("--")})
    return merged


def size_matched_arms(cfg: dict) -> list[dict]:
    """The registered 21-arm size-matched matrix (protocol
    paper2_size_matched_own_transformer_001): per zero-drift scenario, 1 never-adapt +
    3 policies x 2 candidate sizes, own_transformer_per_model only. The ONLY flag that
    varies between the size conditions is --candidate-size-per-class (nested canonical
    draw in the science module)."""
    arms = []
    for sc, sdef in cfg["scenarios"].items():
        base = _merge(cfg["fixed_flags"], sdef["override_flags"])
        arms.append(dict(tag=f"sm_{sc}_never", scenario=sc, policy="never",
                         transformer_policy="frozen_initial_transformer",
                         candidate_size=None,
                         data=cfg["data"][sdef["data"]],
                         flags=dict(base, **{"--adaptation-gate": "none"})))
        for pol in ("naive", "point", "strict"):
            pflags = cfg["policies"][pol]
            for size in cfg["candidate_sizes_per_class"]:
                arms.append(dict(tag=f"sm_{sc}_{pol}_{size}", scenario=sc,
                                 policy=pol, transformer_policy="own_transformer_per_model",
                                 candidate_size=int(size),
                                 data=cfg["data"][sdef["data"]],
                                 flags=_merge(base, pflags,
                                              {"--candidate-size-per-class": str(size)})))
    if len(arms) != cfg["expected_arms"]:
        raise SystemExit(f"grid enumerates {len(arms)} arms, expected {cfg['expected_arms']}")
    tags = [a["tag"] for a in arms]
    if len(set(tags)) != len(tags):
        raise SystemExit("duplicate arm tags in grid")
    return arms


def size_matched_drift_arms(cfg: dict) -> list[dict]:
    """post-KBS B2 (protocol post_kbs_size_matched_drift_001): the registered 21-arm
    full-drift matrix -- per full-drift scenario, 1 never-adapt + 3 policies x 2 nested
    candidate sizes, own_transformer_per_model only, --nested-draw-domain drift. The
    ONLY flags that vary between size conditions are --candidate-size-per-class (nested
    canonical draw at sev(t)) with the shared drift-domain switch."""
    arms = []
    prefix = cfg.get("_tag_prefix", "smd")
    for sc, sdef in cfg["scenarios"].items():
        base = _merge(cfg["fixed_flags"], sdef["override_flags"])
        arms.append(dict(tag=f"{prefix}_{sc}_never", scenario=sc, policy="never",
                         transformer_policy="frozen_initial_transformer",
                         candidate_size=None,
                         data=cfg["data"][sdef["data"]],
                         flags=dict(base, **{"--adaptation-gate": "none"})))
        for pol in ("naive", "point", "strict"):
            pflags = cfg["policies"][pol]
            for size in cfg["candidate_sizes_per_class"]:
                arms.append(dict(tag=f"{prefix}_{sc}_{pol}_{size}", scenario=sc,
                                 policy=pol, transformer_policy="own_transformer_per_model",
                                 candidate_size=int(size),
                                 data=cfg["data"][sdef["data"]],
                                 flags=_merge(base, pflags,
                                              {"--candidate-size-per-class": str(size),
                                               "--nested-draw-domain": "drift"})))
    if len(arms) != cfg["expected_arms"]:
        raise SystemExit(f"grid enumerates {len(arms)} arms, expected {cfg['expected_arms']}")
    tags = [a["tag"] for a in arms]
    if len(set(tags)) != len(tags):
        raise SystemExit("duplicate arm tags in grid")
    return arms


def common_harness_arms(cfg: dict) -> list[dict]:
    """post-KBS B1 (protocol post_kbs_common_harness_baselines_001 + amendment 001):
    the amended 96-arm matrix -- per scenario, 1 never-adapt + the primary policies at
    2,000/class (plain balanced draw at proposal-time severity) + the secondary
    512-sensitivity policies. own_transformer_per_model only; per-policy flags come
    from the frozen v2 config (origins recorded per arm).
    """
    arms = []
    prefix = cfg.get("_tag_prefix", "bh")
    for sc in cfg["scenarios_list"]:
        sdef = cfg["scenarios"][sc]
        base = _merge(cfg["fixed_flags"], sdef["override_flags"])
        arms.append(dict(tag=f"{prefix}_{sc}_never", scenario=sc, policy="never",
                         transformer_policy="frozen_initial_transformer",
                         candidate_size=None, origin="anchor",
                         data=cfg["data"][sdef["data"]],
                         flags=dict(base, **{"--adaptation-gate": "none"})))
        for size_key, pols in ((str(cfg["primary_candidate_size_per_class"]),
                                cfg["primary_policies"]),
                               (str(cfg["secondary_candidate_size_per_class"]),
                                cfg["secondary_policies_512"])):
            for pol in pols:
                pdef = cfg["policies"][pol]
                arms.append(dict(tag=f"{prefix}_{sc}_{pol}_{size_key}", scenario=sc,
                                 policy=pol,
                                 transformer_policy="own_transformer_per_model",
                                 candidate_size=int(size_key),
                                 origin=pdef.get("origin", ""),
                                 data=cfg["data"][sdef["data"]],
                                 flags=_merge(base, pdef["flags"],
                                              {"--adapt-size-per-class": size_key})))
    if len(arms) != cfg["expected_arms"]:
        raise SystemExit(f"grid enumerates {len(arms)} arms, expected {cfg['expected_arms']}")
    tags = [a["tag"] for a in arms]
    if len(set(tags)) != len(tags):
        raise SystemExit("duplicate arm tags in grid")
    return arms


def confirmatory_arms(cfg: dict) -> list[dict]:
    """The registered confirmatory matrix for the loaded config."""
    if cfg.get("matrix_kind") in ("post_kbs_common_harness_baselines",
                                   "ijis_exact_value_disjoint_b1"):
        return common_harness_arms(cfg)
    if cfg.get("matrix_kind") in ("post_kbs_size_matched_drift",
                                   "ijis_exact_value_disjoint_b2"):
        return size_matched_drift_arms(cfg)
    if cfg.get("matrix_kind") == "size_matched":
        return size_matched_arms(cfg)
    arms = []
    for sc, sdef in cfg["scenarios"].items():
        base = _merge(cfg["fixed_flags"], sdef["override_flags"])
        arms.append(dict(tag=f"sp_{sc}_never", scenario=sc, policy="never",
                         transformer_policy="frozen_initial_transformer",
                         data=cfg["data"][sdef["data"]],
                         flags=dict(base, **{"--adaptation-gate": "none"})))
        for pol in ("naive", "point", "strict"):
            pflags = cfg["policies"][pol]
            for tpol in cfg["transformer_policies"]:
                arms.append(dict(tag=f"sp_{sc}_{pol}_{POLICY_SHORT[tpol]}", scenario=sc,
                                 policy=pol, transformer_policy=tpol,
                                 data=cfg["data"][sdef["data"]],
                                 flags=_merge(base, pflags)))
    if len(arms) != cfg["expected_arms"]:
        raise SystemExit(f"grid enumerates {len(arms)} arms, expected {cfg['expected_arms']}")
    tags = [a["tag"] for a in arms]
    if len(set(tags)) != len(tags):
        raise SystemExit("duplicate arm tags in grid")
    return arms


def parity_arms(cfg: dict) -> list[dict]:
    arms = []
    for pa in cfg["parity_arms"]:
        sdef = cfg["scenarios"][pa["scenario"]]
        base = _merge(cfg["fixed_flags"], sdef["override_flags"])
        pflags = pa.get("policy_flags") or cfg["policies"][pa["policy"]]
        arms.append(dict(tag=pa["tag"], scenario=pa["scenario"], policy=pa["policy"],
                         transformer_policy=pa.get("transformer_policy",
                                                   "frozen_initial_transformer"),
                         data=cfg["data"][sdef["data"]], flags=_merge(base, pflags),
                         published_dir=pa["published_dir"]))
    return arms


def smoke_arms(cfg: dict) -> list[dict]:
    sel = set(cfg["smoke_arms"])
    arms = [a for a in confirmatory_arms(cfg) if a["tag"] in sel]
    missing = sel - {a["tag"] for a in arms}
    if missing:
        raise SystemExit(f"smoke arms not in registered grid: {sorted(missing)}")
    return arms


def resolve_args(cfg: dict, arm: dict, outdir: Path, seeds: list[int]):
    """Resolve the arm's flags through the SAME argparse surface as the historical CLI."""
    from src.experiments.run_paper2_readaptation_v2 import build_parser
    argv = ["--data-ref", str(ROOT / arm["data"]["ref"]),
            "--data-cur", str(ROOT / arm["data"]["cur"]),
            "--outdir", str(outdir),
            "--seeds", ",".join(str(s) for s in seeds),
            "--methods", cfg["methods"]]
    for k, v in arm["flags"].items():
        argv += [k, str(v)]
    return build_parser().parse_args(argv), argv


def firewall(cfg: dict, seeds: list[int], *, mode: str, authorized: bool) -> None:
    """T12: the confirmatory block may never run in smoke/parity/development modes."""
    hit = sorted(set(seeds) & reserved_seeds(cfg))
    if not hit:
        return
    block = f"{cfg['confirmatory_seeds']['start']}-{cfg['confirmatory_seeds']['end']}"
    if mode in ("smoke", "parity", "dry-run", "development"):
        raise SystemExit(f"CONFIRMATORY SEED FIREWALL: seeds {hit} are reserved "
                         f"({block}) and can NEVER run in --{mode} mode.")
    if not authorized:
        raise SystemExit(f"CONFIRMATORY SEED FIREWALL: seeds {hit} are reserved for the "
                         f"registered confirmatory matrix; pass --confirmatory-authorized "
                         f"only in the authorized future phase.")


def environment_info() -> dict:
    info = dict(python=sys.version, executable=sys.executable, platform=platform.platform())
    for mod in ("numpy", "pandas", "sklearn", "scipy"):
        try:
            info[mod] = __import__(mod).__version__
        except Exception:
            info[mod] = "unavailable"
    return info


def git_source() -> dict:
    def _git(*a):
        try:
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                                  text=True, timeout=30).stdout.strip()
        except Exception:
            return "unknown"
    return dict(source_commit_sha=_git("rev-parse", "HEAD"),
                working_tree_dirty=bool(_git("status", "--porcelain")))


_POOLS_CACHE: dict[str, object] = {}


def load_pools(arm: dict):
    from src.experiments.run_paper2_progressive_readaptation import (
        load_binary_dataset, make_pools)
    key = json.dumps(arm["data"], sort_keys=True)
    if key not in _POOLS_CACHE:
        X_ref, y_ref = load_binary_dataset(ROOT / arm["data"]["ref"], "Label")
        X_cur, y_cur = load_binary_dataset(ROOT / arm["data"]["cur"], "Label")
        common = sorted(set(X_ref.columns).intersection(X_cur.columns))
        _POOLS_CACHE[key] = make_pools(X_ref, y_ref, X_cur, y_cur, common)
    return _POOLS_CACHE[key]


def _recording_candidate_factory(inner, seed: int, base_per_class: int, records: list,
                                 stream_raw=None):
    """Provenance capture for the size-matched control (protocol section 2.4): wraps the
    environment's candidate_factory, recording per candidate the size, the full
    training-batch row hash, the row hash of the nested initial `base_per_class` subset
    (the first 2*base rows ARE the base batch, by the canonical-draw construction), and
    the complete preprocessing/classifier provenance already computed by
    build_candidate_pipeline. Pure logging: the returned pipeline is untouched."""
    from src.experiments.symmetric_pipeline import rows_hash

    def factory(X_raw, y, cseed, C, proba):
        pipe = inner(X_raw, y, cseed, C, proba)
        n = len(y)
        rec = dict(seed=int(seed),
                   candidate_size_per_class=int(n // 2),
                   n_rows=int(n),
                   nested_base_per_class=int(base_per_class),
                   nested_prefix_row_hash=rows_hash(X_raw[: 2 * base_per_class],
                                                    y[: 2 * base_per_class]),
                   **{k: v for k, v in pipe.metadata.items()})
        if stream_raw is not None:
            cw = rec.get("creation_window")
            rec["candidate_sev"] = (float(stream_raw[cw][2])
                                    if cw is not None and 0 <= cw < len(stream_raw)
                                    else None)
        records.append(rec)
        return pipe

    return factory


def run_one_arm(cfg: dict, arm: dict, outdir: Path, seeds: list[int], *,
                mode: str, smoke: bool = False) -> None:
    from src.experiments import run_paper2_readaptation_v2 as v2
    from src.experiments.symmetric_pipeline import build_raw_environment, stream_raw_hash

    outdir.mkdir(parents=True, exist_ok=True)
    args, argv = resolve_args(cfg, arm, outdir, seeds)
    pools = load_pools(arm)
    methods = [] if arm["policy"] == "never" else [cfg["methods"]]
    t0 = datetime.datetime.now(datetime.timezone.utc)
    (outdir / "command.txt").write_text(
        " ".join([sys.executable, "-m", cfg["runner_module"]] + argv) + "\n", encoding="utf-8")
    (outdir / "environment.json").write_text(
        json.dumps(environment_info(), indent=2), encoding="utf-8")

    size_matched = "--candidate-size-per-class" in arm["flags"]
    prov_records: list[dict] = []
    win_rows, trig_rows, sum_rows, res_all, shashes, role_audits = [], [], [], [], [], []
    for seed in seeds:
        print(f"[{arm['tag']} SEED={seed}]", flush=True)
        env = build_raw_environment(pools, args, seed, arm["transformer_policy"])
        if env.role_assignment_audit is not None:
            role_audits.append(dict(arm=arm["tag"], scenario=arm["scenario"],
                                    **env.role_assignment_audit))
        if size_matched:
            env.candidate_factory = _recording_candidate_factory(
                env.candidate_factory, seed, int(args.adapt_size_per_class), prov_records,
                stream_raw=env.stream_raw)
        shashes.append((seed, stream_raw_hash(env.stream_raw)))
        w_, t_, s_, r_ = v2.run_seed(env, args, seed, methods)
        win_rows.extend(w_); trig_rows.extend(t_); sum_rows.extend(s_); res_all.extend(r_)
    if size_matched:
        with open(outdir / "candidate_provenance.jsonl", "w", encoding="utf-8") as fh:
            for rec in prov_records:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
    if role_audits:
        import pandas as pd
        pd.DataFrame(role_audits).to_csv(outdir / "role_assignment_audit.csv", index=False)

    agg = v2.write_outputs(outdir, win_rows, trig_rows, sum_rows, res_all)
    print(agg.to_string(index=False))
    t1 = datetime.datetime.now(datetime.timezone.utc)
    (outdir / "raw_stream_hash.txt").write_text(
        "".join(f"{s},{h}\n" for s, h in shashes), encoding="utf-8")
    (outdir / "run_config.json").write_text(json.dumps(dict(
        tag=arm["tag"], mode=mode, config_version=cfg["config_version"],
        config_file=cfg.get("_config_path", str(CONFIG_PATH.relative_to(ROOT))),
        config_sha256=sha256_file(ROOT / cfg.get("_config_path",
                                                 str(CONFIG_PATH.relative_to(ROOT)))),
        runner_module=cfg["runner_module"], science_module=cfg["science_module"],
        methods=cfg["methods"], seeds=[int(s) for s in seeds],
        scenario=arm["scenario"], policy=arm["policy"],
        transformer_policy=arm["transformer_policy"],
        detector_transform_policy=cfg["detector_transform_policy"],
        data=arm["data"], resolved_flags=arm["flags"], argv=argv,
        derived_operational_from=cfg.get("_derived_operational_from"),
        smoke_only=bool(smoke), started_utc=t0.isoformat(), finished_utc=t1.isoformat(),
        **git_source()), indent=2), encoding="utf-8")
    if smoke:
        (outdir / SMOKE_MARKER).write_text(
            "SMOKE_ONLY_DO_NOT_ANALYZE\nThese outputs use smoke seeds outside the reserved "
            "confirmatory block and must never be aggregated, compared or interpreted.\n",
            encoding="utf-8")
    missing = [f for f in RUNNER_OUTPUTS if not (outdir / f).exists()]
    (outdir / "completion_marker.json").write_text(json.dumps(dict(
        tag=arm["tag"], complete=not missing, missing=missing, mode=mode,
        smoke_only=bool(smoke), finished_utc=t1.isoformat(),
        duration_s=round((t1 - t0).total_seconds(), 1)), indent=2), encoding="utf-8")
    if missing:
        raise SystemExit(f"{arm['tag']}: outputs missing after run: {missing}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# The ONLY tolerated non-byte difference vs the published arms: `served_model_version` was
# added to the window log by f27bded ("Fix deferred-commit timing", the temporal-semantics
# instrumentation audited by audit_paper2_claims q1fp G1) AFTER the published frontier CSVs
# were generated. It is pure logging; every published column must still match exactly.
JUSTIFIED_EXTRA_COLS = {
    "paper2_progressive_readaptation_window_results.csv": {"served_model_version"},
}


def _value_identical(pub_path: Path, new_path: Path, allowed_extra: set[str]) -> tuple[bool, str]:
    """Exact string-level equality on every published column; extra new columns must be
    in the justified allowlist. Returns (ok, detail)."""
    import pandas as pd
    a = pd.read_csv(pub_path, dtype=str)
    b = pd.read_csv(new_path, dtype=str)
    if len(a) != len(b):
        return False, f"row count {len(a)} vs {len(b)}"
    missing = [c for c in a.columns if c not in b.columns]
    if missing:
        return False, f"published columns missing in new output: {missing}"
    extra = [c for c in b.columns if c not in a.columns]
    if set(extra) - allowed_extra:
        return False, f"unjustified extra columns: {sorted(set(extra) - allowed_extra)}"
    eq = (a.fillna("<NA>") == b[list(a.columns)].fillna("<NA>")).all().all()
    if not bool(eq):
        d = (a.fillna("<NA>") != b[list(a.columns)].fillna("<NA>"))
        bad = d.any()[d.any()].index.tolist()
        return False, f"value differences in columns: {bad[:6]}"
    return True, f"all {len(a.columns)} published columns exactly equal" + (
        f"; justified extra columns: {sorted(extra)}" if extra else "")


def compare_parity(arm: dict, outdir: Path) -> dict:
    """Comparison of every runner CSV against the published v1.20.2 arm: byte-identical,
    or exactly value-identical with only explicitly justified extra logging columns."""
    pub = ROOT / arm["published_dir"]
    files = sorted(p.name for p in pub.glob("paper2_*.csv"))
    rows = []
    for name in files:
        new = outdir / name
        if not new.exists():
            rows.append(dict(file=name, status="MISSING_NEW"))
            continue
        h_pub, h_new = sha256_file(pub / name), sha256_file(new)
        if h_pub == h_new:
            rows.append(dict(file=name, status="BIT_IDENTICAL",
                             sha256_published=h_pub, sha256_new=h_new))
            continue
        ok, detail = _value_identical(pub / name, new, JUSTIFIED_EXTRA_COLS.get(name, set()))
        rows.append(dict(file=name,
                         status="VALUE_IDENTICAL_JUSTIFIED_COLS" if ok else "DIFFERS",
                         sha256_published=h_pub, sha256_new=h_new, detail=detail))
    verdict = "PASS" if rows and all(
        r["status"] in ("BIT_IDENTICAL", "VALUE_IDENTICAL_JUSTIFIED_COLS") for r in rows) else "FAIL"
    report = dict(tag=arm["tag"], published_dir=arm["published_dir"],
                  outdir=str(outdir), files=rows, verdict=verdict)
    (outdir / "parity_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[parity {verdict}] {arm['tag']}")
    for r in rows:
        print(f"    {r['status']:>14}  {r['file']}")
    return report


def validate_complete(cfg: dict, *, parity: bool) -> None:
    if parity:
        outroot = ROOT / cfg["output_paths"]["parity_outroot"]
        bad = []
        for arm in parity_arms(cfg):
            rp = outroot / arm["tag"] / "parity_report.json"
            if not rp.exists():
                bad.append((arm["tag"], "no parity_report.json"))
                continue
            rep = json.loads(rp.read_text(encoding="utf-8"))
            if rep.get("verdict") != "PASS":
                bad.append((arm["tag"], f"verdict={rep.get('verdict')}"))
        if bad:
            print("PARITY INCOMPLETE:")
            for t, why in bad:
                print(f"  {t}: {why}")
            raise SystemExit(1)
        print(f"PARITY COMPLETE: all {len(parity_arms(cfg))} parity arms BIT_IDENTICAL vs "
              f"published v1.20.2 outputs")
        return
    outroot = ROOT / cfg["output_paths"]["confirmatory_outroot"]
    missing = [a["tag"] for a in confirmatory_arms(cfg)
               if not (outroot / a["tag"] / "completion_marker.json").exists()]
    if missing:
        print(f"INCOMPLETE: {len(missing)}/{cfg['expected_arms']} confirmatory arms absent "
              f"(expected in this phase: the confirmatory matrix has NOT been executed)")
        for t in missing:
            print(" ", t)
        raise SystemExit(1)
    print(f"{cfg['expected_arms']}/{cfg['expected_arms']} COMPLETE: all registered "
          f"confirmatory arms present")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--list-arms", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--run", action="store_true", help="confirmatory matrix (future phase only)")
    p.add_argument("--parity", action="store_true",
                   help="frozen-mode parity vs published q1fc arms (historical seeds)")
    p.add_argument("--smoke", action="store_true",
                   help="registered smoke arms on smoke seeds, outputs SMOKE_ONLY")
    p.add_argument("--only-arm", type=str, default=None)
    p.add_argument("--resume", action="store_true", help="skip arms with completion marker")
    p.add_argument("--force", action="store_true", help="overwrite existing outputs")
    p.add_argument("--validate-complete", action="store_true")
    p.add_argument("--seeds", type=str, default=None,
                   help="override seeds (development only; confirmatory block always firewalled)")
    p.add_argument("--confirmatory-authorized", action="store_true",
                   help="REQUIRED for confirmatory seeds; must NOT be used in the "
                        "preparation phase")
    p.add_argument("--config", type=Path, default=None,
                   help="registered config JSON (default: the symmetric-pipeline dynamic "
                        "config; pass configs/size_matched_own_transformer_v1.json for the "
                        "size-matched control matrix)")
    a = p.parse_args()
    cfg = load_config(a.config)

    if a.confirmatory_authorized and (a.smoke or a.parity or a.dry_run):
        raise SystemExit("--confirmatory-authorized cannot be combined with "
                         "--smoke/--parity/--dry-run (T12 firewall)")

    if a.list_arms:
        for i, arm in enumerate(confirmatory_arms(cfg)):
            print(i, arm["tag"], f"[{arm['transformer_policy']}]")
        for arm in parity_arms(cfg):
            print("parity:", arm["tag"], "->", arm["published_dir"])
        print("smoke:", ", ".join(cfg["smoke_arms"]), "| smoke seeds:", cfg["smoke_seeds"])
        print("confirmatory seeds (RESERVED):",
              f"{cfg['confirmatory_seeds']['start']}-{cfg['confirmatory_seeds']['end']}")
        return

    if a.validate_complete:
        validate_complete(cfg, parity=a.parity)
        return

    if a.dry_run:
        arms = confirmatory_arms(cfg)
        seeds = seed_range(cfg["confirmatory_seeds"])
        firewall(cfg, [], mode="dry-run", authorized=False)   # dry-run never executes seeds
        outroot = ROOT / cfg["output_paths"]["confirmatory_outroot"]
        for arm in arms if a.only_arm is None else [x for x in arms if x["tag"] == a.only_arm]:
            _, argv = resolve_args(cfg, arm, outroot / arm["tag"], seeds)
            print("DRY-RUN", arm["tag"], "::", " ".join(argv))
        print(f"DRY-RUN ONLY: {len(arms)} confirmatory arms enumerated; nothing executed; "
              f"seeds {cfg['confirmatory_seeds']['start']}-{cfg['confirmatory_seeds']['end']} "
              f"remain firewalled")
        return

    if a.parity:
        seeds = ([int(s) for s in a.seeds.split(",")] if a.seeds
                 else seed_range(cfg["parity_seeds"]))
        firewall(cfg, seeds, mode="parity", authorized=False)
        outroot = ROOT / cfg["output_paths"]["parity_outroot"]
        sel = parity_arms(cfg)
        if a.only_arm is not None:
            sel = [x for x in sel if x["tag"] == a.only_arm]
            if not sel:
                raise SystemExit(f"unknown parity arm {a.only_arm}")
        reports = []
        for arm in sel:
            outdir = outroot / arm["tag"]
            if a.resume and (outdir / "parity_report.json").exists():
                print(f"[skip] {arm['tag']}")
                reports.append(json.loads((outdir / "parity_report.json").read_text(encoding="utf-8")))
                continue
            if outdir.exists() and any(outdir.iterdir()) and not a.force and not a.resume:
                raise SystemExit(f"{arm['tag']}: output exists at {outdir}; use --force/--resume")
            run_one_arm(cfg, arm, outdir, seeds, mode="parity")
            reports.append(compare_parity(arm, outdir))
        verdict = "PASS" if reports and all(r["verdict"] == "PASS" for r in reports) else "FAIL"
        print(f"PARITY OVERALL: {verdict} ({len(reports)} arms)")
        if verdict != "PASS":
            raise SystemExit(1)
        return

    if a.smoke:
        seeds = ([int(s) for s in a.seeds.split(",")] if a.seeds else cfg["smoke_seeds"])
        firewall(cfg, seeds, mode="smoke", authorized=False)
        outroot = ROOT / cfg["output_paths"]["smoke_outroot"]
        sel = smoke_arms(cfg)
        if a.only_arm is not None:
            sel = [x for x in sel if x["tag"] == a.only_arm]
        for arm in sel:
            outdir = outroot / arm["tag"]
            if a.resume and (outdir / "completion_marker.json").exists():
                print(f"[skip] {arm['tag']}")
                continue
            if outdir.exists() and any(outdir.iterdir()) and not a.force and not a.resume:
                raise SystemExit(f"{arm['tag']}: output exists at {outdir}; use --force/--resume")
            run_one_arm(cfg, arm, outdir, seeds, mode="smoke", smoke=True)
        print(f"SMOKE DONE: outputs under {outroot} are {SMOKE_MARKER}")
        return

    if a.run:
        seeds = ([int(s) for s in a.seeds.split(",")] if a.seeds
                 else seed_range(cfg["confirmatory_seeds"]))
        mode = "run" if a.confirmatory_authorized else "development"
        firewall(cfg, seeds, mode=mode, authorized=a.confirmatory_authorized)
        outroot = ROOT / cfg["output_paths"]["confirmatory_outroot"]
        arms = confirmatory_arms(cfg)
        if a.only_arm is not None:
            arms = [x for x in arms if x["tag"] == a.only_arm]
            if not arms:
                raise SystemExit(f"unknown arm {a.only_arm}")
        for arm in arms:
            outdir = outroot / arm["tag"]
            if a.resume and (outdir / "completion_marker.json").exists():
                print(f"[skip] {arm['tag']}")
                continue
            if outdir.exists() and any(outdir.iterdir()) and not a.force and not a.resume:
                raise SystemExit(f"{arm['tag']}: output exists at {outdir}; use --force/--resume")
            run_one_arm(cfg, arm, outdir, seeds, mode=mode)
        return

    p.print_help()


if __name__ == "__main__":
    main()
