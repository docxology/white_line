"""Re-derive every number the manuscript states from the code that produces it.

White Line's manuscript assertions used to be lexical: a substring check for
``"seven-input"``, a check that a helper name is mentioned. Those pass while a
table drifts. They did: the intake table in ``04b_distributional_views.md``
listed seven of the eight ``IntakeCode`` members under prose promising that
"a zero is reported, never omitted", and no test read the table at all.

Every test below parses the manuscript and compares each cell against a fresh
computation. A test that asserted a literal would be no better than the prose
it checks, so nothing here hard-codes an expected count; the expectations are
computed from ``WHITE_RECORDS``, ``events_tally``, ``coverage_matrix``, and the
live enumerations. Each parser is paired with a positive control that feeds it
a drifted table and asserts the comparison fails.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from white_line import (
    WHITE_RECORDS,
    AbsenceKind,
    AbsenceState,
    IntakeCode,
    coverage_matrix,
    decay_timeline,
    decay_transition_offsets,
    events_tally,
    reconciliation_matrix,
    records_by_kind,
    worked_intake_observations,
    worked_report,
)
from white_line.analysis import ASSERTABLE_STATES
from white_line.figures.legibility import manuscript_dir
from white_line.formalism import split_citations

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = manuscript_dir(PROJECT_ROOT)

#: English spellings for the small counts this manuscript writes out in words.
#: This is a spelling table, not an expectation: every count compared against
#: the manuscript below is computed from the package first and only then
#: rendered through this map.
_NUMBER_WORDS = {
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    11: "eleven",
}


def _spell(count: int) -> str:
    """Return the manuscript's spelling of ``count``.

    Raises:
        AssertionError: If the count has no spelling. A silent numeric
            fallback would let a re-derived count match a table that spells
            its numbers, hiding the drift these tests exist to catch.
    """

    assert count in _NUMBER_WORDS, f"no spelling recorded for {count}"
    return _NUMBER_WORDS[count]


def _read(name: str) -> str:
    """Return one manuscript file's text."""

    return (MANUSCRIPT / name).read_text(encoding="utf-8")


def _table_rows(text: str, first_cell: str) -> list[list[str]]:
    """Return the body rows of the markdown table whose first data cell matches.

    Args:
        text: The manuscript file's full text.
        first_cell: A substring identifying the table's first data row.

    Returns:
        One list of stripped cell strings per body row.

    Raises:
        AssertionError: If no table contains a row starting with ``first_cell``.
            An empty scan set would make every assertion below vacuous.
    """

    lines = text.splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith("|") and first_cell in line.split("|")[1]
        ),
        None,
    )
    assert start is not None, f"no table row containing {first_cell!r}"
    rows: list[list[str]] = []
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if set("".join(cells)) <= {"-", ":", " "}:
            continue
        rows.append(cells)
    assert rows, "table body is empty"
    return rows


def _strip_markup(cell: str) -> str:
    """Return a table cell without backticks or bold markers."""

    return cell.replace("`", "").replace("*", "").strip()


def parse_intake_table(text: str) -> dict[str, int]:
    """Return the manuscript's intake table as a code-to-count mapping."""

    return {
        _strip_markup(row[0]): int(_strip_markup(row[1]))
        for row in _table_rows(text, "NON_ITERABLE_INPUT")
    }


def parse_coverage_table(text: str) -> tuple[dict[str, dict[str, int]], dict[str, int]]:
    """Return the coverage table's cells and its stated column sums."""

    rows = _table_rows(text, "EPISTEMIC")
    header = next(
        line
        for line in text.splitlines()
        if line.startswith("| Kind") and "NAMED" in line
    )
    columns = [_strip_markup(cell) for cell in header.strip().strip("|").split("|")][1:]
    cells: dict[str, dict[str, int]] = {}
    column_sums: dict[str, int] = {}
    for row in rows:
        label = _strip_markup(row[0])
        values = [int(_strip_markup(cell)) for cell in row[1:]]
        if label == "Column sum":
            column_sums = dict(zip(columns, values, strict=True))
        else:
            cells[label] = dict(zip(columns, values, strict=True))
    return cells, column_sums


