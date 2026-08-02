"""Build deterministic White Line schematics from the versioned registry.

The package owns the drawing and artifact protocol. This script supplies the
operator-facing command only; the figures remain schematics of the ledger, not
evidence of a cause, completeness, or a diagnosis.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from white_line.figures import build_figures


def main() -> None:
    """Build figures under an optional project root and report the artifact count."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root", type=Path, help="root that receives output/figures"
    )
    args = parser.parse_args()
    paths = build_figures(args.project_root)
    pngs = [path for path in paths if path.suffix == ".png"]
    print(
        f"generated {len(pngs)} PNG figures ({len(paths)} artifacts) under {paths[0].parent}"
    )


if __name__ == "__main__":
    main()
