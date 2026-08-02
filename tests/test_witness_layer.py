"""The witness layer: conflict co-presence, facets, returns, and envelopes.

Every case here runs the real ``assess_absence`` and reads real reports; the
projection property and the due-date boundary are proven against live
assessments, not against restatements of the rules. Several tests carry the
canonical witness-case families (STATE, RETURN) from the 2026-07-29 design
review in their names.
"""

from __future__ import annotations

import dataclasses
import json
from datetime import date

import pytest

from white_line import (
    ACCEPT_OPEN_IS_HONEST,
    ENVELOPE_SCHEMA,
    LEDGER_VERSION,
    REASON_UNRESOLVED,
    REPORT_SCHEMA,
    RETURN_BOUNDARY_CONFIRMATION,
    RETURN_OBSERVATION_OR_SCOPE,
    SCOPE_AND_NONCLAIMS,
    TRIGGER_HORIZON,
    TRIGGER_NO_OBSERVATION,
    TRIGGER_UNDATED_NAMING,
    WHITE_LINE_ID,
    WHITE_RECORDS,
    WORKED_AS_OF,
    AbsenceFinding,
    AbsenceKind,
    AbsenceObservation,
    AbsenceState,
    DisclosureStance,
    EpistemicSettlement,
    IntakeCode,
    TemporalStatus,
    WitnessFacets,
    assess_absence,
    canonical_envelope,
    canonical_report,
    envelope_matches_report,
    finding_facets,
    project_facets,
    report_digest,
    report_envelope,
    report_facets,
    return_contracts,
    scoring_branch_battery,
    worked_report,
)

RECORDS_BY_ID = {record.id: record for record in WHITE_RECORDS}


def _finding(report, record_id: str) -> AbsenceFinding:
    found = report.finding_for(record_id)
    assert found is not None
    return found


# ---------------------------------------------------------------------------
# Conflict co-presence: the displaced state survives as typed data.
# ---------------------------------------------------------------------------


def test_conflict_preserves_both_surfaces_as_typed_data() -> None:
    """STATE case: strong support and strong resistance stay co-present.

    The cautious resolution stands, and the displaced assertion remains
    readable from the report itself — as a typed state, not only as prose.
    """

    report = assess_absence(
        (
            AbsenceObservation("unasked-question", AbsenceState.NAMED, "first"),
            AbsenceObservation("unasked-question", AbsenceState.WITHHELD, "second"),
        ),
        as_of=WORKED_AS_OF,
    )
    assert _finding(report, "unasked-question").state is AbsenceState.WITHHELD
    event = next(
        item
        for item in report.intake_events
        if item.code is IntakeCode.CONFLICTING_STATES
    )
    assert event.state is AbsenceState.WITHHELD
    assert event.displaced_state is AbsenceState.NAMED
    assert {event.state, event.displaced_state} == {
        AbsenceState.WITHHELD,
        AbsenceState.NAMED,
    }


def test_conflict_records_the_displaced_state_when_the_held_observation_wins() -> None:
    """When the earlier observation is the more cautious one, the incoming
    assertion is the displaced surface."""

    report = assess_absence(
        (
            AbsenceObservation("unasked-question", AbsenceState.WITHHELD, "first"),
            AbsenceObservation("unasked-question", AbsenceState.NAMED, "second"),
        ),
        as_of=WORKED_AS_OF,
    )
    event = next(
        item
        for item in report.intake_events
        if item.code is IntakeCode.CONFLICTING_STATES
    )
    assert event.state is AbsenceState.WITHHELD
    assert event.displaced_state is AbsenceState.NAMED


def test_duplicate_replacement_also_names_the_displaced_state() -> None:
    report = assess_absence(
        (
            AbsenceObservation("negative-space", AbsenceState.NAMED, "first"),
            AbsenceObservation("negative-space", AbsenceState.NAMED, "second"),
        ),
        as_of=WORKED_AS_OF,
    )
    event = next(
        item for item in report.intake_events if item.code is IntakeCode.DUPLICATE_STATE
    )
    assert event.state is AbsenceState.NAMED
    assert event.displaced_state is AbsenceState.NAMED


