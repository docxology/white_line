from dataclasses import replace

import pytest

import white_line as wl


def report(note="open"):
    return wl.assess_absence((wl.AbsenceObservation(
        "unasked-question", wl.AbsenceState.UNRESOLVED, note
    ),), as_of="2026-07-18")


def test_exact_return_reference_distinguishes_notes_and_events():
    first = report()
    others = (report("different"), replace(first, intake_events=(
        wl.IntakeEvent(wl.IntakeCode.NON_OBSERVATION, "another event", 0),
    )))
    contract = wl.return_contracts(first)[0]
    assert contract.originating_report_ref == wl.report_digest(first)
    assert contract == wl.return_contracts(report())[0]
    for other in others:
        assert contract.originating_report_ref != wl.return_contracts(other)[0].originating_report_ref


def test_recorded_return_checks_the_contract_and_report_pair():
    prior = report()
    contract = wl.return_contracts(prior)[0]
    assert wl.return_matches_contract(contract, prior, contract.originating_report_ref, contract.record_id)
    assert not wl.return_matches_contract(contract, report("other"), contract.originating_report_ref, contract.record_id)
    assert not wl.return_matches_contract(contract, prior, "0" * 64, contract.record_id)
    assert not wl.return_matches_contract(contract, prior, contract.originating_report_ref, "other")
    assert not wl.return_matches_contract(replace(contract, trigger="edited"), prior, contract.originating_report_ref, contract.record_id)


@pytest.mark.parametrize("outer", ["snapshot-1", b"snapshot-1"])
def test_snapshot_collection_is_not_a_scalar(outer):
    with pytest.raises(TypeError):
        wl.report_envelope(report(), source_snapshot_refs=outer)


def test_custom_registry_is_not_labeled_as_shipped():
    records = (replace(wl.WHITE_RECORDS[0], prompt="custom prompt"),) + wl.WHITE_RECORDS[1:]
    native = wl.assess_absence((), records, as_of="2026-07-18")
    envelope = wl.report_envelope(native)
    assert envelope.registry_version == "custom/unknown"
    wl.validate_envelope_contract(envelope)


@pytest.mark.parametrize("field,value,matches,valid", [
    ("schema_version", "other/1", True, False),
    ("line_id", "another-line", True, False),
    ("subject_id", "another-subject", True, True),
    ("review_date", "2026-07-19", False, True),
    ("registry_version", "invented", True, False),
    ("registry_digest", "0" * 64, False, False),
    ("native_status", (("unasked-question", "NAMED"),), False, True),
    ("report_ref", "0" * 64, False, True),
    ("source_snapshot_refs", ("another-snapshot",), True, True),
    ("scope_and_nonclaims", (), True, False),
])
def test_envelope_fields_have_separate_validation_boundaries(field, value, matches, valid):
    native = report()
    envelope = wl.report_envelope(native, source_snapshot_refs=("snapshot-1",))
    changed = replace(envelope, **{field: value})
    assert wl.envelope_matches_report(changed, native) is matches
    if valid:
        wl.validate_envelope_contract(changed)
    else:
        with pytest.raises(ValueError):
            wl.validate_envelope_contract(changed)
    assert wl.envelope_digest(changed) != wl.envelope_digest(envelope)


def test_valid_envelope_and_digest_repeat():
    envelope = wl.report_envelope(report(), source_snapshot_refs=("snapshot-1",))
    wl.validate_envelope_contract(envelope)
    assert wl.envelope_digest(envelope) == wl.envelope_digest(envelope)
