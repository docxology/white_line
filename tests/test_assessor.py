"""Staged assessment semantics: intake, conflicts, staleness, reason trails."""

from datetime import date, datetime

import pytest
from white_line import (
    WHITE_RECORDS,
    AbsenceObservation,
    AbsenceState,
    IntakeCode,
    IntakeEvent,
    assess_absence,
    registry_digest,
    scoring_branch_battery,
    scoring_branch_observations,
)


def _finding(report, record_id):
    return next(item for item in report.findings if item.record_id == record_id)


def test_report_covers_every_record_and_tally_counts_all_states() -> None:
    report = assess_absence(
        (
            AbsenceObservation("unobserved-dependency", AbsenceState.NAMED),
            AbsenceObservation(
                "withheld-material", AbsenceState.WITHHELD, "consent boundary"
            ),
            AbsenceObservation("unasked-question", AbsenceState.UNRESOLVED),
        )
    )
    assert len(report.findings) == len(WHITE_RECORDS)
    tally = report.tally()
    assert set(tally) == set(AbsenceState)
    assert tally[AbsenceState.NAMED] == 1
    assert tally[AbsenceState.WITHHELD] == 1
    assert tally[AbsenceState.UNRESOLVED] == 1
    assert tally[AbsenceState.NOT_RECORDED] == len(WHITE_RECORDS) - 3
    assert report.intake_notes == ()
    assert report.review_date
    assert report.registry_digest == registry_digest(WHITE_RECORDS)
    assert report.accepted_observation_count == 3
    assert report.set_aside_count == 0


def test_none_observations_are_treated_as_an_empty_ledger() -> None:
    report = assess_absence(None)
    assert all(
        finding.state is AbsenceState.NOT_RECORDED for finding in report.findings
    )
    assert report.intake_notes == ()
    assert report.intake_events == ()


def test_non_observation_input_is_set_aside_with_a_note() -> None:
    report = assess_absence(["not an observation", 17])
    assert all(
        finding.state is AbsenceState.NOT_RECORDED for finding in report.findings
    )
    assert len(report.intake_notes) == 2
    assert "not an absence observation" in report.intake_notes[0]
    assert report.intake_events[0].code is IntakeCode.NON_OBSERVATION
    assert report.set_aside_count == 2


def test_non_iterable_observations_are_set_aside_without_raising() -> None:
    report = assess_absence(17)
    assert report.intake_events[0].code is IntakeCode.NON_ITERABLE_INPUT
    assert report.finding_for("negative-space").state is AbsenceState.NOT_RECORDED


def test_unknown_and_non_string_record_ids_are_set_aside() -> None:
    report = assess_absence(
        (
            AbsenceObservation("no-such-record", AbsenceState.NAMED),
            AbsenceObservation(99, AbsenceState.NAMED),
        )
    )
    assert all(
        finding.state is AbsenceState.NOT_RECORDED for finding in report.findings
    )
    assert len(report.intake_notes) == 2
    assert all("unknown record id" in note for note in report.intake_notes)


def test_untyped_state_is_set_aside() -> None:
    report = assess_absence((AbsenceObservation("negative-space", "NAMED"),))
    assert _finding(report, "negative-space").state is AbsenceState.NOT_RECORDED
    assert any("untyped state" in note for note in report.intake_notes)


def test_observations_cannot_assert_not_recorded() -> None:
    report = assess_absence(
        (AbsenceObservation("negative-space", AbsenceState.NOT_RECORDED),)
    )
    finding = _finding(report, "negative-space")
    assert finding.state is AbsenceState.NOT_RECORDED
    assert finding.reasons == ("no absence note was recorded",)
    assert any("reserved for the ledger" in note for note in report.intake_notes)


