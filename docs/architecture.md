# Architecture

White Line is a small modular package under `src/white_line/`:

| Module | Responsibility |
| --- | --- |
| `model/` | Typed vocabulary: `kinds.py` (`AbsenceKind`, `AbsenceState`, `caution_rank`), `records.py` (`AbsenceRecord`), `reports.py` (`AbsenceObservation`, `IntakeCode`, `IntakeEvent` — whose `IntakeEvent.displaced_state` field keeps a reconciled-away assertion typed and co-present — `AbsenceFinding`, `WhiteReport`) |
| `models.py` | Public alias of `model/`; `white_line.models` and `white_line.model` export the same names |
| `registry.py` | The versioned ledger: eleven records across epistemic, ethical, and contemplative absence, each with a reviewer prompt and a review horizon |
| `assessor.py` | `assess_absence`: staged assessment (intake, reconciliation, findings), plus the named constant reasons `SCORING_REASONS`, `REASON_NOT_RECORDED`, `REASON_WITHHELD`, `REASON_UNBOUNDED_WITHHOLDING`, `REASON_UNRESOLVED`, and `REASON_NAMED` that the manuscript quotes verbatim |
| `analysis.py` | Pure, additive views over a report: `decay_timeline`, `decay_transition_offsets`, `reconciliation_matrix`, `events_tally`, `coverage_matrix`, and `expiry_horizon` (returning `ExpiryEntry`); not a second assessor and not a score |
| `protocol.py` | Bounded human follow-up directives; never an approval, compliance, or safety verdict |
| `facets.py` | Factors a finding's caution-ordered state into typed facets — `EpistemicSettlement`, `DisclosureStance`, `TemporalStatus`, carried by `WitnessFacets` via `finding_facets`/`report_facets` — with `project_facets` recovering the shipped state; a factorization of recorded data, never new observations |
| `returns.py` | `return_contracts` (returning `ReturnContract`): the review horizon read forward as an obligation — trigger, due date, expected return, and observable acceptance condition per finding, each pointing back at the producing report; fulfilling a contract earns a re-review, never a pass |
| `envelope.py` | The cross-instrument report envelope (`line.report-envelope/1.0`): `report_envelope` (returning `ReportEnvelope`), `canonical_envelope`, `envelope_matches_report`, and the transportable non-claims `SCOPE_AND_NONCLAIMS`; points at the complete canonical report by digest and never reinterprets it |
| `dates.py` | `coerce_date`, `coerce_review_date`, and `usable_observation_date`: the single implementation of date resolution, so no view can age an observation the assessor refused to age |
| `serialization.py` | Canonical JSON form, order-independent SHA-256 digest, the review manifest, and the complete-report serialization `canonical_report`/`report_digest` (`REPORT_SCHEMA`) that envelopes point at |
| `invariants.py` | Structural soundness battery over the registry, plus `defect_registries` and `invariant_defect_battery`, which run every check over a registry carrying exactly the defect it guards against and return one `DefectProbe` per check |
| `worked_examples.py` | `WORKED_AS_OF`/`worked_intake_observations`/`worked_report`, `EXPIRY_AS_OF`/`expiry_observations`/`expiry_report`, `intake_reachability_battery`, and `scoring_branch_observations`/`scoring_branch_battery` (returning `ScoringProbe`): the shared deterministic input sets behind the documentation recipes and the figures. Each is an input set, never a stored result |
| `audit.py` | `audit_project`, `digest_inputs`, `figure_link_errors`, `manifest_blocking_errors`, and `write_source_manifest`: the source, figure, and rendered-bundle consistency gate; it checks structural agreement, not the truth of any observation |
| `figures/` | Deterministic schematics built from the versioned registry: `build_figures`, `FIGURE_PLATES`, and `FigurePlate`. `canvas.py` holds the legibility floor and canvas-width cap, `metrics.py` reads rendered plates back, and `legibility.py` converts a canvas size into a printed point size; the figures are schematics of the ledger, not evidence |
| `formalism.py` | Reads the manuscript's fenced formalism blocks the way the renderer's filter does: `parse_blocks` returns a `FormalismBlock` per block with the number that will be printed, `declared_prefixes` and `split_citations` separate formalism references from bibliography keys, `hand_written_numbers` and `strip_code` find numbers written into prose, and `read_manuscript` loads the sources. `FORMALISM_TITLES` and `FORMALISM_PREFIXES` pin the kind-to-title and kind-to-prefix tables |
| `version.py` | `__version__` (package), `LEDGER_VERSION` (registry content), and `LEDGER_VERSION_DIGEST`, the pinned registry digest that makes the bump instruction an audit failure rather than a convention |

The package root re-exports the entire public surface, so every callable above
is importable directly from `white_line`.

## Staged assessment

`assess_absence(observations, records=WHITE_RECORDS, as_of=None)` runs in
three stages:

1. **Intake.** Anything that fails the input contract is set aside with a typed
   `IntakeEvent` and a string-compatible note in `WhiteReport.intake_notes`:
   non-observation inputs, non-iterable input, unknown or non-string record ids,
   untyped states, and observations that try to assert `NOT_RECORDED` (a state
   reserved for the ledger itself). An otherwise valid observation with a
   non-string, non-empty ``observed_on`` is retained but emits
   ``UNDATED_OBJECT``: its date object is not coerced, so it cannot enter
   staleness accounting. Discarding and loss of dating never happen silently.
