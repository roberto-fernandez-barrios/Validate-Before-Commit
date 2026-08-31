"""Coarse per-arm wall-clock summary for the frozen-vs-own and 512-vs-2000 arms (editorial).

Post-KBS revision (audits/kbs_rejection_revision_report.md, Task 8): Reviewer #2 asked for
operational context on the computational overhead of self-contained versus frozen-transformer
pipelines. No isolated timing benchmark of the two policies exists in the artifact. What does
exist is the ``duration_s`` field that every confirmatory arm's ``completion_marker.json``
records (wall-clock of the whole arm: stream generation, detector scoring, candidate training
and evaluation, run sequentially on one machine). This script summarizes those fields; it
reads only ``results/raw/**/completion_marker.json`` + ``run_config.json``, runs no
experiment, touches no sealed CSV, and writes only under ``audits/`` (outside
``results/tables`` so that ``MANIFEST.sha256`` stays untouched).

The numbers are operational context, not a benchmark, and the manuscript labels them as such
(main text, Discussion: "Computational overhead of self-contained challengers").

Outputs:
  audits/pipeline_arm_wallclock_summary.csv   one row per arm, plus matched-pair ratios
  (stdout)                                    the aggregate figures quoted in the manuscript
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
SYM = REPO / "results" / "raw" / "symmetric_pipeline"
SM = REPO / "results" / "raw" / "size_matched_own_transformer"
OUT = REPO / "audits" / "pipeline_arm_wallclock_summary.csv"


def _arms(root: Path, prefix: str) -> list[dict]:
    rows = []
    for d in sorted(root.glob(f"{prefix}_*")):
        marker, cfg = d / "completion_marker.json", d / "run_config.json"
        if not (marker.exists() and cfg.exists()):
            continue
        m = json.loads(marker.read_text(encoding="utf-8"))
        c = json.loads(cfg.read_text(encoding="utf-8"))
        rows.append(dict(
            block="symmetric_pipeline" if prefix == "sp" else "size_matched_own_transformer",
            arm=c["tag"], scenario=c["scenario"], policy=c["policy"],
            transformer_policy=c.get("transformer_policy", ""),
            candidate_size_per_class=str(c.get("candidate_size_per_class")
                                         or c.get("resolved_flags", {}).get(
                                             "--candidate-size-per-class")
                                         or c.get("resolved_flags", {}).get(
                                             "--adapt-size-per-class") or ""),
            complete=bool(m.get("complete")), duration_s=float(m["duration_s"]),
            finished_utc=m.get("finished_utc", "")))
    return rows


def main() -> None:
    rows = _arms(SYM, "sp") + _arms(SM, "sm")
    if not rows:
        raise SystemExit("no completion markers under results/raw (raw outputs are not "
                         "redistributed; this summary needs a local confirmatory run)")
    df = pd.DataFrame(rows)

    # frozen vs own, matched on (scenario, policy) within the symmetric-pipeline block
    sp = df[df.block == "symmetric_pipeline"]
    pairs = []
    for (sc, pol), g in sp.groupby(["scenario", "policy"]):
        fr = g[g.transformer_policy == "frozen_initial_transformer"]
        ow = g[g.transformer_policy == "own_transformer_per_model"]
        if len(fr) == 1 and len(ow) == 1:
            pairs.append(dict(block="symmetric_pipeline", scenario=sc, policy=pol,
                              frozen_s=float(fr.duration_s.iloc[0]),
                              own_s=float(ow.duration_s.iloc[0]),
                              ratio_own_over_frozen=float(ow.duration_s.iloc[0]
                                                          / fr.duration_s.iloc[0])))
    # 2000 vs 512 per class, matched on (scenario, policy) within the size-matched block
    sm = df[df.block == "size_matched_own_transformer"]
    size_pairs = []
    for (sc, pol), g in sm.groupby(["scenario", "policy"]):
        a = g[g.candidate_size_per_class == "512"]
        b = g[g.candidate_size_per_class == "2000"]
        if len(a) == 1 and len(b) == 1:
            size_pairs.append(dict(block="size_matched_own_transformer", scenario=sc,
                                   policy=pol, s512_s=float(a.duration_s.iloc[0]),
                                   s2000_s=float(b.duration_s.iloc[0]),
                                   ratio_2000_over_512=float(b.duration_s.iloc[0]
                                                             / a.duration_s.iloc[0])))

    OUT.parent.mkdir(exist_ok=True)
    per_arm = df.assign(kind="arm")
    pr = pd.DataFrame(pairs).assign(kind="pair_frozen_vs_own")
    sz = pd.DataFrame(size_pairs).assign(kind="pair_512_vs_2000")
    pd.concat([per_arm, pr, sz], ignore_index=True, sort=False).to_csv(OUT, index=False)

    r = [p["ratio_own_over_frozen"] for p in pairs]
    q = [p["ratio_2000_over_512"] for p in size_pairs]
    print(f"symmetric-pipeline arms: {len(sp)}; matched frozen/own pairs: {len(pairs)}")
    if r:
        print(f"  own/frozen wall-clock ratio: mean {st.mean(r):.2f}, "
              f"min {min(r):.2f}, max {max(r):.2f}")
    print(f"size-matched arms: {len(sm)}; matched 512/2000 pairs: {len(size_pairs)}")
    if q:
        print(f"  2000/512 wall-clock ratio: mean {st.mean(q):.2f}, "
              f"min {min(q):.2f}, max {max(q):.2f}")
    print(f"wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
