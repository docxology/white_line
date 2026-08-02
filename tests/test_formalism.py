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

The second family is semantic: every definition is compared against the code it
describes. The alphabets are read from the enumerations, the tuple definitions
from the dataclass fields, the caution order from ``caution_rank``, the intake
partition from ``IntakeCode`` and ``SET_ASIDE_CODES``, the date branches from
``usable_observation_date``, the scoring reasons from findings a live
``assess_absence`` call returned, and the directive map from the protocol. A
definition that drifted from the code would fail here rather than describe an
evaluator that no longer exists.
"""

from __future__ import annotations

import dataclasses
import inspect
import re
from datetime import date
from pathlib import Path

import pytest
from white_line import (
    SCORING_REASONS,
    WHITE_RECORDS,
    WORKED_AS_OF,
    AbsenceFinding,
    AbsenceKind,
    AbsenceObservation,
    AbsenceRecord,
    AbsenceState,
    DisclosureStance,
    EpistemicSettlement,
    IntakeCode,
    IntakeEvent,
    ReportEnvelope,
    ReturnContract,
    TemporalStatus,
    WhiteReport,
    WitnessFacets,
    all_ledger_checks,
    assess_absence,
    caution_rank,
    finding_facets,
    project_facets,
    review_action_for_state,
    scoring_branch_battery,
    usable_observation_date,
)
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
from white_line.model import SET_ASIDE_CODES

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "manuscript"

SOURCES = read_manuscript(MANUSCRIPT)
BLOCKS = parse_blocks(SOURCES)
BY_LABEL = {block.label: block for block in BLOCKS}
PROSE = "\n".join(SOURCES[name] for name in sorted(SOURCES))


def _body(label: str) -> str:
    """Return one formalism block's body, failing loudly if it is absent."""

    assert label in BY_LABEL, f"no formalism block is labelled {label!r}"
    return BY_LABEL[label].body


def _mathit_tokens(body: str) -> list[str]:
    """Return the ``\\mathit{...}`` names a tuple definition lists, in order."""

    return [
        token.replace("\\_", "_")
        for token in re.findall(r"\\mathit\{([^}]+)\}", body)
    ]


# --------------------------------------------------------------------------- #
# Structural: labels, references, and the absence of hand-written numbers
# --------------------------------------------------------------------------- #
def test_the_manuscript_declares_formalism_blocks_at_all() -> None:
    """An empty scan set would make every check in this module vacuous."""

    assert BLOCKS, "the manuscript declares no formalism blocks"
    assert {block.kind for block in BLOCKS} <= set(FORMALISM_TITLES)


def test_every_formalism_block_carries_a_unique_prefixed_label() -> None:
    """A block with no label is numbered but can never be referenced."""

    unlabelled = [
        f"{block.source}:{block.printed}" for block in BLOCKS if not block.label
    ]
    assert not unlabelled, unlabelled
    wrong_prefix = [
        block.label
        for block in BLOCKS
        if not block.label.startswith(f"{FORMALISM_PREFIXES[block.kind]}:")
    ]
    assert not wrong_prefix, wrong_prefix
    labels = [block.label for block in BLOCKS]
    assert len(labels) == len(set(labels)), "duplicate formalism label"


def test_the_label_check_rejects_an_unlabelled_block() -> None:
    """Positive control: a block written without an identifier is caught."""

    planted = parse_blocks(
        {"planted.md": "::: {.definition title=\"Nameless\"}\nBody.\n:::\n"}
    )
    assert len(planted) == 1
    assert planted[0].label == ""
    assert planted[0].printed == "Definition 1 (Nameless)"


def test_the_label_check_rejects_the_wrong_prefix_for_a_kind() -> None:
    """Positive control: a proposition labelled ``def:`` is caught."""

    planted = parse_blocks({"planted.md": "::: {.proposition #def:wrong}\nX.\n:::\n"})
    assert len(planted) == 1
    block = planted[0]
    assert not block.label.startswith(f"{FORMALISM_PREFIXES[block.kind]}:")


