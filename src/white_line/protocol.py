"""Human review protocol derived from a :class:`WhiteReport`.

The assessor reports states; this module describes the smallest responsible
follow-up for each state. It intentionally does not return ``COMPLIANT`` or a
similar approval result. Human judgment, consent, security review, and
domain-specific evidence remain outside this package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .model import AbsenceFinding, AbsenceState, WhiteReport


class ReviewAction(str, Enum):
    """Bounded follow-up verbs; none is an authorization or safety verdict."""

    RETAIN_NAMED_SCOPE = "RETAIN_NAMED_SCOPE"
    REOPEN_OR_BOUND = "REOPEN_OR_BOUND"
    HONOR_AND_CONFIRM_BOUNDARY = "HONOR_AND_CONFIRM_BOUNDARY"
    RECORD_OR_EXPLICITLY_SCOPE = "RECORD_OR_EXPLICITLY_SCOPE"


@dataclass(frozen=True)
class ReviewDirective:
    """One human-readable next step for one finding."""

    record_id: str
    state: AbsenceState
    action: ReviewAction
    instruction: str
    requires_follow_up: bool


_DIRECTIVES: dict[AbsenceState, tuple[ReviewAction, str, bool]] = {
    AbsenceState.NAMED: (
        ReviewAction.RETAIN_NAMED_SCOPE,
        "Keep the absence explicit; do not treat naming as resolution or evidence of cause.",
        False,
    ),
    AbsenceState.UNRESOLVED: (
        ReviewAction.REOPEN_OR_BOUND,
        "Revisit the open question, bound it, or record why it remains unresolved.",
        True,
    ),
    AbsenceState.WITHHELD: (
        ReviewAction.HONOR_AND_CONFIRM_BOUNDARY,
        "Honor the withholding and confirm the duty, consent, or safety boundary without seeking disclosure.",
        True,
    ),
    AbsenceState.NOT_RECORDED: (
        ReviewAction.RECORD_OR_EXPLICITLY_SCOPE,
        "Record an observation or explicitly state that this category was not reviewed.",
        True,
    ),
}


def directive_for_finding(finding: AbsenceFinding) -> ReviewDirective:
    """Translate one state into a bounded, non-authorizing follow-up."""

    action, instruction, requires_follow_up = _DIRECTIVES[finding.state]
    return ReviewDirective(
        finding.record_id,
        finding.state,
        action,
        instruction,
        requires_follow_up,
    )


def review_directives(report: WhiteReport) -> tuple[ReviewDirective, ...]:
    """Return directives in the report's registry order."""

    return tuple(directive_for_finding(finding) for finding in report.findings)


def review_action_for_state(state: AbsenceState) -> ReviewAction:
    """Return the protocol action used for a state, for diagrams and tooling."""

    return _DIRECTIVES[state][0]


def requires_follow_up(state: AbsenceState) -> bool:
    """Return whether the state requires a human follow-up step."""

    return _DIRECTIVES[state][2]
