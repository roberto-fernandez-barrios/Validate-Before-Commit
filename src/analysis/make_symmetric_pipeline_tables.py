"""Emit the LaTeX tables for the symmetric-pipeline confirmatory replication.

Main body:
  tab:symmetric_pipeline -- the central 12-row matrix (6 scenarios x frozen/own)
  tab:symmetric_security -- security guardrail panel (own-transformer gates vs naive)
Supplement (S7):
  table_symmetric_supp_contrasts -- all 24 frozen-family contrasts, Holm + CI90 equivalence
  table_symmetric_supp_harm      -- harmful future value at H1/3/5/10 + censoring
  table_symmetric_supp_interaction -- gate x transformer interactions (secondary)

Reads exclusively the frozen analysis outputs under
results/tables/symmetric_pipeline_dynamic_001/ (registered protocol
notes/paper2_symmetric_pipeline_dynamic_protocol_001.md + Appendix A), plus descriptive
frozen-side contrasts recomputed from by_seed.csv with the same deterministic bootstrap
(labelled 'desc|', outside the frozen families, uncorrected -- stated in the captions).
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from src.analysis.make_symmetric_pipeline_dynamic_001 import (
    FROZ,
    OWN,
    SEEDS,
    boot_ci,
    paired,
)

SP = "results/tables/symmetric_pipeline_dynamic_001"
OUTS = ["manuscript/tables", "manuscript/tables_ieee"]

SC_NAME = {
    "ps_full": "PortScan full", "unsw_full": "UNSW-Recon full", "ton_full": "ToN-IoT full",
    "ps_zero": "PortScan zero", "unsw_zero": "UNSW-Recon zero", "ton_zero": "ToN-IoT zero",
}
SCENARIOS = list(SC_NAME)


def write(name: str, body: str) -> None:
    for d in OUTS:
        os.makedirs(d, exist_ok=True)
        star = body if d.endswith("tables") else body.replace("{table}", "{table*}")
        open(f"{d}/{name}", "w", encoding="utf-8", newline="\n").write(star)
    print(f"wrote {name}")


def fmt(effect: float, lo: float, hi: float, dag: bool = False) -> str:
    d = "$^{\\dagger}$" if dag else ""
    return f"${effect:+.2f}$ [{lo:.2f}, {hi:.2f}]{d}"


def load():
    df = pd.read_csv(f"{SP}/by_seed.csv")
    # "n/a" (the never-arm transformer policy) is in pandas' default NA list
    df["transformer_policy"] = df["transformer_policy"].fillna("n/a")
    con = pd.read_csv(f"{SP}/paired_contrasts.csv")
    mult = pd.read_csv(f"{SP}/multiplicity.csv")
    sec = pd.read_csv(f"{SP}/security_metrics.csv")
    harm = pd.read_csv(f"{SP}/harmful_commit_summary.csv")
    eq = pd.read_csv(f"{SP}/equivalence.csv")
    ti = pd.read_csv(f"{SP}/transformer_interaction.csv")
    return df, con, mult, sec, harm, eq, ti


def frozen_desc(df, sc, a, b):
    """Descriptive frozen-side paired contrast (same machinery, outside the families)."""
    d = paired(df, sc, a, b)
    lo, hi = boot_ci(d, f"desc|{sc}|{a}|{b}|95", 0.95)
    return float(d.mean()), lo, hi


def main_table(df, con, mult):
    def own_cell(name):
        r = con[con.contrast == name].iloc[0]
        m = mult[mult.contrast == name].iloc[0]
        return fmt(r.effect_pp, r.ci95_lo, r.ci95_hi, dag=bool(m.significant_holm))

    rows = []
    for sc in SCENARIOS:
        nev = df[(df.scenario == sc) & (df.policy == "never")].ba.mean() * 100
        f_nn = fmt(*frozen_desc(df, sc, ("naive", FROZ), ("never", "n/a")))
        f_pn = fmt(*frozen_desc(df, sc, ("point", FROZ), ("naive", FROZ)))
        f_sn = fmt(*frozen_desc(df, sc, ("strict", FROZ), ("naive", FROZ)))
        rows.append(f"{SC_NAME[sc]} & frozen & {nev:.2f} & {f_nn} & {f_pn} & {f_sn} \\\\")
        o_nn = own_cell(f"{sc}: own-naive vs never")
        o_pn = own_cell(f"{sc}: own-point vs own-naive")
        o_sn = own_cell(f"{sc}: own-strict vs own-naive")
        rows.append(f" & own & {nev:.2f} & {o_nn} & {o_pn} & {o_sn} \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    tex = f"""\\begin{{table}}
