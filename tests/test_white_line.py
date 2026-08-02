from white_line import (
    AbsenceKind,
    AbsenceObservation,
    AbsenceState,
    WHITE_RECORDS,
    assess_absence,
    canonical_registry,
    record_ids,
    registry_digest,
)


def test_registry_is_unique_and_typed() -> None:
    assert len(record_ids()) == len(set(record_ids()))
    assert {record.kind for record in WHITE_RECORDS} == {
        AbsenceKind.EPISTEMIC,
        AbsenceKind.ETHICAL,
        AbsenceKind.CONTEMPLATIVE,
    }
    assert registry_digest(WHITE_RECORDS) == registry_digest(
        tuple(reversed(WHITE_RECORDS))
    )
    assert canonical_registry(WHITE_RECORDS)


def test_unrecorded_absence_is_not_recorded() -> None:
    report = assess_absence(())
    assert all(
        finding.state is AbsenceState.NOT_RECORDED for finding in report.findings
    )
    assert report.findings[0].kind is AbsenceKind.EPISTEMIC


def test_unresolved_and_withheld_stay_distinct() -> None:
    report = assess_absence(
        (
            AbsenceObservation("unobserved-dependency", AbsenceState.UNRESOLVED),
            AbsenceObservation(
                "withheld-material", AbsenceState.WITHHELD, "consent boundary"
            ),
        )
    )
    states = {finding.record_id: finding.state for finding in report.findings}
    assert states["unobserved-dependency"] is AbsenceState.UNRESOLVED
    assert states["withheld-material"] is AbsenceState.WITHHELD


def test_named_negative_space_does_not_become_a_causal_claim() -> None:
    report = assess_absence((AbsenceObservation("negative-space", AbsenceState.NAMED),))
    finding = next(
        item for item in report.findings if item.record_id == "negative-space"
    )
    assert finding.state is AbsenceState.NAMED
    assert "explicitly named" in finding.reasons[0]
