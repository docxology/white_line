"""Derive how large a plate's smallest label prints on the rendered page.

A White Line plate carries its meaning in shape and text as well as colour, so
that the figure survives greyscale printing and colour-blind reading. That
contract fails silently if the text is too small to read: the shipped figures
once bottomed out at 3.39 pt, well under any legible size, and nothing in the
build noticed.

This module supplies the arithmetic that turns a canvas-unit font size into a
printed point size, reading the inputs from the project rather than from
constants:

* ``manuscript/config.yaml`` declares the LaTeX ``geometry`` margins, which fix
  the width and height of the text block.
* ``manuscript/*.md`` declares each figure's ``width=NN%`` embed attribute.
* ``rendering.figure_height_fraction`` in the same config caps a figure's
  height as a fraction of ``\\textheight``. Because Pandoc emits
  ``keepaspectratio``, the *smaller* of the width and height bounds wins — so a
  tall plate can be shrunk by the height cap until its labels are unreadable no
  matter how large they are in canvas units.

The module computes; ``tests/test_figure_legibility.py`` is the gate, and it
cross-checks these derived numbers against the rendered ``.tex`` and ``.log``
so a template-side geometry change cannot drift past the check.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

#: Smallest printed size, in PostScript points, a figure label may have.
MINIMUM_POINT_SIZE = 6.0

#: Paper dimensions in inches. The sibling template renders letter by default;
#: a project that changes paper size must change these together with the gate.
PAPER_WIDTH_INCHES = 8.5
PAPER_HEIGHT_INCHES = 11.0

#: The renderer's default when ``rendering.figure_height_fraction`` is absent.
DEFAULT_FIGURE_HEIGHT_FRACTION = 0.50

POINTS_PER_INCH = 72.0

_GEOMETRY_RE = re.compile(r'^\s*geometry:\s*"([^"]+)"\s*$', re.MULTILINE)
_HEIGHT_FRACTION_RE = re.compile(
    r"^\s*figure_height_fraction:\s*([0-9.]+)\s*$", re.MULTILINE
)
_FRONT_MATTER_FRACTION_RE = re.compile(
    r"^\s*front_matter_figure_height_fraction:\s*([0-9.]+)\s*$", re.MULTILINE
)
_EMBED_RE = re.compile(
    r"\]\((?:\./|\.\./)*output/figures/([^)]+\.png)\)\{([^}]*)\}",
)
_WIDTH_ATTRIBUTE_RE = re.compile(r"width=(\d+(?:\.\d+)?)%")
_TEX_WIDTH_RE = re.compile(r"\\textwidth=([\d.]+)pt")
_TEX_HEIGHT_RE = re.compile(r"\\textheight=([\d.]+)pt")
_INCLUDEGRAPHICS_RE = re.compile(
    r"\\includegraphics\[width=([\d.]+)\\linewidth,height=([\d.]+)\\textheight,"
    r"keepaspectratio.*?\]\{\.\./figures/([^}]+)\}",
    re.S,
)

#: TeX points per inch, for reading LaTeX dimensions out of a ``.log``.
TEX_POINTS_PER_INCH = 72.27


@dataclass(frozen=True)
class PageMetrics:
    """The page-side inputs to a figure's rendered size."""

    text_width_inches: float
    text_height_inches: float
    figure_height_fraction: float


def _margins(geometry: str) -> dict[str, float]:
    """Return the inch margins declared in a LaTeX ``geometry`` option string."""

    margins: dict[str, float] = {}
    for item in geometry.split(","):
        key, _, raw = item.strip().partition("=")
        raw = raw.strip()
        if raw.endswith("in"):
            margins[key.strip()] = float(raw[:-2])
    missing = {"left", "right", "top", "bottom"} - set(margins)
    if missing:
        raise ValueError(
            f"geometry {geometry!r} is missing inch margins for {sorted(missing)}"
        )
    return margins


# White Line carries its manuscript under ``docs/manuscript/``; the earlier
# ``manuscript/`` layout is still resolved for compatibility so a checkout
# from either layout (or the transition between them) audits and measures
# against the real sources rather than a missing directory.
MANUSCRIPT_DIR_NAMES: tuple[str, ...] = ("docs/manuscript", "manuscript")


def manuscript_dir(project_root: Path) -> Path:
    """Return the manuscript directory: ``docs/manuscript/`` if present,
    else the earlier ``manuscript/`` layout.

    Raises ``FileNotFoundError`` when neither layout exists, so a caller never
    silently measures an empty glob.
    """

    root = project_root.resolve()
    for relative in MANUSCRIPT_DIR_NAMES:
        candidate = root / relative
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(
        f"no manuscript directory under {root}: expected one of "
        + ", ".join(MANUSCRIPT_DIR_NAMES)
    )


