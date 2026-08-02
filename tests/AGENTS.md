# Test folder contract

`tests/` exercises the public API, assessor, protocol, analysis, serialization,
deterministic figures, manuscript bindings, the audit gate, and cross-cutting
contracts.

## Test modules

- `test_api.py` — imports, version markers, public surface
- `test_white_line.py` — core package smoke and default call forms
- `test_assessor.py` — assess_absence staging, intake, conflict resolution
- `test_registry.py` — WHITE_RECORDS, registry digest, and lookups
- `test_invariants.py` — structural checks and planted-bad cases
- `test_protocol.py` — review_directives and follow-up actions
- `test_analysis.py` — decay timeline, conflict lattice, coverage matrix
- `test_dates.py` — date handling, undated objects, horizon expiry
- `test_serialization.py` — canonical JSON and registry digest
- `test_figures.py` — figure determinism and registry metadata
- `test_figure_legibility.py` — printed text size and page-fit constraints
- `test_manuscript_bindings.py` — prose, figure, and bibliography bindings
- `test_formalism.py` — formalism block parsing, prefixes, citation split
- `test_audit.py` — audit_project gate checks
- `test_docs.py` — documentation recipes produce expected output
- `test_publication_metadata.py` — publication metadata across config and package
- `test_scripts_cli.py` — every read-only script passes on good input
- `test_standalone.py` — the package works without sibling repos
- `test_witness_layer.py` — witness-layer contracts and return envelopes
- `test_no_mocks.py` — lexical ban on mocks, stand-in names, path hardcodes

## Invariants

- No mocks. Use real records, temporary output roots, and planted-bad registries.
- Keep project coverage at or above the `90` floor in `pyproject.toml`.
- Import figure builders from `white_line.figures`, not from `scripts/`.

## Validation

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 --cov-report=term-missing
```