# --------------------------------------------------------------------------- #
# The intake table (the drift this module exists to prevent)
# --------------------------------------------------------------------------- #
def test_intake_table_has_one_row_per_intake_code_with_re_derived_counts() -> None:
    printed = parse_intake_table(_read("04b_distributional_views.md"))
    tally = events_tally(worked_report())
    expected = {code.value: count for code, count in tally.items()}
    assert printed == expected
    assert len(printed) == len(IntakeCode)
    assert list(printed) == [code.value for code in IntakeCode]


def test_the_intake_table_check_rejects_an_omitted_row() -> None:
    """Positive control: replay the exact drift that survived the old tests."""

    text = _read("04b_distributional_views.md")
    drifted = "\n".join(
        line
        for line in text.splitlines()
        if not line.startswith("| `UNDATED_OBJECT`")
    )
    assert drifted != text
    printed = parse_intake_table(drifted)
    tally = events_tally(worked_report())
    assert printed != {code.value: count for code, count in tally.items()}
    assert len(printed) == len(IntakeCode) - 1


def test_the_intake_table_check_rejects_a_wrong_count() -> None:
    """Positive control: a right-shaped table with one wrong number fails."""

    text = _read("04b_distributional_views.md")
    drifted = text.replace(
        "| `UNKNOWN_RECORD`      |     1 |", "| `UNKNOWN_RECORD`      |     4 |"
    )
    assert drifted != text
    tally = events_tally(worked_report())
    assert parse_intake_table(drifted) != {
        code.value: count for code, count in tally.items()
    }


def test_the_stated_event_and_note_totals_match_the_report() -> None:
    text = _read("04b_distributional_views.md")
    report = worked_report()
    total = sum(events_tally(report).values())
    assert total == len(report.intake_events) == len(report.intake_notes)
    # The sentence opens a paragraph, so the row count is capitalised there.
    assert (
        f"{_spell(len(IntakeCode))} rows for {_spell(len(IntakeCode))} codes, "
        f"{_spell(total)} events" in text.lower()
    )
    assert f"exactly {_spell(total)} matching intake\nnotes" in text


# --------------------------------------------------------------------------- #
# The coverage matrix
# --------------------------------------------------------------------------- #
def test_coverage_table_cells_re_derive_from_the_worked_report() -> None:
    cells, column_sums = parse_coverage_table(_read("04b_distributional_views.md"))
    matrix = coverage_matrix(worked_report())
    assert set(cells) == {kind.value for kind in AbsenceKind}
    for kind in AbsenceKind:
        row = cells[kind.value]
        for state in AbsenceState:
            assert row[state.value] == matrix[kind][state.value if False else state]
        assert row["Row sum"] == sum(matrix[kind].values())
    for state in AbsenceState:
        assert column_sums[state.value] == sum(
            matrix[kind][state] for kind in AbsenceKind
        )
    assert column_sums["Row sum"] == len(WHITE_RECORDS)


def test_the_coverage_table_check_rejects_a_drifted_cell() -> None:
    """Positive control: one altered cell breaks the comparison."""

    text = _read("04b_distributional_views.md")
    drifted = text.replace(
        "| `EPISTEMIC`     |       0 |            1 |",
        "| `EPISTEMIC`     |       2 |            1 |",
    )
    assert drifted != text
    cells, _sums = parse_coverage_table(drifted)
    matrix = coverage_matrix(worked_report())
    assert cells["EPISTEMIC"]["NAMED"] != matrix[AbsenceKind.EPISTEMIC][
        AbsenceState.NAMED
    ]


def test_the_stated_row_sums_match_the_registry_partition() -> None:
    text = _read("04b_distributional_views.md")
    grouped = records_by_kind()
    sizes = [len(grouped[kind]) for kind in AbsenceKind]
    stated = ", ".join(f"${size}$" for size in sizes)
    assert f"Row sums\n({stated})" in text