def test_conflicting_states_resolve_toward_caution_in_either_order() -> None:
    cautious_last = assess_absence(
        (
            AbsenceObservation("withheld-material", AbsenceState.NAMED),
            AbsenceObservation(
                "withheld-material", AbsenceState.WITHHELD, "duty of care"
            ),
        )
    )
    cautious_first = assess_absence(
        (
            AbsenceObservation(
                "withheld-material", AbsenceState.WITHHELD, "duty of care"
            ),
            AbsenceObservation("withheld-material", AbsenceState.NAMED),
        )
    )
    for report in (cautious_last, cautious_first):
        assert _finding(report, "withheld-material").state is AbsenceState.WITHHELD
        assert any("more cautious WITHHELD" in note for note in report.intake_notes)


def test_three_or_more_observers_resolve_to_the_most_cautious() -> None:
    """Caution monotonicity at the arity it is stated for, not only two observers.

    The proposition speaks of "the most cautious accepted observer", with no
    bound on how many there are, while the exhaustive reconciliation test only
    covers ordered pairs. This closes the running-maximum claim over every
    ordered triple of assertable states, and checks which observer's note
    survives. That follows from the two documented rules together: a conflict
    keeps the strictly more cautious observation, and a same-state duplicate
    keeps the last-listed one, so the retained observation is the *last*
    observer at the maximum caution rank.
    """

    from itertools import product

    from white_line import caution_rank
    from white_line.analysis import ASSERTABLE_STATES

    triples = list(product(ASSERTABLE_STATES, repeat=3))
    assert len(triples) == len(ASSERTABLE_STATES) ** 3 == 27
    for triple in triples:
        observations = tuple(
            AbsenceObservation("missing-null-results", state, f"observer {index}")
            for index, state in enumerate(triple)
        )
        report = assess_absence(observations, as_of="2026-07-18")
        finding = _finding(report, "missing-null-results")
        most_cautious = max(caution_rank(state) for state in triple)
        assert caution_rank(finding.state) == most_cautious, triple
        # Every observation after the first leaves an event, so nothing is
        # silently dropped even when three observers agree.
        assert len(report.intake_events) == 2, triple
        winner = max(
            index
            for index, state in enumerate(triple)
            if caution_rank(state) == most_cautious
        )
        assert f"recorded note: observer {winner}" in finding.reasons, triple


def test_the_running_maximum_check_rejects_a_less_cautious_resolution() -> None:
    """Positive control: the assertion above can fail.

    A resolution that kept the *last* observer rather than the most cautious
    one would satisfy a shape-only test. Here the expected rank is computed
    from a deliberately wrong rule and the real report contradicts it.
    """

    from white_line import caution_rank

    triple = (AbsenceState.WITHHELD, AbsenceState.NAMED, AbsenceState.NAMED)
    report = assess_absence(
        tuple(
            AbsenceObservation("missing-null-results", state, f"observer {index}")
            for index, state in enumerate(triple)
        ),
        as_of="2026-07-18",
    )
    finding = _finding(report, "missing-null-results")
    last_wins = caution_rank(triple[-1])
    assert caution_rank(finding.state) != last_wins
    assert finding.state is AbsenceState.WITHHELD


def test_duplicate_same_state_keeps_the_last_listed_note_and_records_the_event() -> (
    None
):
    report = assess_absence(
        (
            AbsenceObservation(
                "unasked-question", AbsenceState.UNRESOLVED, "first pass"
            ),
            AbsenceObservation(
                "unasked-question", AbsenceState.UNRESOLVED, "second pass"
            ),
        )
    )
    finding = _finding(report, "unasked-question")
    assert finding.state is AbsenceState.UNRESOLVED
    assert "recorded note: second pass" in finding.reasons
    assert report.intake_events[0].code is IntakeCode.DUPLICATE_STATE
    assert "kept the last-listed" in report.intake_notes[0]


def test_withholding_without_a_stated_boundary_is_flagged() -> None:
    report = assess_absence(
        (AbsenceObservation("withheld-material", AbsenceState.WITHHELD),)
    )
    finding = _finding(report, "withheld-material")
    assert finding.state is AbsenceState.WITHHELD
    assert any("restraint should name its duty" in reason for reason in finding.reasons)


