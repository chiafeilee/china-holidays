import pytest

from holidays import Holiday


def test_is_holiday():
    holiday = Holiday(2023)
    assert "2023-10-06" in holiday


def test_not_a_holiday():
    holiday = Holiday(2023)
    assert "2023-04-28" not in holiday


def test_is_workday():
    holiday = Holiday(2023)
    assert holiday.is_workday("2023-10-07")
