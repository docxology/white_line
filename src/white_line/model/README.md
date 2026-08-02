# Ledger model

This folder defines the frozen records passed between the assessor and its
consumers. Start with [`kinds.py`](kinds.py) for the state vocabulary, then
[`records.py`](records.py) and [`reports.py`](reports.py).

Use `uv run pytest tests/test_assessor.py tests/test_api.py -q` when changing a
model boundary. Assessment behavior lives one level up in
[../assessor.py](../assessor.py), not here.

Read [AGENTS.md](AGENTS.md) for signatures and invariants, then
[../README.md](../README.md) and [../../../README.md](../../../README.md) for
the package and project context.

Project root: [AGENTS.md](../../../AGENTS.md) and [README.md](../../../README.md).
