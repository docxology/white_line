"""The absence record type: one named, bounded gap the ledger tracks."""

from __future__ import annotations

from dataclasses import dataclass

from .kinds import AbsenceKind


@dataclass(frozen=True)
class AbsenceRecord:
    """One category of absence the ledger asks a reviewer to look for.

    ``prompt`` is the question a reviewer should sit with when reviewing the
    record. ``review_horizon_days`` bounds how long a dated ``NAMED``
    observation stays fresh: past the horizon, a naming decays back to
    ``UNRESOLVED`` until it is re-reviewed, because an old naming is itself a
    quiet form of absence.
    """

    id: str
    title: str
    kind: AbsenceKind
    description: str
    prompt: str = ""
    review_horizon_days: int = 90

    def canonical(self) -> dict[str, object]:
        """Return the stable, serialization-ready form of the record."""

        return {
            "id": self.id,
            "title": self.title,
            "kind": self.kind.value,
            "description": self.description,
            "prompt": self.prompt,
            "review_horizon_days": self.review_horizon_days,
        }
