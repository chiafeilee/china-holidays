import pytest

from holidays import Holiday


def test_is_holiday():
    holiday = Holiday(2022)
    assert "2022-10-06" in holiday


def test_not_a_holiday():
    holiday = Holiday(2022)
    assert "2022-09-30" not in holiday


def test_is_workday():
    holiday = Holiday(2022)
    assert holiday.is_workday("2022-10-08")