def test_every_formalism_reference_resolves_to_a_declared_block() -> None:
    """An unresolved reference ships as literal markup in every edition."""

    references, _keys = split_citations(PROSE, declared_prefixes(BLOCKS))
    assert references, "the manuscript makes no formalism references"
    dangling = sorted(
        reference for reference in references
        if reference not in BY_LABEL
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
    assert "def:kindz" not in BY_LABEL


def test_no_manuscript_file_writes_a_formalism_number_by_hand() -> None:
    """The whole point of the fenced syntax is that no such literal exists."""

    offences = {
        name: found
        for name, text in SOURCES.items()
        if (found := hand_written_numbers(text))
    }
    assert not offences, offences


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
# The binding table, keyed on labels
# --------------------------------------------------------------------------- #
BINDING_ROW_RE = re.compile(
    r"^\| \[@(?P<label>[a-z]+:[a-z0-9-]+)\][^|]*\| `(?P<test>[^`]+)` \|", re.M
)


def _binding_rows() -> list[tuple[str, str]]:
    """Return the (label, test reference) pairs of the binding table."""

    rows = BINDING_ROW_RE.findall(SOURCES["03b_formalism.md"])
    assert rows, "the formalism section must carry a claim-to-test table"
    return rows


def test_the_binding_table_names_tests_that_exist() -> None:
    """A row naming a renamed test would read as covered while nothing checked."""

    sources = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted((PROJECT_ROOT / "tests").glob("test_*.py"))
    }
    for _label, reference in _binding_rows():
        file_name, _, function = reference.partition("::")
        assert file_name in sources, f"{reference} names no test file"
        assert f"def {function}(" in sources[file_name], f"{reference} names no test"


def test_the_binding_table_check_rejects_a_renamed_test() -> None:
    """Positive control: a row naming a missing test is caught."""

    sources = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted((PROJECT_ROOT / "tests").glob("test_*.py"))
    }
    file_name, function = "test_analysis.py", "test_no_such_function_exists"
    assert file_name in sources
    assert f"def {function}(" not in sources[file_name]


def test_every_formalism_block_has_a_binding_row() -> None:
    """A definition or proposition with no named test is an unbound claim."""

    bound = {label for label, _reference in _binding_rows()}
    declared = {block.label for block in BLOCKS}
    assert declared, "no formalism blocks to bind"
    assert not declared - bound, sorted(declared - bound)
    assert not bound - declared, sorted(bound - declared)


# --------------------------------------------------------------------------- #
# Semantic: each definition against the code it describes
# --------------------------------------------------------------------------- #
def test_the_kind_alphabet_in_prose_is_the_enumeration() -> None:
    body = _body("def:kinds")
    named = set(re.findall(r"\\texttt\{([A-Z_\\]+)\}", body))
    assert {name.replace("\\_", "_") for name in named} == {
        kind.value for kind in AbsenceKind
    }
    assert f"|K| = {len(AbsenceKind)}$" in body


def test_the_state_alphabet_in_prose_is_the_enumeration() -> None:
    body = _body("def:states")
    named = set(re.findall(r"\\texttt\{([A-Z_\\]+)\}", body))
    assert {name.replace("\\_", "_") for name in named} == {
        state.value for state in AbsenceState
    }
    assert f"|S| = {len(AbsenceState)}$" in body


def test_the_alphabet_check_rejects_a_dropped_member() -> None:
    """Positive control: a definition missing one member fails the comparison."""

    drifted = _body("def:states").replace(", \\texttt{WITHHELD}", "")
    named = {
        name.replace("\\_", "_")
        for name in re.findall(r"\\texttt\{([A-Z_\\]+)\}", drifted)
    }
    assert named != {state.value for state in AbsenceState}


#: Each tuple definition and the dataclass whose fields it must list.
TUPLE_DEFINITIONS = (
    ("def:record", AbsenceRecord),
    ("def:observation", AbsenceObservation),
    ("def:finding", AbsenceFinding),
    ("def:report", WhiteReport),
    ("def:event", IntakeEvent),
    ("def:facets", WitnessFacets),
    ("def:return", ReturnContract),
    ("def:envelope", ReportEnvelope),
)


@pytest.mark.parametrize(("label", "cls"), TUPLE_DEFINITIONS)
def test_every_tuple_definition_lists_its_dataclass_fields(
    label: str, cls: type
) -> None:
    """The tuple in prose must be the record the code actually carries."""

    listed = _mathit_tokens(_body(label))
    fields = [field.name for field in dataclasses.fields(cls)]
    # A name may be repeated in the prose that follows the tuple; compare the
    # opening run, which is the tuple itself, and then the set.
    assert listed[: len(fields)] == fields, label
    assert set(listed) <= set(fields), label