2. **Reconciliation.** When multiple observations name the same record with
   different states, the more cautious state wins (`WITHHELD` over
   `UNRESOLVED` over `NAMED`) and the conflict is noted. Same-state duplicates
   keep the last-listed observation — the rule is positional, not
   chronological — and are also recorded as events. Both reconciliation
   events carry the displaced observation's state as typed data
   (`IntakeEvent.displaced_state`), so a conflict stays readable as two
   co-present surfaces rather than only as a note that a conflict occurred;
   the cautious resolution still stands. No input can
   make an absence look more settled than its most cautious observer reported.
3. **Findings.** Every registry record gets an `AbsenceFinding` with a full
   reasons trail. Dated `NAMED` observations older than the record's
   `review_horizon_days` (relative to `as_of`, default today) decay to
   `UNRESOLVED` until re-reviewed — the old naming is no longer current evidence
   for a settled state.
   A `WITHHELD` observation without a stated boundary keeps its state but is
   flagged: restraint should name its duty. Unreadable or future observation
   dates are ignored with an explicit reason. A retained ``UNDATED_OBJECT``
   likewise names in its reasons that its non-ISO date cannot age; this keeps
   the existing fail-open decay behavior visible without changing acceptance.

The positional default-registry call form `assess_absence(observations)` keeps
its behavior for well-formed, undated input; everything above is additive.
Derived views stay downstream of assessment: given a report,
`expiry_horizon(report)` lists the current dated `NAMED` findings ordered by
how near they are to their review boundary, returning `ExpiryEntry` values.

## The witness layer: facets, returns, and the envelope

The binding and compatibility contract is in
[witness_contracts.md](witness_contracts.md). `binding.py` supplies shared
registry/report validation. `return_matches_contract` checks an exact prior
report/record pair. `validate_envelope_contract` and `envelope_digest` are
separate from the narrow `envelope_matches_report` check.

Three downstream modules make the assessment contract transportable without
changing it.

`facets.py` treats the caution order as what it is — a safe projection — and
factors each finding into the three questions the single state compresses:
epistemic settlement (`NOT_RECORDED`/`NAMED`/`UNRESOLVED`, or `UNDISCLOSED`
behind a stated withholding), disclosure stance (`OPEN`/`WITHHELD`), and
temporal status (`CURRENT`/`STALE`/`UNDATED`, resolved through the same
single date rule the assessor scored with). `project_facets` states the
projection, and the test suite proves branch-by-branch that projecting the
derived facets of any live finding recovers the finding's state — including
decay, which the factorization recovers as `NAMED` + `STALE` projecting to
`UNRESOLVED`, so a decayed naming keeps its prior naming and its age rather
than being rewritten as asserted doubt. The derivation reads only recorded
data and rejects malformed typed assertion/state/date combinations. It does
not authenticate display reasons or establish a finding's author.

`returns.py` reads the review horizon forward as an obligation rather than a
clock: one `ReturnContract` per finding with a trigger, a due date (the last
review date on which a current dated naming is still current, proven against
the assessor at the boundary), the artifact class that would count as a
return, and an observable acceptance condition. A `WITHHELD` contract's
return is boundary confirmation, never disclosure; an `UNRESOLVED` return may
honestly leave the question open. Every contract points back at the review
date, registry digest, and exact canonical report reference that set it.

`envelope.py` exports the cross-instrument report envelope
(`line.report-envelope/1.0`): the review date, the ledger and registry
versions, the complete ordered per-record states as this line's
`native_status`, a SHA-256 pointer (`report_ref`) to the full
`canonical_report` output, caller-supplied source snapshot references, and
the transportable non-claims. The envelope points at the native report and
never reinterprets it; sibling instruments export the same shape by
publishing the same schema string, never by importing one another, and
envelopes from different lines must not be compared, ranked, averaged, or
merged. `envelope_matches_report` is the read-back check for an archived
pair.

## Invariants and defined-defect detection tests

`invariants.py` provides six structural checks, each returning a frozen
`LedgerCheck(name, passed, detail)`:

- `ids_are_distinct` — no duplicate record ids
- `ids_are_canonical_slugs` — ids are lowercase hyphenated slugs
- `fields_are_inhabited` — id, title, description, and prompt are non-blank strings
- `kinds_are_valid_and_covered` — every kind is a real `AbsenceKind` and every kind appears at least once
- `horizons_are_positive` — review horizons are positive integers
- `serialization_is_stable` — the canonical form builds, parses, and digests independently of record order

`all_ledger_checks()` runs the battery; `ledger_sound()` collapses it to a
boolean. The assessor applies the same battery to custom registries and fails
closed with a `ValueError` if one is malformed.

Detection is shipped, not only tested. `defect_registries()` builds one
registry per check carrying exactly the defect that check guards against, and
`invariant_defect_battery()` runs the whole battery over each of them, refusing
to return unless the targeted check rejected its own registry and the live
registry passed everything. It returns a `DefectProbe` per check with the
detail string the check actually produced, which is what the manuscript's
defect-detection proposition and the invariant-battery figure display. This
demonstrates rejection of the planted defects; it is not a proof that every
conceivable structural fault is absent.

## Digest and manifest

`registry_digest` hashes the id-sorted canonical JSON, so the digest is
independent of record order and changes when any record's content changes.
`registry_manifest` bundles the package and ledger schema versions,
`LEDGER_VERSION`, record counts by kind, and the digest for change review. Each
`WhiteReport` also carries the review date and digest of the registry used to
produce it. Store those values with a review record, re-run
`scripts/check_registry.py` later, and silent registry edits surface as a
digest mismatch. This is a review and drift-detection instrument for the
ledger's own content; it has no security or safety semantics.
