# Publication and citation

## How to cite

Version 0.9.1 is a documentation-only patch prepared for repository release.
Use the repository and, once created, its tag separately from the last verified Zenodo deposition:

> Friedman, D. A. (2026). *White Line: A Typed Ledger for the Edge of the Claim* (version
> 0.9.1) [Software and manuscript]. GitHub.
> <https://github.com/docxology/white_line>

BibTeX:

```bibtex
@software{friedman_white_line_2026,
  author  = {Friedman, Daniel Ari},
  title   = {White Line: A Typed Ledger for the Edge of the Claim},
  version = {0.9.1},
  year    = {2026},
  url     = {https://github.com/docxology/white_line},
  note    = {Repository release candidate; the next Zenodo version DOI remains pending}
}
```

For the last verified deposition, cite the DOI separately, without attributing
the repository version to it:

> Friedman, D. A. (2026). *White Line: A Typed Ledger for the Edge of the Claim*
> [Software and manuscript]. Zenodo. <https://doi.org/10.5281/zenodo.21754242>

`CITATION.cff`, `.zenodo.json`, and `manuscript/config.yaml` carry synchronized
version metadata and retain the last verified DOI as required by the
release procedure. That retained identifier does not identify a new 0.9.1
deposition. `tests/test_publication_metadata.py` checks their agreement.

## Persistent Identifiers and Verification

Version 0.9.1 is a repository release candidate. The DOI below remains the last verified
deposition; it does not assert that Zenodo has published this software version.
Verify the actual successor archive separately; no new DOI is asserted here.

This repository carries an asserted, verified Zenodo DOI (`10.5281/zenodo.21754242`).
`tests/test_publication_metadata.py` refuses any unverified DOI-shaped string in
the citation metadata unless that exact DOI is listed as verified inside the test
itself. A placeholder DOI that renders like a real one is worse than no DOI: it
survives copy-and-paste into someone else's bibliography and points nowhere.

## Authorized automatic publication for this release

On November 8, 2026, the owner authorized this GitHub Release campaign with the
existing public repositories' Zenodo hooks left active. Inspect the authenticated
hook state immediately before publication and verify the resulting archive's
repository, tag, version, and contents. Never prefill a DOI or amend an immutable
tag to add one learned afterward. PyPI, private-source disclosure, and new
private-sibling deposit automation remain unauthorized. The manual procedure
below is an alternative, not a prerequisite for this authorized integration.

## Manual reserve-first DOI publication

1. Create the Zenodo deposition **without publishing it**, and reserve its DOI.
2. Record the reserved DOI in this repository: add it under `identifiers:` in
   `CITATION.cff`, add it to `related_identifiers` in `.zenodo.json` if
   relevant, add `publication.doi` to `manuscript/config.yaml`, and add the
   exact string to the verified list in `tests/test_publication_metadata.py`.
   The gate turns green only when a person has asserted the DOI is real.
3. Re-render the manuscript so the printed artifact carries its own DOI. A PDF
   deposited without its DOI on the cover cannot be cited from the paper alone.
4. Upload the re-rendered artifacts and publish the deposition.

## The other works

Current membership belongs to the [Line Set declaration](https://github.com/docxology/line_set).
The original four-color citation cohort below is
retained with its already recorded DOI relationships; it is not an exhaustive
membership or publication inventory. The colorless wrapper `line_set` and
Witness Register are not colors. Optional or access-controlled source
availability is separate from membership. No work imports another, and the
shared report-envelope schema string is aligned by convention, not dependency.
No new DOI or publication status is asserted here.
Violet, Copper, and Iron sources are access-controlled. Copper records dimensioned
resource use, outstanding commitments, and attributed burdens, not White
completeness or fair allocation. Missing recovery evidence can be White absence;
Iron's recorded scenario-target comparisons do not promise future recovery.

| Work | Role | Repository | DOI |
| --- | --- | --- | --- |
| `red_line` | line — what I refuse (personal security boundary) | <https://github.com/docxology/red_line> | `https://doi.org/10.5281/zenodo.21754240` |
| `black_line` | line — how I try to do strong work (declaration coverage) | <https://github.com/docxology/black_line> | `https://doi.org/10.5281/zenodo.21754236` |
| `golden_line` | line — what is worth reaching toward (directional readings) | <https://github.com/docxology/golden_line> | `https://doi.org/10.5281/zenodo.21754238` |
| `line_set` | the reader that declares the set and checks vocabulary separation | <https://github.com/docxology/line_set> | `https://doi.org/10.5281/zenodo.21754244` |
| `witness_register` | companion beside the set — co-registration without aggregation | <https://github.com/docxology/witness_register> | `https://doi.org/10.5281/zenodo.21754246` |

## Repository publication checklist (applied before this repository went public)

- [ ] Every gate in `AGENTS.md` green on a clean checkout.
- [ ] `LICENSE` present and accurate.
- [ ] No absolute local paths, secrets, or private-project names in any tracked
      file (`tests/test_publication_metadata.py` checks the first of these).
- [ ] Git history contains nothing that should not be public — the published
      history is a fresh initial-release commit, not a monorepo extract.
- [ ] The rendered PDF regenerated at the release tree.
