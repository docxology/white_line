# Project commands

Run these commands from the project root:

```bash
uv run python scripts/check_registry.py
uv run python scripts/build_figures.py
uv run python scripts/audit_project.py --report
```

The first checks the live registry, the second regenerates `output/figures/`,
and the third checks source/render structure. All three run from this
repository alone. For a release bundle, render through the external
`docxology/template` engine before `--write-manifest`; that engine is the only
tool this project needs and does not contain.

Read [AGENTS.md](AGENTS.md) for flags and boundaries, then
[../docs/development.md](../docs/development.md) for the full sequence and
[../README.md](../README.md) for project orientation.

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
