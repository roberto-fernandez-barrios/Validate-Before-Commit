"""Guards for the closed IJIS pre-submission pass (audits/ijis_hostile_prereview_2026-09-01.md,
resolved in audits/ijis_hostile_prereview_resolution_2026-09-01.md).

Every clarification added in that pass is pinned here against the sealed CSV it was read from,
and the wording the pass fixed cannot silently regress: the between-seed-block scoping of the
historical frozen harm (-1.64 / -1.97 / -4.95), the per-sub-cell provenance of Table 3, the
pooled-versus-regime-specific correlation wording around Fig. 2, the exact chronological
replay count (13 = 7 + 6), the reference-parameter scope of the DDM/ADWIN cells, the
one-scenario-per-benchmark statement, the abstract without the bare 'ATC' acronym, the
security-significance paragraph with its explicit out-of-scope sentence, and the removal of
internal artifact identifiers from the main paper. The registered outcomes (HOMOGENEOUS-SIZE
BENEFIT, 0/6 matched gate benefit, ATTENUATION) are re-asserted unchanged.
"""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from tests.conftest import REPO

MS = REPO / "manuscript"
T = REPO / "results" / "tables"
MAIN = (MS / "main.tex").read_text(encoding="utf-8")
IEEE = (MS / "main_ieee.tex").read_text(encoding="utf-8")
SPRINGER = (MS / "main_springer.tex").read_text(encoding="utf-8")
SUPP = (MS / "supplement.tex").read_text(encoding="utf-8")
SYN = (MS / "tables" / "table_synthesis.tex").read_text(encoding="utf-8")
CHRONO = (MS / "tables" / "table_chronological_q1.tex").read_text(encoding="utf-8")


def _flat(t: str) -> str:
    return re.sub(r"\s+", " ", t).lower()


def _body(t: str) -> str:
    """Main text from the Introduction to the declarations (the Data-availability statement
    legitimately names artifact versions and is checked separately)."""
    end = t.find("\\section*{Declaration of competing interest}")
    return t[t.index("\\section{Introduction}"): end if end != -1 else len(t)]


def _abstract(t: str) -> str:
    return re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", t, re.S).group(1)


# ---------------------------------------------------------------- A: -1.64 vs -4.95 scoping
def test_frozen_harm_between_block_paragraph_matches_sealed_csvs():
    # block A: harness-v2 replication, seeds 104-133
    v2 = pd.read_csv(T / "paper2_v2_replication_001" / "summary.csv")
    r = v2[(v2.detector == "ks") & (v2.regime == "ton_scanning") & (v2.arm == "none")].iloc[0]
    assert round(float(r.gain_pts), 2) == -1.64 and round(float(r.ci_lo), 2) == -2.72
    assert round(float(r.ci_hi), 2) == -0.64
    # block F: frontier anchor, seeds 501-530
    fa = pd.read_csv(T / "paper2_final_q1" / "frontier_anchors.csv")
    f = fa[(fa.scenario == "ton_full") & (fa.policy == "none")].iloc[0]
    assert round(float(f.gain), 2) == -1.97 and round(float(f.lo), 2) == -4.0
    assert round(float(f["hi"]), 2) == -0.14
    # block B: symmetric replication frozen arm, seeds 3001-3030 (per-seed values sealed)
    bs = pd.read_csv(T / "symmetric_pipeline_dynamic_001" / "by_seed.csv")
    bs = bs[bs.scenario == "ton_full"]
    never = bs[bs.policy == "never"].set_index("seed").ba
    frz = bs[(bs.policy == "naive") & (bs.transformer_policy == "frozen_initial_transformer")
             ].set_index("seed").ba
    gain = ((frz - never.loc[frz.index]) * 100).values
    assert len(gain) == 30
    assert round(float(gain.mean()), 2) == -4.95
    assert round(float(np.median(gain)), 1) == -2.4
    assert int((gain < -10).sum()) == 7
    sec = MAIN.split("\\label{sec:historical}")[1].split("\\label{sec:symmetric}")[0]
    f_ = _flat(sec)
    assert "absolute harm magnitudes in this configuration vary between seed blocks" in f_
    for s in ("$-1.64$ [$-2.72$, $-0.64$]", "$-1.97$ [$-4.00$, $-0.14$]",
              "$-4.95$ [$-7.15$, $-2.86$]", "seeds 104--133", "seeds 501--530", "seeds 3001--3030",
              "median stream loses $2.4$ points", "seven of thirty streams lose more than ten"):
        assert s in sec, s
    # the paired/comparative scoping and the non-reliance of B1/B2 on the absolute values
    assert "paired within-block contrasts" in f_
    assert "do not use these historical absolute values" in f_
    # the paragraph must not blame the bootstrap without an analysis (none was run)
    for banned in ("underestimates uncertainty", "bootstrap fails", "invalid confidence"):
        assert banned not in f_, banned
    # the historical -1.64 must still be quoted as the same configuration, never as a
    # different estimand
    assert "different configuration" not in f_


