"""Factor a finding's single caution-ordered state into typed facets.

The ledger's total caution order (``NOT_RECORDED < NAMED < UNRESOLVED <
WITHHELD``) is a safe *projection*: it prevents disagreement or age from
making the record look more settled. It is not the whole state space. A
finding's state compresses three different questions — how epistemically
settled the record is, whether disclosure is being withheld, and how current
the recorded observation is — into one ordered value. This module makes that
compression inspectable by deriving the three facets from a finding and by
stating the projection rule that recovers the shipped state from them.

Nothing here changes what the assessor records or emits. ``finding_facets``
reads a finding the assessor produced; ``project_facets`` is the projection
rule, and for every finding a live ``assess_absence`` call produces, the
projection of the derived facets equals the finding's state (the test suite
proves this branch by branch). The facets describe recorded data only: they
are not new observations, ``UNDISCLOSED`` is a statement about what the
ledger can see rather than an accusation, and ``STALE`` describes the age of
a recording, never the world the record points at.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from collections.abc import Iterable

from .assessor import REASON_UNRESOLVED
from .dates import coerce_date, usable_observation_date
from .model import (
    AbsenceFinding,
    AbsenceRecord,
    AbsenceState,
    WhiteReport,
)
from .registry import WHITE_RECORDS


class EpistemicSettlement(str, Enum):
    """How settled the recorded question is, as far as the ledger can see.

    ``UNDISCLOSED`` marks the settlement behind a stated withholding: the
    ledger records that a boundary exists and refuses to guess what sits
    behind it. It is a visibility statement, not a suspicion.
    """

    NOT_RECORDED = "NOT_RECORDED"
    NAMED = "NAMED"
    UNRESOLVED = "UNRESOLVED"
    UNDISCLOSED = "UNDISCLOSED"


class DisclosureStance(str, Enum):
    """Whether the record's material is under a stated withholding.

    ``OPEN`` means no withholding is recorded — a statement about the ledger,
    never a claim that disclosure is complete or authorized.
    """

    OPEN = "OPEN"
    WITHHELD = "WITHHELD"


class TemporalStatus(str, Enum):
    """How current the recorded observation is under the record's horizon.

    ``UNDATED`` covers every observation without a usable ISO date — absent,
    non-string object, unreadable, or future-dated — exactly the set the
    date-resolution rule excludes from staleness accounting. For states other
    than ``NAMED`` the assessor does not decay on staleness; there the facet
    is descriptive age accounting only, never a rewrite of the state.
    """

    CURRENT = "CURRENT"
    STALE = "STALE"
    UNDATED = "UNDATED"


@dataclass(frozen=True)
class WitnessFacets:
    """One finding's state, factored into its three recorded dimensions."""

    record_id: str
    settlement: EpistemicSettlement
    disclosure: DisclosureStance
    temporality: TemporalStatus


def project_facets(facets: WitnessFacets) -> AbsenceState:
    """Project factored facets back onto the single caution-ordered state.

    The rule restates the shipped contract: a withholding outranks
    everything; an absent recording stays ``NOT_RECORDED``; a stale naming is
    reported ``UNRESOLVED`` (the decay rule, recovered here as a projection
    rather than a rewrite); otherwise the settlement carries through. The one
    combination with no recorded meaning — ``UNDISCLOSED`` settlement with an
    ``OPEN`` stance — fails closed, because a hidden settlement without a
    stated withholding is not a state this ledger can have recorded.
    """

    if facets.disclosure is DisclosureStance.WITHHELD:
        return AbsenceState.WITHHELD
    if facets.settlement is EpistemicSettlement.UNDISCLOSED:
        raise ValueError(
            "UNDISCLOSED settlement without a WITHHELD stance is not a "
            "recordable combination"
        )
    if facets.settlement is EpistemicSettlement.NOT_RECORDED:
        return AbsenceState.NOT_RECORDED
    if facets.settlement is EpistemicSettlement.UNRESOLVED:
        return AbsenceState.UNRESOLVED
    if facets.temporality is TemporalStatus.STALE:
        return AbsenceState.UNRESOLVED
    return AbsenceState.NAMED


