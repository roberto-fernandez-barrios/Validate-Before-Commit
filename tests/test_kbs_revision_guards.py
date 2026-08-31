"""Guards for the post-KBS editorial revision (notes/kbs_revision_editorial_protocol_001.md).

Pin what the revision added so it cannot silently regress or drift from the sealed outputs:
the explicit configuration-dependence statement in the Introduction, the contribution
hierarchy, the information-parity paragraph in section 5.2, the baseline-comparison section
and table (every number re-checked against the sealed CSV it came from), the overhead paragraph
(marked as operational context; ratios re-derived from the completion markers when present),
the relocated VBC-SG definitions in Supplement S2.13, and the integrity of every
main -> supplement pointer.
"""
from __future__ import annotations

import re
import statistics as st

import pandas as pd
import pytest

from tests.conftest import REPO

MAIN = (REPO / "manuscript" / "main.tex").read_text(encoding="utf-8")
IEEE = (REPO / "manuscript" / "main_ieee.tex").read_text(encoding="utf-8")
SUPP = (REPO / "manuscript" / "supplement.tex").read_text(encoding="utf-8")
README = (REPO / "README.md").read_text(encoding="utf-8")
T = REPO / "results" / "tables"
FULLTAB = (REPO / "manuscript" / "tables" / "table_baselines_full.tex"
           ).read_text(encoding="utf-8")


def _flat(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower())


# ---------------------------------------------------------------- introduction / hierarchy
def test_intro_states_configuration_dependence_before_results():
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE)):
        intro = t.split("\\section{Introduction}")[1].split("\\section{Related work}")[0]
        f = _flat(intro)
        assert "scope of the net-harm findings" in f, name
        assert "configuration-dependent" in f, name
        assert "we do not claim them as universal properties" in f, name
        assert "robust learners" in f and "self-contained, size-matched challengers" in f, name
        assert "a statement about the configuration that produced it" in f, name


def test_contribution_hierarchy_explicit():
    f = _flat(MAIN)
    for marker in ("primary --- candidate comparability before promotion",
                   "secondary --- conditional validation",
                   "tertiary --- formal, diagnostic and operational instruments"):
        assert marker in f, marker
    assert "not universal policies or primary contributions" in f


def test_no_generic_adaptation_is_harmful_wording():
    banned = [r"adaptation is (generally|usually|typically) harmful",
              r"retraining is (generally|usually|typically) harmful",
              r"adaptive promotion is (generally|usually|intrinsically) (harmful|dangerous)"]
    for name in ("manuscript/main.tex", "manuscript/main_ieee.tex", "manuscript/supplement.tex",
                 "README.md", "manuscript/highlights.md"):
        f = _flat((REPO / name).read_text(encoding="utf-8"))
        for pat in banned:
            assert not re.search(pat, f), f"{name}: {pat}"


# ---------------------------------------------------------------- section 5.2 information parity
def test_section_5_2_information_parity_paragraph():
    sec = MAIN.split("\\label{sec:sizematched}")[1].split("\\label{sec:gatevalue}")[0]
    f = _flat(sec)
    assert "what nominal sample-size parity does and does not match" in f
    assert ("effective sample size, temporal coverage, temporal diversity, subtype support, "
            "duplication, label quality, prevalence or information content") in f
    assert "pool draws are with replacement" in f
    assert "nominal parity is not information parity" in f
    assert "isolates the nominal row-count factor" in f


# ---------------------------------------------------------------- baseline comparison section
def _table_rows(src: str = None, label: str = "tab:baselines_full") -> dict[str, list[str]]:
    """Map the leading cell of every data row of a baselines table to its cell list."""
    block = (FULLTAB if src is None else src).split(
        "\\label{" + label + "}")[1].split("\\end{tabular}")[0]
    rows = {}
    for line in block.splitlines():
        if "&" not in line or line.strip().startswith(("Policy", "\\multicolumn")):
            continue
        cells = [c.strip() for c in line.rstrip("\\").split("&")]
        rows.setdefault(cells[0], []).append(cells)
    return rows


def _num(cell: str) -> float:
    m = re.search(r"([+-]?\d+\.\d+)", cell.replace("$", "").replace("{,}", ""))
    assert m, cell
    return float(m.group(1))


def _nth(rows, label, n):
    assert label in rows, f"row missing from tab:baselines: {label!r}"
    return rows[label][n]


