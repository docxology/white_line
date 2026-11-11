"""Bind the manuscript's formalism blocks to the code they describe.

Two families of check live here.

The first is structural, and it exists because auto-numbering can fail
silently. The renderer numbers a block only if it is written as a fenced Div,
resolves a reference only from a declared label, and leaves an undeclared
reference as literal ``[@label]`` markup in the PDF while still exiting zero.
A hand-written "Definition 4" is worse still: nothing renumbers it, so it goes
stale the moment a block is inserted above it and no tool ever says so. The
checks below refuse all three, and each is paired with a positive control that
plants the violation and asserts the check catches it.

The semantic checks exercise date branches, native reason coverage, the facet
projection domain, and factorization. Authored prose, copied source fields,
signatures, and incidental structural counts are not their test oracles.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from white_line import (
    SCORING_REASONS,
    WHITE_RECORDS,
    WORKED_AS_OF,
    AbsenceState,
    DisclosureStance,
    EpistemicSettlement,
    TemporalStatus,
    WitnessFacets,
    finding_facets,
    project_facets,
    scoring_branch_battery,
    usable_observation_date,
)
from white_line.figures.legibility import manuscript_dir
from white_line.formalism import (
    FORMALISM_PREFIXES,
    FORMALISM_TITLES,
    declared_prefixes,
    hand_written_numbers,
    parse_blocks,
    read_manuscript,
    split_citations,
    strip_code,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = manuscript_dir(PROJECT_ROOT)

SOURCES = read_manuscript(MANUSCRIPT)
BLOCKS = parse_blocks(SOURCES)
DECLARED_LABELS = frozenset(block.label for block in BLOCKS)
PROSE = "\n".join(SOURCES[name] for name in sorted(SOURCES))


# --------------------------------------------------------------------------- #
# Structural: labels, references, and the absence of hand-written numbers
# --------------------------------------------------------------------------- #
def test_the_manuscript_declares_formalism_blocks_at_all() -> None:
    """An empty scan set would make every check in this module vacuous."""

    assert BLOCKS, "the manuscript declares no formalism blocks"
    assert {block.kind for block in BLOCKS} <= set(FORMALISM_TITLES)


def test_every_formalism_block_carries_a_unique_prefixed_label() -> None:
    """A block with no label is numbered but can never be referenced."""

    unlabeled = [
        f"{block.source}:{block.printed}" for block in BLOCKS if not block.label
    ]
    assert not unlabeled, unlabeled
    wrong_prefix = [
        block.label
        for block in BLOCKS
        if not block.label.startswith(f"{FORMALISM_PREFIXES[block.kind]}:")
    ]
    assert not wrong_prefix, wrong_prefix
    labels = [block.label for block in BLOCKS]
    assert len(labels) == len(set(labels)), "duplicate formalism label"


def test_the_label_check_rejects_an_unlabeled_block() -> None:
    """Positive control: a block written without an identifier is caught."""

    planted = parse_blocks(
        {"planted.md": '::: {.definition title="Nameless"}\nBody.\n:::\n'}
    )
    assert len(planted) == 1
    assert planted[0].label == ""
    assert planted[0].printed == "Definition 1 (Nameless)"


def test_the_label_check_rejects_the_wrong_prefix_for_a_kind() -> None:
    """Positive control: a proposition labeled ``def:`` is caught."""

    planted = parse_blocks({"planted.md": "::: {.proposition #def:wrong}\nX.\n:::\n"})
    assert len(planted) == 1
    block = planted[0]
    assert not block.label.startswith(f"{FORMALISM_PREFIXES[block.kind]}:")


def test_every_formalism_reference_resolves_to_a_declared_block() -> None:
    """An unresolved reference ships as literal markup in every edition."""

    references, _keys = split_citations(PROSE, declared_prefixes(BLOCKS))
    assert references, "the manuscript makes no formalism references"
    dangling = sorted(
        reference
        for reference in references
        if reference not in DECLARED_LABELS
        and reference.partition(":")[0] not in {"sec", "fig"}
    )
    assert not dangling, dangling


def test_the_reference_check_rejects_a_dangling_label() -> None:
    """Positive control: a typo'd reference is caught, not passed through."""

    prefixes = declared_prefixes(BLOCKS)
    references, keys = split_citations(
        "By [@def:kindz] the registry is well formed [@haraway1988].", prefixes
    )
    assert references == frozenset({"def:kindz"})
    assert keys == frozenset({"haraway1988"})
    assert "def:kindz" not in DECLARED_LABELS


