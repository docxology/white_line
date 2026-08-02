# `white-line` skill — technical reference

| File | Role |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The descriptor: YAML frontmatter (`name`, `description`) plus the body |
| [`AGENTS.md`](AGENTS.md) | This file — the folder contract |
| [`README.md`](README.md) | Orientation for a person browsing the tree |

## Audience

Agents that need to assess observations against the registry, read a
`WhiteReport`, sweep decay horizons, tabulate intake events, check the registry
digest, or run the publication audit.

## What the descriptor asserts, and where each claim is checked

| Claim in `SKILL.md` | Checked against |
| --- | --- |
| `assess_absence` signature and staging | [`src/white_line/assessor.py`](../../../src/white_line/assessor.py) |
| The four states and the caution order | [`src/white_line/model/kinds.py`](../../../src/white_line/model/kinds.py) |
| Intake codes, including `UNDATED_OBJECT` | [`src/white_line/model/reports.py`](../../../src/white_line/model/reports.py) |
| Registry size and per-kind horizons | [`src/white_line/registry.py`](../../../src/white_line/registry.py) |
| Analysis helpers and what they omit | [`src/white_line/analysis.py`](../../../src/white_line/analysis.py) |
| Follow-up actions | [`src/white_line/protocol.py`](../../../src/white_line/protocol.py) |
| The release sequence and gate | [`src/white_line/audit.py`](../../../src/white_line/audit.py) |

## What a change here must preserve

- The frontmatter `name` is `white-line`; a runtime loads the skill by that
  name, so renaming it breaks callers.
- The `description` carries the USE WHEN trigger. Keep it accurate: an
  over-broad trigger loads the skill for work it does not cover.
- The gotchas section describes probed behaviour. Re-run the probe before
  editing an entry — in particular the undated-date-object path, which is
  accepted, records `UNDATED_OBJECT`, and does not decay.
- The claim boundary holds: the ledger records state and never infers why
  something is absent.

## Verifying

```bash
uv run python -c "import white_line; print(sorted(white_line.__all__))"
uv run python scripts/check_registry.py
uv run pytest -q
```

Project root: [AGENTS.md](../../../AGENTS.md) and [README.md](../../../README.md).
