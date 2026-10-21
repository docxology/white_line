"""Decay sweeps, the reconciliation matrix, and distributional summaries.

Everything here runs the real public API over the live registry (or small
real registries built inline); nothing is mocked and no observation data is
fabricated as if it were observed — cohorts are explicit test inputs.
"""

from datetime import date, datetime, timedelta

import pytest

from white_line import (
    ASSERTABLE_STATES,
    WHITE_RECORDS,
    AbsenceKind,
    AbsenceObservation,
    AbsenceRecord,
    AbsenceState,
    AbsenceFinding,
    IntakeCode,
    SET_ASIDE_CODES,
    WhiteReport,
    assess_absence,
    caution_rank,
    coverage_matrix,
    decay_timeline,
    decay_transition_offsets,
    events_tally,
    expiry_horizon,
    reconciliation_matrix,
    records_by_kind,
)

ANCHOR = "2026-01-01"


def _all_named_cohort() -> tuple[AbsenceObservation, ...]:
    return tuple(
        AbsenceObservation(
            record.id, AbsenceState.NAMED, "dated naming for the sweep", ANCHOR
        )
        for record in WHITE_RECORDS
    )


# --------------------------------------------------------------------------- #
# decay_timeline
# --------------------------------------------------------------------------- #
def test_decay_timeline_covers_the_inclusive_range_in_order() -> None:
    points = decay_timeline(_all_named_cohort(), ANCHOR, "2026-01-11")
    assert len(points) == 11
    assert points[0].review_date == "2026-01-01"
    assert points[-1].review_date == "2026-01-11"
    assert [point.offset_days for point in points] == list(range(11))


def test_decay_timeline_migrates_named_records_at_each_horizon_crossing() -> None:
    points = decay_timeline(_all_named_cohort(), ANCHOR, "2027-02-05")
    assert points[0].tally[AbsenceState.NAMED] == len(WHITE_RECORDS)
    assert points[0].tally[AbsenceState.UNRESOLVED] == 0
    assert points[-1].tally[AbsenceState.NAMED] == 0
    assert points[-1].tally[AbsenceState.UNRESOLVED] == len(WHITE_RECORDS)
    # A naming decays the first day it is strictly past its horizon.
    expected = tuple(
        sorted({record.review_horizon_days + 1 for record in WHITE_RECORDS})
    )
    assert decay_transition_offsets(points) == expected


def test_decay_timeline_named_counts_are_monotone_and_totals_conserved() -> None:
    points = decay_timeline(_all_named_cohort(), ANCHOR, "2027-02-05", step_days=5)
    named = [point.tally[AbsenceState.NAMED] for point in points]
    unresolved = [point.tally[AbsenceState.UNRESOLVED] for point in points]
    assert all(later <= earlier for earlier, later in zip(named, named[1:]))
    assert all(later >= earlier for earlier, later in zip(unresolved, unresolved[1:]))
    for point in points:
        assert sum(point.tally.values()) == len(WHITE_RECORDS)
        assert set(point.tally) == set(AbsenceState)


def test_decay_timeline_with_no_observations_stays_not_recorded() -> None:
    points = decay_timeline(None, ANCHOR, "2026-01-05")
    for point in points:
        assert point.tally[AbsenceState.NOT_RECORDED] == len(WHITE_RECORDS)


def test_decay_timeline_accepts_date_objects_and_custom_registries() -> None:
    registry = (
        AbsenceRecord(
            "short-gap",
            "Short gap",
            AbsenceKind.EPISTEMIC,
            "One bounded gap.",
            "Seen it?",
            3,
        ),
        AbsenceRecord(
            "held-bound",
            "Held boundary",
            AbsenceKind.ETHICAL,
            "One held boundary.",
            "Whose duty?",
            30,
        ),
        AbsenceRecord(
            "open-field",
            "Open field",
            AbsenceKind.CONTEMPLATIVE,
            "Left open.",
            "Still open?",
            30,
        ),
    )
    observations = (AbsenceObservation("short-gap", AbsenceState.NAMED, "", ANCHOR),)
    points = decay_timeline(
        observations, date(2026, 1, 1), date(2026, 1, 6), records=registry
    )
    states = [point.tally[AbsenceState.NAMED] for point in points]
    assert states == [1, 1, 1, 1, 0, 0]
    assert decay_transition_offsets(points) == (4,)