def test_baselines_section_present_and_wired():
    assert "\\label{sec:baselines}" in MAIN and "\\label{tab:baselines}" in MAIN
    assert MAIN.count("\\ref{sec:baselines}") >= 3
    f = _flat(MAIN)
    assert "comparison with evaluated baselines and alternative update policies" in f
    assert "comparison with strong baselines" not in f, "SoTA-style title banned"
    assert "cross-block comparisons are descriptive" in f
    assert "supports no common ranking" in f
    assert "\\label{tab:baselines}" in MAIN, "compact core table must stay in the body"
    assert "\\label{tab:baselines_full}" in FULLTAB
    assert "\\input{tables/table_baselines_full.tex}" in SUPP
    # the section is the last Results subsection so supplement '§5.5' pointers stay valid
    results = MAIN.split("\\section{Results}")[1].split("\\section{Discussion}")[0]
    subs = re.findall(r"\\subsection\{([^}]*)\}", results)
    assert subs[-1].startswith("Comparison with evaluated baselines")
    assert len(subs) == 6


def test_baselines_block_I_matches_policy_frontier_csv():
    rows = _table_rows()
    F = pd.read_csv(T / "paper2_policy_frontier_005" / "frontier.csv")

    def g(policy, regime):
        return float(F[(F.policy == policy) & (F.regime == regime)].gain.iloc[0])

    expect = {
        "Always-deploy (naive) [std]": "naive",
        "Sliding-window update, always deploy [std]": "sliding_window",
        "Calibrated soft ensemble, always deploy [std]": "ensemble_cal",
        "DDM trigger (\\texttt{river}, 8 labels/window) [ref]": "ddm_river_b8",
        "Point gate, $b{=}32$ [ours]": "labeled_probe_b32",
        "Holdout gate (dedup.\\ batch probe) [ours-var]": "holdout_dedup",
        "LCB gate, $b{=}64$ [ours-var]": "lcb_b64",
        "Two-stage split gate ($\\delta{=}0.05$) [ours]": "two_stage_split_d05",
    }
    for label, pol in expect.items():
        cells = _nth(rows, label, 0)          # first occurrence = Block I
        for i, regime in ((5, "portscan"), (6, "unsw_recon"), (7, "ton_scanning")):
            assert abs(_num(cells[i]) - g(pol, regime)) <= 0.006, (label, regime)
        tot = float(F[(F.policy == pol) & (F.regime == "ton_scanning")].total_labels.iloc[0])
        assert abs(_num(cells[8] + ".0") - tot) < 1.0, (label, "labels")
    # McNemar and ADWIN come from their own sealed CSVs
    A6 = pd.read_csv(T / "paper2_amendment_006" / "summary.csv")
    mc = _nth(rows, "Exact McNemar, $b{=}32$, $\\alpha{=}0.05$ [ours-var]", 0)
    for i, regime in ((5, "portscan"), (6, "unsw_recon"), (7, "ton_scanning")):
        v = float(A6[(A6.arm == "mcnemar32") & (A6.regime == regime)].gain.iloc[0])
        assert abs(_num(mc[i]) - v) <= 0.006, ("mcnemar", regime)
    R4 = pd.read_csv(T / "paper2_amendment_004" / "robustness.csv")
    ad = _nth(rows, "ADWIN trigger (\\texttt{river}, 8 labels/window) [ref]", 0)
    for i, regime in ((5, "portscan"), (6, "unsw_recon"), (7, "ton_scanning")):
        v = float(R4[(R4.arm == "adwinriver_none") & (R4.regime == regime)].gain.iloc[0])
        assert abs(_num(ad[i]) - v) <= 0.006, ("adwin", regime)


def test_baselines_block_II_matches_zero_drift_csv():
    rows = _table_rows()
    A8 = pd.read_csv(T / "paper2_amendment_008" / "summary.csv")

    def g(arm, regime):
        return float(A8[(A8.arm == arm) & (A8.regime == regime)].gain.iloc[0])

    expect = {("Always-deploy (naive) [std]", 1): "rand_s0_none",
              ("Point gate, $b{=}32$ [ours]", 1): "rand_s0_lp32",
              ("Exact McNemar, $b{=}32$ [ours-var]", 0): "rz_mcnemar32",
              ("Sequential probe (4-look Bonferroni), $b{\\le}64$ [ours-var]", 0):
                  "rz_seqav64",
              ("Always-deploy, real KS-max trigger$^{a}$ [std]", 0):
                  "sev0_none"}
    for (label, n), arm in expect.items():
        cells = _nth(rows, label, n)
        for i, regime in ((5, "portscan"), (6, "unsw_recon"), (7, "ton_scanning")):
            assert abs(_num(cells[i]) - g(arm, regime)) <= 0.006, (label, regime)


