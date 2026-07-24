"""final-q1 mandatory tests: evidence tiers, strict baseline, latency documentation, and
main/supplement consistency (protocol q1_max_protocol.md)."""
from __future__ import annotations

import json
import re

import pytest

from tests.conftest import REPO

MAIN = (REPO / "manuscript" / "main.tex")
SUPP = (REPO / "manuscript" / "supplement.tex")


def test_evidence_tier_labels():
    # KBS final scope reduction: the full six-tier taxonomy moved to Supplement S0 (evidence
    # hierarchy and provenance); the main body keeps a single "Evidence stages" paragraph
    # pointing to it. The taxonomy and its markers are pinned in the supplement.
    text = SUPP.read_text(encoding="utf-8")
    assert "Six tiers of evidence" in text
    for marker in ("Registered confirmatory core", "Registered symmetric-pipeline replication",
                   "Registered follow-ups",
                   "Feasibility, of two kinds", "External boundary", "Exploratory"):
        assert marker in text, f"evidence tier missing: {marker}"
    # the confirmatory replications must be labeled internal; "external replication" may only
    # appear negated ("not an external replication"/"not external validations")
    assert re.search(r"\\emph\{internal\} replication", text)
    lowered = text.lower().replace("not an external replication", "")
    assert "external replication" not in lowered
    # the main body must carry the compact provenance pointer, not the full taxonomy
    main = MAIN.read_text(encoding="utf-8")
    assert "Evidence stages" in main and "Supplementary \\S S0" in main


def test_strict_baseline_present():
    causal = (REPO / "manuscript" / "tables" / "table_causal_probe.tex").read_text(encoding="utf-8")
    assert "strict" in causal.lower(), "strict gate missing from the causal comparison table"
    zero = (REPO / "manuscript" / "tables" / "table_zero_drift.tex").read_text(encoding="utf-8")
    main = MAIN.read_text(encoding="utf-8")
    assert "reject-ties" in main or "strict" in zero.lower()


def test_latency_manifest_matches_manuscript():
    text = MAIN.read_text(encoding="utf-8")
    assert "tab:latency" in text, "latency semantics table missing from the manuscript"
    for knob in ("--probe-latency", "--candidate-latency", "--defer-windows"):
        assert knob.replace("--", "") in text.replace("-", "").replace("\\", "") or knob in text
    mf = REPO / "results" / "final_manifest.json"
    if not mf.exists():
        pytest.skip("final_manifest.json not yet generated in this checkout")
    m = json.loads(mf.read_text(encoding="utf-8"))
    lat = m["label_latencies"]
    assert set(lat["probe"]) >= {0, 5, 20}
    assert set(lat["candidate"]) >= {0, 5, 20}


def test_main_supplement_consistency():
    main = MAIN.read_text(encoding="utf-8")
    supp = SUPP.read_text(encoding="utf-8")
    # every "S5.x of the main paper" pointer must target an existing main subsection of Sec. 5
    n_results_subsecs = len(re.findall(r"\\subsection\{", main.split(r"\section{Results}")[1]
                                       .split(r"\section{Discussion}")[0]))
    for m in re.finditer(r"\\S5\.(\d+) of the main paper", supp):
        assert int(m.group(1)) <= n_results_subsecs, f"dead pointer: S5.{m.group(1)}"
    # Proposition 1's proof must exist in the supplement and be referenced from the main body
    assert "Proposition 1" in main and "Proof of Proposition 1" in supp
    assert "S4" in main.split("Proposition 1")[1][:2000]


def test_abstract_length_within_venue_limit():
    """Fase-F regression guard (finding F2): the abstract had grown to 533 words across
    amendments, more than double the venue norm, which is a desk-reject risk. It is rewritten
    to ~265; this test fails if it drifts materially above the limit again."""
    text = MAIN.read_text(encoding="utf-8")
    abstract = text.split(r"\begin{abstract}")[1].split(r"\end{abstract}")[0]
    stripped = re.sub(r"\\[a-zA-Z]+\*?", " ", abstract)
    stripped = re.sub(r"[{}$\\]", " ", stripped)
    stripped = re.sub(r"-{2,}", " ", stripped)
    n = len(stripped.split())
    assert n <= 290, f"abstract is {n} words; the venue norm is ~250 (hard guard at 290)"


