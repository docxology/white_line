#!/usr/bin/env python3
"""Report figure labels that render too small or run past their canvas.

Thin orchestrator: the measurement lives in ``white_line.figures.legibility``
and ``white_line.figures.metrics``, and the gate itself is
``tests/test_figure_legibility.py``. This script prints the same numbers while
a plate is being laid out, so a layout change can be checked without reading a
pytest failure report.

    uv run python scripts/check_figure_layout.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from white_line.figures import FIGURE_PLATES
from white_line.figures.legibility import (
    MINIMUM_POINT_SIZE,
    embedded_figure_widths,
    page_metrics,
    plate_rendered_width_inches,
    point_size,
)
from white_line.figures.metrics import read_labels, svg_canvas_size

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Print per-plate minimum point size and every overflowing label.

    The parser takes no options. It is still constructed, because a check
    script that accepts an unrecognized flag and exits ``0`` reports success
    for a command it never ran — a typo'd flag in a layout pass would read as
    a passing gate.
    """

    argparse.ArgumentParser(description=__doc__).parse_args()
    metrics = page_metrics(PROJECT_ROOT)
    widths = embedded_figure_widths(PROJECT_ROOT)
    worst = None
    failures = 0
    for plate in FIGURE_PLATES:
        svg = plate.render()
        canvas_w, canvas_h = svg_canvas_size(svg)
        labels = read_labels(svg)
        fraction = widths[f"{plate.name}.png"]
        rendered_in, binder = plate_rendered_width_inches(
            canvas_w, canvas_h, fraction, metrics
        )
        smallest = min(label.size for label in labels)
        printed = point_size(smallest, canvas_w, rendered_in)
        overflow = [
            label for label in labels if label.right_edge > canvas_w - 8
        ]
        flag = "" if printed >= MINIMUM_POINT_SIZE else "  << UNDER GATE"
        print(
            f"{plate.name:32} {canvas_w}x{canvas_h:<5} w={fraction:<5} "
            f"bind={binder:<6} min={smallest:>3}u {printed:5.2f}pt "
            f"overflow={len(overflow)}{flag}"
        )
        for label in overflow:
            failures += 1
            print(
                f"    OVERFLOW x={label.x} size={label.size} "
                f"right={label.right_edge:.0f} > {canvas_w}: {label.value!r}"
            )
        if worst is None or printed < worst:
            worst = printed
    print(f"\nminimum rendered point size across all plates: {worst:.2f} pt")
    return 1 if failures or (worst is not None and worst < MINIMUM_POINT_SIZE) else 0


if __name__ == "__main__":
    raise SystemExit(main())
