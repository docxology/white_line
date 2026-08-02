"""Invariant battery: pass on the real ledger, fail on planted defects.

Every check gets a proof-of-detection test: a registry with a planted defect
must make the check fail, and the real registry must make it pass. A green
check that never saw a bad input is not evidence of protection.
"""

import dataclasses

import pytest
from white_line import (
    WHITE_RECORDS,
    AbsenceKind,
    all_ledger_checks,
    defect_registries,
    fields_are_inhabited,
    horizons_are_positive,
    ids_are_canonical_slugs,
    ids_are_distinct,
    invariant_defect_battery,
    kinds_are_valid_and_covered,
    ledger_sound,
    serialization_is_stable,
)


def test_all_checks_pass_on_the_real_registry() -> None:
    results = all_ledger_checks(WHITE_RECORDS)
    assert all(result.passed for result in results), [
        (result.name, result.detail) for result in results if not result.passed
    ]
    assert {result.name for result in results} == {
        "ids_are_distinct",
        "ids_are_canonical_slugs",
        "fields_are_inhabited",
        "kinds_are_valid_and_covered",
        "horizons_are_positive",
        "serialization_is_stable",
    }
    assert all(result.detail == "ok" for result in results)


def test_battery_defaults_to_real_registry_and_ledger_sound_agrees() -> None:
    assert all_ledger_checks() == all_ledger_checks(WHITE_RECORDS)
    assert ledger_sound()
    planted = WHITE_RECORDS + (dataclasses.replace(WHITE_RECORDS[0]),)
    assert not ledger_sound(planted)


def test_ids_are_distinct_detects_a_duplicate_id() -> None:
    assert ids_are_distinct(WHITE_RECORDS).passed
    planted = WHITE_RECORDS + (
        dataclasses.replace(WHITE_RECORDS[0], title="Shadow copy"),
    )
    result = ids_are_distinct(planted)
    assert not result.passed
    assert "unobserved-dependency" in result.detail


def test_ids_are_canonical_slugs_detects_malformed_ids() -> None:
    assert ids_are_canonical_slugs(WHITE_RECORDS).passed
    bad_spelling = (
        dataclasses.replace(WHITE_RECORDS[0], id="Not A Slug!"),
    ) + WHITE_RECORDS[1:]
    assert not ids_are_canonical_slugs(bad_spelling).passed
    non_string = (dataclasses.replace(WHITE_RECORDS[0], id=42),) + WHITE_RECORDS[1:]
    assert not ids_are_canonical_slugs(non_string).passed


def test_fields_are_inhabited_detects_blank_and_non_string_fields() -> None:
    assert fields_are_inhabited(WHITE_RECORDS).passed
    blank_title = (dataclasses.replace(WHITE_RECORDS[0], title="   "),) + WHITE_RECORDS[
        1:
    ]
    result = fields_are_inhabited(blank_title)
    assert not result.passed
    assert ".title" in result.detail
    numeric_prompt = (dataclasses.replace(WHITE_RECORDS[0], prompt=7),) + WHITE_RECORDS[
        1:
    ]
    assert not fields_are_inhabited(numeric_prompt).passed


def test_kinds_are_valid_and_covered_detects_an_untyped_kind() -> None:
    assert kinds_are_valid_and_covered(WHITE_RECORDS).passed
    planted = (
        dataclasses.replace(WHITE_RECORDS[0], kind="EPISTEMIC"),
    ) + WHITE_RECORDS[1:]
    result = kinds_are_valid_and_covered(planted)
    assert not result.passed
    assert "untyped" in result.detail


def test_kinds_are_valid_and_covered_detects_a_lost_layer() -> None:
    gutted = tuple(
        record
        for record in WHITE_RECORDS
        if record.kind is not AbsenceKind.CONTEMPLATIVE
    )
    result = kinds_are_valid_and_covered(gutted)
    assert not result.passed
    assert "CONTEMPLATIVE" in result.detail


