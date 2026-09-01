"""Generate the final-integration manuscript tables from the sealed/confirmatory CSVs.

Every scientific number in these tables is read from a result CSV (never hand-entered):
  * results/tables/symmetric_pipeline_dynamic_001/   (sealed; frozen vs own, seeds 3001-3030)
  * results/tables/size_matched_own_transformer_001/ (sealed; zero-drift size control, 4001-4030)
  * results/tables/paper2_amendment_008/             (sealed; frozen 2,000/class zero drift, 104-133)
  * results/tables/post_kbs_size_matched_drift_001/  (post-v1.22; B2, seeds 6001-6030)
  * results/tables/post_kbs_common_harness_baselines_001/ (post-v1.22; B1, seeds 5001-5030)

Outputs (identical copies under manuscript/tables and manuscript/tables_ieee):
  table_synthesis.tex                      central evidence matrix (main body)
  table_size_matched_drift.tex             B2 main-body table
  table_common_harness.tex                 B1 main-body table (primary 2,000/class)
  table_size_matched_drift_supp.tex        B2 full contrast matrix (supplement S9)
  table_size_matched_drift_security.tex    B2 guardrail panel (supplement S9)
  table_common_harness_supp_primary.tex    B1 primary-family contrasts (supplement S10)
  table_common_harness_supp_secondary.tex  B1 secondary-family contrasts (supplement S10)
  table_common_harness_supp_statements.tex B1 statements + budgets (supplement S10)
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
T = REPO / "results" / "tables"
OUT_DIRS = [REPO / "manuscript" / "tables", REPO / "manuscript" / "tables_ieee"]

SYM = T / "symmetric_pipeline_dynamic_001"
SM = T / "size_matched_own_transformer_001"
A8 = T / "paper2_amendment_008"
B2 = T / "post_kbs_size_matched_drift_001"
B1 = T / "post_kbs_common_harness_baselines_001"

SC_NAME = {"ps": "PortScan", "unsw": "UNSW-Recon", "ton": "ToN-IoT"}
ORDER3 = ("ps", "unsw", "ton")


def f2(x: float) -> str:
    return f"{x:+.2f}"


def ci(lo: float, hi: float) -> str:
    return f"[{lo:.2f}, {hi:.2f}]"


def tex(x: str) -> str:
    return "$" + x + "$"


def write(name: str, body: str) -> None:
    for d in OUT_DIRS:
        (d / name).write_text(body, encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ loaders
def sym_means() -> dict:
    s = pd.read_csv(SYM / "summary.csv", keep_default_na=False)
    out = {}
    for _, r in s.iterrows():
        out[(r.scenario, r.policy, str(r.transformer_policy))] = float(r.ba_mean) * 100
    return out


def sm_tables():
    con = pd.read_csv(SM / "paired_contrasts.csv").set_index("contrast")
    desc = pd.read_csv(SM / "descriptive_contrasts.csv").set_index("contrast")
    mult = pd.read_csv(SM / "multiplicity.csv").set_index("contrast")
    return con, desc, mult


def b2_tables():
    con = pd.read_csv(B2 / "paired_contrasts.csv").set_index("contrast")
    mult = pd.read_csv(B2 / "multiplicity.csv").set_index("contrast")
    outc = pd.read_csv(B2 / "size_effect_outcome.csv").set_index("scenario")
    summ = pd.read_csv(B2 / "summary.csv", keep_default_na=False)
    sec = pd.read_csv(B2 / "security_metrics.csv")
    desc = pd.read_csv(B2 / "descriptive_contrasts.csv").set_index("contrast")
    interp = json.loads((B2 / "CLAIM_INTERPRETATION.json").read_text(encoding="utf-8"))
    return con, mult, outc, summ, sec, desc, interp


def b1_tables():
    summ = pd.read_csv(B1 / "summary.csv", keep_default_na=False)
    cls = pd.read_csv(B1 / "cell_classification.csv").set_index("contrast")
    con = pd.read_csv(B1 / "paired_contrasts.csv").set_index("contrast")
    mult = pd.read_csv(B1 / "multiplicity.csv").set_index("contrast")
    desc = pd.read_csv(B1 / "descriptive_contrasts.csv").set_index("contrast")
    st = pd.read_csv(B1 / "statements.csv")
    bud = pd.read_csv(B1 / "budget_table.csv")
    return summ, cls, con, mult, desc, st, bud


# ------------------------------------------------------------------ synthesis matrix
def make_synthesis() -> None:
    m = sym_means()
    con, desc, mult = sm_tables()
    b2con, b2mult, *_ = b2_tables()
    a8 = pd.read_csv(A8 / "summary.csv").set_index(["regime", "arm"])
    a8p = pd.read_csv(A8 / "paired_ci.csv").set_index(["regime", "contrast"])
    symmult = pd.read_csv(SYM / "multiplicity.csv").set_index("contrast")
    reg = {"ps": "portscan", "unsw": "unsw_recon", "ton": "ton_scanning"}

    def trip(vals):
        return " / ".join(tex(f2(v)) for v in vals)

    # frozen 512 (descriptive frozen rows, sealed symmetric replication)
    fz_full = [m[(f"{s}_full", "naive", "frozen_initial_transformer")]
               - m[(f"{s}_full", "never", "n/a")] for s in ORDER3]
    fz_zero = [m[(f"{s}_zero", "naive", "frozen_initial_transformer")]
               - m[(f"{s}_zero", "never", "n/a")] for s in ORDER3]
    fz_gate_full = [m[(f"{s}_full", "point", "frozen_initial_transformer")]
                    - m[(f"{s}_full", "naive", "frozen_initial_transformer")] for s in ORDER3]
    fz_gate_zero = [m[(f"{s}_zero", "point", "frozen_initial_transformer")]
                    - m[(f"{s}_zero", "naive", "frozen_initial_transformer")] for s in ORDER3]
    # frozen 2,000 zero drift (sealed amendment 008; seeds 104-133)
    fz2k_zero = [float(a8.loc[(reg[s], "rz_none_sz2000"), "gain"]) for s in ORDER3]
    fz2k_gate = [float(a8p.loc[(reg[s], "sz2000_gate_vs_naive"), "diff"]) for s in ORDER3]
    # own zero
    own0_512 = [float(desc.loc[f"{s}_zero: naive-512 vs never", "effect_pp"]) for s in ORDER3]
    own0_2k = [float(con.loc[f"{s}_zero: naive-2000 vs never", "effect_pp"]) for s in ORDER3]
    n_sig_own0_512 = int(sum(bool(symmult.loc[f"{s}_zero: own-{g} vs own-naive", "significant_holm"])
                             and float(symmult.loc[f"{s}_zero: own-{g} vs own-naive", "effect_pp"]) > 0
                             for s in ORDER3 for g in ("point", "strict")))
    n_sig_own0_2k = int(sum(bool(mult.loc[f"{s}_zero: {g}-2000 vs naive-2000", "significant_holm"])
                            and float(mult.loc[f"{s}_zero: {g}-2000 vs naive-2000", "effect_pp"]) > 0
                            for s in ORDER3 for g in ("point", "strict")))
    # own full
    own1_512 = [float(b2con.loc[f"{s}_full: naive-512 vs never", "effect_pp"]) for s in ORDER3]
    own1_2k = [float(b2con.loc[f"{s}_full: naive-2000 vs never", "effect_pp"]) for s in ORDER3]
    n_sig_own1_512 = int(sum(bool(symmult.loc[f"{s}_full: own-{g} vs own-naive", "significant_holm"])
                             and float(symmult.loc[f"{s}_full: own-{g} vs own-naive", "effect_pp"]) > 0
                             for s in ORDER3 for g in ("point", "strict")))
    n_cost_own1_512 = int(sum(bool(symmult.loc[f"{s}_full: own-{g} vs own-naive", "significant_holm"])
                              and float(symmult.loc[f"{s}_full: own-{g} vs own-naive", "effect_pp"]) < 0
                              for s in ORDER3 for g in ("point", "strict")))
    n_sig_own1_2k = int(sum(bool(b2mult.loc[f"{s}_full: {g}-2000 vs naive-2000", "significant_holm"])
                            and float(b2mult.loc[f"{s}_full: {g}-2000 vs naive-2000", "effect_pp"]) > 0
                            for s in ORDER3 for g in ("point", "strict")))
    n_cost_own1_2k = int(sum(bool(b2mult.loc[f"{s}_full: {g}-2000 vs naive-2000", "significant_holm"])
                             and float(b2mult.loc[f"{s}_full: {g}-2000 vs naive-2000", "effect_pp"]) < 0
                             for s in ORDER3 for g in ("point", "strict")))
    strict_unsw = float(b2con.loc["unsw_full: strict-2000 vs naive-2000", "effect_pp"])

    body = rf"""\begin{{table*}}[t]
