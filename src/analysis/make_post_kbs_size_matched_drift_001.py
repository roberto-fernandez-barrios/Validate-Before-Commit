"""Aggregate + analyze the size-matched-under-drift control (21 arms, seeds 6001-6030).

Registered protocol: notes/post_kbs_size_matched_drift_protocol_001.md (design section 2,
families section 3, outcome rules section 4). This script was committed BEFORE the
confirmatory run, as the protocol requires. Statistical machinery is REUSED from the
published modules (deterministic centered paired bootstrap, 100k resamples, per-contrast
label seed; Holm within family; t/Wilcoxon sensitivities). The inferential unit is the
SEED; windows, triggers and commits are never treated as independent units; future-value
summaries are DESCRIPTIVE ONLY and feed no outcome rule (no sign-rate criterion exists
anywhere in this protocol).

Outputs: results/tables/post_kbs_size_matched_drift_001/
  by_seed.csv summary.csv paired_contrasts.csv multiplicity.csv equivalence.csv
  descriptive_contrasts.csv security_metrics.csv harmful_commit_summary.csv
  coupling_audit.csv size_effect_outcome.csv run_completion.csv CLAIM_INTERPRETATION.json
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.make_paper2_q1_multiplicity import (
    PRIMARY,
    boot_p_centered,
    holm,
    p_ttest,
    p_wilcoxon,
)
from src.analysis.make_symmetric_pipeline_dynamic_001 import boot_ci, boot_onesided

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "results" / "raw" / "post_kbs_size_matched_drift"
OUT = REPO / "results" / "tables" / "post_kbs_size_matched_drift_001"
CONFIG = REPO / "configs" / "post_kbs_size_matched_drift_v1.json"

SCENARIOS = ("ps_full", "unsw_full", "ton_full")
SIZES = ("512", "2000")
SEEDS = list(range(6001, 6031))
HORIZONS = (1, 3, 5, 10)

# protocol section 3 margins (absolute percentage points) -- the program's frozen values
BA_MARGIN = 0.5
BA_SENS = (0.2, 1.0)
REC_MARGIN = 1.0
REC_SENS = (0.5, 2.0)
FPR_MARGIN = 0.5
FPR_SENS = (0.25, 1.0)

NEV = ("never", "n/a")


def arm_tag(scenario: str, policy: str, size: str | None) -> str:
    if policy == "never":
        return f"smd_{scenario}_never"
    return f"smd_{scenario}_{policy}_{size}"


def load_by_seed() -> pd.DataFrame:
    """One row per (scenario, policy, candidate_size, seed) with all registered metrics."""
    rows = []
    for sc in SCENARIOS:
        for pol, sizes in (("never", [None]), ("naive", list(SIZES)),
                           ("point", list(SIZES)), ("strict", list(SIZES))):
            for size in sizes:
                d = RAW / arm_tag(sc, pol, size)
                win = pd.read_csv(d / "paper2_progressive_readaptation_window_results.csv")
                bys = pd.read_csv(d / "paper2_progressive_readaptation_by_seed.csv")
                method = "no_adaptation" if pol == "never" else "ks_max"
                w = win[win.method == method]
                res = None
                rl = d / "paper2_v2_resolution_log.csv"
                if pol != "never" and rl.exists():
                    res = pd.read_csv(rl)
                for seed, g in w.groupby("seed"):
                    row = dict(scenario=sc, policy=pol,
                               candidate_size=("n/a" if size is None else size),
                               arm=arm_tag(sc, pol, size), seed=int(seed),
                               ba=float(g.balanced_accuracy.mean()),
                               attack_f1=float(g.f1.mean()),
                               attack_recall=(float(g.recall.mean()) if "recall" in g else np.nan),
                               fpr=(float(g.fpr.mean()) if "fpr" in g else np.nan))
                    b = bys[(bys.seed == seed) & (bys.method == method)]
                    for src, dst in (("n_triggers", "triggers"),
                                     ("n_candidates_trained", "candidates_trained"),
                                     ("n_adaptations", "commits"),
                                     ("n_gate_rejections", "rejects"),
                                     ("labels_used_total", "labels_total"),
                                     ("labels_probe", "labels_probe"),
                                     ("labels_candidate", "labels_candidate")):
                        row[dst] = int(b[src].iloc[0]) if src in b and len(b) else 0
                    if res is not None:
                        rs = res[res.seed == seed]
                        com = rs[rs.resolution_type == "commit"]
                        row["n_resolved_proposals"] = int(len(rs))
                        row["n_commits_logged"] = int(len(com))
                        for h in HORIZONS:
                            ok = com[~com[f"censored_h{h}"].astype(bool)]
                            row[f"mean_delta_res{h}"] = (float(ok[f"delta_res{h}"].mean())
                                                         if len(ok) else np.nan)
                            row[f"harmful_commits_h{h}"] = int((ok[f"delta_res{h}"] < 0).sum())
                            row[f"censored_h{h}"] = int(com[f"censored_h{h}"].astype(bool).sum())
                    rows.append(row)
    df = pd.DataFrame(rows)
    assert sorted(df.seed.unique()) == SEEDS, "seed set mismatch"
    return df


def paired(df: pd.DataFrame, sc: str, a: tuple, b: tuple, metric: str = "ba") -> np.ndarray:
    """Per-seed paired difference metric(armA) - metric(armB), in percentage points.
    The SEED is the inferential unit (protocol section 3)."""
    da = df[(df.scenario == sc) & (df.policy == a[0]) &
            (df.candidate_size == a[1])].set_index("seed")[metric]
    db = df[(df.scenario == sc) & (df.policy == b[0]) &
            (df.candidate_size == b[1])].set_index("seed")[metric]
    assert list(da.index) == list(db.index) == SEEDS
    return (da.to_numpy() - db.to_numpy()) * 100.0


# The four frozen families (protocol section 3)
def family_contrasts():
    fams = []
    for sc in SCENARIOS:
        fams.append(("G1 value of updating", sc,
                     f"{sc}: naive-512 vs never", ("naive", "512"), NEV))
        fams.append(("G1 value of updating", sc,
                     f"{sc}: naive-2000 vs never", ("naive", "2000"), NEV))
    for sc in SCENARIOS:
        fams.append(("G2 size effect (primary)", sc,
                     f"{sc}: naive-2000 vs naive-512", ("naive", "2000"), ("naive", "512")))
    for sc in SCENARIOS:
        fams.append(("G3 gate value at size 2000", sc,
                     f"{sc}: point-2000 vs naive-2000", ("point", "2000"), ("naive", "2000")))
        fams.append(("G3 gate value at size 2000", sc,
                     f"{sc}: strict-2000 vs naive-2000", ("strict", "2000"), ("naive", "2000")))
    for sc in SCENARIOS:
        for pol in ("point", "strict"):
            fams.append(("G4 gate x size interaction (secondary)", sc,
                         f"{sc}: ({pol}-naive)@2000 - ({pol}-naive)@512", ("_ix", pol), None))
    return fams


def contrast_diffs(df: pd.DataFrame, sc: str, A, B) -> np.ndarray:
    if A[0] == "_ix":   # G4: per-seed interaction difference (seed-paired ONLY -- gated
        pol = A[1]      # arms lose proposal coupling after decision divergence, section 2.2)
        return (paired(df, sc, (pol, "2000"), ("naive", "2000"))
                - paired(df, sc, (pol, "512"), ("naive", "512")))
    return paired(df, sc, A, B)


def audit_nesting(df: pd.DataFrame, win_sev: dict) -> int:
    """Protocol 2.1 at confirmatory scale: every full-size candidate's nested prefix hash
    equals the base-size candidate's training hash at the same (seed, creation window); the
    recorded proposal-time severity is identical across sizes and equals the stream's
    severity at that window. Returns verified pairs; raises on any violation."""
    checked = 0
    for sc in SCENARIOS:
        for pol in ("naive", "point", "strict"):
            provs = {}
            for size in SIZES:
                path = RAW / arm_tag(sc, pol, size) / "candidate_provenance.jsonl"
                recs = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
                provs[size] = {(r["seed"], r["creation_window"]): r for r in recs}
            common = set(provs["512"]) & set(provs["2000"])
            assert common, f"no common (seed, window) candidates in {sc}/{pol}"
            for k in common:
                assert provs["2000"][k]["nested_prefix_row_hash"] \
                    == provs["512"][k]["training_row_hash"], \
                    f"NESTING VIOLATION at {sc}/{pol}/{k}"
                assert provs["512"][k]["candidate_size_per_class"] == 512
                assert provs["2000"][k]["candidate_size_per_class"] == 2000
                s5, s2 = provs["512"][k].get("candidate_sev"), provs["2000"][k].get("candidate_sev")
                assert s5 is not None and s5 == s2, \
                    f"SEV MISMATCH across sizes at {sc}/{pol}/{k}: {s5} vs {s2}"
                exp = win_sev[sc].get(k[1])
                assert exp is not None and float(s5) == float(exp), \
                    f"SEV != stream severity at {sc}/{pol}/{k}: {s5} vs {exp}"
                checked += 1
    return checked


def audit_coupling() -> pd.DataFrame:
    """Protocol 2.2: the two NAIVE arms must share identical trigger/commit timelines per
    seed (exactly proposal-coupled); the GATED pairs may diverge after the first discordant
    decision and are seed-paired only. Raises on a naive coupling violation; records the
    first divergence window (or -1) for every pair."""
    rows = []
    for sc in SCENARIOS:
        logs = {}
        for pol in ("naive", "point", "strict"):
            for size in SIZES:
                t = pd.read_csv(RAW / arm_tag(sc, pol, size) / "paper2_v2_trigger_log.csv")
                logs[(pol, size)] = t
        for pol in ("naive", "point", "strict"):
            for seed in SEEDS:
                w5 = logs[(pol, "512")]
                w2 = logs[(pol, "2000")]
                s5 = w5[w5.seed == seed].sort_values("window_idx")
                s2 = w2[w2.seed == seed].sort_values("window_idx")
                t5, t2 = list(s5.window_idx), list(s2.window_idx)
                if t5 == t2:
                    div = -1
                    sev_eq = bool(np.allclose(s5.cand_sev_used.fillna(-9).to_numpy(),
                                              s2.cand_sev_used.fillna(-9).to_numpy()))
                else:
                    div = int(min(set(t5).symmetric_difference(set(t2))))
                    n = 0
                    for a, b in zip(t5, t2):
                        if a != b:
                            break
                        n += 1
                    sev_eq = bool(np.allclose(
                        s5.cand_sev_used.head(n).fillna(-9).to_numpy(),
                        s2.cand_sev_used.head(n).fillna(-9).to_numpy()))
                if pol == "naive":
                    assert div == -1, (f"NAIVE COUPLING VIOLATION {sc} seed {seed}: "
                                       f"trigger timelines diverge at window {div}")
                    assert sev_eq, f"NAIVE SEV COUPLING VIOLATION {sc} seed {seed}"
                rows.append(dict(scenario=sc, policy=pol, seed=seed,
                                 coupling=("proposal-coupled" if div == -1
                                           else "seed-paired (diverged)"),
                                 first_divergence_window=div,
                                 shared_prefix_sev_equal=sev_eq))
    return pd.DataFrame(rows)


def classify(effect: float, ci90: tuple[float, float], p_holm_v: float) -> str:
    """Protocol section 4: magnitude-aware, two-sided, no sign-rate criterion."""
    sig = p_holm_v < 0.05
    if sig and effect >= BA_MARGIN:
        return "SIZE BENEFIT"
    if sig and effect <= -BA_MARGIN:
        return "SIZE COST"
    if -BA_MARGIN < ci90[0] and ci90[1] < BA_MARGIN:
        return "NO MATERIAL SIZE EFFECT"
    return "RESOLVED SUB-MATERIAL" if sig else "UNRESOLVED"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_by_seed()
    df.to_csv(OUT / "by_seed.csv", index=False)

    # per-scenario window severities (from the naive-512 arm's window log; the raw stream
    # is hash-verified identical across arms)
    win_sev = {}
    for sc in SCENARIOS:
        w = pd.read_csv(RAW / arm_tag(sc, "naive", "512")
                        / "paper2_progressive_readaptation_window_results.csv")
        w = w[(w.method == "ks_max") & (w.seed == SEEDS[0])]
        win_sev[sc] = dict(zip(w.window_idx.astype(int), w.severity_t.astype(float)))

    n_nested = audit_nesting(df, win_sev)
    print(f"nesting+sev audit: {n_nested} (seed, window) pairs verified")
    coup = audit_coupling()
    coup.to_csv(OUT / "coupling_audit.csv", index=False)
    print("coupling audit: naive pairs proposal-coupled in "
          f"{int((coup[coup.policy == 'naive'].first_divergence_window == -1).sum())}"
          f"/{len(coup[coup.policy == 'naive'])} seed-scenarios")

    # ---- summary.csv
    summ = (df.groupby(["scenario", "policy", "candidate_size"], as_index=False)
              .agg(ba_mean=("ba", "mean"), ba_sd=("ba", "std"),
                   recall_mean=("attack_recall", "mean"), fpr_mean=("fpr", "mean"),
                   f1_mean=("attack_f1", "mean"), triggers_mean=("triggers", "mean"),
                   candidates_mean=("candidates_trained", "mean"),
                   commits_mean=("commits", "mean"), rejects_mean=("rejects", "mean"),
                   labels_probe_mean=("labels_probe", "mean"),
                   labels_candidate_mean=("labels_candidate", "mean")))
    summ.to_csv(OUT / "summary.csv", index=False)

    # ---- paired contrasts + multiplicity (frozen families, Holm within family)
    crows, mrows = [], []
    for fam, sc, name, A, B in family_contrasts():
        d = contrast_diffs(df, sc, A, B)
        lab = f"smd001|{name}"
        lo95, hi95 = boot_ci(d, lab + "|95", 0.95)
        lo90, hi90 = boot_ci(d, lab + "|90", 0.90)
        crows.append(dict(family=fam, scenario=sc, contrast=name,
                          effect_pp=round(float(d.mean()), 4),
                          ci95_lo=round(lo95, 4), ci95_hi=round(hi95, 4),
                          ci90_lo=round(lo90, 4), ci90_hi=round(hi90, 4),
                          p_raw=boot_p_centered(d, lab), p_ttest=p_ttest(d),
                          p_wilcoxon=p_wilcoxon(d), n_seeds=len(d), p_method=PRIMARY))
    con = pd.DataFrame(crows)
    for fam, g in con.groupby("family"):
        adj = holm(list(g.p_raw))
        for (idx, _), pa in zip(g.iterrows(), adj):
            mrows.append(dict(family=fam, family_size=len(g),
                              contrast=con.loc[idx, "contrast"],
                              effect_pp=con.loc[idx, "effect_pp"],
                              ci95_lo=con.loc[idx, "ci95_lo"], ci95_hi=con.loc[idx, "ci95_hi"],
                              p_raw=con.loc[idx, "p_raw"], p_holm=pa,
                              significant_holm=bool(pa < 0.05), correction="Holm FWER"))
    con.to_csv(OUT / "paired_contrasts.csv", index=False)
    mult = pd.DataFrame(mrows)
    mult.to_csv(OUT / "multiplicity.csv", index=False)

    # ---- descriptive contrasts (uncorrected, labelled)
    drows = []
    for sc in SCENARIOS:
        for name, A, B in ((f"{sc}: point-512 vs naive-512", ("point", "512"), ("naive", "512")),
                           (f"{sc}: strict-512 vs naive-512", ("strict", "512"), ("naive", "512"))):
            d = paired(df, sc, A, B)
            lo, hi = boot_ci(d, f"smd001|desc|{name}", 0.95)
            drows.append(dict(scenario=sc, contrast=name,
                              effect_pp=round(float(d.mean()), 4),
                              ci95_lo=round(lo, 4), ci95_hi=round(hi, 4),
                              note="descriptive, outside the frozen families, uncorrected"))
    pd.DataFrame(drows).to_csv(OUT / "descriptive_contrasts.csv", index=False)

    # ---- equivalence.csv
    erows = []
    for _, r in con.iterrows():
        for margin, kind in [(BA_MARGIN, "primary")] + [(m, "sensitivity") for m in BA_SENS]:
            erows.append(dict(contrast=r["contrast"], margin_pp=margin, margin_kind=kind,
                              ci90_lo=r["ci90_lo"], ci90_hi=r["ci90_hi"],
                              equivalent=bool(-margin < r["ci90_lo"] and r["ci90_hi"] < margin)))
    pd.DataFrame(erows).to_csv(OUT / "equivalence.csv", index=False)

    # ---- security_metrics.csv (NI guardrails gate language only; both sizes)
    srows = []
    for sc in SCENARIOS:
        for size in SIZES:
            for pol in ("naive", "point", "strict"):
                cell = df[(df.scenario == sc) & (df.policy == pol) &
                          (df.candidate_size == size)]
                row = dict(scenario=sc, policy=pol, candidate_size=size,
                           ba=float(cell.ba.mean()) * 100,
                           attack_recall=float(cell.attack_recall.mean()) * 100,
                           fpr=float(cell.fpr.mean()) * 100,
                           attack_f1=float(cell.attack_f1.mean()) * 100)
                if pol in ("point", "strict"):
                    lab = f"smd001|sec|{sc}|{pol}|{size}"
                    d_rec = paired(df, sc, (pol, size), ("naive", size), "attack_recall")
                    d_fpr = paired(df, sc, (pol, size), ("naive", size), "fpr")
                    rec_lo95, _ = boot_onesided(d_rec, lab + "|recall")
                    _, fpr_hi95 = boot_onesided(d_fpr, lab + "|fpr")
                    row.update(d_recall_vs_naive_pp=round(float(d_rec.mean()), 4),
                               recall_onesided_lo95=round(rec_lo95, 4),
                               d_fpr_vs_naive_pp=round(float(d_fpr.mean()), 4),
                               fpr_onesided_hi95=round(fpr_hi95, 4),
                               recall_NI_principal=bool(rec_lo95 > -REC_MARGIN),
                               recall_NI_strict=bool(rec_lo95 > -REC_SENS[0]),
                               recall_NI_lax=bool(rec_lo95 > -REC_SENS[1]),
                               fpr_NI_principal=bool(fpr_hi95 < FPR_MARGIN),
                               fpr_NI_strict=bool(fpr_hi95 < FPR_SENS[0]),
                               fpr_NI_lax=bool(fpr_hi95 < FPR_SENS[1]))
                srows.append(row)
    pd.DataFrame(srows).to_csv(OUT / "security_metrics.csv", index=False)

    # ---- harmful_commit_summary.csv (DESCRIPTIVE ONLY; no outcome rule reads it)
    hrows = []
    for sc in SCENARIOS:
        for size in SIZES:
            for pol in ("naive", "point", "strict"):
                cell = df[(df.scenario == sc) & (df.policy == pol) &
                          (df.candidate_size == size)]
                row = dict(scenario=sc, policy=pol, candidate_size=size,
                           commits_total=int(cell.commits.sum()),
                           commits_logged=int(cell.get("n_commits_logged",
                                                       pd.Series(dtype=float)).sum()))
                for h in HORIZONS:
                    nh = int(cell[f"harmful_commits_h{h}"].sum())
                    nc = int(cell[f"censored_h{h}"].sum())
                    n_eval = row["commits_logged"] - nc
                    row[f"harmful_h{h}"] = nh
                    row[f"censored_h{h}"] = nc
                    row[f"harmful_rate_h{h}"] = round(nh / n_eval, 4) if n_eval > 0 else np.nan
                row["caveat"] = ("DESCRIPTIVE ONLY (protocol section 3): feeds no outcome "
                                 "rule; commits cluster within seed -- no independence "
                                 "assumed, no binomial bound derived")
                hrows.append(row)
    pd.DataFrame(hrows).to_csv(OUT / "harmful_commit_summary.csv", index=False)

    # ---- run_completion.csv
    rrows = []
    for d in sorted(RAW.iterdir()):
        if not d.is_dir():
            continue
        cm = json.loads((d / "completion_marker.json").read_text(encoding="utf-8"))
        rc = json.loads((d / "run_config.json").read_text(encoding="utf-8"))
        sh = hashlib.sha256((d / "raw_stream_hash.txt").read_bytes()).hexdigest()
        rrows.append(dict(arm=d.name, complete=cm["complete"], duration_s=cm["duration_s"],
                          seeds=f"{min(rc['seeds'])}-{max(rc['seeds'])}",
                          n_seeds=len(rc["seeds"]),
                          candidate_size=rc["resolved_flags"].get("--candidate-size-per-class",
                                                                  "n/a"),
                          nested_draw_domain=rc["resolved_flags"].get("--nested-draw-domain",
                                                                      "n/a"),
                          source_commit=rc["source_commit_sha"][:12], mode=rc["mode"],
                          transformer_policy=rc["transformer_policy"],
                          config_sha256=rc.get("config_sha256", ""),
                          derived_operational_from=rc.get("derived_operational_from", ""),
                          raw_stream_hashes_sha256=sh))
    comp = pd.DataFrame(rrows)
    comp.to_csv(OUT / "run_completion.csv", index=False)
    assert len(comp) == 21 and comp.complete.all(), "21/21 completeness violated"
    assert (comp["mode"] == "run").all(), "confirmatory outputs must be authorized-mode"

    # ---- protocol section 4 outcome rules, evaluated literally on G2
    per_sc = {}
    for sc in SCENARIOS:
        name = f"{sc}: naive-2000 vs naive-512"
        r = con[con.contrast == name].iloc[0]
        m = mult[mult.contrast == name].iloc[0]
        cls = classify(float(r["effect_pp"]), (float(r["ci90_lo"]), float(r["ci90_hi"])),
                       float(m["p_holm"]))
        per_sc[sc] = dict(contrast=name, effect_pp=float(r["effect_pp"]),
                          ci95=(float(r["ci95_lo"]), float(r["ci95_hi"])),
                          ci90=(float(r["ci90_lo"]), float(r["ci90_hi"])),
                          p_holm=float(m["p_holm"]), classification=cls)
    classes = {v["classification"] for v in per_sc.values()}
    program = (f"HOMOGENEOUS-{classes.pop()}" if len(classes) == 1 else "HETEROGENEOUS")
    orow = [dict(scenario=sc, **{k: (json.dumps(v) if isinstance(v, tuple) else v)
                                 for k, v in per_sc[sc].items()})
            for sc in SCENARIOS]
    pd.DataFrame(orow).to_csv(OUT / "size_effect_outcome.csv", index=False)

    readings = {
        "SIZE BENEFIT": ("More candidate evidence helps under drift too; the zero-drift "
                         "account extends directionally."),
        "SIZE COST": ("Larger current-mixture candidates over-specialize under an advancing "
                      "ramp even with self-contained preprocessing; this WEAKENS the "
                      "paper's evidence-parity recommendation and must be reported as such."),
        "NO MATERIAL SIZE EFFECT": ("Candidate size is immaterial under full drift at these "
                                    "budgets."),
        "RESOLVED SUB-MATERIAL": ("A resolved but sub-material size effect; reported "
                                  "cell-by-cell, no material claim permitted."),
        "UNRESOLVED": "Unresolved at this precision; no directional claim permitted.",
    }
    payload = dict(
        outcome=program,
        per_scenario=per_sc,
        protocol_file="notes/post_kbs_size_matched_drift_protocol_001.md",
        config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        confirmatory_seeds="6001-6030",
        taxonomy="protocol section 4 (SIZE BENEFIT / SIZE COST / NO MATERIAL SIZE EFFECT / "
                 "RESOLVED SUB-MATERIAL / UNRESOLVED; program HOMOGENEOUS/HETEROGENEOUS)",
        permitted_readings={sc: readings[v["classification"]] for sc, v in per_sc.items()},
        nesting_pairs_verified=n_nested,
        forbidden_claims=[
            "Any PERSISTENCE/ATTENUATION/ELIMINATION label (that taxonomy does not apply here).",
            "Any binomial bound, population probability or production-prevalence estimate "
            "derived from harmful committed proposals (descriptive only; commits cluster "
            "within seed).",
            "Any proposal-coupling claim for gated cross-size contrasts (seed-paired only).",
            "Any presentation of this control as observed-data or operational evidence.",
        ],
        follow_up_authorized=False,
    )
    (OUT / "CLAIM_INTERPRETATION.json").write_text(
        json.dumps(payload, indent=2, default=float), encoding="utf-8")
    print(f"OUTCOME: {program}")
    for sc in SCENARIOS:
        print(f"  {sc}: {per_sc[sc]['classification']}  "
              f"effect {per_sc[sc]['effect_pp']:+.2f} pp  ci95 {per_sc[sc]['ci95']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
