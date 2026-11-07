import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from white_line import WORKED_AS_OF, worked_report
from white_line.analysis import (
    ASSERTABLE_STATES,
    coverage_matrix,
    events_tally,
    reconciliation_matrix,
)
from white_line.figures import FIGURE_PLATES, FigurePlate, build_figures
from white_line.serialization import FIGURE_REGISTRY_SCHEMA
from white_line.figures.plates import contract, overview
from white_line.model import AbsenceKind, IntakeCode
from white_line.registry import WHITE_RECORDS
from white_line.version import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_figure_plate_registry_is_ordered_and_typed() -> None:
    assert all(isinstance(plate, FigurePlate) for plate in FIGURE_PLATES)
    assert [plate.name for plate in FIGURE_PLATES] == [
        "white_cover_art",
        "white_absence_layers",
        "white_registry_taxonomy",
        "white_review_atlas",
        "white_scholarship_map",
        "white_state_machine",
        "white_reason_trail",
        "white_caution_ladder",
        "white_review_protocol",
        "white_decay_timeline",
        "white_conflict_lattice",
        "white_distribution_panels",
        "white_expiry_queue",
        "white_horizon_dispersion",
        "white_invariant_battery",
        "white_facets_lattice",
        "white_intake_reachability",
    ]




def test_display_maps_reject_incomplete_live_alphabets() -> None:
    """The plates fail rather than silently omitting a newly introduced member."""

    original_kind_titles = dict(overview._KIND_TITLE)
    overview._KIND_TITLE.pop(AbsenceKind.EPISTEMIC)
    try:
        with pytest.raises(ValueError, match="kind display maps"):
            overview.absence_layers()
    finally:
        overview._KIND_TITLE.clear()
        overview._KIND_TITLE.update(original_kind_titles)

    original_dating = dict(contract._DATED_INPUT_GLOSS)
    contract._DATED_INPUT_GLOSS.pop(IntakeCode.UNDATED_OBJECT)
    try:
        with pytest.raises(ValueError, match="intake-code gloss maps"):
            contract.state_machine()
    finally:
        contract._DATED_INPUT_GLOSS.clear()
        contract._DATED_INPUT_GLOSS.update(original_dating)



def test_reason_trail_text_stays_inside_its_computed_rows() -> None:
    import xml.etree.ElementTree as ET
    from white_line.figures.plates.evidence import reason_trail

    root = ET.fromstring(reason_trail())
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    panels = [
        element for element in root.findall("svg:rect", namespace)
        if element.get("x") == "110" and element.get("width") == "1380"
        and float(element.get("y", "0")) >= 358
    ][:-1]  # The final panel is the reading rule, not a scoring row.
    texts = root.findall("svg:text", namespace)
    for panel in panels:
        top = float(panel.attrib["y"])
        bottom = top + float(panel.attrib["height"])
        row_text = [
            element for element in texts
            if element.get("x") in {"150", "680"}
            and top <= float(element.attrib["y"]) < bottom + 18
        ]
        assert row_text
        assert max(float(element.attrib["y"]) for element in row_text) + 6 < bottom

def test_figure_builder_is_deterministic(tmp_path: Path) -> None:
    first = build_figures(tmp_path)
    bytes_first = {path.name: path.read_bytes() for path in first}
    second = build_figures(tmp_path)
    assert {path.name: path.read_bytes() for path in second} == bytes_first
    assert (
        (tmp_path / "output" / "figures" / "white_absence_layers.png")
        .read_bytes()
        .startswith(b"\x89PNG\r\n\x1a\n")
    )
    registry = json.loads(
        (tmp_path / "output" / "figures" / "figure_registry.json").read_text()
    )
    assert registry["schema_version"] == FIGURE_REGISTRY_SCHEMA
    assert len(registry["figures"]) == len(FIGURE_PLATES) == 17
    assert any(item["label"] == "fig:white-cover-art" for item in registry["figures"])
    assert any(
        item["label"] == "fig:white-distribution-panels" for item in registry["figures"]
    )
    assert any(
        item["label"] == "fig:white-review-atlas" for item in registry["figures"]
    )
    assert any(
        item["label"] == "fig:white-scholarship-map" for item in registry["figures"]
    )
    assert any(
        item["label"] == "fig:white-review-protocol" for item in registry["figures"]
    )
    assert any(
        item["label"] == "fig:white-decay-timeline" for item in registry["figures"]
    )
    assert any(
        item["label"] == "fig:white-conflict-lattice" for item in registry["figures"]
    )
    scholarship = next(
        item
        for item in registry["figures"]
        if item["label"] == "fig:white-scholarship-map"
    )
    assert "01c_scholarship.md" in scholarship["source"]
    assert all(item["source"].strip() for item in registry["figures"])


