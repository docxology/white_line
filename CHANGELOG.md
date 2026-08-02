# Changelog

## 0.7.0 — 2026-07-29

The witness layer: facets, returns, envelope, conflict co-presence, plus its
formalism window and the facets-lattice plate.

### Witness layer

- `facets.py` separates the rich state from the cautious projection:
  epistemic settlement × disclosure stance × temporal status, with
  `project_facets` recovering the shipped state and the decay rule recovered
  as `NAMED` + `STALE` projecting to `UNRESOLVED`.
- `returns.py` upgrades the review horizon from calendar to obligation:
  trigger, due date, expected return, and an acceptance condition under which
  remaining `UNRESOLVED` is an honest outcome and a `WITHHELD` return is
  boundary confirmation.
- Reconciliation events now carry the displaced observation's state typed
  (`IntakeEvent.displaced_state`), so a conflict is preserved as two surfaces.
- `envelope.py` exports the common report envelope under
  `line.report-envelope/1.0`, with `canonical_report`/`report_digest` added so
  the envelope has a complete native record to point at.
- `manuscript/02c_reproducibility.md` gained the formalism definitions for the
  facet alphabets, `WitnessFacets`, the projection rule, `ReturnContract`,
  `ReportEnvelope`, and `IntakeEvent`; each block bound to a named test.
- New derived plate `white_facets_lattice` draws the full 24-cell projection
  with the live battery's findings marked. The projection truth table is
  21 projecting / 3 fail-closed cells, re-derived and corrected in this window.

### Other

- All 17 SVGs gained accessibility markup; background shifted `#F5E6D3` to
  `#F2EDE5` (differentiates from black_line); 5 tall plates reduced to
  ≤1570px.
- `declared_prefixes()` in `formalism.py` returns `sec`/`fig` to exclude
  cross-references from bibliography-citation matching.
- `tests/test_formalism.py` dangling check excludes `sec`/`fig`;
  `tests/test_manuscript_bindings.py` direction test updated.
- `src/white_line/figures/plates/AGENTS.md` gained `evidence.py`,
  `inspection.py`.
- All READMEs with sibling AGENTS.md now redirect to it.

### Gates

- Full suite: 358 passed, branch coverage 100.00% (1893 statements, 464
  branches, 0 missed).
- Double figure build: byte-identical across all 36 artifacts (17 plates).
- `check_registry.py`: 11 records, `LEDGER_VERSION=2026.07`, digest
  `11047a641a8e…`.