def test_no_manuscript_file_writes_a_formalism_number_by_hand() -> None:
    """The whole point of the fenced syntax is that no such literal exists."""

    offenses = {
        name: found
        for name, text in SOURCES.items()
        if (found := hand_written_numbers(text))
    }
    assert not offenses, offenses


def test_the_hand_written_number_check_rejects_a_planted_literal() -> None:
    """Positive control: prose numbers are caught, code samples are not."""

    assert hand_written_numbers("By Definition 4, the registry is finite.") == (
        "Definition 4",
    )
    assert hand_written_numbers("See Proposition B for the argument.") == (
        "Proposition B",
    )
    fenced = "```text\nProposition B\n```\nAnd nothing else.\n"
    assert hand_written_numbers(fenced) == ()
    assert hand_written_numbers("The token `Definition 4` is quoted.") == ()


def test_every_number_the_renderer_will_print_runs_from_one_per_kind() -> None:
    """Reproduce the filter's counter so the report can state real numbers."""

    seen: dict[str, list[int]] = {}
    for block in BLOCKS:
        if block.number is not None:
            seen.setdefault(block.kind, []).append(block.number)
    assert seen, "no numbered formalism blocks"
    for kind, numbers in seen.items():
        assert numbers == list(range(1, len(numbers) + 1)), kind


# --------------------------------------------------------------------------- #
# Semantic: independently exercised native behavior and calculations
# --------------------------------------------------------------------------- #
#: The date-resolution branches the definition states, as (raw value, whether a
#: date must come back, substring the returned note must contain).
DATE_BRANCHES = (
    (None, False, ""),
    ("", False, ""),
    (date(2026, 1, 5), False, "not an ISO date string"),
    ("not-a-date", False, "unreadable"),
    ("2027-01-01", False, "after the review date"),
    ("2026-06-01", True, ""),
)


def test_every_date_resolution_branch_matches_the_shared_helper() -> None:
    """Each branch the definition states is what the one implementation does."""

    review_date = date(2026, 7, 18)
    for raw, dated, note_fragment in DATE_BRANCHES:
        resolved, note = usable_observation_date(raw, review_date)
        assert (resolved is not None) is dated, raw
        assert note_fragment in note, raw
        if not note_fragment:
            assert note == "", raw


def test_the_date_branch_check_rejects_a_wrong_expectation() -> None:
    """Positive control: the branch table can fail, so passing means something."""

    resolved, note = usable_observation_date("2027-01-01", date(2026, 7, 18))
    assert resolved is None
    assert "unreadable" not in note


def test_scoring_reason_vocabulary_is_exercised_by_the_battery() -> None:
    """Every declared native scoring reason is exercised without prose matching."""

    produced: set[str] = set()
    for probe in scoring_branch_battery():
        produced.update(probe.finding.reasons)
    assert set(SCORING_REASONS) <= produced, sorted(set(SCORING_REASONS) - produced)


def test_the_projection_cell_counts_re_derive_from_the_code() -> None:
    """Exercise the complete facet domain, with one rejected pair per time state."""

    combinations = 0
    fail_closed = 0
    for settlement in EpistemicSettlement:
        for disclosure in DisclosureStance:
            for temporality in TemporalStatus:
                combinations += 1
                try:
                    project_facets(
                        WitnessFacets("probe", settlement, disclosure, temporality)
                    )
                except ValueError:
                    fail_closed += 1
    assert combinations == len(EpistemicSettlement) * len(DisclosureStance) * len(
        TemporalStatus
    )
    assert fail_closed == len(TemporalStatus)


