# Package contract

`white_line` owns the typed ledger. It does not own human authorization,
consent, safety, legality, motive, or a hidden cause. States describe a record
under supplied observations and a supplied review contract.

The package root re-exports the entire public surface listed below: every
callable in this contract is importable directly from `white_line`, and
nothing here is submodule-only.

## Public modules and callables

- `assessor.py`: `assess_absence(observations, records=WHITE_RECORDS,
  as_of=None) -> WhiteReport`. Intake records set-asides, matching retains the
  most cautious assertion, and dated `NAMED` findings older than a record's
  horizon report `UNRESOLVED`.
- `analysis.py`: `decay_timeline(observations, start, end,
  records=WHITE_RECORDS, step_days=1) -> tuple[DecayPoint, ...]`;
  `decay_transition_offsets(points) -> tuple[int, ...]`;
  `reconciliation_matrix() -> dict[tuple[AbsenceState, AbsenceState], AbsenceState]`;
  `events_tally(report) -> dict[IntakeCode, int]`;
  `coverage_matrix(report) -> dict[AbsenceKind, dict[AbsenceState, int]]`;
  `expiry_horizon(report, records=WHITE_RECORDS) -> tuple[ExpiryEntry, ...]`.
  These are pure, additive views, not a second assessor or a score.
- `protocol.py`: `review_action_for_state(state) -> ReviewAction`,
  `requires_follow_up(state) -> bool`, `directive_for_finding(finding) ->
  ReviewDirective`, and `review_directives(report) -> tuple[ReviewDirective,
  ...]`. Directives name bounded follow-up, never approval or safety status.
- `registry.py`: `WHITE_RECORDS`, `record_ids() -> tuple[str, ...]`, and
  `records_by_kind() -> dict[AbsenceKind, tuple[AbsenceRecord, ...]]`.
- `invariants.py`: `all_ledger_checks(records=WHITE_RECORDS) ->
  tuple[LedgerCheck, ...]`, `ledger_sound(records=WHITE_RECORDS) -> bool`, and
  per-invariant checks `ids_are_distinct`, `ids_are_canonical_slugs`,
  `fields_are_inhabited`, `kinds_are_valid_and_covered`,
  `horizons_are_positive`, and `serialization_is_stable`, each taking
  `records` and returning `LedgerCheck`.
- `serialization.py`: `canonical_registry(records) -> str`,
  `registry_digest(records) -> str`, and `registry_manifest(records) ->
  dict[str, object]` provide order-independent registry review data.
- `dates.py`: `coerce_date(value, argument) -> date` and
  `coerce_review_date(value) -> date` are supported caller-boundary helpers
  for explicit review-date coercion.
- `facets.py`: `finding_facets(finding) -> WitnessFacets`,
  `report_facets(report) -> tuple[WitnessFacets, ...]`, and
  `project_facets(facets) -> AbsenceState`: the caution order factored into
  epistemic settlement x disclosure stance x temporal status, with the
  projection recovering the shipped state. A derived view, never a new
  observation.
- `returns.py`: `return_contracts(report) -> tuple[ReturnContract, ...]` reads
  each review horizon forward as a bounded follow-up obligation — trigger, due
  date, expected return, and acceptance condition per finding.
- `envelope.py`: `report_envelope(report, subject_id) -> ReportEnvelope`,
  `canonical_envelope(envelope)`, `envelope_matches_report(envelope, report)`,
  and `SCOPE_AND_NONCLAIMS`: the cross-instrument
  `line.report-envelope/1.0` transport record pointing at the complete
  canonical report by digest.
- `formalism.py`: `parse_blocks`, `declared_prefixes`, `split_citations`,
  `hand_written_numbers`, `strip_code`, `read_manuscript`, `FORMALISM_TITLES`,
  and `FORMALISM_PREFIXES` read the manuscript's fenced formalism blocks the
  way the renderer's numbering filter does, so the audit and the tests share
  one reading.
- `worked_examples.py`: `WORKED_AS_OF`, `worked_intake_observations() ->
  tuple[object, ...]`, and `worked_report() -> WhiteReport` are the shared
  deterministic documentation and figure fixture; `EXPIRY_AS_OF`/
  `expiry_observations()`/`expiry_report()`, `intake_reachability_battery()`,
  and `scoring_branch_observations()`/`scoring_branch_battery()` back the
  expiry, reachability, and branch-coverage figures.
- `audit.py`: `audit_project(project_root) -> dict[str, Any]`,
  `digest_inputs(project_root) -> tuple[str, list[str]]`,
  `figure_link_errors(...) -> list[str]`, `manifest_blocking_errors(errors) ->
  list[str]`, and `write_source_manifest(project_root, report) -> Path` check
  source/render agreement. They do not verify an observation's truth.
- `version.py` defines `__version__`, `LEDGER_VERSION`, and
  `LEDGER_VERSION_DIGEST`; registry-content changes require `LEDGER_VERSION`
  to be bumped and the pinned digest re-verified, or the audit fails. `models.py` is an import-compatible
  re-export of `model` and must remain faithful.

The immutable types and their methods are documented in
[model/AGENTS.md](model/AGENTS.md); figure APIs are in
[figures/AGENTS.md](figures/AGENTS.md). Preserve the caution-only-rises rule,
ledger-reserved `NOT_RECORDED`, typed intake trace, explicit review date and
digest, and pure analysis boundary.

Run `uv run pytest -q` and `uv run pytest --cov=src --cov-report=term-missing
-q`. Start with [README.md](README.md); repository rules are in
[../../AGENTS.md](../../AGENTS.md) and the source-root contract in
[../AGENTS.md](../AGENTS.md).

Project root: [AGENTS.md](../../AGENTS.md) and [README.md](../../README.md).