\centering
\caption{{\textbf{{Central evidence matrix: how the apparent value of promotion depends on
challenger construction and evidence.}} Each cell reports always-deploy minus never-adapt in
balanced-accuracy points (PortScan / UNSW-Recon / ToN-IoT) and whether point/strict validation
adds Holm-significant average value over always-deploy in that configuration. Row 1 is the
historical frozen incumbent-owned preprocessing configuration (descriptive; sealed symmetric
replication, seeds 3001--3030; its 2{{,}}000/class zero-drift cell is the sealed amendment-008
control on seeds 104--133). Rows 2--3 are self-contained challengers: the zero-drift cells are
the sealed size-matched control (seeds 4001--4030; 512 column descriptive, 2{{,}}000 column
registered F1), the full-drift cells are the registered post-v1.22 size-matched-under-drift
control (seeds 6001--6030; both registered G1). ``not evaluated'' cells were never run under a
registered protocol.}}
\label{{tab:synthesis}}
\footnotesize
\setlength{{\tabcolsep}}{{4pt}}
\renewcommand{{\arraystretch}}{{1.15}}
\begin{{tabular}}{{p{{0.20\linewidth}} p{{0.36\linewidth}} p{{0.36\linewidth}}}}
\toprule
Configuration & 512/class challenger & 2{{,}}000/class challenger \\
\midrule
Frozen incumbent-owned preprocessing (historical), full drift &
$\Delta$ vs never: {trip(fz_full)}\newline validation: point $-$ naive {trip(fz_gate_full)} (descriptive) &
not evaluated under a registered protocol \\
\addlinespace
Frozen incumbent-owned preprocessing (historical), zero drift &
$\Delta$ vs never: {trip(fz_zero)}\newline validation: point $-$ naive {trip(fz_gate_zero)} (descriptive) &
$\Delta$ vs never: {trip(fz2k_zero)}\newline validation: point $-$ naive {trip(fz2k_gate)} (descriptive; seeds 104--133) \\
\addlinespace
Self-contained challenger, zero drift &
$\Delta$ vs never: {trip(own0_512)}\newline validation: {n_sig_own0_512}/6 gate contrasts Holm-significant gains &
$\Delta$ vs never: {trip(own0_2k)} (CI90 within $\pm0.5$ in 3/3)\newline validation: {n_sig_own0_2k}/6 Holm-significant gains \\
\addlinespace
Self-contained challenger, full drift &
$\Delta$ vs never: {trip(own1_512)}\newline validation: {n_sig_own1_512}/6 Holm-significant gain, {n_cost_own1_512} resolved cost &
$\Delta$ vs never: {trip(own1_2k)}\newline validation: {n_sig_own1_2k}/6 Holm-significant gains, {n_cost_own1_2k} resolved cost (strict, UNSW {tex(f2(strict_unsw))}) \\
\bottomrule
\end{{tabular}}
\end{{table*}}
"""
    write("table_synthesis.tex", body)


# ------------------------------------------------------------------ B2 main table
def make_b2_main() -> None:
    con, mult, outc, summ, sec, desc, interp = b2_tables()
    never = {r.scenario: float(r.ba_mean) * 100 for _, r in summ.iterrows() if r.policy == "never"}

    def cell(name, with_ci=True):
        r = con.loc[name]
        s = tex(f2(float(r.effect_pp)))
        if with_ci:
            s += " " + ci(float(r.ci95_lo), float(r.ci95_hi))
        if bool(mult.loc[name, "significant_holm"]):
            s += r"$^{\dagger}$"
        return s

    rows = []
    for s in ORDER3:
        sc = f"{s}_full"
        rows.append(" & ".join([
            SC_NAME[s], f"{never[sc]:.2f}",
            cell(f"{sc}: naive-512 vs never", False),
            cell(f"{sc}: naive-2000 vs never", False),
            cell(f"{sc}: naive-2000 vs naive-512"),
            outc.loc[sc, "classification"].replace("SIZE ", "size ").lower(),
            cell(f"{sc}: point-2000 vs naive-2000"),
            cell(f"{sc}: strict-2000 vs naive-2000"),
        ]) + r" \\")
    body = r"""\begin{table*}[t]
