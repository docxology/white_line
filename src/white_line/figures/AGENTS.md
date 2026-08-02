# Figure package contract

This folder owns deterministic SVG/PNG generation and plate registration. It
does not own ledger assessment, analysis semantics, manuscript prose, or a
claim about observed work. Generated figures are schematics of the supplied
registry and report contract.

## Public surface

- `__init__.py` exports `FIGURE_PLATES`, `FigurePlate`, and
  `build_figures(project_root: Path | None = None) -> list[Path]`.
- `build.py` writes SVG and PNG files plus `white_registry.json` and
  `figure_registry.json` beneath `output/figures/`; it calls the configured
  `rsvg-convert` executable. The build order and metadata are deterministic.
- `plates/` defines `FigurePlate(name: str, render: Callable[[], str], label:
  str, caption: str, alt: str, source: str)` and the ordered `FIGURE_PLATES`
  registry. Its renderers are documented in [plates/AGENTS.md](plates/AGENTS.md).
- `canvas.py` provides `escape_text`, `open_canvas(width, height)`,
  `rect(...)`, `text(x, y, value, size, fill, weight)`, `wrap_lines(value,
  size, max_width, bold)`, and `marker(shape, cx, cy, radius, fill)`. It also
  owns two hard limits: `MAX_CANVAS_WIDTH`, because a wider canvas shrinks
  every label on the printed page, and `MIN_TEXT_SIZE`, below which `text`
  raises rather than drawing an unreadable label.
- `metrics.py` supplies Helvetica advance widths and reads rendered plates
  back — every `<text>` element, the declared canvas size, and a PNG's pixel
  dimensions. `legibility.py` turns those into a printed point size using the
  manuscript's embed width and page geometry.
- `palette.py` provides constants and complete display maps, including a
  marker shape per kind so no figure encodes a category in colour alone; it
  has no public callables.

Adding a plate is atomic: update `FIGURE_PLATES`, the count and label
assertions in `tests/test_figures.py`, `docs/development.md`, and a manuscript
embed by filename. No module docstring carries a plate count. A registered but
unembedded figure fails the audit. Do not hand-edit generated files to pass a
gate: `figure_registry.json` records every PNG and SVG byte digest and the
audit re-derives them.

Run `uv run pytest tests/test_figures.py -q`; use `uv run python
scripts/build_figures.py` to regenerate artifacts. Read [README.md](README.md),
[../AGENTS.md](../AGENTS.md), and [../../../AGENTS.md](../../../AGENTS.md).

Project root: [AGENTS.md](../../../AGENTS.md) and [README.md](../../../README.md).