# --------------------------------------------------------------------------- #
# The formal-method section
# --------------------------------------------------------------------------- #
def test_registry_definition_counts_re_derive_from_the_registry() -> None:
    text = _read("03b_formalism.md")
    grouped = records_by_kind()
    assert f"R = (r_1, \\dots, r_{{{len(WHITE_RECORDS)}}})$ of ${len(WHITE_RECORDS)}$" in text
    partition = ", and ".join(
        [
            ", ".join(
                f"${len(grouped[kind])}$ {kind.value.lower()}"
                for kind in list(AbsenceKind)[:-1]
            ),
            f"${len(grouped[list(AbsenceKind)[-1]])}$ {list(AbsenceKind)[-1].value.lower()}",
        ]
    )
    assert f"exactly {partition} records" in text
    horizons = sorted({record.review_horizon_days for record in WHITE_RECORDS})
    assert "\\{" + ", ".join(str(days) for days in horizons) + "\\}" in text


def test_alphabet_sizes_re_derive_from_the_enumerations() -> None:
    text = _read("03b_formalism.md")
    assert f"|K| = {len(AbsenceKind)}$" in text
    assert f"|S| = {len(AbsenceState)}$" in text


def test_decay_transition_days_re_derive_from_a_real_sweep() -> None:
    """The four days quoted in Proposition C come from an executed sweep."""

    text = _read("03b_formalism.md")
    cohort = tuple(
        __import__("white_line").AbsenceObservation(
            record.id, AbsenceState.NAMED, "swept", "2026-01-01"
        )
        for record in WHITE_RECORDS
    )
    offsets = decay_transition_offsets(
        decay_timeline(cohort, "2026-01-01", "2027-02-05")
    )
    quoted = ", ".join(f"${offset}$" for offset in offsets[:-1])
    assert f"offsets {quoted}, and ${offsets[-1]}$" in text
    # The same crossings label the decay figure. Bind the two together so a
    # re-swept offset cannot update the prose and leave the plate behind.
    from white_line.figures.plates.distributions import decay_timeline as plate

    svg = plate()
    for offset in offsets:
        assert f"day {offset}" in svg


def test_named_step_sequence_in_proposition_c_matches_the_sweep() -> None:
    text = _read("03b_formalism.md")
    cohort = tuple(
        __import__("white_line").AbsenceObservation(
            record.id, AbsenceState.NAMED, "swept", "2026-01-01"
        )
        for record in WHITE_RECORDS
    )
    points = decay_timeline(cohort, "2026-01-01", "2027-02-05")
    steps: list[int] = []
    for point in points:
        count = point.tally[AbsenceState.NAMED]
        if not steps or steps[-1] != count:
            steps.append(count)
    # Built outside the f-string: a backslash inside an f-string expression is
    # a syntax error before Python 3.12, and this package targets 3.10.
    sequence = " \\to ".join(str(step) for step in steps)
    assert f"${sequence}$" in text


def test_the_ordered_pair_count_re_derives_from_the_matrix() -> None:
    text = _read("03b_formalism.md")
    pairs = len(reconciliation_matrix())
    assert len(ASSERTABLE_STATES) ** 2 == pairs
    assert f"${pairs}$ ordered pairs" in text
    assert f"all {_spell(pairs)} ordered pairs" in _read("04b_distributional_views.md")


def test_invariant_count_matches_the_check_battery() -> None:
    from white_line import all_ledger_checks

    text = _read("03b_formalism.md")
    checks = all_ledger_checks(WHITE_RECORDS)
    assert f"\\bigwedge_{{i=1}}^{{{len(checks)}}}" in text
    assert f"{_spell(len(checks))} pure-compute checks" in text
    for index in range(1, len(checks) + 1):
        assert f"**$P_{index}$" in text


def test_the_worked_input_count_in_prose_matches_the_shared_example() -> None:
    text = _read("04b_distributional_views.md")
    count = len(worked_intake_observations())
    assert f"following {_spell(count)} inputs" in text
    assert f"{_spell(count)}-input example" in text


# The claim-to-test binding table, and the formalism blocks it keys on, are
# checked in ``tests/test_formalism.py``: those rows are addressed by label
# rather than by a written-out number, so the parser that reads them belongs
# with the rest of the label machinery.


# --------------------------------------------------------------------------- #
# Figure captions must not name a colour the palette does not use
# --------------------------------------------------------------------------- #
#: Colour words the White Line palette does not contain. The palette is teal,
#: ochre, violet, sienna, charcoal, ink, and two paper tones; a caption using
#: any word below would send a reader looking for a colour that is not there.
#: ``blue`` is the case that mattered: the palette constant was named ``BLUE``
#: while holding a teal hex, which is exactly how a caption acquires a colour
#: word the artifact cannot support.
FORBIDDEN_COLOUR_WORDS = ("blue", "green", "red", "yellow", "pink", "grey", "gray")

