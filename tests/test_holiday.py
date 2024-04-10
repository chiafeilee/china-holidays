import pathlib

import pytest

from holidays import Holiday


@pytest.fixture
def holiday():
    h = Holiday(2023)
    h.init_data_source()
    return h


def test_is_holiday(holiday):
    assert "2023-10-06" in holiday


def test_not_a_holiday(holiday):
    assert "2023-04-28" not in holiday


def test_is_working_day(holiday):
    assert holiday.is_working_day("2023-10-07")


def test_generate_holiday_file():
    Holiday.generate_holiday_file(2023, format="pickle")

    file_path = pathlib.Path(__file__).parent.parent / "holiday.pickle"
    assert file_path.exists()