def test_non_reconciliation_events_displace_nothing() -> None:
    report = assess_absence(
        (
            "not an observation at all",
            AbsenceObservation(
                "fallow-ground", AbsenceState.NAMED, "date object", date(2026, 1, 5)
            ),
        ),
        as_of=WORKED_AS_OF,
    )
    assert report.intake_events
    for event in report.intake_events:
        assert event.displaced_state is None


# ---------------------------------------------------------------------------
# Facets: the caution-ordered state is a projection of three typed facets.
# ---------------------------------------------------------------------------


def test_every_scoring_branch_projects_back_to_its_own_state() -> None:
    """The projection property, branch by branch, over live assessments."""

    for probe in scoring_branch_battery():
        record = RECORDS_BY_ID[probe.finding.record_id]
        facets = finding_facets(probe.finding, record, WORKED_AS_OF)
        assert project_facets(facets) is probe.finding.state, probe.branch


def test_report_facets_project_back_for_every_finding_of_the_worked_report() -> None:
    report = worked_report()
    facets = report_facets(report)
    assert [item.record_id for item in facets] == [
        finding.record_id for finding in report.findings
    ]
    for item, finding in zip(facets, report.findings):
        assert project_facets(item) is finding.state


def test_the_projection_truth_table_is_total_except_the_unrecordable_cell() -> None:
    """All 24 facet combinations either project or fail closed, as pinned."""

    expected: dict[
        tuple[EpistemicSettlement, DisclosureStance, TemporalStatus],
        AbsenceState | None,
    ] = {}
    for settlement in EpistemicSettlement:
        for disclosure in DisclosureStance:
            for temporality in TemporalStatus:
                if disclosure is DisclosureStance.WITHHELD:
                    value: AbsenceState | None = AbsenceState.WITHHELD
                elif settlement is EpistemicSettlement.UNDISCLOSED:
                    value = None
                elif settlement is EpistemicSettlement.NOT_RECORDED:
                    value = AbsenceState.NOT_RECORDED
                elif settlement is EpistemicSettlement.UNRESOLVED:
                    value = AbsenceState.UNRESOLVED
                elif temporality is TemporalStatus.STALE:
                    value = AbsenceState.UNRESOLVED
                else:
                    value = AbsenceState.NAMED
                expected[(settlement, disclosure, temporality)] = value
    assert len(expected) == 24
    for (settlement, disclosure, temporality), value in expected.items():
        facets = WitnessFacets("negative-space", settlement, disclosure, temporality)
        if value is None:
            with pytest.raises(ValueError, match="not a\\s+recordable combination"):
                project_facets(facets)
        else:
            assert project_facets(facets) is value


def test_a_decayed_naming_factors_as_named_and_stale_not_as_asserted_doubt() -> None:
    """RETURN case: reopen without condemning — the prior naming and its age
    survive the decay as facets, not only as a reason string."""

    report = assess_absence(
        (
            AbsenceObservation(
                "unasked-question", AbsenceState.NAMED, "named once", "2025-09-01"
            ),
        ),
        as_of=WORKED_AS_OF,
    )
    finding = _finding(report, "unasked-question")
    assert finding.state is AbsenceState.UNRESOLVED
    assert finding.observed_on == "2025-09-01"
    facets = finding_facets(finding, RECORDS_BY_ID["unasked-question"], WORKED_AS_OF)
    assert facets.settlement is EpistemicSettlement.NAMED
    assert facets.temporality is TemporalStatus.STALE
    assert project_facets(facets) is AbsenceState.UNRESOLVED


def test_an_asserted_open_question_factors_as_unresolved_not_as_decay() -> None:
    report = assess_absence(
        (
            AbsenceObservation(
                "unmeasured-uncertainty",
                AbsenceState.UNRESOLVED,
                "still being estimated",
                "2026-07-01",
            ),
        ),
        as_of=WORKED_AS_OF,
    )
    finding = _finding(report, "unmeasured-uncertainty")
    assert REASON_UNRESOLVED in finding.reasons
    facets = finding_facets(
        finding, RECORDS_BY_ID["unmeasured-uncertainty"], WORKED_AS_OF
    )
    assert facets.settlement is EpistemicSettlement.UNRESOLVED
    assert facets.temporality is TemporalStatus.CURRENT


