"""Bind ``data/formalism_claim_ledger.json`` to the manuscript and the package.

The external publication engine's evidence registry knows ``fig:``/``sec:``/
``tbl:``/``eq:``/``lst:`` label prefixes and treats every other ``[@x]`` as a
bibliography key, so a formalism reference is reported as an unsupported
citation unless the project declares it. ``data/formalism_claim_ledger.json``
is that declaration; this module re-derives the whole set from the manuscript
and the running package so a block added, renamed, or removed without the
ledger following fails here rather than surfacing as a red output-validation
report after a render.

Nothing is asserted that was not first executed: the declared labels are
parsed from the real manuscript, and the numeric rows are re-derived by
running ``project_facets`` over every settlement x disclosure-stance x
temporal-status combination. Negative controls prove each gate can fail.
"""

from __future__ import annotations

import json
import re
from itertools import product
from pathlib import Path

from white_line.figures.legibility import manuscript_dir
from white_line.facets import (
    DisclosureStance,
    EpistemicSettlement,
    TemporalStatus,
    WitnessFacets,
    project_facets,
)

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = manuscript_dir(ROOT)
LEDGER = ROOT / "data" / "formalism_claim_ledger.json"

#: A formalism block opener: ``::: {.definition #def:x title="X"}``.
_BLOCK = re.compile(r"^::: \{(?P<attrs>[^}]*)\}\s*$", re.M)
_LABEL = re.compile(r"#([a-z]+:[a-z0-9-]+)")
#: The reference syntax the engine's citation check sees.
_REFERENCE = re.compile(
    r"\[@((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-z0-9-]+)\]"
)


def _body_files() -> list[Path]:
    """Every manuscript body file except the preamble."""

    return [
        path
        for path in sorted(MANUSCRIPT.glob("*.md"))
        if path.name != "preamble.md"
    ]


def _declared_labels() -> set[str]:
    """Every formalism-block label declared anywhere in the manuscript."""

    labels: set[str] = set()
    for path in _body_files():
        for match in _BLOCK.finditer(path.read_text(encoding="utf-8")):
            label = _LABEL.search(match.group("attrs"))
            if label:
                labels.add(label.group(1))
    return labels


def _referenced_labels() -> set[str]:
    """Every ``[@prefix:label]`` formalism reference in the manuscript."""

    refs: set[str] = set()
    for path in _body_files():
        refs.update(_REFERENCE.findall(path.read_text(encoding="utf-8")))
    return refs


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _ledger_citations() -> set[str]:
    return {
        row["value"]
        for row in _ledger()["claims"]
        if row["kind"] == "citation"
    }


def _facet_projection_counts() -> tuple[int, int, int]:
    """Run the real projection over every combination; count outcomes."""

    combos = list(
        product(EpistemicSettlement, DisclosureStance, TemporalStatus)
    )
    projected = 0
    for settlement, stance, temporality in combos:
        facets = WitnessFacets(
            record_id="ledger-derivation",
            settlement=settlement,
            disclosure=stance,
            temporality=temporality,
        )
        try:
            project_facets(facets)
            projected += 1
        except Exception:
            pass
    return len(combos), projected, len(combos) - projected


# ------------------------------------------------------------------- gates


def test_every_declared_label_is_in_the_ledger() -> None:
    """A block declared in the manuscript must be declared to the engine too."""

    declared = _declared_labels()

    assert declared, "no labels declared; this gate would be vacuous"
    assert _ledger_citations() == declared, sorted(
        _ledger_citations() ^ declared
    )


def test_every_ledger_citation_is_a_declared_block() -> None:
    """The ledger cannot declare a label the manuscript does not carry."""

    assert _ledger_citations() <= _declared_labels(), sorted(
        _ledger_citations() - _declared_labels()
    )


def test_every_referenced_label_is_both_declared_and_ledgered() -> None:
    """A reference the prose makes resolves on both sides of the contract."""

    declared = _declared_labels()
    referenced = _referenced_labels()

    assert referenced, "no formalism references found; this gate would be vacuous"
    assert referenced <= declared, sorted(referenced - declared)
    assert referenced <= _ledger_citations(), sorted(
        referenced - _ledger_citations()
    )


def _evidence_path(source_path: str) -> Path:
    """Resolve a ledger evidence path against either manuscript layout.

    The manuscript lives under ``docs/manuscript/`` in the current tree and
    under the earlier ``manuscript/`` layout in previous checkouts; evidence
    rows recorded against either layout must resolve, so the same fallback
    ``white_line.figures.legibility.manuscript_dir`` applies is used here.
    """

    candidate = ROOT / source_path
    if candidate.is_file() or not source_path.startswith("manuscript/"):
        return candidate
    relocated = ROOT / "docs" / source_path
    return relocated


def test_every_ledger_source_path_exists() -> None:
    """A row pointing at a file that is not there is dead evidence."""

    for row in _ledger()["claims"]:
        assert _evidence_path(row["source_path"]).is_file(), row["claim_id"]
        assert row["freshness"] == "active", row["claim_id"]


def test_ledger_claim_ids_are_unique() -> None:
    rows = _ledger()["claims"]

    assert len({row["claim_id"] for row in rows}) == len(rows)


def test_number_rows_match_the_running_package() -> None:
    """The facet-lattice numbers are re-derived by running the package."""

    total, projected, failed = _facet_projection_counts()
    numbers = {
        row["claim_id"]: row["value"]
        for row in _ledger()["claims"]
        if row["kind"] == "number"
    }

    assert numbers["facets_total_combinations"] == total
    assert numbers["facets_project_combinations"] == projected
    assert numbers["facets_fail_closed_combinations"] == failed


# ------------------------------------------------------- negative controls


def test_negative_control_label_gap_fails(tmp_path: Path) -> None:
    """Removing a citation row must break the declared-labels gate."""

    ledger = _ledger()
    ledger["claims"] = [
        row for row in ledger["claims"] if row["value"] != "def:kinds"
    ]
    citations = {
        row["value"] for row in ledger["claims"] if row["kind"] == "citation"
    }

    assert citations != _declared_labels()


def test_negative_control_wrong_number_fails() -> None:
    """A restated (not derived) number must break the numeric gate."""

    ledger = _ledger()
    for row in ledger["claims"]:
        if row["claim_id"] == "facets_total_combinations":
            row["value"] = row["value"] + 1

    total, _projected, _failed = _facet_projection_counts()
    numbers = {
        row["claim_id"]: row["value"]
        for row in ledger["claims"]
        if row["kind"] == "number"
    }
    assert numbers["facets_total_combinations"] != total
