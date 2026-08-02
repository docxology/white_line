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


def test_architecture_table_names_resolve_at_the_package_root() -> None:
    """`docs/architecture.md` claims the root re-exports the whole surface.

    The claim was prose only, and it had already drifted: five names the
    module table lists — `EXPIRY_AS_OF`, `expiry_observations`,
    `expiry_report`, `intake_reachability_battery`, and
    `LEDGER_VERSION_DIGEST` — were absent from the root while the sentence
    below the table said every one was importable. This binds the sentence to
    the table it summarises, so adding a name to the table without exporting
    it fails here rather than in a reader's REPL.
    """

    import re
    from pathlib import Path

    table = [
        line
        for line in (
            Path(__file__).resolve().parents[1] / "docs" / "architecture.md"
        )
        .read_text(encoding="utf-8")
        .splitlines()
        if line.startswith("| `")
    ]
    assert table, "the architecture module table must not be empty"
    names = sorted(
        {
            token
            for line in table
            for token in re.findall(r"`([^`]+)`", line)
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token)
        }
    )
    assert len(names) > 30, f"the scan set collapsed to {len(names)} names"
    missing = [name for name in names if not hasattr(white_line, name)]
    assert not missing, f"named in docs/architecture.md but not at the root: {missing}"
    undeclared = [name for name in names if name not in white_line.__all__]
    assert not undeclared, f"importable but absent from __all__: {undeclared}"
