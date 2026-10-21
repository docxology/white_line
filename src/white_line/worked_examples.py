"""Shared worked inputs for the ledger's distributional views.

Every example here is an *input set*, never a stored result. Callers run them
through the public ``assess_absence`` API, so a figure or a document that
quotes one of these examples is quoting a live computation rather than a
transcript that could drift from the code.
"""

from __future__ import annotations

import json

from dataclasses import dataclass
from datetime import date

from .assessor import assess_absence
from .model import (
    AbsenceFinding,
    AbsenceObservation,
    AbsenceState,
    IntakeCode,
    IntakeEvent,
    WhiteReport,
)


#: Review date for the worked seven-input example cited in the manuscript.
WORKED_AS_OF = "2026-07-18"

#: Review date for the refresh-queue example. Held separate from
#: ``WORKED_AS_OF`` so the two examples can be re-dated independently.
EXPIRY_AS_OF = "2026-07-18"


def worked_intake_observations() -> tuple[object, ...]:
    """Return the seven inputs used to show intake and reconciliation."""

    return (
        AbsenceObservation(
            "unobserved-dependency",
            AbsenceState.NAMED,
            "Checked the upstream feed.",
            "2026-06-01",
        ),
        AbsenceObservation(
            "unobserved-dependency",
            AbsenceState.UNRESOLVED,
            "The feed check did not cover the mirror.",
        ),
        AbsenceObservation(
            "withheld-material",
            AbsenceState.WITHHELD,
            "Identifying details stay out of the publication.",
        ),
        AbsenceObservation(
            "withheld-material", AbsenceState.WITHHELD, "Confirmed with the field team."
        ),
        AbsenceObservation("no-such-record", AbsenceState.NAMED, "typo id"),
        AbsenceObservation(
            "negative-space", AbsenceState.NOT_RECORDED, "trying to assert silence"
        ),
        "not an observation at all",
    )


def worked_report() -> WhiteReport:
    """Assess the worked inputs at their stated review date."""

    return assess_absence(worked_intake_observations(), as_of=WORKED_AS_OF)


def expiry_observations() -> tuple[AbsenceObservation, ...]:
    """Return dated namings that exercise every branch of ``expiry_horizon``.

    The set is built so the refresh queue has something to show *and* both of
    its documented omissions are non-empty: four namings are current and
    therefore queued, one carries no date at all, and one is old enough that
    the assessor already decayed it to ``UNRESOLVED``. A queue drawn from an
    input set with no omissions would silently look complete.
    """

    return (
        AbsenceObservation(
            "unobserved-dependency",
            AbsenceState.NAMED,
            "Upstream feed checked end to end.",
            "2026-05-20",
        ),
        AbsenceObservation(
            "unmeasured-uncertainty",
            AbsenceState.NAMED,
            "Variance stated for the reported figure.",
            "2026-07-02",
        ),
        AbsenceObservation(
            "withheld-material",
            AbsenceState.NAMED,
            "Boundary restated with the field team.",
            "2026-03-11",
        ),
        AbsenceObservation(
            "negative-space",
            AbsenceState.NAMED,
            "The open question was left open on purpose.",
            "2026-06-30",
        ),
        AbsenceObservation(
            "uncredited-labor",
            AbsenceState.NAMED,
            "Credit reviewed, but the reviewer recorded no date.",
        ),
        AbsenceObservation(
            "unasked-question",
            AbsenceState.NAMED,
            "Named once and never revisited.",
            "2025-09-01",
        ),
    )


def expiry_report() -> WhiteReport:
    """Assess the refresh-queue inputs at their stated review date."""

    return assess_absence(expiry_observations(), as_of=EXPIRY_AS_OF)


@dataclass(frozen=True)
class ScoringProbe:
    """One branch of the scoring rule, with the finding it actually produced.

    ``finding`` comes from a live ``assess_absence`` call, so ``reasons`` is
    the trail the evaluator wrote rather than a transcript of it.
    """

    branch: str
    supplied: str
    finding: AbsenceFinding


def scoring_branch_observations() -> tuple[tuple[str, str, object], ...]:
    """Return one input per scoring branch: branch name, record id, input.

    An input of ``None`` means no observation was supplied for that record,
    which is the branch that produces the ledger-reserved state. Every other
    entry is the single observation the branch is reached by.
    """

    return (
        ("no observation supplied", "unasked-question", None),
        (
            "withheld, boundary stated",
            "withheld-material",
            AbsenceObservation(
                "withheld-material",
                AbsenceState.WITHHELD,
                "Identifying details stay out of the publication.",
            ),
        ),
        (
            "withheld, note blank",
            "silenced-perspective",
            AbsenceObservation("silenced-perspective", AbsenceState.WITHHELD, ""),
        ),
        (
            "named but not resolved",
            "unmeasured-uncertainty",
            AbsenceObservation(
                "unmeasured-uncertainty",
                AbsenceState.UNRESOLVED,
                "The variance is still being estimated.",
            ),
        ),
        (
            "named, within horizon",
            "negative-space",
            AbsenceObservation(
                "negative-space",
                AbsenceState.NAMED,
                "Left open on purpose this cycle.",
                "2026-06-30",
            ),
        ),
        (
            "named, past horizon",
            "missing-null-results",
            AbsenceObservation(
                "missing-null-results",
                AbsenceState.NAMED,
                "The dead ends were written up once.",
                "2025-09-01",
            ),
        ),
    )


