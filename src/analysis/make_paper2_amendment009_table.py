"""Emit manuscript/tables/table_amendment009.tex from the amendment-009 summary.csv.

Two panels, both under ZERO drift (random triggers, no drift at all):
  A. the replacement harm across downstream models (full-replacement) + no-PCA,
  B. across update generators (SVC-RBF),
each as naive gain / McNemar-gate gain vs no-adaptation (BA points, 30 seeds).
"""
import os
import pandas as pd

SRC = "results/tables/paper2_amendment_009/summary.csv"
OUT = "manuscript/tables/table_amendment009.tex"
REGS = ["portscan", "unsw_recon", "ton_scanning"]


def g(df, block, family, arm):
    r = df[(df.block == block) & (df.family == family) & (df.drift == "zero") & (df.arm == arm)]
    out = {}
    for reg in REGS:
        rr = r[r.regime == reg]
        out[reg] = f"{rr.iloc[0].gain:+.2f}" if len(rr) else "--"
    return out


def fmt_naive(v):
    return f"$-${v[1:]}" if v.startswith("-") else v


def row(df, block, family, label):
    n = g(df, block, family, "naive")
    gate_arm = "mcnemar"
    gate = g(df, block, family, gate_arm)
    cells = []
    for reg in REGS:
        cells.append(fmt_naive(n[reg]))
        cells.append(fmt_naive(gate[reg]))
    return f"{label} & " + " & ".join(cells) + r" \\"


def main():
    df = pd.read_csv(SRC)
    L = []
    L.append(r"\begin{table*}[t]")
    L.append(r"\centering")
    L.append(r"\caption{\textbf{The zero-drift replacement harm generalizes across downstream "
             r"models and update generators (amendment 009).} Mean gain of naive always-deploy "
             r"vs.\ never-adapting, and of the risk-controlled (exact-McNemar) gate, under "
             r"\emph{zero drift} (drift-independent random triggers, no distribution change), "
             r"balanced-accuracy points, 30 seeds. Naive is net-harmful in every downstream model "
             r"and in every update generator except the calibrated ensemble on PortScan (which "
             r"happens to help, $+0.84$; the risk-averse gate forgoes that gain). The McNemar gate "
             r"recovers essentially all of the loss ($+0.00$) by committing only on statistically "
             r"resolved superiority. The cumulative candidate (trained on \emph{all} observed "
             r"windows) is the most harmful generator, so the harm is not a small-sample effect "
             r"that more data removes.}")
    L.append(r"\label{tab:amendment009}")
    L.append(r"__RESIZE_OPEN__")
    L.append(r"\begin{tabular}{l cc cc cc}")
    L.append(r"\toprule")
    L.append(r" & \multicolumn{2}{c}{PortScan} & \multicolumn{2}{c}{UNSW-Recon} "
             r"& \multicolumn{2}{c}{ToN-IoT} \\")
    L.append(r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}")
    L.append(r"Downstream model / generator & naive & gate & naive & gate & naive & gate \\")
    L.append(r"\midrule")
    L.append(r"\multicolumn{7}{l}{\emph{Downstream models (full replacement)}} \\")
    for fam, lab in [("RF", "Random forest"), ("LogReg", "Logistic regression"),
                     ("MLP", "MLP"), ("SVC-fulldim", "SVC-RBF, full features (no PCA)")]:
        L.append(row(df, "models", fam, lab))
    L.append(r"\addlinespace")
    L.append(r"\multicolumn{7}{l}{\emph{Update generators (SVC-RBF)}} \\")
    for fam, lab in [("ensemble-cal", "Calibrated ensemble"), ("sliding", "Sliding window"),
                     ("cumulative", "Cumulative (all observed data)"), ("replay", "Replay 50/50")]:
        L.append(row(df, "generators", fam, lab))
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}")
    L.append(r"__RESIZE_CLOSE__")
    L.append(r"\end{table*}")
    body = "\n".join(L)
    # CAS: \small (single-column class, table fits). IEEE: resizebox to \textwidth.
    cas = body.replace("__RESIZE_OPEN__", r"\small").replace("__RESIZE_CLOSE__", "")
    ieee = (body.replace("__RESIZE_OPEN__",
                         r"\resizebox{\ifdim\width>\textwidth \textwidth\else\width\fi}{!}{%")
                .replace("__RESIZE_CLOSE__", "}"))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    os.makedirs("manuscript/tables_ieee", exist_ok=True)
    with open(OUT, "w") as f:
        f.write(cas + "\n")
    with open("manuscript/tables_ieee/table_amendment009.tex", "w") as f:
        f.write(ieee + "\n")
    print(f"wrote {OUT} and manuscript/tables_ieee/table_amendment009.tex")


if __name__ == "__main__":
    main()
