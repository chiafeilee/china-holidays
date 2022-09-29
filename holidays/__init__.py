import pickle
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import List, Optional, Union

import arrow
import requests
from bs4 import BeautifulSoup, element


SCRAPE_URL = "http://xxgk.www.gov.cn/search-zhengce/?mode=smart&sort=relevant&page_index=1&page_size=2&title=节假日&tag=国办发明电"
HOLIDAY_FILE = "holiday.pickle"
RE_SENTENCE = re.compile("^([一二三四五六七])、(.+)：(.+)，共(\d)天。([\S]*)$")
RE_YEAR = re.compile("(\d+)年")
DATE_FMT = "YYYY-MM-DD"


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


class HolidayNotice:
    content: element.ResultSet

    def __init__(self, content: element.ResultSet, year: int) -> None:
        self.content = content
        self.year = year

    def _parse_date(self, content: str):
        dates = re.finditer(r"(\d+月\d+日)", content)
        for d in dates:
            rv = (
                f"{self.year}年{d.group()}".replace("年", "-")
                .replace("月", "-")
                .replace("日", "")
            )
            yield as_date_str(rv)

    def holiday(self) -> Optional[HolidayModel]:
        match = RE_SENTENCE.match(self.content.get_text())

        if not match:
            return None

        _, festival, hol, days, shifts = match.groups()

        start_date = hol.split("至")[0]
        if "年" not in start_date:
            start_date = f"{self.year}年{start_date}"

        start_date = as_date_str(
            start_date.replace("年", "-").replace("月", "-").replace("日", "")
        )
        transfer_shifts = []

        if shifts:
            transfer_shifts.extend(list(self._parse_date(shifts)))

        return HolidayModel(self.year, festival, start_date, int(days), transfer_shifts)


def populate():
    notices = requests.get(SCRAPE_URL).json()["data"]
    holidays = []
    ds = {}
    for notice in notices:
        year = RE_YEAR.findall(notice["title"])[0]
        post = requests.get(notice["url"]).content
        soup = BeautifulSoup(post, features="html.parser")
        contents = soup.find_all(
            "p",
            attrs={
                "style": "text-align: justify; text-indent: 2em; font-family: 宋体; margin-top: 0px; margin-bottom: 0px;"
            },
        )
        for c in contents:
            rv = HolidayNotice(c, int(year)).holiday()
            if not rv:
                continue
            holidays.append(asdict(rv))
        ds[year] = holidays

    with open(HOLIDAY_FILE, "wb") as f:
        pickle.dump(ds, f, protocol=pickle.HIGHEST_PROTOCOL)


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
        self.holidays = [HolidayModel(**r) for r in holiday_data[str(self.year)]]

    def __contains__(self, d: Union[str, datetime, date]):
        if not isinstance(d, (str, datetime, date)):
            raise TypeError(f"Can't conver type {type(d)} to date.")

        d = as_date_str(d)
        contained = False
        for h in self.holidays:
            if d in h.dates:
                contained = True
                break
        return contained

    def is_workday(self, d):
        d = arrow.get(d)

        if d.date() in self:
            return False

        all_transfer_shifts: List[str] = []
        for h in self.holidays:
            all_transfer_shifts.extend(h.transfer_shifts)

        str_date = d.format(DATE_FMT)
        return any([d.isoweekday() <= 5, str_date in all_transfer_shifts])