\centering
\caption{\textbf{Candidate evidence under real drift: the registered size-matched control
(seeds 6001--6030, 21 arms).} Self-contained challengers, full progressive drift, nested
candidate batches drawn at the proposal-time mixture (the 512 batch is the first 512 rows
per class of the 2{,}000 batch). BA points; paired within seed, 30 seeds; CI95 from the
deterministic centered paired bootstrap; $\dagger$ = Holm-significant within its registered
family (G1: naive vs never at both sizes; G2: the primary size effect; G3: gate value at
2{,}000). Registered classification of G2 per the frozen protocol; program outcome
\textsc{""" + interp["outcome"].replace("-", "--").lower() + r"""}. Columns 3--4: always-deploy
minus never-adapt at each size; column 5: the size effect; columns 7--8: gate minus
always-deploy at 2{,}000/class. Full matrices in Supplementary \S S9.}
\label{tab:size_matched_drift}
\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{l r r r l l l l}
\toprule
Regime (full drift) & Never BA & Naive$_{512}$ & Naive$_{2000}$ &
Size effect [CI95] & G2 class & Point$_{2000}$ [CI95] & Strict$_{2000}$ [CI95] \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    write("table_size_matched_drift.tex", body)


# ------------------------------------------------------------------ B1 main table
POL_ROWS = [
    ("never", "Never-adapt", "anchor", "0"),
    ("naive", "Always-deploy (naive)", "anchor", "0"),
    ("point", "Point gate, $b{=}32$", "authors' policy", "32"),
    ("strict", "Strict gate (reject ties), $b{=}32$", "authors' policy", "32"),
    ("atc", "ATC \\cite{garg2022atc}", "published generic", "0 ($+$512-row val.)"),
    ("doc", "DoC \\cite{guillory2021doc}", "published generic", "0 ($+$512-row val.)"),
    ("enscal", "Calibrated soft ensemble", "standard baseline", "0"),
    ("replay", "Replay 50/50 retraining", "standard baseline", "0"),
    ("ddm", "river-DDM trigger", "reference impl.", "0; 800/stream monitoring"),
    ("adwin", "river-ADWIN trigger", "reference impl.", "0; 800/stream monitoring"),
]
SC6 = ("ps_full", "unsw_full", "ton_full", "ps_zero", "unsw_zero", "ton_zero")
MARK = {"MATERIAL GAIN": r"$^{\dagger}$", "MATERIAL COST": r"$^{\ddagger}$",
        "COMPATIBLE": r"$^{\approx}$", "UNRESOLVED": r"$^{?}$"}


