---
name: white-line
description: Operate the White Line typed absence ledger — assess_absence with states NAMED/UNRESOLVED/WITHHELD/NOT_RECORDED, staged intake, decay to UNRESOLVED past review horizons, review_directives follow-up, decay/conflict/coverage analyses, registry digest, and the audit_project.py gate. USE WHEN working in projects/working/white_line, calling assess_absence, reading a WhiteReport, sweeping decay horizons, tabulating intake events, checking the registry digest, or auditing the publication bundle.
---

# White Line local skill

White Line is a typed ledger for the edge of a claim. Its executable core is
`assess_absence(observations, records=WHITE_RECORDS, as_of=None)`, which maps
dated reviewer observations onto a versioned eleven-record registry and returns
a `WhiteReport`. Use it to keep what is unknown, withheld, or deliberately open
legible — never to infer *why* something is absent. It is not a safety score,
an accreditation, a moral authority, or a permission mechanism.

## Quick start (from the project root)

```bash
uv run pytest -q                                                  # test suite
uv run python scripts/check_registry.py                           # soundness + digest manifest
uv run python scripts/build_figures.py                            # deterministic figures (writes output/figures/)
uv run python scripts/audit_project.py --report                   # source/render consistency gate
uv run python scripts/audit_project.py --write-manifest --report  # only after a fresh render
```

The equivalent `.venv/bin/python` forms also work against the editable
install. The scripts carry no `sys.path` bootstrap, so they need an
interpreter that already has the package installed.

Figure generation requires the system `rsvg-convert` executable from librsvg.
Render the publication bundle with the external `docxology/template` engine —
cloned or located anywhere on disk, with this checkout linked in as its
`projects/working/white_line` — using
`uv run python scripts/pipeline/stage_03_render.py --project working/white_line`,
then return here for `audit_project.py --write-manifest --report`. That render
is the only step this repository cannot perform alone; see `STANDALONE.md`.

## States

Each finding carries exactly one state:

- `NAMED` — the absence is made explicit by a current observation.
- `UNRESOLVED` — the absence is known but not settled (or a naming went stale).
- `WITHHELD` — material is intentionally not disclosed; honor the boundary.
- `NOT_RECORDED` — no observation was supplied. Reserved for the ledger
  itself: an input asserting it is set aside at intake.

## Core API — worked example (real output)

```python
from white_line import (assess_absence, review_directives, events_tally,
                        AbsenceObservation, AbsenceState)

obs = [
    AbsenceObservation(record_id="unobserved-dependency", state=AbsenceState.NAMED,
                       note="vendor telemetry never sampled", observed_on="2026-07-01"),
    AbsenceObservation(record_id="withheld-material", state=AbsenceState.WITHHELD,
                       note="counsel hold", observed_on="2026-07-10"),
    AbsenceObservation(record_id="unobserved-dependency", state=AbsenceState.UNRESOLVED,
                       note="second reviewer disagrees", observed_on="2026-07-12"),
]
report = assess_absence(obs, as_of="2026-07-22")
# 11 findings: unobserved-dependency -> UNRESOLVED (conflict, caution wins),
# withheld-material -> WITHHELD, the other 9 records -> NOT_RECORDED.
# report.intake_events: [(CONFLICTING_STATES, 'unobserved-dependency')]
# report.review_date == '2026-07-22'; report.registry_digest is the ledger digest.
directives = review_directives(report)
# withheld-material -> action HONOR_AND_CONFIRM_BOUNDARY, requires_follow_up True
```

`observed_on` and `as_of` are ISO `YYYY-MM-DD` strings (a `date` is also
accepted for `as_of`). Every finding carries human-readable `reasons`.

## Staged intake

Assessment runs intake → matching → scoring. Intake sets aside anything that
fails the input contract — non-observations, unknown record ids, untyped
states, asserted `NOT_RECORDED` — and records a typed `IntakeEvent`
(`intake_events`) plus a note (`intake_notes`) for every set-aside, conflict,
and duplicate. An accepted observation whose `observed_on` is not an ISO
string records `UNDATED_OBJECT`: the observation is kept, its dating is not.
Nothing is discarded silently. When observers disagree about one
record, the more cautious state wins (`caution_rank`: `WITHHELD` >
`UNRESOLVED` > `NAMED` > `NOT_RECORDED`); no input can make an absence look
more settled than its most cautious observer reported.

## Decay past the review horizon

A dated `NAMED` observation older than its record's `review_horizon_days`
(relative to `as_of`) is reported `UNRESOLVED` until re-reviewed: an old naming
is not current evidence for a settled state. Horizons are graded by kind —
epistemic and ethical records expire within 90–180 days, contemplative records
last a year (365 days). Always pass an explicit `as_of` for reproducible reviews, and keep
`review_date` and `registry_digest` with the review record.

## Distributional analyses (`white_line.analysis`)

Pure, additive summaries computed *through* `assess_absence` — never a second
implementation of assessment semantics:

