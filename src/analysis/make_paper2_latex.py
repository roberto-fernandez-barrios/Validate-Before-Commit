"""Convert the Markdown manuscript into a compilable Elsevier (elsarticle) LaTeX document.

Ports Abstract + sections 1-8 to LaTeX, preserving \\cite{} commands, converting Markdown
emphasis/headers/lists/code-fences and Unicode symbols to LaTeX, and injecting figure and table floats at
their first in-text mention. Writes manuscript/main.tex. Requires the sanitized tables in
manuscript/tables/ and the figures in docs/img/.
"""
from __future__ import annotations
import re

MD = "manuscript/paper2_manuscript_draft_002.md"
OUT = "manuscript/main.tex"

FIGS = {
    "1":  ("docs/img/fig1_regime_spectrum.png",
           "Readaptation value is regime-dependent and sometimes harmful: best detector-triggered gain over no-adaptation per dataset and attack regime."),
    "2":  ("docs/img/fig2_mechanism_law.png",
           "The benefit of adaptation tracks deployed-model degradation (SVC-RBF, $r=-0.89$)."),
    "2b": ("docs/img/fig2b_mechanism_law_pooled.png",
           "The degradation--benefit law pooled across four downstream classifiers ($r=-0.82$, bootstrap 95\\% CI)."),
    "3":  ("docs/img/fig3_oracle_regret.png",
           "Decision oracle-regret grows with the fraction of streams on which adapting hurts."),
    "4":  ("docs/img/fig4_phase2_gate.png",
           "The validate-before-commit gate preserves benefit and avoids harm, identically for a classical (KS-max) and a quantum (QK-ZZ) detector."),
    "5":  ("docs/img/fig5_label_budget_curve.png",
           "Label-efficiency frontier: gain over no-adaptation versus probe budget; a small probe suffices to avoid harm."),
    "6":  ("docs/img/fig6_downstream_generalization.png",
           "Generalization across four downstream classifiers: net-harm is specific to SVC-RBF; the gate is safe for all."),
    "7":  ("docs/img/fig7_label_latency.png",
           "Gate robustness to label latency: safe with validation labels up to 20 windows stale."),
    "8":  ("docs/img/fig8_probe_poison.png",
           "The gate fails safe under adversarial validation labels (up to 40\\% flipped)."),
}
TABS = {
    "1": "tables/table1_regime_taxonomy.tex", "2": "tables/table2_phase2_gate_summary.tex",
    "3": "tables/table3_phase2_paired_ci.tex", "4": "tables/table4_oracle_regret.tex",
    "5": "tables/table5_phase1_negative.tex", "6": "tables/table6_downstream_generalization.tex",
}
TAB_LABEL = {
    "1": "tab:table1_regime_taxonomy", "2": "tab:table2_phase2_gate_summary",
    "3": "tab:table3_phase2_paired_ci", "4": "tab:table4_oracle_regret",
    "5": "tab:table5_phase1_negative", "6": "tab:table6_downstream_generalization",
}
UNI = [("−", "$-$"), ("≈", "$\\approx$"), ("×", "$\\times$"), ("±", "$\\pm$"),
       ("≥", "$\\ge$"), ("≤", "$\\le$"), ("≠", "$\\neq$"), ("Δ", "$\\Delta$"),
       ("ε", "$\\varepsilon$"), ("λ", "$\\lambda$"), ("γ", "$\\gamma$"),
       ("η", "$\\eta$"), ("→", "$\\to$"), ("—", "---"), ("–", "--"),
       ("§", "\\S"), ("≫", "$\\gg$"), ("’", "'"), ("“", "``"), ("”", "''")]

placed_figs, placed_tabs = set(), set()


def inline(t):
    holds = []

    def hold(m):
        holds.append(m.group(0))
        return f"\x00{len(holds)-1}\x00"

    def hold_code(m):
        inner = m.group(1).replace("_", "\\_").replace("%", "\\%").replace("&", "\\&")
        holds.append("\\texttt{" + inner + "}")
        return f"\x00{len(holds)-1}\x00"

    t = re.sub(r"\$[^$]*\$", hold, t)
    t = re.sub(r"\\cite\{[^}]*\}", hold, t)
    t = re.sub(r"`([^`]*)`", hold_code, t)
    for a, b in [("&", "\\&"), ("%", "\\%"), ("#", "\\#")]:
        t = t.replace(a, b)
    for a, b in UNI:
        t = t.replace(a, b)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\\emph{\1}", t)
    t = re.sub(r"Figs?\.?~?\s*([0-9]+b?)", lambda m: f"Fig.~\\ref{{fig:{m.group(1)}}}" if m.group(1) in FIGS else f"Fig.~{m.group(1)}", t)
    t = re.sub(r"Table~?\s*([0-9]+)", lambda m: f"Table~\\ref{{{TAB_LABEL[m.group(1)]}}}" if m.group(1) in TAB_LABEL else f"Table~{m.group(1)}", t)
    for i, h in enumerate(holds):
        t = t.replace(f"\x00{i}\x00", h)
    return t


