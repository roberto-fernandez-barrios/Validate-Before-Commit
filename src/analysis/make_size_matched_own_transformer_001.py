"""Aggregate + analyze the size-matched own-transformer control (21 arms, seeds 4001-4030).

Registered protocol: notes/paper2_size_matched_own_transformer_protocol_001.md (families
section 5, margins section 4, outcome rules section 6). Statistical machinery is REUSED
from the published make_paper2_q1_multiplicity module (deterministic centered paired
bootstrap, 100k resamples, per-contrast label seed; Holm within family; t-test/Wilcoxon
sensitivities). The inferential unit is the SEED; windows, triggers and commits are never
treated as independent units.

Outputs: results/tables/size_matched_own_transformer_001/
  by_seed.csv summary.csv paired_contrasts.csv multiplicity.csv equivalence.csv
  security_metrics.csv harmful_commit_summary.csv candidate_size_interaction.csv
  run_completion.csv CLAIM_INTERPRETATION.json
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
RAW = REPO / "results" / "raw" / "size_matched_own_transformer"
OUT = REPO / "results" / "tables" / "size_matched_own_transformer_001"
CONFIG = REPO / "configs" / "size_matched_own_transformer_v1.json"

SCENARIOS = ("ps_zero", "unsw_zero", "ton_zero")
SIZES = ("512", "2000")
SEEDS = list(range(4001, 4031))
HORIZONS = (1, 3, 5, 10)

# protocol section 4 margins (absolute percentage points) -- reused v1.21.0 values
BA_MARGIN = 0.5
BA_SENS = (0.2, 1.0)
REC_MARGIN = 1.0
REC_SENS = (0.5, 2.0)
FPR_MARGIN = 0.5
FPR_SENS = (0.25, 1.0)

NEV = ("never", "n/a")


def arm_tag(scenario: str, policy: str, size: str | None) -> str:
    if policy == "never":
        return f"sm_{scenario}_never"
    return f"sm_{scenario}_{policy}_{size}"


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
    """Per-seed paired difference metric(armA) - metric(armB), in percentage points."""
    da = df[(df.scenario == sc) & (df.policy == a[0]) &
            (df.candidate_size == a[1])].set_index("seed")[metric]
    db = df[(df.scenario == sc) & (df.policy == b[0]) &
            (df.candidate_size == b[1])].set_index("seed")[metric]
    assert list(da.index) == list(db.index) == SEEDS
    return (da.to_numpy() - db.to_numpy()) * 100.0


# The four frozen families (protocol section 5): (family, scenario, name, armA, armB)
# F4 rows carry armA/armB = None and are computed as per-seed interaction differences.
def family_contrasts():
    fams = []
    for sc in SCENARIOS:
        fams.append(("F1 size-matched damage", sc,
                     f"{sc}: naive-2000 vs never", ("naive", "2000"), NEV))
    for sc in SCENARIOS:
        fams.append(("F2 candidate-size effect", sc,
                     f"{sc}: naive-2000 vs naive-512", ("naive", "2000"), ("naive", "512")))
    for sc in SCENARIOS:
        fams.append(("F3 gate value at size 2000", sc,
                     f"{sc}: point-2000 vs naive-2000", ("point", "2000"), ("naive", "2000")))
        fams.append(("F3 gate value at size 2000", sc,
                     f"{sc}: strict-2000 vs naive-2000", ("strict", "2000"), ("naive", "2000")))
    for sc in SCENARIOS:
        for pol in ("point", "strict"):
            fams.append(("F4 gate x size interaction (secondary)", sc,
                         f"{sc}: ({pol}-naive)@2000 - ({pol}-naive)@512", ("_ix", pol), None))
    return fams


def contrast_diffs(df: pd.DataFrame, sc: str, A, B) -> np.ndarray:
    if A[0] == "_ix":   # F4: per-seed interaction difference
        pol = A[1]
        return (paired(df, sc, (pol, "2000"), ("naive", "2000"))
                - paired(df, sc, (pol, "512"), ("naive", "512")))
    return paired(df, sc, A, B)


def audit_nesting(df: pd.DataFrame) -> int:
    """T2 at confirmatory scale: every full-size candidate's nested prefix hash equals the
    base-size candidate's training hash at the same (seed, creation window), per scenario
    and policy. Returns the number of verified pairs; raises on any violation."""
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
                checked += 1
    return checked


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_by_seed()
    df.to_csv(OUT / "by_seed.csv", index=False)

    n_nested = audit_nesting(df)
    print(f"nesting audit: {n_nested} (seed, window) pairs verified")

    # ---- summary.csv: cell-level means across seeds
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
        lab = f"sm001|{name}"
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

    # ---- descriptive contrasts needed by the checkpoint (uncorrected, labelled desc|)
    drows = []
    for sc in SCENARIOS:
        for name, A, B in ((f"{sc}: naive-512 vs never", ("naive", "512"), NEV),
                           (f"{sc}: point-512 vs naive-512", ("point", "512"), ("naive", "512")),
                           (f"{sc}: strict-512 vs naive-512", ("strict", "512"), ("naive", "512"))):
            d = paired(df, sc, A, B)
            lo, hi = boot_ci(d, f"sm001|desc|{name}", 0.95)
            drows.append(dict(scenario=sc, contrast=name,
                              effect_pp=round(float(d.mean()), 4),
                              ci95_lo=round(lo, 4), ci95_hi=round(hi, 4),
                              note="descriptive, outside the frozen families, uncorrected"))
    pd.DataFrame(drows).to_csv(OUT / "descriptive_contrasts.csv", index=False)

    # ---- equivalence.csv: CI90-within-margin verdicts for every registered contrast
    erows = []
    for _, r in con.iterrows():
        for margin, kind in [(BA_MARGIN, "primary")] + [(m, "sensitivity") for m in BA_SENS]:
            erows.append(dict(contrast=r["contrast"], margin_pp=margin, margin_kind=kind,
                              ci90_lo=r["ci90_lo"], ci90_hi=r["ci90_hi"],
                              equivalent=bool(-margin < r["ci90_lo"] and r["ci90_hi"] < margin)))
    eq = pd.DataFrame(erows)
    eq.to_csv(OUT / "equivalence.csv", index=False)

    # ---- security_metrics.csv: cells + NI guardrails for gate-vs-naive at the SAME size
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
                    lab = f"sm001|sec|{sc}|{pol}|{size}"
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
    sec = pd.DataFrame(srows)
    sec.to_csv(OUT / "security_metrics.csv", index=False)

    # ---- harmful_commit_summary.csv (descriptive; commits cluster within seed -- caveat)
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
                row["caveat"] = ("descriptive only; commits cluster within seed -- no "
                                 "independence assumed, no binomial bound derived")
                hrows.append(row)
    harm = pd.DataFrame(hrows)
    harm.to_csv(OUT / "harmful_commit_summary.csv", index=False)

    # ---- candidate_size_interaction.csv (E5, secondary; same numbers as family F4)
    irows = []
    for sc in SCENARIOS:
        for pol in ("point", "strict"):
            name = f"{sc}: ({pol}-naive)@2000 - ({pol}-naive)@512"
            r = con[con.contrast == name].iloc[0]
            m = mult[mult.contrast == name].iloc[0]
            irows.append(dict(scenario=sc, gate=pol, interaction_pp=r["effect_pp"],
                              ci95_lo=r["ci95_lo"], ci95_hi=r["ci95_hi"],
                              p_holm=m["p_holm"], significant_holm=m["significant_holm"],
                              note="secondary (protocol E5/F4); never substitutes the "
                                   "primary estimands"))
    pd.DataFrame(irows).to_csv(OUT / "candidate_size_interaction.csv", index=False)

    # ---- run_completion.csv (per-arm provenance ledger)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    protocol_commit = cfg["protocol"]["protocol_commit"][:12]
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
                          source_commit=rc["source_commit_sha"][:12], mode=rc["mode"],
                          transformer_policy=rc["transformer_policy"],
                          config_sha256=rc.get("config_sha256", ""),
                          protocol_commit=protocol_commit,
                          raw_stream_hashes_sha256=sh))
    comp = pd.DataFrame(rrows)
    comp.to_csv(OUT / "run_completion.csv", index=False)
    assert len(comp) == 21 and comp.complete.all(), "21/21 completeness violated"

    # ---- protocol section 6 decision rules, evaluated literally
    def get(name):
        return con[con.contrast == name].iloc[0], mult[mult.contrast == name].iloc[0]

    f1 = {}
    for sc in SCENARIOS:
        r, m = get(f"{sc}: naive-2000 vs never")
        f1[sc] = dict(effect=r["effect_pp"], ci95=(r["ci95_lo"], r["ci95_hi"]),
                      ci90=(r["ci90_lo"], r["ci90_hi"]), p_holm=m["p_holm"],
                      harm_material=bool(r["effect_pp"] <= -BA_MARGIN
                                         and r["ci95_hi"] < 0.0 and m["p_holm"] < 0.05),
                      equiv_pm05=bool(-BA_MARGIN < r["ci90_lo"]
                                      and r["ci90_hi"] < BA_MARGIN))
    ruleP1 = any(v["harm_material"] for v in f1.values())

    gate_wins = {}
    for sc in SCENARIOS:
        for pol in ("point", "strict"):
            name = f"{sc}: {pol}-2000 vs naive-2000"
            r, m = get(name)
            gate_wins[name] = dict(effect=r["effect_pp"], p_holm=m["p_holm"],
                                   win=bool(r["effect_pp"] >= BA_MARGIN and m["p_holm"] < 0.05))
    ruleP2 = any(v["win"] for v in gate_wins.values())

    def cell_guardrails(name):
        sc = name.split(":")[0]
        pol = name.split(": ")[1].split("-")[0]
        s = sec[(sec.scenario == sc) & (sec.policy == pol) &
                (sec.candidate_size == "2000")].iloc[0]
        return bool(s["recall_NI_principal"]), bool(s["fpr_NI_principal"])

    clean_wins, guardrail_restricted_wins = [], []
    for name, v in gate_wins.items():
        if not v["win"]:
            continue
        rec_ok, fpr_ok = cell_guardrails(name)
        (clean_wins if (rec_ok and fpr_ok) else guardrail_restricted_wins).append(name)
    ruleP3 = len(clean_wins) > 0

    ruleE1 = all(v["equiv_pm05"] for v in f1.values())
    gate_equiv = {}
    for sc in SCENARIOS:
        for pol in ("point", "strict"):
            name = f"{sc}: {pol}-2000 vs naive-2000"
            r, _ = get(name)
            gate_equiv[name] = bool(-BA_MARGIN < r["ci90_lo"] and r["ci90_hi"] < BA_MARGIN)
    ruleE2 = all(gate_equiv.values())
    # E3: harmful future value must not contradict the equivalence claim. Registered
    # pre-run: a material contradiction = any dataset where naive-2000 has >= 5 evaluable
    # H5 commits and harmful_rate_h5 >= 0.4 (a promoted-model harm signal incompatible
    # with 'the harm was the size asymmetry').
    e3_detail = {}
    ruleE3 = True
    for sc in SCENARIOS:
        hn = harm[(harm.scenario == sc) & (harm.policy == "naive")
                  & (harm.candidate_size == "2000")].iloc[0]
        n_eval = int(hn["commits_logged"]) - int(hn["censored_h5"])
        rate = hn["harmful_rate_h5"]
        contradiction = bool(n_eval >= 5 and pd.notna(rate) and rate >= 0.4)
        e3_detail[sc] = dict(commits_logged=int(hn["commits_logged"]),
                             evaluable_h5=n_eval, harmful_rate_h5=rate,
                             material_contradiction=contradiction)
        ruleE3 = ruleE3 and not contradiction

    if ruleP1 and ruleP2 and ruleP3:
        outcome = "PERSISTENCE"
    elif ruleE1 and ruleE2 and ruleE3:
        outcome = "ELIMINATION"
    else:
        outcome = "ATTENUATION"

    interp = {
        "PERSISTENCE": ("Candidate-size asymmetry amplifies the effect, but harmful "
                        "promotion persists even for self-contained challengers trained "
                        "with the same per-class sample size as the incumbent."),
        "ELIMINATION": ("The residual zero-drift harm was primarily attributable to "
                        "promoting challengers trained with substantially less data than "
                        "the incumbent."),
        "ATTENUATION": ("Candidate size is an important amplifier, while the remaining "
                        "promotion risk is dataset- and policy-dependent."),
    }
    payload = dict(
        outcome=outcome,
        protocol_commit=cfg["protocol"]["protocol_commit"],
        config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        confirmatory_seeds="4001-4030",
        rules_passed=dict(
            P1_material_size_matched_harm=ruleP1,
            P2_gate_win_ge_0p5_holm_at_2000=ruleP2,
            P3_conclusion_rests_on_guardrail_clean_cell=ruleP3,
            E1_all_naive2000_vs_never_equiv_pm0p5=ruleE1,
            E2_gates_equiv_naive_at_2000_all_datasets=ruleE2,
            E3_no_harmful_future_value_contradiction=ruleE3,
            f1_cells=f1,
            gate_wins={k: v for k, v in gate_wins.items() if v["win"]},
            clean_gate_wins=clean_wins,
            guardrail_restricted_wins=guardrail_restricted_wins,
            gate_equivalence_at_2000=gate_equiv,
            harmful_future_value_naive_2000=e3_detail,
            nesting_pairs_verified=n_nested,
        ),
        primary_conclusion=interp[outcome],
        allowed_claims=[interp[outcome]],
        forbidden_claims=[v for k, v in interp.items() if k != outcome] + [
            "Any binomial bound, population probability or production-prevalence estimate "
            "derived from harmful committed proposals (descriptive only; commits cluster "
            "within seed).",
            "Any presentation of this control as observed-data or operational evidence.",
        ],
        follow_up_authorized=False,
    )
    (OUT / "CLAIM_INTERPRETATION.json").write_text(
        json.dumps(payload, indent=2, default=float), encoding="utf-8")
    print(f"OUTCOME: {outcome}")
    print(json.dumps(payload["rules_passed"], indent=2, default=float)[:2500])
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
