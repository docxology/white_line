"""Tests that plant every release-gate defect the audit can observe."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from white_line.audit import (
    FIGURE_LABEL_RE,
    FIGURE_REFERENCE_RE,
    MANIFEST_STALE_ERROR,
    RENDERER_EXCLUDED_MANUSCRIPT_FILES,
    SECTION_LABEL_RE,
    audit_project,
    figure_link_errors,
    manifest_blocking_errors,
    render_dependent_error,
    source_blocking_errors,
    write_source_manifest,
)
from white_line.figures import FIGURE_PLATES, build_figures
from white_line.registry import WHITE_RECORDS
from white_line.serialization import registry_digest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def materialize_passing_project(project_root: Path) -> Path:
    """Write the smallest rendered tree accepted by the audit."""

    build_figures(project_root)
    figure_registry = json.loads(
        (project_root / "output/figures/figure_registry.json").read_text(
            encoding="utf-8"
        )
    )
    assert figure_registry["registry_digest"] == registry_digest(WHITE_RECORDS)
    assert all(
        entry["source_digest"] == registry_digest(WHITE_RECORDS)
        for entry in figure_registry["figures"]
    )
    manuscript_dir = project_root / "manuscript"
    manuscript_dir.mkdir()
    figure_embeds = "\n".join(
        f"![{plate.caption}](../output/figures/{plate.name}.png){{#{plate.label}}}"
        for plate in FIGURE_PLATES
    )
    manuscript = f"# Minimal audit fixture {{#sec:minimal-audit}}\n\nKnown citation @Known2026.\n\n{figure_embeds}\n"
    (manuscript_dir / "01_minimal.md").write_text(manuscript, encoding="utf-8")
    (manuscript_dir / "references.bib").write_text(
        "@article{Known2026, title={Known}}\n", encoding="utf-8"
    )
    web_dir = project_root / "output/web"
    web_dir.mkdir(parents=True)
    (web_dir / "_combined_manuscript.md").write_text(
        "# Minimal audit fixture {#sec:minimal-audit}\n", encoding="utf-8"
    )
    pdf_dir = project_root / "output/pdf"
    pdf_dir.mkdir(parents=True)
    (pdf_dir / "white_line_combined.pdf").write_bytes(b"%PDF-1.4\nfixture\n")
    initial = audit_project(project_root)
    assert initial["passed"], initial
    assert initial["warnings"]
    write_source_manifest(project_root, initial)
    report = audit_project(project_root)
    assert report["passed"], report
    assert report["warnings"] == []
    return project_root


@pytest.fixture(scope="session")
def passing_project_seed(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build generated artifacts once before copying them into isolated trees."""

    return materialize_passing_project(tmp_path_factory.mktemp("passing-audit-project"))


@pytest.fixture
def passing_project(tmp_path: Path, passing_project_seed: Path) -> Path:
    """Provide a real file tree whose source and rendered inputs agree."""

    shutil.copytree(passing_project_seed, tmp_path, dirs_exist_ok=True)
    return tmp_path


def figure_registry_path(project_root: Path) -> Path:
    """Locate the generated figure registry in a fixture tree."""

    return project_root / "output/figures/figure_registry.json"


def read_figure_registry(project_root: Path) -> dict[str, Any]:
    """Read the generated registry before planting one defect."""

    return json.loads(figure_registry_path(project_root).read_text(encoding="utf-8"))


def write_figure_registry(project_root: Path, registry: object) -> None:
    """Replace the fixture registry with an explicit JSON value."""

    figure_registry_path(project_root).write_text(
        json.dumps(registry), encoding="utf-8"
    )


def refresh_manifest(project_root: Path) -> dict[str, Any]:
    """Keep the manifest current while a test isolates another defect."""

    report = audit_project(project_root)
    write_source_manifest(project_root, report)
    return audit_project(project_root)


def assert_rejected(report: dict[str, Any], fragment: str) -> None:
    """Assert that a planted defect blocks the release gate."""

    assert report["passed"] is False
    assert any(fragment in error for error in report["errors"]), report["errors"]