#: Only caption and alt text is scanned. Body prose legitimately names the
#: sibling works Red Line, Black Line, and Golden Line, which are titles rather
#: than descriptions of any drawn artifact.
CAPTION_RE = re.compile(r"!\[(?P<caption>.+?)\]\((?:\./|\.\./)*output/figures/[^)]+\)", re.S)


def _colour_words(value: str) -> list[str]:
    """Return the forbidden colour words named in ``value``."""

    return [
        word
        for word in FORBIDDEN_COLOUR_WORDS
        if re.search(rf"\b{word}\b", value, re.I)
    ]


def test_no_figure_caption_names_a_colour_the_palette_does_not_use() -> None:
    """A caption naming an absent colour misdescribes the artifact."""

    from white_line.figures import FIGURE_PLATES

    offences: dict[str, list[str]] = {}
    for plate in FIGURE_PLATES:
        named = _colour_words(plate.caption) + _colour_words(plate.alt)
        if named:
            offences[plate.name] = named
    assert not offences, offences

    captions = [
        match.group("caption")
        for path in sorted(MANUSCRIPT.glob("*.md"))
        for match in CAPTION_RE.finditer(path.read_text(encoding="utf-8"))
    ]
    assert len(captions) == len(FIGURE_PLATES), "every plate must be embedded once"
    embedded = {
        caption: named for caption in captions if (named := _colour_words(caption))
    }
    assert not embedded, embedded


def test_the_colour_word_check_rejects_a_planted_colour_name() -> None:
    """Positive control: both halves of the scan reject a planted colour."""

    assert _colour_words("Three blue traces cross the open field.") == ["blue"]
    planted = (
        "![Three blue traces cross the open field.]"
        "(../output/figures/white_cover_art.png){#fig:x width=100%}"
    )
    found = [
        _colour_words(match.group("caption"))
        for match in CAPTION_RE.finditer(planted)
    ]
    assert found == [["blue"]]


# --------------------------------------------------------------------------- #
# Bibliography integrity in both directions
# --------------------------------------------------------------------------- #
def test_every_bibliography_key_is_cited_and_every_citation_is_in_the_bibliography() -> (
    None
):
    """Both directions, with formalism references partitioned out first.

    ``[@def:kinds]`` is a citation as far as pandoc's parser is concerned; the
    renderer's filter consumes it before the bibliography machinery sees it.
    The partition here is the filter's own — a prefix the manuscript declares
    for a formalism label is a formalism reference — so this check cannot start
    reporting a definition label as a missing bibliography entry.
    """

    from white_line.formalism import declared_prefixes, parse_blocks, read_manuscript

    bibliography = (MANUSCRIPT / "references.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@\w+\{\s*([^,\s]+)", bibliography))
    sources = read_manuscript(MANUSCRIPT)
    prose = "\n".join(sources[name] for name in sorted(sources))
    references, cited = split_citations(prose, declared_prefixes(parse_blocks(sources)))
    assert keys, "the bibliography must not be empty"
    assert references, "the manuscript must reference its own formalism blocks"
    assert sorted(keys - cited) == [], "bibliography entries never cited"
    assert sorted(cited - keys) == [], "citations with no bibliography entry"


def test_translated_sources_cite_the_edition_year_not_the_composition_year() -> None:
    """A composition year paired with a modern publisher renders incoherently."""

    bibliography = (MANUSCRIPT / "references.bib").read_text(encoding="utf-8")
    entries = re.split(r"\n(?=@)", bibliography)
    for entry in entries:
        if "translator" not in entry:
            continue
        year = int(re.search(r"year = \{(\d+)\}", entry).group(1))
        assert year >= 1900, entry.splitlines()[0]


@pytest.mark.parametrize("name", sorted(path.name for path in MANUSCRIPT.glob("*.md")))
def test_no_manuscript_file_carries_an_unrendered_placeholder(name: str) -> None:
    text = _read(name)
    assert "TODO" not in text
    assert "{{" not in text
