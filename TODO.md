# Deferred work

This file tracks only open work. Completed windows are logged at the bottom;
`docs/claim_boundaries.md` and the audit gate define what the instrument may
claim regardless of anything listed here.

## Completed — review of 2026-10-20

The review is resolved in [docs/reviews/2026-10-20-resolution.md](docs/reviews/2026-10-20-resolution.md).
The standing Python 3.10/3.14 workflow replaces the historical one-off floor
measurements below; current measured results belong to the release packet.

## Historical interpreter measurements (superseded by the standing matrix)

- The 3.10 floor now has two real measurements beside the static check: on
  2026-07-29 the full suite was run under an actual Python 3.10 interpreter
  (`uv run --python 3.10 --isolated pytest tests/`) and all 352 tests passed,
  and on 2026-08-01 the same recipe was re-run after the suite had grown to
  358 tests — all 358 passed. That is still a dated observation, not a
  standing gate — `ruff`
  (`target-version = "py310"`) remains the only check that runs on every
  edit, and the historical defect this entry records (a construct that
  parsed on 3.12 but made `tests/test_manuscript_bindings.py` uncollectable
  on 3.10 while local runs stayed green) is exactly the kind a one-off
  measurement ages out of. A standing interpreter matrix would close the
  gap properly; the one-command recipe above makes re-measuring cheap.
## Open — inside the current instrument boundary

- `expiry_horizon`, `omitted_namings`, and the refresh-queue plate read one
  pinned observation set. The queue is therefore a demonstration of the helper
  over a constructed input, not a view of any accumulated review history.

## Open — from the 2026-07-29 window, deferred with a stated reason

- Pre-categorical holding (an `UNCLASSIFIED_HELD` record outside the state
  alphabet, proposed by the 2026-07-29 review) is noted as a candidate for
  the separate register work, not this ledger: intake here already leaves a
  typed trace for every rejected input, and a holding pen for observations
  with no category yet would be a new instrument, not a new state.

## Open — intentionally outside the current instrument boundary

- The shared witness register (cross-line co-registration of report
  envelopes) is a separate work by design; White Line ships the envelope
  export and stops. See `docs/correspondence.md`.
- No external attestation or independent observation provenance is claimed.
  Adding an independently authored observation ledger needs its own testable
  provenance contract; the evaluator must keep refusing to infer *why*
  something is absent.
- The registry is source-configured in Python. Moving it to an editable data
  file requires a separate validation and provenance contract (same ladder as the
  sibling instruments).
- Public release: `v0.8.0` shipped a tagged repository release with a release
  packet and compatible publication validation (`docs/releases/`), and
  `CITATION.cff`, `.zenodo.json`, and `docs/publication.md` carry the citation
  workflow. Still open: reserving and minting the next Zenodo version DOI
  using the reserve-first procedure, which the release packet records as
  pending.

## Standing discipline

- After ANY manuscript or figure edit: re-render through the external
  `docxology/template` engine (path-independent invocation in
  `docs/development.md`), then `audit_project.py --write-manifest --report`
  (staleness alone no longer blocks the rewrite; every other error still does).
- Reference the companion works by name and repository URL, never by a relative
  path and never by an import; `tests/test_standalone.py` fails on either. Never
  copy their prose, registries, or code.

## Log