def test_decay_timeline_fails_closed_on_bad_arguments() -> None:
    cohort = _all_named_cohort()
    with pytest.raises(ValueError):
        decay_timeline(cohort, "2026-02-01", "2026-01-01")
    with pytest.raises(ValueError):
        decay_timeline(cohort, ANCHOR, "2026-01-05", step_days=0)
    with pytest.raises(ValueError):
        decay_timeline(cohort, ANCHOR, "2026-01-05", step_days=True)
    with pytest.raises(ValueError):
        decay_timeline(cohort, "not-a-date", "2026-01-05")
    with pytest.raises(TypeError):
        decay_timeline(cohort, ANCHOR, 20260105)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="start must be a date, not a datetime"):
        decay_timeline(cohort, datetime(2026, 1, 1), "2026-01-05")


def test_decay_transition_offsets_is_empty_for_a_flat_sweep() -> None:
    points = decay_timeline(None, ANCHOR, "2026-01-08", step_days=2)
    assert decay_transition_offsets(points) == ()


# --------------------------------------------------------------------------- #
# reconciliation_matrix
# --------------------------------------------------------------------------- #
def test_reconciliation_matrix_is_the_exhaustive_max_caution_table() -> None:
    matrix = reconciliation_matrix()
    assert len(matrix) == len(ASSERTABLE_STATES) ** 2
    for held in ASSERTABLE_STATES:
        for incoming in ASSERTABLE_STATES:
            kept = matrix[(held, incoming)]
            assert caution_rank(kept) == max(caution_rank(held), caution_rank(incoming))
            assert kept in (held, incoming)


def test_reconciliation_matrix_is_symmetric_with_identity_diagonal() -> None:
    matrix = reconciliation_matrix()
    for held in ASSERTABLE_STATES:
        assert matrix[(held, held)] is held
        for incoming in ASSERTABLE_STATES:
            assert matrix[(held, incoming)] is matrix[(incoming, held)]


def test_reconciliation_matrix_never_mentions_the_reserved_state() -> None:
    matrix = reconciliation_matrix()
    assert AbsenceState.NOT_RECORDED not in ASSERTABLE_STATES
    for (held, incoming), kept in matrix.items():
        assert AbsenceState.NOT_RECORDED not in (held, incoming, kept)


def test_reconciliation_matrix_agrees_with_the_assessor_in_both_orders() -> None:
    """All nine ordered pairs — conflicts and the same-state diagonal — match the assessor.

    Diagonal cells exercise the duplicate path (same state kept, `DUPLICATE_STATE`
    event); off-diagonal cells exercise the conflict path. Every cell is checked
    against a real two-observer `assess_absence` call in both arrival orders.
    """

    matrix = reconciliation_matrix()
    record_id = WHITE_RECORDS[0].id
    for held in ASSERTABLE_STATES:
        for incoming in ASSERTABLE_STATES:
            observations = (
                AbsenceObservation(record_id, held, "first observer"),
                AbsenceObservation(record_id, incoming, "second observer"),
            )
            report = assess_absence(observations, as_of=ANCHOR)
            finding = report.finding_for(record_id)
            assert finding is not None
            assert finding.state is matrix[(held, incoming)]
            reversed_report = assess_absence(
                tuple(reversed(observations)), as_of=ANCHOR
            )
            reversed_finding = reversed_report.finding_for(record_id)
            assert reversed_finding is not None
            assert reversed_finding.state is finding.state


# --------------------------------------------------------------------------- #
# events_tally
# --------------------------------------------------------------------------- #
def test_events_tally_lists_every_code_even_at_zero() -> None:
    report = assess_absence((), as_of=ANCHOR)
    tally = events_tally(report)
    assert set(tally) == set(IntakeCode)
    assert all(count == 0 for count in tally.values())
    assert tally[IntakeCode.UNDATED_OBJECT] == 0


