# Figure plates

Each module returns SVG for a declared White Line plate. `overview.py` draws
registry and orientation views, `contract.py` draws assessment and directive
views, and `distributions.py` draws the analysis-derived views.

Do not call these modules to write artifacts directly. Run `uv run python
scripts/build_figures.py` from the project root; `build_figures` registers and
writes every plate under `output/figures/`.

See [AGENTS.md](AGENTS.md) for renderer signatures,
[../README.md](../README.md) for the artifact flow, and
[../../../../README.md](../../../../README.md) for project orientation.

Project root: [AGENTS.md](../../../../AGENTS.md) and [README.md](../../../../README.md).
