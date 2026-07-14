# NOTE (amendment 004): this generator produced the INITIAL manuscript skeleton. The
# manuscript of record is manuscript/main.tex, maintained directly since; do not regenerate over it.
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
           "The degradation--benefit law pooled across four downstream classifiers ($r=-0.81$, bootstrap 95\\% CI)."),
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
           "The gate remains harm-avoiding under randomly corrupted validation labels (up to 40\\% flipped)."),
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


def fig_float(n, env, width, pos):
    path, cap = FIGS[n]
    return (f"\n\\begin{{{env}}}{pos}\n\\centering\n\\includegraphics[width={width}]{{{path}}}\n"
            f"\\caption{{{cap}}}\n\\label{{fig:{n}}}\n\\end{{{env}}}\n")


def floats_for(block, env, width, tab_dir, pos):
    out = ""
    for n in dict.fromkeys(re.findall(r"Figs?\.?~?\s*([0-9]+b?)", block)):
        if n in FIGS and n not in placed_figs:
            placed_figs.add(n)
            block_tex = fig_float(n, env, width, pos)
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


def convert_body(md, env, width, tab_dir, pos):
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
        out.append(floats_for(ln, env, width, tab_dir, pos).rstrip("\n"))
        out.append(inline(ln))
        i += 1
    return "\n".join(out)


def section(md, start, end):
    a = md.index(start)
    return md[a:md.index(end, a)]


ELSEVIER_HEAD = r"""%% Elsevier CAS single-column template (cas-sc) -- target: Knowledge-Based Systems.
%% Requires cas-sc.cls, cas-common.sty (in this folder) and figures at ../docs/img/.
\documentclass[a4paper,fleqn]{cas-sc}
\usepackage[numbers]{natbib}   % KBS uses numbered [1] references, in order of appearance
\graphicspath{{../}}           % figures live at repo-root docs/img/

\begin{document}
\let\WriteBookmarks\relax

\shorttitle{Validate Before Commit}
\shortauthors{Fern\'andez-Barrios et al.}

\title[mode=title]{__TITLE__}

\author[1]{Roberto Fern\'andez-Barrios}[orcid=0009-0003-5312-2634]
\cormark[1]
\ead{roberto.fernandez.b@deusto.es}
\credit{Conceptualization, Methodology, Software, Data curation, Formal analysis, Visualization, Investigation, Writing -- original draft, Writing -- review \& editing}

\author[1]{Iker Pastor-L\'opez}[orcid=0000-0002-3068-6248]
\ead{iker.pastor@deusto.es}
\credit{Supervision, Validation, Writing -- review \& editing}

\author[1]{Amaia Pikatza-Huerga}[orcid=0009-0003-9080-6242]
\ead{a.pikatza@deusto.es}
\credit{Validation, Project administration, Writing -- review \& editing}

\author[1]{Pablo Garc\'ia Bringas}[orcid=0000-0003-3594-9534]
\ead{pablo.garcia.bringas@deusto.es}
\credit{Supervision, Resources, Writing -- review \& editing}

\affiliation[1]{organization={Faculty of Engineering, University of Deusto},
                addressline={Avda. de las Universidades, 24},
                city={Bilbao},
                postcode={48007},
                country={Spain}}

\cortext[1]{Corresponding author}

\begin{abstract}
__ABSTRACT__
\end{abstract}

\begin{graphicalabstract}
\includegraphics[width=\linewidth]{docs/img/graphical_abstract.png}
\end{graphicalabstract}

\begin{highlights}
\item Drift alarms do not reveal if retraining helps; model degradation does ($r\approx-0.85$)
\item Naive drift-triggered retraining can be net-harmful; never adapting can win
\item Validate before commit: deploy a retrained model only if a small probe confirms gain
\item Deploy a retrained candidate only when a small labeled probe confirms improvement
\item Safe across two detectors and four classifiers; pre-registered, 30-seed CIs
\end{highlights}

\begin{keywords}
concept drift \sep intelligent decision support \sep safe model updating \sep label-efficient learning \sep machine learning \sep intrusion detection
\end{keywords}

\maketitle

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
\author{Roberto Fern\'andez-Barrios,~Iker Pastor-L\'opez,~Amaia Pikatza-Huerga,~and~Pablo Garc\'ia~Bringas%
\thanks{The authors are with the Faculty of Engineering, University of Deusto, 48007 Bilbao, Spain
(e-mail: roberto.fernandez.b@deusto.es; iker.pastor@deusto.es; a.pikatza@deusto.es; pablo.garcia.bringas@deusto.es).}}
\markboth{IEEE Transactions on Dependable and Secure Computing}%
{Fern\'andez-Barrios \MakeLowercase{\textit{et al.}}: Validate Before Commit}
\maketitle
\begin{abstract}
__ABSTRACT__
\end{abstract}
\begin{IEEEkeywords}
Adaptive intrusion detection, concept drift, safe model updating, label-efficient learning, retraining policy, network management.
\end{IEEEkeywords}
\IEEEpeerreviewmaketitle

"""

