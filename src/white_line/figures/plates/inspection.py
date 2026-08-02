"""Render inspection plates: the refresh queue, horizon dispersion, and battery.

Each plate here reads a live computation — ``expiry_horizon`` over a shared
worked report, the registry's own horizons, or the intake battery — and draws
what it finds. No count, day, or message in these plates is a literal.
"""

from __future__ import annotations

from collections.abc import Container, Iterable
from statistics import median

from ...analysis import expiry_horizon
from ...dates import coerce_date, usable_observation_date
from ...model import AbsenceObservation, AbsenceState, WhiteReport
from ...registry import WHITE_RECORDS
from ...worked_examples import (
    EXPIRY_AS_OF,
    WORKED_AS_OF,
    expiry_observations,
    expiry_report,
    intake_reachability_battery,
)

from ..metrics import advance_width as _advance
from ..canvas import (
    marker as _marker,
    open_canvas as _open,
    rect as _rect,
    text as _text,
    wrap_lines as _wrap,
)
from ..palette import (
    INK,
    KIND_COLOR as _KIND_COLOR,
    KIND_MARKER as _KIND_MARKER,
    LINE,
    MUTED,
    OCHRE,
    PANEL,
    STATE_COLOR as _STATE_COLOR,
    TEAL,
    VIOLET,
    CREAM,
)

from .overview import live_kinds

#: The two omissions ``expiry_horizon`` documents, with the reason each one
#: is not a queue entry. Drawing them as labelled bands rather than dropping
#: them is the point: an omitted record is exactly the thing this instrument
#: exists to keep visible.
_UNDATED_BAND = "UNDATED NAMING — cannot expire, so it never enters the queue"
_DECAYED_BAND = "ALREADY DECAYED — past its horizon, so the ledger reports UNRESOLVED"


def _record_titles() -> dict[str, str]:
    """Map record id to title for labelling, read from the live registry."""

    return {record.id: record.title for record in WHITE_RECORDS}