def test_hostile_non_string_note_is_ignored_but_state_is_kept() -> None:
    report = assess_absence(
        (AbsenceObservation("withheld-material", AbsenceState.WITHHELD, 123),)
    )
    finding = _finding(report, "withheld-material")
    assert finding.state is AbsenceState.WITHHELD
    assert any("restraint should name its duty" in reason for reason in finding.reasons)
    assert not any("recorded note" in reason for reason in finding.reasons)


def test_fresh_dated_naming_stays_named_with_age_in_reasons() -> None:
    report = assess_absence(
        (
            AbsenceObservation(
                "unobserved-dependency",
                AbsenceState.NAMED,
                "checked inputs",
                "2026-07-01",
            ),
        ),
        as_of="2026-07-15",
    )
    finding = _finding(report, "unobserved-dependency")
    assert finding.state is AbsenceState.NAMED
    assert finding.observed_on == "2026-07-01"
    assert any("within the 90-day horizon" in reason for reason in finding.reasons)
    assert "recorded note: checked inputs" in finding.reasons


def test_stale_naming_decays_to_unresolved_past_the_horizon() -> None:
    report = assess_absence(
        (
            AbsenceObservation(
                "unobserved-dependency", AbsenceState.NAMED, "", "2026-01-01"
            ),
        ),
        as_of=date(2026, 7, 15),
    )
    finding = _finding(report, "unobserved-dependency")
    assert finding.state is AbsenceState.UNRESOLVED
    assert any("past the 90-day review horizon" in reason for reason in finding.reasons)


def test_staleness_defaults_to_today_when_as_of_is_omitted() -> None:
    report = assess_absence(
        (
            AbsenceObservation(
                "unobserved-dependency", AbsenceState.NAMED, "", "2000-01-01"
            ),
        )
    )
    assert _finding(report, "unobserved-dependency").state is AbsenceState.UNRESOLVED


def test_unreadable_observation_date_is_ignored_with_a_reason() -> None:
    report = assess_absence(
        (AbsenceObservation("negative-space", AbsenceState.NAMED, "", "not-a-date"),),
        as_of="2026-07-15",
    )
    finding = _finding(report, "negative-space")
    assert finding.state is AbsenceState.NAMED
    assert any("unreadable" in reason for reason in finding.reasons)


def test_future_observation_date_is_ignored_with_a_reason() -> None:
    report = assess_absence(
        (AbsenceObservation("negative-space", AbsenceState.NAMED, "", "2027-01-01"),),
        as_of="2026-07-15",
    )
    finding = _finding(report, "negative-space")
    assert finding.state is AbsenceState.NAMED
    assert any("after the review date" in reason for reason in finding.reasons)


def test_date_object_is_accepted_with_a_visible_undated_event_and_cannot_decay() -> (
    None
):
    report = assess_absence(
        (
            AbsenceObservation(
                "unobserved-dependency", AbsenceState.NAMED, "", date(2020, 1, 1)
            ),
        ),
        as_of="2026-07-18",
    )
    finding = _finding(report, "unobserved-dependency")
    assert report.intake_events == (
        IntakeEvent(
            IntakeCode.UNDATED_OBJECT,
            "input 0 (unobserved-dependency) has an observation date object that is not an ISO date string; "
            "the observation was accepted at intake and its date cannot participate in staleness accounting",
            0,
            "unobserved-dependency",
            AbsenceState.NAMED,
        ),
    )
    assert finding.state is AbsenceState.NAMED
    assert finding.observed_on == ""
    assert "past the 90-day review horizon" not in finding.reasons
    assert any("not an ISO date string" in reason for reason in finding.reasons)
    assert any(
        "cannot participate in staleness accounting" in reason
        for reason in finding.reasons
    )


def test_none_and_empty_observation_dates_remain_ordinary_undated_input() -> None:
    for raw in (None, ""):
        report = assess_absence(
            (AbsenceObservation("negative-space", AbsenceState.NAMED, "", raw),),
            as_of="2026-07-15",
        )
        finding = _finding(report, "negative-space")
        assert finding.state is AbsenceState.NAMED
        assert finding.observed_on == ""
        assert report.intake_events == ()
        assert finding.reasons == ("the absence is explicitly named",)


