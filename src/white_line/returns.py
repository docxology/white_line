"""Return contracts: what must come back for each finding, and when.

A review horizon is a clock — it says when to look again. A return contract
says what has to come back, what would count as an earned change, and which
review state it returns to. The difference is the difference between a
calendar reminder and a record that can meet new evidence without erasing the
path by which it got here. Each contract therefore carries the review date
and registry digest of the report that produced it, so a later return points
back at the exact state it answers.

Every field is derived deterministically from the finding, its record, and
the report's own review date, through the same single date-resolution rule
the assessor scored with. Nothing here is an approval mechanism: fulfilling a
contract earns a re-review, not a pass, and the honest outcome of a return
may be that the record remains ``UNRESOLVED``. A ``WITHHELD`` contract never
asks for disclosure — its return is a confirmation that the boundary still
holds, from someone with standing to say so.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from collections.abc import Iterable

from .dates import coerce_date, usable_observation_date
from .model import AbsenceRecord, AbsenceState, WhiteReport
from .protocol import ReviewAction, review_action_for_state
from .registry import WHITE_RECORDS


#: The constant trigger and return language, one entry per contract class.
#: They are module constants, not inline strings, so documentation can quote
#: the exact text a live contract carries.
TRIGGER_HORIZON = "the record's review horizon lapses"
TRIGGER_UNDATED_NAMING = (
    "no usable observation date exists, so the naming cannot age; "
    "the return is due at the next review"
)
TRIGGER_OPEN_QUESTION = "the question is standing open now"
TRIGGER_BOUNDARY_CYCLE = "the stated boundary is due for reconfirmation"
TRIGGER_NO_OBSERVATION = "the record has no observation at all"

RETURN_FRESH_NAMING = (
    "a fresh dated observation that re-names, reopens, or withholds the record"
)
RETURN_DATED_NAMING = (
    "a dated re-observation, so the naming can participate in staleness accounting"
)
RETURN_BOUND_OR_REASON = (
    "an observation that bounds the question, resolves it, or records why it stays open"
)
RETURN_BOUNDARY_CONFIRMATION = (
    "a confirmation that the withholding's duty, consent, or safety boundary "
    "still holds — never the withheld material itself"
)
RETURN_OBSERVATION_OR_SCOPE = (
    "an observation, or an explicit statement that this category was not reviewed"
)

ACCEPT_USABLE_DATE = (
    "the returned observation carries a usable ISO date on or after this "
    "report's review date"
)
ACCEPT_BOUNDARY_RESTATED = (
    "the boundary is restated by someone with standing to state it; "
    "remaining WITHHELD is an acceptable outcome"
)
ACCEPT_OPEN_IS_HONEST = (
    "the return is recorded even if the state remains UNRESOLVED; "
    "an honest return may leave the question open"
)
ACCEPT_SCOPE_IS_EXPLICIT = (
    "either an observation enters the ledger or the non-review is stated "
    "in scope, so the silence stops being unaccounted for"
)


@dataclass(frozen=True)
class ReturnContract:
    """One finding's obligation of return, bound to the report that set it.

    ``due_on`` is the last review date on which a current dated naming is
    still current — a strictly later review decays it — and is empty for
    every contract whose trigger is not a horizon lapse. ``review_date`` and
    ``registry_digest`` point back at the producing report so a return can
    name the exact prior state it answers, rather than rewriting history.
    """

    record_id: str
    state: AbsenceState
    action: ReviewAction
    trigger: str
    due_on: str
    expected_return: str
    acceptance_condition: str
    review_date: str
    registry_digest: str


def _named_contract_terms(
    finding_observed_on: str,
    record: AbsenceRecord,
    review_date_iso: str,
) -> tuple[str, str, str, str]:
    """Return (trigger, due_on, expected, acceptance) for a NAMED finding."""

    review_date = coerce_date(review_date_iso, "report.review_date")
    observed, _issue = usable_observation_date(finding_observed_on, review_date)
    if observed is None:
        return (
            TRIGGER_UNDATED_NAMING,
            "",
            RETURN_DATED_NAMING,
            ACCEPT_USABLE_DATE,
        )
    due = observed + timedelta(days=record.review_horizon_days)
    return (
        TRIGGER_HORIZON,
        due.isoformat(),
        RETURN_FRESH_NAMING,
        ACCEPT_USABLE_DATE,
    )


def return_contracts(
    report: WhiteReport,
    records: Iterable[AbsenceRecord] = WHITE_RECORDS,
) -> tuple[ReturnContract, ...]:
    """Derive one return contract per finding, in the report's own order.

    The contracts restate the protocol's follow-up directives as obligations
    with a trigger, an expected artifact, and an observable acceptance
    condition. They add no new judgment: the action verb is the protocol's
    own, the due date is the decay rule read forward, and every contract
    points back at the producing report. None of this authorizes anything.
    """

    records_by_id = {record.id: record for record in records}
    contracts: list[ReturnContract] = []
    for finding in report.findings:
        record = records_by_id.get(finding.record_id)
        if record is None:
            raise ValueError(
                f"finding references unknown record id {finding.record_id!r}"
            )
        if finding.state is AbsenceState.NAMED:
            trigger, due_on, expected, acceptance = _named_contract_terms(
                finding.observed_on, record, report.review_date
            )
        elif finding.state is AbsenceState.UNRESOLVED:
            trigger, due_on, expected, acceptance = (
                TRIGGER_OPEN_QUESTION,
                "",
                RETURN_BOUND_OR_REASON,
                ACCEPT_OPEN_IS_HONEST,
            )
        elif finding.state is AbsenceState.WITHHELD:
            trigger, due_on, expected, acceptance = (
                TRIGGER_BOUNDARY_CYCLE,
                "",
                RETURN_BOUNDARY_CONFIRMATION,
                ACCEPT_BOUNDARY_RESTATED,
            )
        else:  # NOT_RECORDED
            trigger, due_on, expected, acceptance = (
                TRIGGER_NO_OBSERVATION,
                "",
                RETURN_OBSERVATION_OR_SCOPE,
                ACCEPT_SCOPE_IS_EXPLICIT,
            )
        contracts.append(
            ReturnContract(
                finding.record_id,
                finding.state,
                review_action_for_state(finding.state),
                trigger,
                due_on,
                expected,
                acceptance,
                report.review_date,
                report.registry_digest,
            )
        )
    return tuple(contracts)


__all__ = [
    "ACCEPT_BOUNDARY_RESTATED",
    "ACCEPT_OPEN_IS_HONEST",
    "ACCEPT_SCOPE_IS_EXPLICIT",
    "ACCEPT_USABLE_DATE",
    "RETURN_BOUNDARY_CONFIRMATION",
    "RETURN_BOUND_OR_REASON",
    "RETURN_DATED_NAMING",
    "RETURN_FRESH_NAMING",
    "RETURN_OBSERVATION_OR_SCOPE",
    "ReturnContract",
    "TRIGGER_BOUNDARY_CYCLE",
    "TRIGGER_HORIZON",
    "TRIGGER_NO_OBSERVATION",
    "TRIGGER_OPEN_QUESTION",
    "TRIGGER_UNDATED_NAMING",
    "return_contracts",
]
