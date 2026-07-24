# FINAL RELEASE VERSION RESOLUTION

Resolution of the release version for the final KBS narrative-rebuild artifact, before any
merge / tag / release, per the version-resolution rule.

## Observed state

- **Latest public tag:** `v1.22.2` (`git tag --sort=-version:refname` → v1.22.2, v1.22.1, v1.22.0, v1.21.0, …).
- **Current metadata version:** `CITATION.cff` = 1.22.2, `.zenodo.json` = 1.22.2, `references.bib` `note = {Version 1.22.2}`.
- **`main`/`origin/main` HEAD:** `1e0c72f` (tag v1.22.2).
- **No `v1.22.3`, `v1.23.0` tag, branch, or reserved DOI** observed anywhere in the repo.
- **Sealed scientific artifact:** v1.22.0 (`43d9c25`), version DOI `10.5281/zenodo.21517899`, concept DOI `10.5281/zenodo.21322256`. This is the science the manuscript Data Availability cites and the audit pins verbatim.

## Repository version pattern (MINOR vs PATCH)

Established, unambiguous precedent:

- **MINOR bumps integrate new scientific evidence.** `v1.21.0` = symmetric-pipeline replication (new experiment); `v1.22.0` = size-matched control (new experiment).
- **PATCH bumps are editorial-only corrections to the sealed science.** `v1.19.1`, `v1.20.1`, `v1.20.2`, `v1.22.1` (editorial-scope correction: retitled sections, README recommendations, graphical abstract, 17 new tests + 39 audit guards, two derived editorial CSVs, relocated a table), `v1.22.2` (five wording microcorrections).

This narrative rebuild changes **no** scientific content: no new experiment, no changed seed / margin / statistical family / registered outcome; ATTENUATION preserved; `results/raw/**` and every sealed CSV manifest untouched (verify-hashes 185/185). It is a retitle + narrative restructure + abstract rewrite + one derived presentation figure — editorial only.

The directly controlling precedent is **v1.22.1**, which was comparable in structural magnitude (new derived artifacts, new tests/guards, restructured manuscript, changed graphical abstract) yet was a PATCH because it produced no new science.

## Rule application

1. *"If the size-matched scientific version is explicitly reserved and not yet public → use it."* — The size-matched science is **v1.22.0, already public** (tag + DOI). This branch does not apply.
2. *"If that version already exists publicly → use the next semantically correct version per the repo pattern."* — v1.22.0 exists publicly. The repo pattern for an editorial-only change on top of the sealed v1.22.0 science is a **PATCH** increment. The last such patch is v1.22.2, so the next is **v1.22.3**.
3. *"If any ambiguity or collision → stop."* — `v1.22.3` collides with **no** tag, branch or DOI. The MINOR alternative (v1.23.0) was considered and rejected: under this repo's demonstrated pattern MINOR is reserved for new scientific evidence, of which this rebuild adds none; treating it as MINOR would contradict the v1.22.1 precedent. No genuine ambiguity remains.

## Resolution

- **Release version: `v1.22.3`** (editorial PATCH over the sealed v1.22.0 science).
- **Manuscript Data Availability is NOT repointed:** it continues to cite artifact version v1.22.0 and DOI 10.5281/zenodo.21517899 (the sealed science), exactly as v1.22.1 and v1.22.2 did; this is audit-pinned and correct.
- **Mechanical version fields to bump to 1.22.3:** `manuscript/references.bib` (`note = {Version 1.22.3}`, the `make_final_manifest` source-of-truth), `CITATION.cff` (`version`, `date-released`), `.zenodo.json` (`version`, description sentence). Concept DOI `10.5281/zenodo.21322256` unchanged; version DOI for v1.22.3 is **pending Zenodo publication**.
- **No collision / no block.** Proceed to fast-forward merge, seal, tag `v1.22.3`, and release.
