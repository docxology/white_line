"""Write White Line figure artifacts without adding assessment semantics."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

from ..registry import WHITE_RECORDS
from ..serialization import (
    FIGURE_REGISTRY_SCHEMA,
    REGISTRY_ARTIFACT_SCHEMA,
    canonical_registry,
    registry_digest,
)
from ..version import LEDGER_VERSION

from .plates import FIGURE_PLATES

RSVG_CONVERT = "rsvg-convert"


def artifact_digest(path: Path) -> str:
    """Return the SHA-256 of one generated artifact's bytes.

    The figure registry records this for every PNG and SVG it lists so the
    audit can check the raster bytes themselves, not merely that a file with
    the right name exists. Without it, a hand-edited or replaced image passes
    every gate.
    """

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rasterize(svg_path: Path, png_path: Path, figure: str) -> None:
    """Rasterize one SVG or name the missing external rendering prerequisite."""

    executable = os.environ.get("WHITE_LINE_RSVG_CONVERT", RSVG_CONVERT)
    try:
        subprocess.run([executable, "-o", str(png_path), str(svg_path)], check=True)
    except FileNotFoundError as error:
        raise RuntimeError(
            f"{executable!r} could not render {figure}; install librsvg so rsvg-convert is on PATH."
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"{executable!r} failed while rendering {figure}; install or repair librsvg and rerun the figure build."
        ) from error


def _write_registry(figure_dir: Path) -> Path:
    path = figure_dir / "white_registry.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": REGISTRY_ARTIFACT_SCHEMA,
                "ledger_version": LEDGER_VERSION,
                "digest": registry_digest(WHITE_RECORDS),
                "records": json.loads(canonical_registry(WHITE_RECORDS)),
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _write_figure_registry(figure_dir: Path, metadata: list[dict[str, str]]) -> Path:
    path = figure_dir / "figure_registry.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": FIGURE_REGISTRY_SCHEMA,
                "ledger_version": LEDGER_VERSION,
                "registry_digest": registry_digest(WHITE_RECORDS),
                "figures": metadata,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _inject_accessibility(svg_text: str, title: str, desc: str) -> str:
    """Inject ``role=\"img\"``, ``aria-labelledby``, ``<title>``, and ``<desc>``.

    The ``<svg>`` opening tag is extended with accessibility attributes, and
    the ``<title id=\"title\">`` and ``<desc id=\"desc\">`` elements are
    inserted immediately after the background ``<rect>``.
    """

    def _escape(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    svg_text = svg_text.replace(
        '<svg xmlns=',
        '<svg role="img" aria-labelledby="title desc" xmlns=',
        1,
    )
    rect_close = svg_text.index("/>", svg_text.index("<rect")) + 2
    accessibility = (
        f"\n<title id=\"title\">{_escape(title)}</title>"
        f"\n<desc id=\"desc\">{_escape(desc)}</desc>"
    )
    return svg_text[:rect_close] + accessibility + svg_text[rect_close:]


def build_figures(project_root: Path | None = None) -> list[Path]:
    """Build the deterministic SVG, PNG, and registry artifacts."""

    root = project_root or Path(__file__).resolve().parents[3]
    figure_dir = root / "output" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    produced: list[Path] = []
    metadata: list[dict[str, str]] = []
    for plate in FIGURE_PLATES:
        svg_path = figure_dir / f"{plate.name}.svg"
        png_path = figure_dir / f"{plate.name}.png"
        svg_text = plate.render()
        svg_text = _inject_accessibility(svg_text, plate.label, plate.alt)
        svg_path.write_text(svg_text, encoding="utf-8")
        _rasterize(svg_path, png_path, plate.name)
        produced.extend([png_path, svg_path])
        metadata.append(
            {
                "label": plate.label,
                "filename": png_path.name,
                "caption": plate.caption,
                "alt": plate.alt,
                "source": plate.source,
                "generated_by": "scripts/build_figures.py",
                "format": "PNG rasterized from deterministic SVG",
                "source_digest": registry_digest(WHITE_RECORDS),
                "png_digest": artifact_digest(png_path),
                "svg_digest": artifact_digest(svg_path),
            }
        )
    produced.append(_write_registry(figure_dir))
    produced.append(_write_figure_registry(figure_dir, metadata))
    return produced


__all__ = ["RSVG_CONVERT", "artifact_digest", "build_figures"]