def _temporality(
    finding: AbsenceFinding, record: AbsenceRecord, review_date: date
) -> TemporalStatus:
    """Age the finding's recorded date under the single date-resolution rule."""

    observed, _issue = usable_observation_date(finding.observed_on, review_date)
    if observed is None:
        return TemporalStatus.UNDATED
    age_days = (review_date - observed).days
    if age_days > record.review_horizon_days:
        return TemporalStatus.STALE
    return TemporalStatus.CURRENT


def finding_facets(
    finding: AbsenceFinding,
    record: AbsenceRecord,
    review_date: str | date,
) -> WitnessFacets:
    """Derive the three facets one assessed finding actually recorded.

    The derivation reads only data the assessor wrote: the state, the
    retained ``observed_on``, and — to separate an asserted open question
    from a naming that decayed — membership of the pinned ``REASON_UNRESOLVED``
    constant in the reasons trail, the same string the manuscript quotes
    verbatim. A finding whose reasons contradict its dates (an undecayed
    ``UNRESOLVED`` with no asserted-unresolved reason and no stale date) did
    not come from this package's assessor, and the derivation fails closed
    rather than guessing.
    """

    if finding.record_id != record.id:
        raise ValueError(
            f"finding names record {finding.record_id!r} but the supplied "
            f"record is {record.id!r}"
        )
    resolved = coerce_date(review_date, "review_date")
    temporality = _temporality(finding, record, resolved)
    if finding.state is AbsenceState.NOT_RECORDED:
        return WitnessFacets(
            finding.record_id,
            EpistemicSettlement.NOT_RECORDED,
            DisclosureStance.OPEN,
            TemporalStatus.UNDATED,
        )
    if finding.state is AbsenceState.WITHHELD:
        return WitnessFacets(
            finding.record_id,
            EpistemicSettlement.UNDISCLOSED,
            DisclosureStance.WITHHELD,
            temporality,
        )
    if finding.state is AbsenceState.NAMED:
        return WitnessFacets(
            finding.record_id,
            EpistemicSettlement.NAMED,
            DisclosureStance.OPEN,
            temporality,
        )
    # UNRESOLVED: either asserted by an observer, or a naming that decayed.
    if REASON_UNRESOLVED in finding.reasons:
        return WitnessFacets(
            finding.record_id,
            EpistemicSettlement.UNRESOLVED,
            DisclosureStance.OPEN,
            temporality,
        )
    if temporality is not TemporalStatus.STALE:
        raise ValueError(
            f"finding for {finding.record_id!r} is UNRESOLVED without an "
            "asserted-unresolved reason or a stale date; it cannot have come "
            "from this assessor and its facets are not derivable"
        )
    return WitnessFacets(
        finding.record_id,
        EpistemicSettlement.NAMED,
        DisclosureStance.OPEN,
        TemporalStatus.STALE,
    )


def report_facets(
    report: WhiteReport,
    records: Iterable[AbsenceRecord] = WHITE_RECORDS,
) -> tuple[WitnessFacets, ...]:
    """Factor every finding in a report, in the report's registry order.

    The report's own ``review_date`` anchors the temporal facet, so a report
    read back tomorrow factors exactly as it scored today.
    """

    records_by_id = {record.id: record for record in records}
    facets: list[WitnessFacets] = []
    for finding in report.findings:
        record = records_by_id.get(finding.record_id)
        if record is None:
            raise ValueError(
                f"finding references unknown record id {finding.record_id!r}"
            )
        facets.append(finding_facets(finding, record, report.review_date))
    return tuple(facets)


__all__ = [
    "DisclosureStance",
    "EpistemicSettlement",
    "TemporalStatus",
    "WitnessFacets",
    "finding_facets",
    "project_facets",
    "report_facets",
]
