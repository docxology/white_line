"""Define figure colours and display maps without assessing ledger records."""

from __future__ import annotations

from ..model import AbsenceKind, AbsenceState, IntakeCode

PAPER = "#F2EDE5"
CREAM = "#FFFDF8"
WHITE = "#FFFFFF"
INK = "#211A1D"
MUTED = "#6B6062"
TEAL = "#00796B"
OCHRE = "#B66A18"
VIOLET = "#4A148C"
SIENNA = "#8B4513"
CHARCOAL = "#3D3835"
LINE = "#BCAFA6"
PANEL = "#FFF8EE"

KIND_COLOR = {
    AbsenceKind.EPISTEMIC: TEAL,
    AbsenceKind.ETHICAL: OCHRE,
    AbsenceKind.CONTEMPLATIVE: VIOLET,
}
#: A distinct marker shape per kind, so a kind is readable without colour.
#: The figures are printed and read in greyscale as often as in colour; a
#: colour-only encoding would make the kind unrecoverable in either case.
KIND_MARKER = {
    AbsenceKind.EPISTEMIC: "circle",
    AbsenceKind.ETHICAL: "square",
    AbsenceKind.CONTEMPLATIVE: "triangle",
}
KIND_GLOSS = {
    AbsenceKind.EPISTEMIC: "unknown, unobserved, or unresolved",
    AbsenceKind.ETHICAL: "withheld, unrepresented, or not disclosed",
    AbsenceKind.CONTEMPLATIVE: "left open beyond a useful claim",
}
KIND_TITLE = {
    AbsenceKind.EPISTEMIC: "EPISTEMIC ABSENCE",
    AbsenceKind.ETHICAL: "ETHICAL RESTRAINT",
    AbsenceKind.CONTEMPLATIVE: "CONTEMPLATIVE SPACE",
}
KIND_GUARD = {
    AbsenceKind.EPISTEMIC: "do not infer a cause from a gap",
    AbsenceKind.ETHICAL: "do not force disclosure to complete a story",
    AbsenceKind.CONTEMPLATIVE: "do not mistake silence for an invisible force",
}
INTAKE_SET_ASIDE_GLOSS = {
    IntakeCode.NON_ITERABLE_INPUT: "whole input is not iterable",
    IntakeCode.NON_OBSERVATION: "not an absence observation",
    IntakeCode.UNKNOWN_RECORD: "unknown record id",
    IntakeCode.UNTYPED_STATE: "untyped state",
    IntakeCode.RESERVED_STATE: "asserts the ledger-reserved state",
}
DATED_INPUT_GLOSS = {
    IntakeCode.UNDATED_OBJECT: "keeps the observation; drops non-ISO dating"
}
MATCH_STAGE_GLOSS = {
    IntakeCode.CONFLICTING_STATES: "keeps the more cautious state",
    IntakeCode.DUPLICATE_STATE: "keeps the last-listed note",
}
STATE_COLOR = {
    AbsenceState.NOT_RECORDED: MUTED,
    AbsenceState.NAMED: TEAL,
    AbsenceState.UNRESOLVED: OCHRE,
    AbsenceState.WITHHELD: VIOLET,
}
STATE_GLOSS = {
    AbsenceState.NOT_RECORDED: "no observation was supplied (ledger-reserved)",
    AbsenceState.NAMED: "the absence is made explicit",
    AbsenceState.UNRESOLVED: "known but not settled",
    AbsenceState.WITHHELD: "intentionally not disclosed",
}


__all__ = [
    "CHARCOAL",
    "CREAM",
    "DATED_INPUT_GLOSS",
    "INK",
    "INTAKE_SET_ASIDE_GLOSS",
    "KIND_COLOR",
    "KIND_GLOSS",
    "KIND_GUARD",
    "KIND_MARKER",
    "KIND_TITLE",
    "LINE",
    "MATCH_STAGE_GLOSS",
    "MUTED",
    "OCHRE",
    "PANEL",
    "PAPER",
    "SIENNA",
    "STATE_COLOR",
    "STATE_GLOSS",
    "TEAL",
    "VIOLET",
    "WHITE",
]