def test_cover_art_version_text_is_bound_to_the_version_authority(
    tmp_path: Path,
) -> None:
    """The cover-art version text derives from the package version, never a frozen literal."""

    build_figures(tmp_path)
    svg = (tmp_path / "output" / "figures" / "white_cover_art.svg").read_text(
        encoding="utf-8"
    )
    assert f"WHITE LINE · {__version__}" in svg
    # A stale frozen literal (the old "0.3" form without the patch part) must not reappear.
    assert "WHITE LINE · 0.3<" not in svg


def test_analysis_figures_are_derived_from_the_sweep_and_the_matrix(
    tmp_path: Path,
) -> None:
    """The two analysis figures carry data-bound landmarks, not hand-drawn ones."""

    build_figures(tmp_path)
    figure_dir = tmp_path / "output" / "figures"
    decay_svg = (figure_dir / "white_decay_timeline.svg").read_text(encoding="utf-8")
    # Horizon crossings computed by the sweep this build: horizons 90/120/180/365 → days 91/121/181/366.
    for offset in (91, 121, 181, 366):
        assert f"day {offset}" in decay_svg
    assert (
        (figure_dir / "white_decay_timeline.png")
        .read_bytes()
        .startswith(b"\x89PNG\r\n\x1a\n")
    )
    lattice_svg = (figure_dir / "white_conflict_lattice.svg").read_text(
        encoding="utf-8"
    )
    assert "NOT_RECORDED" not in lattice_svg
    assert lattice_svg.count("max caution wins") == 6
    assert lattice_svg.count("identity") == 3
    assert (
        (figure_dir / "white_conflict_lattice.png")
        .read_bytes()
        .startswith(b"\x89PNG\r\n\x1a\n")
    )


def test_layers_figure_is_derived_from_the_kind_vocabulary_and_registry(
    tmp_path: Path,
) -> None:
    """Each layers panel carries the shared gloss and live per-kind registry stats.

    The three gloss strings are hard-coded here on purpose: if the module
    gloss map drifts, or the panels are ever re-hardcoded away from it, this
    test fails rather than silently agreeing with the drifted source.
    """

    build_figures(tmp_path)
    svg = (tmp_path / "output" / "figures" / "white_absence_layers.svg").read_text(
        encoding="utf-8"
    )
    assert "unknown, unobserved, or unresolved" in svg
    assert "withheld, unrepresented, or not disclosed" in svg
    assert "left open beyond a useful claim" in svg
    assert f"THE {len(WHITE_RECORDS)}-RECORD REGISTRY" in svg
    for kind in AbsenceKind:
        records = [record for record in WHITE_RECORDS if record.kind is kind]
        horizons = sorted(record.review_horizon_days for record in records)
        assert kind.value in svg
        assert f"{len(records)} registry records" in svg
        assert f"horizons {horizons[0]}–{horizons[-1]} days" in svg


def test_state_machine_names_every_intake_code(tmp_path: Path) -> None:
    """The intake, dating, and match panels name the full live alphabet."""

    build_figures(tmp_path)
    svg = (tmp_path / "output" / "figures" / "white_state_machine.svg").read_text(
        encoding="utf-8"
    )
    for code in IntakeCode:
        assert code.value in svg
    assert "keeps the observation; drops non-ISO dating" in svg
    assert "STALENESS DECAY" in svg
    assert "UNRESOLVED" in svg


