"""Convert the Markdown manuscript into a compilable LaTeX document.

Two targets:
  elsevier (default) -> manuscript/main.tex        (elsarticle; ESWA / JISA fallbacks)
  ieee               -> manuscript/main_ieee.tex   (IEEEtran; IEEE TNSM / TDSC primary target)

Usage: python -m src.analysis.make_paper2_latex [elsevier|ieee]

Ports Abstract + sections 1-8, preserves \\cite{}, converts Markdown/Unicode to LaTeX, and injects figure
and table floats at their first in-text mention. Needs the tables in manuscript/tables{,_ieee}/ and figures
in docs/img/.
"""
from __future__ import annotations
import re
import sys

MD = "manuscript/paper2_manuscript_draft_002.md"

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
TAB_FILES = {
    "1": "table1_regime_taxonomy.tex", "2": "table2_phase2_gate_summary.tex",
    "3": "table3_phase2_paired_ci.tex", "4": "table4_oracle_regret.tex",
    "5": "table5_phase1_negative.tex", "6": "table6_downstream_generalization.tex",
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

# Secondary / robustness floats moved to an Appendix to keep the main paper lean (KBS <=20 pp guideline).
APPENDIX_FIGS = {"2b", "3", "7"}
APPENDIX_TABS = {"4", "5"}

placed_figs, placed_tabs = set(), set()
appendix_blocks = []


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


def fig_float(n, env, width):
    path, cap = FIGS[n]
    return (f"\n\\begin{{{env}}}[t]\n\\centering\n\\includegraphics[width={width}]{{{path}}}\n"
            f"\\caption{{{cap}}}\n\\label{{fig:{n}}}\n\\end{{{env}}}\n")


def floats_for(block, env, width, tab_dir):
    out = ""
    for n in dict.fromkeys(re.findall(r"Figs?\.?~?\s*([0-9]+b?)", block)):
        if n in FIGS and n not in placed_figs:
            placed_figs.add(n)
            block_tex = fig_float(n, env, width)
            if n in APPENDIX_FIGS:
                appendix_blocks.append(block_tex)
            else:
                out += block_tex
    for n in dict.fromkeys(re.findall(r"Table~?\s*([0-9]+)", block)):
        if n in TAB_FILES and n not in placed_tabs:
            placed_tabs.add(n)
            inp = f"\\input{{{tab_dir}/{TAB_FILES[n]}}}\n"
            if n in APPENDIX_TABS:
                appendix_blocks.append(inp)
            else:
                out += inp
    return out


def convert_body(md, env, width, tab_dir):
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            out.append("\\begin{verbatim}")
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                out.append(lines[i]); i += 1
            out.append("\\end{verbatim}")
            i += 1
            continue
        if ln.startswith("### "):
            out.append("\n\\subsection{" + inline(re.sub(r"^###\s+\d[\w.]*\s*", "", ln).strip()) + "}")
            i += 1; continue
        if ln.startswith("## "):
            out.append("\n\\section{" + inline(re.sub(r"^##\s+\d[\w.]*\s*", "", ln).strip()) + "}")
            i += 1; continue
        if re.match(r"^\s*[-*]\s+", ln):
            out.append("\\begin{itemize}")
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                out.append("  \\item " + inline(re.sub(r"^\s*[-*]\s+", "", lines[i]))); i += 1
            out.append("\\end{itemize}"); continue
        if re.match(r"^\s*\d+\.\s+", ln):
            out.append("\\begin{enumerate}")
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                out.append("  \\item " + inline(re.sub(r"^\s*\d+\.\s+", "", lines[i]))); i += 1
            out.append("\\end{enumerate}"); continue
        if ln.strip() == "" or ln.strip() == "---":
            out.append(""); i += 1; continue
        out.append(floats_for(ln, env, width, tab_dir).rstrip("\n"))
        out.append(inline(ln))
        i += 1
    return "\n".join(out)


def section(md, start, end):
    a = md.index(start)
    return md[a:md.index(end, a)]


ELSEVIER_HEAD = r"""\documentclass[preprint,11pt]{elsarticle}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\graphicspath{{../}}
\usepackage{booktabs}
\usepackage{amsmath,amssymb}
\usepackage{xcolor}
\usepackage[hidelinks]{hyperref}
\journal{Knowledge-Based Systems}
\begin{document}
\begin{frontmatter}
\title{__TITLE__}
\author[a]{Roberto Fern\'andez Barrios\corref{cor}}
\ead{roberto.fernandez.barrios@gmail.com}
\cortext[cor]{Corresponding author.}
\affiliation[a]{organization={TODO: Affiliation}, country={TODO}}
\begin{abstract}
__ABSTRACT__
\end{abstract}
% Highlights are submitted as a separate file (manuscript/highlights.md).
\begin{keyword}
concept drift \sep intelligent decision support \sep safe model updating \sep
label-efficient learning \sep machine learning \sep intrusion detection
\end{keyword}
\end{frontmatter}

"""

IEEE_HEAD = r"""\documentclass[journal]{IEEEtran}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\graphicspath{{../}}
\usepackage{booktabs}
\usepackage{amsmath,amssymb}
\usepackage{cite}
\usepackage[hidelinks]{hyperref}
\begin{document}
\title{__TITLE__}
\author{Roberto Fern\'andez Barrios%
\thanks{R. Fern\'andez Barrios is with TODO: Affiliation (e-mail: roberto.fernandez.barrios@gmail.com).}}
\markboth{IEEE Transactions on Network and Service Management}%
{Fern\'andez Barrios: Validate Before Commit --- Label-Efficient Safe Readaptation for Adaptive NIDS}
\maketitle
\begin{abstract}
__ABSTRACT__
\end{abstract}
\begin{IEEEkeywords}
Adaptive intrusion detection, concept drift, safe model updating, label-efficient learning, retraining policy, network management.
\end{IEEEkeywords}
\IEEEpeerreviewmaketitle

"""

TITLE = "Validate Before Commit: Label-Efficient Safe Readaptation for\\\\ Adaptive Network Intrusion Detection under Concept Drift"

TAIL_ELS = r"""

\section*{CRediT authorship contribution statement}
\textbf{Roberto Fern\'andez Barrios:} Conceptualization, Methodology, Software, Formal analysis,
Investigation, Data curation, Writing -- original draft, Writing -- review \& editing, Visualization.
% Add co-authors and roles as applicable.

\section*{Declaration of competing interest}
The authors declare that they have no known competing financial interests or personal relationships that
could have appeared to influence the work reported in this paper.

\section*{Funding}
% TODO: state funding sources, or use the sentence below if none.
This research did not receive any specific grant from funding agencies in the public, commercial, or
not-for-profit sectors.

\section*{Data availability}
The three public benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) are cited in the text; the code, protocols, and a
reproducibility guide are released as a public artifact~\cite{fernandezbarrios2026artifact} (repository DOI:
TODO -- deposit on Zenodo and insert here).

% TODO (author decision): if generative-AI tools were used in manuscript preparation, add a
% "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"
% section here, per the publisher policy. Remove if not applicable.

\bibliographystyle{elsarticle-num}
\bibliography{references}
\end{document}
"""

TAIL_IEEE = r"""

\section*{Data Availability}
The three public benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) are cited in the text and not redistributed here.
Code and a reproducibility guide are released as a public artifact~\cite{fernandezbarrios2026artifact}.

\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}
"""


def main():
    target = (sys.argv[1] if len(sys.argv) > 1 else "elsevier").lower()
    if target not in ("elsevier", "ieee"):
        raise SystemExit("target must be 'elsevier' or 'ieee'")
    if target == "ieee":
        env, width, tab_dir, head, tail, out = "figure*", "\\textwidth", "tables_ieee", IEEE_HEAD, TAIL_IEEE, "manuscript/main_ieee.tex"
    else:
        env, width, tab_dir, head, tail, out = "figure", "\\linewidth", "tables", ELSEVIER_HEAD, TAIL_ELS, "manuscript/main.tex"

    placed_figs.clear(); placed_tabs.clear(); appendix_blocks.clear()
    md = open(MD, encoding="utf-8").read()
    abstract = inline(section(md, "## Abstract", "## Contributions").split("\n", 2)[2].strip().replace("\n", " "))
    body = convert_body(section(md, "## 1. Introduction", "## Main tables"), env, width, tab_dir)

    appendix = ""
    if appendix_blocks:
        appendix = ("\n\\appendix\n\\section{Additional results and robustness}\n"
                    "The floats below support the main text (mechanism-law pooling, oracle-regret, "
                    "label-latency, and the Phase-1 negative and oracle-regret tables).\n"
                    + "".join(appendix_blocks))

    doc = head.replace("__TITLE__", TITLE).replace("__ABSTRACT__", abstract) + body + appendix + tail
    open(out, "w", encoding="utf-8").write(doc)
    print("wrote", out, "| target:", target)
    print("main figures:", sorted(placed_figs - APPENDIX_FIGS), "| appendix figures:", sorted(placed_figs & APPENDIX_FIGS))
    print("main tables:", sorted(placed_tabs - APPENDIX_TABS), "| appendix tables:", sorted(placed_tabs & APPENDIX_TABS))


if __name__ == "__main__":
    main()