- 2026-08-01 — comprehensive assessment pass (intelligence + visualizations),
  no code change required. Both phases were run against the live tree: the
  full suite (`uv run python -m pytest --cov=src --cov-branch
  --cov-report=term-missing`, 358 passed, 100.00% branch coverage), `uv run
  ruff check src tests scripts` clean, `check_registry.py` reporting the
  pinned digest `11047a64…`, a fresh `build_figures.py` (17 PNG/SVG pairs
  plus the two registry JSONs, byte-identical on rebuild), and the audit
  `--report`. Every figure is bound to a live computation or the registry,
  all 17 plates are embedded exactly once with no orphans, and a visual
  spot-check of the timestamp, refresh-queue, and horizon-dispersion plates
  found no clipped or overlapping labels. The manuscript's figures, tables,
  and prose counts (eleven records, five analysis-backed plates, four decay
  transitions) all re-derive from the code. The only non-green audit signal
  is the expected `source_manifest` staleness — `output/reports/source_manifest.json`
  (digest `8ceb1e14…`) predates the current source digest `f826d74e…`, and
  clearing it requires the external `docxology/template` render which is not
  present on this machine; `manifest_blocking_errors` confirms it is not a
  blocking error, so it is recorded here as the standing pre-render state.
  The one open reproducible-gap item (the 3.10 floor) was re-measured rather
  than left stale: the suite, now 358 tests, still passes in full under a real
  Python 3.10 interpreter via `uv run --python 3.10 --isolated pytest tests/`
  (see the open item above). No defects were found that warranted a change,
  and none was forced for its own sake.

- 2026-07-29 (second window) — the witness layer stated formally, and the
  lattice drawn. `manuscript/03b_formalism.md` gained fenced-Div definitions
  for the intake event, the witness facets, the return contract, and the
  report envelope (`def:event`, `def:facets`, `def:return`, `def:envelope`),
  each bound to `dataclasses.fields` of the live type, plus the projection
  rule and the factorization proposition with claim-to-test rows.
  `tests/test_formalism.py` grew the alphabet-vs-enumeration check, the
  projection cell-count re-derivation, and the factorization check, each
  with an in-suite positive control; on 2026-07-29 three further drifts were
  planted in the real manuscript (a dropped `STALE` from the $T$ alphabet, a
  $21 \to 22$ cell-count drift, a renamed envelope field) and each failed
  exactly its named test before byte-identical restoration. The
  `white_facets_lattice` plate (seventeenth figure) draws all 24 cells with
  the three `UNDISCLOSED`+`OPEN` fail-closed cells hatched and the live
  battery's landings marked; its registered caption, alt text, and
  boundaries were checked against the rendered image. One number in the
  previous window's entry was corrected during this verification: the truth
  table has 21 projecting cells and three fail-closed cells (one per
  temporal status), not 23 and one — re-derived by exhausting
  `project_facets` over $E \times D \times T$. Package 0.6.0 -> 0.7.0
  (version.py, pyproject.toml, manuscript/config.yaml — test-bound), cover
  art re-versioned. Measured gate (2026-07-29, this tree): 352 collected and
  passing tests, 100.00% branch coverage of `src/` (1893 statements, 464
  branches, 0 missed), `ruff check src tests scripts` clean, two independent
  figure builds byte-identical across all 36 artifacts, `check_registry.py`
  reporting the unchanged digest `11047a64…`, and
  `audit_project.py --write-manifest --report` then `--report` both
  `passed: true` with zero errors and zero warnings.