def test_chronological_replay_count_consistent():
    """Fase-F regression guard (finding F3): 'six replays' lingered in the contributions,
    the evidence tiers and Limitations after the matrix grew to thirteen. Any mention of a
    replay TOTAL must say thirteen; 'these six' scoping the first set is allowed."""
    text = MAIN.read_text(encoding="utf-8")
    scoping = ("these", "initial", "above", "first set")
    bad = []
    for m in re.finditer(r"\b[Ss]ix (?:registered |real )?(?:chronological )?replays", text):
        window = text[max(0, m.start() - 60): m.end() + 60].lower()
        if not any(w in window for w in scoping):
            bad.append(text[m.start():m.end()])
    assert not bad, (f"unscoped mention(s) of six replays: {bad} — the matrix has thirteen; "
                     "a mention of the first set must scope itself ('these', 'initial', 'above')")


def test_frontier_headline_not_misattributed():
    """Fase-F regression guard (finding F7): 93% of naive's benefit is the POOLED EB-CS
    variant; the fully stratified VBC-SG reaches 81%. Wherever the 93% headline appears
    outside the results section, the 81% qualifier must appear nearby."""
    for doc in ("manuscript/main.tex", "README.md"):
        text = (REPO / doc).read_text(encoding="utf-8")
        for m in re.finditer(r"93\\?%", text):
            window = text[max(0, m.start() - 400): m.start() + 400]
            assert "81" in window, (
                f"{doc}: the 93% frontier headline appears without the 81% stratified "
                "qualifier nearby — that misattributes a pooled result to VBC-SG")


def test_lifetime_policy_nonvacuity_reported():
    frontier = REPO / "results" / "tables" / "paper2_final_q1" / "budget_frontier.csv"
    if not frontier.exists():
        pytest.skip("budget frontier (Fase C) not yet run")
    text = MAIN.read_text(encoding="utf-8")
    assert ("formal risk endpoint" in text) or ("non-vacuous" in text) or \
           ("nonvacuous" in text), \
        "Fase C ran but the manuscript reports neither a non-vacuous operating point nor " \
        "the registered endpoint sentence"


def test_ab_bootstrap_is_deterministic():
    """final-q1 blocker E3: the equivalence bootstrap must be reproducible ACROSS PROCESSES.

    It previously seeded from Python's built-in hash(), which is salted per interpreter run,
    so two runs of the artifact produced different confidence intervals. The seed is now a
    SHA-256 digest of the key; this test pins that property directly."""
    import subprocess
    import sys as _sys
    from src.analysis.paper2_ab_equivalence import stable_seed

    key = ("ton_scanning", "svc_rbf", "independent", "primary_confirmatory", 1.0)
    here = stable_seed(*key)
    # a *separate interpreter* must produce the same seed (hash() would not)
    out = subprocess.run(
        [_sys.executable, "-c",
         "from src.analysis.paper2_ab_equivalence import stable_seed;"
         f"print(stable_seed(*{key!r}))"],
        cwd=REPO, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-800:]
    assert int(out.stdout.strip()) == here, "bootstrap seed is not stable across processes"
    assert "hash((" not in (REPO / "src" / "analysis" / "paper2_ab_equivalence.py").read_text(
        encoding="utf-8"), "built-in hash() reintroduced as a seed source"


CAUSAL_SCOPE_BANNED = [
    (r"end-to-end causal", "'causal' is reserved for the observed-data arm (no sev(t), no pools)"),
    (r"causal (?:end-to-end|operational|prevalence|acquisition)",
     "the operational simulation draws from the pools; it is not the causal arm"),
    (r"operational[- ]causal", "same: do not fuse the two arms"),
]


def test_causal_label_reserved_for_observed_data_arm():
    """final-q1 blocker 5: 'causal'/'observed-data' must denote ONLY the arm that reads
    neither the true severity nor the environment pools. The operational label-acquisition
    and delay simulation runs inside the pool-based harness and must never be called causal."""
    hits = []
    for doc in ("manuscript/main.tex", "manuscript/main_ieee.tex", "README.md", "REPRODUCE.md"):
        text = (REPO / doc).read_text(encoding="utf-8")
        for pat, why in CAUSAL_SCOPE_BANNED:
            for m in re.finditer(pat, text, flags=re.IGNORECASE):
                hits.append(f"{doc}: {m.group(0)!r} ({why})")
    assert not hits, "causal/operational scope conflated:\n" + "\n".join(hits)