def test_matching_reference_and_registry_sets_yield_no_errors() -> None:
    errors = figure_link_errors(
        referenced_figures={"a.png", "b.png"},
        registered_files={"a.png", "b.png"},
        referenced_labels={"fig:a", "fig:b"},
        registered_labels={"fig:a", "fig:b"},
    )
    assert errors == []


def test_referenced_but_unregistered_figure_is_rejected() -> None:
    errors = figure_link_errors(
        referenced_figures={"a.png", "ghost.png"},
        registered_files={"a.png"},
        referenced_labels={"fig:a", "fig:ghost"},
        registered_labels={"fig:a"},
    )
    assert any("unregistered figures: ['ghost.png']" in error for error in errors)
    assert any("unregistered figure labels: ['fig:ghost']" in error for error in errors)


def test_registered_but_unembedded_figure_is_rejected() -> None:
    """Positive control for the inert-figure direction: generated but never embedded."""

    errors = figure_link_errors(
        referenced_figures={"a.png"},
        registered_files={"a.png", "inert.png"},
        referenced_labels={"fig:a"},
        registered_labels={"fig:a", "fig:inert"},
    )
    assert any(
        "not embedded in any manuscript file: ['inert.png']" in error
        for error in errors
    )
    assert any(
        "never appear in the manuscript: ['fig:inert']" in error for error in errors
    )


def test_both_figure_link_directions_are_reported_together() -> None:
    errors = figure_link_errors(
        referenced_figures={"ghost.png"},
        registered_files={"inert.png"},
        referenced_labels=set(),
        registered_labels=set(),
    )
    assert len(errors) == 2
    assert any("unregistered figures" in error for error in errors)
    assert any("not embedded" in error for error in errors)


def test_real_manuscript_embeds_every_registered_figure_and_vice_versa() -> None:
    """The shipped tree satisfies the bidirectional invariant with the audit regexes."""

    registry_path = PROJECT_ROOT / "output/figures/figure_registry.json"
    assert registry_path.is_file(), "run scripts/build_figures.py first"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    manuscript_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PROJECT_ROOT / "manuscript").glob("*.md"))
    )
    errors = figure_link_errors(
        referenced_figures=set(FIGURE_REFERENCE_RE.findall(manuscript_text)),
        registered_files={entry["filename"] for entry in registry["figures"]},
        referenced_labels=set(FIGURE_LABEL_RE.findall(manuscript_text)),
        registered_labels={entry["label"] for entry in registry["figures"]},
    )
    assert errors == []


#: Written by the external render host; nothing in this repository produces
#: them. ``docs/reproducibility.md`` routes the render through the external
#: ``docxology/template`` engine, so a source-only tree — which is what a clone
#: of this repository is — has no rendered bundle at all.
RENDERED_BUNDLE = (
    Path("output/web/_combined_manuscript.md"),
    Path("output/pdf/white_line_combined.pdf"),
)


def test_real_project_has_no_release_blocker_beyond_manifest_staleness() -> None:
    report = audit_project(PROJECT_ROOT)
    blocking = manifest_blocking_errors(report["errors"])

    missing = [str(path) for path in RENDERED_BUNDLE if not (PROJECT_ROOT / path).is_file()]
    if missing:
        # Positive control: the audit must *report* the absent bundle rather
        # than pass silently, and it must report nothing else. Asserting the
        # residue keeps this branch bound to real behaviour instead of
        # degrading into an unconditional skip that would hide a genuine
        # source-side blocker.
        assert source_blocking_errors(report["errors"]) == []
        assert report["checks"]["rendered_bundle"] is False
        pytest.skip(f"no rendered bundle in this checkout: {missing}")

    assert blocking == []


