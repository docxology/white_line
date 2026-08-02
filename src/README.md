# Source package

The `white_line` package implements the typed absence ledger. Start at
[`white_line/__init__.py`](white_line/__init__.py) for public exports, then
[`white_line/assessor.py`](white_line/assessor.py) for staged assessment and
[`white_line/model/`](white_line/model/) for the immutable types.

Run the package through `uv run pytest -q`. Figure generation is an operator
command in [`../scripts/`](../scripts/), not a package import workflow.

See [AGENTS.md](AGENTS.md) for source ownership and
[white_line/README.md](white_line/README.md) for the internal module map.

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