def test_withholding_factors_as_undisclosed_and_never_decays() -> None:
    """STATE case: protection is honored, not treated as missing evidence."""

    report = assess_absence(
        (
            AbsenceObservation(
                "withheld-material",
                AbsenceState.WITHHELD,
                "duty of care boundary",
                "2020-01-01",
            ),
        ),
        as_of=WORKED_AS_OF,
    )
    finding = _finding(report, "withheld-material")
    assert finding.state is AbsenceState.WITHHELD
    facets = finding_facets(finding, RECORDS_BY_ID["withheld-material"], WORKED_AS_OF)
    assert facets.settlement is EpistemicSettlement.UNDISCLOSED
    assert facets.disclosure is DisclosureStance.WITHHELD
    assert facets.temporality is TemporalStatus.STALE
    assert project_facets(facets) is AbsenceState.WITHHELD


def test_an_unobserved_record_factors_as_not_recorded_not_as_withholding() -> None:
    """STATE case: no observation is held as unobserved, never confused with
    contradiction or withholding."""

    report = assess_absence((), as_of=WORKED_AS_OF)
    finding = _finding(report, "ineffable-remainder")
    facets = finding_facets(finding, RECORDS_BY_ID["ineffable-remainder"], WORKED_AS_OF)
    assert facets.settlement is EpistemicSettlement.NOT_RECORDED
    assert facets.disclosure is DisclosureStance.OPEN
    assert facets.temporality is TemporalStatus.UNDATED


def test_a_current_dated_naming_and_an_undated_object_both_factor_as_named() -> None:
    report = assess_absence(
        (
            AbsenceObservation(
                "negative-space", AbsenceState.NAMED, "current", "2026-06-30"
            ),
            AbsenceObservation(
                "fallow-ground", AbsenceState.NAMED, "date object", date(2026, 1, 5)
            ),
        ),
        as_of=WORKED_AS_OF,
    )
    dated = finding_facets(
        _finding(report, "negative-space"),
        RECORDS_BY_ID["negative-space"],
        WORKED_AS_OF,
    )
    assert dated.settlement is EpistemicSettlement.NAMED
    assert dated.temporality is TemporalStatus.CURRENT
    undated = finding_facets(
        _finding(report, "fallow-ground"), RECORDS_BY_ID["fallow-ground"], WORKED_AS_OF
    )
    assert undated.settlement is EpistemicSettlement.NAMED
    assert undated.temporality is TemporalStatus.UNDATED
    assert project_facets(undated) is AbsenceState.NAMED


def test_facets_fail_closed_on_a_mismatched_record() -> None:
    finding = _finding(assess_absence((), as_of=WORKED_AS_OF), "negative-space")
    with pytest.raises(ValueError, match="supplied\\s+record"):
        finding_facets(finding, RECORDS_BY_ID["fallow-ground"], WORKED_AS_OF)


def test_facets_fail_closed_on_an_unresolved_finding_this_assessor_never_wrote() -> (
    None
):
    """A hand-made UNRESOLVED with no asserted reason and no stale date is
    underivable, and the derivation says so instead of guessing."""

    forged = AbsenceFinding(
        "negative-space",
        AbsenceKind.CONTEMPLATIVE,
        AbsenceState.UNRESOLVED,
        ("a reason this assessor never writes",),
        "2026-06-30",
    )
    with pytest.raises(ValueError, match="cannot have come\\s+from this assessor"):
        finding_facets(forged, RECORDS_BY_ID["negative-space"], WORKED_AS_OF)


def test_report_facets_fail_closed_on_an_unknown_record_id() -> None:
    report = assess_absence((), as_of=WORKED_AS_OF)
    with pytest.raises(ValueError, match="unknown record id"):
        report_facets(report, WHITE_RECORDS[:3])


