# Development

Run the pure-standard-library instrument and its reproducible outputs with:

```bash
uv run python scripts/check_registry.py
uv run python scripts/build_figures.py
uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing
uv run ruff check src tests scripts
uv run mypy src
uv run python scripts/audit_project.py --report
```

Every command above runs from a clone of this repository alone. `output/` is
git-ignored, so the figure build comes before the checks that read it;
`tests/conftest.py` also rebuilds `output/figures/` when it is absent, using this
project's own deterministic builder, so the suite is order-independent rather
than order-fragile. The rebuild is never masked: a builder failure surfaces as
an error.

The lint rules and the `py310` target are pinned in `pyproject.toml`, so the
lint command reproduces rather than depending on whatever settings happen to be
in effect. The target version is load-bearing and not cosmetic: the package
declares `requires-python = ">=3.10"`, and ruff is the only gate here that
catches a construct which parses on 3.12 but not on the declared floor. The
standing `.github/workflows/ci.yml` matrix runs the suite on Python 3.10 and
3.14. Each job builds figures and checks branch coverage, lint, types, the
registry and source audit. Template publication checks remain a separate
external release gate. Use `uv sync --locked` for the recorded tool versions.

`white_line.figures.build_figures` writes seventeen deterministic SVG/PNG
compositions plus the
registry JSON files under `output/figures/`. The audit checks the registry,
figure metadata and links, the recorded PNG and SVG byte digests, bibliography
keys in both directions, required PDF/HTML artifacts, and
source headings in the rendered combined manuscript. It is a consistency gate,
not a truth verifier. For visual iteration, pass a disposable `project_root`
on the mounted development volume to `build_figures`, inspect the resulting PNGs, and copy
only the reviewed generated artifacts into the project output directory.

`tests/test_figure_legibility.py` is the printed-size gate. It reads each
plate's canvas size out of its rendered SVG, the `width=` attribute out of the
manuscript embed, and the page geometry out of `manuscript/config.yaml`, then
computes what a label of `N` canvas units measures on paper and fails below
six points. Two further checks cross-read the `\textwidth` and per-figure
`width`/`height` fractions from the last rendered `.log` and `.tex`, so a
template-side geometry change surfaces as a failure rather than as a quietly
wrong number. Re-render before trusting a green legibility run after any
`config.yaml` or embed-width edit.

Numeric manuscript claims that are not already emitted by the package or its
configuration are registered in `data/claim_ledger.json`. Each row names the
claim and points to the manuscript source that explains it; the sibling
template's evidence-registry validator checks those paths during Stage 04.

Figure rasterization requires `rsvg-convert` from librsvg on `PATH`; it is a
system rendering prerequisite, not a runtime package dependency.

For a full rendered bundle you need one external tool: the `docxology/template`
render engine. It is not vendored here and nothing in this repository can
produce `output/pdf/` or `output/web/` without it. That is an honest external
dependency, and everything above — tests, coverage, registry check, figures, the
legibility gate, and the source-side audit — runs without it.

The template locates a project by a qualified name under its own `projects/`
directory, so link this checkout in from wherever it lives rather than assuming
any particular layout:

```bash
# WHITE_LINE_ROOT: this checkout, anywhere on disk.
# TEMPLATE_ROOT:   a clone of https://github.com/docxology/template, anywhere.
# Both are assigned here; change either path to suit your machine.
export WHITE_LINE_ROOT="$(pwd)"
export TEMPLATE_ROOT="${TEMPLATE_ROOT:-$HOME/template}"

# Clone the engine only if that directory does not already hold one.
[ -d "$TEMPLATE_ROOT/.git" ] || git clone https://github.com/docxology/template "$TEMPLATE_ROOT"

mkdir -p "$TEMPLATE_ROOT/projects/working"
ln -sfn "$WHITE_LINE_ROOT" "$TEMPLATE_ROOT/projects/working/white_line"

cd "$TEMPLATE_ROOT"
uv run python scripts/pipeline/stage_03_render.py --project working/white_line

cd "$WHITE_LINE_ROOT"
uv run python scripts/audit_project.py --write-manifest --report
```

`working/white_line` is the qualified project name the template resolves, not a
path relative to this repository. The render writes back into this checkout's
`output/`, which is why the audit is run here afterwards.

The source manifest is a content fingerprint, not a timestamp or a claim that
the observations are independently verified. If manuscript or figure inputs
change, the manifest must be regenerated only after the bundle is rendered
again.
