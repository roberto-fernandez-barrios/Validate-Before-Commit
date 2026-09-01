# IJIS final integrity closure audit

Date: 2026-09-02. Fixed scope: the twelve authorized closure questions only.

1. **Was the exact-feature-overlap allegation verified? — YES.** Exact cleaned raw X
   duplicates beyond the first group member are 99,839/732,376 (13.63%) for PortScan,
   74,767/205,346 (36.41%) for UNSW-NB15 and 15,775/140,521 (11.23%) for ToN-IoT. The
   historical source-row split permits exact-X groups to cross roles; the per-seed overlap
   audit and candidate/evaluation exposure diagnostics reproduce the allegation.
2. **Does the group-disjoint implementation guarantee zero exact-X cross-role overlap? —
   YES.** All 630 B2 and 2,880 B1 arm-seed role audits report zero exact-X groups in each
   role-pair intersection; the splitter enforces the condition before environment creation.
3. **Was multiplicity preserved? — YES.** Every input row is assigned exactly once, and
   per-stratum and total multiplicities match input in every audit; within-role duplicates
   and registered with-replacement sampling remain intact.
4. **Were contradictory-label groups handled honestly? — YES.** The X-only key keeps all
   original rows and labels together. UNSW-NB15 has 403 contradictory groups involving
   1,828 rows; PortScan and ToN-IoT have none. No deletion, voting or relabelling occurred.
5. **Did B2 survive? — PARTIALLY.** The 512-to-2,000 effect is positive and Holm-resolved
   in all three benchmarks (+0.5276/+1.6734/+0.3815 BA points) and material in two. The
   registered verdict is `PARTIAL ROBUSTNESS`; homogeneous material benefit does not survive.
6. **Did the B1 interpretation survive? — PARTIALLY.** Four of six frozen predicates hold,
   with no gain/cost reversal. Candidate-size-dependent ordering and no global dominance
   survive; ATC and calibrated-ensemble retention statements are narrowed.
7. **Are all affected claims scoped correctly? — YES.** The manuscript distinguishes the
   historical source-row-disjoint design from the governing exact-feature-disjoint
   sensitivity, removes the homogeneous headline, avoids causal leakage claims, and retains
   the registered-reference-parameter qualification for DDM/ADWIN.
8. **Is “real drift” terminology fixed? — YES.** Controlled-pool results are described as
   pool-constructed progressive drift between empirical regime pools; no live claim surface
   calls that trajectory real drift.
9. **Is comparative literature current through September 2026? — YES.** CARAVAN, SPIDER,
   NOCTOWL and ADAWU-IDS were checked at the publisher/paper interface level and compared
   neutrally in the ESM; no unsupported absence or superiority claim is made.
10. **Is the exact current Zenodo DOI used correctly? — YES.** Artifact v1.24.0 is public at
    exact DOI `10.5281/zenodo.22239106`; concept DOI `10.5281/zenodo.21322256` is also
    exposed. The prior v1.23.0 release remains immutable and the v1.24.0 tag was not moved.
11. **Is the final artifact reproducible? — YES.** The exact tag passes 245 tests, 230/230
    pinned hashes with zero extras, claim audit 632/632, and all four PDF builds with zero
    undefined references/citations. The public Zenodo archive is byte-identical to GitHub's
    tag zipball and all 230 sealed CSVs verify after extraction.
12. **Is the IJIS package editorially valid? — YES.** The Springer manuscript is 28 pages,
    ESM is 48 A4 pages, the abstract is 219 words, figures use redundant non-colour encodings,
    the exact DOI and AI-use disclosure are present, and the deterministic 71-file checksum
    list validates with no internal audits or reviewer simulations included.

**READY FOR IJIS SUBMISSION**