def test_folder_guides_are_not_treated_as_manuscript_sections(
    passing_project: Path,
) -> None:
    """Keep required manuscript-folder guidance outside rendered section checks."""

    manuscript = passing_project / "manuscript"
    (manuscript / "AGENTS.md").write_text(
        "# Manuscript folder guidance\n", encoding="utf-8"
    )
    (manuscript / "README.md").write_text(
        "# Manuscript orientation\n", encoding="utf-8"
    )
    report = audit_project(passing_project)
    assert not any(
        "AGENTS.md" in error or "README.md" in error for error in report["errors"]
    )
    assert report["checks"]["ledger_sound"]
    assert report["checks"]["figure_registry"]
    assert report["checks"]["manuscript_section_labels"]
    assert report["checks"]["manuscript_figure_links"]
    assert report["checks"]["bibliography"]
    assert report["checks"]["rendered_bundle"]


def test_renderer_excluded_syntax_file_is_ignored_by_the_audit(
    passing_project: Path,
) -> None:
    """Keep source checks aligned with the template renderer's exclusion set."""

    (passing_project / "manuscript/SYNTAX.md").write_text(
        "# Renderer syntax guide\n", encoding="utf-8"
    )
    report = audit_project(passing_project)
    assert report["passed"], report
    assert "SYNTAX.md" not in report["source_files"]


def test_missing_figure_registry_is_rejected(passing_project: Path) -> None:
    figure_registry_path(passing_project).unlink()
    assert_rejected(
        refresh_manifest(passing_project),
        "output/figures/figure_registry.json is missing",
    )


def test_unreadable_figure_registry_is_rejected(passing_project: Path) -> None:
    figure_registry_path(passing_project).write_text("{", encoding="utf-8")
    assert_rejected(
        refresh_manifest(passing_project),
        "output/figures/figure_registry.json is unreadable JSON",
    )


def test_non_object_figure_registry_is_rejected(passing_project: Path) -> None:
    write_figure_registry(passing_project, [])
    assert_rejected(
        refresh_manifest(passing_project),
        "output/figures/figure_registry.json must contain a JSON object",
    )


def test_non_list_figures_is_rejected(passing_project: Path) -> None:
    registry = read_figure_registry(passing_project)
    registry["figures"] = {}
    write_figure_registry(passing_project, registry)
    assert_rejected(
        refresh_manifest(passing_project), "figure registry 'figures' must be a list"
    )


def test_non_object_figure_entry_is_rejected(passing_project: Path) -> None:
    registry = read_figure_registry(passing_project)
    registry["figures"].append("not an object")
    write_figure_registry(passing_project, registry)
    assert_rejected(
        refresh_manifest(passing_project), "figure registry contains a non-object entry"
    )


def test_duplicate_figure_label_is_rejected(passing_project: Path) -> None:
    registry = read_figure_registry(passing_project)
    registry["figures"][1]["label"] = registry["figures"][0]["label"]
    write_figure_registry(passing_project, registry)
    assert_rejected(
        refresh_manifest(passing_project), "figure registry contains duplicate labels"
    )


def test_wrong_figure_registry_schema_is_rejected(passing_project: Path) -> None:
    registry = read_figure_registry(passing_project)
    registry["schema_version"] = "wrong"
    write_figure_registry(passing_project, registry)
    assert_rejected(
        refresh_manifest(passing_project), "figure registry schema_version is not white-line.figure-registry/1.3"
    )


def test_mismatched_figure_registry_digest_is_rejected(passing_project: Path) -> None:
    registry = read_figure_registry(passing_project)
    registry["registry_digest"] = "wrong"
    write_figure_registry(passing_project, registry)
    assert_rejected(
        refresh_manifest(passing_project),
        "figure registry digest does not match WHITE_RECORDS",
    )


def test_unsafe_figure_filename_is_rejected(passing_project: Path) -> None:
    registry = read_figure_registry(passing_project)
    registry["figures"][0]["filename"] = "../escape.png"
    write_figure_registry(passing_project, registry)
    assert_rejected(
        refresh_manifest(passing_project),
        "figure entry has unsafe filename: '../escape.png'",
    )


def test_missing_png_artifact_is_rejected(passing_project: Path) -> None:
    (passing_project / "output/figures/white_cover_art.png").unlink()
    assert_rejected(
        refresh_manifest(passing_project),
        "missing figure artifact: output/figures/white_cover_art.png",
    )


