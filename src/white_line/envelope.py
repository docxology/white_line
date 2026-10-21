"""The common report envelope White Line exports for co-registration.

A reader holding reports from several independent instruments needs one
uniform way to say "this instrument, about this subject, at this review
moment, said this — and here is the pointer to its complete native report."
The envelope is that data contract and nothing more. It points to the full
canonical report by digest instead of copying or reinterpreting its fields,
so the exporting line remains authoritative about its own vocabulary, and it
carries the instrument's non-claims with it. Contract validation checks their
presence; report matching alone does not.

The shared shape is declared per instrument under the schema string
``line.report-envelope/1.0``; sibling instruments that export the same shape
do so by publishing the same schema string, never by importing one another.
``native_status`` is deliberately typed as this line's own vocabulary — for
White Line, the complete ordered per-record states, because this instrument
has no single overall verdict — and envelopes from different lines must not
be compared, ranked, averaged, or merged on it. An envelope is a witness
record, not a score.
"""

from __future__ import annotations

import json
import hashlib
import re
from dataclasses import dataclass

from collections.abc import Iterable

from .dates import coerce_date
from .model import AbsenceState, WhiteReport
from .serialization import report_digest
from .version import LEDGER_VERSION, LEDGER_VERSION_DIGEST

#: The cross-instrument envelope shape this module exports.
ENVELOPE_SCHEMA = "line.report-envelope/1.0"

#: This instrument's identity inside an envelope.
WHITE_LINE_ID = "white_line"

#: The non-claims every envelope carries, restating the instrument boundary
#: from ``docs/claim_boundaries.md`` in transportable form.
SCOPE_AND_NONCLAIMS: tuple[str, ...] = (
    "records typed absence states for supplied observations at a stated review date",
    "not a detector of hidden causes and not evidence about the unobserved world",
    "not a completeness, diligence, or negligence score",
    "not a moral authority and not a substitute for consent or security review",
    "WITHHELD is not evidence of deception, and NOT_RECORDED is not evidence "
    "that nobody knew or that nothing happened",
)


@dataclass(frozen=True)
class ReportEnvelope:
    """One instrument's complete report, referenced without reinterpretation.

    ``report_ref`` is the SHA-256 of the canonical native report, which
    contains the retained derivation — findings, reasons, intake events, and
    notes. ``native_status`` is the complete ordered per-record state list in
    this line's own vocabulary; it is not a summary and must not become one.
    ``source_snapshot_refs`` is caller-supplied provenance for the material
    the observations were made against; the envelope stores, and does not
    verify, those references.
    """

    schema_version: str
    line_id: str
    subject_id: str
    review_date: str
    registry_version: str
    registry_digest: str
    native_status: tuple[tuple[str, str], ...]
    report_ref: str
    source_snapshot_refs: tuple[str, ...]
    scope_and_nonclaims: tuple[str, ...]


def report_envelope(
    report: WhiteReport,
    subject_id: str = "",
    source_snapshot_refs: Iterable[str] = (),
) -> ReportEnvelope:
    """Wrap a report in the common envelope, pointing at — never re-reading —
    its complete canonical form.

    ``subject_id`` names what was reviewed, in the caller's own reference
    scheme; the ledger does not verify it. The envelope's ``report_ref`` is
    computed from the exact report supplied, so an envelope can only ever
    point at the derivation that produced its states.
    """

    if isinstance(source_snapshot_refs, (str, bytes)):
        raise TypeError("source_snapshot_refs must be a collection, not str or bytes")
    refs = tuple(source_snapshot_refs)
    if not all(isinstance(ref, str) and ref.strip() for ref in refs):
        raise ValueError("source_snapshot_refs must be non-blank strings")
    if not isinstance(subject_id, str):
        raise TypeError("subject_id must be a string")
    envelope = ReportEnvelope(
        ENVELOPE_SCHEMA,
        WHITE_LINE_ID,
        subject_id,
        report.review_date,
        LEDGER_VERSION if report.registry_digest == LEDGER_VERSION_DIGEST else "custom/unknown",
        report.registry_digest,
        tuple((finding.record_id, finding.state.value) for finding in report.findings),
        report_digest(report),
        refs,
        SCOPE_AND_NONCLAIMS,
    )
    validate_envelope_contract(envelope)
    return envelope


