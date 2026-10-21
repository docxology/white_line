"""Render the plates that show a contract being exercised, not described.

Each reads a live computation rather than a stored transcript. The reason
trail draws what the scoring rule wrote for one input per branch; the
invariant battery draws what each structural check returned when it was handed
a registry built to defeat it; the facets lattice draws what ``project_facets``
returns for every facet combination, with the cells the live scoring battery
inhabits marked by deriving each finding's facets at build time. No plate here
contains a literal reason, detail string, state, or verdict — every one of
them is the return value of a call made at build time.
"""

from __future__ import annotations

from ...facets import (
    DisclosureStance,
    EpistemicSettlement,
    TemporalStatus,
    WitnessFacets,
    finding_facets,
    project_facets,
)
from ...invariants import invariant_defect_battery
from ...model import AbsenceState
from ...registry import WHITE_RECORDS
from ...worked_examples import WORKED_AS_OF, scoring_branch_battery

from ..canvas import (
    marker as _marker,
    open_canvas as _open,
    rect as _rect,
    text as _text,
    wrap_lines as _wrap,
)
from ..metrics import advance_width as _advance
from ..palette import (
    INK,
    KIND_COLOR as _KIND_COLOR,
    LINE,
    MUTED,
    OCHRE,
    PANEL,
    STATE_COLOR as _STATE_COLOR,
    TEAL,
    VIOLET,
    CREAM,
)


