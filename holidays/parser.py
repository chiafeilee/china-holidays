import re

import arrow
from bs4 import element

from holidays.model import HolidayModel

DATE_FMT = "YYYY-MM-DD"
PATTERN = "、(.*?)：((?:\d{4}年)?\d{1,2}月\d{1,2}日)[至]?((?:\d{4}年)?(?:\d{1,2}月)?\d{1,2}日)?\S+，共(\d)天。(?:(.*?)上班)?"


class HolidayParser:
    content: element.ResultSet

    def __init__(self, content: element.ResultSet, year: int) -> None:
        self.content = content
        self.year = year

    def _parse_makeup_days(self, makeup_days: str):
        if not makeup_days:
            return []

        date_list = makeup_days.split("、")
        rv = []
        for date_str in date_list:
            date_ = re.findall(r"(\d+月\d+)", date_str)[0]
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

        holiday_name, start_date, end_date, days, makeup_days = match[0]
        prev_holiday = None

        # cross year
        if "年" in start_date and "年" in end_date:
            start_date = self._format_date(start_date)

            # get the previous year's last day and calculate the days
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
                self._parse_makeup_days(makeup_days),
            )

        return prev_holiday, now_holiday
