"""Render contract plates without changing the review protocol."""

from __future__ import annotations

from ...analysis import reconciliation_matrix
from ...model import AbsenceState, IntakeCode, caution_rank
from ...protocol import requires_follow_up, review_action_for_state

from ..canvas import open_canvas as _open, rect as _rect, text as _text
from ..palette import (
    DATED_INPUT_GLOSS as _DATED_INPUT_GLOSS,
    INK,
    INTAKE_SET_ASIDE_GLOSS as _INTAKE_SET_ASIDE_GLOSS,
    LINE,
    MATCH_STAGE_GLOSS as _MATCH_STAGE_GLOSS,
    MUTED,
    OCHRE,
    PANEL,
    PAPER,
    STATE_COLOR as _STATE_COLOR,
    STATE_GLOSS as _STATE_GLOSS,
    TEAL,
    VIOLET,
)

#: The scoring branches, drawn as one panel each. The second gloss line keeps
#: every label inside its panel at the legibility floor rather than running a
#: single long string off the edge.
_SCORE_BRANCHES: tuple[tuple[AbsenceState, str, str, str], ...] = (
    (AbsenceState.NAMED, "dated naming", "within horizon", ""),
    (
        AbsenceState.UNRESOLVED,
        "named-but-open, or a",
        "naming past its horizon",
        "staleness decay",
    ),
    (AbsenceState.WITHHELD, "intentionally", "not disclosed", "names its duty"),
    (AbsenceState.NOT_RECORDED, "no observation", "supplied", "ledger-reserved"),
)


