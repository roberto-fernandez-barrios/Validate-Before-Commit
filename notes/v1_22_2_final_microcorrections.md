# v1.22.2 — Final editorial microcorrections and KBS submission closure

Date: 2026-07-24. Branch: `fix/v1.22.2-final-microcorrections` (from `main` @ v1.22.1,
Commit B `0a5998c`). Closing correction only — no new scientific iteration.

## Context: why v1.22.2 and not an amended v1.22.1

The five microcorrections were authorized after v1.22.1 had already been sealed and
published under the prior authorization (tag `v1.22.1` → `0a5998c`, GitHub Release live,
Zenodo version DOI **10.5281/zenodo.21526663** minted 2026-07-24). Published tags,
releases and Zenodo records are immutable, so the corrections are sealed as the patch
release v1.22.2 under the identical procedure. v1.22.1's identity was closed first: its
minted DOI is recorded in its release notes and in its `release_manifest.json` asset.

## The five microcorrections

1. **Neutral causal language** replacing "manufactured harm" equivalents:
   highlight → "Frozen incumbent-owned preprocessing produced the apparent promotion
   harm"; Discussion Finding 1 → "accounted for the mean full-drift harm"; Finding 3 →
   "asymmetric construction can produce either"; graphical abstract badge → "accounted
   for the full-drift harm"; supplement → "generates the phenomenon" / "the recovery is
   not an artifact of the ramps".
2. **"Fair challenger" ambiguity removed**: "compete under comparable conditions",
   "evaluated on comparable terms", "comparably constructed, comparably evidenced
   proposal/challenger" (conclusion + README blockquote); audit anchor updated.
3. **±0.5-pp margin justified** (Method §3.6, where the margins are frozen): the margin
   equals the materiality threshold the program preregistered for its own harm claims —
   effects below half a BA point are treated as operationally immaterial throughout, and
   the smallest harm called material (−0.65) exceeds it — so CI90-inside equivalence
   certifies a residual mean effect below anything the program treats as material; the
   ±0.2/±1.0 sensitivities bracket margin-dependence.
4. **Two residual claims corrected**: (a) detector-score scope — "the evaluated
   detectors' scores showed no consistent association" (Discussion), "a quantity the
   evaluated drift-detector scores did not track" (README); (b) the README zero-drift
   harm claim now scoped to the evaluated 512-per-class frozen-transformer
   configuration, with the pointer that the mean harm vanishes at nominal
   2,000-per-class parity.
5. **Identity closure**: metadata → 1.22.2 (CITATION.cff, .zenodo.json with change
   note, references.bib artifact note); claim-scope audit regenerated (18 claims,
   0 failing, byte-identical); MANIFEST re-pin idempotent at 185 (no CSV changed);
   4 new audit guards (no "manufacture", no "fair challenger", margin justification
   present, README 512-scope present).

Typographic note: reference leading tightened to 8/9.2pt (class default 8/10pt) to hold
the 33-page budget after the margin-justification addition; content untouched.

## Gates (final build)

pytest **135/135**; audit **629/629** (625 + 4 new); hashes **185/185** (0 extras);
main **33 pp** / supplement **30 pp** / IEEE **25 pp**, 0 undefined refs/citations;
abstract **234** words; body **17,744** (< 17,889 v1.22.0 baseline, same method).
`results/raw/` untouched; no experiments; no seeds; ATTENUATION unchanged; the two
personal untracked files excluded from all commits.

## KBS submission package (Elsevier Editorial Manager)

- `main.pdf` (33 pp, CAS single-column) — manuscript with embedded highlights,
  graphical abstract, CRediT, declarations, Data Availability (artifact v1.22.0 exact
  DOI + concept DOI).
- `supplement.pdf` (30 pp) — supplementary material.
- `manuscript/highlights.md` — 5 bullets, all ≤ 85 characters.
- `docs/img/graphical_abstract.png` — 2129×857 (> 1328×531 minimum).
- Artifact reference for the form: concept DOI 10.5281/zenodo.21322256
  (resolves to latest); exact evaluated version v1.22.0 = 10.5281/zenodo.21517899.
- `main_ieee.pdf` (25 pp) — backup format only, not part of the KBS submission.
