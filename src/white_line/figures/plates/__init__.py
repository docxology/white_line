"""Register White Line figure plates without interpreting their contents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .contract import caution_ladder, review_protocol, state_machine
from .distributions import conflict_lattice, decay_timeline, distribution_panels
from .evidence import facets_lattice, invariant_battery, reason_trail
from .inspection import expiry_queue, horizon_dispersion, intake_reachability
from .overview import (
    absence_layers,
    cover_art,
    registry_taxonomy,
    review_atlas,
    scholarship_map,
)


@dataclass(frozen=True)
class FigurePlate:
    """Describe one generated plate and its declared provenance."""

    name: str
    render: Callable[[], str]
    label: str
    caption: str
    alt: str
    source: str


FIGURE_PLATES = (
    FigurePlate(
        "white_cover_art",
        cover_art,
        "fig:white-cover-art",
        "A charcoal-like cover plate for White Line: congested graphite marks press toward an irregular open field while three colored traces cross it without closing it. The art is a deterministic composition tied to the live registry count; it is a boundary for interpretation, not evidence of a hidden cause.",
        "Charcoal-like White Line cover art showing an irregular open field crossed by sienna, purple, and teal traces amid graphite hatching.",
        "WHITE_RECORDS count and scripts/build_figures.py visual composition",
    ),
    FigurePlate(
        "white_absence_layers",
        absence_layers,
        "fig:white-absence-layers",
        "White Line separates epistemic absence, ethical restraint, and contemplative space. Panels are generated from the AbsenceKind vocabulary and the shared kind glosses, with per-kind record counts and review-horizon ranges read from the live registry. The figure is a deterministic schematic of the typology, not evidence of a causal force, completeness score, or diagnosis.",
        "Three White Line absence layers derived from the kind vocabulary, each with its gloss, guard clause, and live registry record count and horizon range.",
        "white_line registry, state alphabet, and review protocol",
    ),
    FigurePlate(
        "white_registry_taxonomy",
        registry_taxonomy,
        "fig:white-registry-taxonomy",
        "The current versioned absence registry, grouped by kind, with each record's review horizon. Generated directly from WHITE_RECORDS; a record's presence names a category to review, not a populated finding.",
        "Registry taxonomy: eleven absence records in three columns by kind, each with its review horizon in days.",
        "white_line registry, state alphabet, and review protocol",
    ),
    FigurePlate(
        "white_review_atlas",
        review_atlas,
        "fig:white-review-atlas",
        "A compact system map of White Line's three moves: type the limit, reconcile the record, and open a bounded next step. Counts and actions are drawn from the live registry, state enumeration, and review protocol; the atlas makes no claim about an observed population.",
        "White Line review atlas connecting three absence kinds to intake, matching, scoring, and four bounded human follow-up actions.",
        "white_line registry, state alphabet, and review protocol",
    ),
    FigurePlate(
        "white_scholarship_map",
        scholarship_map,
        "fig:white-scholarship-map",
        "A non-exhaustive scholarship-to-design matrix connecting situated knowledge, produced ignorance, missing-data methodology, classification, epistemic justice, refusal, opacity, and contemplative restraint to a limited White Line operation: type, bound, and revisit. The matrix distinguishes reviewer responsibilities from code behavior; it does not claim that the cited traditions are one theory.",
        "Scholarship matrix connecting seven intellectual conversations to the questions they force and White Line's limited type, bound, and revisit operations.",
        "manuscript/01c_scholarship.md synthesis and scripts/build_figures.py layout",
    ),
    FigurePlate(
        "white_state_machine",
        state_machine,
        "fig:white-state-machine",
        "The staged evaluator's decision path: intake sets aside untrusted input with a typed note, dating records a retained observation whose non-ISO date cannot age, matching keeps the more cautious observation per record, and scoring assigns one of four ledger states. The intake, dating, and match categories name every IntakeCode member, so the panels cannot silently drift from the intake rules; the labeled staleness arrow shows a dated NAMED decaying to UNRESOLVED past its horizon. Generated from the evaluator contract, not from observed data.",
        "Evaluator decision path from intake through dating and matching to the four ledger states, with every IntakeCode category named and a labeled staleness-decay arrow from NAMED to UNRESOLVED.",
        "white_line registry, state alphabet, and review protocol",
    ),
    FigurePlate(
        "white_reason_trail",
        reason_trail,
        "fig:white-reason-trail",
        "One row per branch of the scoring rule, each computed by a live assess_absence call and drawn with the ordered reason trail the evaluator returned. The two conditional reasons appear only in the branch that adds them: a blank-note withholding gains the duty reason, and a dated naming gains either its age line or the decay line. The plate quotes what the evaluator wrote, so a reworded reason moves the figure rather than leaving the prose behind. A reason explains one scoring decision, never a judgment of the observation or of whoever supplied it.",
        "One row per scoring branch, each quoting the input supplied, the state the ledger reported, and the numbered reasons the evaluator returned for it.",
        "white_line.worked_examples.scoring_branch_battery run through assess_absence",
    ),
    FigurePlate(
        "white_caution_ladder",
        caution_ladder,
        "fig:white-caution-ladder",
        "The defined caution order drawn from caution_rank: withholding outranks an open question, which outranks a settled naming, which outranks silence. Each rung also reports, live from reconciliation_matrix, in how many of the nine ordered pairs it is the kept state. A higher rung means more restraint, not more danger.",
        "A four-rung caution ladder from NOT_RECORDED at the bottom to WITHHELD at the top, drawn from caution_rank with per-rung reconciliation-pair counts; the reconciliation and staleness rules that use this order are drawn in the conflict-lattice and decay-timeline figures.",
        "white_line registry, state alphabet, and review protocol",
    ),
    FigurePlate(
        "white_review_protocol",
        review_protocol,
        "fig:white-review-protocol",
        "The bounded review protocol maps each ledger state to a follow-up action without producing permission, compliance, or safety approval. It is derived from the state enumeration and review directives.",
        "Review protocol mapping the four absence states to bounded human follow-up actions and a no-certification reading rule.",
        "white_line registry, state alphabet, and review protocol",
    ),
    FigurePlate(
        "white_decay_timeline",
        decay_timeline,
        "fig:white-decay-timeline",
        "Staleness decay computed by sweeping assess_absence over review dates: an illustrative cohort gives every registry record a NAMED observation dated 2026-01-01, and the same input is re-assessed at each later date. Each dashed crossing is one review horizon expiring, moving records from NAMED to UNRESOLVED. The curve describes the staleness contract applied to supplied observations, not observed data about any work.",
        "Step chart of NAMED and UNRESOLVED record counts versus days since a dated naming, with dashed vertical lines at each review-horizon crossing.",
        "white_line.analysis.decay_timeline swept over assess_absence and the live registry",
    ),
    FigurePlate(
        "white_conflict_lattice",
        conflict_lattice,
        "fig:white-conflict-lattice",
        "The full ordered-pair conflict-resolution table for assertable states, generated from caution_rank via reconciliation_matrix. Every cell keeps the more cautious input, the table is symmetric under swapping the observers, and NOT_RECORDED appears nowhere because observations may not assert it. The lattice records the reconciliation contract, not a severity score or a judgment of any observer.",
        "Three-by-three lattice of held versus incoming absence states, each cell colored by the kept, more cautious state with its caution rank.",
        "white_line.analysis.reconciliation_matrix derived from caution_rank",
    ),
    FigurePlate(
        "white_distribution_panels",
        distribution_panels,
        "fig:white-distribution-panels",
        "The two distributional views of the worked seven-input example, computed live through assess_absence, events_tally, and coverage_matrix: intake-event counts per code in the upper panel (zeros reported, never omitted) and the kind-by-state coverage matrix in the lower panel, with row sums matching the registry's partition by kind and column sums matching the report's own tally. Neither an event count nor a cell count is a completeness score, a safety score, or a verdict on whoever supplied the input.",
        "Two-panel figure stacked vertically: horizontal bars of intake-event counts per code above a kind-by-state coverage matrix with live row and column sums for the worked seven-input example.",
        "white_line.analysis.events_tally and coverage_matrix over a live assess_absence report",
    ),
    FigurePlate(
        "white_expiry_queue",
        expiry_queue,
        "fig:white-expiry-queue",
        "The refresh queue computed by white_line.analysis.expiry_horizon over one assessed report: every current dated NAMED finding, ranked nearest-boundary-first, with its kind shown by colour and by marker shape, its age drawn as a filled portion of its own review horizon, and its remaining days stated in words. The helper's two documented omissions are drawn as labelled bands rather than dropped: a naming the evaluator could not date cannot expire, and a naming already past its horizon is reported UNRESOLVED. Queue position is a review cadence, not importance, risk, or a completeness score.",
        "Ranked refresh queue of current dated namings with kind markers, horizon bars, and remaining-day counts, above two labelled bands listing the undated and already-decayed namings the queue omits.",
        "white_line.analysis.expiry_horizon over a live assess_absence report",
    ),
    FigurePlate(
        "white_horizon_dispersion",
        horizon_dispersion,
        "fig:white-horizon-dispersion",
        "Every registry record placed on a shared days axis by its review_horizon_days, grouped into one band per AbsenceKind and keyed by colour and by marker shape, with each kind's median horizon marked. Read from WHITE_RECORDS. The dispersion shows a structural asymmetry the per-kind range in the layers figure compresses away: the contemplative horizons are uniform at one value while the epistemic and ethical horizons spread across several. A horizon is the cadence on which the ledger asks about a record again; it is not a claim about how fast the world changes, and a longer horizon is not a lower priority.",
        "Three horizontal bands, one per absence kind, with a labelled marker per record positioned by its review horizon in days and a dashed line at each kind's median; contemplative records stack at a single value while epistemic and ethical records spread.",
        "WHITE_RECORDS review horizons grouped by AbsenceKind",
    ),
    FigurePlate(
        "white_invariant_battery",
        invariant_battery,
        "fig:white-invariant-battery",
        "One row per structural invariant, computed by running the whole check battery over the live registry and then over a registry carrying exactly the defect that invariant guards against. Each row shows the check's verdict on the real registry and the detail string it returned when it rejected the planted defect, so a check that stopped rejecting would empty its own row rather than pass quietly. The plate demonstrates detection of the planted defects; it is not a claim that the six checks exhaust the structural faults a registry could carry.",
        "One row per structural check, naming the defect planted to defeat it and quoting the detail string the check returned when it refused the planted registry.",
        "white_line.invariants.invariant_defect_battery over the live registry and its planted defects",
    ),
    FigurePlate(
        "white_facets_lattice",
        facets_lattice,
        "fig:white-facets-lattice",
        "The full facet lattice computed by running project_facets over every settlement, disclosure-stance, and temporal-status combination: each cell is coloured and labelled by the single caution-ordered state the projection returns, the cells for an UNDISCLOSED settlement without a stated withholding are drawn hatched because that combination fails closed rather than projecting, and the cells inhabited by the live scoring battery are marked by factoring each of its findings through finding_facets at build time. The one cell where a NAMED settlement projects to UNRESOLVED is the staleness decay recovered as a projection. The lattice is a projection table of recorded-data facets; it is not a claim that richer states exist in the world, and an inhabited cell is a fact about the battery's constructed inputs, never about any observed work.",
        "Eight-row by three-column lattice of witness facet combinations, each cell labelled with the absence state the projection returns, three hatched fail-closed cells for an undisclosed settlement without a stated withholding, and marked cells showing where the live scoring battery's findings land.",
        "white_line.facets.project_facets over every facet combination, with finding_facets over scoring_branch_battery",
    ),
    FigurePlate(
        "white_intake_reachability",
        intake_reachability,
        "fig:white-intake-reachability",
        "A positive control for the intake contract: one constructed input per IntakeCode, each run through assess_absence, drawn as one row with the input quoted beside the typed note the evaluator produced for it. Every member of the live enumeration fires, so a zero in the worked tally means the code was not triggered by that input rather than that the code is unreachable. The battery is built to exercise the contract; it is not observed input, and no note is a verdict on whoever supplied an input.",
        "One row per intake code, each quoting the constructed input that triggers it beside the typed intake note the evaluator returned, showing that every code in the enumeration is reachable.",
        "white_line.worked_examples.intake_reachability_battery run through assess_absence",
    ),
)

__all__ = ["FIGURE_PLATES", "FigurePlate"]