def test_the_tuple_definition_check_rejects_a_missing_field() -> None:
    """Positive control: dropping one component breaks the comparison."""

    drifted = _body("def:report").replace("\\mathit{registry\\_digest}, ", "")
    listed = _mathit_tokens(drifted)
    fields = [field.name for field in dataclasses.fields(WhiteReport)]
    assert listed[: len(fields)] != fields


def test_the_caution_order_in_prose_is_caution_rank() -> None:
    body = _body("def:caution-order")
    printed = {
        name.replace("\\_", "_"): int(rank)
        for name, rank in re.findall(r"c\(\\texttt\{([A-Z_\\]+)\}\) = (\d+)", body)
    }
    assert printed == {state.value: caution_rank(state) for state in AbsenceState}


def test_the_caution_order_check_rejects_a_swapped_rank() -> None:
    """Positive control: swapping two ranks breaks the comparison."""

    drifted = _body("def:caution-order").replace(
        "c(\\texttt{NAMED}) = 1", "c(\\texttt{NAMED}) = 2"
    )
    printed = {
        name.replace("\\_", "_"): int(rank)
        for name, rank in re.findall(r"c\(\\texttt\{([A-Z_\\]+)\}\) = (\d+)", drifted)
    }
    assert printed != {state.value: caution_rank(state) for state in AbsenceState}


def test_the_assessment_map_matches_the_assessor_signature() -> None:
    """The stated parameters and check count must be the evaluator's own."""

    body = _body("def:assessment-map")
    parameters = list(inspect.signature(assess_absence).parameters)
    quoted = re.findall(r"`([a-z_]+)`", body)
    assert quoted[: len(parameters)] == parameters
    assert f"all ${len(all_ledger_checks())}$ structural" in body


def test_the_assessment_map_check_rejects_a_renamed_parameter() -> None:
    """Positive control: a stale parameter name fails the comparison."""

    drifted = _body("def:assessment-map").replace("`as_of`", "`asof`")
    parameters = list(inspect.signature(assess_absence).parameters)
    assert re.findall(r"`([a-z_]+)`", drifted)[: len(parameters)] != parameters


def _intake_partition(body: str) -> list[frozenset[str]]:
    """Return the three code groups the intake definition's partition names."""

    sentence = body.split("Intake therefore uses the whole code alphabet")[-1]
    sentence = sentence.split(". No input")[0]
    return [
        frozenset(re.findall(r"`([A-Z_]+)`", group))
        for group in sentence.split(";")
    ]


def test_the_intake_definition_partitions_the_live_code_alphabet() -> None:
    """Refused, kept-but-undatable, and reconciled must be the code's own split."""

    groups = _intake_partition(_body("def:intake"))
    assert len(groups) == 3, groups
    refused, undatable, reconciled = groups
    assert refused == {code.value for code in SET_ASIDE_CODES}
    assert undatable == {IntakeCode.UNDATED_OBJECT.value}
    assert reconciled == {
        code.value
        for code in IntakeCode
        if code not in SET_ASIDE_CODES and code is not IntakeCode.UNDATED_OBJECT
    }
    assert refused | undatable | reconciled == {code.value for code in IntakeCode}


def test_the_intake_partition_check_rejects_a_misfiled_code() -> None:
    """Positive control: moving one code across the split breaks the match."""

    drifted = _body("def:intake").replace(
        "`UNDATED_OBJECT` keeps one", "`RESERVED_STATE` keeps one"
    )
    refused, undatable, _reconciled = _intake_partition(drifted)
    assert undatable != {IntakeCode.UNDATED_OBJECT.value}


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

    body = _body("def:date-resolution")
    assert "white_line.dates.usable_observation_date" in body
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


def _quoted_reasons(body: str) -> list[str]:
    """Return the multi-word backticked strings the scoring definition quotes."""

    return [
        token for token in re.findall(r"`([^`]+)`", body) if " " in token
    ]


