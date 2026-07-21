"""final-kbs table emitters:
  - table_causal_probe.tex  <- unified window-64 causal matrix (naive/point/strict), from
    results/tables/paper2_final_kbs/summary.csv (block=causal64);
  - table_symmetric_ab.tex  <- 4-condition mechanism control, from symmetric_ab.csv.
Both emitted for tables/ (CAS) and tables_ieee/.
"""
import os
import pandas as pd

FK = "results/tables/paper2_final_kbs"
LBL = {"portscan": "PortScan (benefit)", "unsw_recon": "UNSW Recon (marginal)",
       "ton_scanning": "ToN-IoT (harm)"}
COND = {"independent": "independent (fit on T)", "incumbent_fit": "fit on incumbent",
        "challenger_fit": "fit on challenger", "own_transformer": "own transformer each"}


def fmt(v, lo, hi):
    def s(x):
        return f"$-${abs(x):.2f}" if x < 0 else f"$+${x:.2f}"
    return f"{s(v)} [{lo:.2f}, {hi:.2f}]".replace("[-", "[$-$").replace(", -", ", $-$")


def dual(body, name):
    with open(f"manuscript/tables/{name}", "w") as f:
        f.write(body)
    ieee = (body.replace(r"\begin{table}", r"\begin{table*}[t]")
                .replace(r"\end{table}", r"\end{table*}")
                .replace(r"\linewidth \linewidth", r"\textwidth \textwidth"))
    with open(f"manuscript/tables_ieee/{name}", "w") as f:
        f.write(ieee)


def causal_table():
    df = pd.read_csv(f"{FK}/summary.csv")
    c = df[df.block == "causal64"]

    def cell(reg, drift, arm):
        r = c[(c.regime == reg) & (c.drift == drift) & (c.arm == arm)].iloc[0]
        return fmt(r.gain, r.lo, r.hi)

    L = [r"\begin{table}", r"\centering"]
    L.append(r"\caption{\textbf{Final leakage-free observed-data policy-evaluation arm --- "
             r"unified matrix (final-kbs protocol).} All three datasets at 64-flow windows (the largest "
             r"size UNSW's attack pool supports without replacement; a 128-flow sensitivity for "
             r"PortScan/ToN-IoT appears in the amendment notes with the same conclusions). Stream "
             r"drawn without replacement from globally value-deduplicated pools --- "
             r"candidate/future-evaluation collisions \emph{exactly zero} in every cell; no probe "
             r"$\Rightarrow$ reject (zero unvalidated commits); observed threshold recomputed only "
             r"at $\ge$30 score-windows. Policies: naive always-deploy, the point gate "
             r"($\ge$, $b{=}32$) and the strict reject-ties gate ($>$). Balanced-accuracy points "
             r"vs.\ never adapting, 30 seeds, 95\% bootstrap CIs.}")
    L.append(r"\label{tab:causal_probe}")
    L.append(r"\resizebox{\ifdim\width>\linewidth \linewidth\else\width\fi}{!}{%")
    L.append(r"\begin{tabular}{llrrr}")
    L.append(r"\toprule")
    L.append(r"Regime & Drift & Naive & Point gate ($\ge$) & Strict gate ($>$) \\")
    L.append(r"\midrule")
    for reg in ("portscan", "unsw_recon", "ton_scanning"):
        for drift in ("full", "mild"):
            L.append(f"{LBL[reg]} & {drift} & {cell(reg, drift, 'none')} & "
                     f"{cell(reg, drift, 'lp32')} & {cell(reg, drift, 'strict')} \\\\")
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}}")
    L.append(r"\end{table}")
    dual("\n".join(L) + "\n", "table_causal_probe.tex")
    print("causal table written")


def ab_table():
    d = pd.read_csv(f"{FK}/symmetric_ab.csv")
    d = d[d.contrast == "rand"]
    L = [r"\begin{table}", r"\centering"]
    L.append(r"\caption{\textbf{The zero-drift mechanism, identified: the symmetric A/B control "
             r"(final-kbs).} Two equal-size models on disjoint (globally value-deduplicated, "
             r"no-replacement) samples of the same distribution; incumbent role randomized per "
             r"seed; gap = BA(challenger) $-$ BA(incumbent) on a disjoint evaluation block, 30 "
             r"seeds, 95\% CIs. For the fragile SVC-RBF in the harm-regime dataset the effect "
             r"satisfies all four identification criteria: $\approx$0 under an independent "
             r"transformer, systematic incumbent advantage when the transformer is fit on the "
             r"incumbent, \emph{inversion} when fit on the challenger, and \emph{elimination} "
             r"when each model brings its own transformer. Random forest shows no effect "
             r"anywhere: the mechanism is learner-specific.}")
    L.append(r"\label{tab:symmetric_ab}")
    L.append(r"\resizebox{\ifdim\width>\linewidth \linewidth\else\width\fi}{!}{%")
    L.append(r"\begin{tabular}{llrrrr}")
    L.append(r"\toprule")
    L.append(r" & & \multicolumn{4}{c}{Transformer condition} \\")
    L.append(r"\cmidrule(lr){3-6}")
    L.append(r"Dataset & Model & independent & fit incumbent & fit challenger & own each \\")
    L.append(r"\midrule")
    for reg in ("portscan", "unsw_recon", "ton_scanning"):
        for mt in ("svc_rbf", "random_forest"):
            cells = []
            for cond in ("independent", "incumbent_fit", "challenger_fit", "own_transformer"):
                r = d[(d.dataset == reg) & (d.model == mt) & (d.condition == cond)].iloc[0]
                cells.append(fmt(r.gap, r.lo, r.hi))
            mtl = "SVC-RBF" if mt == "svc_rbf" else "RF"
            L.append(f"{LBL[reg]} & {mtl} & " + " & ".join(cells) + r" \\")
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}}")
    L.append(r"\end{table}")
    dual("\n".join(L) + "\n", "table_symmetric_ab.tex")
    print("A/B table written")


if __name__ == "__main__":
    os.makedirs("manuscript/tables_ieee", exist_ok=True)
    causal_table()
    ab_table()
