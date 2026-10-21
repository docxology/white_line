"""Observation, intake-event, finding, and report types.

The report deliberately carries its review date and registry digest. A state
without those two pieces of context is not reproducible: the same observation
can age differently tomorrow, and a custom registry can change the meaning of
an id. ``intake_notes`` remains a string-compatible view for callers of the
first API; ``intake_events`` is the typed form for audit and downstream tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from .kinds import AbsenceKind, AbsenceState


@dataclass(frozen=True)
class AbsenceObservation:
    """A reviewer's dated claim about one record's state.

    ``observed_on`` is an optional ISO ``YYYY-MM-DD`` string. Undated
    observations are accepted; they cannot participate in staleness
    accounting. A non-string date object is also accepted, but is recorded as
    ``UNDATED_OBJECT`` and cannot age; the ledger does not coerce it into a
    date.
    """

    record_id: str
    state: AbsenceState
    note: str = ""
    observed_on: str | date | None = ""


class IntakeCode(str, Enum):
    """Machine-readable records of input handling or reconciliation."""

    # The complete input cannot enter the assessor.
    NON_ITERABLE_INPUT = "NON_ITERABLE_INPUT"
    NON_OBSERVATION = "NON_OBSERVATION"
    UNKNOWN_RECORD = "UNKNOWN_RECORD"
    UNTYPED_STATE = "UNTYPED_STATE"
    RESERVED_STATE = "RESERVED_STATE"
    # An accepted observation has no ISO date for staleness accounting.
    UNDATED_OBJECT = "UNDATED_OBJECT"
    # Multiple accepted observations require one retained record state.
    CONFLICTING_STATES = "CONFLICTING_STATES"
    DUPLICATE_STATE = "DUPLICATE_STATE"


#: The intake codes that mean an input was *set aside* in the manuscript's
#: intake-stage sense: the input never reached matching or scoring. ``UNDATED_OBJECT``
#: is deliberately absent — that observation is accepted, only its date is
#: unusable — and so are the two match-stage codes, which describe how two
#: accepted observations were reconciled rather than an input being refused.
SET_ASIDE_CODES: frozenset[IntakeCode] = frozenset(
    {
        IntakeCode.NON_ITERABLE_INPUT,
        IntakeCode.NON_OBSERVATION,
        IntakeCode.UNKNOWN_RECORD,
        IntakeCode.UNTYPED_STATE,
        IntakeCode.RESERVED_STATE,
    }
)


@dataclass(frozen=True)
class IntakeEvent:
    """One explicit intake or reconciliation event.

    ``position`` refers to the input position when one exists. Events are
    descriptive audit data, not a verdict on the person or project that
    supplied the input.

    ``displaced_state`` preserves reconciliation as co-present data: for the
    two match-stage codes it is the asserted state of the observation the
    reconciliation replaced, so a conflict remains readable as two typed
    surfaces rather than only as a note that a conflict occurred. It is
    ``None`` for every set-aside and dating event, where nothing was
    displaced. Preserving the displaced state does not reopen the retained
    one: the cautious resolution stands.
    """

    code: IntakeCode
    message: str
    position: int | None = None
    record_id: str = ""
    state: AbsenceState | None = None
    displaced_state: AbsenceState | None = None


@dataclass(frozen=True)
class AbsenceFinding:
    """One record's assessed state, with the full trail of reasons."""

    record_id: str
    kind: AbsenceKind
    state: AbsenceState
    reasons: tuple[str, ...]
    observed_on: str = ""
    asserted_state: AbsenceState | None = None


@dataclass(frozen=True)
class WhiteReport:
    """A typed absence ledger plus notes about input handling.

    ``intake_notes`` records each set-aside, reconciliation, or accepted
    non-ISO date object, so discarding and dating loss never happen silently.
    """

    findings: tuple[AbsenceFinding, ...]
    intake_notes: tuple[str, ...] = ()
    review_date: str = ""
    registry_digest: str = ""
    intake_events: tuple[IntakeEvent, ...] = ()

    def tally(self) -> dict[AbsenceState, int]:
        """Count findings per state; every state appears, even at zero."""

        counts = {state: 0 for state in AbsenceState}
        for finding in self.findings:
            counts[finding.state] += 1
        return counts

    def finding_for(self, record_id: str) -> AbsenceFinding | None:
        """Return one finding by id, or ``None`` when it is not in the report."""

        return next(
            (finding for finding in self.findings if finding.record_id == record_id),
            None,
        )

    @property
    def accepted_observation_count(self) -> int:
        """Count findings backed by an accepted observation."""

        return sum(
            finding.state is not AbsenceState.NOT_RECORDED for finding in self.findings
        )

    @property
    def intake_event_count(self) -> int:
        """Count every typed intake event that explains input handling.

        This is the total across all of ``IntakeCode``: inputs that were set
        aside, an accepted observation whose date could not be used, and the
        two match-stage reconciliation events.
        """

        return len(self.intake_events) if self.intake_events else len(self.intake_notes)

    @property
    def set_aside_count(self) -> int:
        """Count inputs that intake refused, in the intake stage's narrow sense.

        Only the codes in ``SET_ASIDE_CODES`` count. An ``UNDATED_OBJECT``
        observation was accepted and scored, and a ``CONFLICTING_STATES`` or
        ``DUPLICATE_STATE`` event describes reconciliation between two
        accepted observations, so none of the three is a set-aside. For a
        report carrying only the first API's string ``intake_notes`` the codes
        are not recoverable, and the note count is reported instead.
        """

        if not self.intake_events:
            return len(self.intake_notes)
        return sum(event.code in SET_ASIDE_CODES for event in self.intake_events)