def test_baselines_block_III_matches_exploratory_csvs():
    rows = _table_rows()
    LF = pd.read_csv(T / "paper2_phase2h_labelfree_gates_001" / "paper2_labelfree_gates_summary.csv")
    LF = LF[LF.downstream == "svc_rbf"]
    RP = pd.read_csv(T / "paper2_phase2i_replay_baseline_001" / "summary.csv")

    def lf(gate, regime):
        return float(LF[(LF.gate == gate) & (LF.regime == regime)].gain_pts.iloc[0])

    def rp(arm, regime):
        return float(RP[(RP.arm == arm) & (RP.regime == regime)].gain_pts.iloc[0])

    expect = {("Always-deploy (naive) [std]", 2): ("lf", "naive"),
              ("Point gate, $b{=}32$ [ours]", 2): ("lf", "lp32"),
              ("Disagreement gate ($\\tau{=}0.15$) [ours-var]", 0): ("lf", "unsup"),
              ("ATC gate \\cite{garg2022atc} [pub]", 0): ("lf", "atc"),
              ("DoC gate \\cite{guillory2021doc} [pub]", 0): ("lf", "doc"),
              ("Replay 50/50 retraining, always deploy [std]", 0): ("rp", "replay_naive"),
              ("Replay 50/50 $+$ point gate, $b{=}32$ [ours-var]", 0): ("rp", "replay_lp32")}
    for (label, n), (src, key) in expect.items():
        cells = _nth(rows, label, n)
        for i, regime in ((5, "portscan"), (6, "unsw_recon"), (7, "ton_scanning")):
            v = lf(key, regime) if src == "lf" else rp(key, regime)
            assert abs(_num(cells[i]) - v) <= 0.006, (label, regime)


def test_baselines_block_IV_matches_budget_frontier():
    rows = _table_rows()
    B = pd.read_csv(T / "paper2_final_q1" / "budget_frontier.csv")
    A = pd.read_csv(T / "paper2_final_q1" / "frontier_anchors.csv")

    def anchor(policy, scenario):
        return float(A[(A.policy == policy) & (A.scenario == scenario)].gain.iloc[0])

    for label, n, pol in (("Always-deploy (naive) [std]", 3, "none"),
                          ("Point gate, $b{=}32$ [ours]", 3, "point"),
                          ("Strict gate (reject ties), $b{=}32$ [ours]", 0, "strict")):
        cells = _nth(rows, label, n)
        assert abs(_num(cells[5]) - anchor(pol, "ps_full")) <= 0.006, (label, "ps_full")
        assert abs(_num(cells[7]) - anchor(pol, "ton_zero")) <= 0.006, (label, "ton_zero")
    for label, pol in (("Pooled EB-CS $+$ defer, cap 512 [ours-var]", "ebcsdef"),
                       ("VBC-SG-Cohort-sim, cap 512 [ours]", "vbccoh"),
                       ("VBC-SG-Refresh, cap 512 [ours-var]", "vbcref")):
        cells = _nth(rows, label, 0)
        r = B[(B.scenario == "ps_full") & (B.policy == pol) & (B.cap == 512)
              & (B.schedule == "bonf")].iloc[0]
        assert abs(_num(cells[5]) - float(r.gain)) <= 0.006, (label, "gain")
        pct = int(re.search(r"\((\d+)\\%\)", cells[5]).group(1))
        assert pct == int(round(float(r.e2_frac_naive) * 100)), (label, "pct")
        assert abs(int(cells[8]) - float(r.labels_probe_per_proposal)) < 1.0, (label, "labels")
        z = B[(B.scenario == "ton_zero") & (B.policy == pol) & (B.cap == 512)
              & (B.schedule == "bonf")].iloc[0]
        assert float(z.gain) == 0.0 and int(z.commits_total) == 0 and int(z.proposals) == 91
        assert "0 commits" in cells[7]


