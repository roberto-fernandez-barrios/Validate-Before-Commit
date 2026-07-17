"""Emit the FINAL causal table (Table 8 replacement, amendment 013) from
results/tables/paper2_amendment_013/summary.csv (block=causal_final).

Replaces tables/table_causal_probe.tex (+ tables_ieee/) with the leakage-free stream
(global value-dedup, without replacement, collisions exactly 0), no-probe->reject
(0 unvalidated commits) and min-calib-30 recalibration. The superseded leaky numbers
live in the amendment notes, not in the paper's main table.
"""
import os
import pandas as pd

SRC = "results/tables/paper2_amendment_013/summary.csv"
LBL = {"portscan": "PortScan (benefit)", "unsw_recon": "UNSW Recon (marginal)",
       "ton_scanning": "ToN-IoT (harm)"}


def fmt(v, lo, hi):
    def s(x):
        return f"$-${abs(x):.2f}" if x < 0 else f"$+${x:.2f}"
    return f"{s(v)} [{lo:.2f}, {hi:.2f}]".replace("[-", "[$-$").replace(", -", ", $-$")


def main():
    df = pd.read_csv(SRC)
    cf = df[df.block == "causal_final"]

    def row(reg, drift):
        n = cf[(cf.regime == reg) & (cf.drift == drift) & (cf.arm == "naive")].iloc[0]
        g = cf[(cf.regime == reg) & (cf.drift == drift) & (cf.arm == "gate")].iloc[0]
        return (f"{LBL[reg]} & {fmt(n.gain, n.lo, n.hi)} & {fmt(g.gain, g.lo, g.hi)} & "
                f"{fmt(g.gate_vs_naive, g.gvn_lo, g.gvn_hi)} \\\\")

    L = []
    L.append(r"\begin{table}")
    L.append(r"\centering")
    L.append(r"\caption{\textbf{The gate does not need the simulator --- final leakage-free "
             r"causal arm (Algorithm 1B, amendments 011--013).} Candidate = last eight "
             r"\emph{observed} windows; probe = 32 observed rows ($t{-}9$), row-identity disjoint "
             r"from training; detector recalibrated from observed windows only (threshold updated "
             r"only once $\ge$30 observed score-windows exist; the result is insensitive to this "
             r"minimum, \S\ref{sec:v2}). The stream draws every window \emph{without replacement} "
             r"from a globally value-deduplicated pool, so no identical feature vector appears in "
             r"more than one window: audited candidate-training/future-evaluation collisions are "
             r"\emph{exactly zero}. When no observed probe exists yet (early triggers, 0.6--1.0 "
             r"per stream) the gate \emph{rejects} --- zero unvalidated commits, so the "
             r"\S\ref{sec:riskgates} guarantee scope covers every committed update. Pool-size "
             r"feasibility, surfaced by the abort-on-exhaustion assertion, requires a larger "
             r"window-partition share for the no-replacement stream (0.75; UNSW 0.9) and, for "
             r"UNSW at full drift, 64-flow windows (its attack pool holds 2{,}664 unique rows, "
             r"fewer than the ${\sim}3{,}900$ that 128-flow windows would consume) --- naive and "
             r"gate share the identical stream in every cell, so all contrasts remain paired. "
             r"Earlier "
             r"versions of this arm (amendments 006--008; pool-sampled recalibration, then "
             r"residual train/future-eval overlap) are superseded and retained only in the "
             r"registered amendment notes. Balanced-accuracy points vs.\ never adapting, 30 "
             r"seeds, 95\% bootstrap CIs.}")
    L.append(r"\label{tab:causal_probe}")
    L.append(r"\resizebox{\ifdim\width>\linewidth \linewidth\else\width\fi}{!}{%")
    L.append(r"\begin{tabular}{lrrr}")
    L.append(r"\toprule")
    L.append(r"Regime & Naive (observed candidates) & Causal gate (1B) & Gate $-$ naive (paired) \\")
    L.append(r"\midrule")
    for reg in ("portscan", "unsw_recon", "ton_scanning"):
        L.append(row(reg, "full"))
    L.append(r"\midrule")
    L.append(r"\multicolumn{4}{l}{\emph{Mild drift ($\mathrm{sev}_{\max}{=}0.25$), same pipeline "
             r"--- both defenses in one leakage-free experiment:}} \\")
    for reg in ("portscan", "unsw_recon", "ton_scanning"):
        L.append(row(reg, "mild"))
    L.append(r"\bottomrule")
    L.append(r"\end{tabular}}")
    L.append(r"\end{table}")
    body = "\n".join(L) + "\n"
    with open("manuscript/tables/table_causal_probe.tex", "w") as f:
        f.write(body)
    ieee = body.replace(r"\begin{table}", r"\begin{table*}[t]") \
               .replace(r"\end{table}", r"\end{table*}") \
               .replace(r"\linewidth \linewidth", r"\textwidth \textwidth")
    os.makedirs("manuscript/tables_ieee", exist_ok=True)
    with open("manuscript/tables_ieee/table_causal_probe.tex", "w") as f:
        f.write(ieee)
    print("wrote table_causal_probe.tex (CAS + IEEE)")
    print(body)


if __name__ == "__main__":
    main()