- `decay_timeline(obs, start, end, step_days=1)` — re-assess the same
  observations across a sweep of review dates; returns `DecayPoint`s with full
  state tallies. A `NAMED` naming on a 90-day-horizon record dated
  `2026-07-01` flips to `UNRESOLVED` at offset day 91 (verified).
- `decay_transition_offsets(points)` — the day offsets where any tally moves.
- `reconciliation_matrix()` — the full ordered-pair conflict-resolution table
  over assertable states (the manuscript's caution-monotonicity proposition).
- `events_tally(report)` — count per `IntakeCode` (input-handling audit data).
- `coverage_matrix(report)` — kind-by-state cross-tab of findings.
- `expiry_horizon(report)` — current dated `NAMED` findings ordered by days
  remaining before their record's horizon. Undated namings and already-decayed
  ones are absent: the first cannot expire, the second already did.

These views back the decay-timeline and conflict-lattice figures and the
manuscript's distributional-views section. None is a completeness, diligence,
or negligence score.

## Review directives

`review_directives(report)` maps each finding to one bounded follow-up:
`RETAIN_NAMED_SCOPE`, `REOPEN_OR_BOUND`, `HONOR_AND_CONFIRM_BOUNDARY`, or
`RECORD_OR_EXPLICITLY_SCOPE`. `requires_follow_up` flags all states except
`NAMED`. No directive is an approval, compliance result, or safety verdict.

## Gates

`white_line.audit` owns the gate logic; `scripts/audit_project.py` is the thin
CLI over it. `audit_project` is a root export, so a caller can import it
directly from `white_line` instead of shelling out.

The gate checks registry soundness, figure registry/digest agreement,
manuscript figure links in both directions (a referenced-but-unregistered
figure and a registered-but-unembedded figure both fail), bibliography keys,
source headings in the rendered bundle, and the source manifest fingerprint.
Write the manifest only after a fresh render passes the audit. A passing audit
is structural agreement, not truth verification.

## Gotchas (probed against the real API)

- `observed_on` must be an ISO **string**. Passing a `datetime.date` object
  leaves the observation *undated*: it is still accepted and counted, but
  staleness decay never fires. The dropped dating is visible — intake emits an
  `UNDATED_OBJECT` event and the finding's `reasons` names it. The object is
  not coerced into a date, so this path stays fail-open for decay.
- `as_of=None` anchors staleness to *today* — non-reproducible. Always pass an
  explicit review date in anything scripted or published.
- A future-dated `observed_on` is ignored (noted in `reasons`), making the
  observation undated rather than rejected.
- Duplicate same-state observations for one record keep the last-listed and
  log a `DUPLICATE_STATE` event; conflicting states log `CONFLICTING_STATES`
  and keep the more cautious.
- Paper-version authority is `manuscript/config.yaml`; package and installed
  metadata are kept equal by the version tests. Registry content changes must
  bump `LEDGER_VERSION` **and** re-pin `LEDGER_VERSION_DIGEST` in
  `src/white_line/version.py`; the audit fails until they agree, so a reworded
  description can no longer slip through with counts and kinds unchanged.
  Re-pin with `uv run python -c "from white_line import WHITE_RECORDS,
  registry_digest; print(registry_digest(WHITE_RECORDS))"`.
- Every generated figure must be embedded by filename in a `manuscript/*.md`
  file; a generated-but-unembedded figure fails the audit and is forbidden.
  `figure_registry.json` records each PNG and SVG byte digest and the audit
  re-derives them, so a hand-edited raster fails too.
- No in-figure label may print below six points. `canvas.text` refuses a size
  under `MIN_TEXT_SIZE`, `open_canvas` refuses a width over
  `MAX_CANVAS_WIDTH`, and `tests/test_figure_legibility.py` re-derives the
  printed size from the embed width and page geometry. Grow a plate downward,
  never sideways, and re-render before trusting a green legibility run after
  editing `manuscript/config.yaml` or an embed width.

## The report envelope (cross-instrument transport)

```python
from white_line import report_envelope, canonical_envelope, envelope_matches_report

envelope = report_envelope(report, subject_id="your reference for what was reviewed")
canonical_envelope(envelope)              # store beside canonical_report(report)
envelope_matches_report(envelope, report) # read-back check for an archived pair
```

One `line.report-envelope/1.0` record pointing at the complete canonical
report (`report_digest`) without reinterpreting it. `native_status` is the
ordered per-record states; the ledger's non-claims travel inside the record.
The witness layer also ships `facets.py` (settlement x disclosure x
temporality, `project_facets` recovers the shipped state) and `returns.py`
(one `ReturnContract` per finding).

## Claim boundaries

States describe the ledger's record under a supplied review contract — never
people, populations, motives, safety, legality, or permission. `WITHHELD` is
not evidence of deception; `NOT_RECORDED` is not evidence that nobody knew;
`UNRESOLVED` is not proof a hidden cause exists; a filled tally row is not
diligence and an empty one is not negligence; a passing audit or matching
digest is not a truth or safety certificate. See `docs/claim_boundaries.md`
before adding any prose or API surface that could imply otherwise.