def test_multiplicity_policy_matches_what_was_applied():
    """final-q1 Fase F: the manuscript's stated multiplicity policy must match the analysis
    that actually ran. Sol's rule: the audit fails if the paper says 'without multiplicity
    correction' while Holm/BH were applied, or claims Holm/BH without the table existing."""
    import pandas as pd
    text = MAIN.read_text(encoding="utf-8")
    says_holm = "Holm" in text
    says_bh = "Benjamini" in text
    says_none = "without multiplicity correction" in text
    f = REPO / "results" / "tables" / "paper2_final_q1" / "multiplicity.csv"
    if not f.exists():
        assert not (says_holm or says_bh), \
            "the paper claims Holm/BH but results/.../multiplicity.csv does not exist"
        return
    M = pd.read_csv(f)
    applied = set(M.method.unique())
    assert ("Holm" in applied) == says_holm, "Holm claim and Holm application disagree"
    assert ("Benjamini-Hochberg" in applied) == says_bh, "BH claim and BH application disagree"
    assert not says_none, ("the paper still says 'without multiplicity correction' while "
                           "corrections were applied")
    # and the headline that no conclusion depends on the correction must actually hold
    nominal = M[M.p_raw < 0.05]
    assert bool(nominal.significant_adj.all()), (
        "the paper says every nominally significant contrast survives adjustment, but "
        f"{int((~nominal.significant_adj).sum())} do not")


def test_chronological_healthy_claim_matches_data():
    """final-q1 (recommendable): the healthy-incumbent chronological claim must match the CSV.

    A published abstract said "on timelines that keep the incumbent healthy EVERY gate beats
    always-deploying". It was false twice over: on the Wednesday intra-day replay no gate
    beats naive, and on UNSW-40 the VBC-SG variant does not either. This guard recomputes the
    fact from the artifact and fails if the manuscript universalises it again."""
    import pandas as pd
    f = REPO / "results" / "tables" / "paper2_final_q1" / "chronological_replays.csv"
    if not f.exists():
        pytest.skip("chronological matrix not yet aggregated")
    C = pd.read_csv(f)
    healthy = sorted({s for s in C.stream.unique()
                      if float(C[C.stream == s].noadapt_ba.iloc[0]) >= 0.80})
    all_beat = []
    for s in healthy:
        sub = C[C.stream == s]
        naive = float(sub[sub.policy == "none"].gain_ba.iloc[0])
        gates = {p: float(sub[sub.policy == p].gain_ba.iloc[0])
                 for p in ("point", "strict", "vbccoh") if len(sub[sub.policy == p])}
        all_beat.append(all(g > naive for g in gates.values()))
    universal = all(all_beat)
    text = MAIN.read_text(encoding="utf-8")
    # Substring logic rather than a regex: LaTeX markup between the words
    # ("every gate \emph{beats}") makes a pattern brittle, and a guard that silently fails
    # to match is worse than no guard at all -- this one did, and was caught by testing it
    # against the false claim before trusting it.
    low = text.lower()
    # Every way we have actually written this claim wrong so far. "every gate" was the first;
    # "all three gates" slipped past a guard that only knew the first phrasing, which is why
    # the set is explicit and the test is checked against each variant.
    UNIVERSALS = ("every gate", "all three gates", "all gates", "all the gates",
                  "each gate", "all four gates")
    claims_universal = False
    for _m in re.finditer("healthy", low):
        # Sentence boundary = period followed by whitespace. A bare "." split truncates on
        # decimals like "82.9\%" and silently blinded an earlier version of this guard.
        window = re.split(r"\.\s", low[_m.end(): _m.end() + 200])[0]
        if any(u in window for u in UNIVERSALS) and "beat" in window:
            claims_universal = True
            break
    assert claims_universal == universal, (
        f"manuscript claims every gate beats naive on healthy timelines = {claims_universal}, "
        f"but the data say {universal} (healthy streams: {healthy}); "
        "at least one healthy replay has a gate that does not beat always-deploying")


