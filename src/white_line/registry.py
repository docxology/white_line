"""The versioned White Line absence registry.

Eleven records across the three kinds of absence. The registry is finite and
deliberate: each record names one bounded category of gap, restraint, or
negative space, together with the reviewer's question (``prompt``) and how
long a dated naming stays fresh (``review_horizon_days``).
"""

from __future__ import annotations

from .model import AbsenceKind, AbsenceRecord

WHITE_RECORDS: tuple[AbsenceRecord, ...] = (
    # Epistemic absence: what is unknown, unobserved, or unquantified.
    AbsenceRecord(
        "unobserved-dependency",
        "Unobserved dependency",
        AbsenceKind.EPISTEMIC,
        "A condition, dataset, actor, or system dependency has not been observed.",
        "Which inputs has no one actually looked at?",
        90,
    ),
    AbsenceRecord(
        "unmeasured-uncertainty",
        "Unmeasured uncertainty",
        AbsenceKind.EPISTEMIC,
        "A reported result carries no stated error, confidence, or variance, so its precision is unknown.",
        "What would change if the error bars turned out to be wide?",
        120,
    ),
    AbsenceRecord(
        "missing-null-results",
        "Missing null results",
        AbsenceKind.EPISTEMIC,
        "Failed attempts and dead ends that shaped the work are absent from the record.",
        "Which failures taught the most, and where are they written down?",
        180,
    ),
    AbsenceRecord(
        "unasked-question",
        "Unasked question",
        AbsenceKind.EPISTEMIC,
        "A question that would materially test the work has not been posed.",
        "What question is being avoided because the answer could be costly?",
        90,
    ),
    # Ethical restraint: what is withheld, unrepresented, or uncredited.
    AbsenceRecord(
        "withheld-material",
        "Withheld material",
        AbsenceKind.ETHICAL,
        "Material is intentionally not disclosed because disclosure could violate consent, safety, or a duty of care.",
        "What duty of care keeps this closed, and who reviews that boundary?",
        180,
    ),
    AbsenceRecord(
        "silenced-perspective",
        "Unrepresented perspective",
        AbsenceKind.ETHICAL,
        "A person or perspective affected by the work is not represented in the available account.",
        "Who bears the consequences of this work but has no voice in this account?",
        120,
    ),
    AbsenceRecord(
        "uncredited-labor",
        "Uncredited labor",
        AbsenceKind.ETHICAL,
        "Labor, care, or prior art that made the work possible is not credited in the account.",
        "Whose work is load-bearing here without being named?",
        180,
    ),
    AbsenceRecord(
        "unacknowledged-limit",
        "Unacknowledged limitation",
        AbsenceKind.ETHICAL,
        "A known limitation that affects people who rely on the work is not stated where they would see it.",
        "Where would a reader first need this caveat, and is it there?",
        90,
    ),
    # Contemplative space: what is left open on purpose.
    AbsenceRecord(
        "negative-space",
        "Contemplative negative space",
        AbsenceKind.CONTEMPLATIVE,
        "The work leaves room for what cannot be usefully named, measured, or possessed as a claim.",
        "What is this work deliberately leaving open rather than claiming?",
        365,
    ),
    AbsenceRecord(
        "fallow-ground",
        "Fallow ground",
        AbsenceKind.CONTEMPLATIVE,
        "A line of work is deliberately left unworked for a season so that it can rest and ripen.",
        "What is being left unworked right now, and until when?",
        365,
    ),
    AbsenceRecord(
        "ineffable-remainder",
        "Ineffable remainder",
        AbsenceKind.CONTEMPLATIVE,
        "What the work points toward exceeds what its language can carry; the remainder is left unsaid rather than approximated.",
        "What is tempting to over-state simply to have said something?",
        365,
    ),
)


def record_ids() -> tuple[str, ...]:
    """Return registry record ids in registry order."""

    return tuple(record.id for record in WHITE_RECORDS)


def records_by_kind() -> dict[AbsenceKind, tuple[AbsenceRecord, ...]]:
    """Partition the registry by absence kind; every kind is a key."""

    grouped: dict[AbsenceKind, tuple[AbsenceRecord, ...]] = {
        kind: () for kind in AbsenceKind
    }
    for record in WHITE_RECORDS:
        grouped[record.kind] = grouped[record.kind] + (record,)
    return grouped
