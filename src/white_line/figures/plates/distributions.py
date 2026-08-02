"""Render derived distribution plates without creating analysis results."""

from __future__ import annotations

from ...analysis import (
    ASSERTABLE_STATES,
    coverage_matrix,
    decay_timeline as assess_decay_timeline,
    decay_transition_offsets,
    events_tally,
    reconciliation_matrix,
)
from ...model import (
    AbsenceKind,
    AbsenceObservation,
    AbsenceState,
    IntakeCode,
    caution_rank,
)
from ...registry import WHITE_RECORDS
from ...worked_examples import WORKED_AS_OF, worked_report

from ..canvas import open_canvas as _open, rect as _rect, text as _text
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


def decay_timeline() -> str:
    """Plot a real decay sweep: an all-NAMED dated cohort re-assessed daily."""

    anchor = "2026-01-01"
    cohort = tuple(
        AbsenceObservation(
            record.id, AbsenceState.NAMED, "dated naming for the sweep", anchor
        )
        for record in WHITE_RECORDS
    )
    points = assess_decay_timeline(cohort, anchor, "2027-02-05")
    transitions = decay_transition_offsets(points)
    total = len(WHITE_RECORDS)
    max_offset = points[-1].offset_days

    x0, x1 = 190, 1470
    y_bottom, y_top = 880, 350

    def sx(offset: int) -> float:
        """Map a review-day offset to the timeline's horizontal coordinate."""

        return x0 + (x1 - x0) * offset / max_offset

    def sy(count: int) -> float:
        """Map a state tally to the timeline's vertical coordinate."""

        return y_bottom - (y_bottom - y_top) * count / total

    def step_path(state: AbsenceState) -> str:
        """Return the SVG step path for one state across the assessed sweep."""

        counts = [point.tally[state] for point in points]
        path = [f"M{sx(0):.1f} {sy(counts[0]):.1f}"]
        for index in range(1, len(counts)):
            if counts[index] != counts[index - 1]:
                path.append(f"H{sx(points[index].offset_days):.1f}")
                path.append(f"V{sy(counts[index]):.1f}")
        path.append(f"H{sx(max_offset):.1f}")
        return " ".join(path)

    parts = _open(1600, 1180)
    parts += [
        _text(110, 88, "THE DECAY TIMELINE", 26, VIOLET, "700"),
        _text(110, 140, "A dated naming does not stay settled forever", 40, INK, "700"),
        _text(
            110,
            186,
            f"All {total} records receive a NAMED observation dated {anchor}; the same input",
            22,
            MUTED,
        ),
        _text(110, 216, "is re-assessed at every later review date.", 22, MUTED),
        _text(
            110,
            264,
            "COMPUTED BY SWEEPING assess_absence OVER REVIEW DATES · AN ILLUSTRATIVE COHORT, NOT OBSERVED PROJECT DATA",
            18,
            TEAL,
            "700",
        ),
    ]
    # Axes and grid.
    for count in range(total + 1):
        y = sy(count)
        parts.append(
            f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{LINE}" stroke-width="1" opacity="0.6"/>'
        )
        parts.append(_text(x0 - 46, int(y) + 7, f"{count}", 18, MUTED))
    for offset in range(0, max_offset + 1, 100):
        x = sx(offset)
        parts.append(
            f'<line x1="{x:.1f}" y1="{y_bottom}" x2="{x:.1f}" y2="{y_bottom + 12}" stroke="{MUTED}" stroke-width="2"/>'
        )
        parts.append(_text(int(x) - 20, y_bottom + 44, f"{offset}", 18, MUTED))
    parts.append(
        f'<line x1="{x0}" y1="{y_bottom}" x2="{x1}" y2="{y_bottom}" stroke="{INK}" stroke-width="2"/>'
    )
    parts.append(
        f'<line x1="{x0}" y1="{y_top}" x2="{x0}" y2="{y_bottom}" stroke="{INK}" stroke-width="2"/>'
    )
    parts.append(
        _text(
            560,
            y_bottom + 86,
            "days between the dated naming and the review date",
            20,
            INK,
        )
    )
    parts.append(_text(110, 320, "records in each state", 20, INK))
    # Horizon crossings: each transition offset is horizon + 1 days after the naming.
    for offset in transitions:
        x = sx(offset)
        parts.append(
            f'<line x1="{x:.1f}" y1="{y_top}" x2="{x:.1f}" y2="{y_bottom}" stroke="{VIOLET}" '
            'stroke-width="2" stroke-dasharray="3 10"/>'
        )
        parts.append(_text(int(x) - 40, y_top - 16, f"day {offset}", 18, VIOLET, "700"))
    # The two step curves, drawn from the swept tallies.
    parts.append(
        f'<path d="{step_path(AbsenceState.NAMED)}" fill="none" stroke="{TEAL}" stroke-width="6" stroke-linecap="round"/>'
    )
    parts.append(
        f'<path d="{step_path(AbsenceState.UNRESOLVED)}" fill="none" stroke="{OCHRE}" stroke-width="6" stroke-linecap="round" stroke-dasharray="14 8"/>'
    )
    parts.extend(
        [
            f'<line x1="1010" y1="1000" x2="1060" y2="1000" stroke="{TEAL}" stroke-width="6"/>',
            _text(1074, 1007, "NAMED", 19, TEAL, "700"),
            f'<line x1="1210" y1="1000" x2="1260" y2="1000" stroke="{OCHRE}" stroke-width="6" stroke-dasharray="14 8"/>',
            _text(1274, 1007, "UNRESOLVED", 19, OCHRE, "700"),
            _text(
                110,
                1007,
                "Each dashed crossing is one review horizon expiring:",
                19,
                INK,
            ),
            _text(
                110,
                1036,
                "the naming is one day past its horizon and decays to UNRESOLVED.",
                19,
                INK,
            ),
            _text(
                110,
                1084,
                "Decay only raises caution; no review date makes an aged naming look more settled.",
                19,
                MUTED,
            ),
            _text(110, 1114, "The curve describes the contract, not the world.", 19, MUTED),
            "</svg>",
        ]
    )
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Figure 9: the ordered-pair conflict-resolution lattice (from the analysis).
def conflict_lattice() -> str:
    """Draw every ordered-pair resolution from reconciliation_matrix()."""

    matrix = reconciliation_matrix()
    states = ASSERTABLE_STATES
    cell_w, cell_h = 330, 166
    grid_x, grid_y = 420, 400

    lattice_bottom = grid_y + len(states) * cell_h
    rule_top = lattice_bottom + 40
    height = rule_top + 210
    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE CONFLICT-RESOLUTION LATTICE", 26, VIOLET, "700"),
        _text(110, 140, "Every disagreement resolves toward caution", 40, INK, "700"),
        _text(
            110,
            186,
            f"All {len(matrix)} ordered pairs of assertable states, resolved by the defined caution order.",
            22,
            MUTED,
        ),
        _text(
            110,
            216,
            "The ledger-reserved fourth state appears nowhere: observations may not assert it.",
            22,
            MUTED,
        ),
        _text(
            110,
            264,
            "GENERATED FROM caution_rank VIA reconciliation_matrix · A CONTRACT TABLE, NOT A SEVERITY OR SAFETY SCORE",
            18,
            TEAL,
            "700",
        ),
        _text(grid_x, grid_y - 60, "LATER (INCOMING) OBSERVATION →", 19, VIOLET, "700"),
        _text(130, grid_y - 60, "EARLIER (HELD) ↓", 19, VIOLET, "700"),
    ]
    for col, state in enumerate(states):
        x = grid_x + col * cell_w
        parts.append(
            _text(
                x + 18,
                grid_y - 24,
                f"{state.value} · rank {caution_rank(state)}",
                18,
                _STATE_COLOR[state],
                "700",
            )
        )
    for row, held in enumerate(states):
        y = grid_y + row * cell_h
        parts.append(_text(130, y + 72, held.value, 19, _STATE_COLOR[held], "700"))
        parts.append(_text(130, y + 104, f"rank {caution_rank(held)}", 18, MUTED))
        for col, incoming in enumerate(states):
            kept = matrix[(held, incoming)]
            color = _STATE_COLOR[kept]
            x = grid_x + col * cell_w
            parts.append(_rect(x, y, cell_w - 14, cell_h - 14, PANEL, color, 3))
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell_w - 14}" height="10" fill="{color}"/>'
            )
            parts.append(_text(x + 18, y + 70, kept.value, 22, color, "700"))
            parts.append(
                _text(
                    x + 18,
                    y + 106,
                    f"kept · caution rank {caution_rank(kept)}",
                    18,
                    MUTED,
                )
            )
            note = "identity" if held is incoming else "max caution wins"
            parts.append(_text(x + 18, y + 142, note, 18, color, "700"))
    parts.extend(
        [
            _rect(110, rule_top, 1380, 170, CREAM, INK, 2),
            _text(140, rule_top + 46, "READING RULE", 19, VIOLET, "700"),
            _text(
                140,
                rule_top + 88,
                "The table is symmetric: swapping the two observers never changes the kept state, so arrival order carries no authority.",
                20,
                INK,
            ),
            _text(
                140,
                rule_top + 126,
                "No cell is less cautious than either of its inputs. The lattice records the",
                19,
                MUTED,
            ),
            _text(
                140,
                rule_top + 156,
                "reconciliation contract, not a judgment of any observer.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Figure 10: the two distributional views of one worked report.
def distribution_panels() -> str:
    """Draw ``events_tally`` and ``coverage_matrix`` for one worked report.

    Every count in the figure is computed here, through the public
    ``assess_absence`` call on the worked observations — no tally, sum, or
    cell value is a hand-typed literal.

    The two views are stacked rather than placed side by side: at the
    legibility floor a four-column state grid no longer fits in half the
    canvas width without truncating ``NOT_RECORDED``, and truncating a state
    name would break the shape-and-text reading the figures depend on.
    """

    report = worked_report()
    tally = events_tally(report)
    matrix = coverage_matrix(report)
    kinds = list(AbsenceKind)
    states = list(AbsenceState)
    total_events = sum(tally.values())
    total_findings = len(report.findings)

    intake_top = 300
    intake_stride = 50
    intake_h = 110 + len(IntakeCode) * intake_stride
    grid_top = intake_top + intake_h + 46
    col_w = 210
    row_h = 86
    grid_h = 150 + len(kinds) * row_h + 60
    rule_top = grid_top + grid_h + 40
    height = rule_top + 200

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "TWO DISTRIBUTIONAL VIEWS", 26, VIOLET, "700"),
        _text(
            110, 140, "How input was handled, and where the states sit", 40, INK, "700"
        ),
        _text(
            110,
            186,
            f"The worked seven-input example assessed against the live registry: {total_events} intake",
            22,
            MUTED,
        ),
        _text(
            110,
            216,
            f"events became {total_findings} findings, one per record.",
            22,
            MUTED,
        ),
        _text(
            110,
            264,
            f"COMPUTED THROUGH assess_absence · REVIEW DATE {WORKED_AS_OF} · COUNTS DESCRIBE INPUT HANDLING, NOT ANY PERSON OR WORK",
            18,
            TEAL,
            "700",
        ),
        _rect(110, intake_top, 1380, intake_h, PANEL, LINE, 2),
        _text(
            142, intake_top + 46, "INTAKE EVENTS BY CODE — events_tally", 21, VIOLET, "700"
        ),
        _text(
            142, intake_top + 78, "every code is reported, including zeros", 18, MUTED
        ),
    ]
    # Upper panel: one bar per intake code, scaled by the live count.
    bar_x = 640
    for index, code in enumerate(IntakeCode):
        y = intake_top + 130 + index * intake_stride
        count = tally[code]
        color = OCHRE if count else MUTED
        parts.append(_text(160, y + 6, code.value, 19, color, "700"))
        if count:
            parts.append(
                f'<rect x="{bar_x}" y="{y - 14}" width="{count * 240}" height="26" fill="{color}" opacity="0.8"/>'
            )
        else:
            parts.append(
                f'<rect x="{bar_x}" y="{y - 14}" width="10" height="26" fill="none" stroke="{color}" stroke-width="2"/>'
            )
        parts.append(
            _text(
                bar_x + max(count * 240, 10) + 16, y + 6, str(count), 19, color, "700"
            )
        )
    # Lower panel: the kind-by-state grid with live row and column sums.
    parts.append(_rect(110, grid_top, 1380, grid_h, PANEL, LINE, 2))
    parts.append(
        _text(
            142,
            grid_top + 46,
            "FINDINGS BY KIND × STATE — coverage_matrix",
            21,
            VIOLET,
            "700",
        )
    )
    parts.append(
        _text(
            142,
            grid_top + 78,
            "row sums = registry partition · column sums = report tally",
            18,
            MUTED,
        )
    )
    grid_x = 470
    header_y = grid_top + 132
    for index, state in enumerate(states):
        parts.append(
            _text(
                grid_x + index * col_w,
                header_y,
                state.value,
                18,
                _STATE_COLOR[state],
                "700",
            )
        )
    parts.append(
        _text(grid_x + len(states) * col_w, header_y, "row sum", 18, INK, "700")
    )
    for index, kind in enumerate(kinds):
        y = header_y + 24 + index * row_h
        row = matrix[kind]
        parts.append(_text(142, y + 56, kind.value, 20, _KIND_COLOR[kind], "700"))
        for column, state in enumerate(states):
            x = grid_x + column * col_w
            count = row[state]
            color = _STATE_COLOR[state] if count else MUTED
            parts.append(
                _rect(
                    x, y, 190, 80, CREAM if count else PANEL, color, 3 if count else 1
                )
            )
            parts.append(_text(x + 82, y + 54, str(count), 22, color, "700"))
        parts.append(
            _text(
                grid_x + len(states) * col_w + 20,
                y + 54,
                str(sum(row.values())),
                20,
                INK,
                "700",
            )
        )
    sum_y = header_y + 24 + len(kinds) * row_h
    parts.append(_text(142, sum_y + 40, "column sum", 19, INK, "700"))
    for column, state in enumerate(states):
        col_total = sum(matrix[kind][state] for kind in kinds)
        parts.append(
            _text(
                grid_x + column * col_w + 82,
                sum_y + 40,
                str(col_total),
                20,
                _STATE_COLOR[state],
                "700",
            )
        )
    parts.append(
        _text(
            grid_x + len(states) * col_w + 20,
            sum_y + 40,
            str(total_findings),
            22,
            VIOLET,
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
                "An event count is audit data about input handling, never a verdict on whoever supplied the input.",
                20,
                INK,
            ),
            _text(
                140,
                rule_top + 122,
                "No cell is a completeness or coverage score; a zero is an absence of the event, not evidence about the world.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)
