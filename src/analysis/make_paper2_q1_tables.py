"""final-q1: emit the LaTeX tables for the Fase C/D results into manuscript/tables{,_ieee}/.

  tab:budget_frontier  -- the registered lifetime budget frontier (D3 endpoints e1-e6)
  tab:ab_equivalence   -- the confirmatory A/B with CI-based equivalence verdicts + scaler/PCA decomposition
Reads only the frozen CSVs under results/tables/paper2_final_q1 and paper2_final_kbs, so
every number in the manuscript traces to an artifact file.
"""
from __future__ import annotations

import os

import pandas as pd

Q1 = "results/tables/paper2_final_q1"
FK = "results/tables/paper2_final_kbs"
OUTS = ["manuscript/tables", "manuscript/tables_ieee"]
POL_NAME = {"ebcsdef": "Pooled EB-CS + defer", "vbccoh": "VBC-SG-Cohort",
            "vbcref": "VBC-SG-Refresh"}
STAR = "*"


def write(name: str, body: str) -> None:
    for d in OUTS:
        os.makedirs(d, exist_ok=True)
        star = body if d.endswith("tables") else body.replace("{table}", "{table*}")
        open(f"{d}/{name}", "w", encoding="utf-8", newline="\n").write(star)
    print(f"wrote {name}")


