"""Registry shape: counts, ordering, kind coverage, and versioning."""

from importlib.metadata import version as installed_version
from pathlib import Path
import re

from white_line.figures.legibility import manuscript_dir
from white_line import (
    LEDGER_VERSION,
    WHITE_RECORDS,
    AbsenceKind,
    __version__,
    record_ids,
    records_by_kind,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_registry_has_eleven_records_covering_every_kind() -> None:
    assert len(WHITE_RECORDS) == 11
    assert {record.kind for record in WHITE_RECORDS} == set(AbsenceKind)


def test_record_ids_are_unique_and_in_registry_order() -> None:
    ids = record_ids()
    assert len(ids) == len(set(ids))
    assert ids == tuple(record.id for record in WHITE_RECORDS)


def test_records_by_kind_partitions_the_registry() -> None:
    grouped = records_by_kind()
    assert set(grouped) == set(AbsenceKind)
    regrouped = [record for kind in AbsenceKind for record in grouped[kind]]
    assert sorted(record.id for record in regrouped) == sorted(record_ids())
    assert len(grouped[AbsenceKind.EPISTEMIC]) == 4
    assert len(grouped[AbsenceKind.ETHICAL]) == 4
    assert len(grouped[AbsenceKind.CONTEMPLATIVE]) == 3


def test_every_record_carries_a_prompt_and_positive_horizon() -> None:
    for record in WHITE_RECORDS:
        assert record.prompt.strip()
        assert record.review_horizon_days > 0


def test_version_markers_are_exposed() -> None:
    assert LEDGER_VERSION
    config = (manuscript_dir(PROJECT_ROOT) / "config.yaml").read_text(
        encoding="utf-8"
    )
    paper_version = re.search(r'^  version: "([^"]+)"$', config, re.MULTILINE)
    assert paper_version is not None
    assert paper_version.group(1) == __version__
    assert installed_version("white_line") == __version__