def scoring_branch_battery(
    branches: tuple[tuple[str, str, object], ...] | None = None,
) -> tuple[ScoringProbe, ...]:
    """Assess one input per scoring branch and return what each produced.

    The battery is the executable form of the scoring rule: each branch is
    reached by a real ``assess_absence`` call, and the finding it returns
    carries the ordered reasons the evaluator wrote.

    Args:
        branches: Branch name, record id, and input triples, defaulting to
            ``scoring_branch_observations()``. A deliberately wrong battery is
            how the guards below are shown to reject.

    Raises:
        ValueError: If a branch names a record the report does not carry, or if
            the battery does not reach every member of the state alphabet. A
            battery that missed a state would demonstrate less than it claims.
    """

    probes: list[ScoringProbe] = []
    for branch, record_id, supplied in (
        scoring_branch_observations() if branches is None else branches
    ):
        report = assess_absence(
            () if supplied is None else (supplied,), as_of=WORKED_AS_OF
        )
        finding = report.finding_for(record_id)
        if finding is None:
            raise ValueError(f"branch {branch!r} names unknown record {record_id!r}")
        rendered = (
            "no observation for this record"
            if supplied is None
            else _render_observation(supplied)
        )
        probes.append(ScoringProbe(branch, rendered, finding))
    reached = {probe.finding.state for probe in probes}
    missing = sorted(state.value for state in AbsenceState if state not in reached)
    if missing:
        raise ValueError(f"the scoring battery never reaches {missing}")
    return tuple(probes)


@dataclass(frozen=True)
class IntakeProbe:
    """One intake-battery case: the input supplied and the event it produced.

    ``rendered_input`` is derived from the supplied object, not written by
    hand, so the quoted input in a figure cannot drift from the input the
    assessor actually consumed.
    """

    code: IntakeCode
    rendered_input: str
    event: IntakeEvent


def _render_observation(observation: object) -> str:
    """Return a short source-like rendering of one battery input."""

    if not isinstance(observation, AbsenceObservation):
        return repr(observation)
    state = observation.state
    state_text = (
        state.value if isinstance(state, AbsenceState) else repr(state)
    )
    dated = observation.observed_on
    if isinstance(dated, str) and dated:
        tail = f", {dated!r}"
    elif isinstance(dated, date):
        tail = f", date({dated.year}, {dated.month}, {dated.day})"
    else:
        tail = ""
    return f"AbsenceObservation({observation.record_id!r}, {state_text}{tail})"


def intake_probe_inputs() -> tuple[tuple[IntakeCode, object], ...]:
    """Return one minimal input per ``IntakeCode``, in enumeration order.

    Each entry pairs the code the input is designed to reach with the input
    itself. ``NON_ITERABLE_INPUT`` is reached only by a whole input that is
    not iterable, so the battery supplies whole inputs rather than a single
    observation list.
    """

    return (
        (IntakeCode.NON_ITERABLE_INPUT, 42),
        (IntakeCode.NON_OBSERVATION, ("not an observation at all",)),
        (
            IntakeCode.UNKNOWN_RECORD,
            (AbsenceObservation("no-such-record", AbsenceState.NAMED, "typo id"),),
        ),
        (
            IntakeCode.UNTYPED_STATE,
            (AbsenceObservation("unasked-question", json.loads('"NAMED"'), "a bare string"),),
        ),
        (
            IntakeCode.RESERVED_STATE,
            (
                AbsenceObservation(
                    "negative-space", AbsenceState.NOT_RECORDED, "asserting silence"
                ),
            ),
        ),
        (
            IntakeCode.UNDATED_OBJECT,
            (
                AbsenceObservation(
                    "fallow-ground",
                    AbsenceState.NAMED,
                    "a date object, not an ISO string",
                    date(2026, 1, 5),
                ),
            ),
        ),
        (
            IntakeCode.CONFLICTING_STATES,
            (
                AbsenceObservation(
                    "missing-null-results", AbsenceState.NAMED, "first observer"
                ),
                AbsenceObservation(
                    "missing-null-results", AbsenceState.WITHHELD, "second observer"
                ),
            ),
        ),
        (
            IntakeCode.DUPLICATE_STATE,
            (
                AbsenceObservation(
                    "silenced-perspective", AbsenceState.WITHHELD, "first note"
                ),
                AbsenceObservation(
                    "silenced-perspective", AbsenceState.WITHHELD, "second note"
                ),
            ),
        ),
    )


def intake_reachability_battery(
    probe_inputs: tuple[tuple[IntakeCode, object], ...] | None = None,
) -> tuple[IntakeProbe, ...]:
    """Run the battery and return the event each designed input produced.

    This is a positive control for the intake contract: it demonstrates that
    every ``IntakeCode`` is reachable, which a tally showing three zeros
    cannot. It is a constructed battery, not observed input.

    Args:
        probe_inputs: The code-and-input pairs to run, defaulting to
            ``intake_probe_inputs()``. Supplying a deliberately wrong battery
            is how the two guards below are shown to reject; a guard that has
            never rejected anything is not protection.

    Raises:
        ValueError: If a probe fails to reach the code it targets, or if the
            battery does not cover the full live ``IntakeCode`` alphabet. An
            uncovered code would make the control vacuous for that code.
    """

    probes: list[IntakeProbe] = []
    for code, supplied in (
        intake_probe_inputs() if probe_inputs is None else probe_inputs
    ):
        report = assess_absence(supplied, as_of=WORKED_AS_OF)
        event = next(
            (item for item in report.intake_events if item.code is code), None
        )
        if event is None:
            raise ValueError(f"intake probe for {code.value} produced no such event")
        observations = supplied if isinstance(supplied, tuple) else (supplied,)
        rendered = " + ".join(_render_observation(item) for item in observations)
        probes.append(IntakeProbe(code, rendered, event))
    if tuple(probe.code for probe in probes) != tuple(IntakeCode):
        raise ValueError("the intake battery must cover every IntakeCode member, in order")
    return tuple(probes)