def test_the_factorization_proposition_holds_over_a_live_battery() -> None:
    """Projecting the derived facets of every live finding recovers its state."""

    records_by_id = {record.id: record for record in WHITE_RECORDS}
    probes = scoring_branch_battery()
    assert probes, "the scoring battery must not be empty"
    decayed_branches = 0
    for probe in probes:
        facets = finding_facets(
            probe.finding, records_by_id[probe.finding.record_id], WORKED_AS_OF
        )
        assert project_facets(facets) is probe.finding.state, probe.branch
        if (
            facets.settlement is EpistemicSettlement.NAMED
            and facets.temporality is TemporalStatus.STALE
        ):
            decayed_branches += 1
            assert probe.finding.state is AbsenceState.UNRESOLVED, probe.branch
    # The decay branch is exercised, so the NAMED + STALE clause is not vacuous.
    assert decayed_branches > 0


def test_the_factorization_check_rejects_a_swapped_projection() -> None:
    """Positive control: the projection can disagree with a state, so agreement
    over the battery means something."""

    decayed = WitnessFacets(
        "probe",
        EpistemicSettlement.NAMED,
        DisclosureStance.OPEN,
        TemporalStatus.STALE,
    )
    assert project_facets(decayed) is not AbsenceState.NAMED
    assert project_facets(decayed) is AbsenceState.UNRESOLVED


# --------------------------------------------------------------------------- #
# The parser itself
# --------------------------------------------------------------------------- #
def test_an_unclosed_fence_is_reported_rather_than_guessed() -> None:
    with pytest.raises(ValueError, match="unclosed formalism fence"):
        parse_blocks({"planted.md": "::: {.definition #def:x}\nBody with no end.\n"})


def test_an_unnumbered_block_consumes_no_number() -> None:
    blocks = parse_blocks(
        {
            "planted.md": (
                "::: {.definition #def:a}\nOne.\n:::\n\n"
                '::: {.definition .unnumbered #def:b title="Aside"}\nTwo.\n:::\n\n'
                "::: {.definition #def:c}\nThree.\n:::\n"
            )
        }
    )
    assert [block.number for block in blocks] == [1, None, 2]
    assert blocks[1].printed == "Definition (Aside)"
    assert blocks[2].printed == "Definition 2"


def test_blocks_are_numbered_in_combined_document_order() -> None:
    """Sources are read in the order the renderer combines them."""

    blocks = parse_blocks(
        {
            "02_b.md": "::: {.proposition #prop:second}\nB.\n:::\n",
            "01_a.md": "::: {.proposition #prop:first}\nA.\n:::\n",
        }
    )
    assert [block.label for block in blocks] == ["prop:first", "prop:second"]
    assert [block.number for block in blocks] == [1, 2]


def test_stripping_code_preserves_line_offsets() -> None:
    text = "before\n```\nfenced\nlines\n```\nafter `inline` end\n"
    stripped = strip_code(text)
    assert stripped.count("\n") == text.count("\n")
    assert "fenced" not in stripped
    assert "inline" not in stripped
    assert "before" in stripped and "after" in stripped


@pytest.mark.parametrize(
    "literal",
    [
        "```markdown\n{sample}```\n",
        "~~~~markdown\n{sample}~~~~\n",
        "````markdown\n```\n{sample}```\n`````\n",
        "~~~markdown\n```\n{sample}~~\n~~~\n",
        "   ```markdown\n{sample}   ```\n",
        "    ::: {{.definition #def:quoted}}\n    Definition 4 [@Quoted]\n    :::\n",
        "\t::: {{.definition #def:quoted}}\n\tDefinition 4 [@Quoted]\n\t:::\n",
        "`` {sample} ` still literal ``\n",
    ],
)
def test_literal_samples_do_not_declare_cite_or_number_formalism(literal):
    sample = "::: {.definition #def:quoted}\nDefinition 4 [@Quoted]\n:::\n"
    quoted = literal.format(sample=sample)
    live = "::: {.definition #def:real}\nLive [@RealBook].\n:::\n"
    text = quoted + "\n" + live + "See [@def:real; @OtherBook], Proposition B.\n"
    blocks = parse_blocks({"sample.md": text})
    assert [(block.label, block.number) for block in blocks] == [("def:real", 1)]
    assert split_citations(text, declared_prefixes(blocks)) == (
        frozenset({"def:real"}),
        frozenset({"RealBook", "OtherBook"}),
    )
    assert hand_written_numbers(text) == ("Proposition B",)


