"""Shared date coercion for review and analysis boundaries."""

from datetime import date, datetime

import pytest

from white_line.dates import coerce_date, coerce_review_date


def test_coerce_date_parses_iso_strings_and_preserves_dates() -> None:
    supplied = date(2026, 7, 18)
    assert coerce_date("2026-07-18", "start") == supplied
    assert coerce_date(supplied, "start") is supplied


def test_coerce_date_rejects_datetime_before_the_date_branch() -> None:
    with pytest.raises(TypeError, match="start must be a date, not a datetime"):
        coerce_date(datetime(2026, 7, 18), "start")


def test_coerce_date_names_its_argument_for_malformed_and_wrong_types() -> None:
    with pytest.raises(ValueError, match="end must be an ISO date in YYYY-MM-DD form"):
        coerce_date("2026-02-30", "end")
    with pytest.raises(ValueError, match="end must be an ISO date in YYYY-MM-DD form"):
        coerce_date("20260718", "end")
    with pytest.raises(TypeError, match="end must be an ISO date string or a date"):
        coerce_date(17, "end")  # type: ignore[arg-type]


def test_coerce_review_date_uses_today_only_for_none() -> None:
    assert coerce_review_date(None) == date.today()
    assert coerce_review_date("2026-07-18") == date(2026, 7, 18)