def reason_trail() -> str:
    """Draw one row per scoring branch, quoting the reasons it produced.

    The state machine plate shows which branch a record takes; this plate shows
    what the branch then wrote. That distinction is the reason it exists: a
    reader who wants to know why a record is `UNRESOLVED` needs the reason
    trail, and until now the trail appeared nowhere in the figures.
    """

    probes = scoring_branch_battery()
    reason_x, reason_width = 680, 620
    wrapped = [
        [_wrap(reason, 18, reason_width) for reason in probe.finding.reasons]
        for probe in probes
    ]
    input_lines = [_wrap(probe.supplied, 18, 420) for probe in probes]
    row_heights = [
        74
        + max(
            sum(len(lines) for lines in reasons) * 24 + (len(reasons) - 1) * 6,
            len(supplied) * 24 + 26,
        )
        for reasons, supplied in zip(wrapped, input_lines, strict=True)
    ]
    row_tops: list[int] = []
    cursor = 358
    for row_height in row_heights:
        row_tops.append(cursor)
        cursor += row_height
    rule_top = cursor + 30
    height = rule_top + 180

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE REASON TRAIL", 26, VIOLET, "700"),
        _text(110, 140, "Every branch, and what it wrote down", 40, INK, "700"),
        _text(
            110,
            186,
            f"One input per branch of the scoring rule, each assessed live: "
            f"{len(probes)} branches, {len(probes)} findings.",
            22,
            MUTED,
        ),
        _text(
            110,
            216,
            "A reason explains one scoring decision; it is never a judgment of the observation.",
            22,
            MUTED,
        ),
        _text(
            110,
            266,
            f"COMPUTED THROUGH assess_absence · REVIEW DATE {WORKED_AS_OF} · A DECISION TRAIL, NOT EVIDENCE ABOUT ANY WORK",
            18,
            TEAL,
            "700",
        ),
        _text(150, 326, "BRANCH AND SUPPLIED INPUT", 18, VIOLET, "700"),
        _text(reason_x, 326, "THE ORDERED REASONS THE ASSESSOR RETURNED", 18, VIOLET, "700"),
    ]
    for index, probe in enumerate(probes):
        y = row_tops[index]
        row_h = row_heights[index]
        finding = probe.finding
        color = _STATE_COLOR[finding.state]
        parts.append(
            _rect(110, y, 1380, row_h - 18, PANEL if index % 2 == 0 else CREAM, LINE, 1)
        )
        parts.append(
            f'<rect x="110" y="{y}" width="10" height="{row_h - 18}" fill="{color}"/>'
        )
        parts.append(_text(150, y + 44, probe.branch, 21, INK, "700"))
        for line_index, line in enumerate(input_lines[index]):
            parts.append(_text(150, y + 78 + line_index * 30, line, 18, MUTED))
        parts.append(
            _text(
                150,
                y + 78 + len(input_lines[index]) * 30 + 4,
                f"→ {finding.state.value}",
                20,
                color,
                "700",
            )
        )
        kind_label = finding.kind.value
        parts.append(
            _text(
                1460 - int(_advance(kind_label, 18, True)),
                y + 44,
                kind_label,
                18,
                _KIND_COLOR[finding.kind],
                "700",
            )
        )
        reason_y = y + 50
        for reason_index, lines in enumerate(wrapped[index]):
            parts.append(
                _text(reason_x - 34, reason_y + 8, f"{reason_index + 1}", 18, color, "700")
            )
            for line_index, line in enumerate(lines):
                parts.append(
                    _text(reason_x, reason_y + 8 + line_index * 30, line, 18, INK)
                )
            reason_y += len(lines) * 30 + 8
    parts.extend(
        [
            _rect(110, rule_top, 1380, 150, CREAM, INK, 2),
            _text(140, rule_top + 44, "READING RULE", 19, VIOLET, "700"),
            _text(
                140,
                rule_top + 84,
                "The trail records why the ledger reported a state, and its order is the order the rule appended.",
                20,
                INK,
            ),
            _text(
                140,
                rule_top + 122,
                "A long trail is not a worse record than a short one; it is a record with more context attached.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


def invariant_battery() -> str:
    """Draw each structural check rejecting the defect it guards against.

    The manuscript's defect-detection proposition is a claim about what the
    checks do when handed bad input, and until this plate the figures showed
    only the registry the checks pass on. Each row here is one call: the
    verdict on the live registry, the defect planted, and the detail string the
    check returned when it refused the planted registry.
    """

    probes = invariant_defect_battery()
    detail_x, detail_width = 620, 830
    defects = [_wrap(probe.defect, 18, 440) for probe in probes]
    details = [_wrap(probe.rejected_detail, 18, detail_width) for probe in probes]
    row_heights = [
        112 + max(len(defect), len(detail) + 1) * 27
        for defect, detail in zip(defects, details, strict=True)
    ]
    row_tops: list[int] = []
    cursor = 358
    for row_height in row_heights:
        row_tops.append(cursor)
        cursor += row_height
    rule_top = cursor + 40
    height = rule_top + 200

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE INVARIANT BATTERY", 26, VIOLET, "700"),
        _text(110, 140, "Every check, actually rejecting", 40, INK, "700"),
        _text(
            110,
            186,
            f"All {len(probes)} structural checks pass on the live registry and are then run "
            "over a registry",
            22,
            MUTED,
        ),
        _text(110, 216, "carrying exactly the defect each one guards against.", 22, MUTED),
        _text(
            110,
            266,
            "DETECTION OF THE PLANTED DEFECTS · NOT A CLAIM THAT SIX CHECKS EXHAUST THE FAULTS A REGISTRY COULD CARRY",
            18,
            TEAL,
            "700",
        ),
        _text(150, 326, "CHECK AND PLANTED DEFECT", 18, VIOLET, "700"),
        _text(detail_x, 326, "WHAT THE CHECK RETURNED WHEN IT REFUSED", 18, VIOLET, "700"),
    ]
    for index, probe in enumerate(probes):
        y = row_tops[index]
        row_h = row_heights[index]
        parts.append(
            _rect(110, y, 1380, row_h - 18, PANEL if index % 2 == 0 else CREAM, LINE, 1)
        )
        parts.append(
            f'<rect x="110" y="{y}" width="10" height="{row_h - 18}" fill="{OCHRE}"/>'
        )
        parts.append(
            _text(150, y + 44, f"P{index + 1} · {probe.check_name}", 20, OCHRE, "700")
        )
        for line_index, line in enumerate(defects[index]):
            parts.append(_text(150, y + 80 + line_index * 30, line, 18, MUTED))
        parts.append(
            _text(
                detail_x,
                y + 44,
                f"live registry: {probe.live_detail} · planted registry: rejected",
                18,
                TEAL,
                "700",
            )
        )
        for line_index, line in enumerate(details[index]):
            parts.append(_text(detail_x, y + 80 + line_index * 30, line, 18, INK))
        if probe.also_failed:
            parts.append(
                _text(
                    detail_x,
                    y + 80 + len(details[index]) * 30,
                    f"the same registry also trips: {', '.join(probe.also_failed)}",
                    18,
                    MUTED,
                )
            )
    parts.extend(
        [
            _rect(110, rule_top, 1380, 150, CREAM, INK, 2),
            _text(140, rule_top + 44, "READING RULE", 19, VIOLET, "700"),
            _text(
                140,
                rule_top + 84,
                "A row shows that this check refuses this defect, which is narrower than saying the registry is sound.",
                20,
                INK,
            ),
            _text(
                140,
                rule_top + 122,
                "A defect no check was written for would leave every row here unchanged.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


def battery_facet_cells() -> dict[
    tuple[EpistemicSettlement, DisclosureStance, TemporalStatus], int
]:
    """Count the live scoring battery's findings per facet cell.

    Each count comes from a real ``assess_absence`` call: the battery is run,
    every finding is factored through ``finding_facets`` at the battery's own
    review date, and the resulting cell is tallied. Nothing is asserted about
    cells the battery does not reach — an uninhabited cell is a fact about the
    battery's constructed inputs, not about the projection.
    """

    records_by_id = {record.id: record for record in WHITE_RECORDS}
    cells: dict[
        tuple[EpistemicSettlement, DisclosureStance, TemporalStatus], int
    ] = {}
    for probe in scoring_branch_battery():
        facets = finding_facets(
            probe.finding, records_by_id[probe.finding.record_id], WORKED_AS_OF
        )
        key = (facets.settlement, facets.disclosure, facets.temporality)
        cells[key] = cells.get(key, 0) + 1
    return cells


def facets_lattice() -> str:
    """Draw every facet combination and the state ``project_facets`` returns.

    One row per settlement-and-stance pair, one column per temporal status.
    Each cell's state, the fail-closed cells, and the battery markers are all
    computed at build time: the projection is called on every combination, and
    a combination it refuses is drawn hatched with the refusal named rather
    than being dropped or guessed at.
    """

    projected: dict[
        tuple[EpistemicSettlement, DisclosureStance, TemporalStatus],
        AbsenceState | None,
    ] = {}
    for settlement in EpistemicSettlement:
        for disclosure in DisclosureStance:
            for temporality in TemporalStatus:
                try:
                    state: AbsenceState | None = project_facets(
                        WitnessFacets("cell", settlement, disclosure, temporality)
                    )
                except ValueError:
                    state = None
                projected[(settlement, disclosure, temporality)] = state
    fail_closed = sum(1 for value in projected.values() if value is None)
    inhabited = battery_facet_cells()

    label_x = 110
    cell_x0, cell_w, cell_gap = 600, 282, 16
    columns = {
        temporality: cell_x0 + index * (cell_w + cell_gap)
        for index, temporality in enumerate(TemporalStatus)
    }
    top = 390
    row_h = 106
    rows = [
        (settlement, disclosure)
        for settlement in EpistemicSettlement
        for disclosure in DisclosureStance
    ]
    rule_top = top + len(rows) * row_h + 30
    height = rule_top + 190

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE FACETS LATTICE", 26, VIOLET, "700"),
        _text(110, 140, "Every combination, and what it projects to", 40, INK, "700"),
        _text(
            110,
            186,
            f"project_facets over all {len(projected)} settlement × stance × "
            f"temporality combinations: {len(projected) - fail_closed} project, "
            f"{fail_closed} fail closed.",
            22,
            MUTED,
        ),
        _text(
            110,
            216,
            "Marked cells use typed assertions from the live scoring battery, "
            "factored through finding_facets at build time.",
            22,
            MUTED,
        ),
        _text(
            110,
            266,
            f"COMPUTED THROUGH project_facets AND finding_facets · REVIEW DATE "
            f"{WORKED_AS_OF} · RECORDED-DATA FACETS, NOT A RICHER WORLD",
            18,
            TEAL,
            "700",
        ),
        _text(label_x, 352, "SETTLEMENT AND STANCE", 18, VIOLET, "700"),
    ]
    for temporality, column_x in columns.items():
        parts.append(_text(column_x + 16, 352, temporality.value, 18, VIOLET, "700"))
    for index, (settlement, disclosure) in enumerate(rows):
        y = top + index * row_h
        parts.append(
            _rect(110, y, 1380, row_h - 12, PANEL if index % 2 == 0 else CREAM, LINE, 1)
        )
        parts.append(_text(label_x + 30, y + 44, settlement.value, 20, INK, "700"))
        parts.append(
            _text(label_x + 30, y + 76, f"stance {disclosure.value}", 18, MUTED)
        )
        for temporality, column_x in columns.items():
            state = projected[(settlement, disclosure, temporality)]
            if state is None:
                parts.append(_rect(column_x, y + 8, cell_w, row_h - 28, CREAM, MUTED, 2))
                for offset in range(176, cell_w, 36):
                    parts.append(
                        f'<line x1="{column_x + offset}" y1="{y + 8}" '
                        f'x2="{column_x + offset - 20}" y2="{y + row_h - 20}" '
                        f'stroke="{MUTED}" stroke-width="2"/>'
                    )
                parts.append(
                    _text(column_x + 16, y + 44, "FAILS CLOSED", 18, MUTED, "700")
                )
                parts.append(
                    _text(column_x + 16, y + 74, "not recordable", 18, MUTED)
                )
                continue
            color = _STATE_COLOR[state]
            parts.append(
                f'<rect x="{column_x}" y="{y + 8}" width="{cell_w}" '
                f'height="{row_h - 28}" fill="{color}" opacity="0.14"/>'
            )
            parts.append(_rect(column_x, y + 8, cell_w, row_h - 28, "none", color, 2))
            parts.append(_text(column_x + 16, y + 44, state.value, 20, color, "700"))
            if state is AbsenceState.UNRESOLVED and (
                settlement is EpistemicSettlement.NAMED
            ):
                parts.append(
                    _text(column_x + 16, y + 70, "the staleness decay", 18, MUTED)
                )
            count = inhabited.get((settlement, disclosure, temporality), 0)
            if count:
                parts.append(_marker("circle", column_x + 24, y + 86, 8, INK))
                parts.append(
                    _text(
                        column_x + 42,
                        y + 92,
                        f"live battery ×{count}",
                        18,
                        INK,
                        "700",
                    )
                )
    parts.extend(
        [
            _rect(110, rule_top, 1380, 150, CREAM, INK, 2),
            _text(140, rule_top + 44, "READING RULE", 19, VIOLET, "700"),
            _text(
                140,
                rule_top + 84,
                "A cell names the one caution-ordered state the ledger reports for records whose facets land there.",
                20,
                INK,
            ),
            _text(
                140,
                rule_top + 122,
                "The lattice is a projection table of recorded-data facets; it is not a claim that richer states exist in the world.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


__all__ = ["battery_facet_cells", "facets_lattice", "invariant_battery", "reason_trail"]
