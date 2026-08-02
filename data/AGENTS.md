# Data contract

This folder owns source data committed with the project. At present,
`claim_ledger.json` registers numeric manuscript claims and the source paths
that explain them. It does not own the Python registry (`../src/white_line/registry.py`),
generated figure registries, or rendered evidence reports.

Keep JSON valid and paths real. A ledger entry supports traceability only; it
does not independently verify an observation, establish completeness, safety,
legality, permission, or a hidden cause. Validate through the template Stage 04
workflow after a relevant manuscript change, then run the local audit.

Read [README.md](README.md), [../AGENTS.md](../AGENTS.md), and
[../docs/reproducibility.md](../docs/reproducibility.md).

Project root: [AGENTS.md](../AGENTS.md) and [README.md](../README.md).
