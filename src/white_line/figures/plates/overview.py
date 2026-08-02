"""Render overview plates without extending the ledger's assessment semantics."""

from __future__ import annotations

from ...model import AbsenceKind, AbsenceState
from ...protocol import review_action_for_state
from ...registry import WHITE_RECORDS
from ...serialization import registry_digest
from ...version import __version__

from ..canvas import open_canvas as _open, rect as _rect, text as _text
from ..palette import (
    CHARCOAL,
    INK,
    KIND_COLOR as _KIND_COLOR,
    KIND_GLOSS as _KIND_GLOSS,
    KIND_GUARD as _KIND_GUARD,
    KIND_TITLE as _KIND_TITLE,
    LINE,
    MUTED,
    OCHRE,
    PANEL,
    PAPER,
    SIENNA,
    STATE_COLOR as _STATE_COLOR,
    TEAL,
    VIOLET,
    CREAM,
)


def live_kinds() -> list[AbsenceKind]:
    """Return the live kind alphabet, refusing an incomplete display map.

    Every kind-keyed plate reads its columns from here rather than from a
    hand-written list, so a new or renamed ``AbsenceKind`` member fails the
    build instead of being silently dropped off the right-hand edge of a
    fixed column layout.
    """

    kinds = list(AbsenceKind)
    for display_map in (_KIND_TITLE, _KIND_GUARD, _KIND_GLOSS, _KIND_COLOR):
        if set(kinds) != set(display_map):
            raise ValueError(
                "kind display maps must cover exactly the AbsenceKind members"
            )
    return kinds


def column_positions(count: int, left: int, right: int, column_width: int) -> list[int]:
    """Spread ``count`` equal columns across ``left``–``right``.

    Positions are computed from the live member count rather than zipped
    against a fixed tuple of coordinates. A zip truncates silently, which is
    how a whole kind could vanish from a plate whose own header still counted
    it.
    """

    if count < 2:
        return [left]
    stride = (right - column_width - left) // (count - 1)
    return [left + index * stride for index in range(count)]


