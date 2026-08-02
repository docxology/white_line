"""Measure figure text and read rendered plates back for inspection.

Two capabilities live here, and both are used by the builder and by the
legibility gate so the two cannot disagree:

* **Advance widths.** The plates request ``Arial, sans-serif``; Arial is
  metric-compatible with Helvetica, so the Adobe core Helvetica advance widths
  give a close estimate of where a label stops being drawn.
  ``canvas.wrap_lines`` uses this to break a long string onto several lines,
  and ``tests/test_figure_legibility.py`` uses it to assert that no label runs
  off its canvas.
* **Readback.** Parsers that recover every ``<text>`` element and the declared
  canvas size from a rendered plate, plus a PNG's pixel dimensions. The gate
  measures what a plate actually drew rather than what its source intended.
"""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from pathlib import Path

# Helvetica / Helvetica-Bold advance widths, in 1/1000 em, from the Adobe core
# font metrics. Arial is metric-compatible with Helvetica, which is what the
# plates request.
_REGULAR = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667,
    "'": 191, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, ":": 278, ";": 278, "<": 584, "=": 584, ">": 584,
    "?": 556, "@": 1015, "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556,
    "`": 333, "{": 334, "|": 260, "}": 334, "~": 584,
    "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722,
    "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722,
    "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
    "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556,
    "h": 556, "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556,
    "o": 556, "p": 556, "q": 556, "r": 333, "s": 500, "t": 278, "u": 556,
    "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
}
_BOLD = {
    " ": 278, "!": 333, '"': 474, "#": 556, "$": 556, "%": 889, "&": 722,
    "'": 238, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, ":": 333, ";": 333, "<": 584, "=": 584, ">": 584,
    "?": 611, "@": 975, "[": 333, "\\": 278, "]": 333, "^": 584, "_": 556,
    "`": 333, "{": 389, "|": 280, "}": 389, "~": 584,
    "A": 722, "B": 722, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 556, "K": 722, "L": 611, "M": 833, "N": 722,
    "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722,
    "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
    "a": 556, "b": 611, "c": 556, "d": 611, "e": 556, "f": 333, "g": 611,
    "h": 611, "i": 278, "j": 278, "k": 556, "l": 278, "m": 889, "n": 611,
    "o": 611, "p": 611, "q": 611, "r": 389, "s": 556, "t": 333, "u": 611,
    "v": 556, "w": 778, "x": 556, "y": 556, "z": 500,
}
# Non-ASCII characters the plates actually use.
_EXTRA = {"·": 333, "–": 556, "—": 1000, "×": 584, "→": 1000, "↑": 1000}
_DIGITS = 556
_FALLBACK = 611


def advance_width(value: str, size: int, bold: bool) -> float:
    """Return the estimated drawn width of ``value`` in canvas units."""

    table = _BOLD if bold else _REGULAR
    total = 0
    for character in value:
        if character.isdigit():
            total += _DIGITS
        elif character in table:
            total += table[character]
        elif character in _EXTRA:
            total += _EXTRA[character]
        else:
            total += _FALLBACK
    return total * size / 1000.0




TEXT_ELEMENT_RE = re.compile(
    r'<text x="(-?\d+)" y="(-?\d+)" font-family="[^"]*" font-size="(\d+)px" '
    r'font-weight="(\d+)" fill="[^"]*">(.*?)</text>'
)
SVG_SIZE_RE = re.compile(r'<svg[^>]*width="(\d+)" height="(\d+)"')


@dataclass(frozen=True)
class Label:
    """One ``<text>`` element read back out of a rendered plate."""

    x: int
    y: int
    size: int
    bold: bool
    value: str

    @property
    def right_edge(self) -> float:
        """Estimated x coordinate where the label stops being drawn."""

        return self.x + advance_width(self.value, self.size, self.bold)


def read_labels(svg: str) -> list[Label]:
    """Return every text element in a plate's SVG, in document order."""

    labels: list[Label] = []
    for x, y, size, weight, value in TEXT_ELEMENT_RE.findall(svg):
        unescaped = (
            value.replace("&quot;", '"')
            .replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("&amp;", "&")
        )
        labels.append(Label(int(x), int(y), int(size), int(weight) >= 700, unescaped))
    return labels


def svg_canvas_size(svg: str) -> tuple[int, int]:
    """Return the declared (width, height) of a plate's SVG canvas."""

    match = SVG_SIZE_RE.search(svg)
    if match is None:
        raise ValueError("SVG has no declared width and height")
    return int(match.group(1)), int(match.group(2))


def png_pixel_size(path: Path) -> tuple[int, int]:
    """Return a PNG's pixel dimensions straight from its IHDR chunk.

    The rasterizer is asked for the SVG's declared size, so this is how the
    gate confirms that one canvas unit really is one PNG pixel — the
    assumption the whole point-size derivation rests on.
    """

    header = path.read_bytes()[:24]
    width, height = struct.unpack(">II", header[16:24])
    return width, height


__all__ = [
    "Label",
    "advance_width",
    "png_pixel_size",
    "read_labels",
    "svg_canvas_size",
]