def test_baselines_block_V_matches_registered_replications():
    rows = _table_rows()
    C = pd.read_csv(T / "symmetric_pipeline_dynamic_001" / "paired_contrasts.csv")
    full = _nth(rows, "Always-deploy, 512/class, full drift [std]", 0)
    for i, sc in ((5, "ps_full"), (6, "unsw_full"), (7, "ton_full")):
        v = float(C[C.contrast == f"{sc}: own-naive vs never"].effect_pp.iloc[0])
        assert abs(_num(full[i]) - v) <= 0.006, sc
    E = pd.read_csv(T / "v1_22_1_editorial" / "evidence_validation_tradeoff.csv")
    for label, pol in (("Always-deploy, 512/class, zero drift [std]", "naive_512"),
                       ("Strict gate, 512/class, zero drift [ours]", "strict_512"),
                       ("Always-deploy, 2{,}000/class, zero drift [std]",
                        "naive_2000")):
        cells = _nth(rows, label, 0)
        for i, sc in ((5, "ps_zero"), (6, "unsw_zero"), (7, "ton_zero")):
            v = float(E[(E.policy == pol) & (E.scenario == sc)].ba_vs_never_pp.iloc[0])
            assert abs(_num(cells[i]) - v) <= 0.006, (label, sc)


def test_baselines_93_percent_marked_pooled_and_near_81():
    f = _flat(MAIN) + " " + _flat(FULLTAB)
    for m in re.finditer(r"93\\%", f):
        w = f[max(0, m.start() - 40): m.end() + 240]
        assert "pooled" in w or "approximate" in w
        assert "81" in f[max(0, m.start() - 400): m.end() + 400]


# ---------------------------------------------------------------- overhead paragraph (Task 8)
def test_overhead_paragraph_is_operational_context_not_benchmark():
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE)):
        f = _flat(t)
        assert "computational overhead of self-contained challengers (operational implication, " \
               "not a benchmark)" in f, name
        assert "we did not run an isolated timing study" in f, name
        assert "not a benchmark" in f, name
        i = f.index("computational overhead of self-contained challengers")
        para = f[i: i + 2500]
        assert "114" in para and "drift detector rather than the challenger pipeline" in para, name


def test_overhead_ratios_match_completion_markers_when_present():
    csv = REPO / "audits" / "pipeline_arm_wallclock_summary.csv"
    if not csv.exists():
        pytest.skip("wall-clock summary not generated (needs local results/raw)")
    S = pd.read_csv(csv)
    r = S[S.kind == "pair_frozen_vs_own"].ratio_own_over_frozen.astype(float)
    q = S[S.kind == "pair_512_vs_2000"].ratio_2000_over_512.astype(float)
    assert len(r) == 18 and len(q) == 9
    f = _flat(MAIN)
    assert f"{st.mean(r):.2f}$\\times$" in f.replace(" ", "") or \
        f"average ${st.mean(r):.2f}\\times$" in f
    assert f"range ${min(r):.2f}$--${max(r):.2f}$" in f
    lo, hi = min(q), max(q)
    assert "$1.2$--$1.5\\times$" in f and 1.15 <= lo <= 1.25 and 1.45 <= hi <= 1.55


# ---------------------------------------------------------------- supplement relocation / pointers
def _supp_sections():
    """[(title, [subsection titles])] in order; S0 is the first entry."""
    out = []
    # anchored at line start so the \newcommand{\bsection}... preamble line is not counted
    for m in re.finditer(r"^\\(section|subsection)\{(.*)\}\s*$", SUPP, re.M):
        if m.group(1) == "section":
            out.append((m.group(2), []))
        else:
            out[-1][1].append(m.group(2))
    return out


def test_vbcsg_details_relocated_to_S2_13():
    secs = _supp_sections()
    s2 = secs[2]
    assert s2[0].startswith("Registered-extension details")
    assert len(s2[1]) == 13 and s2[1][12].startswith("VBC-SG: continuation modes")
    assert "\\label{sec:S2_vbcsg}" in SUPP
    for phrase in ("Continuation modes under deferral", "Deployment-long risk budget",
                   "Four properties, stated at the strength we can support",
                   "Cohort-sim does not model retention and delayed adjudication"):
        assert phrase in SUPP, phrase
    riskgates = MAIN.split("\\label{sec:riskgates}")[1].split("\\section{Experimental design}")[0]
    assert "Supplementary \\S S2.13" in riskgates
    for tag in ("(A) Point and strict validation", "(B) Risk-controlled validation",
                "(C) Pooled versus stratified guarantees", "(D) VBC-SG: commit, reject or defer",
                "(E) What VBC-SG guarantees", "(F) What VBC-SG does not guarantee"):
        assert tag in riskgates, tag
    assert "Proposition 1" in riskgates and "S4" in riskgates
    assert "cohort-sim" in riskgates.lower()
    assert len(riskgates.split()) < 1100, "section 3.5 must stay condensed"


