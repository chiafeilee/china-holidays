import json
import pickle
import re
from dataclasses import asdict
from datetime import date, datetime
from typing import List, Literal, Union

import arrow

from holidays.crawler import Crawler
from holidays.model import HolidayModel
from holidays.parser import HolidayParser

HOLIDAY_FILE = "holiday.{format}"
HOLIDAY_FILE_FORMAT = Literal["pickle", "json", "ics"]
RE_YEAR = re.compile("(\d+)年")
DATE_FMT = "YYYY-MM-DD"


class Holiday:
    year: int
    holidays: List[HolidayModel] = []

    def __init__(self, year: int) -> None:
        self.year = year
        self.holidays = []
        self.holiday_dates = set()

    def __contains__(self, date_: Union[str, datetime, date]):
        if not isinstance(date_, (str, datetime, date)):
            raise TypeError(f"Can't conver type {type(date_)} to date.")

        str_date = arrow.get(date_).format(DATE_FMT)

        return str_date in self.holiday_dates

    def init_data_source(self, source_fmt: HOLIDAY_FILE_FORMAT = "pickle"):
        with open(HOLIDAY_FILE.format(format=source_fmt), "rb") as f:
            try:
                holiday_data = pickle.load(f)

                self.holidays = [
                    HolidayModel(**r)
                    for r in [h for h in holiday_data if h["year"] == self.year]
                ]

                for h in self.holidays:
                    for d in h.dates:
                        self.holiday_dates.add(d)
            except Exception:
                raise Exception("Holiday data source file not found")

    def is_working_day(self, date_):
        date_ = arrow.get(date_)

        if date_.date() in self:
            return False

        all_makeup_days: List[str] = []
        for h in self.holidays:
            all_makeup_days.extend(h.makeup_days or [])

        str_date = date_.format(DATE_FMT)
        return any([date_.isoweekday() <= 5, str_date in all_makeup_days])

    @classmethod
    def generate_holiday_file(cls, year, format: HOLIDAY_FILE_FORMAT = "pickle"):
        holidays = []
        contents = Crawler(year).parse()

        for content in contents:
            prev, now = HolidayParser(content, int(year)).parse()
            if not prev and not now:
                continue

            if prev:
                holidays.append(asdict(prev))
            holidays.append(asdict(now))

        with open(HOLIDAY_FILE.format(format=format), "wb") as f:
            if format == "pickle":
                pickle.dump(holidays, f, protocol=pickle.HIGHEST_PROTOCOL)
            elif format == "json":
                json.dump(holidays, f)
            elif format == "ics":
                # TODO: Implement ics file generation
                pass
            else:
                raise ValueError(f"Unsupported format: {format}")