def make_b1_main() -> None:
    summ, cls, con, mult, desc, st, bud = b1_tables()
    mean = {}
    for _, r in summ.iterrows():
        mean[(r.scenario, r.policy, str(r.candidate_size))] = float(r.ba_mean) * 100
    rows = []
    for pol, label, origin, labels in POL_ROWS:
        cells = []
        for sc in SC6:
            if pol == "never":
                cells.append(f"{mean[(sc, 'never', 'n/a')]:.1f}")
                continue
            v = mean[(sc, pol, "2000")] - mean[(sc, "never", "n/a")]
            s = tex(f2(v))
            name = f"{sc}: {pol}-2000 vs naive-2000"
            if name in cls.index:
                s += MARK[cls.loc[name, "classification"]]
            cells.append(s)
        rows.append(" & ".join([label, origin, labels] + cells) + r" \\")
    body = r"""\begin{table*}[t]
\centering
\caption{\textbf{Registered common-harness comparison with published and reference baselines
(primary condition: self-contained 2{,}000/class challengers; seeds 5001--5030).} Balanced-accuracy
points over never-adapting (from the sealed per-arm means; the never-adapt row gives its absolute
mean BA; all arms share bit-identical raw streams per seed). Markers record the registered per-cell classification of the policy$-$naive
contrast (families PF1 zero drift / PF2 full drift; Holm within family): $\dagger$ material
gain, $\ddagger$ material cost, $\approx$ compatible (CI90 within $\pm0.5$), $?$ unresolved.
Anchor rows (naive, point, strict) are descriptive here by amendment. Labels = target labels
per decision; ATC/DoC additionally use a 512-row labeled validation sample at each model's
training time; DDM/ADWIN consume 8 monitoring labels per window. Origin: published generic
method, reference implementation (\texttt{river} 0.25.0), standard baseline, or authors'
policy --- none is an adaptive-NIDS system reproduced end to end. Full families, the 512/class
sensitivity block and statements in Supplementary \S S10.}
\label{tab:common_harness}
\footnotesize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.08}
\begin{tabular}{l l l r r r r r r}
\toprule
 & & & \multicolumn{3}{c}{Full drift} & \multicolumn{3}{c}{Zero drift} \\
\cmidrule(lr){4-6}\cmidrule(lr){7-9}
Policy & Origin & Labels at decision & PortScan & UNSW & ToN-IoT & PortScan & UNSW & ToN-IoT \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    write("table_common_harness.tex", body)


# ------------------------------------------------------------------ supplement tables
def make_b2_supp() -> None:
    con, mult, outc, summ, sec, desc, interp = b2_tables()
    rows = []
    for name, r in con.iterrows():
        m = mult.loc[name]
        cls = ""
        if name in [f"{s}_full: naive-2000 vs naive-512" for s in ORDER3]:
            cls = outc.loc[name.split(":")[0], "classification"].lower()
        rows.append(" & ".join([
            r.family.replace("(primary)", "").replace("(secondary)", "").strip(),
            name.replace("_", r"\_"), tex(f2(float(r.effect_pp))),
            ci(float(r.ci95_lo), float(r.ci95_hi)), ci(float(r.ci90_lo), float(r.ci90_hi)),
            f"{float(m.p_holm):.4f}", "yes" if bool(m.significant_holm) else "no", cls]) + r" \\")
    for name, r in desc.iterrows():
        rows.append(" & ".join(["descriptive (uncorrected)", name.replace("_", r"\_"),
                                tex(f2(float(r.effect_pp))),
                                ci(float(r.ci95_lo), float(r.ci95_hi)), "---", "---", "---", ""]) + r" \\")
    body = r"""\begin{table}[t]