def test_frozen_harm_scoping_survives_in_ports():
    for name, t in (("main_ieee.tex", IEEE), ("main_springer.tex", SPRINGER)):
        f = _flat(t)
        assert "absolute harm magnitudes in this configuration vary between seed blocks" in f, name
        assert "$-1.97$ [$-4.00$, $-0.14$]".lower() in f, name


# ---------------------------------------------------------------- B: Table 3 provenance
def test_table3_names_the_seed_block_of_every_summary():
    cap = SYN.split("\\label{tab:synthesis}")[0]
    tab = SYN.split("\\label{tab:synthesis}")[1]
    assert "names the 30-seed block it was estimated in" in _flat(cap)
    assert "absolute frozen-configuration magnitudes differ between seed blocks" in _flat(cap)
    # the 512/class validation summaries of rows 3-4 come from the symmetric replication and
    # must say so next to the Delta that comes from another block
    assert tab.count("seeds 3001--3030, Table~\\ref{tab:symmetric_pipeline}") == 2
    assert tab.count("seeds 4001--4030") == 2 and tab.count("seeds 6001--6030") == 2
    assert "seeds 104--133; descriptive" in tab
    assert "same block; registered F3" in tab and "same block; registered G3" in tab
    # every data row carries a seed-block statement in each evaluated cell
    rows = [r for r in tab.split("\\addlinespace") if "$\\Delta$ vs never" in r]
    assert len(rows) == 4
    for r in rows:
        cells = [c for c in r.split("&") if "$\\Delta$ vs never" in c]
        for c in cells:
            assert re.search(r"seeds \d{3,4}--\d{3,4}", c), c
    for jargon in ("amendment-008", "post-v1.22", "v1.2"):
        assert jargon not in SYN, jargon
    # identical copies for the two-column ports
    for d in ("tables_ieee", "tables_springer"):
        other = (MS / d / "table_synthesis.tex").read_text(encoding="utf-8")
        assert other.replace("Online Resource~1, \\S", "Supplementary \\S") == SYN or other == SYN, d