def state_machine() -> str:
    """Draw the staged decision path with categories named by ``IntakeCode``.

    The set-aside, dating, and match panels iterate the live enumeration
    through module-level gloss maps; the coverage check below makes a new or
    renamed intake code fail this build instead of silently drifting from
    the manuscript's intake-stage rules. The intake stage is a stacked list rather than a
    row of small boxes so each code and gloss stays legible in print.
    """

    covered = (
        set(_INTAKE_SET_ASIDE_GLOSS) | set(_DATED_INPUT_GLOSS) | set(_MATCH_STAGE_GLOSS)
    )
    if covered != set(IntakeCode):
        raise ValueError(
            "intake-code gloss maps must cover exactly the IntakeCode members"
        )
    intake_top = 300
    intake_stride = 58
    intake_h = 90 + len(_INTAKE_SET_ASIDE_GLOSS) * intake_stride
    match_top = intake_top + intake_h + 40
    date_top = match_top + 150
    score_top = date_top + 190
    score_h = 210
    decay_y = score_top + score_h + 70
    rule_top = decay_y + 40
    height = rule_top + 220

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE STAGED ASSESSOR", 26, VIOLET, "700"),
        _text(110, 140, "Intake, then dating, matching, and scoring", 40, INK, "700"),
        _text(
            110,
            186,
            "Every set-aside input leaves a typed note; a conflict resolves toward the",
            22,
            MUTED,
        ),
        _text(110, 216, "more cautious state; nothing is dropped silently.", 22, MUTED),
    ]
    # Stage 1: intake — one row per set-aside IntakeCode member.
    parts.append(_rect(110, intake_top, 1380, intake_h, PANEL, LINE, 2))
    parts.append(
        _text(
            140,
            intake_top + 44,
            "1 · INTAKE — set aside what cannot be trusted (with a typed note)",
            21,
            TEAL,
            "700",
        )
    )
    for index, (code, gloss) in enumerate(_INTAKE_SET_ASIDE_GLOSS.items()):
        y = intake_top + 88 + index * intake_stride
        parts.append(
            f'<rect x="140" y="{y - 22}" width="1320" height="{intake_stride - 12}" fill="{PAPER}" stroke="{LINE}" stroke-width="1"/>'
        )
        parts.append(_text(164, y + 8, code.value, 19, OCHRE, "700"))
        parts.append(_text(600, y + 8, gloss, 19, INK))
    # Stage 2: matching — the typed trace codes come from the same enumeration.
    parts.append(_rect(110, match_top, 1380, 130, PANEL, LINE, 2))
    parts.append(
        _text(
            140,
            match_top + 44,
            "2 · MATCH — keep at most one observation per record",
            21,
            TEAL,
            "700",
        )
    )
    parts.append(
        _text(
            140,
            match_top + 78,
            "conflicting states for one record resolve toward the more cautious (higher caution rank)",
            19,
            MUTED,
        )
    )
    match_gloss = " · ".join(
        f"{code.value} {gloss}" for code, gloss in _MATCH_STAGE_GLOSS.items()
    )
    parts.append(
        _text(140, match_top + 110, f"typed match events: {match_gloss}", 18, OCHRE, "700")
    )
    # Stage 3: dating — a non-ISO object remains accepted but cannot age.
    parts.append(_rect(110, date_top, 1380, 120, PANEL, LINE, 2))
    parts.append(
        _text(
            140,
            date_top + 44,
            "3 · DATE — retain ISO dates for staleness accounting",
            21,
            TEAL,
            "700",
        )
    )
    dating_gloss = " · ".join(
        f"{code.value} {gloss}" for code, gloss in _DATED_INPUT_GLOSS.items()
    )
    parts.append(
        _text(140, date_top + 84, f"typed dating event: {dating_gloss}", 19, OCHRE, "700")
    )
    # Stage 4: scoring → one panel per ledger state.
    parts.append(
        _text(
            140,
            score_top - 30,
            "4 · SCORE — assign one ledger state per record",
            21,
            TEAL,
            "700",
        )
    )
    for index, (state, gloss_one, gloss_two, tag) in enumerate(_SCORE_BRANCHES):
        bx = 110 + index * 350
        color = _STATE_COLOR[state]
        parts.append(_rect(bx, score_top, 320, score_h, PAPER, color, 3))
        parts.append(
            f'<rect x="{bx}" y="{score_top}" width="320" height="8" fill="{color}"/>'
        )
        parts.append(_text(bx + 20, score_top + 54, state.value, 21, color, "700"))
        parts.append(
            _text(
                bx + 20,
                score_top + 88,
                f"caution rank {caution_rank(state)}",
                18,
                MUTED,
                "700",
            )
        )
        parts.append(_text(bx + 20, score_top + 126, gloss_one, 18, INK))
        parts.append(_text(bx + 20, score_top + 154, gloss_two, 18, INK))
        if tag:
            parts.append(_text(bx + 20, score_top + 190, tag, 18, color, "700"))
    # Staleness arrow NAMED -> UNRESOLVED: labeled, and prominent by design —
    # it is the single dynamic transition the contract defines.
    parts.append(
        f'<path d="M270 {score_top + score_h + 4} C 330 {score_top + score_h + 60}, 560 {score_top + score_h + 60}, 618 {score_top + score_h + 6}" '
        f'fill="none" stroke="{OCHRE}" stroke-width="5" marker-end="url(#ar)"/>'
    )
    parts.append(
        '<defs><marker id="ar" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto">'
        f'<path d="M0 0 L6 3 L0 6 Z" fill="{OCHRE}"/></marker></defs>'
    )
    parts.append(
        _text(
            658,
            decay_y,
            "STALENESS DECAY — a dated NAMED past its review horizon reports UNRESOLVED",
            19,
            OCHRE,
            "700",
        )
    )
    parts.extend(
        [
            _rect(110, rule_top, 1380, 180, PANEL, LINE, 2),
            _text(140, rule_top + 46, "THE RULE UNDER THE DEFINED ORDER", 19, VIOLET, "700"),
            _text(
                140,
                rule_top + 86,
                "No input can make an absence look more settled than its most cautious observer reported.",
                21,
                INK,
            ),
            _text(
                140,
                rule_top + 124,
                "A dated naming older than its review horizon is reported UNRESOLVED, not NAMED.",
                19,
                MUTED,
            ),
            _text(
                140,
                rule_top + 154,
                "The ledger records state; it never infers why something is absent.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Figure 4: the caution ladder.
def caution_ladder() -> str:
    """Draw the live caution order and its reconciliation consequences."""

    ordered = sorted(AbsenceState, key=caution_rank, reverse=True)
    matrix = reconciliation_matrix()
    top = 300
    row_h = 176
    rungs_bottom = top + len(ordered) * row_h
    height = rungs_bottom + 190
    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE CAUTION ORDER", 26, VIOLET, "700"),
        _text(110, 140, "Conflicts resolve toward greater caution", 40, INK, "700"),
        _text(
            110,
            186,
            "When observers disagree, the ledger keeps the more cautious state.",
            22,
            MUTED,
        ),
        _text(110, 216, "Staleness only raises caution; it never lowers it.", 22, MUTED),
    ]
    for index, state in enumerate(ordered):
        y = top + index * row_h
        color = _STATE_COLOR[state]
        rank = caution_rank(state)
        width = 560 + rank * 150
        parts.append(_rect(110, y, width, row_h - 26, PAPER, color, 3))
        parts.append(
            f'<rect x="110" y="{y}" width="12" height="{row_h - 26}" fill="{color}"/>'
        )
        parts.append(_text(146, y + 52, state.value, 26, color, "700"))
        parts.append(_text(146, y + 90, _STATE_GLOSS[state], 19, INK))
        if state is AbsenceState.NOT_RECORDED:
            pair_note = "not assertable (ledger-reserved)"
        else:
            wins = sum(1 for kept in matrix.values() if kept is state)
            pair_note = f"kept in {wins} of {len(matrix)} ordered pairs"
        parts.append(_text(146, y + 124, f"reconciliation: {pair_note}", 18, MUTED))
        parts.append(_text(width - 20, y + 56, f"rank {rank}", 22, MUTED, "700"))
        if index < len(ordered) - 1:
            arrow_y = y + row_h - 26
            parts.append(
                f'<path d="M60 {arrow_y + 26} L 60 {y + 6}" fill="none" stroke="{MUTED}" '
                'stroke-width="3" marker-end="url(#up)"/>'
            )
    parts.append(
        '<defs><marker id="up" markerWidth="12" markerHeight="12" refX="4" refY="2" orient="auto">'
        f'<path d="M0 6 L4 0 L8 6 Z" fill="{MUTED}"/></marker></defs>'
    )
    side_top = top + row_h + 20
    parts.extend(
        [
            _rect(1130, side_top, 360, 420, PANEL, LINE, 2),
            _text(1156, side_top + 44, "WHERE THE ORDER IS USED", 18, VIOLET, "700"),
            _text(1156, side_top + 92, "conflict lattice: a", 18, INK),
            _text(1156, side_top + 120, "disagreement keeps", 18, INK),
            _text(1156, side_top + 148, "the higher rung", 18, INK),
            _text(1156, side_top + 200, "decay timeline: an aged", 18, INK),
            _text(1156, side_top + 228, "naming moves up, never down", 18, INK),
            _text(1156, side_top + 280, "this ladder draws the order", 18, MUTED),
            _text(1156, side_top + 308, "itself, not those rules", 18, MUTED),
            _text(1156, side_top + 356, "pair counts read live from", 18, MUTED),
            _text(1156, side_top + 384, "reconciliation_matrix", 18, MUTED),
            _text(110, rungs_bottom + 26, "MORE CAUTIOUS ↑", 19, VIOLET, "700"),
            _text(
                110,
                rungs_bottom + 68,
                "Withholding outranks an open question, which outranks a settled naming, which outranks silence.",
                21,
                INK,
            ),
            _text(
                110,
                rungs_bottom + 110,
                "The order is a discipline, not a severity score: a higher rung means more restraint, not more danger.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Figure 5: bounded human follow-up, derived from the review protocol.
def review_protocol() -> str:
    """Draw the bounded follow-up action assigned to each ledger state."""

    states = list(AbsenceState)
    top = 300
    row_h = 156
    rows_bottom = top + len(states) * row_h
    rule_top = rows_bottom + 34
    height = rule_top + 220
    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE REVIEW PROTOCOL", 26, VIOLET, "700"),
        _text(110, 140, "A state opens a bounded next step", 40, INK, "700"),
        _text(
            110,
            186,
            "The protocol describes follow-up; it never returns permission,",
            22,
            MUTED,
        ),
        _text(110, 216, "compliance, or proof of safety.", 22, MUTED),
        _text(
            110,
            264,
            "DERIVED FROM THE STATE ENUMERATION AND REVIEW DIRECTIVES · HUMAN JUDGMENT REMAINS REQUIRED",
            18,
            TEAL,
            "700",
        ),
    ]
    for index, state in enumerate(states):
        y = top + index * row_h
        color = _STATE_COLOR[state]
        action = review_action_for_state(state).value
        follow_up = "FOLLOW UP" if requires_follow_up(state) else "RETAIN SCOPE"
        parts.extend(
            [
                _rect(110, y, 1380, row_h - 20, PAPER, color, 3),
                f'<rect x="110" y="{y}" width="14" height="{row_h - 20}" fill="{color}"/>',
                _text(158, y + 54, state.value, 24, color, "700"),
                _text(158, y + 96, action, 19, INK, "700"),
                _text(820, y + 54, follow_up, 19, color, "700"),
                _text(820, y + 96, _STATE_GLOSS[state], 19, MUTED),
            ]
        )
    parts.extend(
        [
            _rect(110, rule_top, 1380, 150, PANEL, LINE, 2),
            _text(140, rule_top + 44, "READING RULE", 19, VIOLET, "700"),
            _text(
                140,
                rule_top + 84,
                "Every state remains local evidence about the record, not a finding about hidden causes, people, or safety.",
                20,
                INK,
            ),
            _text(
                140,
                rule_top + 122,
                "Re-run after material context changes; preserve the report date and registry digest with the review record.",
                19,
                MUTED,
            ),
            _text(
                110,
                rule_top + 200,
                "A responsible protocol makes the next question visible without pretending the instrument can answer it.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)
