from dataclasses import replace

import pytest

import white_line as wl
from white_line.audit import _witness_contract_sound


@pytest.mark.parametrize("identifier", ["-leading", "trailing-", "unobserved dep", "unobserved-dependencу"])
def test_noncanonical_slug_grammar_controls(identifier):
    records = (replace(wl.WHITE_RECORDS[0], id=identifier),) + wl.WHITE_RECORDS[1:]
    assert not wl.ids_are_canonical_slugs(records).passed


@pytest.mark.parametrize("identifier", ["a", "a1", "multi-segment-id-2"])
def test_valid_slug_controls(identifier):
    records = (replace(wl.WHITE_RECORDS[0], id=identifier),) + wl.WHITE_RECORDS[1:]
    assert wl.ledger_sound(records)


def test_compound_probe_reports_collateral_failure_without_exclusivity_claim():
    probes = list(wl.defect_registries())
    target, description, records = probes[1]
    records = (replace(records[0], prompt=""),) + records[1:]
    probes[1] = target, description, records
    result = wl.invariant_defect_battery(registries=tuple(probes))
    assert "fields_are_inhabited" in result[1].also_failed


@pytest.mark.parametrize("assertion,state,observed", [
    (wl.AbsenceState.NAMED, wl.AbsenceState.UNRESOLVED, "2026-07-01"),
    (wl.AbsenceState.UNRESOLVED, wl.AbsenceState.NAMED, "2020-01-01"),
    (wl.AbsenceState.NOT_RECORDED, wl.AbsenceState.UNRESOLVED, "2020-01-01"),
])
def test_inconsistent_typed_transition_is_rejected(assertion, state, observed):
    native = wl.assess_absence((wl.AbsenceObservation(
        "unobserved-dependency", wl.AbsenceState.NAMED, "scope", "2026-07-01"
    ),), as_of="2026-07-18").findings[0]
    with pytest.raises(ValueError):
        wl.finding_facets(replace(native, state=state, asserted_state=assertion,
                                 observed_on=observed), wl.WHITE_RECORDS[0], "2026-07-18")


@pytest.mark.parametrize("change", [
    {"native_status": ()}, {"native_status": (("a", "unknown"),)},
    {"native_status": (("a", "NAMED"), ("a", "WITHHELD"))},
    {"native_status": (("a",),)}, {"subject_id": None},
    {"review_date": None}, {"source_snapshot_refs": "scalar"},
    {"source_snapshot_refs": ("",)}, {"report_ref": "bad"},
    {"scope_and_nonclaims": (None,)},
])
def test_envelope_malformed_shapes_are_rejected(change):
    native = wl.assess_absence((), as_of="2026-07-18")
    envelope = wl.report_envelope(native)
    with pytest.raises(ValueError):
        wl.validate_envelope_contract(replace(envelope, **change))


def test_audit_witness_check_has_a_negative_control():
    report = wl.worked_report()
    assert _witness_contract_sound(report)
    assert not _witness_contract_sound(replace(report, registry_digest="0" * 64))


@pytest.mark.parametrize("consumer", [wl.report_facets, wl.return_contracts, wl.expiry_horizon])
def test_untyped_registry_or_finding_entries_fail_explicitly(consumer):
    report = wl.worked_report()
    with pytest.raises(ValueError, match="non-AbsenceRecord"):
        consumer(report, (None,))
    with pytest.raises(ValueError, match="non-AbsenceFinding"):
        consumer(replace(report, findings=(None,)))
    findings = (replace(report.findings[0], state="NAMED"),) + report.findings[1:]
    with pytest.raises(ValueError, match="AbsenceState"):
        consumer(replace(report, findings=findings))


def test_untyped_public_witness_objects_are_rejected():
    with pytest.raises(ValueError):
        wl.validate_envelope_contract(None)
    with pytest.raises(ValueError):
        wl.project_facets(None)
    with pytest.raises(ValueError):
        wl.finding_facets(None, wl.WHITE_RECORDS[0], "2026-07-18")


@pytest.mark.parametrize("consumer", [wl.report_facets, wl.return_contracts, wl.expiry_horizon])
@pytest.mark.parametrize("change", [
    {"observed_on": "2020-01-01"},
    {"asserted_state": None},
    {"asserted_state": wl.AbsenceState.UNRESOLVED},
])
def test_all_consumers_reject_inconsistent_finding_provenance(consumer, change):
    report = wl.assess_absence((wl.AbsenceObservation(
        "unobserved-dependency", wl.AbsenceState.NAMED, "scope", "2026-07-01"
    ),), as_of="2026-07-18")
    malformed = replace(report, findings=(
        replace(report.findings[0], **change),
    ) + report.findings[1:])
    with pytest.raises(ValueError):
        consumer(malformed)


@pytest.mark.parametrize("consumer", [wl.report_facets, wl.return_contracts, wl.expiry_horizon])
def test_all_consumers_validate_date_even_without_observations(consumer):
    report = wl.assess_absence((), as_of="2026-07-18")
    with pytest.raises(ValueError, match="date"):
        consumer(replace(report, review_date="not-a-date"))


@pytest.mark.parametrize("kind", [None, "EPISTEMIC"])
def test_direct_facets_reject_matching_invalid_kinds(kind):
    finding = wl.assess_absence((), as_of="2026-07-18").findings[0]
    with pytest.raises(ValueError, match="kind"):
        wl.finding_facets(replace(finding, kind=kind),
                          replace(wl.WHITE_RECORDS[0], kind=kind), "2026-07-18")


@pytest.mark.parametrize("identifier", [42, None, "bad id", "slug\n"])
def test_direct_facets_reject_matching_invalid_identifiers(identifier):
    finding = wl.assess_absence((), as_of="2026-07-18").findings[0]
    with pytest.raises(ValueError, match="id"):
        wl.finding_facets(replace(finding, record_id=identifier),
                          replace(wl.WHITE_RECORDS[0], id=identifier), "2026-07-18")


@pytest.mark.parametrize("horizon", [0, -1, True, "90"])
def test_direct_facets_reject_invalid_horizons(horizon):
    finding = wl.assess_absence((), as_of="2026-07-18").findings[0]
    with pytest.raises(ValueError, match="horizon"):
        wl.finding_facets(finding, replace(wl.WHITE_RECORDS[0], review_horizon_days=horizon),
                          "2026-07-18")