# ---------------------------------------------------------------- C: Fig. 2 / 5.7 / 6 numbers
def test_mechanism_correlations_pooled_vs_regime_specific():
    m = pd.read_csv(T / "paper2_v2_replication_001" / "mechanism.csv").set_index("regime")
    pooled = m.loc["POOLED"]
    assert round(float(pooled.r_deg), 2) == -0.57
    # the CSV stores r_score to three decimals (0.025); the figure computes it at full precision
    # from the same 250 triggers and prints +0.02, which the text quotes
    assert abs(float(pooled.r_score) - 0.02) <= 0.0051
    assert int(pooled.n_triggers) == 250
    reg = m.loc[["portscan", "unsw_recon", "ton_scanning"]]
    assert round(float(reg.r_deg.max()), 2) == -0.67 and round(float(reg.r_deg.min()), 2) == -0.70
    assert round(float(reg.r_score.min()), 2) == -0.01 and round(float(reg.r_score.max()), 2) == 0.05
    qk = pd.read_csv(T / "paper2_decision_quality_005" / "mechanism_by_detector.csv")
    q = qk[(qk.detector == "qk") & (qk.regime == "POOLED")].iloc[0]
    assert round(float(q.r_deg), 2) == -0.59 and round(float(q.r_score), 2) == 0.01
    sec = MAIN.split("\\label{sec:boundaries}")[1].split("\\section{Discussion}")[0]
    f = _flat(sec)
    assert "regime-specific r $= -$0.67 to $-$0.70".lower() in f
    assert "pooled over the three regimes r $= -$0.57".lower() in f
    assert "regime-specific r $= -$0.01 to $+$0.05".lower() in f and "pooled $+$0.02" in f
    cap = MAIN.split("\\label{fig:9}")[0].rsplit("\\caption{", 1)[1]
    fc = _flat(cap)
    assert "pooled" in fc and "$r=-0.57$ and $-0.59$" in cap and "$+0.02$ and $+0.01$" in cap
    assert "computed within each regime and are a different statistic" in fc
    assert "the mechanism figure" not in fc
    # section 6 must use the same statistic and scope, not the exploratory +0.06
    disc = MAIN.split("\\section{Discussion}")[1]
    assert "r $\\approx$ +0.06" not in disc
    assert "regime-specific $r$ between $-0.01$ and $+0.05$ at 250 logged triggers, pooled $+0.02$" in disc
    # non-causal status stated narrowly (no new analysis inserted)
    assert "does not identify a causal mechanism" in f
    assert "regression to the mean" not in f


def test_quarter_of_commits_replaced_by_exact_sealed_value():
    dm = pd.read_csv(T / "paper2_decision_quality_004" / "decision_metrics.csv")
    rate = float(dm[dm.regime == "POOLED"].harmful_commit_rate.iloc[0])
    assert round(rate * 100) == 23
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE), ("main_springer.tex", SPRINGER)):
        assert "quarter of its commits" not in t, name
        assert "23\\% of its commits had negative realized value" in t, name
    risk = MAIN.split("\\label{sec:riskgates}")[1].split("\\section{Experimental design}")[0]
    assert "S2.10" in risk


# ---------------------------------------------------------------- E: chronological replay count
def test_chronological_replay_count_seven_plus_six():
    c = pd.read_csv(T / "paper2_final_q1" / "chronological_replays.csv")
    assert c.stream.nunique() == 7
    assert "Seven pre-enumerated" in CHRONO and "final-q1" not in CHRONO
    sec = MAIN.split("\\label{sec:boundaries}")[1].split("\\section{Discussion}")[0]
    f = _flat(sec)
    assert ("thirteen registered replays on real, chronologically ordered streams were evaluated "
            "in total: the seven of the pre-enumerated final matrix reported in table~\\ref{tab:"
            "chronological_q1} (seeds 601--630) and six earlier registered replays reported in "
            "supplementary \\s s2.6") in f
    assert "7 in Table~\\ref{tab:chronological_q1}, 6 earlier" in MAIN
    assert "(seven in the registered final matrix, six earlier)" in MAIN
    s26 = SUPP.split("Chronological replays: the full per-replay account")[1][:12000]
    assert "sixth registered replay" in s26 and "these six replays" in s26


# ---------------------------------------------------------------- F: DDM / ADWIN scope
def test_monitor_cells_scoped_to_reference_parameters():
    cfg = json.loads((REPO / "configs" / "post_kbs_common_harness_baselines_v2.json").read_text(encoding="utf-8"))
    for pol in ("ddm", "adwin"):
        flags = cfg["policies"][pol]["flags"]
        assert flags["--monitor-labels"] == "8"
        assert not any(k.startswith("--adwin") or k.startswith("--ddm") for k in flags), pol
    src = (REPO / "src" / "experiments" / "run_paper2_readaptation_v2.py").read_text(encoding="utf-8")
    assert "river_drift.binary.DDM()" in src and "river_drift.ADWIN(delta=0.002)" in src
    for name, t in (("main.tex", MAIN), ("main_ieee.tex", IEEE), ("main_springer.tex", SPRINGER)):
        f = _flat(t)
        assert f.count("reference parameters") >= 3, name
        assert "the monitors were not tuned" in f, name
        assert "adwin $\\delta=0.002$" in f, name
        assert "a parameter sweep would be required before reading them as properties of the methods" in f, name
        for banned in ("adwin is ineffective", "ddm is harmful", "adwin fails", "ddm fails"):
            assert banned not in f, (name, banned)


