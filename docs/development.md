# Development

From the White Line repository root, install `uv` and librsvg's
`rsvg-convert` (the `librsvg2-bin` package on Debian or Ubuntu). Use Python
3.11 or later. The package has no runtime Python dependencies. The locked
development environment installs pytest, Ruff, mypy, and coverage tools.

Run the following to set up the environment and check the source and figures.

```bash
uv sync --locked --python 3.11
uv run --locked --python 3.11 python scripts/check_registry.py
uv run --locked --python 3.11 python scripts/build_figures.py
uv run --locked --python 3.11 pytest tests/ --cov=src --cov-branch --cov-report=term-missing
uv run --locked --python 3.11 ruff check src tests scripts
uv run --locked --python 3.11 mypy src
uv run --locked --python 3.11 python scripts/audit_project.py --report
```

Every command above runs from a clone of this repository alone. `output/` is
git-ignored, so the figure build comes before the checks that read it;
`tests/conftest.py` also rebuilds `output/figures/` when it is absent, using this
project's own deterministic builder, so the suite is order-independent rather
than order-fragile. The rebuild is never masked: a builder failure surfaces as
an error.

The lint rules and the `py311` target are pinned in `pyproject.toml`; mypy
likewise targets Python 3.11. These targets enforce the declared
`requires-python = ">=3.11"` floor even when development uses a newer
interpreter. The selected development interpreter is Python 3.15, and the
standing `.github/workflows/ci.yml` matrix runs Python 3.11 and 3.15. Each job
builds figures and checks branch coverage, lint, types, the registry, and the
source audit. Template publication checks remain a separate external release
gate. Regenerate `uv.lock` with `uv lock` after dependency or Python-requirement
changes, then use `uv sync --locked` for the recorded tool versions. Historical
release packets retain the interpreter versions actually measured then.

`white_line.figures.build_figures` writes seventeen deterministic SVG/PNG
compositions plus the
registry JSON files under `output/figures/`. The audit checks the registry,
figure metadata and links, the recorded PNG and SVG byte digests, bibliography
keys in both directions, required PDF/HTML artifacts, and
source headings in the rendered combined manuscript. It is a consistency gate,
not a truth verifier. For visual iteration, pass a disposable `project_root`
on the mounted development volume to `build_figures`, inspect the resulting PNGs, and copy
only the reviewed generated artifacts into the project output directory.

The current figure metadata schema is `white-line.figure-registry/2.0`.
Each figure, including the cover, serializes its authored description as
`alt_text`; `caption` remains separate. Consumers must read `alt_text` rather
than a legacy `alt` key or a caption fallback. The native audit requires a
nonblank `alt_text`. Historical release artifacts retain their original schema.

`tests/test_figure_legibility.py` is the printed-size gate. It reads each
plate's canvas size out of its rendered SVG, the `width=` attribute out of the
manuscript embed, and the page geometry out of `docs/manuscript/config.yaml`, then
computes what a label of `N` canvas units measures on paper and fails below
six points. Two further checks cross-read the `\textwidth` and per-figure
`width`/`height` fractions from the last rendered `.log` and `.tex`, so a
template-side geometry change surfaces as a failure rather than as a quietly
wrong number. Re-render before trusting a green legibility run after any
`config.yaml` or embed-width edit.

The targeted config reader ignores commented-out keys and accepts ordinary
trailing comments on quoted geometry and numeric height caps without a YAML
dependency. Front-matter and body height caps must still agree. The US Letter,
inch-margin model and six-point floor are unchanged.

Formalism declarations, citations, and hand-written-number checks share one
offset- and newline-preserving literal-code mask. Backtick and tilde fences
close only with the same character and a sufficient run length; inline code
uses equal backtick runs, and four-space or tab-indented code is excluded.
Literal examples cannot declare or close live Divs, consume their numbers, or
add bibliography keys. Parsed live blocks retain their original source bodies,
including code samples; live citations still determine bibliography membership.

Numeric manuscript claims that are not already emitted by the package or its
configuration are registered in `data/claim_ledger.json`. Each row names the
claim and points to the manuscript source that explains it; the sibling
template's evidence-registry validator checks those paths during Stage 04.

Figure rasterization requires `rsvg-convert` from librsvg on `PATH`; it is a
system rendering prerequisite, not a runtime package dependency.

## Render and validate the manuscript

[The manuscript source](manuscript/README.md) lives in `docs/manuscript/`.
`config.yaml` sets the publication metadata, page geometry, figure height, and
output formats. The numbered Markdown sections use `preamble.md` and
`references.bib`. Run with a fresh checkout so all generated files belong to
the same source revision.

Install Pandoc, XeLaTeX, and the TeX packages listed in the
[pinned template requirements](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/README.md#L565-L574).
The template uses Python 3.14 or later. Run the following from the White Line repository root.

```bash
white_line_root="$(pwd)"
template_root="$(mktemp -d)/template"
git clone https://github.com/docxology/template "$template_root"
git -C "$template_root" checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2

uv sync --locked --python 3.11
uv run --locked --python 3.11 python scripts/build_figures.py

mkdir -p "$template_root/projects/working"
ln -s "$white_line_root" "$template_root/projects/working/white_line"

(
  cd "$template_root"
  uv sync --locked --no-dev
  uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/white_line
  uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/white_line
)

uv run --locked --python 3.11 python scripts/audit_project.py --require-render --write-manifest --report
uv run --locked --python 3.11 python scripts/check_figure_layout.py
```

The template resolves `working/white_line` inside its own `projects/` tree and
discovers `docs/manuscript/` in that checkout. It writes the PDF to
`output/pdf/white_line_combined.pdf` and the HTML to `output/web/index.html`
under the White Line checkout. The strict audit writes
`output/reports/white_line_audit.json`. Review the PDF and HTML for the ordered
sections, bibliography entries, and figure embeds before publishing.

The default audit is source-only: its zero exit code may defer missing rendered
artifacts, while the JSON still reports those errors and `passed: false`.
Only `--require-render` is the post-render release gate. Its PDF check verifies
the signature, not complete PDF validity; the external publication validator
remains separate.

The source manifest is a content fingerprint, not a timestamp or a claim that
the observations are independently verified. If manuscript or figure inputs
change, the manifest must be regenerated only after the bundle is rendered
again.