def test_caution_ladder_pair_counts_come_from_the_reconciliation_matrix(
    tmp_path: Path,
) -> None:
    """Each rung's ordered-pair annotation matches a fresh matrix computation."""

    build_figures(tmp_path)
    svg = (tmp_path / "output" / "figures" / "white_caution_ladder.svg").read_text(
        encoding="utf-8"
    )
    matrix = reconciliation_matrix()
    for state in ASSERTABLE_STATES:
        wins = sum(1 for kept in matrix.values() if kept is state)
        assert f"kept in {wins} of {len(matrix)} ordered pairs" in svg
    assert "not assertable (ledger-reserved)" in svg


def test_distribution_panels_are_computed_through_the_public_api(
    tmp_path: Path,
) -> None:
    """The distribution figure's counts match the shared worked report."""

    build_figures(tmp_path)
    svg = (tmp_path / "output" / "figures" / "white_distribution_panels.svg").read_text(
        encoding="utf-8"
    )
    report = worked_report()
    tally = events_tally(report)
    matrix = coverage_matrix(report)
    assert f"{sum(tally.values())} intake" in svg
    assert f"events became {len(report.findings)} findings" in svg
    assert f"REVIEW DATE {WORKED_AS_OF}" in svg
    for code in IntakeCode:
        assert code.value in svg
    # One bar per code, in enumeration order, with its length re-derived from
    # the live tally rather than read back as a shape-only count. A zero row
    # draws a fixed-width open stub so the code stays visible.
    bars = [
        (int(y), int(width))
        for y, width in re.findall(
            r'<rect x="640" y="(-?\d+)" width="(\d+)" height="26"', svg
        )
    ]
    assert len(bars) == len(IntakeCode)
    assert [y for y, _width in bars] == sorted(y for y, _width in bars)
    for (_y, width), code in zip(bars, IntakeCode, strict=True):
        assert width == (tally[code] * 240 if tally[code] else 10)
    # Every bar stays inside the drawn intake panel, not merely on the canvas.
    panel = re.search(r'<rect x="110" y="(\d+)" width="1380" height="(\d+)"', svg)
    assert panel is not None
    panel_top, panel_height = int(panel.group(1)), int(panel.group(2))
    assert all(
        panel_top < y and y + 26 < panel_top + panel_height for y, _width in bars
    )
    for kind, row in matrix.items():
        assert kind.value in svg
        assert str(sum(row.values())) in svg
    assert (
        (tmp_path / "output" / "figures" / "white_distribution_panels.png")
        .read_bytes()
        .startswith(b"\x89PNG\r\n\x1a\n")
    )


def test_missing_converter_names_the_figure_and_remedy(tmp_path: Path) -> None:
    environment = {
        **os.environ,
        "WHITE_LINE_RSVG_CONVERT": "white-line-no-such-rsvg-convert",
    }
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; from white_line.figures import build_figures; build_figures(Path('missing-converter-output'))",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "white-line-no-such-rsvg-convert" in completed.stderr
    assert "white_cover_art" in completed.stderr
    assert "install librsvg" in completed.stderr

    previous = os.environ.get("WHITE_LINE_RSVG_CONVERT")
    os.environ["WHITE_LINE_RSVG_CONVERT"] = "white-line-no-such-rsvg-convert"
    try:
        with pytest.raises(RuntimeError, match="white_cover_art") as error:
            build_figures(tmp_path / "in-process")
    finally:
        if previous is None:
            del os.environ["WHITE_LINE_RSVG_CONVERT"]
        else:
            os.environ["WHITE_LINE_RSVG_CONVERT"] = previous
    assert "install librsvg" in str(error.value)


def test_failing_converter_names_the_figure_and_remedy(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; from white_line.figures import build_figures; build_figures(Path('failing-converter-output'))",
        ],
        cwd=tmp_path,
        env={**os.environ, "WHITE_LINE_RSVG_CONVERT": "/usr/bin/false"},
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "/usr/bin/false" in completed.stderr
    assert "white_cover_art" in completed.stderr
    assert "repair librsvg" in completed.stderr

    previous = os.environ.get("WHITE_LINE_RSVG_CONVERT")
    os.environ["WHITE_LINE_RSVG_CONVERT"] = "/usr/bin/false"
    try:
        with pytest.raises(RuntimeError, match="white_cover_art") as error:
            build_figures(tmp_path / "in-process")
    finally:
        if previous is None:
            del os.environ["WHITE_LINE_RSVG_CONVERT"]
        else:
            os.environ["WHITE_LINE_RSVG_CONVERT"] = previous
    assert "repair librsvg" in str(error.value)