def test_missing_svg_companion_is_rejected(passing_project: Path) -> None:
    (passing_project / "output/figures/white_cover_art.svg").unlink()
    assert_rejected(
        refresh_manifest(passing_project),
        "missing SVG companion: output/figures/white_cover_art.svg",
    )


@pytest.mark.parametrize(
    "field", ("label", "caption", "alt", "source", "source_digest")
)
def test_blank_figure_metadata_is_rejected(passing_project: Path, field: str) -> None:
    registry = read_figure_registry(passing_project)
    registry["figures"][0][field] = " "
    write_figure_registry(passing_project, registry)
    assert_rejected(
        refresh_manifest(passing_project),
        f"figure entry 'white_cover_art.png' has no usable {field}",
    )


def test_stale_per_entry_digest_is_rejected(passing_project: Path) -> None:
    registry = read_figure_registry(passing_project)
    registry["figures"][0]["source_digest"] = "outdated"
    write_figure_registry(passing_project, registry)
    assert_rejected(
        refresh_manifest(passing_project),
        "figure entry 'white_cover_art.png' has a stale registry digest",
    )


def test_missing_white_registry_is_rejected(passing_project: Path) -> None:
    (passing_project / "output/figures/white_registry.json").unlink()
    assert_rejected(
        refresh_manifest(passing_project),
        "output/figures/white_registry.json is missing",
    )


def test_mismatched_white_registry_digest_is_rejected(passing_project: Path) -> None:
    path = passing_project / "output/figures/white_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    registry["digest"] = "wrong"
    path.write_text(json.dumps(registry), encoding="utf-8")
    assert_rejected(
        refresh_manifest(passing_project),
        "white registry artifact digest does not match WHITE_RECORDS",
    )


def test_mismatched_white_registry_records_are_rejected(passing_project: Path) -> None:
    path = passing_project / "output/figures/white_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    registry["records"] = []
    path.write_text(json.dumps(registry), encoding="utf-8")
    assert_rejected(
        refresh_manifest(passing_project),
        "white registry artifact records do not match WHITE_RECORDS",
    )


def test_unlabelled_first_manuscript_heading_is_rejected(passing_project: Path) -> None:
    manuscript = passing_project / "manuscript/01_minimal.md"
    manuscript.write_text(
        manuscript.read_text(encoding="utf-8").replace(" {#sec:minimal-audit}", "", 1),
        encoding="utf-8",
    )
    combined = passing_project / "output/web/_combined_manuscript.md"
    combined.write_text("# Minimal audit fixture\n", encoding="utf-8")
    assert_rejected(
        refresh_manifest(passing_project),
        "manuscript files lack a labelled H1 section heading: ['01_minimal.md']",
    )


def test_missing_bibliography_key_is_rejected(passing_project: Path) -> None:
    manuscript = passing_project / "manuscript/01_minimal.md"
    manuscript.write_text(
        manuscript.read_text(encoding="utf-8").replace("@Known2026", "@Missing2026"),
        encoding="utf-8",
    )
    assert_rejected(
        refresh_manifest(passing_project),
        "manuscript cites missing bibliography keys: ['Missing2026']",
    )


def test_missing_combined_manuscript_is_rejected(passing_project: Path) -> None:
    (passing_project / "output/web/_combined_manuscript.md").unlink()
    assert_rejected(
        refresh_manifest(passing_project),
        "output/web/_combined_manuscript.md is missing",
    )


def test_missing_pdf_is_rejected(passing_project: Path) -> None:
    (passing_project / "output/pdf/white_line_combined.pdf").unlink()
    assert_rejected(
        refresh_manifest(passing_project),
        "output/pdf/white_line_combined.pdf is missing or not a PDF",
    )


def test_non_pdf_artifact_is_rejected(passing_project: Path) -> None:
    (passing_project / "output/pdf/white_line_combined.pdf").write_bytes(b"not a PDF")
    assert_rejected(
        refresh_manifest(passing_project),
        "output/pdf/white_line_combined.pdf is missing or not a PDF",
    )


