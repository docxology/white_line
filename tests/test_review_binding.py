from dataclasses import replace

import pytest

from white_line import (
    WHITE_RECORDS, AbsenceKind, AbsenceObservation, AbsenceState,
    assess_absence, expiry_horizon, report_facets, return_contracts,
)

CONSUMERS = (report_facets, return_contracts, expiry_horizon)


def named_report():
    return assess_absence((AbsenceObservation(
        "unobserved-dependency", AbsenceState.NAMED, "scope", "2026-07-01"
    ),), as_of="2026-07-18")


@pytest.mark.parametrize("consumer", CONSUMERS)
@pytest.mark.parametrize("change", [
    {"review_horizon_days": 1}, {"kind": AbsenceKind.ETHICAL},
    {"description": "different description"}, {"prompt": "different prompt"},
])
def test_consumers_reject_replacement_registry(consumer, change):
    records = (replace(WHITE_RECORDS[0], **change),) + WHITE_RECORDS[1:]
    with pytest.raises(ValueError, match="registry digest"):
        consumer(named_report(), records)


@pytest.mark.parametrize("consumer", CONSUMERS)
def test_consumers_reject_duplicate_registry(consumer):
    with pytest.raises(ValueError, match="structural"):
        consumer(named_report(), WHITE_RECORDS + WHITE_RECORDS[:1])


@pytest.mark.parametrize("consumer", CONSUMERS)
def test_consumers_accept_registry_reordering(consumer):
    report = named_report()
    assert consumer(report) == consumer(report, reversed(WHITE_RECORDS))


@pytest.mark.parametrize("consumer", CONSUMERS)
def test_consumers_reject_old_reports_without_digest(consumer):
    with pytest.raises(ValueError, match="unbound.*digest"):
        consumer(replace(named_report(), registry_digest=""))


@pytest.mark.parametrize("consumer", CONSUMERS)
@pytest.mark.parametrize("mutation", ["duplicate", "kind", "unknown", "missing"])
def test_consumers_reject_invalid_finding_identity(consumer, mutation):
    report = named_report()
    findings = report.findings
    if mutation == "duplicate":
        findings += findings[:1]
    elif mutation == "missing":
        findings = findings[1:]
    elif mutation == "kind":
        findings = (replace(findings[0], kind=AbsenceKind.ETHICAL),) + findings[1:]
    else:
        findings = (replace(findings[0], record_id="unknown-record"),) + findings[1:]
    with pytest.raises(ValueError):
        consumer(replace(report, findings=findings))
