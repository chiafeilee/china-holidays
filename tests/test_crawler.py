import pytest
from bs4.element import Tag
from selenium import webdriver

from holidays.crawler import Crawler


@pytest.fixture
def crawler():
    c = Crawler(2023)
    return c


def test_get_holiday_link(crawler):
    driver = webdriver.Chrome(options=crawler.options)
    link = crawler.get_holiday_link(driver)
    assert link.startswith("http")


def test_get_holiday_content(crawler):
    content = crawler.get_holiday_content()
    assert len(content) > 0
    assert isinstance(content[0], Tag)


def test_parse(crawler):
    parsed_content = crawler.parse()
    assert len(parsed_content) > 0
    assert isinstance(parsed_content[0], Tag)