def test_every_supplementary_pointer_in_main_resolves():
    secs = _supp_sections()
    assert secs[6][0].startswith("Multiplicity"), "S6 must be the multiplicity section"
    assert secs[5][0].startswith("Total label"), "S5 must be the label ledger"
    for m in re.finditer(r"\\S S(\d+)(?:\.(\d+))?", MAIN):
        n = int(m.group(1))
        assert n < len(secs), m.group(0)
        if m.group(2):
            assert int(m.group(2)) <= len(secs[n][1]), m.group(0)
    # the BH block is in S6, the ownership A/B and budget-frontier tables in S2.12
    bh = MAIN[MAIN.index("Benjamini--Hochberg \\cite"):][:300]
    assert "\\S S6" in bh
    assert "Ownership A/B & Support & role-randomized transformer & 2001--2100 & " \
           "Feature scaling owns the effect & \\S S2.12" in SUPP
    assert "\\S S2.8" not in MAIN.split("\\label{tab:evidence_map}")[1][:2000]


def test_readme_reviewer_quick_map_paths_exist():
    sec = README.split("## Reviewer quick map")[1].split("## TL;DR")[0]
    assert sec.count("\n| ") >= 10, "nine numbered rows expected"
    for p in re.findall(r"`([^`]+)`", sec):
        if "…" in p or p.startswith(("cd ", "python ", "make ", "--", "CLAIM_INTERPRETATION")):
            continue
        if p.startswith(("manuscript/", "configs/", "notes/", "docs/", "results/",
                         "REPRODUCE.md", "audits/")):
            assert (REPO / p.rstrip("/")).exists(), p


def test_baselines_compact_core_matches_csvs():
    """The compact in-body table (paired v2 panel + exploratory ATC/DoC panel) matches the
    sealed CSVs, and its two panels are explicitly labelled with their comparability."""
    rows = _table_rows(src=MAIN, label="tab:baselines")
    F = pd.read_csv(T / "paper2_policy_frontier_005" / "frontier.csv")

    def g(policy, regime):
        return float(F[(F.policy == policy) & (F.regime == regime)].gain.iloc[0])

    core = {"Always-deploy (naive)": "naive",
            "Sliding-window update": "sliding_window",
            "Calibrated soft ensemble": "ensemble_cal",
            "DDM trigger (\\texttt{river})": "ddm_river_b8",
            "Point gate, $b{=}32$": "labeled_probe_b32",
            "Two-stage split gate ($\\delta{=}0.05$)": "two_stage_split_d05"}
    for label, pol in core.items():
        cells = _nth(rows, label, 0)
        for i, regime in ((4, "portscan"), (5, "unsw_recon"), (6, "ton_scanning")):
            assert abs(_num(cells[i]) - g(pol, regime)) <= 0.006, (label, regime)
    A6 = pd.read_csv(T / "paper2_amendment_006" / "summary.csv")
    mc = _nth(rows, "Exact McNemar, $b{=}32$", 0)
    R4 = pd.read_csv(T / "paper2_amendment_004" / "robustness.csv")
    ad = _nth(rows, "ADWIN trigger (\\texttt{river})", 0)
    LF = pd.read_csv(T / "paper2_phase2h_labelfree_gates_001"
                     / "paper2_labelfree_gates_summary.csv")
    LF = LF[LF.downstream == "svc_rbf"]

    def lf(gate, regime):
        return float(LF[(LF.gate == gate) & (LF.regime == regime)].gain_pts.iloc[0])

    for i, regime in ((4, "portscan"), (5, "unsw_recon"), (6, "ton_scanning")):
        v = float(A6[(A6.arm == "mcnemar32") & (A6.regime == regime)].gain.iloc[0])
        assert abs(_num(mc[i]) - v) <= 0.006, ("mcnemar", regime)
        v = float(R4[(R4.arm == "adwinriver_none") & (R4.regime == regime)].gain.iloc[0])
        assert abs(_num(ad[i]) - v) <= 0.006, ("adwin", regime)
        for label, key in (("Always-deploy (naive, v1)", "naive"),
                           ("ATC gate \\cite{garg2022atc}", "atc"),
                           ("DoC gate \\cite{guillory2021doc}", "doc"),
                           ("Point gate, $b{=}32$ (v1)", "lp32")):
            cells = _nth(rows, label, 0)
            assert abs(_num(cells[i]) - lf(key, regime)) <= 0.006, (label, regime)
    cap = MAIN.split("\\label{tab:baselines}")[0][-2200:]
    fcap = _flat(cap)
    assert "directly comparable" in fcap and "not comparable with the top panel" in fcap