- 2026-07-29 — the witness layer: facets, returns, envelope, and conflict
  co-presence. Prompted by "The Space Between the Lines" (an external
  reviewer, with an analytic reader, 2026-07-29), a design review of the line
  set; the received review
  and the adopted/deferred/declined mapping are recorded in
  `docs/correspondence.md`, including answers to its three direct questions.
  Four additions, none of which changes what the assessor records or emits:
  (1) `IntakeEvent.displaced_state` — both reconciliation events now carry
  the displaced observation's state typed, so a conflict survives as two
  co-present surfaces rather than only as a note; the cautious resolution is
  unchanged and the event messages are byte-identical. (2) `facets.py` — the
  caution order factored into epistemic settlement × disclosure stance ×
  temporal status (`WitnessFacets`), with `project_facets` recovering the
  shipped state; the projection property is proven branch-by-branch over
  `scoring_branch_battery` and the worked report, the full 24-cell truth
  table is pinned (21 project; the three `UNDISCLOSED`+`OPEN` cells — one per
  temporal status — fail closed, re-derived 2026-07-29 by exhausting
  `project_facets` over $E \times D \times T$),
  and decay is recovered as `NAMED`+`STALE` → `UNRESOLVED`, so a decayed
  naming keeps its prior naming and age. The derivation fails closed on an
  `UNRESOLVED` finding this assessor could not have written. (3) `returns.py`
  — one `ReturnContract` per finding: trigger, due date (the last current
  review date, proven by assessing the same observation on the due date and
  one day after), expected return, and acceptance condition; a `WITHHELD`
  return is boundary confirmation never disclosure, an `UNRESOLVED` return
  may honestly stay open, and every contract points back at its report's
  review date and registry digest. (4) `envelope.py` plus
  `serialization.canonical_report`/`report_digest` — the cross-instrument
  report envelope (`line.report-envelope/1.0`) pointing at the complete
  canonical report by digest, carrying the instrument's transportable
  non-claims; `envelope_matches_report` verifies an archived pair. The
  shared witness register the review proposes is deliberately NOT built
  here (see `docs/correspondence.md`). Package 0.5.0 -> 0.6.0 for the new
  public surface; `LEDGER_VERSION` unchanged because registry content did
  not change (digest `11047a64…` verified unchanged). Measured gate: 340
  collected and passing tests (312 before; 28 new in
  `tests/test_witness_layer.py`), 100.00% branch coverage of `src/` (1832
  statements, 442 branches, 0 missed), `ruff check src tests scripts` clean
  under the pinned config, two independent figure builds byte-identical
  across all 34 artifacts (cover re-versioned to 0.6.0), a re-rendered
  37-page PDF, and an audit after `--write-manifest` reporting
  `passed: true` with zero errors and zero warnings.

- 2026-07-28 — formalism auto-numbering, defect batteries, scholarship, and an
  editorial pass. The formal-method section no longer contains a hand-written
  number: all thirteen definitions and eight propositions are fenced Divs
  (`::: {.definition #def:name title="Name"}`), every cross-reference is
  `[@label]`, and the claim-to-test table is keyed on labels. The lettered
  Propositions A-H became labelled blocks that the renderer numbers 1-8.
  `src/white_line/formalism.py` reproduces the renderer's reading of that
  syntax so the audit and the tests share one parse; without it the audit's
  citation scan would have reported `def:kinds` as a missing bibliography key.
  `tests/test_formalism.py` (36 tests) asserts that every block carries a
  correctly prefixed unique label, that every reference resolves, that no
  manuscript file writes a formalism number outside a code block, and that
  every block has a binding row — each paired with a positive control. Proved
  by planting three violations at once (a prose "Proposition 3", a typo'd
  `[@prop:totalitee]`, and a block with its identifier removed): five tests
  failed and the files were restored.
  Formal-method completeness: every definition is now compared against the code
  it describes rather than merely stated near it — alphabets against the
  enumerations, tuple definitions against `dataclasses.fields`, the caution
  order against `caution_rank`, the intake partition against `IntakeCode` and
  `SET_ASIDE_CODES`, the date branches against `usable_observation_date`, the
  scoring reasons against findings a live `assess_absence` returned, and the
  directive map against the protocol. The scoring reasons were extracted into
  named constants (`SCORING_REASONS`) so the manuscript quotes the code's own
  strings. `invariant_defect_battery` and `scoring_branch_battery` moved
  detection and branch coverage out of the test suite and into the package,
  where a figure and the manuscript can read them.
  Scholarship: eight sources added and each verified against its publisher or
  DOI record before use — Sells 1994 and Turner 1995 (apophasis reads as
  performed unsaying, not reported experience), Little 1988, Molenberghs et al.
  2008, and Manski 2003 (observed data cannot adjudicate MNAR against its MAR
  counterpart; partial identification reports bounds where White Line reports
  nothing), and Oreskes & Conway 2010, Rayner 2012, and Gross & McGoey 2015
  (manufactured doubt and uncomfortable knowledge are processes with agents the
  ledger cannot represent).
  Figures: two new derived plates, `white_reason_trail` (the ordered reasons a
  live assessment wrote for each branch of the scoring rule) and
  `white_invariant_battery` (the detail string each check returned when handed
  a registry built to defeat it), taking the registry from fourteen to sixteen.
  Package 0.4.0 -> 0.5.0 for the new public surface; `LEDGER_VERSION` unchanged
  because registry content did not change.
  Measured gate: 312 collected and passing tests (270 before), 100.00% branch
  coverage of `src/` (1656 statements, 396 branches, 0 missed),
  `ruff 0.16.0 check src tests scripts` clean under the pinned config, two
  independent figure builds byte-identical across all 34 artifacts, minimum
  rendered label size 6.20 pt across all sixteen plates, a 37-page PDF (34
  before) with 0 undefined references, 0 undefined citations, no `??`, and no
  literal `[@...]` markup, and an audit reporting `passed: true` with zero
  errors and zero warnings.

