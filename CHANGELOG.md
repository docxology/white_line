# Changelog

## 0.9.1 — 2026-11-08

- Documentation-only patch: use the current Line Set declaration, distinguish
  Copper's resource accounting from completeness and Iron's recorded recovery
  comparisons from missing-evidence records, and state access-controlled sources.
- Delete incidental signature, source-field, alphabet/prose, structural-count,
  and test-name wiring assertions without repinning them. Preserve native date
  branches, reason coverage, projection/factorization calculations, metadata
  validity, and historical byte custody; label the selected test table honestly.
- Synchronize current descriptive version metadata. Native evaluator semantics,
  ledger identity, schemas, historical captures, and DOI identities are unchanged.
  No generated artifacts, deposit, or new release verification is asserted here.

## 0.9.0 — 2026-11-06

- Use native numbered section citations without duplicated prefixes or nested
  hand-written links in the manuscript roadmap.
- Correct the documented native witness signatures and add a human-governed
  exact-return recipe that retains every unaccepted prior obligation.
- Align CI, Ruff, mypy, and support prose with the existing Python >=3.11
  requirement and selected Python 3.15 interpreter; dependency requirements
  are unchanged.
- Distinguish the original four colors from the current eight peer instruments,
  the colorless wrapper, and Witness. Use American English in maintained prose
  and figure sources; preserve historical evidence.
- Replace wording and copied-output assertions with native behavioral return
  regressions. Assessment, facets, contradiction handling, and native ledger
  and report identities are unchanged.
- Keep facet-lattice state, staleness, and live-battery annotations inside their
  cells with additional vertical clearance.
- Clarify the retained citation cohort without treating it as the current
  instrument roster; keep citation checks independent of incidental counts.
- Express the figure-legibility geometry comment in millimeters and check the
  typed rejection rather than pinning its wording.
- Keep the rendered-bundle check false when a PDF exists but lacks its PDF
  signature; the error list and check status now describe the same boundary.
- Size reason-trail rows from the actual text leading, preserving clearance
  between the computed reason trail and the next row.
- Distinguish source-only audit success from the mandatory post-render
  `--require-render` release gate. No new Zenodo deposition is asserted.
- Emit figure registry 2.0 with canonical `alt_text` metadata and migrate the
  native audit consumer, so the publication engine can resolve accessible
  descriptions without falling back to captions. Retain historical registries.
- Remove the lexical superseded-code branding check, which rejects descriptive
  compatibility-test names without testing native behavior.

## 0.8.0 — 2026-10-21

Bind derived views to the producing registry and return contracts to the exact
native report. Add independent envelope contract validation and whole-envelope
digests, with custom registry versions explicitly unknown. Typed assertion
provenance replaces display-reason parsing in facets. Reject malformed facet
values, fix unsupported-date equality, require whole-string slugs, and guard
calendar endpoints. Document finite producer and retained-history boundaries.
Add a standing Python 3.10/3.14 matrix, locked lint/type tooling, and executed
counterexamples. The state alphabet, caution order, registry content, and
withholding boundary are unchanged. See the
[review disposition](docs/reviews/2026-10-20-resolution.md) and release packet.

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