def test_horizons_are_positive_detects_bad_horizons() -> None:
    assert horizons_are_positive(WHITE_RECORDS).passed
    zero = (
        dataclasses.replace(WHITE_RECORDS[0], review_horizon_days=0),
    ) + WHITE_RECORDS[1:]
    assert not horizons_are_positive(zero).passed
    boolean = (
        dataclasses.replace(WHITE_RECORDS[0], review_horizon_days=True),
    ) + WHITE_RECORDS[1:]
    assert not horizons_are_positive(boolean).passed
    text = (
        dataclasses.replace(WHITE_RECORDS[0], review_horizon_days="90"),
    ) + WHITE_RECORDS[1:]
    assert not horizons_are_positive(text).passed


def test_serialization_is_stable_detects_an_unserializable_record() -> None:
    assert serialization_is_stable(WHITE_RECORDS).passed
    planted = (
        dataclasses.replace(WHITE_RECORDS[0], description=object()),
    ) + WHITE_RECORDS[1:]
    result = serialization_is_stable(planted)
    assert not result.passed
    assert "unbuildable" in result.detail


def test_serialization_is_stable_detects_an_order_dependent_digest() -> None:
    # Two records sharing an id: the id-sort is stable, so the canonical
    # payload keeps input order and the digest depends on record order.
    twin = dataclasses.replace(WHITE_RECORDS[0], title="Different twin")
    planted = WHITE_RECORDS + (twin,)
    result = serialization_is_stable(planted)
    assert not result.passed
    assert "order" in result.detail


# --------------------------------------------------------------------------- #
# The shipped battery, which the manuscript and a figure both read
# --------------------------------------------------------------------------- #
def test_the_defect_battery_rejects_every_planted_defect() -> None:
    """The claim that each check detects its defect is executed, not asserted.

    The per-check tests above plant a defect and inspect one check.
    ``invariant_defect_battery`` does the same thing as a shipped call, which
    is what the manuscript's defect-detection proposition and the invariant
    figure both display. Binding it here keeps that display honest: the battery
    refuses to return unless every targeted check rejected its own defect.
    """

    probes = invariant_defect_battery()
    assert [probe.check_name for probe in probes] == [
        result.name for result in all_ledger_checks(WHITE_RECORDS)
    ]
    for probe in probes:
        assert probe.live_detail == "ok", probe.check_name
        assert probe.rejected_detail != "ok", probe.check_name
        assert probe.defect, probe.check_name
        assert probe.check_name not in probe.also_failed


def test_the_battery_refuses_a_defect_its_check_does_not_catch() -> None:
    """Positive control: a registry that is not defective must not pass here.

    Without this the battery could silently accept a probe whose registry the
    check happily approves, and every row it drew would be a claim about
    nothing.
    """

    with pytest.raises(ValueError, match="passed on the registry planted"):
        invariant_defect_battery(
            registries=(
                ("ids_are_distinct", "no defect at all", WHITE_RECORDS),
            )
        )


def test_the_battery_refuses_an_incomplete_cover_of_the_checks() -> None:
    """A battery that skips a check would make the claim vacuous for it."""

    full = defect_registries()
    with pytest.raises(ValueError, match="every structural check, in order"):
        invariant_defect_battery(registries=full[:-1])


def test_the_battery_refuses_an_unknown_check_name() -> None:
    with pytest.raises(ValueError, match="not a structural check"):
        invariant_defect_battery(
            registries=(("no_such_check", "irrelevant", WHITE_RECORDS),)
        )


def test_the_battery_refuses_a_registry_that_is_already_unsound() -> None:
    """The live registry must pass before any planted defect means anything."""

    broken = (dataclasses.replace(WHITE_RECORDS[0], prompt=""),) + WHITE_RECORDS[1:]
    with pytest.raises(ValueError, match="already fails"):
        invariant_defect_battery(broken)


def test_every_planted_registry_is_actually_different_from_the_live_one() -> None:
    """A probe whose registry equals the real one would prove nothing.

    Compared by ``repr`` rather than by ``==``: ``AbsenceKind`` is a ``str``
    enum, so the bare string ``"EPISTEMIC"`` compares equal to the member it
    impersonates and an equality check would report the untyped-kind registry
    as unchanged. That is the same blind spot ``kinds_are_valid_and_covered``
    exists to close, and a test written with the blunter operator would have
    inherited it.
    """

    live = repr(WHITE_RECORDS)
    for name, _defect, planted in defect_registries():
        assert repr(planted) != live, name
