"""The figure legibility gate: no label may print below six points.

Every White Line plate repeats its meaning in shape and text so the figure
survives greyscale printing and colour-blind reading. That contract is void if
the text is too small to read, and nothing in the build noticed when it was:
before this gate, the smallest labels in the shipped PDF printed at 3.39 pt,
because a ``height=0.5\\textheight`` cap bound before width on the tall plates
and shrank the whole image.

The gate derives the printed size rather than asserting it. For each plate it
reads the canvas size out of the rendered SVG, the ``width=`` attribute out of
the manuscript embed, and the page geometry out of ``manuscript/config.yaml``,
then computes how many points a label of ``N`` canvas units occupies on paper.
Two further tests cross-check that derivation against the geometry the last
render actually used, so a template-side change cannot leave the number quietly
wrong.

Each gate here is paired with a positive control that plants the defect the
gate exists to catch and asserts rejection.
"""

from datetime import date
from pathlib import Path

import pytest
from white_line.figures import FIGURE_PLATES, build_figures
from white_line.figures.canvas import (
    MAX_CANVAS_WIDTH,
    MIN_TEXT_SIZE,
    open_canvas,
    text,
    wrap_lines,
)
from white_line.figures.legibility import (
    DEFAULT_FIGURE_HEIGHT_FRACTION,
    MINIMUM_POINT_SIZE,
    PAPER_HEIGHT_INCHES,
    PAPER_WIDTH_INCHES,
    PageMetrics,
    embedded_figure_widths,
    observed_latex_geometry,
    page_metrics,
    plate_rendered_width_inches,
    point_size,
)
from white_line.figures.metrics import (
    advance_width,
    png_pixel_size,
    read_labels,
    svg_canvas_size,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: A rendered figure must leave room on the page for its own caption. The
#: captions in this manuscript run three to six lines at the body size, which
#: is roughly one inch, so a plate may occupy at most this fraction of the
#: text block.
MAX_HEIGHT_FRACTION_OF_TEXT_BLOCK = 0.85


def _measure(plate_name: str, svg: str) -> tuple[float, str, float]:
    """Return (smallest printed point size, binding dimension, printed height)."""

    canvas_width, canvas_height = svg_canvas_size(svg)
    labels = read_labels(svg)
    assert labels, f"{plate_name} draws no text at all"
    metrics = page_metrics(PROJECT_ROOT)
    fraction = embedded_figure_widths(PROJECT_ROOT)[f"{plate_name}.png"]
    printed_width, binder = plate_rendered_width_inches(
        canvas_width, canvas_height, fraction, metrics
    )
    smallest = min(label.size for label in labels)
    printed_height = printed_width * canvas_height / canvas_width
    return point_size(smallest, canvas_width, printed_width), binder, printed_height


def test_the_measurement_reproduces_the_documented_derivation() -> None:
    """The page geometry read from config.yaml is the one the manuscript declares."""

    metrics = page_metrics(PROJECT_ROOT)
    # left=0.33in and right=0.33in on letter paper.
    assert metrics.text_width_inches == pytest.approx(PAPER_WIDTH_INCHES - 0.66)
    assert metrics.text_height_inches == pytest.approx(PAPER_HEIGHT_INCHES - 1.10)
    # An 18-unit label on a full-width 1600-unit canvas.
    assert point_size(
        MIN_TEXT_SIZE, MAX_CANVAS_WIDTH, metrics.text_width_inches
    ) == pytest.approx(6.35, abs=0.01)


def test_every_figure_label_prints_at_or_above_six_points() -> None:
    """No shipped plate draws a label that prints below the legibility floor."""

    assert FIGURE_PLATES, "the scan set must not be empty"
    measured = {
        plate.name: _measure(plate.name, plate.render())[0] for plate in FIGURE_PLATES
    }
    assert len(measured) == len(FIGURE_PLATES)
    too_small = {
        name: size for name, size in measured.items() if size < MINIMUM_POINT_SIZE
    }
    assert not too_small, f"labels print below {MINIMUM_POINT_SIZE} pt: {too_small}"


def test_the_gate_rejects_a_plate_whose_smallest_label_was_shrunk() -> None:
    """Positive control: shrink one label and the same measurement fails.

    The label is injected as raw SVG rather than through ``canvas.text``,
    because ``canvas.text`` refuses the size outright. This proves the
    measurement — not only the builder-side guard — can reject.
    """

    plate = FIGURE_PLATES[0]
    healthy = plate.render()
    assert _measure(plate.name, healthy)[0] >= MINIMUM_POINT_SIZE
    shrunken = healthy.replace(
        "</svg>",
        '<text x="100" y="100" font-family="Arial, sans-serif" font-size="9px" '
        'font-weight="400" fill="#211A1D">shrunken</text></svg>',
    )
    assert shrunken != healthy
    assert _measure(plate.name, shrunken)[0] < MINIMUM_POINT_SIZE


def test_canvas_text_refuses_a_size_below_the_floor() -> None:
    """Positive control for the builder-side guard."""

    assert text(0, 0, "fine", MIN_TEXT_SIZE)
    with pytest.raises(ValueError, match="legibility"):
        text(0, 0, "too small", MIN_TEXT_SIZE - 1)


def test_open_canvas_refuses_a_canvas_wider_than_the_cap() -> None:
    """Positive control: a wider canvas would shrink every label on the page."""

    assert open_canvas(MAX_CANVAS_WIDTH, 400)
    with pytest.raises(ValueError, match="MAX_CANVAS_WIDTH"):
        open_canvas(MAX_CANVAS_WIDTH + 1, 400)


def test_width_binds_the_rendered_size_for_every_plate() -> None:
    """The height cap must not be what sets a plate's printed size.

    This is the root cause the gate exists for: when height binds, the plate
    is scaled down and ``MIN_TEXT_SIZE`` buys nothing.
    """

    binders = {
        plate.name: _measure(plate.name, plate.render())[1] for plate in FIGURE_PLATES
    }
    assert set(binders.values()) == {"width"}, binders


def test_the_height_bound_is_detectable_when_it_would_bind() -> None:
    """Positive control: restoring the old 0.5 cap makes height bind again."""

    plate = next(
        item for item in FIGURE_PLATES if item.name == "white_scholarship_map"
    )
    canvas_width, canvas_height = svg_canvas_size(plate.render())
    live = page_metrics(PROJECT_ROOT)
    old_cap = PageMetrics(live.text_width_inches, live.text_height_inches, 0.50)
    printed, binder = plate_rendered_width_inches(
        canvas_width, canvas_height, 1.0, old_cap
    )
    assert binder == "height"
    assert point_size(MIN_TEXT_SIZE, canvas_width, printed) < MINIMUM_POINT_SIZE


def test_every_plate_leaves_room_on_the_page_for_its_caption() -> None:
    """A plate must print short enough that its caption fits under it."""

    metrics = page_metrics(PROJECT_ROOT)
    ceiling = MAX_HEIGHT_FRACTION_OF_TEXT_BLOCK * metrics.text_height_inches
    heights = {
        plate.name: _measure(plate.name, plate.render())[2] for plate in FIGURE_PLATES
    }
    too_tall = {name: height for name, height in heights.items() if height > ceiling}
    assert not too_tall, f"plates exceed {ceiling:.2f} in of text block: {too_tall}"


def test_no_label_runs_past_the_edge_of_its_canvas() -> None:
    """A legible label that overruns its canvas is still unreadable."""

    overflowing: dict[str, list[str]] = {}
    for plate in FIGURE_PLATES:
        svg = plate.render()
        canvas_width, _height = svg_canvas_size(svg)
        beyond = [
            label.value
            for label in read_labels(svg)
            if label.right_edge > canvas_width - 8
        ]
        if beyond:
            overflowing[plate.name] = beyond
    assert not overflowing, overflowing


def test_the_overflow_check_rejects_a_label_placed_past_the_edge() -> None:
    """Positive control for the overflow check."""

    plate = FIGURE_PLATES[0]
    svg = plate.render()
    canvas_width, _height = svg_canvas_size(svg)
    planted = svg.replace(
        "</svg>",
        f'<text x="{canvas_width - 40}" y="100" font-family="Arial, sans-serif" '
        'font-size="20px" font-weight="400" fill="#211A1D">runs off the right edge'
        "</text></svg>",
    )
    beyond = [
        label.value
        for label in read_labels(planted)
        if label.right_edge > canvas_width - 8
    ]
    assert beyond == ["runs off the right edge"]


def test_wrap_lines_keeps_every_line_inside_the_requested_width() -> None:
    """The wrapper and the overflow check share one width estimate."""

    message = (
        "input 0 (fallow-ground) has an observation date object that is not an "
        "ISO date string; the observation was accepted at intake"
    )
    lines = wrap_lines(message, 18, 600)
    assert len(lines) > 1
    assert " ".join(lines) == message
    for line in lines:
        assert advance_width(line, 18, False) <= 600


def test_rasterized_pixels_match_the_declared_canvas(tmp_path: Path) -> None:
    """One canvas unit is one PNG pixel, which the point-size derivation assumes."""

    build_figures(tmp_path)
    figure_dir = tmp_path / "output" / "figures"
    for plate in FIGURE_PLATES:
        declared = svg_canvas_size((figure_dir / f"{plate.name}.svg").read_text())
        assert png_pixel_size(figure_dir / f"{plate.name}.png") == declared


def test_derived_geometry_matches_the_last_rendered_latex() -> None:
    """Cross-check: the config-derived geometry equals what the render used.

    ``observed_latex_geometry`` returns ``None`` before the project has ever
    been rendered, which is a legitimate state for a fresh checkout; the check
    is skipped only then, and never masked when the artifacts exist.
    """

    observed = observed_latex_geometry(PROJECT_ROOT)
    if observed is None:
        pytest.skip("no rendered LaTeX artifacts in this checkout")
    metrics = page_metrics(PROJECT_ROOT)
    assert observed["text_width_inches"] == pytest.approx(
        metrics.text_width_inches, abs=0.01
    )
    assert observed["text_height_inches"] == pytest.approx(
        metrics.text_height_inches, abs=0.01
    )
    declared = embedded_figure_widths(PROJECT_ROOT)
    figures = observed["figures"]
    assert isinstance(figures, dict)
    for filename, (width_fraction, height_fraction) in sorted(figures.items()):
        assert width_fraction == pytest.approx(declared[filename], abs=0.001)
        assert height_fraction == pytest.approx(
            metrics.figure_height_fraction, abs=0.001
        )


def test_page_metrics_refuses_a_geometry_without_margins(tmp_path: Path) -> None:
    """Positive control: a guessed text width would make every number fiction."""

    manuscript = tmp_path / "manuscript"  # earlier-layout fixture tree
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text(
        'metadata:\n  geometry: "top=0.55in,bottom=0.55in"\n', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="left/right|missing inch margins"):
        page_metrics(tmp_path)

    (manuscript / "config.yaml").write_text("metadata:\n  license: none\n", encoding="utf-8")
    with pytest.raises(ValueError, match="metadata.geometry"):
        page_metrics(tmp_path)


def test_embedded_widths_cover_every_registered_plate() -> None:
    """A plate with no manuscript embed has no measurable printed size."""

    widths = embedded_figure_widths(PROJECT_ROOT)
    missing = [
        plate.name for plate in FIGURE_PLATES if f"{plate.name}.png" not in widths
    ]
    assert not missing, missing
    assert all(0 < value <= 1.0 for value in widths.values())


def test_marker_shapes_cover_the_kind_alphabet_without_colour() -> None:
    """Shape carries the kind, so the figures read in greyscale."""

    from white_line.figures.palette import KIND_COLOR, KIND_MARKER
    from white_line.model import AbsenceKind

    assert set(KIND_MARKER) == set(AbsenceKind)
    assert len(set(KIND_MARKER.values())) == len(AbsenceKind)
    # Colour is a second, redundant channel — never the only one.
    assert len(set(KIND_COLOR.values())) == len(AbsenceKind)


def test_figure_builds_are_byte_identical_on_a_second_run(tmp_path: Path) -> None:
    """Determinism: nothing in the plates depends on today's date or set order."""

    first = {path.name: path.read_bytes() for path in build_figures(tmp_path)}
    second = {path.name: path.read_bytes() for path in build_figures(tmp_path)}
    assert first == second
    assert date.today() is not None  # the plates never read it; this only documents so
    assert all(b"today" not in payload for payload in first.values())


def test_marker_refuses_an_unknown_shape() -> None:
    """Positive control: a silent fallback would erase the kind distinction."""

    from white_line.figures.canvas import marker

    assert marker("circle", 10, 10, 4, "#000000").startswith("<circle")
    assert marker("square", 10, 10, 4, "#000000").startswith("<rect")
    assert marker("triangle", 10, 10, 4, "#000000").startswith("<path")
    with pytest.raises(ValueError, match="unknown marker shape"):
        marker("diamond", 10, 10, 4, "#000000")


def test_wrap_lines_returns_no_lines_for_an_empty_string() -> None:
    """An empty label draws nothing rather than one blank line."""

    assert wrap_lines("", 18, 600) == []
    assert wrap_lines("solo", 18, 600) == ["solo"]


def test_a_word_longer_than_the_wrap_width_is_kept_whole() -> None:
    """Breaking mid-identifier would be harder to read than the overhang."""

    from white_line.figures.metrics import advance_width

    word = "unobserved-dependency-with-a-very-long-identifier"
    assert advance_width(word, 18, False) > 200
    assert wrap_lines(word, 18, 200) == [word]


def test_column_positions_places_a_single_column_at_the_left_margin() -> None:
    """A one-member alphabet has no stride to compute."""

    from white_line.figures.plates.overview import column_positions

    assert column_positions(1, 110, 1490, 440) == [110]
    spread = column_positions(3, 110, 1490, 440)
    assert spread[0] == 110
    assert spread == sorted(spread)
    assert spread[-1] + 440 <= 1490


def test_svg_canvas_size_refuses_a_plate_with_no_declared_size() -> None:
    """The whole point-size derivation rests on the declared canvas."""

    with pytest.raises(ValueError, match="no declared width and height"):
        svg_canvas_size("<svg xmlns='http://www.w3.org/2000/svg'></svg>")


def test_geometry_readback_is_none_before_any_render(tmp_path: Path) -> None:
    """A fresh checkout has no rendered LaTeX to cross-check against."""

    assert observed_latex_geometry(tmp_path) is None
    pdf_dir = tmp_path / "output" / "pdf"
    pdf_dir.mkdir(parents=True)
    (pdf_dir / "_combined_manuscript.log").write_text("no dimensions here\n")
    # A .log without a .tex is still an incomplete render.
    assert observed_latex_geometry(tmp_path) is None
    (pdf_dir / "_combined_manuscript.tex").write_text("\\documentclass{article}\n")
    # Both files present, but the log records no \textwidth.
    assert observed_latex_geometry(tmp_path) is None
    (pdf_dir / "_combined_manuscript.log").write_text(
        "\\textwidth=553.58849pt\n\\textheight=715.47255pt\n"
    )
    observed = observed_latex_geometry(tmp_path)
    assert observed is not None
    assert observed["text_width_inches"] == pytest.approx(7.66, abs=0.01)
    assert observed["figures"] == {}


def test_non_inch_geometry_units_are_not_read_as_inches(tmp_path: Path) -> None:
    """A margin in millimetres is not silently treated as a margin in inches."""

    manuscript = tmp_path / "manuscript"  # earlier-layout fixture tree
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text(
        'metadata:\n  geometry: "left=0.42in,right=0.42in,top=14mm,bottom=0.55in"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing inch margins"):
        page_metrics(tmp_path)


def test_page_metrics_refuses_unequal_figure_height_fractions(tmp_path: Path) -> None:
    """Positive control: the renderer caps the first figure separately.

    A config declaring a different front-matter cap would make one plate's
    printed size depend on its position in the combined document, which this
    module does not model. It must raise rather than report a wrong number.
    """

    manuscript = tmp_path / "manuscript"  # earlier-layout fixture tree
    manuscript.mkdir(parents=True)
    geometry = 'metadata:\n  geometry: "left=0.42in,right=0.42in,top=0.55in,bottom=0.55in"\n'
    (manuscript / "config.yaml").write_text(
        "rendering:\n  figure_height_fraction: 1.0\n"
        "  front_matter_figure_height_fraction: 0.5\n" + geometry,
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="front_matter_figure_height_fraction"):
        page_metrics(tmp_path)

    (manuscript / "config.yaml").write_text(
        "rendering:\n  figure_height_fraction: 1.0\n"
        "  front_matter_figure_height_fraction: 1.0\n" + geometry,
        encoding="utf-8",
    )
    assert page_metrics(tmp_path).figure_height_fraction == 1.0

    # Both keys absent: the renderer's own default applies to every figure.
    (manuscript / "config.yaml").write_text(geometry, encoding="utf-8")
    assert page_metrics(tmp_path).figure_height_fraction == (
        DEFAULT_FIGURE_HEIGHT_FRACTION
    )
