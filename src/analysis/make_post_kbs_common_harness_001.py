"""Aggregate + analyze the amended common-harness baselines experiment (96 arms,
seeds 5001-5030).

Registered protocol: notes/post_kbs_common_harness_baselines_protocol_001.md as amended by
notes/post_kbs_common_harness_baselines_amendment_001.md (families amendment section 4;
per-cell outcome rules and statements S1-S4). This script is committed BEFORE the
confirmatory run. Statistical machinery is REUSED from the published modules. The
inferential unit is the SEED. Anchor-vs-anchor contrasts (naive-never, gate-naive) are
DESCRIPTIVE here by amendment: their registered hypotheses live in the sealed zero-drift
control and in the size-matched-drift experiment, and this experiment must not double-test
them. No sign-rate criterion exists anywhere.

Outputs: results/tables/post_kbs_common_harness_baselines_001/
  by_seed.csv summary.csv paired_contrasts.csv multiplicity.csv equivalence.csv
  descriptive_contrasts.csv cell_classification.csv statements.csv budget_table.csv
  security_metrics.csv run_completion.csv CLAIM_INTERPRETATION.json
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
RAW = REPO / "results" / "raw" / "post_kbs_common_harness_baselines"
OUT = REPO / "results" / "tables" / "post_kbs_common_harness_baselines_001"
CONFIG = REPO / "configs" / "post_kbs_common_harness_baselines_v2.json"

SCENARIOS = ("ps_full", "unsw_full", "ton_full", "ps_zero", "unsw_zero", "ton_zero")
ZERO = ("ps_zero", "unsw_zero", "ton_zero")
FULL = ("ps_full", "unsw_full", "ton_full")
PRIMARY_POLICIES = ("naive", "point", "strict", "atc", "doc", "enscal", "replay",
                    "ddm", "adwin")
SECONDARY_512 = ("naive", "point", "strict", "atc", "doc", "enscal")
COMPARED = ("atc", "doc", "enscal", "replay", "ddm", "adwin")   # PF1/PF2 members
SEEDS = list(range(5001, 5031))

BA_MARGIN = 0.5
BA_SENS = (0.2, 1.0)
REC_MARGIN = 1.0
REC_SENS = (0.5, 2.0)
FPR_MARGIN = 0.5
FPR_SENS = (0.25, 1.0)


def arm_tag(sc: str, pol: str, size: str | None) -> str:
    if pol == "never":
        return f"bh_{sc}_never"
    return f"bh_{sc}_{pol}_{size}"


def load_by_seed() -> pd.DataFrame:
    rows = []
    cells = [("never", None)]
    cells += [(p, "2000") for p in PRIMARY_POLICIES]
    cells += [(p, "512") for p in SECONDARY_512]
    for sc in SCENARIOS:
        for pol, size in cells:
            d = RAW / arm_tag(sc, pol, size)
            win = pd.read_csv(d / "paper2_progressive_readaptation_window_results.csv")
            bys = pd.read_csv(d / "paper2_progressive_readaptation_by_seed.csv")
            method = "no_adaptation" if pol == "never" else "ks_max"
            w = win[win.method == method]
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
                                 ("labels_monitor", "labels_monitor"),
                                 ("labels_candidate", "labels_candidate")):
                    row[dst] = int(b[src].iloc[0]) if src in b and len(b) else 0
                rows.append(row)
    df = pd.DataFrame(rows)
    assert sorted(df.seed.unique()) == SEEDS, "seed set mismatch"
    return df


def paired(df, sc, a, b, metric="ba"):
    da = df[(df.scenario == sc) & (df.policy == a[0]) &
            (df.candidate_size == a[1])].set_index("seed")[metric]
    db = df[(df.scenario == sc) & (df.policy == b[0]) &
            (df.candidate_size == b[1])].set_index("seed")[metric]
    assert list(da.index) == list(db.index) == SEEDS
    return (da.to_numpy() - db.to_numpy()) * 100.0


def family_contrasts():
    fams = []
    for pol in COMPARED:
        for sc in ZERO:
            fams.append(("PF1 zero-drift loss avoidance @2000", sc,
                         f"{sc}: {pol}-2000 vs naive-2000", (pol, "2000"), ("naive", "2000")))
        for sc in FULL:
            fams.append(("PF2 full-drift benefit retention @2000", sc,
                         f"{sc}: {pol}-2000 vs naive-2000", (pol, "2000"), ("naive", "2000")))
    for pol in ("atc", "doc"):
        for sc in SCENARIOS:
            fams.append(("PF3 estimators vs point @2000", sc,
                         f"{sc}: {pol}-2000 vs point-2000", (pol, "2000"), ("point", "2000")))
    for pol in ("atc", "doc", "enscal"):
        for sc in SCENARIOS:
            fams.append(("SF4 512 sensitivity (secondary)", sc,
                         f"{sc}: {pol}-512 vs naive-512", (pol, "512"), ("naive", "512")))
    for pol in ("point", "strict", "atc", "doc", "enscal"):
        for sc in SCENARIOS:
            fams.append(("SF5 method x size interaction (secondary)", sc,
                         f"{sc}: ({pol}-naive)@2000 - ({pol}-naive)@512", ("_ix", pol), None))
    return fams


def contrast_diffs(df, sc, A, B):
    if A[0] == "_ix":   # seed-paired only (amendment section 2): no proposal coupling claimed
        pol = A[1]
        return (paired(df, sc, (pol, "2000"), ("naive", "2000"))
                - paired(df, sc, (pol, "512"), ("naive", "512")))
    return paired(df, sc, A, B)


def classify(effect, ci90, p_holm_v):
    """Amendment section 4: magnitude-aware, two-sided, no sign-rate criterion."""
    sig = (p_holm_v is not None) and (p_holm_v < 0.05)
    if sig and effect >= BA_MARGIN:
        return "MATERIAL GAIN"
    if sig and effect <= -BA_MARGIN:
        return "MATERIAL COST"
    if -BA_MARGIN < ci90[0] and ci90[1] < BA_MARGIN:
        return "COMPATIBLE"
    return "UNRESOLVED"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_by_seed()
    df.to_csv(OUT / "by_seed.csv", index=False)

    summ = (df.groupby(["scenario", "policy", "candidate_size"], as_index=False)
              .agg(ba_mean=("ba", "mean"), ba_sd=("ba", "std"),
                   recall_mean=("attack_recall", "mean"), fpr_mean=("fpr", "mean"),
                   f1_mean=("attack_f1", "mean"), triggers_mean=("triggers", "mean"),
                   commits_mean=("commits", "mean"), rejects_mean=("rejects", "mean"),
                   labels_probe_mean=("labels_probe", "mean"),
                   labels_monitor_mean=("labels_monitor", "mean"),
                   labels_candidate_mean=("labels_candidate", "mean")))
    summ.to_csv(OUT / "summary.csv", index=False)

    crows, mrows = [], []
    for fam, sc, name, A, B in family_contrasts():
        d = contrast_diffs(df, sc, A, B)
        lab = f"bh001|{name}"
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

    # descriptive anchors + the point/strict 512 cells needed by S4's COMPATIBLE leg
    drows = []
    for sc in SCENARIOS:
        names = [(f"{sc}: naive-2000 vs never", ("naive", "2000"), ("never", "n/a")),
                 (f"{sc}: point-2000 vs naive-2000 (anchor)", ("point", "2000"), ("naive", "2000")),
                 (f"{sc}: strict-2000 vs naive-2000 (anchor)", ("strict", "2000"), ("naive", "2000")),
                 (f"{sc}: naive-512 vs never", ("naive", "512"), ("never", "n/a")),
                 (f"{sc}: point-512 vs naive-512", ("point", "512"), ("naive", "512")),
                 (f"{sc}: strict-512 vs naive-512", ("strict", "512"), ("naive", "512")),
                 (f"{sc}: replay-2000 vs naive-2000 (dup of PF row)", ("replay", "2000"), ("naive", "2000"))]
        for name, A, B in names[:6]:
            d = paired(df, sc, A, B)
            lo, hi = boot_ci(d, f"bh001|desc|{name}", 0.95)
            l90, h90 = boot_ci(d, f"bh001|desc90|{name}", 0.90)
            drows.append(dict(scenario=sc, contrast=name,
                              effect_pp=round(float(d.mean()), 4),
                              ci95_lo=round(lo, 4), ci95_hi=round(hi, 4),
                              ci90_lo=round(l90, 4), ci90_hi=round(h90, 4),
                              note="descriptive by amendment (anchor or secondary cell), uncorrected"))
    desc = pd.DataFrame(drows)
    desc.to_csv(OUT / "descriptive_contrasts.csv", index=False)

    erows = []
    for _, r in con.iterrows():
        for margin, kind in [(BA_MARGIN, "primary")] + [(m, "sensitivity") for m in BA_SENS]:
            erows.append(dict(contrast=r["contrast"], margin_pp=margin, margin_kind=kind,
                              ci90_lo=r["ci90_lo"], ci90_hi=r["ci90_hi"],
                              equivalent=bool(-margin < r["ci90_lo"] and r["ci90_hi"] < margin)))
    pd.DataFrame(erows).to_csv(OUT / "equivalence.csv", index=False)

    # ---- per-cell classification (registered families only)
    krows = []
    mm = mult.set_index("contrast")
    for _, r in con.iterrows():
        ph = float(mm.loc[r["contrast"], "p_holm"])
        cls = classify(float(r["effect_pp"]), (float(r["ci90_lo"]), float(r["ci90_hi"])), ph)
        krows.append(dict(family=r["family"], scenario=r["scenario"], contrast=r["contrast"],
                          effect_pp=r["effect_pp"], p_holm=ph, classification=cls))
    kdf = pd.DataFrame(krows)
    kdf.to_csv(OUT / "cell_classification.csv", index=False)

    # ---- statements S1-S4 (amendment section 4), evaluated literally
    def cls_of(name):
        m = kdf[kdf.contrast == name]
        return m.classification.iloc[0] if len(m) else None

    statements = []
    for pol in COMPARED:
        zero_cls = [cls_of(f"{sc}: {pol}-2000 vs naive-2000") for sc in ZERO]
        s1 = (sum(c == "MATERIAL GAIN" for c in zero_cls) >= 2
              and not any(c == "MATERIAL COST" for c in zero_cls))
        full_cls = [cls_of(f"{sc}: {pol}-2000 vs naive-2000") for sc in FULL]
        s2 = any(c == "MATERIAL COST" for c in full_cls)
        statements.append(dict(statement="S1 avoids zero-drift loss under final harness",
                               policy=pol, holds=bool(s1),
                               detail=json.dumps(dict(zip(ZERO, zero_cls)))))
        statements.append(dict(statement="S2 pays for it at full drift",
                               policy=pol, holds=bool(s2),
                               detail=json.dumps(dict(zip(FULL, full_cls)))))
    for pol in ("atc", "doc"):
        pf3 = [cls_of(f"{sc}: {pol}-2000 vs point-2000") for sc in SCENARIOS]
        statements.append(dict(statement="S3 matches the point gate (all six COMPATIBLE)",
                               policy=pol, holds=bool(all(c == "COMPATIBLE" for c in pf3)),
                               detail=json.dumps(dict(zip(SCENARIOS, pf3)))))

    # S4 ordering change: Holm-sig material SF5 interaction AND a material classification
    # flip between the sizes on that scenario (amendment section 4).
    d90 = desc.set_index("contrast")

    def cls512(pol, sc):
        if pol in ("atc", "doc", "enscal"):
            return cls_of(f"{sc}: {pol}-512 vs naive-512")
        r = d90.loc[f"{sc}: {pol}-512 vs naive-512"]
        # descriptive cell: only the CI-based COMPATIBLE/UNRESOLVED legs are available
        return classify(float(r["effect_pp"]), (float(r["ci90_lo"]), float(r["ci90_hi"])), None)

    for pol in ("point", "strict", "atc", "doc", "enscal"):
        fired = []
        for sc in SCENARIOS:
            name = f"{sc}: ({pol}-naive)@2000 - ({pol}-naive)@512"
            r = kdf[kdf.contrast == name].iloc[0]
            ix_material = (r.classification in ("MATERIAL GAIN", "MATERIAL COST"))
            if pol in ("point", "strict"):
                c2000 = cls_of(f"{sc}: {pol}-2000 vs naive-2000")  # not in a family -> None
                if c2000 is None:
                    rr = d90.loc[f"{sc}: {pol}-2000 vs naive-2000 (anchor)"]
                    c2000 = classify(float(rr["effect_pp"]),
                                     (float(rr["ci90_lo"]), float(rr["ci90_hi"])), None)
            else:
                c2000 = cls_of(f"{sc}: {pol}-2000 vs naive-2000")
            c512 = cls512(pol, sc)
            flip = ((c2000 == "MATERIAL GAIN" and c512 in ("MATERIAL COST", "COMPATIBLE"))
                    or (c2000 == "MATERIAL COST" and c512 in ("MATERIAL GAIN", "COMPATIBLE"))
                    or (c2000 == "COMPATIBLE" and c512 in ("MATERIAL GAIN", "MATERIAL COST")))
            if ix_material and flip:
                fired.append(dict(scenario=sc, interaction_pp=float(r.effect_pp),
                                  cls_2000=c2000, cls_512=c512))
        statements.append(dict(statement="S4 method ordering changes with candidate size",
                               policy=pol, holds=bool(fired),
                               detail=json.dumps(fired) if fired
                               else "no material ordering change was resolved"))
    st = pd.DataFrame(statements)
    st.to_csv(OUT / "statements.csv", index=False)

    # ---- budget table (documented, not equalized; ATC/DoC validation labels analytic)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    gval = int(cfg["policies"]["atc"]["flags"]["--gate-val-size"])
    brows = []
    for sc in SCENARIOS:
        for pol, size in [(p, "2000") for p in PRIMARY_POLICIES] + \
                         [(p, "512") for p in SECONDARY_512]:
            cell = df[(df.scenario == sc) & (df.policy == pol) & (df.candidate_size == size)]
            extra_val = (float(cell.candidates_trained.mean()) * gval + gval
                         if pol in ("atc", "doc") else 0.0)
            brows.append(dict(scenario=sc, policy=pol, candidate_size=size,
                              origin=cfg["policies"][pol]["origin"],
                              labels_probe_mean=float(cell.labels_probe.mean()),
                              labels_monitor_mean=float(cell.labels_monitor.mean()),
                              labels_candidate_mean=float(cell.labels_candidate.mean()),
                              labels_trainingtime_validation_analytic=round(extra_val, 1),
                              note=("ATC/DoC validation samples are drawn at training time "
                                    "and are not in the runner's counters; documented "
                                    "analytically (candidates x gate-val-size + one "
                                    "incumbent sample)" if extra_val else "")))
    pd.DataFrame(brows).to_csv(OUT / "budget_table.csv", index=False)

    # ---- guardrails (language-gating): policy vs naive at the same size
    srows = []
    for sc in SCENARIOS:
        for pol, size in ([(p, "2000") for p in PRIMARY_POLICIES if p != "naive"]
                          + [(p, "512") for p in SECONDARY_512 if p != "naive"]):
            lab = f"bh001|sec|{sc}|{pol}|{size}"
            d_rec = paired(df, sc, (pol, size), ("naive", size), "attack_recall")
            d_fpr = paired(df, sc, (pol, size), ("naive", size), "fpr")
            rec_lo95, _ = boot_onesided(d_rec, lab + "|recall")
            _, fpr_hi95 = boot_onesided(d_fpr, lab + "|fpr")
            srows.append(dict(scenario=sc, policy=pol, candidate_size=size,
                              d_recall_vs_naive_pp=round(float(d_rec.mean()), 4),
                              recall_onesided_lo95=round(rec_lo95, 4),
                              d_fpr_vs_naive_pp=round(float(d_fpr.mean()), 4),
                              fpr_onesided_hi95=round(fpr_hi95, 4),
                              recall_NI_principal=bool(rec_lo95 > -REC_MARGIN),
                              fpr_NI_principal=bool(fpr_hi95 < FPR_MARGIN)))
    pd.DataFrame(srows).to_csv(OUT / "security_metrics.csv", index=False)

    # ---- run_completion
    rrows = []
    for d in sorted(RAW.iterdir()):
        if not d.is_dir():
            continue
        cm = json.loads((d / "completion_marker.json").read_text(encoding="utf-8"))
        rc = json.loads((d / "run_config.json").read_text(encoding="utf-8"))
        rrows.append(dict(arm=d.name, complete=cm["complete"], duration_s=cm["duration_s"],
                          seeds=f"{min(rc['seeds'])}-{max(rc['seeds'])}",
                          n_seeds=len(rc["seeds"]), mode=rc["mode"],
                          adapt_size=rc["resolved_flags"].get("--adapt-size-per-class", ""),
                          trigger_mode=rc["resolved_flags"].get("--trigger-mode", ""),
                          gate=rc["resolved_flags"].get("--adaptation-gate", ""),
                          source_commit=rc["source_commit_sha"][:12],
                          config_sha256=rc.get("config_sha256", "")))
    comp = pd.DataFrame(rrows)
    comp.to_csv(OUT / "run_completion.csv", index=False)
    assert len(comp) == 96 and comp.complete.all(), "96/96 completeness violated"
    assert (comp["mode"] == "run").all(), "confirmatory outputs must be authorized-mode"

    payload = dict(
        outcome="cell-classification map + statements S1-S4 (no single label; no ranking)",
        protocol_file="notes/post_kbs_common_harness_baselines_protocol_001.md",
        amendment_file="notes/post_kbs_common_harness_baselines_amendment_001.md",
        config_sha256=hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        confirmatory_seeds="5001-5030",
        statements=[dict(statement=s["statement"], policy=s["policy"],
                         holds=bool(s["holds"])) for s in statements],
        forbidden_claims=[
            "Any 'SoTA comparison' or global-superiority claim (trade-off mapping only).",
            "Any adaptive-NIDS SoTA label for any evaluated row.",
            "Any inferential use of the descriptive anchor contrasts (registered "
            "hypotheses live in the sealed zero-drift control and in "
            "post_kbs_size_matched_drift).",
            "Any proposal-coupling claim for cross-size contrasts (seed-paired only).",
            "Any pooling of these results with other seed blocks or harnesses.",
        ],
        follow_up_authorized=False,
    )
    (OUT / "CLAIM_INTERPRETATION.json").write_text(
        json.dumps(payload, indent=2, default=float), encoding="utf-8")
    print("STATEMENTS:")
    for s in statements:
        print(f"  {s['statement']:60s} {s['policy']:8s} -> {s['holds']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