\\centering
\\caption{{\\textbf{{The symmetric-pipeline dynamic replication (registered; seeds 3001--3030).}}
Shared raw stream per seed (hash-verified across all seven arms); \\emph{{frozen}} = historical
frozen-initial-transformer policy, \\emph{{own}} = self-contained pipelines (each challenger
fits its own scaler/PCA on its own raw batch, bit-identical across policies; commits deploy
the complete bundle). BA points, paired within seed, 30 seeds, deterministic paired-bootstrap
CI95; $\\dagger$ = Holm-significant within its registered family (own rows); frozen rows are
descriptive (uncorrected). Zero drift: random trigger $p{{=}}0.05$, no drift; the detector
representation stays the initial transformer under both policies.}}
\\label{{tab:symmetric_pipeline}}
\\small
\\resizebox{{\\ifdim\\width>\\linewidth \\linewidth\\else\\width\\fi}}{{!}}{{%
\\begin{{tabular}}{{l l r l l l}}
\\toprule
Regime & Transf. & Never BA & Naive $-$ never & Point $-$ naive & Strict $-$ naive \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}}}
\\end{{table}}
"""
    write("table_symmetric_pipeline.tex", tex)


def security_table(sec):
    rows = []
    for sc in SCENARIOS:
        for pol in ("point", "strict"):
            s = sec[(sec.scenario == sc) & (sec.policy == pol)
                    & (sec.transformer_policy == OWN)].iloc[0]
            rec_v = "pass" if s.recall_NI_principal else "\\textbf{fail}"
            fpr_v = "pass" if s.fpr_NI_principal else "\\textbf{fail}"
            rows.append(
                f"{SC_NAME[sc]} & {pol} & ${s.d_recall_vs_naive_pp:+.2f}$ "
                f"(${s.recall_onesided_lo95:+.2f}$) & {rec_v} & "
                f"${s.d_fpr_vs_naive_pp:+.2f}$ (${s.fpr_onesided_hi95:+.2f}$) & {fpr_v} \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    tex = f"""\\begin{{table}}
\\centering
\\caption{{\\textbf{{Security guardrails for the own-transformer gates (vs.\\ own-naive).}}
Paired per-seed $\\Delta$recall and $\\Delta$FPR (pp); parentheses: one-sided 95\\% bound
tested against the preregistered NI margins (recall $>-1.0$; FPR $<+0.5$). All winning cells
pass both margins except UNSW-Recon zero/strict (recall bound $-1.26$; passes the lax $-2.0$)
--- a trade-off, not a security improvement. Guardrails restrict language only; BA determines
the registered classification (Appendix~A).}}
\\label{{tab:symmetric_security}}
\\footnotesize
\\begin{{tabular}}{{l l l l l l}}
\\toprule
Regime & Gate & $\\Delta$recall (lb$_{{95}}$) & NI & $\\Delta$FPR (ub$_{{95}}$) & NI \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    write("table_symmetric_security.tex", tex)


