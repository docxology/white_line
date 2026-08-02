# White Line as a separated copy

This repository is the whole of White Line. It carries its own Python package,
tests, documentation, manuscript, references, figure builder, and release audit.
It is one of five works in the line set, and it is the only one of them you need
in order to run everything below.

## What a separated copy is

The four line works — Red, Black, Golden, White — and the set reader `line_set`
were extracted into their own repositories. A separated copy is a clone of one
of them, held on its own, with no sibling checkout beside it and no monorepo
around it. This document states what that copy can do and what it cannot, so a
reader who has only this repository is never left guessing which documented step
is unreachable.

## What it can do alone

From a clone of this repository and nothing else:

- Install: `pyproject.toml` declares `dependencies = []`. The package is pure
  standard library on Python 3.10 or later; the `dev` group is `pytest` and
  `pytest-cov`.
- Run the full test suite and meet the coverage gate (`fail_under = 90`).
- `scripts/check_registry.py` — the live registry and its invariant battery.
- `scripts/build_figures.py` — every SVG/PNG plate plus `figure_registry.json`
  and `white_registry.json`, deterministically. This needs the system
  `rsvg-convert` executable from librsvg on `PATH`; it is a rasterizer, not a
  Python dependency, and the build fails with an explicit install message when
  it is absent.
- `scripts/check_figure_layout.py` — the printed-size and overflow report.
- `scripts/audit_project.py --report` — every source-side release check:
  ledger soundness, the pinned registry digest, figure registry schema and byte
  digests, bidirectional manuscript/figure links, section labels, and
  bibliography keys in both directions.

No module in `src/white_line/` imports `red_line`, `black_line`, `golden_line`,
or `line_set`, and no path in this repository resolves above its own root.

## What it cannot do alone

**Render the publication bundle.** `output/pdf/white_line_combined.pdf` and
`output/web/_combined_manuscript.md` are written by the `docxology/template`
render engine, which is a separate repository and is not vendored here. Nothing
in `src/` or `scripts/` produces those files; `src/white_line/audit.py` only
reads them.

This is a declared external dependency, not a hidden one. The consequences are
bounded and named:

- `scripts/audit_project.py` runs its source checks and *defers* the
  render-dependent errors, reporting them and exiting 0, unless you pass
  `--require-render` to demand the post-render gate.
- Two tests skip with a named reason rather than failing, and each asserts the
  artifact is genuinely absent first, so the skip is a positive control and not
  a silent pass:
  - `tests/test_audit.py::test_real_project_has_no_release_blocker_beyond_manifest_staleness`
    — skips as `no rendered bundle in this checkout: [...]` after asserting that
    `source_blocking_errors` is empty and `checks["rendered_bundle"]` is `False`.
  - `tests/test_figure_legibility.py::test_derived_geometry_matches_the_last_rendered_latex`
    — skips as `no rendered LaTeX artifacts in this checkout` after
    `observed_latex_geometry` returns `None`.

The path-independent render invocation is in
[docs/development.md](docs/development.md): clone or locate the template
anywhere, link this checkout in as its `projects/working/white_line`, and render
with the qualified project name `working/white_line`. That name is resolved by
the template inside its own `projects/` tree; it is not a path relative to this
repository.

## The other works

Each companion is its own repository and is referenced by name and URL, never by
a relative path and never by an import:

| Work | Repository | What it is |
| --- | --- | --- |
| Red Line | <https://github.com/docxology/red_line> | the personal security boundary and explicit No document |
| Black Line | <https://github.com/docxology/black_line> | strong practice |
| Golden Line | <https://github.com/docxology/golden_line> | aspiration |
| `line_set` | <https://github.com/docxology/line_set> | the thin reader that declares the set and carries its shared framing |

White Line copies none of their prose, registries, or implementation modules,
and defers to none of them. Their absence changes nothing about what this
repository does.

## What this document is not

It is not a claim that the instrument is correct, that any recorded absence is
true, or that a passing audit certifies anything about the world. Those limits
are stated in [docs/claim_boundaries.md](docs/claim_boundaries.md) and
[manuscript/05_limits.md](manuscript/05_limits.md), and nothing here softens
them.
