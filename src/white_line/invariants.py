"""Structural soundness checks over the White Line absence ledger.

Pure-compute checks (no I/O) that validate the *shape* of the registry
rather than any single assessment. Each check returns a
:class:`LedgerCheck` with a name, a pass flag, and a human-readable detail;
``all_ledger_checks`` runs the whole battery and ``ledger_sound`` collapses
it to a boolean.

The companion test suite exercises detection: for every check it plants a
defined defective registry and asserts the check fails on it, while also
asserting the check passes on the real registry. A check that has never seen a
bad input does not count as protection against that defect class.

The digest consulted here is a change-review/drift instrument for the
ledger's own content; it has no security or safety semantics.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .model import AbsenceKind, AbsenceRecord
from .registry import WHITE_RECORDS
from .serialization import canonical_registry, registry_digest

_SLUG = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

_REQUIRED_TEXT_FIELDS = ("id", "title", "description", "prompt")


@dataclass(frozen=True)
class LedgerCheck:
    """One structural check outcome."""

    name: str
    passed: bool
    detail: str


def ids_are_distinct(records: tuple[AbsenceRecord, ...]) -> LedgerCheck:
    """No two records may share an id; a duplicate makes findings ambiguous."""

    ids = [record.id for record in records]
    duplicates = sorted({repr(item) for item in ids if ids.count(item) > 1})
    return LedgerCheck(
        "ids_are_distinct",
        not duplicates,
        "ok" if not duplicates else f"duplicate record ids: {duplicates}",
    )


def ids_are_canonical_slugs(records: tuple[AbsenceRecord, ...]) -> LedgerCheck:
    """Every id must be a lowercase hyphenated slug — the reviewed spelling."""

    bad = [
        repr(record.id)
        for record in records
        if not isinstance(record.id, str) or not _SLUG.fullmatch(record.id)
    ]
    return LedgerCheck(
        "ids_are_canonical_slugs",
        not bad,
        "ok" if not bad else f"non-canonical record ids: {bad}",
    )


def fields_are_inhabited(records: tuple[AbsenceRecord, ...]) -> LedgerCheck:
    """id, title, description, and prompt must be non-blank strings.

    A record with a blank prompt gives a reviewer nothing to sit with; a
    blank description records nothing at all.
    """

    bad: list[str] = []
    for record in records:
        for field_name in _REQUIRED_TEXT_FIELDS:
            value = getattr(record, field_name)
            if not isinstance(value, str) or not value.strip():
                bad.append(f"{record.id!r}.{field_name}")
    return LedgerCheck(
        "fields_are_inhabited",
        not bad,
        "ok" if not bad else f"blank or non-string fields: {bad}",
    )


def kinds_are_valid_and_covered(records: tuple[AbsenceRecord, ...]) -> LedgerCheck:
    """Every kind must be a real AbsenceKind, and every kind must appear.

    Frozen dataclasses do not type-check their fields, so a bare string can
    impersonate a kind. And a ledger with no contemplative (or epistemic, or
    ethical) records has silently lost a whole layer of absence.
    """

    invalid = [
        repr(record.id)
        for record in records
        if not isinstance(record.kind, AbsenceKind)
    ]
    present = {
        record.kind for record in records if isinstance(record.kind, AbsenceKind)
    }
    missing = sorted(kind.value for kind in AbsenceKind if kind not in present)
    ok = not invalid and not missing
    return LedgerCheck(
        "kinds_are_valid_and_covered",
        ok,
        "ok" if ok else f"untyped kinds on: {invalid}; uncovered kinds: {missing}",
    )


def horizons_are_positive(records: tuple[AbsenceRecord, ...]) -> LedgerCheck:
    """Review horizons must be positive integers.

    A zero or negative horizon makes every dated naming instantly stale, and
    a non-integer horizon breaks staleness arithmetic downstream.
    """

    bad = [
        f"{record.id!r}={record.review_horizon_days!r}"
        for record in records
        if isinstance(record.review_horizon_days, bool)
        or not isinstance(record.review_horizon_days, int)
        or record.review_horizon_days <= 0
    ]
    return LedgerCheck(
        "horizons_are_positive",
        not bad,
        "ok" if not bad else f"non-positive or non-integer horizons: {bad}",
    )


def serialization_is_stable(records: tuple[AbsenceRecord, ...]) -> LedgerCheck:
    """The canonical form must build, parse as JSON, and digest order-free.

    If two records shared an id, the id-sorted canonical payload would keep
    input order and the digest would depend on record order — silent drift a
    stored manifest could no longer catch.
    """

    try:
        json.loads(canonical_registry(tuple(records)))
        forward = registry_digest(tuple(records))
        backward = registry_digest(tuple(reversed(tuple(records))))
    except (AttributeError, TypeError, ValueError) as exc:
        return LedgerCheck(
            "serialization_is_stable", False, f"canonical form is unbuildable: {exc}"
        )
    if forward != backward:
        return LedgerCheck(
            "serialization_is_stable", False, "digest depends on record order"
        )
    return LedgerCheck("serialization_is_stable", True, "ok")


_CHECKS = (
    ids_are_distinct,
    ids_are_canonical_slugs,
    fields_are_inhabited,
    kinds_are_valid_and_covered,
    horizons_are_positive,
    serialization_is_stable,
)


def all_ledger_checks(
    records: tuple[AbsenceRecord, ...] = WHITE_RECORDS,
) -> tuple[LedgerCheck, ...]:
    """Run every structural check over ``records``."""

    frozen = tuple(records)
    return tuple(check(frozen) for check in _CHECKS)


def ledger_sound(records: tuple[AbsenceRecord, ...] = WHITE_RECORDS) -> bool:
    """True iff every structural check passes on ``records``."""

    return all(check.passed for check in all_ledger_checks(records))


@dataclass(frozen=True)
class DefectProbe:
    """One structural check shown rejecting the defect it guards against.

    ``rejected_detail`` is the detail string the check returned when it was run
    over a registry carrying the planted defect, not a description written by
    hand. ``also_failed`` names the other checks the same registry trips, which
    is information rather than noise: a defect that is visible to two checks is
    a defect two checks would catch.
    """

    check_name: str
    defect: str
    live_detail: str
    rejected_detail: str
    also_failed: tuple[str, ...]


def _replace(
    records: tuple[AbsenceRecord, ...], index: int, **changes: object
) -> tuple[AbsenceRecord, ...]:
    """Return ``records`` with one record's fields overridden.

    ``dataclasses.replace`` would type-check nothing either, but it also
    refuses a field that is not declared. Building the record positionally
    keeps the planted defects able to carry deliberately wrong runtime types,
    which is the whole point of the checks that look for them.
    """

    original = records[index]
    fields: dict[str, object] = {
        "id": original.id,
        "title": original.title,
        "kind": original.kind,
        "description": original.description,
        "prompt": original.prompt,
        "review_horizon_days": original.review_horizon_days,
    }
    fields.update(changes)
    planted = AbsenceRecord(**fields)  # type: ignore[arg-type]
    return records[:index] + (planted,) + records[index + 1 :]


def defect_registries(
    records: tuple[AbsenceRecord, ...] = WHITE_RECORDS,
) -> tuple[tuple[str, str, tuple[AbsenceRecord, ...]], ...]:
    """Return one planted-defect registry per check, in check order.

    Each entry is the name of the check the defect targets, a short description
    of what was planted, and the defective registry itself. The two
    serialization entries are deliberately different: an exactly duplicated
    record leaves the id-sorted payload unchanged and so trips only the
    distinct-id check, while a duplicated *id* over differing content makes the
    payload depend on input order and trips the digest as well.
    """

    return (
        (
            "ids_are_distinct",
            "record 2 is an exact copy of record 1, so one id names two entries",
            records[:1] + (records[0],) + records[2:],
        ),
        (
            "ids_are_canonical_slugs",
            "record 1's id is written in the unreviewed spelling 'Unobserved_Dependency'",
            _replace(records, 0, id="Unobserved_Dependency"),
        ),
        (
            "fields_are_inhabited",
            "record 1's reviewer prompt is blank, so a reviewer is given nothing to sit with",
            _replace(records, 0, prompt="   "),
        ),
        (
            "kinds_are_valid_and_covered",
            "record 1's kind is the bare string 'EPISTEMIC', which a frozen dataclass accepts",
            _replace(records, 0, kind="EPISTEMIC"),
        ),
        (
            "horizons_are_positive",
            "record 1's review horizon is 0 days, which makes every dated naming instantly stale",
            _replace(records, 0, review_horizon_days=0),
        ),
        (
            "serialization_is_stable",
            "records 1 and 2 share an id but differ in content, so the digest follows input order",
            _replace(records, 1, id=records[0].id),
        ),
    )


def invariant_defect_battery(
    records: tuple[AbsenceRecord, ...] = WHITE_RECORDS,
    registries: tuple[tuple[str, str, tuple[AbsenceRecord, ...]], ...] | None = None,
) -> tuple[DefectProbe, ...]:
    """Run every check over the live registry and over its planted defect.

    This is the executable form of the manuscript's defect-detection claim. It
    is not a test helper: a figure and the release report both read it, so the
    claim they display is the result of running the checks rather than a
    sentence about them.

    Args:
        records: The registry the checks must pass on.
        registries: Check name, defect description, and defective registry
            triples, defaulting to ``defect_registries(records)``. Supplying a
            battery whose defect does not trip its check is how the guards
            below are shown to reject.

    Raises:
        ValueError: If the live registry fails any check, if a targeted check
            passes on the registry built to defeat it, or if the battery does
            not cover every check exactly once and in order. A battery that
            silently skipped a check would make the claim vacuous for it.
    """

    live = {check.name: check for check in all_ledger_checks(records)}
    unsound = sorted(name for name, check in live.items() if not check.passed)
    if unsound:
        raise ValueError(f"the live registry already fails {unsound}")
    probes: list[DefectProbe] = []
    for target, defect, planted in (
        defect_registries(records) if registries is None else registries
    ):
        outcomes = {check.name: check for check in all_ledger_checks(planted)}
        if target not in outcomes:
            raise ValueError(f"{target!r} is not a structural check")
        if outcomes[target].passed:
            raise ValueError(
                f"{target!r} passed on the registry planted to defeat it: {defect}"
            )
        probes.append(
            DefectProbe(
                target,
                defect,
                live[target].detail,
                outcomes[target].detail,
                tuple(
                    sorted(
                        name
                        for name, check in outcomes.items()
                        if not check.passed and name != target
                    )
                ),
            )
        )
    expected = tuple(check.__name__ for check in _CHECKS)
    if tuple(probe.check_name for probe in probes) != expected:
        raise ValueError(
            "the defect battery must cover every structural check, in order"
        )
    return tuple(probes)