def validate_envelope_contract(envelope: ReportEnvelope) -> None:
    if not isinstance(envelope, ReportEnvelope):
        raise ValueError("expected a ReportEnvelope")
    if envelope.schema_version != ENVELOPE_SCHEMA or envelope.line_id != WHITE_LINE_ID:
        raise ValueError("unsupported envelope schema or line identity")
    if not isinstance(envelope.subject_id, str):
        raise ValueError("subject_id must be a string")
    if not isinstance(envelope.review_date, str):
        raise ValueError("review_date must be an ISO string")
    coerce_date(envelope.review_date, "review_date")
    for value in (envelope.report_ref, envelope.registry_digest):
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError("report and registry references must be SHA-256 hex digests")
    expected_version = (
        LEDGER_VERSION if envelope.registry_digest == LEDGER_VERSION_DIGEST else "custom/unknown"
    )
    if envelope.registry_version != expected_version:
        raise ValueError("registry version/digest policy mismatch")
    if not isinstance(envelope.native_status, tuple) or not envelope.native_status:
        raise ValueError("native_status must be a nonempty tuple of id/state pairs")
    seen: set[str] = set()
    for pair in envelope.native_status:
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise ValueError("native_status requires id/state pairs")
        record_id, state = pair
        if (not isinstance(record_id, str)
                or re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", record_id) is None
                or record_id in seen
                or not isinstance(state, str)
                or state not in {item.value for item in AbsenceState}):
            raise ValueError("invalid or duplicate native status")
        seen.add(record_id)
    if (not isinstance(envelope.source_snapshot_refs, tuple)
            or not all(isinstance(ref, str) and ref.strip() for ref in envelope.source_snapshot_refs)):
        raise ValueError("source_snapshot_refs must be a tuple of nonblank strings")
    if (not isinstance(envelope.scope_and_nonclaims, tuple)
            or not all(isinstance(item, str) and item.strip() for item in envelope.scope_and_nonclaims)
            or not set(SCOPE_AND_NONCLAIMS).issubset(envelope.scope_and_nonclaims)):
        raise ValueError("required scope and nonclaims must remain attached")


def envelope_digest(envelope: ReportEnvelope) -> str:
    return hashlib.sha256(canonical_envelope(envelope).encode("utf-8")).hexdigest()


def canonical_envelope(envelope: ReportEnvelope) -> str:
    """Serialize an envelope to stable JSON for archiving beside its report.

    Store this string next to the ``canonical_report`` output it points at;
    the pair allows report matching. Separately validate the envelope contract
    and compare a whole-envelope digest with a trusted archival manifest.
    """

    payload = {
        "schema_version": envelope.schema_version,
        "line_id": envelope.line_id,
        "subject_id": envelope.subject_id,
        "review_date": envelope.review_date,
        "registry_version": envelope.registry_version,
        "registry_digest": envelope.registry_digest,
        "native_status": [list(pair) for pair in envelope.native_status],
        "report_ref": envelope.report_ref,
        "source_snapshot_refs": list(envelope.source_snapshot_refs),
        "scope_and_nonclaims": list(envelope.scope_and_nonclaims),
    }
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def envelope_matches_report(envelope: ReportEnvelope, report: WhiteReport) -> bool:
    """Return whether an envelope still points at exactly this report.

    This is the read-back check for an archived pair: the digest, the review
    date, the registry digest, and the per-record states must all agree. A
    mismatch means these fields disagree. Other fields may change without
    affecting this result: use contract validation and a separately trusted
    whole-envelope digest for those boundaries. No check establishes truth.
    """

    return (
        envelope.report_ref == report_digest(report)
        and envelope.review_date == report.review_date
        and envelope.registry_digest == report.registry_digest
        and envelope.native_status
        == tuple(
            (finding.record_id, finding.state.value) for finding in report.findings
        )
    )


__all__ = [
    "ENVELOPE_SCHEMA",
    "ReportEnvelope",
    "SCOPE_AND_NONCLAIMS",
    "WHITE_LINE_ID",
    "canonical_envelope",
    "envelope_matches_report",
    "envelope_digest",
    "validate_envelope_contract",
    "report_envelope",
]
