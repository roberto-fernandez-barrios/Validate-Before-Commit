"""Emit the LaTeX tables for the size-matched own-transformer control.

Main body:
  tab:size_matched -- the central 3-row decisive-control matrix (one row per zero-drift
  benchmark: 512 harm replication, 2000 equivalence, size effect, gate effects at 2000)
  tab:size_matched_security -- guardrail summary at the matched size
Supplement (S8):
  table_size_matched_supp_contrasts -- all 18 F1-F4 contrasts, Holm + CI90 equivalence
  table_size_matched_supp_harm      -- future-negative sign accounting at H1/3/5/10 + censoring
  table_size_matched_supp_interaction -- gate x size interactions (F4, secondary)

Reads exclusively the frozen analysis outputs under
results/tables/size_matched_own_transformer_001/ (registered protocol
notes/paper2_size_matched_own_transformer_protocol_001.md); no number is hand-typed.
"""
from __future__ import annotations

import os

import pandas as pd

SM = "results/tables/size_matched_own_transformer_001"
OUTS = ["manuscript/tables", "manuscript/tables_ieee"]

SC_NAME = {
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
    df = pd.read_csv(f"{SM}/by_seed.csv")
    con = pd.read_csv(f"{SM}/paired_contrasts.csv")
    mult = pd.read_csv(f"{SM}/multiplicity.csv")
    eq = pd.read_csv(f"{SM}/equivalence.csv")
    sec = pd.read_csv(f"{SM}/security_metrics.csv", dtype={"candidate_size": str})
    harm = pd.read_csv(f"{SM}/harmful_commit_summary.csv", dtype={"candidate_size": str})
    desc = pd.read_csv(f"{SM}/descriptive_contrasts.csv")
    ix = pd.read_csv(f"{SM}/candidate_size_interaction.csv")
    return df, con, mult, eq, sec, harm, desc, ix


def cell(con, mult, name):
    r = con[con.contrast == name].iloc[0]
    m = mult[mult.contrast == name].iloc[0]
    return fmt(r.effect_pp, r.ci95_lo, r.ci95_hi, dag=bool(m.significant_holm))


def main_table(df, con, mult, eq, desc):
    rows = []
    for sc in SCENARIOS:
        nev = df[(df.scenario == sc) & (df.policy == "never")].ba.mean() * 100
        d = desc[desc.contrast == f"{sc}: naive-512 vs never"].iloc[0]
        c512 = fmt(d.effect_pp, d.ci95_lo, d.ci95_hi)
        c2000 = cell(con, mult, f"{sc}: naive-2000 vs never")
        e = eq[(eq.contrast == f"{sc}: naive-2000 vs never")
               & (eq.margin_kind == "primary")].iloc[0]
        eqv = "yes" if e.equivalent else "no"
        size = cell(con, mult, f"{sc}: naive-2000 vs naive-512")
        pt = cell(con, mult, f"{sc}: point-2000 vs naive-2000")
        st = cell(con, mult, f"{sc}: strict-2000 vs naive-2000")
        rows.append(f"{SC_NAME[sc]} & {nev:.2f} & {c512} & {c2000} & {eqv} & "
                    f"{size} & {pt} & {st} \\\\")
    body = "\n".join(rows)
    tex = f"""\\begin{{table}}
\\centering
\\caption{{\\textbf{{The size-matched self-contained challenger control (registered; seeds
4001--4030).}} Zero drift, random proposal trigger, own-transformer only; the sole new
variable is the challenger's per-class training size (512 vs.\\ the incumbent's 2{{,}}000),
with nested candidate batches (\\S\\ref{{sec:sizematched_method}}). BA points, paired within
seed, 30 fresh seeds, paired-bootstrap CI95; $\\dagger$ = Holm-significant within its
registered family; the 512-vs-never column is descriptive (uncorrected). \\emph{{eq}}: CI90
fully inside the preregistered $\\pm0.5$-point equivalence margin.}}
\\label{{tab:size_matched}}
\\small
\\resizebox{{\\ifdim\\width>\\linewidth \\linewidth\\else\\width\\fi}}{{!}}{{%
\\begin{{tabular}}{{l r l l c l l l}}
\\toprule
Regime & Never BA & Naive$_{{512}}-$never & Naive$_{{2000}}-$never & eq &
Naive$_{{2000}}-$naive$_{{512}}$ & Point$_{{2000}}-$naive$_{{2000}}$ &
Strict$_{{2000}}-$naive$_{{2000}}$ \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}}}
\\end{{table}}
"""
    write("table_size_matched.tex", tex)


def security_table(sec):
    rows = []
    for sc in SCENARIOS:
        for pol in ("point", "strict"):
            s = sec[(sec.scenario == sc) & (sec.policy == pol)
                    & (sec.candidate_size == "2000")].iloc[0]
            rec_v = "pass" if s.recall_NI_principal else "\\textbf{fail}"
            fpr_v = "pass" if s.fpr_NI_principal else "\\textbf{fail}"
            rows.append(
                f"{SC_NAME[sc]} & {pol} & ${s.d_recall_vs_naive_pp:+.2f}$ "
                f"(${s.recall_onesided_lo95:+.2f}$) & {rec_v} & "
                f"${s.d_fpr_vs_naive_pp:+.2f}$ (${s.fpr_onesided_hi95:+.2f}$) & {fpr_v} \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    s512 = sec[(sec.scenario == "unsw_zero") & (sec.policy == "strict")
               & (sec.candidate_size == "512")].iloc[0]
    tex = f"""\\begin{{table}}
\\centering
\\caption{{\\textbf{{Security guardrails at the matched size (gates vs.\\ naive, both at
2{{,}}000/class).}} Paired per-seed $\\Delta$recall and $\\Delta$FPR (pp); parentheses:
one-sided 95\\% bound tested against the preregistered NI margins (recall $>-1.0$;
FPR $<+0.5$). All six matched-size cells pass both margins; at 512 the zero-drift
UNSW-Recon strict cell again fails recall non-inferiority
(bound ${s512.recall_onesided_lo95:+.2f}$), replicating the prior trade-off. Absence of a
security trade-off is not evidence of gate utility: the same cells show no significant BA
gain (main text, size-matched table).}}
\\label{{tab:size_matched_security}}
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
    write("table_size_matched_security.tex", tex)


def supp_contrasts(con, mult, eq):
    rows = []
    for fam, g in mult.groupby("family", sort=False):
        rows.append(f"\\multicolumn{{5}}{{l}}{{\\emph{{{fam}}}}} \\\\")
        for _, m in g.iterrows():
            r = con[con.contrast == m.contrast].iloc[0]
            e = eq[(eq.contrast == m.contrast) & (eq.margin_kind == "primary")].iloc[0]
            eqv = "yes" if e.equivalent else "no"
            cname = m.contrast.replace("_", "\\_").replace("@", "\\,@\\,")
            rows.append(f"{cname} & ${r.effect_pp:+.2f}$ "
                        f"[{r.ci95_lo:.2f}, {r.ci95_hi:.2f}] & {m.p_raw:.5f} & "
                        f"{m.p_holm:.5f} & {eqv} \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Size-matched control: every contrast of the four frozen families (F1--F4),
deterministic centered paired bootstrap (100k resamples), Holm within family.
\\emph{{equiv}}: CI90 fully inside the preregistered $\\pm0.5$-point equivalence margin
($\\pm0.2$/$\\pm1.0$ sensitivities in \\texttt{{equivalence.csv}}). F4 interactions are
secondary. Sensitivity $p$-values (paired $t$, Wilcoxon) are in the artifact
(\\texttt{{paired\\_contrasts.csv}}).}}
\\label{{tab:size_matched_supp_contrasts}}
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
    write("table_size_matched_supp_contrasts.tex", tex)


def supp_harm(harm):
    rows = []
    for sc in SCENARIOS:
        for size in ("512", "2000"):
            for pol in ("naive", "point", "strict"):
                h = harm[(harm.scenario == sc) & (harm.policy == pol)
                         & (harm.candidate_size == size)].iloc[0]
                cells = " & ".join(
                    f"{int(h[f'harmful_h{k}'])}/{int(h['commits_logged'] - h[f'censored_h{k}'])}"
                    for k in (1, 3, 5, 10))
                rows.append(f"{SC_NAME[sc]} & {size} & {pol} & "
                            f"{int(h.commits_logged)} & {cells} \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Size-matched control: future-negative signs (negative candidate-minus-incumbent
balanced accuracy over the H windows after the commit's resolution) out of the commits
evaluable at each horizon; denominators exclude right-censored commits. At the matched size
the mean five-window future value is $\\approx 0$ in every benchmark, so the near-50\\%
H5 sign rates are proposal-level variability around a null mean, not directional loss.
Descriptive only: commits cluster within seeds, are not independent trials, and no
population rate or deployment probability is inferred.}}
\\label{{tab:size_matched_supp_harm}}
\\scriptsize
\\begin{{tabular}}{{l l l r r r r r}}
\\toprule
Regime & Size & Policy & Commits & H1 & H3 & H5 & H10 \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    write("table_size_matched_supp_harm.tex", tex)


def supp_interaction(ix):
    rows = []
    for sc in SCENARIOS:
        cells = []
        for pol in ("point", "strict"):
            r = ix[(ix.scenario == sc) & (ix.gate == pol)].iloc[0]
            dag = "$^{\\dagger}$" if bool(r.significant_holm) else ""
            cells.append(f"${r.interaction_pp:+.2f}$ [{r.ci95_lo:.2f}, {r.ci95_hi:.2f}]{dag}")
        rows.append(f"{SC_NAME[sc]} & {cells[0]} & {cells[1]} \\\\")
    body = "\n".join(rows)
    tex = f"""\\begin{{table}}
\\centering
\\caption{{Secondary gate$\\times$size interactions (family F4, Holm within family;
$\\dagger$ = significant): $(\\mathrm{{gate}}-\\mathrm{{naive}})_{{2000}} -
(\\mathrm{{gate}}-\\mathrm{{naive}})_{{512}}$, balanced-accuracy points, CI95. Uniformly
negative: the gates' value at 512 was largely compensation for the challenger's evidence
disadvantage, and it shrinks significantly once the sizes match --- a secondary registered
reading, never a substitute for the primary estimands.}}
\\label{{tab:size_matched_supp_interaction}}
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
    write("table_size_matched_supp_interaction.tex", tex)


def main() -> None:
    df, con, mult, eq, sec, harm, desc, ix = load()
    main_table(df, con, mult, eq, desc)
    security_table(sec)
    supp_contrasts(con, mult, eq)
    supp_harm(harm)
    supp_interaction(ix)


if __name__ == "__main__":
    main()
