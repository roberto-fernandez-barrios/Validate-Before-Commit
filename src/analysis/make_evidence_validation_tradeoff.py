"""Evidence-vs-validation trade-off table for the size-matched control (v1.22.1).

Editorial derived analysis only (protocol: notes/v1_22_1_editorial_scope_protocol.md).
Sources are exclusively the sealed v1.22.0 outputs of the size-matched
own-transformer control (by_seed.csv, summary.csv, paired_contrasts.csv,
run_completion.csv, security_metrics.csv) plus the frozen config
configs/size_matched_own_transformer_v1.json; descriptive_contrasts.csv and
multiplicity.csv are read only as identity cross-checks of recomputed values.

The table answers one question from existing outputs: what does investing in more
nominal candidate-training evidence (512 -> 2,000 per class) buy, versus keeping
the challenger small and spending a small validation probe? Nominal adjudication
counts only -- candidate-training labels and probe labels are NOT claimed to have
equal acquisition cost, no inspected-flow or monetary cost is modeled, and this is
not an end-to-end economic analysis.

Statistics: per-seed paired BA differences (unit: seed) with the identical
deterministic centered paired bootstrap already sealed in the artifact
(boot_ci / boot_p_centered / holm reused verbatim). Cells that exist in the sealed
CSVs are recomputed and asserted byte-equal; the only new numbers are the
descriptive, uncorrected gate-vs-never CI95 cells, labelled as such.

Outputs:
  results/tables/v1_22_1_editorial/evidence_validation_tradeoff.csv
  manuscript/generated/table_evidence_validation_tradeoff.tex
  manuscript/tables/table_evidence_validation_tradeoff.tex        (copy for \\input)
  manuscript/tables_ieee/table_evidence_validation_tradeoff.tex   (two-column variant)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.make_paper2_q1_multiplicity import boot_p_centered, holm
from src.analysis.make_symmetric_pipeline_dynamic_001 import boot_ci

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "results" / "tables" / "size_matched_own_transformer_001"
OUT = REPO / "results" / "tables" / "v1_22_1_editorial"
GEN = REPO / "manuscript" / "generated"
CONFIG = REPO / "configs" / "size_matched_own_transformer_v1.json"

SCENARIOS = ("ps_zero", "unsw_zero", "ton_zero")
DATASET = {"ps_zero": "CICIDS2017-PortScan", "unsw_zero": "UNSW-NB15",
           "ton_zero": "ToN-IoT"}
SEEDS = list(range(4001, 4031))
N_CLASSES = 2

MAIN_POLICIES = (("naive", "512"), ("point", "512"), ("strict", "512"),
                 ("naive", "2000"))
SUPP_POLICIES = (("point", "2000"), ("strict", "2000"))


def paired(df: pd.DataFrame, sc: str, a: tuple, b: tuple) -> np.ndarray:
    da = df[(df.scenario == sc) & (df.policy == a[0]) &
            (df.candidate_size == a[1])].set_index("seed")["ba"]
    db = df[(df.scenario == sc) & (df.policy == b[0]) &
            (df.candidate_size == b[1])].set_index("seed")["ba"]
    assert list(da.index) == list(db.index) == SEEDS
    return (da.to_numpy() - db.to_numpy()) * 100.0


def nominal_counts(df: pd.DataFrame, cfg: dict) -> dict:
    """Candidate/probe labels per proposal, derived from config AND logs; assert equal."""
    probe_cfg = int(cfg["policies"]["point"]["--probe-size"])
    assert probe_cfg == int(cfg["policies"]["strict"]["--probe-size"])
    sizes = [int(s) for s in cfg["candidate_sizes_per_class"]]
    counts = {}
    for size in sizes:
        cand_cfg = N_CLASSES * size
        g = df[(df.candidate_size == str(size)) & (df.candidates_trained > 0)]
        cand_log = (g.labels_candidate / g.candidates_trained).round(6).unique()
        assert list(cand_log) == [float(cand_cfg)], (
            f"candidate labels/proposal from logs {cand_log} != config {cand_cfg}")
        gates = g[g.policy.isin(["point", "strict"])]
        probe_log = (gates.labels_probe / gates.candidates_trained).round(6).unique()
        assert list(probe_log) == [float(probe_cfg)], (
            f"probe labels/proposal from logs {probe_log} != config {probe_cfg}")
        naive = g[g.policy == "naive"]
        assert (naive.labels_probe == 0).all(), "naive arms must consume zero probe labels"
        counts[str(size)] = dict(candidate=cand_cfg, probe=probe_cfg)
    incumbent = int(cfg["incumbent_train_size_per_class"])
    extra_per_class = incumbent - min(sizes)
    extra_total = N_CLASSES * extra_per_class
    assert extra_per_class == 1488 and extra_total == 2976, (
        "nominal additional candidate labels must be 1,488/class = 2,976/proposal")
    counts["extra_512_to_2000"] = extra_total
    return counts


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    GEN.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    # keep_default_na=False so the literal candidate_size value "n/a" survives as a string
    df = pd.read_csv(SRC / "by_seed.csv", keep_default_na=False, na_values=[""])
    df = df.astype({"candidate_size": str, "ba": float, "labels_probe": float,
                    "labels_candidate": float, "candidates_trained": float})
    summ = pd.read_csv(SRC / "summary.csv", keep_default_na=False, na_values=[""])
    con = pd.read_csv(SRC / "paired_contrasts.csv")
    comp = pd.read_csv(SRC / "run_completion.csv")
    sec = pd.read_csv(SRC / "security_metrics.csv")
    desc = pd.read_csv(SRC / "descriptive_contrasts.csv")   # identity checks only
    mult = pd.read_csv(SRC / "multiplicity.csv")            # identity checks only

    assert comp.complete.all() and len(comp) == 21, "sealed run must be 21/21 complete"
    counts = nominal_counts(df, cfg)

    # Recompute Holm inside the sealed F3 family and assert identity with multiplicity.csv
    f3 = con[con.family == "F3 gate value at size 2000"].reset_index(drop=True)
    f3_holm = holm(list(f3.p_raw))
    m3 = mult[mult.family == "F3 gate value at size 2000"].set_index("contrast")
    holm_sig = {}
    for (_, r), ph in zip(f3.iterrows(), f3_holm):
        assert round(ph, 10) == round(float(m3.loc[r.contrast, "p_holm"]), 10)
        holm_sig[r.contrast] = bool(ph < 0.05)
        assert holm_sig[r.contrast] == bool(m3.loc[r.contrast, "significant_holm"])

    con_ix = con.set_index("contrast")
    desc_ix = desc.set_index("contrast")
    sec_ix = sec.set_index(["scenario", "policy", "candidate_size"])
    summ_ix = summ.astype({"candidate_size": str}).set_index(
        ["scenario", "policy", "candidate_size"])

    def vs_never(sc: str, pol: str, size: str) -> dict:
        """Paired BA-vs-never effect + CI95. Sealed cells asserted; new cells descriptive."""
        d = paired(df, sc, (pol, size), ("never", "n/a"))
        name = f"{sc}: {pol}-{size} vs never"
        if pol == "naive" and size == "2000":                    # sealed F1 (registered)
            lo, hi = boot_ci(d, f"sm001|{name}|95", 0.95)
            row = con_ix.loc[name]
            assert (round(float(d.mean()), 4) == float(row.effect_pp)
                    and round(lo, 4) == float(row.ci95_lo)
                    and round(hi, 4) == float(row.ci95_hi)), f"identity failed: {name}"
            return dict(eff=float(row.effect_pp), lo=float(row.ci95_lo),
                        hi=float(row.ci95_hi), status="registered F1 (not significant)")
        lo, hi = boot_ci(d, f"sm001|desc|{name}", 0.95)
        cell = dict(eff=round(float(d.mean()), 4), lo=round(lo, 4), hi=round(hi, 4),
                    status="descriptive, uncorrected")
        if name in desc_ix.index:                                # sealed descriptive cell
            row = desc_ix.loc[name]
            assert (cell["eff"] == float(row.effect_pp) and cell["lo"] == float(row.ci95_lo)
                    and cell["hi"] == float(row.ci95_hi)), f"identity failed: {name}"
        return cell

    def gate_gain(sc: str, pol: str, size: str) -> dict:
        if pol == "naive":
            return dict(eff=np.nan, lo=np.nan, hi=np.nan, status="n/a (reference)")
        d = paired(df, sc, (pol, size), ("naive", size))
        name = f"{sc}: {pol}-{size} vs naive-{size}"
        if size == "2000":                                       # sealed F3 (registered)
            lo, hi = boot_ci(d, f"sm001|{name}|95", 0.95)
            row = con_ix.loc[name]
            assert (round(float(d.mean()), 4) == float(row.effect_pp)
                    and round(lo, 4) == float(row.ci95_lo)
                    and round(hi, 4) == float(row.ci95_hi)), f"identity failed: {name}"
            sig = holm_sig[name]
            return dict(eff=float(row.effect_pp), lo=float(row.ci95_lo),
                        hi=float(row.ci95_hi),
                        status=f"registered F3, Holm {'significant' if sig else 'n.s.'}")
        lo, hi = boot_ci(d, f"sm001|desc|{name}", 0.95)          # sealed descriptive cell
        row = desc_ix.loc[name]
        assert (round(float(d.mean()), 4) == float(row.effect_pp)
                and round(lo, 4) == float(row.ci95_lo)
                and round(hi, 4) == float(row.ci95_hi)), f"identity failed: {name}"
        return dict(eff=float(row.effect_pp), lo=float(row.ci95_lo),
                    hi=float(row.ci95_hi), status="descriptive, uncorrected")

    def guardrails(sc: str, pol: str, size: str) -> tuple[str, str]:
        if pol == "naive":
            return "n/a (reference)", "n/a (reference)"
        r = sec_ix.loc[(sc, pol, int(size))]
        return (f"recall NI vs naive-{size}: {'pass' if bool(r.recall_NI_principal) else 'FAIL'}",
                f"FPR NI vs naive-{size}: {'pass' if bool(r.fpr_NI_principal) else 'FAIL'}")

    rows = []
    for block, cells in (("main", MAIN_POLICIES), ("supplementary", SUPP_POLICIES)):
        for sc in SCENARIOS:
            for pol, size in cells:
                v = vs_never(sc, pol, size)
                g = gate_gain(sc, pol, size)
                rec, fpr = guardrails(sc, pol, size)
                probe = counts[size]["probe"] if pol in ("point", "strict") else 0
                cand = counts[size]["candidate"]
                rows.append(dict(
                    block=block, dataset=DATASET[sc], scenario=sc,
                    policy=f"{pol}_{size}", candidate_size_per_class=int(size),
                    candidate_labels_per_proposal=cand,
                    probe_labels_per_proposal=probe,
                    total_adjudicated_labels_per_proposal=cand + probe,
                    ba_vs_never_pp=v["eff"], ba_vs_never_ci95_lo=v["lo"],
                    ba_vs_never_ci95_hi=v["hi"], ba_vs_never_status=v["status"],
                    gate_gain_vs_naive_pp=g["eff"], gate_gain_ci95_lo=g["lo"],
                    gate_gain_ci95_hi=g["hi"], gate_gain_status=g["status"],
                    commits_per_seed=round(float(
                        summ_ix.loc[(sc, pol, size), "commits_mean"]), 3),
                    recall_guardrail=rec, fpr_guardrail=fpr,
                    additional_candidate_labels_512_to_2000=counts["extra_512_to_2000"]))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "evidence_validation_tradeoff.csv", index=False)

    # ---- LaTeX table (main block: 12 rows; supplementary block in the table note)
    def fmt(eff, lo, hi):
        if pd.isna(eff):
            return "---"
        return f"${eff:+.2f}$ [{lo:+.2f}, {hi:+.2f}]"

    pol_label = {"naive_512": "naive 512", "point_512": "point 512 + 32-label probe",
                 "strict_512": "strict 512 + 32-label probe", "naive_2000": "naive 2{,}000"}
    lines_c = []
    for sc in SCENARIOS:
        block = out[(out.scenario == sc) & (out.block == "main")]
        first = True
        for _, r in block.iterrows():
            ds = f"\\multirow{{4}}{{*}}{{{DATASET[sc]}}}" if first else ""
            first = False
            sig = ("\\dag" if "Holm significant" in r.gate_gain_status else "")
            gg = fmt(r.gate_gain_vs_naive_pp, r.gate_gain_ci95_lo, r.gate_gain_ci95_hi)
            lines_c.append(
                f"{ds} & {pol_label[r.policy]} & {r.candidate_labels_per_proposal:,} & "
                f"{r.probe_labels_per_proposal} & "
                f"{fmt(r.ba_vs_never_pp, r.ba_vs_never_ci95_lo, r.ba_vs_never_ci95_hi)} & "
                f"{gg}{sig} & {r.commits_per_seed:.2f} \\\\")
        lines_c.append("\\midrule")
    body = "\n".join(lines_c[:-1])

    caption = (
        "Nominal evidence--validation trade-off under the preregistered zero-drift "
        "size-matched control (own-transformer, random proposals, balanced pools, "
        "SVC-RBF, seeds 4001--4030). ``Cand.''/``Probe'' are nominal adjudicated labels "
        "per proposal; moving from 512 to 2{,}000 per class adds "
        "$2\\times1{,}488 = 2{,}976$ candidate-training labels per proposal versus the "
        "32-label point/strict probe --- counts, not costs: inspected-flow acquisition "
        "is not modeled and no economic dominance is claimed. Paired per-seed BA "
        "contrasts (CI95, deterministic centered paired bootstrap): naive-2{,}000 vs "
        "never is registered F1, gate gains at 2{,}000 are registered F3 (none "
        "Holm-significant), 512-side and gate-vs-never cells are descriptive, "
        "uncorrected. The supplementary point/strict-2{,}000 policies differ from "
        "naive-2{,}000 by $<0.14$ pp (non-significant, CI90-equivalent within "
        "$\\pm$0.5 pp). Guardrails: all matched-size gate cells pass recall/FPR "
        "non-inferiority; at 512 the UNSW strict cell fails recall non-inferiority "
        "(Supplementary~\\S S8).")

    tex = f"""\\begin{{table}}[t]
