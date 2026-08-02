"""Public alias for the White Line model package.

``white_line.models`` exports the same public names as ``white_line.model``.
Both import paths are supported.
"""

from .model import (
    SET_ASIDE_CODES,
    AbsenceFinding,
    AbsenceKind,
    AbsenceObservation,
    AbsenceRecord,
    AbsenceState,
    IntakeCode,
    IntakeEvent,
    WhiteReport,
    caution_rank,
)

__all__ = [
    "AbsenceFinding",
    "AbsenceKind",
    "AbsenceObservation",
    "AbsenceRecord",
    "AbsenceState",
    "IntakeCode",
    "IntakeEvent",
    "SET_ASIDE_CODES",
    "WhiteReport",
    "caution_rank",
]