def test_every_quoted_scoring_reason_is_produced_by_the_assessor() -> None:
    """A reason quoted in prose must be one a live assessment actually wrote."""

    quoted = _quoted_reasons(_body("def:scoring"))
    assert sorted(quoted) == sorted(SCORING_REASONS)
    produced: set[str] = set()
    from white_line import scoring_branch_battery

    for probe in scoring_branch_battery():
        produced.update(probe.finding.reasons)
    assert set(quoted) <= produced, sorted(set(quoted) - produced)


def test_the_scoring_reason_check_rejects_a_reworded_reason() -> None:
    """Positive control: a reason the assessor never writes is caught."""

    drifted = _body("def:scoring").replace(
        "`no absence note was recorded`", "`nothing was recorded here`"
    )
    assert sorted(_quoted_reasons(drifted)) != sorted(SCORING_REASONS)


def test_the_directive_map_in_prose_is_the_protocol_map() -> None:
    """Every arrow in the definition must be the action the protocol returns."""

    body = _body("def:directive")
    printed = {
        state.replace("\\_", "_"): action.replace("\\_", "_")
        for state, action in re.findall(
            r"\\rho\(\\mathrm\{([A-Z_\\]+)\}\) &= \\mathrm\{([A-Z_\\]+)\}", body
        )
    }
    assert printed == {
        state.value: review_action_for_state(state).value for state in AbsenceState
    }


def test_the_directive_map_check_rejects_a_swapped_action() -> None:
    """Positive control: pointing one state at another's action is caught."""

    drifted = _body("def:directive").replace(
        "\\rho(\\mathrm{NAMED}) &= \\mathrm{RETAIN\\_NAMED\\_SCOPE}",
        "\\rho(\\mathrm{NAMED}) &= \\mathrm{REOPEN\\_OR\\_BOUND}",
    )
    printed = {
        state.replace("\\_", "_"): action.replace("\\_", "_")
        for state, action in re.findall(
            r"\\rho\(\\mathrm\{([A-Z_\\]+)\}\) &= \\mathrm\{([A-Z_\\]+)\}", drifted
        )
    }
    assert printed != {
        state.value: review_action_for_state(state).value for state in AbsenceState
    }


def _facet_alphabet(body: str, letter: str) -> set[str]:
    """Return the members one facet alphabet lists in the definition body."""

    match = re.search(letter + r" = \\\{(.+?)\\\}", body, re.S)
    assert match is not None, f"def:facets states no alphabet {letter}"
    return {
        name.replace("\\_", "_")
        for name in re.findall(r"\\texttt\{([A-Z_\\]+)\}", match.group(1))
    }


def test_the_facet_alphabets_in_prose_are_the_enumerations() -> None:
    """Each stated facet alphabet must be the live enumeration, member for member."""

    body = _body("def:facets")
    for letter, enumeration in (
        ("E", EpistemicSettlement),
        ("D", DisclosureStance),
        ("T", TemporalStatus),
    ):
        assert _facet_alphabet(body, letter) == {
            member.value for member in enumeration
        }, letter
        assert f"|{letter}| = {len(enumeration)}$" in body


def test_the_facet_alphabet_check_rejects_a_dropped_member() -> None:
    """Positive control: an alphabet missing one member fails the comparison."""

    drifted = _body("def:facets").replace(
        "\\texttt{UNDISCLOSED}", "\\texttt{UNRESOLVED}"
    )
    assert drifted != _body("def:facets")
    assert _facet_alphabet(drifted, "E") != {
        member.value for member in EpistemicSettlement
    }


def test_the_projection_cell_counts_re_derive_from_the_code() -> None:
    """The 24/21/3 split in the projection definition is computed, not typed."""

    body = _body("def:projection")
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
    assert (
        f"Of the ${combinations}$ combinations in $E \\times D \\times T$, "
        f"${combinations - fail_closed}$ project and ${fail_closed}$ fail" in body
    )


def test_the_projection_count_check_rejects_a_drifted_number() -> None:
    """Positive control: one altered count breaks the comparison."""

    drifted = _body("def:projection").replace("$21$ project", "$22$ project")
    assert "Of the $24$ combinations in $E \\times D \\times T$, $21$ project" not in (
        drifted
    )


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
                "::: {.definition .unnumbered #def:b title=\"Aside\"}\nTwo.\n:::\n\n"
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