def test_events_tally_counts_real_intake_events_per_code() -> None:
    record_id = WHITE_RECORDS[0].id
    observations = (
        AbsenceObservation(record_id, AbsenceState.NAMED, "first"),
        AbsenceObservation(record_id, AbsenceState.WITHHELD, "conflicting"),
        AbsenceObservation(record_id, AbsenceState.WITHHELD, "duplicate"),
        AbsenceObservation("no-such-record", AbsenceState.NAMED, "unknown id"),
        AbsenceObservation(WHITE_RECORDS[1].id, AbsenceState.NOT_RECORDED, "reserved"),
        "not an observation",  # type: ignore[arg-type]
    )
    report = assess_absence(observations, as_of=ANCHOR)
    tally = events_tally(report)
    assert tally[IntakeCode.CONFLICTING_STATES] == 1
    assert tally[IntakeCode.DUPLICATE_STATE] == 1
    assert tally[IntakeCode.UNKNOWN_RECORD] == 1
    assert tally[IntakeCode.RESERVED_STATE] == 1
    assert tally[IntakeCode.NON_OBSERVATION] == 1
    assert tally[IntakeCode.NON_ITERABLE_INPUT] == 0
    assert tally[IntakeCode.UNTYPED_STATE] == 0
    assert tally[IntakeCode.UNDATED_OBJECT] == 0
    # The tally counts every intake event, which is what intake_event_count
    # reports. set_aside_count is narrower on purpose: it counts only the
    # codes the intake stage calls a set-aside, so the two reconciliation events
    # above are excluded from it.
    assert sum(tally.values()) == report.intake_event_count
    assert report.set_aside_count == sum(
        tally[code] for code in SET_ASIDE_CODES
    )
    assert report.set_aside_count == 3
    assert report.intake_event_count == 5


# --------------------------------------------------------------------------- #
# coverage_matrix
# --------------------------------------------------------------------------- #
def test_coverage_matrix_has_every_kind_by_state_cell() -> None:
    report = assess_absence(None, as_of=ANCHOR)
    matrix = coverage_matrix(report)
    assert set(matrix) == set(AbsenceKind)
    for row in matrix.values():
        assert set(row) == set(AbsenceState)


def test_coverage_matrix_row_and_column_sums_match_the_registry_and_tally() -> None:
    record_ids_by_kind = {
        kind: [record.id for record in records]
        for kind, records in records_by_kind().items()
    }
    observations = (
        AbsenceObservation(
            record_ids_by_kind[AbsenceKind.EPISTEMIC][0], AbsenceState.NAMED, "", ANCHOR
        ),
        AbsenceObservation(
            record_ids_by_kind[AbsenceKind.ETHICAL][0],
            AbsenceState.WITHHELD,
            "duty of care named",
        ),
        AbsenceObservation(
            record_ids_by_kind[AbsenceKind.CONTEMPLATIVE][0],
            AbsenceState.UNRESOLVED,
            "still open",
        ),
    )
    report = assess_absence(observations, as_of=ANCHOR)
    matrix = coverage_matrix(report)
    tally = report.tally()
    for kind, records in records_by_kind().items():
        assert sum(matrix[kind].values()) == len(records)
    for state in AbsenceState:
        assert sum(matrix[kind][state] for kind in AbsenceKind) == tally[state]
    assert matrix[AbsenceKind.EPISTEMIC][AbsenceState.NAMED] == 1
    assert matrix[AbsenceKind.ETHICAL][AbsenceState.WITHHELD] == 1
    assert matrix[AbsenceKind.CONTEMPLATIVE][AbsenceState.UNRESOLVED] == 1


# --------------------------------------------------------------------------- #
# expiry_horizon
# --------------------------------------------------------------------------- #
def test_expiry_horizon_lists_current_dated_namings_in_refresh_order() -> None:
    report = assess_absence(
        (
            AbsenceObservation(
                "unobserved-dependency", AbsenceState.NAMED, "fresh", "2026-06-01"
            ),
            AbsenceObservation(
                "unmeasured-uncertainty",
                AbsenceState.NAMED,
                "at boundary",
                "2026-03-20",
            ),
            AbsenceObservation("negative-space", AbsenceState.NAMED, "undated"),
            AbsenceObservation(
                "unasked-question", AbsenceState.NAMED, "stale", "2026-01-01"
            ),
        ),
        as_of="2026-07-18",
    )
    entries = expiry_horizon(report)
    assert [entry.record_id for entry in entries] == [
        "unmeasured-uncertainty",
        "unobserved-dependency",
    ]
    assert all(entry.days_remaining >= 0 for entry in entries)
    assert all(entry.observed_on for entry in entries)
    assert all(entry.record_id != "unasked-question" for entry in entries)