# ---------------------------------------------------------------- 8/9: scenarios, margin
def test_one_scenario_per_benchmark_and_margin_scope():
    for cfg_name, expect in (("symmetric_pipeline_dynamic_v1.json", 6),
                             ("size_matched_own_transformer_v1.json", 3),
                             ("post_kbs_common_harness_baselines_v2.json", 6)):
        cfg = json.loads((REPO / "configs" / cfg_name).read_text(encoding="utf-8"))
        assert set(cfg["data"]) == {"portscan", "unsw_recon", "ton_scanning"}, cfg_name
        assert len(cfg["scenarios"]) == expect, cfg_name
    b2 = json.loads((REPO / "configs" / "post_kbs_size_matched_drift_v1.json").read_text(encoding="utf-8"))
    assert b2["scenarios"] == ["ps_full", "unsw_full", "ton_full"]
    f = _flat(MAIN)
    assert ("uses exactly one primary scenario per benchmark --- cicids2017 portscan, unsw-nb15 "
            "reconnaissance and ton-iot scanning") in f
    assert "the exploratory stage spans all seven regimes" in f
    assert "equals the materiality threshold" in f  # kept for the claim audit
    assert ("study-level preregistered materiality and equivalence threshold, not a universal "
            "operational security threshold") in f
    assert "flows per day" not in f and "flows/day" not in f


# ---------------------------------------------------------------- 13: abstract
def test_abstract_without_bare_atc_and_with_security_clause():
    a = _abstract(MAIN)
    n = len(a.split())
    assert 200 <= n <= 235, n
    assert "ATC" not in a and "DoC" not in a
    assert "label-free estimator" in a
    assert "Promotion is security-relevant" in a
    f = _flat(a)
    for s in ("threat model", "adversar", "poison", "attacker"):
        assert s not in f, s
    for s in ("materially benchmark-dependent rather than homogeneous",
              "policy conclusions were partially robust", "no policy globally dominated"):
        assert s in f, s


# ---------------------------------------------------------------- 7: security significance
def test_security_significance_minimal_with_explicit_out_of_scope():
    f = _flat(MAIN)
    intro = _flat(MAIN.split("\\section{Introduction}")[1].split("\\section{Related work}")[0])
    assert "security-relevant integrity decision" in intro
    disc = _flat(MAIN.split("\\section{Discussion}")[1].split("\\section{Limitations}")[0])
    assert "security significance and scope" in disc
    assert ("the present experiments do not model an adversary manipulating the update process"
            in disc)
    assert "the evaluated validation policies are not claimed as poisoning defenses" in disc
    assert "\\cite{biggio2012poisoning}" in MAIN
    for banned in ("defends against poisoning", "poisoning defense that", "robust to poisoning",
                   "threat model of this paper", "we formalize the threat"):
        assert banned not in f, banned
    kw = re.search(r"\\begin\{keywords\}(.*?)\\end\{keywords\}", MAIN, re.S).group(1)
    assert "poison" not in kw.lower()
    title = re.search(r"\\title\[mode=title\]\{(.*?)\}\n", MAIN, re.S).group(1)
    assert title == ("Candidate Comparability Before Promotion: Conditional Validation in Adaptive "
                     "Network Intrusion Detection")


