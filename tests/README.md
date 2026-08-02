# Tests

The suite verifies the ledger contract, the public API, lexical guardrails,
generated figures, documentation recipes, and artifact audit. Start with
[`test_assessor.py`](test_assessor.py) for assessment behavior and
[`test_docs.py`](test_docs.py) for pinned recipe execution.

Run all checks with `uv run pytest -q`. For source coverage use `uv run pytest
--cov=src --cov-report=term-missing -q`.

See [AGENTS.md](AGENTS.md) for test boundaries, then
[../docs/development.md](../docs/development.md) and
[../src/white_line/README.md](../src/white_line/README.md).

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
