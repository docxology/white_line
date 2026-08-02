"""Run the White Line source, figure, and rendered-artifact release gate.

This is intentionally a small, dependency-free audit. It does not certify a
project or verify the truth of an observation. It verifies that the local
source, generated figures, manuscript references, and rendered bundle agree
well enough for a human to review them together.

Typical release sequence::

    uv run python scripts/build_figures.py
    uv run python scripts/audit_project.py --write-manifest
    # render through the external docxology/template engine; see
    # docs/development.md for the path-independent invocation
    uv run python scripts/audit_project.py --write-manifest

The second manifest write is the meaningful one: it records the exact
manuscript and figure inputs that the rendered bundle passed against.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from white_line.audit import (
    audit_project,
    manifest_blocking_errors,
    render_dependent_error,
    source_blocking_errors,
    write_source_manifest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Run the audit and return its release-gate exit code."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root", type=Path, default=PROJECT_ROOT, help="project tree to audit"
    )
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="write the current source fingerprint",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="write output/reports/white_line_audit.json",
    )
    parser.add_argument(
        "--require-render",
        action="store_true",
        help="fail on render-dependent errors instead of deferring them (post-render gate)",
    )
    args = parser.parse_args()
    root = args.project_root.resolve()
    report = audit_project(root)
    if args.write_manifest and not manifest_blocking_errors(report["errors"]):
        write_source_manifest(root, report)
        report = audit_project(root)
    if args.report:
        report_path = root / "output/reports/white_line_audit.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["passed"]:
        return 0

    # The release sequence in this module's docstring audits the source before
    # the render and again after it. In the pre-render pass the rendered
    # bundle does not exist yet, so its errors are undecided rather than
    # failed: report them and exit on what is actually decidable. Pass
    # --require-render to demand the post-render gate.
    deferred = [error for error in report["errors"] if render_dependent_error(error)]
    if deferred and not args.require_render:
        blocking = source_blocking_errors(report["errors"])
        print(f"pre-render audit: {len(deferred)} render-dependent error(s) deferred")
        if blocking:
            print(f"source-side errors that do not depend on the render: {blocking}")
            return 1
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
