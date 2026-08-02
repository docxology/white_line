from white_line import (
    AbsenceObservation,
    AbsenceState,
    ReviewAction,
    assess_absence,
    requires_follow_up,
    review_directives,
)


def test_review_protocol_maps_states_to_bounded_follow_up() -> None:
    report = assess_absence(
        (
            AbsenceObservation("unobserved-dependency", AbsenceState.NAMED),
            AbsenceObservation("unasked-question", AbsenceState.UNRESOLVED),
            AbsenceObservation(
                "withheld-material", AbsenceState.WITHHELD, "consent boundary"
            ),
        ),
        as_of="2026-07-18",
    )
    directives = {
        directive.record_id: directive for directive in review_directives(report)
    }
    assert directives["unobserved-dependency"].action is ReviewAction.RETAIN_NAMED_SCOPE
    assert not directives["unobserved-dependency"].requires_follow_up
    assert directives["unasked-question"].action is ReviewAction.REOPEN_OR_BOUND
    assert (
        directives["withheld-material"].action
        is ReviewAction.HONOR_AND_CONFIRM_BOUNDARY
    )
    assert (
        directives["negative-space"].action is ReviewAction.RECORD_OR_EXPLICITLY_SCOPE
    )
    assert requires_follow_up(AbsenceState.NOT_RECORDED)
    assert not requires_follow_up(AbsenceState.NAMED)
