# `.agents/` — technical reference

Agent skill descriptors for this project. This directory carries no executable
code and no import surface: the package never reads it, `pytest` never collects
it, and `white_line.audit` never inspects it.

## Layout

| Path | Holds |
| --- | --- |
| [`skills/`](skills/) | One directory per skill descriptor |
| [`skills/white-line/SKILL.md`](skills/white-line/SKILL.md) | The operating walkthrough for this project |

## What a change here must preserve

- **Descriptors follow the code, not the reverse.** A statement in a descriptor
  is a claim about the current API. When `src/white_line/` changes, the
  descriptor is updated in the same change or it is wrong.
- **The root [AGENTS.md](../AGENTS.md) is authoritative.** Where a descriptor
  and the working contract disagree, the contract wins and the descriptor is
  the defect.
- **Gotchas are probed, not recalled.** Every behaviour the skill describes as
  a gotcha — the undated date object recording `UNDATED_OBJECT`, `as_of=None`
  anchoring to today, a future-dated observation being ignored, duplicate
  handling keeping the last-listed — was executed against the real API before
  being written down. Re-probe before editing one.
- **The absence boundary holds here too.** States describe a record under a
  supplied review contract, never people, motives, safety, legality,
  permission, or hidden causes.

## Verifying a descriptor

There is no automated gate over this directory, so check it by hand against the
code it describes:

```bash
uv run python -c "import white_line; print(sorted(white_line.__all__))"
uv run pytest -q
```

Every symbol a descriptor names must appear in the package's public surface or
in a module it names explicitly.

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