# --------------------------------------------------------------------------- #
# The three inspection plates and the battery that backs one of them
# --------------------------------------------------------------------------- #
def test_the_intake_battery_reaches_every_code_with_a_derived_rendering() -> None:
    """The battery is the positive control the reachability plate draws."""

    from datetime import date

    from white_line.worked_examples import (
        intake_probe_inputs,
        intake_reachability_battery,
    )

    probes = intake_reachability_battery()
    assert tuple(probe.code for probe in probes) == tuple(IntakeCode)
    for probe in probes:
        assert probe.event.code is probe.code
        assert probe.event.message.strip()
        assert probe.rendered_input.strip()
    # The rendering is derived from the supplied object, not hand-written.
    undated = next(probe for probe in probes if probe.code is IntakeCode.UNDATED_OBJECT)
    assert "date(2026, 1, 5)" in undated.rendered_input
    non_iterable = next(
        probe for probe in probes if probe.code is IntakeCode.NON_ITERABLE_INPUT
    )
    assert non_iterable.rendered_input == "42"
    # An ISO-string date renders as the quoted string it was supplied as.
    from white_line.worked_examples import _render_observation
    from white_line.model import AbsenceObservation, AbsenceState

    assert (
        _render_observation(
            AbsenceObservation(
                "fallow-ground", AbsenceState.NAMED, "note", "2026-01-05"
            )
        )
        == "AbsenceObservation('fallow-ground', NAMED, '2026-01-05')"
    )
    assert (
        _render_observation(
            AbsenceObservation(
                "fallow-ground", AbsenceState.NAMED, "note", date(2026, 1, 5)
            )
        )
        == "AbsenceObservation('fallow-ground', NAMED, date(2026, 1, 5))"
    )
    assert len(intake_probe_inputs()) == len(IntakeCode)


def test_the_battery_guards_reject_a_probe_that_misses_its_code() -> None:
    """Positive control: a guard that has never rejected is not protection."""

    from white_line.model import AbsenceObservation, AbsenceState
    from white_line.worked_examples import (
        intake_probe_inputs,
        intake_reachability_battery,
    )

    # A probe declaring UNTYPED_STATE but supplying a perfectly typed input.
    wrong_target = (
        (
            IntakeCode.UNTYPED_STATE,
            (AbsenceObservation("unasked-question", AbsenceState.NAMED, "well typed"),),
        ),
    )
    with pytest.raises(ValueError, match="produced no such event"):
        intake_reachability_battery(wrong_target)

    # A battery that reaches its codes but does not cover the alphabet.
    short = intake_probe_inputs()[:-1]
    assert len(short) < len(IntakeCode)
    with pytest.raises(ValueError, match="every IntakeCode member"):
        intake_reachability_battery(short)


def test_only_a_supplied_naming_can_sit_in_an_omission_band() -> None:
    """A reviewer-asserted UNRESOLVED was never a naming, so it never decayed.

    Without this filter the band labeled "already decayed — past its horizon"
    would collect observations that were asserted `UNRESOLVED` outright and
    never aged at all, which misreports what the ledger did.
    """

    from white_line import assess_absence
    from white_line.analysis import expiry_horizon
    from white_line.figures.plates.inspection import omitted_namings
    from white_line.model import AbsenceObservation, AbsenceState

    observations = (
        # Current dated naming: queued.
        AbsenceObservation(
            "unobserved-dependency", AbsenceState.NAMED, "fresh", "2026-07-01"
        ),
        # Naming with no date: undated band.
        AbsenceObservation("uncredited-labor", AbsenceState.NAMED, "no date"),
        # Naming aged past its horizon: decayed band.
        AbsenceObservation(
            "unasked-question", AbsenceState.NAMED, "stale", "2025-09-01"
        ),
        # Asserted UNRESOLVED, never a naming: neither band.
        AbsenceObservation("missing-null-results", AbsenceState.UNRESOLVED, "open"),
        # Asserted WITHHELD, never a naming: neither band.
        AbsenceObservation("withheld-material", AbsenceState.WITHHELD, "duty stated"),
        # A naming that lost a conflict to a more cautious observer: the
        # ledger does not report it as a naming, so it is in neither band.
        AbsenceObservation(
            "silenced-perspective", AbsenceState.NAMED, "named", "2026-07-10"
        ),
        AbsenceObservation(
            "silenced-perspective", AbsenceState.WITHHELD, "boundary stated"
        ),
    )
    report = assess_absence(observations, as_of="2026-07-18")
    queued = {entry.record_id for entry in expiry_horizon(report)}
    assert queued == {"unobserved-dependency"}
    assert report.finding_for("silenced-perspective").state is AbsenceState.WITHHELD
    undated, decayed = omitted_namings(report, observations, queued)
    assert undated == ("uncredited-labor",)
    assert decayed == ("unasked-question",)
    assert "silenced-perspective" not in undated + decayed
    # The two non-namings are UNRESOLVED and WITHHELD in the report, so a
    # state-only split would have swept the first into the decayed band.
    assert report.finding_for("missing-null-results").state is AbsenceState.UNRESOLVED
    assert "missing-null-results" not in decayed