\\centering
\\caption{{{caption}}}
\\label{{tab:evidence_validation_tradeoff}}
\\footnotesize
\\setlength{{\\tabcolsep}}{{3.5pt}}
\\begin{{tabular}}{{l l r r l l r}}
\\toprule
Dataset & Policy & Cand. & Probe & BA vs never [CI95] & Gate gain vs naive [CI95] & Commits/seed \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    (GEN / "table_evidence_validation_tradeoff.tex").write_text(tex, encoding="utf-8",
                                                                newline="\n")
    (REPO / "manuscript" / "tables" / "table_evidence_validation_tradeoff.tex"
     ).write_text(tex, encoding="utf-8", newline="\n")
    tex_ieee = tex.replace("\\begin{table}[t]", "\\begin{table*}[t]").replace(
        "\\end{table}", "\\end{table*}")
    (REPO / "manuscript" / "tables_ieee" / "table_evidence_validation_tradeoff.tex"
     ).write_text(tex_ieee, encoding="utf-8", newline="\n")

    n_main = int((out.block == "main").sum())
    print(f"evidence_validation_tradeoff: {len(out)} rows ({n_main} main + "
          f"{len(out) - n_main} supplementary); extra candidate labels 512->2000 = "
          f"{counts['extra_512_to_2000']} per proposal; all sealed identity checks passed")


if __name__ == "__main__":
    main()