TITLE = "Validate Before Commit: Label-Efficient Commit Decisions for Drift-Triggered Classifier Updates in Network Intrusion Detection"

TAIL_ELS = r"""

\section*{Declaration of competing interest}
The authors declare that they have no known competing financial interests or personal relationships that
could have appeared to influence the work reported in this paper.

\section*{Funding}
This research did not receive any specific grant from funding agencies in the public, commercial, or
not-for-profit sectors.

\section*{Data availability}
The three public benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) are cited in the text; the code, protocols, and a
reproducibility guide are released as a public artifact~\cite{fernandezbarrios2026artifact}
(Zenodo, DOI \href{https://doi.org/10.5281/zenodo.21322256}{10.5281/zenodo.21322256}).

\section*{Declaration of generative AI and AI-assisted technologies in the manuscript preparation process}
During the preparation of this work the authors used Claude (Anthropic) to assist with drafting and editing
the manuscript text and with the implementation of the analysis scripts. After using this tool, the authors
reviewed, verified and edited the content as needed and take full responsibility for the content of the
published article.

% CRediT roles are declared via \credit{} in the front matter and printed here:
\printcredits

\bibliographystyle{unsrtnat}  % numbered, in order of appearance (KBS style). For Elsevier's exact CAS
                              % numbered style use \bibliographystyle{cas-model1-num-names} (from the CAS bundle).
\bibliography{references}
\end{document}
"""

TAIL_IEEE = r"""

\section*{Data Availability}
The three public benchmarks (CICIDS2017, UNSW-NB15, ToN-IoT) are cited in the text and not redistributed here.
Code and a reproducibility guide are released as a public artifact~\cite{fernandezbarrios2026artifact}
(Zenodo, DOI 10.5281/zenodo.21322256).

\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}
"""


def main():
    target = (sys.argv[1] if len(sys.argv) > 1 else "elsevier").lower()
    if target not in ("elsevier", "ieee"):
        raise SystemExit("target must be 'elsevier' or 'ieee'")
    if target == "ieee":
        env, width, tab_dir, pos, head, tail, out = "figure*", "\\textwidth", "tables_ieee", "[t]", IEEE_HEAD, TAIL_IEEE, "manuscript/main_ieee.tex"
    else:
        env, width, tab_dir, pos, head, tail, out = "figure", "\\linewidth", "tables", "", ELSEVIER_HEAD, TAIL_ELS, "manuscript/main.tex"

    placed_figs.clear(); placed_tabs.clear(); appendix_blocks.clear()
    md = open(MD, encoding="utf-8").read()
    abstract = inline(section(md, "## Abstract", "## Contributions").split("\n", 2)[2].strip().replace("\n", " "))
    body = convert_body(section(md, "## 1. Introduction", "## Main tables"), env, width, tab_dir, pos)

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
