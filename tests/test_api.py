"""Public API surface, the models alias, and positional call forms."""

import white_line
from white_line.models import (
    AbsenceKind as AliasKind,
    AbsenceRecord as AliasRecord,
)
from white_line.model import AbsenceKind, AbsenceRecord


def test_every_declared_export_is_importable() -> None:
    for name in white_line.__all__:
        assert getattr(white_line, name) is not None


def test_models_module_is_a_public_alias() -> None:
    """The public alias exports the same names as the model package.

    Comparing the two ``__all__`` lists is not enough on its own: the alias
    listed ``SET_ASIDE_CODES`` without importing it, so the lists matched while
    ``from white_line.models import SET_ASIDE_CODES`` raised. Every declared
    name is therefore resolved on both modules and checked to be the same
    object.
    """

    assert AliasKind is AbsenceKind
    assert AliasRecord is AbsenceRecord
    assert white_line.models.__all__ == white_line.model.__all__
    assert white_line.models.__all__, "the alias must export something"
    for name in white_line.models.__all__:
        assert hasattr(white_line.models, name), f"{name} is declared but absent"
        assert getattr(white_line.models, name) is getattr(white_line.model, name)


def test_positional_assess_absence_call_form() -> None:
    """A positional records argument still yields one finding per record."""

    report = white_line.assess_absence((), white_line.WHITE_RECORDS)
    assert len(report.findings) == len(white_line.WHITE_RECORDS)
    assert all(finding.reasons for finding in report.findings)