def test_manifest_completeness_final_q1():
    """final-q1 blocker 4: the manifest must carry the fields the reviewer enumerated --
    prevalence 0.005, training delays {0,5}, the immediate/deferred harm split, the ledger --
    so a reader can check the artifact's scope without reading the code."""
    import json as _json
    mf = REPO / "results" / "final_manifest.json"
    if not mf.exists():
        pytest.skip("final_manifest.json not generated")
    m = _json.loads(mf.read_text(encoding="utf-8"))
    assert 0.005 in m["prevalences"]["operational"], "pi=0.005 missing from the manifest"
    assert set(m["training_delay_windows"]) == {0, 5}, "training delays {0,5} missing"
    h = m["harmful_commits"]
    for k in ("commits_total", "immediate", "deferred", "evaluable_h5", "censored_h5",
              "harmful_h5", "harmful_immediate", "harmful_deferred"):
        assert k in h, f"harm accounting field missing: {k}"
    assert h["immediate"] + h["deferred"] == h["commits_total"], "commit split does not sum"
    assert h["evaluable_h5"] + h["censored_h5"] == h["commits_total"], \
        "every commit must be evaluable or censored"
    assert h["harmful_immediate"] + h["harmful_deferred"] == h["harmful_h5"]
    led = m["experiment_ledger"]
    assert led["missing_blocks"] == [], f"ledger blocks with no outputs: {led['missing_blocks']}"
    # M3: no final-q1 directory may be left unclaimed by any block (and not declared superseded)
    assert led.get("n_orphan_dirs", 0) == 0, \
        f"orphan final-q1 directories claimed by no block: {led.get('orphan_dirs')}"
    # M1 (reproducibility record): the operational e2e seed window must be the dual-sample
    # 801-830 arm the table actually reports, not the superseded 701-730 pilot
    assert m["seeds"]["q1_operational_e2e"].startswith("801-830"), \
        f"operational seed window stale: {m['seeds']['q1_operational_e2e']}"
    # the sealing field must be the non-circular source_commit_sha, never commit_sha
    assert "source_commit_sha" in m and "commit_sha" not in m


def test_final_editorial_no_overclaims():
    """Final editorial guard (Blocks 1-8): fail on any claim stronger than the evidence,
    matched by MEANING (banned phrases plus windowed proximity) rather than one exact string,
    so a reworded false claim is still caught. Scans the CAS source, the IEEE port and the
    supplement. Each pattern is checked against the specific false variant it must reject."""
    docs = {}
    for d in ("main.tex", "main_ieee.tex", "supplement.tex"):
        p = REPO / "manuscript" / d
        if p.exists():
            docs[d] = re.sub(r"\s+", " ", p.read_text(encoding="utf-8").lower())

    banned = [
        (r"full protection", "B6: 'full protection' overclaims formal control"),
        (r"costs no labels at all", "B2: strict is no-ADDITIONAL-label, not label-free"),
        (r"zero-cost strict", "B2: use 'no-additional-label strict'"),
        (r"reproduces every conclusion", "B5: causal arm does not reproduce every conclusion"),
        (r"assumed zero throughout", "B4: operational arm evaluates a 5-window training delay"),
        (r"instantaneous in every arm", "B4: operational arm evaluates a 5-window training delay"),
        (r"scoring all 520 commits", "B8: the H5 endpoint scores 506 evaluable, not all 520"),
        (r"significantly outperforms both naive", "B7: significance is harm-regime only"),
        (r"every gate beats", "B3: not every gate beats always-deploying on healthy timelines"),
    ]
    v = []
    for name, t in docs.items():
        for pat, why in banned:
            if re.search(pat, t):
                v.append(f"{name}: {why}")
        # B5: 'statistically indistinguishable' must not describe causal-vs-oracle
        for m in re.finditer(r"statistically indistinguishable", t):
            w = t[max(0, m.start() - 120): m.end() + 120]
            if "oracle" in w or "causal gate" in w:
                v.append(f"{name}: B5 causal-vs-oracle 'statistically indistinguishable'")
        # B3: 'all three gates' must not be claimed above/beating always-deploying
        for m in re.finditer(r"all three gates", t):
            w = t[m.start(): m.end() + 90]
            if ("above" in w or "beat" in w) and "always" in w:
                v.append(f"{name}: B3 'all three gates ... above/beat always-deploying'")
        # B3: 'match(es)-or-beat(s) always-deploying' (false joint UNSW+Wednesday claim)
        for m in re.finditer(r"match(?:es)?[ -]or[ -]beat", t):
            w = t[m.start(): m.end() + 45]
            if "always-deploying" in w or "always deploying" in w:
                v.append(f"{name}: B3 'match or beat always-deploying'")
        # B1: every '93%' benefit claim must be marked as the APPROXIMATE POOLED analysis and
        # thereby distinguished from the fully stratified variant
        for m in re.finditer(r"93\s*\?%", t):
            w = t[max(0, m.start() - 40): m.end() + 240]
            if ("benefit" in w or "always-deploying" in w) and not \
               ("approximate" in w or "pooled" in w):
                v.append(f"{name}: B1 '93%' benefit claim not marked approximate/pooled")

    assert not v, "editorial overclaim(s) detected:\n  " + "\n  ".join(sorted(set(v)))