def test_missing_rendered_source_heading_is_rejected(passing_project: Path) -> None:
    (passing_project / "output/web/_combined_manuscript.md").write_text(
        "# Another heading\n", encoding="utf-8"
    )
    assert_rejected(
        refresh_manifest(passing_project),
        "rendered manuscript is missing source headings",
    )


def test_missing_source_manifest_warns_without_blocking(passing_project: Path) -> None:
    (passing_project / "output/reports/source_manifest.json").unlink()
    report = audit_project(passing_project)
    assert report["passed"]
    assert report["errors"] == []
    assert report["warnings"] == [
        "output/reports/source_manifest.json is missing; run with --write-manifest after rendering"
    ]


def test_stale_source_manifest_is_rejected_but_can_be_rewritten(
    passing_project: Path,
) -> None:
    manuscript = passing_project / "manuscript/01_minimal.md"
    manuscript.write_text(
        manuscript.read_text(encoding="utf-8") + "\nCurrent source changed.\n",
        encoding="utf-8",
    )
    stale = audit_project(passing_project)
    assert_rejected(stale, MANIFEST_STALE_ERROR)
    assert manifest_blocking_errors(stale["errors"]) == []
    manifest_path = write_source_manifest(passing_project, stale)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert set(manifest) == {
        "schema_version",
        "source_digest",
        "registry_digest",
        "source_files",
    }
    renewed = audit_project(passing_project)
    assert renewed["passed"]
    assert MANIFEST_STALE_ERROR not in renewed["errors"]


def test_stale_manifest_alone_does_not_block_a_manifest_rewrite() -> None:
    assert manifest_blocking_errors([MANIFEST_STALE_ERROR]) == []


def test_any_other_error_still_blocks_a_manifest_rewrite() -> None:
    other = "manuscript references unregistered figures: ['ghost.png']"
    assert manifest_blocking_errors([MANIFEST_STALE_ERROR, other]) == [other]
    assert manifest_blocking_errors([other]) == [other]


def test_figure_regexes_match_the_manuscript_embed_form() -> None:
    sample = "![A caption.](../output/figures/white_example.png){#fig:white-example width=80%}"
    assert FIGURE_REFERENCE_RE.findall(sample) == ["white_example.png"]
    assert re.findall(FIGURE_LABEL_RE, sample) == ["fig:white-example"]


def test_manuscript_section_labels_match_the_sidecar_convention() -> None:
    for path in sorted((PROJECT_ROOT / "manuscript").glob("*.md")):
        if (
            path.name == "preamble.md"
            or path.name in RENDERER_EXCLUDED_MANUSCRIPT_FILES
        ):
            continue
        first_heading = next(
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("# ")
        )
        assert SECTION_LABEL_RE.match(first_heading), path