def omitted_namings(
    report: WhiteReport,
    observations: Iterable[AbsenceObservation],
    queued_ids: Container[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split the namings ``expiry_horizon`` left out into the two bands.

    Only a supplied ``NAMED`` observation can be an omitted *naming*: an
    observation a reviewer asserted as ``UNRESOLVED`` or ``WITHHELD`` was never
    a naming and never entered the queue's population, so drawing it under
    "already decayed" would misreport what the ledger did. The band split is
    therefore taken from the observation's asserted state together with the
    finding the assessor returned.

    Returns:
        Sorted ids of namings that could not be dated, and of namings the
        assessor decayed past their horizon.
    """

    undated: list[str] = []
    decayed: list[str] = []
    review_date = coerce_date(report.review_date, "report.review_date")
    for observation in observations:
        if observation.state is not AbsenceState.NAMED:
            continue
        if observation.record_id in queued_ids:
            continue
        finding = report.finding_for(observation.record_id)
        if finding is None:
            continue
        usable, _issue = usable_observation_date(finding.observed_on, review_date)
        if finding.state is AbsenceState.NAMED and usable is None:
            undated.append(observation.record_id)
        elif finding.state is AbsenceState.UNRESOLVED:
            decayed.append(observation.record_id)
    return tuple(sorted(undated)), tuple(sorted(decayed))


def expiry_queue() -> str:
    """Draw ``expiry_horizon`` as a ranked, nearest-boundary-first strip.

    The queue rows and both omission bands are derived from one live
    ``assess_absence`` report: an observation is queued when the helper
    returns it, sits in the undated band when the assessor could not use its
    date, and sits in the decayed band when its naming already aged past the
    record's horizon. The three groups therefore partition the supplied
    namings by construction, and the plate reports that partition rather than
    asserting it.
    """

    report = expiry_report()
    entries = expiry_horizon(report)
    titles = _record_titles()

    undated, decayed = omitted_namings(
        report, expiry_observations(), {entry.record_id for entry in entries}
    )

    widest = max(entry.horizon_days for entry in entries)
    bar_x, bar_w = 700, 620
    row_h = 118
    top = 340
    queue_bottom = top + len(entries) * row_h
    band_h = 104
    bands_top = queue_bottom + 60
    rule_top = bands_top + 2 * band_h + 60
    height = rule_top + 200

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE REFRESH QUEUE", 26, VIOLET, "700"),
        _text(110, 140, "Which naming comes due first", 40, INK, "700"),
        _text(
            110,
            186,
            f"expiry_horizon over one assessed report: {len(entries)} current dated namings, "
            f"ranked nearest-boundary-first.",
            22,
            MUTED,
        ),
        _text(
            110,
            216,
            "A queue position is a review cadence, not a measure of importance or risk.",
            22,
            MUTED,
        ),
        _text(
            110,
            266,
            f"COMPUTED THROUGH assess_absence · REVIEW DATE {EXPIRY_AS_OF} · A REFRESH SCHEDULE, NOT A COMPLETENESS OR SAFETY SCORE",
            18,
            TEAL,
            "700",
        ),
        _text(150, 314, "RECORD", 18, VIOLET, "700"),
        _text(bar_x, 314, "AGE AND REMAINING DAYS AGAINST THE RECORD'S HORIZON", 18, VIOLET, "700"),
    ]
    for index, entry in enumerate(entries):
        y = top + index * row_h
        color = _KIND_COLOR[entry.kind]
        parts.append(_rect(110, y, 1380, row_h - 18, PANEL if index % 2 == 0 else CREAM, LINE, 1))
        parts.append(_marker(_KIND_MARKER[entry.kind], 152, y + 44, 13, color))
        parts.append(_text(184, y + 52, titles[entry.record_id], 21, INK, "700"))
        parts.append(_text(184, y + 84, f"{entry.kind.value} · observed {entry.observed_on}", 18, color, "700"))
        span = int(bar_w * entry.horizon_days / widest)
        aged = int(span * entry.age_days / entry.horizon_days)
        parts.append(
            f'<rect x="{bar_x}" y="{y + 34}" width="{span}" height="28" fill="none" stroke="{color}" stroke-width="2"/>'
        )
        parts.append(
            f'<rect x="{bar_x}" y="{y + 34}" width="{aged}" height="28" fill="{color}" opacity="0.75"/>'
        )
        parts.append(
            _text(
                bar_x,
                y + 92,
                f"{entry.age_days} days old of {entry.horizon_days} · {entry.days_remaining} days remaining",
                18,
                INK,
            )
        )
        parts.append(_text(1400, y + 52, f"#{index + 1}", 22, MUTED, "700"))
    for offset, (band_title, ids) in enumerate(
        ((_UNDATED_BAND, undated), (_DECAYED_BAND, decayed))
    ):
        y = bands_top + offset * band_h
        parts.append(_rect(110, y, 1380, band_h - 20, CREAM, MUTED, 3))
        parts.append(
            f'<rect x="110" y="{y}" width="1380" height="8" fill="{MUTED}"/>'
        )
        parts.append(_text(140, y + 50, band_title, 19, MUTED, "700"))
        listed = ", ".join(titles[record_id] for record_id in ids) or "none in this input"
        parts.append(_text(140, y + 82, f"{len(ids)} in this input: {listed}", 18, INK))
    parts.extend(
        [
            _rect(110, rule_top, 1380, 150, CREAM, INK, 2),
            _text(140, rule_top + 44, "READING RULE", 19, VIOLET, "700"),
            _text(
                140,
                rule_top + 84,
                "The two bands are drawn, not dropped: an omitted naming is still a naming a reviewer supplied.",
                20,
                INK,
            ),
            _text(
                140,
                rule_top + 122,
                "A short remaining count means the naming is due for re-review, never that the underlying work is wrong.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


def horizon_dispersion() -> str:
    """Draw one labelled dot per record on a days axis, grouped by kind.

    Every position, median, and count is read from ``WHITE_RECORDS``. Records
    get one row each rather than sharing an axis line, so no label hides
    another and a reader can follow any single record from its name to its
    horizon.

    The reading the plate supports and the per-kind range in the layers figure
    cannot: contemplative horizons are uniform where the other two kinds are
    spread, so the ledger revisits contemplative space on one annual cadence
    while epistemic and ethical records come due on several shorter ones.
    """

    kinds = live_kinds()
    grouped = {
        kind: sorted(
            (record for record in WHITE_RECORDS if record.kind is kind),
            key=lambda record: (record.review_horizon_days, record.id),
        )
        for kind in kinds
    }
    horizons = sorted({record.review_horizon_days for record in WHITE_RECORDS})
    axis_max = max(horizons)
    label_right, x0, x1 = 660, 720, 1420
    row_stride = 42
    top = 350

    def sx(days: float) -> int:
        """Map a horizon in days to the shared horizontal axis."""

        return int(x0 + (x1 - x0) * days / axis_max)

    band_heights = [110 + len(grouped[kind]) * row_stride + 50 for kind in kinds]
    band_tops: list[int] = []
    cursor = top
    for band_height in band_heights:
        band_tops.append(cursor)
        cursor += band_height + 26
    rule_top = cursor + 20
    height = rule_top + 170

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE HORIZON DISPERSION", 26, VIOLET, "700"),
        _text(110, 140, "How often each kind comes back for review", 40, INK, "700"),
        _text(
            110,
            186,
            "One dot per registry record, positioned by its review_horizon_days.",
            22,
            MUTED,
        ),
        _text(
            110,
            216,
            "Kinds differ by colour and by marker shape; a horizon is a review cadence,",
            22,
            MUTED,
        ),
        _text(110, 246, "not a rate at which the world changes.", 22, MUTED),
        _text(
            110,
            296,
            f"READ FROM THE {len(WHITE_RECORDS)}-RECORD REGISTRY · NOT A PRIORITY, SEVERITY, OR COMPLETENESS SCORE",
            18,
            TEAL,
            "700",
        ),
    ]
    for kind, band_top, band_height in zip(kinds, band_tops, band_heights, strict=True):
        color = _KIND_COLOR[kind]
        shape = _KIND_MARKER[kind]
        records = grouped[kind]
        middle = median(record.review_horizon_days for record in records)
        rows_top = band_top + 104
        axis_y = rows_top + len(records) * row_stride + 4
        parts.append(_rect(110, band_top, 1380, band_height, PANEL, LINE, 1))
        parts.append(_marker(shape, 152, band_top + 46, 13, color))
        parts.append(_text(184, band_top + 54, kind.value, 21, color, "700"))
        parts.append(
            _text(
                480,
                band_top + 54,
                f"{len(records)} records · median horizon {middle:g} days",
                19,
                MUTED,
                "700",
            )
        )
        parts.append(
            f'<line x1="{sx(middle)}" y1="{band_top + 84}" x2="{sx(middle)}" y2="{axis_y}" stroke="{color}" stroke-width="4" stroke-dasharray="7 6"/>'
        )
        parts.append(
            _text(
                sx(middle) - int(_advance(f"median {middle:g}", 18, True) / 2),
                band_top + 76,
                f"median {middle:g}",
                18,
                color,
                "700",
            )
        )
        for index, record in enumerate(records):
            y = rows_top + index * row_stride
            cx = sx(record.review_horizon_days)
            parts.append(
                _text(
                    label_right - int(_advance(record.title, 18, False)),
                    y + 7,
                    record.title,
                    18,
                    INK,
                )
            )
            parts.append(
                f'<line x1="{label_right + 20}" y1="{y}" x2="{cx - 16}" y2="{y}" stroke="{LINE}" stroke-width="2" stroke-dasharray="2 8"/>'
            )
            parts.append(_marker(shape, cx, y, 12, color))
            parts.append(
                _text(cx + 22, y + 7, f"{record.review_horizon_days} days", 18, color, "700")
            )
        parts.append(
            f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="{MUTED}" stroke-width="3"/>'
        )
        for days in horizons:
            parts.append(
                f'<line x1="{sx(days)}" y1="{axis_y}" x2="{sx(days)}" y2="{axis_y + 14}" stroke="{MUTED}" stroke-width="2"/>'
            )
            parts.append(
                _text(sx(days) - int(_advance(str(days), 18, False) / 2), axis_y + 46, f"{days}", 18, MUTED)
            )
        parts.append(_text(label_right - 90, axis_y + 46, "days", 18, MUTED))
    parts.extend(
        [
            _rect(110, rule_top, 1380, 150, CREAM, INK, 2),
            _text(140, rule_top + 44, "READING RULE", 19, VIOLET, "700"),
            _text(
                140,
                rule_top + 84,
                "The contemplative rows sit on one value because those horizons are uniform, which is a design commitment.",
                20,
                INK,
            ),
            _text(
                140,
                rule_top + 122,
                "A longer horizon means the ledger asks about that record less often; it says nothing about the record\'s weight.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


def intake_reachability() -> str:
    """Draw the intake battery: one row per code, input beside typed note.

    The worked distribution figure reports three intake codes as zero, and a
    zero bar cannot distinguish "this code exists and was not triggered here"
    from "this code is dead". This plate is the positive control that settles
    the difference: each row quotes an input constructed to reach exactly one
    code and shows the note the assessor actually produced for it. The battery
    is constructed to exercise the contract; it is not observed input.
    """

    probes = intake_reachability_battery()
    # Wrap widths keep both lines inside the row panel (x 110-1490), not
    # merely inside the canvas: a line that clears the canvas but overruns
    # its panel still reads as broken.
    note_x, note_width = 300, 1160
    input_x, input_width = 224, 1240
    wrapped = [_wrap(probe.event.message, 18, note_width) for probe in probes]
    wrapped_inputs = [_wrap(probe.rendered_input, 18, input_width) for probe in probes]
    # Rows are sized individually: a uniform height set by the longest note
    # would pad every other row and push the plate past a printable height.
    row_heights = [
        68 + (len(note) + len(shown)) * 24
        for note, shown in zip(wrapped, wrapped_inputs, strict=True)
    ]
    row_tops: list[int] = []
    top = 350
    cursor = top
    for row_height in row_heights:
        row_tops.append(cursor)
        cursor += row_height
    rows_bottom = cursor
    rule_top = rows_bottom + 30
    height = rule_top + 180

    parts = _open(1600, height)
    parts += [
        _text(110, 88, "THE INTAKE BATTERY", 26, VIOLET, "700"),
        _text(110, 140, "Every intake code, actually reached", 40, INK, "700"),
        _text(
            110,
            186,
            f"One constructed input per code, run through assess_absence: all "
            f"{len(probes)} of the live IntakeCode members fire.",
            22,
            MUTED,
        ),
        _text(
            110,
            216,
            "A zero in the worked tally therefore means untriggered here, never unreachable.",
            22,
            MUTED,
        ),
        _text(
            110,
            266,
            f"A CONSTRUCTED BATTERY · REVIEW DATE {WORKED_AS_OF} · NOT OBSERVED INPUT AND NOT A VERDICT ON ANY SUPPLIER",
            18,
            TEAL,
            "700",
        ),
        _text(150, 322, "CODE, TRIGGERING INPUT, AND THE TYPED NOTE PRODUCED", 18, VIOLET, "700"),
    ]
    for index, probe in enumerate(probes):
        y = row_tops[index]
        row_h = row_heights[index]
        state = probe.event.state
        color = _STATE_COLOR[state] if state is not None else OCHRE
        parts.append(
            _rect(110, y, 1380, row_h - 16, PANEL if index % 2 == 0 else CREAM, LINE, 1)
        )
        parts.append(
            f'<rect x="110" y="{y}" width="10" height="{row_h - 16}" fill="{color}"/>'
        )
        parts.append(_text(150, y + 44, probe.code.value, 20, OCHRE, "700"))
        parts.append(_text(150, y + 78, "input:", 18, MUTED, "700"))
        for line_index, line in enumerate(wrapped_inputs[index]):
            parts.append(_text(input_x, y + 78 + line_index * 30, line, 18, INK))
        note_y = y + 78 + len(wrapped_inputs[index]) * 30
        parts.append(_text(150, note_y, "typed note:", 18, MUTED, "700"))
        for line_index, line in enumerate(wrapped[index]):
            parts.append(_text(note_x, note_y + line_index * 30, line, 18, INK))
    parts.extend(
        [
            _rect(110, rule_top, 1380, 150, CREAM, INK, 2),
            _text(140, rule_top + 44, "READING RULE", 19, VIOLET, "700"),
            _text(
                140,
                rule_top + 84,
                "This plate establishes reachability of each code, not that any real input would ever produce it.",
                20,
                INK,
            ),
            _text(
                140,
                rule_top + 122,
                "A typed note describes what intake did with an input; it is never a judgment of whoever supplied it.",
                19,
                MUTED,
            ),
            "</svg>",
        ]
    )
    return "".join(parts)


__all__ = [
    "expiry_queue",
    "horizon_dispersion",
    "intake_reachability",
    "omitted_namings",
]
