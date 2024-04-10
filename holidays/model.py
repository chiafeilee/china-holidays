from dataclasses import dataclass
from typing import List, Optional

import arrow

DATE_FMT = "YYYY-MM-DD"


@dataclass
class HolidayModel:
    year: int
    """年份"""

    name: str
    """节日名称"""

    start_date: str
    """假期开始日期"""

    days: int
    """假期天数"""

    makeup_days: Optional[List[str]]
    """调休日"""

    @property
    def dates(self):
        rv = [self.start_date]
        for i in range(1, self.days):
            rv.append(arrow.get(self.start_date).shift(days=i).format(DATE_FMT))
        return rv