def page_metrics(project_root: Path) -> PageMetrics:
    """Read the text-block size and figure height cap from ``config.yaml``.

    The keys are extracted by targeted pattern, not by a YAML parser: the
    package is deliberately pure standard library, and only these scalars are
    needed. A malformed or absent ``geometry`` raises rather than falling back
    to a guess, because a guessed text width would make the whole legibility
    number fiction.

    Raises:
        ValueError: If ``metadata.geometry`` is absent or carries no inch
            margins, or if ``front_matter_figure_height_fraction`` differs from
            ``figure_height_fraction``. The renderer applies the former to the
            first figure in the combined document and the latter to every other
            one, so unequal values would make a plate's printed size depend on
            its position in the document — something this module does not
            model, and would therefore report wrongly rather than not at all.
    """

    config = (manuscript_dir(project_root) / "config.yaml").read_text(
        encoding="utf-8"
    )
    geometry_match = _GEOMETRY_RE.search(config)
    if geometry_match is None:
        raise ValueError("manuscript/config.yaml declares no metadata.geometry")
    margins = _margins(geometry_match.group(1))
    fraction_match = _HEIGHT_FRACTION_RE.search(config)
    fraction = (
        float(fraction_match.group(1))
        if fraction_match
        else DEFAULT_FIGURE_HEIGHT_FRACTION
    )
    front_match = _FRONT_MATTER_FRACTION_RE.search(config)
    front_fraction = (
        float(front_match.group(1))
        if front_match
        else DEFAULT_FIGURE_HEIGHT_FRACTION
    )
    if front_fraction != fraction:
        raise ValueError(
            "rendering.front_matter_figure_height_fraction "
            f"({front_fraction:g}) must equal rendering.figure_height_fraction "
            f"({fraction:g}); the renderer applies the first to the leading "
            "figure only, and a position-dependent cap cannot be gated here"
        )
    return PageMetrics(
        PAPER_WIDTH_INCHES - margins["left"] - margins["right"],
        PAPER_HEIGHT_INCHES - margins["top"] - margins["bottom"],
        fraction,
    )


def embedded_figure_widths(project_root: Path) -> dict[str, float]:
    """Map each embedded figure filename to its declared width fraction.

    An embed with no explicit ``width=`` attribute defaults to the full line
    width, matching Pandoc.
    """

    widths: dict[str, float] = {}
    for path in sorted(manuscript_dir(project_root).glob("*.md")):
        for filename, attributes in _EMBED_RE.findall(path.read_text(encoding="utf-8")):
            match = _WIDTH_ATTRIBUTE_RE.search(attributes)
            widths[filename] = float(match.group(1)) / 100.0 if match else 1.0
    return widths


def plate_rendered_width_inches(
    canvas_width: int,
    canvas_height: int,
    width_fraction: float,
    metrics: PageMetrics,
) -> tuple[float, str]:
    """Return a plate's printed width in inches and which bound produced it.

    ``keepaspectratio`` fits the image inside the declared width × height box,
    so whichever bound is tighter sets the rendered size. A ``"height"`` result
    means the plate is being shrunk below its declared width, which shrinks
    every label with it.
    """

    by_width = width_fraction * metrics.text_width_inches
    by_height = (
        metrics.figure_height_fraction
        * metrics.text_height_inches
        * canvas_width
        / canvas_height
    )
    if by_height < by_width:
        return by_height, "height"
    return by_width, "width"


def point_size(canvas_size: int, canvas_width: int, rendered_width: float) -> float:
    """Return the printed size, in points, of a ``canvas_size``-unit label."""

    return canvas_size / canvas_width * rendered_width * POINTS_PER_INCH


def observed_latex_geometry(project_root: Path) -> dict[str, object] | None:
    """Read the geometry the last render actually used, or ``None``.

    Returns the ``\\textwidth`` and ``\\textheight`` recorded in the rendered
    ``.log`` (converted to inches) and the per-figure ``width``/``height``
    fractions the rendered ``.tex`` carries. The gate compares these against
    the values derived from ``config.yaml``, so a template-side change to the
    page or the figure height cap surfaces as a test failure rather than as a
    quietly wrong legibility number.
    """

    log_path = project_root / "output" / "pdf" / "_combined_manuscript.log"
    tex_path = project_root / "output" / "pdf" / "_combined_manuscript.tex"
    if not log_path.is_file() or not tex_path.is_file():
        return None
    log = log_path.read_text(encoding="utf-8", errors="replace")
    width_match = _TEX_WIDTH_RE.search(log)
    height_match = _TEX_HEIGHT_RE.search(log)
    if width_match is None or height_match is None:
        return None
    figures = {
        filename: (float(width), float(height))
        for width, height, filename in _INCLUDEGRAPHICS_RE.findall(
            tex_path.read_text(encoding="utf-8")
        )
    }
    return {
        "text_width_inches": float(width_match.group(1)) / TEX_POINTS_PER_INCH,
        "text_height_inches": float(height_match.group(1)) / TEX_POINTS_PER_INCH,
        "figures": figures,
    }


__all__ = [
    "DEFAULT_FIGURE_HEIGHT_FRACTION",
    "MINIMUM_POINT_SIZE",
    "PAPER_HEIGHT_INCHES",
    "PAPER_WIDTH_INCHES",
    "PageMetrics",
    "embedded_figure_widths",
    "observed_latex_geometry",
    "page_metrics",
    "plate_rendered_width_inches",
    "point_size",
]
