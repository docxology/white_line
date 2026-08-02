"""Deterministic absence-registry serialization and review manifest.

The digest here is a change-review and drift-detection aid for the ledger's
own content: it lets a stored manifest be compared against a later checkout
so silent edits surface during review. It carries no security or safety
semantics.
"""

from __future__ import annotations

import hashlib
import json

from .model import AbsenceRecord, WhiteReport
from .version import LEDGER_VERSION, __version__

#: Schema identifiers are namespaced per payload shape. Three different JSON
#: documents used to declare a bare ``"1.1"``/``"1.2"``, which made the string
#: useless for telling one payload from another during review.
REGISTRY_MANIFEST_SCHEMA = "white-line.registry-manifest/1.1"
REGISTRY_ARTIFACT_SCHEMA = "white-line.registry-artifact/1.1"
FIGURE_REGISTRY_SCHEMA = "white-line.figure-registry/1.3"
REPORT_SCHEMA = "white-line.report/1.0"


def canonical_registry(records: tuple[AbsenceRecord, ...]) -> str:
    """Serialize records to compact, id-sorted, key-sorted JSON."""

    payload = [item.canonical() for item in sorted(records, key=lambda item: item.id)]
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def registry_digest(records: tuple[AbsenceRecord, ...]) -> str:
    """SHA-256 over the canonical form; stable across record order."""

    return hashlib.sha256(canonical_registry(records).encode("utf-8")).hexdigest()


def canonical_report(report: WhiteReport) -> str:
    """Serialize a complete report to stable JSON so it can be archived.

    Two identical assessments produce byte-identical output, which lets a
    report be diffed, cited, and pointed at by digest in a review record. The
    serialization is complete — findings with their full reasons trails,
    typed intake events including any displaced state, notes, review date,
    and registry digest — because a reference to a report is only a witness
    if the whole derivation is behind it.
    """

    payload = {
        "schema_version": REPORT_SCHEMA,
        "review_date": report.review_date,
        "registry_digest": report.registry_digest,
        "intake_notes": list(report.intake_notes),
        "intake_events": [
            {
                "code": event.code.value,
                "message": event.message,
                "position": event.position,
                "record_id": event.record_id,
                "state": event.state.value if event.state else None,
                "displaced_state": (
                    event.displaced_state.value if event.displaced_state else None
                ),
            }
            for event in report.intake_events
        ],
        "findings": [
            {
                "record_id": finding.record_id,
                "kind": finding.kind.value,
                "state": finding.state.value,
                "reasons": list(finding.reasons),
                "observed_on": finding.observed_on,
            }
            for finding in report.findings
        ],
    }
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def report_digest(report: WhiteReport) -> str:
    """SHA-256 over the canonical report; the pointer an envelope carries."""

    return hashlib.sha256(canonical_report(report).encode("utf-8")).hexdigest()


def registry_manifest(records: tuple[AbsenceRecord, ...]) -> dict[str, object]:
    """Summarize the ledger for change review: versions, counts, and digest."""

    kinds: dict[str, int] = {}
    for record in records:
        kinds[record.kind.value] = kinds.get(record.kind.value, 0) + 1
    return {
        "schema_version": REGISTRY_MANIFEST_SCHEMA,
        "package_version": __version__,
        "ledger_version": LEDGER_VERSION,
        "record_count": len(records),
        "records_by_kind": dict(sorted(kinds.items())),
        "digest": registry_digest(records),
    }


__all__ = [
    "FIGURE_REGISTRY_SCHEMA",
    "REGISTRY_ARTIFACT_SCHEMA",
    "REGISTRY_MANIFEST_SCHEMA",
    "REPORT_SCHEMA",
    "canonical_registry",
    "canonical_report",
    "registry_digest",
    "registry_manifest",
    "report_digest",
]
