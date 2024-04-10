import pytest
from bs4 import BeautifulSoup

from holidays.parser import HolidayParser


@pytest.fixture
def parser():
    content = BeautifulSoup("<html><body>...</body></html>", "html.parser")
    year = 2023
    return HolidayParser(content, year)


def test_parse_with_cross_year(parser):
    parser.content = BeautifulSoup(
        "一、元旦：2022年12月31日至2023年1月2日放假调休，共3天。",
        "html.parser",
    )
    prev_holiday, now_holiday = parser.parse()

    assert prev_holiday.year == 2022
    assert prev_holiday.name == "元旦"
    assert prev_holiday.start_date == "2022-12-31"
    assert prev_holiday.days == 1
    assert prev_holiday.makeup_days is None

    assert now_holiday.year == 2023
    assert now_holiday.name == "元旦"
    assert now_holiday.start_date == "2023-01-01"
    assert now_holiday.days == 2
    assert now_holiday.makeup_days is None


def test_parse_without_cross_year(parser):
    parser.content = BeautifulSoup("三、清明节：4月5日放假，共1天。", "html.parser")
    prev_holiday, now_holiday = parser.parse()

    assert prev_holiday is None

    assert now_holiday.year == 2023
    assert now_holiday.name == "清明节"
    assert now_holiday.start_date == "2023-04-05"
    assert now_holiday.days == 1
    assert now_holiday.makeup_days is None


def test_parse_with_makeup_days(parser):
    parser.content = BeautifulSoup(
        "四、劳动节：4月29日至5月3日放假调休，共5天。4月23日（星期日）、5月6日（星期六）上班。",
        "html.parser",
    )
    prev_holiday, now_holiday = parser.parse()

    assert prev_holiday is None

    assert now_holiday.year == 2023
    assert now_holiday.name == "劳动节"
    assert now_holiday.start_date == "2023-04-29"
    assert now_holiday.days == 5
    assert now_holiday.makeup_days == ["2023-04-23", "2023-05-06"]