# ---------------------------------------------------------------------------
# Return contracts: a trigger, an expected artifact, an acceptance condition.
# ---------------------------------------------------------------------------


def test_every_finding_gets_one_contract_pointing_back_at_its_report() -> None:
    report = worked_report()
    contracts = return_contracts(report)
    assert [item.record_id for item in contracts] == [
        finding.record_id for finding in report.findings
    ]
    for contract, finding in zip(contracts, report.findings):
        assert contract.state is finding.state
        assert contract.review_date == report.review_date
        assert contract.registry_digest == report.registry_digest
        assert contract.trigger
        assert contract.expected_return
        assert contract.acceptance_condition


def test_the_due_date_is_the_last_current_day_proven_through_the_assessor() -> None:
    """RETURN case: the contract's due date is bound to the decay rule by
    assessing the same observation on the due date and one day later."""

    observation = AbsenceObservation(
        "negative-space", AbsenceState.NAMED, "left open on purpose", "2026-06-30"
    )
    report = assess_absence((observation,), as_of=WORKED_AS_OF)
    contract = next(
        item for item in return_contracts(report) if item.record_id == "negative-space"
    )
    assert contract.trigger == TRIGGER_HORIZON
    assert contract.due_on == "2027-06-30"  # 2026-06-30 + 365 days
    on_due = assess_absence((observation,), as_of=contract.due_on)
    assert _finding(on_due, "negative-space").state is AbsenceState.NAMED
    after_due = assess_absence((observation,), as_of="2027-07-01")
    assert _finding(after_due, "negative-space").state is AbsenceState.UNRESOLVED


def test_an_undated_naming_owes_a_dateable_return_instead_of_a_due_date() -> None:
    report = assess_absence(
        (AbsenceObservation("uncredited-labor", AbsenceState.NAMED, "no date"),),
        as_of=WORKED_AS_OF,
    )
    contract = next(
        item
        for item in return_contracts(report)
        if item.record_id == "uncredited-labor"
    )
    assert contract.trigger == TRIGGER_UNDATED_NAMING
    assert contract.due_on == ""


def test_a_withheld_contract_never_asks_for_the_withheld_material() -> None:
    """STATE case: the boundary is honored; return is confirmation, not
    disclosure."""

    report = assess_absence(
        (AbsenceObservation("withheld-material", AbsenceState.WITHHELD, "boundary"),),
        as_of=WORKED_AS_OF,
    )
    contract = next(
        item
        for item in return_contracts(report)
        if item.record_id == "withheld-material"
    )
    assert contract.expected_return == RETURN_BOUNDARY_CONFIRMATION
    assert "never the withheld material" in contract.expected_return


def test_an_open_question_may_honestly_remain_open() -> None:
    report = assess_absence(
        (AbsenceObservation("unasked-question", AbsenceState.UNRESOLVED, "open"),),
        as_of=WORKED_AS_OF,
    )
    contract = next(
        item
        for item in return_contracts(report)
        if item.record_id == "unasked-question"
    )
    assert contract.acceptance_condition == ACCEPT_OPEN_IS_HONEST
    assert "may leave the question open" in contract.acceptance_condition


def test_an_unrecorded_category_owes_an_observation_or_an_explicit_scope() -> None:
    report = assess_absence((), as_of=WORKED_AS_OF)
    contract = return_contracts(report)[0]
    assert contract.state is AbsenceState.NOT_RECORDED
    assert contract.trigger == TRIGGER_NO_OBSERVATION
    assert contract.expected_return == RETURN_OBSERVATION_OR_SCOPE


def test_return_contracts_fail_closed_on_an_unknown_record_id() -> None:
    report = assess_absence((), as_of=WORKED_AS_OF)
    with pytest.raises(ValueError, match="unknown record id"):
        return_contracts(report, WHITE_RECORDS[:3])


# ---------------------------------------------------------------------------
# Canonical report and the common envelope.
# ---------------------------------------------------------------------------


