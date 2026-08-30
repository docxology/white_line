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

## Formalism claim ledger (2026-08-29)

`formalism_claim_ledger.json` declares the manuscript's formalism-block labels
(`def:`/`prop:`) and the facet-lattice numbers stated in 03b_formalism.md, so
the render engine's evidence registry resolves those `[@...]` cross-references
instead of reporting them as unsupported bibliography citations. Every row is
derived from the manuscript or the package;
`tests/test_formalism_claim_ledger.py` re-derives the whole set (including a
live `project_facets` sweep over all settlement × stance × temporality
combinations) and fails if a block is added, renamed, or removed without this
file following.