def fig_float(n):
    path, cap = FIGS[n]
    return (f"\n\\begin{{figure}}[t]\n\\centering\n\\includegraphics[width=\\linewidth]{{{path}}}\n"
            f"\\caption{{{cap}}}\n\\label{{fig:{n}}}\n\\end{{figure}}\n")


def floats_for(block):
    out = ""
    for n in dict.fromkeys(re.findall(r"Figs?\.?~?\s*([0-9]+b?)", block)):
        if n in FIGS and n not in placed_figs:
            placed_figs.add(n); out += fig_float(n)
    for n in dict.fromkeys(re.findall(r"Table~?\s*([0-9]+)", block)):
        if n in TABS and n not in placed_tabs:
            placed_tabs.add(n); out += f"\\input{{{TABS[n]}}}\n"
    return out


def convert_body(md):
    """Convert the section-1..8 body (a markdown string) to LaTeX."""
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):  # code fence -> verbatim (Algorithm 1)
            out.append("\\begin{verbatim}")
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                out.append(lines[i]); i += 1
            out.append("\\end{verbatim}")
            i += 1
            continue
        if ln.startswith("### "):
            title = re.sub(r"^###\s+\d[\w.]*\s*", "", ln).strip()
            out.append("\n\\subsection{" + inline(title) + "}")
            i += 1
            continue
        if ln.startswith("## "):
            title = re.sub(r"^##\s+\d[\w.]*\s*", "", ln).strip()
            out.append("\n\\section{" + inline(title) + "}")
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", ln):  # bullet list
            out.append("\\begin{itemize}")
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                item = re.sub(r"^\s*[-*]\s+", "", lines[i])
                out.append("  \\item " + inline(item))
                i += 1
            out.append("\\end{itemize}")
            continue
        if re.match(r"^\s*\d+\.\s+", ln):  # numbered list
            out.append("\\begin{enumerate}")
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                item = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                out.append("  \\item " + inline(item))
                i += 1
            out.append("\\end{enumerate}")
            continue
        if ln.strip() == "" or ln.strip() == "---":
            out.append("")
            i += 1
            continue
        # normal paragraph: inject floats for first mentions, then the text
        out.append(floats_for(ln).rstrip("\n"))
        out.append(inline(ln))
        i += 1
    return "\n".join(out)


def section(md, start, end):
    a = md.index(start)
    b = md.index(end, a)
    return md[a:b]


def main():
    md = open(MD, encoding="utf-8").read()
    abstract_md = section(md, "## Abstract", "## Contributions").split("\n", 2)[2].strip()
    abstract = inline(abstract_md.replace("\n", " "))
    body_md = section(md, "## 1. Introduction", "## Main tables")
    body = convert_body(body_md)

    doc = r"""\documentclass[preprint,11pt]{elsarticle}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\graphicspath{{../}}   % main.tex lives in manuscript/; figures are at repo-root docs/img/
\usepackage{booktabs}
\usepackage{amsmath,amssymb}
\usepackage{xcolor}
\usepackage[hidelinks]{hyperref}

\journal{Computers \& Security}

\begin{document}
\begin{frontmatter}

\title{Validate Before Commit: Label-Efficient Safe Readaptation for\\
Adaptive Network Intrusion Detection under Concept Drift}

\author[a]{Roberto Fern\'andez Barrios\corref{cor}}
\ead{roberto.fernandez.barrios@gmail.com}
\cortext[cor]{Corresponding author.}
% \author[a]{Co-Author Name}
\affiliation[a]{organization={TODO: Affiliation}, country={TODO}}

\begin{abstract}
""" + abstract + r"""
\end{abstract}

% Highlights are submitted as a separate file (see manuscript/highlights.md).

\begin{keyword}
adaptive intrusion detection \sep concept drift \sep safe model updating \sep
label-efficient learning \sep retraining policy \sep network security
\end{keyword}

\end{frontmatter}

""" + body + r"""

\section*{Data availability}
The three public benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) are cited in the text and not redistributed
here. Code and a reproducibility guide are released as a public artifact.

\bibliographystyle{elsarticle-num}
\bibliography{references}

\end{document}
"""
    open(OUT, "w", encoding="utf-8").write(doc)
    print("wrote", OUT)
    print("figures placed:", sorted(placed_figs))
    print("tables placed:", sorted(placed_tabs))


if __name__ == "__main__":
    main()