def test_datetime_observation_date_is_visible_but_not_coerced_or_aged() -> None:
    report = assess_absence(
        (
            AbsenceObservation(
                "negative-space", AbsenceState.NAMED, "", datetime(2020, 1, 1)
            ),
        ),
        as_of="2026-07-15",
    )
    finding = _finding(report, "negative-space")
    assert finding.state is AbsenceState.NAMED
    assert finding.observed_on == ""
    assert [event.code for event in report.intake_events] == [IntakeCode.UNDATED_OBJECT]
    assert any("not an ISO date string" in reason for reason in finding.reasons)


def test_observation_dated_exactly_on_review_date_is_accepted() -> None:
    """Boundary: observed == as_of is present, not future (cutoff is exclusive).

    Pins the `observed > as_of` comparison so flipping it to `>=` (which would
    discard a same-day observation as future-dated) makes a test go red. Without
    this, the future-date branch is executed by off-boundary inputs but its
    boundary value is unasserted.
    """
    review = date(2026, 7, 15)
    finding = _finding(
        assess_absence(
            (
                AbsenceObservation(
                    "unobserved-dependency", AbsenceState.NAMED, "", review.isoformat()
                ),
            ),
            as_of=review,
        ),
        "unobserved-dependency",
    )
    assert finding.state is AbsenceState.NAMED
    assert finding.observed_on == review.isoformat()
    assert not any("after the review date" in reason for reason in finding.reasons)
    assert any("0 days before review" in reason for reason in finding.reasons)


def test_invalid_review_date_fails_closed() -> None:
    import pytest

    with pytest.raises(ValueError, match="ISO date"):
        assess_absence((), as_of="2026-02-30")


def test_malformed_custom_registry_fails_closed() -> None:
    import dataclasses
    import pytest

    malformed = (dataclasses.replace(WHITE_RECORDS[0], title=""),) + WHITE_RECORDS[1:]
    with pytest.raises(ValueError, match="structural checks"):
        assess_absence((), records=malformed)


def test_invalid_review_date_type_fails_closed() -> None:
    from datetime import datetime
    import pytest

    with pytest.raises(TypeError, match="not a datetime"):
        assess_absence((), as_of=datetime(2026, 7, 18))
    with pytest.raises(TypeError, match="as_of must be an ISO date string or a date"):
        assess_absence((), as_of=17)


def test_non_record_registry_entry_fails_closed() -> None:
    import pytest

    with pytest.raises(ValueError, match="non-AbsenceRecord"):
        assess_absence((), records=(object(),))


# --------------------------------------------------------------------------- #
# The shipped scoring battery, which the reason-trail figure reads
# --------------------------------------------------------------------------- #
def test_the_scoring_battery_reaches_every_branch_of_the_rule() -> None:
    """One live assessment per branch, each carrying the reasons it wrote."""

    probes = scoring_branch_battery()
    assert [probe.branch for probe in probes] == [
        branch for branch, _record_id, _supplied in scoring_branch_observations()
    ]
    assert {probe.finding.state for probe in probes} == set(AbsenceState)
    for probe in probes:
        assert probe.finding.reasons, probe.branch
        assert probe.supplied, probe.branch
    decayed = next(probe for probe in probes if probe.branch == "named, past horizon")
    assert decayed.finding.state is AbsenceState.UNRESOLVED
    assert "past the" in decayed.finding.reasons[0]


def test_the_scoring_battery_refuses_a_branch_naming_an_unknown_record() -> None:
    """Positive control: the record guard rejects, so passing means something."""

    with pytest.raises(ValueError, match="names unknown record"):
        scoring_branch_battery(branches=(("typo", "no-such-record", None),))


def test_the_scoring_battery_refuses_a_battery_that_misses_a_state() -> None:
    """A battery that never reaches a state would show less than it claims."""

    only_unrecorded = (("no observation supplied", "unasked-question", None),)
    with pytest.raises(ValueError, match="never reaches"):
        scoring_branch_battery(branches=only_unrecorded)
