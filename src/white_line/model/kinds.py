"""Enumerated kinds and states for the White Line absence ledger."""

from __future__ import annotations

from enum import Enum


class AbsenceKind(str, Enum):
    """What sort of limit a record describes."""

    EPISTEMIC = "EPISTEMIC"
    ETHICAL = "ETHICAL"
    CONTEMPLATIVE = "CONTEMPLATIVE"


class AbsenceState(str, Enum):
    """The ledger state assigned to a record at review time.

    ``NOT_RECORDED`` is reserved for the ledger itself: it marks the meta-gap
    of a record nobody wrote an observation for. Observations may not assert
    it directly.
    """

    NAMED = "NAMED"
    UNRESOLVED = "UNRESOLVED"
    WITHHELD = "WITHHELD"
    NOT_RECORDED = "NOT_RECORDED"


_CAUTION_RANK: dict[AbsenceState, int] = {
    AbsenceState.NOT_RECORDED: 0,
    AbsenceState.NAMED: 1,
    AbsenceState.UNRESOLVED: 2,
    AbsenceState.WITHHELD: 3,
}


def caution_rank(state: AbsenceState) -> int:
    """Order states by caution; conflicts resolve toward the higher rank.

    Withholding outranks an open question, which outranks a settled naming.
    Under the defined reconciliation contract, a disagreement never resolves
    to a state more settled than its most cautious observer reported.
    """

    return _CAUTION_RANK[state]