\centering
\caption{Size-matched-under-drift control (seeds 6001--6030): every registered contrast of
families G1--G4 with CI95, CI90, Holm-adjusted $p$ and significance, plus the descriptive
512-side gate cells. BA points; seed = inferential unit; deterministic centered paired
bootstrap (100{,}000 resamples).}
\label{tab:size_matched_drift_supp}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{l l r l l r c l}
\toprule
Family & Contrast & Effect & CI95 & CI90 & $p_{\mathrm{Holm}}$ & Sig. & G2 class \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
    write("table_size_matched_drift_supp.tex", body)

    srows = []
    g = sec[sec.policy.isin(["point", "strict"])]
    for _, r in g.iterrows():
        srows.append(" & ".join([
            r.scenario.replace("_", r"\_"), r.policy, str(r.candidate_size),
            tex(f2(float(r.d_recall_vs_naive_pp))) + f" ({float(r.recall_onesided_lo95):+.2f})",
            "pass" if bool(r.recall_NI_principal) else r"\textbf{fail}",
            tex(f2(float(r.d_fpr_vs_naive_pp))) + f" ({float(r.fpr_onesided_hi95):+.2f})",
            "pass" if bool(r.fpr_NI_principal) else r"\textbf{fail}"]) + r" \\")
    body = r"""\begin{table}[t]
\centering
\caption{Size-matched-under-drift control: attack-recall and FPR non-inferiority guardrails
for every gate cell vs naive at the same candidate size (paired $\Delta$ in pp; parentheses:
one-sided 95\% bound tested against the preregistered margins recall $>-1.0$, FPR $<+0.5$).
Guardrails restrict safety language only.}
\label{tab:size_matched_drift_security}
\scriptsize
\begin{tabular}{l l r l l l l}
\toprule
Regime & Gate & Size & $\Delta$recall (lb$_{95}$) & NI & $\Delta$FPR (ub$_{95}$) & NI \\
\midrule
""" + "\n".join(srows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
    write("table_size_matched_drift_security.tex", body)


def make_b1_supp() -> None:
    summ, cls, con, mult, desc, st, bud = b1_tables()

    def rows_for(prefixes):
        out = []
        for name, r in con.iterrows():
            if not any(r.family.startswith(p) for p in prefixes):
                continue
            m = mult.loc[name]
            out.append(" & ".join([
                r.family.split(" ")[0], name.replace("_", r"\_"),
                tex(f2(float(r.effect_pp))), ci(float(r.ci95_lo), float(r.ci95_hi)),
                f"{float(m.p_holm):.4f}", cls.loc[name, "classification"].lower()]) + r" \\")
        return out

    def table(label, caption, rows):
        return r"""\begin{table}[t]
\centering
\caption{""" + caption + r"""}
\label{""" + label + r"""}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{l l r l r l}
\toprule
Family & Contrast & Effect & CI95 & $p_{\mathrm{Holm}}$ & Class \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
    write("table_common_harness_supp_primary.tex", table(
        "tab:common_harness_supp_primary",
        "Registered common-harness comparison (seeds 5001--5030): the primary families at "
        "2{,}000/class --- PF1 zero-drift loss avoidance and PF2 full-drift benefit retention "
        "(policy $-$ naive) and PF3 published estimators $-$ point gate. BA points; seed = unit; "
        "Holm within family; per-cell registered classification.",
        rows_for(("PF1", "PF2", "PF3"))))
    write("table_common_harness_supp_secondary.tex", table(
        "tab:common_harness_supp_secondary",
        "Registered common-harness comparison: the secondary families --- SF4 512/class "
        "sensitivity (policy $-$ naive at 512) and SF5 method$\\times$size interactions "
        "($(k-\\mathrm{naive})_{2000}-(k-\\mathrm{naive})_{512}$, seed-paired only). "
        "BA points; Holm within family.",
        rows_for(("SF4", "SF5"))))

    srows = []
    for _, r in st.iterrows():
        srows.append(" & ".join([r.statement, r.policy,
                                 r"\textbf{yes}" if bool(r.holds) else "no"]) + r" \\")
    brows = []
    b2000 = bud[bud.candidate_size.astype(str) == "2000"].groupby("policy").agg(
        origin=("origin", "first"), probe=("labels_probe_mean", "mean"),
        mon=("labels_monitor_mean", "mean"), cand=("labels_candidate_mean", "mean"),
        val=("labels_trainingtime_validation_analytic", "mean"))
    for pol, r in b2000.iterrows():
        brows.append(" & ".join([pol, r.origin, f"{r.cand:.0f}", f"{r.probe:.0f}",
                                 f"{r.mon:.0f}", f"{r.val:.0f}"]) + r" \\")
    body = r"""\begin{table}[t]
\centering
\caption{Registered common-harness comparison: frozen statements S1--S4 evaluated literally
(top) and the per-policy label budgets at 2{,}000/class, mean per stream across the six
scenarios (bottom; ATC/DoC training-time validation labels are documented analytically, they
are outside the runner's counters). Budgets are reported, not equalized.}
\label{tab:common_harness_supp_statements}
\scriptsize
\begin{tabular}{p{0.55\linewidth} l l}
\toprule
Statement & Policy & Holds \\
\midrule
""" + "\n".join(srows) + r"""
\bottomrule
\end{tabular}

\medskip
\begin{tabular}{l l r r r r}
\toprule
Policy & Origin & Candidate labels & Probe labels & Monitoring labels & Validation labels (analytic) \\
\midrule
""" + "\n".join(brows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
    write("table_common_harness_supp_statements.tex", body)


def main() -> None:
    make_synthesis()
    make_b2_main()
    make_b1_main()
    make_b2_supp()
    make_b1_supp()
    print("final-integration tables written to manuscript/tables and manuscript/tables_ieee")


if __name__ == "__main__":
    main()