def test_omitted_namings_ignores_an_id_absent_from_the_report() -> None:
    """An observation whose id no record carries has no finding to classify."""

    from white_line import assess_absence
    from white_line.figures.plates.inspection import omitted_namings
    from white_line.model import AbsenceObservation, AbsenceState

    stray = AbsenceObservation("no-such-record", AbsenceState.NAMED, "typo id")
    report = assess_absence((stray,), as_of="2026-07-18")
    assert report.finding_for("no-such-record") is None
    assert omitted_namings(report, (stray,), frozenset()) == ((), ())


def test_the_expiry_queue_draws_both_omission_bands_with_live_contents() -> None:
    """Both documented omissions are drawn, and neither band is empty."""

    from white_line.analysis import expiry_horizon
    from white_line.figures.plates.inspection import expiry_queue
    from white_line.worked_examples import expiry_observations, expiry_report

    svg = expiry_queue()
    report = expiry_report()
    entries = expiry_horizon(report)
    assert entries, "the queue fixture must produce at least one entry"
    titles = {record.id: record.title for record in WHITE_RECORDS}
    for index, entry in enumerate(entries):
        assert titles[entry.record_id] in svg
        assert (
            f"{entry.age_days} days old of {entry.horizon_days} · "
            f"{entry.days_remaining} days remaining" in svg
        )
        assert f"#{index + 1}" in svg
    assert "UNDATED NAMING" in svg
    assert "ALREADY DECAYED" in svg
    queued = {entry.record_id for entry in entries}
    from white_line.figures.plates.inspection import omitted_namings

    undated, decayed = omitted_namings(report, expiry_observations(), queued)
    assert undated and decayed, "both bands must be exercised by the fixture"
    for record_id in (*undated, *decayed):
        assert titles[record_id] in svg
    assert "none in this input" not in svg


def test_battery_facet_cells_preserve_every_scoring_branch():
    """Battery cells retain the facets of every native scoring branch."""

    from white_line import (
        WORKED_AS_OF,
        DisclosureStance,
        EpistemicSettlement,
        TemporalStatus,
        WitnessFacets,
        finding_facets,
        project_facets,
        scoring_branch_battery,
    )
    from white_line.figures.plates.evidence import battery_facet_cells
    from white_line.model import AbsenceState

    # The battery marks are derived from finding_facets over live findings.
    cells = battery_facet_cells()
    records_by_id = {record.id: record for record in WHITE_RECORDS}
    expected: dict[tuple, int] = {}
    for probe in scoring_branch_battery():
        facets = finding_facets(
            probe.finding, records_by_id[probe.finding.record_id], WORKED_AS_OF
        )
        key = (facets.settlement, facets.disclosure, facets.temporality)
        expected[key] = expected.get(key, 0) + 1
    assert cells == expected
    assert sum(cells.values()) == len(scoring_branch_battery())
    # The decay cell is annotated: NAMED settlement projecting to UNRESOLVED.
    decay = WitnessFacets(
        "cell",
        EpistemicSettlement.NAMED,
        DisclosureStance.OPEN,
        TemporalStatus.STALE,
    )
    assert project_facets(decay) is AbsenceState.UNRESOLVED
