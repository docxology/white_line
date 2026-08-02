"""The common report envelope White Line exports for co-registration.

A reader holding reports from several independent instruments needs one
uniform way to say "this instrument, about this subject, at this review
moment, said this — and here is the pointer to its complete native report."
The envelope is that data contract and nothing more. It points to the full
canonical report by digest instead of copying or reinterpreting its fields,
so the exporting line remains authoritative about its own vocabulary, and it
carries the instrument's non-claims with it, so a stored envelope cannot
quietly outgrow what the instrument was allowed to say.

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
from dataclasses import dataclass

from collections.abc import Iterable

from .model import WhiteReport
from .serialization import report_digest
from .version import LEDGER_VERSION

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
    contains the full derivation — findings, reasons, intake events, and
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

    refs = tuple(source_snapshot_refs)
    if not all(isinstance(ref, str) and ref.strip() for ref in refs):
        raise ValueError("source_snapshot_refs must be non-blank strings")
    if not isinstance(subject_id, str):
        raise TypeError("subject_id must be a string")
    return ReportEnvelope(
        ENVELOPE_SCHEMA,
        WHITE_LINE_ID,
        subject_id,
        report.review_date,
        LEDGER_VERSION,
        report.registry_digest,
        tuple((finding.record_id, finding.state.value) for finding in report.findings),
        report_digest(report),
        refs,
        SCOPE_AND_NONCLAIMS,
    )


def canonical_envelope(envelope: ReportEnvelope) -> str:
    """Serialize an envelope to stable JSON for archiving beside its report.

    Store this string next to the ``canonical_report`` output it points at;
    the pair is the smallest archive from which a later review can verify
    that the envelope and the derivation still agree.
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
    mismatch means one of the two was edited after export; the check cannot
    say which, and it says nothing about the truth of either.
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
    "report_envelope",
]
