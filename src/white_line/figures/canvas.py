"""Provide small SVG primitives without assigning meaning to a plate."""

from __future__ import annotations

from .metrics import advance_width
from .palette import TEAL, INK, LINE, OCHRE, PAPER, VIOLET

#: Widest canvas any plate may open, in canvas units.
#:
#: Rendered point size depends only on the ratio of a label's size to the
#: canvas width, because the manuscript embeds every plate at a fraction of
#: ``\linewidth``. Capping the width therefore caps how small a label can get.
MAX_CANVAS_WIDTH = 1600

#: Smallest label, in canvas units, any plate may draw.
#:
#: Derivation, reproduced by ``tests/test_figure_legibility.py`` from the
#: rendered geometry rather than asserted here: the manuscript's text block is
#: ``\textwidth`` = 7.66 in wide (letter paper less the 0.42 in side margins
#: declared in ``manuscript/config.yaml``). A plate embedded at ``width=100%``
#: on a ``MAX_CANVAS_WIDTH``-unit canvas renders one canvas unit at
#: ``7.66 / 1600`` in, so an ``N``-unit label renders at
#: ``N * 7.66 * 72 / 1600`` = ``N * 0.3447`` pt. A floor of 18 units therefore
#: renders at 6.20 pt, just above the 6 pt legibility gate. Anything below this
#: floor was unreadable in print: the shipped figures previously bottomed out
#: at 3.39 pt.
#:
#: The height cap matters too. ``rendering.figure_height_fraction`` in
#: ``manuscript/config.yaml`` must stay large enough that width, not height,
#: binds the rendered size; otherwise a tall plate is shrunk and this floor
#: buys nothing. The legibility test checks that condition per figure.
MIN_TEXT_SIZE = 18


def escape_text(value: str) -> str:
    """Escape text inserted between SVG text tags."""

    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def text(
    x: int, y: int, value: str, size: int, fill: str = INK, weight: str = "400"
) -> str:
    """Return one SVG text element, refusing a size below the legibility floor.

    Raises:
        ValueError: If ``size`` is under ``MIN_TEXT_SIZE``. Failing here rather
            than in review is the point: an illegible label is a defect in the
            accessibility contract these figures rely on, since shape and text
            are what carry the meaning when colour is unavailable.
    """

    if size < MIN_TEXT_SIZE:
        raise ValueError(
            f"figure text size {size} is below the {MIN_TEXT_SIZE}-unit legibility "
            f"floor (label {value!r}); see canvas.MIN_TEXT_SIZE for the derivation"
        )
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}px" font-weight="{weight}" fill="{fill}">{escape_text(value)}</text>'


def rect(
    x: int,
    y: int,
    width: int,
    height: int,
    fill: str,
    stroke: str = LINE,
    stroke_width: int = 2,
) -> str:
    """Return one SVG rectangle element."""

    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'


def wrap_lines(
    value: str, size: int, max_width: int, bold: bool = False
) -> list[str]:
    """Break ``value`` into lines that each fit within ``max_width`` units.

    Word wrapping uses the same advance widths the legibility gate uses to
    locate a label's right edge, so a wrapped line cannot pass the wrapper and
    fail the gate. A single word longer than ``max_width`` is emitted on its
    own line rather than split: the plates draw identifiers and messages, and a
    mid-token break would be harder to read than an overhang the gate reports.
    """

    words = value.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}" if current else word
        if current and advance_width(candidate, size, bold) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def marker(shape: str, cx: int, cy: int, radius: int, fill: str) -> str:
    """Return one SVG marker of the named shape, centred on ``(cx, cy)``.

    Shape carries the same distinction colour does, so a reader in greyscale
    or with a colour-vision difference still recovers the category.

    Raises:
        ValueError: If ``shape`` is not one of the drawn shapes. A silent
            fallback would erase the distinction the marker exists to carry.
    """

    if shape == "circle":
        return f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}"/>'
    if shape == "square":
        side = radius * 2
        return f'<rect x="{cx - radius}" y="{cy - radius}" width="{side}" height="{side}" fill="{fill}"/>'
    if shape == "triangle":
        return (
            f'<path d="M{cx} {cy - radius} L{cx + radius} {cy + radius} '
            f'L{cx - radius} {cy + radius} Z" fill="{fill}"/>'
        )
    raise ValueError(f"unknown marker shape {shape!r}")


def open_canvas(width: int, height: int) -> list[str]:
    """Open a standard White Line SVG canvas.

    Raises:
        ValueError: If ``width`` exceeds ``MAX_CANVAS_WIDTH``. A wider canvas
            silently shrinks every label on the page, which is the failure
            ``MIN_TEXT_SIZE`` exists to prevent. Height is unconstrained: a
            taller plate costs nothing once width binds the rendered size.
    """

    if width > MAX_CANVAS_WIDTH:
        raise ValueError(
            f"canvas width {width} exceeds MAX_CANVAS_WIDTH {MAX_CANVAS_WIDTH}; "
            "a wider canvas renders every label smaller on the page"
        )
    motif_x = width - 280
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
        f'<path d="M{motif_x} 40 C {motif_x + 44} 16, {motif_x + 92} 68, {motif_x + 136} 42" fill="none" stroke="{VIOLET}" stroke-width="4" stroke-linecap="round"/>',
        f'<path d="M{motif_x + 10} 62 C {motif_x + 58} 38, {motif_x + 104} 88, {motif_x + 164} 56" fill="none" stroke="{TEAL}" stroke-width="3" stroke-linecap="round"/>',
        f'<circle cx="{motif_x + 182}" cy="42" r="5" fill="{OCHRE}"/>',
    ]


__all__ = [
    "MAX_CANVAS_WIDTH",
    "MIN_TEXT_SIZE",
    "escape_text",
    "marker",
    "open_canvas",
    "rect",
    "text",
    "wrap_lines",
]
