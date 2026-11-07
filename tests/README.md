# Tests

The suite verifies the ledger contract, the public API, generated figures, and
artifact audit. Start with [`test_assessor.py`](test_assessor.py) for assessment
behavior and [`test_review_identity.py`](test_review_identity.py) for exact
return bindings and fresh-assessment boundaries. Exercise documentation recipes
as disposable native smoke runs rather than pinning copied stdout.

Run all checks with `uv run pytest -q`. For source coverage use `uv run pytest
--cov=src --cov-report=term-missing -q`.

See [AGENTS.md](AGENTS.md) for test boundaries, then
[../docs/development.md](../docs/development.md) and
[../src/white_line/README.md](../src/white_line/README.md).

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