def test_audit_cli_reports_json_for_a_real_temporary_tree(tmp_path: Path) -> None:
    materialize_passing_project(tmp_path)
    completed = subprocess.run(
        [sys.executable, "scripts/audit_project.py", "--project-root", str(tmp_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    report = json.loads(completed.stdout)
    assert report["passed"]
    assert report["errors"] == []


def test_registry_content_edit_without_re_pinning_the_digest_is_rejected(
    passing_project: Path,
) -> None:
    """Positive control for the ``LEDGER_VERSION`` bump instruction.

    The instruction "bump ``LEDGER_VERSION`` when registry content changes" was
    enforced by nothing. The silent case is a reworded description: the record
    count and the per-kind partition are untouched, so every count-based
    baseline still matches. Here that exact edit is planted and the audit must
    refuse it until ``LEDGER_VERSION_DIGEST`` is re-pinned.
    """

    from dataclasses import replace

    from white_line.version import LEDGER_VERSION_DIGEST

    reworded = (
        replace(WHITE_RECORDS[0], description=WHITE_RECORDS[0].description + " Also."),
        *WHITE_RECORDS[1:],
    )
    assert len(reworded) == len(WHITE_RECORDS)
    assert [record.kind for record in reworded] == [
        record.kind for record in WHITE_RECORDS
    ]
    assert registry_digest(reworded) != LEDGER_VERSION_DIGEST

    report = audit_project(passing_project, records=reworded)
    assert_rejected(report, "without re-pinning LEDGER_VERSION_DIGEST")
    assert report["checks"]["ledger_version_pinned"] is False
    # The unmodified registry still passes, so the check is not simply broken.
    assert audit_project(passing_project)["checks"]["ledger_version_pinned"] is True


def test_hand_edited_png_bytes_are_rejected(passing_project: Path) -> None:
    """A replaced raster used to pass: the audit only checked the filename."""

    png = passing_project / "output/figures/white_cover_art.png"
    original = png.read_bytes()
    png.write_bytes(original + b"\n% edited by hand\n")
    report = refresh_manifest(passing_project)
    assert_rejected(
        report,
        "output/figures/white_cover_art.png bytes do not match the png_digest",
    )
    assert report["checks"]["figure_artifact_bytes"] is False
    png.write_bytes(original)
    assert refresh_manifest(passing_project)["passed"]


def test_hand_edited_svg_bytes_are_rejected(passing_project: Path) -> None:
    svg = passing_project / "output/figures/white_cover_art.svg"
    svg.write_text(svg.read_text(encoding="utf-8") + "<!-- edited -->", encoding="utf-8")
    assert_rejected(
        refresh_manifest(passing_project),
        "output/figures/white_cover_art.svg bytes do not match the svg_digest",
    )


def test_wrong_white_registry_schema_is_rejected(passing_project: Path) -> None:
    path = passing_project / "output/figures/white_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    registry["schema_version"] = "1.1"
    path.write_text(json.dumps(registry), encoding="utf-8")
    assert_rejected(
        refresh_manifest(passing_project), "white registry schema_version is not"
    )


def test_missing_bibliography_is_reported_not_raised(passing_project: Path) -> None:
    """Every other absent artifact is a structured error; so is this one."""

    (passing_project / "manuscript/references.bib").unlink()
    report = refresh_manifest(passing_project)
    assert_rejected(report, "manuscript/references.bib is missing")
    # The cited key now has no entry, which is the second, separate error.
    assert_rejected(report, "manuscript cites missing bibliography keys")
    assert report["checks"]["bibliography"] is False


def test_uncited_bibliography_entry_is_rejected(passing_project: Path) -> None:
    bibliography = passing_project / "manuscript/references.bib"
    bibliography.write_text(
        bibliography.read_text(encoding="utf-8")
        + "@article{NeverCited2026, title={Unused}}\n",
        encoding="utf-8",
    )
    assert_rejected(
        refresh_manifest(passing_project),
        "bibliography keys are never cited in the manuscript: ['NeverCited2026']",
    )


def test_render_dependent_error_matches_only_render_surface_errors() -> None:
    """Positive and negative control for the render-phase classifier."""

    assert render_dependent_error("output/web/_combined_manuscript.md is missing")
    assert render_dependent_error(
        "output/pdf/white_line_combined.pdf is missing or not a PDF"
    )
    assert render_dependent_error(
        "rendered manuscript is missing source headings: ['# Abstract']"
    )
    assert not render_dependent_error(MANIFEST_STALE_ERROR)
    assert not render_dependent_error(
        "manuscript cites missing bibliography keys: ['Ghost2026']"
    )
    assert not render_dependent_error("figure registry is missing")


def test_source_blocking_errors_keeps_source_defects_and_drops_render_and_manifest() -> None:
    """A render-phase carve-out must not swallow a real source-side blocker."""

    errors = [
        "output/web/_combined_manuscript.md is missing",
        "rendered manuscript is missing source headings: ['# Abstract']",
        MANIFEST_STALE_ERROR,
        "manuscript cites missing bibliography keys: ['Ghost2026']",
    ]
    assert source_blocking_errors(errors) == [
        "manuscript cites missing bibliography keys: ['Ghost2026']"
    ]
    assert source_blocking_errors(errors[:3]) == []