def budget_frontier() -> None:
    R = pd.read_csv(f"{Q1}/budget_frontier.csv")
    A = pd.read_csv(f"{Q1}/frontier_anchors.csv")
    ps = R[(R.scenario == "ps_full") & (R.schedule == "bonf")]
    zero = R[(R.scenario == "ton_zero") & (R.schedule == "bonf")]
    naive = float(A[(A.scenario == "ps_full") & (A.policy == "none")].gain.iloc[0])
    strict = A[(A.scenario == "ps_full") & (A.policy == "strict")].iloc[0]
    strict_z = A[(A.scenario == "ton_zero") & (A.policy == "strict")].iloc[0]
    point_z = A[(A.scenario == "ton_zero") & (A.policy == "point")].iloc[0]

    rows = []
    for pol in ("ebcsdef", "vbccoh", "vbcref"):
        for cap in (64, 128, 256, 512, 1024):
            r = ps[(ps.policy == pol) & (ps.cap == cap)]
            z = zero[(zero.policy == pol) & (zero.cap == cap)]
            if not len(r) or not len(z):
                continue
            r = r.iloc[0]; z = z.iloc[0]
            frac = "" if r.commits_total == 0 else f"{100*r.e2_frac_naive:.0f}\\%"
            rows.append(f"{POL_NAME[pol]} & {cap} & ${r.gain:+.2f}$ & {frac} & "
                        f"{r.labels_probe_per_proposal:.0f} & {r.e4_abstention:.2f} & "
                        f"{r.e5_delay_windows:.1f} & {int(z.commits_total)} \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    tex = f"""\\begin{{table}}[t]
\\centering
\\caption{{\\textbf{{The registered budget frontier for the deployment-long guarantee (final-q1).}}
Lifetime-budgeted risk gates ($\\alpha_{{\\mathrm{{life}}}}{{=}}0.10$, Bonferroni spending; the
$p$-series schedule is within $0.1$ points throughout and is in the artifact), pristine seeds
501--530. \\emph{{Gain}} is balanced-accuracy points over never-adapting on CICIDS-PortScan at
full drift, where always-deploying gains ${naive:+.2f}$; \\emph{{\\% naive}} is the fraction of
that benefit recovered; \\emph{{labels}} are probe labels per proposal (candidate \\emph{{training}}
already costs 1{{,}}024); \\emph{{abst.}} is the fraction of proposals resolved as neither commit
nor futility; \\emph{{delay}} is deferral windows to a decision; the last column is commits under
\\emph{{zero drift}} across 91 proposals. The pre-declared non-vacuity target (commits,
$\\ge$50\\% of naive, zero zero-drift commits, $<$1{{,}}024 labels) is met by twelve
configurations across both alpha-spending schedules (the seven Bonferroni rows shown here plus
five $p$-series) --- the deployment-long guarantee is a matter of budget, not of the rule. For
reference, the no-additional-label strict gate (same probe as the point gate, no extra labels) scores ${strict.gain:+.2f}$ here and ${strict_z.gain:+.2f}$
under zero drift (vs the point gate's ${point_z.gain:+.2f}$).}}
\\label{{tab:budget_frontier}}
\\small
\\begin{{tabular}}{{l r r r r r r r}}
\\toprule
Policy & cap & gain & \\% naive & labels & abst. & delay & zero-drift commits \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    write("table_budget_frontier.tex", tex)


def ab_equivalence() -> None:
    E = pd.read_csv(f"{FK}/ab_equivalence.csv")
    C = pd.read_csv(f"{FK}/symmetric_ab_conf2001_2100.csv")
    prim = E[(E.analysis == "primary_confirmatory") & (E.margin == 1.0)]
    dsname = {"portscan": "CICIDS-PortScan", "unsw_recon": "UNSW-Recon",
              "ton_scanning": "ToN-IoT"}
    cname = {"independent": "Independent transformer",
             "own_transformer": "Own transformer per model",
             "inc_scaler_indep_pca": "Incumbent \\emph{scaler}, independent PCA",
             "indep_scaler_inc_pca": "Independent scaler, incumbent \\emph{PCA}"}
    # pilot (30 seeds) carries the two ownership-inversion conditions, which the confirmatory
    # run did not repeat; they are labelled as pilot so the two seed sets are never conflated
    P = pd.read_csv(f"{FK}/symmetric_ab.csv")
    pil = P[(P.contrast == "rand") & (P.model == "svc_rbf")]
    rows = []
    for cond in ("independent", "own_transformer"):
        for ds in ("portscan", "unsw_recon", "ton_scanning"):
            r = prim[(prim.condition == cond) & (prim.dataset == ds)]
            if not len(r):
                continue
            r = r.iloc[0]
            v = "\\textbf{equivalent}" if r.equivalent else "not established"
            rows.append(f"{cname[cond]} & {dsname[ds]} & ${r.mean_gap:+.2f}$ & "
                        f"[${r.ci90_lo:+.2f}$, ${r.ci90_hi:+.2f}$] & {v} \\\\")
        rows.append("\\addlinespace")
    for cond in ("inc_scaler_indep_pca", "indep_scaler_inc_pca"):
        r = prim[(prim.condition == cond) & (prim.dataset == "ton_scanning")]
        if len(r):
            r = r.iloc[0]
            v = "\\textbf{equivalent}" if r.equivalent else "not established"
            rows.append(f"{cname[cond]} & {dsname['ton_scanning']} & ${r.mean_gap:+.2f}$ & "
                        f"[${r.ci90_lo:+.2f}$, ${r.ci90_hi:+.2f}$] & {v} \\\\")
    rows.append("\\addlinespace")
    rows.append("\\multicolumn{5}{l}{\\emph{Ownership inversion (pilot, 30 seeds; CI95)}} \\\\")
    for cond, lab in (("incumbent_fit", "Transformer fitted on the \\emph{incumbent}"),
                      ("challenger_fit", "Transformer fitted on the \\emph{challenger}")):
        r = pil[(pil.condition == cond) & (pil.dataset == "ton_scanning")]
        if len(r):
            r = r.iloc[0]
            rows.append(f"{lab} & {dsname['ton_scanning']} & ${r.gap:+.2f}$ & "
                        f"[${r.lo:+.2f}$, ${r.hi:+.2f}$] & --- \\\\")
    body = "\n".join(rows)
    tex = f"""\\begin{{table}}[t]
\\centering
\\caption{{\\textbf{{Confirmatory symmetric A/B with equivalence testing and a mechanism
decomposition (final-q1).}} Role-randomized challenger$-$incumbent gap (balanced-accuracy
points) on globally value-deduplicated, disjoint blocks, SVC-RBF, on 100 \\emph{{fresh}}
confirmatory seeds (2001--2100); the original 30 seeds are re-labelled a pilot and excluded
here. Equivalence is a bootstrap CI-based assessment at the pre-registered $\\pm1.0$-point
materiality margin --- declared iff the 90\\% seed-level bootstrap interval lies inside the
margin, the interval-inclusion form of TOST; ``not established'' means the gap is unresolved
\\emph{{and}} too imprecise to declare practically zero --- not that an effect was shown. The
middle block decomposes transformer ownership: giving the incumbent only the
\\emph{{standardizer}} reproduces essentially the whole ownership advantage, while giving it
only the \\emph{{PCA}} does not, which localizes the mechanism to the feature scaling that
sets the RBF kernel's geometry. The final block is the ownership \\emph{{inversion}} from the
30-seed pilot --- the load-bearing identification evidence, kept separate because those seeds
generated the hypothesis: whichever model's data fits the transformer gains the advantage.}}
\\label{{tab:ab_equivalence}}
\\small
\\begin{{tabular}}{{l l r l l}}
\\toprule
Condition & Benchmark & gap & CI90 & equivalence ($\\pm1.0$) \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    write("table_ab_equivalence.tex", tex)


def chronological() -> None:
    R = pd.read_csv(f"{Q1}/chronological_replays.csv")
    label = {"tue_wedthufri": "Tue $\\to$ Wed+Thu+Fri", "wed_fri": "Wed $\\to$ Fri",
             "thu_fri": "Thu $\\to$ Fri", "wed_intraday": "Wed intra-day",
             "thu_intraday": "Thu intra-day", "unsw_20": "UNSW (train 20\\%)",
             "unsw_40": "UNSW (train 40\\%)"}
    pol = {"none": "naive", "point": "point", "strict": "strict", "vbccoh": "VBC-SG"}
    rows = []
    for s in label:
        sub = R[R.stream == s]
        if not len(sub):
            continue
        na = sub.iloc[0].noadapt_ba
        cells = []
        for p in ("none", "point", "strict", "vbccoh"):
            r = sub[sub.policy == p]
            cells.append(f"${100*r.iloc[0].gain_ba:+.2f}$" if len(r) else "---")
        rows.append(f"{label[s]} & {100*na:.1f} & " + " & ".join(cells) + " \\\\")
    body = "\n".join(rows)
    tex = f"""\\begin{{table}}[t]
\\centering
\\caption{{\\textbf{{The registered chronological matrix (final-q1).}} Seven pre-enumerated
replays on genuinely time-ordered captures --- every train$\\to$future day pair of CICIDS2017
with an attack-bearing training day, two intra-day splits, and the UNSW-NB15 timeline at two
training fractions --- each processed as 200 windows of 256 flows in capture order, seeds
601--630. Columns are balanced-accuracy points over never-adapting (two-class windows only);
\\emph{{no-adapt}} is the frozen incumbent's absolute BA, the health indicator that governs
which regime a stream is in. \\textbf{{No stream shows net harm}}, consistent with the six
earlier replays. Where the incumbent collapses (CICIDS), updating helps a lot and the gates
cost almost nothing; where it stays healthy (both UNSW timelines), the point and strict gates are
\\emph{{above}} always-deploying (VBC-SG on the 20\\% split but not the 40\\% split), and the
no-additional-label strict rule is the best of the three.}}
\\label{{tab:chronological_q1}}
\\small
\\begin{{tabular}}{{l r r r r r}}
\\toprule
Replay & no-adapt BA & naive & point & strict & VBC-SG \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    write("table_chronological_q1.tex", tex)


def operational() -> None:
    R = pd.read_csv(f"{Q1}/operational_e2e.csv")
    base = R[(R.cand_latency == 5) & (R.train_delay == 0)]
    dsn = {"portscan": "CICIDS-PortScan", "ton": "ToN-IoT"}
    acqn = {"random": "Random inspection", "alert_enriched": "Alert-enriched",
            "disagreement": "Disagreement", "hybrid": "Hybrid"}
    rows = []
    for ds in ("portscan", "ton"):
        for acq in ("random", "alert_enriched", "disagreement", "hybrid"):
            cells = []
            for pi in (0.005, 0.01, 0.05, 0.10):
                r = base[(base.dataset == ds) & (base.prevalence == pi)
                         & (base.acquisition == acq)]
                v = r.iloc[0].discovery_flows_per_attack if len(r) else float("nan")
                cells.append(f"{v:.0f}" if v == v else "---")
            rows.append(f"{dsn[ds]} & {acqn[acq]} & " + " & ".join(cells) + " \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    tex = f"""\\begin{{table}}[t]
\\centering
\\caption{{\\textbf{{Attack-label acquisition yield under operational prevalence (final-q1).}}
Inspected flows per adjudicated \\emph{{attack}} label found in the auxiliary
\\emph{{discovery}} queue of a pool-based operational acquisition-yield simulation (seeds
801--830; the earlier 701--730 window is a pilot). Adjudication candidates are drawn at
operating prevalence $\\pi$ and every probe label arrives five windows late; the evaluation
stream and detector calibration remain balanced, and the candidate training batch remains
balanced per class with its acquisition cost \\emph{{not}} modeled --- so this arm measures
label-acquisition yield, not the end-to-end cost of the commit decision. The adjudication
budget is split in two: the enriched discovery half measures attack-\\emph{{finding}} yield
only, while an independent \\emph{{uniform}} validation half at operating prevalence is the
only sample the commit rule is shown (32 adjudications per decision, compared by plain
accuracy; at extreme prevalence it may contain no attacks) --- so an enriched sample is never
used as an estimate of deployed performance, and enrichment neither reduces the validation
adjudications nor cheapens the commit decision itself. Acquisition policies rank candidate
flows by model \\emph{{predictions}} only, never by ground truth, so they are implementable:
an analyst inspects the queue the deployed detector already produces. Alert-enriched
inspection \\emph{{finds an attack}} 5--8$\\times$ more cheaply than random inspection at
every prevalence, and hybrid 3--6$\\times$; ranking by candidate/incumbent
\\emph{{disagreement}} barely helps, because the two models differ near the decision boundary
rather than on the minority class. The honest headline: the decision still requires its 32
uniform validation adjudications; what enrichment changes is the cost of \\emph{{finding
attack labels}} in the discovery queue, at the yields tabulated here.}}
\\label{{tab:operational_e2e}}
\\small
\\begin{{tabular}}{{l l r r r r}}
\\toprule
 & & \\multicolumn{{4}}{{c}}{{flows inspected per attack label, at $\\pi =$}} \\\\
\\cmidrule(lr){{3-6}}
Benchmark & Acquisition & 0.005 & 0.01 & 0.05 & 0.10 \\\\
\\midrule
{body}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
    write("table_operational_e2e.tex", tex)


if __name__ == "__main__":
    budget_frontier()
    ab_equivalence()
    chronological()
    operational()
