# Source-root contract

`src/` is the import root for the `white_line` package. It owns package code,
not command-line orchestration (`../scripts/`), tests (`../tests/`), prose
(`../docs/` and `../manuscript/`), or generated artifacts (`../output/`).

The only package directory is [`white_line/`](white_line/). Its public import
surface is defined by `white_line.__all__`; preserve that surface when
reorganizing modules. `white_line.models` is a public alias exporting the same
names as `white_line.model`; both import paths are supported, so keep them in
step. Run `uv run pytest -q` after source changes and `uv run pytest --cov=src
--cov-report=term-missing -q` before handoff.

Read [README.md](README.md) for orientation, the root [AGENTS.md](../AGENTS.md)
for repository invariants, and [white_line/AGENTS.md](white_line/AGENTS.md)
for the module-level contract.

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
