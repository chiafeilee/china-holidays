import pickle
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import List, Optional, Union

import arrow
import requests
from bs4 import BeautifulSoup, element


SCRAPE_URL = "http://xxgk.www.gov.cn/search-zhengce/?mode=smart&sort=time&page_index=1&page_size=2&title=节假日"
HOLIDAY_FILE = "holiday.pickle"
RE_YEAR = re.compile("(\d+)年")
DATE_FMT = "YYYY-MM-DD"
PATTERN = "、(.*?)：((?:\d{4}年)?\d{1,2}月\d{1,2}日)[至]?((?:\d{4}年)?(?:\d{1,2}月)?\d{1,2}日)?\S+，共(\d)天。(?:(.*?)上班)?"


def as_date_str(d):
    return arrow.get(d).format(DATE_FMT)


@dataclass
class HolidayModel:
    year: int
    festival: str
    start: str
    days: int
    transfer_shifts: Optional[List[str]]

    @property
    def dates(self):
        rv = [self.start]
        for i in range(1, self.days):
            rv.append(arrow.get(self.start).shift(days=i).format(DATE_FMT))
        return rv


class HolidayParser:
    content: element.ResultSet

    def __init__(self, content: element.ResultSet, year: int) -> None:
        self.content = content
        self.year = year

    def _parse_shifts(self, shifts: str):
        if not shifts:
            return []
        shift_list = shifts.split("、")
        rv = []
        for s in shift_list:
            date_ = re.findall(r"(\d+月\d+)", s)[0]
            rv.append(
                arrow.get(f"{self.year}-{date_.replace('月', '-')}").format(DATE_FMT)
            )
        return rv

    def _format_date(self, date_str: str):
        return arrow.get(re.sub(r"年|月", "-", date_str).replace("日", "")).format(
            DATE_FMT
        )

    def parse(self):
        match = re.findall(PATTERN, self.content.get_text())
        if not match:
            return None, None

        holiday_name, start_date, end_date, days, shifts = match[0]
        prev_holiday = None

        # cross year
        if "年" in start_date and "年" in end_date:
            start_date = self._format_date(start_date)
            prev_year = int(start_date.split("-")[0])
            prev_year_last_day = arrow.get(f"{prev_year}-12-31")
            prev_holiday_days = (prev_year_last_day - arrow.get(start_date)).days + 1
            prev_holiday = HolidayModel(
                prev_year, holiday_name, start_date, prev_holiday_days, None
            )
            now_holiday = HolidayModel(
                self.year,
                holiday_name,
                f"{self.year}-01-01",
                int(days) - prev_holiday_days,
                None,
            )
        else:
            if "年" not in start_date:
                start_date = f"{self.year}年{start_date}"

            start_date = self._format_date(start_date)
            now_holiday = HolidayModel(
                self.year,
                holiday_name,
                start_date,
                int(days),
                self._parse_shifts(shifts),
            )
        return prev_holiday, now_holiday


def populate():
    notices = requests.get(SCRAPE_URL).json()["data"]
    holidays = []
    for notice in notices:
        year = RE_YEAR.findall(notice["title"])[0]
        post = requests.get(notice["url"]).content
        soup = BeautifulSoup(post, features="html.parser")
        contents = soup.find_all("p")

        for c in contents:
            prev, now = HolidayParser(c, int(year)).parse()
            if not prev and not now:
                continue

            if prev:
                holidays.append(asdict(prev))
            holidays.append(asdict(now))

    with open(HOLIDAY_FILE, "wb") as f:
        pickle.dump(holidays, f, protocol=pickle.HIGHEST_PROTOCOL)


try:
    with open(HOLIDAY_FILE, "rb") as f:
        holiday_data = pickle.load(f)
except Exception as e:
    populate()


class Holiday:
    year: int
    holidays: List[HolidayModel] = []

    def __init__(self, year: int) -> None:
        self.year = year
        self.holidays = [
            HolidayModel(**r)
            for r in [h for h in holiday_data if h["year"] == self.year]
        ]
        self.holiday_dates = set()
        for h in self.holidays:
            for d in h.dates:
                self.holiday_dates.add(d)

    def __contains__(self, d: Union[str, datetime, date]):
        if not isinstance(d, (str, datetime, date)):
            raise TypeError(f"Can't conver type {type(d)} to date.")

        str_date = as_date_str(d)

        return str_date in self.holiday_dates

    def is_workday(self, d):
        d = arrow.get(d)

        if d.date() in self:
            return False

        all_transfer_shifts: List[str] = []
        for h in self.holidays:
            all_transfer_shifts.extend(h.transfer_shifts or [])

        str_date = d.format(DATE_FMT)
        return any([d.isoweekday() <= 5, str_date in all_transfer_shifts])
