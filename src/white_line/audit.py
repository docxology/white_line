"""Check that White Line source and rendered artifacts agree."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .figures.build import artifact_digest
from .formalism import declared_prefixes, parse_blocks, split_citations
from .invariants import all_ledger_checks
from .model import AbsenceRecord
from .registry import WHITE_RECORDS
from .serialization import (
    FIGURE_REGISTRY_SCHEMA,
    REGISTRY_ARTIFACT_SCHEMA,
    canonical_registry,
    registry_digest,
)
from .version import LEDGER_VERSION_DIGEST

MANIFEST_STALE_ERROR = (
    "source manifest digest does not match current manuscript and figure inputs"
)

#: Errors the audit can only clear once the sibling template checkout has
#: rendered the bundle. Before that they are not false, they are undecided,
#: and the difference matters: the documented release sequence audits the
#: source *before* the render, so treating them as failures makes the
#: pre-render audit unconditionally red on a clean tree — and green only when
#: a previous render's ``output/`` happened to survive, which is an audit of
#: artifacts it was not describing.
RENDER_MISSING_ERRORS: frozenset[str] = frozenset(
    {
        "output/web/_combined_manuscript.md is missing",
        "output/pdf/white_line_combined.pdf is missing or not a PDF",
    }
)
RENDER_HEADINGS_ERROR_PREFIX = "rendered manuscript is missing source headings:"

#: Mirrors the sibling template renderer's manuscript exclusion contract.
RENDERER_EXCLUDED_MANUSCRIPT_FILES: frozenset[str] = frozenset(
    {"AGENTS.md", "README.md", "SYNTAX.md"}
)

FIGURE_REFERENCE_RE = re.compile(r"\]\(\.\./output/figures/([^)]+\.png)\)")
FIGURE_LABEL_RE = re.compile(r"\{#(fig:[^\s}]+)")
SECTION_LABEL_RE = re.compile(r"^# .+\{#(sec:[^\s}]+)\}\s*$")
BIBLIOGRAPHY_ENTRY_RE = re.compile(r"@\w+\{\s*([^,\s]+)", re.MULTILINE)


def digest_inputs(project_root: Path) -> tuple[str, list[str]]:
    """Hash the files that must agree with a rendered publication bundle."""

    root = project_root.resolve()
    paths = sorted(
        [
            *(
                path
                for path in root.glob("manuscript/*")
                if path.name not in RENDERER_EXCLUDED_MANUSCRIPT_FILES
            ),
            root / "output/figures/figure_registry.json",
            root / "output/figures/white_registry.json",
        ],
        key=lambda path: path.relative_to(root).as_posix(),
    )
    digest = hashlib.sha256()
    included: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
        included.append(relative)
    return digest.hexdigest(), included


def figure_link_errors(
    referenced_figures: set[str],
    registered_files: set[str],
    referenced_labels: set[str],
    registered_labels: set[str],
) -> list[str]:
    """Cross-check manuscript figure references against the registry in both directions.

    A referenced-but-unregistered figure is a broken link; a
    registered-but-unembedded figure is inert output and equally forbidden.
    """

    errors: list[str] = []
    missing_figures = sorted(referenced_figures - registered_files)
    missing_labels = sorted(referenced_labels - registered_labels)
    orphan_figures = sorted(
        item for item in registered_files - referenced_figures if isinstance(item, str)
    )
    orphan_labels = sorted(
        item for item in registered_labels - referenced_labels if isinstance(item, str)
    )
    if missing_figures:
        errors.append(f"manuscript references unregistered figures: {missing_figures}")
    if missing_labels:
        errors.append(f"manuscript uses unregistered figure labels: {missing_labels}")
    if orphan_figures:
        errors.append(
            f"registered figures are not embedded in any manuscript file: {orphan_figures}"
        )
    if orphan_labels:
        errors.append(
            f"registered figure labels never appear in the manuscript: {orphan_labels}"
        )
    return errors


def _load_json(
    path: Path, project_root: Path, errors: list[str]
) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(project_root)} is unreadable JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path.relative_to(project_root)} must contain a JSON object")
        return None
    return value


def audit_project(
    project_root: Path, records: Iterable[AbsenceRecord] = WHITE_RECORDS
) -> dict[str, Any]:
    """Return a deterministic audit report for ``project_root``.

    ``records`` defaults to the live registry. It is injectable so that a test
    can plant the exact drift this audit exists to catch — a registry edit that
    changes content without re-pinning ``LEDGER_VERSION_DIGEST`` — against a
    real rendered tree, rather than asserting the message by hand.
    """

    root = project_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    record_tuple = tuple(records)
    ledger_results = all_ledger_checks(record_tuple)
    checks["ledger_sound"] = all(result.passed for result in ledger_results)
    errors.extend(
        f"ledger {result.name}: {result.detail}"
        for result in ledger_results
        if not result.passed
    )

    # A registry-content edit changes this digest. Requiring the pinned value
    # to be re-stated alongside LEDGER_VERSION turns "bump LEDGER_VERSION when
    # registry content changes" from an instruction into a gate: without it, a
    # reworded description leaves record counts and kinds untouched and every
    # other check green.
    live_registry_digest = registry_digest(record_tuple)
    ledger_version_pinned = live_registry_digest == LEDGER_VERSION_DIGEST
    if not ledger_version_pinned:
        errors.append(
            "registry content changed without re-pinning LEDGER_VERSION_DIGEST: "
            f"live digest {live_registry_digest} does not match the pinned "
            f"{LEDGER_VERSION_DIGEST}; bump LEDGER_VERSION and re-pin the digest"
        )
    checks["ledger_version_pinned"] = ledger_version_pinned

    figure_dir = root / "output/figures"
    figure_registry_path = figure_dir / "figure_registry.json"
    figure_registry = (
        _load_json(figure_registry_path, root, errors)
        if figure_registry_path.is_file()
        else None
    )
    if figure_registry is None and not figure_registry_path.is_file():
        errors.append("output/figures/figure_registry.json is missing")
    figure_entries = figure_registry.get("figures", []) if figure_registry else []
    if not isinstance(figure_entries, list):
        errors.append("figure registry 'figures' must be a list")
        figure_entries = []
    labels = [
        label if isinstance(label := entry.get("label"), str) else None
        for entry in figure_entries
        if isinstance(entry, dict)
    ]
    checks["figure_registry"] = bool(figure_entries) and len(labels) == len(set(labels))
    if len(labels) != len(set(labels)):
        duplicate_labels = sorted(
            {label for label in labels if labels.count(label) > 1},
            key=lambda label: "" if label is None else label,
        )
        errors.append(f"figure registry contains duplicate labels: {duplicate_labels}")
    artifact_bytes_agree = True
    if figure_registry:
        if figure_registry.get("schema_version") != FIGURE_REGISTRY_SCHEMA:
            errors.append(
                f"figure registry schema_version is not {FIGURE_REGISTRY_SCHEMA}"
            )
        if figure_registry.get("registry_digest") != live_registry_digest:
            errors.append("figure registry digest does not match WHITE_RECORDS")
        for entry in figure_entries:
            if not isinstance(entry, dict):
                errors.append("figure registry contains a non-object entry")
                artifact_bytes_agree = False
                continue
            filename = entry.get("filename")
            if not isinstance(filename, str) or Path(filename).name != filename:
                errors.append(f"figure entry has unsafe filename: {filename!r}")
                artifact_bytes_agree = False
                continue
            png = figure_dir / filename
            svg = figure_dir / f"{Path(filename).stem}.svg"
            if not png.is_file():
                errors.append(f"missing figure artifact: output/figures/{filename}")
                artifact_bytes_agree = False
            if not svg.is_file():
                errors.append(f"missing SVG companion: output/figures/{svg.name}")
                artifact_bytes_agree = False
            for field in (
                "label",
                "caption",
                "alt",
                "source",
                "source_digest",
                "png_digest",
                "svg_digest",
            ):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    errors.append(f"figure entry {filename!r} has no usable {field}")
                    artifact_bytes_agree = False
            if entry.get("source_digest") != live_registry_digest:
                errors.append(f"figure entry {filename!r} has a stale registry digest")
            # Byte-level binding: without it a hand-edited or replaced raster
            # passes the gate, because every other check reads names and JSON.
            for artifact, field in ((png, "png_digest"), (svg, "svg_digest")):
                if not artifact.is_file():
                    continue
                if entry.get(field) != artifact_digest(artifact):
                    errors.append(
                        f"output/figures/{artifact.name} bytes do not match the "
                        f"{field} recorded in figure_registry.json"
                    )
                    artifact_bytes_agree = False
    else:
        artifact_bytes_agree = False
    checks["figure_artifact_bytes"] = artifact_bytes_agree

    white_registry_path = figure_dir / "white_registry.json"
    white_registry = (
        _load_json(white_registry_path, root, errors)
        if white_registry_path.is_file()
        else None
    )
    if white_registry is None and not white_registry_path.is_file():
        errors.append("output/figures/white_registry.json is missing")
    if white_registry:
        if white_registry.get("schema_version") != REGISTRY_ARTIFACT_SCHEMA:
            errors.append(
                f"white registry schema_version is not {REGISTRY_ARTIFACT_SCHEMA}"
            )
        if white_registry.get("digest") != live_registry_digest:
            errors.append("white registry artifact digest does not match WHITE_RECORDS")
        if white_registry.get("records") != json.loads(
            canonical_registry(record_tuple)
        ):
            errors.append("white registry artifact records do not match WHITE_RECORDS")

    manuscript_files = sorted(
        path
        for path in (root / "manuscript").glob("*.md")
        if path.name not in RENDERER_EXCLUDED_MANUSCRIPT_FILES
    )
    manuscript_sources = {
        path.name: path.read_text(encoding="utf-8") for path in manuscript_files
    }
    manuscript_text = "\n".join(
        manuscript_sources[name] for name in sorted(manuscript_sources)
    )
    missing_section_labels = []
    for path in manuscript_files:
        if path.name == "preamble.md":
            continue
        first_heading = next(
            (
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.startswith("# ")
            ),
            "",
        )
        if not SECTION_LABEL_RE.match(first_heading):
            missing_section_labels.append(path.name)
    if missing_section_labels:
        errors.append(
            f"manuscript files lack a labelled H1 section heading: {missing_section_labels}"
        )
    checks["manuscript_section_labels"] = not missing_section_labels
    referenced_figures = set(FIGURE_REFERENCE_RE.findall(manuscript_text))
    referenced_labels = set(FIGURE_LABEL_RE.findall(manuscript_text))
    registered_files = {
        filename
        for entry in figure_entries
        if isinstance(entry, dict)
        and isinstance(filename := entry.get("filename"), str)
    }
    registered_labels = {
        label
        for entry in figure_entries
        if isinstance(entry, dict) and isinstance(label := entry.get("label"), str)
    }
    link_errors = figure_link_errors(
        referenced_figures, registered_files, referenced_labels, registered_labels
    )
    errors.extend(link_errors)
    checks["manuscript_figure_links"] = not link_errors

    # Read like every other artifact: a missing file is a reported error, not
    # an unhandled traceback out of the middle of the audit.
    try:
        bibliography = (root / "manuscript/references.bib").read_text(encoding="utf-8")
    except OSError:
        errors.append("manuscript/references.bib is missing")
        bibliography = ""
    # ``[@def:kinds]`` parses as a citation but is consumed by the renderer's
    # formalism filter before the bibliography machinery sees it. Partitioning
    # with the filter's own rule keeps a definition label from being reported
    # here as a bibliography entry the manuscript forgot to write.
    _references, citation_keys = split_citations(
        manuscript_text, declared_prefixes(parse_blocks(manuscript_sources))
    )
    bib_keys = set(BIBLIOGRAPHY_ENTRY_RE.findall(bibliography))
    missing_citations = sorted(citation_keys - bib_keys)
    # The reverse direction: an entry no prose cites is an unbacked claim of
    # scholarship. It is an error, not a warning, because docs/scholarship_map.md
    # states that each entry records the edition or DOI used for a claim.
    orphan_citations = sorted(bib_keys - citation_keys)
    if missing_citations:
        errors.append(
            f"manuscript cites missing bibliography keys: {missing_citations}"
        )
    if orphan_citations:
        errors.append(
            f"bibliography keys are never cited in the manuscript: {orphan_citations}"
        )
    checks["bibliography"] = not missing_citations and not orphan_citations

    combined = root / "output/web/_combined_manuscript.md"
    pdf = root / "output/pdf/white_line_combined.pdf"
    if not combined.is_file():
        errors.append("output/web/_combined_manuscript.md is missing")
        combined_text = ""
    else:
        combined_text = combined.read_text(encoding="utf-8")
    if not pdf.is_file() or not pdf.read_bytes().startswith(b"%PDF-"):
        errors.append("output/pdf/white_line_combined.pdf is missing or not a PDF")
    source_headings = []
    for path in manuscript_files:
        heading = next(
            (
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.startswith("# ")
            ),
            "",
        )
        if heading:
            source_headings.append(heading)
    missing_headings = []
    for heading in source_headings:
        rendered_heading = re.sub(r"\s*\{#[^}]+\}", "", heading)
        if heading not in combined_text and rendered_heading not in combined_text:
            missing_headings.append(heading)
    if missing_headings:
        errors.append(
            f"rendered manuscript is missing source headings: {missing_headings}"
        )
    checks["rendered_bundle"] = (
        not missing_headings and combined.is_file() and pdf.is_file()
    )

    source_digest, source_files = digest_inputs(root)
    source_manifest_path = root / "output/reports/source_manifest.json"
    source_manifest = (
        _load_json(source_manifest_path, root, errors)
        if source_manifest_path.is_file()
        else None
    )
    if source_manifest is None:
        warnings.append(
            "output/reports/source_manifest.json is missing; run with --write-manifest after rendering"
        )
    elif source_manifest.get("source_digest") != source_digest:
        errors.append(MANIFEST_STALE_ERROR)
    checks["source_manifest"] = (
        source_manifest is not None
        and source_manifest.get("source_digest") == source_digest
    )

    return {
        "schema_version": "1.0",
        "passed": not errors,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "registry_digest": live_registry_digest,
        "source_digest": source_digest,
        "source_files": source_files,
    }


def manifest_blocking_errors(errors: list[str]) -> list[str]:
    """Errors that must block a manifest rewrite.

    A stale manifest digest is exactly the condition ``--write-manifest`` is
    asked to repair, so it alone must not block the rewrite; every other error
    still does. Without this carve-out the documented release sequence
    deadlocks after any manuscript edit.
    """

    return [error for error in errors if error != MANIFEST_STALE_ERROR]


def render_dependent_error(error: str) -> bool:
    """Whether *error* can only be cleared by rendering the bundle."""

    return error in RENDER_MISSING_ERRORS or error.startswith(
        RENDER_HEADINGS_ERROR_PREFIX
    )


def source_blocking_errors(errors: list[str]) -> list[str]:
    """Errors decidable without a rendered bundle.

    The pre-render audit runs before the sibling template checkout has written
    ``output/web/`` and ``output/pdf/``. Only these errors can be acted on at
    that point; the render-dependent ones stay in ``errors`` and still block
    the post-render audit, which is the gate that matters for release.
    """

    return [error for error in manifest_blocking_errors(errors) if not render_dependent_error(error)]


def write_source_manifest(project_root: Path, report: dict[str, Any]) -> Path:
    """Write the source fingerprint returned by an audit."""

    path = project_root.resolve() / "output/reports/source_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "source_digest": report["source_digest"],
                "registry_digest": report["registry_digest"],
                "source_files": report["source_files"],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


__all__ = [
    "BIBLIOGRAPHY_ENTRY_RE",
    "FIGURE_LABEL_RE",
    "FIGURE_REFERENCE_RE",
    "MANIFEST_STALE_ERROR",
    "RENDERER_EXCLUDED_MANUSCRIPT_FILES",
    "SECTION_LABEL_RE",
    "audit_project",
    "digest_inputs",
    "figure_link_errors",
    "manifest_blocking_errors",
    "write_source_manifest",
]
