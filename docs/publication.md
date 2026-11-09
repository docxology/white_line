# Publication and citation

## How to cite

For source version 0.9.2, use the repository citation until an archive for that
exact edition is independently verified:

> Friedman, D. A. (2026). *White Line: A Typed Ledger for the Edge of the Claim* (version
> 0.9.2) [Software source]. GitHub.
> <https://github.com/docxology/white_line>

BibTeX:

```bibtex
@software{friedman_white_line_2026,
  author  = {Friedman, Daniel Ari},
  title   = {White Line: A Typed Ledger for the Edge of the Claim},
  version = {0.9.2},
  year    = {2026},
  url     = {https://github.com/docxology/white_line}
}
```

Previously verified source archive: version 0.9.1,
<https://doi.org/10.5281/zenodo.24069434>. It identifies that source ZIP only,
not version 0.9.2 or a standalone rendered manuscript. The earlier historical
archive retains DOI `10.5281/zenodo.21754242`; this metadata does not establish
its edition, so no software version is inferred for it.

`CITATION.cff`, `.zenodo.json`, and `manuscript/config.yaml` carry synchronized
version metadata and separate prior archive references.
`tests/test_publication_metadata.py` checks version agreement.

## Persistent Identifiers and Verification

Verify the actual archive record's repository, tag, version, and contents before
assigning its identifier to that edition/object. Current metadata uses the
repository until the exact edition/object is independently verified.
A local metadata assertion is not external publication evidence. Keep historical
title/DOI pairs unchanged; never invent identifiers or rewrite issued bytes.

## Authorized automatic publication

On November 8, 2026, the owner authorized this GitHub Release campaign with the
existing public repositories' Zenodo hooks left active. Future use requires
actual owner authority for that release and object. Inspect the authenticated
hook state immediately before publication and verify the resulting archive's
repository, tag, version, and contents. Never prefill a DOI or amend an immutable
tag to add one learned afterward. PyPI, private-source disclosure, and new
private-sibling deposit automation remain unauthorized. The manual procedure
below is an alternative, not a universal prerequisite.

## Manual reserve-first DOI publication

1. With owner authority for the specific object, create an unpublished Zenodo
   deposition and reserve its DOI. A reservation is not a published deposit.
2. Identify the exact software source or standalone manuscript being deposited.
   If rendering a manuscript with its reserved DOI, label the reservation
   accurately; a source ZIP DOI does not identify a separate PDF.
3. Publish only the authorized bytes, then independently verify the actual
   record's repository, tag, version, and contents.
4. Record the verified identifier for that exact edition/object. If source has
   advanced, retain it as a versioned historical reference, not a current DOI.
   Never amend an immutable tag or archive to insert a DOI learned afterward.

## The other works

Current membership belongs to the [Line Set declaration](https://github.com/docxology/line_set).
The original four-color citation cohort below is
retained with its already recorded DOI relationships; it is not an exhaustive
membership or publication inventory. The colorless wrapper `line_set` and
Witness Register are not colors. Optional or access-controlled source
availability is separate from membership. Native instruments do not import
siblings. Main deliberately imports published namespace bindings only; Witness
receives report envelopes by value. The shared report-envelope schema is aligned
by convention, not a shared runtime dependency.
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

## Before each release

- [ ] Every gate in `AGENTS.md` green on a clean checkout.
- [ ] `LICENSE` present and accurate.
- [ ] No absolute local paths, secrets, or private-project names in any tracked
      file (`tests/test_publication_metadata.py` checks the first of these).
- [ ] Review newly published Git history for disclosure. The fresh initial-release
      history was a first-publication decision, not an instruction to reset it.
- [ ] The rendered PDF regenerated at the release tree.