def _report_with_every_event_shape():
    return assess_absence(
        (
            "not an observation at all",
            AbsenceObservation("unasked-question", AbsenceState.NAMED, "first"),
            AbsenceObservation("unasked-question", AbsenceState.WITHHELD, "second"),
        ),
        as_of=WORKED_AS_OF,
    )


def test_canonical_report_is_deterministic_and_complete() -> None:
    first = canonical_report(_report_with_every_event_shape())
    second = canonical_report(_report_with_every_event_shape())
    assert first == second
    payload = json.loads(first)
    assert payload["schema_version"] == REPORT_SCHEMA
    assert payload["review_date"] == WORKED_AS_OF
    assert len(payload["findings"]) == len(WHITE_RECORDS)
    events = payload["intake_events"]
    non_observation = next(item for item in events if item["code"] == "NON_OBSERVATION")
    assert non_observation["state"] is None
    assert non_observation["displaced_state"] is None
    conflict = next(item for item in events if item["code"] == "CONFLICTING_STATES")
    assert conflict["state"] == "WITHHELD"
    assert conflict["displaced_state"] == "NAMED"


def test_report_digest_distinguishes_reports() -> None:
    empty = assess_absence((), as_of=WORKED_AS_OF)
    other = assess_absence((), as_of="2026-07-19")
    assert report_digest(empty) != report_digest(other)
    assert report_digest(empty) == report_digest(assess_absence((), as_of=WORKED_AS_OF))


def test_the_envelope_points_at_the_native_report_without_reinterpreting_it() -> None:
    report = worked_report()
    envelope = report_envelope(
        report, subject_id="worked-example", source_snapshot_refs=("snapshot-1",)
    )
    assert envelope.schema_version == ENVELOPE_SCHEMA
    assert envelope.line_id == WHITE_LINE_ID
    assert envelope.subject_id == "worked-example"
    assert envelope.review_date == report.review_date
    assert envelope.registry_version == LEDGER_VERSION
    assert envelope.registry_digest == report.registry_digest
    assert envelope.native_status == tuple(
        (finding.record_id, finding.state.value) for finding in report.findings
    )
    assert envelope.report_ref == report_digest(report)
    assert envelope.source_snapshot_refs == ("snapshot-1",)
    assert envelope.scope_and_nonclaims == SCOPE_AND_NONCLAIMS
    assert any("not a" in claim for claim in envelope.scope_and_nonclaims)


def test_canonical_envelope_round_trips_and_is_deterministic() -> None:
    report = worked_report()
    envelope = report_envelope(report, subject_id="worked-example")
    first = canonical_envelope(envelope)
    second = canonical_envelope(report_envelope(report, subject_id="worked-example"))
    assert first == second
    payload = json.loads(first)
    assert payload["line_id"] == WHITE_LINE_ID
    assert payload["native_status"][0][0] == report.findings[0].record_id
    assert payload["scope_and_nonclaims"] == list(SCOPE_AND_NONCLAIMS)


def test_envelope_matches_report_verifies_an_archived_pair() -> None:
    report = worked_report()
    envelope = report_envelope(report, subject_id="worked-example")
    assert envelope_matches_report(envelope, report)
    other = assess_absence((), as_of="2026-07-19")
    assert not envelope_matches_report(envelope, other)
    for tamper in (
        {"report_ref": "0" * 64},
        {"review_date": "2020-01-01"},
        {"registry_digest": "0" * 64},
        {"native_status": ()},
    ):
        assert not envelope_matches_report(
            dataclasses.replace(envelope, **tamper), report
        )


def test_envelope_input_validation_fails_closed() -> None:
    report = worked_report()
    with pytest.raises(ValueError, match="non-blank strings"):
        report_envelope(report, source_snapshot_refs=("",))
    with pytest.raises(ValueError, match="non-blank strings"):
        report_envelope(report, source_snapshot_refs=(42,))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="subject_id must be a string"):
        report_envelope(report, subject_id=7)  # type: ignore[arg-type]