def cover_art() -> str:
    """Build a reproducible charcoal-like cover plate with a literal open line."""

    width, height = 1600, 1000
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
    ]
    # Congested graphite marks represent the pressure to complete a story.
    for index in range(22):
        x = 38 + index * 68
        y = 115 + (index % 5) * 34
        parts.append(
            f'<path d="M{x} {y + 690} C {x + 80} {y + 520}, {x - 20} {y + 260}, {x + 110} {y}" '
            f'fill="none" stroke="{CHARCOAL}" stroke-width="{3 + index % 4}" opacity="{0.22 + (index % 4) * 0.06}" '
            'stroke-linecap="round"/>'
        )
    for index in range(18):
        x = 470 + index * 64
        parts.append(
            f'<path d="M{x} 150 L {x - 150} 820" fill="none" stroke="{CHARCOAL}" '
            f'stroke-width="{2 + index % 3}" opacity="{0.18 + (index % 3) * 0.06}" stroke-linecap="round"/>'
        )
    # A bright, irregular aperture: the boundary is an opening, not an object.
    parts.extend(
        [
            f'<path d="M258 206 C 418 116, 560 184, 706 164 C 900 136, 1054 204, 1236 174 C 1394 148, 1476 296, 1386 432 C 1318 536, 1384 686, 1218 766 C 1046 850, 900 754, 730 818 C 554 884, 380 824, 270 700 C 178 596, 140 362, 258 206 Z" fill="{CREAM}" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>',
            f'<path d="M150 604 C 328 478, 492 536, 668 448 S 1014 316, 1450 402" fill="none" stroke="{SIENNA}" stroke-width="13" stroke-linecap="round"/>',
            f'<path d="M116 316 C 344 246, 488 342, 650 310 S 1038 224, 1490 300" fill="none" stroke="{VIOLET}" stroke-width="12" stroke-linecap="round"/>',
            f'<path d="M272 748 C 444 658, 594 782, 764 710 S 1050 632, 1328 714" fill="none" stroke="{TEAL}" stroke-width="8" stroke-linecap="round"/>',
            f'<path d="M730 166 C 680 294, 754 396, 716 512 S 768 690, 730 818" fill="none" stroke="{INK}" stroke-width="4" stroke-dasharray="4 18" stroke-linecap="round"/>',
            f'<path d="M278 842 C 410 892, 580 876, 720 902 S 1030 918, 1290 856" fill="none" stroke="{CHARCOAL}" stroke-width="5" stroke-linecap="round"/>',
        ]
    )
    # Eleven ledger marks keep the art visibly tethered to the live registry.
    for index in range(len(WHITE_RECORDS)):
        x = 294 + index * 92
        parts.append(
            f'<path d="M{x} 884 L {x + 14} 914" stroke="{SIENNA if index % 2 else VIOLET}" stroke-width="4" stroke-linecap="round"/>'
        )
    parts.extend(
        [
            _text(1288, 942, f"WHITE LINE · {__version__}", 20, CHARCOAL, "700"),
            "</svg>",
        ]
    )
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Figure 1: scholarship translated into design guardrails.
def scholarship_map() -> str:
    """Draw the bounded scholarship-to-design translation matrix."""

    streams = [
        (
            "SITUATED KNOWLEDGE",
            "Haraway · Harding",
            "where is the account located?",
            "record date and provenance;",
            "ask about position",
            TEAL,
        ),
        (
            "PRODUCED IGNORANCE",
            "Proctor · Schiebinger · Mills · McGoey",
            "how was the gap made or maintained?",
            "name provenance;",
            "do not infer motive",
            OCHRE,
        ),
        (
            "MISSINGNESS",
            "Rubin · Little",
            "what mechanism would justify inference?",
            "do not impute a mechanism:",
            "not MCAR, MAR, or MNAR",
            SIENNA,
        ),
        (
            "CLASSIFICATION",
            "Bowker · Star · D'Ignazio · Klein",
            "what does this category expose or hide?",
            "version the registry;",
            "do not call it neutral",
            TEAL,
        ),
        (
            "JUSTICE + RESISTANCE",
            "Fricker · Dotson · Medina",
            "who can participate as a knower?",
            "a state label is not authority,",
            "diagnosis, or a verdict",
            VIOLET,
        ),
        (
            "REFUSAL + OPACITY",
            "Tuck · Simpson · Nissenbaum · Glissant",
            "who bears the cost of completion?",
            "access is not entitlement;",
            "refusal is not a deficit",
            VIOLET,
        ),
        (
            "DISCIPLINED RESTRAINT",
            "Nāgārjuna · Wittgenstein · Keats · Cage",
            "what should remain unasserted?",
            "open space is not a hidden cause;",
            "a remainder stays unsaid",
            SIENNA,
        ),
    ]
    row_h = 132
    top = 330
    rows_bottom = top + len(streams) * row_h
    block_top = rows_bottom + 26
    height = block_top + 280
    parts = _open(1600, height)
    parts += [
        _text(110, 88, "SCHOLARSHIP → DESIGN", 26, VIOLET, "700"),
        _text(110, 140, "Seven conversations, one bounded translation", 40, INK, "700"),
        _text(
            110,
            184,
            "White Line does not turn distinct literatures into one theory.",
            22,
            MUTED,
        ),
        _text(
            110,
            214,
            "It asks what each prevents a small absence ledger from erasing or exposing.",
            22,
            MUTED,
        ),
        _text(
            110,
            262,
            "NOT AN EXHAUSTIVE LITERATURE REVIEW · CONSTRAINTS IN, LIMITED OPERATIONS OUT",
            18,
            TEAL,
            "700",
        ),
        _text(300, 312, "FIELD, SOURCES, AND THE QUESTION FORCED", 18, VIOLET, "700"),
        _text(950, 312, "WHITE LINE RESPONSE (LIMITED)", 18, VIOLET, "700"),
    ]
    for index, (title, sources, question, response, response_two, color) in enumerate(
        streams
    ):
        y = top + index * row_h
        parts.extend(
            [
                _rect(
                    110, y, 1380, row_h - 16, PANEL if index % 2 == 0 else CREAM, LINE, 1
                ),
                f'<path d="M140 {y + 66} C 178 {y + 40}, 224 {y + 92}, 274 {y + 64}" fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round"/>',
                _text(300, y + 42, title, 21, color, "700"),
                _text(300, y + 74, sources, 18, MUTED),
                _text(300, y + 108, question, 20, INK),
                _text(950, y + 46, response, 19, INK),
                _text(950, y + 76, response_two, 19, INK),
                _text(950, y + 108, "reviewer responsibility", 18, color, "700"),
            ]
        )
    parts.extend(
        [
            _rect(110, block_top, 1380, 168, CREAM, INK, 3),
            _text(140, block_top + 44, "IMPLEMENTED THIN SLICE", 20, VIOLET, "700"),
            _text(180, block_top + 100, "TYPE", 28, TEAL, "700"),
            _text(180, block_top + 138, "what kind of limit", 18, MUTED),
            _text(620, block_top + 100, "BOUND", 28, OCHRE, "700"),
            _text(620, block_top + 138, "what must not be inferred", 18, MUTED),
            _text(1060, block_top + 100, "REVISIT", 28, VIOLET, "700"),
            _text(1060, block_top + 138, "what changed context reopens", 18, MUTED),
            _text(
                110,
                block_top + 226,
                "The literature supplies reasons for restraint; the package supplies a bounded trace,",
                20,
                INK,
            ),
            _text(
                110,
                block_top + 258,
                "not a theory of justice or a detector of hidden causes.",
                20,
                INK,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Figure 1: three absence layers (retained, code-derived from the kinds).
def absence_layers() -> str:
    """Draw one panel per ``AbsenceKind`` member from the shared kind maps.

    Titles, colors, glosses, and guard clauses come from the module-level
    kind maps (the same ``_KIND_GLOSS`` the taxonomy and atlas draw from);
    each panel's record count and review-horizon range are read from the
    live registry. A new or renamed kind fails this build instead of
    silently drifting.
    """

    kinds = live_kinds()
    grouped = {
        kind: [record for record in WHITE_RECORDS if record.kind is kind]
        for kind in kinds
    }
    column_w = 420
    xs = column_positions(len(kinds), 150, 1490, column_w)
    panel_top = 310
    panel_h = 400
    parts = _open(1600, 1080)
    parts += [
        _text(110, 90, "THE WHITE LINE", 26, VIOLET, "700"),
        _text(
            110, 142, "Absence needs a type before it needs an answer", 42, INK, "700"
        ),
        _text(
            110,
            188,
            "An absence ledger keeps gaps, restraint, and negative space",
            22,
            MUTED,
        ),
        _text(110, 218, "from collapsing into one unsupported claim.", 22, MUTED),
        _text(
            110,
            268,
            f"DRAWN FROM THE KIND VOCABULARY AND THE {len(WHITE_RECORDS)}-RECORD REGISTRY · NOT EVIDENCE OF A CAUSE",
            18,
            TEAL,
            "700",
        ),
        f'<rect x="110" y="{panel_top}" width="1380" height="{panel_h}" fill="none" stroke="{LINE}" stroke-width="2"/>',
    ]
    for index in range(1, len(kinds)):
        divider = xs[index] - 30
        parts.append(
            f'<line x1="{divider}" y1="{panel_top}" x2="{divider}" y2="{panel_top + panel_h}" stroke="{LINE}" stroke-width="2"/>'
        )
    for kind, x in zip(kinds, xs, strict=True):
        color = _KIND_COLOR[kind]
        records = grouped[kind]
        horizons = sorted(record.review_horizon_days for record in records)
        parts.extend(
            [
                f'<circle cx="{x + 34}" cy="{panel_top + 60}" r="26" fill="{PAPER}" stroke="{color}" stroke-width="7"/>',
                f'<circle cx="{x + 34}" cy="{panel_top + 60}" r="7" fill="{color}"/>',
                _text(x, panel_top + 138, _KIND_TITLE[kind], 21, color, "700"),
                _text(x, panel_top + 170, kind.value, 18, MUTED, "700"),
                _text(x, panel_top + 212, _KIND_GLOSS[kind], 18, INK),
                _text(x, panel_top + 248, _KIND_GUARD[kind], 18, MUTED),
                _text(
                    x,
                    panel_top + 296,
                    f"{len(records)} registry records",
                    18,
                    color,
                    "700",
                ),
                _text(
                    x,
                    panel_top + 326,
                    f"horizons {horizons[0]}–{horizons[-1]} days",
                    18,
                    color,
                    "700",
                ),
                _text(
                    x,
                    panel_top + 370,
                    "record state, do not fill the gap",
                    18,
                    color,
                    "700",
                ),
            ]
        )
    parts.extend(
        [
            f'<path d="M180 848 C 380 798, 520 898, 760 838 S 1170 788, 1420 868" fill="none" stroke="{LINE}" stroke-width="3" stroke-dasharray="2 18" stroke-linecap="round"/>',
            _text(110, 800, "ABSENCE IS NOT EVIDENCE", 24, INK, "700"),
            _text(110, 916, "READING RULE", 18, VIOLET, "700"),
            _text(
                110,
                956,
                "Name what is missing, why it is missing if that is known, and what the record must not imply.",
                20,
                INK,
            ),
            _text(
                110,
                1000,
                "White Line marks limits of knowledge and obligation; it does not assert",
                19,
                MUTED,
            ),
            _text(110, 1030, "a literal invisible causal force.", 19, MUTED),
            "</svg>",
        ]
    )
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Figure 2: registry taxonomy — every record, grouped by kind.
def registry_taxonomy() -> str:
    """Draw every live registry record grouped by its declared kind.

    Columns, the header's kind count, and the canvas height are all derived
    from the live alphabet and the live registry, so a fourth kind or a
    longer column changes the plate instead of falling off it.
    """

    kinds = live_kinds()
    grouped: dict[AbsenceKind, list] = {kind: [] for kind in kinds}
    for record in WHITE_RECORDS:
        grouped[record.kind].append(record)

    col_w = 440
    xs = column_positions(len(kinds), 110, 1490, col_w)
    top = 310
    record_stride = 150
    panel_heights = [200 + len(grouped[kind]) * record_stride for kind in kinds]
    footer_top = top + max(panel_heights) + 60
    height = footer_top + 100

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE WHITE LINE REGISTRY", 26, VIOLET, "700"),
        _text(
            110,
            140,
            f"{len(WHITE_RECORDS)} absence records across {len(kinds)} kinds",
            40,
            INK,
            "700",
        ),
        _text(
            110,
            186,
            "Finite, versioned, and deliberate: each record names one bounded gap,",
            22,
            MUTED,
        ),
        _text(110, 216, "restraint, or negative space.", 22, MUTED),
        _text(
            110,
            266,
            "GENERATED FROM THE VERSIONED ABSENCE REGISTRY · NOT A COMPLETENESS SCORE",
            18,
            TEAL,
            "700",
        ),
    ]
    for kind, x, panel_h in zip(kinds, xs, panel_heights, strict=True):
        color = _KIND_COLOR[kind]
        records = grouped[kind]
        parts.append(_rect(x, top, col_w, panel_h, PANEL, LINE, 2))
        parts.append(
            f'<rect x="{x}" y="{top}" width="{col_w}" height="8" fill="{color}"/>'
        )
        parts.append(_text(x + 24, top + 56, kind.value, 24, color, "700"))
        parts.append(_text(x + 24, top + 92, _KIND_GLOSS[kind], 18, MUTED))
        parts.append(
            _text(x + 24, top + 128, f"{len(records)} records", 18, color, "700")
        )
        y = top + 196
        for record in records:
            parts.append(f'<circle cx="{x + 32}" cy="{y - 7}" r="7" fill="{color}"/>')
            parts.append(_text(x + 52, y, record.title, 19, INK, "700"))
            parts.append(_text(x + 52, y + 32, f"id: {record.id}", 18, MUTED))
            parts.append(
                _text(
                    x + 52,
                    y + 62,
                    f"review horizon: {record.review_horizon_days} days",
                    18,
                    color,
                    "700",
                )
            )
            y += record_stride
    parts.extend(
        [
            _text(
                110,
                footer_top,
                "A record's presence names a category worth reviewing; it is never a claim",
                20,
                MUTED,
            ),
            _text(
                110,
                footer_top + 32,
                "that the category is populated in any given work.",
                20,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


# --------------------------------------------------------------------------- #
# Figure 3: the review atlas — a compact view of the whole instrument.
def review_atlas() -> str:
    """Draw one compact view of the registry, assessor, and review loop.

    The three panels are sized from the live kind and state alphabets, so a
    new member lengthens a column instead of being dropped while the header
    keeps counting it.
    """

    digest = registry_digest(WHITE_RECORDS)[:8]
    kinds = live_kinds()
    states = list(AbsenceState)
    kind_stride = 152
    state_stride = 122
    panel_top = 310
    panel_h = max(
        190 + len(kinds) * kind_stride,
        150 + len(states) * state_stride + 150,
        700,
    )
    footer_top = panel_top + panel_h + 56
    height = footer_top + 130

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE REVIEW ATLAS", 26, VIOLET, "700"),
        _text(
            110,
            140,
            "From a missing context to a bounded next question",
            40,
            INK,
            "700",
        ),
        _text(
            110,
            186,
            "A small instrument with a deliberately visible boundary: type the gap,",
            22,
            MUTED,
        ),
        _text(
            110, 216, "reconcile the record, then choose a human next step.", 22, MUTED
        ),
        _text(
            110,
            266,
            f"{len(WHITE_RECORDS)} REGISTRY RECORDS · {len(kinds)} KINDS · {len(states)} STATES · DIGEST {digest}",
            18,
            TEAL,
            "700",
        ),
        _rect(110, panel_top, 480, panel_h, PANEL, LINE, 2),
        _rect(630, panel_top, 420, panel_h, PANEL, LINE, 2),
        _rect(1090, panel_top, 400, panel_h, PANEL, LINE, 2),
        _text(140, panel_top + 52, "1 · TYPE THE LIMIT", 20, VIOLET, "700"),
        _text(
            140, panel_top + 86, "Different absences need different duties.", 18, MUTED
        ),
        _text(660, panel_top + 52, "2 · RECONCILE THE RECORD", 20, VIOLET, "700"),
        _text(
            660, panel_top + 86, "Intake leaves a trace; caution only rises.", 18, MUTED
        ),
        _text(1118, panel_top + 52, "3 · OPEN THE NEXT STEP", 20, VIOLET, "700"),
        _text(1118, panel_top + 86, "Follow up without certifying.", 18, MUTED),
        f'<path d="M590 {panel_top + 320} C 608 {panel_top + 262}, 614 {panel_top + 262}, 630 {panel_top + 320}" fill="none" stroke="{TEAL}" stroke-width="4" stroke-linecap="round"/>',
        f'<path d="M1050 {panel_top + 320} C 1068 {panel_top + 262}, 1074 {panel_top + 262}, 1090 {panel_top + 320}" fill="none" stroke="{OCHRE}" stroke-width="4" stroke-linecap="round"/>',
    ]
    y = panel_top + 160
    for kind in kinds:
        color = _KIND_COLOR[kind]
        parts.extend(
            [
                f'<path d="M146 {y - 22} C 190 {y - 48}, 230 {y + 6}, 268 {y - 22}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round"/>',
                f'<circle cx="150" cy="{y + 30}" r="11" fill="{PAPER}" stroke="{color}" stroke-width="4"/>',
                _text(178, y + 37, kind.value, 20, color, "700"),
                _text(140, y + 72, _KIND_GLOSS[kind], 18, INK),
            ]
        )
        y += kind_stride
    stage_top = panel_top + 170
    parts.extend(
        [
            _text(
                140, panel_top + panel_h - 76, "The kind is a scope boundary,", 18, MUTED
            ),
            _text(140, panel_top + panel_h - 44, "not a severity score.", 18, MUTED),
            _rect(660, stage_top, 360, 96, CREAM, TEAL, 3),
            _text(684, stage_top + 40, "INTAKE", 20, TEAL, "700"),
            _text(684, stage_top + 74, "screen and record why", 18, INK),
            f'<path d="M840 {stage_top + 96} C 808 {stage_top + 124}, 808 {stage_top + 152}, 840 {stage_top + 180}" fill="none" stroke="{LINE}" stroke-width="3" stroke-dasharray="3 12" stroke-linecap="round"/>',
            _rect(660, stage_top + 190, 360, 96, CREAM, OCHRE, 3),
            _text(684, stage_top + 230, "MATCH", 20, OCHRE, "700"),
            _text(684, stage_top + 264, "one record, cautious merge", 18, INK),
            f'<path d="M840 {stage_top + 286} C 808 {stage_top + 314}, 808 {stage_top + 342}, 840 {stage_top + 370}" fill="none" stroke="{LINE}" stroke-width="3" stroke-dasharray="3 12" stroke-linecap="round"/>',
            _rect(660, stage_top + 380, 360, 82, CREAM, VIOLET, 3),
            _text(684, stage_top + 432, "SCORE → one state", 20, VIOLET, "700"),
            _text(
                660,
                panel_top + panel_h - 76,
                "The report keeps its review date,",
                18,
                MUTED,
            ),
            _text(
                660,
                panel_top + panel_h - 44,
                "digest, and typed intake events.",
                18,
                MUTED,
            ),
        ]
    )
    y = panel_top + 156
    for state in states:
        color = _STATE_COLOR[state]
        action = review_action_for_state(state).value
        parts.extend(
            [
                f'<circle cx="1128" cy="{y - 6}" r="8" fill="{color}"/>',
                _text(1150, y, state.value, 19, color, "700"),
                _text(1118, y + 34, action, 18, INK),
            ]
        )
        y += state_stride
    parts.extend(
        [
            f'<path d="M1118 {panel_top + panel_h - 132} C 1186 {panel_top + panel_h - 168}, 1286 {panel_top + panel_h - 98}, 1396 {panel_top + panel_h - 140}" fill="none" stroke="{VIOLET}" stroke-width="4" stroke-linecap="round"/>',
            _text(1118, panel_top + panel_h - 76, "HUMAN REVIEW", 18, VIOLET, "700"),
            _text(
                1118,
                panel_top + panel_h - 44,
                "A next question is not approval.",
                18,
                INK,
            ),
            _rect(110, footer_top, 1380, 100, CREAM, INK, 2),
            _text(140, footer_top + 42, "READING RULE", 18, VIOLET, "700"),
            _text(
                140,
                footer_top + 78,
                "The instrument tells us where to look again; it does not tell us what a hidden cause is.",
                20,
                INK,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)