# ---------------------------------------------------------------- 11: jargon / terminology
def test_internal_artifact_identifiers_out_of_main_paper():
    body = _body(MAIN)
    for tag in ("amendment-008", "v1.20.2", "v1.21.0", "post-v1.22", "final-q1", "authorized-mode",
                "verified virgin", "harness v2", "harness (v2)", "v2 harness", "clean source tree",
                "harness-v2-protocol", "(in the artifact)", "own-transformer", "Algorithm 1A",
                "Algorithm 1B", "quarter of its commits"):
        assert tag not in body, tag
    # the Data-availability statement names artifact versions by necessity, but not with the
    # internal 'post-v1.22' shorthand
    assert "post-v1.22" not in MAIN and "artifact version v1.24.0" in MAIN
    assert "previous v1.23.0 release remains immutable" in MAIN
    for t in (SYN, CHRONO):
        assert "final-q1" not in t and "amendment-008" not in t
    # a single reader-facing name per policy in the gate definitions
    gates = MAIN.split("\\label{sec:gates}")[1].split("\\label{sec:riskgates}")[0]
    for s in ("\\textbf{always-deploy} (\\texttt{none}; written \\emph{naive} in estimand names and tables)",
              "\\textbf{point gate} (\\texttt{labeled\\_probe}", "\\textbf{strict gate}",
              "\\textbf{disagreement gate} (\\texttt{unsup\\_disagree}"):
        assert s in gates, s
    assert "\\emph{challenger} for the model itself and \\emph{candidate} for its role" in MAIN


def test_algorithm_is_a_captioned_figure_in_all_ports():
    assert "\\label{fig:algorithm}" in MAIN and "Fig.~\\ref{fig:algorithm}" in MAIN
    for name, t in (("main_ieee.tex", IEEE), ("main_springer.tex", SPRINGER)):
        i = t.index("\\label{fig:algorithm}")
        start = t.rfind("\\begin{figure*}", 0, i)
        end = t.index("\\end{figure*}", i)
        block = t[start:end]
        assert "\\begin{verbatim}" in block and "\\caption{" in block, name
        assert block.count("\\begin{figure*}") == 1, name  # the port must not nest a second float


# ---------------------------------------------------------------- 10: IJIS format defects
def test_springer_port_format_fixes():
    lines = SPRINGER.splitlines()
    assert "spmpsci.bst" in lines[2] and "spphys" not in lines[2]
    assert "\\paragraph{Consent for publication} Not applicable" in SPRINGER
    i = SPRINGER.index("\\label{tab:evidence_map}")
    assert SPRINGER.rfind("\\begin{table*}", 0, i) > SPRINGER.rfind("\\begin{table}", 0, i)
    i = IEEE.index("\\label{tab:evidence_map}")
    assert IEEE.rfind("\\begin{table*}", 0, i) > IEEE.rfind("\\begin{table}", 0, i)
    fig = (REPO / "src" / "analysis" / "make_paper2_pertrigger_figure.py").read_text(encoding="utf-8")
    assert "suptitle" not in fig and "set_title" not in fig
    bundle = (REPO / "src" / "analysis" / "make_ijis_submission_bundle.py").read_text(encoding="utf-8")
    assert "the corresponding sections" not in bundle and "_section_numbers" in bundle
    cover = (REPO / "notes" / "ijis_cover_letter.md").read_text(encoding="utf-8")
    assert "Published conclusions about adaptive" not in cover
    assert "exact-cleaned-feature-disjoint sensitivity" in cover.replace("\n", " ")
    assert "simulated reviewer" not in cover.lower() and "KBS" not in cover


# ---------------------------------------------------------------- registered outcomes unchanged
def test_registered_outcomes_unchanged():
    b2 = json.loads((T / "post_kbs_size_matched_drift_001" / "CLAIM_INTERPRETATION.json").read_text(encoding="utf-8"))
    assert b2["outcome"] == "HOMOGENEOUS-SIZE BENEFIT"
    sm = json.loads((T / "size_matched_own_transformer_001" / "CLAIM_INTERPRETATION.json").read_text(encoding="utf-8"))
    assert sm.get("outcome") == "ATTENUATION"
    mult = pd.read_csv(T / "post_kbs_size_matched_drift_001" / "multiplicity.csv").set_index("contrast")
    g3 = mult[mult.index.str.contains(r"-2000 vs naive-2000")]
    assert len(g3) == 6 and int(((g3.effect_pp > 0) & g3.significant_holm).sum()) == 0
    f = _flat(MAIN)
    for s in ("homogeneous-size benefit", "0/6", "attenuation", "+0.82", "+1.66", "+1.00",
              "does not retroactively change"):
        assert s in f, s