def test_live_formalism_retains_original_code_body_and_ignores_literal_closers():
    body = (
        "Live prose [@Book].\n\n"
        "````markdown\n:::\n::: {.definition #def:quoted}\n"
        "Definition 4 [@Quoted]\n```\n````\n\n"
        "An inline `` ` [@AlsoQuoted] `` sample.\n"
        "    :::\n"
        "More live prose."
    )
    text = "::: {.definition #def:real}\n" + body + "\n:::\n"
    (block,) = parse_blocks({"body.md": text})
    assert block.label == "def:real"
    assert block.number == 1
    assert block.body == body
    assert split_citations(block.body, declared_prefixes((block,))) == (
        frozenset(),
        frozenset({"Book"}),
    )
    assert hand_written_numbers(block.body) == ()


@pytest.mark.parametrize(
    "literal_closer",
    [
        "```\n:::\n```\n",
        "~~~\n:::\n~~~\n",
        "    :::\n",
        "`\n:::\n`\n",
    ],
)
def test_literal_closers_cannot_hide_an_unclosed_live_div(literal_closer):
    with pytest.raises(ValueError):
        parse_blocks({"unclosed.md": "::: {.definition #def:real}\n" + literal_closer})


@pytest.mark.parametrize(
    "text",
    [
        "before\r\n````\r\n```\r\nDefinition 4\r\n````\r\nafter `inline` end\r\n",
        "before\n~~~\n[@Quoted]\n~~~\nafter `` x ` y `` end\n",
        "before\n\n    Definition 4\n\t[@Quoted]\n\nafter\n",
    ],
)
def test_literal_mask_preserves_character_offsets_and_line_breaks(text):
    masked = strip_code(text)
    assert len(masked) == len(text)
    assert [(index, char) for index, char in enumerate(masked) if char in "\r\n"] == [
        (index, char) for index, char in enumerate(text) if char in "\r\n"
    ]
    assert masked.index("after") == text.index("after")
    assert hand_written_numbers(text) == ()
    assert split_citations(text, frozenset()) == (frozenset(), frozenset())


def test_equal_inline_runs_keep_real_citations_outside_literal_spans():
    text = "`` ` [@Quoted] `` and `[@Hidden]` but [@Live; @def:real]."
    assert split_citations(text, frozenset({"def"})) == (
        frozenset({"def:real"}),
        frozenset({"Live"}),
    )
    assert split_citations("`unclosed [@Live]", frozenset()) == (
        frozenset(),
        frozenset({"Live"}),
    )


@pytest.mark.parametrize("separator", ["\n\n", "\n```\ncode\n```\n"])
def test_unmatched_inline_runs_do_not_cross_paragraph_or_block_boundaries(separator):
    text = "`unclosed" + separator + "Definition 4 [@Live] `unclosed"
    assert hand_written_numbers(text) == ("Definition 4",)
    assert split_citations(text, frozenset()) == (frozenset(), frozenset({"Live"}))


@pytest.mark.parametrize(
    "opener,closer",
    [
        ("````", "```"),
        ("~~~~", "~~~"),
        ("```", "~~~"),
        ("~~~", "```"),
        ("```", "``` not a closer"),
    ],
)
def test_short_wrong_or_nonterminal_fences_leave_the_literal_open(opener, closer):
    text = opener + "\n" + closer + "\nDefinition 4 [@Quoted]\n"
    assert hand_written_numbers(text) == ()
    assert split_citations(text, frozenset()) == (frozenset(), frozenset())
    assert parse_blocks({"sample.md": text + "::: {.definition #def:quoted}\n"}) == ()
