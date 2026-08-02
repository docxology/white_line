"""Every operator script must refuse input it does not understand.

Two of the four scripts had no argument parser at all. They ignored an
unrecognized flag and a stray positional argument alike and exited ``0``,
which is the worst possible failure for a *check* script: a mistyped flag in
a release sequence prints a clean report for a command that was never the one
requested. The gate below runs each script's real entry point in a
subprocess, so it measures the exit code an operator would actually see.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

#: Every script an operator is told to run. Derived from the directory rather
#: than listed by hand: a new script joins the gate without an edit here, and
#: an empty scan set fails the emptiness assertion below rather than passing
#: vacuously.
SCRIPTS = tuple(
    sorted(
        path.name
        for path in (PROJECT_ROOT / "scripts").glob("*.py")
        if path.name != "__init__.py"
    )
)

#: Inputs no script defines. Each must be refused, not ignored.
REJECTED_ARGUMENTS = (
    ["--definitely-not-a-flag"],
    ["--project-root"],  # option present on two scripts, value missing
    ["a-stray-positional"],
    ["--"],  # end-of-options followed by nothing meaningful
    ["-x"],
)


def _run(script: str, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, f"scripts/{script}", *arguments],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_the_script_scan_set_is_not_empty() -> None:
    """A gate over zero scripts would pass without checking anything."""

    assert len(SCRIPTS) >= 4, SCRIPTS
    assert "check_registry.py" in SCRIPTS
    assert "check_figure_layout.py" in SCRIPTS


@pytest.mark.parametrize("script", SCRIPTS)
@pytest.mark.parametrize("arguments", REJECTED_ARGUMENTS, ids=lambda a: " ".join(a))
def test_every_script_fails_closed_on_input_it_does_not_define(
    script: str, arguments: list[str]
) -> None:
    """An unrecognized argument must produce a non-zero exit, never a report."""

    completed = _run(script, arguments)
    assert completed.returncode != 0, (
        f"scripts/{script} accepted {arguments!r} and exited 0; "
        f"stdout={completed.stdout[:200]!r}"
    )
    assert "usage:" in completed.stderr.lower(), completed.stderr[:200]


@pytest.mark.parametrize("script", ("check_registry.py", "check_figure_layout.py"))
def test_the_read_only_checks_still_succeed_on_real_input(script: str) -> None:
    """Positive control: the refusal above is not a blanket failure."""

    completed = _run(script, [])
    assert completed.returncode == 0, completed.stderr[:400]
    assert completed.stdout.strip()


def test_help_is_available_on_every_script() -> None:
    """``--help`` proves each script has a parser rather than ignoring input."""

    for script in SCRIPTS:
        completed = _run(script, ["--help"])
        assert completed.returncode == 0, script
        assert "usage:" in completed.stdout.lower(), script


#: The two artifacts no code in this repository writes. The render engine that
#: produces them lives in ``docxology/template``; a clone of this repository is
#: a source-only tree by construction.
RENDERED_BUNDLE = (
    "output/web/_combined_manuscript.md",
    "output/pdf/white_line_combined.pdf",
)


def _source_only_tree(tmp_path: Path) -> Path:
    """A tree with source, figures, and a fresh manifest, but no rendered bundle."""

    from test_audit import materialize_passing_project

    materialize_passing_project(tmp_path)
    for relative in RENDERED_BUNDLE:
        assert (tmp_path / relative).is_file(), relative
        (tmp_path / relative).unlink()
    return tmp_path


def test_audit_defers_render_errors_without_a_bundle_and_still_exits_zero(
    tmp_path: Path,
) -> None:
    """A separated copy must be able to run the source-side gate to completion.

    Absence is asserted first, so this is a positive control rather than a
    tolerated silence: the audit must *report* the missing bundle while the
    process exits ``0`` on what is actually decidable without a render.
    """

    root = _source_only_tree(tmp_path)
    for relative in RENDERED_BUNDLE:
        assert not (root / relative).is_file(), relative

    completed = _run("audit_project.py", ["--project-root", str(root)])
    assert completed.returncode == 0, completed.stdout[-600:]
    assert "render-dependent error(s) deferred" in completed.stdout
    assert "output/web/_combined_manuscript.md is missing" in completed.stdout
    assert "source-side errors" not in completed.stdout


def test_require_render_turns_the_deferred_errors_back_into_a_failure(
    tmp_path: Path,
) -> None:
    """The post-render gate must not be softened by the pre-render carve-out."""

    root = _source_only_tree(tmp_path)
    completed = _run("audit_project.py", ["--project-root", str(root), "--require-render"])
    assert completed.returncode == 1, completed.stdout[-600:]
    assert "output/pdf/white_line_combined.pdf is missing" in completed.stdout


def test_a_source_side_defect_still_fails_the_pre_render_audit(tmp_path: Path) -> None:
    """Positive control: the deferral must not swallow a real source blocker."""

    root = _source_only_tree(tmp_path)
    manuscript = root / "manuscript/01_minimal.md"
    manuscript.write_text(
        manuscript.read_text(encoding="utf-8").replace("@Known2026", "@Missing2026"),
        encoding="utf-8",
    )

    completed = _run("audit_project.py", ["--project-root", str(root)])
    assert completed.returncode == 1, completed.stdout[-600:]
    assert "source-side errors that do not depend on the render" in completed.stdout
    assert "Missing2026" in completed.stdout