def supp_contrasts(con, mult, eq):
    rows = []
    for fam, g in mult.groupby("family", sort=False):
        rows.append(f"\\multicolumn{{5}}{{l}}{{\\emph{{{fam}}}}} \\\\")
        for _, m in g.iterrows():
            r = con[con.contrast == m.contrast].iloc[0]
            e = eq[(eq.contrast == m.contrast) & (eq.margin_kind == "primary")].iloc[0]
            eqv = "yes" if e.equivalent else "no"
            cname = m.contrast.replace("_", "\\_")
            rows.append(f"{cname} & ${r.effect_pp:+.2f}$ "
                        f"[{r.ci95_lo:.2f}, {r.ci95_hi:.2f}] & {m.p_raw:.5f} & "
                        f"{m.p_holm:.5f} & {eqv} \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Symmetric-pipeline replication: every contrast of the four frozen families
(F1--F4), deterministic centered paired bootstrap (100k resamples), Holm within family.
\\emph{{equiv}}: CI90 fully inside the preregistered $\\pm0.5$-point equivalence margin.
Sensitivity $p$-values (paired $t$, Wilcoxon) are in the artifact
(\\texttt{{paired\\_contrasts.csv}}).}}
\\label{{tab:symmetric_supp_contrasts}}
\\scriptsize
\\begin{{tabular}}{{l r r r c}}
\\toprule
Contrast & effect [CI95] & $p$ & $p_{{\\mathrm{{Holm}}}}$ & equiv $\\pm0.5$ \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    write("table_symmetric_supp_contrasts.tex", tex)


def supp_harm(harm):
    rows = []
    for sc in SCENARIOS:
        for tp, tname in ((FROZ, "frozen"), (OWN, "own")):
            for pol in ("naive", "point", "strict"):
                h = harm[(harm.scenario == sc) & (harm.policy == pol)
                         & (harm.transformer_policy == tp)].iloc[0]
                cells = " & ".join(
                    f"{int(h[f'harmful_h{k}'])}/{int(h['commits_logged'] - h[f'censored_h{k}'])}"
                    for k in (1, 3, 5, 10))
                rows.append(f"{SC_NAME[sc]} & {tname} & {pol} & "
                            f"{int(h.commits_logged)} & {cells} \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Symmetric-pipeline replication: harmful commits (negative candidate-minus-incumbent
balanced accuracy over the H windows after the commit's resolution) out of the commits
evaluable at each horizon; the denominator excludes right-censored commits whose horizon runs
past the stream end. Descriptive only: commits cluster within seeds, are not independent
trials, and no population rate is inferred.}}
\\label{{tab:symmetric_supp_harm}}
\\scriptsize
\\begin{{tabular}}{{l l l r r r r r}}
\\toprule
Regime & Transf. & Policy & Commits & H1 & H3 & H5 & H10 \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    write("table_symmetric_supp_harm.tex", tex)


def supp_interaction(ti):
    rows = []
    for sc in SCENARIOS:
        cells = []
        for pol in ("point", "strict"):
            r = ti[(ti.scenario == sc) & (ti.gate == pol)].iloc[0]
            cells.append(f"${r.interaction_pp:+.2f}$ [{r.ci95_lo:.2f}, {r.ci95_hi:.2f}]")
        rows.append(f"{SC_NAME[sc]} & {cells[0]} & {cells[1]} \\\\")
    body = "\n".join(rows)
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Secondary descriptive gate$\\times$transformer interactions:
$(\\mathrm{{gate}}-\\mathrm{{naive}})_{{\\mathrm{{own}}}} -
(\\mathrm{{gate}}-\\mathrm{{naive}})_{{\\mathrm{{frozen}}}}$, balanced-accuracy points,
CI95. Large negative ToN/zero-drift values say the gate's \\emph{{marginal}} value shrinks
where own-transformer construction already removed most of the frozen-policy harm --- the
registered secondary reading, not a primary estimand.}}
\\label{{tab:symmetric_supp_interaction}}
\\small
\\begin{{tabular}}{{l r r}}
\\toprule
Regime & point & strict \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    write("table_symmetric_supp_interaction.tex", tex)


def main() -> None:
    df, con, mult, sec, harm, eq, ti = load()
    assert sorted(df.seed.unique()) == SEEDS
    main_table(df, con, mult)
    security_table(sec)
    supp_contrasts(con, mult, eq)
    supp_harm(harm)
    supp_interaction(ti)


if __name__ == "__main__":
    main()