- 2026-07-27 — adversarial verification pass. Three defects found and fixed,
  each re-derived rather than inherited. (1) `docs/architecture.md` claimed
  "the package root re-exports the entire public surface, so every callable
  above is importable directly from `white_line`", while five names its own
  module table lists — `EXPIRY_AS_OF`, `expiry_observations`, `expiry_report`,
  `intake_reachability_battery`, and `LEDGER_VERSION_DIGEST` — were absent
  from the root. The code was strengthened to match the prose rather than the
  prose weakened, and `tests/test_api.py` now parses that table and asserts
  every backticked identifier in it resolves at the root, so the sentence is
  bound to the table it summarizes. (2) `scripts/check_registry.py` and
  `scripts/check_figure_layout.py` had no argument parser: both accepted an
  unrecognized flag or a stray positional and exited `0`, printing a clean
  report for a command that was never run. Both now parse, and
  `tests/test_scripts_cli.py` runs every script in `scripts/` against five
  classes of undefined input and requires a non-zero exit plus a usage line.
  (3) The registered caption and alt text for `white_distribution_panels`
  described the two panels as side by side ("on the left"/"on the right");
  the plate stacks them, intake events at canvas y=346-828 above the coverage
  matrix at y=950-1388, which is what the manuscript embed already said. The
  caption was corrected to the manuscript's reading; the PNG bytes are
  unchanged. Also re-rendered and re-wrote the source manifest, which had gone
  stale when a manuscript edit landed without a re-render — a true positive,
  not a nuisance failure. Measured gate: 246 collected and passing tests,
  100.00% branch coverage of `src/` (1446 statements, 346 branches, 0 missed),
  `ruff 0.13.0 check src tests scripts` clean under the pinned config, two
  independent figure builds byte-identical, minimum rendered label size
  6.20 pt across all fourteen plates, and an audit reporting `passed: true`
  with zero errors and zero warnings. The legibility gate was positive-
  controlled by lowering `MIN_TEXT_SIZE` to 17 and one `white_caution_ladder`
  label with it: the gate failed at 5.8599 pt and named the plate, and both
  files were restored to their exact prior SHA-256.