def test_expiry_horizon_tie_breaks_by_record_id() -> None:
    report = assess_absence(
        (
            AbsenceObservation(
                "unobserved-dependency", AbsenceState.NAMED, "first", "2026-06-01"
            ),
            AbsenceObservation(
                "unasked-question", AbsenceState.NAMED, "second", "2026-06-01"
            ),
        ),
        as_of="2026-07-18",
    )
    entries = expiry_horizon(report)
    assert [entry.record_id for entry in entries] == [
        "unasked-question",
        "unobserved-dependency",
    ]


def test_expiry_horizon_omits_an_accepted_non_iso_date_object() -> None:
    report = assess_absence(
        (
            AbsenceObservation(
                "unobserved-dependency", AbsenceState.NAMED, "kept", date(2020, 1, 1)
            ),
        ),
        as_of="2026-07-18",
    )
    finding = report.finding_for("unobserved-dependency")
    assert finding is not None
    assert finding.state is AbsenceState.NAMED
    assert finding.observed_on == ""
    assert expiry_horizon(report) == ()


def test_expiry_horizon_fails_closed_for_an_empty_review_date() -> None:
    with pytest.raises(ValueError, match="review_date"):
        expiry_horizon(WhiteReport(()))


def test_expiry_horizon_fails_closed_for_an_unknown_named_record() -> None:
    report = WhiteReport(
        (
            AbsenceFinding(
                "missing-record",
                AbsenceKind.EPISTEMIC,
                AbsenceState.NAMED,
                (),
                "2026-07-01",
            ),
        ),
        review_date="2026-07-18",
    )
    with pytest.raises(ValueError, match="unbound report"):
        expiry_horizon(report)


def test_expiry_horizon_omits_a_naming_the_assessor_could_not_date() -> None:
    """An unreadable or future stored date is omitted, not aged or raised.

    ``expiry_horizon`` resolves dates through the same helper the scoring
    stage uses, so a date the assessor discarded cannot reappear here as an
    age. Before this binding the unreadable case raised out of the middle of
    the helper and the future case produced a negative age with more days
    remaining than the record's whole horizon.
    """

    for stored in ("not-a-date", "2027-01-01"):
        report = assess_absence((AbsenceObservation(
            "unobserved-dependency", AbsenceState.NAMED, "scope", stored
        ),), as_of="2026-07-18")
        assert expiry_horizon(report) == ()


def test_expiry_horizon_omits_a_future_naming_the_assessor_ignored() -> None:
    """The end-to-end future-date case, through the public assessor."""

    report = assess_absence(
        (
            AbsenceObservation(
                "unobserved-dependency", AbsenceState.NAMED, "dated ahead", "2027-01-01"
            ),
        ),
        as_of="2026-07-18",
    )
    finding = report.finding_for("unobserved-dependency")
    assert finding is not None
    assert any("after the review date" in reason for reason in finding.reasons)
    assert expiry_horizon(report) == ()


def test_expiry_horizon_days_remaining_tracks_the_assessor_across_a_sweep() -> None:
    """Differential binding: the queue holds a naming exactly while it is NAMED.

    For every age from well inside the horizon to well past it, the helper
    returns a non-negative ``days_remaining`` entry precisely when
    ``assess_absence`` still reports ``NAMED``. Duplicated staleness
    arithmetic that disagreed with the assessor by even one day would fail
    at the boundary.
    """

    record = next(item for item in WHITE_RECORDS if item.id == "unobserved-dependency")
    review = date(2026, 7, 18)
    for age in range(0, record.review_horizon_days + 4):
        observed = review - timedelta(days=age)
        report = assess_absence(
            (
                AbsenceObservation(
                    record.id, AbsenceState.NAMED, "swept", observed.isoformat()
                ),
            ),
            as_of=review,
        )
        finding = report.finding_for(record.id)
        assert finding is not None
        entries = expiry_horizon(report)
        queued = [entry for entry in entries if entry.record_id == record.id]
        assert bool(queued) is (finding.state is AbsenceState.NAMED)
        if queued:
            assert queued[0].age_days == age
            assert queued[0].days_remaining == record.review_horizon_days - age
            assert queued[0].days_remaining >= 0
