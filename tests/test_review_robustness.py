from dataclasses import replace
from datetime import date, datetime

import pytest

import white_line as wl


@pytest.mark.parametrize("field", ["settlement", "disclosure", "temporality"])
@pytest.mark.parametrize("value", [None, "WITHHELD", object()])
def test_untyped_facets_are_rejected(field, value):
    facets = wl.WitnessFacets("unasked-question", wl.EpistemicSettlement.NAMED,
                             wl.DisclosureStance.OPEN, wl.TemporalStatus.CURRENT)
    with pytest.raises(ValueError):
        wl.project_facets(replace(facets, **{field: value}))


@pytest.mark.parametrize("state,date_text,change", [
    (wl.AbsenceState.NAMED, "2026-07-01", {"observed_on": "2020-01-01"}),
    (wl.AbsenceState.NOT_RECORDED, "", {"observed_on": "2026-07-01"}),
    (wl.AbsenceState.NAMED, "", {"state": "NAMED"}),
    (wl.AbsenceState.NAMED, "", {"kind": wl.AbsenceKind.ETHICAL}),
])
def test_impossible_findings_are_rejected(state, date_text, change):
    obs = () if state is wl.AbsenceState.NOT_RECORDED else (
        wl.AbsenceObservation("unobserved-dependency", state, "scope", date_text),)
    finding = wl.assess_absence(obs, as_of="2026-07-18").findings[0]
    with pytest.raises(ValueError):
        wl.finding_facets(replace(finding, **change), wl.WHITE_RECORDS[0], "2026-07-18")


def test_display_prose_does_not_decide_assertion_or_decay():
    for state, observed in [(wl.AbsenceState.NAMED, "2020-01-01"),
                            (wl.AbsenceState.UNRESOLVED, "2026-07-01")]:
        finding = wl.assess_absence((wl.AbsenceObservation(
            "unobserved-dependency", state, "scope", observed
        ),), as_of="2026-07-18").findings[0]
        assert wl.finding_facets(finding, wl.WHITE_RECORDS[0], "2026-07-18") == wl.finding_facets(
            replace(finding, reasons=("edited display prose",)), wl.WHITE_RECORDS[0], "2026-07-18")


class EqualityMustNotRun:
    def __eq__(self, other):
        raise RuntimeError("unsupported date equality invoked")


@pytest.mark.parametrize("raw", [EqualityMustNotRun(), date(2020, 1, 1), datetime(2020, 1, 1)])
def test_unsupported_date_is_accepted_undated_without_equality(raw):
    report = wl.assess_absence((wl.AbsenceObservation(
        "unobserved-dependency", wl.AbsenceState.NAMED, "scope", raw
    ),), as_of="2026-07-18")
    assert report.findings[0].state is wl.AbsenceState.NAMED
    assert report.findings[0].observed_on == ""
    assert report.intake_events[0].code is wl.IntakeCode.UNDATED_OBJECT
    assert report.set_aside_count == 0


def test_iterator_producer_failure_propagates_without_partial_report():
    def producer():
        yield wl.AbsenceObservation("unasked-question", wl.AbsenceState.NAMED)
        raise RuntimeError("producer interrupted")
    with pytest.raises(RuntimeError, match="producer interrupted"):
        wl.assess_absence(producer(), as_of="2026-07-18")


@pytest.mark.parametrize("suffix", ["\n", "\r", " space", "-", "\t"])
def test_slug_consumes_entire_identifier(suffix):
    records = (replace(wl.WHITE_RECORDS[0], id="unobserved-dependency" + suffix),) + wl.WHITE_RECORDS[1:]
    assert not wl.ids_are_canonical_slugs(records).passed
    with pytest.raises(ValueError, match="structural"):
        wl.assess_absence((), records, as_of="2026-07-18")


@pytest.mark.parametrize("start,end,step,count", [
    (date.max, date.max, 1, 1),
    (date(9999, 12, 30), date.max, 1, 2),
    (date(2026, 1, 1), date(2026, 1, 3), 10**30, 1),
])
def test_sweep_stops_before_out_of_range_step(start, end, step, count):
    assert len(wl.decay_timeline((), start, end, step_days=step)) == count


def test_unrepresentable_contract_due_date_is_explicit():
    records = (replace(wl.WHITE_RECORDS[0], review_horizon_days=10**30),) + wl.WHITE_RECORDS[1:]
    report = wl.assess_absence((wl.AbsenceObservation(
        records[0].id, wl.AbsenceState.NAMED, "scope", "2026-07-01"
    ),), records, as_of="2026-07-18")
    with pytest.raises(ValueError, match="due date.*representable"):
        wl.return_contracts(report, records)


def test_archive_intentionally_loses_displaced_notes_but_refs_can_distinguish():
    def history(note):
        return wl.assess_absence((
            wl.AbsenceObservation("unasked-question", wl.AbsenceState.NAMED, note),
            wl.AbsenceObservation("unasked-question", wl.AbsenceState.WITHHELD, "boundary"),
        ), as_of="2026-07-18")
    first, second = history("first displaced note"), history("second displaced note")
    assert wl.canonical_report(first) == wl.canonical_report(second)
    assert wl.canonical_envelope(wl.report_envelope(first)) == wl.canonical_envelope(wl.report_envelope(second))
    assert wl.envelope_digest(wl.report_envelope(first, source_snapshot_refs=("authorized-a",))) != wl.envelope_digest(
        wl.report_envelope(second, source_snapshot_refs=("authorized-b",)))