- 2026-07-27 — legibility, binding, and inspection pass. Every in-figure label
  now prints at or above six points: the shipped PDF's smallest label measured
  3.39 pt before (the scholarship matrix, whose 12-unit labels rendered at 255
  ppi because a `height=0.5\textheight` cap bound before width) and 6.20 pt
  after, measured with `pdfimages -list` on both PDFs. The fix is structural —
  `canvas.MIN_TEXT_SIZE` refuses a label below the floor, `MAX_CANVAS_WIDTH`
  refuses a canvas that would shrink one, `rendering.figure_height_fraction`
  and `front_matter_figure_height_fraction` are both 1.0 so width binds for
  every plate, and `tests/test_figure_legibility.py` re-derives each plate's
  printed size from the PNG dimensions, the embed width, and the page geometry,
  cross-checked against the `\textwidth` and per-figure fractions the last
  render actually used. Added three derived plates (`white_expiry_queue`,
  `white_horizon_dispersion`, `white_intake_reachability`), taking the registry
  from eleven to fourteen. Added `tests/test_manuscript_bindings.py`, which
  re-derives every table and count in the manuscript rather than checking for
  substrings — the omission of `UNDATED_OBJECT` from the intake table survived
  the old lexical checks and is now impossible. Pinned `LEDGER_VERSION_DIGEST`
  and the per-artifact PNG/SVG byte digests so a registry reword or a
  hand-edited raster fails the audit. Closed Proposition B at arity three,
  corrected the refresh queue's band split so a reviewer-asserted `UNRESOLVED`
  is no longer drawn as "already decayed", fixed `SET_ASIDE_CODES` being
  declared in `white_line.models.__all__` without being imported, and removed a
  vacuous `... or True` assertion. Measured gate: 221 collected and passing
  tests, 100.00% branch coverage of `src/` (1446 statements, 346 branches, 0
  missed), `uvx ruff check src tests scripts` clean under the newly pinned
  config, two independent figure builds byte-identical, and an audit reporting
  `passed: true` with zero errors and zero warnings.

- 2026-07-26 — additive API + documentation pass: bumped the package version
  0.3.0 -> 0.4.0 for `expiry_horizon`, `ExpiryEntry`, and
  `IntakeCode.UNDATED_OBJECT` while holding `LEDGER_VERSION` at `2026.07`;
  made the package root re-export the full public surface (including the
  audit, dates, and figures APIs); converted `figures/**` self-imports from
  absolute to relative form; unified all three `scripts/` entrypoints on the
  editable-install bootstrap with no `sys.path` manipulation; and corrected
  the documentation drift from those changes. Gate: 100.00% branch coverage of
  `src/`, and an audit whose only outstanding error was the expected
  source-manifest staleness (zero blocking errors). The test count originally
  recorded here — and in the entry below — was 132 in both, carried forward
  rather than re-measured; a later audit collected 137 from the same
  changeset, so neither figure described the tree it was written against. The
  numbers are dropped rather than replaced, because the intermediate trees are
  not recoverable and a substituted count would be no better sourced than the
  one it replaced. Re-measure with
  `uv run pytest tests/ --collect-only -q | tail -1`. The "ruff clean" claim in
  the original entry named no rule set or target version and was not
  reproducible; `pyproject.toml` pins both as of 2026-07-27.

- 2026-07-26 — remediation closure: extracted the figure builder and audit
  gate into `src/white_line/`; unified date handling in `dates.py`; shared the
  worked example; added `expiry_horizon` and `UNDATED_OBJECT`; expanded audit
  tests; documented every folder; and added executed review-protocol recipes.
  Final gate: 100.00% branch coverage of `src/`. (Test count dropped; see the
  note in the entry above.)

- 2026-07-22 — distributional expansion + operability pass: added
  `src/white_line/analysis.py` (`decay_timeline`, `decay_transition_offsets`,
  `reconciliation_matrix`, `events_tally`, `coverage_matrix`), two derived
  embedded figures (`white_decay_timeline`, `white_conflict_lattice`), new
  manuscript section `04b_distributional_views.md` plus layers/formalism/limits
  expansions with executed-probe corrections (per-kind horizons, last-listed
  duplicate semantics); `audit_project.py` gained the bidirectional
  figure-link check (orphan figures now fail, positive-controlled in
  `tests/test_audit.py`) and the stale-manifest rewrite deadlock fix;
  `.agents/skills/white-line/SKILL.md` and `AGENTS.md` created. Suite
  50 → 75 passing; audit `passed: true` with zero errors.
