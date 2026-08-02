# Model contract

This folder owns the immutable vocabulary and report records used by the
assessor. It does not decide intake, reconciliation, staleness, directives, or
artifact generation; those are owned by sibling modules.

## Public types and guarantees

- `kinds.py`: `AbsenceKind` and `AbsenceState` are string enums;
  `caution_rank(state: AbsenceState) -> int` defines the only reconciliation
  order. `NOT_RECORDED` is ledger-reserved and cannot be asserted by an input.
- `records.py`: `AbsenceRecord(id: str, title: str, kind: AbsenceKind,
  description: str, prompt: str = "", review_horizon_days: int = 90)`;
  `record.canonical() -> dict[str, object]` returns its stable form.
- `reports.py`: `AbsenceObservation(record_id: str, state: AbsenceState,
  note: str = "", observed_on: str = "")`, `IntakeEvent(code: IntakeCode,
  message: str, position: int | None = None, record_id: str = "", state:
  AbsenceState | None = None)`, `AbsenceFinding(record_id: str, kind:
  AbsenceKind, state: AbsenceState, reasons: tuple[str, ...], observed_on:
  str = "")`, and `WhiteReport(findings: tuple[AbsenceFinding, ...],
  intake_notes: tuple[str, ...] = (), review_date: str = "", registry_digest:
  str = "", intake_events: tuple[IntakeEvent, ...] = ())` are frozen data
  classes. `WhiteReport.tally() -> dict[AbsenceState, int]`,
  `finding_for(record_id: str) -> AbsenceFinding | None`, and properties
  `accepted_observation_count` and `set_aside_count` expose derived report
  data. `IntakeCode` is the complete typed intake-event enum.

Changing a type requires matching assessor, serializer, tests, documentation,
figures, and audit changes. Preserve the trace fields (`reasons`, review date,
digest, and intake events) and the rule that a type records a ledger state,
not a fact about a person or world.

Run `uv run pytest tests/test_assessor.py tests/test_api.py -q`. Read
[README.md](README.md), [../AGENTS.md](../AGENTS.md), and the root
[../../../AGENTS.md](../../../AGENTS.md).

Project root: [AGENTS.md](../../../AGENTS.md) and [README.md](../../../README.md).
