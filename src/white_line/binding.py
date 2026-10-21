from collections.abc import Iterable
from datetime import date

from .dates import coerce_date, usable_observation_date
from .invariants import all_ledger_checks, horizons_are_positive, ids_are_canonical_slugs
from .model import AbsenceFinding, AbsenceKind, AbsenceRecord, AbsenceState, WhiteReport
from .serialization import registry_digest


def _validate_finding(
    finding: AbsenceFinding, record: AbsenceRecord, review_date: date
) -> date | None:
    if not isinstance(finding, AbsenceFinding) or not isinstance(record, AbsenceRecord):
        raise ValueError("expected an AbsenceFinding and AbsenceRecord")
    if (not isinstance(finding.record_id, str)
            or not ids_are_canonical_slugs((record,)).passed
            or finding.record_id != record.id):
        raise ValueError("finding id does not match a canonical supplied record id")
    if (not isinstance(finding.kind, AbsenceKind)
            or not isinstance(record.kind, AbsenceKind)
            or finding.kind is not record.kind):
        raise ValueError("finding kind does not match a typed record kind")
    if not horizons_are_positive((record,)).passed:
        raise ValueError("record horizon must be a positive integer")
    if not isinstance(finding.state, AbsenceState) or not isinstance(finding.observed_on, str):
        raise ValueError("finding state or date is malformed")
    if finding.state is AbsenceState.NOT_RECORDED:
        if finding.observed_on or finding.asserted_state is not None:
            raise ValueError("NOT_RECORDED cannot have an observation or assertion")
        return None
    if not isinstance(finding.asserted_state, AbsenceState):
        raise ValueError("finding without typed assertion cannot have come from this assessor schema")
    if finding.asserted_state is AbsenceState.NOT_RECORDED:
        raise ValueError("NOT_RECORDED cannot be asserted")
    observed, _issue = usable_observation_date(finding.observed_on, review_date)
    stale = observed is not None and (review_date - observed).days > record.review_horizon_days
    expected = finding.asserted_state
    if expected is AbsenceState.NAMED and stale:
        expected = AbsenceState.UNRESOLVED
    if finding.state is not expected:
        raise ValueError("finding state and typed assertion contradict its date/horizon")
    return observed


def validate_report_registry(
    report: WhiteReport, records: Iterable[AbsenceRecord]
) -> dict[str, AbsenceRecord]:
    materialized = tuple(records)
    if not all(isinstance(record, AbsenceRecord) for record in materialized):
        raise ValueError("registry structural error: non-AbsenceRecord entry")
    failures = [check for check in all_ledger_checks(materialized) if not check.passed]
    if failures:
        raise ValueError("registry structural checks failed: " + "; ".join(
            f"{check.name}: {check.detail}" for check in failures
        ))
    by_id = {record.id: record for record in materialized}
    if not report.registry_digest:
        raise ValueError("unbound report without registry digest cannot be bound; reassess explicitly")
    if registry_digest(materialized) != report.registry_digest:
        raise ValueError("report registry digest does not match supplied registry")
    review_date = coerce_date(report.review_date, "report.review_date")
    seen: set[str] = set()
    for finding in report.findings:
        if not isinstance(finding, AbsenceFinding):
            raise ValueError("report contains a non-AbsenceFinding entry")
        if not isinstance(finding.record_id, str) or finding.record_id not in by_id:
            raise ValueError(f"finding references unknown record id {finding.record_id!r}")
        if finding.record_id in seen:
            raise ValueError("report contains duplicate finding ids")
        seen.add(finding.record_id)
        if (not isinstance(finding.kind, AbsenceKind)
                or finding.kind is not by_id[finding.record_id].kind):
            raise ValueError("finding kind does not match registry")
        if not isinstance(finding.state, AbsenceState):
            raise ValueError("finding state must be an AbsenceState")
        _validate_finding(finding, by_id[finding.record_id], review_date)
    if seen != set(by_id):
        raise ValueError("report must contain exactly one finding per registry record")
    return by_id
