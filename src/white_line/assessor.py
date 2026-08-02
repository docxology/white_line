"""Staged absence assessment: intake, reconciliation, then a typed ledger.

The assessment is deliberately staged. Intake sets aside anything it cannot
trust — non-observations, unknown record ids, untyped states, observations
that try to assert the ledger-reserved ``NOT_RECORDED`` — and records why in
``WhiteReport.intake_notes`` so nothing is discarded silently. Conflicting
observations for the same record resolve toward the more cautious state.
Dated ``NAMED`` observations decay back to ``UNRESOLVED`` once they age past
the record's review horizon: the old naming is no longer current evidence for
a settled state.

Throughout, the ledger records state; it never infers why something is
absent, and under the defined contract no input can make an absence look more
settled than its most cautious observer reported.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import cast

from .model import (
    AbsenceFinding,
    AbsenceObservation,
    AbsenceRecord,
    AbsenceState,
    IntakeCode,
    IntakeEvent,
    WhiteReport,
    caution_rank,
)
from .dates import coerce_review_date, usable_observation_date
from .invariants import all_ledger_checks
from .registry import WHITE_RECORDS
from .serialization import registry_digest


#: The constant reasons the scoring rule can emit, in the order its branches
#: are stated. They are named rather than inlined because the manuscript quotes
#: them verbatim: a test compares the quoted strings against these constants and
#: against the reasons a live assessment returned, so a reworded reason fails
#: the build instead of leaving the prose describing an evaluator that no longer
#: exists. The two remaining reasons — the age line and the decay line — carry
#: computed day counts and are formatted at the point of use.
REASON_NOT_RECORDED = "no absence note was recorded"
REASON_WITHHELD = "material is intentionally withheld"
REASON_UNBOUNDED_WITHHOLDING = (
    "no boundary is stated for the withholding; restraint should name its duty"
)
REASON_UNRESOLVED = "the absence is named but not resolved"
REASON_NAMED = "the absence is explicitly named"

#: Every constant reason, for callers that need the whole alphabet.
SCORING_REASONS: tuple[str, ...] = (
    REASON_NOT_RECORDED,
    REASON_WITHHELD,
    REASON_UNBOUNDED_WITHHOLDING,
    REASON_UNRESOLVED,
    REASON_NAMED,
)


def _clean_text(value: object) -> str:
    """Return a stripped string, or empty for hostile non-string input."""

    return value.strip() if isinstance(value, str) else ""


def _has_undated_object(observation: AbsenceObservation) -> bool:
    """Return whether ``observed_on`` is an accepted non-string object.

    ``None`` and the empty string are intentionally ordinary undated input.
    Any other non-string value remains an accepted observation, but cannot
    participate in staleness accounting. Keeping this classification here
    makes intake and finding reasons describe the same runtime boundary.
    """

    raw = observation.observed_on
    return raw is not None and not isinstance(raw, str)


def _observation_date(
    observation: AbsenceObservation, as_of: date
) -> tuple[date | None, str]:
    """Parse ``observed_on``; return (date-or-None, issue-note).

    The rule itself lives in ``white_line.dates.usable_observation_date`` so
    that every reader of a report resolves dates the same way the scoring
    stage did.
    """

    return usable_observation_date(observation.observed_on, as_of)


def _intake(
    observations: object | None,
    known_ids: frozenset[str],
) -> tuple[dict[str, AbsenceObservation], tuple[IntakeEvent, ...]]:
    """Validate inputs; keep one trusted observation per record.

    An otherwise valid observation with a non-string ``observed_on`` is
    accepted by intake and emits ``UNDATED_OBJECT``. The event exposes the
    existing fail-open treatment for decay without coercing the object or
    aging it. Acceptance at intake is not retention: the reconciliation step
    below may still replace that observation, and it emits its own event
    saying so, so the pair of events describes the full disposition.
    """

    events: list[IntakeEvent] = []
    accepted: dict[str, AbsenceObservation] = {}
    iterable: Iterable[object]
    if observations is None:
        iterable = ()
    else:
        try:
            iterable = iter(cast(Iterable[object], observations))
        except TypeError:
            return {}, (
                IntakeEvent(
                    IntakeCode.NON_ITERABLE_INPUT,
                    "observations is not iterable and was set aside",
                ),
            )
    for position, observation in enumerate(iterable):
        if not isinstance(observation, AbsenceObservation):
            events.append(
                IntakeEvent(
                    IntakeCode.NON_OBSERVATION,
                    f"input {position} is not an absence observation and was set aside",
                    position,
                )
            )
            continue
        if (
            not isinstance(observation.record_id, str)
            or observation.record_id not in known_ids
        ):
            events.append(
                IntakeEvent(
                    IntakeCode.UNKNOWN_RECORD,
                    f"input {position} names an unknown record id and was set aside",
                    position,
                    observation.record_id
                    if isinstance(observation.record_id, str)
                    else "",
                )
            )
            continue
        if not isinstance(observation.state, AbsenceState):
            events.append(
                IntakeEvent(
                    IntakeCode.UNTYPED_STATE,
                    f"input {position} ({observation.record_id}) carries an untyped state and was set aside",
                    position,
                    observation.record_id,
                )
            )
            continue
        if observation.state is AbsenceState.NOT_RECORDED:
            events.append(
                IntakeEvent(
                    IntakeCode.RESERVED_STATE,
                    f"input {position} ({observation.record_id}) asserts NOT_RECORDED; "
                    "that state is reserved for the ledger itself and was set aside",
                    position,
                    observation.record_id,
                    observation.state,
                )
            )
            continue
        if _has_undated_object(observation):
            events.append(
                IntakeEvent(
                    IntakeCode.UNDATED_OBJECT,
                    f"input {position} ({observation.record_id}) has an observation date object that is not "
                    "an ISO date string; the observation was accepted at intake and its date cannot "
                    "participate in staleness accounting",
                    position,
                    observation.record_id,
                    observation.state,
                )
            )
        held = accepted.get(observation.record_id)
        if held is None:
            accepted[observation.record_id] = observation
        elif held.state is not observation.state:
            kept = (
                observation
                if caution_rank(observation.state) > caution_rank(held.state)
                else held
            )
            displaced = held if kept is observation else observation
            accepted[observation.record_id] = kept
            events.append(
                IntakeEvent(
                    IntakeCode.CONFLICTING_STATES,
                    f"conflicting states for {observation.record_id}; kept the more cautious {kept.state.value}",
                    position,
                    observation.record_id,
                    kept.state,
                    displaced.state,
                )
            )
        else:
            accepted[observation.record_id] = observation
            events.append(
                IntakeEvent(
                    IntakeCode.DUPLICATE_STATE,
                    f"duplicate {observation.state.value} observations for {observation.record_id}; kept the last-listed",
                    position,
                    observation.record_id,
                    observation.state,
                    held.state,
                )
            )
    return accepted, tuple(events)


def _finding(
    record: AbsenceRecord, observation: AbsenceObservation | None, as_of: date
) -> AbsenceFinding:
    """Assess one record against its (possibly missing) observation."""

    if observation is None:
        return AbsenceFinding(
            record.id,
            record.kind,
            AbsenceState.NOT_RECORDED,
            (REASON_NOT_RECORDED,),
        )
    observed, date_issue = _observation_date(observation, as_of)
    note = _clean_text(observation.note)
    state = observation.state
    reasons: list[str] = []
    if state is AbsenceState.WITHHELD:
        reasons.append(REASON_WITHHELD)
        if not note:
            reasons.append(REASON_UNBOUNDED_WITHHOLDING)
    elif state is AbsenceState.UNRESOLVED:
        reasons.append(REASON_UNRESOLVED)
    else:  # NAMED (NOT_RECORDED was screened out at intake)
        age = (as_of - observed).days if observed is not None else None
        if age is not None and age > record.review_horizon_days:
            state = AbsenceState.UNRESOLVED
            reasons.append(
                f"the naming is {age} days old, past the {record.review_horizon_days}-day "
                "review horizon; treated as unresolved until re-reviewed"
            )
        else:
            reasons.append(REASON_NAMED)
            if age is not None:
                reasons.append(
                    f"observed {age} days before review, within the "
                    f"{record.review_horizon_days}-day horizon"
                )
    if date_issue:
        reasons.append(date_issue)
    if note:
        reasons.append(f"recorded note: {note}")
    return AbsenceFinding(
        record.id,
        record.kind,
        state,
        tuple(reasons),
        observation.observed_on if isinstance(observation.observed_on, str) else "",
    )


def assess_absence(
    observations: object | None,
    records: Iterable[AbsenceRecord] = WHITE_RECORDS,
    as_of: str | date | None = None,
) -> WhiteReport:
    """Return a typed absence ledger; it does not infer why something is absent.

    ``as_of`` anchors staleness accounting (ISO string, ``date``, or ``None``
    for today). Calling ``assess_absence(observations)`` against the default
    registry keeps its behavior for well-formed, undated input.
    """

    review_date = coerce_review_date(as_of)
    record_tuple = tuple(records)
    if not all(isinstance(record, AbsenceRecord) for record in record_tuple):
        raise ValueError("absence registry contains a non-AbsenceRecord entry")
    failed_checks = [
        check for check in all_ledger_checks(record_tuple) if not check.passed
    ]
    if failed_checks:
        detail = "; ".join(f"{check.name}: {check.detail}" for check in failed_checks)
        raise ValueError(f"absence registry failed structural checks: {detail}")
    accepted, events = _intake(
        observations, frozenset(record.id for record in record_tuple)
    )
    findings = tuple(
        _finding(record, accepted.get(record.id), review_date)
        for record in record_tuple
    )
    notes = tuple(event.message for event in events)
    return WhiteReport(
        findings,
        notes,
        review_date.isoformat(),
        registry_digest(record_tuple),
        events,
    )
