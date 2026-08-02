"""Descriptive analyses over the assessment contract: sweeps and tables.

Every helper here is a pure, additive summary computed *through* the public
``assess_absence`` API or directly from the defined caution order. Nothing in
this module changes what the ledger records or how a state is assigned; it
only makes the existing contract inspectable — how dated namings migrate to
``UNRESOLVED`` across review dates, which current namings near a review
horizon, how any ordered pair of asserted states reconciles, and how findings
distribute across kinds and states.

None of these summaries is a completeness score, a safety score, or evidence
of a hidden cause. A decay curve or refresh schedule describes the staleness
contract applied to supplied observations; it says nothing about the world the
records point at.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta

from .assessor import assess_absence
from .dates import coerce_date, usable_observation_date
from .model import (
    AbsenceKind,
    AbsenceObservation,
    AbsenceRecord,
    AbsenceState,
    IntakeCode,
    WhiteReport,
    caution_rank,
)
from .registry import WHITE_RECORDS

#: States an observation may assert. ``NOT_RECORDED`` is ledger-reserved
#: (screened out at intake), so it can never appear in a reconciliation.
ASSERTABLE_STATES: tuple[AbsenceState, ...] = tuple(
    state for state in AbsenceState if state is not AbsenceState.NOT_RECORDED
)


@dataclass(frozen=True)
class DecayPoint:
    """One review date in a decay sweep, with the full state tally.

    ``offset_days`` counts days from the sweep's start date; ``tally`` maps
    every member of the state alphabet to a count, including zeros, exactly
    as ``WhiteReport.tally`` does for a single report.
    """

    review_date: str
    offset_days: int
    tally: dict[AbsenceState, int]


def decay_timeline(
    observations: Iterable[AbsenceObservation] | None,
    start: str | date,
    end: str | date,
    records: Iterable[AbsenceRecord] = WHITE_RECORDS,
    step_days: int = 1,
) -> tuple[DecayPoint, ...]:
    """Sweep review dates from ``start`` to ``end`` and tally each ledger.

    The same observations are assessed at every review date in the inclusive
    range, ``step_days`` apart, via the public ``assess_absence`` API. The
    sweep makes the staleness contract visible: as the review date moves past
    a record's horizon, its dated ``NAMED`` observation is reported
    ``UNRESOLVED``. The sweep changes nothing about assessment semantics.

    Args:
        observations: The observation set to hold fixed across the sweep.
        start: First review date (ISO string or ``date``).
        end: Last review date, inclusive; must not precede ``start``.
        records: The registry to assess against (defaults to the live one).
        step_days: Positive gap in days between consecutive review dates.

    Returns:
        One ``DecayPoint`` per review date, in ascending date order.

    Raises:
        ValueError: If ``end`` precedes ``start`` or ``step_days`` < 1, or if
            a date string is not ISO formatted.
        TypeError: If a date argument is neither a string nor a ``date``.
    """

    start_date = coerce_date(start, "start")
    end_date = coerce_date(end, "end")
    if end_date < start_date:
        raise ValueError("end must not precede start")
    if not isinstance(step_days, int) or isinstance(step_days, bool) or step_days < 1:
        raise ValueError("step_days must be a positive integer")
    observation_tuple = tuple(observations) if observations is not None else None
    record_tuple = tuple(records)
    points: list[DecayPoint] = []
    current = start_date
    while current <= end_date:
        report = assess_absence(observation_tuple, record_tuple, as_of=current)
        points.append(
            DecayPoint(current.isoformat(), (current - start_date).days, report.tally())
        )
        current += timedelta(days=step_days)
    return tuple(points)


def decay_transition_offsets(points: Iterable[DecayPoint]) -> tuple[int, ...]:
    """Return the day offsets at which any state tally changes.

    A returned offset is the first day whose tally differs from the previous
    point's tally. For an all-``NAMED`` dated cohort these are the horizon
    crossings; the helper itself just reports where the swept ledger moved.
    """

    offsets: list[int] = []
    previous: dict[AbsenceState, int] | None = None
    for point in points:
        if previous is not None and point.tally != previous:
            offsets.append(point.offset_days)
        previous = point.tally
    return tuple(offsets)


def reconciliation_matrix() -> dict[tuple[AbsenceState, AbsenceState], AbsenceState]:
    """Return the full ordered-pair conflict-resolution table.

    For every ordered pair ``(held, incoming)`` of assertable states, the
    value is the state the intake stage keeps: the maximum of the pair under
    ``caution_rank``. The table is symmetric — resolution does not depend on
    which observation arrived first — and its diagonal is the identity.
    ``NOT_RECORDED`` appears nowhere because observations may not assert it.
    """

    return {
        (held, incoming): max(held, incoming, key=caution_rank)
        for held in ASSERTABLE_STATES
        for incoming in ASSERTABLE_STATES
    }


def events_tally(report: WhiteReport) -> dict[IntakeCode, int]:
    """Count intake events per code; every code appears, even at zero.

    This mirrors ``WhiteReport.tally`` for the intake side of the ledger:
    a distributional view of *why* inputs were set aside or reconciled.
    An event count is audit data about input handling, never a verdict on
    whoever supplied the input.
    """

    counts = {code: 0 for code in IntakeCode}
    for event in report.intake_events:
        counts[event.code] += 1
    return counts


def coverage_matrix(report: WhiteReport) -> dict[AbsenceKind, dict[AbsenceState, int]]:
    """Cross-tabulate findings by kind and state; every cell is present.

    The matrix answers "which kinds currently carry which states" for one
    report. Row and column sums agree with ``records_by_kind`` sizes and
    ``report.tally`` respectively. It is a distributional summary of the
    ledger, not a completeness or coverage *score* of any work.
    """

    matrix = {kind: {state: 0 for state in AbsenceState} for kind in AbsenceKind}
    for finding in report.findings:
        matrix[finding.kind][finding.state] += 1
    return matrix


@dataclass(frozen=True)
class ExpiryEntry:
    """One current dated naming, positioned against its review horizon."""

    record_id: str
    kind: AbsenceKind
    observed_on: str
    horizon_days: int
    age_days: int
    days_remaining: int


def expiry_horizon(
    report: WhiteReport,
    records: Iterable[AbsenceRecord] = WHITE_RECORDS,
) -> tuple[ExpiryEntry, ...]:
    """List current dated ``NAMED`` findings nearest their review boundary.

    A naming whose ``observed_on`` the assessor could not use for staleness
    accounting cannot expire and is omitted: that covers undated namings, a
    retained non-ISO date object, an unreadable string, and a date after the
    review date, which the manuscript's date-resolution rule discards outright. A naming that has
    already decayed is ``UNRESOLVED`` and is omitted as well. The date rule is
    read from ``white_line.dates.usable_observation_date`` — the same helper
    the scoring stage applies — so this view cannot age an observation the
    assessor refused to age.

    This is a refresh schedule for supplied observations, not a completeness
    score, safety score, or evidence about the world.
    """

    review_date = coerce_date(report.review_date, "report.review_date")
    records_by_id = {record.id: record for record in records}
    entries: list[ExpiryEntry] = []
    for finding in report.findings:
        if finding.state is not AbsenceState.NAMED:
            continue
        observed, _issue = usable_observation_date(finding.observed_on, review_date)
        if observed is None:
            continue
        record = records_by_id.get(finding.record_id)
        if record is None:
            raise ValueError(
                f"NAMED finding references unknown record id {finding.record_id!r}"
            )
        age_days = (review_date - observed).days
        entries.append(
            ExpiryEntry(
                finding.record_id,
                record.kind,
                finding.observed_on,
                record.review_horizon_days,
                age_days,
                record.review_horizon_days - age_days,
            )
        )
    return tuple(
        sorted(entries, key=lambda entry: (entry.days_remaining, entry.record_id))
    )


__all__ = [
    "ASSERTABLE_STATES",
    "DecayPoint",
    "ExpiryEntry",
    "coverage_matrix",
    "decay_timeline",
    "decay_transition_offsets",
    "events_tally",
    "expiry_horizon",
    "reconciliation_matrix",
]
