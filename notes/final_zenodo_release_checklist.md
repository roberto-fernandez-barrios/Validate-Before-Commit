# Zenodo release checklist — v1.23.0 (verified state and remaining human actions)

Date: 2026-09-01. Mechanism: the repository's GitHub–Zenodo integration creates a new
version of the concept record automatically when a GitHub release is published; no manual
Zenodo upload is part of the workflow.

## Verified (read back from the public Zenodo API and the archive itself)
- Record id **22229253** — version **1.23.0** — DOI **10.5281/zenodo.22229253**.
- Concept DOI **10.5281/zenodo.21322256** (concept record 21322256; resolves to this version).
- Title: "Validate Before Commit: reproducibility artifact (code and protocols)".
- Creators: Fernández-Barrios, Roberto (0009-0003-5312-2634); Pastor-López, Iker
  (0000-0002-3068-6248); Pikatza-Huerga, Amaia (0009-0003-9080-6242); García Bringas, Pablo
  (0000-0003-3594-9534) — all Faculty of Engineering, University of Deusto.
- Publication date 2026-09-01; licence MIT; resource type software; related identifier
  `https://github.com/roberto-fernandez-barrios/Validate-Before-Commit/tree/v1.23.0`
  (isSupplementTo).
- Archived file `roberto-fernandez-barrios/Validate-Before-Commit-v1.23.0.zip`, 3,961,394
  bytes, MD5 `650e9fb963ac10360710771d2f033612`, SHA-256
  `2715e3a6f3cc638ab7699461c27c1a70fe40fe4b009af2d8bf5a7d9ffb35d23d` — byte-identical to
  GitHub's zipball of the tag (`git describe` prefix `…-1c5d249`), and the 207 sealed CSVs
  inside it hash exactly to `results/tables/MANIFEST.sha256`.
- Relationship to previous versions: same concept record as 1.22.9 (record 21623666, DOI
  10.5281/zenodo.21623666) and 1.22.8 (21621939); the historical science DOI v1.22.0
  (10.5281/zenodo.21517899) remains the exact version cited in the manuscript for the
  v1.22 line.
- `dist/release_manifest.json` (uploaded as a release asset) records all of the above; the
  repository itself does not embed the version DOI (established convention: DOIs are
  registered post-mint in release assets/notes, the tag is never moved).

## Remaining human actions
1. None required for the archive to be complete and citable: the deposit exists, is public,
   and contains the sealed B1/B2 evidence.
2. Optional, at the author's discretion: embed the version DOI 10.5281/zenodo.22229253 in the
   manuscript's Data-availability statement through a documented editorial patch release
   (the v1.22.x precedent: a new patch version, never a rewrite of v1.23.0). The manuscript
   currently cites the concept DOI, the exact v1.22.0 science DOI and "sealed in artifact
   version v1.23.0", which resolves correctly without that patch.
3. Optional: review the Zenodo record page once for the description text mirrored from
   `.zenodo.json` (it now names B1/B2); no metadata error was found.
