"""Date coercion at the ledger's explicit review boundaries."""

from __future__ import annotations

from datetime import date, datetime


def coerce_date(value: str | date, argument: str) -> date:
    """Return an ISO date or supplied ``date``; reject other values."""

    if isinstance(value, str):
        shape_is_calendar_date = (
            len(value) == 10
            and value[4] == "-"
            and value[7] == "-"
            and value[:4].isdigit()
            and value[5:7].isdigit()
            and value[8:].isdigit()
        )
        if not shape_is_calendar_date:
            raise ValueError(f"{argument} must be an ISO date in YYYY-MM-DD form")
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                f"{argument} must be an ISO date in YYYY-MM-DD form"
            ) from exc
    if isinstance(value, datetime):
        raise TypeError(f"{argument} must be a date, not a datetime")
    if isinstance(value, date):
        return value
    raise TypeError(f"{argument} must be an ISO date string or a date")


def coerce_review_date(value: str | date | None) -> date:
    """Return today's date for ``None`` or coerce an explicit review date."""

    return date.today() if value is None else coerce_date(value, "as_of")


#: Note emitted for an accepted observation whose ``observed_on`` is neither
#: ``None``, the empty string, nor a string at all. The observation is kept;
#: only its dating is unusable.
UNDATED_OBJECT_NOTE = (
    "the observation date object is not an ISO date string; it was kept but cannot "
    "participate in staleness accounting"
)


def usable_observation_date(
    raw: object, review_date: date
) -> tuple[date | None, str]:
    """Resolve an ``observed_on`` value for staleness accounting.

    This is the single implementation of the manuscript's date-resolution rule
    :math:`\\delta`. The assessor uses it when scoring a record, and
    ``white_line.analysis.expiry_horizon`` uses it when reading a report back,
    so the two can never disagree about which dates staleness accounting may
    use.

    Args:
        raw: The observation's ``observed_on`` value, of any runtime type.
        review_date: The report's resolved review date.

    Returns:
        A pair of (usable date or ``None``, issue note). The note is empty
        when there is nothing to report — either the date is usable, or the
        observation was ordinary undated input.
    """

    if raw is None or raw == "":
        return None, ""
    if not isinstance(raw, str):
        return None, UNDATED_OBJECT_NOTE
    try:
        observed = coerce_date(raw, "observation date")
    except ValueError:
        return None, f"the observation date {raw!r} is unreadable and was ignored"
    if observed > review_date:
        return (
            None,
            f"the observation date {raw!r} is after the review date and was ignored",
        )
    return observed, ""


__all__ = [
    "UNDATED_OBJECT_NOTE",
    "coerce_date",
    "coerce_review_date",
    "usable_observation_date",
]
